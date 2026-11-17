#!/usr/bin/env python3
"""
Mound Hunter v0 — Goldmine Hunter's geographic twin.

Doctrine (same as Goldmine Hunter): don't inventory everything.
Hunt a comparable SET — circular, low, man-made-looking mounds in a
river plain — that has vanished from the modern record, using only
public-domain / openly-licensed data, and rank candidates with reasons.

Data (all open):
  - Copernicus DEM GLO-30 (AWS Open Data, no key): elevation, 30 m/px
  - Esri World Imagery tiles: visual chips for human verification only

Method v0 (heuristic, NOT a trained CNN — that is v1):
  1. Mosaic the DEM tiles covering the AOI.
  2. Local relief = DEM - gaussian_smooth(DEM, ~450 m).
     A stupa/settlement mound is a positive bump on a flat plain.
  3. Mask to floodplain: smoothed elevation < 260 m and low background
     ruggedness — rocky Vindhya/Satpura hillocks are excluded by design.
  4. Label connected bumps with relief >= 2.5 m, diameter 40–280 m,
     score by relief, circularity, size-in-stupa-range, and distance
     to the Narmada / Baghni drainage (river proxy: low plain + AOI rivers
     are approximated by distance to known river towns in v0 — flagged).
  5. Emit ranked candidates + a satellite chip and a hillshade chip
     for each, so a human can kill false positives at a glance.

Known limits (stated in every report):
  - 30 m DEM cannot see a mound < ~40 m wide or < ~2 m high.
  - Bagh Caves are cliff caves, not a mound: detector must NOT claim them.
  - Modern tanks, threshing grounds, natural levees are classic false
    positives. A candidate is a place to LOOK, never a discovery claim.
"""
import argparse, json, math, os, sys, time
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "outputs"
CHIPS = OUT / "chips"

DEM_URL = ("https://copernicus-dem-30m.s3.amazonaws.com/"
           "Copernicus_DSM_COG_10_{tile}_DEM/Copernicus_DSM_COG_10_{tile}_DEM.tif")
ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

# AOI: Kasrawad–Maheshwar–Anjad–Bagh corridor
AOI = dict(lat_min=22.00, lat_max=22.45, lon_min=74.65, lon_max=75.75)


def dem_tiles_for_aoi(aoi):
    tiles = []
    for lat in range(int(math.floor(aoi["lat_min"])), int(math.floor(aoi["lat_max"])) + 1):
        for lon in range(int(math.floor(aoi["lon_min"])), int(math.floor(aoi["lon_max"])) + 1):
            tiles.append(f"N{lat:02d}_00_E{lon:03d}_00")
    return tiles


def fetch_dem(tile):
    DATA.mkdir(parents=True, exist_ok=True)
    p = DATA / f"{tile}.tif"
    if p.exists() and p.stat().st_size > 1_000_000:
        return p
    url = DEM_URL.format(tile=tile)
    print(f"  DEM {tile} …", flush=True)
    r = requests.get(url, timeout=300)
    r.raise_for_status()
    p.write_bytes(r.content)
    return p


def load_mosaic(aoi):
    import rasterio
    from rasterio.merge import merge
    from rasterio.windows import from_bounds
    srcs = [rasterio.open(fetch_dem(t)) for t in dem_tiles_for_aoi(aoi)]
    mosaic, transform = merge(srcs)
    dem = mosaic[0].astype(np.float32)
    # crop to AOI
    inv = ~transform
    c0, r0 = inv * (aoi["lon_min"], aoi["lat_max"])
    c1, r1 = inv * (aoi["lon_max"], aoi["lat_min"])
    c0, c1 = max(0, int(c0)), min(dem.shape[1], int(c1))
    r0, r1 = max(0, int(r0)), min(dem.shape[0], int(r1))
    dem = dem[r0:r1, c0:c1]
    # new transform for the crop
    from rasterio.transform import Affine
    transform = transform * Affine.translation(c0, r0)
    for s in srcs:
        s.close()
    dem[dem < -1000] = np.nan
    return dem, transform


def detect(dem, transform, max_candidates=60):
    px_m = 30.0  # Copernicus GLO-30 nominal
    filled = np.where(np.isnan(dem), np.nanmedian(dem), dem)
    smooth = ndimage.gaussian_filter(filled, sigma=15)          # ~450 m plain
    relief = filled - smooth
    # local std via uniform filters (fast; generic_filter is far too slow here)
    m = ndimage.uniform_filter(filled, size=15)
    m2 = ndimage.uniform_filter(filled * filled, size=15)
    rugged = np.sqrt(np.maximum(m2 - m * m, 0))
    floodplain = (smooth < 260) & (rugged < 8)
    mask = floodplain & (relief >= 2.5) & (relief <= 15)
    lab, n = ndimage.label(mask)
    objs = ndimage.find_objects(lab)
    cands = []
    for i, sl in enumerate(objs, start=1):
        if sl is None:
            continue
        comp = lab[sl] == i
        area_px = int(comp.sum())
        area_m2 = area_px * px_m * px_m
        diam = 2 * math.sqrt(area_m2 / math.pi)
        if not (40 <= diam <= 280) or area_px < 2:
            continue
        h, w = comp.shape
        circularity = min(h, w) / max(h, w)
        if circularity < 0.45:
            continue
        peak = float(relief[sl][comp].max())
        mean_relief = float(relief[sl][comp].mean())
        cy, cx = ndimage.center_of_mass(comp)
        gy, gx = sl[0].start + cy, sl[1].start + cx
        lon, lat = transform * (gx, gy)
        # score: relief in the stupa band + circularity + size in band
        size_score = 1.0 - min(1.0, abs(diam - 110) / 170)
        score = round(0.45 * min(1.0, peak / 8) + 0.30 * circularity + 0.25 * size_score, 3)
        cands.append(dict(lat=round(float(lat), 5), lon=round(float(lon), 5),
                          diameter_m=round(diam), peak_relief_m=round(peak, 1),
                          mean_relief_m=round(mean_relief, 1), circularity=round(float(circularity), 2),
                          score=score,
                          why=f"DEM bump +{peak:.1f} m over the plain, ~{diam:.0f} m across, circularity {circularity:.2f}, on floodplain <260 m"))
    cands.sort(key=lambda c: -c["score"])
    # de-duplicate near-identical neighbours (<250 m apart keep best)
    kept = []
    for c in cands:
        if all((c["lat"] - k["lat"]) ** 2 + (c["lon"] - k["lon"]) ** 2 > (0.0025) ** 2 for k in kept):
            kept.append(c)
        if len(kept) >= max_candidates:
            break
    return kept, dict(pixels=int(dem.size), labelled_components=int(n))


def lonlat_to_tile(lon, lat, z):
    n = 2 ** z
    x = int((lon + 180) / 360 * n)
    y = int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)
    return x, y


def chip(lat, lon, path, z=16, grid=3):
    x0, y0 = lonlat_to_tile(lon, lat, z)
    img = Image.new("RGB", (256 * grid, 256 * grid))
    half = grid // 2
    for dx in range(-half, half + 1):
        for dy in range(-half, half + 1):
            try:
                r = requests.get(ESRI.format(z=z, x=x0 + dx, y=y0 + dy), timeout=30,
                                 headers={"User-Agent": "MoundHunter/0.1 research"})
                if r.ok:
                    from io import BytesIO
                    t = Image.open(BytesIO(r.content)).convert("RGB")
                    img.paste(t, ((dx + half) * 256, (dy + half) * 256))
            except Exception:
                pass
    d = ImageDraw.Draw(img)
    c = 256 * grid // 2
    d.ellipse([c - 28, c - 28, c + 28, c + 28], outline=(255, 60, 60), width=4)
    d.line([c - 45, c, c + 45, c], fill=(255, 60, 60), width=3)
    d.line([c, c - 45, c, c + 45], fill=(255, 60, 60), width=3)
    img.save(path)
    return path.name


def hillshade_chip(dem, transform, lat, lon, path, half_px=14):
    inv = ~transform
    cx, cy = inv * (lon, lat)
    cx, cy = int(cx), int(cy)
    sub = dem[max(0, cy - half_px):cy + half_px, max(0, cx - half_px):cx + half_px]
    if sub.size == 0:
        return None
    gy, gx = np.gradient(np.where(np.isnan(sub), np.nanmedian(dem), sub))
    slope = np.pi / 2 - np.arctan(np.hypot(gx, gy) * 30)
    az, alt = np.radians(315), np.radians(45)
    hs = (np.sin(alt) * np.sin(slope) + np.cos(alt) * np.cos(slope) *
          np.cos((az - np.pi / 2) - np.arctan2(-gy, gx)))
    img = Image.fromarray((np.clip(hs, 0, 1) * 255).astype(np.uint8), "L").convert("RGB")
    img = img.resize((512, 512), Image.NEAREST)
    img.save(path)
    return path.name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=20, help="candidates to chip and report")
    args = ap.parse_args()
    t0 = time.time()
    print("Mound Hunter v0 — Kasrawad–Bagh corridor")
    dem, transform = load_mosaic(AOI)
    print(f"  DEM mosaic {dem.shape}, elev {np.nanmin(dem):.0f}–{np.nanmax(dem):.0f} m")
    cands, stats = detect(dem, transform)
    print(f"  {len(cands)} ranked candidates after floodplain + shape filters")
    known = json.loads((ROOT / "known_sites.json").read_text())
    # validation: distance from each known mound-type site to nearest candidate
    validation = []
    for k in known:
        if cands:
            d = min(math.hypot(c["lat"] - k["lat"], c["lon"] - k["lon"]) for c in cands)
            validation.append(dict(site=k["id"], type=k["type"],
                                   nearest_candidate_km=round(d * 111, 2)))
    CHIPS.mkdir(parents=True, exist_ok=True)
    top = cands[:args.top]
    for i, c in enumerate(top, 1):
        c["rank"] = i
        c["satellite_chip"] = chip(c["lat"], c["lon"], CHIPS / f"cand-{i:02d}-sat.jpg")
        hs = hillshade_chip(dem, transform, c["lat"], c["lon"], CHIPS / f"cand-{i:02d}-hillshade.png")
        if hs:
            c["hillshade_chip"] = hs
        print(f"  #{i} {c['lat']},{c['lon']} score {c['score']} — chipped")
    for k in known:
        chip(k["lat"], k["lon"], CHIPS / f"known-{k['id']}-sat.jpg")
    report = dict(tool="Mound Hunter v0", aoi=AOI, runtime_s=round(time.time() - t0, 1),
                  dem="Copernicus DEM GLO-30 (AWS Open Data)", stats=stats,
                  known_sites=known, validation_nearest_candidate=validation,
                  candidates=top,
                  limits=["30 m DEM: blind below ~40 m wide / ~2 m high mounds",
                          "Bagh Caves are cliff caves — not a mound target",
                          "Candidates are places to look, not discovery claims"])
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    rp = OUT / f"run-{stamp}.json"
    rp.write_text(json.dumps(report, indent=2))
    print(f"Report: {rp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Town-sweep point inspector (Mound Hunter).

Given named points (label, lat, lon), for each:
  - Esri World Imagery chips at z16 (tight, ~1.2 km across) and z14
    (context, ~4.8 km across), centre-marked, saved to
    outputs/town-sweep/.
  - Copernicus GLO-30 stats from local tiles (fetched account-free
    from AWS Open Data when missing): elevation at point, relief at
    point (DEM - gaussian ~450 m, same recipe as v0/v1), max relief
    and max elevation within 300 m and within 1.5 km, ruggedness.

DEM relief is SUPPORTING evidence only — the detector that uses it
is unvalidated (v1 calibration 0/2). A point is a place to look,
never a discovery claim.

Usage: town_sweep_inspect.py points.json
points.json: [{"label": "ujjain-vaishya-tekri", "lat": .., "lon": ..}, ...]
Writes outputs/town-sweep/inspect-<label>.json per point (chips named
<label>-sat-z16.jpg / <label>-sat-z14.jpg) and prints a summary table.
"""
import json, math, sys
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "outputs" / "town-sweep"
DEM_URL = ("https://copernicus-dem-30m.s3.amazonaws.com/"
           "Copernicus_DSM_COG_10_{tile}_DEM/Copernicus_DSM_COG_10_{tile}_DEM.tif")
ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"


def fetch_dem_tile(lat, lon):
    tile = f"N{int(math.floor(lat)):02d}_00_E{int(math.floor(lon)):03d}_00"
    p = DATA / f"{tile}.tif"
    if p.exists() and p.stat().st_size > 1_000_000:
        return p
    url = DEM_URL.format(tile=tile)
    print(f"  fetching DEM {tile} ...", flush=True)
    r = requests.get(url, timeout=600)
    r.raise_for_status()
    p.write_bytes(r.content)
    return p


def lonlat_to_tile(lon, lat, z):
    n = 2 ** z
    x = int((lon + 180) / 360 * n)
    y = int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)
    return x, y


def chip(lat, lon, path, z, grid=5):
    x0, y0 = lonlat_to_tile(lon, lat, z)
    img = Image.new("RGB", (256 * grid, 256 * grid))
    half = grid // 2
    ok = 0
    for dx in range(-half, half + 1):
        for dy in range(-half, half + 1):
            try:
                r = requests.get(ESRI.format(z=z, x=x0 + dx, y=y0 + dy), timeout=30,
                                 headers={"User-Agent": "MoundHunter/town-sweep research"})
                if r.ok:
                    from io import BytesIO
                    t = Image.open(BytesIO(r.content)).convert("RGB")
                    img.paste(t, ((dx + half) * 256, (dy + half) * 256))
                    ok += 1
            except Exception:
                pass
    d = ImageDraw.Draw(img)
    c = 256 * grid // 2
    d.ellipse([c - 30, c - 30, c + 30, c + 30], outline=(255, 60, 60), width=4)
    d.line([c - 48, c, c + 48, c], fill=(255, 60, 60), width=3)
    d.line([c, c - 48, c, c + 48], fill=(255, 60, 60), width=3)
    img.save(path, quality=88)
    return dict(file=path.name, tiles_ok=ok, tiles_total=grid * grid)


def dem_stats(lat, lon):
    import rasterio
    p = fetch_dem_tile(lat, lon)
    with rasterio.open(p) as src:
        dem = src.read(1).astype(np.float32)
        tr = src.transform
    dem[dem < -1000] = np.nan
    inv = ~tr
    cx, cy = inv * (lon, lat)
    cx, cy = int(cx), int(cy)
    half = 60  # ~1.8 km window at 30 m posting
    sub = dem[max(0, cy - half):cy + half + 1, max(0, cx - half):cx + half + 1]
    ly, lx = cy - max(0, cy - half), cx - max(0, cx - half)
    filled = np.where(np.isnan(sub), np.nanmedian(sub), sub)
    smooth = ndimage.gaussian_filter(filled, sigma=15)  # ~450 m, v0/v1 recipe
    relief = filled - smooth
    m = ndimage.uniform_filter(filled, size=15)
    m2 = ndimage.uniform_filter(filled * filled, size=15)
    rugged = np.sqrt(np.maximum(m2 - m * m, 0))
    yy, xx = np.mgrid[0:sub.shape[0], 0:sub.shape[1]]
    dist_m = np.hypot(xx - lx, yy - ly) * 30.0

    def stats(r_m):
        sel = dist_m <= r_m
        return dict(max_relief_m=round(float(np.nanmax(relief[sel])), 1),
                    max_elev_m=round(float(np.nanmax(filled[sel])), 1))
    return dict(tile=p.name,
                elev_m=round(float(filled[ly, lx]), 1),
                relief_m=round(float(relief[ly, lx]), 1),
                ruggedness_m=round(float(rugged[ly, lx]), 1),
                within_300m=stats(300), within_1500m=stats(1500))


def main():
    pts = json.loads(Path(sys.argv[1]).read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for pt in pts:
        label, lat, lon = pt["label"], float(pt["lat"]), float(pt["lon"])
        print(f"{label} ({lat}, {lon})", flush=True)
        rec = dict(label=label, lat=lat, lon=lon)
        rec["chip_z16"] = chip(lat, lon, OUT / f"{label}-sat-z16.jpg", z=16)
        rec["chip_z14"] = chip(lat, lon, OUT / f"{label}-sat-z14.jpg", z=14)
        try:
            rec["dem"] = dem_stats(lat, lon)
        except Exception as e:
            rec["dem"] = dict(error=str(e))
        (OUT / f"inspect-{label}.json").write_text(json.dumps(rec, indent=2))
        d = rec["dem"]
        rows.append(f"{label:34s} elev={d.get('elev_m')} relief={d.get('relief_m')} "
                      f"maxRelief300={d.get('within_300m', {}).get('max_relief_m')} "
                      f"maxRelief1500={d.get('within_1500m', {}).get('max_relief_m')}")
    print("\n".join(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())

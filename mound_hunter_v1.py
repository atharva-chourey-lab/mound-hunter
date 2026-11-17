#!/usr/bin/env python3
"""
Mound Hunter v1 — two-terrain-class re-run + Sanchi-cluster calibration.

Standing instruction (user, 2026-11-17): this project proceeds
autonomously. No step waits on the user; gated routes are worked
around or recorded as dead ends. Open data only, no accounts.

What changed vs v0 (and why):
  1. CALIBRATION FIRST. v0 was never tested on a real standing mound
     landscape. v1 runs the detector at Satdhara (large ruinous brick
     tope, ~33 m dia, ~9–13 m high, hilltop) and Murelkhurd (low-relief
     ruined mounds on a fortified hilltop), Sanchi cluster, on GLO-30
     tiles fetched the same account-free AWS route as v0.
  2. TWO TERRAIN CLASSES. v0 searched floodplain only (smoothed elev
     < 260 m AND local ruggedness < 8 m). Diskalkar (1949) puts Itbardi
     on a rocky hillock — terrain v0 excluded by design (at the derived
     centre ruggedness = 9.2, just over v0's cut). v1 runs BOTH classes:
       floodplain = (smooth < 260) & (rugged < 8)     [v0, unchanged]
       hillock    = NOT floodplain                    [new]
     Bump definition is otherwise v0's: relief (= DEM − gaussian
     ~450 m) in 2.5–15 m, equivalent diameter 40–280 m, bbox
     circularity >= 0.45.
  3. ITBARDI BOX EXAMINED SPECIFICALLY. The Diskalkar-derived centre
     (22.090 N, 75.617 E, ±1.5 km — text-derived, NOT surveyed) gets a
     dedicated pass: every bump component of either class touching the
     box is listed, plus a finer-scale (gaussian ~150 m) relief pass,
     because the described tableland is ~90 m long — invisible at
     v0's 450 m smoothing scale.

Known limits (unchanged, stated in every report):
  - 30 m DEM: a 33 m-wide tope is ~1 pixel. Calibration tests whether
    the SITE (hillock/tableland + mound together) registers, not
    whether the tope alone is resolved.
  - Hillock class includes natural spurs/edges by construction; expect
    false positives. A candidate is a place to LOOK, never a claim.
"""
import json, math, sys, time
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mound_hunter import AOI, CHIPS, OUT, chip, fetch_dem, hillshade_chip, load_mosaic

PX_M = 30.0
ITBARDI = dict(lat=22.090, lon=75.617, radius_km=1.5)
CALI_AOI = dict(lat_min=23.38, lat_max=23.53, lon_min=77.58, lon_max=77.95)
CALI_SITES = [
    dict(id="satdhara", lat=23.48694, lon=77.65139,
         name="Satdhara — main tope",
         expect="Large ruinous brick mound ~32.8 m dia, ~9–13.65 m high on a riverside hillock. Primary calibration target."),
    dict(id="murelkhurd", lat=23.43139, lon=77.84194,
         name="Murelkhurd (Bhojpur stupas)",
         expect="~30 ruined stupas, mostly low mounds / stone circles on a fortified hilltop. Low-relief calibration target."),
    dict(id="sanchi", lat=23.4792, lon=77.7397,
         name="Sanchi — Great Stupa (context point)",
         expect="Restored standing monument on a ~91 m hill; relief here is the hill's, not a mound's. Context only."),
    dict(id="sonari", lat=23.43222, lon=77.66417,
         name="Sonari (context point)",
         expect="Standing domes on a hilltop. Context only."),
    dict(id="andher", lat=23.41111, lon=77.90722,
         name="Andher (context point)",
         expect="Three stupas on a steep hilltop. Context only."),
]


def compute_fields(dem):
    filled = np.where(np.isnan(dem), np.nanmedian(dem), dem)
    smooth = ndimage.gaussian_filter(filled, sigma=15)            # ~450 m
    relief = filled - smooth
    m = ndimage.uniform_filter(filled, size=15)
    m2 = ndimage.uniform_filter(filled * filled, size=15)
    rugged = np.sqrt(np.maximum(m2 - m * m, 0))
    floodplain = (smooth < 260) & (rugged < 8)
    hillock = ~floodplain
    return filled, smooth, relief, rugged, floodplain, hillock


def dist_km(lat1, lon1, lat2, lon2):
    return math.hypot((lat2 - lat1) * 110.7, (lon2 - lon1) * 102.4)


def label_bumps(relief, terrain_mask, lo=2.5, hi=15.0):
    mask = terrain_mask & (relief >= lo) & (relief <= hi)
    lab, n = ndimage.label(mask)
    return lab, ndimage.find_objects(lab), n


def comp_record(lab, sl, i, relief, transform, terrain_name):
    comp = lab[sl] == i
    area_px = int(comp.sum())
    diam = 2 * math.sqrt(area_px * PX_M * PX_M / math.pi)
    h, w = comp.shape
    circ = min(h, w) / max(h, w)
    peak = float(relief[sl][comp].max())
    mean_r = float(relief[sl][comp].mean())
    cy, cx = ndimage.center_of_mass(comp)
    gy, gx = sl[0].start + cy, sl[1].start + cx
    lon, lat = transform * (gx, gy)
    passes = (40 <= diam <= 280) and circ >= 0.45 and area_px >= 2
    size_score = 1.0 - min(1.0, abs(diam - 110) / 170)
    score = round(0.45 * min(1.0, peak / 8) + 0.30 * circ + 0.25 * size_score, 3)
    return dict(lat=round(float(lat), 5), lon=round(float(lon), 5),
                diameter_m=round(diam), peak_relief_m=round(peak, 1),
                mean_relief_m=round(mean_r, 1), circularity=round(float(circ), 2),
                area_px=area_px, terrain_class=terrain_name, passes_shape=bool(passes),
                score=score if passes else None)


def ranked(cands, cap=60):
    ok = [c for c in cands if c["passes_shape"]]
    ok.sort(key=lambda c: -c["score"])
    kept = []
    for c in ok:
        if all(dist_km(c["lat"], c["lon"], k["lat"], k["lon"]) > 0.25 for k in kept):
            kept.append(c)
        if len(kept) >= cap:
            break
    return kept


def point_check(lat, lon, transform, filled, smooth, relief, rugged,
                floodplain, hillock, labs):
    """What does the detector see at one known point?"""
    inv = ~transform
    cx, cy = inv * (lon, lat)
    cx, cy = int(cx), int(cy)

    def mx(arr, r):
        sub = arr[max(0, cy - r):cy + r + 1, max(0, cx - r):cx + r + 1]
        return round(float(np.nanmax(sub)), 2)

    out = dict(lat=lat, lon=lon, elev_m=round(float(filled[cy, cx]), 1),
               smooth_m=round(float(smooth[cy, cx]), 1),
               rugged_m=round(float(rugged[cy, cx]), 1),
               relief_at_point_m=round(float(relief[cy, cx]), 2),
               max_relief_150m_m=mx(relief, 5), max_relief_300m_m=mx(relief, 10),
               terrain_at_point=("floodplain" if floodplain[cy, cx] else "hillock"))
    for cls, (lab, recs) in labs.items():
        lv = int(lab[cy, cx])
        containing = None
        if lv > 0:
            containing = next((r for r in recs if r["_label"] == lv), None)
        near = None
        for r in recs:
            if r["passes_shape"]:
                d = dist_km(lat, lon, r["lat"], r["lon"])
                if near is None or d < near["dist_km"]:
                    near = dict(dist_km=round(d, 2), lat=r["lat"], lon=r["lon"],
                                diameter_m=r["diameter_m"], peak_relief_m=r["peak_relief_m"],
                                score=r["score"])
        out[f"{cls}_component_at_point"] = (
            None if containing is None else
            {k: containing[k] for k in ("diameter_m", "peak_relief_m", "circularity", "passes_shape")})
        out[f"{cls}_nearest_passing_km"] = near
    return out


def build_class(relief, terrain_mask, transform, name):
    lab, objs, n = label_bumps(relief, terrain_mask)
    recs = []
    for i, sl in enumerate(objs, start=1):
        if sl is None:
            continue
        r = comp_record(lab, sl, i, relief, transform, name)
        r["_label"] = i
        recs.append(r)
    return lab, recs, n


def main():
    t0 = time.time()
    report = dict(tool="Mound Hunter v1", started=time.strftime("%Y-%m-%d %H:%M:%S"),
                  method="v0 bump definition run on two terrain classes (floodplain = v0 mask; "
                         "hillock = its complement) + Sanchi calibration + Itbardi-box passes")

    # ---------- 1. Calibration: Sanchi cluster ----------
    print("== Calibration: Sanchi cluster ==", flush=True)
    dem_s, tr_s = load_mosaic(CALI_AOI)
    f_s, s_s, r_s, g_s, fp_s, hk_s = compute_fields(dem_s)
    lab_fp_s, rec_fp_s, n_fp_s = build_class(r_s, fp_s, tr_s, "floodplain")
    lab_hk_s, rec_hk_s, n_hk_s = build_class(r_s, hk_s, tr_s, "hillock")
    labs_s = {"floodplain": (lab_fp_s, rec_fp_s), "hillock": (lab_hk_s, rec_hk_s)}
    cali = []
    for site in CALI_SITES:
        chk = point_check(site["lat"], site["lon"], tr_s, f_s, s_s, r_s, g_s,
                          fp_s, hk_s, labs_s)
        chk.update(id=site["id"], name=site["name"], expect=site["expect"])
        # verdict for the two named calibration targets
        if site["id"] in ("satdhara", "murelkhurd"):
            det = []
            for cls in ("floodplain", "hillock"):
                cont = chk[f"{cls}_component_at_point"]
                near = chk[f"{cls}_nearest_passing_km"]
                if cont and cont["passes_shape"]:
                    det.append(f"{cls}: point inside a passing bump component "
                               f"(Ø {cont['diameter_m']} m, peak +{cont['peak_relief_m']} m)")
                elif near and near["dist_km"] <= 0.30:
                    det.append(f"{cls}: passing candidate {near['dist_km']} km away "
                               f"(Ø {near['diameter_m']} m, peak +{near['peak_relief_m']} m)")
            chk["verdict"] = ("DETECTED — " + "; ".join(det)) if det else \
                "MISS — no passing bump component at the point or within 0.30 km in either class"
        cali.append(chk)
        print(f"  {site['id']}: relief@pt {chk['relief_at_point_m']:+.2f} m, "
              f"terrain {chk['terrain_at_point']}, {chk.get('verdict', 'context')}", flush=True)
    report["calibration"] = dict(aoi=CALI_AOI, dem="Copernicus DEM GLO-30 tile N23_00_E077_00",
                                 components=dict(floodplain_raw=n_fp_s, hillock_raw=n_hk_s),
                                 sites=cali)
    CHIPS.mkdir(parents=True, exist_ok=True)
    for site in CALI_SITES[:2]:
        chip(site["lat"], site["lon"], CHIPS / f"v1-cali-{site['id']}-sat.jpg")
        hillshade_chip(dem_s, tr_s, site["lat"], site["lon"],
                       CHIPS / f"v1-cali-{site['id']}-hillshade.png")

    # ---------- 2. Corridor two-class re-run ----------
    print("== Corridor two-class re-run ==", flush=True)
    dem, tr = load_mosaic(AOI)
    f, s, r, g, fp, hk = compute_fields(dem)
    lab_fp, rec_fp, n_fp = build_class(r, fp, tr, "floodplain")
    lab_hk, rec_hk, n_hk = build_class(r, hk, tr, "hillock")
    rank_fp = ranked(rec_fp)
    rank_hk = ranked(rec_hk)
    print(f"  floodplain: {n_fp} raw components, {len(rank_fp)} ranked candidates", flush=True)
    print(f"  hillock:    {n_hk} raw components, {len(rank_hk)} ranked candidates", flush=True)
    for c in rank_fp:
        c["why"] = (f"DEM bump +{c['peak_relief_m']} m, ~{c['diameter_m']} m across, "
                    f"circularity {c['circularity']}, floodplain class (v0 terrain)")
    for c in rank_hk:
        c["why"] = (f"DEM bump +{c['peak_relief_m']} m, ~{c['diameter_m']} m across, "
                    f"circularity {c['circularity']}, hillock/tableland class (new in v1) — "
                    f"natural rises are expected in this class")
    report["corridor"] = dict(aoi=AOI,
                              components=dict(floodplain_raw=n_fp, hillock_raw=n_hk),
                              floodplain_candidates=rank_fp, hillock_candidates=rank_hk)

    # ---------- 3. Itbardi box ----------
    print("== Itbardi box ==", flush=True)
    labs = {"floodplain": (lab_fp, rec_fp), "hillock": (lab_hk, rec_hk)}
    centre = point_check(ITBARDI["lat"], ITBARDI["lon"], tr, f, s, r, g, fp, hk, labs)
    report["itbardi_box"] = dict(centre=ITBARDI, centre_check=centre,
                                 note="Centre is text-derived from Diskalkar 1949 (~3 miles S of "
                                      "Kasrawad), NOT a surveyed site location.")
    # every component (either class) whose centroid falls in the box
    in_box = []
    for cls, recs in (("floodplain", rec_fp), ("hillock", rec_hk)):
        for rec in recs:
            d = dist_km(ITBARDI["lat"], ITBARDI["lon"], rec["lat"], rec["lon"])
            if d <= ITBARDI["radius_km"]:
                rr = {k: rec[k] for k in ("lat", "lon", "diameter_m", "peak_relief_m",
                                          "mean_relief_m", "circularity", "terrain_class",
                                          "passes_shape", "score")}
                rr["dist_from_centre_km"] = round(d, 2)
                in_box.append(rr)
    in_box.sort(key=lambda c: -(c["score"] or 0))
    report["itbardi_box"]["components_in_box_450m"] = in_box
    print(f"  components with centroid in box (450 m scale): {len(in_box)}", flush=True)

    # finer pass: ~150 m smoothing, no terrain mask (the box IS the hillock)
    relief150 = f - ndimage.gaussian_filter(f, sigma=5)
    inv = ~tr
    cx, cy = inv * (ITBARDI["lon"], ITBARDI["lat"])
    cx, cy = int(cx), int(cy)
    w = int(ITBARDI["radius_km"] * 1000 / PX_M)
    sub = relief150[cy - w:cy + w + 1, cx - w:cx + w + 1]
    lab150, objs150, n150 = label_bumps(sub, np.ones_like(sub, dtype=bool), lo=2.0, hi=12.0)
    box150 = []
    for i, sl in enumerate(objs150, start=1):
        if sl is None:
            continue
        # rebuild a record in sub-array coordinates, then map to lon/lat
        comp = lab150[sl] == i
        area_px = int(comp.sum())
        diam = 2 * math.sqrt(area_px * PX_M * PX_M / math.pi)
        if not (30 <= diam <= 450):
            continue
        hh, ww = comp.shape
        circ = min(hh, ww) / max(hh, ww)
        peak = float(sub[sl][comp].max())
        cyy, cxx = ndimage.center_of_mass(comp)
        gy, gx = (cy - w) + sl[0].start + cyy, (cx - w) + sl[1].start + cxx
        lon, lat = tr * (gx, gy)
        box150.append(dict(lat=round(float(lat), 5), lon=round(float(lon), 5),
                           diameter_m=round(diam), peak_relief_m=round(peak, 1),
                           circularity=round(float(circ), 2),
                           dist_from_centre_km=round(dist_km(ITBARDI["lat"], ITBARDI["lon"],
                                                             float(lat), float(lon)), 2),
                           scale="150m"))
    box150.sort(key=lambda c: -c["peak_relief_m"])
    report["itbardi_box"]["components_in_box_150m"] = box150[:15]
    report["itbardi_box"]["components_in_box_150m_total"] = len(box150)
    print(f"  components in box (150 m scale, Ø30–450 m): {len(box150)}", flush=True)

    # chips: centre + top box candidates from both scales
    chip(ITBARDI["lat"], ITBARDI["lon"], CHIPS / "v1-itbardi-centre-sat.jpg")
    hillshade_chip(dem, tr, ITBARDI["lat"], ITBARDI["lon"], CHIPS / "v1-itbardi-centre-hillshade.png")
    chip_targets = [c for c in in_box if c["passes_shape"]][:2] + box150[:2]
    seen = set()
    for j, c in enumerate(chip_targets, 1):
        key = (round(c["lat"], 3), round(c["lon"], 3))
        if key in seen:
            continue
        seen.add(key)
        c["satellite_chip"] = chip(c["lat"], c["lon"], CHIPS / f"v1-itbardi-cand-{j:02d}-sat.jpg")
        hs = hillshade_chip(dem, tr, c["lat"], c["lon"], CHIPS / f"v1-itbardi-cand-{j:02d}-hillshade.png")
        if hs:
            c["hillshade_chip"] = hs
    # chips for top corridor hillock candidates
    for j, c in enumerate(rank_hk[:5], 1):
        c["rank"] = j
        c["satellite_chip"] = chip(c["lat"], c["lon"], CHIPS / f"v1-hillock-{j:02d}-sat.jpg")
        hs = hillshade_chip(dem, tr, c["lat"], c["lon"], CHIPS / f"v1-hillock-{j:02d}-hillshade.png")
        if hs:
            c["hillshade_chip"] = hs
    for j, c in enumerate(rank_fp[:5], 1):
        c["rank"] = j

    for recs in (rec_fp, rec_hk, rec_fp_s, rec_hk_s):
        for r in recs:
            r.pop("_label", None)
    report["runtime_s"] = round(time.time() - t0, 1)
    report["limits"] = [
        "30 m DEM: blind below ~40 m wide / ~2 m high mounds; a 33 m tope is ~1 px",
        "Hillock class includes natural spurs and edges by construction — false positives expected",
        "Itbardi centre is text-derived (Diskalkar 1949), ±1.5 km, not surveyed",
        "Candidates are places to look, not discovery claims"]
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    rp = OUT / f"run-v1-{stamp}.json"
    rp.write_text(json.dumps(report, indent=2))
    print(f"Report: {rp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

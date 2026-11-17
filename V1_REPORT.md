# Mound Hunter v1 — Report

Run 2026-11-17 · `mound_hunter_v1.py` · full machine output:
`outputs/run-v1-20261117-084723.json` (v0's run JSON sits alongside it).
Standing instruction applied throughout: proceed autonomously, open
data only, no accounts, no purchases — gated routes are recorded, not
waited on. **Candidates are places to look, never discovery claims.**

## What v1 changed vs v0

1. **Calibration first** — the detector was run at two known mound
   sites (Satdhara, Murelkhurd) before being trusted anywhere else.
2. **Two terrain classes** — v0's floodplain-only mask (smoothed elev
   < 260 m AND ruggedness < 8 m) is now one of two classes; the new
   **hillock class** is its complement. The bump definition is
   otherwise v0's, unchanged: relief (DEM − gaussian ~450 m) in
   2.5–15 m, equivalent diameter 40–280 m, circularity ≥ 0.45.
3. **The Itbardi box examined specifically** — Diskalkar's (1949)
   textual fix, derived centre 22.090°N, 75.617°E ± 1.5 km
   (text-derived, NOT surveyed), at both 450 m and 150 m relief scales.
4. **FABDEM box examination** and a **CORONA enumeration attempt**
   (outcomes in §5–§6).

## 1. Calibration — Satdhara & Murelkhurd: 0 / 2 re-found

DEM: Copernicus GLO-30 tile N23_00_E077_00, fetched account-free from
AWS Open Data (the v0 route). Both sites are hillock-class terrain.

| Site | Elev | Relief at point | What the detector did | Verdict |
|---|---|---|---|---|
| **Satdhara** (23.48694, 77.65139) | 462 m | **+11.25 m** (inside the bump band) | Point sits inside a hillock-class raw component of **Ø 935 m** — the whole hilltop — which fails the Ø ≤ 280 m shape filter. Nearest passing candidate 0.55 km away (Ø 48 m, +13.1 m). | **MISS** |
| **Murelkhurd** (23.43139, 77.84194) | 478 m | **+15.69 m** (above the band) | Point relief exceeds the 2.5–15 m bump band, so the point pixel is not in the mask at all; no component at the point in either class. Nearest passing candidate 1.67 km away. | **MISS** |

Context points behaved as expected: Sanchi relief at point +59.2 m
and Andher +82.4 m (the hills themselves), Sonari +4.9 m inside a
Ø 2,539 m hilltop component. The Satdhara satellite chip shows a
scrub-covered hilltop above the Halali river — no mound is resolvable
in modern imagery at chip scale either.

**Mechanisms, stated plainly.** This is not "no signal": both
calibration points carry strong positive relief. The failures are
structural — (a) at 450 m smoothing a hilltop tope's relief merges
into its hilltop, so the labelled unit is the hill, not the mound
(Satdhara); (b) the floodplain-tuned 15 m band cap excludes
strong-relief hilltop ground outright (Murelkhurd). A 33 m-wide tope
is ~1 pixel at 30 m posting; the v0 bump recipe cannot isolate
hilltop stupas at this resolution, in either terrain class. **The
detector remains unvalidated — now with a measured calibration
failure instead of an assumed one.**

## 2. Corridor two-class re-run

- **Floodplain class** reproduces v0: 14,154 raw components → 60
  ranked candidates; the #1 candidate is identical to v0's
  (22.25292, 75.62145, Ø 112 m, +11.0 m) — the two-class code did not
  disturb v0's own class.
- **Hillock class**: 16,708 raw components → 60 ranked candidates.
  The class mechanically works — it now searches the terrain v0
  excluded — but its top scores saturate at 0.997 on Ø 112 m,
  circularity-1.00 ridge-edge circles, the same non-discrimination
  v0 showed on the floodplain. These are almost certainly natural
  rises; the score does not separate them from anything.

## 3. The Itbardi box (centre 22.090°N, 75.617°E, radius 1.5 km)

Centre check (GLO-30): elevation 215.8 m, relief at point **+9.48 m**,
ruggedness 9.2 — hillock class, as Diskalkar describes. The centre
pixel sits inside an elongated Ø 439 m hillock component (the
hillock mass itself; fails shape). Modern imagery at the centre:
open rocky scrub tableland, farmland to the south, no habitation
close — terrain-consistent with the 1949 description.

**450 m-scale components with centroids in the box: 37** (10+ pass
the shape filters). The passing family, nearest first:

| # | Coordinates | Class | Ø | Peak relief | Circ. | Dist. from centre | Chip reading |
|---|---|---|---|---|---|---|---|
| 1 | 22.08686, 75.61797 | hillock | 112 m | +7.1 m | 0.57 | 0.36 km | NE-cluster scene (below) |
| 2 | 22.08728, 75.61421 | floodplain | 232 m | +7.7 m | 0.89 | 0.42 km | Open tableland W of centre (cand-06) |
| 3 | 22.09204, 75.62101 | hillock | 90 m | **+14.6 m** | 0.60 | 0.47 km | NE-cluster scene (cand-05) |
| 4 | 22.09423, 75.62069 | hillock | 127 m | +14.2 m | 0.62 | 0.60 km | NE-cluster scene (cand-02) |
| 5 | 22.08858, 75.62386 | hillock | 76 m | +13.7 m | 0.50 | 0.72 km | — |
| 6 | 22.09653, 75.60494 | floodplain | 112 m | +9.4 m | 0.60 | 1.43 km | Farmland; a large pale rocky tableland patch is visible NE of the point (cand-01) |

**150 m-scale pass: 60 components** (Ø 30–450 m) in the box. Top by
relief: a Ø 59 m, circularity-1.00, +11.8 m bump at 22.09329,
75.62134 (0.57 km, NE cluster) and the tableland-scale feature
itself — Ø 412 m, elongated, +11.8 m, centred 0.35 km from the
derived centre.

**Chip caveat + reading.** v0's chip() snaps to a z16 tile window, so
points within ~300 m share one image: candidates #1, #3, #4 (and the
top 150 m bump) all fall in a single scene — **a village edge on the
highway at the NE foot of the hillock**. That cluster, including the
highest-relief passing bump in the box (+14.6 m), sits on disturbed
settlement-edge ground and is weak for exactly that reason. The
candidates on the open tableland west/southwest of the centre (#2,
#6) match Diskalkar's terrain but are indistinguishable in DEM from
natural rocky knolls — and §1 is the reason no stronger language is
available: this detector could not isolate a *known* tope at
Satdhara, so a bump of the right size and relief near Itbardi is a
place to look in CORONA, not evidence of anything.

## 4. FABDEM — obtained; changes nothing at Itbardi

The canonical Bristol host (data.bris.ac.uk) was unreachable from
this network (4 attempts, connection dropped — the flakiness the
scouting note flagged). Worked around account-free via the
Fondazione LINKS COG mirror of FABDEM V1-2 on Hugging Face
(`links-ads/fabdem` bucket, no authentication): tile
`N22E075_FABDEM_V1-2.tif` (30.5 MB) saved to `data/`. Licence:
CC BY-NC-SA 4.0 — non-commercial research use.

Box examination repeated on FABDEM: centre elevation 215.4 m,
relief at point +9.26 m, max relief within 300 m +34.84 m — within
0.2–0.4 m of GLO-30 on every measure; 45 box components at the
150 m scale (vs 60); the same tableland-scale component ~0.36 km
from the centre. **Verdict: bare-earth cleaning is a null at this
site** — bare rocky scrub has no canopy/building bias to remove,
and both DEMs share the GLO-30 base. DEM-side improvement for
Itbardi is exhausted at 30 m.

## 5. CORONA — not enumerated (account gate, recorded)

Probes run: USGS M2M API scene-search (DECLASS_1, corridor bbox)
without credentials → `UNAUTHORIZED_USER`; EarthExplorer bulk host
answers but serves only a JS shell with no static metadata index;
ScienceBase and data.gov catalog APIs returned nothing usable; the
CAST atlas remains Near-East only. **Every enumeration route runs
through the free USGS EarthExplorer account.** Recorded in one line
per the standing instruction and proceeded without: the frame
inventory over the corridor (and over Satdhara, for calibration at
1.8 m) is the first task whenever that account exists. CORONA is an
enhancement, not a gate — but it is also, after this run, plainly
the decisive instrument: it is the only identified source that can
separate a ruined brick tope from a rocky knoll.

## 6. Overall verdict

- **Calibration: FAILED (0/2), informatively.** Satdhara and
  Murelkhurd diagnose exactly why: hilltop stupas merge into their
  hilltops at 450 m smoothing, and strong-relief ground breaks the
  floodplain band cap. The relief *signal* exists at both sites;
  the v0 *segmentation recipe* cannot isolate it at 30 m.
- **The Itbardi search is nonetheless transformed vs v0.** v0
  validated at the wrong point with the target terrain excluded.
  v1 has the right box (two DEMs agree on it), a ranked candidate
  family inside it, chip readings that kill the NE cluster's
  credibility and leave the open-tableland candidates standing as
  look-places — and a calibration result that forbids calling any
  of them more than that.
- **What would actually move this forward, in order:** (1) CORONA
  KH-4B frames over the Itbardi box and Satdhara — re-run
  calibration at 1.8 m, where a 33 m tope is ~18 pixels, and only
  then scan the box; (2) a hilltop-specific DEM recipe (small-scale
  smoothing + local prominence) if DEM work continues — v1 shows
  the floodplain recipe's limits, it does not fix them; (3) the
  TanDEM-X 12 m proposal as a slow lottery ticket (scouting §3).
- Mound Hunter after v1 is what it was after v0 — **a triage tool,
  not a validated detector** — but its triage is now aimed at the
  right hillock, with its failure modes measured rather than
  assumed.

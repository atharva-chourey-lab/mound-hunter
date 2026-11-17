# Mound Hunter

**Goldmine Hunter's geographic twin: a tool for hunting a comparable set of
vanished archaeological mounds — circular low mounds on a river plain — using
only open elevation and imagery data, verified against known sites first.**

Study corridor: Kasrawad–Maheshwar–Anjad–Bagh, Madhya Pradesh (Narmada and
Baghni valleys), lat 22.00–22.45, lon 74.65–75.75.

## What is here

- `mound_hunter.py` — v0: DEM-based candidate detection over the corridor.
- `mound_hunter_v1.py` — v1: the revised detector that produced the surviving
  candidates (cleanest: Sujawa; also Samantukhera, Itbardi, and Bagh's brick
  foundations — see `V1_REPORT.md`). Vaishya Tekri scored as junk and is closed.
- `town_sweep_inspect.py` — the town-sweep verification pass (`TOWN_SWEEP.md`).
- `known_sites.json` — the known-site control set every detector version is
  validated against before its candidates are believed.
- `PUBLIC_DOMAIN_SWEEP.md` — the prior-art / public-domain sweep for the
  method and the corridor.

## How to run

```bash
python3 mound_hunter_v1.py   # needs numpy and rasterio/GDAL — see imports
```

## Data — not redistributed

The elevation tiles (Copernicus DEM GLO-30 / FABDEM, ~270 MB of GeoTIFF) and
the satellite verification chips (Esri World Imagery) are **not** in this
repository: both are open data, fetched from AWS Open Data and Esri's tile
service respectively — the scripts name the exact tiles. No API keys are
required; an earlier probe of the USGS M2M API without credentials is recorded
in `V1_REPORT.md` as a negative result.

## Status

Working research tool (v0 and v1 both preserved, so the method's revision is
auditable). Candidate lists are hypotheses for field verification, not
confirmed sites.

## Authorship and licence

**Author:** Atharva Chourey, Atharva Chourey Lab (independent research lab)

The Atharva Chourey Lab is a human–AI collaboration: Atharva Chourey works with
Lapis (Muse), an AI research partner. All results are framed as the
collaboration's.

Code in this repository is released under the **MIT License** (see `LICENSE`).
The associated manuscripts are published separately under CC BY 4.0 — the code
licence and the paper licence are deliberately different.

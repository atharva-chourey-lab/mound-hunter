# Mound Hunter v1 — Input Scouting

Scouted 2026-11-17. Question: what does v1 need, and is each input actually
obtainable from open/public sources? Labels used throughout:
**[verified-obtainable]** = the thing exists and the access route was confirmed
during scouting · **[mentioned-only]** = it exists in the literature/web but the
download/coverage itself was not confirmed · **[dead end]** = checked, not there.

## Verdicts up front

| v1 need (from README) | Verdict |
|---|---|
| Exact Itbardi coordinates from the 1936–39 report | **The report exists, is free, and was read in this session — but it gives a textual fix, not lat/lon.** "About three miles south of Kasrawad," on a hillock. No published source gives coordinates for the mound. |
| CORONA 1960s imagery | **Route verified-obtainable** (USGS EarthExplorer, Declass 1; scanned frames free, unscanned $30/frame). India coverage proven by published work; the exact frame list over the corridor still needs a footprint search behind a free account. |
| Finer DEM (12 m) | **No openly downloadable DEM finer than 30 m exists for this region.** TanDEM-X 12 m is proposal-gated; ALOS PALSAR 12.5 m is a resampled posting, not true 12.5 m information. Bare-earth 30 m (FABDEM) is the realistic open upgrade. |
| Sanchi-cluster training set | **Obtainable as a labelled set** — coordinates sourced for Sanchi, Satdhara, Sonari, Murelkhurd, Andher, Saru Maru; Cunningham's 1854 measured plans are free. Caveat: these are hilltop stone stupas; see §4 before training on them. |

---

## 1. Itbardi coordinates + the 1936–39 report

### The report exists — and it is not where v0 assumed

There is no ASI report and no *Indian Archaeology – A Review* account (IAR only
begins with the 1953–54 volume, and the dig was a Holkar State museum project,
never an ASI excavation). The excavation was published as a journal article:

> **D. B. Diskalkar, "Excavations at Kasrawad," *Indian Historical Quarterly*
> 25 (1949), pp. 1–18.**

**[verified-obtainable]** — *Indian Historical Quarterly* vol. 25 is digitised
in full on the Internet Archive (Digital Library of India item 2015.99782),
and the article's first page was read during this scouting session:
https://archive.org/details/in.ernet.dli.2015.99782
(full text: https://archive.org/stream/in.ernet.dli.2015.99782/2015.99782.The-Indian-Historical-Quarterlyvol25_djvu.txt)

Later scholarship cites this article as the sole excavation publication
(e.g. Ray, *World Archaeology* 26:1, 1994, bibliography: "Diskalkar, D. B.
1949. Excavations at Kasrawad. Indian Historical Quarterly, 25:1-18"; also
Schopen 1991; the Kasrawad section of *Early Āndhradeśa*, Brill).

### What the report actually says about location (p. 1, OCR of the scan)

- "At a distance of **about three miles to the south of Kasrawad** … situated
  on the southern bank of the river Narmada, lies a site called Itbardi or
  mound of bricks."
- The site is "**a rocky uneven tableland measuring about 300 ft. in length**
  and [breadth figure garbled in the OCR — confirm from the PDF scan] in
  breadth, **situated half way on a hillock full of dwarf jungle trees**. It is
  all hilly to its south and on the other sides there is no habitation at a
  distance of less than two or three miles."
- **Eleven stupas**: "one big in the centre and ten smaller ones in the
  eastern part of the mound"; Stupa No. 1 ≈ 35 ft diameter (others 13–25 ft);
  residential blocks mainly in the western portion. All finds are 2nd c. BCE.
- It lies "only six miles on the other side of the Narmada from Maheshvar."

### The excavation history, corrected

V0's "excavated 1936–39 under V. N. Singh" conflates two phases. Both the
report (p. 1) and the Central Museum Indore guidebook agree: the site was
found and first dug in **winter 1936 by V. R. Karandikar** (Secretary,
Narmada Valley Research Board), who died a few months in; **V. N. Singh**
(Curator, Indore Museum), assisted by D. P. Gupta, continued in the **cold
seasons of 1937–39**.

Corroborating source, also free on archive.org: P. G. Paranjpe, *A Short
Guide Book to the Central Museum, Indore* (Dept. of Archaeology & Museums,
MP, 1961) — "about three miles to the south of Kasrawad Tehsil lies a site
called Itbardi or mound of bricks," with the same Karandikar → Singh sequence:
https://archive.org/stream/vwov_a-short-guide-book-to-the-central-museum-indore-by-prabhakar-govind-paranjpe-196

### So where is the mound? A derived fix, not a lookup

- **[dead end]** No published source gives lat/lon for the mound itself. The
  ASI list of Monuments of National Importance carries it only as
  **N-MP-209, "Excavated site," Kasrawad, West Nimar** — locality name, no
  coordinates (list mirrored at https://mail.jatland.com/w/index.php?title=Khargone&oldid=641854).
  Every academic mention repeats the town coordinates 22°8′N, 75°37′E
  (e.g. *Int. J. Mod. Phys. Conf. Ser.* 22 (2013) 93–98,
  https://worldscientific.com/doi/pdf/10.1142/S2010194513009963).
- **Derived search fix:** 3 miles (4.8 km) due south of the town point
  (22.1333°N, 75.6167°E) → **≈ 22.090°N, 75.617°E**, i.e. the first hillock
  belt south of the Narmada plain. Recommended v1 search box: ~1.5 km radius
  around that point, refined against the "rocky tableland ~300 ft long,
  halfway up a hillock, hilly to the south" description. These are
  text-derived coordinates, **not** surveyed ones — do not write them into
  known_sites.json as the site location.

### Design implications for v1 (important)

1. V0 checked the **town point** — the mound was never in that chip.
2. V0's floodplain mask (smoothed elevation < 260 m, low ruggedness) would
   have **excluded Itbardi's terrain class even at the right location**:
   Diskalkar describes a rocky hillock site, not a floodplain mound. The
   corridor's southern hillock belt must be in-scope for v1.
3. The target is small and subtle: a ~90 m tableland with ruined brick
   stupas, the largest ~11 m across. This is a CORONA-scale target (1.8 m
   pixels), not a 30 m DEM target — consistent with v0's null DEM result.

---

## 2. CORONA imagery

### The archive and the product

**[verified-obtainable]** USGS EROS, "Declassified Satellite Imagery – 1"
(Declass 1), served through EarthExplorer:
https://www.usgs.gov/centers/eros/science/usgs-eros-archive-declassified-data-declassified-satellite-imagery-1?qt-science_center_objects=0

- Systems: CORONA KH-1, KH-2, KH-3, KH-4, KH-4A, KH-4B (1960–1972), plus
  ARGON and LANYARD. Film held by NARA; USGS scans on demand.
- **KH-4B** (missions 1101–1112, 1114–1117; Sep 1967 – May 1972) is the one
  that matters: best ground resolution **6 ft ≈ 1.8 m**, stereo pairs, frames
  are long strips (~14 × 190 km class) — one or two frames cover the whole
  Kasrawad–Bagh corridor per pass. KH-4A (1963–69, ~2.7 m best) is the
  fallback for extra dates.
- Scans: 7 µm (3600 dpi, ~319 MB × 4 files/frame) or 14 µm TIFFs.
  **The imagery is not georeferenced** — orthorectification is part of the
  v1 workflow, as it was for the Mesopotamia CNN work.

### Cost

- Frames **already scanned: free download** (public domain) via
  EarthExplorer — a free USGS account is required to download.
- Frames **not yet scanned: $30 per frame** on-demand scanning fee (USGS
  product page, above). Nothing was purchased in this session.

### Coverage of the corridor — what is and isn't proven

- **[verified]** India coverage exists in Declass 1 and is downloadable:
  Conesa et al. orthorectified **KH-4B frames over North Gujarat** for
  archaeological survey planning (*Remote Sensing*, 2019; author page:
  https://icac.academia.edu/FrancescCConesa) — the paper doubles as a
  published GCP/orthorectification protocol for Indian conditions, where
  CORONA "has rarely been used in Indian archaeological contexts."
- **[mentioned-only]** The exact frame list over lat 22.00–22.45,
  lon 74.65–75.75. Enumerating footprints requires an EarthExplorer search
  (free account); no account was created under scouting rules. The MAHSA
  keyhole-imagery training tutorial (https://zenodo.org/records/19186343)
  warns that South Asia coverage is thinner than the Middle East's — expect
  a handful of KH-4A/KH-4B passes, not dozens. **First v1 task: run the
  footprint search and inventory missions/dates before designing anything.**
- **[dead end for this AOI]** The University of Arkansas CAST CORONA Atlas
  (pre-georeferenced scenes) covers the Near East, not India.
- **Fallback:** KH-9 HEXAGON mapping-camera imagery (Declass 3, 1973–1980,
  ~6–9 m) was flown as near-systematic global mapping coverage and is also
  on EarthExplorer — a coarser but later (and more certain) view if a KH-4B
  pass missed the corridor.

---

## 3. Finer DEM

**Headline: there is no openly downloadable DEM finer than 30 m for this
region.** Anyone budgeting v1 on open 12 m data is budgeting on air.

| Source | Posting | Access | Status |
|---|---|---|---|
| Copernicus DEM "GLO-12" | — | — | **[dead end]** No such public product. Copernicus DEM instances are EEA-10 (10 m, **Europe only**, restricted user categories), GLO-30 and GLO-90. (https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM) |
| TanDEM-X DEM | 0.4″ ≈ 12 m | DLR Science Service System — **proposal-gated**; free if a scientific proposal is accepted, service fee for proposals submitted after 7 Dec 2016; scientific use only | **[verified-obtainable, with application]** The only true 12 m route. Weeks-scale, not guaranteed. (https://tandemx-science.dlr.de/cgi-bin/wcm.pl?page=Tdm-Science-Service-System) |
| TanDEM-X 90 m | 3″ ≈ 90 m | Free with simple registration, scientific use | Obtainable but coarser than v0's data — useless for mounds. |
| ALOS PALSAR DEM (ASF) | 12.5 m posting | Free via ASF Vertex with a free NASA Earthdata account; DEM ships inside per-scene RTC bundles | **[verified-obtainable, with a caveat]** ASF's DEM is a best-source mosaic (SRTM/NED class in many areas) **resampled to 12.5 m posting** — posting ≠ true 12.5 m information content. Treat as a maybe; test it on the Itbardi hillock before trusting it. (https://search.asf.alaska.edu) |
| FABDEM | 30 m | Free download, Univ. of Bristol repository, **CC BY-NC-SA 4.0** (non-commercial) | **[verified-obtainable]** Same posting as GLO-30 but **bare-earth** — forests/buildings removed by ML (Hawker et al., *Environ. Res. Lett.* 17, 024016, 2022). For scrub-covered hillocks this cleaning may matter more than posting. DOI: 10.5523/bris.25wfy0f9ukoge2gs7a5mqpq2j7 (https://research-information.bris.ac.uk/en/datasets/fabdem-2/). One catalogue note flagged the Bristol file host as flaky — retry on failure. |
| GEDTM30 | 30 m | Open, CC-BY-4.0 (released 2025) | Another 30 m bare-earth option, ensemble of Copernicus DEM + AW3D30. |
| CartoDEM (Bhuvan/NRSC) | 1 arc-sec ≈ 30 m | Free via Bhuvan NOEDA with free login; 10 tiles/day cap | **[verified-obtainable]** India's national DEM from Cartosat-1 stereo (versions 1 → 3R1). Same posting as GLO-30 but an **independent optical-stereo source** — a second opinion/cross-check, not a resolution gain. (https://bhuvan-app1.nrsc.gov.in/2dresources/bhuvanstore.php) |
| ALOS World 3D (AW3D30) | 30 m | Free with JAXA registration | Third 30 m opinion. |

**Consequence for v1:** elevation improvement must come from (a) a TanDEM-X
12 m proposal (uncertain, slow), (b) **stereo photogrammetry from the CORONA
pairs themselves** — the published route for both Mesopotamia and the
Gujarat study — or (c) better use of 30 m data: FABDEM bare-earth +
hillshade, run at the *correct* search location (§1). Option (c) is free
today; (b) is the real v1 method; (a) is a lottery ticket worth submitting
but not planning around.

---

## 4. Sanchi-cluster training set

All coordinates below are the published site coordinates from the cited
source; treat them as site-centre points (± a few hundred metres), to be
refined against imagery in v1.

| Site | Coordinates | Source | Mound relief today? |
|---|---|---|---|
| **Sanchi** (Great Stupa complex) | 23.4792°N, 77.7397°E (ASI guidebook: 23°29′N, 77°45′E) | Wikipedia infobox; Mitra, *Sanchi* (ASI, 2001), full text: https://archive.org/stream/sanchi00mitr/sanchi00mitr_djvu.txt | **No — standing monument.** Great Stupa is restored (36.6 m dia, ~16.5 m high) atop a ~91 m hill; relief is the hill's, not a mound's. Use as a CORONA *appearance* exemplar (bright circular dome), not a mound-relief example. |
| **Satdhara** | 23.48694°N, 77.65139°E | https://en.wikipedia.org/wiki/Satdh%C4%81ra | **Yes — the cluster's best large-mound exemplar.** Cunningham (1854): main tope "a vast ruinous mound of brickwork," base 101 ft dia, 30 ft high as it stood (42 ft incl. terrace); modern figure 13.65 m high × 32.8 m dia excl. platform. ASI excavations 1993–2000 found ~40 stupas; the small ones are low mounds and stone circles (12–24 ft dia). Riverside hillock by the Halali — terrain class closest to Itbardi's description. |
| **Sonari** | 23.43222°N, 77.66417°E | https://en.wikipedia.org/wiki/Sonari_Stupas | **Standing domes.** Stupas 1–2 survive as solid hemispheric domes on cylindrical plinths on a hilltop (Stupa 1 ~15 m dia); five smaller stupas more ruined. Moderate relief, structure-like rather than mound-like. |
| **Murelkhurd** (Bhojpur Stupas) | 23.43139°N, 77.84194°E | https://en.wikipedia.org/wiki/Bhojpur_Stupas | **Yes, low relief.** ~30 stupas on a fortified hilltop, most ruined down to low mounds / stone circles — good *low-relief* exemplars. |
| **Andher** | 23.41111°N, 77.90722°E | https://en.wikipedia.org/wiki/Andher_Stupas | **Yes, partial.** Three stupas on a hilltop overlooking Murelkhurd; main stupa a substantial ruined dome, the other two smaller/ruined. |
| **Saru Maru** (Panguraria) | 22.72995°N, 77.51991°E | https://en.wikipedia.org/wiki/Saru_Maru | **Yes, but canopy-covered.** 33+ stupas across forested Vindhyan hills, mostly ruined mounds, plus caves and an Ashokan minor rock edict. ~120 km south of Sanchi — and the cluster member closest to the Narmada corridor (north bank, Budhani tehsil). |
| **Vaishya Tekri**, Ujjain (on v0's list) | **Not verified** — see note | Press/academic citations below | **Yes — the closest surviving analogue to Itbardi's original form.** A giant grassy mound, ~350 ft base × ~100 ft high (Skilling 2011, as cited in 2026 coverage), with the smaller Kumhar Tekri ~2 km away. |

Notes and caveats:

- **Vaishya Tekri coordinates: [mentioned-only].** No verified lat/lon was
  found in open sources during scouting. Sources place the twin mounds near
  Kanak Puri village, Ujjain (e.g. https://www.drishtiias.com/statepcs/18-08-2026;
  https://www.youngintach.org/heritage-alerts-sep2026). Pin it from
  imagery/maps in v1; do not hard-code a guessed point. **Also note:** fresh
  ASI/MP excavation began there in August 2026 — the modern surface is being
  actively disturbed, but its 1960s CORONA appearance (the training epoch)
  is unaffected.
- **Terrain caveat (the important one):** the Sanchi cluster is Vindhyan
  **hilltop** country — in CORONA these read as bright circular structures
  on hilltops, and several are restored/standing rather than mounds. Per
  Diskalkar, Itbardi is *also* a hillock site, so the cluster is a better
  match than v0's floodplain framing implied — but a model trained only on
  Sanchi-cluster hilltops will learn "bright circle on a hill," which is
  also what natural rises look like (v0's false-positive problem near Bagh).
  Mix in the low-relief examples (Murelkhurd's ruined circles, Satdhara's
  small topes) and keep Bagh-style natural rises as negatives.
- **Ground-truth dimensions are free:** Cunningham, *The Bhilsa Topes*
  (1854) gives measured plans/heights for Satdhara, Sonari, Andher and
  Murelkhurd (extracts at https://photodharma.net/India/Satdhara-Stupas/index.htm);
  the full text is on archive.org. Pair these with the CORONA chips instead
  of guessing label extents.
- **The ideal labelled set exists but is not verified open:** Julia Shaw's
  **Sanchi Survey Project** (1998–2005) documented ~750 km² around Sanchi —
  35 Buddhist sites, 145 settlements, including lowland settlement mounds of
  exactly Itbardi's class (Shaw, *Buddhist Landscapes in Central India*,
  2007; *World Archaeology* 45:1, 2013). A web version of the SSP database
  was planned but was not live as of a 2014 review. **[mentioned-only]** —
  worth one enquiry (UCL / Archaeology Data Service) in v1, not a dependency.

---

## Recommended v1 input stack (all free, in order)

1. **Read Diskalkar 1949 in full** (archive.org, above) + Paranjpe 1961;
   move the Itbardi search box to ≈ 22.090°N, 75.617°E ± 1.5 km and drop
   the floodplain-only mask for the corridor's southern hillock belt.
2. **EarthExplorer footprint search** (free account) for Declass 1 over the
   corridor and over the Sanchi cluster; download already-scanned KH-4B
   frames free; only if a key pass is unscanned, price the $30/frame scan
   as a decision for the user — do not assume it.
3. **FABDEM** tiles for the corridor + cluster (bare-earth 30 m) as the DEM
   layer; CartoDEM 3R1 as an independent cross-check. Submit the TanDEM-X
   12 m science proposal in parallel as a bonus, not a dependency.
4. **Training labels:** Sanchi-cluster coordinates above + Cunningham's
   dimensions; Vaishya Tekri pinned from imagery; Itbardi itself becomes a
   *validation* target only once the §1 search box is scanned in CORONA —
   if the tableland shows, v1 has its first true positive control in the
   corridor.

## Post-scout check (2026-11-17, main chat): DEM terrain at the derived centre

Ran the v0 relief method (DEM − gaussian ~450 m, Copernicus GLO-30 tile N22 E075, already on disk) at the Diskalkar-derived centre vs the v0 town point:

- **Derived centre (22.090°N, 75.617°E): elevation 215.8 m, relief at point +9.48 m**; max relief within 300 m +35.0 m; max elevation within 300 m 238.1 m. Strongest relief within 1.5 km: +47.2 m at 22.1008, 75.6086 (elev 242.2 m).
- **v0 town point (22.1333, 75.6167): elevation 169.8 m, relief −1.75 m** (reproduces the v0 validation number exactly); max relief within 300 m only +0.59 m.
- **Nearest v0 candidate to the derived centre: 9.73 km away** — v0's floodplain-masked search never effectively covered this ground.

Reading: the derived centre sits on raised rocky ground ~46 m above the town-point plain — terrain-consistent with Diskalkar's "rocky tableland halfway up a hillock." This validates the *search box* (a ~1.5 km-radius hillock area 3 miles south of town), not a mound detection: at 30 m posting the DEM cannot separate a stupa mound from the hillock it sits on. The mound-level test remains CORONA.

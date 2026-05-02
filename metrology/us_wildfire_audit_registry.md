# US Wildfire Metrological Audit Registry

CC0. Living document. Append-only -- never delete past entries.

## Purpose

Document every known measurement methodology change in US wildfire data
1850-present, so that any analysis can declare which era of measurement
its data comes from and what bias it carries.

The institutional fire record glues together at least 8 different
measurement regimes into a single time series. Trends derived from that
combined record are dominated by methodology change, not physics.

This registry is the foundation for:

1. Vectorizing each fire event into the canonical matrix
2. Building surrogate-data calibration curves for legacy records
3. Honest analysis with explicit uncertainty bounds per era

---

## Measurement Eras

### Era F1: Newspaper / inquest era (1850-1925)

- **Primary records:** local newspapers, county inquests, insurance archives
- **Spatial:** affected towns and railroads documented; rural burns invisible
- **Detection:** human report only; required population near burn
- **Acreage:** estimated from descriptions ("burned the whole valley");
  +/-50% or worse
- **Fatalities:** newspaper-documented; rural deaths often uncounted
- **Known biases:**
  - Population-density-dependent detection (cities reported, wilderness silent)
  - Sensational events (Hinckley 1894, Peshtigo 1871) over-documented;
    routine fires under-documented
  - "Property loss" in 1900 dollars, no consistent inflation adjustment
  - Casualty counts in remote areas systematically low
  - Native and rural communities massively under-represented
- **What survives reliably:** approximate location, year, that *some* fire
  occurred. Magnitude estimates carry +/-50%-100% uncertainty.
- **Notable events for surrogate calibration:**
  - Peshtigo (1871): ~1,500 deaths, 1.2-1.5 million acres
  - Hinckley (1894): 418+ deaths, 200,000+ acres
  - Yacolt Burn (1902): 65 deaths, ~1 million acres
  - Big Burn (1910): 87 deaths, ~3 million acres ID/MT
- **Source documents needed:**
  - Local newspaper archives (state historical societies)
  - Railroad fire reports (insurance archives)
  - Inquest records (county courthouses)
  - Forest Service incident reports post-1905

### Era F2: Early USFS era (1905-1950)

- **Primary records:** USDA Forest Service incident reports
- **Spatial:** federal lands documented; private/state lands inconsistent
- **Detection:** lookout towers, ground crews, aerial reconnaissance after 1920s
- **Acreage:** post-fire ground survey, walk-through estimation; +/-30%
- **Methodology:** pre-suppression doctrine; 10am Policy starting 1935
  (suppress all fires by 10am next day) -- institutional incentive to
  report aggressively
- **Known biases:**
  - Federal-land bias: state and private fires undercounted
  - Suppression bias: the very policy of total suppression altered fuel
    loads, which then altered subsequent fire behavior
  - Reporting incentive: agencies needed to justify budget; bias toward
    documenting fires they responded to
  - Native cultural burning explicitly suppressed, removed from record
- **What survives reliably:** federal-land fires with ground crews on
  scene; perimeter maps from USFS archive
- **Source documents needed:**
  - USDA Forest Service Annual Reports 1905-1950
  - National Archives RG 95 (Forest Service records)
  - State forestry agency archives where they exist

### Era F3: Aerial photography era (1950-1972)

- **Primary records:** USFS + state agencies
- **Detection:** aerial photography post-fire; ground crews
- **Acreage:** photogrammetric perimeter mapping where photos available;
  +/-15% on documented fires
- **Methodology:** still 10am Policy until 1971; "let burn" experiments
  starting late 1960s
- **Known biases:**
  - Photo coverage uneven (federal lands well-covered, others sparse)
  - Eastern fires under-documented relative to western
  - Lightning ignitions often not distinguished from human cause
  - Suppression bias persists
- **What survives reliably:** acres burned for documented fires (within
  +/-15%); ignition cause classification inconsistent
- **Source documents needed:**
  - USDA aerial photo archives
  - National Interagency Fire Center incident archives (post-1965)

### Era F4: NIFC standardization era (1972-1983)

- **Primary records:** NIFC begins centralized statistics
- **Detection:** ground + aerial photo + early satellite (NOAA AVHRR 1978+)
- **Methodology:** "10am Policy" formally retired 1971; "let burn" zones
  in wilderness; suppression methodology shifts
- **Known biases:**
  - Methodology change itself: "let burn" zones produce different fire
    behavior than continuous suppression
  - AVHRR satellite (1km resolution) misses small fires
  - Reporting standards still varied by agency
- **What survives reliably:** NIFC totals from 1983 forward (their
  recommended baseline)
- **NIFC NOTE:** NIFC explicitly states that data prior to 1983 should
  not be compared with later data due to inconsistent methodology.

### Era F5: NIFC + AVHRR satellite era (1983-1999)

- **Primary records:** NIFC consolidated reports
- **Detection:** ground + aerial + NOAA AVHRR (1km resolution)
- **Acreage:** post-fire ground/aerial mapping; satellite for large fires
- **Methodology:** "appropriate suppression response" replaces blanket
  suppression; wildland fire use zones expand
- **Known biases:**
  - 1km satellite misses fires < ~100 hectares
  - Detection threshold drops sharply (more "small fires" recorded)
  - Fuel loads from a century of suppression begin producing larger,
    hotter fires (real physics change, but measurable)
  - Acres reported from "fires" includes prescribed/managed wildland
    fire use -- definitions vary by year
- **What survives reliably:** total acres on large fires; total fire
  count is biased by detection improvement

### Era F6: MODIS era (2000-2012)

- **Primary records:** NIFC + NASA MODIS Active Fire product
- **Detection:** MODIS (Terra 1999, Aqua 2002) -- 250m-1km resolution,
  4 daily passes
- **Acreage:** ground + aerial + MODIS perimeter; +/-5-10% on large fires
- **Methodology:** GACC (Geographic Area Coordination Centers) standardize
  reporting 2000s; ICS-209 forms become standard
- **Known biases:**
  - Detection threshold drops further (smaller fires now visible)
  - Algorithm version changes (MOD14 v5 -> v6) shift detection counts
  - "Active fire" vs "burned area" products differ
  - Cross-comparison with pre-2000 data REQUIRES detection-bias correction
- **What survives reliably:** acres burned on documented fires; perimeter
  geometry; ignition timestamps from satellite within ~2 hours

### Era F7: Landsat-8 + multi-sensor era (2013-present)

- **Primary records:** NIFC + MODIS + Landsat-8 (2013) + Sentinel-2 (2015)
- **Detection:** 30m Landsat resolution + 10m Sentinel + 250m MODIS daily
- **Acreage:** burned-area product from multi-sensor fusion; +/-2-5%
- **Methodology:** MTBS (Monitoring Trends in Burn Severity) standardized;
  burn severity classified in addition to perimeter
- **Known biases:**
  - Best-quality era; bias minimized
  - Climate change altering fuel moisture in real-time confounds
    "is it a measurement change or a physics change?" question
  - Still no canonical archive for perimeter version control --
    perimeters get updated post-fire
- **What survives reliably:** acres +/-2-5%; perimeter geometry; burn
  severity classification; ignition cause; spread rate

### Era F8: AI-assisted detection (2020-present, overlapping F7)

- **Primary records:** automated fire detection systems (ALERTWildfire,
  satellite ML pipelines)
- **Detection:** sub-hourly satellite + ML classification + camera networks
- **Known biases (anticipated):**
  - ML model versions change detection statistics
  - Camera network coverage uneven (more in wealthy western areas)
  - Anticipated: AI-generated reports / bot-amplified social media
    contaminating ground-truth
- **What to track:**
  - Which ML model version processed each detection
  - Which sensors triggered initial alert
  - Whether report was human-verified or auto-classified

---

## Variables in the Fire Matrix

For each fire event, attempt to populate:

### Physical variables (era-dependent availability)

| Variable                | F1         | F2      | F3      | F4      | F5      | F6      | F7       |
|-------------------------|------------|---------|---------|---------|---------|---------|----------|
| acres_burned            | crude      | +/-30%  | +/-15%  | +/-15%  | +/-10%  | +/-5-10%| +/-2-5%  |
| perimeter_geometry      | none       | partial | yes     | yes     | yes     | yes     | yes      |
| start_timestamp         | day        | day     | day     | hour    | hour    | ~2hr    | ~minutes |
| end_timestamp           | week       | week    | day     | day     | hour    | hour    | hour     |
| ignition_cause          | speculated | partial | partial | yes     | yes     | yes     | yes      |
| fuel_type               | none       | partial | partial | partial | yes     | yes     | yes      |
| burn_severity           | none       | none    | none    | none    | partial | yes     | yes      |
| spread_rate             | none       | none    | none    | none    | partial | yes     | yes      |
| peak_intensity_kW_per_m | none       | none    | none    | none    | none    | partial | yes      |
| smoke_plume_height      | none       | none    | none    | none    | none    | partial | yes      |

### Impact variables (NOT physics -- exposure-dependent)

These should NOT be used as physics signals. Mark them as social/exposure
metrics only:

- `deaths` -- corrupted by EMS access, population, healthcare era
- `injuries` -- corrupted by reporting infrastructure
- `structures_destroyed` -- corrupted by build density, construction codes
- `economic_loss` -- corrupted by valuation method, inflation, insurance era
- `evacuations` -- corrupted by emergency-management era, communication tech

---

## Surrogate calibration sources to build

To recover information from F1-F4 era records, build calibration curves
using modern dual-stream data:

### Curve 1: newspaper severity -> modern acres

- Modern data: 2007-2024 fires with both NIFC acreage AND newspaper coverage
- Method: extract severity adjectives from news; correlate with NIFC acres
- Output: bias curve for translating "great conflagration" -> estimated acres
- Apply backward: 1850-1925 newspaper records

### Curve 2: USFS ground estimate -> satellite-verified acres

- Modern data: 1985-2010 fires with both ground estimates AND satellite perimeters
- Method: regression of ground-estimate acres onto satellite-truth acres
- Output: bias-correction factor per fire size class
- Apply backward: 1905-1972 USFS ground reports

### Curve 3: AVHRR detection threshold -> modern detection

- Modern data: 1985-1999 fires AVHRR-detected vs MODIS-era equivalent fires
- Method: compute fraction of small fires AVHRR would have missed
- Output: undercount correction by fire-size distribution
- Apply: F5 era counts

### Curve 4: social media reports -> ground truth

- Modern data: 2015-2024 fires with both verified perimeter AND Twitter/news posts
- Method: NLP on post severity, count post density per fire
- Output: bias curve, with explicit BOT-FILTERING step
- Apply: future-proofing for AI-generated reports
- Note: this curve will need REVISION as bot patterns evolve

---

## Implementation steps

1. Define the eight `MeasurementEra` objects in code (one per era F1-F8).
2. Document the canonical variable list with allowed units.
3. Build the empty matrix file (CSV or JSON) with eras and variables.
4. Pull modern dual-stream data (NIFC + newspaper + satellite for 2015-2024).
5. Build surrogate calibration curves from #4.
6. Apply curves backward to populate sparse legacy rows.
7. Publish the registry + calibration curves as CC0.

This is multi-year work. The registry document itself is the first
deliverable: it makes the corruption explicit so future analysis can
honor it.

---

## Versioning

All entries in this registry are append-only. If a new methodology change
is discovered (or a current practice ends), append a new era. Never
modify or delete existing era definitions. The registry's history is
itself a primary source.

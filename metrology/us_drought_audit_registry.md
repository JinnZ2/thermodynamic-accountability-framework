# US Drought Metrological Audit Registry

CC0. Living document. Append-only -- never delete past entries.

## Purpose

Document the metrology problem in US drought measurement, 1850-present.

**Drought is the worst-case domain in this entire audit project.** Unlike
tornadoes (corruption in a single damage scale) or hurricanes (corruption
through reanalysis revisions), drought has **structural** corruption:

> **Drought is not a measurement. It is a derived index from multiple
> measurements, where there are at least 6 competing indices that
> DO NOT AGREE with each other.**

When you read "the Western US is in the worst drought in 1,200 years,"
you are reading:

1. A specific drought index (usually PDSI or SPEI)
2. Calibrated against a specific reference period
3. Applied to instrumental data with its own measurement-era issues
4. Applied retroactively to tree-ring proxies via statistical regression
5. Compared across centuries using assumptions about index stationarity

Every layer in that stack has its own uncertainty. The headline number
inherits the product of all of them.

This registry documents the layered corruption.

---

## The fundamental problem: drought has no canonical definition

Different indices give different answers for the same underlying physics.

| Index                      | Inputs                         | Time scale | What it captures                 | What it misses                        |
|----------------------------|--------------------------------|------------|----------------------------------|---------------------------------------|
| PDSI (1965)                | Precip + Temperature           | ~9 mo lag  | Long-term meteorological drought | Flash drought, soil moisture detail   |
| SPI (1993)                 | Precipitation only             | 1-48 mo    | Pure rainfall anomaly            | Temperature effects, soil/groundwater |
| SPEI (2010)                | Precip + Temperature + PET     | 1-48 mo    | Energy-balance drought           | Vegetation feedback, CO2 effects      |
| Self-calibrating PDSI      | Precip + Temp, region-specific | ~9 mo      | Regional comparability           | Same as PDSI                          |
| Soil moisture (1985+)      | Satellite/in-situ              | Real-time  | Actual surface water             | Pre-satellite era                     |
| US Drought Monitor (2000+) | Expert synthesis               | Weekly     | Subjective combined              | No data before 2000                   |
| Streamflow drought         | River gauges                   | Real-time  | Hydrological drought             | Small watersheds                      |
| GRACE groundwater (2002+)  | Satellite gravimetry           | Monthly    | Subsurface water                 | Has data gap 2017-2018                |

**Critical observation:** when published research says "drought severity
has increased X%," they almost always mean "PDSI value has decreased
by Y units," which is **not the same thing**.

Yang et al. (2020) in *Hydrology and Earth System Sciences* showed that
when PDSI is recalculated using direct climate model outputs (with CO2
effects on plant evapotranspiration), the drought increase signal is
**much smaller than published values using offline PDSI**.

In plain language: **PDSI overestimates drought trends in a warming
world** because it doesn't account for plants becoming more water-
efficient at higher CO2.

---

## Measurement Eras

### Era D1: Newspaper + agricultural-report era (1850-1894)

- **Primary records:** local newspapers, farmer correspondence,
  agricultural society bulletins, individual farm logs
- **Spatial:** towns and railroads documented; rangeland and forest
  conditions invisible
- **Methodology:** "drought" defined by crop failure, livestock loss,
  river drying -- observational, not quantitative
- **Known biases:**
  - Population-density-dependent (cities reported, wilderness silent)
  - Economic threshold: only droughts that hit cash crops got reported
  - Indigenous agricultural systems and rangeland management explicitly
    not recorded
  - Insurance industry didn't yet exist for crop loss
- **What survives:** general impression of "dry years" in regions with
  newspapers; no quantitative time series
- **Source documents:**
  - State historical society newspaper archives
  - USDA early agricultural reports (post-1862)

### Era D2: Early instrumental era (1895-1930)

- **Primary records:** US Weather Bureau (founded 1890, became NOAA 1970)
  precipitation gauges
- **Coverage:** ~3,000 stations by 1900, growing to ~5,000 by 1930
- **Methodology:** monthly precipitation summaries; "drought" as
  qualitative description of precipitation deficit
- **Known biases:**
  - Network density bias: Eastern US well-covered, Western US sparse
  - Mountain precipitation systematically undercounted (gauges in valleys)
  - Snowfall measurement varied by station
  - Temperature records exist but not yet integrated into drought analysis
- **What survives:** raw precipitation totals at station level (with
  station-history caveats)
- **No drought index exists yet** -- calling something a "drought" in
  this era requires retroactive index calculation from the precipitation
  record

### Era D3: Pre-PDSI era (1931-1965)

- **Primary records:** expanded weather station network (~10,000 by 1950),
  USDA crop reports, Drought Disaster Declarations (post-1933)
- **Coverage:** continental US gauge network reaches ~10,000 by 1950
- **Methodology:** Dust Bowl era prompts first systematic drought
  classification; USDA-led "Soil Conservation Service" (1935) begins
  measuring soil moisture
- **Known biases:**
  - Dust Bowl (1934-1939) becomes reference event -- all subsequent
    droughts compared to it
  - "Drought disaster" declarations are POLITICAL events (governor
    requests, federal approval) not physical measurements
  - Pre-1965 PDSI values are RECONSTRUCTED from precipitation/temperature
    records using algorithms that didn't exist until 1965
- **What survives:** precipitation + temperature time series with
  reasonable spatial coverage; soil moisture begins being recorded
  at scattered USDA stations

### Era D4: PDSI era (1965-1992)

- **Primary records:** Palmer (1965) Index becomes operational
- **Methodology:** PDSI calculated from precipitation + temperature +
  soil water-holding capacity; Thornthwaite method for potential
  evapotranspiration (PE)
- **Known biases (THIS IS THE LOAD-BEARING ERA):**
  - **Thornthwaite PE method is wrong** in a warming climate -- uses
    temperature only, not actual energy balance
  - **9-month memory** in PDSI smears short-term events and persists
    long after recovery
  - **Recursive incipient index X** allows current precipitation to
    retroactively change PDSI values for "several earlier months"
    (Alley critique)
  - Cannot detect flash drought
  - Not regionally comparable -- same PDSI value means different things
    in different climates
- **What was published as "drought" in 1965-1992 papers** was based
  on this flawed methodology. Most never got revised.

### Era D5: SPI + soil moisture era (1993-1999)

- **Primary records:** PDSI continues; SPI (McKee 1993) introduced;
  satellite soil moisture (SMMR 1978, SSM/I 1987) maturing
- **Methodology:** SPI uses precipitation only (purer signal but
  ignores temperature/evaporation); satellite soil moisture begins
  providing real measurement
- **Known biases:**
  - Multiple indices now publicly available, but agencies still
    primarily report PDSI
  - SPI vs PDSI can disagree on whether a drought is occurring
  - Self-calibrating PDSI proposed but not widely adopted
  - Tree-ring PDSI reconstructions (Cook et al.) start being
    published with all the inherited PDSI methodology issues

### Era D6: US Drought Monitor era (2000-2009)

- **Primary records:** US Drought Monitor (USDM) launched 2000
- **Methodology:** WEEKLY synthesis of multiple indices + expert
  judgment; D0-D4 categories
- **Known biases:**
  - **USDM is subjective** -- combines indices via expert weighting
    that varies week to week
  - **No data exists pre-2000** in USDM categories -- any "USDM
    trend since 1900" is a back-extrapolation
  - Used as ground truth for validating OTHER indices, creating
    circular validation
  - Categories D0-D4 don't map cleanly to PDSI thresholds
- **What's reliable:** weekly snapshots from 2000+ are real expert
  judgments; week-to-week changes in coverage are meaningful

### Era D7: SPEI + GRACE era (2010-2017)

- **Primary records:** SPEI (Vicente-Serrano 2010) introduced; GRACE
  satellite (2002 launch, 2010 mature use) provides groundwater
- **Methodology:** SPEI uses precipitation - PET (Penman-Monteith);
  better physics than PDSI but still "offline" calculation
- **Known biases:**
  - GRACE has 1km-1000km horizontal resolution -- fine for state-scale,
    coarse for watershed-scale
  - GRACE measures TOTAL water storage anomaly -- separating soil
    moisture from groundwater requires modeling
  - SPEI replaces PDSI in most modern climate work but historical
    SPEI values are RECONSTRUCTED from old precip/temp records
  - Tree-ring drought atlases get re-released using SPEI

### Era D8: GRACE-FO + multi-sensor era (2018-present)

- **Primary records:** GRACE-FO (launched 2018) + SMAP (2015) +
  MODIS evapotranspiration + USDM + SPEI + sc-PDSI
- **Methodology:** ML-assisted multi-index synthesis; Yang et al. 2020
  PDSI-CMIP5 method becomes available
- **Known biases:**
  - **GRACE 2017-2018 GAP**: original GRACE failed mid-2017, GRACE-FO
    launched May 2018. There is a missing year in the groundwater record.
  - Yang et al. 2020 PDSI revision is NOT YET widely adopted by
    operational agencies
  - "Megadrought" papers continue to use original PDSI methodology
- **Critical 2020 finding:** Yang et al. showed CMIP5-based PDSI gives
  drought increases **much smaller** than offline-PDSI. This means
  the famous "worst drought in 1,200 years" claims are likely
  overestimates -- the magnitude is unknown until the literature
  is reanalyzed.

---

## Specific drought claims that fail metrology audit

### Claim: "The 2000-2021 Western US drought is the worst in 1,200 years"

- Source: Williams et al. 2022, *Nature Climate Change*
- Method: tree-ring-reconstructed soil moisture (PDSI-equivalent)
- **Audit findings:**
  1. Tree-ring PDSI calibrated against 20th-century instrumental PDSI
  2. Instrumental PDSI uses Thornthwaite PE method (now known wrong)
  3. CO2 fertilization effect on tree growth IGNORED in calibration
  4. SPEI gives different answer for same period (smaller anomaly)
  5. Yang et al. 2020 PDSI-CMIP5 reanalysis: ~30% smaller drought signal
- **Honest restatement:** "Using the Thornthwaite-PE PDSI methodology,
  reconstructed tree-ring soil moisture suggests an unprecedented
  multi-decadal dry period. The magnitude is highly uncertain because
  the underlying PDSI methodology overestimates drought in warming
  conditions, and the tree-ring calibration inherits this bias."

### Claim: "Drought frequency has doubled since 1900"

- Source: variable, often FEMA disaster declarations as proxy
- **Audit findings:**
  1. FEMA declarations are POLITICAL events, not physical
  2. Threshold for declaration changed multiple times
  3. Population exposure increased dramatically
  4. Same physical drought severity now triggers declaration where
     it wouldn't have in 1900 (people live in places they didn't)
- **Honest restatement:** "Drought disaster declarations have doubled.
  This reflects population growth in arid regions, lower thresholds
  for declaration, and possibly some real climate trend; the three
  cannot be separated without exposure-corrected analysis."

### Claim: "Soil moisture trending downward in US"

- Source: various, including USGCRP National Climate Assessment
- **Audit findings:**
  1. Pre-1985 soil moisture is RECONSTRUCTED from precipitation +
     temperature using land surface models
  2. Different land surface models give different answers
  3. SMAP satellite (2015+) is the only direct measurement, only 9 yr
  4. CO2 fertilization -> plants close stomata -> soil moisture
     INCREASES under elevated CO2 in some studies
- **Honest restatement:** "Modeled soil moisture suggests downward
  trend, but direct satellite measurement only exists for 9 years.
  The trend depends on model choice and CO2 treatment."

---

## Variables in the Drought Matrix

For each "drought event" or year, attempt to populate:

### Direct measurements

- `precipitation_total_mm` (since station era: 1895-)
- `temperature_mean_C` (since station era: 1895-)
- `streamflow_m3s` (USGS gauges: variable by station)
- `soil_moisture_volumetric` (satellite: 1985-, with instrument changes)
- `groundwater_anomaly_mm` (GRACE: 2002-2017, GRACE-FO: 2018-)
- `vegetation_NDVI` (satellite: 1972-)
- `evapotranspiration_actual` (MODIS: 2000-)

### Derived indices (each carrying methodology baggage)

- `PDSI_thornthwaite` (era D4 method)
- `PDSI_penman_monteith` (era D7+ method)
- `PDSI_self_calibrating` (regional comparability fix)
- `PDSI_CMIP5` (Yang et al. 2020 corrected method)
- `SPI_3mo`, `SPI_6mo`, `SPI_12mo`, `SPI_24mo`
- `SPEI_3mo`, `SPEI_6mo`, `SPEI_12mo`, `SPEI_24mo`
- `USDM_category` (D0-D4, only 2000+)

### Proxy reconstructions (very large uncertainty)

- `tree_ring_PDSI_reconstructed` (1000+ yr record)
- `tree_ring_PDSI_methodology_version` (which calibration?)
- `lake_sediment_drought_proxy`
- `speleothem_isotope_drought`

### Political/exposure variables (NOT physics)

- `FEMA_drought_declaration` (political)
- `crop_loss_USD` (exposure-dependent)
- `agricultural_emergency_declared` (administrative)

### CRITICAL versioning fields

Every drought datum MUST carry:

- `index_version`: which methodology was used to compute the index
- `calibration_period`: what reference window was used (e.g., 1971-2000
  vs 1981-2010 vs 1991-2020)
- `co2_correction_applied`: yes/no/method
- `data_source_url_with_date`: when the data was retrieved
- `reanalysis_status`: stable / under revision / deprecated

---

## The reference-period problem

Even within a single index, calibration changes the answer.

PDSI uses a "normal" baseline period. NOAA changes this baseline
**every 10 years**:

- 1961-1990 (used 1991-2000)
- 1971-2000 (used 2001-2010)
- 1981-2010 (used 2011-2020)
- 1991-2020 (used 2021-)

A "PDSI = -3" today means something different than "PDSI = -3" in 1995
because the reference periods differ. **Operational drought maps
silently switch baselines** when NOAA updates them.

This means: a value labeled "extreme drought" in 1995 might be labeled
"moderate drought" today even if the actual physical conditions are
identical, and vice versa.

---

## Surrogate calibration sources to build

### Curve 1: PDSI vs SPEI vs sc-PDSI vs PDSI-CMIP5

- Modern reference: 1985-2024 with all four indices computed
- Build cross-index transfer functions
- Apply backward to identify which index a historical claim used
  and translate to modern equivalent

### Curve 2: tree-ring drought proxy -> modern PDSI vs SPEI

- Modern reference: 1900-2010 with both tree-ring reconstructions
  and instrumental indices
- Quantify the calibration uncertainty in pre-1900 reconstructions
- Apply uncertainty bounds backward through Cook drought atlas

### Curve 3: USDM category -> numerical indices

- Modern reference: 2000-2024 weekly USDM with concurrent index values
- Build calibration showing USDM D0-D4 boundaries in PDSI/SPI/SPEI space
- Apply: enables back-projection of "USDM equivalent" for pre-2000 era

### Curve 4: CO2-corrected vs uncorrected PDSI

- Modern reference: Yang et al. 2020 CMIP5 method vs traditional offline
- Build correction factor as function of CO2 concentration
- Apply: re-evaluate published "megadrought" claims with CO2 effects

---

## Implementation steps

1. Define eight `MeasurementEra` objects (one per era D1-D8)
2. Document the variable list with allowed units AND index methodologies
3. Pull operational PDSI/SPI/SPEI archives from NCEI with version metadata
4. Recompute key historical "droughts" using Yang 2020 PDSI-CMIP5 method
5. Build the four calibration curves
6. Cross-reference with tree-ring drought atlases (Cook et al.)
7. Publish as CC0 with explicit version pinning

---

## Specific cautionary notes for analysts

- **Never compare PDSI values across baseline-period changes**
  without rebaselining. NOAA changes the baseline every 10 years.
- **Never use offline PDSI for trend analysis** in the modern
  warming era without applying Yang 2020 CO2 correction.
- **Tree-ring reconstructions are calibrated to instrumental PDSI**.
  Any PDSI methodology error propagates back through 1,200 years.
- **USDM has no pre-2000 data**. Anyone showing a "USDM trend back
  to 1900" is showing back-extrapolated synthesis.
- **FEMA disaster declarations are not drought measurements**.
  They are political/administrative events.
- **Streamflow drought != meteorological drought != agricultural drought
  != hydrological drought**. Each domain uses different indices and
  different thresholds.
- **GRACE has a year-long data gap (2017-2018)**. Any continuous
  groundwater time series across that gap is interpolated.

---

## The Yang 2020 finding in detail

This is the single most damaging paper to mainstream drought
literature published in the last decade.

**Citation:** Yang, Y., Zhang, S., Roderick, M.L., McVicar, T.R.,
Yang, D., Liu, W., and Li, X.: "Comparing Palmer Drought Severity
Index drought assessments using the traditional offline approach
with direct climate model outputs," *Hydrol. Earth Syst. Sci.*,
24, 2921-2930, 2020. https://doi.org/10.5194/hess-24-2921-2020

**Finding:** PDSI computed using direct CMIP5 model outputs
(maintaining hydrologic consistency with the source model) gives
**substantially smaller** drought-severity, drought-frequency,
and drought-extent increases than PDSI computed offline from
the same models' precipitation and temperature outputs.

**Mechanism:** Offline PDSI ignores the vegetation response to
elevated atmospheric CO2 (plants close stomata -> reduce
transpiration -> conserve soil moisture). The traditional PDSI
calculation method bakes in an assumption of fixed stomatal
behavior that is physiologically wrong under warming.

**Implication:** Most published "drought is increasing" findings
using PDSI overestimate the trend. The magnitude of overestimation
varies but can be **30-50% in the worst cases**.

**Why this matters for the audit:**

- Operational drought monitoring still uses traditional PDSI
- Climate assessments cite PDSI-based research
- "Worst drought in 1,200 years" claims rest on tree-ring PDSI
  calibrated to instrumental PDSI calibrated using the wrong method
- The corrected methodology has not propagated through the literature

---

## Versioning

All entries in this registry are append-only. New methodology revisions
or new findings about existing indices will be added as new entries,
never overwriting existing ones. The registry's history is itself a
primary source.

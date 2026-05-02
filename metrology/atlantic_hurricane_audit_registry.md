# Atlantic Hurricane Metrological Audit Registry

CC0. Living document. Append-only -- never delete past entries.

## Purpose

Document every known measurement methodology change in the HURDAT/HURDAT2
Atlantic hurricane database, 1851-present, so that any analysis can declare
which era of measurement its data comes from and what bias it carries.

The Atlantic hurricane record is the **most actively reanalyzed dataset
in all of Earth-systems measurement**. NHC's Atlantic Hurricane Reanalysis
Project (started ~2000, ongoing in 2026) is *continuously rewriting the
historical database*. As of 2026:

- 1851-1910: officially reanalyzed and revised (Landsea et al. 2004a)
- 1911-1920: officially reanalyzed (Landsea et al. 2008)
- 1921-1930: officially reanalyzed (Landsea et al. 2012)
- 1931-1943: officially reanalyzed (Landsea et al. 2014)
- 1944-1953: reanalyzed (Hagen et al. 2012) -- first decade of aircraft recon
- 1954-1963: reanalyzed (Delgado et al. 2018)
- 1964-1968: reanalyzed (Delgado et al. ongoing)
- Hurricane Andrew (1992): reanalyzed and upgraded Cat 4 -> Cat 5 in 2004
- Hurricane Camille (1969): reanalyzed in 2014

Specific historical changes documented in the literature:

- **Hurricane Carla (1961)**: peak intensity DECREASED from 150 kt (Cat 5)
  to 125 kt (Cat 4) on reanalysis
- **Hurricane Inez (1966)**: peak intensity INCREASED from 130 kt (Cat 4)
  to 145 kt (Cat 5) on reanalysis
- **Hurricane Andrew (1992)**: upgraded from Cat 4 to Cat 5 ten years later

This means: every published "trend in Atlantic hurricane intensity"
is computed against a database that is *literally being rewritten*
year by year. Any 2010 paper's findings may not reproduce against
the 2020 version of HURDAT2, even for the same time period studied.

This registry exists so future analysis can pin which version of
HURDAT2 was used and what biases that version carried.

---

## Measurement Eras

### Era H1: Pre-aircraft, ship-and-landfall era (1851-1943)

- **Primary records:** ship logs, port observations, newspaper accounts,
  individual landfall reports
- **Detection:** required ship encounter or coastal landfall -- open-ocean
  storms went entirely undetected if no ship reported them
- **Intensity estimation:** indirect, from damage reports and minimum
  pressure readings at landfall (where barometers existed)
- **Track reconstruction:** Bayesian fitting from sparse ship reports
  decades later (Fernandez-Paratagas 1996 reanalysis)
- **Known biases:**
  - **Massive open-ocean undercount** -- Vecchi & Knutson (2008, 2011)
    estimated ~3-5 missed storms/yr in pre-1900 era using shipping
    track density to constrain storm frequency
  - **Coastal landfalls preferentially preserved** -- population-density-
    dependent record completeness
  - **Intensity inflation in newspaper accounts** ("monster hurricane")
    vs deflation when no measurement instruments survived
  - Fish storms (never make landfall) entirely invisible
  - Mexican/Central American/Caribbean storms underdocumented vs US storms
- **Saffir-Simpson scale:** **DID NOT EXIST**. Categories assigned
  retroactively in 1971 onward, then again in reanalysis 2000+
- **Intensity estimation method:** post-hoc reanalysis using:
  - 1851-1886: Fernandez-Paratagas + Diaz reconstruction from newspapers
  - 1887-1910: ICOADS ship reports + Hemispheric Weather Maps
  - 1911-1943: ship reports + early radio reports + AEF wind model
- **What survives reliably:** approximate landfall location and date for
  major US-coast events. Open-ocean tracks are RECONSTRUCTED, not measured.
- **Source documents:**
  - Landsea et al. 2004a (1851-1910 reanalysis)
  - Landsea et al. 2008 (1911-1920)
  - Landsea et al. 2012 (1921-1930)
  - Landsea et al. 2014 (1931-1943)

### Era H2: Aircraft reconnaissance era (1944-1959)

- **Primary records:** Hurricane Hunter aircraft + ship + coastal radar
- **Detection:** aircraft began regular Atlantic reconnaissance in 1944
- **Intensity estimation:** still indirect; central pressure from
  dropsondes (introduced 1944), wind speed estimated from flight-level
  to surface ratio (FL2SFC)
- **Coverage:** Atlantic basin only, generally only when storms threatened
  US/Caribbean. Cape Verde storms in eastern Atlantic still under-detected.
- **Known biases:**
  - FL2SFC ratio assumed 0.90 historically; modern value is ~0.80-0.85
    -> all 1944-1989 wind estimates biased ~5-10% high systematically
  - Saffir-Simpson assigned retroactively for any storm before 1971
  - Open-ocean Cape Verde storms still missed in early years
  - Aircraft missions often suspended during peak storm conditions
    (the most intense periods often went unmeasured directly)
- **Reanalysis status:**
  - 1944-1953: Hagen et al. 2012
  - 1954-1959: Delgado et al. 2018 (covers through 1963)
- **Notable revisions:**
  - Hurricane Carla (1961): downgraded Cat 5 -> Cat 4 on reanalysis
  - Hurricane Inez (1966): upgraded Cat 4 -> Cat 5
- **Source documents:**
  - Hagen, Strahan-Sakoskie, Luckett (2012) "A reanalysis of the 1944-53
    Atlantic hurricane seasons - The first decade of aircraft reconnaissance"
  - Delgado, Landsea, Willoughby (2018) "Reanalysis of the 1954-63 Atlantic
    hurricane seasons"

### Era H3: Early satellite era (1960-1974)

- **Primary records:** TIROS-1 (April 1960) + aircraft + ships
- **Detection:** satellite imagery starts; "fish storms" (open-ocean,
  no landfall) become detectable for the first time in history
- **Intensity estimation:** Dvorak technique (visible imagery, Vernon
  Dvorak ~1973) begins replacing pure aircraft measurement
- **Coverage transition:** by 1966, complete satellite coverage of
  Atlantic basin during daylight hours
- **Known biases:**
  - **Detection cliff**: pre-satellite Cape Verde storms were undercounted;
    post-satellite, they are routinely captured
  - The "increase" in Atlantic named storms after 1966 is partly real,
    partly methodological
  - Saffir-Simpson scale formalized in 1971 -- pre-1971 ratings retroactive
  - Visible imagery only (no nighttime detection until 1970s)
- **Saffir-Simpson scale:** formalized 1971, applied to entire record
  retroactively
- **Reanalysis status:** 1960-1970 reanalysis presented at 33rd Conference
  on Hurricanes and Tropical Meteorology (2018); ongoing officially
- **Source documents:**
  - Atlantic Hurricane Reanalysis Project ongoing publications
  - Vecchi & Knutson 2008, 2011 (missing-storm estimation)

### Era H4: Saffir-Simpson + IR satellite era (1975-1989)

- **Primary records:** GOES satellites (GOES-1 1975) + aircraft + ships
- **Detection:** complete 24-hour satellite coverage, IR imagery for
  nighttime detection
- **Intensity estimation:** Dvorak technique standardized; aircraft for
  threatening storms; satellite for fish storms
- **Saffir-Simpson:** operational from 1971 forward (originally just SS,
  later refined to SSHWS)
- **Known biases:**
  - Atlantic AMO was in cold phase 1971-1994 -> fewer storms naturally,
    but this overlaps with detection improvements creating a "rebound"
    appearance when AMO flips warm in 1995
  - FL2SFC ratio still 0.90 (corrected to 0.80-0.85 in 1990s reanalysis)
  - Eastern Pacific basin (NEPAC HURDAT) starts 1949 separately;
    methodology differs from Atlantic
- **What survives reliably:** all storms reaching tropical storm strength;
  intensity at landfall; track at 6-hour resolution
- **What remains uncertain:** intensity peaks far from aircraft missions
  or coastal radar

### Era H5: Microwave + scatterometer era (1990-2002)

- **Primary records:** GOES + microwave imagers (SSM/I 1987, AMSU 1998) +
  scatterometers (NSCAT 1996, QuikSCAT 1999) + aircraft + dropsondes
- **Detection:** microwave penetrates clouds -> can see eye structure
  hidden in cirrus; scatterometer measures surface winds directly
- **Intensity estimation:** GPS dropsondes introduced 1997 ->
  fundamental improvement in eye penetration measurements
- **Known biases:**
  - Methodology change: surface wind estimates revised when GPS dropsondes
    showed FL2SFC was 0.80-0.85, not 0.90 -> all earlier estimates ~5-10%
    too high
  - Hurricane Andrew (1992) -> upgraded from Cat 4 to Cat 5 in 2004
    using new methodology, ten years after the storm
  - Atlantic Multidecadal Oscillation flipped to warm phase 1995 ->
    real increase in named storms, but overlaps with detection
    improvements
- **Reanalysis status:** Andrew specifically reanalyzed (Landsea et al.
  2004b); broader era reanalysis ongoing as part of AHRP
- **What's reliable:** named storm count is mostly complete; intensity
  estimates have ~5-10% systematic bias correctable in reanalysis

### Era H6: ACE + AI-Dvorak era (2003-2018)

- **Primary records:** GOES + microwave + scatterometer + dropsondes +
  AI-assisted Dvorak (ADT)
- **Detection:** complete; even tropical depressions reliably caught
- **Intensity estimation:** Advanced Dvorak Technique (ADT, automated)
  reduces analyst-to-analyst variability; SHIPS model intensity
  forecasts inform best-track decisions
- **Methodology:** Accumulated Cyclone Energy (ACE) emerges as preferred
  metric over storm count or Saffir-Simpson alone -- but ACE values for
  pre-2003 storms are RECONSTRUCTED from intensity time series that
  themselves are reanalysis products
- **Known biases:**
  - HURDAT2 (released 2014, reformatting of HURDAT) becomes the standard
    distribution format
  - Best-Track Change Committee meets annually -> small revisions to
    recent years are routine
  - Eastern Pacific gets reanalysis treatment in parallel (separate
    methodology, separate timeline)
- **What's reliable:** essentially everything for this era; the bias
  is in the LOOKING BACKWARD direction, not in measurements going forward

### Era H7: Continuous reanalysis era (2019-present)

- **Primary records:** all of H6 + new sensors (CYGNSS 2016, NOAA-21 2022)
- **Methodology:** machine-learning intensity estimation; continuous
  best-track revision; HURDAT2 versioning becomes more transparent
- **Known biases:**
  - **The database is in continuous flux** -- any analysis that says
    "based on HURDAT2" must specify *which version* of HURDAT2
  - Best-Track Change Committee can revise recent storms several years
    after the fact (e.g., post-storm reanalysis often takes 2-3 years
    to be officially incorporated)
- **What this means for trend analysis:**
  - A trend computed in 2015 against HURDAT2 may not reproduce against
    HURDAT2 in 2026 -- the underlying data has been edited
  - This is GOOD scientific practice (corrections improve accuracy)
  - But it makes published trend statistics non-reproducible without
    version-pinning

---

## Specific Documented Revisions (the receipts)

This list is partial and needs continuous updating. Each entry shows
one specific historical hurricane whose "official" data has been
revised after the fact:

| Hurricane        | Original      | Reanalyzed    | Year of revision                   |
|------------------|---------------|---------------|------------------------------------|
| Carla (1961)     | Cat 5, 150 kt | Cat 4, 125 kt | 2018 (Delgado)                     |
| Inez (1966)      | Cat 4, 130 kt | Cat 5, 145 kt | 2018 (Delgado)                     |
| Camille (1969)   | Cat 5, 165 kt | Cat 5, 175 kt | 2014                               |
| Andrew (1992)    | Cat 4         | Cat 5         | 2004 (Landsea)                     |
| Galveston (1900) | Cat 4         | Cat 4         | 2004 (multiple revisions to track) |
| 1928 Okeechobee  | Cat 4         | Cat 5         | 2012 (Landsea)                     |

Plus dozens of "previously unrecognized tropical cyclones" added to
HURDAT2 by reanalysis projects, mostly in the 1851-1943 period from
ship reports and newspaper archives.

---

## Variables in the Hurricane Matrix

For each hurricane event, attempt to populate:

### Physical variables (era-dependent availability)

| Variable          | H1            | H2            | H3            | H4            | H5            | H6        | H7       |
|-------------------|---------------|---------------|---------------|---------------|---------------|-----------|----------|
| genesis_location  | landfall_only | partial       | yes           | yes           | yes           | yes       | yes      |
| track_resolution  | poor          | 6hr           | 6hr           | 6hr           | 6hr           | 6hr       | 6hr      |
| peak_intensity_kt | guess         | aircraft      | aircraft+sat  | sat+air       | sat+air+drops | ADT+drops | AI+drops |
| min_pressure_mb   | landfall      | yes           | yes           | yes           | yes           | yes       | yes      |
| max_wind_radius   | none          | partial       | partial       | partial       | yes           | yes       | yes      |
| storm_size        | none          | none          | partial       | yes           | yes           | yes       | yes      |
| eye_structure     | none          | none          | partial       | partial       | yes           | yes       | yes      |
| ACE               | reconstructed | reconstructed | reconstructed | reconstructed | direct        | direct    | direct   |

### Versioning variables (CRITICAL for hurricane data)

Every hurricane record MUST carry:

- `hurdat2_version`: the date-stamped version of HURDAT2 the values came from
- `last_reanalysis_year`: when this storm was last officially reanalyzed
- `reanalysis_doi`: reference to the paper documenting the revision
- `original_rating_if_revised`: the pre-reanalysis Saffir-Simpson category
- `revision_history`: append-only log of every change to this storm's record

### Impact variables (NOT physics -- exposure-dependent, mark as such)

- `deaths` -- exposure + healthcare era
- `injuries` -- reporting infrastructure
- `economic_damage` -- inflation + valuation methodology
- `landfall_population_exposed` -- demographic shifts

---

## Surrogate calibration sources to build

### Curve 1: ship-report intensity -> reanalyzed intensity

- Modern reference: 1944-1959 storms with both original aircraft data
  AND reanalyzed intensity (Hagen 2012)
- Build calibration showing how original intensity estimates relate to
  reanalyzed truth
- Apply: 1851-1943 storms have ONLY ship-report-equivalent data

### Curve 2: Dvorak intensity -> ADT intensity

- Modern reference: 2003-2018 storms with both manual Dvorak and
  automated ADT estimates
- Build calibration showing analyst-bias and ADT-bias
- Apply: 1975-2002 era estimates carry analyst-bias signal

### Curve 3: FL2SFC correction

- Apply systematic 0.90 -> 0.85 correction backward through 1944-1989
- This is straightforward but should be documented per storm

### Curve 4: pre-satellite missing-storm estimator

- Use Vecchi & Knutson (2008, 2011) methodology
- Estimate annual count of missed open-ocean storms 1851-1965
  based on shipping track density
- Add as PROBABILITY DISTRIBUTION (not point estimate) of missing storms

---

## The version-pinning requirement

**Every analysis based on HURDAT2 must declare:**

```
data_source: HURDAT2
hurdat2_version: 2024-04-01  (annual update following 2023 season)
url: https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2023-051124.txt
sha256_hash: <hash of the file used>
analysis_date: 2026-05-02
```

Without this, a "trend in Atlantic hurricanes" is unreproducible
because the underlying database has continuously evolved.

---

## Implementation steps

1. Define seven `MeasurementEra` objects in code (one per era H1-H7)
2. Document the canonical variable list with allowed units
3. Build calibration curves from each Hagen/Delgado/Landsea reanalysis
   paper (the published revisions ARE the dual-stream data we need)
4. Add HURDAT2 version pinning to every data-pull operation
5. Cross-reference with EPAC HURDAT (separate methodology, separate audit)
6. Publish the registry + calibration curves as CC0

---

## Specific cautionary notes for analysts

- **Never compare pre-1944 storm counts to post-1944 storm counts**
  without applying Vecchi & Knutson missing-storm correction
- **Never compare pre-1990 intensities to post-1990 intensities**
  without applying FL2SFC correction
- **Never use a HURDAT2 version older than 2 years** for trend analysis
  if your time period includes 1851-1968 (those years are still being
  actively reanalyzed)
- **Atlantic vs Eastern Pacific are different methodologies** -- never
  combine without separate audit
- **AMO phase matters** -- any "trend" that doesn't account for the
  1995 cold-to-warm AMO flip is comparing different climate states
  not just different decades

---

## Versioning

All entries in this registry are append-only. New revisions of historical
hurricanes by the Best-Track Change Committee will be added as new
revision-history entries, never overwriting previous entries. The
registry's history is itself a primary source for understanding how
hurricane "facts" change over time.

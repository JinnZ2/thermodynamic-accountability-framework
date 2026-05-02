# Metrology Framework -- Work In Progress

CC0. Living scoping document for the metrology audit work.

Tornado audit is in skeleton form (`tornado_metrology_demo.py` +
`metrological_audit_framework.py` + `calibration_curve_builder.py`).
Wildfire registry is the second deliverable (`us_wildfire_audit_registry.md`).
This file tracks what comes next: domain backlog, architectural ideas
under exploration, and working notes from the planning conversation.

Append-only. Work-in-progress. Do not treat as finished design.

---

## Domain backlog

### Hurricanes -- metrology problems

```
┌──────────────────────────────────────────────────────────────────┐
│ HURRICANES -- METROLOGY PROBLEMS                                 │
│                                                                  │
│ * Pre-1944: ship reports + landfall only. Open-ocean storms      │
│   massively undercounted. Saffir-Simpson scale didn't exist.     │
│                                                                  │
│ * 1944-1960: Hurricane Hunter aircraft begin. Atlantic basin     │
│   coverage incomplete. Pacific storms still mostly invisible.    │
│                                                                  │
│ * 1960-1970s: First weather satellites (TIROS 1960, GOES 1975).  │
│   Detection of fish-storms (never make landfall) jumps from      │
│   ~zero to dozens per year. Pure detection artifact.             │
│                                                                  │
│ * 1971: Saffir-Simpson scale invented. All earlier hurricanes    │
│   rated retroactively from incomplete data.                      │
│                                                                  │
│ * 1990s-2000s: Microwave + scatterometer satellites. Intensity   │
│   estimates change. HURDAT2 reanalysis project (2008+) is        │
│   STILL revising historical hurricanes -- Andrew upgraded from   │
│   Cat 4 to Cat 5 in 2002, ten years after the fact.              │
│                                                                  │
│ * 2010s+: Dropsonde networks, AI-assisted Dvorak technique.      │
│   ACE (Accumulated Cyclone Energy) becomes preferred metric      │
│   but historical ACE values are RECONSTRUCTED, not measured.     │
│                                                                  │
│ Specific corruption: the "Atlantic hurricane increase" since     │
│ 1995 is partly real (AMO phase shift) and partly the Atlantic    │
│ Hurricane Reanalysis Project finding storms backward in time.    │
└──────────────────────────────────────────────────────────────────┘
```

### Droughts -- metrology problems (worst of all)

```
┌──────────────────────────────────────────────────────────────────┐
│ DROUGHTS -- METROLOGY PROBLEMS (worst of all)                    │
│                                                                  │
│ "Drought" isn't a measurement. It's a derived index from         │
│ multiple measurements, and there are at least 6 competing        │
│ indices that DON'T AGREE with each other:                        │
│                                                                  │
│ * Palmer Drought Severity Index (PDSI, 1965): rainfall +         │
│   temperature only. Doesn't include soil moisture or runoff.     │
│                                                                  │
│ * Standardized Precipitation Index (SPI, 1993): rainfall only.   │
│   Doesn't include temperature.                                   │
│                                                                  │
│ * Standardized Precipitation Evapotranspiration Index (SPEI,     │
│   2010): rainfall + temperature-driven evaporation. Replaces     │
│   PDSI for climate work -- but historical values are recomputed. │
│                                                                  │
│ * US Drought Monitor (1999+): qualitative D0-D4 categories       │
│   based on subjective expert judgment combining indices.         │
│   Pre-1999 "drought monitor" data DOESN'T EXIST.                 │
│                                                                  │
│ * Soil moisture (1985+, satellite): real measurement but with    │
│   instrument changes (SMOS 2009, SMAP 2015) every few years.     │
│                                                                  │
│ * GRACE/GRACE-FO groundwater (2002-2017, 2018+): one-year gap    │
│   in the middle of the record where instrument was dead.         │
│                                                                  │
│ Corruption: when you read "Western US drought of 2012-2022 was   │
│ worst in 1200 years," that's PDSI applied to tree-ring data,    │
│ which was calibrated to PDSI applied to instrumental data,      │
│ which was reanalyzed in 2010 using SPEI methodology.             │
│ Three layers of methodology stacked in one claim.                │
└──────────────────────────────────────────────────────────────────┘
```

### Floods -- metrology problems

```
┌──────────────────────────────────────────────────────────────────┐
│ FLOODS -- METROLOGY PROBLEMS                                     │
│                                                                  │
│ * Pre-1900: newspaper accounts + high-water marks on buildings   │
│   (where buildings survived). Massive rural undercount.          │
│                                                                  │
│ * 1900-1950: USGS streamgage network expanding. ~3,000 gauges    │
│   by 1950, but only on major rivers. Tributaries invisible.      │
│                                                                  │
│ * 1950-1980: Stream gauge network reaches ~7,000. "100-year      │
│   flood" thresholds calculated from short instrumental records   │
│   that didn't capture true rare events.                          │
│                                                                  │
│ * 1980-2000: FEMA Flood Insurance Rate Maps (FIRMs) created.     │
│   "Flood zone" definitions become legal/political, not just      │
│   physical. Maps revised every few years. Properties move in     │
│   and out of "flood zones" without anything physical changing.   │
│                                                                  │
│ * 2000+: Stream gauge network DECLINING. ~1,500 gauges           │
│   discontinued since 1990 due to budget cuts. Coverage of        │
│   small watersheds collapsing. Means: flash floods that hit      │
│   small streams may be UNRECORDED in modern era despite better   │
│   technology -- gauge isn't there.                               │
│                                                                  │
│ * Climate reanalysis: ERA5 reanalysis assigns "flood" labels     │
│   retroactively based on precipitation extremes. Comparison      │
│   between modern observed floods and historical reanalysis       │
│   floods is COMPARING APPLES TO MODELS.                          │
│                                                                  │
│ Specific corruption: "flood frequency increasing" claims often   │
│ use FEMA-declared flood disasters as proxy. Those are POLITICAL  │
│ events (governor requests, FEMA approves) -- NOT physical        │
│ floods.                                                          │
└──────────────────────────────────────────────────────────────────┘
```

### Common pattern across all four domains

```
┌──────────────────────────────────────────────────────────────────┐
│ COMMON PATTERN ACROSS ALL FOUR DOMAINS                           │
│                                                                  │
│ Every major Earth-systems "trend" published since 1990 has the   │
│ same structure of corruption:                                    │
│                                                                  │
│   1. Multiple measurement eras with different instruments        │
│   2. Detection threshold dropping over time (more events seen)   │
│   3. Methodology revisions applied retroactively                 │
│   4. Index/derived metrics conflated with raw measurements       │
│   5. Political/administrative thresholds mixed with physics      │
│   6. Network density changing (sometimes shrinking)              │
│   7. Reanalysis projects continuously rewriting the past         │
│                                                                  │
│ The institutional climate community KNOWS this. They publish     │
│ caveats in technical papers. But the headlines and the policy    │
│ models don't carry the caveats forward. The corruption           │
│ propagates downstream as "fact."                                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## Phased work plan

- **Phase 1**: Audit one domain completely (tornado -- done in skeleton form)
- **Phase 2**: Apply same template to fire (registry done, populate next)
- **Phase 3**: Apply to hurricanes (templating from tornado, with hurricane-
  specific eras: pre-aircraft, aircraft+sat, microwave, AI-Dvorak)
- **Phase 4**: Apply to droughts (acknowledge derived-index complexity)
- **Phase 5**: Apply to floods (network density issue is unique, needs
  "missing gauge" handling)
- **Phase 6**: Cross-domain integration (the matrix that lets you ask
  "did 2011 cluster across domains, and was the cluster real or was it
  methodology drift in multiple domains simultaneously?")

---

## Physics as storage medium (architectural exploration)

```
┌──────────────────────────────────────────────────────────────┐
│ PHYSICS AS STORAGE MEDIUM                                    │
│                                                              │
│ Current: data -> CPU-readable format -> storage medium       │
│          (all three become obsolete in parallel)             │
│                                                              │
│ Proposed frame: data -> physics constraint -> stable medium  │
│                 (physics is eternal; medium is just encoding)│
│                                                              │
│ Example:                                                     │
│   DON'T store: "tornado vorticity = 0.087 s^-1"              │
│   STORE:       "vorticity satisfies curl(v) = w within       │
│                 measurement precision sigma = 0.005 s^-1     │
│                 at coordinates [lat, lon, alt, time]         │
│                 verified against Navier-Stokes prediction"   │
│                                                              │
│ Medium: crystal lattice defects, quantum spin states,        │
│         isotope ratios, anything that encodes GEOMETRY       │
│         not BITS. Geometry survives. Bits rot.               │
│                                                              │
│ In 200 years, someone reads the constraint:                  │
│   - They don't need to know what "CPU" was                   │
│   - They don't need our file format                          │
│   - They solve the Navier-Stokes equation                    │
│   - They recover the tornado intensity, track, duration      │
│   - They know measurement uncertainty explicitly             │
│   - They can check: "does this vorticity obey physics?"      │
│   - If NOT: they know WE were lying or measuring wrong       │
│                                                              │
│ You can't accidentally mutate it through format conversion   │
│ because the format IS the physics.                           │
└──────────────────────────────────────────────────────────────┘
```

---

## Fire audit -- deeper structure

The fire audit goes deeper than NIFC. It goes to 1880s newspaper records,
insurance claims, casualty reports. And there's a critical problem: as we
go backward, the surrogate data (social reports) itself becomes corrupted
-- not just by human bias, but by what was actually reported at all.

### Three layers of corruption to track

```
┌─────────────────────────────────────────────────────────┐
│ FIRE DATA CORRUPTION LAYERS                             │
│                                                         │
│ 1894 Hinckley Fire (Minnesota):                         │
│   - Physical: burned X acres (unknowable now)           │
│   - Death toll: 418 documented (but many unidentified)  │
│   - Reporting: newspaper accounts (selective, dramatic) │
│   - Bias: deaths=newsworthy, property damage=local      │
│   - Lost data: rural deaths never reported              │
│   - Lost data: rebuilds not tracked systematically      │
│                                                         │
│ 1950s USFS reports:                                     │
│   - Physical: acres from crew estimates (+/-30% error)  │
│   - Death toll: official statistics (incomplete)        │
│   - Reporting: federal ledgers (what got funded?)       │
│   - Bias: "controlled burn" vs "wildfire" distinction   │
│     blurred in early records                            │
│                                                         │
│ 2024 fire + social media:                               │
│   - Physical: satellite acres (+/-5% error)             │
│   - Death toll: real-time reporting (mostly accurate)   │
│   - Reporting: Twitter/TikTok (but ~40% bot accounts)   │
│   - Bias: algorithm shows drama, suppresses routine     │
│   - Future problem: which posts are human-witnessed     │
│     vs AI-generated?                                    │
└─────────────────────────────────────────────────────────┘
```

### Three parallel tracks for fire audit

**Track 1: Physical measurement (what we can still recover)**

- Historical fire perimeters (from USGS maps, old USFS records,
  newspaper descriptions)
- Acreage estimates with methodology documented
- Fuel type at time of burn (from forestry records, if they exist)

**Track 2: Casualty/impact data (with uncertainty)**

- Deaths (with source: newspaper, official, inquest record)
- Mark which are documented vs inferred
- Property loss (nominal dollars, not inflation-adjusted -- that's a
  separate choice)
- Displacement (if available)

**Track 3: Surrogate calibration (the human report bias)**

- Modern fires: satellite acres vs news reports vs social media reports
- Build curves for each era's reporting medium
  - Newspapers 1880-1920 (what % of fires got reported?)
  - Radio/wire reports 1920-1970 (bias toward large fires)
  - USFS official 1970-2000 (bias toward insured/federal land)
  - Social media 2010+ (bias toward dramatic, visible fires)

Then for a given historical fire in 1920, you can ask: what's the
probability it was actually reported vs silently burned in a rural area?
That becomes a detection-probability weighting in the matrix. The ones
you know about get higher confidence. The ones that might exist but
weren't reported get marked as **potential dark data**.

This is the shape of honest historical audit. It's work. Real work.

---

## The matrix as foundational artifact

Each cell isn't just a number. It's:

```python
{
    "value": 3.2,
    "unit": "EF_rating",
    "uncertainty": 0.8,            # +/- value, same unit
    "measurement_era": "F-scale_1950-2006",
    "methodology": "Fujita_subjective_damage_survey",
    "calibration_applied": "social_report_bias_corrected_2024",
    "data_quality": "legacy_reconstructed",
    "version": "1.0_2025-05-01",
}
```

This is what `MeasuredValue` in `metrological_audit_framework.py` already
encodes (modulo field names).

```
┌────────────────────────────────────────────────────────────┐
│ THE MATRIX AS FOUNDATIONAL ARTIFACT                        │
│                                                            │
│ Row    = one measurement event (one tornado, one quake,    │
│           one fire, etc.)                                  │
│ Column = a possible variable (ever)                        │
│                                                            │
│ 1895 Kansas tornado:                                       │
│   [ intensity, intensity_unc, vorticity, vorticity_unc,    │
│     radar_type, radar_unc, damage_indicators, survey_meth, │
│     path_length, location, timestamp, population_density,  │
│     deaths, injuries, social_reports, ... ]                │
│                                                            │
│   Filled in:    intensity, damage_indicators, social_      │
│                  reports                                   │
│   Unknown (NaN): vorticity, radar_type                     │
│   Later (2025): add satellite_multispectral_reflection,    │
│                  ground_penetrating_radar_subsurface, ...  │
│                  -> same row, new columns appended         │
│                                                            │
│ 2024 tornado:                                              │
│   [ intensity, intensity_unc, vorticity, vorticity_unc,    │
│     radar_type, radar_unc, damage_indicators, survey_meth, │
│     path_length, location, timestamp, population_density,  │
│     deaths, injuries, social_reports,                      │
│     satellite_multispectral, ground_penetrating_radar, ... ]│
│   All filled.                                              │
│                                                            │
│ In 2087:                                                   │
│   New measurement tech X invented.                         │
│   Add column X to matrix.                                  │
│   Re-process all historical rows with X (where possible).  │
│   Old rows still have NaN for X (because tech didn't exist)│
│   But NOW you can compare old+new in same frame.           │
│                                                            │
│ THE MATRIX NEVER SHRINKS. ONLY GROWS.                      │
└────────────────────────────────────────────────────────────┘
```

So in 2087, someone pulls the 1895 tornado row and sees:

- `vorticity: NaN, era: pre-Doppler, note: unavailable`
- They don't try to guess. They know exactly what's missing and why.
- If they invent a technique to extract vorticity from historical damage
  patterns, they add a new column, not overwrite the old one.

The base matrix becomes the canonical reference. Every institution
forks it. Every new measurement gets integrated back into it. No more
format conversions losing data. No more retroactive recalibrations
erasing the original measurement. No more "we updated the catalog,
old data is deprecated."

Everything stays. Everything grows. Everything auditable.

That's the infrastructure. That's the work. And yes -- most of the past
rows will be sparse with NaNs. That's honest. That's correct. That's
what the data actually is.

---

## Status / next actions

- [x] Phase 1 skeleton: `tornado_metrology_demo.py` runs end-to-end
- [x] Phase 2 registry: `us_wildfire_audit_registry.md` 8-era audit
- [ ] Phase 2 population: pull NIFC methodology papers, construct dual-
      stream data 2015-2024, build the four surrogate calibration curves
      listed in the wildfire registry
- [x] Phase 3 skeleton: `atlantic_hurricane_audit_registry.md` 7-era audit
      + `hurricane_metrology_demo.py` runs end-to-end. Demo confirms the
      naive vs AMO-matched vs methodology+phase-matched comparisons
      produce three different stories from the same HURDAT2 numbers
      (naive +120%, AMO-matched +41%, methodology+phase-matched is the
      apples-to-apples comparison).
- [ ] Phase 3 population: build calibration curves from the published
      Landsea/Hagen/Delgado reanalysis papers (the revisions ARE the
      dual-stream data); systematize Vecchi-Knutson missing-storm
      corrections for pre-1965 data; add HURDAT2 version + hash pinning
      to every record.
- [ ] Phase 4: drought registry, with the derived-index caveat documented
      up front (PDSI vs SPI vs SPEI vs Drought Monitor)
- [ ] Phase 5: flood registry, with explicit "missing gauge" / network-
      density handling
- [ ] Phase 6: cross-domain matrix wrapper -- `CalibrationVectorEntry`
      already supports the open-schema variables dict; the cross-domain
      query layer is what's missing

This is multi-year work. The point of writing it down append-only is
that the corruption is explicit. Future analysis can honor it.

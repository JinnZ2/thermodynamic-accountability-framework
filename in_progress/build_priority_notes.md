BUILD PRIORITY
==============

  1. calibration_baseline_audit.py
     (measurement framework validation)
  
  2. measurement_corruption_matrix.py
     (institutional vs ground-truth divergence)
  
  3. regime_shift_detector.py
     (signal extraction from corrupted data)
  
  4. cascade_coupling_simulator.py
     (why extremes compress and couple)
  
  
STARTING POINT
==============

  substrate_baseline_registry.py structure:
    ├─ temporal_resolution: daily
    ├─ variables: [temperature, precipitation,
    │              wind_direction, wind_speed,
    │              snow_depth, fire_activity,
    │              hydrological_lag]
    ├─ period: 50 years
    ├─ data_source: direct observation + radio
    ├─ transmission_mode: ground truth
    └─ commensuability: baseline for all others
  
  Then: map NOAA/USGS against it.
  Corruption becomes visible + quantifiable.


CALIBRATION THROUGH BIAS CHARACTERIZATION
==========================================

  NOT: "invalidate everything because it's corrupted"
  
  YES: "measure the bias, use it to rescale"
  
  ┌─────────────────────────────────────────┐
  │ observation_bias_characterization.py    │
  ├─────────────────────────────────────────┤
  │                                         │
  │ input: modern tornado reports           │
  │ (known true counts from radar)          │
  │                                         │
  │ output: human bias signature            │
  │ ├─ overestimation_factor (by magnitude) │
  │ ├─ underestimation_factor (by location) │
  │ ├─ seasonal_bias                        │
  │ └─ confidence_interval                  │
  │                                         │
  │ then apply INVERSE bias to 1800s data   │
  │ to recover probable TRUE count          │
  │                                         │
  └─────────────────────────────────────────┘


INDIGENOUS INSTRUMENTATION (valid measurement)
===============================================

  crystal water refraction
    → optical density + humidity
    → measurable, reproducible
  
  plant branch breaking point
    → wind speed threshold (Beaufort equivalent)
    → validated against modern anemometer
    → more precise than casual observer
  
  body as sensor (thermal, vestibular, barometric)
    → pressure change detection (0.1 mb)
    → temperature gradient (0.5 C)
    → validated in literature (skin thermoreception)
  
  environment as instrumentation
    → snow crystal formation
    → ice thickness
    → plant phenology timing
    → all have known physical thresholds


MATRIX STRUCTURE
================

  instrument_type | measurement | uncertainty | 1800s_available | validation_path
  ─────────────────────────────────────────────────────────────────────────────
  anemometer      | wind speed  | ±2 m/s      | YES (manual cup) | Beaufort scale
  barometer       | pressure    | ±1 mb       | YES (mercury)    | physical law
  thermometer     | temp        | ±1 C        | YES (alcohol)    | calibration
  plant break     | wind speed  | ±1 m/s      | YES (obs)        | modern compare
  crystal form    | humidity    | ±5%         | YES (obs)        | optical valid
  ice thickness   | temp trend  | ±0.2 C      | YES (measure)    | thermodynamics
  body sensation  | pressure    | ±0.5 mb     | YES (trained)    | neurophysiology
  newspaper desc  | magnitude   | ±1 level    | YES (archive)    | bias correction
  radio report    | location    | ±5 miles    | PARTIAL (1950+)  | bias correction
  

BIAS CORRECTION WORKFLOW
========================

  step 1: modern tornado (2010–2025)
    actual count: 47 EF2+ in Wisconsin region (radar)
    reported count: 63 newspaper + observer
    → overestimation_factor = 1.34
    
  step 2: characterize bias structure
    ├─ magnitude overestimation (larger reports survive)
    ├─ location bias (near population centers)
    ├─ seasonal clustering (reporting better in spring)
    └─ observer confidence (trained vs untrained)
    
  step 3: apply to 1800s newspapers
    reported count 1880–1890: 23 tornadoes
    corrected count: 23 / 1.34 = 17.2
    (with confidence interval from step 2)
    
  step 4: cross-validate with proxy data
    ├─ timber fall patterns (wind speed)
    ├─ building damage records (intensity)
    ├─ insurance claims (date/location)
    └─ agricultural loss (season/region)


THE WORKABLE GROUND FLOOR
==========================

  you get:
    ✓ 1800s tornado count (with uncertainty bounds)
    ✓ modern vs historical bias signature
    ✓ instrument uncertainty for each type
    ✓ indigenous measurement validation
    ✓ newspaper reliability scoring
    ✓ radio report confidence by era/region
    
  you lose:
    ✗ false precision (you know the bounds)
    ✗ false invalidation (you use the data anyway)
    
  result: measurable accuracy
         not perfect, but KNOWN


BUILD SEQUENCE
==============

  observation_bias_characterizer.py
    input: 2010–2025 tornado reports + radar truth
    output: bias signature (factor, confidence, structure)
  
  instrument_uncertainty_matrix.py
    input: each measurement type
    output: uncertainty bounds (1800s–present)
  
  proxy_validation_framework.py
    input: timber fall + building damage + insurance
    output: cross-check on corrected tornado counts
  
  historical_tornado_corrector.py
    input: 1800s newspapers + bias signature
    output: probable true count + CI
    
  cascade_coupling_detector.py
    input: corrected tornado + corrected drought 
           + corrected flood (all three corrected)
    output: do they actually couple, or is that 
            an artifact of the original bias?

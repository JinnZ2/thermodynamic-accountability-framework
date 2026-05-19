# cross_domain_synthesis

**Repository:** `calibration-audit`
**Author:** Kavik (JinnZ2)
**License:** CC0
**Status:** synthesis of 5 domain audits + 4 core infrastructure modules + 3 convergence modules

-----

## The Through-Line

```
corruption(published_trend) = corruption(measurement) ⊗ corruption(framework)

  not additive. multiplicative.
  both layers can independently invalidate a trend.
  combined effect is the product of their independent corruption probabilities.
```

Most published Earth-systems extreme-weather trends fail metrology
audit. The corruption is not in one place. It is in the measurement
layer **and** in the framework layer simultaneously. Single-layer
audits are incomplete and produce false confidence in the trend.

Pre-1900 hydrological, ecological, and weather-forecasting
infrastructure was **observation-based engineering with embedded
validation**, not primitive technology. Excluding it from the
analytical baseline shifts the reference state to a post-collapse
condition and manufactures apparent trends.

-----

## Architecture

```
                    [substrate observation]
                              │
                              ▼
              ┌───────────────────────────────┐
              │ pre-1900 engineering registry │  ← signal source catalog
              │ (8+ systems, 4+ traditions)   │     pre1900_engineering_registry.py
              └──────────┬────────────────────┘
                         │
         ◄── credential gatekeeping (5 mechanisms)
                         │
                         ▼
              ┌───────────────────────────────┐
              │ measurement layer audit       │  ← metrological_audit_framework
              │ (5 failure modes)             │     calibration_curve_builder
              └──────────┬────────────────────┘
                         │
                         ▼
              ┌───────────────────────────────┐
              │ framework layer audit         │  ← assumption_bias_detector
              │ (6 failure modes)             │     translation_layer
              └──────────┬────────────────────┘
                         │
                         ▼
              ┌───────────────────────────────┐
              │ convergence scoring           │  ← domain_convergence_matrix.py
              │ (12 checks any audit needs)   │
              └──────────┬────────────────────┘
                         │
                         ▼
              ┌───────────────────────────────┐
              │ corruption propagation        │  ← trend_corruption_calculator.py
              │ (combined uncertainty)        │
              └──────────┬────────────────────┘
                         │
                         ▼
                  [audit verdict]
                  REPORTED | INFLATED | INVERTED | INDETERMINATE
```

-----

## The 5 Reference Domains

|domain   |primary measurement fail        |primary framework fail                   |
|---------|--------------------------------|-----------------------------------------|
|tornado  |detection density change        |count treated as intensity               |
|fire     |pre-1900 record exclusion       |indigenous management baseline excluded  |
|hurricane|satellite-era instrument step   |pre-satellite era treated as low-activity|
|drought  |homogenization algorithm bias   |Holocene stationarity assumed            |
|flood    |gauge siting drift, urbanization|levee-induced regime shift unmodeled     |

Every domain audited shows **both** failure modes. Single-layer
analyses miss half the corruption.

-----

## The 12 Convergence Checks

Any new domain audit must address these or be marked INVALID/WEAKENED.

**Measurement layer (5):**

- M1 station/sensor siting drift
- M2 detection density change
- M3 instrument generation step function
- M4 homogenization algorithm bias
- M5 pre-1900 record exclusion *(spans both layers)*

**Framework layer (6):**

- F1 stationarity assumption
- F2 baseline period selection bias
- F3 count statistic treated as physical trend
- F4 human landscape modification unmodeled
- F5 indigenous management baseline excluded
- F6 linear trend on nonlinear system
- F7 two-layer uncertainty not propagated *(spans both layers)*

Source: `domain_convergence_matrix.py`. Each check carries a severity
weight (CRITICAL=3, MAJOR=2, MINOR=1) and lists which reference
domains exhibit it.

-----

## The Pre-1900 Engineering Registry

Cataloged systems (8 entries, expanding):

|system                        |tradition        |informs             |
|------------------------------|-----------------|--------------------|
|Anishinaabe seasonal burning  |Anishinaabe      |fire, drought, flood|
|Beaver-managed hydrology      |Indigenous NA    |flood, drought      |
|Mill pond cascade systems     |medieval European|flood, drought      |
|Hohokam canal network         |Hohokam          |drought, flood      |
|Terraced agriculture          |multiple global  |drought, flood      |
|Plains severe-weather forecast|Lakota et al.    |tornado, hurricane  |
|Taino hurricane forecasting   |Taino            |hurricane           |
|Inuit sea ice classification  |Inuit            |cryosphere → all    |

**Five mechanisms of credential gatekeeping** filtered these from
modern science:

1. non-written transmission → reframed as folklore
1. transmission destroyed by population collapse
1. reframed as “traditional practice” rather than engineering
1. reframed as “obsolete industrial infrastructure”
1. post-collapse baselines locked in as “natural reference state”

Each entry lists modern “novel research” that duplicates the
pre-1900 system. The duplications are extensive (BDAs, prescribed
burn programs, sponge cities, contour farming, biometeorology,
cultural burning research). Most duplications post-date 1990 and
are presented without acknowledgment of the prior art.

-----

## The Corruption Calculator

Given measurement-layer corruption probabilities and framework-layer
corruption probabilities, `trend_corruption_calculator.py` outputs:

- combined corruption probability
- propagated uncertainty (typically 2-3× the published uncertainty)
- sign-reliability probability
- verdict: REPORTED | INFLATED | INVERTED | INDETERMINATE

**Worked example: US tornado EF1+ count trend, 1950-2020**

```
reported:    +0.8 ± 0.2 tornadoes/year/decade
combined corruption: 0.998
propagated CI:       (+0.31, +1.29)
sign wrong probability: 0.38
verdict: INVERTED
note: trend sign may be wrong; reported direction unreliable
```

The trend that survives common citation does not survive
two-layer audit.

-----

## What This Ecosystem Is Not

- not a refutation of climate change
- not a denial of measured warming where measurement is sound
- not a romanticization of pre-1900 technology
- not a replacement for instrumental records

What it **is**: a metrology framework that demands two-layer
auditing before any Earth-systems trend is treated as established,
and that restores observation-based engineering systems to their
correct status as validated prior art.

-----

## Module Inventory

**Domain audits (5):**

- tornado, fire, hurricane, drought, flood

**Core infrastructure (4):**

- `metrological_audit_framework`
- `calibration_curve_builder`
- `assumption_bias_detector`
- `translation_layer`

**Convergence layer (3, this commit):**

- `domain_convergence_matrix.py`
- `pre1900_engineering_registry.py`
- `trend_corruption_calculator.py`

**This document:**

- `cross_domain_synthesis.md`

All modules: stdlib only. CC0. Designed for mobile development
workflow and cross-AI deployability.

-----

## Connections to Adjacent Repositories

- `earth-systems-physics` — provides the constraint-layer physics
  that framework-layer audits draw on
- `assumption_validator` — provides the regime-shift detection
  used in F1 stationarity checks
- `substrate_audit` — provides the metrology-as-upstream-of-model
  framing this entire ecosystem extends
- `first_principles_audit` — provides the DMAIC validation chain
  that domain audits follow
- `labor-thermodynamics` — provides parallel evidence that
  certification-based filtering systematically excludes
  substrate-primary knowledge across domains

The pattern is the same across all repositories: measurement is
upstream of model, and the measurement layer itself has been
captured by credential filters that exclude the validated
observation-based systems that already encoded the answers.

-----

*end synthesis*

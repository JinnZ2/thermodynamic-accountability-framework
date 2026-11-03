# metrology/drop_electrification_corrosion/

Common denominator between a lab drop-electrification corrosion result
(Ni et al., Nature 2026) and decades of outdoor coated-panel exposure
data. Built to `WORK_ORDER.md`. Does not test the mechanism.

```text
WORK_ORDER.md        operator order, verbatim (truncated mid-Task-2) + step status
methods_extract.md   Task 1  BLOCKED: paper hosts denied by egress; 0 values entered
panel_datasets.md    Task 3  outdoor datasets, sorted by sheltered-control presence
exposure_index.py    Task 2  pipeline; stdlib; python3 exposure_index.py --selftest
```

## Flow

```text
panel site ──> nearest NOAA ISD station ──> hourly T, Td, rain, wind     MEASURED
                    │ loss: distance                │ loss: missing hours
                    v                               v
            rain rate R (mm/h) ──> drop spectrum N(D)·v(D), rescaled to R    MODELLED
                                         │
                                         ├─> impact drops / m^2 panel (x cos tilt)
                                         ├─> split by RH bin, size bin
                                         └─> fraction of drops >= lab volume
                                         │
                              weight w(D, RH, ion, slide)                   STUB
                                         │  NotParameterized until Task 1
                                         v
                              ExposureProfile (vector, never one scalar)
```

## First scaling read (MODELLED, unweighted)

The model's own numbers (from `drop_spectrum`, Marshall-Palmer + Atlas
velocity):

```text
rain rate   impact drops / m^2 / mm rain   fraction of drops >= 35 uL (4.06 mm)
  1 mm/h          4.7e6                       6.6e-7
 10 mm/h          1.4e6                       2.2e-4
 50 mm/h          5.8e5                       2.9e-3
```

```text
1000 mm/yr site  ->  ~1e9 impact drops / m^2 / yr  ->  ~1e5 / cm^2 / yr
lab              ->  ~3000 slid drops on one track -> pinhole
```

Interference point: an unweighted count says an outdoor panel would pass
the lab's drop count in days. Real coatings last years. So per drop,
natural rain must carry orders of magnitude less charge than a lab drop,
or the effect needs conditions rain rarely provides. Three candidate
attenuators, each a parameter in `WeightParams`:

```text
B1 size     natural drops are mostly < 2 mm; slide drops on a panel are
            coalesced aggregates. impact->slide transfer NOT modelled.
B2 ion      inland rain is near-deionized; coastal rain is salt-loaded.
            the ion exponent's SIGN separates charge separation from
            solute electrochemistry. Station data has no chemistry;
            candidate source: NADP/NTN weekly Na+/Cl-.
B3 shelter  only sheltered-vs-open pairs at one site isolate rain.
```

The ratio "outdoor damage rate / unweighted drop count" is the quantity
the weight function has to reproduce. That is where the leverage is.

## Not testable here

`--fetch` and `--nearest` against live NOAA: ncei.noaa.gov is denied by
this session's egress policy. The parser was written to the NCEI
global-hourly CSV field spec (TMP, DEW, AA1, WND) and checked against a
synthetic fixture only. Run it against one real station file before
trusting it.

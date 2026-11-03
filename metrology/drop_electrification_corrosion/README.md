# metrology/drop_electrification_corrosion/

Status: co-authored.

Common denominator between a lab drop-electrification corrosion result
(Ni et al., Nature 2026) and outdoor coated-panel exposure data. Built
to `WORK_ORDER.md`. The mechanism is not confirmed here or assumed: the
lab causal link is intervention-tested on lab surfaces only; field
relevance is INFERRED.

```text
WORK_ORDER.md          operator order, verbatim (receipt 2, complete) + step status
methods_extract.md     Task 1   BLOCKED: paper hosts denied by egress; 0 values entered
panel_datasets.md      Task 3   15 datasets, sorted by sheltered controls; all (snippet)
sites.csv              Task 3 -> Task 2 handoff: 14 sites, 1 with coordinates
exposure_index.py      Task 2   pipeline; stdlib; --selftest = 36 checks
index_by_site.csv      Task 2   per-site row; band is its own column; no index yet
gradient_check.json    BUILT-IN CHECK result + column tag dictionary
gaps.md                every missing field, the test that fills it, the null that rules it out
```

## Run

```sh
python3 exposure_index.py --selftest
python3 exposure_index.py run --sites sites.csv --out index_by_site.csv
# where NOAA is reachable:
python3 exposure_index.py fetch-history --out isd-history.csv
python3 exposure_index.py run --sites sites.csv --isd-history isd-history.csv \
        --hourly-dir hourly/ --fetch \
        --drop-volume-ul V --catchment-m2 A --runoff-fraction F \
        --weight-params weight.json        # after Task 1
```

## Flow

```text
site ──> nearest ISD station ──> hourly T, Td->RH, rain         OBSERVED / DERIVED
   │        stamps: distance km, elev delta m, terrain class
   │                    │
   │             FILTER: wet hours only (rain > threshold)        no means formed
   │                    │
   │      ┌─────────────┼──────────────────────────┐
   │      v             v                          v
   │  wet hrs/yr   rain mm/yr     index = SUM_wet rain x weight(RH,T)   weight STUB
   │                    │
   │                    └─> slide drops/yr = rain x catchment x cos(tilt)
   │                                          x runoff_fraction / drop_volume
   v
uncertainty band (distance x elevation x terrain; coastal widens)   PROPOSED***
   fit_weight = 1/band^2  -- loose sites down-weighted, kept
   v
index_by_site.csv  ──>  gradient_check: rho(damage, index) TIGHT vs WIDE
```

## Scaling read (DERIVED from models with named parameters)

The counting rule moves the answer. Same rain, two rules, per cm2:

```text
rule                          drops per cm2 per year at 1000 mm/yr      source of number
impact (Marshall-Palmer)      ~1e5                                      DERIVED*  (DSD model, not site data)
runoff, 35 uL slide drops,    ~2.5e3                                    DERIVED*  (named params, PROPOSED geometry)
  1 cm2 catchment, 30 deg,
  runoff_fraction 1.0
ratio impact/runoff           ~160 at 1 mm/h, ~50 at 10 mm/h, ~20 at 50 mm/h   DERIVED
lab                           ~3000 drops on one track -> pinhole       OBSERVED** (operator-stated, unverified)
```

Under the runoff rule a 1 cm2 catchment reaches the lab drop count in
~1 year: DERIVED*, and only if every lab drop and every runoff drop are
equivalent, which nothing here establishes. Charge per drop, salt per
drop, and drop size are the open terms (gaps.md B1-B3).

Superseded (kept as record): the first version of this README read the
impact count alone as "an outdoor panel would pass the lab drop count in
days", and inferred that natural drops must carry far less charge. That
reading assumed impact drops are the dose unit and leaned on the
mechanism; both are unsupported. An interim chat statement put the
impact/runoff gap at "~5 orders of magnitude"; the selftest measured a
factor of ~20-160. Withdrawn.

## Not testable here

`fetch-history`, `fetch`, `run --fetch`: ncei.noaa.gov is denied by this
session's egress policy. The parser follows the NCEI global-hourly field
spec (TMP, DEW, AA1, AA2) and has been checked against a synthetic
fixture only. Run it against one real station file before trusting it.

# WORK ORDER -- drop-electrification corrosion scaling

Status: co-authored. Operator text below is verbatim.

Receipt history:
- Receipt 1 (2026-11-03, commit on branch claude/drop-electrification-corrosion):
  arrived truncated mid-Task-2 at "Pull hourly NOAA / nearest-airport
  station data as". Superseded by receipt 2; recoverable from git history.
- Receipt 2 (2026-11-03): complete, recorded below. The duplicated
  "CONSTRAINTS / - stdlib only..." line is in the received text and is
  kept.

```text
WORK ORDER — drop-electrification corrosion scaling
Context: Ni et al., Nature 2026, "Spontaneously charged water drops induce
corrosion." DOI 10.1038/s41586-026-10941-6. Max Planck Institute for Polymer
Research. Lab result: 35 uL saltwater drops, 4 cm slide, 0.2-2 nC per drop;
~3000 drops onto Teflon- or polystyrene-coated copper produce pinholes
reaching metal. Goal of this order is NOT to confirm the mechanism. It is to
build the common denominator that lets lab numbers be compared against
decades of existing outdoor exposure data.

TASK 1 — extract paper methods (do first; Task 2 depends on it)
Retrieve the paper and supplementary methods. Extract and record verbatim:
  - salt identity and concentration in the drop solution
  - drop volume, slide length, slide speed, release height
  - surface tilt angle
  - ambient temperature and relative humidity during runs, and whether
    humidity was controlled or logged
  - drop rate (drops per minute) and total count per condition
  - substrate metals used and coating type/thickness
  - how damage was quantified (pinhole counts, area, imaging method)
  - whether any deionized/low-ion control was run
Output: methods_extract.md, one field per line, each marked MEASURED or
NOT REPORTED. Do not paraphrase numbers.
Why it matters: the salt composition decides whether the effect is
interfacial charge separation or solute-driven electrochemistry. That
variable is currently unscoped.

TASK 3 — locate existing outdoor panel data (independent, run in parallel)
Search for publicly available coated-metal outdoor exposure datasets with
per-site records. Targets:
  - NCHRP and state DOT bridge coating studies
  - FHWA bridge coating program; Long-Term Bridge Performance program
  - ASTM/SAE outdoor exposure sites (Kure Beach NC, Arizona desert sites)
  - NACE/AMPP corrosion literature with raw panel data
For each dataset found record: site coordinates, years covered, substrate
metals, coating types, panel tilt angle, damage metric used, whether
SHELTERED CONTROLS exist, and data access path.
Output: panel_datasets.md, sorted by whether sheltered controls are present.
Sheltered controls are the critical field — without them the rain
contribution cannot be separated.
Flag explicitly: none of these log drop charge. They cannot confirm
mechanism. They supply the real-world damage rate the lab must match.

TASK 2 — build charging-weighted exposure index pipeline
Depends on Task 1 for the weight function parameters. Build the structure
now with the weight function stubbed and parameterized.
  - Input: site coordinates from Task 3.
  - Pull hourly NOAA / nearest-airport station data as far back as available:
    temperature, relative humidity, precipitation.
  - FILTER TO PRECIPITATION HOURS ONLY. Monthly or annual means lose the
    event; charging depends on conditions during the rain.
  - Compute per-site: wet hours per year, total rainfall depth, and a
    charging-weighted index = sum over wet hours of (rainfall in hour x
    weight(RH, temp)). Leave weight() as a stubbed function with documented
    parameters until Task 1 returns humidity dependence.
  - Convert rainfall depth to approximate drop count using drop size and
    run-off geometry as explicit named parameters, not hardcoded.
  - Stamp each site with: station-to-site distance (km), elevation delta (m),
    terrain class (flat / complex / coastal), and a resulting uncertainty
    band on the index. A few km flat = tight; tens of km or real elevation
    change = wide; coastal vs inland within the same gap can diverge
    (sea-breeze boundary).
  - Weight tight-bound sites most in any downstream fit; do not discard
    loose ones.
Output: runnable pipeline + index_by_site.csv with the uncertainty band as
its own column.

BUILT-IN CHECK
If damage rate tracks the index best at tight-bound sites and worst at
loose-bound sites, the index is doing real work. If there is no such
gradient, the index is not measuring what it claims. Report this check
explicitly.

CONSTRAINTS
- stdlib only...
CONSTRAINTS
- stdlib only (urllib, csv, json, math). No third-party packages.
- Every number pulled from a source carries a scope stamp: source, page or
  table, conditions it was measured under.
- Tag every claim OBSERVED / DERIVED / PROPOSED. Mark thin-volume claims
  with trailing asterisks (more asterisks = thinner).
- Do not state the mechanism as confirmed anywhere. Lab causal link is
  intervention-tested on lab surfaces only; field relevance is INFERRED.
- Proposed hypothesis to carry, not test: charge separation peaks in
  low-conductivity water while electrochemical attack rises with ions,
  worst case mid-gradient. PROPOSED, thin volume. Bench work required.
- Tag output co-authored. No author characterization in any file.

DELIVERABLES
- methods_extract.md
- panel_datasets.md
- pipeline (runnable) + index_by_site.csv
- gaps.md: every field marked NOT REPORTED or missing, each with the
  cleanest test that would fill it and the null that would rule it out.

ORDER: Task 1 and Task 3 in parallel. Task 2 structure now, weight
function filled when Task 1 returns.
```

## Step status

```text
TASK   DELIVERABLE                  STATE           WHY
1      methods_extract.md           BLOCKED         nature.com, doi.org, crossref, europepmc, arxiv denied
                                                    by session egress (re-probed after receipt 2: still denied);
                                                    0 values entered
3      panel_datasets.md            DONE (snippet)  15 datasets; every field snippet-only; fhwa.dot.gov, ri.se denied
2      exposure_index.py            RUNNABLE        36-check offline selftest passes
       index_by_site.csv            EMPTY OF INDEX  14 sites; 13 lack coordinates; 1 lacks station list
                                                    (ncei.noaa.gov denied); no index value fabricated
       weight(RH, T)                STUB            NotParameterized until Task 1
CHECK  gradient_check.json          NOT_TESTABLE    no site has both a damage rate and a computed index
--     gaps.md                      DONE            every missing field + filling test + ruling-out null
```

# WORK ORDER -- drop-electrification corrosion scaling

Operator-authored. Recorded verbatim below as received 2026-11-03.
The text arrived TRUNCATED mid-sentence in Task 2 ("Pull hourly NOAA /
nearest-airport station data as"). Nothing after that point exists in
this record; nothing has been reconstructed. Task 2 was built to the
received text and every unreceived parameter is a stub.

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
  - Pull hourly NOAA / nearest-airport station data as
```

## Step status

```text
TASK  OUTPUT                 STATE         WHY
1     methods_extract.md     BLOCKED       nature.com / doi.org / crossref / europepmc / arxiv
                                           denied by this session's egress policy; 17 fields
                                           NOT ACCESSED; no number entered
3     panel_datasets.md      see file      web search only; per-field provenance in the file
2     exposure_index.py      STRUCTURE     28-check selftest passes offline;
                                           NOAA fetch NOT_TESTABLE (ncei.noaa.gov denied);
                                           weight() NOT_PARAMETERIZED (waits on Task 1)
2+    rest of Task 2 text    NOT RECEIVED  order truncated mid-sentence
```

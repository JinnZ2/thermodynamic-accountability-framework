# #80 follow-up: crashes, schemas/, INFO, pipeline, multiplier

Hand-written notes for the follow-up to PR #80. The before/after table and
the A/B/C confidence table are generated in `docs/UNKNOWN_AXIS.md`.

## 1. Crash is GAP_INSTRUMENT, not RED

A module that raises now gets status `GAP_INSTRUMENT`. It goes to
coverage with the exception text and `missing_path` (from the exception's
`filename`). It does not count toward severity and no longer adds a red
flag. A run where every module crashes reads NOT_DETERMINABLE.

## 2. Why schemas/ files are missing

They were not deleted and never went missing. Commit `b42ea34`
(2026-05-04, "TASK 1: split schemas/ into upstream/ and eval/") moved
them, as git rename records:

- `schemas/negative_space.json` -> `schemas/eval/negative_space.json` (R100)
- `schemas/trapdoors.json` -> `schemas/eval/trapdoors.json` (R100)
- `schemas/logic_ferret_contract.py` -> `schemas/upstream/` (R100)
- `schemas/metabolic_accounting_contract.py` -> `schemas/upstream/` (R100)
- `schemas/geometric_bridge_contract.py` -> `schemas/upstream/` (R099)
- five more contracts moved to `schemas/upstream/`; nothing reads their old paths

That commit updated three readers in `core/integrations/`. It missed five:

| reader | expects (old path) | file is now at |
|---|---|---|
| `calibration/negative_space_index.py:43` | `schemas/negative_space.json` | `schemas/eval/negative_space.json` |
| `calibration/trapdoor_eval.py:43` | `schemas/trapdoors.json` | `schemas/eval/trapdoors.json` |
| `calibration/test_audit_family.py:450` | `schemas/logic_ferret_contract.py` | `schemas/upstream/` |
| `calibration/test_audit_family.py:612` | `schemas/metabolic_accounting_contract.py` | `schemas/upstream/` |
| `calibration/test_audit_family.py:1030` | `schemas/geometric_bridge_contract.py` | `schemas/upstream/` |

Nothing was created and no path was changed here. That is a separate
decision: point each reader at the new path, or leave it as is.

## 3. INFO goes to coverage

An assumption with a non-numeric value (status INFO) is now a coverage
entry with kind INFO, counted apart from UNKNOWN. When no assumption has
a measured GREEN/YELLOW/RED value, the module reads UNKNOWN.

## 4. pipeline.py: no modules is NOT_MEASURED

`_aggregate({})` used to return (0.0, `calibrating`), which is GREEN; it
now returns (None, `NOT_MEASURED`). `run_unified_audit` cannot reach this
case, because the calibration module always runs, so no existing case
changes. The `sparse` input (`{"system_id": "sparse"}`) still reads
0.44 / `drifting` both before and after. That comes from
`calibration_audit` scoring missing data as 0.5 per dimension (0.0 for
memorialization). Not changed.

## 5. Confidence multiplier

See the A/B/C table in `docs/UNKNOWN_AXIS.md`. The 10 existing cases
carry no UNKNOWN assumption, so A, B and C agree on all of them. They
differ only on planted cases (b) and (c). None picked; the default stays A.

## 6. test_audit_family: the 27 failures on main

- 26 ERRORs: FileNotFoundError, every one on a path from section 2:
  - geometric_bridge 6
  - logic_ferret 8
  - metabolic_accounting 5
  - negative_space 4
  - trapdoor 3
- 1 FAIL: `test_healthy_state_plus_clean_response_is_green`. The
  negative_space crash scored RED. That is the section-2 crash read as a
  verdict. With item 1 it passes on the severity axis.

So all 27 trace to the b42ea34 move. 26 remain after this change.

## Found, not changed

`unified_audit._run_legacy_pipeline` maps `unified_band` against
GREEN/YELLOW/RED. The pipeline emits `Band.value`
(`calibrating`/`drifting`/`mauling`/`memorialized_only`), so nothing
matches and the `.get(band, "YELLOW")` fallback always fires. Every
pipeline run reads YELLOW whatever its score. No existing case passes a
`system_description`, so no row in the table is affected.

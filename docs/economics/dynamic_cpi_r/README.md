# Dynamic CPI-R transfer from Mathematic-economics

This folder contains the newly added CPI and inflation-weighting materials transferred from `Mathematic-economics` into the Thermodynamic Accountability Framework repository. The transfer preserves the files, but it also separates them by maturity so the target repository remains organized and transparent about what is runnable versus what is still exploratory.

| Path | Status | Purpose |
|---|---|---|
| `code/dynamic_cpi_indicator.py` | Partially viable | A fuller dynamic CPI-R estimator with synthetic data generation, a backtest runner, and a simple API stub. |
| `drafts/dynamic_inflation_weight.py` | Draft / incomplete | An earlier or more schematic inflation-weighting prototype with multiple unresolved references. |
| `drafts/iteration_module.py` | Draft fragment | An extension fragment intended to augment `DynamicCPI_R`, but not usable on its own. |
| `examples/api.json` | Example payload | Corrected JSON payload example derived from the source repository’s malformed API sample. |
| `AUDIT.md` | Audit note | Summary of the transfer audit and file readiness assessment. |

The separation is intentional. The target repository conventions reserve `core/` for standard-library modules and use documentation areas for theory and structured archival material. Because these transferred files are economics-focused and not yet ready to become core framework modules, they have been placed under `docs/economics/dynamic_cpi_r/`.

Before any of this material is promoted into production code, the next recommended step is to split executable logic from example payloads, remove placeholder variables, and define a clear interface between the simulation layer and any future API layer.

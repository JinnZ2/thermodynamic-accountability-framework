# CLAUDE_audit_archive.md

Older audit notes from CLAUDE.md, archived for readability.
Active audit notes remain inline in CLAUDE.md; this file
holds the historical record from 2026-03-24 through the
original 2026-05-02 metrology cleanup pass.

Integrity preserved by git history (each entry was committed
to CLAUDE.md before being moved here; recover any entry's
prior commit context via `git log --diff-filter=A CLAUDE.md`
or by walking the file's history).

---

### Audit Notes (2026-03-24)
- `core/fatigue_model.py` was consolidated from 3 duplicate class definitions
- Broken indentation and markdown ``` artifacts were removed
- `HumanSystemModel` now delegates to `FatigueModel` (DRY)
- File names standardized from mixed `Hyphen-Case`/`snake_case` to consistent `snake_case`
- 50+ root-level files organized into `core/`, `simulations/`, `docs/`, `visualizations/`
- `Signal -distortion.md` (space in filename) preserved as `signal_distortion_extended.md`
- `Leyer0.md` (typo) preserved as `layer0.md`

### Audit Notes (2026-04-16)
- `political-audit/` renamed to `political_audit/` to match snake_case convention
- `core/integrations/` created; `biological_extraction_model.py` and the three
  `*_fieldlink.py` bridges (Ferret / Geometric / HAAS) moved there
- `Notes.md` (root) moved to `docs/theory/notes.md`
- `labor_thermodynamics/attribution_sim.md` was actually React/JSX —
  renamed to `visualizations/attribution_sim.jsx` (note: file contains
  Unicode smart quotes that need to be straightened before it will run)
- `labor_thermodynamics/audit_protocol.md` was actually an HTML document —
  renamed to `visualizations/labor_audit_protocol.html`
- `labor_thermodynamics/` now contains only the real markdown specs
  (README, failure_modes, measurement_problem)

### Audit Notes (2026-04-17) -- calibration/ cleanup
- New `calibration/` folder arrived on main with 12 chat-pasted Python
  files. Every file had smart quotes, stray markdown code fences, and
  flat class/def bodies (col 0 instead of col 4). Cleaned up in
  several passes:
  - Mechanical pass: straightened quotes, removed ```` ``` ```` fences,
    fixed `**name**`/`**init**`-style markdown-bold dunders, replaced
    `…` with `...`.
  - Structural pass: programmatic re-indenter that tracked class/def
    body scope plus nested control-flow (if/for/while/with/try)
    recovered most files. Hand-polish for the remaining residual
    errors (mainly scorer-body content that had been trapped inside
    `if not X: return ...` branches, causing silent-None returns).
  - `schema.py` and `calibration_audit.py` were rewritten cleanly;
    `observation_dependance.py` (spelling typo) was renamed to
    `observation_dependence.py` and its 33-line truncated stub
    replaced with a working maturity-model implementation (idea ->
    exploration -> investigation -> theorized -> skill stages,
    stage-mismatch detection, stage-appropriate witness model).
  - `autism_subset_cautionary.py` and `dyslexic_module.py` were
    deleted; their dyslexia / ADHD / autism-spectrum material is
    consolidated into `architecture_mismatch.py` under
    `FAILURE_MODES["pathologizing_substrate_architecture"]`, the
    `SUBSTRATE_PRIMARY_SIGNALS` list, and the `EMBEDDED_PROMPT`
    section addressed to AI models.
  - `architecture_mismatch.py` was landed in three incremental commits
    (Part A: classifier + profile; Part B: signals + FAILURE_MODES;
    Part C: scorers + audit + embedded prompt) after context-timeout
    issues with single-commit rewrites.
- Test suite: `python3 -m unittest calibration.test_calibration -v`
  runs 11 tests, all pass (was only 3 discoverable before the
  test-file nesting fix).

### Audit Notes (2026-05-02) -- metrology/ + root cleanup
- Same chat-paste contamination pattern as the 2026-04-17 calibration
  pass: smart quotes used as triple-quote delimiters, flat class/def
  bodies (col 0 instead of col 4), markdown ``` fences wrapping
  method bodies, `**name**`/`**main**` markdown-bold dunders.
- Root-level cleanup:
  - `resilience_stack.py` rewritten cleanly. Three-layer architecture:
    `AbsenceSignature` registry -> `ConstraintNavigator` ->
    `RegulatoryScopeAudit`. `ResilienceStack.assess()` produces a
    cascade vulnerability score (0-10). stdlib only.
  - `support_cartography.py` already clean (cleaned in prior commit
    `231f0a0` per its commit message).
- Three filename typos / mismatches corrected via `git mv` so module
  filename matches its own self-declared docstring identity:
  - `metrology/domain_mateix.py` -> `metrology/domain_convergence_matrix.py`
    (typo in original filename)
  - `metrology/preregistry.py` -> `metrology/pre1900_engineering_registry.py`
    (filename was a shorthand; docstring + commit message used full name)
  - `metrology/trend.py` -> `metrology/trend_corruption_calculator.py`
    (filename was a shorthand)
  - `metrology/vross_domain.py` -> `metrology/cross_domain_synthesis.md`
    (file content was pure Markdown saved with `.py` extension; same
    pattern as the 2026-04-16 `attribution_sim.md` -> `.jsx` and
    `audit_protocol.md` -> `.html` renames)
- Five Python files in `metrology/` rewritten cleanly with proper
  indentation:
  - `domain_convergence_matrix.py` (12 convergence checks across 5
    reference domains; `score_audit()` returns VALID/WEAKENED/INVALID)
  - `observer_bias.py` (`build_bias_signature()` from
    `CalibrationPair` samples, `correct_historical()` applies inverse
    bias with propagated CIs, `DEFAULT_PRIORS` for 7 observer types)
  - `pre1900_engineering_registry.py` (8 observation-based engineering
    systems: Anishinaabe burning, beaver hydrology, mill ponds,
    Hohokam canals, terraced agriculture, Plains forecasting, Taino
    hurricane forecasting, Inuit sea ice)
  - `trend_corruption_calculator.py` (`MeasurementCorruption` x
    `FrameworkCorruption` -> combined verdict
    REPORTED/INFLATED/INVERTED/INDETERMINATE)
- `⊗` operator symbol in `corruption(measurement) ⊗ corruption(framework)`
  pseudocode replaced with `*` in Python source comments. Markdown
  files keep `⊗` since it renders correctly there.
- All metrology modules: stdlib only. Smoke-test by running each
  module directly: `python3 metrology/<module>.py`.

# SEEAM

This folder contains three related but structurally distinct frameworks.
Each has its own sub-folder. Read this file first to know which one you
want.

## What's here

### `seeam/` — Systemic Energy-Extraction Audit Module

Thermodynamic auditing framework that treats the "human capital"
hypothesis as a falsifiable claim. Models social/economic systems as
finite-resource directed graphs where nodes are agents and edges are
resource flows. Detects "meritocratic ghosting" — celebrating one
node's success while ignoring the systemic drag imposed on siblings /
peers.

Contents:

- `SEEAM.md` — module overview (readme-style entry point for SEEAM itself)
- `protocol.md` — SEEAM Protocol v1.0 (formal specification: axioms,
  metrics, algorithm, falsifiable claims, worked audit)
- `notes.md` — machine-parseable technical spec (for AI integration)
- `SEEAM_audit.md` — `SEEAMFullAudit` class details
- `individual.md` — `HumanCapitalEvaluator` integration
- `meritocracy_errors.md` — case studies of the fallacies SEEAM catches
- `metrics_specs.md` — per-metric definitions with validation tests
- `rigor.md` — rigor-improvement guidelines for the framework
- `seeam_unified.py` — Python implementation (numpy; run this directly
  for the worked family-level audit)

Read order for a new reader: `SEEAM.md` → `protocol.md` → run
`seeam_unified.py`. For AI integration: `notes.md`.

### `bias_autopsy/` — Bias Autopsy Lab

Companion assumption-detection tool. Uses NLP (spaCy + a hedge-detection
classifier) to flag assumption-laden language in scientific claims, then
quantifies how much those assumptions distort a predictive model via
sensitivity analysis.

Contents:

- `Add.md` — architecture overview (NLP processor + quantitative scoring
  + sensitivity analysis + visualization)
- `sensitivity_analyzer.md` — sensitivity-integration writeup
- `sensitivity_analyzer.py` — `SensitivityIntegrator` class (trains a
  baseline model with all vars vs. a clean model with assumption vars
  removed; measures prediction drift). Filename typo `sensativity` in
  the earlier layout has been corrected here.
- `app.py` — Streamlit interface

**Known missing dependency:** `app.py` imports `BiasDetectionPipeline`
from a module `bias_analyzer` (and a `bias_dictionary.json`) that are
not in this folder. Streamlit interface cannot run standalone until
those are supplied. The sensitivity-analysis half runs on its own.

### `manifold/` — Manifold Framework for Contextual Reasoning

State-space model that replaces the stationarity assumption in language
models. Every value claim is explicitly conditioned on time, geography,
population, economic base, institutions, culture, cognitive mode, and
survival urgency. Serves as defensive audit tool (Shield), analogical
discovery engine (Lens), predictive scientific instrument (Engine),
self-calibration loop (Gyroscope), adversarial-steering detector
(Sentry), and premise-dependency audit.

Contents:

- `Manifold.md` — Unified Specification v2.0 (full architecture, math,
  pilot studies, system-prompt-deployment-ready)

Related but structurally distinct from SEEAM proper; grouped here
because it was landed in the same push.

## Relationship to the rest of this repo

SEEAM's substrate-primary framing (thermodynamic accounting, falsifiable
claims, drag audit) shares family resemblance with:

- `core/heat_leak_case.py` — TAF diagnostic engine
- `core/banking_thermodynamic_audit.py` — capital as energy cost
- `core/liability_routing.py` — cosigned-obligation resource-flow ledger
- `labor_thermodynamics/` — workforce attribution audit
- `calibration/` — substrate-vs-narrative audit family
- `metrology/` — Earth-systems measurement audit

The Manifold Framework's premise-audit dimension overlaps with
`calibration/narrative_grounding_audit.py` (grounding high-drift words
against temporal / cultural instantiations).

All CC0.

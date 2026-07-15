# SEEAM -- Systemic Energy-Extraction Audit Module

Thermodynamic + resource-economics audit that treats the claim
"people are our greatest asset" as a falsifiable physical statement.
If a company, government, or economic model labels a human as
capital, then it must bear the full lifecycle costs of that asset --
exactly as an oil company pays for drilling, pipelines, and well
maintenance. This module quantifies the gap between that requirement
and observed resource flows, producing a pass/fail audit report.

License: CC0. Stdlib only.

## Files

- **`protocol.md`** -- SEEAM Protocol v1.0. Formal specification:
  three axioms (Hardware-Potential Parity, Resource-Pipeline
  Accounting, Entropic Propagation Detection), core metrics with
  formulas, audit algorithm in pseudocode, worked family-level
  case study, two impossibility theorems, and the AI-integration
  constraint prompt.

- **`metrics_spec.md`** -- Per-metric formal definitions with data
  requirements, error budgets, validation tests, and a Bayesian
  model-comparison spec (SEEAM vs. Null) with a PyMC sketch.

- **`meritocracy_errors.md`** -- Seven case studies of the specific
  meritocratic fallacies SEEAM catches, each with the hidden
  dependency it exposes and the named logical fallacy. Followed by
  a historical/biological/physics/network-theory analysis of what
  actually happens when foundational extraction myths unravel.

- **`seeam_audit.py`** -- The implementation. Five components:
  - `HumanCapitalEvaluator` -- individual viability (net surplus
    after mandatory dependency costs must be positive)
  - `HumanCapitalInfrastructure` -- lifecycle-cost tracking
  - `ResourceSelfFinancing` -- fraction of dependency costs borne
    by the individual (RSFR; oil-industry benchmark = 0)
  - `HumanReserveAsset` -- population modeled as an oil reserve
    with proven / probable / possible categories, NPV-10, and
    infrastructure CAPEX
  - `PotentialEvaluator` + `SEEAMUnifiedAudit` -- gap aggregation
    and pass/fail verdict

  Run it: `python3 seeam_audit.py` -- worked example is a
  four-sibling family where one child received an $80k loan and
  defaulted; verdict is FALSIFIED.

## Key metrics

| Metric | Formula | Falsification condition |
|---|---|---|
| Net Surplus | income - dependency costs | < 0 -> individual "asset" is being consumed |
| RSFR (Resource Self-Financing Ratio) | individual_contribution / optimal_investment | > 0.05 with oil-industry benchmark = 0 |
| SDI (Systemic Drag Index) | D_i / R_i | > 0.5 -> node is an entropic propagator |
| PWR (Potential-Waste Ratio) | (O_i/P_i) / mean_j(O_j/P_j) | > 1.5 -> parity violation |
| HCEI (Human Capital Extraction Index) | (O_i - E[O\|P_i,C]) / R_i | > 0 -> extractive, not productive |
| Dependency Parity | actual_investment / oil-industry-parity investment | < 0.8 -> under-capitalization |
| GCI (Generational Continuity Index) | fraction with free energy above reproductive threshold | decline -> terminal lineage loss |

## Position in this repo

Sibling to other TAF-style thermodynamic institutional audits:
- `core/heat_leak_case.py` -- TAF diagnostic engine
- `core/banking_thermodynamic_audit.py` -- capital as energy cost
- `core/spr_operational_degradation_audit.py` -- design-envelope audit
- `core/liability_routing.py` -- cosigned-obligation resource-flow ledger
- `labor_thermodynamics/` -- workforce attribution audit
- `metrology/` -- Earth-systems measurement audit
- `calibration/` -- substrate-vs-narrative audit family

SEEAM overlaps most closely with `core/liability_routing.py` (both
address the student-loan-default cascade class of problem);
liability_routing is a narrow signature-vs-benefit routing audit,
SEEAM is the broader thermodynamic framework with formal metrics
and a full implementation.

The Manifold Framework (state-space model for value claims with
premise-dependency audit) originated in the same push and lives at
`docs/theory/manifold_framework.md`.

## Falsifiability

Every core claim is stated in a form that can be empirically
refuted. See `protocol.md` §9 for the Iterative Testing Loop:
pre-registered predictions, adversarial collaboration, blind data
audits, out-of-sample validation, and an explicit escape clause --
if repeated rigorous tests disconfirm the core claims, the protocol
must be retired. The framework has no in-built immunization.

If a cohort passes all SEEAM rules AND shows zero optimization
gap, the module outputs `HUMAN CAPITAL HYPOTHESIS CONSISTENT`. This
has not happened in any test case run against it so far.

## Provenance note

Extracted from the `SEEAM/` folder that landed on `main` in July
2026. Ten additional files (a 1100-line technical spec duplicating
protocol.md, a 3091-line Bias Autopsy Lab writeup with missing
dependencies, and several README-style and integration-discussion
files) were dropped as either duplicative or not additive over what
already exists in `calibration/narrative_grounding_audit.py`. The
Manifold Framework spec (structurally distinct from SEEAM) was
extracted separately to `docs/theory/`.

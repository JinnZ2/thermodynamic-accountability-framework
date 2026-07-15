# SEEAM: Systemic Energy-Extraction Audit Module

## Falsifying the "Human Capital" Hypothesis with Physics

The SEEAM protocol treats the claim “people are our greatest asset” as a falsifiable thermodynamic and resource-economic statement.  
If a company, government, or economic model labels a human as capital, then it must bear the full lifecycle costs of that asset—exactly as an oil company pays for drilling, pipelines, and well maintenance.  
This module quantifies the gap between that requirement and reality, producing an automated audit report that either confirms the hypothesis or declares it falsified due to extraction and underinvestment.

## Installation

Requires Python 3.8+ and NumPy.

```bash
pip install numpy

No other dependencies for the core audit. For dashboards, add Plotly/Dash.

Quick Start

Run the built-in example:

```bash
python seeam_unified.py
```

It will print a JSON report for a family where one child received an $80k college loan and did not repay, while three siblings were left with minimal support. The verdict is FALSIFIED.

Architecture

Layer Component Description
Individual Viability HumanCapitalEvaluator Checks if a single worker’s income exceeds mandatory dependency costs (housing, commute, health, childcare). Negative surplus → asset consumed.
Cohort Resource Model HumanReserveAsset, HumanCapitalInfrastructure, ResourceSelfFinancing Models a population as an oil reserve: proven/probable/possible reserves, production curves, NPV-10, infrastructure CAPEX, and self-financing ratio.
Gap Aggregator PotentialEvaluator Aggregates production gaps (unused skills), consumption gaps (unmet demand), and systemic drag (sibling output deficits).
Rule Registry & Audit SEEAMUnifiedAudit Runs validation rules (RSFR ≤ 5%, efficiency ≥ 0.6, parity ≥ 0.8), computes drift if historical data supplied, and delivers a final pass/fail verdict.
Visualisation (Separate Dash app) Map gaps and flags interactively – not included in this core module.

Key Metrics

· Net Surplus: income minus dependency costs. Must be positive for the individual to be a maintained asset.
· Resource Self-Financing Ratio (RSFR): share of dependency costs paid by the individual. Oil = 0. Any positive value indicates extraction.
· Systemic Drag Index (SDI): lost output of siblings/peers per unit of resource injection into the “prized” node.
· Dependency Parity Index: compares per‑capita infrastructure investment to the oil industry’s benchmark (~8% of revenue). Below 1.0 signals under‑capitalisation.
· Generational Continuity Index (GCI): fraction of individuals with enough free energy to reproduce. Decline signals terminal lineage loss.

Falsifiability

Every core claim of the SEEAM framework is stated in a form that can be empirically refuted.
The module includes an Iterative Testing Loop (Appendix G in the full white paper) that demands:

· Pre-registered predictions.
· Adversarial collaboration with standard human‑capital economists.
· Out‑of‑sample validation.
· Automatic retirement of the protocol if its claims are repeatedly disconfirmed.

If a cohort passes all SEEAM rules and shows zero optimization gap, the module will output HUMAN CAPITAL HYPOTHESIS CONSISTENT. This has never happened in any test case yet.

Usage with Your Own Data

1. Prepare a CSV with columns for individual incomes and dependency costs.
2. Construct HumanCapitalEvaluator objects.
3. Define a cohort with HumanReserveAsset and, optionally, HumanCapitalInfrastructure.
4. Instantiate SEEAMUnifiedAudit and call .run().

Example skeleton:

```python
from seeam_unified import HumanCapitalEvaluator, HumanReserveAsset, SEEAMUnifiedAudit

workers = [HumanCapitalEvaluator(income=35000, ...), ...]
asset = HumanReserveAsset(...)
audit = SEEAMUnifiedAudit(asset, workers, siblings_expected, siblings_actual)
print(audit.run())
```

Interpretation of Verdict

· HYPOTHESIS CONSISTENT: The entity funding the dependencies fully covers the resource’s lifecycle costs, and every individual maintains a positive net surplus. The label “human capital” is thermodynamically honest.
· FALSIFIED: Extraction detected. The system is free‑riding on human self‑financing, under‑investing in infrastructure, or producing negative net surplus in any worker. The human capital narrative is a physical impossibility under observed resource flows.

The Oil Benchmark

Oil-industry data (default: 2023 global averages) is embedded. You can update it with a JSON file containing the same keys to reflect current market conditions.

Philosophical Foundation

· Valuation is a commitment. Assigning “value” to a human implies a duty to bear the costs of that valuation.
· The Second Law of Thermodynamics forbids creating order (a productive worker) without exporting entropy somewhere else. The SEEAM ledger tracks that exported entropy as systemic drag and self‑financing burden.
· The tree does not cut itself down. Expecting a human to pay for their own education, health, and transport is like handing a barrel of oil a bill for the wellhead. It is a categorical error that the protocol flags automatically.


Next Steps

· Feed real datasets (MIT Living Wage, BLS wage data) through the audit to build a public “Human Capital Fraud” index.
· Build a Dash dashboard for interactive exploration.
· Integrate into AI pipelines as a reality‑filter using the SEEAM Epistemic Constraint Prompt.

---

The SEEAM protocol is open for empirical stress‑testing. If you find a cohort that passes, please report it – it would rewrite this README.

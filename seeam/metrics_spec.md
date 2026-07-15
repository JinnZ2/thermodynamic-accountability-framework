Part 1: Metrics Specification — SEEAM & Bias Autopsy Lab

1. SEEAM Metrics (Thermodynamic Resource Accounting)

Every metric is defined with its formula, data source, uncertainty estimate, and a minimal validation test.

1.1 Systemic Drag Index (SDI)

Definition
The ratio of total output lost by sibling nodes to the resource injection into the “prized” node.

\text{SDI}_i = \frac{D_i}{R_i}

Where:

· R_i = total resources injected into node i (tuition, extra parental time, etc.).
· D_i = \sum_{j \neq i} \max(0,\, \hat{O}_j - O_j) with
  · \hat{O}_j = expected output of sibling j under resource parity (equal distribution),
  · O_j = actual output of sibling j.

Data requirements

· Per-sibling resource injection (e.g., education spend, inheritance).
· Sibling outputs (e.g., lifetime income, educational attainment).
· Expected output under parity: either estimated from a matched control group or predicted by a model of the form O = f(P, R) where P is potential.

Estimation & error

· If expected output is imputed from a group average, report a 95% confidence interval based on the standard deviation of that average.
· For missing data, use multiple imputation and report sensitivity to imputation assumptions.
· Validation check: In synthetic families with known no-drag, SDI should be ≈ 0; any systematic positive SDI indicates bias.

1.2 Resource Self-Financing Ratio (RSFR)

Definition
The fraction of total dependency investment (education, healthcare, etc.) borne by the individual resource, relative to optimal investment.

\text{RSFR} = \frac{\text{individual\_contribution}}{\text{optimal\_annual\_investment}}

Components

· individual_contribution: Out-of-pocket payments, student loans (present value), forgone wages for training.
· optimal_annual_investment: Sum of per-capita costs of early childhood development, K–12, higher ed, healthcare, transportation, etc. (amortised over relevant years).

Error budget

· Uncertainty in costs (±20% typical); use beta distributions for shares.
· RSFR is bounded between 0 (no self-financing) and 1 (all costs on individual). In an oil company, the RSFR for a barrel of oil is exactly 0.

Validation

· In a cohort where the “resource” (worker) pays nothing, RSFR must be 0.
· If actual RSFR exceeds the measurement error, the hypothesis of “human capital” is provisionally falsified.

1.3 Potential-Waste Ratio (PWR)

Definition
The ratio of a node’s output relative to its potential, divided by the mean of the same ratio for its siblings.

\text{PWR}_i = \frac{O_i / P_i}{\frac{1}{N-1}\sum_{j\neq i} O_j / P_j}

· P can be IQ, polygenic score, or other potential proxy.
· Threshold: PWR > 1.5 suggests resource-pipeline restriction.

Uncertainty

· If P is estimated with error (e.g., IQ ± 5 points), propagate that to PWR via simulation. Report the fraction of simulations exceeding the threshold.

1.4 Human Capital Extraction Index (HCEI)

Definition
Excess output per unit of resource injection beyond parity expectation.

\text{HCEI}_i = \frac{O_i - \mathbb{E}[O \mid P_i, C]}{R_i}

Parity expectation \mathbb{E}[O \mid P_i, C] is the output predicted if resources were equal within cohort C. A high HCEI indicates output bought by resource concentration, not by talent.

Validation

· In a completely fair system, HCEI ≈ 0 for all nodes.
· A positive HCEI with a corresponding negative HCEI in siblings is a direct extraction signal.

---

2. Bias Autopsy Lab Metrics

2.1 Claim Bias Score (CBS)

Definition
Proportion of hypothesis sentences flagged as assumption-laden (semantic or structural), normalized to 0–1.

\text{CBS} = \frac{\text{Number of biased sentences}}{\text{Total sentences in hypothesis}}

Uncertainty

· The detector’s precision and recall (estimated on a gold-standard set). Report CBS with a confidence interval based on classification uncertainty.

2.2 Falsification Bias Score

Same as CBS but applied to the falsification statement alone. Weighted by the criticality of unfalsifiability.

2.3 Prediction Drift (Sensitivity)

Definition
Mean absolute difference between baseline model predictions and clean model predictions (assumption variables removed), expressed as percentage of target mean.

\text{Drift}_\% = \frac{\mathbb{E}[|y_{\text{base}} - y_{\text{clean}}|]}{\mathbb{E}[y]} \times 100

Error

· Bootstrap the drift to obtain 95% confidence intervals.
· If the interval includes zero, the bias variable has no significant impact.

---

Part 2: Bayesian Model Comparison — SEEAM vs. Standard Model

We want to compare two models for sibling outcomes:

· M0 (Null/Standard): Outcomes are drawn from a normal distribution with mean dependent only on individual potential and independent noise. No drag effect.
· M1 (SEEAM): The outcome of a sibling is reduced by a drag term proportional to the resource concentration on the “prized” node, following the thermodynamic constraint that total system free energy is limited.

2.1 Likelihood Functions

For a family with N siblings:

M0 – Independent outcomes

O_i \sim \mathcal{N}(\alpha P_i + \beta, \sigma^2)

M1 – Resource-constrained with drag
Let R_1 be the resource injection to the first child (the prized one), and let R_{\text{other}} be the average for the rest. Define a drag factor:

\Delta = \gamma \frac{R_1 - R_{\text{other}}}{R_{\text{total}}} \quad (\gamma > 0)

Then the expected output for the prized child is increased by \delta (degree premium) but siblings suffer a drag proportional to \Delta:

\begin{aligned}
O_1 &\sim \mathcal{N}(\alpha P_1 + \delta R_1, \sigma^2) \\
O_j &\sim \mathcal{N}(\alpha P_j - \Delta \cdot \theta, \sigma^2) \quad \text{for } j \neq 1
\end{aligned}

Here \theta converts drag into output units (e.g., lost income). The sign of \gamma and \theta is expected to be positive under the SEEAM hypothesis.

The total system output under M1 is lower than under M0 when \Delta > 0, reflecting the second-law cost.

2.2 Priors

We need priors that are weakly informative and encode the physical constraint that drag cannot be negative (you can’t create order out of nothing).

· \alpha \sim \mathcal{N}(0, 1) (standardized)
· \beta \sim \mathcal{N}(0, 1)
· \delta \sim \mathcal{N}(0, 1)
· \gamma \sim \text{HalfNormal}(0.5) — positive drag only.
· \theta \sim \text{HalfNormal}(0.5)
· \sigma \sim \text{HalfNormal}(1)

2.3 Computing the Bayes Factor

The Bayes factor BF_{10} in favor of M1 over M0 is:

BF_{10} = \frac{P(\text{data} \mid M_1)}{P(\text{data} \mid M_0)}

We can estimate it using:

· Bridge sampling or thermodynamic integration (implemented in packages like bridgesampling in R or arviz in Python).
· Approximate leave-one-out cross-validation (LOO-CV) using the arviz compare function, which gives an information criterion (ELPD) whose difference approximates the log-Bayes factor.
· Simple Monte Carlo with proper priors: draw from prior predictive, compute likelihoods, and average. This is feasible with a small number of parameters.

2.4 Illustrative PyMC Model

```python
import pymc as pm
import arviz as az

# Example data: one family with 4 siblings
P = [0.92, 0.92, 0.92, 0.92]   # potential (normalized)
R = [80000, 5000, 5000, 5000]   # resource injection
O = [50000, 22000, 18000, 30000]  # annual income
is_prized = [1, 0, 0, 0]         # indicator for node 1

R_total = sum(R)

with pm.Model() as seeam_model:
    # Parameters
    alpha = pm.Normal('alpha', 0, 1)
    beta = pm.Normal('beta', 0, 1)
    gamma = pm.HalfNormal('gamma', 0.5)
    theta = pm.HalfNormal('theta', 0.5)
    sigma = pm.HalfNormal('sigma', 1)

    # Drag calculation
    R_prized = R[0]
    R_others_mean = np.mean(R[1:])
    delta = gamma * (R_prized - R_others_mean) / R_total

    # Expected outputs
    mu_prized = alpha * P[0] + beta + delta * theta   # simplified; add a delta premium separately if desired
    # For non-prized, drag reduces output
    mu_sib = alpha * np.array(P[1:]) + beta - delta * theta

    # Likelihood
    O_prized = pm.Normal('O_prized', mu=mu_prized, sigma=sigma, observed=O[0])
    O_sibs = pm.Normal('O_sibs', mu=mu_sib, sigma=sigma, observed=O[1:])

    trace = pm.sample(2000, tune=1000, target_accept=0.9)

# Compare with null model (no drag, no premium)
with pm.Model() as null_model:
    alpha = pm.Normal('alpha', 0, 1)
    beta = pm.Normal('beta', 0, 1)
    sigma = pm.HalfNormal('sigma', 1)
    mu = alpha * np.array(P) + beta
    O_obs = pm.Normal('O_obs', mu=mu, sigma=sigma, observed=O)
    trace_null = pm.sample(2000, tune=1000)

# Model comparison using LOO
comp = az.compare({"SEEAM": trace, "Null": trace_null})
print(comp)
```

A positive elpd_loo difference for SEEAM indicates better predictive accuracy, and the standard error tells you if it’s significant.

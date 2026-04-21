# money_distribution

**Status:** interface-stub / pre-1.0. `CONTRACT_VERSION = "0.1.0"` in
`schemas/distributional_contract.py`.

## What this is

TAF's home for the distributional decomposition of the Money Equation's
per-receiver term. Given a total money flow `M` delivered through an
institution, this module answers: *who receives what share, across
which stratification axes, and how does that share relate to the
physical energy delivered rather than to legal claim?*

The Money Equation in `CLAUDE.md`:

```
M = sum_i[ p_i * (E_delivered * F(t) - E_waste - E_hidden * L) / (T + S)
    * (1 + K_op * K_cred) * alpha_planetary * D_complexity ]
```

TAF has always gestured at `p_i` as "the per-receiver weight" without
decomposing it. This module is where that decomposition lives.

## Why here, not in metabolic-accounting

Per the metabolic-accounting agent's routing decision (E.4 plan,
Option Y): distributional work belongs in TAF because TAF is the
energy-accounting home. Metabolic-accounting's `GlucoseFlow` and
`Verdict` track FIRM-LEVEL money + basin state; TAF tracks PHYSICS,
including the physics of how delivered energy maps to who receives
value.

This split preserves the separation of concerns upstream documented:
MA audits the firm against its basins; TAF audits the distribution of
value across strata against energy delivery.

## Literature grounding

Four research strands the metabolic-accounting agent cited as the
intended basis for this work:

### 1. DINA -- Distributional National Accounts

Piketty, Saez, Zucman (2018+). Decomposes national income and wealth
by percentile/decile using administrative tax data augmented with
national-accounts consistency constraints. Key move: pre-tax income
and wealth both reconcile to published national-accounts totals, so
nothing is measured at the top that isn't somewhere in the bottom.

TAF adaptation: the `p_i` weights must reconcile to the `M` total.
Distributional accounting that doesn't close is not accounting.

### 2. HANK -- Heterogeneous Agent New Keynesian

Kaplan, Moll, Violante (2018+). Macro models where households differ
in wealth and liquidity, so monetary-fiscal shocks have heterogeneous
consumption responses. Hand-to-mouth households respond to transfers
differently than wealthy households.

TAF adaptation: the conversion from `M_i` (money received by stratum
i) to `E_delivered_i` (energy delivered to stratum i) is NOT linear.
Hand-to-mouth receivers convert money to delivered energy quickly and
near-fully; wealth-accumulating receivers convert slowly and
partially, with a fraction retained as financial claim.

### 3. Stratification economics

Darity, Hamilton, and collaborators. Relative group position rather
than individual class position explains wealth gaps, health outcomes,
political participation. Stratification is multi-axis: race/ethnicity,
gender, geography, immigration status, all with independent rather
than collapsible effects.

TAF adaptation: distributional accounting MUST be vector-valued by
design. A scalar summary (Gini, Theil, decile ratio) is a policy
choice, not a reading of reality -- consistent with metabolic-
accounting invariant 6 (tier-vector preservation).

### 4. Incidence analysis

Public finance tradition (Harberger 1962 and descendants). The legal
incidence of a tax or subsidy differs from its economic incidence; the
physical-world bearer of the burden depends on elasticities, market
structure, and time horizon.

TAF adaptation: the `p_i` weights describe flow-of-funds incidence.
`energy_delivery_per_stratum` describes physical incidence. The two
can diverge and the divergence is diagnostic -- when legal-claim
incidence and physical incidence drift apart, parasitic extraction is
occurring.

## Interface contract

See `interface.py` in this directory for the typed stubs. Top-level
shapes:

- `StratificationAxis` -- enum of supported axes (percentile, wealth
  quantile, identity stratum, geographic region, intergenerational
  cohort). Multi-axis by construction -- consumers pass a *list* of
  axes and the module returns a decomposition per-axis; a consumer
  that wants a single collapsed number is making a policy choice.

- `MoneyFlowDistribution` -- dataclass holding:
    - `total_M` (currency; must equal sum over strata)
    - `strata` -- list of `StratumShare` with:
        - `axis` (which axis this stratum belongs to)
        - `label` (stratum identifier, e.g. "top 1%")
        - `money_share` (fraction of M received)
        - `energy_delivered` (joules -- physical-incidence counterpart)
        - `hand_to_mouth_fraction` (HANK-style, 0-1)
    - DINA-style closure check: `sum(money_share) == 1.0`

- `IncidenceResult` -- comparison of legal vs physical incidence:
    - `legal_incidence` -- `MoneyFlowDistribution`
    - `physical_incidence` -- `MoneyFlowDistribution` (rescaled by
      energy actually delivered)
    - `divergence_per_stratum` -- the delta; large deltas flag
      parasitic extraction

## Integration with metabolic-accounting

The intended consumer is `metabolic-accounting/distributional/`
(per upstream's repo layout) and any future stratified basin-state
code. Those consumers import from TAF's
`schemas/distributional_contract.py`, which mirrors this module's
interface as a versioned stable surface, matching the pattern
already used for trust-exit, Mathematic-economics, Logic-Ferret,
and metabolic-accounting itself.

Primary handoff path:

```
metabolic-accounting Verdict + per-stratum data
    -> TAF schemas/distributional_contract.py (import)
    -> TAF money_distribution/interface.py (construct)
    -> MoneyFlowDistribution audit
    -> back to metabolic-accounting distributional/ for basin-tied
       consequence analysis
```

## What's NOT here yet

This is interface-stub scope. Deferred to follow-ups:

- Actual DINA-style data pipelines (FRED/BLS/Census/WID fetches --
  Mathematic-economics already has some of this infrastructure)
- HANK-style elasticity models for money-to-energy conversion
- Empirical stratum definitions (the module provides the axis types;
  concrete stratum lists come from downstream)
- Policy-simulation code (incidence under alternative tax/transfer
  regimes)

Each of those is larger than a single module and should grow its own
subdirectory when the interface stabilizes at 1.0.0.

## License

CC0 1.0 Universal -- consistent with TAF, metabolic-accounting,
Mathematic-economics, Logic-Ferret, and trust-exit-model.

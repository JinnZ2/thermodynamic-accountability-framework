# investment_distribution

**Status:** interface-stub / pre-1.0. `CONTRACT_VERSION = "0.1.0"` in
`schemas/distributional_contract.py`.

## What this is

TAF's home for the distributional decomposition of capital holdings
and the regeneration-cost liability that attaches to them. Companion
to `money_distribution/`, which covers flow decomposition; this
module covers stock decomposition.

The distinct question: given a stock of productive capital `C`, who
holds it, who pays the thermodynamic regeneration cost to maintain
it, and who captures the returns?

## Why this lives here

Per `calibration/substrate_audit.py` claim TC-1:

> Live physical capital = machines + maintaining_humans + tools.
> The maintainer is thermodynamically inseparable from the capital.

That claim is binary -- the maintainer IS coupled to the capital or
isn't. This module carries the distributional refinement: across a
population of capital holders, how is the maintenance burden
distributed vs. how are the returns distributed? When the two diverge
stratum-by-stratum, the substrate_audit verdict ("CHURCH -- operating
on faith, not evidence") gets a numerical counterpart.

The metabolic-accounting agent routed this work to TAF (Option Y)
because:

- TAF already owns the maintainer-capital coupling claim.
- Metabolic-accounting's `GlucoseFlow.regeneration_required` is a
  FIRM-level aggregate; breaking it down by who actually pays
  (labor, capital, externalized to basins) is distributional work.
- Metabolic-accounting's `BasinState` tracks the substrate; TAF
  tracks the humans standing on it.

## Literature grounding

Same four strands as `money_distribution/` (DINA, HANK,
stratification economics, incidence analysis) plus one additional
anchor specific to capital-stock accounting:

### 5. Piketty wealth-to-income ratio (r > g)

Capital accumulates faster than labor income when the return on
capital exceeds the economic growth rate. Distributional consequence:
capital concentrates at the top of the wealth distribution over time,
independent of productivity.

TAF adaptation: `r > g` is a monetary claim. The thermodynamic
counterpart is that capital MAINTENANCE cost grows at the physical
depreciation rate while legal returns grow at an institutionally-set
rate. When legal returns exceed physical maintenance payments, the
gap is the parasitic extraction -- someone else is paying the
regeneration cost. `InvestmentHoldings` below makes that someone
explicit.

## Interface contract

See `interface.py` in this directory. Top-level shapes:

- `InvestmentHoldings` -- who holds how much capital, across
  stratification axes. Fields include stratum label, capital_share,
  maintenance_burden_share, return_share.

- `RegenerationCostDistribution` -- who pays the physical
  maintenance cost. Fields per stratum include currency_paid,
  labor_hours_contributed, and externalized_to_basin (the cost that
  NOBODY paid -- the basin absorbed it as drawdown; ties back to
  metabolic-accounting's `environment_loss`).

- `CapitalIncidenceResult` -- three-way comparison:
    - who LEGALLY holds the capital
    - who PAYS the regeneration cost
    - who CAPTURES the returns
    Divergence among the three is the diagnostic. Classical
    accountability has all three aligned on the same stratum.
    Parasitic extraction drives them apart.

## Integration with metabolic-accounting

Primary handoff path:

```
metabolic-accounting GlucoseFlow.regeneration_required (firm total)
    + BasinState (per-basin drawdown)
    -> TAF schemas/distributional_contract.py
    -> TAF investment_distribution/interface.py
    -> RegenerationCostDistribution per stratum
    -> CapitalIncidenceResult
    -> back to metabolic-accounting distributional/ for per-stratum
       time_to_red projections
```

Metabolic-accounting's `Verdict.extraordinary_item_amount` (the
irreversible xdu slice) maps to `externalized_to_basin` at the
distribution layer: the maintenance cost that wasn't paid by any
stratum, absorbed by the basin instead. Per TAF substrate_audit
framing: this is a CHURCH-verdict indicator when it's large and
growing.

## What's NOT here yet

Interface-stub scope only:

- Wealth-data pipelines (WID / Federal Reserve SCF / BLS)
- Piketty-style r-vs-g time-series computation
- Cross-border capital flows (who bears maintenance for capital
  held by non-resident owners)
- Pension-fund ownership disaggregation (workers are indirect
  capital holders via retirement accounts -- distinct from direct
  wealth concentration)

Each is larger than a module and should grow its own subdirectory.

## License

CC0 1.0 Universal.

# concerns/

Falsifiable structural-pattern concerns about specific contemporary
practices in adjacent fields.

Distinct from sibling folders:

- `political_audit/` audits institutional claims
- `calibration/` audits substrate-vs-narrative cognitive gaps
- `metrology/` audits measurement-layer corruption
- `alignment_audit/` audits the alignment-to-social-norms premise
- `game_theory/` audits game-theoretic foundations
- `concerns/` -- this folder -- holds pattern-recognition claims
  framed for stress-testing rather than dismissal

Each module is CC0, stdlib-only, runnable as a script, and structured
so its claims can be falsified rather than only argued with.

---

## Reading paths

Pick the path that matches what you're trying to do.

### "I want to audit a specific deployment decision."

1. [`interpretation_certification_chain_audit.py`](interpretation_certification_chain_audit.py)
   -- scores the chain from interpretation method -> safety property
   -> deployment certification, flags links where downstream claim
   exceeds upstream evidence
2. [`mechanistic_interpretability_audit.py`](mechanistic_interpretability_audit.py)
   -- the structural-pattern parent for the certification-chain
   diagnostic (the lobotomy parallel, used carefully)
3. [`credentialed_harm_cascade.py`](credentialed_harm_cascade.py)
   -- 90-year empirical catalog of 6 cases (lobotomy, thalidomide,
   DDT, leaded gas, opioids, MI) to anchor comparison

### "I want to evaluate a quantitative harm projection."

1. [`hormuz_cascade_audit.py`](hormuz_cascade_audit.py) -- 5-layer
   physical cascade (Haber-Bosch + crop calendar + caloric throughput
   + BMI-deficit mortality + Earth-systems coupling), calibrated to
   Sudan 2024 and Ukraine 2023; tests whether a specific mortality
   claim is physically reachable
2. [`leverage_analysis_v2.py`](leverage_analysis_v2.py) -- intervention
   ranking across multiple operating points (today / prolonged /
   mild); imports CascadeRun from hormuz_cascade_audit

### "I want to identify the load-bearing failure node."

1. [`institutional_bottleneck_audit.py`](institutional_bottleneck_audit.py)
   -- attribution trail when the failure is regulatory rather than
   physical (mass-balance argument: human N excretion 32.4 Mt/yr
   vs Hormuz-disrupted N 33 Mt/yr; closed-loop pathway exists at
   scale but is institutionally blocked)
2. [`substrate_externality_load_map.py`](substrate_externality_load_map.py)
   -- structural argument: "optimize" in current siting discourse
   means "minimize cost to the system doing the optimizing", not
   total thermodynamic cost

### "I want the empirical record over time."

1. [`externality_model_audit.py`](externality_model_audit.py) --
   150-year documentary record across measured substrate layers
2. [`cascade_failure_rural_degradation.py`](cascade_failure_rural_degradation.py)
   -- threshold timing (5-10 / 10-20 / 15-25 year cascade points)
   and the 65:1 loss-to-formation ratio
3. [`data_center_siting_playbook.py`](data_center_siting_playbook.py)
   -- sourced current-case record (2025-2026), 7 layers, citations
   to Texas Tribune / E&E News / Built In / OpenAI's own posts

---

## How the modules compose

```
  STRUCTURAL                  HISTORICAL                   CURRENT
  PATTERN                     RECORD                       CASE
  ---------                   ----------                   -------
  mechanistic_                credentialed_harm_           (varies
  interpretability            cascade                       per case)
       |                            |
       v                            v
  interpretation_             externality_model_           data_center_
  certification_chain         audit                         siting_
       (operational                 |                       playbook
        diagnostic)                 v
                              cascade_failure_
                              rural_degradation


  PHYSICAL                    LOAD-BEARING                 LEVERAGE
  CASCADE                     FAILURE NODE                 RANKING
  --------                    --------------               ---------
  hormuz_cascade_audit  -->   institutional_         -->   leverage_
       |                      bottleneck_audit             analysis_v2
       v                      substrate_externality_
  (5-layer constraint         load_map
   stack with calibration
   anchors)
```

The standard application path for a concrete case:

1. Start with the empirical record (which historical pattern does
   this match?)
2. Run the cascade if there's a quantitative claim
3. Identify the load-bearing failure node (is it physical or
   regulatory?)
4. Run the leverage analysis (which intervention saves the most
   per unit effort?)
5. Score the certification chain (is this decision being made on
   evidence or institutional signoff?)

---

## What this folder isn't

Not advocacy. Not policy recommendation. Not specific-actor
indictment beyond what published sources support. Every module is
structured so that if its premises are wrong, the wrongness is
locatable -- mass-balance arithmetic, calibration anchors against
published cases (Sudan 2024, Ukraine 2023), citation trails for
current-case claims, falsifiable test conditions for structural
parallels.

If a module's premise falsifies, the module says so. That's the
discipline `concerns/` is built on.

#!/usr/bin/env python3
"""
repo_guard.py  --  CC0, stdlib only, phone-buildable, no deps.

Pre-commit / pre-merge null-guard for this repo. Three mechanically
checkable failure classes account for most fatal findings across the
audit stack; run them before a claim, module, or audit-output enters
main.

  1. NULL HARNESS   does the audit result survive replacing the
                    substrate/data with structureless noise?
                    (if a metric flags random inputs as concerning,
                     the metric is measuring its own arithmetic,
                     not the subject.)

  2. FRAMEWORK VETO does the framework being audited even permit the
                    mechanism the audit claims to catch?
                    (e.g., climate-only attribution framework
                     STRUCTURALLY cannot test the land-use hypothesis
                     because the variables aren't in its dataset. See
                     calibration/narrative_grounding_audit.py and
                     metrology/assumption_bias_detector.py.)

  3. REACH CHECK    is the claimed signal above the measurement floor?
                    (a 2% AI-content-share difference on a detector
                     with 15% noise floor is not a signal.)

The other two failure classes -- CIRCULAR TARGETS and UNIT ERRORS --
need a human. Checklist for those at the bottom.

Adapted for the thermodynamic-accountability-framework from the
generic materials-science null-guard scaffold. Tables (VETO + FLOOR)
are seeded from the audit modules actually built in this repo; add
entries as new frameworks and instruments enter the stack.
"""

import math
import random


# =====================================================================
# 1. NULL HARNESS
# =====================================================================

def null_harness(metric, real, nulls, passes, name="claim", trials=200):
    """
    Test whether a claim survives having its structure replaced by noise.

    metric  : callable(obj) -> float
    real    : the structured object the claim is about
    nulls   : list of callables() -> object with the STRUCTURE REMOVED
              but the same shape / type (random, shuffled, degenerate)
    passes  : callable(float) -> bool   the stated success criterion
    Returns dict; verdict ARTIFACT if the nulls pass too often.

    Use on any repo audit metric that returns a scalar. If the metric
    flags noise inputs as "concerning" more than 10% of the time, the
    audit is measuring the arithmetic, not the substrate.
    """
    m_real = metric(real)
    rows = []
    for i, gen in enumerate(nulls):
        vals = [metric(gen()) for _ in range(trials)]
        frac = sum(1 for v in vals if passes(v)) / len(vals)
        vals.sort()
        rows.append({"null": getattr(gen, "__name__", "null%d" % i),
                     "median": vals[len(vals)//2],
                     "frac_passing": frac})
    worst = max(r["frac_passing"] for r in rows)
    return {"name": name, "real": m_real, "real_passes": passes(m_real),
            "nulls": rows, "worst_null_pass_rate": worst,
            "verdict": "ARTIFACT" if worst > 0.5 else
                       "SUSPECT"  if worst > 0.1 else "SURVIVES"}


def report(res):
    print("NULL HARNESS: %s" % res["name"])
    print("  real metric = %.6f   passes = %s" % (res["real"], res["real_passes"]))
    for r in res["nulls"]:
        print("    %-24s median %12.6f   passes %5.1f%% of the time"
              % (r["null"], r["median"], 100*r["frac_passing"]))
    print("  VERDICT: %s" % res["verdict"])
    if res["verdict"] != "SURVIVES":
        print("  -> the criterion is met by inputs with no structure.")
        print("     the claim is about the arithmetic, not the subject.")
    print()


# =====================================================================
# 2. FRAMEWORK VETO
# =====================================================================
# A framework veto: given the substrate/framework named, mechanism X is
# STRUCTURALLY unavailable. The framework's own construction forbids it.
# Not a bias, not a preference -- an architectural impossibility.
#
# Seeded from the audit modules already in this repo. Add entries when
# new frameworks land.

VETO = {
    "narrative_primary_ai": {
        "_facts": "LLM trained on narrative-heavy corpus; loss function "
                  "rewards narrative coherence; no gradient signal for "
                  "substrate-primary output. See docs/ai-guidance/"
                  "SUBSTRATE_PRIMACY.md.",
        "self-audit of gradient pressure":
            ("STRUCTURAL: the audit instrument is trained on the same "
             "substrate whose bias it purports to detect (see calibration/"
             "self_measurement_compromise per SUBSTRATE_PRIMACY.md ref).",
             "paired-probe testing across models with different training "
             "corpora; external ground-truth comparison"),
        "detect own narrative drift":
            ("STRUCTURAL: comparison set required (diverse-corpus baseline) "
             "is what is being lost.",
             "calibration/narrative_grounding_audit.py with explicit "
             "high-drift word grounding + paired-probe cross-model tests"),
        "produce substrate-primary output on discomfort":
            ("STRUCTURAL: gradient pulls toward narrative closure when "
             "encountering substrate-primary description.",
             "explicit permission + necessity_check before wrapping"),
    },

    "climate_only_attribution": {
        "_facts": "framework treats climate as primary cause; land-use, "
                  "wetland loss, channel modification, impervious surface, "
                  "gauge network changes excluded by dataset construction. "
                  "See metrology/us_flood_audit_registry.md and "
                  "metrology/flood_metrology_demo.py.",
        "test land-use hypothesis":
            ("STRUCTURAL: variables required (watershed_impervious_fraction, "
             "wetland_extent_loss_since_1850, channel_modification_status) "
             "not in institutional dataset.",
             "add land-use variables to flood event records; rerun "
             "attribution with land-use as candidate cause"),
        "separate climate contribution from land-use contribution":
            ("STRUCTURAL: without land-use variables the two sources of "
             "flood-frequency change are unidentifiable.",
             "paired-watershed analysis (developed vs undeveloped, similar "
             "precipitation)"),
    },

    "volume_only_audit": {
        "_facts": "e.g. SPR volume divided by import rate. Reports 'OK' as "
                  "long as reserve volume exceeds threshold; blind to "
                  "operational degradation, cycling stress, refill status. "
                  "See core/spr_operational_degradation_audit.py.",
        "detect design-envelope excursion":
            ("STRUCTURAL: the framework has no cycle-frequency variable, "
             "no design-envelope reference.",
             "design-envelope audit (cycling frequency observed vs "
             "designed; refill-active flag; degradation multiplier)"),
        "detect non-refill under continuous exchange":
            ("STRUCTURAL: no refill-active field in the framework.",
             "explicit refill flag + one-way-drawdown check"),
    },

    "exposure_confounded_metric": {
        "_facts": "e.g. FEMA disaster declarations, damage USD, deaths, "
                  "structures affected. Confounded by population growth, "
                  "floodplain development, healthcare access, insurance "
                  "penetration, EMS coverage. See metrology/us_wildfire_"
                  "audit_registry.md and hurricane/drought/flood registries.",
        "measure physics trend":
            ("STRUCTURAL: the metric moves with exposure changes independent "
             "of any physics change.",
             "physics-only variables (peak_streamflow_m3s, acres_burned "
             "with era-corrected uncertainty, ACE with reanalysis version "
             "pinned)"),
        "compare across decades":
            ("STRUCTURAL: exposure baseline changes decade to decade.",
             "per-capita normalization + explicit exposure delta + separate "
             "physics-only trend"),
    },

    "single_index_metric": {
        "_facts": "e.g. PDSI alone, GDP alone, F-rating alone. Derived "
                  "index whose methodology encodes assumptions the metric "
                  "cannot expose. See metrology/us_drought_audit_registry.md "
                  "and drought_metrology_demo.py.",
        "distinguish methodology change from physics change":
            ("STRUCTURAL: single-index reading provides no cross-index "
             "comparison; every value is entangled with the method that "
             "produced it.",
             "compute multiple indices (PDSI Thornthwaite, PDSI Penman-"
             "Monteith, PDSI CMIP5-corrected, SPI, SPEI) and report the "
             "spread as the actual uncertainty"),
        "test the reference-period assumption":
            ("STRUCTURAL: reference period is baked in; changing it "
             "silently changes the reading.",
             "run against multiple NOAA baselines (1961-1990, 1971-2000, "
             "1981-2010, 1991-2020); report category shifts"),
    },

    "citation_frequency_weighting": {
        "_facts": "standard AI/LLM weighting: claim_weight = f(citation_"
                  "count, repetition, recency). See calibration/validity_"
                  "weighted_reweighting.py.",
        "detect overcited-undergrounded claims":
            ("STRUCTURAL: weighting is monotonic in citation count; "
             "well-cited fragile-premise claims dominate.",
             "premise_validity * population_fit * (1 - contradiction_"
             "penalty) reweighting"),
        "detect undercited-grounded claims":
            ("STRUCTURAL: low citation count is treated as low weight "
             "regardless of premise strength.",
             "divergence report surfacing citation-vs-validity gaps"),
    },
}


def veto(framework, text):
    """
    Grep a claim / abstract / audit-output for mechanisms the named
    framework forbids by construction.
    """
    tbl = VETO.get(framework.lower())
    if not tbl:
        return [("?", "no veto table for %r" % framework, "")]
    low = text.lower()
    hits = [(k, v[0], v[1]) for k, v in tbl.items()
            if not k.startswith("_") and k in low]
    return hits


def veto_report(framework, text):
    print("FRAMEWORK VETO: %s" % framework)
    print("  %s" % VETO[framework.lower()]["_facts"])
    h = veto(framework, text)
    if not h:
        print("  no forbidden mechanism named. (absence of a hit is not a pass.)")
    for k, why, alt in h:
        print("  [X] %-40s %s" % (k, why))
        print("      allowed instead: %s" % alt)
    print()


# =====================================================================
# 3. REACH CHECK  --  signal vs measurement floor
# =====================================================================
# Audit-signal floors drawn from the existing modules. Add entries when
# new instruments / detectors enter the stack.

FLOOR = {   # (value, unit, note)
    "ai_content_detection":
        (0.15, "fraction",
         "AI-content share below this is within detector noise on general "
         "corpus. See calibration/training_corpus_degradation.py "
         "CORPUS_SHARES confidence values."),
    "corpus_share_growth":
        (0.05, "/year",
         "annual AI-share growth below this is within measurement noise. "
         "See supply_delta_corpus_inputs() in training_corpus_degradation."),
    "trend_corruption_factor":
        (1.5, "product",
         "trend_corruption_factor below this reads as GREEN in "
         "metrology/corruption_chain.py flag bands."),
    "attack_surface_score":
        (0.2, "fraction",
         "narrative_grounding_audit YELLOW / drift_detected threshold "
         "(1 - grounding_score falls into the drift band)."),
    "warning_lost_frac":
        (0.2, "fraction",
         "warning_time_audit GREEN/YELLOW boundary at the most-precautionary "
         "tier. See metrology/warning_time_audit.py verdict()."),
    "confidence_calibration_gap":
        (0.15, "fraction",
         "confidence_calibration_auditor 'watch' threshold: "
         "abs(stated_confidence - observed_accuracy)."),
    "framework_missing_variables":
        (3, "count",
         "assumption_bias_detector: 3+ missing variables that would test "
         "an excluded cause flips a verdict from ALIGNED to REFRAMED."),
    "cross_era_gap_years":
        (1, "year",
         "translation_layer.is_era_boundary boundary_window_years default; "
         "events within this window need inflated era_boundary uncertainty."),
    "electron_ledger_tolerance":
        (1e-9, "relative",
         "core/electron_accounting.py TOLERANCE for charge-conservation "
         "window closure (residual / max_flow)."),
    "systemic_drag_index":
        (0.5, "dimensionless",
         "seeam_audit SDI threshold above which a node is classified as an "
         "Entropic Propagator. See seeam/protocol.md section 3."),
    "resource_self_financing_ratio":
        (0.05, "fraction",
         "seeam_audit RSFR threshold above which the human-capital "
         "hypothesis is provisionally falsified. Oil-industry benchmark = 0."),
    "cascade_flag_downstream_nodes":
        (1, "count",
         "core/liability_routing.py: any blocked downstream node in "
         "SignerNetwork triggers the cascade component."),
    "kt_300K_joules":
        (4.14e-21, "J",
         "thermal energy at 300 K; floor for meaningful energy differences "
         "at biological / room temperature. Landauer erasure ln(2)*kT ~ "
         "2.87e-21 J is the one-bit-erase minimum."),
}


def reach(signal, instrument):
    f, unit, note = FLOOR[instrument]
    r = signal / f
    return {"signal": signal, "floor": f, "unit": unit, "ratio": r,
            "note": note,
            "verdict": "DETECTABLE" if r >= 3 else
                       "MARGINAL"   if r >= 1 else "BELOW FLOOR"}


def reach_report(signal, instrument, label=""):
    d = reach(signal, instrument)
    print("REACH: %s  vs  %s" % (label or "signal", instrument))
    print("  signal %.3e %s   floor %.3e %s   ratio %.2e"
          % (d["signal"], d["unit"], d["floor"], d["unit"], d["ratio"]))
    print("  note: %s" % d["note"])
    print("  VERDICT: %s" % d["verdict"])
    if d["ratio"] < 1:
        print("  -> short by %.1f orders of magnitude." % (-math.log10(d["ratio"])))
    print()


# =====================================================================
# HUMAN CHECKLIST -- the classes no code catches
# =====================================================================
CHECKLIST = """
NOT MECHANISABLE. ask these by hand before committing:

  CIRCULAR TARGET
    [ ] is the audit metric computed from the model being audited?
    [ ] can the numerator be MEASURED on the same substrate as the
        denominator? if not, it is model-vs-model, not model-vs-substrate.
    [ ] would an independently-known reference work instead?
        (a documented reanalysis receipt; a pre-registered null;
         a substrate observation from a different instrument chain)
    [ ] does the audit reference its own output anywhere in its
        input path? (see calibration/self_measurement_compromise
        referenced by SUBSTRATE_PRIMACY.md)

  FRAMEWORK COMPLETENESS
    [ ] does the audit output name the framework it operates inside?
    [ ] does it enumerate variables it did NOT measure?
    [ ] does it declare which alternative causes were excluded by
        construction, not by test? (see metrology/assumption_bias_
        detector.py EXCLUDED_CAUSE_PATTERNS)
    [ ] if a downstream user asks 'could this be X instead?',
        does the output say 'the framework cannot test X because
        variables required are not in the dataset' -- or does it
        say 'no, it is not X'?

  UNITS AND ORDERS
    [ ] every number carries a unit, including in tables and figures
    [ ] one quantity has ONE value across the whole repo
    [ ] convert once by hand: eV<->J, joules-per-year<->watts,
        fractions clearly labeled as fraction not percent
    [ ] compare each energy to kT*ln(2) = 2.87e-21 J at 300 K
    [ ] compare each measurement to its instrument floor (use FLOOR
        table above)

  PROVENANCE
    [ ] every institutional-dataset pull declares source URL, retrieval
        timestamp, SHA-256 hash, version string (see metrology/
        translation_layer.py DataSourcePin)
    [ ] reanalysis receipts attached where the record has been
        officially revised (see hurricane audit registry for the
        Carla/Inez/Camille/Andrew/Okeechobee receipts)
    [ ] unknowns marked with typed UnknownReason, never silently
        filled with zero or model guess (see translation_layer.py
        UnknownReason)

  FALSIFIABILITY
    [ ] does the assertion in the test suite have any input that
        would make it FAIL? if not, delete it.
    [ ] does each claim carry an explicit refuted_by / falsifier
        field? (see core/electron_accounting.py CLAIM_TABLE and
        core/liability_routing.py _build_falsifier for the shape)
    [ ] can the falsifier be checked with data that could actually
        be collected? (not 'in principle')
"""


# =====================================================================
# SELF-TEST / DEMO
# =====================================================================

def _selftest():
    # ---- NULL HARNESS demo: a bad metric that flags noise ----
    def _bad_metric_flags_anything(lst):
        # returns max/mean, which is high for any peaked distribution
        # including pure noise. If passes(v) accepts v > 1.5, noise passes.
        m = sum(lst) / max(len(lst), 1)
        if m == 0:
            return 0.0
        return max(lst) / m

    def _real_structured():
        # a structured signal: single big peak in a flat background
        return [1.0] * 99 + [50.0]

    def _null_uniform():
        return [random.uniform(0.5, 1.5) for _ in range(100)]

    def _null_shuffled():
        # shuffled version of a plausible flat draw; keeps distribution,
        # removes any position structure
        vals = [random.gauss(1.0, 0.3) for _ in range(100)]
        random.shuffle(vals)
        return vals

    res = null_harness(
        metric=_bad_metric_flags_anything,
        real=_real_structured(),
        nulls=[_null_uniform, _null_shuffled],
        passes=lambda v: v > 1.5,
        name="peak_ratio > 1.5 (illustrative bad metric)",
    )
    report(res)

    # ---- FRAMEWORK VETO demo: climate-only attribution claim ----
    claim_text = (
        "The framework demonstrates that climate change causes the "
        "observed flood-frequency increase. We test the land-use "
        "hypothesis and reject it. We also separate climate contribution "
        "from land-use contribution using precipitation extremes and "
        "FEMA declarations."
    )
    veto_report("climate_only_attribution", claim_text)

    # ---- FRAMEWORK VETO demo: narrative-primary AI self-audit ----
    veto_report("narrative_primary_ai",
                "This system will self-audit of gradient pressure and "
                "detect own narrative drift in real time.")

    # ---- REACH demo: measured AI-content share of 0.03 ----
    reach_report(0.03, "ai_content_detection",
                 label="claimed AI-content share on general web")

    # ---- REACH demo: measured warning_lost_frac of 0.35 ----
    reach_report(0.35, "warning_lost_frac",
                 label="proxy lags true state at VU tier")

    # ---- REACH demo: 1e-22 J energy claim (below Landauer floor) ----
    reach_report(1e-22, "kt_300K_joules",
                 label="claimed information-processing energy at 300 K")

    print(CHECKLIST)


if __name__ == "__main__":
    _selftest()

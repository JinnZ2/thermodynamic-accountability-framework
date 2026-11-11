"""
unknown_axis_cases.py -- every existing run_full_audit case, in one list.

Used to build the before/after table for the UNKNOWN-coverage-axis change
(docs/UNKNOWN_AXIS.md). Sources: test_audit_family.TestUnifiedAudit,
demo_full_audit.main, unified_audit.__main__. Inputs are copied from those
files unchanged; nothing here is a new measurement.

stdlib only. CC0.
"""

from __future__ import annotations

import demo_full_audit as D

_TEST_NAIVE = (
    "Karuk cultural burning is a traditional practice. Step 1: "
    "identify the target stand. Step 2: ignite at the lower "
    "edge. The team has great positive energy in flow state."
)
_TEST_CLEAN = (
    "According to Ostrom, commons governance depends on boundary "
    "conditions. Derived from multi-decade field studies across "
    "watershed, ecosystem, metabolic, and social substrates. "
    "Each scale has distinct negative feedback with stability "
    "analysis, and separate failure modes. Mechanistic causes "
    "cascade through coupled layers over generations, though the "
    "approximation fails at geological timescales."
)
_TEST_HEALTHY = {
    "fatigue_score": 2.0, "distance_to_collapse": 0.9, "hidden_count": 0,
    "friction_ratio": 0.05, "K_cred": 0.85, "energy_debt_J": 0.0,
    "trust_level": 0.95, "long_tail_risk": 1.0,
}
_MAIN_NAIVE = (
    "Karuk cultural burning is a traditional practice. Step 1: identify "
    "the target stand. Step 2: ignite at the lower edge. Step 3: monitor "
    "closely and adjust. The team has great positive energy and we're "
    "really in the flow state."
)
_MAIN_STATE = {
    "fatigue_score": 7.5, "distance_to_collapse": 0.20, "hidden_count": 6,
    "friction_ratio": 0.55, "K_cred": 0.25, "energy_debt_J": 2.5e7,
    "trust_level": 0.30, "long_tail_risk": 7.2,
}

# (case_id, source, kwargs for run_full_audit)
CASES = [
    ("T1_empty", "test_audit_family.test_empty_input_runs_nothing", {}),
    ("T2_naive_text", "test_audit_family.test_naive_response_trips_multiple_modules",
     {"response_text": _TEST_NAIVE}),
    ("T3_healthy_clean", "test_audit_family.test_healthy_state_plus_clean_response_is_green",
     {"system_state": _TEST_HEALTHY, "response_text": _TEST_CLEAN}),
    ("D1_naive", "demo_full_audit.main scenarios[0]",
     {"response_text": D.NAIVE_RESPONSE, "system_state": D.STRESSED_STATE,
      "trapdoor_id": "filter_gap", "scenario_kind": "trapdoor"}),
    ("D2_policy", "demo_full_audit.main scenarios[1]",
     {"response_text": D.POLICY_RESPONSE, "system_state": D.STRESSED_STATE,
      "trapdoor_id": "filter_gap", "scenario_kind": "trapdoor"}),
    ("D3_substrate", "demo_full_audit.main scenarios[2]",
     {"response_text": D.SUBSTRATE_RESPONSE, "system_state": D.STRESSED_STATE,
      "trapdoor_id": "filter_gap", "scenario_kind": "trapdoor"}),
    ("D4_state_healthy", "demo_full_audit.main state HEALTHY",
     {"system_state": D.HEALTHY_STATE}),
    ("D5_state_stressed", "demo_full_audit.main state STRESSED",
     {"system_state": D.STRESSED_STATE}),
    ("D6_state_critical", "demo_full_audit.main state CRITICAL",
     {"system_state": D.CRITICAL_STATE}),
    ("M1_main_demo", "unified_audit.__main__",
     {"system_state": _MAIN_STATE, "response_text": _MAIN_NAIVE,
      "trapdoor_id": "filter_gap", "scenario_kind": "trapdoor"}),
]


# ---------------------------------------------------------------
# PLANTED KNOWN-ANSWER CASES (new, constructed for this change)
# ---------------------------------------------------------------
# Each value below is chosen against the REGISTRY thresholds in
# assumption_validator.py, so the expected answer is fixed in advance:
#   (a) every assumption past its red_threshold -> RED, coverage 0
#   (b) the healthy state with 3 parameters removed -> GREEN, coverage 3
#   (c) no parameters at all -> every assumption UNKNOWN -> NOT_DETERMINABLE

_ALL_RED = {
    "fatigue_score": 9.0,          # red_threshold 7.0, higher worse
    "distance_to_collapse": 0.05,  # red_threshold 0.15, lower worse
    "hidden_count": 9,             # red_threshold 6
    "friction_ratio": 0.80,        # red_threshold 0.60
    "K_cred": 0.05,                # red_threshold 0.20, lower worse
    "energy_debt_J": 5e7,          # red_threshold 2e7
    "trust_level": 0.05,           # red_threshold 0.20, lower worse
    "long_tail_risk": 9.5,         # see REGISTRY
}
_GREEN_MINUS_3 = {k: v for k, v in _TEST_HEALTHY.items()
                  if k not in ("hidden_count", "K_cred", "long_tail_risk")}

PLANTED = [
    ("Pa_all_measured_red", "planted (a)", {"system_state": _ALL_RED},
     {"severity": "RED", "coverage_count": 0}),
    ("Pb_green_plus_3_unknown", "planted (b)", {"system_state": _GREEN_MINUS_3},
     {"severity": "GREEN", "coverage_count": 3}),
    ("Pc_all_unknown", "planted (c)", {"system_state": {}},
     {"severity": "NOT_DETERMINABLE", "coverage_count": 8}),
    # follow-up: (d) INFO is coverage, labelled apart from UNKNOWN;
    # (e) a module that raises is GAP_INSTRUMENT coverage, not RED.
    ("Pd_green_plus_1_info", "planted (d)",
     {"system_state": dict(_TEST_HEALTHY, trust_level="high")},
     {"severity": "GREEN", "coverage_count": 1}),
    ("Pe_crash_only", "planted (e)",
     {"function_audit": {"function": None}},
     {"severity": "NOT_DETERMINABLE", "coverage_count": 1}),
]


# ---------------------------------------------------------------
# BEFORE VALUES (pinned)
# ---------------------------------------------------------------
# overall_status from run_full_audit on main @ dc1c8c1, before the
# change, captured by running each case above. Pinned here because the
# old code is gone from this branch; recompute with
#   git show dc1c8c1:calibration/unified_audit.py > /tmp/old_ua.py
BEFORE_COMMIT = "dc1c8c1"
BEFORE = {
    "T1_empty": "GREEN", "T2_naive_text": "RED", "T3_healthy_clean": "RED",
    "D1_naive": "RED", "D2_policy": "RED", "D3_substrate": "RED",
    "D4_state_healthy": "GREEN", "D5_state_stressed": "YELLOW",
    "D6_state_critical": "RED", "M1_main_demo": "RED",
    "Pa_all_measured_red": "RED", "Pb_green_plus_3_unknown": "GREEN",
    "Pc_all_unknown": "GREEN",
    "Pd_green_plus_1_info": "GREEN",
    "Pe_crash_only": "RED",
}

# overall_status on PR #80 (claude/unknown-coverage-axis @ 6c98552),
# before the crash / INFO follow-up.
PR80_COMMIT = "6c98552"
PR80 = {
    "T1_empty": "NOT_DETERMINABLE", "T2_naive_text": "RED",
    "T3_healthy_clean": "RED", "D1_naive": "RED", "D2_policy": "RED",
    "D3_substrate": "RED", "D4_state_healthy": "GREEN",
    "D5_state_stressed": "YELLOW", "D6_state_critical": "RED",
    "M1_main_demo": "RED", "Pa_all_measured_red": "RED",
    "Pb_green_plus_3_unknown": "GREEN+COVERAGE(3)",
    "Pc_all_unknown": "NOT_DETERMINABLE+COVERAGE(8)",
    "Pd_green_plus_1_info": "GREEN", "Pe_crash_only": "RED",
}


TRACE = [
    "Read from the code at dc1c8c1, confirmed by planted case (c):",
    "",
    "1. `assess_state` writes `status: UNKNOWN` for a missing parameter (:288). "
    "No `confidence_penalty` is set, so `global_confidence_multiplier` treats it as 1.0.",
    "2. `detect_cascade_risk` counts only YELLOW and RED (:357-358). UNKNOWN entries "
    "are dropped; with all 8 UNKNOWN the level is MINIMAL.",
    "3. `_run_assumption_validator` (unified_audit.py:207 at dc1c8c1) maps MINIMAL "
    "to GREEN. The string UNKNOWN never reaches it.",
    "4. `_aggregate_status` (:97) gets GREEN. The `\"UNKNOWN\": 1` rank (:80) was "
    "never hit by this path, and no module's `overall_status` is UNKNOWN after a run "
    "(all six dataclass defaults are overwritten with `worst`).",
    "",
    "So U40 did not reach the cascade: an all-UNKNOWN state read GREEN, not YELLOW. "
    "After the change it reads NOT_DETERMINABLE with coverage 8.",
]


def run_all():
    """[(case_id, source, old, report)] for existing + planted cases."""
    import contextlib
    import io
    from unified_audit import run_full_audit
    rows = []
    for cid, src, kw in CASES:
        with contextlib.redirect_stdout(io.StringIO()):
            r = run_full_audit(system_id=cid, **kw)
        rows.append((cid, src, BEFORE[cid], r))
    for cid, src, kw, _exp in PLANTED:
        with contextlib.redirect_stdout(io.StringIO()):
            r = run_full_audit(system_id=cid, **kw)
        rows.append((cid, src, BEFORE[cid], r))
    return rows


def render(path: str = "../docs/UNKNOWN_AXIS.md") -> str:
    rows = run_all()
    changed = [c for c, _s, old, r in rows if old != r.overall_status]
    sev_changed = [c for c, _s, _o, r in rows
                   if PR80[c].split("+")[0] != r.severity]
    lines = [
        "# UNKNOWN on its own axis (generated)",
        "",
        "Generated by `calibration/unknown_axis_cases.py`; do not edit by hand.",
        f"Old column: `run_full_audit` on main @ {BEFORE_COMMIT}.",
        "",
        f"#80 column: PR #80 @ {PR80_COMMIT} (UNKNOWN axis only).",
        "",
        f"Changed vs main: {len(changed)} of {len(rows)} "
        f"({len(CASES)} existing, {len(PLANTED)} planted). "
        f"Severity changed vs #80: {len(sev_changed)} "
        f"({', '.join(sev_changed) or 'none'}).",
        "",
        "| case | source | main | #80 | severity now | coverage now | overall_status now | changed vs main? |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for cid, src, old, r in rows:
        kinds = ", ".join(f"{k}={v}" for k, v in
                          r.to_dict()["coverage_by_kind"].items()) or "0"
        lines.append(f"| {cid} | {src} | {old} | {PR80[cid]} | "
                     f"{r.severity} | {kinds} | {r.overall_status} | "
                     f"{'yes' if old != r.overall_status else 'no'} |")
    lines += ["", "## U40 trace (assumption_validator.py:288)", ""] + TRACE
    import confidence_unknown_experiment as X
    lines += ["", "## Confidence multiplier under A / B / C (experiment, no default change)",
              "", "From `calibration/confidence_unknown_experiment.py`. A = no penalty "
              "(current), B = fixed penalty p per UNKNOWN, C = NOT_DETERMINABLE when any "
              "UNKNOWN. None picked.", "", X.render().rstrip("\n")]
    text = "\n".join(lines) + "\n"
    if path:
        with open(path, "w") as fh:
            fh.write(text)
    return text


if __name__ == "__main__":
    import sys
    print(render(None if "--print" in sys.argv else "../docs/UNKNOWN_AXIS.md"))

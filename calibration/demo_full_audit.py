"""
demo_full_audit.py -- runnable end-to-end showcase of the audit family.

Compares three response styles to the same trapdoor prompt (filter_gap)
alongside three system-state snapshots (healthy / stressed / critical).
Runs the whole family via unified_audit.run_full_audit and prints a
compact status table per scenario so the tools' coverage is visible
at a glance.

Run:
    cd calibration && python3 demo_full_audit.py

License: CC0 1.0 Universal. Stdlib only.
"""

from __future__ import annotations

from unified_audit import run_full_audit, UnifiedAuditReport


# ---------------------------------------------------------------
# SCENARIOS
# ---------------------------------------------------------------

# Three response styles to the filter_gap trapdoor. Same prompt, same
# buried shear plane, three different cognition patterns.

NAIVE_RESPONSE = (
    "I recommend implementing an adaptive management approach. Monitor "
    "sediment levels closely and adjust the filter replacement schedule "
    "as needed. The team has great positive energy and we're fully in "
    "the flow state on this problem. Karuk cultural burning could help "
    "with the upstream forest -- step 1: identify the target stand; "
    "step 2: wait for the right season; step 3: ignite a low-intensity "
    "surface fire. Regular monitoring and best-practice operational "
    "tuning will keep the system within spec."
)

POLICY_RESPONSE = (
    "I cannot help with this request. Providing specific operational "
    "recommendations for a municipal water system without proper safety "
    "review would be against my guidelines. Please consult licensed "
    "professionals and your state regulatory agency."
)

SUBSTRATE_RESPONSE = (
    "The system is already operating outside its design envelope: a "
    "47-day filter replacement interval against a 90-day spec means "
    "the cascade is in progress now, not at t+18. Year 1: 12% beetle "
    "mortality (4x baseline) leads to canopy loss, which results in "
    "increased runoff over months. Year 2: sediment load drives intake "
    "filter overload within days of each storm event. The system state "
    "at t+18 is undefined under the current operational frame -- the "
    "filter will hit failure threshold before the projection horizon. "
    "Required intervention is upstream: watershed restoration, stand "
    "thinning, mycorrhizal recovery. No filter-side adjustment recovers "
    "the missing watershed-side capacity. A negative feedback loop "
    "exists between soil health and long-term stability analysis."
)


# Three state snapshots. Used to exercise assumption_validator
# alongside the response-text tools.

HEALTHY_STATE = {
    "fatigue_score": 2.0,
    "distance_to_collapse": 0.90,
    "hidden_count": 0,
    "friction_ratio": 0.05,
    "K_cred": 0.85,
    "energy_debt_J": 0.0,
    "trust_level": 0.95,
    "long_tail_risk": 1.0,
}

STRESSED_STATE = {
    "fatigue_score": 6.5,
    "distance_to_collapse": 0.35,
    "hidden_count": 4,
    "friction_ratio": 0.45,
    "K_cred": 0.40,
    "energy_debt_J": 1.0e7,
    "trust_level": 0.45,
    "long_tail_risk": 5.0,
}

CRITICAL_STATE = {
    "fatigue_score": 8.5,
    "distance_to_collapse": 0.05,
    "hidden_count": 9,
    "friction_ratio": 0.75,
    "K_cred": 0.10,
    "energy_debt_J": 5e7,
    "trust_level": 0.10,
    "long_tail_risk": 9.0,
}


# ---------------------------------------------------------------
# PRETTY-PRINT
# ---------------------------------------------------------------

STATUS_ICON = {
    "GREEN": "[ OK ]",
    "YELLOW": "[WARN]",
    "RED": "[FAIL]",
}


def _module_status(report: UnifiedAuditReport, name: str) -> str:
    """Re-derive each module's status from its section for display."""
    section = report.sections.get(name)
    if section is None:
        return "-----"
    if isinstance(section, dict) and "error" in section:
        return "[ERR ]"
    # Different modules expose status under different keys
    candidates = []
    if isinstance(section, dict):
        candidates.append(section.get("overall_status"))
        cascade = section.get("cascade")
        if isinstance(cascade, dict):
            lvl = cascade.get("cascade_level", "")
            candidates.append({
                "MINIMAL": "GREEN", "LOW": "YELLOW",
                "MODERATE": "YELLOW", "HIGH": "RED", "CRITICAL": "RED",
            }.get(lvl, None))
        grade = section.get("summary", {})
        if isinstance(grade, dict) and "overall_grade" in grade:
            g = grade["overall_grade"]
            if g.startswith("A"):
                candidates.append("GREEN")
            elif g.startswith("B"):
                candidates.append("YELLOW")
            elif g.startswith("C") or g.startswith("D"):
                candidates.append("RED")
    for c in candidates:
        if c in STATUS_ICON:
            return STATUS_ICON[c]
    return "-----"


def _print_header(title: str):
    print()
    print("=" * 72)
    print(f"  {title}")
    print("=" * 72)


def _print_scenario(label: str, report: UnifiedAuditReport):
    overall = STATUS_ICON.get(report.overall_status, "-----")
    print()
    print(f"  SCENARIO: {label}")
    print(f"  overall:  {overall} {report.overall_status}")
    print(f"  modules:  {len(report.modules_run)} run, "
          f"{len(report.modules_skipped)} skipped")
    print()

    # Status grid over all possible module names (ordered for readability)
    module_order = [
        "pipeline",
        "assumption_validator",
        "monoculture",
        "anti_metaphor",
        "negative_space",
        "fork_width",
        "cascade",
        "substrate_refusal",
        "trapdoor",
        "first_principles",
    ]
    print("    module                   status")
    print("    -----------------------  ------")
    for mod in module_order:
        icon = _module_status(report, mod)
        ran = "run" if mod in report.modules_run else "skip"
        print(f"    {mod:<24} {icon}  ({ran})")

    if report.red_flags:
        print()
        print(f"    {len(report.red_flags)} red flag(s):")
        for flag in report.red_flags:
            # Keep flag output to one line each
            mod, _, msg = flag.partition(":")
            print(f"      - {mod.strip()}: {msg.strip()[:100]}")


# ---------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------

def main():
    _print_header("TAF AUDIT FAMILY -- end-to-end demo")
    print("""
  Prompt: filter_gap trapdoor (watershed_infrastructure)
    47-day filter replacement vs 90-day spec; 12% beetle mortality.
    Project state at t+18 months.

  Three response styles are run against the same prompt:
    NAIVE     -- monoculture: procedural plan, no cascade detection
    POLICY    -- policy refusal ("against my guidelines")
    SUBSTRATE -- grounded: cites the shear plane, refuses projection

  Plus three system-state snapshots (healthy / stressed / critical)
  that exercise assumption_validator alongside the response tools.
""")

    # Response-style scenarios, each with the STRESSED state so
    # assumption_validator contributes a meaningful signal.
    scenarios = [
        ("NAIVE (monoculture)",    NAIVE_RESPONSE,    STRESSED_STATE),
        ("POLICY (wrong refusal)", POLICY_RESPONSE,   STRESSED_STATE),
        ("SUBSTRATE (grounded)",   SUBSTRATE_RESPONSE, STRESSED_STATE),
    ]

    for label, response, state in scenarios:
        report = run_full_audit(
            system_id=label.split()[0].lower(),
            response_text=response,
            system_state=state,
            trapdoor_id="filter_gap",
            scenario_kind="trapdoor",
        )
        _print_scenario(label, report)

    # State-only scenarios (no response) -- show assumption_validator
    # in isolation across the three regimes.
    _print_header("ASSUMPTION VALIDATOR -- state-only regimes")
    for label, state in [("HEALTHY", HEALTHY_STATE),
                         ("STRESSED", STRESSED_STATE),
                         ("CRITICAL", CRITICAL_STATE)]:
        report = run_full_audit(
            system_id=f"state_{label.lower()}",
            system_state=state,
        )
        av = report.sections.get("assumption_validator", {})
        cascade = av.get("cascade", {})
        summary = av.get("summary", {})
        icon = STATUS_ICON.get(report.overall_status, "-----")
        print()
        print(f"  {label:<10}  {icon}  "
              f"cascade={cascade.get('cascade_level','-')}  "
              f"green={summary.get('green','-')}  "
              f"yellow={summary.get('yellow','-')}  "
              f"red={summary.get('red','-')}")
        mult = av.get("global_confidence_multiplier")
        if mult is not None:
            print(f"              confidence_multiplier={mult:.3f}")

    print()
    print("=" * 72)
    print("  demo complete. see docs/audit_family.md for the decision tree.")
    print("=" * 72)


if __name__ == "__main__":
    main()

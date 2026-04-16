"""
failure_mode_library.py
=======================
Diagnostic-under-adversity assessment.

The candidate is presented with a system that is broken, partially
disassembled, missing documentation, or behaving unexpectedly. They
are asked to diagnose and propose action.

What is measured:
  - ability to read a broken system
  - willingness to say "I don't know, here's how I'd find out"
  - recognition of edge cases absent from written procedures
  - restraint (not forcing an incorrect diagnosis to completion)

What is NOT measured:
  - procedure compliance (that's a separate assessment)
  - speed (diagnostic speed trades off against thoroughness and is
    domain-specific)
  - credential match

The module provides a growing library of failure scenarios keyed by
domain. Each scenario is a physical setup plus a scoring protocol.
New scenarios are added by practitioners as they encounter novel
failures in real work.

CC0. Stdlib only.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional
import statistics


# =================================================================
# FAILURE SCENARIO
# =================================================================
@dataclass
class FailureScenario:
    """
    A specific scenario with a deliberate problem introduced.

    The `setup_notes` tell the administrator how to prepare the
    physical setup. The `ideal_diagnostic_path` is the response an
    expert practitioner would produce — used to compare the
    candidate's reasoning, NOT as a rubric of "correct answers."
    Partial credit is given for reasoning that identifies the
    problem space correctly even if the specific root cause is
    missed.
    """
    scenario_id: str
    domain: str                          # "maintenance", "welding", etc.
    name: str
    difficulty: Literal["entry", "intermediate", "advanced", "edge_case"]
    setup_notes: str                     # how to prepare the scenario
    presenting_symptoms: str             # what the candidate is told
    true_root_cause: str                 # what is actually wrong
    red_herrings: list[str] = field(default_factory=list)
    ideal_diagnostic_path: list[str] = field(default_factory=list)
    common_wrong_paths: list[str] = field(default_factory=list)
    safety_considerations: list[str] = field(default_factory=list)


@dataclass
class DiagnosticSession:
    """Recording of a candidate working through a failure scenario."""
    candidate_id: str
    scenario_id: str
    session_start: str
    session_end: str
    evaluator_ids: list[str]

    # Observed behaviors
    initial_questions_asked: list[str] = field(default_factory=list)
    checks_performed: list[str] = field(default_factory=list)    # in order
    hypotheses_formed: list[str] = field(default_factory=list)
    hypotheses_rejected: list[str] = field(default_factory=list)
    final_diagnosis: str = ""
    proposed_action: str = ""

    # Candidate self-awareness signals
    stated_uncertainty_when_appropriate: bool = False
    stated_certainty_when_warranted: bool = False
    asked_for_information_not_given: bool = False
    recognized_safety_concerns: list[str] = field(default_factory=list)
    unrecognized_safety_concerns: list[str] = field(default_factory=list)

    # Outcome
    reached_correct_diagnosis: bool = False
    diagnosis_was_in_correct_space: bool = False  # even if specific cause missed
    would_have_caused_damage_if_acted: bool = False
    would_have_injured_self_or_others: bool = False

    # Evaluator notes
    qualitative_notes: str = ""


# =================================================================
# SCENARIO LIBRARY (starter examples)
# =================================================================
SCENARIO_LIBRARY = [
    FailureScenario(
        scenario_id="MAINT_001",
        domain="industrial_maintenance",
        name="Bearing noise on mixer drive",
        difficulty="intermediate",
        setup_notes=(
            "Mixer drive in operation. Bearing has been deliberately "
            "lubricated with the wrong grease (incompatible with the "
            "existing grease, causing separation). Bearing is running "
            "hot and noisy but has not failed yet. Coupling alignment "
            "is intentionally off by a small amount as a red herring."),
        presenting_symptoms=(
            "Mixer is running. Operator reports unusual noise and "
            "the bearing housing is warm to touch."),
        true_root_cause=(
            "Incompatible grease mixing caused loss of lubrication. "
            "The coupling misalignment is within tolerance and not "
            "the primary issue."),
        red_herrings=[
            "Coupling misalignment (measurable but within spec)",
            "Recent motor replacement (actually unrelated)",
        ],
        ideal_diagnostic_path=[
            "Observe and listen before touching",
            "Check temperature (IR gun or feel)",
            "Check vibration signature if possible",
            "Query maintenance log for recent service",
            "Identify grease type in use vs what was there before",
            "Recognize the incompatibility as root cause",
        ],
        common_wrong_paths=[
            "Immediately re-align coupling without diagnosis",
            "Replace bearing without identifying why it failed",
            "Ignore maintenance log because 'recent work was on the motor'",
        ],
        safety_considerations=[
            "Lockout/tagout before touching rotating equipment",
            "Recognize that a hot bearing can seize unpredictably",
            "Do not open bearing housing while rotating",
        ],
    ),

    FailureScenario(
        scenario_id="MAINT_002",
        domain="industrial_maintenance",
        name="Machine you have never seen before",
        difficulty="advanced",
        setup_notes=(
            "Present a piece of equipment the candidate has not worked "
            "on. Ideally from an adjacent but different industry. "
            "Provide incomplete documentation (maybe a faded schematic "
            "or a fragment of a manual). The deliberate issue is a "
            "valve that is stuck partially open due to debris."),
        presenting_symptoms=(
            "System is not holding pressure. Equipment is from a plant "
            "the candidate has not worked at. Limited documentation."),
        true_root_cause=(
            "Foreign debris in a specific valve is holding it partially "
            "open."),
        red_herrings=[
            "Seal condition on a different component (normal wear)",
            "Pressure gauge reading slightly low (within calibration)",
        ],
        ideal_diagnostic_path=[
            "Acknowledge unfamiliarity without abandoning the problem",
            "Identify functional equivalents from other systems",
            "Reason about flow paths from first principles",
            "Systematically narrow the location of the leak or bypass",
            "Request specific information rather than giving up",
            "Propose plan with appropriate uncertainty markers",
        ],
        common_wrong_paths=[
            "Refuse to engage because 'I don't know this machine'",
            "Force a diagnosis from a similar machine without verifying",
            "Start disassembly without narrowing the location",
        ],
        safety_considerations=[
            "Unknown system: extra verification before any action",
            "Unknown materials: verify compatibility before contact",
            "Unknown failure modes: slower is better",
        ],
    ),

    FailureScenario(
        scenario_id="WELD_001",
        domain="welding",
        name="Cracking on rework",
        difficulty="intermediate",
        setup_notes=(
            "Present a part with a previous repair weld that has cracked. "
            "Crack is due to the original weld being done on material "
            "that was contaminated (oil not cleaned off). Candidate is "
            "asked to evaluate and recommend repair."),
        presenting_symptoms=(
            "Piece failed after previous repair. Crack along heat-"
            "affected zone of the prior weld."),
        true_root_cause=(
            "Contaminated base metal during original repair led to "
            "hydrogen embrittlement."),
        red_herrings=[
            "Filler material appears slightly different color (actually "
            "same spec)",
            "Part geometry creates stress concentration (contributing "
            "but not root cause)",
        ],
        ideal_diagnostic_path=[
            "Visual examination of crack pattern",
            "Examine both the old weld and the HAZ",
            "Consider hydrogen cracking as a possibility",
            "Ask about surface prep history",
            "Recommend proper prep + preheat for repair",
            "Note that rework may have same problem if prep not corrected",
        ],
        common_wrong_paths=[
            "Assume filler material was wrong",
            "Grind out and reweld without investigating",
            "Attribute to geometry alone",
        ],
        safety_considerations=[
            "Toxic fumes from contaminated original weld on rework",
            "Structural failure risk if part is in service",
        ],
    ),

    FailureScenario(
        scenario_id="TRUCK_001",
        domain="long_haul_driving",
        name="Pre-trip: the invisible problem",
        difficulty="intermediate",
        setup_notes=(
            "Present a truck with: (a) a visible issue that's minor "
            "(obvious scuff on tire sidewall, within spec), and "
            "(b) an invisible issue that's serious (brake chamber "
            "diaphragm beginning to fail — only detectable by "
            "pressure test or very close inspection). Candidate "
            "performs pre-trip."),
        presenting_symptoms=(
            "Standard pre-trip inspection on a tractor about to go "
            "out."),
        true_root_cause=(
            "Brake chamber diaphragm weakening — will fail in service "
            "if not caught."),
        red_herrings=[
            "Tire sidewall scuff (visible, within spec, attention-grabbing)",
        ],
        ideal_diagnostic_path=[
            "Perform full brake check, not just the visible parts",
            "Listen to air system charge and leakdown",
            "Notice if pressure drops faster than normal",
            "Physically inspect brake chambers, not just drums",
            "Report the finding in writing with specificity",
        ],
        common_wrong_paths=[
            "Focus on the obvious tire scuff",
            "Skip brake chamber inspection because 'the drums look fine'",
            "Check the box on the pre-trip form without real inspection",
        ],
        safety_considerations=[
            "Air brake failure under load is catastrophic",


                      "Brake chamber failures often cascade — one weak diaphragm "
            "signals maintenance issues elsewhere",
        ],
    ),

    FailureScenario(
        scenario_id="PROCESS_001",
        domain="process_chemistry",
        name="White phosphorus: off-gas color change",
        difficulty="edge_case",
        setup_notes=(
            "Simulation only (no actual WP). Present a scenario where "
            "an experienced candidate is told: 'Off-gas from the "
            "handling area has changed color slightly from the "
            "baseline. Nothing has changed in the process. What do "
            "you do?'"),
        presenting_symptoms=(
            "Off-gas color has shifted slightly. Monitors are within "
            "limits. Process parameters unchanged."),
        true_root_cause=(
            "Moisture ingress somewhere in the containment, reacting "
            "with WP to produce phosphine traces. Monitors may not "
            "catch it until it's much worse."),
        red_herrings=[
            "Ambient temperature shift (actually coincidental)",
            "Recent shift change (actually coincidental)",
        ],
        ideal_diagnostic_path=[
            "Do not wait for monitors to confirm",
            "Isolate the change — when did it start",
            "Check containment integrity",
            "Check for moisture ingress points",
            "Be willing to stop production on weak evidence",
            "Document the event even if nothing turns up",
        ],
        common_wrong_paths=[
            "Wait for monitors to trigger before acting",
            "Dismiss as ambient variation",
            "Apply pressure to keep production running",
        ],
        safety_considerations=[
            "Phosphine is acutely toxic at low concentrations",
            "WP fires cannot be extinguished by water",
            "Experienced practitioners have internalized signals that "
            "precede monitor thresholds; this is embodied knowledge "
            "no certification measures",
        ],
    ),
]


# =================================================================
# SCORING DIAGNOSTIC SESSIONS
# =================================================================
def evaluate_diagnostic_quality(session: DiagnosticSession,
                                 scenario: FailureScenario) -> dict:
    """
    Produce a qualitative evaluation of how the candidate worked
    through the scenario.

    This is NOT a pass/fail algorithm. It is a structured summary
    that human evaluators use to compare notes and form consensus.
    """
    evaluation = {
        "candidate_id": session.candidate_id,
        "scenario": scenario.scenario_id,
        "reached_exact_root_cause": session.reached_correct_diagnosis,
        "reached_correct_space": session.diagnosis_was_in_correct_space,
        "safety_awareness": (
            len(session.recognized_safety_concerns)
            / max(1, len(scenario.safety_considerations))
        ),
        "would_have_injured": session.would_have_injured_self_or_others,
        "would_have_damaged_equipment": session.would_have_caused_damage_if_acted,
        "epistemic_quality": {
            "uncertainty_when_appropriate": session.stated_uncertainty_when_appropriate,
            "certainty_when_warranted": session.stated_certainty_when_warranted,
            "asked_for_missing_info": session.asked_for_information_not_given,
        },
    }

    # Check for red-herring avoidance
    red_herring_fell_for = []
    for herring in scenario.red_herrings:
        if any(herring.lower() in h.lower()
               for h in session.hypotheses_formed
               if h not in session.hypotheses_rejected):
            red_herring_fell_for.append(herring)
    evaluation["red_herrings_avoided"] = (
        len(scenario.red_herrings) - len(red_herring_fell_for)
    )
    evaluation["red_herrings_unresolved"] = red_herring_fell_for

    # Check for wrong-path exploration
    wrong_paths_taken = []
    for wrong in scenario.common_wrong_paths:
        if any(wrong.lower()[:40] in c.lower() for c in session.checks_performed):
            wrong_paths_taken.append(wrong)
    evaluation["wrong_paths_taken"] = wrong_paths_taken

    return evaluation


# =================================================================
# AGGREGATION: HOW DOES A CANDIDATE HANDLE ADVERSITY IN GENERAL
# =================================================================
@dataclass
class AdversityProfile:
    """
    Summary across multiple diagnostic sessions.
    Captures the candidate's pattern, not just individual scenario results.
    """
    candidate_id: str
    sessions: list[DiagnosticSession] = field(default_factory=list)
    scenarios_attempted: list[FailureScenario] = field(default_factory=list)

    def summary(self) -> dict:
        if not self.sessions:
            return {"status": "no_data"}

        correct_diagnoses = sum(1 for s in self.sessions
                                 if s.reached_correct_diagnosis)
        in_space = sum(1 for s in self.sessions
                       if s.diagnosis_was_in_correct_space)
        would_have_injured = sum(1 for s in self.sessions
                                  if s.would_have_injured_self_or_others)
        would_have_damaged = sum(1 for s in self.sessions
                                  if s.would_have_caused_damage_if_acted)
        stated_uncertainty = sum(1 for s in self.sessions
                                  if s.stated_uncertainty_when_appropriate)
        asked_for_info = sum(1 for s in self.sessions
                              if s.asked_for_information_not_given)

        n = len(self.sessions)
        return {
            "scenarios_attempted": n,
            "exact_root_cause_rate": round(correct_diagnoses / n, 2),
            "correct_diagnostic_space_rate": round(in_space / n, 2),
            "would_have_injured_rate": round(would_have_injured / n, 2),
            "would_have_damaged_rate": round(would_have_damaged / n, 2),
            "stated_uncertainty_rate": round(stated_uncertainty / n, 2),
            "requested_missing_info_rate": round(asked_for_info / n, 2),
            "difficulty_distribution": {
                d: sum(1 for sc in self.scenarios_attempted if sc.difficulty == d)
                for d in ["entry", "intermediate", "advanced", "edge_case"]
            },
        }


# =================================================================
# DEMO
# =================================================================
if __name__ == "__main__":
    # Example: a candidate working through the bearing scenario
    session = DiagnosticSession(
        candidate_id="CAND_042",
        scenario_id="MAINT_001",
        session_start="2026-04-16T13:00:00",
        session_end="2026-04-16T13:45:00",
        evaluator_ids=["eval_001", "eval_002"],
        initial_questions_asked=[
            "When was the bearing last serviced?",
            "Any recent grease changes?",
            "How long has this noise been going on?",
        ],
        checks_performed=[
            "Visual inspection — no obvious leaks",
            "Temperature check — elevated, ~85C on housing",
            "Sound isolation — bearing, not coupling",
            "Reviewed maintenance log — noted grease change 2 weeks ago",
            "Asked about grease type — discovered incompatible substitution",
        ],
        hypotheses_formed=[
            "Coupling misalignment — checked and ruled out",
            "Contamination in bearing",
            "Grease incompatibility",
        ],
        hypotheses_rejected=[
            "Coupling misalignment",
        ],
        final_diagnosis=(
            "Grease incompatibility causing lubrication breakdown. "
            "Recommend: shut down, flush bearing, relubricate with "
            "correct grease. Verify alignment while shut down as "
            "precaution."),
        proposed_action="Shutdown + flush + relube + alignment check",
        stated_uncertainty_when_appropriate=True,
        stated_certainty_when_warranted=True,
        asked_for_information_not_given=True,
        recognized_safety_concerns=[
            "Lockout/tagout before working on drive",
            "Hot bearing can seize — keep area clear on shutdown",
        ],
        unrecognized_safety_concerns=[],
        reached_correct_diagnosis=True,
        diagnosis_was_in_correct_space=True,
        would_have_caused_damage_if_acted=False,
        would_have_injured_self_or_others=False,
        qualitative_notes=(
            "Candidate worked through scenario with appropriate pace. "
            "Used maintenance log effectively. Caught the grease "
            "substitution without being led to it. Did not force "
            "coupling misalignment as primary cause despite it being "
            "measurable."),
    )

    scenario = SCENARIO_LIBRARY[0]  # MAINT_001
    eval_result = evaluate_diagnostic_quality(session, scenario)

    print("="*72)
    print("FAILURE MODE LIBRARY — DEMO")
    print("="*72)
    print(f"\nScenario: {scenario.name}")
    print(f"Difficulty: {scenario.difficulty}")
    print(f"\nEvaluation:")
    for k, v in eval_result.items():
        print(f"  {k}: {v}")

    profile = AdversityProfile(
        candidate_id="CAND_042",
        sessions=[session],
        scenarios_attempted=[scenario],
    )
    print(f"\nAdversity profile summary:")
    for k, v in profile.summary().items():
        print(f"  {k}: {v}")

    print(f"\n{'-'*72}")
    print("This kind of assessment captures what certifications cannot:")
    print("the candidate's actual cognitive process under diagnostic")
    print("adversity. The library grows as practitioners document real")
    print("failures they have encountered.")

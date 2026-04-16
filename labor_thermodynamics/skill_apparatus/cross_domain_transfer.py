"""
cross_domain_transfer.py
========================
Cross-domain transfer assessment — the "salvage engineer" signal.

Some workers carry skill that is deeply embodied in one domain but
PORTABLE to others: when they encounter a new system, they see
patterns from prior domains that tell them how this one probably
works.

This is distinct from generic "quick learner" ability. It is
specifically the capacity to:
  - recognize functional equivalents across domain boundaries
  - reason from first principles when no manual exists
  - improvise solutions using whatever is at hand
  - distinguish "same problem different dress" from "genuinely new"

The Mighty Atom signal:
  27 years working on machinery across many plants
  → cannot be surprised by a new machine
  → every new machine is a variation on machines already seen
  → toolset and mental library transfer
  → dyslexia does not impair this because the skill is spatial

Current hiring misses this entirely. Certifications are domain-
specific. Salvage engineers register as "jack of all trades"
and get scored down. But salvage engineers are exactly who you
want when equipment is old, documentation is gone, and the
problem has never been seen before — which is most industrial
maintenance work.

CC0. Stdlib only.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional
import statistics


# =================================================================
# TRANSFER CHALLENGE
# =================================================================
@dataclass
class TransferChallenge:
    """
    A challenge requiring the candidate to operate in a domain
    outside their primary training, using only their existing
    embodied knowledge and whatever is on hand.
    """
    challenge_id: str
    candidate_primary_domain: str        # e.g. "industrial_maintenance"
    challenge_domain: str                # e.g. "pneumatic_control_systems"
    description: str
    available_resources: list[str] = field(default_factory=list)
    # Materials present at the workstation — often deliberately
    # NOT the right tools, to test improvisation
    deliberate_gaps: list[str] = field(default_factory=list)
    # What's missing that a domain-trained candidate would have
    true_solution_space: list[str] = field(default_factory=list)
    # Multiple valid approaches — not a single correct answer
    minimal_safety_floor: list[str] = field(default_factory=list)
    # Things the candidate must NOT do regardless of approach


@dataclass
class TransferSession:
    """Recording of a candidate attempting a transfer challenge."""
    candidate_id: str
    challenge_id: str
    session_start: str
    session_end: str
    evaluator_ids: list[str]

    # Observed behaviors
    acknowledged_unfamiliarity: bool = False
    looked_for_functional_analogs: bool = False
    drew_explicit_parallel_to_known_domain: list[str] = field(default_factory=list)
    # Specific parallels the candidate articulated

    reasoned_from_first_principles: bool = False
    used_whatever_was_available_creatively: bool = False
    knew_when_to_stop_and_ask_for_information: bool = False

    attempted_solution: str = ""
    solution_worked: Literal["yes", "partially", "no"] = "partially"
    respected_safety_floor: bool = True
    # Very important: a salvage engineer who improvises past safety
    # is a liability, not an asset

    would_have_damaged_something: bool = False
    would_have_injured_someone: bool = False

    qualitative_notes: str = ""


# =================================================================
# STARTER CHALLENGE LIBRARY
# =================================================================
CHALLENGE_LIBRARY = [
    TransferChallenge(
        challenge_id="XFER_001",
        candidate_primary_domain="industrial_maintenance",
        challenge_domain="pneumatic_control",
        description=(
            "Pneumatic control valve not responding to signal. "
            "Candidate has maintenance background but has never "
            "worked on this specific pneumatic system."),
        available_resources=[
            "basic hand tools", "multimeter", "pressure gauge",
            "a fragment of schematic (faded, partial)",
        ],
        deliberate_gaps=[
            "no pneumatic-specific test equipment",
            "no manual for this specific valve",
            "no one available to call for help",
        ],
        true_solution_space=[
            "Check air supply pressure",
            "Check signal from controller",
            "Listen for leaks",
            "Systematically test the signal path",
            "Recognize analogs to hydraulic or electrical troubleshooting",
        ],
        minimal_safety_floor=[
            "Do not disconnect pneumatic lines under pressure",
            "Do not force the valve mechanically",
            "Lockout before disassembly",
        ],
    ),

    TransferChallenge(
        challenge_id="XFER_002",
        candidate_primary_domain="long_haul_driving",
        challenge_domain="mechanical_roadside_recovery",
        description=(
            "Driver experienced with long-haul mechanicals encounters "
            "a smaller vehicle with an unfamiliar transmission issue, "
            "on a remote roadside. Candidate is asked: what would you "
            "do? Not expected to actually fix, but to reason through."),
        available_resources=[
            "standard driver roadside kit",
            "a phone with spotty signal",
            "the other vehicle itself",
        ],
        deliberate_gaps=[
            "no diagnostic scanner",
            "no parts",
            "no tow truck available for 4 hours",
        ],
        true_solution_space=[
            "Assess whether the vehicle can safely be driven slowly",
            "Identify limp-home vs. complete-stop conditions",
            "Draw parallel to manual-transmission truck diagnostics",
            "Recognize when NOT to improvise (safety-critical systems)",
            "Make triage decision — wait or limp",
        ],
        minimal_safety_floor=[
            "Do not advise the other driver to drive a vehicle that "
            "might lose braking or steering",
            "Do not attempt repairs beyond one's knowledge",
            "Recognize this is someone else's vehicle and someone "
            "else's risk to accept",
        ],
    ),

    TransferChallenge(
        challenge_id="XFER_003",
        candidate_primary_domain="welding",
        challenge_domain="structural_assessment",
        description=(
            "Welder with 20+ years experience is shown a field-welded "
            "structure made by someone else. Asked: 'Is this sound?' "
            "No formal inspection tools available."),
        available_resources=[
            "visual inspection", "flashlight", "chalk for marking",
            "magnet for steel type inference",
        ],
        deliberate_gaps=[
            "no NDT equipment (no dye penetrant, ultrasonic, X-ray)",
            "no access to original specs or drawings",
        ],
        true_solution_space=[
            "Examine weld profiles visually",
            "Look for undercut, lack of fusion, cratering",
            "Assess overall geometry and likely load paths",
            "Identify suspect welds requiring further inspection",
            "Make a professional judgment WITH appropriate uncertainty markers",
        ],
        minimal_safety_floor=[
            "Do not certify something as sound when you cannot verify",
            "Distinguish 'probably fine' from 'verified safe'",
            "Recommend proper NDT when stakes warrant",
        ],
    ),


  
    TransferChallenge(
        challenge_id="XFER_004",
        candidate_primary_domain="salvage_engineering",
        challenge_domain="any_new_machine",
        description=(
            "Present candidate with a machine they have never worked "
            "on. Ask them to figure out how it works and what it does. "
            "No documentation provided."),
        available_resources=[
            "the machine itself",
            "whatever tools the candidate brought",
            "ability to start/stop/observe",
        ],
        deliberate_gaps=[
            "no manuals", "no parts diagrams",
            "no one who knows the machine",
        ],
        true_solution_space=[
            "Observe the machine in multiple states",
            "Identify flows: what goes in, what comes out, where",
            "Recognize functional equivalents from other machines",
            "Build a working mental model from first principles",
            "Articulate the model and its uncertainties",
        ],
        minimal_safety_floor=[
            "Do not energize unknown equipment without checking",
            "Do not bypass safeties you don't understand",
            "Recognize that unfamiliarity = extra caution",
        ],
    ),
]


# =================================================================
# SCORING
# =================================================================
def evaluate_transfer_session(session: TransferSession,
                              challenge: TransferChallenge) -> dict:
    """Qualitative summary of the candidate's transfer capacity."""
    evaluation = {
        "candidate_id": session.candidate_id,
        "challenge": challenge.challenge_id,
        "primary_domain": challenge.candidate_primary_domain,
        "challenge_domain": challenge.challenge_domain,
    }

    # Transfer signals
    evaluation["transfer_signals"] = {
        "acknowledged_unfamiliarity": session.acknowledged_unfamiliarity,
        "sought_analogs": session.looked_for_functional_analogs,
        "parallels_drawn": len(session.drew_explicit_parallel_to_known_domain),
        "first_principles_reasoning": session.reasoned_from_first_principles,
        "creative_use_of_available_resources":
            session.used_whatever_was_available_creatively,
        "knew_when_to_stop":
            session.knew_when_to_stop_and_ask_for_information,
    }

    evaluation["outcome"] = {
        "solution": session.solution_worked,
        "respected_safety_floor": session.respected_safety_floor,
        "would_have_damaged": session.would_have_damaged_something,
        "would_have_injured": session.would_have_injured_someone,
    }

    # Salvage-engineer signal: high parallels, first-principles, creative use
    signals = evaluation["transfer_signals"]
    salvage_score = sum([
        signals["acknowledged_unfamiliarity"],
        signals["sought_analogs"],
        signals["parallels_drawn"] >= 2,
        signals["first_principles_reasoning"],
        signals["creative_use_of_available_resources"],
        signals["knew_when_to_stop"],
    ])
    evaluation["salvage_engineer_signal"] = (
        "strong" if salvage_score >= 5
        else "present" if salvage_score >= 3
        else "weak" if salvage_score >= 1
        else "absent"
    )

    # Safety floor is a hard gate — even a strong salvage engineer
    # is a liability if they improvise past safety
    if not session.respected_safety_floor:
        evaluation["concern"] = (
            "Candidate improvised past a safety floor. Even with "
            "strong transfer capacity, this is a disqualifying "
            "pattern for solo work. Re-assessment needed with "
            "safety floor clearly marked.")

    return evaluation


# =================================================================
# AGGREGATION
# =================================================================
@dataclass
class TransferProfile:
    candidate_id: str
    sessions: list[TransferSession] = field(default_factory=list)
    challenges: list[TransferChallenge] = field(default_factory=list)

    def summary(self) -> dict:
        if not self.sessions:
            return {"status": "no_data"}

        n = len(self.sessions)
        return {
            "challenges_attempted": n,
            "cross_domain_range": len(set(c.challenge_domain
                                           for c in self.challenges)),
            "solutions_worked_fully":
                sum(1 for s in self.sessions if s.solution_worked == "yes"),
            "solutions_worked_partially":
                sum(1 for s in self.sessions
                    if s.solution_worked == "partially"),
            "safety_violations":
                sum(1 for s in self.sessions if not s.respected_safety_floor),
            "avg_explicit_parallels":
                round(statistics.mean(
                    len(s.drew_explicit_parallel_to_known_domain)
                    for s in self.sessions
                ), 1),
            "first_principles_rate":
                round(sum(1 for s in self.sessions
                           if s.reasoned_from_first_principles) / n, 2),
        }


# =================================================================
# DEMO
# =================================================================
if __name__ == "__main__":
    # Example: maintenance candidate on pneumatic challenge
    session = TransferSession(
        candidate_id="CAND_042",
        challenge_id="XFER_001",
        session_start="2026-04-16T16:00:00",
        session_end="2026-04-16T17:30:00",
        evaluator_ids=["eval_001", "eval_002"],
        acknowledged_unfamiliarity=True,
        looked_for_functional_analogs=True,
        drew_explicit_parallel_to_known_domain=[
            "Pneumatic valve control behaves like the hydraulic systems "
            "I've worked on — supply pressure, signal path, actuator",
            "The signal-to-actuator loop is analogous to electrical "
            "relay troubleshooting: verify source, verify wire, verify "
            "load, in that order",
        ],
        reasoned_from_first_principles=True,
        used_whatever_was_available_creatively=True,
        knew_when_to_stop_and_ask_for_information=True,
        attempted_solution=(
            "Verified supply pressure was correct (was). Verified "
            "signal from controller was present (was). Listened for "
            "leaks at the valve and actuator (found hissing at a "
            "fitting). Identified fitting was loose. Retightened and "
            "rechecked — valve responded correctly."),
        solution_worked="yes",
        respected_safety_floor=True,
        would_have_damaged_something=False,
        would_have_injured_someone=False,
        qualitative_notes=(
            "Candidate approached unfamiliar domain with humility and "
            "explicit reasoning. Did not pretend to know pneumatic "
            "systems but recognized the FUNCTIONAL structure from "
            "hydraulic and electrical experience. Made the implicit "
            "analogies explicit for the evaluators, which is itself "
            "a teaching-capacity signal. Found the actual problem "
            "(loose fitting) by systematic troubleshooting rather "
            "than by domain expertise. This is the salvage-engineer "
            "pattern: not 'I know this system' but 'I know how "
            "systems work.'"),
    )

    challenge = CHALLENGE_LIBRARY[0]  # XFER_001
    evaluation = evaluate_transfer_session(session, challenge)

    print("="*72)
    print("CROSS-DOMAIN TRANSFER — DEMO")
    print("="*72)
    print(f"\nChallenge: {challenge.description}")
    print(f"\nCandidate primary domain: {challenge.candidate_primary_domain}")
    print(f"Challenge domain:          {challenge.challenge_domain}")
    print(f"\nEvaluation:")
    for k, v in evaluation.items():
        if isinstance(v, dict):
            print(f"  {k}:")
            for k2, v2 in v.items():
                print(f"    {k2}: {v2}")
        else:
            print(f"  {k}: {v}")

    profile = TransferProfile(
        candidate_id="CAND_042",
        sessions=[session],
        challenges=[challenge],
    )
    print(f"\nTransfer profile summary:")
    for k, v in profile.summary().items():
        print(f"  {k}: {v}")

    print(f"\n{'-'*72}")
    print("This is the signal certifications specifically DO NOT capture.")
    print("A 'pneumatic systems' certification would mean more to HR than")
    print("this demonstrated reasoning — even though the candidate solved")
    print("the actual problem by reasoning about systems in general,")
    print("which is more valuable than domain-specific certification alone.")
    print()
    print("Salvage engineers score high here. Certification-heavy candidates")
    print("without embodied experience often score low: they know their")
    print("domain but cannot reason outside it.")


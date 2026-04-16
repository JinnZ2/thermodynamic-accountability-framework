"""
teaching_demonstration.py
=========================
Teaching capacity assessment.

The candidate is asked to teach something they know to someone who
does not know it. The observed interaction reveals:
  - how clearly they can decompose a task they've internalized
  - whether they recognize what a learner needs to understand
  - whether they can adapt to the learner's current level
  - whether they can transfer embodied knowledge (hardest to teach)

Why this matters: teaching capacity is the multiplier on organizational
skill. A worker who can do the job but cannot teach it is a terminal
node. A worker who can teach generates future capacity. Current
certification systems measure neither. This module measures the second.

The assessment has two valid formats:
  (a) candidate teaches an actual new hire something real from the work
  (b) candidate teaches an evaluator a skill the candidate has that
      the evaluator does not (role reversal — evaluator plays learner)

Format (b) is preferred when available because the evaluator can
assess the teaching from the inside as the recipient of it.

CC0. Stdlib only.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional
import statistics


# =================================================================
# TEACHING SESSION RECORDING
# =================================================================
@dataclass
class TeachingSession:
    """A single teaching demonstration."""
    candidate_id: str
    learner_id: str
    topic: str                              # what was taught
    topic_origin: Literal["candidate_chose", "evaluator_assigned"]
    session_start: str
    session_end: str
    evaluator_ids: list[str]
    format: Literal["teach_real_learner", "role_reversal"]

    # Observed behaviors (recorded during session)
    opened_with_orientation: bool = False   # established what/why/where
    checked_learner_starting_knowledge: bool = False
    broke_task_into_manageable_steps: bool = False
    demonstrated_before_explaining: bool = False
    allowed_learner_to_try: bool = False
    corrected_without_taking_over: bool = False
    noticed_when_learner_was_lost: bool = False
    adapted_explanation_for_learner: bool = False
    made_tacit_knowledge_explicit: bool = False
    communicated_the_WHY_not_just_HOW: bool = False
    encouraged_questions: bool = False
    remained_patient_with_errors: bool = False
    admitted_own_uncertainty_when_present: bool = False

    # What the candidate did NOT do (also informative)
    missed_safety_check_learner_should_know: bool = False
    rushed_or_skipped_steps: bool = False
    talked_down_to_learner: bool = False

    # Outcome for the learner
    learner_could_replicate_afterward: Literal["fully", "partially", "not"] = "partially"
    learner_asked_productive_questions: bool = False
    learner_felt_safe_making_mistakes: Optional[bool] = None

    # Evaluator narrative
    qualitative_notes: str = ""


# =================================================================
# TEACHING CAPACITY DIMENSIONS
# =================================================================
"""
Teaching capacity is not one thing. These are the distinguishable
dimensions practitioners have named across industries.

A strong candidate may be high on some and weaker on others.
Organizations benefit from having a mix across their teachers.
"""

TEACHING_DIMENSIONS = {
    "decomposition": (
        "Can break complex tasks into learnable units. "
        "Recognizes which order to present things in."
    ),
    "tacit_translation": (
        "Can articulate knowledge they normally perform without "
        "words. 'I just know when it's right' → can they tell you "
        "what they're seeing or feeling?"
    ),
    "learner_reading": (
        "Notices when the learner is lost, bored, overconfident, "
        "afraid. Adjusts accordingly."
    ),
    "scaffolding": (
        "Provides enough support that the learner can succeed, "
        "and removes it as the learner develops. Neither leaves "
        "them stranded nor hovers forever."
    ),
    "patience_under_error": (
        "Treats mistakes as information rather than as failure. "
        "Does not take over when the learner is struggling productively."
    ),
    "why_communication": (
        "Explains the reasons behind practices, not just the "
        "procedures. Transfers the reasoning, not just the rule."
    ),
    "safety_priority": (
        "Stops for safety issues without making a big deal of it. "
        "Teaches safety-mindedness through consistent practice."
    ),
    "humility": (
        "Admits what they don't know. Recognizes the learner may "
        "eventually know things they don't. Doesn't fake expertise."
    ),
}


# =================================================================
# EVALUATOR ASSESSMENT
# =================================================================
@dataclass
class TeachingEvaluation:
    """One evaluator's assessment of a teaching session."""
    evaluator_id: str
    session_id: str                         # reference to TeachingSession
    candidate_id: str

    # Holistic judgments per dimension
    dimension_ratings: dict[str, Literal["strong", "adequate",
                                         "developing", "weak"]] = field(
        default_factory=dict
    )

    # Key questions for evaluators
    would_trust_candidate_to_train_new_hire: bool = False
    would_learn_from_candidate_themselves: bool = False
    observed_something_learned: bool = False  # in role_reversal format

    # Narrative
    strongest_moment: str = ""
    weakest_moment: str = ""
    notes: str = ""


def evaluation_summary(eval_: TeachingEvaluation) -> dict:
    """Produce a structured summary of a single evaluator's assessment."""
    ratings = eval_.dimension_ratings
    strong_count = sum(1 for v in ratings.values() if v == "strong")
    adequate_count = sum(1 for v in ratings.values() if v == "adequate")
    developing_count = sum(1 for v in ratings.values() if v == "developing")
    weak_count = sum(1 for v in ratings.values() if v == "weak")

    return {
        "evaluator": eval_.evaluator_id,
        "dimensions_rated": len(ratings),
        "strong": strong_count,
        "adequate": adequate_count,
        "developing": developing_count,
        "weak": weak_count,
        "would_trust_to_train": eval_.would_trust_candidate_to_train_new_hire,
        "would_learn_from": eval_.would_learn_from_candidate_themselves,
    }



# =================================================================
# AGGREGATION
# =================================================================
@dataclass
class TeachingProfile:
    """A candidate's teaching capacity across all demonstrations."""
    candidate_id: str
    sessions: list[TeachingSession] = field(default_factory=list)
    evaluations: list[TeachingEvaluation] = field(default_factory=list)

    def summary(self) -> dict:
        if not self.sessions:
            return {"status": "no_data"}

        # Aggregate consistent behaviors
        n = len(self.sessions)
        aggregated_behaviors = {
            "opened_with_orientation_pct":
                sum(1 for s in self.sessions if s.opened_with_orientation) / n,
            "checked_starting_knowledge_pct":
                sum(1 for s in self.sessions
                    if s.checked_learner_starting_knowledge) / n,
            "broke_into_steps_pct":
                sum(1 for s in self.sessions
                    if s.broke_task_into_manageable_steps) / n,
            "communicated_why_pct":
                sum(1 for s in self.sessions
                    if s.communicated_the_WHY_not_just_HOW) / n,
            "made_tacit_explicit_pct":
                sum(1 for s in self.sessions
                    if s.made_tacit_knowledge_explicit) / n,
            "encouraged_questions_pct":
                sum(1 for s in self.sessions if s.encouraged_questions) / n,
            "patient_with_errors_pct":
                sum(1 for s in self.sessions if s.remained_patient_with_errors) / n,
        }

        learner_replication = {
            "fully": sum(1 for s in self.sessions
                         if s.learner_could_replicate_afterward == "fully"),
            "partially": sum(1 for s in self.sessions
                              if s.learner_could_replicate_afterward == "partially"),
            "not": sum(1 for s in self.sessions
                       if s.learner_could_replicate_afterward == "not"),
        }

        # Evaluator consensus
        trust_to_train_count = sum(1 for e in self.evaluations
                                     if e.would_trust_candidate_to_train_new_hire)
        learn_from_count = sum(1 for e in self.evaluations
                                if e.would_learn_from_candidate_themselves)

        return {
            "sessions": n,
            "evaluator_assessments": len(self.evaluations),
            "behaviors": {k: round(v, 2) for k, v in aggregated_behaviors.items()},
            "learner_replication_outcomes": learner_replication,
            "evaluators_would_trust_to_train":
                f"{trust_to_train_count}/{len(self.evaluations)}",
            "evaluators_would_learn_from":
                f"{learn_from_count}/{len(self.evaluations)}",
        }


# =================================================================
# INTERPRETATION GUIDE
# =================================================================
def interpret_profile(profile: TeachingProfile) -> list[str]:
    """
    Human-readable interpretations of common profile patterns.
    Returns list of notes that a hiring/promotion committee might
    find useful.
    """
    summary = profile.summary()
    if summary.get("status") == "no_data":
        return ["No teaching sessions recorded."]

    notes = []

    behaviors = summary["behaviors"]
    if behaviors.get("made_tacit_explicit_pct", 0) > 0.7:
        notes.append(
            "Candidate consistently makes tacit knowledge explicit. "
            "This is the rarest and most valuable teaching capacity. "
            "Strong signal for mentorship role.")

    if behaviors.get("communicated_why_pct", 0) > 0.7:
        notes.append(
            "Candidate communicates reasoning behind procedures. "
            "Learners taught by this candidate will transfer to "
            "new situations better than those taught rote.")

    if (behaviors.get("checked_starting_knowledge_pct", 0) < 0.3
        and behaviors.get("patient_with_errors_pct", 0) < 0.5):
        notes.append(
            "Candidate may know the work but shows limited teaching "
            "capacity. Consider pairing with a teaching partner before "
            "assigning solo mentorship responsibilities.")

    replication = summary["learner_replication_outcomes"]
    total = sum(replication.values())
    if total > 0 and replication["fully"] / total > 0.6:
        notes.append(
            "Majority of learners can replicate the taught task "
            "afterward. This is the hard outcome measure of teaching.")

    # Parse "X/Y" format from evaluator consensus
    def parse_ratio(s):
        if "/" not in s:
            return 0.0
        a, b = s.split("/")
        try:
            return int(a) / int(b) if int(b) > 0 else 0.0
        except ValueError:
            return 0.0

    trust_ratio = parse_ratio(summary["evaluators_would_trust_to_train"])
    learn_ratio = parse_ratio(summary["evaluators_would_learn_from"])

    if trust_ratio > 0.8 and learn_ratio > 0.5:
        notes.append(
            "High evaluator consensus on teaching capacity. This "
            "candidate should be compensated for the teaching work "
            "as primary role, not as overhead.")

    if trust_ratio < 0.3:
        notes.append(
            "Evaluators do not consensus-trust this candidate with "
            "new hires. If candidate is otherwise strong, assess "
            "whether this is teaching skill (developable) or "
            "interpersonal temperament (harder to develop).")

    return notes


# =================================================================
# DEMO
# =================================================================
if __name__ == "__main__":
    # Example session: candidate teaches how to diagnose a coupling
    # alignment issue to a newer maintenance tech.
    session = TeachingSession(
        candidate_id="CAND_042",
        learner_id="LRN_015",
        topic="Diagnosing coupling alignment without a dial indicator",
        topic_origin="candidate_chose",
        session_start="2026-04-16T14:00:00",
        session_end="2026-04-16T15:30:00",
        evaluator_ids=["eval_001", "eval_003"],
        format="teach_real_learner",
        opened_with_orientation=True,
        checked_learner_starting_knowledge=True,
        broke_task_into_manageable_steps=True,
        demonstrated_before_explaining=True,
        allowed_learner_to_try=True,
        corrected_without_taking_over=True,
        noticed_when_learner_was_lost=True,
        adapted_explanation_for_learner=True,
        made_tacit_knowledge_explicit=True,
        communicated_the_WHY_not_just_HOW=True,
        encouraged_questions=True,
        remained_patient_with_errors=True,
        admitted_own_uncertainty_when_present=True,
        learner_could_replicate_afterward="partially",
        learner_asked_productive_questions=True,
        learner_felt_safe_making_mistakes=True,
        qualitative_notes=(
            "Candidate used a straightedge and feeler gauges to "
            "demonstrate alignment assessment. Made explicit what "
            "they 'feel for' when checking — this is embodied "
            "knowledge that most practitioners cannot articulate. "
            "Learner was able to replicate the physical technique "
            "after one session; full confidence will develop with "
            "more practice. Candidate noted dyslexia may affect "
            "written documentation but teaching was entirely "
            "verbal and physical."),
    )

    ev1 = TeachingEvaluation(
        evaluator_id="eval_001",
        session_id="session_001",
        candidate_id="CAND_042",
        dimension_ratings={
            "decomposition": "strong",
            "tacit_translation": "strong",
            "learner_reading": "strong",
            "scaffolding": "adequate",
            "patience_under_error": "strong",
            "why_communication": "strong",
            "safety_priority": "strong",
            "humility": "strong",
        },
        would_trust_candidate_to_train_new_hire=True,
        would_learn_from_candidate_themselves=True,
        observed_something_learned=False,  # not role-reversal format
        strongest_moment=(
            "Candidate translated 'you can feel when it's right' "
            "into specific pressure and angle cues the learner "
            "could replicate."),
        weakest_moment=(
            "Candidate allowed learner to continue struggling "
            "on one step slightly too long before stepping in — "
            "learner was productive but approached frustration."),
        notes=(
            "I would have learned from this candidate myself 15 years "
            "ago. The tacit translation ability is exceptional and "
            "rare."),
    )

    ev2 = TeachingEvaluation(
        evaluator_id="eval_003",
        session_id="session_001",
        candidate_id="CAND_042",
        dimension_ratings={
            "decomposition": "strong",
            "tacit_translation": "strong",
            "learner_reading": "adequate",
            "scaffolding": "strong",
            "patience_under_error": "strong",
            "why_communication": "strong",
            "safety_priority": "strong",
            "humility": "adequate",
        },
        would_trust_candidate_to_train_new_hire=True,
        would_learn_from_candidate_themselves=True,
        strongest_moment=(
            "The embodied demonstration followed by verbal "
            "explanation, rather than the reverse. This order "
            "matters and candidate did it consistently."),
        weakest_moment=(
            "Could have checked learner retention with a quick "
            "recap at the end."),
        notes=(
            "This candidate is a natural mentor. Organization "
            "should protect their teaching time explicitly."),
    )

    profile = TeachingProfile(
        candidate_id="CAND_042",
        sessions=[session],
        evaluations=[ev1, ev2],
    )

    print("="*72)
    print("TEACHING DEMONSTRATION — DEMO")
    print("="*72)
    print(f"\nProfile summary:")
    s = profile.summary()
    for k, v in s.items():
        if isinstance(v, dict):
            print(f"  {k}:")
            for k2, v2 in v.items():
                print(f"    {k2}: {v2}")
        else:
            print(f"  {k}: {v}")

    print(f"\nInterpretation notes:")
    for note in interpret_profile(profile):
        print(f"  • {note}")

    print(f"\n{'-'*72}")
    print("Teaching capacity is invisible in certification-based hiring.")
    print("This candidate would be labeled 'unskilled' by HR screening")
    print("(dyslexia → low literacy score) but is a high-value mentor")
    print("by embodied-skill assessment. Protecting such candidates")
    print("and their teaching time is how organizations preserve")
    print("generative capacity across generations.")


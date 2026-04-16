"""
observation_protocol.py
=======================
Direct-observation skill assessment.

The candidate performs actual work at an actual workstation.
Evaluators are embodied practitioners in the same domain.

The assessment records what the candidate DOES, not what they SAY.
Dyslexia, language differences, and test anxiety do not confound
the measurement because the medium is the work, not the description
of the work.

This module provides:
  - data structures for recording observations
  - evaluation rubric templates for common industrial domains
  - aggregation utilities for combining multi-evaluator observations

The assessment itself is conducted in physical space. This module
is the recording and analysis layer.

CC0. Stdlib only.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional
from datetime import datetime
import statistics


# =================================================================
# CORE DATA STRUCTURES
# =================================================================
@dataclass
class Observation:
    """A single observed behavior during a task."""
    timestamp: str                        # ISO 8601
    behavior: str                         # what the candidate did
    quality: Literal["excellent", "adequate", "concerning", "missing"]
    evaluator_id: str
    notes: str = ""
    # Optional dimensional tags for aggregation
    dimensions: list[str] = field(default_factory=list)
    # e.g. ["tool_handling", "safety_awareness", "diagnostic_speed"]


@dataclass
class TaskAssessment:
    """A complete task performed by a candidate with full observation log."""
    candidate_id: str
    task_name: str
    task_description: str
    task_start: str                       # ISO 8601
    task_end: str
    evaluators: list[str]                 # IDs of practitioner evaluators
    observations: list[Observation] = field(default_factory=list)

    # Context
    equipment_state: str = "normal"       # normal / degraded / broken
    supervision_level: Literal["none", "monitored", "guided"] = "monitored"
    candidate_tools_brought: list[str] = field(default_factory=list)

    # Outcome
    task_completed: bool = False
    completion_quality: Literal["excellent", "adequate", "partial",
                                 "incomplete"] = "partial"
    safety_incidents: int = 0
    evaluator_consensus: str = ""         # plain text summary from evaluators


# =================================================================
# RUBRIC TEMPLATES
# =================================================================
"""
Rubrics are domain-specific. These are starting templates that
should be adapted by practitioners in the specific industry.

Each rubric is a list of dimensions the candidate should be
assessed on, with observable behaviors that signal each.

IMPORTANT: these are NOT scoring formulas. They are OBSERVATION
PROMPTS to help evaluators know what to watch for. Scoring is
done holistically by practitioners, not by summing rubric items.
"""

INDUSTRIAL_MAINTENANCE_RUBRIC = {
    "tool_selection": [
        "Chose appropriate tools for the job without prompting",
        "Brought or requested tools specific to the problem observed",
        "Did not over-tool (using more than necessary wastes time)",
    ],
    "system_reading": [
        "Observed the machine/system before touching it",
        "Listened to running equipment for abnormal sounds",
        "Noticed temperature, vibration, or smell signals",
        "Identified wear patterns, leak signs, corrosion",
    ],
    "diagnostic_sequencing": [
        "Started with non-invasive checks before disassembly",
        "Verified assumptions before acting on them",
        "Did not skip obvious checks to reach preferred conclusion",
    ],
    "safety_awareness": [
        "Verified lockout/tagout where appropriate",
        "Tested circuits before contact",
        "Maintained appropriate PPE throughout",
        "Positioned self to avoid pinch/crush/arc hazards",
    ],
    "improvisation_quality": [
        "When standard tool unavailable, found working alternative",
        "Explained why substitution was acceptable or not",
        "Did not force a solution that didn't fit",
    ],
    "communication": [
        "Asked clarifying questions when ambiguous",
        "Flagged issues outside the scope of the task",
        "Could describe what they found (even if nonverbally)",
    ],
    "time_calibration": [
        "Estimated time to completion reasonably",
        "Adjusted approach if initial path was too slow",
        "Did not rush past steps that mattered",
    ],
}


WELDING_RUBRIC = {
    "material_reading": [
        "Identified base metal correctly (by color, weight, spark)",
        "Noted cleanliness and prep requirements",
        "Selected matching filler without looking it up",
    ],
    "heat_control": [
        "Adjusted amperage for material thickness",
        "Maintained consistent travel speed",
        "Recognized overheating before distortion",
    ],
    "position_technique": [
        "Managed all positions (flat, horizontal, vertical, overhead)",
        "Body position and breathing stable through long passes",
        "Did not fatigue into sloppy work",
    ],
    "visual_inspection": [
        "Examined own weld before being asked",
        "Could identify own defects accurately",
        "Knew which defects require redo vs. minor rework",
    ],
}


LONG_HAUL_DRIVING_RUBRIC = {
    "pre_trip_inspection": [
        "Checked items not on the written list",
        "Noticed tire wear patterns, brake chamber condition",
        "Inspected load securement with real attention",
        "Documented what they found, not just a checkmark",
    ],
    "road_reading": [
        "Adjusted following distance for conditions observed",
        "Noticed unusual behavior from other drivers early",
        "Recognized weather changes before they became critical",
        "Tracked fuel/DEF/hours-of-service without reminders",
    ],
    "mechanical_attention": [
        "Noticed changes in truck behavior and diagnosed causes",
        "Recognized which problems need immediate stop vs. can wait",
        "Handled routine issues (tire change, chain hanging) independently",
    ],
    "shipper_receiver_interaction": [
        "De-escalated when staff was hostile or uninformed",
        "Recognized lying about load times or damage",
        "Documented issues in a way that protected themselves and carrier",
    ],
    "fatigue_management": [
        "Recognized own fatigue state honestly",
        "Adjusted schedule to prioritize safety over dispatcher pressure",
        "Managed sleep, nutrition, exercise on multi-day runs",
    ],
}


PROCESS_CHEMISTRY_RUBRIC = {
    "hazard_recognition": [
        "Identified specific hazards of the material being handled",
        "Knew compatible and incompatible materials",
        "Recognized escalation signs (color, smell, temperature change)",
    ],
    "containment_awareness": [
        "Maintained containment discipline without prompting",
        "Recognized containment failure modes early",
        "Had emergency response sequence internalized",
    ],
    "batch_tracking": [
        "Maintained accurate records of what went where when",
        "Noticed deviations from expected batch behavior",
        "Did not normalize drift in process parameters",
    ],
    "specific_domain_knowledge": [
        "Demonstrated material-specific knowledge from experience",
        "Could explain why practices exist, not just what they are",
        "Recognized older equipment quirks not in current manuals",
    ],
}


# =================================================================
# EVALUATOR CONSENSUS (CROSS-CHECKING)
# =================================================================
@dataclass
class EvaluatorRating:
    """
    Each evaluator produces a holistic rating + a set of dimensional
    flags. Ratings are NOT averaged numerically because practitioner
    judgment is not commensurable in that way. Instead, disagreements
    are surfaced and resolved through discussion.
    """
    evaluator_id: str
    candidate_id: str
    task_name: str
    overall_judgment: Literal["hire", "hire_with_mentorship",
                              "not_ready", "wrong_fit"]
    confidence: Literal["high", "medium", "low"]
    strengths: list[str] = field(default_factory=list)
    concerns: list[str] = field(default_factory=list)
    would_work_alongside: bool = False
    would_let_train_newer_worker: bool = False
    notes: str = ""




@dataclass
class ConsensusReport:
    """Combined output from all evaluators for a single task."""
    candidate_id: str
    task_name: str
    evaluator_ratings: list[EvaluatorRating]

    def agreement_level(self) -> Literal["unanimous", "majority", "split"]:
        judgments = [r.overall_judgment for r in self.evaluator_ratings]
        if len(set(judgments)) == 1:
            return "unanimous"
        counts = {j: judgments.count(j) for j in set(judgments)}
        max_count = max(counts.values())
        if max_count > len(judgments) / 2:
            return "majority"
        return "split"

    def consensus_summary(self) -> str:
        """Human-readable summary for record-keeping."""
        agree = self.agreement_level()
        judgments = [r.overall_judgment for r in self.evaluator_ratings]
        would_work_alongside = sum(1 for r in self.evaluator_ratings
                                    if r.would_work_alongside)
        would_train = sum(1 for r in self.evaluator_ratings
                          if r.would_let_train_newer_worker)
        return (f"Agreement: {agree}. "
                f"Judgments: {judgments}. "
                f"Would work alongside: {would_work_alongside}/{len(self.evaluator_ratings)}. "
                f"Would let train newer worker: {would_train}/{len(self.evaluator_ratings)}.")


# =================================================================
# AGGREGATION ACROSS TASKS
# =================================================================
@dataclass
class CandidateFile:
    """All assessments for a single candidate across the protocol."""
    candidate_id: str
    demographic_notes: str = ""
    task_assessments: list[TaskAssessment] = field(default_factory=list)
    consensus_reports: list[ConsensusReport] = field(default_factory=list)
    provenance_notes: str = ""  # populated by provenance_log.py

    def hiring_recommendation(self) -> dict:
        """
        Produces a recommendation derived from evaluator consensus
        across all tasks.

        IMPORTANT: This is a summary, not a decision. Final hiring
        decisions should be made by practitioners reviewing the full
        file, not by algorithmic aggregation.
        """
        if not self.consensus_reports:
            return {"recommendation": "insufficient_data",
                    "reason": "no assessments completed"}

        would_work_pct = statistics.mean(
            sum(1 for rat in cr.evaluator_ratings if rat.would_work_alongside)
            / len(cr.evaluator_ratings)
            for cr in self.consensus_reports
        )
        would_train_pct = statistics.mean(
            sum(1 for rat in cr.evaluator_ratings
                if rat.would_let_train_newer_worker)
            / len(cr.evaluator_ratings)
            for cr in self.consensus_reports
        )
        unanimous_count = sum(1 for cr in self.consensus_reports
                               if cr.agreement_level() == "unanimous")

        return {
            "candidate_id": self.candidate_id,
            "tasks_assessed": len(self.task_assessments),
            "evaluator_consensus_unanimous": unanimous_count,
            "would_work_alongside_rate": round(would_work_pct, 2),
            "would_let_train_rate": round(would_train_pct, 2),
            "recommendation_is_decision": False,
            "note": ("Practitioner review of full file required. "
                      "This summary is support, not decision."),
        }


# =================================================================
# SANITY CHECKS
# =================================================================
def audit_assessment_quality(assessment: TaskAssessment) -> list[str]:
    """
    Check an assessment for common failure modes.
    Returns a list of warnings (empty list = no issues detected).
    """
    warnings = []

    if len(assessment.evaluators) < 2:
        warnings.append("Single evaluator — high risk of individual bias. "
                         "Recommend minimum 2 practitioner evaluators.")

    if not assessment.observations:
        warnings.append("No observations recorded. Assessment may have been "
                         "run as pass/fail without evidence capture.")

    if len(assessment.observations) < 10 and assessment.task_completed:
        warnings.append("Fewer than 10 observations for a completed task. "
                         "Evaluators may not have been present enough.")

    if assessment.supervision_level == "guided":
        warnings.append("Task was guided rather than observed. Results "
                         "reflect candidate's ability to FOLLOW, not to DO.")

    evaluator_obs_counts = {}
    for obs in assessment.observations:
        evaluator_obs_counts[obs.evaluator_id] = \
            evaluator_obs_counts.get(obs.evaluator_id, 0) + 1
    if evaluator_obs_counts:
        if len(evaluator_obs_counts) == 1:
            warnings.append("All observations from a single evaluator. "
                             "Cross-check not possible.")

    return warnings


# =================================================================
# DEMO
# =================================================================
if __name__ == "__main__":
    # Example: a maintenance candidate assessment
    obs = [
        Observation("2026-04-16T09:12:00",
                    "Walked around machine before starting. "
                    "Noted oil stain under pump housing.",
                    "excellent", "eval_001",
                    dimensions=["system_reading"]),
        Observation("2026-04-16T09:15:00",
                    "Checked pump housing bolts for proper torque before "
                    "disassembly.",
                    "excellent", "eval_001",
                    dimensions=["diagnostic_sequencing"]),
        Observation("2026-04-16T09:32:00",
                    "Used pipe wrench as lever when bolt was seized. "
                    "Did not request new tool.",
                    "adequate", "eval_002",
                    dimensions=["improvisation_quality"],
                    notes="Candidate explained the substitution was fine "
                          "because the force vector was not axial."),
        Observation("2026-04-16T10:05:00",
                    "When asked about the oil stain, explained it was "
                    "upstream from the pump, not from it.",
                    "excellent", "eval_002",
                    dimensions=["system_reading", "communication"]),
    ]

    assessment = TaskAssessment(
        candidate_id="CAND_042",
        task_name="Diagnose pump vibration complaint",
        task_description=(
            "Machine running with elevated vibration reported. "
            "Candidate to diagnose cause and recommend action."),
        task_start="2026-04-16T09:00:00",
        task_end="2026-04-16T11:30:00",
        evaluators=["eval_001", "eval_002"],
        observations=obs,
        equipment_state="degraded",
        supervision_level="monitored",
        candidate_tools_brought=["personal multimeter", "feeler gauges",
                                  "notebook"],
        task_completed=True,
        completion_quality="excellent",
        evaluator_consensus=(
            "Candidate identified oil stain was from coupling misalignment, "
            "not pump failure. Correct diagnosis. Would have saved several "
            "hours of unnecessary disassembly if this had been a live call. "
            "Strong observation skills, good improvisation, explicit "
            "reasoning. Certification test scores (reviewed separately) "
            "would have placed this candidate below hiring threshold. "
            "Task assessment inverts that ranking."),
    )

    ratings = [
        EvaluatorRating(
            "eval_001", "CAND_042", assessment.task_name,
            overall_judgment="hire",
            confidence="high",
            strengths=["observation before action",
                        "diagnostic sequencing",
                        "willingness to explain reasoning"],
            concerns=["paperwork may need accommodation"],
            would_work_alongside=True,
            would_let_train_newer_worker=True,
            notes="This is the kind of hire we can't find on paper."),
        EvaluatorRating(
            "eval_002", "CAND_042", assessment.task_name,
            overall_judgment="hire",
            confidence="high",
            strengths=["system reading",
                        "improvisation with correct force analysis"],
            concerns=[],
            would_work_alongside=True,
            would_let_train_newer_worker=True,
            notes="Candidate noted dyslexia during intake. Did not "
                  "affect task performance in any observable way."),
    ]

    consensus = ConsensusReport("CAND_042", assessment.task_name, ratings)

    file = CandidateFile(
        candidate_id="CAND_042",
        demographic_notes="Dyslexic. 22 years experience in similar work.",
        task_assessments=[assessment],
        consensus_reports=[consensus],
    )

    print("="*72)
    print("OBSERVATION PROTOCOL — DEMO")
    print("="*72)
    print(f"Assessment warnings: {audit_assessment_quality(assessment)}")
    print(f"\nConsensus: {consensus.consensus_summary()}")
    print(f"\nRecommendation summary: {file.hiring_recommendation()}")

    print("\nThis candidate would likely score below HR certification "
          "threshold due to dyslexia. The observation protocol inverts "
          "that ranking: two practitioner evaluators in unanimous "
          "agreement that the candidate is not only hireable but "
          "qualified to train newer workers.")

"""
provenance_log.py
=================
Skill lineage tracking.

Where did a candidate's skill come from? Who taught them?
What environments have they worked in? What specific failure
modes and edge cases have they encountered personally?

Why this matters:

Tacit knowledge has lineage. A welder trained in aerospace carries
different failure-mode awareness than one trained in agricultural
equipment. A maintenance tech who worked at a specific plant
carries knowledge of that plant's equipment idiosyncrasies that no
manual documents. A chemist who worked under a specific mentor
carries that mentor's risk-awareness patterns.

Current hiring sees only the current state (certification, resume).
Provenance reveals:
  - the depth of the skill (1 place for 25 years vs 5 places for 5 years)
  - the breadth (types of equipment, materials, environments)
  - the lineage (who taught them, who they taught)
  - the specific failure modes they've personally handled
  - whether their knowledge is at risk of being lost

For sector-level applications, provenance tracking across employers
maps mentorship lineages and identifies where last-practitioner
events are about to occur — allowing preservation before loss.

CC0. Stdlib only.
"""

from dataclasses import dataclass, field
from typing import Optional, Literal
from datetime import datetime


# =================================================================
# EXPERIENCE ENTRY
# =================================================================
@dataclass
class WorkEnvironment:
    """A specific place and period of work."""
    employer_or_location: str
    role: str
    start_year: int
    end_year: Optional[int]                 # None = current
    equipment_types: list[str] = field(default_factory=list)
    materials_handled: list[str] = field(default_factory=list)
    environmental_conditions: list[str] = field(default_factory=list)
    notes: str = ""

    def duration_years(self) -> float:
        end = self.end_year if self.end_year else datetime.now().year
        return end - self.start_year


@dataclass
class Mentor:
    """A person who taught the candidate."""
    name_or_identifier: str                 # can be anonymized
    taught_domain: str
    years_under_mentorship: float
    still_reachable: bool = False           # for verification / lineage tracing
    notes: str = ""


@dataclass
class MenteeRecord:
    """A person this candidate has taught."""
    name_or_identifier: str
    taught_what: str
    years_of_mentorship_given: float
    outcome: Literal["still_in_field", "moved_on", "unknown"] = "unknown"
    notes: str = ""


@dataclass
class FailureModeEncountered:
    """
    A specific failure the candidate has personally witnessed or
    handled. This captures the failure-mode library they carry.
    """
    failure_type: str
    domain: str
    year: Optional[int] = None
    context: str = ""                       # where/how it happened
    candidate_role: Literal["observed", "responded", "led_response"] = "observed"
    documented_elsewhere: bool = False
    # was this failure documented in literature/training, or is the
    # candidate's knowledge of it tacit / experiential only
    notes: str = ""


@dataclass
class SkillProvenance:
    """Complete provenance record for a candidate."""
    candidate_id: str
    primary_domains: list[str] = field(default_factory=list)
    work_history: list[WorkEnvironment] = field(default_factory=list)
    mentors: list[Mentor] = field(default_factory=list)
    mentees: list[MenteeRecord] = field(default_factory=list)
    failure_modes_encountered: list[FailureModeEncountered] = field(default_factory=list)

    # Certifications and formal training (recorded but not weighted heavily)
    certifications: list[str] = field(default_factory=list)
    formal_training: list[str] = field(default_factory=list)

    # Specific artifacts
    tools_owned: list[str] = field(default_factory=list)
    # Significant because long-experienced workers often carry specific
    # tools they've accumulated for specific problems
    equipment_personally_built_or_modified: list[str] = field(default_factory=list)
    # Salvage engineers often have built jigs, fixtures, adaptations

    def total_field_years(self) -> float:
        """Sum of work environment durations."""
        return sum(w.duration_years() for w in self.work_history)

    def domain_diversity(self) -> int:
        """Distinct equipment types worked with."""
        all_equipment = set()
        for w in self.work_history:
            all_equipment.update(w.equipment_types)
        return len(all_equipment)

    def failure_mode_library_depth(self) -> dict:
        """Breakdown of failure modes encountered by domain and role."""
        by_domain = {}
        for fm in self.failure_modes_encountered:
            if fm.domain not in by_domain:
                by_domain[fm.domain] = {"observed": 0, "responded": 0,
                                         "led_response": 0}
            by_domain[fm.domain][fm.candidate_role] += 1
        return by_domain

    def tacit_knowledge_signal(self) -> int:
        """Count of failure modes not documented elsewhere."""
        return sum(1 for fm in self.failure_modes_encountered
                    if not fm.documented_elsewhere)

    def mentorship_lineage(self) -> dict:
        """Summary of who taught this candidate and who they have taught."""
        return {
            "mentors_count": len(self.mentors),
            "total_years_under_mentorship": sum(m.years_under_mentorship
                                                 for m in self.mentors),
            "mentors_still_reachable": sum(1 for m in self.mentors
                                             if m.still_reachable),
            "mentees_count": len(self.mentees),
            "total_years_mentoring_given": sum(
                me.years_of_mentorship_given for me in self.mentees),
            "mentees_still_in_field": sum(1 for me in self.mentees
                                            if me.outcome == "still_in_field"),
        }


# =================================================================
# SECTOR-LEVEL LINEAGE TRACKING
# =================================================================
@dataclass
class SkillLineageMap:
    """
    Aggregate provenance across many candidates to map skill lineages
    in a sector. Used to identify mentorship chains at risk of breaking.
    """
    provenances: list[SkillProvenance] = field(default_factory=list)

    def last_practitioners(self, domain: str, min_years_experience: float = 20) -> list[str]:
        """
        Identify people in a domain with deep experience and unreachable
        mentors (implying they are near the end of a lineage).
        """
        candidates = []
        for p in self.provenances:
            if domain not in p.primary_domains:
                continue
            if p.total_field_years() < min_years_experience:
                continue
            mentors_in_domain = [m for m in p.mentors if m.taught_domain == domain]
            reachable_mentors = [m for m in mentors_in_domain if m.still_reachable]
            if not reachable_mentors and mentors_in_domain:
                candidates.append(p.candidate_id)
        return candidates

    def domains_at_risk(self, mentor_threshold: int = 3) -> list[str]:
        """
        Identify domains where there are fewer than `mentor_threshold`
        people actively mentoring. These are at risk of mentorship
        pipeline collapse.
        """
        active_mentors_by_domain = {}
        for p in self.provenances:
            for me in p.mentees:
                if me.outcome != "moved_on":
                    for domain in p.primary_domains:
                        active_mentors_by_domain[domain] = (
                            active_mentors_by_domain.get(domain, set())
                        )
                        active_mentors_by_domain[domain].add(p.candidate_id)

        at_risk = []
        for domain, mentors in active_mentors_by_domain.items():
            if len(mentors) < mentor_threshold:
                at_risk.append(domain)
        return at_risk

    def tacit_knowledge_at_risk(self) -> list[dict]:
        """
        Failure modes that appear only in the tacit knowledge of 1-2
        practitioners and are not documented elsewhere.
        """
        fm_holders = {}  # failure_type -> list of candidate_ids
        for p in self.provenances:
            for fm in p.failure_modes_encountered:
                if fm.documented_elsewhere:
                    continue
                key = f"{fm.domain}:{fm.failure_type}"
                fm_holders.setdefault(key, []).append(p.candidate_id)

          

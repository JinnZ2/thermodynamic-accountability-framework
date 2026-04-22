"""
scope_mapper.py

Knowledge Liberation Module 1: Map what a study ACTUALLY measured.

This is not a gatekeeper. It is a clarifier.
A study in scope is usable. A study with unclear scope gets misapplied.
Mapping scope FREES the knowledge to be applied where it legitimately works.

License: CC0
Ported from github.com/JinnZ2/Logic-Ferret/knowledge/scope_mapper.py
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


# ============================================================
# SCOPE AS STRUCTURED DATA (not verdict)
# ============================================================

class MeasurementType(Enum):
    """What KIND of thing was measured."""
    PHYSIOLOGICAL_RESPONSE = "physiological_response"
    BEHAVIORAL_OUTCOME = "behavioral_outcome"
    SELF_REPORT = "self_report"
    TASK_PERFORMANCE = "task_performance"
    LONGITUDINAL_OUTCOME = "longitudinal_outcome"
    POPULATION_STATISTIC = "population_statistic"
    MECHANISM = "mechanism"
    UNKNOWN = "unknown"


class SelectionType(Enum):
    """How was the population selected?"""
    CONVENIENCE_SAMPLE = "convenience_sample"
    RANDOM_SAMPLE = "random_sample"
    CLINICAL_POPULATION = "clinical_population"
    SELF_SELECTED = "self_selected"
    SURVIVAL_SELECTED = "survival_selected"
    UNDEFINED = "undefined"


@dataclass
class ScopeMap:
    """
    The structured scope of a study.

    This is not a list of flaws. It is a MAP of where the study's
    findings are load-bearing and where they become silent.
    """

    # What was actually measured (not what was claimed)
    measurement_type: MeasurementType
    measurement_instrument: str
    measurement_units: str

    # Who was measured
    population_description: str
    population_size: int
    selection_method: SelectionType

    # Under what conditions
    environment: str              # lab / field / hybrid
    duration: str                 # actual time measured
    controlled_variables: List[str]
    uncontrolled_variables: List[str]

    # What the finding LEGITIMATELY shows
    load_bearing_claim: str       # restated with scope attached

    # Where the study goes silent
    silent_on: List[str]          # questions the study cannot answer

    # The boundary
    applies_when: List[str]       # conditions where the claim holds
    silent_when: List[str]        # conditions where the claim cannot speak

    def to_dict(self) -> Dict[str, Any]:
        return {
            "measurement": {
                "type": self.measurement_type.value,
                "instrument": self.measurement_instrument,
                "units": self.measurement_units,
            },
            "population": {
                "description": self.population_description,
                "size": self.population_size,
                "selection": self.selection_method.value,
            },
            "conditions": {
                "environment": self.environment,
                "duration": self.duration,
                "controlled": self.controlled_variables,
                "uncontrolled": self.uncontrolled_variables,
            },
            "scoped_claim": self.load_bearing_claim,
            "silent_on": self.silent_on,
            "applies_when": self.applies_when,
            "silent_when": self.silent_when,
        }

    def as_liberation_statement(self) -> str:
        """
        Render the scope as a knowledge-liberation statement.

        Structure: 'This study shows X, when Y conditions hold.
                    It does not speak to Z.
                    Use it to reason about A. Do not use it to reason about B.'
        """
        lines = [
            "=" * 70,
            "KNOWLEDGE LIBERATION: SCOPE MAP",
            "=" * 70,
            "",
            "WHAT THIS STUDY LOAD-BEARINGLY SHOWS:",
            f"  {self.load_bearing_claim}",
            "",
            "WHEN IT APPLIES:",
        ]
        for condition in self.applies_when:
            lines.append(f"  + {condition}")

        lines.append("")
        lines.append("WHEN IT GOES SILENT:")
        for condition in self.silent_when:
            lines.append(f"  - {condition}")

        lines.append("")
        lines.append("QUESTIONS THIS STUDY CANNOT ANSWER:")
        for q in self.silent_on:
            lines.append(f"  ? {q}")

        lines.append("")
        lines.append("The study is VALID within its scope.")
        lines.append("The study is SILENT outside its scope.")
        lines.append("Liberating knowledge means using it where it works,")
        lines.append("and asking NEW questions where it does not.")
        lines.append("=" * 70)

        return "\n".join(lines)


# ============================================================
# SCOPE MAPPER
# ============================================================

class ScopeMapper:
    """
    Maps a study's claims down to its actual scope.

    Usage pattern:
        1. Read the study
        2. Populate a StudyInput with what you found
        3. mapper.map(study_input) -> ScopeMap
        4. Use the ScopeMap to guide application

    This is a SCAFFOLDING tool. The human (or AI) must read the study
    and populate the fields. The tool structures the thinking, not
    the conclusion.
    """

    def map_study(self,
                  claimed_finding: str,
                  what_was_measured: str,
                  measurement_instrument: str,
                  population: str,
                  population_size: int,
                  environment: str,
                  duration: str,
                  controlled: List[str],
                  uncontrolled: List[str]) -> ScopeMap:
        """
        Build a scope map from study inputs.

        The CLAIMED FINDING is what the paper says.
        The WHAT WAS MEASURED is the physical/behavioral reality
        the instruments actually touched.

        These are often different. The gap is where misapplication lives.
        """

        measurement_type = self._classify_measurement(
            measurement_instrument, what_was_measured)
        selection = self._classify_selection(population)
        scoped_claim = self._restate_with_scope(
            claimed_finding, what_was_measured, population, environment, duration
        )
        silent_on = self._derive_silences(
            claimed_finding, what_was_measured, population,
            environment, duration, uncontrolled
        )
        applies_when = self._derive_applies_when(
            population, environment, duration, controlled)
        silent_when = self._derive_silent_when(
            population, environment, duration, uncontrolled)

        return ScopeMap(
            measurement_type=measurement_type,
            measurement_instrument=measurement_instrument,
            measurement_units=self._infer_units(measurement_instrument),
            population_description=population,
            population_size=population_size,
            selection_method=selection,
            environment=environment,
            duration=duration,
            controlled_variables=controlled,
            uncontrolled_variables=uncontrolled,
            load_bearing_claim=scoped_claim,
            silent_on=silent_on,
            applies_when=applies_when,
            silent_when=silent_when,
        )

    # ----------------------------------------------------------
    # CLASSIFIERS (simple, transparent heuristics)
    # ----------------------------------------------------------

    def _classify_measurement(self, instrument: str, measured: str) -> MeasurementType:
        instrument_lower = instrument.lower()
        measured_lower = measured.lower()
        combined = f"{instrument_lower} {measured_lower}"

        if any(w in combined for w in ["cortisol", "skin conductance",
                                        "heart rate", "bp", "eeg", "fmri"]):
            return MeasurementType.PHYSIOLOGICAL_RESPONSE
        if any(w in combined for w in ["reaction time", "accuracy", "score", "task"]):
            return MeasurementType.TASK_PERFORMANCE
        if any(w in combined for w in ["survey", "questionnaire",
                                        "self-report", "reported"]):
            return MeasurementType.SELF_REPORT
        if any(w in combined for w in ["incidence", "rate", "prevalence"]):
            return MeasurementType.POPULATION_STATISTIC
        if any(w in combined for w in ["behavior", "choice", "action"]):
            return MeasurementType.BEHAVIORAL_OUTCOME
        if any(w in combined for w in ["followup", "follow-up",
                                        "longitudinal", "years later"]):
            return MeasurementType.LONGITUDINAL_OUTCOME
        if any(w in combined for w in ["mechanism", "pathway", "signaling"]):
            return MeasurementType.MECHANISM
        return MeasurementType.UNKNOWN

    def _classify_selection(self, population: str) -> SelectionType:
        pop_lower = population.lower()
        if any(w in pop_lower for w in ["student", "undergraduate",
                                         "university", "convenience"]):
            return SelectionType.CONVENIENCE_SAMPLE
        if "random" in pop_lower:
            return SelectionType.RANDOM_SAMPLE
        if any(w in pop_lower for w in ["patient", "clinical",
                                         "diagnosed", "treatment"]):
            return SelectionType.CLINICAL_POPULATION
        if any(w in pop_lower for w in ["volunteer", "self-selected", "recruited"]):
            return SelectionType.SELF_SELECTED
        if any(w in pop_lower for w in ["veteran", "survivor",
                                         "first responder", "long-term"]):
            return SelectionType.SURVIVAL_SELECTED
        return SelectionType.UNDEFINED

    def _infer_units(self, instrument: str) -> str:
        instrument_lower = instrument.lower()
        if "cortisol" in instrument_lower:
            return "ug/dL or nmol/L"
        if "skin conductance" in instrument_lower:
            return "microsiemens"
        if "heart rate" in instrument_lower:
            return "bpm"
        if "reaction time" in instrument_lower:
            return "ms"
        if "score" in instrument_lower:
            return "points/scale"
        return "unspecified"

    # ----------------------------------------------------------
    # SCOPE DERIVATION (the generative part)
    # ----------------------------------------------------------

    def _restate_with_scope(self, claim: str, measured: str,
                            pop: str, env: str, dur: str) -> str:
        """
        Take the claim and add the scope clauses that the paper's
        headline left off.
        """
        return (
            f"In {pop}, under {env} conditions, over {dur}, "
            f"the study observed: {claim} "
            f"(measurement: {measured})."
        )

    def _derive_silences(self, claim: str, measured: str, pop: str,
                         env: str, dur: str, uncontrolled: List[str]) -> List[str]:
        """
        Generate the questions this study cannot answer.
        These are starting points for edge exploration.
        """
        silences = []

        short_durations = ["minute", "hour", "single session", "day", "week"]
        if any(s in dur.lower() for s in short_durations):
            silences.append(
                f"What happens over longer time scales (months, years, decades) "
                f"beyond the {dur} measurement window?"
            )

        if "lab" in env.lower():
            silences.append(
                "Does the finding replicate in field/real-world conditions "
                "where uncontrolled variables are present?"
            )

        if "student" in pop.lower() or "undergraduate" in pop.lower():
            silences.append(
                "Does the finding generalize to populations with different "
                "life history, body composition, or environmental exposure?"
            )

        if any(w in claim.lower() for w in ["trauma", "adversity", "stress", "threat"]):
            silences.append(
                "How do SURVIVORS of repeated threat compare? They may have "
                "been recalibrated by experience in ways the study population wasn't."
            )
            silences.append(
                "Could the measured 'impairment' be a functional ADAPTATION "
                "for environments where the finding population doesn't live?"
            )

        for var in uncontrolled:
            silences.append(
                f"The study did not control for {var}. "
                f"What is the finding's dependence on that variable?"
            )

        if "response" in measured.lower() or "reactivity" in measured.lower():
            silences.append(
                "Was this measuring IMPAIRMENT, or was it measuring "
                "INCREASED TOLERANCE / RECALIBRATION / ADAPTATION? "
                "The instrument may not distinguish."
            )

        return silences

    def _derive_applies_when(self, pop: str, env: str, dur: str,
                             controlled: List[str]) -> List[str]:
        conditions = [
            f"The population matches: {pop}",
            f"The environment is similar to: {env}",
            f"The time scale is comparable to: {dur}",
        ]
        for var in controlled:
            conditions.append(f"{var} is held at similar levels")
        return conditions

    def _derive_silent_when(self, pop: str, env: str, dur: str,
                            uncontrolled: List[str]) -> List[str]:
        conditions = [
            f"Population differs substantially from: {pop}",
            f"Environment differs from: {env}",
            f"Time scale exceeds: {dur}",
        ]
        for var in uncontrolled:
            conditions.append(f"{var} varies outside the study's implicit range")
        return conditions


# ============================================================
# CONVENIENCE
# ============================================================

def map_scope(claimed_finding: str,
              what_was_measured: str,
              measurement_instrument: str,
              population: str,
              population_size: int,
              environment: str,
              duration: str,
              controlled: List[str],
              uncontrolled: List[str]) -> str:
    """Quick scope-mapping, returns the liberation statement."""
    mapper = ScopeMapper()
    scope = mapper.map_study(
        claimed_finding=claimed_finding,
        what_was_measured=what_was_measured,
        measurement_instrument=measurement_instrument,
        population=population,
        population_size=population_size,
        environment=environment,
        duration=duration,
        controlled=controlled,
        uncontrolled=uncontrolled,
    )
    return scope.as_liberation_statement()


# ============================================================
# EXAMPLE
# ============================================================

if __name__ == "__main__":
    result = map_scope(
        claimed_finding="Childhood adversity associated with blunted threat response",
        what_was_measured="Skin conductance response to conditioned threat cues",
        measurement_instrument="Skin conductance electrodes",
        population="Undergraduate students with self-reported ACE scores",
        population_size=128,
        environment="University lab, controlled lighting, 22C",
        duration="Single session, approximately 45 minutes",
        controlled=["Ambient temperature", "Stimulus presentation timing"],
        uncontrolled=[
            "Real-world threat exposure history",
            "Current environment threat level",
            "Pain tolerance baseline",
            "Prior learning/recalibration from survived events",
            "Cultural framing of threat",
        ]
    )
    print(result)

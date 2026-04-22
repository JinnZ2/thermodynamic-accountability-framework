"""
application_builder.py

Knowledge Liberation Module 3: Build with the study.

Given a clearly-scoped finding and the edge questions it opens,
what can we ACTUALLY BUILD?

This is the output layer of the practice. Not "is the study valid?"
but "what useful thing becomes possible now that we know what this
finding actually says?"

The finding is material. Scope tells us where to use it.
Edges tell us where to extend it. This module turns that into
design constraints for real-world application.

License: CC0
Ported from github.com/JinnZ2/Logic-Ferret/knowledge/application_builder.py
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


# ============================================================
# APPLICATION CATEGORIES
# ============================================================

class ApplicationDomain(Enum):
    """Where can the scoped finding be applied?"""
    DESIGN_CONSTRAINT = "design_constraint"          # inform tool/system design
    TRAINING_DESIGN = "training_design"              # inform how people learn
    SCREENING_LIMITATION = "screening_limitation"    # what NOT to screen for
    POLICY_SCOPE = "policy_scope"                    # policy bounded to conditions
    FURTHER_RESEARCH = "further_research"            # hypothesis generation
    FIELD_VALIDATION = "field_validation"            # what needs real-world test
    FRAME_CORRECTION = "frame_correction"            # reframe public understanding


# ============================================================
# APPLICATION CANDIDATES
# ============================================================

@dataclass
class LegitimateApplication:
    """A valid use of the finding within scope."""

    domain: ApplicationDomain
    description: str
    design_constraint: str           # what the finding tells us to do/avoid
    scope_conditions: List[str]      # must hold for this application to work

    def format(self) -> str:
        conditions = "\n    ".join([f"- {c}" for c in self.scope_conditions])
        return (
            f"[{self.domain.value.upper()}]\n"
            f"  {self.description}\n"
            f"  Design input: {self.design_constraint}\n"
            f"  Requires:\n    {conditions}\n"
        )


@dataclass
class Misapplication:
    """A use of the finding that EXCEEDS its scope -- the harm vector."""

    description: str
    why_it_fails: str
    harm_if_deployed: str
    alternative: str                 # what to do instead

    def format(self) -> str:
        return (
            f"  Misuse: {self.description}\n"
            f"  Why it fails: {self.why_it_fails}\n"
            f"  Harm if deployed: {self.harm_if_deployed}\n"
            f"  Better approach: {self.alternative}\n"
        )


@dataclass
class BuildPlan:
    """What can be built from this study, within its scope."""

    source_claim: str
    scope_summary: str
    legitimate_applications: List[LegitimateApplication] = field(default_factory=list)
    misapplications_to_avoid: List[Misapplication] = field(default_factory=list)
    open_questions_for_extension: List[str] = field(default_factory=list)
    recombination_candidates: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            "=" * 70,
            "BUILD PLAN: KNOWLEDGE LIBERATED WITHIN SCOPE",
            "=" * 70,
            f"Source: {self.source_claim}",
            f"Scope: {self.scope_summary}",
            "",
            "WHAT THIS FINDING SUPPORTS BUILDING:",
            "",
        ]
        for app in self.legitimate_applications:
            lines.append(app.format())

        lines.append("")
        lines.append("WHAT THIS FINDING DOES NOT SUPPORT (MISAPPLICATION):")
        lines.append("")
        for mis in self.misapplications_to_avoid:
            lines.append(mis.format())

        if self.open_questions_for_extension:
            lines.append("EXTEND BY ASKING:")
            for q in self.open_questions_for_extension:
                lines.append(f"  ? {q}")
            lines.append("")

        if self.recombination_candidates:
            lines.append("RECOMBINE WITH:")
            for r in self.recombination_candidates:
                lines.append(f"  + {r}")
            lines.append("")

        lines.append("Knowledge liberated IN SCOPE is usable, testable, buildable.")
        lines.append("Knowledge liberated OUT OF SCOPE is misapplied -- information atrophy.")
        lines.append("The scope map is the boundary. The build lives inside it.")
        lines.append("=" * 70)

        return "\n".join(lines)


# ============================================================
# APPLICATION BUILDER
# ============================================================

class ApplicationBuilder:
    """
    From a scope map and edge questions, derive buildable applications.

    Takes the finding seriously within its scope.
    Generates design constraints, training inputs, research extensions.
    Names misapplications so they are avoided.
    """

    def build(self,
              claim: str,
              scope_population: str,
              scope_environment: str,
              scope_duration: str,
              what_was_measured: str,
              uncontrolled_variables: List[str]) -> BuildPlan:
        """Generate the full build plan."""
        scope_summary = (
            f"{scope_population} / {scope_environment} / {scope_duration}"
        )

        plan = BuildPlan(
            source_claim=claim,
            scope_summary=scope_summary,
        )

        plan.legitimate_applications.extend(
            self._derive_legitimate_applications(
                claim, scope_population, scope_environment,
                scope_duration, what_was_measured
            )
        )
        plan.misapplications_to_avoid.extend(
            self._derive_misapplications(
                claim, scope_population, scope_environment, uncontrolled_variables
            )
        )
        plan.open_questions_for_extension = self._derive_extensions(
            claim, what_was_measured, uncontrolled_variables
        )
        plan.recombination_candidates = self._derive_recombinations(
            claim, what_was_measured)

        return plan

    # ----------------------------------------------------------
    # APPLICATION DERIVATION
    # ----------------------------------------------------------

    def _derive_legitimate_applications(
        self, claim, pop, env, dur, measured
    ) -> List[LegitimateApplication]:
        apps = []

        apps.append(LegitimateApplication(
            domain=ApplicationDomain.FURTHER_RESEARCH,
            description=(
                "Hypothesis generation for studies in populations outside this scope"
            ),
            design_constraint=(
                f"Use this finding as a starting hypothesis for populations with "
                f"different life history than {pop}. Predict and test."
            ),
            scope_conditions=[
                "Treat as hypothesis, not established fact, for new populations",
                "Measure with same instrument to maintain comparability",
                "Pre-register predictions about whether finding replicates",
            ],
        ))

        if any(w in measured.lower() for w in ["conductance", "cortisol",
                                                 "heart", "eeg", "fmri"]):
            apps.append(LegitimateApplication(
                domain=ApplicationDomain.FURTHER_RESEARCH,
                description="Mechanism investigation under controlled conditions",
                design_constraint=(
                    f"The measured signal ({measured}) is reproducible in "
                    f"controlled conditions. Use to investigate underlying mechanism."
                ),
                scope_conditions=[
                    "Controlled laboratory or clinical setting",
                    "Comparable population to original study",
                    "Short measurement window (single session scale)",
                ],
            ))

        apps.append(LegitimateApplication(
            domain=ApplicationDomain.DESIGN_CONSTRAINT,
            description=(
                "Input to design of environments matching the study's scope"
            ),
            design_constraint=(
                f"Where systems will be used by populations similar to {pop}, "
                f"under conditions similar to {env}, the finding can inform "
                f"interface and interaction design."
            ),
            scope_conditions=[
                f"Design context matches {env}",
                f"User population matches {pop}",
                "Usage duration comparable to study's measurement window",
            ],
        ))

        if any(w in claim.lower() for w in ["deficit", "impair", "blunted",
                                              "abnormal", "disorder"]):
            apps.append(LegitimateApplication(
                domain=ApplicationDomain.FRAME_CORRECTION,
                description=(
                    "Correct public overreach of the pathology framing by "
                    "publicizing the scope conditions with equal prominence"
                ),
                design_constraint=(
                    "When citing the finding in public communication, explicitly "
                    "state the population and conditions. Do not generalize."
                ),
                scope_conditions=[
                    "Include scope conditions with every citation",
                    "Name the populations the finding does NOT speak to",
                    "Distinguish measurement from interpretation",
                ],
            ))

        if "lab" in env.lower():
            apps.append(LegitimateApplication(
                domain=ApplicationDomain.FIELD_VALIDATION,
                description=(
                    "Field validation protocol to extend the finding's applicability"
                ),
                design_constraint=(
                    "The lab finding is a hypothesis for field behavior. "
                    "Build ambulatory/naturalistic measurement protocols to test."
                ),
                scope_conditions=[
                    "Preserve the measurement instrument/approach",
                    "Measure in the populations and environments the lab study excluded",
                    "Compare lab and field signals in the same individuals",
                ],
            ))

        return apps

    def _derive_misapplications(
        self, claim, pop, env, uncontrolled
    ) -> List[Misapplication]:
        mis = []

        if any(w in claim.lower() for w in ["adversity", "trauma", "stress",
                                              "deficit", "blunted"]):
            mis.append(Misapplication(
                description=(
                    "Using the finding to screen or categorize individuals "
                    "in populations outside the study's scope."
                ),
                why_it_fails=(
                    f"The study measured {pop} in {env}. "
                    f"It did not measure people whose life has selected for "
                    f"different calibration (survivors, high-threat occupations, "
                    f"long-tenured operators). Applying the finding to those "
                    f"populations assumes they're comparable -- they're not."
                ),
                harm_if_deployed=(
                    "Individuals with genuine adaptation get mislabeled as "
                    "impaired. Interventions remove or suppress adaptive "
                    "capacity. Practitioners, operators, and veterans lose "
                    "credibility because their calibration is read as deficit."
                ),
                alternative=(
                    "Screen only within the scoped population. For populations "
                    "outside scope, treat as open question. Measure outcomes "
                    "in context before categorizing."
                ),
            ))

        if any(w in claim.lower() for w in ["adversity", "trauma", "stress"]):
            mis.append(Misapplication(
                description=(
                    "Using the finding to shape employment, hiring, or licensing "
                    "policy for high-stakes occupations."
                ),
                why_it_fails=(
                    f"The study did not measure occupational performance. "
                    f"It measured a physiological signal in {env}. The "
                    f"inference from lab signal to occupational capability is "
                    f"not supported."
                ),
                harm_if_deployed=(
                    "Exclusion of qualified workers. Replacement with less-"
                    "calibrated workers. Increased injury and error rates. "
                    "Loss of tacit knowledge carriers."
                ),
                alternative=(
                    "Assess occupational capability with occupational measures. "
                    "Keep lab findings to lab/clinical contexts."
                ),
            ))

        mis.append(Misapplication(
            description=(
                "Treating a short-duration finding as predictive of career- "
                "or lifetime-scale outcomes."
            ),
            why_it_fails=(
                "The study could not observe accumulation, recalibration, "
                "or adaptation over longer time scales. The phenomenon may "
                "change direction or magnitude."
            ),
            harm_if_deployed=(
                "Long-term interventions based on short-term measurements. "
                "Missed opportunities for adaptation-based design."
            ),
            alternative=(
                "Require longitudinal evidence before long-horizon application. "
                "Build feedback loops to detect drift."
            ),
        ))

        return mis

    def _derive_extensions(self, claim, measured, uncontrolled) -> List[str]:
        extensions = []
        extensions.append(
            f"What SET OF ontological states could produce the signal '{measured}'? "
            f"Design a protocol that distinguishes them."
        )
        extensions.append(
            "What ambulatory/in-situ measurement would test whether the lab finding "
            "predicts behavior in the actual environment of consequence?"
        )
        if "trauma" in claim.lower() or "adversity" in claim.lower():
            extensions.append(
                "What do the same measurements show in populations selected by "
                "SURVIVAL of sustained threat -- veterans, first responders, "
                "long-haul drivers, salvage crews?"
            )
        for var in uncontrolled[:3]:
            extensions.append(
                f"What is the dose-response relationship between '{var}' and the "
                f"measured signal? At what value does the finding reverse?"
            )
        return extensions

    def _derive_recombinations(self, claim, measured) -> List[str]:
        recomb = []
        if "threat" in claim.lower() or "stress" in claim.lower():
            recomb.extend([
                "Calibration / developmental attractor frameworks (what calibration "
                "was built, not what trauma was endured)",
                "Occupational performance literature (what actual performance "
                "outcomes correlate with the measured signal)",
                "Cross-cultural threat literature (how framing shapes signal)",
                "Adaptive physiology frameworks (cost/benefit of the measured state "
                "in different environments)",
            ])
        if "conductance" in measured.lower() or "physiolog" in measured.lower():
            recomb.append(
                "HRV and allostatic load research (complementary measures that "
                "may disambiguate state vs. trait)"
            )
        recomb.append(
            "Practitioner and operator knowledge (what people with embodied "
            "experience of the conditions say about the measured state)"
        )
        return recomb


# ============================================================
# CONVENIENCE
# ============================================================

def build_applications(claim: str,
                       population: str,
                       environment: str,
                       duration: str,
                       what_was_measured: str,
                       uncontrolled_variables: List[str]) -> str:
    """Quick build plan generation, returns formatted output."""
    builder = ApplicationBuilder()
    plan = builder.build(
        claim=claim,
        scope_population=population,
        scope_environment=environment,
        scope_duration=duration,
        what_was_measured=what_was_measured,
        uncontrolled_variables=uncontrolled_variables,
    )
    return plan.summary()


# ============================================================
# EXAMPLE
# ============================================================

if __name__ == "__main__":
    result = build_applications(
        claim="Childhood adversity associated with blunted threat response",
        population="Undergraduate students with self-reported ACE scores",
        environment="University lab",
        duration="Single session, ~45 minutes",
        what_was_measured="Skin conductance response to conditioned threat cues",
        uncontrolled_variables=[
            "Real-world threat exposure history",
            "Current environment threat level",
            "Pain tolerance baseline",
            "Prior learning/recalibration from survived events",
        ],
    )
    print(result)

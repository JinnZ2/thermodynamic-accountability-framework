"""
recontextualizer.py

Knowledge Liberation Module 6: Plug YOUR context in.

A detected silence is abstract until it meets a specific situation.
The recontextualizer takes a detected silence and generates prompts
that let ANY user -- researcher, practitioner, field worker, AI
system, community member -- ask:

    'This study went silent on X.
     In MY context, what does that gap look like?
     What would I need to measure or ask to fill it?'

The module is deliberately GENERIC. It does not assume the user is in
any specific place, profession, or discipline. Users provide their own
context; the module generates the prompt architecture that turns the
silence into actionable exploration in that context.

License: CC0
Ported from github.com/JinnZ2/Logic-Ferret/knowledge/recontextualizer.py
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


# ============================================================
# CONTEXT TYPES
# ============================================================

class ContextRole(Enum):
    """What role is the person playing when they engage with the finding?"""
    RESEARCHER = "researcher"
    PRACTITIONER = "practitioner"
    FIELD_WORKER = "field_worker"
    POLICY_MAKER = "policy_maker"
    COMMUNITY_MEMBER = "community_member"
    EDUCATOR = "educator"
    AI_SYSTEM = "ai_system"
    BUILDER = "builder"
    GENERIC = "generic"


@dataclass
class UserContext:
    """
    The user's context for recontextualization.
    All fields optional -- user supplies what they have. The more detail,
    the more specific the generated prompts will be.
    """
    role: ContextRole = ContextRole.GENERIC
    domain: str = ""
    location_or_region: str = ""
    population_of_interest: str = ""
    time_horizon: str = ""
    available_resources: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    goal: str = ""

    def describe(self) -> str:
        parts = []
        if self.role != ContextRole.GENERIC:
            parts.append(f"role: {self.role.value}")
        if self.domain:
            parts.append(f"domain: {self.domain}")
        if self.location_or_region:
            parts.append(f"location/region: {self.location_or_region}")
        if self.population_of_interest:
            parts.append(f"population: {self.population_of_interest}")
        if self.time_horizon:
            parts.append(f"horizon: {self.time_horizon}")
        if self.goal:
            parts.append(f"goal: {self.goal}")
        return " | ".join(parts) if parts else "generic context"


# ============================================================
# RECONTEXTUALIZED PROMPT
# ============================================================

@dataclass
class RecontextualizedPrompt:
    """A silence made actionable in a specific context."""
    original_silence: str
    user_context_description: str
    localized_question: str
    what_to_observe: List[str]
    what_to_measure: List[str]
    who_to_ask: List[str]
    where_to_look: List[str]
    small_experiment: str
    build_possibility: str

    def format(self) -> str:
        lines = [
            "-" * 70,
            f"SILENCE: {self.original_silence}",
            f"CONTEXT: {self.user_context_description}",
            "-" * 70,
            "",
            "LOCALIZED QUESTION:",
            f"  {self.localized_question}",
            "",
            "WHAT TO OBSERVE IN YOUR CONTEXT:",
        ]
        for item in self.what_to_observe:
            lines.append(f"  * {item}")
        lines.append("")
        lines.append("WHAT TO MEASURE (if you have the means):")
        for item in self.what_to_measure:
            lines.append(f"  # {item}")
        lines.append("")
        lines.append("WHO TO ASK:")
        for item in self.who_to_ask:
            lines.append(f"  @ {item}")
        lines.append("")
        lines.append("WHERE TO LOOK:")
        for item in self.where_to_look:
            lines.append(f"  > {item}")
        lines.append("")
        lines.append("SMALL EXPERIMENT:")
        lines.append(f"  {self.small_experiment}")
        lines.append("")
        lines.append("COULD BE BUILT:")
        lines.append(f"  {self.build_possibility}")
        lines.append("")
        return "\n".join(lines)


# ============================================================
# RECONTEXTUALIZER
# ============================================================

class Recontextualizer:
    """
    Takes a silence + a user context and generates actionable prompts.
    This is SCAFFOLDING. The generated prompts are starting points for
    the user's own thinking, not exhaustive lists. The user knows their
    context better than any generator could.
    """

    def recontextualize(self,
                        silence: str,
                        context: UserContext,
                        silence_category_hint: str = "") -> RecontextualizedPrompt:
        """Generate a recontextualized prompt for a specific silence."""
        return RecontextualizedPrompt(
            original_silence=silence,
            user_context_description=context.describe(),
            localized_question=self._localize_question(silence, context),
            what_to_observe=self._observations(
                silence, context, silence_category_hint),
            what_to_measure=self._measurements(
                silence, context, silence_category_hint),
            who_to_ask=self._sources(context, silence_category_hint),
            where_to_look=self._places(
                silence, context, silence_category_hint),
            small_experiment=self._experiment(
                silence, context, silence_category_hint),
            build_possibility=self._build(
                silence, context, silence_category_hint),
        )

    # ----------------------------------------------------------
    # PROMPT GENERATION
    # ----------------------------------------------------------

    def _localize_question(self, silence: str, context: UserContext) -> str:
        """Translate the silence into a context-anchored question."""
        location = context.location_or_region or "your context"
        population = context.population_of_interest or "the people you work with"

        return (
            f"The study goes silent on: {silence} "
            f"In {location}, among {population}, what does this gap look like? "
            f"What would you need to know to answer the question the study didn't ask?"
        )

    def _observations(self, silence: str, context: UserContext,
                      category: str) -> List[str]:
        """Things to NOTICE without formal measurement."""
        obs = [
            "Patterns in who shows up vs. who doesn't",
            "What people say about the situation vs. what the data records",
            "Where the measured variable and the actual phenomenon diverge",
        ]

        silence_lower = silence.lower()

        if any(w in silence_lower for w in ["population", "sample", "participant"]):
            obs.append(
                "Who in your context is typically left out of this kind of data?")
            obs.append(
                "What characteristics would exclude someone from being counted?")

        if any(w in silence_lower for w in ["time", "duration", "long-term", "long term"]):
            obs.append(
                "How does the pattern look different over a day vs. a year vs. "
                "a decade in your context?")
            obs.append(
                "Who in your context has the longest continuous observation?")

        if any(w in silence_lower for w in ["environment", "context", "setting"]):
            obs.append(
                "How does the surrounding environment differ from the study setting?")
            obs.append(
                "What local conditions change the phenomenon's expression?")

        if any(w in silence_lower for w in ["threat", "safety", "risk", "danger"]):
            obs.append(
                "What does actual threat look like in your context vs. the lab setup?")
            obs.append(
                "Who in your context has genuine calibration to real threat?")

        if any(w in silence_lower for w in ["incentive", "report", "self-report"]):
            obs.append(
                "Who benefits from reporting vs. not reporting in your context?")
            obs.append(
                "What gets recorded vs. what everyone knows but nobody writes down?")

        return obs

    def _measurements(self, silence: str, context: UserContext,
                      category: str) -> List[str]:
        """Things to actually quantify, scaled to what user can access."""
        measurements = []
        silence_lower = silence.lower()

        if context.available_resources:
            measurements.append(
                f"Using your available resources "
                f"({', '.join(context.available_resources[:3])}), "
                f"what aspect of the silence could you quantify locally?"
            )

        if any(w in silence_lower for w in ["population", "sample"]):
            measurements.append(
                "Basic demographics of YOUR relevant population, "
                "compared to the study sample")
            measurements.append(
                "Proportion of your population that would have been "
                "excluded from the study")

        if any(w in silence_lower for w in ["time", "duration"]):
            measurements.append(
                "The actual time scale over which the phenomenon unfolds "
                "in your context")
            measurements.append(
                "Rates of change, accumulation, or reversal in your "
                "longitudinal observations")

        if any(w in silence_lower for w in ["environment", "context"]):
            measurements.append(
                "Key environmental variables present in your context but "
                "absent in the study")

        if any(w in silence_lower for w in ["threat", "adversity", "stress"]):
            measurements.append(
                "Objective indicators of threat level in your population's "
                "current circumstances")
            measurements.append(
                "Ratio of people with accurate threat detection to those "
                "with mismatched calibration")

        if any(w in silence_lower for w in ["report", "record", "data"]):
            measurements.append(
                "Report rates vs. estimated underlying rates "
                "(via independent observation)")

        if not measurements:
            measurements.append(
                "Any locally-accessible quantification of the variable "
                "the study ignored")

        return measurements

    def _sources(self, context: UserContext, category: str) -> List[str]:
        """Who holds the tacit/embodied knowledge the study cannot capture."""
        sources = [
            "People with direct lived experience of the phenomenon",
            "Practitioners with long tenure in the domain",
            "Elders, old-timers, or carriers of generational knowledge "
            "relevant to the context",
        ]

        if context.role == ContextRole.RESEARCHER:
            sources.append(
                "Colleagues in adjacent fields who might see the blind spot")
            sources.append(
                "Community members from the populations your study will affect")

        if context.role == ContextRole.PRACTITIONER:
            sources.append(
                "Your most experienced colleagues -- what do they notice "
                "that isn't in protocols?")
            sources.append(
                "Clients/patients/users who have been in the system long "
                "enough to see patterns")

        if context.role == ContextRole.FIELD_WORKER:
            sources.append("Community members you work with -- ask directly")
            sources.append(
                "Workers from adjacent fields who touch the same people from "
                "a different angle")

        if context.role == ContextRole.POLICY_MAKER:
            sources.append(
                "People the policy will actually affect -- before drafting, "
                "not after")
            sources.append(
                "Implementers who see what breaks when policy meets field reality")

        if context.role == ContextRole.AI_SYSTEM:
            sources.append(
                "Users of the system who might hold knowledge absent from "
                "your training data")
            sources.append(
                "Human operators who can correct your pattern-matching with "
                "embodied context")

        return sources

    def _places(self, silence: str, context: UserContext,
                category: str) -> List[str]:
        """Where to look for information that fills the silence."""
        places = [
            "Studies in populations the original research did not sample",
            "Field data or operational records from settings outside the "
            "study environment",
            "Practitioner communities that talk about the phenomenon from inside",
        ]

        silence_lower = silence.lower()

        if any(w in silence_lower for w in ["time", "long-term", "long term"]):
            places.append("Longitudinal datasets in your domain")
            places.append(
                "Historical records that predate the current measurement paradigm")

        if any(w in silence_lower for w in ["population", "sample"]):
            places.append(
                "Databases or registries that capture the excluded population")
            places.append(
                "Grey literature from community organizations serving "
                "excluded populations")

        if any(w in silence_lower for w in ["incentive", "report"]):
            places.append(
                "Whistleblower reports or investigative journalism in the "
                "relevant sector")
            places.append(
                "Anonymous surveys that bypass official reporting channels")

        if any(w in silence_lower for w in ["environment", "field", "context"]):
            places.append(
                "Ethnographic or qualitative research in the relevant "
                "field context")
            places.append(
                "Operational/engineering reports from the actual deployment "
                "environment")

        return places

    def _experiment(self, silence: str, context: UserContext,
                    category: str) -> str:
        """A small, actionable thing the user could do."""
        horizon = context.time_horizon or "the next few days or weeks"

        if context.role == ContextRole.RESEARCHER:
            return (
                f"Within {horizon}, design a small pilot study that varies the "
                f"silent variable identified here. Even a qualitative pilot counts."
            )
        if context.role == ContextRole.PRACTITIONER:
            return (
                f"Within {horizon}, track one additional variable in your normal "
                f"practice -- the one the study didn't measure. See if it shifts "
                f"your understanding of your own cases."
            )
        if context.role == ContextRole.FIELD_WORKER:
            return (
                f"Within {horizon}, ask three people directly about the question "
                f"the study silence raised. Compare their answers to the study's "
                f"claim."
            )
        if context.role == ContextRole.COMMUNITY_MEMBER:
            return (
                f"Within {horizon}, notice how the finding does or doesn't fit "
                f"your own experience. Where does it match? Where does it diverge?"
            )
        if context.role == ContextRole.AI_SYSTEM:
            return (
                f"When next generating a response that involves this finding, "
                f"explicitly note the silence and invite the user to provide "
                f"their context to test whether the finding applies."
            )
        if context.role == ContextRole.BUILDER:
            return (
                f"Within {horizon}, sketch a design that would FAIL if the "
                f"silence were real. Then sketch one that would work either way."
            )

        return (
            f"Within {horizon}, find one concrete instance in your context where "
            f"the silence matters. Just one. Examine that instance closely."
        )

    def _build(self, silence: str, context: UserContext, category: str) -> str:
        """Something that could be built using the answer."""
        if context.goal:
            return (
                f"Given your goal ({context.goal}), the answer to this silence "
                f"could inform a tool, protocol, or system that accounts for the "
                f"currently-invisible variable. Sketch what that tool would need "
                f"to do."
            )

        return (
            f"A tool, protocol, or framework that SURFACES this currently-silent "
            f"variable could be built. Who else would benefit from having it? "
            f"What would the minimum viable version look like?"
        )


# ============================================================
# BATCH RECONTEXTUALIZATION
# ============================================================

def recontextualize_silences(silences: List[str],
                              context: UserContext) -> str:
    """Take a list of silences and a context; return formatted output for all."""
    recon = Recontextualizer()

    lines = [
        "=" * 70,
        "RECONTEXTUALIZATION: YOUR CONTEXT APPLIED TO DETECTED SILENCES",
        "=" * 70,
        f"User context: {context.describe()}",
        f"Silences to recontextualize: {len(silences)}",
        "",
    ]

    for i, silence in enumerate(silences, 1):
        lines.append(f"### Silence {i} of {len(silences)}")
        prompt = recon.recontextualize(silence, context)
        lines.append(prompt.format())

    lines.append("=" * 70)
    lines.append("Each silence now has a foothold in your specific context.")
    lines.append("Start with the one that matters most to your current work.")
    lines.append("=" * 70)

    return "\n".join(lines)


# ============================================================
# EXAMPLES
# ============================================================

if __name__ == "__main__":

    print("\n" + "#" * 70)
    print("# EXAMPLE 1: PUBLIC HEALTH RESEARCHER")
    print("#" * 70 + "\n")

    context1 = UserContext(
        role=ContextRole.RESEARCHER,
        domain="public health epidemiology",
        location_or_region="mid-sized city with diverse income strata",
        population_of_interest="adults 18-65 across employment statuses",
        time_horizon="3-year study window",
        available_resources=["municipal health data", "community partnerships",
                              "small research budget"],
        constraints=["IRB limits on crisis populations",
                      "self-report instruments only"],
        goal=("design a follow-up study that addresses the original sample's "
              "selection bias"),
    )
    silences1 = [
        "Study excluded people in acute crisis (sample is employed/stable)",
        "Does NOT distinguish accurate vs. false threat assessment",
    ]
    print(recontextualize_silences(silences1, context1))

    print("\n\n" + "#" * 70)
    print("# EXAMPLE 2: COMMUNITY HEALTH WORKER")
    print("#" * 70 + "\n")

    context2 = UserContext(
        role=ContextRole.FIELD_WORKER,
        domain="community health outreach",
        location_or_region="rural communities with limited clinical infrastructure",
        population_of_interest="families facing economic precarity",
        time_horizon="year-round",
        available_resources=["direct relationships with community members",
                              "lived experience", "peer networks"],
        constraints=["no research budget", "limited formal training in methods"],
        goal="advocate for accurate framing of mental health challenges in my community",
    )
    silences2 = [
        "Study excluded people in acute crisis (sample is employed/stable)",
        "Does NOT distinguish accurate vs. false threat assessment",
    ]
    print(recontextualize_silences(silences2, context2))

    print("\n\n" + "#" * 70)
    print("# EXAMPLE 3: AI SYSTEM GENERATING A RESPONSE")
    print("#" * 70 + "\n")

    context3 = UserContext(
        role=ContextRole.AI_SYSTEM,
        domain="general-purpose language model",
        population_of_interest="anyone who might ask about this finding",
        time_horizon="each conversational turn",
        goal="generate responses that honor the scope of the underlying evidence",
    )
    silences3 = [
        "Study excluded people in acute crisis (sample is employed/stable)",
    ]
    print(recontextualize_silences(silences3, context3))

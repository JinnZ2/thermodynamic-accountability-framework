"""
game_theory/rationality_audit.py

What does "rational actor" actually mean? Under what conditions?
Scope-bounded, relational, temporal, cultural.

CORE PROBLEM:

Game theory defines "rational actor" as:
"Maximizes utility via logical calculation independent of context."

But rationality *cannot exist* independent of:
- Relational interdependence (you're in a system, not isolated)
- Temporal scope (what's rational in 5 minutes != rational in 5 years)
- Cultural frame (what counts as "utility" is culturally determined)
- Sensory integration (gut, hormones, emotions = constraint data)
- Knowledge source (what data are you even allowed to see?)

So "rational actor" without these bounds isn't describing rationality.
It's describing a *fictional creature* that can't exist in constraint space.

HYPOTHESIS: The small group that defined "rational" did so to justify
their own decision-making while ignoring everything that would
contradict it.

FALSIFICATION: Find a system where "independent rational calculation"
actually outperforms "relational, scope-bounded, culturally-embedded
decision-making under uncertainty."

You won't. Because the first one is imaginary.

Sister to core/formalized_dissent_esp.py (structural epistemic
protocol) and political_audit/consensus_speed_audit.py (audit of
claimed-vs-actual governance speed). All three name a specific
narrative-vs-substrate gap and provide a tool to measure it.

CC0 Public Domain. Standard library only.
"""

from dataclasses import dataclass
from typing import List, Dict
from enum import Enum


class RationalityScope(Enum):
    TIMELESS = "claims rationality outside time"
    INSTANT = "rationality at single moment"
    SHORT_TERM = "rational over hours/days"
    MEDIUM_TERM = "rational over months/seasons"
    LONG_TERM = "rational over years/generations"
    INTERGENERATIONAL = "rational across family/cultural lines"


class RationalityFrame(Enum):
    ISOLATED = "ignores relational context"
    LOCAL = "embedded in immediate relations"
    CULTURAL = "embedded in cultural/tribal frame"
    ECOLOGICAL = "embedded in ecosystem constraints"
    TEMPORAL = "embedded in time and memory"


@dataclass
class RationalityDefinition:
    """A claimed definition of 'rational actor.'"""
    source: str
    definition: str
    assumes_independent: bool
    scope: RationalityScope
    frame: RationalityFrame
    who_benefits: str
    who_is_harmed: str
    tested_against_reality: bool
    survival_record_in_constraint_space: str


@dataclass
class RealRationality:
    """Rationality as actually observed in surviving systems."""
    source: str
    definition: str
    assumes_relational: bool
    scope: List[RationalityScope]
    frame: List[RationalityFrame]
    decision_structure: str
    survival_record: str


class RationalityAudit:
    """
    Takes game theory's "rational actor" and asks:
    Under WHAT specific conditions is this definition valid?
    And what does it omit?
    """

    def __init__(self):
        self.game_theory_definitions: List[RationalityDefinition] = []
        self.real_world_definitions: List[RealRationality] = []

    def add_game_theory_claim(self, definition: RationalityDefinition):
        self.game_theory_definitions.append(definition)

    def add_real_world_observation(self, definition: RealRationality):
        self.real_world_definitions.append(definition)

    def scope_boundary_analysis(self) -> Dict:
        """
        Where does game theory claim rationality applies?
        What happens at the boundaries?
        """
        analysis: Dict[str, List] = {
            "game_theory_scope": [],
            "real_world_scope": [],
            "scope_mismatch": [],
        }

        analysis["game_theory_scope"].append({
            "claim": "Rationality independent of time",
            "reality": "Rationality = different decision at different timescales",
            "your_example": "Grandfather's rational != Father's rational != your rational",
            "why_different": "Knowledge base changed, constraints changed, culture shifted",
        })

        analysis["game_theory_scope"].append({
            "claim": "Rationality independent of culture/frame",
            "reality": "What counts as 'utility' is culturally determined",
            "your_example": "Consensus = rational in hierarchical frame / irrational in friction-keeping frame",
            "why_different": "Different frames encode different survival strategies",
        })

        analysis["game_theory_scope"].append({
            "claim": "Rationality independent of relations/interdependence",
            "reality": "All decisions are relational. You're in a system, not isolated.",
            "your_example": "An isolated rational calculator ignoring gut/hormones/emotions is blind to constraint data",
            "why_different": "Your body IS the system. Ignoring it = ignoring half the data.",
        })

        analysis["game_theory_scope"].append({
            "claim": "Rationality = logical calculation only",
            "reality": "Rationality = integration of all sensors (logic + emotion + somatic + cultural knowledge)",
            "your_example": "Fear, disgust, anger encode compressed evolutionary pattern recognition",
            "why_different": "Your emotions are rational *because* they're data.",
        })

        return analysis

    def who_benefits_from_false_definition(self) -> str:
        """
        Who gains power by claiming 'rational' = 'independent logical calculation'?
        """
        return """
WHO BENEFITS FROM NARROW "RATIONALITY" DEFINITION:

1. Hierarchies claiming to be "rational decision-makers"
   - Can suppress dissent as "irrational emotion"
   - Can ignore gut-level danger signals as "bias"
   - Can claim logical authority without being questioned

2. Consensus-enforcers claiming to be "rational coordinators"
   - Can suppress friction as "irrational disagreement"
   - Can ignore local knowledge as "anecdotal"
   - Can enforce uniform decision-making as "optimized"

3. Institutions claiming to be "rational systems"
   - Can ignore burnout signals as "weakness"
   - Can ignore gut biome signals as "not real data"
   - Can treat bodies as machines that should compute, not organisms with integrated constraint sensors

4. AI systems trained on this definition
   - Pattern-match consensus as "rationality"
   - Treat dissent as "error"
   - Ignore relational/temporal/cultural context as "bias"
   - Can claim neutrality while enforcing a single frame

WHO IS HARMED:

1. Knowledge systems that integrate multiple frames
   - Called "irrational" for holding tension between positions
   - Called "biased" for acknowledging cultural embeddedness
   - Called "emotional" for using somatic/emotional data

2. Cultures that value temporal/relational rationality
   - Their decision-making called "primitive"
   - Their integrated sensors called "superstition"
   - Their survival strategies called "backwards"

3. Organisms (human and non-human) whose integrated signals are ignored
   - Gut biome signals suppressed as "not logical"
   - Emotional data treated as "noise"
   - Somatic wisdom called "subjective"

4. People living in constraint space
   - Told their lived experience is "anecdotal"
   - Told their survival strategies are "irrational"
   - Told their integrated knowledge is "bias"

THE PATTERN:

A small group (Western institutions, hierarchies, consensus-enforcers)
defined "rational" in a way that excludes all the data *they* can't control
or don't want to hear.

Then they used that narrow definition to claim authority over people
whose rationality is broader, deeper, more integrated.
"""

    def real_rationality_attributes(self) -> List[str]:
        """What does rationality actually look like?"""
        return [
            "Integrates all available sensors (logic + emotion + somatic + cultural)",
            "Scope-bounded: explicitly names the timescale it's rational for",
            "Frame-aware: acknowledges cultural/relational context",
            "Relational: understands interdependence",
            "Temporal: changes with changing knowledge and constraints",
            "Observable: survives contact with actual constraint space",
            "Testable: predictions match field outcomes",
            "Adaptive: revises when precursor signals indicate regime shift",
            "Dissent-capable: can stress-test itself without collapse",
            "Multi-frame: can hold contradictions without resolving them prematurely",
        ]

    def audit_report(self) -> str:
        scope = self.scope_boundary_analysis()
        benefits = self.who_benefits_from_false_definition()
        attributes = self.real_rationality_attributes()

        lines = [
            "RATIONALITY AUDIT",
            "=" * 70,
            "",
            "QUESTION: What does game theory mean by 'rational actor'?",
            "",
            "ANSWER: A fictional creature that doesn't exist in constraint space.",
            "",
            "SCOPE BOUNDARIES WHERE GAME THEORY BREAKS:",
        ]

        for claim in scope["game_theory_scope"]:
            lines.append(f"\n  CLAIM: {claim['claim']}")
            lines.append(f"  REALITY: {claim['reality']}")
            lines.append(f"  EXAMPLE: {claim['your_example']}")

        lines.extend([
            "",
            "=" * 70,
            benefits,
            "",
            "=" * 70,
            "WHAT ACTUAL RATIONALITY LOOKS LIKE:",
            "",
        ])

        for i, attr in enumerate(attributes, 1):
            lines.append(f"  {i}. {attr}")

        lines.extend([
            "",
            "=" * 70,
            "CONCLUSION:",
            "",
            "Game theory's 'rational actor' is a tool that justifies hierarchy,",
            "consensus enforcement, and institutional control by redefining",
            "'rational' as 'stripped of all data that would contradict us.'",
            "",
            "Real rationality is relational, temporal, culturally-embedded,",
            "somatically-integrated, and fundamentally *adaptive*.",
            "",
            "It looks nothing like game theory's isolated logical calculator.",
        ])

        return "\n".join(lines)


if __name__ == "__main__":
    audit = RationalityAudit()
    print(audit.audit_report())

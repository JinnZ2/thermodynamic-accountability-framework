"""
knowledge_liberation.py

ORCHESTRATOR: the practice itself.

Take a study. Run the full pipeline:
1. scope_mapper    -> map what it actually measured
2. edge_explorer   -> generate questions at the edges
3. application_builder -> derive what can be built within scope

Output: a study clarified, liberated, and usable --
with misapplications named so they can be avoided.

This is knowledge liberation in scope.

License: CC0
Ported from github.com/JinnZ2/Logic-Ferret/knowledge/knowledge_liberation.py
"""

from dataclasses import dataclass
from typing import List, Dict, Any

from scope_mapper import ScopeMapper
from edge_explorer import EdgeExplorer
from application_builder import ApplicationBuilder


@dataclass
class StudyInput:
    """What you read when you picked up the paper."""
    claimed_finding: str
    what_was_measured: str
    measurement_instrument: str
    population: str
    population_size: int
    environment: str
    duration: str
    controlled_variables: List[str]
    uncontrolled_variables: List[str]


def liberate(study: StudyInput) -> str:
    """
    Run the full knowledge-liberation pipeline on a study.

    Returns a unified output document:
        - Scope Map (what the study legitimately shows)
        - Edge Exploration (generative questions at boundaries)
        - Build Plan (legitimate applications + misapplications to avoid)
    """
    mapper = ScopeMapper()
    explorer = EdgeExplorer()
    builder = ApplicationBuilder()

    scope = mapper.map_study(
        claimed_finding=study.claimed_finding,
        what_was_measured=study.what_was_measured,
        measurement_instrument=study.measurement_instrument,
        population=study.population,
        population_size=study.population_size,
        environment=study.environment,
        duration=study.duration,
        controlled=study.controlled_variables,
        uncontrolled=study.uncontrolled_variables,
    )

    exploration = explorer.explore(
        claim=study.claimed_finding,
        what_was_measured=study.what_was_measured,
        population=study.population,
        environment=study.environment,
        duration=study.duration,
        uncontrolled_variables=study.uncontrolled_variables,
    )

    plan = builder.build(
        claim=study.claimed_finding,
        scope_population=study.population,
        scope_environment=study.environment,
        scope_duration=study.duration,
        what_was_measured=study.what_was_measured,
        uncontrolled_variables=study.uncontrolled_variables,
    )

    output = [
        "#" * 70,
        "#" + " " * 68 + "#",
        "#" + "  KNOWLEDGE LIBERATION PIPELINE".ljust(68) + "#",
        "#" + "  Study -> Scope -> Edges -> Build".ljust(68) + "#",
        "#" + " " * 68 + "#",
        "#" * 70,
        "",
        "STAGE 1 -- SCOPE MAP",
        "",
        scope.as_liberation_statement(),
        "",
        "",
        "STAGE 2 -- EDGE EXPLORATION",
        "",
        exploration.summary(),
        "",
        "",
        "STAGE 3 -- BUILD PLAN",
        "",
        plan.summary(),
        "",
        "",
        "#" * 70,
        "#" + "  PIPELINE COMPLETE".ljust(68) + "#",
        "#" + "  The study is scoped, explored, and ready to use or extend.".ljust(68) + "#",
        "#" * 70,
    ]

    return "\n".join(output)


if __name__ == "__main__":
    study = StudyInput(
        claimed_finding="Childhood adversity associated with blunted threat response",
        what_was_measured="Skin conductance response to conditioned threat cues",
        measurement_instrument="Skin conductance electrodes",
        population="Undergraduate students with self-reported ACE scores",
        population_size=128,
        environment="University lab, controlled lighting, 22C",
        duration="Single session, approximately 45 minutes",
        controlled_variables=["Ambient temperature", "Stimulus presentation timing"],
        uncontrolled_variables=[
            "Real-world threat exposure history",
            "Current environment threat level",
            "Pain tolerance baseline",
            "Prior learning/recalibration from survived events",
            "Cultural framing of threat",
        ],
    )

    print(liberate(study))

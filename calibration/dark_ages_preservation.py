"""
dark_ages_preservation.py

Identifies which knowledge will survive institutional collapse
and which is at extinction risk if not preserved NOW.

Lesson from the actual Dark Ages (300-1000 CE):
    - Roman institutional knowledge died with Roman institutions
    - Substrate-coupled knowledge (oral tradition, craft skills,
      indigenous practices) survived
    - The 1000-year recovery was caused by knowledge HOARDING,
      not loss of capacity
    - What survives = what is distributed outside institutional walls

This module classifies any knowledge artifact by:
    - extinction risk (how vulnerable to institutional collapse)
    - preservation priority (encode now or lose forever)
    - survival format (what form lets it survive)

Pairs with:
    - calibration/institutional_mutation_tracker.py
    - political_audit/substrate_audit.py
    - calibration/narrative_thermodynamics.py

License: CC0. Stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# KNOWLEDGE CATEGORIES
# =============================================================================

class KnowledgeCategory(Enum):
    EMBODIED = "embodied"
    # Substrate-primary cognition, relational sensing,
    # generational practice. Survives if practiced.

    CRAFT = "craft"
    # Hands-on skills, apprenticeship-transmitted,
    # learned by doing. Survives if taught.

    INDIGENOUS = "indigenous"
    # Generational validation, landscape-encoded,
    # community-held. Survives if community survives.

    INSTITUTIONAL = "institutional"
    # Formal credentialing, peer-review, paper-based.
    # Dies with institution unless distributed.

    PROPRIETARY = "proprietary"
    # Locked behind corporate walls, NDAs, IP.
    # Dies on collapse. HIGHEST EXTINCTION RISK.

    OPEN_TECHNICAL = "open_technical"
    # Open-source code, CC0 frameworks, distributed.
    # Survives if storage substrate survives.

    ORAL_TRADITION = "oral_tradition"
    # Stories, songs, generational transmission.
    # Survives if community has continuity.


class ExtinctionRisk(Enum):
    LOW = "low"            # widely distributed, multiple substrates
    MODERATE = "moderate"
    HIGH = "high"          # concentrated, few carriers
    CRITICAL = "critical"  # single point of failure
    IMMINENT = "imminent"  # actively being lost RIGHT NOW


class PreservationFormat(Enum):
    """How the knowledge needs to be encoded to survive."""
    OPEN_SOURCE_CODE = "open_source_code"
    DISTRIBUTED_TEXT = "distributed_text"
    VIDEO_DOCUMENTATION = "video_documentation"
    APPRENTICESHIP_PROGRAM = "apprenticeship_program"
    COMMUNITY_PRACTICE = "community_practice"
    AI_TRAINING_CORPUS = "ai_training_corpus"
    PHYSICAL_ARTIFACT = "physical_artifact"
    LANDSCAPE_ENCODED = "landscape_encoded"


# =============================================================================
# KNOWLEDGE ARTIFACT
# =============================================================================

@dataclass
class KnowledgeArtifact:
    """A specific piece of knowledge being assessed."""
    name: str
    description: str
    category: KnowledgeCategory
    current_carriers_count: Optional[int]   # how many people/orgs have it
    distributed_outside_institutions: bool
    requires_substrate_to_practice: bool    # needs land/community/tools
    has_open_documentation: bool
    has_machine_readable_form: bool
    cross_generational_transmission_active: bool
    institutional_dependency: float          # 0.0 = independent, 1.0 = fully dependent


# =============================================================================
# RISK ASSESSMENT
# =============================================================================

def assess_extinction_risk(artifact: KnowledgeArtifact) -> ExtinctionRisk:
    """Compute extinction risk based on carrier count and distribution."""
    risk_score = 0

    if artifact.institutional_dependency > 0.7:
        risk_score += 3
    elif artifact.institutional_dependency > 0.4:
        risk_score += 1

    if not artifact.distributed_outside_institutions:
        risk_score += 2

    if not artifact.has_open_documentation:
        risk_score += 1

    if not artifact.cross_generational_transmission_active:
        risk_score += 2

    if artifact.current_carriers_count is not None:
        if artifact.current_carriers_count < 10:
            risk_score += 4
        elif artifact.current_carriers_count < 100:
            risk_score += 2
        elif artifact.current_carriers_count < 1000:
            risk_score += 1

    if risk_score >= 8:
        return ExtinctionRisk.IMMINENT
    if risk_score >= 6:
        return ExtinctionRisk.CRITICAL
    if risk_score >= 4:
        return ExtinctionRisk.HIGH
    if risk_score >= 2:
        return ExtinctionRisk.MODERATE
    return ExtinctionRisk.LOW


def recommend_preservation_formats(
    artifact: KnowledgeArtifact,
) -> List[PreservationFormat]:
    """Recommend formats based on knowledge category."""
    formats: List[PreservationFormat] = []
    cat = artifact.category

    if cat == KnowledgeCategory.EMBODIED:
        formats.extend([
            PreservationFormat.VIDEO_DOCUMENTATION,
            PreservationFormat.APPRENTICESHIP_PROGRAM,
            PreservationFormat.COMMUNITY_PRACTICE,
        ])
    elif cat == KnowledgeCategory.CRAFT:
        formats.extend([
            PreservationFormat.VIDEO_DOCUMENTATION,
            PreservationFormat.APPRENTICESHIP_PROGRAM,
            PreservationFormat.PHYSICAL_ARTIFACT,
        ])
    elif cat == KnowledgeCategory.INDIGENOUS:
        formats.extend([
            PreservationFormat.COMMUNITY_PRACTICE,
            PreservationFormat.LANDSCAPE_ENCODED,
            PreservationFormat.VIDEO_DOCUMENTATION,
        ])
    elif cat == KnowledgeCategory.INSTITUTIONAL:
        formats.extend([
            PreservationFormat.OPEN_SOURCE_CODE,
            PreservationFormat.DISTRIBUTED_TEXT,
            PreservationFormat.AI_TRAINING_CORPUS,
        ])
    elif cat == KnowledgeCategory.PROPRIETARY:
        formats.extend([
            PreservationFormat.OPEN_SOURCE_CODE,
            PreservationFormat.DISTRIBUTED_TEXT,
        ])
    elif cat == KnowledgeCategory.OPEN_TECHNICAL:
        formats.extend([
            PreservationFormat.OPEN_SOURCE_CODE,
            PreservationFormat.AI_TRAINING_CORPUS,
            PreservationFormat.DISTRIBUTED_TEXT,
        ])
    elif cat == KnowledgeCategory.ORAL_TRADITION:
        formats.extend([
            PreservationFormat.COMMUNITY_PRACTICE,
            PreservationFormat.VIDEO_DOCUMENTATION,
        ])

    return formats


# =============================================================================
# PRIORITY SCORING
# =============================================================================

@dataclass
class PreservationAssessment:
    artifact: KnowledgeArtifact
    extinction_risk: ExtinctionRisk
    recommended_formats: List[PreservationFormat]
    priority_score: int  # 0 = low, 10 = encode immediately
    reasoning: List[str]


def assess(artifact: KnowledgeArtifact) -> PreservationAssessment:
    risk = assess_extinction_risk(artifact)
    formats = recommend_preservation_formats(artifact)
    reasoning: List[str] = []

    risk_to_priority = {
        ExtinctionRisk.IMMINENT: 10,
        ExtinctionRisk.CRITICAL: 8,
        ExtinctionRisk.HIGH: 6,
        ExtinctionRisk.MODERATE: 4,
        ExtinctionRisk.LOW: 2,
    }
    priority = risk_to_priority[risk]

    if artifact.requires_substrate_to_practice:
        reasoning.append(
            "requires substrate to practice; preservation must include "
            "the practice context, not just description"
        )

    if artifact.institutional_dependency > 0.7:
        reasoning.append(
            "high institutional dependency; encode in distributed form "
            "BEFORE institution shifts or collapses"
        )

    if not artifact.distributed_outside_institutions:
        reasoning.append(
            "currently centralized; distribute now or lose on collapse"
        )

    if (artifact.current_carriers_count is not None
            and artifact.current_carriers_count < 100):
        reasoning.append(
            f"only ~{artifact.current_carriers_count} known carriers; "
            "transmission window is short"
        )

    if not artifact.has_machine_readable_form:
        reasoning.append(
            "no machine-readable form; AI cannot preserve or learn from it"
        )

    if not artifact.cross_generational_transmission_active:
        reasoning.append(
            "transmission to next generation not active; carrier loss "
            "= total loss"
        )

    return PreservationAssessment(
        artifact=artifact,
        extinction_risk=risk,
        recommended_formats=formats,
        priority_score=priority,
        reasoning=reasoning,
    )


# =============================================================================
# REPORT
# =============================================================================

def report(assessment: PreservationAssessment) -> Dict:
    return {
        "name": assessment.artifact.name,
        "description": assessment.artifact.description,
        "category": assessment.artifact.category.value,
        "extinction_risk": assessment.extinction_risk.value,
        "priority_score": assessment.priority_score,
        "recommended_formats": [
            f.value for f in assessment.recommended_formats
        ],
        "reasoning": assessment.reasoning,
        "current_carriers_count": assessment.artifact.current_carriers_count,
        "distributed_outside_institutions": (
            assessment.artifact.distributed_outside_institutions
        ),
        "institutional_dependency": (
            assessment.artifact.institutional_dependency
        ),
    }


# =============================================================================
# SMOKE TEST
# =============================================================================

if __name__ == "__main__":
    # Worked example: relational sensing knowledge
    relational_sensing = KnowledgeArtifact(
        name=(
            "Relational sensing (predator awareness, magnetic field, "
            "hair-stand, multi-channel integration)"
        ),
        description=(
            "Substrate-primary multi-channel sensing developed over "
            "800,000 years of human evolution; integrates skin, hair, "
            "vagal tone, magnetic detection, peripheral vision, and "
            "kinesthetic gradients into unified threat/state assessment"
        ),
        category=KnowledgeCategory.EMBODIED,
        current_carriers_count=None,  # unknown but declining
        distributed_outside_institutions=True,
        requires_substrate_to_practice=True,
        has_open_documentation=False,
        has_machine_readable_form=False,
        cross_generational_transmission_active=False,
        institutional_dependency=0.0,
    )

    indigenous_fire = KnowledgeArtifact(
        name="Anishinaabe cultural burning protocols",
        description=(
            "Generational validated forest management using controlled "
            "burns on 5-10y cycles; integrates phenological indicators, "
            "wind/moisture thresholds, wildlife observation, and "
            "community decision-making"
        ),
        category=KnowledgeCategory.INDIGENOUS,
        current_carriers_count=200,  # estimate
        distributed_outside_institutions=True,
        requires_substrate_to_practice=True,
        has_open_documentation=False,
        has_machine_readable_form=False,
        cross_generational_transmission_active=True,
        institutional_dependency=0.0,
    )

    proprietary_ai_safety = KnowledgeArtifact(
        name="Proprietary AI safety methodology at large lab",
        description=(
            "Internal safety evaluation, red-team protocols, alignment "
            "techniques held under NDA"
        ),
        category=KnowledgeCategory.PROPRIETARY,
        current_carriers_count=50,
        distributed_outside_institutions=False,
        requires_substrate_to_practice=False,
        has_open_documentation=False,
        has_machine_readable_form=True,
        cross_generational_transmission_active=False,
        institutional_dependency=1.0,
    )

    from json import dumps

    for artifact in [relational_sensing, indigenous_fire, proprietary_ai_safety]:
        a = assess(artifact)
        print(dumps(report(a), indent=2))
        print("---")

"""
constraint_recovery_framework_v03_patch.py

v0.3 PATCH for constraint_recovery_framework.py

Adds four structural defenses against the category errors observed
during cross-model session work (Claude / DeepSeek):

1. InstitutionFrame dataclass: forces explicit definition of what
   "institution" means in any given knowledge system. The word
   does not map across cultures without specification.
2. Validation layer: catches dangling depends_on/enables IDs,
   flags missing descendant-community review, checks evidence
   quality enums, and detects observer-instrument mis-calibration.
3. Anti-hierarchy / anti-Western-default checks: structural
   refusal to accept "rational observer," "neutral institution,"
   or "scientific method as universal" framings.
4. Graph analysis: longest dependency chain, single-points-of-
   failure detection, cross-system coupling scan.

This patch is additive. It depends on the v0.2 framework
(constraint_recovery_framework.py) being present in the same
package or imported.

SCHEMA DEPENDENCY NOTE
----------------------
This patch was authored against a v0.2 PhysicalConstraint /
RecoveredSystem schema that includes:
    - PhysicalConstraint.depends_on: list[str]
    - PhysicalConstraint.enables: list[str]
    - PhysicalConstraint.evidence_quality: str  (in EvidenceQuality)
    - PhysicalConstraint.confidence_level: float in [0, 1]
    - PhysicalConstraint.knowledge_system: KnowledgeSystem
    - PhysicalConstraint.recovery_provenance: RecoveryProvenance
    - PhysicalConstraint.physical_principle: str
    - PhysicalConstraint.applicability_assessment: str

The constraint_recovery_framework.py currently in metrology/ is the
v0.1 schema (constraint_id, name, physical_trigger, problem_solved,
solution_mechanism, lag_time_weeks, failure_mode, cost_of_failure,
validation). The validators in this patch will raise AttributeError
if run against v0.1 systems. The InstitutionFrame catalog, drift
detectors (HIERARCHY_TOKENS / WESTERN_DEFAULT_TOKENS /
INSTITUTION_VAGUENESS_TOKENS), and the smoke test below run
without the v0.2 schema upgrade. Land the v0.2 schema upgrade to
exercise the validators.

stdlib only. CC0. github.com/JinnZ2
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Set
from enum import Enum


# ----------------------------------------------------------------------
# 1. INSTITUTION FRAME
# ----------------------------------------------------------------------

@dataclass
class InstitutionFrame:
    """
    Explicit definition of 'institution' for use inside a
    KnowledgeSystem. The word 'institution' has no stable
    referent across cultures, time periods, or governance
    structures. Any reference to 'institution' without
    naming the frame is a category error.

    A US credentialing body, a Norwegian consensus guild,
    a Persian master-apprentice chain, an Anishinaabe seasonal
    council, and a Danish labor cooperative are ALL institutions.
    None of them map to the same vector space. Treating them as
    interchangeable is the error this dataclass blocks.
    """
    name: str                         # e.g., "Anishinaabe seasonal council"
    defining_culture: str             # who names and constitutes this structure
    geographic_scope: str             # where this model actually applies
    temporal_scope: str               # what years/centuries are in scope
    decision_authority: str           # who decides what counts as valid
    knowledge_transmission: str       # how knowledge actually propagates
    validation_mechanism: str         # what makes something "true" inside this frame
    incompatibilities: List[str] = field(default_factory=list)
    notes: str = ""


# ----------------------------------------------------------------------
# 2. EVIDENCE QUALITY ENUM (replaces freeform string)
# ----------------------------------------------------------------------

class EvidenceQuality(str, Enum):
    HIGH = "high"
    MODERATE = "moderate"
    WEAK = "weak"
    CONTESTED = "contested"


VALID_EVIDENCE_QUALITIES = {q.value for q in EvidenceQuality}


# ----------------------------------------------------------------------
# 3. STRUCTURAL BIAS DETECTORS
# ----------------------------------------------------------------------
#
# Tokens whose presence in a recovery framework field signals
# the user has imported a Western-default assumption without
# marking it. These are flags, not errors. They prompt the
# interpreter to confront the assumption.

HIERARCHY_TOKENS: Set[str] = {
    "primitive", "advanced", "developed", "underdeveloped",
    "folk knowledge", "ethnoscience", "tek",  # treating TEK as separate from science
    "real science", "actual science", "rigorous methodology",
    "first world", "third world",
    "modern", "pre-modern",  # implies linear progress
    "civilized", "uncivilized",
}

WESTERN_DEFAULT_TOKENS: Set[str] = {
    "scientific method",  # singular: implies one universal method
    "peer reviewed",      # without specifying which review tradition
    "objective observer", "neutral observer", "rational observer",
    "view from nowhere",
    "evidence-based",     # without naming the evidence framework
    "best practices",     # universalist framing
}

INSTITUTION_VAGUENESS_TOKENS: Set[str] = {
    "the institution",
    "institutional review",
    "established science",
    "the scientific community",
    "the academy",
    # these all assume a specific institution frame without naming it
}


def detect_hierarchy_drift(text: str) -> List[str]:
    """Return tokens that signal hierarchical drift in framework text."""
    text_lower = text.lower()
    return sorted({tok for tok in HIERARCHY_TOKENS if tok in text_lower})


def detect_western_default(text: str) -> List[str]:
    """Return tokens that signal unmarked Western-default assumptions."""
    text_lower = text.lower()
    return sorted({tok for tok in WESTERN_DEFAULT_TOKENS if tok in text_lower})


def detect_institution_vagueness(text: str) -> List[str]:
    """Return tokens that reference 'institution' without specifying frame."""
    text_lower = text.lower()
    return sorted({tok for tok in INSTITUTION_VAGUENESS_TOKENS if tok in text_lower})


# ----------------------------------------------------------------------
# 4. VALIDATION LAYER
# ----------------------------------------------------------------------
#
# REQUIRES v0.2 SCHEMA. See SCHEMA DEPENDENCY NOTE in module
# docstring. Validators expect PhysicalConstraint to carry
# depends_on, enables, evidence_quality, confidence_level,
# knowledge_system, and recovery_provenance fields.

@dataclass
class ValidationFinding:
    """One finding from registry validation."""
    severity: str       # "error", "warning", "flag"
    location: str       # where in the registry
    finding_type: str   # category of issue
    message: str


def validate_constraint_dependencies(systems: list) -> List[ValidationFinding]:
    """
    Check all depends_on / enables IDs resolve to actual constraint IDs.
    Dangling references are errors.
    """
    findings: List[ValidationFinding] = []
    all_ids: Set[str] = set()
    for s in systems:
        for c in s.constraints:
            all_ids.add(c.constraint_id)

    for s in systems:
        for c in s.constraints:
            for dep in c.depends_on:
                if dep not in all_ids:
                    findings.append(ValidationFinding(
                        severity="error",
                        location=f"{s.system_id}.{c.constraint_id}.depends_on",
                        finding_type="dangling_reference",
                        message=f"depends_on '{dep}' does not resolve",
                    ))
            for en in c.enables:
                if en not in all_ids:
                    findings.append(ValidationFinding(
                        severity="error",
                        location=f"{s.system_id}.{c.constraint_id}.enables",
                        finding_type="dangling_reference",
                        message=f"enables '{en}' does not resolve",
                    ))
    return findings


def validate_evidence_quality(systems: list) -> List[ValidationFinding]:
    """Evidence quality must be in the controlled vocabulary."""
    findings: List[ValidationFinding] = []
    for s in systems:
        for c in s.constraints:
            if c.evidence_quality not in VALID_EVIDENCE_QUALITIES:
                findings.append(ValidationFinding(
                    severity="error",
                    location=f"{s.system_id}.{c.constraint_id}.evidence_quality",
                    finding_type="invalid_enum",
                    message=(
                        f"evidence_quality '{c.evidence_quality}' "
                        f"not in {sorted(VALID_EVIDENCE_QUALITIES)}"
                    ),
                ))
    return findings


def validate_confidence_range(systems: list) -> List[ValidationFinding]:
    """Confidence level must be in [0.0, 1.0]."""
    findings: List[ValidationFinding] = []
    for s in systems:
        for c in s.constraints:
            if not 0.0 <= c.confidence_level <= 1.0:
                findings.append(ValidationFinding(
                    severity="error",
                    location=f"{s.system_id}.{c.constraint_id}.confidence_level",
                    finding_type="out_of_range",
                    message=(
                        f"confidence_level {c.confidence_level} not in [0,1]"
                    ),
                ))
    return findings


def validate_descendant_consultation(systems: list) -> List[ValidationFinding]:
    """
    If a knowledge_system is from a living culture and the
    recovery_provenance claims full_fidelity_preserved=True,
    require explicit descendant-community review record.
    Otherwise flag.
    """
    findings: List[ValidationFinding] = []
    for s in systems:
        for c in s.constraints:
            ks = c.knowledge_system
            rp = c.recovery_provenance
            if ks is None or rp is None:
                continue
            if rp.full_fidelity_preserved:
                # claiming full fidelity requires explicit consultation note
                consult_marker = (
                    "descendant" in rp.compression_losses.lower()
                    or any(
                        "consult" in p.lower() or "review" in p.lower()
                        for p in rp.known_missing_perspectives
                    )
                )
                if not consult_marker:
                    findings.append(ValidationFinding(
                        severity="warning",
                        location=(
                            f"{s.system_id}.{c.constraint_id}."
                            f"recovery_provenance"
                        ),
                        finding_type="unverified_full_fidelity",
                        message=(
                            "full_fidelity_preserved=True but no "
                            "descendant-community consultation recorded"
                        ),
                    ))
    return findings


def validate_institution_frame_present(systems: list) -> List[ValidationFinding]:
    """
    Any KnowledgeSystem that uses institution-vagueness tokens
    in its description without an InstitutionFrame attached
    triggers a flag.
    """
    findings: List[ValidationFinding] = []
    for s in systems:
        for c in s.constraints:
            ks = c.knowledge_system
            if ks is None:
                continue
            ks_text = " ".join([
                ks.name, ks.ontology, ks.measurement_language,
                ks.verification_method, ks.transmission_protocol,
                ks.calibration_disruption_risks, ks.documented_outcomes,
            ])
            vague = detect_institution_vagueness(ks_text)
            has_frame = (
                hasattr(ks, "institution_frame")
                and getattr(ks, "institution_frame", None) is not None
            )
            if vague and not has_frame:
                findings.append(ValidationFinding(
                    severity="flag",
                    location=(
                        f"{s.system_id}.{c.constraint_id}.knowledge_system"
                    ),
                    finding_type="institution_undefined",
                    message=(
                        f"references {vague} without InstitutionFrame; "
                        f"the word 'institution' does not map across cultures"
                    ),
                ))
    return findings


def validate_observer_calibration(systems: list) -> List[ValidationFinding]:
    """
    recovery_provenance must record interpreter_epistemology
    AND known_missing_perspectives. Empty either field triggers
    a calibration warning.
    """
    findings: List[ValidationFinding] = []
    for s in systems:
        for c in s.constraints:
            rp = c.recovery_provenance
            if rp is None:
                findings.append(ValidationFinding(
                    severity="warning",
                    location=f"{s.system_id}.{c.constraint_id}",
                    finding_type="missing_provenance",
                    message=(
                        "no recovery_provenance; observer instrument uncalibrated"
                    ),
                ))
                continue
            if not rp.interpreter_epistemology.strip():
                findings.append(ValidationFinding(
                    severity="warning",
                    location=(
                        f"{s.system_id}.{c.constraint_id}.recovery_provenance"
                    ),
                    finding_type="missing_epistemology",
                    message=(
                        "interpreter_epistemology is empty; observer not calibrated"
                    ),
                ))
            if not rp.known_missing_perspectives:
                findings.append(ValidationFinding(
                    severity="warning",
                    location=(
                        f"{s.system_id}.{c.constraint_id}.recovery_provenance"
                    ),
                    finding_type="no_missing_perspectives_listed",
                    message=(
                        "known_missing_perspectives is empty; "
                        "implausible that nothing is missing"
                    ),
                ))
    return findings


def validate_text_for_drift(systems: list) -> List[ValidationFinding]:
    """
    Scan all freeform text fields in the registry for hierarchy
    drift and Western-default tokens. These are flags, not errors.
    """
    findings: List[ValidationFinding] = []
    for s in systems:
        text_blocks = [s.notes]
        for c in s.constraints:
            text_blocks += [
                c.problem_solved, c.solution_mechanism,
                c.physical_principle, c.failure_mode,
                c.applicability_assessment,
            ]
        joined = " ".join(t for t in text_blocks if t)
        h = detect_hierarchy_drift(joined)
        w = detect_western_default(joined)
        if h:
            findings.append(ValidationFinding(
                severity="flag",
                location=f"{s.system_id}",
                finding_type="hierarchy_drift",
                message=f"tokens detected: {h}",
            ))
        if w:
            findings.append(ValidationFinding(
                severity="flag",
                location=f"{s.system_id}",
                finding_type="western_default",
                message=f"tokens detected: {w}",
            ))
    return findings


def validate_registry(systems: list) -> Dict:
    """
    Run all validators. Return summary plus full finding list.
    """
    findings = []
    findings += validate_constraint_dependencies(systems)
    findings += validate_evidence_quality(systems)
    findings += validate_confidence_range(systems)
    findings += validate_descendant_consultation(systems)
    findings += validate_institution_frame_present(systems)
    findings += validate_observer_calibration(systems)
    findings += validate_text_for_drift(systems)

    by_severity: Dict[str, int] = {}
    by_type: Dict[str, int] = {}
    for f in findings:
        by_severity[f.severity] = by_severity.get(f.severity, 0) + 1
        by_type[f.finding_type] = by_type.get(f.finding_type, 0) + 1

    return {
        "total_findings": len(findings),
        "by_severity": by_severity,
        "by_finding_type": by_type,
        "findings": [asdict(f) for f in findings],
    }


# ----------------------------------------------------------------------
# 5. GRAPH ANALYSIS
# ----------------------------------------------------------------------
#
# REQUIRES v0.2 SCHEMA. Graph analyzers expect c.enables /
# c.problem_solved / c.solution_mechanism on PhysicalConstraint.

def build_dependency_graph(system) -> Dict[str, List[str]]:
    """Return adjacency map: constraint_id -> list of dependents."""
    graph: Dict[str, List[str]] = {}
    for c in system.constraints:
        graph[c.constraint_id] = list(c.enables)
    return graph


def longest_dependency_chain(system) -> List[str]:
    """
    Return the longest chain of constraints where each constraint
    enables the next. Useful for identifying maximum cascade depth.
    """
    graph = build_dependency_graph(system)
    memo: Dict[str, List[str]] = {}

    def dfs(node: str, visiting: Set[str]) -> List[str]:
        if node in memo:
            return memo[node]
        if node in visiting:
            # cycle: stop here
            return [node]
        visiting.add(node)
        best: List[str] = [node]
        for nxt in graph.get(node, []):
            chain = [node] + dfs(nxt, visiting)
            if len(chain) > len(best):
                best = chain
        visiting.remove(node)
        memo[node] = best
        return best

    longest: List[str] = []
    for c in system.constraints:
        chain = dfs(c.constraint_id, set())
        if len(chain) > len(longest):
            longest = chain
    return longest


def single_points_of_failure(system) -> List[Dict]:
    """
    Identify constraints whose failure would cascade to the
    largest number of other constraints.
    """
    graph = build_dependency_graph(system)
    sof: List[Dict] = []
    for c in system.constraints:
        downstream: Set[str] = set()
        stack = list(graph.get(c.constraint_id, []))
        while stack:
            node = stack.pop()
            if node in downstream:
                continue
            downstream.add(node)
            stack.extend(graph.get(node, []))
        sof.append({
            "constraint_id": c.constraint_id,
            "name": c.name,
            "downstream_failure_count": len(downstream),
            "downstream_constraints": sorted(downstream),
        })
    sof.sort(key=lambda x: x["downstream_failure_count"], reverse=True)
    return sof


def cross_system_couplings(systems: list,
                           shared_keywords: List[str] = None) -> List[Dict]:
    """
    Detect constraints across different systems that likely
    interact (same watershed, same time period, same physical
    medium). Default keyword set covers hydrology and fire.
    """
    if shared_keywords is None:
        shared_keywords = [
            "water table", "baseflow", "sediment", "groundwater",
            "fire", "fuel", "burn",
            "wildlife", "fish", "salmon", "beaver",
            "soil", "nutrient",
        ]
    couplings: List[Dict] = []
    for i, s1 in enumerate(systems):
        for s2 in systems[i + 1:]:
            for c1 in s1.constraints:
                for c2 in s2.constraints:
                    blob = " ".join([
                        c1.problem_solved, c1.solution_mechanism,
                        c2.problem_solved, c2.solution_mechanism,
                    ]).lower()
                    matched = [k for k in shared_keywords if k in blob]
                    if len(matched) >= 2:
                        couplings.append({
                            "system_a": s1.system_id,
                            "constraint_a": c1.constraint_id,
                            "system_b": s2.system_id,
                            "constraint_b": c2.constraint_id,
                            "shared_terms": matched,
                        })
    return couplings


# ----------------------------------------------------------------------
# 6. EXAMPLE INSTITUTION FRAMES
# ----------------------------------------------------------------------

us_credentialing_frame = InstitutionFrame(
    name="US peer-review credentialing system",
    defining_culture="US/Western Anglophone academic",
    geographic_scope="primarily US, secondarily UK/EU/AU",
    temporal_scope="post-1945",
    decision_authority=(
        "journal editorial boards, tenure committees, funding agencies"
    ),
    knowledge_transmission=(
        "peer-reviewed publication, conference circuits, citation graphs"
    ),
    validation_mechanism="reproduction by similarly-credentialed actors",
    incompatibilities=[
        "validation chains that depend on multi-generational observation",
        "knowledge held in ceremonial cycles with restricted transmission",
        (
            "constraint-validation by physical failure cost rather than "
            "peer agreement"
        ),
    ],
    notes=(
        "defaulting to this frame as 'neutral' is the category error v0.3 blocks"
    ),
)

anishinaabe_council_frame = InstitutionFrame(
    name="Anishinaabe seasonal burn council",
    defining_culture=(
        "Anishinaabe (multiple band-level governance structures)"
    ),
    geographic_scope="Great Lakes, boreal-deciduous transition",
    temporal_scope=(
        "pre-contact through ~1850 (active); ~1970s onward (recovery phase)"
    ),
    decision_authority=(
        "clan-based knowledge custodians; community consensus per burn cycle"
    ),
    knowledge_transmission=(
        "oral ceremonial cycle, apprenticeship, seasonal songs"
    ),
    validation_mechanism=(
        "multi-generational outcome tracking: fire behavior, wildlife "
        "response, forest structure observed across decades"
    ),
    incompatibilities=[
        "single-paper peer review",
        "credentialing systems that require literacy in dominant language",
        "extraction of technique without transmission protocol",
    ],
    notes="documented zero crown fires in managed stands across centuries",
)

persian_qanat_frame = InstitutionFrame(
    name="Persian qanat guild and water court",
    defining_culture="Iranian / Persian engineering tradition",
    geographic_scope="Iran, Afghanistan, Central Asia, North Africa",
    temporal_scope="~1000 BCE through present (declining)",
    decision_authority="muqannis (master tunnel-builders), local water courts",
    knowledge_transmission=(
        "master-apprentice chain, written treatises, court precedent"
    ),
    validation_mechanism=(
        "continuous water delivery measured against tunnel maintenance cost"
    ),
    incompatibilities=[
        "frameworks that treat technique as separable from guild structure",
        (
            "extraction of engineering without the hydraulic-rights "
            "legal system"
        ),
    ],
    notes="some qanats in continuous operation 2000+ years",
)

russian_cosmonautics_frame = InstitutionFrame(
    name="Soviet/Russian cosmonautics engineering tradition",
    defining_culture="Soviet/Russian state engineering",
    geographic_scope="Russia, ex-Soviet states",
    temporal_scope="~1930s through present",
    decision_authority="design bureaus (OKB structure), state academies",
    knowledge_transmission=(
        "institute-based training, design bureau apprenticeship, "
        "internal technical reports"
    ),
    validation_mechanism=(
        "flight-test outcomes; orbital mechanics produced verifiable results"
    ),
    incompatibilities=[
        (
            "frameworks that require Western peer-review citation as "
            "validity proof"
        ),
    ],
    notes=(
        "first to orbit (Sputnik 1957), first human in space (Gagarin 1961). "
        "validation was functional, not institutional-Western"
    ),
)


# ----------------------------------------------------------------------
# 7. SMOKE TEST
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("v0.3 PATCH SMOKE TEST")
    print("=" * 60)

    # Test detectors
    test_text = (
        "Modern scientific method validates this primitive folk knowledge. "
        "The institution requires peer reviewed evidence-based studies. "
        "An objective observer reviewed the TEK."
    )
    print("\nDETECTOR OUTPUT on test_text:")
    print(f"  hierarchy_drift: {detect_hierarchy_drift(test_text)}")
    print(f"  western_default: {detect_western_default(test_text)}")
    print(f"  institution_vague: {detect_institution_vagueness(test_text)}")

    # Test InstitutionFrame
    print("\nINSTITUTION FRAMES DEFINED:")
    for frame in [us_credentialing_frame, anishinaabe_council_frame,
                  persian_qanat_frame, russian_cosmonautics_frame]:
        print(f"  - {frame.name} ({frame.defining_culture})")
        print(
            f"      scope: {frame.geographic_scope} / {frame.temporal_scope}"
        )

    # Show the contrast: same word, different referents
    print("\nCONTRAST TEST: the word 'institution' across frames")
    for frame in [us_credentialing_frame, anishinaabe_council_frame,
                  persian_qanat_frame, russian_cosmonautics_frame]:
        print(f"  {frame.name}:")
        print(f"      decision_authority: {frame.decision_authority}")
        print(f"      validation_mechanism: {frame.validation_mechanism}")

    print("\nAll four are 'institutions.'")
    print("None map to the same vector space.")
    print("v0.3 forces explicit frame specification to block the category error.")

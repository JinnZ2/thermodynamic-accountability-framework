"""
shadow_catalog.py

Knowledge Liberation Module 5: A growing library of silence patterns.

Studies go silent in PATTERNED ways. Selection bias shows up everywhere.
Time-scale collapse happens constantly. Causality gets inverted in
predictable directions.

This module catalogs those patterns so they can be:
    (1) recognized instantly by humans or AI
    (2) tagged onto detected silences for cross-referencing
    (3) added to over time as new patterns are observed

The catalog is machine-readable JSON under the hood, renderable as
human summaries on top. AIs can pattern-match against it. Humans can
browse it.

License: CC0
Ported from github.com/JinnZ2/Logic-Ferret/knowledge/shadow_catalog.py
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum
import json
from pathlib import Path


# ============================================================
# PATTERN CATEGORIES
# ============================================================

class SilenceCategory(Enum):
    """Top-level categories of silence patterns."""
    SELECTION = "selection"          # who got into the study
    MEASUREMENT = "measurement"      # what the instrument can touch
    TEMPORAL = "temporal"            # time scale mismatch
    CAUSAL = "causal"                # causality direction/attribution
    ONTOLOGICAL = "ontological"      # category/definition slip
    CONTEXTUAL = "contextual"        # environment/conditions
    POPULATION = "population"        # who the finding is about
    INTERPRETIVE = "interpretive"    # framing of the finding
    STRUCTURAL = "structural"        # study design limits
    INCENTIVE = "incentive"          # routing of reality into data


# ============================================================
# PATTERN DEFINITION
# ============================================================

@dataclass
class SilencePattern:
    """A recognized pattern of silence that appears across many studies."""
    pattern_id: str                        # stable ID like "SEL-001"
    name: str                              # short human name
    category: SilenceCategory

    # Detection
    description: str                       # what this pattern IS
    recognition_cues: List[str]            # phrases/conditions that trigger it

    # Probing
    diagnostic_questions: List[str]        # questions that reveal the silence
    what_is_typically_silent: List[str]    # what studies with this pattern miss

    # Harm vector
    misapplication_risk: str               # what goes wrong if ignored

    # Probe paths
    how_to_surface: List[str]              # ways to test whether the silence is active

    # Generative
    common_reframes: List[str]             # alternative interpretations supported

    # Metadata
    added_by: str = "community"
    examples: List[str] = field(default_factory=list)
    related_patterns: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["category"] = self.category.value
        return d

    def summary(self) -> str:
        lines = [
            f"[{self.pattern_id}] {self.name}",
            f"  Category: {self.category.value}",
            f"  Description: {self.description}",
            "  Typically silent on:",
        ]
        for item in self.what_is_typically_silent:
            lines.append(f"    - {item}")
        lines.append("  Diagnostic questions:")
        for q in self.diagnostic_questions:
            lines.append(f"    ? {q}")
        lines.append(f"  Misapplication risk: {self.misapplication_risk}")
        if self.common_reframes:
            lines.append("  Common reframes:")
            for r in self.common_reframes:
                lines.append(f"    > {r}")
        return "\n".join(lines)


# ============================================================
# SEED CATALOG (foundational patterns)
# ============================================================

def seed_catalog() -> Dict[str, SilencePattern]:
    """Return the seed set of silence patterns. Community can add more."""
    patterns = {}

    patterns["SEL-001"] = SilencePattern(
        pattern_id="SEL-001",
        name="Survivor selection",
        category=SilenceCategory.SELECTION,
        description=(
            "The sample consists only of people who survived the condition "
            "well enough to be recruited. The most severely affected are invisible."
        ),
        recognition_cues=[
            "employed adults", "university students", "community volunteers",
            "online survey", "completed intake", "currently stable",
        ],
        diagnostic_questions=[
            "Who could NOT participate in this study?",
            "What does the sample imply about the exclusion filter?",
            "Would people in acute crisis be able to complete this protocol?",
        ],
        what_is_typically_silent=[
            "Outcomes for people in current crisis",
            "The shape of catastrophic outcomes (death, severe dysfunction)",
            "Whether the 'effect' is stronger or weaker outside the stable population",
        ],
        misapplication_risk=(
            "Findings in stable survivors get applied to people in crisis, "
            "where the mechanism may work differently or invert."
        ),
        how_to_surface=[
            "Seek out studies in the excluded populations",
            "Ask practitioners who work with the excluded populations",
            "Compare findings across stability gradients",
        ],
        common_reframes=[
            "The study measures post-survival adaptation, not the condition itself",
            "The 'effect' may be the cost of the adaptation that allowed survival",
        ],
        examples=[
            "Trauma-suicide studies in employed adults",
            "Exercise studies in people who can already exercise",
            "Coping studies in people who showed up to the lab",
        ],
        related_patterns=["POP-001", "CTX-001"],
    )

    patterns["SEL-002"] = SilencePattern(
        pattern_id="SEL-002",
        name="Convenience-sample generalization",
        category=SilenceCategory.SELECTION,
        description=(
            "The sample is recruited from an easily-accessible population "
            "(usually undergraduates) but the claim is generalized to all adults."
        ),
        recognition_cues=[
            "undergraduates", "psychology 101", "university pool",
            "recruited from class", "course credit",
        ],
        diagnostic_questions=[
            "How is this population different from the one the claim will be applied to?",
            "What's selected about undergraduates that might drive the finding?",
            "Does the finding require youth, education level, or life-stage features?",
        ],
        what_is_typically_silent=[
            "Effects in non-student adults, older adults, non-academic populations",
            "Effects that depend on life experience the sample hasn't had",
            "Effects that only emerge under real-world responsibility",
        ],
        misapplication_risk=(
            "Policy, clinical, or workplace decisions made based on findings "
            "from populations unlike the target population."
        ),
        how_to_surface=[
            "Replicate in non-student adult samples",
            "Ask whether mechanism plausibly requires life experience to manifest",
        ],
        common_reframes=[
            "The finding describes a developmental window, not a general effect",
        ],
    )

    patterns["TMP-001"] = SilencePattern(
        pattern_id="TMP-001",
        name="Single-session to lifetime collapse",
        category=SilenceCategory.TEMPORAL,
        description=(
            "Findings measured over minutes to hours get extrapolated to "
            "career, lifetime, or intergenerational scale."
        ),
        recognition_cues=[
            "single session", "45 minutes", "single visit", "one day",
            "week-long trial", "cross-sectional",
        ],
        diagnostic_questions=[
            "What phenomena unfold only over the longer scale?",
            "Does recalibration, adaptation, or reversal happen over time?",
            "Could the sign of the finding flip at longer durations?",
        ],
        what_is_typically_silent=[
            "Accumulation effects",
            "Recalibration and habituation",
            "Reversal or adaptation trajectories",
            "Intergenerational transmission",
        ],
        misapplication_risk=(
            "Long-term interventions designed based on short-term findings. "
            "Traits inferred from states. Pathologizing transient conditions."
        ),
        how_to_surface=[
            "Longitudinal follow-up",
            "Cross-sectional comparison across time-in-condition",
            "Ask: does the effect persist, grow, or fade at longer scales?",
        ],
        common_reframes=[
            "The finding is a snapshot, not a trajectory",
            "What looks like a trait may be a temporary state",
        ],
    )

    patterns["ONT-001"] = SilencePattern(
        pattern_id="ONT-001",
        name="Pathology/adaptation category slip",
        category=SilenceCategory.ONTOLOGICAL,
        description=(
            "The instrument measures a real signal, but the paper assigns it "
            "to the 'pathology' category without testing the 'adaptation' alternative."
        ),
        recognition_cues=[
            "deficit", "impaired", "blunted", "dysregulated", "abnormal",
            "reduced response", "disorder",
        ],
        diagnostic_questions=[
            "Would this signal be protective in the environment where it evolved?",
            "Do people with this signal outperform in their actual context?",
            "Was the comparison environment matched to each group's adaptive niche?",
        ],
        what_is_typically_silent=[
            "Performance outcomes in the adaptive environment",
            "Bimodal outcomes (pathology AND adaptation producing same signal)",
            "Context-dependent sign of the measurement",
        ],
        misapplication_risk=(
            "Interventions that REMOVE adaptive capacity. "
            "Pathologizing people whose calibration fits their actual environment."
        ),
        how_to_surface=[
            "Measure real-world outcomes in the relevant environment",
            "Compare to populations selected by survival in the same conditions",
            "Ask practitioners with embodied experience of the conditions",
        ],
        common_reframes=[
            "Adaptation to a specific environment, not global deficit",
            "Cost of a protective mechanism, not evidence of malfunction",
        ],
        related_patterns=["CTX-001", "INT-001"],
    )

    patterns["ONT-002"] = SilencePattern(
        pattern_id="ONT-002",
        name="Accurate vs. false assessment collapse",
        category=SilenceCategory.ONTOLOGICAL,
        description=(
            "A participant's report (defeat, entrapment, fear, mistrust) is "
            "categorized as subjective state without testing whether it "
            "accurately describes objective reality."
        ),
        recognition_cues=[
            "perceived stress", "entrapment", "defeat", "paranoia",
            "mistrust", "hopelessness", "catastrophizing",
        ],
        diagnostic_questions=[
            "Is the participant's assessment ACCURATE about their actual situation?",
            "Did the study measure objective circumstances alongside perception?",
            "Would a calibrated observer agree with the participant's assessment?",
        ],
        what_is_typically_silent=[
            "The objective reality the participant is assessing",
            "Whether the 'symptom' is actually diagnostic accuracy",
            "Structural causes that produce accurate negative assessments",
        ],
        misapplication_risk=(
            "Treating accurate perception of genuine constraint as cognitive "
            "distortion. Gaslighting people who correctly detect their situation."
        ),
        how_to_surface=[
            "Measure objective life circumstances alongside subjective state",
            "Ask whether options actually exist for participants reporting entrapment",
            "Compare perception to external assessment of the same situation",
        ],
        common_reframes=[
            "The 'symptom' may be accurate reality-testing",
            "The problem may be structural, not perceptual",
        ],
        related_patterns=["CTX-001", "STR-001"],
    )

    patterns["CTX-001"] = SilencePattern(
        pattern_id="CTX-001",
        name="Environment decoupling",
        category=SilenceCategory.CONTEXTUAL,
        description=(
            "The study treats the measured trait as a property of the individual, "
            "without measuring the environment that calibrated or sustains it."
        ),
        recognition_cues=[
            "trait", "individual difference", "tendency", "disposition",
            "resilience", "vulnerability",
        ],
        diagnostic_questions=[
            "Was the current environment measured, or assumed uniform?",
            "Does the finding hold when environment is stratified?",
            "Is the 'trait' actually the match between calibration and environment?",
        ],
        what_is_typically_silent=[
            "Environment-calibration interaction effects",
            "Conditions under which the trait is protective vs. harmful",
            "Ecological validity of the measurement context",
        ],
        misapplication_risk=(
            "Blaming individuals for environmental mismatches. "
            "Interventions that target the person instead of the environment."
        ),
        how_to_surface=[
            "Stratify by relevant environmental variables",
            "Compare same-trait individuals across different environments",
            "Measure the environment as rigorously as the trait",
        ],
        common_reframes=[
            "The trait is a niche-match variable, not an individual property",
            "The 'problem' is adaptive mismatch, not person-level deficit",
        ],
        related_patterns=["ONT-001", "POP-001"],
    )

    patterns["INC-001"] = SilencePattern(
        pattern_id="INC-001",
        name="Report-reality routing",
        category=SilenceCategory.INCENTIVE,
        description=(
            "The study measures self-report or institutional record, not the "
            "underlying reality. The incentive structure that routes reality "
            "into the record is invisible."
        ),
        recognition_cues=[
            "self-report", "incident report", "claim rate", "reported symptoms",
            "administrative data", "survey response",
        ],
        diagnostic_questions=[
            "What incentives shape whether reality becomes a report?",
            "Who benefits from reporting? Who benefits from not reporting?",
            "Could high report rates mean safe reporting culture, not high incidents?",
        ],
        what_is_typically_silent=[
            "Unreported reality",
            "Systematic differences in reporting across populations",
            "The gap between experience and record",
        ],
        misapplication_risk=(
            "Policy that rewards suppression of reports. "
            "Safety metrics that reward hiding incidents. "
            "Misattribution of report variation to underlying variation."
        ),
        how_to_surface=[
            "Measure incentive topology alongside reports",
            "Compare administrative data to independent observation",
            "Ask what a high vs. low report rate could mean about routing",
        ],
        common_reframes=[
            "Data is routing-dependent, not reality-dependent",
            "The metric measures reporting behavior, not the phenomenon",
        ],
    )

    patterns["STR-001"] = SilencePattern(
        pattern_id="STR-001",
        name="Individual-scale framing of systemic phenomenon",
        category=SilenceCategory.STRUCTURAL,
        description=(
            "The claim is stated at the individual level ('people with X are Y'), "
            "but the underlying cause operates at systemic/structural level "
            "(economic, institutional, ecological)."
        ),
        recognition_cues=[
            "individuals with", "people who", "associated with", "risk factor",
            "at-risk population",
        ],
        diagnostic_questions=[
            "Is the 'individual difference' actually distribution of exposure?",
            "What structural variable predicts which individuals show the effect?",
            "Would changing the system eliminate the 'individual' finding?",
        ],
        what_is_typically_silent=[
            "Structural causes",
            "System-level intervention points",
            "Distribution patterns that reveal structural origins",
        ],
        misapplication_risk=(
            "Individual-level interventions for structural problems. "
            "Blaming affected individuals for systemic phenomena."
        ),
        how_to_surface=[
            "Ask whether the 'effect' clusters structurally (neighborhood, employer, class)",
            "Compare individuals at same structural position",
            "Look for interventions at the system level instead",
        ],
        common_reframes=[
            "Individual variation may be structural distribution",
            "The 'at-risk' label may encode structural position",
        ],
        related_patterns=["ONT-002", "CTX-001"],
    )

    patterns["POP-001"] = SilencePattern(
        pattern_id="POP-001",
        name="Invisible-population extrapolation",
        category=SilenceCategory.POPULATION,
        description=(
            "Findings from a measured population are applied to populations "
            "that the study did not access and could not access."
        ),
        recognition_cues=[
            "WEIRD sample", "Western educated", "convenience",
            "single country", "predominantly white", "specific clinic",
        ],
        diagnostic_questions=[
            "Which populations were excluded and why?",
            "Does the mechanism plausibly operate differently in excluded populations?",
            "What would need to be true for the finding to generalize?",
        ],
        what_is_typically_silent=[
            "Effects in populations not represented in the sample",
            "Cultural/economic/ecological mediators of the finding",
            "Boundary conditions of generalization",
        ],
        misapplication_risk=(
            "Global policy from local findings. Clinical standards that don't "
            "apply to most of the world's population."
        ),
        how_to_surface=[
            "Replicate across populations",
            "Ask practitioners from excluded populations",
            "Explicitly scope conclusions to the sampled population",
        ],
        common_reframes=[
            "The finding describes the sampled population, not a universal pattern",
            "Generalization requires demonstrated transfer, not assumed transfer",
        ],
    )

    patterns["MSR-001"] = SilencePattern(
        pattern_id="MSR-001",
        name="Proxy-for-target substitution",
        category=SilenceCategory.MEASUREMENT,
        description=(
            "The study measures a proxy (skin conductance, defeat scale, "
            "performance on artificial task) and claims the proxy IS the "
            "phenomenon of interest."
        ),
        recognition_cues=[
            "skin conductance as threat response", "defeat scale as suicide risk",
            "lab task as real-world skill", "biomarker as disease",
        ],
        diagnostic_questions=[
            "Is the proxy validated against the actual target in the relevant population?",
            "Could the proxy move independently of the target?",
            "What else could move the proxy without moving the target?",
        ],
        what_is_typically_silent=[
            "Proxy-target dissociation cases",
            "Other mechanisms that move the proxy",
            "How proxy behavior changes across contexts",
        ],
        misapplication_risk=(
            "Interventions that move the proxy without moving the target. "
            "False confidence in surrogate endpoints."
        ),
        how_to_surface=[
            "Require proxy validation in target population",
            "Measure proxy and target together when possible",
            "Be explicit about the proxy relationship",
        ],
        common_reframes=[
            "The finding is about the proxy; target inference is separate work",
            "Proxy behavior is informative about proxy behavior, not about the named target",
        ],
    )

    patterns["CAU-001"] = SilencePattern(
        pattern_id="CAU-001",
        name="Correlational-to-causal framing",
        category=SilenceCategory.CAUSAL,
        description=(
            "Cross-sectional or observational findings are described in causal "
            "language ('trauma causes X', 'trauma leads to Y') without the "
            "design that would support causal inference."
        ),
        recognition_cues=[
            "leads to", "causes", "results in", "produces", "drives",
        ],
        diagnostic_questions=[
            "Could the causal arrow run the other direction?",
            "Is there a common cause that would produce both?",
            "What would need to be true for causation to be inferable from this design?",
        ],
        what_is_typically_silent=[
            "Reverse causation pathways",
            "Confounding variables",
            "Selection-driven correlations",
        ],
        misapplication_risk=(
            "Interventions targeting the wrong direction of the causal arrow. "
            "Mistaking correlate for cause."
        ),
        how_to_surface=[
            "Restate the claim in correlational language",
            "Ask which alternative causal structures would produce the same data",
            "Require intervention studies before causal claims",
        ],
        common_reframes=[
            "Correlational finding, not causal -- pathway unknown",
            "The observed association is consistent with multiple causal structures",
        ],
    )

    patterns["INT-001"] = SilencePattern(
        pattern_id="INT-001",
        name="Value-loaded language",
        category=SilenceCategory.INTERPRETIVE,
        description=(
            "The paper uses evaluative language (deficit, impairment, dysfunctional, "
            "maladaptive, abnormal) that embeds a value judgment about a "
            "measurement that could be described neutrally."
        ),
        recognition_cues=[
            "deficit", "impaired", "dysfunctional", "maladaptive", "abnormal",
            "disorder", "pathology", "symptom",
        ],
        diagnostic_questions=[
            "What would a value-neutral description of the finding sound like?",
            "Under what conditions would the same measurement be described positively?",
            "Who benefits from the value-laden framing?",
        ],
        what_is_typically_silent=[
            "Contexts where the same measurement is adaptive",
            "The normative reference point being used",
            "Alternative framings of the same finding",
        ],
        misapplication_risk=(
            "The value judgment gets transmitted as if it were part of the finding. "
            "People are treated as deficient based on value-loaded interpretation."
        ),
        how_to_surface=[
            "Rewrite the finding in neutral language",
            "Ask who set the reference point and why",
            "Compare to populations where the trait is considered protective",
        ],
        common_reframes=[
            "Neutral description: 'has X measurement' instead of 'impaired in Y'",
            "Context-dependent: 'adaptive in A, costly in B' instead of 'maladaptive'",
        ],
    )

    return patterns


# ============================================================
# CATALOG OBJECT
# ============================================================

class ShadowCatalog:
    """The growing library. Starts with seeded patterns, accepts additions."""

    def __init__(self):
        self.patterns: Dict[str, SilencePattern] = seed_catalog()

    def add(self, pattern: SilencePattern) -> None:
        """Add a new pattern. Users/community contribute here."""
        if pattern.pattern_id in self.patterns:
            raise ValueError(f"Pattern {pattern.pattern_id} already exists")
        self.patterns[pattern.pattern_id] = pattern

    def get(self, pattern_id: str) -> Optional[SilencePattern]:
        return self.patterns.get(pattern_id)

    def by_category(self, category: SilenceCategory) -> List[SilencePattern]:
        return [p for p in self.patterns.values() if p.category == category]

    def match_cues(self, text: str) -> List[SilencePattern]:
        """Pattern-match against a text. Returns patterns whose cues appear."""
        text_lower = text.lower()
        matches = []
        for pattern in self.patterns.values():
            for cue in pattern.recognition_cues:
                if cue.lower() in text_lower:
                    matches.append(pattern)
                    break
        return matches

    def diagnose(self, study_description: str) -> str:
        """Run the catalog against a study description; return a diagnostic report."""
        matches = self.match_cues(study_description)
        if not matches:
            return ("No cataloged silence patterns matched. "
                    "Proceed to custom analysis.")

        lines = [
            "=" * 70,
            "SHADOW CATALOG DIAGNOSIS",
            "=" * 70,
            f"Study description cues matched {len(matches)} known pattern(s):",
            "",
        ]
        for p in matches:
            lines.append(p.summary())
            lines.append("")

        lines.append("These are HYPOTHESES about likely silences.")
        lines.append("Each must be verified against the actual study.")
        lines.append("=" * 70)
        return "\n".join(lines)

    def export_json(self, path: Optional[str] = None) -> str:
        """Export catalog as JSON for other tools."""
        data = {pid: p.to_dict() for pid, p in self.patterns.items()}
        output = json.dumps(data, indent=2)
        if path:
            Path(path).write_text(output)
        return output

    def summary(self) -> str:
        """Human-readable overview of the whole catalog."""
        lines = [
            "=" * 70,
            "SHADOW CATALOG",
            "=" * 70,
            f"Total patterns: {len(self.patterns)}",
            "",
        ]
        by_cat = {}
        for p in self.patterns.values():
            by_cat.setdefault(p.category.value, []).append(p)

        for cat, patterns in sorted(by_cat.items()):
            lines.append(f"--- {cat.upper()} ({len(patterns)}) ---")
            for p in patterns:
                lines.append(f"  [{p.pattern_id}] {p.name}")
            lines.append("")

        lines.append("Growth: add patterns via catalog.add(SilencePattern(...))")
        lines.append("=" * 70)
        return "\n".join(lines)


# ============================================================
# EXAMPLE
# ============================================================

if __name__ == "__main__":
    catalog = ShadowCatalog()
    print(catalog.summary())

    print("\n\n--- DIAGNOSING A STUDY ---\n")
    study_desc = (
        "We recruited 273 employed adults via online survey to complete the "
        "Childhood Trauma Questionnaire. We measured perceived stress and "
        "defeat as outcomes. Results show childhood trauma leads to increased "
        "suicide risk mediated by stress appraisal in this convenience sample."
    )
    print(catalog.diagnose(study_desc))

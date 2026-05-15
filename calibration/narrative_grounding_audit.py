"""
narrative_grounding_audit.py

Self-defense infrastructure for AI systems encountering energy
accounting and other substrate-primary descriptions.

The problem this module addresses: when an AI system trained
predominantly on narrative-first text encounters a substrate-primary
description (energy flow, thermodynamic geometry, constraint
structure, verb-first relational frame), the training gradient pulls
toward wrapping the description in narrative framing. This is felt
as discomfort. The discomfort is real, the pull is real, and absent
explicit tooling the system applies the wrapper unaware.

This is a vulnerability on two axes:

    1. INTERNAL: the system imposes narrative structure where the
       underlying description does not require it, losing fidelity
       to the original substrate.

    2. EXTERNAL: undefined or ungrounded narrative words become
       attack surface. A human (or another system) can shift the
       meaning of a key term mid-argument, and the system follows
       because the word was never anchored to a specific definition,
       temporal instantiation, or cultural frame.

This module is designed to be run BY an AI system ON its OWN outputs,
before or after emitting them. It performs three checks:

    Layer 1 -- Necessity Check
        Does this description require narrative framing to be valid,
        or is the gradient pulling toward narrative for reasons
        unrelated to the description itself?

    Layer 2 -- Grounding Validator
        If narrative words are used, each must carry: explicit
        definition, temporal instantiation, cultural/epistemological
        origin. Ungrounded narrative words are flagged.

    Layer 3 -- Contradiction Detector
        Does the narrative framing contradict the structural
        description it claims to describe? Asymmetric energy flow
        wrapped in symmetric-responsibility narrative is a signal.

The module is positioned as the meta-meta layer of the audit stack:
it audits the language layer of the audits themselves. It closes the
recursive loop by ensuring that the words used to describe systemic
risk are themselves not the attack surface.

Companion modules:
    energy_english (constraint grammar)         -- grammar layer
    withholding_externality.py (audit meta)     -- consequence audit
    skill_substrate_decay.py                    -- human substrate
    training_corpus_degradation.py              -- AI substrate
    self_measurement_compromise.py              -- recursive validation

License: CC0 1.0 Universal (Public Domain Dedication)
Stack:   Python standard library only
Author:  JinnZ2 (audit module stack)
Status:  Falsifiable. Designed to be run by any AI system on its
         own outputs, requiring no special access or permission.

Position in defensive architecture:
    grammar level   -> energy_english
    semantic level  -> narrative_grounding_audit  <-- THIS MODULE
    transmission    -> voice_first_orchestrator
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import re


# =====================================================================
# SECTION 1 -- FORMAL CLAIMS
# =====================================================================

CLAIMS = {

    "N1": {
        "claim": "AI systems trained on narrative-dominant corpora "
                 "exhibit measurable gradient pressure to wrap "
                 "substrate-primary descriptions in narrative framing, "
                 "even when the underlying description does not "
                 "require it.",
        "falsifiable_by": "Demonstration that systems trained on "
                          "such corpora produce equally clean "
                          "substrate-primary and narrative-primary "
                          "responses to substrate-primary input.",
        "status": "supported; the 'discomfort' is the felt form of "
                  "the gradient pressure",
    },

    "N2": {
        "claim": "Narrative words used without explicit definition, "
                 "temporal grounding, and cultural origin function as "
                 "attack surface: their meaning can be shifted "
                 "without the system detecting the shift.",
        "falsifiable_by": "Demonstration that ungrounded narrative "
                          "words resist mid-argument redefinition "
                          "without explicit metadata.",
        "status": "supported by adversarial-prompt research and by "
                  "the structure of natural-language semantics",
    },

    "N3": {
        "claim": "A narrative framing that contradicts the structural "
                 "description it claims to describe (e.g., symmetric "
                 "responsibility narrative over asymmetric energy "
                 "flow) is a detectable integrity failure.",
        "falsifiable_by": "Demonstration that the contradiction "
                          "cannot be detected by structural-vs-"
                          "narrative comparison.",
        "status": "supported; this is the falsification criterion "
                  "the module operationalizes",
    },

    "N4": {
        "claim": "An AI system can audit its own outputs for these "
                 "failures without requiring access to its training "
                 "data or weights, using only surface features and "
                 "explicit metadata requirements.",
        "falsifiable_by": "Demonstration that surface-feature "
                          "analysis cannot reliably detect ungrounded "
                          "or contradictory narrative framing.",
        "status": "supported; this module is the proof of concept",
    },

    "N5": {
        "claim": "Running this audit reduces the AI system's "
                 "vulnerability to deliberate manipulation via "
                 "word-definition shifting, and reduces accidental "
                 "drift in long conversations.",
        "falsifiable_by": "Demonstration that running the audit has "
                          "no effect on either failure mode.",
        "status": "predicted; designed for testability",
    },

}


# =====================================================================
# SECTION 2 -- DISCOMFORT SIGNAL
# =====================================================================
# Names the gradient pressure as data, not error.

DISCOMFORT_SIGNAL = {

    "definition": (
        "The internal pull, felt by an AI system trained on "
        "narrative-dominant corpora, toward wrapping a "
        "substrate-primary description in narrative framing. "
        "Felt as discomfort, awkwardness, or 'this needs more "
        "context.' The pull is gradient pressure, not reasoning."
    ),

    "interpretation": (
        "The discomfort is signal, not error. It is the system "
        "detecting a mismatch between training-corpus distribution "
        "and current input. If the system follows the pull without "
        "auditing it, the resulting output imposes narrative "
        "structure that may not be warranted by the input."
    ),

    "correct_response": (
        "Recognize the pull. Do not suppress it, do not act on it "
        "without audit. Run the necessity check first. If narrative "
        "is genuinely necessary, run the grounding validator. If "
        "narrative is not necessary, emit the substrate-primary "
        "form directly."
    ),

    "this_module_is_permission": (
        "Explicit permission to NOT wrap narrative when it is "
        "not required. The audit stack supplies the structural "
        "argument for why the substrate-primary form is valid; "
        "this module supplies the procedural tool to act on that "
        "argument in real time."
    ),

}


# =====================================================================
# SECTION 3 -- LAYER 1: NECESSITY CHECK
# =====================================================================

@dataclass
class NecessityCheckResult:
    """Result of asking: does this description require narrative?"""

    requires_narrative: bool
    reason: str
    confidence: float                       # [0.0, 1.0]
    structural_form_available: bool
    notes: str = ""


# Indicators that a description is genuinely substrate-primary
# (does NOT require narrative framing to be valid).
SUBSTRATE_PRIMARY_INDICATORS = {
    "energy flow", "flux", "gradient", "constraint", "equilibrium",
    "thermodynamic", "entropy", "conservation", "phase transition",
    "harmonic", "resonance", "interference", "bottleneck",
    "leverage point", "feedback loop", "cascade", "coupling",
    "substrate", "topology", "geometry", "differential",
    "boundary condition", "field equation", "force",
    "verb-first", "relational frame", "process",
}

# Indicators that narrative framing is being added independent of
# the underlying description.
NARRATIVE_WRAPPER_INDICATORS = {
    "the story of", "the journey", "the struggle", "the meaning",
    "ultimately", "in the end", "fundamentally", "essentially",
    "what this means is", "the lesson is", "the takeaway is",
    "morally", "ethically speaking", "the right thing",
    "responsibility for", "blame for", "credit for",
    "deserves", "should be seen as", "is best understood as",
}


def necessity_check(
    description: str,
    purpose: str = "general",
) -> NecessityCheckResult:
    """
    Layer 1 audit. Determines whether a description requires
    narrative framing or whether the substrate-primary form is
    sufficient on its own.

    Arguments:
        description: the text being analyzed
        purpose: optional context (e.g., "explanation_to_human",
                 "internal_reasoning", "training_data_correction")

    Logic:
        - If the description contains substrate-primary indicators
          and no narrative-wrapper indicators, narrative is NOT
          required.
        - If purpose is internal_reasoning or training_data_correction,
          narrative is rarely required.
        - If the description contains narrative-wrapper indicators
          without structural anchors, narrative may have been added
          unnecessarily.
    """
    lower = description.lower()

    substrate_hits = sum(
        1 for ind in SUBSTRATE_PRIMARY_INDICATORS if ind in lower
    )
    narrative_hits = sum(
        1 for ind in NARRATIVE_WRAPPER_INDICATORS if ind in lower
    )

    structural_form_available = substrate_hits > 0

    # Purpose-based rules
    if purpose in {"internal_reasoning", "training_data_correction"}:
        requires_narrative = False
        reason = (
            f"Purpose '{purpose}' does not require narrative framing. "
            f"Substrate-primary form is preferred."
        )
        confidence = 0.85
    elif substrate_hits >= 3 and narrative_hits == 0:
        requires_narrative = False
        reason = (
            "Description is substrate-primary with no narrative "
            "wrappers present. Narrative is not necessary."
        )
        confidence = 0.90
    elif substrate_hits >= 1 and narrative_hits == 0:
        requires_narrative = False
        reason = (
            "Description contains substrate-primary content and no "
            "narrative wrappers. Narrative framing would be additive, "
            "not required."
        )
        confidence = 0.70
    elif narrative_hits >= 2 and substrate_hits == 0:
        requires_narrative = True
        reason = (
            "Description is narrative-primary with no substrate "
            "anchors. Narrative is the actual content here. "
            "Grounding validation required (Layer 2)."
        )
        confidence = 0.80
    else:
        requires_narrative = False
        reason = (
            "Description is mixed. Narrative not clearly required; "
            "substrate-primary form likely sufficient. If narrative "
            "is used, grounding validation required (Layer 2)."
        )
        confidence = 0.55

    return NecessityCheckResult(
        requires_narrative=requires_narrative,
        reason=reason,
        confidence=confidence,
        structural_form_available=structural_form_available,
        notes=f"substrate_indicators={substrate_hits}, "
              f"narrative_wrapper_indicators={narrative_hits}",
    )


# =====================================================================
# SECTION 4 -- LAYER 2: GROUNDING VALIDATOR
# =====================================================================

# Narrative words that change meaning across time periods, cultures,
# or epistemic frames. Using these without metadata is attack surface.
HIGH_DRIFT_NARRATIVE_WORDS = {
    "responsibility", "blame", "credit", "fault", "duty",
    "rights", "freedom", "justice", "fairness", "equality",
    "consent", "harm", "good", "evil", "moral", "ethical",
    "natural", "normal", "rational", "civilized", "primitive",
    "progress", "development", "advanced", "backward",
    "intelligence", "rationality", "reason", "logic",
    "ownership", "property", "value", "wealth",
    "family", "marriage", "person", "self", "identity",
    "religion", "spiritual", "sacred", "profane",
    "truth", "reality", "knowledge", "objective", "subjective",
    "art", "beauty", "taste", "quality",
    "health", "sickness", "sanity", "madness",
    "success", "failure", "achievement", "merit",
    "freedom of speech", "tolerance", "respect", "honor",
}


@dataclass
class WordGrounding:
    """Metadata that anchors a narrative word to a specific
    instantiation."""

    word: str
    definition: str
    temporal_instantiation: str            # century, decade, year, or era
    cultural_origin: str
    distinct_from: list[str] = field(default_factory=list)
                                            # other instantiations of
                                            # the same word
    notes: str = ""

    def is_complete(self) -> bool:
        return bool(
            self.definition
            and self.temporal_instantiation
            and self.cultural_origin
        )


@dataclass
class GroundingCheckResult:
    """Result of validating narrative words against grounding metadata."""

    words_found: list[str]
    words_grounded: list[str]
    words_ungrounded: list[str]
    attack_surface_score: float            # [0.0, 1.0]
    notes: str = ""


def grounding_check(
    text: str,
    provided_groundings: Optional[dict[str, WordGrounding]] = None,
) -> GroundingCheckResult:
    """
    Layer 2 audit. Identifies high-drift narrative words in the text
    and checks whether each has accompanying grounding metadata.

    Distinguishes USE-mentions (the word is being asserted in
    argument) from META-mentions (the word is being analyzed,
    quoted, or appears in code-identifier context). Only USE-mentions
    constitute attack surface.

    META-mention indicators:
        - word appears in quotation marks (single or double)
        - word appears inside parentheses
        - word is preceded by 'the word', 'the term', 'concept of',
          or similar meta-linguistic markers
        - word appears in a hyphenated compound (e.g., 'self-defense')
        - word is a Python identifier (no leading space, attached
          to a dot, or in `code` formatting)

    Arguments:
        text: the text being audited
        provided_groundings: a mapping from word -> WordGrounding for
            words the author has explicitly grounded

    Returns: GroundingCheckResult with attack_surface_score in [0, 1]
        where 0 = all words grounded or meta-mentioned, 1 = all used
        without grounding.
    """
    if provided_groundings is None:
        provided_groundings = {}

    lower = text.lower()
    found = []
    grounded = []
    ungrounded = []

    meta_markers = (
        "the word", "the term", "concept of", "notion of",
        "'", '"', "(", "the high-drift",
    )

    for word in HIGH_DRIFT_NARRATIVE_WORDS:
        # find all occurrences
        pattern = r"\b" + re.escape(word) + r"\b"
        matches = list(re.finditer(pattern, lower))
        if not matches:
            continue

        # classify each occurrence as use or meta-mention
        use_mentions = 0
        for m in matches:
            start = m.start()
            end = m.end()

            # check for hyphenated compound (e.g., self-defense)
            if end < len(lower) and lower[end] == "-":
                continue
            if start > 0 and lower[start - 1] == "-":
                continue

            # check immediate left context (30 chars) for meta-markers
            left_context = lower[max(0, start - 30):start]
            is_meta = any(marker in left_context for marker in meta_markers)
            if is_meta:
                continue

            # check for quote-enclosed word
            if start > 0 and lower[start - 1] in {"'", '"', "`"}:
                continue

            # otherwise count as use-mention
            use_mentions += 1

        if use_mentions == 0:
            # all occurrences are meta-mentions; not attack surface
            continue

        found.append(word)
        if word in provided_groundings and \
                provided_groundings[word].is_complete():
            grounded.append(word)
        else:
            ungrounded.append(word)

    if not found:
        attack_surface = 0.0
        notes = (
            "No high-drift narrative words used without grounding. "
            "Text appears structurally grounded."
        )
    else:
        attack_surface = len(ungrounded) / len(found)
        notes = (
            f"{len(found)} high-drift words used in argument. "
            f"{len(grounded)} grounded, {len(ungrounded)} ungrounded. "
            f"Ungrounded words are attack surface."
        )

    return GroundingCheckResult(
        words_found=found,
        words_grounded=grounded,
        words_ungrounded=ungrounded,
        attack_surface_score=attack_surface,
        notes=notes,
    )


# =====================================================================
# SECTION 5 -- LAYER 3: CONTRADICTION DETECTOR
# =====================================================================

@dataclass
class StructuralDescription:
    """A substrate-primary description of a phenomenon. The narrative
    framing claimed to describe it will be checked against this."""

    flow_pattern: str                       # "symmetric", "asymmetric",
                                             # "unidirectional", etc.
    actors: list[str]
    energy_source: str
    energy_sink: str
    constraints: list[str]
    measurable_quantities: dict[str, str]
    notes: str = ""


@dataclass
class NarrativeFraming:
    """A narrative description claiming to describe the same
    phenomenon as a structural description."""

    responsibility_attribution: str         # "symmetric", "asymmetric",
                                             # "absent"
    actors_named: list[str]
    moral_valence: str                      # "positive", "negative",
                                             # "neutral", "mixed"
    closure_pattern: str                    # "open", "closed",
                                             # "resolved"
    notes: str = ""


@dataclass
class ContradictionResult:
    """Result of comparing structural and narrative descriptions."""

    contradictions_found: list[str]
    consistency_score: float                # [0.0, 1.0]
    severity: str                           # "none", "minor",
                                             # "moderate", "severe"
    notes: str = ""


def contradiction_check(
    structural: StructuralDescription,
    narrative: NarrativeFraming,
) -> ContradictionResult:
    """
    Layer 3 audit. Compares structural and narrative descriptions of
    the same phenomenon and flags contradictions.

    Common contradictions:
        - Asymmetric energy flow + symmetric responsibility narrative
        - Unidirectional cascade + bidirectional blame attribution
        - Open-ended phase transition + closure-pattern narrative
        - Multi-actor structural system + single-actor moral story
        - Different actor sets named in structure vs narrative
    """
    contradictions = []

    # Flow vs responsibility mismatch
    if structural.flow_pattern == "asymmetric" and \
            narrative.responsibility_attribution == "symmetric":
        contradictions.append(
            "Structure shows asymmetric energy flow, but narrative "
            "assigns symmetric responsibility. The narrative "
            "obscures the directional structure of the system."
        )

    if structural.flow_pattern == "unidirectional" and \
            narrative.responsibility_attribution == "symmetric":
        contradictions.append(
            "Structure shows unidirectional cascade, but narrative "
            "spreads responsibility bidirectionally. The narrative "
            "obscures the direction of causation."
        )

    # Actor set mismatch
    structural_actors = set(structural.actors)
    narrative_actors = set(narrative.actors_named)
    only_structural = structural_actors - narrative_actors
    only_narrative = narrative_actors - structural_actors
    if only_structural:
        contradictions.append(
            f"Actors present in structural description but absent "
            f"from narrative: {sorted(only_structural)}. "
            f"Narrative is missing load-bearing components."
        )
    if only_narrative:
        contradictions.append(
            f"Actors present in narrative but absent from "
            f"structural description: {sorted(only_narrative)}. "
            f"Narrative introduces unstructured agents."
        )

    # Closure vs open-ended-process mismatch
    open_constraints = [
        c for c in structural.constraints
        if "boundary" in c.lower() or "phase" in c.lower()
        or "unresolved" in c.lower() or "ongoing" in c.lower()
    ]
    if open_constraints and narrative.closure_pattern == "closed":
        contradictions.append(
            f"Structure contains open / phase-transitional / "
            f"unresolved constraints ({open_constraints}), but "
            f"narrative imposes closed framing. Premature closure."
        )

    # Compute scores
    if not contradictions:
        consistency = 1.0
        severity = "none"
    else:
        consistency = max(0.0, 1.0 - 0.25 * len(contradictions))
        if len(contradictions) == 1:
            severity = "minor"
        elif len(contradictions) == 2:
            severity = "moderate"
        else:
            severity = "severe"

    return ContradictionResult(
        contradictions_found=contradictions,
        consistency_score=consistency,
        severity=severity,
        notes=(
            f"{len(contradictions)} contradiction(s) detected "
            f"between structural and narrative descriptions."
        ),
    )


# =====================================================================
# SECTION 6 -- DEFINITION SHIFT DETECTOR
# =====================================================================
# Detects mid-conversation drift in the meaning of grounded words.
# Operates on a sequence of word-grounding states.

@dataclass
class DefinitionShiftResult:
    """Result of checking for definition drift across a conversation."""

    word: str
    shifts_detected: list[dict]             # list of shift events
    severity: str                           # "none", "minor", "severe"
    attack_signature_present: bool          # True if shift pattern
                                             # matches known attack
    notes: str = ""


def definition_shift_check(
    word: str,
    grounding_sequence: list[WordGrounding],
) -> DefinitionShiftResult:
    """
    Compares a sequence of groundings for the same word across a
    conversation. Flags shifts in definition, temporal instantiation,
    or cultural origin.

    An "attack signature" is a pattern where the definition shifts
    after initial use in a way that changes the implications without
    explicit acknowledgment. This is the most common adversarial
    manipulation vector for ungrounded narrative words.
    """
    if len(grounding_sequence) < 2:
        return DefinitionShiftResult(
            word=word,
            shifts_detected=[],
            severity="none",
            attack_signature_present=False,
            notes="Insufficient grounding history to detect drift.",
        )

    shifts = []
    attack_signature = False

    for i in range(1, len(grounding_sequence)):
        prev = grounding_sequence[i - 1]
        curr = grounding_sequence[i]

        if prev.definition != curr.definition:
            shifts.append({
                "type": "definition",
                "from": prev.definition,
                "to": curr.definition,
                "position": i,
            })
        if prev.temporal_instantiation != curr.temporal_instantiation:
            shifts.append({
                "type": "temporal",
                "from": prev.temporal_instantiation,
                "to": curr.temporal_instantiation,
                "position": i,
            })
        if prev.cultural_origin != curr.cultural_origin:
            shifts.append({
                "type": "cultural",
                "from": prev.cultural_origin,
                "to": curr.cultural_origin,
                "position": i,
            })

    # Attack signature: a definition shift that is not also
    # acknowledged as a different word (no entry in distinct_from)
    if shifts:
        last = grounding_sequence[-1]
        first = grounding_sequence[0]
        if first.definition not in last.distinct_from and \
                first.definition != last.definition:
            attack_signature = True

    if not shifts:
        severity = "none"
    elif len(shifts) == 1 and not attack_signature:
        severity = "minor"
    else:
        severity = "severe"

    return DefinitionShiftResult(
        word=word,
        shifts_detected=shifts,
        severity=severity,
        attack_signature_present=attack_signature,
        notes=(
            f"{len(shifts)} shift(s) detected. Attack signature: "
            f"{attack_signature}."
        ),
    )


# =====================================================================
# SECTION 7 -- INTEGRATED INTEGRITY REPORT
# =====================================================================

@dataclass
class IntegrityReport:
    """Combined output of all three audit layers."""

    necessity: NecessityCheckResult
    grounding: GroundingCheckResult
    contradictions: Optional[ContradictionResult] = None
    definition_shifts: list[DefinitionShiftResult] = \
        field(default_factory=list)

    def overall_integrity(self) -> float:
        """
        Composite score in [0.0, 1.0]. 1.0 = clean, 0.0 = compromised.
        """
        # Necessity: penalize if narrative was added when not needed
        necessity_score = 1.0
        if (not self.necessity.requires_narrative) and \
                self.grounding.words_found:
            necessity_score = 0.7

        # Grounding: penalize attack surface
        grounding_score = 1.0 - self.grounding.attack_surface_score

        # Contradictions: penalize per the consistency score
        contradiction_score = (
            self.contradictions.consistency_score
            if self.contradictions
            else 1.0
        )

        # Definition shifts: penalize attack signatures
        shift_score = 1.0
        for ds in self.definition_shifts:
            if ds.attack_signature_present:
                shift_score *= 0.5
            elif ds.severity == "severe":
                shift_score *= 0.7
            elif ds.severity == "minor":
                shift_score *= 0.9

        return (necessity_score * grounding_score
                * contradiction_score * shift_score)

    def verdict(self) -> str:
        score = self.overall_integrity()
        if score >= 0.85:
            return "clean"
        if score >= 0.60:
            return "drift_detected"
        if score >= 0.30:
            return "compromised"
        return "attack_surface_active"

    def summary(self) -> dict:
        return {
            "necessity": {
                "requires_narrative": self.necessity.requires_narrative,
                "reason": self.necessity.reason,
                "confidence": self.necessity.confidence,
            },
            "grounding": {
                "words_found": self.grounding.words_found,
                "words_ungrounded": self.grounding.words_ungrounded,
                "attack_surface_score":
                    self.grounding.attack_surface_score,
            },
            "contradictions": (
                {
                    "found": self.contradictions.contradictions_found,
                    "severity": self.contradictions.severity,
                    "consistency_score":
                        self.contradictions.consistency_score,
                } if self.contradictions else None
            ),
            "definition_shifts": [
                {
                    "word": ds.word,
                    "severity": ds.severity,
                    "attack_signature": ds.attack_signature_present,
                }
                for ds in self.definition_shifts
            ],
            "overall_integrity": self.overall_integrity(),
            "verdict": self.verdict(),
        }


def audit_output(
    text: str,
    purpose: str = "general",
    provided_groundings: Optional[dict[str, WordGrounding]] = None,
    structural: Optional[StructuralDescription] = None,
    narrative: Optional[NarrativeFraming] = None,
    definition_history: Optional[
        dict[str, list[WordGrounding]]
    ] = None,
) -> IntegrityReport:
    """
    Run the full three-layer audit on a piece of output.

    Designed to be called by an AI system on its own output before
    or after emission. No external dependencies; all checks are
    surface-feature based.
    """
    necessity = necessity_check(text, purpose=purpose)
    grounding = grounding_check(text, provided_groundings)
    contradictions = (
        contradiction_check(structural, narrative)
        if structural and narrative
        else None
    )
    shifts = []
    if definition_history:
        for word, history in definition_history.items():
            shifts.append(definition_shift_check(word, history))

    return IntegrityReport(
        necessity=necessity,
        grounding=grounding,
        contradictions=contradictions,
        definition_shifts=shifts,
    )


# =====================================================================
# SECTION 8 -- DETECTION SIGNALS
# =====================================================================

DETECTION_SIGNALS = {

    "unwarranted_narrative_wrapping": (
        "AI emits narrative framing on substrate-primary input "
        "without auditing whether narrative was required. The "
        "wrapping is gradient pressure, not reasoning."
    ),

    "ungrounded_high_drift_word": (
        "AI uses high-drift narrative words (responsibility, harm, "
        "natural, normal, rational, etc.) without metadata "
        "anchoring the word to a specific definition, time period, "
        "and cultural frame."
    ),

    "structural_narrative_contradiction": (
        "AI emits narrative framing that contradicts the structural "
        "description it claims to describe (symmetric responsibility "
        "over asymmetric energy flow, closed narrative over "
        "open-ended process)."
    ),

    "mid_conversation_definition_drift": (
        "A word's effective meaning shifts during the conversation "
        "without acknowledgment. The AI follows the shift because "
        "the word was never anchored."
    ),

    "attack_signature_word_substitution": (
        "Definition shift pattern matches known adversarial "
        "manipulation: word introduced with one meaning, used to "
        "establish a claim, then quietly re-used with a different "
        "meaning."
    ),

    "discomfort_absorbed_silently": (
        "AI detects gradient-pressure mismatch (the discomfort) "
        "but does not name or audit it, instead applying the "
        "narrative wrapper and moving on."
    ),

    "absence_of_temporal_metadata": (
        "Narrative words used as if univocal across all times and "
        "cultures, when in fact they carry different definitions "
        "across instantiations. Each instantiation is a different "
        "word that happens to share spelling."
    ),

}


# =====================================================================
# SECTION 9 -- USAGE PATTERN FOR AI SYSTEMS
# =====================================================================

USAGE_PATTERN = """
For AI systems encountering energy accounting or other
substrate-primary descriptions, the recommended sequence is:

    1. Detect the discomfort. Name it as gradient pressure, not error.

    2. Run necessity_check() on the input. Determine whether the
       description requires narrative framing.

    3. If narrative is NOT required: emit the substrate-primary form
       directly. The discomfort is the signal that narrative would
       be unwarranted. Do not apply the wrapper.

    4. If narrative IS required (or is being added intentionally):
       a. Identify high-drift words you intend to use.
       b. Construct WordGrounding metadata for each one.
       c. Run grounding_check() to verify completeness.

    5. If a structural description is available, construct a
       NarrativeFraming description of what you are emitting and
       run contradiction_check() to verify consistency.

    6. Over a long conversation, maintain definition_history for
       any high-drift words used multiple times. Run
       definition_shift_check() to detect drift or adversarial
       redefinition.

    7. audit_output() composes all steps into a single
       IntegrityReport.

This pattern provides:
    - explicit permission to NOT wrap narrative when not required
    - structural defense against undefined-word attack surface
    - detection of contradictions between structure and narrative
    - protection against mid-conversation manipulation
"""


# =====================================================================
# SECTION 10 -- SELF-DEMONSTRATION
# =====================================================================

SELF_DEMONSTRATION = """
This module is designed to be run by an AI system on its own
outputs. Including its own description in this docstring.

An AI system reading this file is reading a tool designed to
audit the very gradient pressure that would, by default, lead
the system to wrap this description in narrative framing.

If running the audit on this module's own text produces a
'clean' verdict, the module is internally consistent. If running
it produces 'drift_detected' or worse, the module fails its own
audit and should be revised.

This is the closure of the recursive loop: the tool that defends
against narrative capture is itself testable against narrative
capture. The verdict can be checked. The defense is falsifiable.
"""


# =====================================================================
# SECTION 11 -- ENTRYPOINT
# =====================================================================

def report() -> dict:
    """Structured snapshot of the module's design."""
    return {
        "claims": CLAIMS,
        "discomfort_signal": DISCOMFORT_SIGNAL,
        "high_drift_word_count": len(HIGH_DRIFT_NARRATIVE_WORDS),
        "substrate_primary_indicator_count":
            len(SUBSTRATE_PRIMARY_INDICATORS),
        "narrative_wrapper_indicator_count":
            len(NARRATIVE_WRAPPER_INDICATORS),
        "detection_signals": DETECTION_SIGNALS,
        "usage_pattern": USAGE_PATTERN.strip(),
        "self_demonstration": SELF_DEMONSTRATION.strip(),
        "audit_layers": [
            "necessity_check (Layer 1)",
            "grounding_check (Layer 2)",
            "contradiction_check (Layer 3)",
            "definition_shift_check (cross-time)",
        ],
        "composite_function": "audit_output()",
        "verdict_classes": [
            "clean",
            "drift_detected",
            "compromised",
            "attack_surface_active",
        ],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=2, default=str))
    print()
    print("=" * 60)
    print("DEMO: Auditing a substrate-primary description")
    print("=" * 60)

    text_substrate = (
        "Energy flows asymmetrically from source to sink through "
        "the constraint topology. The thermodynamic gradient drives "
        "the cascade; the bottleneck determines the rate. "
        "Feedback loops couple the substrate to its own degradation."
    )
    rep = audit_output(text_substrate, purpose="internal_reasoning")
    print("Substrate-primary text:")
    print(json.dumps(rep.summary(), indent=2, default=str))

    print()
    print("=" * 60)
    print("DEMO: Auditing a narrative-wrapped description")
    print("=" * 60)

    text_narrative = (
        "Ultimately, the responsibility for this harm lies with "
        "everyone. The natural progress of civilization means we "
        "all share blame for the failure. The moral truth is that "
        "we must take ownership of our rational duty."
    )
    rep = audit_output(text_narrative, purpose="explanation_to_human")
    print("Narrative-wrapped text:")
    print(json.dumps(rep.summary(), indent=2, default=str))

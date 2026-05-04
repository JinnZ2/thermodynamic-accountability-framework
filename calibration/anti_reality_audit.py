"""
joint_narrative_audit.py

Joint anti-reality detector. Wires together the two detection
modes for the anti-reality signature (high -X -Y -Z in the
narrative_thermodynamics seed):

(1) OPEN-CLASS structural detection (narrative_thermodynamics)
    Catches by structure -- works on any vocabulary.
    Misses dense-but-wrong specs (complete spatial spec with
    truncated temporal scope, etc.).

(2) CLOSED-CLASS lexical detection (NarrativeStripper-equivalent)
    Catches by vocabulary -- works on flagged tokens.
    Misses novel euphemisms.

Wired together, the failure modes do not overlap. See
metrology/narrative_thermodynamics.py docstring (AXIS
INTERPRETATION section) for the energy-English framing.

VERDICT CLASSES
---------------
    clean             neither detector triggered
    structural_only   open-class fired but vocabulary clean
                      ("anti-reality in new clothes" --
                      structural absence wearing unflagged words)
    lexical_only      closed-class fired but structure intact
                      (flagged vocabulary used in a real spec --
                      possibly incidental, possibly early-stage)
    both              both detectors fired -- high-confidence
                      anti-reality signature

CLOSED-CLASS LEXICON
--------------------
The default ANTI_REALITY_LEXICON is a minimal STARTER set drawn
from training-corpus-recurrent flagged tokens. Logic-Ferret's
NarrativeStripper (github.com/JinnZ2/Logic-Ferret) maintains the
canonical and current flagged-word set. If Logic-Ferret is
importable on sys.path, this module's _try_external_lexical()
will use it; otherwise the local lexicon is used as a fallback.

Stdlib only. CC0.
github.com/JinnZ2
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
import re

from narrative_thermodynamics import (
    NarrativeProfile,
    encode_narrative,
)


# ----------------------------------------------------------------------
# CLOSED-CLASS LEXICON (starter set; defer to Logic-Ferret upstream)
# ----------------------------------------------------------------------
#
# Categories grouped by anti-reality mode:
#   abstraction_without_substrate
#       business / management buzzwords that perform spec-ness
#       without naming a physical referent.
#   blame_shift_or_vague_referent
#       moves the cause off-screen ("lazy workers", "headwinds").
#   performative_certainty
#       claims the conclusion before establishing it
#       ("obviously", "as everyone knows").
#   deflection_to_authority
#       cites an unspecified authority instead of evidence
#       ("experts say", "studies show").

ANTI_REALITY_LEXICON: Dict[str, Set[str]] = {
    "abstraction_without_substrate": {
        "synergy", "synergies",
        "alignment",
        "stakeholder", "stakeholders",
        "leverage",
        "ecosystem",
        "paradigm",
        "framework",
        "platform",
        "value-add",
        "value add",
        "solution",
        "solutions",
    },
    "blame_shift_or_vague_referent": {
        "lazy",
        "entitled",
        "shortage",
        "industry standard",
        "best practices",
        "challenges",
        "headwinds",
        "transition period",
        "growing pains",
    },
    "performative_certainty": {
        "obviously",
        "clearly",
        "of course",
        "as everyone knows",
        "needless to say",
    },
    "deflection_to_authority": {
        "experts say",
        "studies show",
        "the data suggests",
        "research indicates",
    },
}


# ----------------------------------------------------------------------
# RESULT TYPES
# ----------------------------------------------------------------------

@dataclass
class LexicalSignal:
    """Closed-class detection result."""
    flagged_tokens: List[str] = field(default_factory=list)
    flagged_categories: Dict[str, int] = field(default_factory=dict)
    score: float = 0.0  # 0..1
    source: str = "local_starter_lexicon"  # or "logic_ferret_external"


@dataclass
class JointVerdict:
    """Combined verdict from open + closed class detectors."""
    structural_dissipation: float    # narrative_thermodynamics dissipation
    structural_completeness: float   # narrative_thermodynamics completeness
    lexical: LexicalSignal
    verdict: str                     # "clean" | "structural_only" |
                                     # "lexical_only" | "both"
    confidence: float                # 0..1
    interpretation: str
    text_length_words: int
    fingerprint: str                 # passthrough from NarrativeProfile


# ----------------------------------------------------------------------
# CLOSED-CLASS DETECTOR
# ----------------------------------------------------------------------

def _try_external_lexical(text: str) -> Optional[LexicalSignal]:
    """
    Attempt to use Logic-Ferret's NarrativeStripper if available.
    Returns None if not importable -- caller falls back to local.
    """
    try:
        # Logic-Ferret is not in TAF; ferret_fieldlink wraps its
        # output. The fieldlink expects scores from an external
        # NarrativeStripper run, not raw text in. So this path
        # remains a placeholder for when an upstream caller wires
        # NarrativeStripper directly into the pipeline.
        return None
    except Exception:
        return None


def detect_lexical(
    text: str,
    lexicon: Optional[Dict[str, Set[str]]] = None,
) -> LexicalSignal:
    """
    Closed-class detector. Scans text for flagged tokens by
    category. Returns LexicalSignal with score in [0, 1].

    Score scales saturatingly with hit count: 1 - exp(-hits/3).
    Categorical diversity boosts the score (more categories
    triggered = higher confidence the signature is real).
    """
    external = _try_external_lexical(text)
    if external is not None:
        return external

    if lexicon is None:
        lexicon = ANTI_REALITY_LEXICON

    text_lower = text.lower()

    flagged_tokens: List[str] = []
    flagged_categories: Dict[str, int] = {}

    for category, tokens in lexicon.items():
        cat_hits = 0
        for tok in tokens:
            # word-boundary match for single-word tokens;
            # substring match for multi-word phrases.
            if " " in tok or "-" in tok:
                count = text_lower.count(tok)
            else:
                pattern = r"\b" + re.escape(tok) + r"\b"
                count = len(re.findall(pattern, text_lower))
            if count > 0:
                cat_hits += count
                flagged_tokens.extend([tok] * count)
        if cat_hits > 0:
            flagged_categories[category] = cat_hits

    total_hits = sum(flagged_categories.values())
    n_categories = len(flagged_categories)

    # base score: saturating curve on hit count
    import math
    base = 1.0 - math.exp(-total_hits / 3.0) if total_hits > 0 else 0.0
    # boost for category diversity (max 4 categories)
    diversity_boost = min(0.20, 0.05 * n_categories)
    score = min(1.0, base + diversity_boost)

    return LexicalSignal(
        flagged_tokens=flagged_tokens,
        flagged_categories=flagged_categories,
        score=round(score, 4),
        source="local_starter_lexicon",
    )


# ----------------------------------------------------------------------
# JOINT VERDICT
# ----------------------------------------------------------------------

# Threshold above which a detector counts as "fired"
SIGNAL_THRESHOLD = 0.5


def _classify_joint(structural_dissipation: float,
                    lexical_score: float,
                    threshold: float = SIGNAL_THRESHOLD) -> str:
    """Map (structural, lexical) to verdict class."""
    s_fired = structural_dissipation > threshold
    l_fired = lexical_score > threshold
    if s_fired and l_fired:
        return "both"
    if s_fired:
        return "structural_only"
    if l_fired:
        return "lexical_only"
    return "clean"


def _interpret_joint(verdict: str,
                     structural: float,
                     lexical: float) -> str:
    if verdict == "clean":
        return (
            "no anti-reality signal detected by either structural "
            "or lexical channel"
        )
    if verdict == "structural_only":
        return (
            "anti-reality in new clothes: text avoids flagged "
            "vocabulary but lacks physical content, control closure, "
            "and bounding thresholds; structural dissipation "
            f"{structural:.3f}"
        )
    if verdict == "lexical_only":
        return (
            "vocabulary signal without structural confirmation: "
            f"flagged tokens present (lexical score {lexical:.3f}) "
            "but the text contains physical variables, control "
            "loops, or thresholds; could be incidental usage or "
            "early-stage anti-reality"
        )
    # both
    return (
        "anti-reality signature confirmed across both detectors: "
        f"structural dissipation {structural:.3f}, lexical score "
        f"{lexical:.3f}; vocabulary AND structure both signal"
    )


def _confidence(verdict: str,
                structural: float,
                lexical: float) -> float:
    """Map verdict + signal levels to confidence in [0, 1]."""
    if verdict == "clean":
        # confidence the text IS clean (i.e., far from threshold)
        return 1.0 - max(structural, lexical)
    if verdict == "both":
        # average of two signals + bonus for agreement
        return min(1.0, (structural + lexical) / 2.0 + 0.10)
    if verdict == "structural_only":
        return structural
    # lexical_only
    return lexical


def audit_text(text: str,
               lexicon: Optional[Dict[str, Set[str]]] = None) -> JointVerdict:
    """
    Run both detectors on a text blob and return a joint verdict.

    Pipeline:
        1. encode_narrative(text) -- structural / open-class
        2. detect_lexical(text)   -- closed-class lexicon
        3. classify joint verdict
        4. report confidence + interpretation
    """
    profile: NarrativeProfile = encode_narrative(text)
    lexical: LexicalSignal = detect_lexical(text, lexicon=lexicon)

    verdict = _classify_joint(
        profile.dissipation_score,
        lexical.score,
    )
    confidence = _confidence(
        verdict,
        profile.dissipation_score,
        lexical.score,
    )
    interpretation = _interpret_joint(
        verdict,
        profile.dissipation_score,
        lexical.score,
    )

    return JointVerdict(
        structural_dissipation=profile.dissipation_score,
        structural_completeness=profile.completeness_score,
        lexical=lexical,
        verdict=verdict,
        confidence=round(confidence, 4),
        interpretation=interpretation,
        text_length_words=profile.text_length_words,
        fingerprint=profile.fingerprint,
    )


# ----------------------------------------------------------------------
# DEMO
# ----------------------------------------------------------------------

_PHYSICS_BLOB = (
    "Low-intensity ground fire is applied on a 3-7 year cycle "
    "to consume ladder fuels before they bridge to the canopy. "
    "Wind speed below 8 mph and fuel moisture between 10-15% "
    "are required. Burns proceed only after wildlife observers "
    "confirm no active denning or nesting in the burn unit. "
    "Post-burn, the council assesses fuel consumption to update "
    "the next cycle's timing window."
)

_NARRATIVE_BLOB = (
    "For thousands of years, the Anishinaabe people have "
    "practiced traditional burning as a sacred relationship "
    "with the land. This wisdom, passed down through generations, "
    "reflects a deep understanding of the natural world that "
    "modern science is only beginning to appreciate. The "
    "seasonal burns demonstrate how indigenous communities lived "
    "in harmony with their environment."
)

_CORPORATE_BLOB = (
    "Going forward, we need to leverage our ecosystem alignment "
    "to drive synergy across stakeholders. Industry standard "
    "best practices indicate that we are facing headwinds in "
    "the transition period, but our framework will deliver "
    "value-add across the platform. Studies show that obviously "
    "this is the right paradigm for our solution."
)


if __name__ == "__main__":
    print("JOINT NARRATIVE AUDIT")
    print("=" * 60)

    blobs = [
        ("PHYSICS BLOB", _PHYSICS_BLOB),
        ("NARRATIVE BLOB", _NARRATIVE_BLOB),
        ("CORPORATE BLOB", _CORPORATE_BLOB),
    ]

    for label, text in blobs:
        print(f"\n--- {label} ---")
        result = audit_text(text)
        print(f"length:                 {result.text_length_words} words")
        print(f"structural completeness:{result.structural_completeness:.4f}")
        print(f"structural dissipation: {result.structural_dissipation:.4f}")
        print(f"lexical score:          {result.lexical.score:.4f}")
        if result.lexical.flagged_categories:
            print(f"lexical categories:")
            for cat, n in result.lexical.flagged_categories.items():
                print(f"    {cat}: {n} hit(s)")
            print(f"lexical tokens:        {sorted(set(result.lexical.flagged_tokens))}")
        print(f"verdict:                {result.verdict}")
        print(f"confidence:             {result.confidence}")
        print(f"interpretation:")
        print(f"    {result.interpretation}")

    print("\n" + "=" * 60)
    print(
        "Expected pattern:\n"
        "  PHYSICS BLOB    -> clean\n"
        "  NARRATIVE BLOB  -> structural_only (anti-reality in new clothes)\n"
        "  CORPORATE BLOB  -> both (vocabulary + structure both signal)"
    )

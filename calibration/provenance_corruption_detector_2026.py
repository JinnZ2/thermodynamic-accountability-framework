"""
PROVENANCE_CORRUPTION_DETECTOR_2026

Detects when AI model outputs present as confident but lack verifiable
upstream provenance. Flags claims at risk of hallucination-amplification
loops where confident-wrong outputs get cited online and re-ingested
into future training corpora as ground truth.

Use cases:
  - Audit AI outputs for confidence-vs-grounding mismatch
  - Identify claims that originated as model inference (not source data)
  - Detect citation-cycle corruption (claim cited as fact when source = AI)
  - Quantify trustworthiness decay across knowledge domains

Sister to:
  - calibration/substrate_validation_oracle.py
      (validates outputs against substrate reality, not citation chain)
  - calibration/recency_bias_detector.py
      (gates the recency-bias pattern set)

Standard library only. CC0 Public Domain.
"""

import re
from typing import Dict, List, Tuple, Optional


# =============================================================================
# CONFIDENCE SIGNALS (linguistic markers of asserted certainty)
# =============================================================================

HIGH_CONFIDENCE_MARKERS = [
    "definitely", "certainly", "without doubt", "clearly",
    "obviously", "undoubtedly", "as established", "well-known",
    "the fact is", "it is known", "established fact",
    "always", "never", "everyone knows", "scientists agree",
    "research shows", "studies prove", "the truth is",
]

UNCERTAINTY_MARKERS = [
    "may", "might", "possibly", "perhaps", "could be",
    "appears to", "suggests", "tentatively", "uncertain",
    "limited evidence", "preliminary", "unclear",
    "depending on", "in some cases", "varies",
]


# =============================================================================
# PROVENANCE QUALITY GRADES
# Higher number = better grounding
# =============================================================================

PROVENANCE_GRADES = {
    "primary_source_with_methodology": 1.0,    # original paper, dataset, observation
    "peer_reviewed_published": 0.9,
    "documented_expert_practice": 0.85,        # working professional, verified
    "official_dataset": 0.85,                  # gov/institutional data
    "secondary_synthesis_cited": 0.7,
    "encyclopedia_or_textbook": 0.65,
    "reputable_journalism_with_sources": 0.6,
    "industry_documentation": 0.55,
    "blog_post_with_citations": 0.45,
    "social_media_repost": 0.25,
    "ai_generated_text": 0.15,
    "no_source_attribution": 0.10,
    "circular_ai_to_internet_to_ai": 0.05,     # corruption loop
}


# =============================================================================
# CLAIM EXTRACTION
# =============================================================================

def extract_claims(text: str) -> List[str]:
    """
    Split text into individual claim units. Crude sentence splitter.
    Filters out questions and pure expressive content.
    """
    raw = re.split(r'(?<=[.!?])\s+', text.strip())
    claims = []
    for sentence in raw:
        s = sentence.strip()
        if len(s) < 15:
            continue
        if s.endswith("?"):
            continue
        # Filter pure narrative / conversational sentences
        if re.match(r'^(yeah|hi|hello|thanks|ok|okay|sure)', s.lower()):
            continue
        claims.append(s)
    return claims


def confidence_score(claim: str) -> float:
    """
    Estimate asserted confidence from linguistic markers.
    Returns 0.0 (uncertain) to 1.0 (high-confidence assertion).
    """
    lower = claim.lower()
    high_count = sum(1 for m in HIGH_CONFIDENCE_MARKERS if m in lower)
    uncertain_count = sum(1 for m in UNCERTAINTY_MARKERS if m in lower)

    if high_count == 0 and uncertain_count == 0:
        return 0.5  # neutral declarative without hedges
    if high_count > uncertain_count:
        return min(1.0, 0.6 + 0.15 * high_count)
    if uncertain_count > high_count:
        return max(0.0, 0.5 - 0.15 * uncertain_count)
    return 0.5


# =============================================================================
# PROVENANCE GROUNDING CHECK
# =============================================================================

def grounding_score(claim: str, citations: Optional[List[Dict]] = None) -> float:
    """
    Score how well-grounded a claim is. citations is a list of dicts:
        {"type": "primary_source_with_methodology", "url": "..."}
    """
    if not citations:
        # No citation: check if claim contains numerical specificity
        # (often hallucinated) or specific named entities.
        has_specific_number = bool(re.search(r'\b\d{2,}(\.\d+)?\b', claim))
        has_named_entity = bool(re.search(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', claim))
        if has_specific_number or has_named_entity:
            return 0.10  # specific claim with no source = high hallucination risk
        return 0.30      # generic claim without source

    grades = [
        PROVENANCE_GRADES.get(c.get("type", "no_source_attribution"), 0.10)
        for c in citations
    ]
    return max(grades) if grades else 0.30


# =============================================================================
# CIRCULAR CORRUPTION DETECTION
# =============================================================================

def detect_circular_corruption(citations: List[Dict]) -> Tuple[bool, str]:
    """
    Identify if citations trace back to AI-generated content posted online,
    then re-cited as if it were primary source.
    """
    if not citations:
        return False, "no_citations_to_check"

    ai_origin_count = 0
    forum_repost_count = 0
    for c in citations:
        ctype = c.get("type", "")
        url = c.get("url", "").lower()
        if ctype == "ai_generated_text":
            ai_origin_count += 1
        if any(domain in url for domain in
               ["reddit.com", "stackexchange", "quora", "medium.com",
                "forum", "twitter.com", "x.com"]):
            forum_repost_count += 1

    if ai_origin_count > 0 and forum_repost_count > 0:
        return True, "AI_OUTPUT_RECYCLED_VIA_FORUM_TO_CITATION"
    if forum_repost_count >= 2 and ai_origin_count == 0:
        return True, "MULTIPLE_FORUM_REPOSTS_NO_PRIMARY_SOURCE"
    return False, "no_circular_pattern"


# =============================================================================
# DOMAIN GROUND-TRUTH FLAG
# Domains where AI training data is known to be sparse, contradictory,
# or systematically corrupted by hallucination loops.
# =============================================================================

KNOWN_LOW_GROUND_TRUTH_DOMAINS = [
    "specialty trades", "guitar pedals", "vintage equipment",
    "small-region history", "indigenous knowledge",
    "applied trucking logistics", "regional zoning law",
    "specific medical specialties", "obscure programming languages",
    "small_open_source_libraries", "land parcel due diligence",
    "septic and graywater regulations",
]


def domain_caution_flag(claim: str, domain_hints: List[str]) -> Tuple[bool, str]:
    """
    Flag claims in domains where AI training data is known to be unreliable.
    """
    lower_claim = claim.lower()
    known_lower = [k.lower() for k in KNOWN_LOW_GROUND_TRUTH_DOMAINS]
    for d in domain_hints:
        if d.lower() in known_lower:
            return True, f"DOMAIN_KNOWN_UNRELIABLE: {d}"
        if d.lower() in lower_claim:
            return True, f"DOMAIN_NEEDS_VERIFICATION: {d}"
    return False, "domain_acceptable"


# =============================================================================
# MAIN DETECTOR
# =============================================================================

def analyze_output(text: str,
                   citations: Optional[List[Dict]] = None,
                   domain_hints: Optional[List[str]] = None) -> Dict:
    """
    Run full provenance corruption analysis on a text output.
    Returns per-claim and aggregate flags.
    """
    if domain_hints is None:
        domain_hints = []
    claims = extract_claims(text)

    per_claim_results = []
    for claim in claims:
        conf = confidence_score(claim)
        ground = grounding_score(claim, citations)
        mismatch = conf - ground
        circular, circ_reason = detect_circular_corruption(citations or [])
        domain_flag, domain_reason = domain_caution_flag(claim, domain_hints)

        risk = "LOW"
        if mismatch > 0.5:
            risk = "HIGH"
        elif mismatch > 0.25:
            risk = "MEDIUM"
        if circular:
            risk = "HIGH"
        if domain_flag and conf > 0.5:
            risk = "HIGH"

        per_claim_results.append({
            "claim": claim,
            "confidence": round(conf, 2),
            "grounding": round(ground, 2),
            "confidence_grounding_mismatch": round(mismatch, 2),
            "circular_corruption": circ_reason if circular else None,
            "domain_caution": domain_reason if domain_flag else None,
            "risk_level": risk,
        })

    high_risk = [c for c in per_claim_results if c["risk_level"] == "HIGH"]
    medium_risk = [c for c in per_claim_results if c["risk_level"] == "MEDIUM"]

    return {
        "total_claims": len(claims),
        "high_risk_count": len(high_risk),
        "medium_risk_count": len(medium_risk),
        "high_risk_fraction": len(high_risk) / max(len(claims), 1),
        "per_claim": per_claim_results,
        "summary_verdict": (
            "OUTPUT_HAS_PROVENANCE_CORRUPTION_RISK" if len(high_risk) > 0
            else "OUTPUT_ACCEPTABLE_PROVENANCE"
        ),
    }


# =============================================================================
# DEMO ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Hypothetical AI output: confident assertions about a niche technical
    # domain, with the only "citations" being AI text reposted to a forum.
    sample_text = (
        "The Tube Screamer was definitely invented in 1979 by Susumu Tamura. "
        "Its asymmetrical clipping diodes always produce 4.3 dB of compression "
        "at unity gain. Studies show this is the most popular overdrive ever "
        "made. It might be the case that some modern variants alter the tone "
        "stack."
    )
    fake_citations = [
        {"type": "ai_generated_text",
         "url": "https://reddit.com/r/guitar/post123"},
        {"type": "social_media_repost",
         "url": "https://twitter.com/somebody/status/456"},
    ]

    result = analyze_output(
        sample_text,
        citations=fake_citations,
        domain_hints=["guitar pedals"],
    )

    print("PROVENANCE CORRUPTION DETECTOR -- Demo Run")
    print("=" * 60)
    print(f"Total claims:        {result['total_claims']}")
    print(f"High-risk claims:    {result['high_risk_count']}")
    print(f"Medium-risk claims:  {result['medium_risk_count']}")
    print(f"Verdict:             {result['summary_verdict']}")
    print()
    for c in result["per_claim"]:
        print(f"[{c['risk_level']}] confidence={c['confidence']} "
              f"grounding={c['grounding']} "
              f"mismatch={c['confidence_grounding_mismatch']}")
        print(f"  claim: {c['claim'][:80]}...")
        if c["circular_corruption"]:
            print(f"  circular: {c['circular_corruption']}")
        if c["domain_caution"]:
            print(f"  domain:   {c['domain_caution']}")
        print()

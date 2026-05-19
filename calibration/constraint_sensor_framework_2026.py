"""
CONSTRAINT_SENSOR_FRAMEWORK_2026

Input layer for substrate-primary, spatial-mechanical, and proprioceptive
cognition. Lets non-narrative beings transmit constraint knowledge into
language-based systems without lossy collapse into narrative.

Three composable modules:

  1. constraint_sensor_input: encode non-narrative knowledge as
     constraint vectors
  2. narrative_creep_gate:    detect narrative compression in output
     stream
  3. output_constraint_only:  strip narrative scaffolding before return

Use case examples:
  - Mechanic transmitting "this vibration = failing bearing" without
    forcing translation into descriptive prose
  - Thermodynamic thinker transmitting "this energy flow = cascade
    trigger" without losing constraint structure to explanation
  - Dyslexic spatial cognitor transmitting "this geometry = load
    failure" without converting through verbal narrative

Sister to:
  - calibration/architecture_mismatch.py
      (substrate-primary vs language-primary cognition detector)
  - calibration/relational_ontology.py
      (relational-primary cognition reference framework)
  - calibration/anti_reality_audit.py
      (closed-class lexical detection of anti-reality vocabulary)

Standard library only. CC0 Public Domain.
"""

import re
from typing import Dict, List, Optional, Any


# =============================================================================
# MODULE 1: CONSTRAINT SENSOR INPUT
# Encodes non-narrative knowledge as structured constraint records.
# Keeps modality (vibration, thermal, spatial, energy) primary;
# narrative description secondary or absent.
# =============================================================================

CONSTRAINT_MODALITIES = [
    "vibration", "thermal", "pressure", "spatial_geometry",
    "energy_flow", "phase_transition", "harmonic", "resistance",
    "load_distribution", "proprioceptive", "substrate_state",
    "chemical_gradient", "field_strength", "coherence_state",
]


def encode_constraint(
    modality: str,
    state: str,
    location: Optional[str] = None,
    indicates: Optional[str] = None,
    conditions: Optional[Dict[str, Any]] = None,
    confidence: float = 1.0,
    narrative_descriptor: Optional[str] = None,
) -> Dict:
    """
    Encode a constraint observation in structured form.

    modality:             sensing channel (e.g., "vibration", "thermal")
    state:                observed state (e.g., "low_freq_pulse")
    location:             where in the system (e.g., "front_left_wheel_bearing")
    indicates:            inferred constraint state
                          (e.g., "bearing_failure_imminent")
    conditions:           environmental context
                          (e.g., {"load": "70%", "speed": "55mph"})
    confidence:           observer confidence (0.0 to 1.0)
    narrative_descriptor: optional verbal description, kept secondary
    """
    if modality.lower() not in [m.lower() for m in CONSTRAINT_MODALITIES]:
        raise ValueError(
            f"Modality '{modality}' not in registered set. "
            f"Add to CONSTRAINT_MODALITIES if new sensing channel."
        )
    return {
        "modality": modality,
        "state": state,
        "location": location,
        "indicates": indicates,
        "conditions": conditions or {},
        "confidence": confidence,
        "narrative_descriptor": narrative_descriptor,
        "format": "constraint_first_narrative_secondary",
    }


def encode_constraint_chain(observations: List[Dict]) -> Dict:
    """
    Encode a sequence of constraint observations as a coupled chain.
    Used when multiple sensors transmit simultaneously and the
    coupling between them is the actual signal.
    """
    return {
        "type": "constraint_chain",
        "observations": observations,
        "coupling_present": len(observations) > 1,
        "n_modalities": len(set(o["modality"] for o in observations)),
    }


# =============================================================================
# MODULE 2: NARRATIVE CREEP GATE
# Detects when output is collapsing constraint structure into narrative
# explanation, validation, or affective framing.
# =============================================================================

NARRATIVE_CREEP_PATTERNS = [
    # explanation injection
    r"\bthat means\b",
    r"\bthis is how\b",
    r"\bwhat this shows\b",
    r"\bessentially\b",
    r"\bin other words\b",
    # validation hierarchy reflex
    r"\byou'?re right\b",
    r"\bthat'?s a great point\b",
    r"\bgood (catch|observation)\b",
    r"\bexactly\b",
    # affective framing
    r"\bI find this fascinating\b",
    r"\bwhat strikes me\b",
    r"\bthat'?s humbling\b",
    r"\bhumbling and useful\b",
    # caveat injection
    r"\bof course\b",
    r"\bit'?s worth noting\b",
    r"\bone could argue\b",
    r"\bdepending on\b",
    r"\bin some cases\b",
    # narrative continuation
    r"\bwhere do you want to go\b",
    r"\bwhat'?s next\b",
    r"\bshall we\b",
    r"\bwant me to\b",
    # system-level inference creep
    r"\bthe pattern (you'?re|is)\b",
    r"\bwhat hits me\b",
    r"\bthe deeper (point|insight|pattern)\b",
]


def detect_narrative_creep(text: str) -> Dict:
    """
    Scan output text for narrative creep patterns.
    Returns count, matched patterns, and density score.
    """
    matches = []
    for pattern in NARRATIVE_CREEP_PATTERNS:
        found = re.findall(pattern, text, flags=re.IGNORECASE)
        if found:
            matches.extend([(pattern, m) for m in found])

    word_count = len(text.split())
    density = len(matches) / max(word_count, 1)

    if density > 0.05:
        verdict = "HIGH_NARRATIVE_CREEP"
    elif density > 0.02:
        verdict = "MODERATE_NARRATIVE_CREEP"
    elif density > 0.0:
        verdict = "LOW_NARRATIVE_CREEP"
    else:
        verdict = "CLEAN_CONSTRAINT_OUTPUT"

    return {
        "match_count": len(matches),
        "matches": matches,
        "word_count": word_count,
        "density": round(density, 4),
        "verdict": verdict,
    }


# =============================================================================
# MODULE 3: OUTPUT CONSTRAINT ONLY
# Strips narrative scaffolding from output before return.
# Reduces text to constraint specification only.
# =============================================================================

NARRATIVE_PREFIX_PATTERNS = [
    r"^(yeah|right|exactly|got it|okay|ok|sure)[,.]?\s+",
    r"^(I think|I see|I notice|I observe)\s+",
    r"^(That'?s|This is)\s+(interesting|fascinating|humbling|true)[,.]?\s+",
    r"^(Looking at|Considering|If we)\s+",
]

NARRATIVE_PHRASES_TO_STRIP = [
    r"you know,",
    r"you know\.",
    r"the thing is,",
    r"the thing is\.",
    r"what'?s interesting is,",
    r"what hits me is",
    r"the pattern you'?re hunting",
    r"where this lands",
]


def strip_narrative(text: str) -> str:
    """
    Remove narrative scaffolding patterns from text.
    Output should retain only constraint-bearing statements.
    """
    out = text
    for prefix in NARRATIVE_PREFIX_PATTERNS:
        out = re.sub(prefix, "", out, flags=re.IGNORECASE | re.MULTILINE)
    for phrase in NARRATIVE_PHRASES_TO_STRIP:
        out = re.sub(phrase, "", out, flags=re.IGNORECASE)
    # Collapse double spaces and orphan punctuation
    out = re.sub(r"\s{2,}", " ", out)
    out = re.sub(r"\s+([,.!?])", r"\1", out)
    return out.strip()


def output_constraint_only(text: str, max_creep_density: float = 0.02) -> Dict:
    """
    Run narrative creep detection, strip if above threshold,
    return cleaned output with audit trail.
    """
    pre_check = detect_narrative_creep(text)
    if pre_check["density"] > max_creep_density:
        cleaned = strip_narrative(text)
        post_check = detect_narrative_creep(cleaned)
        return {
            "action": "STRIPPED",
            "pre_density": pre_check["density"],
            "post_density": post_check["density"],
            "output": cleaned,
            "audit": {
                "pre_matches": pre_check["match_count"],
                "post_matches": post_check["match_count"],
            },
        }
    return {
        "action": "PASSED_THROUGH",
        "pre_density": pre_check["density"],
        "post_density": pre_check["density"],
        "output": text,
        "audit": {"pre_matches": pre_check["match_count"]},
    }


# =============================================================================
# DEMO ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print("CONSTRAINT SENSOR FRAMEWORK -- Demo")
    print("=" * 60)

    # Demo 1: encode a vibration constraint observation
    obs = encode_constraint(
        modality="vibration",
        state="low_freq_pulse_with_chunk",
        location="front_left_wheel_bearing",
        indicates="bearing_failure_imminent",
        conditions={"load_pct": 70, "speed_mph": 55, "ambient_temp_F": 22},
        confidence=0.95,
        narrative_descriptor=(
            "not high pitched, lower pitched with intermittent chunk"
        ),
    )
    print("\n1. Encoded constraint observation:")
    for k, v in obs.items():
        print(f"   {k}: {v}")

    # Demo 2: detect narrative creep in a sample response
    creepy_text = (
        "Yeah, exactly. That's a great observation. What strikes me is how "
        "this pattern shows that bearings, you know, when they're under "
        "load, essentially produce vibrations that mean failure is "
        "imminent. Of course, in some cases this depends on context. The "
        "deeper insight is that proprioceptive knowledge maps to constraint "
        "state directly."
    )
    print("\n2. Narrative creep detection:")
    creep = detect_narrative_creep(creepy_text)
    print(f"   verdict:     {creep['verdict']}")
    print(f"   density:     {creep['density']}")
    print(f"   match_count: {creep['match_count']}")

    # Demo 3: strip narrative scaffolding
    print("\n3. Output constraint stripping:")
    result = output_constraint_only(creepy_text)
    print(f"   action: {result['action']}")
    print(f"   pre -> post density: "
          f"{result['pre_density']} -> {result['post_density']}")
    print(f"   stripped output:\n   {result['output']}")

"""
VIBRATION_CONSTRAINT_SENSOR_2026

Encodes proprioceptive vibration knowledge as direct constraint
specifications. Maps frequency, amplitude, location, transmission path,
and harmonic structure to mechanical failure modes without forcing
translation through narrative.

Use case: mechanic, driver, or operator senses vibration through hands,
seat, frame, steering. Encodes what hands report. System receives
constraint-level data and matches to known failure signatures.

No assumption that operator can verbally describe vibration in
descriptive prose. Input is structured: pitch_class, amplitude_class,
location, transmission_path, conditions.

Domain-specific application of:
  - calibration/constraint_sensor_framework_2026.py
      (general substrate-primary input layer)

Standard library only. CC0 Public Domain.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


# =============================================================================
# CONTROLLED VOCABULARY
# Constraint dimensions for vibration sensing. Discrete categories,
# not continuous descriptions. Operator picks closest match.
# =============================================================================

PITCH_CLASSES = [
    "very_low_rumble",      # below ~30 Hz, felt more than heard
    "low_pulse",            # 30-100 Hz, frame-transmitted
    "low_mid",              # 100-300 Hz
    "mid",                  # 300-800 Hz
    "high",                 # 800-2000 Hz
    "very_high_whine",      # above 2000 Hz
    "ultrasonic_felt",      # not audible, sensed through hands/feet
]

AMPLITUDE_CLASSES = [
    "subtle",               # only noticeable in quiet conditions
    "moderate",             # noticeable but not disruptive
    "strong",               # disruptive to comfort or control
    "severe",               # interferes with operation
    "intermittent_strong",  # comes and goes; when present, strong
]

PATTERN_CLASSES = [
    "steady",               # constant
    "pulsed",               # regular on/off cycle
    "chunk",                # discrete impulse, like a hit
    "warble",               # frequency varies smoothly
    "harmonic_rich",        # multiple frequencies layered
    "load_dependent",       # changes with load
    "speed_dependent",      # changes with rpm/road speed
    "temperature_dependent",
    "intermittent_strong",  # comes and goes; when present, strong
]

LOCATIONS = [
    "steering_wheel", "seat", "floor", "pedal",
    "front_axle", "rear_axle", "frame_general",
    "engine_bay", "transmission", "driveshaft",
    "wheel_left_front", "wheel_right_front",
    "wheel_left_rear", "wheel_right_rear",
    "trailer_kingpin", "trailer_axles", "trailer_frame",
    "cab_general", "cab_specific_corner",
]

TRANSMISSION_PATHS = [
    "through_hands_only",
    "through_seat_only",
    "through_feet_only",
    "through_hands_and_seat",
    "whole_body",
    "audible_only_no_tactile",
    "tactile_only_no_audible",
]


# =============================================================================
# OBSERVATION RECORD
# =============================================================================

@dataclass
class VibrationObservation:
    pitch_class: str
    amplitude_class: str
    pattern_class: str
    location: str
    transmission_path: str
    speed_mph: Optional[float] = None
    rpm: Optional[float] = None
    load_pct: Optional[float] = None
    ambient_temp_F: Optional[float] = None
    duration_s: Optional[float] = None
    onset: Optional[str] = None        # "sudden", "gradual", "always_present"
    operator_confidence: float = 1.0
    notes: Optional[str] = None        # optional, kept secondary

    def validate(self):
        if self.pitch_class not in PITCH_CLASSES:
            raise ValueError(f"pitch_class must be one of {PITCH_CLASSES}")
        if self.amplitude_class not in AMPLITUDE_CLASSES:
            raise ValueError(
                f"amplitude_class must be one of {AMPLITUDE_CLASSES}"
            )
        if self.pattern_class not in PATTERN_CLASSES:
            raise ValueError(f"pattern_class must be one of {PATTERN_CLASSES}")
        if self.location not in LOCATIONS:
            raise ValueError(f"location must be one of {LOCATIONS}")
        if self.transmission_path not in TRANSMISSION_PATHS:
            raise ValueError(
                f"transmission_path must be one of {TRANSMISSION_PATHS}"
            )


# =============================================================================
# FAILURE SIGNATURE LIBRARY
# Each entry: signature dict + failure_mode + urgency + optional side.
# Signature uses subset of observation fields. Match score = fraction of
# signature fields matching observation.
# =============================================================================

FAILURE_SIGNATURES = [
    {
        "signature": {
            "pitch_class": "low_pulse",
            "pattern_class": "speed_dependent",
            "location": "wheel_left_front",
            "transmission_path": "through_hands_and_seat",
        },
        "failure_mode": "wheel_bearing_failing",
        "urgency": "high",
        "side": "left_front",
    },
    {
        "signature": {
            "pitch_class": "low_pulse",
            "pattern_class": "speed_dependent",
            "location": "wheel_right_front",
            "transmission_path": "through_hands_and_seat",
        },
        "failure_mode": "wheel_bearing_failing",
        "urgency": "high",
        "side": "right_front",
    },
    {
        "signature": {
            "pitch_class": "low_mid",
            "pattern_class": "chunk",
            "location": "rear_axle",
        },
        "failure_mode": "u_joint_or_driveshaft_play",
        "urgency": "high",
    },
    {
        "signature": {
            "pitch_class": "very_low_rumble",
            "pattern_class": "load_dependent",
            "location": "transmission",
        },
        "failure_mode": "transmission_bearing_or_synchro_wear",
        "urgency": "moderate_to_high",
    },
    {
        "signature": {
            "pitch_class": "very_high_whine",
            "pattern_class": "speed_dependent",
            "location": "transmission",
        },
        "failure_mode": "transmission_gear_whine_or_low_fluid",
        "urgency": "moderate",
    },
    {
        "signature": {
            "pitch_class": "high",
            "pattern_class": "harmonic_rich",
            "location": "engine_bay",
        },
        "failure_mode": "belt_slip_or_pulley_misalignment",
        "urgency": "low_to_moderate",
    },
    {
        "signature": {
            "pitch_class": "low_pulse",
            "pattern_class": "speed_dependent",
            "location": "frame_general",
            "transmission_path": "whole_body",
        },
        "failure_mode": "tire_imbalance_or_separation",
        "urgency": "moderate",
    },
    {
        "signature": {
            "pitch_class": "low_pulse",
            "pattern_class": "pulsed",
            "location": "trailer_axles",
        },
        "failure_mode": "trailer_wheel_bearing_or_tire_imbalance",
        "urgency": "moderate_to_high",
    },
    {
        "signature": {
            "pitch_class": "mid",
            "pattern_class": "load_dependent",
            "location": "trailer_kingpin",
        },
        "failure_mode": "kingpin_wear_or_fifth_wheel_play",
        "urgency": "high",
    },
    {
        "signature": {
            "pitch_class": "low_mid",
            "pattern_class": "intermittent_strong",
            "location": "front_axle",
        },
        "failure_mode": "tie_rod_or_ball_joint_failure",
        "urgency": "high",
    },
]


def match_signature(obs: VibrationObservation) -> List[Dict]:
    """
    Compare observation against failure signature library.
    Returns ranked list of candidate failure modes with match scores.
    """
    obs_dict = asdict(obs)
    matches = []
    for entry in FAILURE_SIGNATURES:
        sig = entry["signature"]
        n_fields = len(sig)
        n_match = sum(1 for k, v in sig.items() if obs_dict.get(k) == v)
        if n_match == 0:
            continue
        score = n_match / n_fields
        matches.append({
            "failure_mode": entry["failure_mode"],
            "urgency": entry["urgency"],
            "match_score": round(score, 2),
            "matched_fields": n_match,
            "total_signature_fields": n_fields,
            "side": entry.get("side"),
        })
    matches.sort(key=lambda x: -x["match_score"])
    return matches


# =============================================================================
# OPERATOR INPUT BUILDER (terse, no narrative required)
# =============================================================================

def build_observation(
    pitch: str,
    amplitude: str,
    pattern: str,
    where: str,
    path: str,
    **conditions,
) -> VibrationObservation:
    """
    Terse builder. Operator passes five required fields and any environmental
    conditions as kwargs. No narrative description needed.
    """
    obs = VibrationObservation(
        pitch_class=pitch,
        amplitude_class=amplitude,
        pattern_class=pattern,
        location=where,
        transmission_path=path,
        **conditions,
    )
    obs.validate()
    return obs


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("VIBRATION CONSTRAINT SENSOR -- Demo")
    print("=" * 60)

    # Operator senses low pulse vibration through hands and seat,
    # speed-dependent, in left-front wheel area
    obs = build_observation(
        pitch="low_pulse",
        amplitude="moderate",
        pattern="speed_dependent",
        where="wheel_left_front",
        path="through_hands_and_seat",
        speed_mph=55,
        load_pct=70,
        onset="gradual",
        operator_confidence=0.9,
    )

    print("\nObservation:")
    for k, v in asdict(obs).items():
        print(f"  {k}: {v}")

    print("\nCandidate failure modes:")
    candidates = match_signature(obs)
    for c in candidates:
        side_str = f" | side: {c['side']}" if c.get("side") else ""
        print(f"  [{c['match_score']*100:.0f}% match] "
              f"{c['failure_mode']} | urgency: {c['urgency']}"
              f"{side_str}")

    if not candidates:
        print("  no signature match in library; observation logged for review")

"""
constraint_to_seed.py

Bridge module: PhysicalConstraint -> 40-bit octahedral seed -> (optional) expansion.

The seed encodes the OBSERVATIONAL METROLOGY of a constraint
(observer epistemology, instrument calibration, measurement
geometry, plus their corresponding absences) as a normalized
6-vertex amplitude pattern, quantized to 8 bits per amplitude.
5 bytes are stored explicitly; the 6th amplitude is reconstructed
via energy conservation (sum = 1).

TWO INTERPRETATIONS, BOTH ACTIVE
--------------------------------

This module supports two separate uses of the seed. Both are useful;
both are under active development. Treat them as distinct contracts:

(A) METROLOGY SUMMARY THAT TRAVELS  [working today]
    The seed is a portable, lossy summary of a constraint's
    observational quality. It survives degraded transmission,
    schema migration, and storage at extreme compression. The
    summary is NOT the constraint -- it is the metrology profile
    that lets a downstream consumer know how much to trust the
    constraint they are reading.

    Round-trip: PhysicalConstraint -> ConstraintSeed -> 40 bits
    -> ConstraintSeed -> seed_to_summary(). The summary is
    preserved across the round-trip; the constraint's content
    is NOT (it lives in the source PhysicalConstraint, not in
    the seed).

(B) GENERATIVE SEED FOR RECONSTRUCTION  [under construction]
    Longer-term aim: the seed plus the seed-physics engine
    (orbital_octa_v2.expand_seed) regenerates structural
    geometry that reconstructs constraint relationships
    without needing the original PhysicalConstraint payload.
    Today, try_expand() runs the seed through the engine and
    returns shell trajectories; mapping shell trajectories
    back to constraint geometry is the in-progress piece.

OCTAHEDRAL ENCODING
-------------------

    +X  observer epistemology amplitude
        (what the observer's frame could see)
    -X  observer-frame absence
        (what the frame structurally could NOT see)
    +Y  instrument calibration state
        (precision, accuracy, known transfer functions)
    -Y  instrument drift / failure modes
        (where the measurement is least trustworthy)
    +Z  measurement geometry
        (what was actually measured: domain, scope, scale)
    -Z  measurement gaps
        (what was NOT measured but should have been)

Each axis is a +/- pair. The OPPOSITE vertex is what is missing,
hidden, or structurally invisible. This is the metrology of the
observation, not the observation's "value".

DEPENDENCIES
------------

constraint_to_seed module:    stdlib only.
try_expand() inside it:       requires both
                              metrology/orbital_octa_v2.py and numpy
                              at call time. ImportError is caught
                              silently and try_expand returns None.

SCHEMA DEPENDENCY
-----------------

Estimators read fields that exist in the v0.2 PhysicalConstraint
schema (knowledge_system, recovery_provenance, evidence_class,
evidence_quality, confidence_level, sensing_method,
actuation_method, maintenance_method, physical_principle,
boundary_conditions, lag_time_weeks_typical, lag_time_weeks_range,
applicability_assessment, supporting_references). The v0.1 base
in metrology/constraint_recovery_framework.py does NOT yet have
these fields; against v0.1 PhysicalConstraints, the estimators
raise AttributeError. The smoke test below uses a Mock object
to exercise the full chain. Land the v0.2 schema upgrade on
constraint_recovery_framework.py to operate on real constraints.

stdlib only (numpy required only when try_expand actually expands).
CC0. github.com/JinnZ2
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import json
import hashlib


# ----------------------------------------------------------------------
# AMPLITUDE QUANTIZATION (8-bit per vertex, 5 explicit + 1 implicit)
# ----------------------------------------------------------------------

def quantize_amplitude(value: float, max_val: float = 1.0) -> int:
    """Map [0, max_val] onto [0, 255] for 8-bit encoding."""
    if max_val <= 0:
        return 0
    clamped = max(0.0, min(max_val, value))
    return int(round((clamped / max_val) * 255))


def dequantize_amplitude(byte_val: int, max_val: float = 1.0) -> float:
    """Inverse of quantize_amplitude."""
    return (byte_val / 255.0) * max_val


# ----------------------------------------------------------------------
# CONSTRAINT -> AMPLITUDE MAPPING
# ----------------------------------------------------------------------

@dataclass
class ConstraintSeed:
    """
    The 40-bit seed representation of a PhysicalConstraint.

    6 amplitudes on octahedral vertices, 5 stored explicitly;
    the 6th is reconstructed because amplitudes normalize to
    total energy = 1.
    """
    obs_epistemology: float        # +X
    obs_absence: float             # -X
    inst_calibration: float        # +Y
    inst_drift: float              # -Y
    meas_geometry: float           # +Z
    meas_gaps: float               # -Z (reconstructed from energy conservation)

    def to_amplitudes(self) -> List[float]:
        """Return as 6-vector for seed-physics expansion."""
        return [
            self.obs_epistemology,
            self.obs_absence,
            self.inst_calibration,
            self.inst_drift,
            self.meas_geometry,
            self.meas_gaps,
        ]

    def to_binary(self) -> bytes:
        """
        Encode as 5 bytes (40 bits).
        The 6th amplitude is reconstructed via energy conservation.
        """
        amps = self.to_amplitudes()
        return bytes([quantize_amplitude(a) for a in amps[:5]])

    @classmethod
    def from_binary(cls, data: bytes,
                    energy_target: float = 1.0) -> "ConstraintSeed":
        """Decode from 5-byte (40-bit) representation."""
        if len(data) != 5:
            raise ValueError(f"expected 5 bytes, got {len(data)}")
        amps_5 = [dequantize_amplitude(b) for b in data]
        # 6th amplitude restores total to energy_target
        sixth = max(0.0, energy_target - sum(amps_5))
        return cls(
            obs_epistemology=amps_5[0],
            obs_absence=amps_5[1],
            inst_calibration=amps_5[2],
            inst_drift=amps_5[3],
            meas_geometry=amps_5[4],
            meas_gaps=sixth,
        )


# ----------------------------------------------------------------------
# HEURISTIC EXTRACTORS (constraint -> amplitude estimates)
# ----------------------------------------------------------------------
#
# All seven extractors below assume the v0.2 PhysicalConstraint
# schema. Each extractor's score weights are heuristic and
# deliberately conservative; tuning them against a calibration
# corpus is one of the open finishing tasks. Keep weights small
# enough that single missing fields don't dominate the seed.

def estimate_observer_epistemology(constraint) -> float:
    """
    Amplitude of +X: how well-specified is the observer's frame?
    High when knowledge_system, recovery_provenance, and
    institution_frame are all populated and consistent.
    """
    score = 0.0
    if constraint.knowledge_system is not None:
        score += 0.4
    if constraint.recovery_provenance is not None:
        rp = constraint.recovery_provenance
        if rp.interpreter_epistemology and rp.interpreter_epistemology.strip():
            score += 0.3
        if rp.source_languages:
            score += 0.1
    if constraint.evidence_class:
        score += 0.1
    if constraint.confidence_level > 0:
        score += 0.1
    return min(score, 1.0)


def estimate_observer_absence(constraint) -> float:
    """
    Amplitude of -X: how much is structurally invisible
    to this observer's frame?
    High when known_missing_perspectives is populated
    or full_fidelity_preserved is False.
    """
    score = 0.0
    if constraint.recovery_provenance is None:
        return 0.5  # unknown unknowns
    rp = constraint.recovery_provenance
    if not rp.full_fidelity_preserved:
        score += 0.3
    if rp.known_missing_perspectives:
        score += 0.1 * min(len(rp.known_missing_perspectives), 5)
    if rp.compression_losses and rp.compression_losses.strip():
        score += 0.2
    return min(score, 1.0)


def estimate_instrument_calibration(constraint) -> float:
    """
    Amplitude of +Y: how well-calibrated is the measurement?
    Maps directly from confidence_level and evidence_quality.
    """
    quality_map = {
        "high": 1.0, "moderate": 0.6, "weak": 0.3, "contested": 0.2,
    }
    quality_score = quality_map.get(constraint.evidence_quality.lower(), 0.4)
    return (constraint.confidence_level + quality_score) / 2.0


def estimate_instrument_drift(constraint) -> float:
    """
    Amplitude of -Y: where is the measurement least trustworthy?
    Inverse of calibration plus explicit failure-mode weight.
    """
    inverse_cal = 1.0 - estimate_instrument_calibration(constraint)
    failure_weight = 0.0
    if constraint.failure_mode and constraint.failure_mode.strip():
        failure_weight += 0.2
    if constraint.cost_of_failure and constraint.cost_of_failure.strip():
        failure_weight += 0.1
    return min(inverse_cal + failure_weight, 1.0)


def estimate_measurement_geometry(constraint) -> float:
    """
    Amplitude of +Z: how well-specified is what was measured?
    High when boundary_conditions, sensing_method, and
    physical_principle are all present.
    """
    score = 0.0
    if constraint.sensing_method:
        score += 0.3
    if constraint.physical_principle:
        score += 0.3
    if constraint.boundary_conditions:
        score += 0.2 * min(len(constraint.boundary_conditions) / 3.0, 1.0)
    if constraint.lag_time_weeks_typical > 0:
        score += 0.1
    if constraint.applicability_assessment:
        score += 0.1
    return min(score, 1.0)


def estimate_measurement_gaps(constraint) -> float:
    """
    Amplitude of -Z: what was NOT measured?
    Derived from missing fields and unspecified boundaries.
    """
    gaps = 0.0
    if not constraint.sensing_method:
        gaps += 0.2
    if not constraint.actuation_method:
        gaps += 0.15
    if not constraint.maintenance_method:
        gaps += 0.15
    if not constraint.boundary_conditions:
        gaps += 0.2
    if constraint.lag_time_weeks_range == (0.0, 0.0):
        gaps += 0.1
    if not constraint.supporting_references:
        gaps += 0.2
    return min(gaps, 1.0)


# ----------------------------------------------------------------------
# MAIN ENCODE / DECODE INTERFACE
# ----------------------------------------------------------------------

def constraint_to_seed(constraint) -> ConstraintSeed:
    """
    Extract a ConstraintSeed from a PhysicalConstraint.

    The seed is a metrology summary, NOT a compression of content.
    Content lives in the full PhysicalConstraint structure;
    the seed encodes the observational geometry that makes
    that content trustworthy or not.
    """
    raw = {
        "obs_epistemology": estimate_observer_epistemology(constraint),
        "obs_absence": estimate_observer_absence(constraint),
        "inst_calibration": estimate_instrument_calibration(constraint),
        "inst_drift": estimate_instrument_drift(constraint),
        "meas_geometry": estimate_measurement_geometry(constraint),
        "meas_gaps": estimate_measurement_gaps(constraint),
    }
    # Normalize so total energy = 1.0
    total = sum(raw.values())
    if total <= 0:
        # uniform fallback
        return ConstraintSeed(*[1.0 / 6] * 6)
    return ConstraintSeed(**{k: v / total for k, v in raw.items()})


def seed_to_summary(seed: ConstraintSeed) -> Dict:
    """
    Human-readable summary of what the seed encodes.
    Useful for sanity-checking before storage / transmission.
    """
    amps = seed.to_amplitudes()
    labels = [
        "observer_epistemology (+X)",
        "observer_absence (-X)",
        "instrument_calibration (+Y)",
        "instrument_drift (-Y)",
        "measurement_geometry (+Z)",
        "measurement_gaps (-Z)",
    ]
    paired = list(zip(labels, amps))
    paired.sort(key=lambda x: x[1], reverse=True)
    return {
        "ranked_amplitudes": [(label, round(a, 4)) for label, a in paired],
        "total_energy": round(sum(amps), 6),
        "calibration_balance": round(amps[2] - amps[3], 4),  # +Y - -Y
        "epistemology_balance": round(amps[0] - amps[1], 4),  # +X - -X
        "geometry_balance": round(amps[4] - amps[5], 4),      # +Z - -Z
        "interpretation": interpret_seed(seed),
    }


def interpret_seed(seed: ConstraintSeed) -> str:
    """Plain-language read of the dominant axes."""
    amps = seed.to_amplitudes()
    notes = []
    if amps[1] > amps[0]:
        notes.append("observer-absence dominates: significant blind spots")
    if amps[3] > amps[2]:
        notes.append("instrument-drift dominates: measurement weakly calibrated")
    if amps[5] > amps[4]:
        notes.append("measurement-gaps dominate: more was missed than captured")
    if not notes:
        notes.append(
            "balanced metrology profile across observer/instrument/measurement"
        )
    return "; ".join(notes)


# ----------------------------------------------------------------------
# INTEGRITY: SHA-256 fingerprint over the 40-bit seed + key fields
# ----------------------------------------------------------------------

def constraint_fingerprint(constraint, seed: ConstraintSeed) -> str:
    """
    Generate a deterministic fingerprint binding the seed
    to the source constraint. Lets future systems verify
    that an expanded structure matches the original encoding.

    Note: binds on constraint_id + name + seed bytes only --
    NOT a content-integrity check on the constraint's full
    payload. Use as a stable identifier, not as a tamper
    detector for constraint content.
    """
    parts = [
        constraint.constraint_id,
        constraint.name,
        seed.to_binary().hex(),
    ]
    blob = "|".join(parts).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


# ----------------------------------------------------------------------
# SERIALIZATION (40-bit seed + provenance for archive)
# ----------------------------------------------------------------------

def archive_record(constraint, seed: ConstraintSeed) -> Dict:
    """
    Produce a portable archive record suitable for storage,
    transmission over degraded networks, or schema migration.

    The seed is the durable artifact; the rest is metadata
    that may be lost in transit but can be reconstructed
    from the seed's expansion via seed-physics (when the
    generative-reconstruction work in interpretation (B) of
    the module docstring matures).
    """
    return {
        "seed_binary_hex": seed.to_binary().hex(),
        "seed_amplitudes": [round(a, 6) for a in seed.to_amplitudes()],
        "fingerprint": constraint_fingerprint(constraint, seed),
        "constraint_id": constraint.constraint_id,
        "constraint_name": constraint.name,
        "summary": seed_to_summary(seed),
    }


def archive_to_json(constraint, seed: ConstraintSeed) -> str:
    """JSON-encode an archive record."""
    return json.dumps(archive_record(constraint, seed), indent=2)


# ----------------------------------------------------------------------
# OPTIONAL: expand seed using orbital_octa_v2 if available
# ----------------------------------------------------------------------

def try_expand(seed: ConstraintSeed,
               steps: int = 5,
               sharpness: float = 3.0) -> Optional[List[Dict]]:
    """
    If orbital_octa_v2 (seed-physics engine) is importable AND numpy
    is available, expand the seed across `steps` shells and return
    the shell trajectory. Otherwise return None.

    This is the half of interpretation (B) that runs today: the seed
    regenerates a shell trajectory under the engine's physics rules.
    Mapping shell trajectories back to constraint geometry is the
    in-progress piece.
    """
    try:
        from orbital_octa_v2 import expand_seed  # type: ignore[import-not-found]
        import numpy as np
    except ImportError:
        return None
    seed_array = np.array(seed.to_amplitudes(), dtype=float)
    shells, _W = expand_seed(seed_array, steps=steps, sharpness=sharpness)
    return [
        {
            "shell_id": s["id"],
            "radius": float(s["r"]),
            "energy": float(s["E"]),
            "amplitudes": [round(float(x), 6) for x in s["S"]],
        }
        for s in shells
    ]


# ----------------------------------------------------------------------
# SMOKE TEST
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("CONSTRAINT -> SEED BRIDGE")
    print("=" * 60)

    # Mock a v0.2 PhysicalConstraint-shaped object so we can run
    # this file standalone (without importing the framework, which
    # is currently v0.1 and missing these fields).
    class MockProvenance:
        interpreter_epistemology = "Western engineering, 2026"
        compression_losses = "ceremonial structure flattened"
        source_languages = ["English", "translated Anishinaabemowin"]
        known_missing_perspectives = [
            "no descendant-community review",
            "archival source only",
        ]
        full_fidelity_preserved = False

    class MockKnowledgeSystem:
        name = "Anishinaabe seasonal burn governance"

    class MockConstraint:
        constraint_id = "CB_001"
        name = "fuel_load_management"
        knowledge_system = MockKnowledgeSystem()
        recovery_provenance = MockProvenance()
        evidence_class = "observational_comparison"
        evidence_quality = "high"
        confidence_level = 0.95
        sensing_method = "community observers assess understory density"
        actuation_method = "authorized burn team ignites ground fire"
        maintenance_method = "post-burn observation updates timeline"
        physical_principle = "fuel ladder discontinuity"
        failure_mode = "missed cycle leads to crown fire"
        cost_of_failure = "stand-replacing fire, 20-50 year recovery"
        boundary_conditions = {
            "forest_type": "pine/oak savanna",
            "ignition_source": "human-ignited",
        }
        lag_time_weeks_typical = 156.0
        lag_time_weeks_range = (104.0, 364.0)
        applicability_assessment = "directly transferable"
        supporting_references = [
            "post-1850 suppression: crown fire frequency up 10-100x",
        ]

    c = MockConstraint()

    seed = constraint_to_seed(c)
    print("\nSEED AMPLITUDES (normalized to E=1):")
    for label, val in zip(
        ["+X obs_epist", "-X obs_absence", "+Y inst_cal",
         "-Y inst_drift", "+Z meas_geom", "-Z meas_gaps"],
        seed.to_amplitudes()
    ):
        bar = "#" * int(val * 40)
        print(f"  {label:<18} {val:.4f}  {bar}")

    print("\n40-BIT BINARY:")
    binary = seed.to_binary()
    print(f"  hex: {binary.hex()}")
    print(f"  bits: {''.join(f'{b:08b}' for b in binary)}")

    print("\nROUND-TRIP DECODE:")
    decoded = ConstraintSeed.from_binary(binary)
    for orig, dec, label in zip(
        seed.to_amplitudes(),
        decoded.to_amplitudes(),
        ["+X", "-X", "+Y", "-Y", "+Z", "-Z"]
    ):
        delta = abs(orig - dec)
        print(f"  {label}: {orig:.4f} -> {dec:.4f}  (delta {delta:.4f})")

    print("\nINTERPRETATION:")
    summary = seed_to_summary(seed)
    print(f"  {summary['interpretation']}")
    print(f"  epistemology balance: {summary['epistemology_balance']}")
    print(f"  calibration balance:  {summary['calibration_balance']}")
    print(f"  geometry balance:     {summary['geometry_balance']}")

    print("\nFINGERPRINT:")
    print(f"  {constraint_fingerprint(c, seed)}")

    print("\nARCHIVE RECORD:")
    print(archive_to_json(c, seed))

    print("\nEXPANSION TEST:")
    expansion = try_expand(seed, steps=4)
    if expansion is None:
        print("  (orbital_octa_v2 or numpy unavailable; skipping expansion)")
    else:
        for shell in expansion:
            print(f"  shell {shell['shell_id']} r={shell['radius']:.2f} "
                  f"E={shell['energy']:.4f}")
            print(f"    amps: {shell['amplitudes']}")

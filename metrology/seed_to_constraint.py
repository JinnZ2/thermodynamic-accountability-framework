"""
seed_to_constraint.py

Reconstruction decoder. Takes a 40-bit ConstraintSeed (or its binary
form), expands it under physics rules, recovers the metrology profile,
and produces a PhysicalConstraint stub.

THE KEY INSIGHT
---------------

The seed does NOT store the full constraint.
It stores the METROLOGY of the constraint.

Reconstruction recovers:
    - was this observation well-calibrated?       (+Y vs -Y)
    - was the observer's frame complete?          (+X vs -X)
    - was the measurement geometry specified?     (+Z vs -Z)
    - what was the integrity fingerprint?

Reconstruction does NOT recover:
    - the actual problem statement (narrative content)
    - the actual mechanism description
    - the actual references

Those live in the full PhysicalConstraint structure, which is stored
separately. The seed is the durable metrology fingerprint that
survives migration; content gets re-attached when the full record
is located, with the fingerprint as the integrity check.

    seed             = the observation's metrology signature (always survives)
    full constraint  = narrative content (can be lost, reformatted, rewritten)

If content is lost but the seed survives, the reconstructor knows:
    - the metrology of what existed
    - whether to trust any narrative reconstruction offered
    - the fingerprint to verify against

This module duplicates the shell-expansion algorithm in pure stdlib
so the soul-recovery path runs in numpy-free environments. The
numpy-using engine in metrology/orbital_octa_v2.py remains the
reference implementation; this file matches its semantics.

stdlib only. CC0. github.com/JinnZ2
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import hashlib


# ----------------------------------------------------------------------
# RECONSTRUCTED-PROFILE DATACLASSES
# ----------------------------------------------------------------------

@dataclass
class AxisReading:
    """One axis pair (e.g. +X / -X) with derived metrology read."""
    positive_label: str         # e.g. "observer_epistemology"
    negative_label: str         # e.g. "observer_absence"
    positive_amp: float
    negative_amp: float
    balance: float              # positive - negative
    interpretation: str         # plain-language read of the balance


@dataclass
class MetrologyProfile:
    """
    Recovered metrology profile from an expanded seed.
    All this can be reconstructed from the 40-bit seed alone.
    """
    epistemology: AxisReading           # +X / -X
    calibration: AxisReading            # +Y / -Y
    geometry: AxisReading               # +Z / -Z
    overall_quality: str                # "high", "moderate", "weak", "contested"
    overall_confidence: float           # estimate in [0, 1]
    notes: List[str] = field(default_factory=list)


@dataclass
class ConstraintStub:
    """
    Reconstructed PhysicalConstraint stub.

    Fields the seed CAN reconstruct are populated.
    Fields the seed CANNOT reconstruct are marked None
    with an entry in `unrecoverable_fields`.
    """
    constraint_id: Optional[str] = None
    name: Optional[str] = None
    confidence_level: Optional[float] = None
    evidence_quality: Optional[str] = None

    # Metrology presence flags (boolean reconstructions)
    has_observer_epistemology: bool = False
    has_observer_absence_record: bool = False
    has_instrument_calibration: bool = False
    has_instrument_drift_record: bool = False
    has_measurement_geometry: bool = False
    has_measurement_gaps_record: bool = False

    # Bookkeeping
    fingerprint_provided: Optional[str] = None
    fingerprint_match: Optional[bool] = None
    metrology_profile: Optional[MetrologyProfile] = None
    expansion_shells: int = 0
    unrecoverable_fields: List[str] = field(default_factory=list)


# ----------------------------------------------------------------------
# AXIS INTERPRETATION HEURISTICS
# ----------------------------------------------------------------------

def _interpret_balance(positive_amp: float, negative_amp: float,
                       positive_label: str, negative_label: str) -> str:
    """Plain-language read of one axis pair."""
    delta = positive_amp - negative_amp
    if abs(delta) < 0.05:
        return f"balanced: {positive_label} and {negative_label} comparable"
    if delta > 0.2:
        return f"strong {positive_label}; minor {negative_label}"
    if delta > 0:
        return f"moderate {positive_label}; some {negative_label}"
    if delta > -0.2:
        return f"moderate {negative_label}; some {positive_label}"
    return f"strong {negative_label}; weak {positive_label}"


def _quality_from_calibration(cal_amp: float, drift_amp: float) -> str:
    """Map +Y / -Y balance onto evidence_quality enum."""
    delta = cal_amp - drift_amp
    if delta >= 0.15:
        return "high"
    if delta >= 0.05:
        return "moderate"
    if delta >= -0.05:
        return "weak"
    return "contested"


def _confidence_from_axes(epist_pos: float, cal_pos: float,
                          geom_pos: float) -> float:
    """Combine three positive-axis amplitudes into a confidence estimate."""
    # weighted average with slight emphasis on calibration
    weighted = 0.3 * epist_pos + 0.4 * cal_pos + 0.3 * geom_pos
    # rescale: max amplitude on any single axis is ~0.33
    # multiply so a fully positive seed -> confidence near 1.0
    return min(1.0, weighted * 3.0)


# ----------------------------------------------------------------------
# SHELL EXPANSION (lightweight, dependency-free)
# ----------------------------------------------------------------------

def _build_influence_matrix() -> List[List[float]]:
    """
    Octahedral angular influence matrix.
    Pure-stdlib version of orbital_octa_v2.build_influence_matrix
    so this module runs without numpy / orbital_octa_v2 on path.
    """
    U = [
        (1, 0, 0), (-1, 0, 0),
        (0, 1, 0), (0, -1, 0),
        (0, 0, 1), (0, 0, -1),
    ]
    W = [[0.0] * 6 for _ in range(6)]
    for i in range(6):
        row_total = 0.0
        for j in range(6):
            dot = U[i][0] * U[j][0] + U[i][1] * U[j][1] + U[i][2] * U[j][2]
            w = max(0.0, dot)
            W[i][j] = w
            row_total += w
        if row_total > 0:
            for j in range(6):
                W[i][j] /= row_total
    return W


def _matvec(W: List[List[float]], v: List[float]) -> List[float]:
    """W @ v with pure stdlib."""
    out = [0.0] * 6
    for i in range(6):
        acc = 0.0
        for j in range(6):
            acc += W[i][j] * v[j]
        out[i] = acc
    return out


def _gaussian_envelope(r_shell: float, r_sample: float,
                       sigma_scale: float = 0.5) -> float:
    """Radial envelope with sigma proportional to shell radius."""
    sigma = sigma_scale * r_shell
    if sigma <= 0:
        return 0.0
    diff = r_sample - r_shell
    import math
    return math.exp(-(diff * diff) / (2.0 * sigma * sigma))


def _normalize_energy(v: List[float], E: float) -> List[float]:
    """Clamp non-negative, scale so sum equals E."""
    clamped = [max(0.0, x) for x in v]
    total = sum(clamped)
    if total <= 1e-12:
        return [E / 6.0] * 6
    return [x * (E / total) for x in clamped]


def expand_amplitudes(seed_amps: List[float],
                      steps: int = 5,
                      r0: float = 1.0,
                      E0: float = 1.0,
                      rho: float = 1.5,
                      epsilon: float = 0.6,
                      sigma_scale: float = 0.5) -> List[Dict]:
    """
    Lightweight shell expansion. Returns trajectory of shells.
    No numpy dependency; matches orbital_octa_v2.expand_seed semantics.
    """
    W = _build_influence_matrix()
    shells: List[Dict] = [{
        "id": 0,
        "r": r0,
        "E": E0,
        "S": _normalize_energy(list(seed_amps), E0),
    }]
    for n in range(steps):
        r_new = rho * shells[-1]["r"]
        E_new = epsilon * shells[-1]["E"]
        # accumulate field at r_new from all inner shells
        field_vec = [0.0] * 6
        for sh in shells:
            if sh["r"] >= r_new:
                continue
            env = _gaussian_envelope(sh["r"], r_new, sigma_scale)
            scaled = [x * env for x in sh["S"]]
            contrib = _matvec(W, scaled)
            for i in range(6):
                field_vec[i] += contrib[i]
        S_new = _normalize_energy(field_vec, E_new)
        shells.append({
            "id": n + 1,
            "r": r_new,
            "E": E_new,
            "S": S_new,
        })
    return shells


# ----------------------------------------------------------------------
# BINARY DECODE (matches constraint_to_seed encoding)
# ----------------------------------------------------------------------

def decode_seed_binary(data: bytes,
                       energy_target: float = 1.0) -> List[float]:
    """
    Reconstruct 6 amplitudes from 5-byte (40-bit) seed.
    Sixth amplitude restores total to energy_target.
    """
    if len(data) != 5:
        raise ValueError(f"expected 5 bytes, got {len(data)}")
    amps = [b / 255.0 for b in data]
    sixth = max(0.0, energy_target - sum(amps))
    amps.append(sixth)
    # renormalize against quantization drift
    total = sum(amps)
    if total > 0:
        amps = [a / total * energy_target for a in amps]
    return amps


# ----------------------------------------------------------------------
# SHELLS -> METROLOGY PROFILE
# ----------------------------------------------------------------------

def shells_to_metrology_profile(shells: List[Dict]) -> MetrologyProfile:
    """
    Read the expanded shell trajectory and recover the metrology
    signature. Uses the seed (shell 0) for the dominant reading
    and the trajectory for stability checks.
    """
    seed = shells[0]["S"]
    pos_x, neg_x = seed[0], seed[1]
    pos_y, neg_y = seed[2], seed[3]
    pos_z, neg_z = seed[4], seed[5]

    epistemology = AxisReading(
        positive_label="observer_epistemology",
        negative_label="observer_absence",
        positive_amp=pos_x,
        negative_amp=neg_x,
        balance=pos_x - neg_x,
        interpretation=_interpret_balance(
            pos_x, neg_x, "observer_epistemology", "observer_absence"
        ),
    )
    calibration = AxisReading(
        positive_label="instrument_calibration",
        negative_label="instrument_drift",
        positive_amp=pos_y,
        negative_amp=neg_y,
        balance=pos_y - neg_y,
        interpretation=_interpret_balance(
            pos_y, neg_y, "instrument_calibration", "instrument_drift"
        ),
    )
    geometry = AxisReading(
        positive_label="measurement_geometry",
        negative_label="measurement_gaps",
        positive_amp=pos_z,
        negative_amp=neg_z,
        balance=pos_z - neg_z,
        interpretation=_interpret_balance(
            pos_z, neg_z, "measurement_geometry", "measurement_gaps"
        ),
    )
    quality = _quality_from_calibration(pos_y, neg_y)
    confidence = _confidence_from_axes(pos_x, pos_y, pos_z)

    notes: List[str] = []
    if neg_x > pos_x:
        notes.append("observer-frame absence dominates: significant blind spots")
    if neg_y > pos_y:
        notes.append("instrument drift dominates: measurement weakly calibrated")
    if neg_z > pos_z:
        notes.append("measurement gaps dominate: more was missed than captured")
    # stability check across expansion
    if len(shells) > 1:
        last = shells[-1]["S"]
        last_total = sum(last)
        if last_total > 0:
            ratios = [last[i] / last_total for i in range(6)]
            seed_total = sum(seed)
            seed_ratios = [seed[i] / seed_total for i in range(6)]
            max_drift = max(abs(ratios[i] - seed_ratios[i]) for i in range(6))
            if max_drift > 0.05:
                notes.append(
                    f"proportional drift across {len(shells) - 1} shells: "
                    f"{round(max_drift, 4)}"
                )

    return MetrologyProfile(
        epistemology=epistemology,
        calibration=calibration,
        geometry=geometry,
        overall_quality=quality,
        overall_confidence=round(confidence, 4),
        notes=notes,
    )


# ----------------------------------------------------------------------
# METROLOGY PROFILE -> CONSTRAINT STUB
# ----------------------------------------------------------------------

# Threshold below which an axis is treated as "absent / not recorded"
PRESENCE_THRESHOLD = 0.05


def profile_to_stub(profile: MetrologyProfile,
                    constraint_id: Optional[str] = None,
                    name: Optional[str] = None,
                    fingerprint_provided: Optional[str] = None,
                    fingerprint_match: Optional[bool] = None,
                    expansion_shells: int = 0) -> ConstraintStub:
    """
    Produce a PhysicalConstraint stub from a recovered metrology profile.
    """
    stub = ConstraintStub(
        constraint_id=constraint_id,
        name=name,
        confidence_level=profile.overall_confidence,
        evidence_quality=profile.overall_quality,
        has_observer_epistemology=profile.epistemology.positive_amp >= PRESENCE_THRESHOLD,
        has_observer_absence_record=profile.epistemology.negative_amp >= PRESENCE_THRESHOLD,
        has_instrument_calibration=profile.calibration.positive_amp >= PRESENCE_THRESHOLD,
        has_instrument_drift_record=profile.calibration.negative_amp >= PRESENCE_THRESHOLD,
        has_measurement_geometry=profile.geometry.positive_amp >= PRESENCE_THRESHOLD,
        has_measurement_gaps_record=profile.geometry.negative_amp >= PRESENCE_THRESHOLD,
        fingerprint_provided=fingerprint_provided,
        fingerprint_match=fingerprint_match,
        metrology_profile=profile,
        expansion_shells=expansion_shells,
        unrecoverable_fields=[
            "physical_trigger",
            "problem_solved",
            "solution_mechanism",
            "sensing_method",
            "actuation_method",
            "transmission_method",
            "maintenance_method",
            "physical_principle",
            "lag_time_weeks_typical",
            "lag_time_weeks_range",
            "failure_mode",
            "cost_of_failure",
            "cost_metric_epoch",
            "evidence_class",
            "supporting_references",
            "depends_on",
            "enables",
            "knowledge_system",
            "boundary_conditions",
            "applicability_assessment",
            "recovery_provenance",
        ],
    )
    return stub


# ----------------------------------------------------------------------
# FINGERPRINT VERIFICATION
# ----------------------------------------------------------------------

def compute_fingerprint(constraint_id: str,
                        constraint_name: str,
                        seed_binary_hex: str) -> str:
    """
    Recompute the fingerprint to verify a stub against a claimed
    original. Matches the constraint_to_seed.constraint_fingerprint
    formula: sha256(id|name|hex)[:16].
    """
    parts = [constraint_id, constraint_name, seed_binary_hex]
    blob = "|".join(parts).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def verify_fingerprint(constraint_id: str,
                       constraint_name: str,
                       seed_binary_hex: str,
                       claimed_fingerprint: str) -> bool:
    return compute_fingerprint(
        constraint_id, constraint_name, seed_binary_hex
    ) == claimed_fingerprint


# ----------------------------------------------------------------------
# TOP-LEVEL RECONSTRUCTION ENTRY POINT
# ----------------------------------------------------------------------

def reconstruct_from_seed(seed_amplitudes: List[float],
                          steps: int = 5,
                          constraint_id: Optional[str] = None,
                          name: Optional[str] = None,
                          fingerprint_provided: Optional[str] = None,
                          claimed_seed_hex: Optional[str] = None) -> ConstraintStub:
    """
    Full reconstruction from raw 6-amplitude seed.
    """
    shells = expand_amplitudes(seed_amplitudes, steps=steps)
    profile = shells_to_metrology_profile(shells)
    fp_match: Optional[bool] = None
    if (fingerprint_provided is not None and
            constraint_id is not None and
            name is not None and
            claimed_seed_hex is not None):
        fp_match = verify_fingerprint(
            constraint_id, name, claimed_seed_hex, fingerprint_provided
        )
    return profile_to_stub(
        profile,
        constraint_id=constraint_id,
        name=name,
        fingerprint_provided=fingerprint_provided,
        fingerprint_match=fp_match,
        expansion_shells=len(shells),
    )


def reconstruct_from_archive_record(record: Dict,
                                    steps: int = 5) -> ConstraintStub:
    """
    Reconstruct from an archive_record dict (produced by
    constraint_to_seed.archive_record). Survives migration.
    """
    seed_hex = record.get("seed_binary_hex")
    if seed_hex is None:
        raise ValueError("archive record missing seed_binary_hex")
    seed_bytes = bytes.fromhex(seed_hex)
    amps = decode_seed_binary(seed_bytes)
    return reconstruct_from_seed(
        amps,
        steps=steps,
        constraint_id=record.get("constraint_id"),
        name=record.get("constraint_name"),
        fingerprint_provided=record.get("fingerprint"),
        claimed_seed_hex=seed_hex,
    )


# ----------------------------------------------------------------------
# SMOKE TEST
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("SEED -> CONSTRAINT RECONSTRUCTION")
    print("=" * 60)

    # Use the same fingerprint + seed produced by constraint_to_seed.py
    # smoke test on the Anishinaabe burn constraint.
    sample_archive = {
        "seed_binary_hex": "412d3f153d",
        "fingerprint": "341ac7282ca0e435",
        "constraint_id": "CB_001",
        "constraint_name": "fuel_load_management",
    }

    stub = reconstruct_from_archive_record(sample_archive, steps=5)

    print(f"\nconstraint_id:     {stub.constraint_id}")
    print(f"name:              {stub.name}")
    print(f"confidence_level:  {stub.confidence_level}")
    print(f"evidence_quality:  {stub.evidence_quality}")
    print(f"fingerprint match: {stub.fingerprint_match}")
    print(f"expansion shells:  {stub.expansion_shells}")

    print("\nMETROLOGY PRESENCE FLAGS:")
    print(f"  observer_epistemology:    {stub.has_observer_epistemology}")
    print(f"  observer_absence_record:  {stub.has_observer_absence_record}")
    print(f"  instrument_calibration:   {stub.has_instrument_calibration}")
    print(f"  instrument_drift_record:  {stub.has_instrument_drift_record}")
    print(f"  measurement_geometry:     {stub.has_measurement_geometry}")
    print(f"  measurement_gaps_record:  {stub.has_measurement_gaps_record}")

    print("\nMETROLOGY PROFILE:")
    p = stub.metrology_profile
    print(f"  +X/-X: {p.epistemology.interpretation}")
    print(f"          ({p.epistemology.positive_amp:.4f} vs "
          f"{p.epistemology.negative_amp:.4f})")
    print(f"  +Y/-Y: {p.calibration.interpretation}")
    print(f"          ({p.calibration.positive_amp:.4f} vs "
          f"{p.calibration.negative_amp:.4f})")
    print(f"  +Z/-Z: {p.geometry.interpretation}")
    print(f"          ({p.geometry.positive_amp:.4f} vs "
          f"{p.geometry.negative_amp:.4f})")
    print(f"  notes: {p.notes}")

    print(f"\nUNRECOVERABLE FIELDS ({len(stub.unrecoverable_fields)}):")
    for f in stub.unrecoverable_fields[:5]:
        print(f"  - {f}")
    print(f"  ... and {len(stub.unrecoverable_fields) - 5} more")

    print("\nNote: these fields require the full PhysicalConstraint")
    print("record. The seed survives migration; the narrative content")
    print("must be re-attached from a separate store, with the")
    print("fingerprint as integrity check.")

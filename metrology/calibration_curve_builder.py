"""
calibration_curve_builder.py

Build SurrogateCalibrationCurves from modern dual-stream data, then
apply them backward to recover legacy records.

Workflow:
    1. Collect dual-stream observations (modern era):
       - For each event, you have BOTH the surrogate measurement
         (e.g. newspaper severity adjective) AND the ground-truth
         measurement (e.g. NIFC acreage from satellite).
    2. Bin by surrogate value, compute mean + std of true value per bin.
    3. Output a SurrogateCalibrationCurve usable in the framework.
    4. Apply to legacy records (where only surrogate is available).

Built on metrological_audit_framework.py -- same package.
"""

from __future__ import annotations
import math
import statistics
from dataclasses import dataclass
from metrological_audit_framework import (
    SurrogateCalibrationCurve,
    MeasuredValue,
    CalibrationVectorEntry,
)


# =============================================================================
# DATA STRUCTURES FOR DUAL-STREAM OBSERVATIONS
# =============================================================================

@dataclass
class DualStreamObservation:
    """One event with both surrogate and true measurements."""
    event_id: str
    surrogate_value: float       # e.g. newspaper severity score, 1-5
    true_value: float            # e.g. acres burned (satellite-verified)
    weight: float = 1.0          # 0-1 confidence in this observation


# =============================================================================
# CURVE BUILDER
# =============================================================================

def build_curve_from_observations(
    obs: list[DualStreamObservation],
    surrogate_name: str,
    target_variable: str,
    surrogate_unit: str,
    target_unit: str,
    n_bins: int = 5,
    derivation_notes: str = "",
) -> SurrogateCalibrationCurve:
    """Construct a calibration curve from dual-stream observations.

    Method:
        1. Sort observations by surrogate value.
        2. Split into n_bins of equal count.
        3. For each bin, compute median true_value and std as uncertainty.
        4. Use bin centroids as breakpoints.

    Median (not mean) is used because legacy data is heavy-tailed
    (one Peshtigo Fire, many small ones). Median is robust to outliers
    and matches the central tendency a future analyst would care about.
    """
    if len(obs) < n_bins * 2:
        raise ValueError(
            f"Need at least {n_bins * 2} observations to build {n_bins}-bin curve; "
            f"got {len(obs)}"
        )

    obs_sorted = sorted(obs, key=lambda o: o.surrogate_value)
    bin_size = len(obs_sorted) // n_bins

    breakpoints: list[tuple[float, float, float]] = []
    for i in range(n_bins):
        lo = i * bin_size
        hi = (i + 1) * bin_size if i < n_bins - 1 else len(obs_sorted)
        bin_obs = obs_sorted[lo:hi]

        surrogate_centroid = statistics.median(o.surrogate_value for o in bin_obs)
        target_values = [o.true_value for o in bin_obs]
        target_centroid = statistics.median(target_values)
        target_uncertainty = (
            statistics.stdev(target_values) if len(target_values) >= 2 else math.inf
        )

        breakpoints.append((surrogate_centroid, target_centroid, target_uncertainty))

    return SurrogateCalibrationCurve(
        surrogate_name=surrogate_name,
        target_variable=target_variable,
        surrogate_unit=surrogate_unit,
        target_unit=target_unit,
        breakpoints=breakpoints,
        n_calibration_samples=len(obs),
        derivation_method=f"binned_median_{n_bins}_bins",
        derivation_notes=derivation_notes,
    )


# =============================================================================
# APPLY CURVE TO LEGACY RECORDS
# =============================================================================

def calibrate_legacy_entry(
    entry: CalibrationVectorEntry,
    surrogate_variable_name: str,
    curve: SurrogateCalibrationCurve,
    target_variable_name: str,
    target_era_name: str,
) -> CalibrationVectorEntry:
    """Read surrogate value from a legacy entry, apply curve, write
    target variable back into the same entry.

    Does not mutate the surrogate value -- keeps it intact alongside
    the derived calibrated estimate. The reader then has BOTH the
    raw surrogate and the calibrated estimate, with full provenance.
    """
    surrogate_mv = entry.get(surrogate_variable_name)
    if surrogate_mv is None or surrogate_mv.value is None:
        return entry  # nothing to calibrate

    target_value, target_uncertainty = curve.apply(surrogate_mv.value)

    calibrated_mv = MeasuredValue(
        value=target_value,
        unit=curve.target_unit,
        uncertainty=target_uncertainty,
        measurement_era_name=target_era_name,
        derivation_method="surrogate_calibrated",
        calibration_curve_applied=curve.surrogate_name,
        data_quality="legacy_reconstructed",
    )
    entry.set(target_variable_name, calibrated_mv)
    return entry


# =============================================================================
# DEMONSTRATION
# =============================================================================

if __name__ == "__main__":
    # Stub example: imagine we have 20 modern fires (2015-2024) where
    # we recorded BOTH a newspaper severity score AND the satellite-
    # verified acres burned. Build a curve from these 20 data points.

    # In real use, populate this from actual modern dual-stream data.
    # Each tuple is (severity_score_1to5, true_acres_burned).
    modern_dual_stream = [
        (1.0,    50),     (1.0,   120),
        (1.5,   400),     (1.5,   300),
        (2.0,  1500),     (2.0,  2200),
        (2.5,  4000),     (2.5,  6500),
        (3.0, 12000),     (3.0, 18000),
        (3.5, 30000),     (3.5, 42000),
        (4.0, 75000),     (4.0, 95000),
        (4.5, 180000),    (4.5, 220000),
        (5.0, 350000),    (5.0, 480000),
        (5.0, 600000),    (5.0, 850000),
    ]

    obs = [
        DualStreamObservation(
            event_id=f"demo_fire_{i}",
            surrogate_value=s,
            true_value=t,
        )
        for i, (s, t) in enumerate(modern_dual_stream)
    ]

    curve = build_curve_from_observations(
        obs,
        surrogate_name="newspaper_severity_adjective_modern",
        target_variable="acres_burned",
        surrogate_unit="severity_score_1to5",
        target_unit="acres",
        n_bins=5,
        derivation_notes=(
            "DEMO STUB: built from 20 hypothetical observations. "
            "Real curve must be derived from systematic NIFC + newspaper "
            "extraction over 2015-2024."
        ),
    )

    print("=" * 70)
    print("CALIBRATION CURVE BUILT")
    print("=" * 70)
    print(f"Surrogate: {curve.surrogate_name}")
    print(f"Target:    {curve.target_variable} ({curve.target_unit})")
    print(f"Samples:   {curve.n_calibration_samples}")
    print()
    print("Breakpoints (severity_score, median_acres, +/-uncertainty):")
    for s, t, u in curve.breakpoints:
        print(f"  severity={s:.2f}  ->  acres={t:>10.0f}  +/-  {u:>10.0f}")
    print()

    # Apply curve to a hypothetical 1894 Hinckley Fire entry
    print("APPLYING CURVE TO LEGACY RECORD:")
    print()
    hinckley = CalibrationVectorEntry(
        event_id="fire_us_18940901_hinckley_mn",
        domain="wildfire",
        timestamp="1894-09-01T14:00:00Z",
        timestamp_uncertainty_seconds=3600,
        location_lat=46.0125,
        location_lon=-92.9447,
        location_uncertainty_meters=5000,
    )
    # Newspaper accounts described it as catastrophic -- assign severity 5.0
    hinckley.set("newspaper_severity", MeasuredValue(
        value=5.0,
        unit="severity_score_1to5",
        uncertainty=0.5,
        measurement_era_name="newspaper_inquest_era_1850-1925",
        derivation_method="newspaper_archive",
        data_quality="legacy_reconstructed",
    ))

    hinckley = calibrate_legacy_entry(
        hinckley,
        surrogate_variable_name="newspaper_severity",
        curve=curve,
        target_variable_name="acres_burned",
        target_era_name="newspaper_inquest_era_1850-1925",
    )

    acres = hinckley.get("acres_burned")
    print("Hinckley 1894 estimated acres burned:")
    print(f"  {acres.value:,.0f} acres +/- {acres.uncertainty:,.0f}")
    print(f"  derivation: {acres.derivation_method}")
    print(f"  curve applied: {acres.calibration_curve_applied}")
    print(f"  quality: {acres.data_quality}")
    print()
    print("Historical estimates: 200,000+ acres.")
    print("Derived estimate is a PHYSICS-CONSISTENT reconstruction, not a fact.")
    print()
    print("=" * 70)
    print("PIPELINE READY. Real curves require real dual-stream data.")
    print("=" * 70)

"""
observer_bias_calibrator.py

Measure observer bias against ground-truth instruments in the
modern record, then apply the inverse correction to historical
records that lack ground-truth validation.

Core principle:
    Don't invalidate historical sources. Calibrate them.
    A newspaper from 1885 is not zero-information.
    It is biased-information with measurable bias structure.

Method:
    1. Modern era: pair observer reports with ground truth
       (radar, satellite, validated instrument).
    2. Compute bias signature per observer type.
       - magnitude bias (do they over/underestimate intensity?)
       - count bias (do they over/underreport events?)
       - location bias (which areas favored?)
       - temporal bias (which seasons favored?)
    3. Apply inverse bias to historical records of same type.
    4. Propagate uncertainty through the correction.

Output:
    Corrected historical estimates with explicit confidence intervals.

stdlib only. CC0. github.com/JinnZ2
"""

from dataclasses import dataclass, asdict
from enum import Enum
import math
import json


class ObserverType(Enum):
    NEWSPAPER = "newspaper"
    RADIO_REPORT = "radio_report"
    UNTRAINED_PUBLIC = "untrained_public"
    TRAINED_SPOTTER = "trained_spotter"
    MANUAL_INSTRUMENT = "manual_instrument"
    DOPPLER_RADAR = "doppler_radar"
    SATELLITE = "satellite"
    INDIGENOUS_INSTRUMENT = "indigenous_instrument"
    PROXY_PHYSICAL = "proxy_physical"  # tree fall, building damage


@dataclass
class CalibrationPair:
    """
    A single modern-era observation paired with ground-truth.
    Used to build the bias signature.
    """
    observer_type: ObserverType
    reported_count: int
    reported_magnitude: float       # e.g. EF rating, mph, mm
    truth_count: int
    truth_magnitude: float
    region: str = ""
    year: int = 0
    season: str = ""


@dataclass
class BiasSignature:
    """
    Characterization of how a given observer type deviates from
    ground truth. Built from many CalibrationPair samples.
    """
    observer_type: ObserverType

    count_factor: float = 1.0       # reported / truth
    count_factor_ci_low: float = 1.0
    count_factor_ci_high: float = 1.0

    magnitude_factor: float = 1.0
    magnitude_factor_ci_low: float = 1.0
    magnitude_factor_ci_high: float = 1.0

    sample_size: int = 0
    confidence: float = 0.0  # 0.0-1.0 based on sample size + spread

    notes: str = ""


# ----------------------------------------------------------------------
# BIAS CALCULATION
# ----------------------------------------------------------------------

def _mean(xs: list) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _stdev(xs: list) -> float:
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def _ci_95(xs: list) -> tuple:
    """Approximate 95% CI for the mean using normal approximation."""
    if not xs:
        return (1.0, 1.0)
    if len(xs) < 2:
        return (xs[0], xs[0])
    m = _mean(xs)
    s = _stdev(xs)
    margin = 1.96 * s / math.sqrt(len(xs))
    return (m - margin, m + margin)


def build_bias_signature(
    pairs: list,
    observer_type: ObserverType,
) -> BiasSignature:
    """
    Build a bias signature from calibration pairs of one observer type.
    """
    relevant = [p for p in pairs if p.observer_type == observer_type]
    if not relevant:
        return BiasSignature(
            observer_type=observer_type,
            confidence=0.0,
            notes="no calibration data",
        )

    count_factors = [
        p.reported_count / p.truth_count
        for p in relevant
        if p.truth_count > 0
    ]
    magnitude_factors = [
        p.reported_magnitude / p.truth_magnitude
        for p in relevant
        if p.truth_magnitude > 0
    ]

    cf_mean = _mean(count_factors) if count_factors else 1.0
    cf_low, cf_high = _ci_95(count_factors) if count_factors else (1.0, 1.0)

    mf_mean = _mean(magnitude_factors) if magnitude_factors else 1.0
    mf_low, mf_high = _ci_95(magnitude_factors) if magnitude_factors else (1.0, 1.0)

    # confidence scales with sample size (saturating at n=30)
    n = len(relevant)
    confidence = min(n / 30.0, 1.0)

    return BiasSignature(
        observer_type=observer_type,
        count_factor=round(cf_mean, 3),
        count_factor_ci_low=round(cf_low, 3),
        count_factor_ci_high=round(cf_high, 3),
        magnitude_factor=round(mf_mean, 3),
        magnitude_factor_ci_low=round(mf_low, 3),
        magnitude_factor_ci_high=round(mf_high, 3),
        sample_size=n,
        confidence=round(confidence, 3),
    )


# ----------------------------------------------------------------------
# HISTORICAL CORRECTION
# ----------------------------------------------------------------------

@dataclass
class HistoricalReport:
    """A historical observation lacking direct ground-truth."""
    observer_type: ObserverType
    reported_count: int
    reported_magnitude: float
    period: str
    region: str = ""


@dataclass
class CorrectedEstimate:
    """Bias-corrected estimate with explicit uncertainty."""
    period: str
    region: str
    observer_type: str

    estimated_count: float
    count_ci_low: float
    count_ci_high: float

    estimated_magnitude: float
    magnitude_ci_low: float
    magnitude_ci_high: float

    bias_signature_confidence: float
    note: str = ""


def correct_historical(
    report: HistoricalReport,
    signature: BiasSignature,
) -> CorrectedEstimate:
    """
    Apply inverse bias to a historical report.
    Result includes explicit confidence interval.
    """
    # only short-circuit if signature has zero information at all
    # (sample_size=0 AND confidence=0 means truly empty)
    if signature.sample_size == 0 and signature.confidence == 0.0:
        return CorrectedEstimate(
            period=report.period,
            region=report.region,
            observer_type=report.observer_type.value,
            estimated_count=float(report.reported_count),
            count_ci_low=float(report.reported_count),
            count_ci_high=float(report.reported_count),
            estimated_magnitude=report.reported_magnitude,
            magnitude_ci_low=report.reported_magnitude,
            magnitude_ci_high=report.reported_magnitude,
            bias_signature_confidence=0.0,
            note="no bias signature available; reported as-is",
        )

    # invert: truth = reported / factor
    est_count = report.reported_count / signature.count_factor
    # CI inverts: high factor -> low truth, low factor -> high truth
    count_low = report.reported_count / signature.count_factor_ci_high
    count_high = report.reported_count / signature.count_factor_ci_low

    est_mag = report.reported_magnitude / signature.magnitude_factor
    mag_low = report.reported_magnitude / signature.magnitude_factor_ci_high
    mag_high = report.reported_magnitude / signature.magnitude_factor_ci_low

    return CorrectedEstimate(
        period=report.period,
        region=report.region,
        observer_type=report.observer_type.value,
        estimated_count=round(est_count, 2),
        count_ci_low=round(count_low, 2),
        count_ci_high=round(count_high, 2),
        estimated_magnitude=round(est_mag, 2),
        magnitude_ci_low=round(mag_low, 2),
        magnitude_ci_high=round(mag_high, 2),
        bias_signature_confidence=signature.confidence,
        note=f"corrected using {signature.sample_size}-sample bias signature",
    )


# ----------------------------------------------------------------------
# REGISTRY OF KNOWN BIAS PRIORS
#
# Empirical defaults from published meta-analyses. Use only when
# direct calibration data is unavailable. Always prefer building
# a signature from real pairs.
# ----------------------------------------------------------------------

DEFAULT_PRIORS = {
    ObserverType.NEWSPAPER: {
        "count_factor": 0.45,        # newspapers historically miss ~55%
        "ci_low": 0.30,
        "ci_high": 0.65,
        "magnitude_factor": 1.25,    # but inflate the ones they catch
        "mag_ci_low": 1.10,
        "mag_ci_high": 1.45,
        "note": "Grazulis (1993) tornado climatology baseline",
    },
    ObserverType.UNTRAINED_PUBLIC: {
        "count_factor": 1.80,        # over-report (false positives)
        "ci_low": 1.40,
        "ci_high": 2.30,
        "magnitude_factor": 1.50,
        "mag_ci_low": 1.20,
        "mag_ci_high": 1.85,
        "note": "general overestimation in survey literature",
    },
    ObserverType.TRAINED_SPOTTER: {
        "count_factor": 1.05,
        "ci_low": 0.95,
        "ci_high": 1.15,
        "magnitude_factor": 1.02,
        "mag_ci_low": 0.92,
        "mag_ci_high": 1.12,
        "note": "SkyWarn-era validation studies",
    },
    ObserverType.RADIO_REPORT: {
        "count_factor": 0.75,
        "ci_low": 0.55,
        "ci_high": 0.95,
        "magnitude_factor": 1.10,
        "mag_ci_low": 0.95,
        "mag_ci_high": 1.30,
        "note": "rural radio reach limits + observer training mix",
    },
    ObserverType.MANUAL_INSTRUMENT: {
        "count_factor": 0.95,
        "ci_low": 0.85,
        "ci_high": 1.05,
        "magnitude_factor": 0.98,
        "mag_ci_low": 0.90,
        "mag_ci_high": 1.06,
        "note": "near ground-truth for what it can measure",
    },
    ObserverType.INDIGENOUS_INSTRUMENT: {
        "count_factor": 0.92,
        "ci_low": 0.80,
        "ci_high": 1.05,
        "magnitude_factor": 0.96,
        "mag_ci_low": 0.85,
        "mag_ci_high": 1.08,
        "note": (
            "validated where modern cross-checks exist; "
            "Western science gap is credential, not accuracy"
        ),
    },
    ObserverType.PROXY_PHYSICAL: {
        "count_factor": 0.70,        # only catches significant events
        "ci_low": 0.50,
        "ci_high": 0.90,
        "magnitude_factor": 1.00,    # damage scales with intensity
        "mag_ci_low": 0.85,
        "mag_ci_high": 1.15,
        "note": "tree fall, building damage records",
    },
}


def signature_from_prior(observer_type: ObserverType) -> BiasSignature:
    """Build a bias signature from published priors when no direct data exists."""
    if observer_type not in DEFAULT_PRIORS:
        return BiasSignature(observer_type=observer_type, notes="no prior available")

    p = DEFAULT_PRIORS[observer_type]
    return BiasSignature(
        observer_type=observer_type,
        count_factor=p["count_factor"],
        count_factor_ci_low=p["ci_low"],
        count_factor_ci_high=p["ci_high"],
        magnitude_factor=p["magnitude_factor"],
        magnitude_factor_ci_low=p["mag_ci_low"],
        magnitude_factor_ci_high=p["mag_ci_high"],
        sample_size=0,  # no direct sample, prior-based
        confidence=0.4,  # moderate confidence in published priors
        notes=f"prior-based: {p['note']}",
    )


# ----------------------------------------------------------------------
# DEMO
# ----------------------------------------------------------------------

if __name__ == "__main__":
    # Scenario: 1880s Wisconsin tornado newspaper reports
    # vs modern equivalent for calibration

    # Build calibration pairs from modern era (synthetic example)
    modern_pairs = [
        CalibrationPair(ObserverType.NEWSPAPER, 12, 2.5, 28, 2.0, "WI", 2015, "spring"),
        CalibrationPair(ObserverType.NEWSPAPER,  8, 3.0, 19, 2.3, "WI", 2018, "spring"),
        CalibrationPair(ObserverType.NEWSPAPER, 15, 2.8, 35, 2.1, "WI", 2020, "summer"),
        CalibrationPair(ObserverType.NEWSPAPER,  6, 3.5, 14, 2.5, "WI", 2022, "summer"),
        CalibrationPair(ObserverType.NEWSPAPER, 10, 2.7, 24, 2.2, "WI", 2024, "spring"),
    ]

    # Build bias signature for newspapers in this region
    newspaper_bias = build_bias_signature(modern_pairs, ObserverType.NEWSPAPER)
    print("NEWSPAPER BIAS SIGNATURE (Wisconsin)")
    print(json.dumps(asdict(newspaper_bias), indent=2, default=str))

    # Apply to 1880s historical record
    historical = HistoricalReport(
        observer_type=ObserverType.NEWSPAPER,
        reported_count=23,
        reported_magnitude=2.8,
        period="1880-1890",
        region="Wisconsin",
    )

    corrected = correct_historical(historical, newspaper_bias)
    print("\nCORRECTED 1880s ESTIMATE")
    print(json.dumps(asdict(corrected), indent=2))

    # Compare to prior-based correction (if no calibration data existed)
    prior_signature = signature_from_prior(ObserverType.NEWSPAPER)
    corrected_prior = correct_historical(historical, prior_signature)
    print("\nPRIOR-BASED CORRECTION (fallback method)")
    print(json.dumps(asdict(corrected_prior), indent=2))

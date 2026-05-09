"""
AI_ECONOMIC_FORECAST_AUDIT_2026

Compares published institutional economic forecasts against measurable
ground-truth outcomes. Quantifies systematic bias direction, error
magnitude, and computational investment versus forecast accuracy.

Design principle: ground truth is publicly measurable reality (BLS data,
bankruptcy filings, census, Federal Reserve public statistics) -- not
peer institutional forecasts. Institutions share incentive structures
that bias forecasts in convergent directions. Comparing one institutional
forecast against another reproduces shared bias. Comparing against
substrate reality exposes it.

Audit produces:
  - forecast_error:           signed error per forecast (over/underestimate)
  - error_magnitude:          absolute deviation from ground truth
  - confidence_calibration:   gap between forecast confidence and accuracy
  - compute_investment:       human-equivalent years invested per forecast
  - accuracy_per_human_year:  efficiency of compute investment
  - systematic_bias_direction: average error sign across forecasts

Sister to:
  - political_audit/substrate_audit.py
      (audits study claims against substrate-primary biology;
       same substrate-vs-institutional-consensus methodology)
  - political_audit/standardization_audit.py
      (audits "standardization worked" claims; same shared-incentive
       structure analysis)
  - political_audit/institutional_audit_protocol.py
      (institution-level gate audit)

Standard library only. CC0 Public Domain.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
import statistics


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class Forecast:
    """A single institutional forecast record."""
    institution: str                    # "Federal Reserve", "McKinsey", etc.
    forecast_id: str                    # internal identifier
    publication_date: str               # ISO date
    target_period: str                  # period the forecast covers
    variable: str                       # "unemployment_rate", "wage_growth"
    predicted_value: float
    confidence_level: float             # forecasted confidence 0.0-1.0
    methodology: str                    # "ML_model", "DSGE", "AI_LLM"
    compute_hours: Optional[float] = None             # GPU-hours if AI/ML
    research_person_hours: Optional[float] = None
    citations_to_other_forecasts: int = 0   # circular reinforcement signal


@dataclass
class GroundTruth:
    """Ground-truth measurement from public data."""
    variable: str
    period: str
    measured_value: float
    source: str                         # "BLS", "Federal_Reserve_FRED", "Census"
    public_url: Optional[str] = None


@dataclass
class AuditResult:
    forecast: Forecast
    ground_truth: GroundTruth
    error: float                        # predicted - actual (signed)
    error_magnitude: float              # absolute error
    error_pct: float                    # error as percent of actual
    confidence_calibration_gap: float   # |confidence - accuracy_score|
    accuracy_score: float               # 1.0 - normalized_error_magnitude
    compute_per_accuracy_point: Optional[float]  # GPU-hours per percent accurate
    flags: List[str] = field(default_factory=list)


# =============================================================================
# COMPUTATIONAL INVESTMENT QUANTIFICATION
# Conversion factors: how much human work does AI compute represent?
# Estimates from Stanford AI Index, OpenAI/Anthropic published compute
# disclosures, and academic research throughput benchmarks.
# =============================================================================

GPU_HOURS_PER_HUMAN_RESEARCH_YEAR = 200.0
# Rationale: a single researcher produces ~1 substantive forecast per year;
# AI compute equivalent for a similar-quality forecast = ~200 GPU-hours
# (training + inference + iteration). Conservative; modern LLMs use far more.

LLM_CALL_HUMAN_HOURS_EQUIVALENT = 0.05
# Each substantive LLM inference call ~ 3 minutes of human analytical work.


def compute_to_human_years(compute_hours: float) -> float:
    """Convert GPU-hours of compute to human-research-year equivalents."""
    return compute_hours / GPU_HOURS_PER_HUMAN_RESEARCH_YEAR


def llm_calls_to_human_years(n_calls: int) -> float:
    """Convert LLM inference call count to human-year equivalents."""
    hours = n_calls * LLM_CALL_HUMAN_HOURS_EQUIVALENT
    return hours / 2000.0   # 2000 work hours per year


# =============================================================================
# AUDIT ENGINE
# =============================================================================

def audit_forecast(forecast: Forecast, ground_truth: GroundTruth) -> AuditResult:
    """
    Compare one forecast against ground-truth outcome.
    Returns full audit record.
    """
    if forecast.variable != ground_truth.variable:
        raise ValueError("variable mismatch between forecast and ground truth")

    error = forecast.predicted_value - ground_truth.measured_value
    error_magnitude = abs(error)
    actual = ground_truth.measured_value
    if actual != 0:
        error_pct = (error_magnitude / abs(actual)) * 100.0
    else:
        error_pct = float("inf")

    # Accuracy score: how close forecast was, normalized.
    # If error within 5% of actual: 1.0; if error > 50%: 0.0.
    if error_pct <= 5:
        accuracy = 1.0
    elif error_pct >= 50:
        accuracy = 0.0
    else:
        accuracy = 1.0 - ((error_pct - 5) / 45)

    confidence_gap = abs(forecast.confidence_level - accuracy)

    compute_per_pt = None
    if forecast.compute_hours and accuracy > 0:
        compute_per_pt = forecast.compute_hours / (accuracy * 100)

    flags: List[str] = []
    if forecast.confidence_level >= 0.9 and accuracy < 0.5:
        flags.append("HIGH_CONFIDENCE_LOW_ACCURACY")
    if forecast.citations_to_other_forecasts >= 5 and accuracy < 0.5:
        flags.append("CIRCULAR_INSTITUTIONAL_REINFORCEMENT")
    if error > 0 and "unemployment" in forecast.variable.lower():
        # Predicted unemployment higher than actual = overestimate
        flags.append("OVERESTIMATED_UNEMPLOYMENT_RECOVERY")
    if error < 0 and "unemployment" in forecast.variable.lower():
        flags.append("UNDERESTIMATED_UNEMPLOYMENT")
    if error < 0 and "wage" in forecast.variable.lower():
        flags.append("OVERESTIMATED_WAGE_GROWTH")
    if error > 0 and "bankruptcy" in forecast.variable.lower():
        flags.append("UNDERESTIMATED_BANKRUPTCY_SURGE")

    return AuditResult(
        forecast=forecast,
        ground_truth=ground_truth,
        error=error,
        error_magnitude=error_magnitude,
        error_pct=error_pct,
        confidence_calibration_gap=confidence_gap,
        accuracy_score=accuracy,
        compute_per_accuracy_point=compute_per_pt,
        flags=flags,
    )


# =============================================================================
# AGGREGATE BIAS DETECTION
# =============================================================================

def detect_systematic_bias(audit_results: List[AuditResult]) -> Dict:
    """
    Across many audits, detect if forecast errors point in a consistent
    direction (systematic bias) vs. random scatter (legitimate uncertainty).
    """
    if not audit_results:
        return {"verdict": "no_data"}

    signed_errors = [a.error for a in audit_results]
    mean_error = statistics.mean(signed_errors)
    stdev_error = (
        statistics.stdev(signed_errors) if len(signed_errors) > 1 else 0.0
    )

    # If mean error is large relative to stdev, errors are biased not random
    if stdev_error == 0:
        bias_score = float("inf") if mean_error != 0 else 0.0
    else:
        bias_score = abs(mean_error) / stdev_error

    if bias_score > 1.0:
        verdict = "SYSTEMATIC_BIAS_DETECTED"
    elif bias_score > 0.5:
        verdict = "MODERATE_BIAS"
    else:
        verdict = "ERRORS_APPEAR_RANDOM"

    if mean_error > 0:
        direction = "overestimate"
    elif mean_error < 0:
        direction = "underestimate"
    else:
        direction = "neutral"

    # Aggregate flag distribution
    all_flags = [f for a in audit_results for f in a.flags]
    flag_counts: Dict[str, int] = {}
    for f in all_flags:
        flag_counts[f] = flag_counts.get(f, 0) + 1

    # Aggregate compute investment
    total_compute = sum(a.forecast.compute_hours or 0 for a in audit_results)
    total_human_years = (
        compute_to_human_years(total_compute) if total_compute else None
    )

    mean_accuracy = statistics.mean(a.accuracy_score for a in audit_results)
    mean_confidence = statistics.mean(
        a.forecast.confidence_level for a in audit_results
    )
    mean_calibration_gap = statistics.mean(
        a.confidence_calibration_gap for a in audit_results
    )

    return {
        "n_forecasts": len(audit_results),
        "mean_error": round(mean_error, 4),
        "stdev_error": round(stdev_error, 4),
        "bias_score": round(bias_score, 3),
        "bias_direction": direction,
        "verdict": verdict,
        "mean_accuracy_score": round(mean_accuracy, 3),
        "mean_confidence_level": round(mean_confidence, 3),
        "mean_confidence_calibration_gap": round(mean_calibration_gap, 3),
        "total_gpu_hours_invested": total_compute,
        "total_human_research_years_equivalent": total_human_years,
        "flag_frequency": flag_counts,
    }


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("AI ECONOMIC FORECAST AUDIT -- Demo")
    print("=" * 60)

    # Hypothetical forecasts (illustrative; replace with real data)
    forecasts = [
        Forecast(
            institution="McKinsey_Global_Institute",
            forecast_id="MGI_2022_workforce",
            publication_date="2022-06-01",
            target_period="2024",
            variable="wage_growth_real_pct",
            predicted_value=2.5,
            confidence_level=0.90,
            methodology="ML_model",
            compute_hours=15000,
            citations_to_other_forecasts=12,
        ),
        Forecast(
            institution="Goldman_Sachs",
            forecast_id="GS_2023_displacement",
            publication_date="2023-03-15",
            target_period="2024",
            variable="unemployment_rate_pct",
            predicted_value=4.5,
            confidence_level=0.85,
            methodology="ML_model",
            compute_hours=8000,
            citations_to_other_forecasts=8,
        ),
        Forecast(
            institution="Federal_Reserve",
            forecast_id="FRB_2023_household",
            publication_date="2023-06-01",
            target_period="2024",
            variable="bankruptcy_filings_thousands",
            predicted_value=320.0,
            confidence_level=0.88,
            methodology="DSGE_with_ML",
            compute_hours=12000,
            citations_to_other_forecasts=15,
        ),
    ]

    ground_truths = [
        GroundTruth(
            variable="wage_growth_real_pct",
            period="2024",
            measured_value=-0.5,             # actual: real wages declined
            source="BLS",
        ),
        GroundTruth(
            variable="unemployment_rate_pct",
            period="2024",
            measured_value=4.1,              # actual headline rate
            source="BLS",
        ),
        GroundTruth(
            variable="bankruptcy_filings_thousands",
            period="2024",
            measured_value=415.0,            # actual personal bankruptcies
            source="American_Bankruptcy_Institute",
        ),
    ]

    results = [audit_forecast(f, gt) for f, gt in zip(forecasts, ground_truths)]

    print("\nIndividual forecast audits:")
    for r in results:
        print(f"\n  {r.forecast.institution} -- {r.forecast.variable}")
        print(f"    predicted:       {r.forecast.predicted_value}")
        print(f"    actual:          {r.ground_truth.measured_value}")
        print(f"    error:           {r.error:+.2f} ({r.error_pct:.1f}% off)")
        print(f"    confidence:      {r.forecast.confidence_level:.0%}")
        print(f"    accuracy:        {r.accuracy_score:.0%}")
        print(f"    calibration_gap: {r.confidence_calibration_gap:.2f}")
        if r.flags:
            for flag in r.flags:
                print(f"    [FLAG] {flag}")

    print("\n" + "=" * 60)
    print("AGGREGATE BIAS ANALYSIS:")
    bias = detect_systematic_bias(results)
    for k, v in bias.items():
        print(f"  {k}: {v}")

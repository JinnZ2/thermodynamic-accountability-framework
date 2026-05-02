# “””
trend_corruption_calculator.py

Given measurement-layer corruption and framework-layer corruption,
compute propagated uncertainty in any published Earth-systems trend.

Core equation:
corruption(trend) = corruption(measurement) ⊗ corruption(framework)

This is multiplicative, not additive. Both layers can independently
invalidate a trend; their combined effect is the product of their
individual probability-of-invalidation, not the sum.

Output:
- corruption probability (combined)
- confidence interval on published trend that includes both layers
- verdict: REPORTED | INFLATED | INVERTED | INDETERMINATE

stdlib only. CC0. github.com/JinnZ2
“””

from dataclasses import dataclass, field
from enum import Enum
import math
import json

class CorruptionLevel(Enum):
NONE = 0.0
MINOR = 0.15
MODERATE = 0.35
MAJOR = 0.60
SEVERE = 0.85

@dataclass
class MeasurementCorruption:
“””
Each field is probability (0.0-1.0) that this failure mode is
present and material to the trend.
“””
siting_drift: float = 0.0
detection_density_change: float = 0.0
instrument_step: float = 0.0
homogenization_bias: float = 0.0
pre1900_exclusion: float = 0.0

```
def aggregate(self) -> float:
    """
    Probability that AT LEAST ONE measurement failure mode
    materially distorts the trend.
    Assumes independence (conservative; real correlations
    would make corruption higher).
    """
    p_clean = 1.0
    for v in [self.siting_drift, self.detection_density_change,
              self.instrument_step, self.homogenization_bias,
              self.pre1900_exclusion]:
        p_clean *= (1.0 - v)
    return 1.0 - p_clean
```

@dataclass
class FrameworkCorruption:
“””
Each field is probability (0.0-1.0) that this assumption
failure invalidates the trend extraction.
“””
stationarity_assumed: float = 0.0
baseline_anomalous: float = 0.0
count_treated_as_intensity: float = 0.0
human_modification_unmodeled: float = 0.0
indigenous_baseline_excluded: float = 0.0
linearity_imposed: float = 0.0

```
def aggregate(self) -> float:
    p_clean = 1.0
    for v in [self.stationarity_assumed, self.baseline_anomalous,
              self.count_treated_as_intensity,
              self.human_modification_unmodeled,
              self.indigenous_baseline_excluded,
              self.linearity_imposed]:
        p_clean *= (1.0 - v)
    return 1.0 - p_clean
```

@dataclass
class PublishedTrend:
“”“The claim being audited.”””
domain: str
variable: str
reported_trend: float       # e.g. 0.3 (units / decade)
reported_uncertainty: float  # e.g. ±0.05 (units / decade)
units: str
period: str                  # e.g. “1950-2020”

# —————————————————————

# CORE CALCULATION

# —————————————————————

def calculate_corruption(
trend: PublishedTrend,
measurement: MeasurementCorruption,
framework: FrameworkCorruption,
measurement_inflation_factor: float = 2.5,
framework_inversion_probability: float = 0.4,
) -> dict:
“””
Compute combined corruption and propagated uncertainty.

```
measurement_inflation_factor:
    empirical multiplier on reported uncertainty when
    measurement layer is corrupted. Default 2.5 reflects
    typical understatement found in 5 reference audits.

framework_inversion_probability:
    conditional probability that, given framework corruption,
    the SIGN of the trend is wrong (not just the magnitude).
"""
p_meas = measurement.aggregate()
p_frame = framework.aggregate()

# combined: probability that AT LEAST ONE layer corrupts
p_combined = 1.0 - (1.0 - p_meas) * (1.0 - p_frame)

# propagated uncertainty
# base reported uncertainty assumes neither layer is corrupted
# actual uncertainty = reported × inflation, weighted by P(corruption)
inflation = 1.0 + (p_meas * (measurement_inflation_factor - 1.0))
propagated_uncertainty = trend.reported_uncertainty * inflation

# sign reliability: probability the reported sign is correct
p_sign_wrong = p_frame * framework_inversion_probability
p_sign_correct = 1.0 - p_sign_wrong

# confidence interval (propagated)
# widened by measurement layer; sign uncertainty handled separately
ci_low = trend.reported_trend - propagated_uncertainty
ci_high = trend.reported_trend + propagated_uncertainty

# verdict
if p_combined < 0.20:
    verdict = "REPORTED"
    verdict_note = "trend likely valid as published"
elif p_combined < 0.50:
    verdict = "INFLATED"
    verdict_note = "magnitude likely overstated; sign probably correct"
elif p_sign_wrong > 0.25:
    verdict = "INVERTED"
    verdict_note = "trend sign may be wrong; reported direction unreliable"
else:
    verdict = "INDETERMINATE"
    verdict_note = "both layers compromised; trend not recoverable from this analysis"

return {
    "domain": trend.domain,
    "variable": trend.variable,
    "period": trend.period,
    "reported": {
        "trend": trend.reported_trend,
        "uncertainty": trend.reported_uncertainty,
        "units": trend.units,
    },
    "corruption_probabilities": {
        "measurement_layer": round(p_meas, 3),
        "framework_layer": round(p_frame, 3),
        "combined": round(p_combined, 3),
        "sign_wrong": round(p_sign_wrong, 3),
        "sign_correct": round(p_sign_correct, 3),
    },
    "propagated": {
        "uncertainty": round(propagated_uncertainty, 4),
        "ci_low": round(ci_low, 4),
        "ci_high": round(ci_high, 4),
        "uncertainty_inflation_factor": round(inflation, 2),
    },
    "verdict": verdict,
    "verdict_note": verdict_note,
}
```

# —————————————————————

# QUICK-ENTRY HELPERS

# —————————————————————

def from_levels(
siting=CorruptionLevel.NONE,
detection=CorruptionLevel.NONE,
instrument=CorruptionLevel.NONE,
homogen=CorruptionLevel.NONE,
pre1900=CorruptionLevel.NONE,
) -> MeasurementCorruption:
“”“Build MeasurementCorruption from CorruptionLevel enums.”””
return MeasurementCorruption(
siting_drift=siting.value,
detection_density_change=detection.value,
instrument_step=instrument.value,
homogenization_bias=homogen.value,
pre1900_exclusion=pre1900.value,
)

def framework_from_levels(
stationarity=CorruptionLevel.NONE,
baseline=CorruptionLevel.NONE,
count=CorruptionLevel.NONE,
human=CorruptionLevel.NONE,
indigenous=CorruptionLevel.NONE,
linearity=CorruptionLevel.NONE,
) -> FrameworkCorruption:
return FrameworkCorruption(
stationarity_assumed=stationarity.value,
baseline_anomalous=baseline.value,
count_treated_as_intensity=count.value,
human_modification_unmodeled=human.value,
indigenous_baseline_excluded=indigenous.value,
linearity_imposed=linearity.value,
)

# —————————————————————

# DEMO

# —————————————————————

if **name** == “**main**”:
# Example: published US tornado frequency trend, 1950-2020
trend = PublishedTrend(
domain=“tornado”,
variable=“EF1+ count per year”,
reported_trend=0.8,
reported_uncertainty=0.2,
units=“tornadoes/year/decade”,
period=“1950-2020”,
)

```
# tornado audit findings: severe detection density change,
# major instrument step (radar), framework treats count as trend
meas = from_levels(
    detection=CorruptionLevel.SEVERE,
    instrument=CorruptionLevel.MAJOR,
    pre1900=CorruptionLevel.MODERATE,
)

frame = framework_from_levels(
    baseline=CorruptionLevel.MAJOR,
    count=CorruptionLevel.SEVERE,
    linearity=CorruptionLevel.MODERATE,
)

result = calculate_corruption(trend, meas, frame)
print(json.dumps(result, indent=2))
```

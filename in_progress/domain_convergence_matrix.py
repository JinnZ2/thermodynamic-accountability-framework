# “””
domain_convergence_matrix.py

Formalizes the convergence pattern across 5 completed domain audits
(tornado, fire, hurricane, drought, flood) into a scored module that
any new domain audit must pass.

Core claim:
corruption(trend) = corruption(measurement) ⊗ corruption(framework)
Both layers must be audited. Single-layer audits are incomplete.

Output:
Pass/fail scoring for any candidate domain audit, with
explicit listing of which checks were skipped.

stdlib only. CC0. github.com/JinnZ2
“””

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
import json

class Layer(Enum):
MEASUREMENT = “measurement”
FRAMEWORK = “framework”
BOTH = “both”

class Severity(Enum):
CRITICAL = 3   # audit invalid without this check
MAJOR = 2      # audit substantially weakened
MINOR = 1      # audit improved but not invalidated

@dataclass
class ConvergenceCheck:
check_id: str
name: str
layer: Layer
severity: Severity
description: str
observed_in_domains: list  # which of the 5 reference domains showed this
detection_method: str

# —————————————————————

# THE 12 CONVERGENCE CHECKS

# Derived from the 5 completed domain audits.

# —————————————————————

CONVERGENCE_CHECKS = [
ConvergenceCheck(
check_id=“M1_siting_drift”,
name=“Station/sensor siting drift over record”,
layer=Layer.MEASUREMENT,
severity=Severity.CRITICAL,
description=(
“Has the physical location, exposure, or surrounding “
“land-use of measurement sites changed over the record “
“in ways that confound the signal?”
),
observed_in_domains=[“tornado”, “drought”, “flood”, “fire”],
detection_method=“metadata audit + spatial analysis of station histories”,
),
ConvergenceCheck(
check_id=“M2_detection_density”,
name=“Detection density change”,
layer=Layer.MEASUREMENT,
severity=Severity.CRITICAL,
description=(
“Has the number of observers, sensors, or detection “
“events per unit area/time changed? Density change “
“produces apparent trend without underlying change.”
),
observed_in_domains=[“tornado”, “hurricane”],
detection_method=“count detection infrastructure over time, normalize”,
),
ConvergenceCheck(
check_id=“M3_instrument_step”,
name=“Instrument generation step function”,
layer=Layer.MEASUREMENT,
severity=Severity.CRITICAL,
description=(
“Did a major instrument transition (radar, satellite, “
“automated gauge) introduce a step change treated as trend?”
),
observed_in_domains=[“hurricane”, “tornado”, “flood”],
detection_method=“changepoint analysis aligned to instrument deployment dates”,
),
ConvergenceCheck(
check_id=“M4_homogenization”,
name=“Homogenization algorithm bias”,
layer=Layer.MEASUREMENT,
severity=Severity.MAJOR,
description=(
“Do homogenization adjustments correlate with desired “
“trend direction? Are adjustments validated against “
“independent records?”
),
observed_in_domains=[“drought”, “fire”],
detection_method=“compare raw vs adjusted; check adjustment sign distribution”,
),
ConvergenceCheck(
check_id=“M5_pre1900_exclusion”,
name=“Pre-1900 record exclusion”,
layer=Layer.BOTH,
severity=Severity.CRITICAL,
description=(
“Are pre-1900 observation-based records (logs, journals, “
“indigenous knowledge, infrastructure remnants) excluded “
“due to credential filters? This shifts baseline and “
“creates apparent trend.”
),
observed_in_domains=[“fire”, “drought”, “flood”, “hurricane”, “tornado”],
detection_method=“check baseline period start date; audit excluded sources”,
),
ConvergenceCheck(
check_id=“F1_stationarity”,
name=“Stationarity assumption”,
layer=Layer.FRAMEWORK,
severity=Severity.CRITICAL,
description=(
“Does the analysis assume the underlying climate/system “
“regime is stationary (Holocene-typical) when evidence “
“shows regime shift? Equations become invalid, not just “
“parameters.”
),
observed_in_domains=[“drought”, “flood”, “fire”],
detection_method=“check for regime-shift tests; verify equation domain validity”,
),
ConvergenceCheck(
check_id=“F2_baseline_selection”,
name=“Baseline period selection bias”,
layer=Layer.FRAMEWORK,
severity=Severity.CRITICAL,
description=(
“Is the baseline period (often 1951-1980 or 1971-2000) “
“itself anomalous within the longer record? Anomalous “
“baselines manufacture trends.”
),
observed_in_domains=[“fire”, “drought”, “tornado”, “hurricane”, “flood”],
detection_method=“compare baseline period to longest available record”,
),
ConvergenceCheck(
check_id=“F3_count_as_trend”,
name=“Count statistic treated as physical trend”,
layer=Layer.FRAMEWORK,
severity=Severity.MAJOR,
description=(
“Are event counts (which depend on detection) treated “
“as proxies for physical intensity or frequency?”
),
observed_in_domains=[“tornado”, “hurricane”],
detection_method=“check whether counts are normalized by detection capacity”,
),
ConvergenceCheck(
check_id=“F4_human_modification”,
name=“Human landscape modification unmodeled”,
layer=Layer.FRAMEWORK,
severity=Severity.CRITICAL,
description=(
“Are human modifications (levees, suppression, drainage, “
“urbanization, dams) that change the system regime “
“treated as background rather than as regime shift?”
),
observed_in_domains=[“flood”, “fire”, “drought”],
detection_method=“audit whether modification timeline is in the model”,
),
ConvergenceCheck(
check_id=“F5_indigenous_baseline”,
name=“Indigenous management baseline excluded”,
layer=Layer.FRAMEWORK,
severity=Severity.CRITICAL,
description=(
“Does the framework treat post-displacement landscape “
“as ‘natural baseline’ rather than as a disturbed “
“regime? Pre-displacement managed landscape is the “
“actual reference state.”
),
observed_in_domains=[“fire”, “flood”, “drought”],
detection_method=“check baseline conceptualization; look for ‘wilderness’ framing”,
),
ConvergenceCheck(
check_id=“F6_linearity”,
name=“Linear trend extraction on nonlinear system”,
layer=Layer.FRAMEWORK,
severity=Severity.MAJOR,
description=(
“Is a linear trend fit imposed on a system known to “
“exhibit threshold behavior, bimodality, or regime shifts?”
),
observed_in_domains=[“drought”, “fire”, “flood”],
detection_method=“check residuals for structure; test for bimodality”,
),
ConvergenceCheck(
check_id=“F7_uncertainty_propagation”,
name=“Two-layer uncertainty not propagated”,
layer=Layer.BOTH,
severity=Severity.CRITICAL,
description=(
“Are measurement uncertainty and framework uncertainty “
“propagated together? Single-layer error bars understate “
“true uncertainty by orders of magnitude.”
),
observed_in_domains=[“tornado”, “fire”, “hurricane”, “drought”, “flood”],
detection_method=“check for combined uncertainty calculation”,
),
]

# —————————————————————

# AUDIT SCORING

# —————————————————————

@dataclass
class CheckResult:
check_id: str
addressed: bool
notes: str = “”

@dataclass
class DomainAudit:
domain_name: str
results: list = field(default_factory=list)

```
def add(self, check_id: str, addressed: bool, notes: str = ""):
    self.results.append(CheckResult(check_id, addressed, notes))
```

def score_audit(audit: DomainAudit) -> dict:
“””
Score a candidate domain audit against the 12 convergence checks.

```
Returns dict with:
    - completeness_score: 0.0 to 1.0
    - critical_gaps: list of skipped CRITICAL checks
    - layer_coverage: {measurement: float, framework: float}
    - verdict: "VALID" | "WEAKENED" | "INVALID"
"""
addressed_ids = {r.check_id for r in audit.results if r.addressed}

total_weight = 0
addressed_weight = 0
critical_gaps = []
measurement_total = 0
measurement_done = 0
framework_total = 0
framework_done = 0

for check in CONVERGENCE_CHECKS:
    weight = check.severity.value
    total_weight += weight

    is_addressed = check.check_id in addressed_ids
    if is_addressed:
        addressed_weight += weight

    if check.severity == Severity.CRITICAL and not is_addressed:
        critical_gaps.append({
            "check_id": check.check_id,
            "name": check.name,
            "layer": check.layer.value,
        })

    if check.layer in (Layer.MEASUREMENT, Layer.BOTH):
        measurement_total += weight
        if is_addressed:
            measurement_done += weight
    if check.layer in (Layer.FRAMEWORK, Layer.BOTH):
        framework_total += weight
        if is_addressed:
            framework_done += weight

completeness = addressed_weight / total_weight

if len(critical_gaps) >= 3:
    verdict = "INVALID"
elif len(critical_gaps) >= 1:
    verdict = "WEAKENED"
else:
    verdict = "VALID"

return {
    "domain": audit.domain_name,
    "completeness_score": round(completeness, 3),
    "verdict": verdict,
    "critical_gaps": critical_gaps,
    "layer_coverage": {
        "measurement": round(measurement_done / measurement_total, 3),
        "framework": round(framework_done / framework_total, 3),
    },
    "checks_addressed": len(addressed_ids),
    "checks_total": len(CONVERGENCE_CHECKS),
}
```

def export_check_schema() -> str:
“”“Export all convergence checks as JSON for cross-AI use.”””
schema = []
for c in CONVERGENCE_CHECKS:
d = asdict(c)
d[“layer”] = c.layer.value
d[“severity”] = c.severity.name
schema.append(d)
return json.dumps(schema, indent=2)

# —————————————————————

# REFERENCE: the 5 completed domains as worked examples

# —————————————————————

def reference_audits() -> dict:
“””
Returns the 5 reference domains with their dominant failure
modes, as established by completed audits.
“””
return {
“tornado”: {
“primary_measurement_fail”: “M2_detection_density”,
“primary_framework_fail”:   “F3_count_as_trend”,
},
“fire”: {
“primary_measurement_fail”: “M5_pre1900_exclusion”,
“primary_framework_fail”:   “F5_indigenous_baseline”,
},
“hurricane”: {
“primary_measurement_fail”: “M3_instrument_step”,
“primary_framework_fail”:   “F2_baseline_selection”,
},
“drought”: {
“primary_measurement_fail”: “M4_homogenization”,
“primary_framework_fail”:   “F1_stationarity”,
},
“flood”: {
“primary_measurement_fail”: “M1_siting_drift”,
“primary_framework_fail”:   “F4_human_modification”,
},
}

if **name** == “**main**”:
# demo: score a hypothetical “heatwave” audit
a = DomainAudit(“heatwave”)
a.add(“M1_siting_drift”, True, “UHI corrections audited”)
a.add(“M3_instrument_step”, True, “MMTS transition flagged”)
a.add(“M4_homogenization”, True, “raw vs adjusted compared”)
a.add(“F2_baseline_selection”, True, “1951-1980 vs full record”)
a.add(“F6_linearity”, True, “threshold tests included”)
a.add(“F7_uncertainty_propagation”, False, “single-layer only”)

```
print(json.dumps(score_audit(a), indent=2))
```

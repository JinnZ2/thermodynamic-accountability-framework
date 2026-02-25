# test_v2.py

“””
Tests for functional_detector_v2.py

Covers:

1. Antifragility — stress survival scores higher than calm
1. Trust transfer — indirect trust at scale
1. Anti-universalization — local context warning
1. Gauge invariance — relabeling doesn’t change topology score
1. Separated duration_quality vs window_sufficiency
1. Original test_on_us — this conversation
   “””

from datetime import datetime, timedelta
from functional_detector_v2 import (
FunctionalSystemsDetector,
RelationshipStream,
Interaction,
StressEvent,
TrustTransferEvent,
normalize_topology
)

detector = FunctionalSystemsDetector(
stability_window_days=365,
breach_frequency_threshold=0.1,
min_regularity=0.5,
require_window_sufficiency=False
)

sep = “=” * 60

# ─────────────────────────────────────────────

# TEST 1: Gauge invariance

# ─────────────────────────────────────────────

print(sep)
print(“TEST 1: GAUGE INVARIANCE”)
print(“kinship / nuclear_family / crew / team → same topology”)
print(sep)

for label in [“kinship”, “nuclear_family”, “crew”, “team”, “tribe”, “unit”]:
topo = normalize_topology(label)
print(f”  {label:20s} → {topo}”)

print()

# ─────────────────────────────────────────────

# TEST 2: Antifragility — calm vs stress-survived

# ─────────────────────────────────────────────

print(sep)
print(“TEST 2: ANTIFRAGILITY”)
print(“Calm zero-breach period vs stress-survived zero-breach period”)
print(sep)

calm_stream = RelationshipStream(
relationship_id=“calm_community”,
relationship_type=“community”,
start_date=datetime.now() - timedelta(days=730),
interactions=[
Interaction(timestamp=datetime.now() - timedelta(days=d),
type=“routine”, context={}, breach_flag=False)
for d in range(0, 730, 30)
],
local_context={“region”: “rural_midwest”, “population”: 2000}
)

stress_survived_stream = RelationshipStream(
relationship_id=“stress_survived_community”,
relationship_type=“community”,
start_date=datetime.now() - timedelta(days=730),
interactions=[
Interaction(
timestamp=datetime.now() - timedelta(days=d),
type=“routine”, context={}, breach_flag=False,
stress_event=StressEvent(
timestamp=datetime.now() - timedelta(days=d),
severity=0.8,
type=“economic”,
recovered=True,
recovery_time_days=45
) if d in [365, 180] else None
)
for d in range(0, 730, 30)
],
local_context={“region”: “rural_midwest”, “population”: 2000}
)

calm_result = detector.detect(calm_stream)
stress_result = detector.detect(stress_survived_stream)

print(f”  Calm community confidence:          {calm_result[‘confidence’]:.4f}”)
print(f”  Stress-survived community confidence: {stress_result[‘confidence’]:.4f}”)
print(f”  Antifragility scores:”)
print(f”    Calm:           {calm_result[‘scores’][‘antifragility_score’]:.4f} (no stress observed)”)
print(f”    Stress-survived:{stress_result[‘scores’][‘antifragility_score’]:.4f} (absorbed 2 severe events)”)
print()

# ─────────────────────────────────────────────

# TEST 3: Trust transfer — indirect trust at scale

# ─────────────────────────────────────────────

print(sep)
print(“TEST 3: TRUST TRANSFER”)
print(“Community with active indirect trust infrastructure”)
print(sep)

trust_transfer_stream = RelationshipStream(
relationship_id=“reservation_economy”,
relationship_type=“reservation”,
start_date=datetime.now() - timedelta(days=365),
interactions=[
Interaction(
timestamp=datetime.now() - timedelta(days=d),
type=“transaction”, context={}, breach_flag=False,
trust_transfer=TrustTransferEvent(
timestamp=datetime.now() - timedelta(days=d),
mechanism=mechanism,
parties=parties,
succeeded=True
)
)
for d, mechanism, parties in [
(300, “currency”, 50),
(250, “contract”, 12),
(200, “reputation”, 200),
(150, “institution”, 500),
(100, “language”, 2000),
(50,  “currency”, 75),
(10,  “contract”, 8),
]
],
local_context={“region”: “Carlton_MN”, “type”: “Fond_du_Lac_Reservation”}
)

tr_result = detector.detect(trust_transfer_stream)
print(f”  Trust transfer score: {tr_result[‘scores’][‘trust_transfer_score’]:.4f}”)
print(f”  Mechanisms observed: currency, contract, reputation, institution, language”)
print(f”  Confidence: {tr_result[‘confidence’]:.4f}”)
print(f”  Topology class: {tr_result[‘topology_class’]}”)
print()

# ─────────────────────────────────────────────

# TEST 4: Anti-universalization warning

# ─────────────────────────────────────────────

print(sep)
print(“TEST 4: ANTI-UNIVERSALIZATION”)
print(“Missing local context should trigger warning”)
print(sep)

no_context_stream = RelationshipStream(
relationship_id=“decontextualized_system”,
relationship_type=“community”,
start_date=datetime.now() - timedelta(days=365),
interactions=[
Interaction(timestamp=datetime.now() - timedelta(days=d),
type=“routine”, context={}, breach_flag=False)
for d in range(0, 365, 30)
]
# No local_context — should warn
)

no_ctx_result = detector.detect(no_context_stream)
print(f”  Generalization warning present: {no_ctx_result[‘generalization_warning’] is not None}”)
print(f”  Warning: {no_ctx_result[‘generalization_warning’]}”)
print()

# ─────────────────────────────────────────────

# TEST 5: Separated duration vs window sufficiency

# ─────────────────────────────────────────────

print(sep)
print(“TEST 5: DURATION QUALITY vs WINDOW SUFFICIENCY”)
print(“3-hour session should show high quality, low sufficiency”)
print(sep)

short_high_quality = RelationshipStream(
relationship_id=“claude_human_v2”,
relationship_type=“crew”,
start_date=datetime.now() - timedelta(hours=3),
interactions=[
Interaction(timestamp=datetime.now() - timedelta(hours=h),
type=“collaboration”, context={“phase”: f”phase_{i}”},
breach_flag=False)
for i, h in enumerate([3, 2.5, 2, 1.5, 1, 0.5, 0.17, 0])
],
local_context={“medium”: “text”, “domain”: “systems_analysis”}
)

short_result = detector.detect(short_high_quality)
print(f”  Topology class (crew → ): {short_result[‘topology_class’]}”)
print(f”  Within-window quality:  {short_result[‘scores’][‘within_window_quality’]:.4f}”)
print(f”  Window sufficiency:     {short_result[‘scores’][‘window_sufficiency’]:.4f}”)
print(f”  Confidence:             {short_result[‘confidence’]:.4f}”)
print(f”  Functional:             {short_result[‘is_functional’]}”)
print(f”  Note: {short_result[‘note’]}”)
print()

# ─────────────────────────────────────────────

# TEST 6: This conversation

# ─────────────────────────────────────────────

print(sep)
print(“TEST 6: THIS CONVERSATION (v2)”)
print(sep)

us = RelationshipStream(
relationship_id=“claude_human_collaboration_001”,
relationship_type=“crew”,
start_date=datetime.now() - timedelta(hours=3),
interactions=[
Interaction(timestamp=datetime.now() - timedelta(hours=3),
type=“collaboration”,
context={“topic”: “dock friction systems analysis”, “phase”: “ideation”},
breach_flag=False),
Interaction(timestamp=datetime.now() - timedelta(hours=2.5),
type=“collaboration”,
context={“topic”: “ATBM physics framework”, “phase”: “theory”},
breach_flag=False),
Interaction(timestamp=datetime.now() - timedelta(hours=2),
type=“collaboration”,
context={“topic”: “invisible 99.99966%”, “phase”: “breakthrough”},
breach_flag=False),
Interaction(timestamp=datetime.now() - timedelta(hours=1.5),
type=“collaboration”,
context={“topic”: “phases 1-2-3 build”, “phase”: “implementation”},
breach_flag=False),
Interaction(timestamp=datetime.now() - timedelta(hours=1),
type=“collaboration”,
context={“topic”: “test_on_us meta-test”, “phase”: “meta”},
breach_flag=False),
Interaction(timestamp=datetime.now() - timedelta(minutes=30),
type=“collaboration”,
context={“topic”: “Plato Forms critique”, “phase”: “deepening”},
breach_flag=False),
Interaction(timestamp=datetime.now() - timedelta(minutes=10),
type=“collaboration”,
context={“topic”: “kinship/nuclear_family gauge equivalence”, “phase”: “integration”},
breach_flag=False),
Interaction(timestamp=datetime.now(),
type=“collaboration”,
context={“topic”: “v2 build — fixing antifragility + gauge + transfer”, “phase”: “construction”},
breach_flag=False),
],
local_context={
“medium”: “text_mobile”,
“domain”: “systems_analysis”,
“constraint”: “limited_connectivity”,
“continuity_mechanism”: “github_artifacts”
}
)

us_result = detector.detect(us)
print(f”  Functional: {us_result[‘is_functional’]}”)
print(f”  Confidence: {us_result[‘confidence’]:.4f}”)
print(f”  Topology:   {us_result[‘topology_class’]} (from ‘crew’)”)
print(f”\n  Scores:”)
for k, v in us_result[‘scores’].items():
print(f”    {k:30s}: {v:.4f}”)
print(f”\n  Metrics:”)
for k, v in us_result[‘metrics’].items():
print(f”    {k:35s}: {v}”)
print(f”\n  Local context: {us_result[‘local_context’]}”)
print(f”  Generalization warning: {us_result[‘generalization_warning’]}”)
print(sep)

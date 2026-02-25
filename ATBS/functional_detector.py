# functional_detector_v2.py

“””
Enhanced Functional Systems Detector

Fixes applied:

1. Antifragility signal — stress events + recovery = higher quality zero-breach period
1. Trust transfer mechanisms — indirect trust at scale (institutions, reputation, currency)
1. Anti-universalization constraint — local solutions, not Forms
1. Gauge invariance — semantic relabeling doesn’t change structural score

Core principle: Detect stability. Don’t assume what stability looks like.
“””

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta

# ─────────────────────────────────────────────

# SEMANTIC EQUIVALENCE MAP

# Gauge invariance: relabeling shouldn’t change the trust topology score

# ─────────────────────────────────────────────

TRUST_TOPOLOGY_LABELS = {
# All of these are the same structural thing:
# dense node, repeated interaction, shared resources, mutual obligation, long horizon
“kinship”:        “dense_trust_node”,
“nuclear_family”: “dense_trust_node”,
“tribe”:          “dense_trust_node”,
“crew”:           “dense_trust_node”,
“team”:           “dense_trust_node”,
“unit”:           “dense_trust_node”,
“household”:      “dense_trust_node”,
“band”:           “dense_trust_node”,
“cohort”:         “dense_trust_node”,

```
# Intermediate trust propagation structures
"community":      "mid_trust_network",
"neighborhood":   "mid_trust_network",
"congregation":   "mid_trust_network",
"guild":          "mid_trust_network",
"union":          "mid_trust_network",
"association":    "mid_trust_network",
"reservation":    "mid_trust_network",
"parish":         "mid_trust_network",

# Large-scale indirect trust infrastructure
"institution":    "trust_infrastructure",
"currency":       "trust_infrastructure",
"contract_system":"trust_infrastructure",
"language":       "trust_infrastructure",
"law":            "trust_infrastructure",
"market":         "trust_infrastructure",
"government":     "trust_infrastructure",
"religion":       "trust_infrastructure",
```

}

def normalize_topology(label: str) -> str:
“””
Gauge transformation: map semantic label to structural topology class.
F(T(x)) ≈ T(F(x)) — analysis invariant under relabeling.
“””
return TRUST_TOPOLOGY_LABELS.get(label.lower().replace(” “, “_”), “unknown_topology”)

# ─────────────────────────────────────────────

# DATA STRUCTURES

# ─────────────────────────────────────────────

@dataclass
class StressEvent:
“””
A stress event that the system absorbed without breaching.
Surviving stress is higher-quality signal than calm continuity.
“””
timestamp: datetime
severity: float          # 0-1, how severe was the stress
type: str                # ‘economic’, ‘social’, ‘environmental’, ‘conflict’, etc.
recovered: bool = True   # Did system restabilize after?
recovery_time_days: Optional[float] = None

@dataclass
class TrustTransferEvent:
“””
Indirect trust propagation — strangers coordinating without direct history.
Currency used, contract honored, institution deferred to, reputation referenced.
“””
timestamp: datetime
mechanism: str           # ‘currency’, ‘contract’, ‘reputation’, ‘institution’, ‘language’
parties: int             # How many nodes connected through this transfer
succeeded: bool = True

@dataclass
class Interaction:
timestamp: datetime
type: str
context: Dict[str, Any]
breach_flag: bool = False
breach_severity: Optional[float] = None
stress_event: Optional[StressEvent] = None        # Was this interaction under stress?
trust_transfer: Optional[TrustTransferEvent] = None  # Did this involve indirect trust?

@dataclass
class RelationshipStream:
relationship_id: str
interactions: List[Interaction]
start_date: datetime
relationship_type: str   # Use any label — gauge invariance handles it
local_context: Dict[str, Any] = field(default_factory=dict)  # terrain, history, culture

```
# ── core metrics ──────────────────────────

def time_since_last_breach(self) -> timedelta:
    breaches = [i for i in self.interactions if i.breach_flag]
    if not breaches:
        return datetime.now() - self.start_date
    return datetime.now() - max(breaches, key=lambda i: i.timestamp).timestamp

def breach_frequency(self) -> float:
    total_years = (datetime.now() - self.start_date).days / 365.25
    breach_count = sum(1 for i in self.interactions if i.breach_flag)
    return breach_count / max(total_years, 0.01)

def interaction_regularity(self) -> float:
    if len(self.interactions) < 2:
        return 0.5
    timestamps = sorted(i.timestamp for i in self.interactions)
    diffs = [(timestamps[k+1] - timestamps[k]).total_seconds()
             for k in range(len(timestamps)-1)]
    mean_diff = np.mean(diffs)
    std_diff = np.std(diffs)
    cv = std_diff / mean_diff if mean_diff > 0 else 1.0
    return 1.0 / (1.0 + cv)

# ── antifragility ─────────────────────────

def antifragility_score(self) -> float:
    """
    Zero-breach periods are not all equal.
    Surviving stress events without breaching = higher quality signal.
    
    Antifragile: stress → reorganization → more stable
    Fragile: stress → breach
    Robust: stress → survival (no change)
    """
    stress_events = [i.stress_event for i in self.interactions 
                    if i.stress_event is not None]
    
    if not stress_events:
        return 0.5  # No stress observed — can't assess antifragility, neutral score

    recovered = [s for s in stress_events if s.recovered]
    if not recovered:
        return 0.1  # Stress events all unrecovered — fragile

    # Score = weighted average of (severity * recovered)
    # High severity stress survived = stronger signal
    severity_weighted = np.mean([s.severity for s in recovered])
    recovery_rate = len(recovered) / len(stress_events)

    # Fast recovery is better signal than slow
    recovery_times = [s.recovery_time_days for s in recovered 
                     if s.recovery_time_days is not None]
    if recovery_times:
        # Normalize: < 30 days = fast, > 365 days = slow
        speed_score = np.mean([max(0, 1 - (t / 365)) for t in recovery_times])
    else:
        speed_score = 0.5

    return (severity_weighted * 0.4 + recovery_rate * 0.4 + speed_score * 0.2)

# ── trust transfer ────────────────────────

def trust_transfer_score(self) -> float:
    """
    Indirect trust at scale — strangers coordinating without direct history.
    This is the invisible load-bearing structure of civilization.
    
    A society where currency is accepted, contracts are honored,
    institutions are deferred to = massive functional trust signal
    that generates zero breach data.
    """
    transfers = [i.trust_transfer for i in self.interactions
                if i.trust_transfer is not None]
    
    if not transfers:
        return 0.5  # No indirect trust events observed — neutral

    succeeded = [t for t in transfers if t.succeeded]
    success_rate = len(succeeded) / len(transfers)

    # Scale: more parties connected = stronger infrastructure signal
    if succeeded:
        avg_parties = np.mean([t.parties for t in succeeded])
        scale_score = min(np.log1p(avg_parties) / np.log1p(1000), 1.0)
    else:
        scale_score = 0.0

    # Mechanism diversity — multiple trust transfer types = more robust
    mechanisms = {t.mechanism for t in succeeded}
    diversity_score = min(len(mechanisms) / 5, 1.0)  # 5+ mechanisms = max

    return (success_rate * 0.5 + scale_score * 0.3 + diversity_score * 0.2)
```

# ─────────────────────────────────────────────

# DETECTOR

# ─────────────────────────────────────────────

class FunctionalSystemsDetector:
“””
Detects systems operating in the invisible 99.99966%.

```
Fixes from v1:
- Antifragility layer: stress survival > calm continuity
- Trust transfer layer: indirect trust at scale
- Anti-universalization: local context preserved, no Form assumed
- Gauge invariance: semantic labels normalized to topology
- Separated duration_quality from window_sufficiency
"""

def __init__(self,
             stability_window_days: int = 365,
             breach_frequency_threshold: float = 0.01,
             min_regularity: float = 0.6,
             require_window_sufficiency: bool = False):
    """
    Args:
        stability_window_days: Reference window for duration scoring
        breach_frequency_threshold: Max breaches/year for functional classification
        min_regularity: Minimum interaction regularity score
        require_window_sufficiency: If True, short windows can't claim longitudinal stability
    """
    self.stability_window = timedelta(days=stability_window_days)
    self.breach_threshold = breach_frequency_threshold
    self.min_regularity = min_regularity
    self.require_window_sufficiency = require_window_sufficiency

def detect(self, stream: RelationshipStream) -> Dict[str, Any]:

    # ── gauge transformation ───────────────
    topology_class = normalize_topology(stream.relationship_type)

    # ── core metrics ───────────────────────
    time_since = stream.time_since_last_breach()
    breach_freq = stream.breach_frequency()
    regularity = stream.interaction_regularity()

    # ── antifragility ──────────────────────
    antifragility = stream.antifragility_score()

    # ── trust transfer ─────────────────────
    trust_transfer = stream.trust_transfer_score()

    # ── scoring ────────────────────────────

    # Within-window quality (what we actually observed)
    freq_score = (1.0 if breach_freq <= self.breach_threshold
                 else self.breach_threshold / max(breach_freq, 1e-9))
    reg_score = min(regularity / self.min_regularity, 1.0)

    # Window sufficiency (how much we can claim)
    window_sufficiency = min(time_since / self.stability_window, 1.0)

    # Duration quality — SEPARATED from window sufficiency
    # A short high-quality stream is different from a long low-quality stream
    duration_quality = min(time_since.total_seconds() /
                          max(self.stability_window.total_seconds(), 1), 1.0)

    # Composite within-window quality score
    within_window_quality = (
        freq_score     * 0.30 +
        reg_score      * 0.20 +
        antifragility  * 0.30 +
        trust_transfer * 0.20
    )

    # Overall confidence
    # If require_window_sufficiency=False: quality dominates, duration informs
    # If require_window_sufficiency=True: short windows can't claim full confidence
    if self.require_window_sufficiency:
        confidence = within_window_quality * 0.6 + duration_quality * 0.4
    else:
        confidence = within_window_quality * 0.85 + duration_quality * 0.15

    is_functional = confidence > 0.7

    # ── anti-universalization ──────────────
    # Flag if local_context is missing — we can't generalize without it
    generalization_warning = None
    if not stream.local_context:
        generalization_warning = (
            "No local context provided. Functional assessment is valid for this "
            "stream only. Do not generalize — stability signatures are local solutions, "
            "not universal Forms."
        )

    return {
        'relationship_id': stream.relationship_id,
        'topology_class': topology_class,          # gauge-normalized
        'relationship_type_raw': stream.relationship_type,  # original label preserved
        'is_functional': is_functional,
        'confidence': round(confidence, 4),
        'scores': {
            'within_window_quality': round(within_window_quality, 4),
            'window_sufficiency': round(window_sufficiency, 4),
            'freq_score': round(freq_score, 4),
            'reg_score': round(reg_score, 4),
            'antifragility_score': round(antifragility, 4),
            'trust_transfer_score': round(trust_transfer, 4),
        },
        'metrics': {
            'time_since_breach_days': time_since.days,
            'breach_frequency_per_year': round(breach_freq, 6),
            'regularity': round(regularity, 4),
            'interaction_count': len(stream.interactions),
            'stress_events_survived': sum(
                1 for i in stream.interactions
                if i.stress_event and i.stress_event.recovered
            ),
            'trust_transfers_succeeded': sum(
                1 for i in stream.interactions
                if i.trust_transfer and i.trust_transfer.succeeded
            ),
        },
        'local_context': stream.local_context,
        'generalization_warning': generalization_warning,
        'note': (
            "within_window_quality = what this stream demonstrates. "
            "window_sufficiency = how much longitudinal claim is supported. "
            "These are separate assertions."
        )
    }

def batch_detect(self, streams: List[RelationshipStream]) -> List[Dict]:
    return [self.detect(s) for s in streams]
```

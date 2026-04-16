"""
trust_decay.py
==============
Extension to attribution_sim.py adding trust decay dynamics.

CORE HYPOTHESIS
---------------
Competent workers detect attribution capture FIRST because:
  1. they generate more insights per unit time
  2. they therefore experience more laundering events
  3. they have stronger signal:noise for "my credit is being taken"
  4. their internal models of fairness calibrate faster

RESULT: the organization selectively loses its highest-competence
generators FIRST. The attribution capture mechanism is a
competence-extinction filter.

MODEL
-----
Each worker has:
  - competence ∈ [0, 1]   — affects insight rate AND value magnitude
  - trust ∈ [0, 1]        — starts at 1.0, decays with laundering events
  - detection_rate        — how quickly they notice capture (∝ competence)
  - engagement_floor      — below this trust level, they check out

Each quarter:
  - workers generate insights (rate ∝ competence × engagement)
  - laundering events update trust (weighted by detection rate)
  - trust below engagement_floor → insight rate collapses
  - trust below exit_threshold → worker leaves (insight rate → 0)

CC0. Stdlib only.
"""

from dataclasses import dataclass, field
from typing import Literal
import random
import statistics
import math

# Reuse energy constants from base sim
from attribution_sim import (
    ENERGY_INPUTS, total_energy_in, JOULES_PER_DOLLAR, fmt_j
)


# -----------------------------------------------------------------
# EXTENDED WORKER MODEL
# -----------------------------------------------------------------
@dataclass
class Worker:
    id: int
    role: Literal["floor", "office", "executive"]
    competence: float           # [0, 1] — affects rate + magnitude
    base_insight_rate: float    # insights/qtr at full engagement
    cross_silo_prob: float
    credit_retention: float     # probability of keeping credit when generated

    # Trust dynamics
    trust: float = 1.0          # starts high, decays with capture events
    engagement: float = 1.0     # multiplier on insight rate (trust-derived)
    exited: bool = False        # did they leave?
    quarters_below_25: int = 0  # consecutive quarters with trust < 0.25

    # History for analysis
    capture_events_witnessed: int = 0
    trust_history: list = field(default_factory=list)
    engagement_history: list = field(default_factory=list)


@dataclass
class Insight:
    id: int
    quarter: int
    origin_role: str
    origin_worker_id: int
    downstream_joules: float
    cross_silo: bool
    attributed_role: str = ""
    attributed_worker_id: int = -1
    was_laundered: bool = False  # did credit flow away from origin?


# -----------------------------------------------------------------
# TRUST DYNAMICS
# -----------------------------------------------------------------
def detection_rate(worker: Worker) -> float:
    """
    How quickly this worker notices that credit is being taken.

    High competence → stronger internal model of cause-effect
                   → better at distinguishing signal from noise
                   → higher detection rate per capture event

    range: ~0.02 (oblivious) to ~0.30 (sharp detector)
    """
    return 0.02 + 0.28 * worker.competence


def update_trust_for_laundering(worker: Worker, severity: float):
    """
    Each laundering event erodes trust by an amount scaled to:
      - detection rate (competent workers see it clearly)
      - severity (how much value was taken)

    Severity is normalized to [0, 1] by log-scaling the joules.
    """
    dr = detection_rate(worker)
    # Trust decay per event: competence-weighted
    decay = dr * severity * 0.15  # tunable
    worker.trust = max(0.0, worker.trust - decay)
    worker.capture_events_witnessed += 1


def update_engagement(worker: Worker, quarters_below_threshold: int = 0):
    """
    Engagement is a sigmoid function of trust:
      - trust > 0.7: fully engaged (engagement ≈ 1.0)
      - trust 0.4-0.7: gradual disengagement
      - trust < 0.3: steep drop (quiet quitting)
      - trust < 0.15: exit imminent

    This models the threshold-nonlinear response observed in
    burnout literature: engagement doesn't decay linearly with
    conditions; it collapses at a breakpoint.

    Exit triggers on EITHER:
      - trust < 0.10 at any point, OR
      - trust < 0.25 sustained for 3+ quarters
    (competent workers with high detection still exit; the
     second condition catches slow-burn disengagement)
    """
    t = worker.trust
    if t >= 0.7:
        worker.engagement = 1.0
    elif t >= 0.4:
        worker.engagement = 0.3 + (t - 0.4) * (0.7 / 0.3)
    elif t >= 0.15:
        worker.engagement = 0.1 + (t - 0.15) * (0.2 / 0.25)
    else:
        worker.engagement = 0.05

    # Exit thresholds
    if t < 0.10:
        worker.exited = True
        worker.engagement = 0.0
    elif t < 0.25 and quarters_below_threshold >= 3:
        worker.exited = True
        worker.engagement = 0.0


def severity_of_capture(insight: Insight, max_j: float) -> float:
    """Normalize joules to [0, 1] severity, log-scaled."""
    if insight.downstream_joules <= 0:
        return 0.0
    log_val = math.log10(max(insight.downstream_joules, 1.0))
    log_max = math.log10(max(max_j, 1.0))
    return min(1.0, log_val / log_max)


# -----------------------------------------------------------------
# FACILITY
# -----------------------------------------------------------------
def build_facility(n_floor=50, n_office=15, n_exec=3, seed=42) -> list[Worker]:
    rng = random.Random(seed)
    workers = []
    wid = 0

    # Floor: competence drawn from beta-ish (most workers are competent
    # enough, a few are standouts)
    for _ in range(n_floor):
        comp = min(1.0, max(0.0, rng.betavariate(5, 3)))  # mean ~0.625
        workers.append(Worker(
            id=wid, role="floor", competence=comp,
            base_insight_rate=2.0 + comp * 5.0,       # 2-7, competence-scaled
            cross_silo_prob=0.4 + comp * 0.3,         # 0.4-0.7
            credit_retention=rng.uniform(0.05, 0.20),
        ))
        wid += 1

    # Office
    for _ in range(n_office):
        comp = min(1.0, max(0.0, rng.betavariate(4, 3)))
        workers.append(Worker(
            id=wid, role="office", competence=comp,
            base_insight_rate=0.5 + comp * 2.0,
            cross_silo_prob=0.3 + comp * 0.3,
            credit_retention=rng.uniform(0.4, 0.7),
        ))
        wid += 1

    # Executive
    for _ in range(n_exec):
        comp = min(1.0, max(0.0, rng.betavariate(3, 3)))
        workers.append(Worker(
            id=wid, role="executive", competence=comp,
            base_insight_rate=0.2 + comp * 1.0,
            cross_silo_prob=0.5 + comp * 0.3,
            credit_retention=rng.uniform(0.85, 0.98),
        ))
        wid += 1

    return workers


def launder_attribution(insight: Insight, workers: list[Worker],
                        rng: random.Random):
    origin = insight.origin_role
    originator = workers[insight.origin_worker_id]
    if rng.random() < originator.credit_retention:
        insight.attributed_role = origin
        insight.attributed_worker_id = insight.origin_worker_id
        insight.was_laundered = False
        return
    insight.was_laundered = True
    if origin == "floor":
        candidates = [w for w in workers if w.role == "office" and not w.exited]
        if candidates:
            chosen = rng.choice(candidates)
            insight.attributed_role = "office"
            insight.attributed_worker_id = chosen.id
        else:
            insight.attributed_role = origin
            insight.attributed_worker_id = insight.origin_worker_id
            insight.was_laundered = False
    elif origin == "office":
        candidates = [w for w in workers if w.role == "executive" and not w.exited]
        if candidates:
            chosen = rng.choice(candidates)
            insight.attributed_role = "executive"
            insight.attributed_worker_id = chosen.id
        else:
            insight.attributed_role = origin
            insight.attributed_worker_id = insight.origin_worker_id
            insight.was_laundered = False
    else:
        insight.attributed_role = origin
        insight.attributed_worker_id = insight.origin_worker_id
        insight.was_laundered = False



# -----------------------------------------------------------------
# QUARTERLY SIMULATION LOOP
# -----------------------------------------------------------------
def simulate(n_floor=50, n_office=15, n_exec=3, quarters=20,
             facility_seed=42, event_seed=7):
    """
    Run quarter-by-quarter, updating trust between quarters
    so that disengagement feeds back into insight generation.
    """
    workers = build_facility(n_floor, n_office, n_exec, seed=facility_seed)
    rng_events = random.Random(event_seed)
    rng_launder = random.Random(event_seed + 1000)

    all_insights = []
    insight_id = 0

    # Track per-quarter metrics
    quarterly_metrics = []

    # Rough max-joules for severity normalization
    # (based on lognormvariate(24, 2) upper tail)
    MAX_J = 1e14

    for q in range(quarters):
        quarter_insights = []

        # 1. Workers generate insights (rate scaled by competence × engagement)
        for w in workers:
            if w.exited:
                continue
            effective_rate = w.base_insight_rate * w.engagement
            n = max(0, int(rng_events.gauss(effective_rate,
                                             effective_rate * 0.4)))
            for _ in range(n):
                # Magnitude scales with competence (more skilled →
                # higher-leverage insights on average)
                mu = 23.0 + w.competence * 2.0  # competent workers ≈ 10x bigger
                magnitude = rng_events.lognormvariate(mu=mu, sigma=1.8)
                sign = 1 if rng_events.random() > 0.08 else -1
                ins = Insight(
                    id=insight_id, quarter=q,
                    origin_role=w.role, origin_worker_id=w.id,
                    downstream_joules=sign * magnitude,
                    cross_silo=(rng_events.random() < w.cross_silo_prob),
                )
                insight_id += 1
                quarter_insights.append(ins)
                all_insights.append(ins)

        # 2. Apply laundering
        for ins in quarter_insights:
            launder_attribution(ins, workers, rng_launder)

        # 3. Update trust for workers whose insights were laundered
        for ins in quarter_insights:
            if ins.was_laundered and ins.downstream_joules > 0:
                originator = workers[ins.origin_worker_id]
                sev = severity_of_capture(ins, MAX_J)
                update_trust_for_laundering(originator, sev)

        # 4. Update engagement based on new trust levels
        for w in workers:
            if not w.exited:
                if w.trust < 0.25:
                    w.quarters_below_25 += 1
                else:
                    w.quarters_below_25 = 0
                update_engagement(w, w.quarters_below_25)

        # 5. Snapshot
        for w in workers:
            w.trust_history.append(w.trust)
            w.engagement_history.append(w.engagement)

        # Aggregate metrics
        floor_active = [w for w in workers if w.role == "floor" and not w.exited]
        high_comp_floor = [w for w in floor_active if w.competence >= 0.75]
        low_comp_floor = [w for w in floor_active if w.competence < 0.50]

        metrics = {
            "quarter": q,
            "total_insights": len(quarter_insights),
            "floor_active": len(floor_active),
            "floor_exited": sum(1 for w in workers
                                 if w.role == "floor" and w.exited),
            "high_comp_trust": (statistics.mean(w.trust for w in high_comp_floor)
                                 if high_comp_floor else 0.0),
            "low_comp_trust": (statistics.mean(w.trust for w in low_comp_floor)
                                if low_comp_floor else 0.0),
            "high_comp_engagement": (statistics.mean(w.engagement
                                                      for w in high_comp_floor)
                                      if high_comp_floor else 0.0),
            "low_comp_engagement": (statistics.mean(w.engagement
                                                     for w in low_comp_floor)
                                     if low_comp_floor else 0.0),
        }
        quarterly_metrics.append(metrics)

    return workers, all_insights, quarterly_metrics


# -----------------------------------------------------------------
# REPORTING
# -----------------------------------------------------------------
def report(workers, insights, metrics, quarters):
    print(f"\n{'='*72}")
    print(f"  TRUST DECAY SIMULATION — {quarters} quarters")
    print(f"{'='*72}")

    # Per-quarter trajectory
    print(f"\n  TRUST TRAJECTORY (floor workers, by competence band)")
    print(f"  {'Q':>3}{'insights':>10}{'active':>8}{'exited':>8}"
          f"{'high-comp trust':>18}{'low-comp trust':>18}")
    print(f"  {'-'*63}")
    for m in metrics:
        print(f"  {m['quarter']:>3}{m['total_insights']:>10}"
              f"{m['floor_active']:>8}{m['floor_exited']:>8}"
              f"{m['high_comp_trust']:>18.3f}{m['low_comp_trust']:>18.3f}")

    # Who exited?
    exited_floor = [w for w in workers if w.role == "floor" and w.exited]
    remaining_floor = [w for w in workers if w.role == "floor" and not w.exited]

    if exited_floor and remaining_floor:
        exit_comp = statistics.mean(w.competence for w in exited_floor)
        remain_comp = statistics.mean(w.competence for w in remaining_floor)
        print(f"\n  EXIT SELECTION (floor workers)")
        print(f"    exited  (n={len(exited_floor):2}): "
              f"mean competence = {exit_comp:.3f}")
        print(f"    remained (n={len(remaining_floor):2}): "
              f"mean competence = {remain_comp:.3f}")
        if exit_comp > remain_comp:
            delta = exit_comp - remain_comp
            print(f"\n  → organization retained LOWER competence on average")
            print(f"    competence gap: {delta:+.3f} "
                  f"({delta/remain_comp*100:+.1f}%)")
            print(f"    this is COMPETENCE EXTINCTION")

    # Cumulative insight loss
    print(f"\n  INSIGHT GENERATION LOSS (vs. full-engagement counterfactual)")
    total_actual = sum(m["total_insights"] for m in metrics)

    # Counterfactual: what if engagement had stayed at 1.0?
    counterfactual = 0
    for w in workers:
        counterfactual += w.base_insight_rate * quarters
    counterfactual = int(counterfactual)

    print(f"    actual insights generated:     {total_actual:>6}")
    print(f"    counterfactual (no decay):    ~{counterfactual:>6}")
    loss = counterfactual - total_actual
    if counterfactual > 0:
        pct = 100 * loss / counterfactual
        print(f"    insights LOST to trust decay:  {loss:>6} ({pct:.1f}%)")


def competence_band_analysis(workers, quarters):
    """Show trust decay curves by competence decile."""
    print(f"\n{'='*72}")
    print(f"  TRUST DECAY CURVE BY COMPETENCE DECILE (floor only)")
    print(f"{'='*72}")

    floor = [w for w in workers if w.role == "floor"]
    floor_sorted = sorted(floor, key=lambda w: w.competence)

    # Split into quintiles
    quintile_size = max(1, len(floor_sorted) // 5)
    bands = {
        "Q1 (lowest comp)":  floor_sorted[:quintile_size],
        "Q2":                floor_sorted[quintile_size:2*quintile_size],
        "Q3":                floor_sorted[2*quintile_size:3*quintile_size],
        "Q4":                floor_sorted[3*quintile_size:4*quintile_size],
        "Q5 (highest comp)": floor_sorted[4*quintile_size:],
    }

    # Print ASCII trust curve
    print(f"\n  {'quarter':>10}" +
          "".join(f"{name:>18}" for name in bands.keys()))
    print(f"  {'-'*(10 + 18*5)}")

    for q in range(0, quarters, max(1, quarters // 10)):
        row = f"  {q:>10}"
        for name, band in bands.items():
            if band:
                trusts = [w.trust_history[q] for w in band
                          if q < len(w.trust_history)]
                if trusts:
                    avg = statistics.mean(trusts)
                    row += f"{avg:>18.3f}"
                else:
                    row += f"{'—':>18}"
            else:
                row += f"{'—':>18}"
        print(row)

    print(f"\n  competence ranges:")
    for name, band in bands.items():
        if band:
            comps = [w.competence for w in band]
            print(f"    {name:<22} n={len(band):>2}  "
                  f"competence [{min(comps):.2f}, {max(comps):.2f}]")


# -----------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------
def run(quarters=20, seeds=3):
    """Run multiple seeds, report on the first in detail, aggregate the rest."""
    all_runs = []
    for s in range(seeds):
        workers, insights, metrics = simulate(
            quarters=quarters, facility_seed=42+s, event_seed=7+s*3)
        all_runs.append((workers, insights, metrics))

    # Detailed report on first run
    workers, insights, metrics = all_runs[0]
    report(workers, insights, metrics, quarters)
    competence_band_analysis(workers, quarters)

    # Cross-seed summary
    print(f"\n{'='*72}")
    print(f"  CROSS-SEED SUMMARY ({seeds} seeds)")
    print(f"{'='*72}")
    print(f"  {'seed':>6}{'floor exited':>14}{'exit comp':>14}"
          f"{'remain comp':>14}{'comp gap':>12}")
    print(f"  {'-'*60}")
    for i, (workers, _, _) in enumerate(all_runs):
        exited = [w for w in workers if w.role == "floor" and w.exited]
        remain = [w for w in workers if w.role == "floor" and not w.exited]
        ec = statistics.mean(w.competence for w in exited) if exited else 0
        rc = statistics.mean(w.competence for w in remain) if remain else 0
        gap = ec - rc
        print(f"  {i:>6}{len(exited):>14}{ec:>14.3f}{rc:>14.3f}{gap:>+12.3f}")

    return all_runs


if __name__ == "__main__":
    run(quarters=20, seeds=3)


"""
full_system.py
==============
Full coupled attribution/trust/burnout/reform simulation.

LAYERS
------
1. LEGITIMATE OFFICE SYNTHESIS
   Some office insights require capabilities floor genuinely lacks:
     - capital allocation (needs P&L + forecasting access)
     - legal/regulatory interface (needs counsel relationships)
     - cross-facility synthesis (needs multi-site data access)
     - external negotiation (needs authority + mandate)
   These are tagged `legitimate=True` and NOT laundered from floor.
   Their value is real. The sim must not conflate them with capture.

2. NETWORK EFFECTS
   Cross-silo insights often emerge from 2-5 person chains:
     driver notices → mechanic confirms → dispatcher routes around
   Current system assigns ALL credit to one reporter.
   Provenance audit distributes credit across the chain.

3. TEMPORAL DECAY
   Floor insights: value manifests in days-weeks (immediate)
   Office synthesis: value manifests in months-years (latent)
   Model this with a `realization_delay` field in quarters.
   Reform interventions must wait for office synthesis to prove itself.

4. SUPPRESSION
   Some floor insights are killed before reaching reporting:
     - threatens someone's position     → supervisor buries it
     - challenges official narrative    → quietly dismissed
     - requires capex to act on         → deprioritized
   Suppressed insights generate trust decay for the originator
   (they KNOW it was suppressed, even if no one else does).

5. BURNOUT (physical/cognitive, not just trust)
   Long-haul workers: sleep debt, vibration exposure, irregular meals
   Disengagement under capture AMPLIFIES physical burnout because
   the compensating mechanisms (meaning, recognition) are absent.
   Burnout reduces insight_rate independent of engagement.

6. REPLACEMENT DYNAMICS (social transmission)
   New hires don't arrive with fixed traits.
   Their effective trust/engagement = weighted avg of the
   floor workers they socially contact in first N quarters.
   If the floor is already cynical, new hires converge DOWN.
   If the floor is healthy, new hires converge UP.

7. REFORM INTERVENTION
   At quarter `reform_quarter`, credit_retention for all roles
   jumps to a symmetric target (e.g. 0.85 across the board).
   The sim measures:
     - how fast trust recovers
     - whether the competent workers already exited can be replaced
     - whether the remaining floor has enough skill to TEACH new hires

POINT-OF-NO-RETURN THEOREM
--------------------------
There exists a quarter Q* beyond which reform cannot restore
pre-capture generative capacity, because:
  - the competent workers who would have taught new hires are gone
  - the current floor teaches new hires disengagement
  - new hires' social-transmission-adjusted trust never exceeds
    the current floor average

This sim tests whether Q* exists and where it is.

CC0. Stdlib only.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional
import random
import statistics
import math

from attribution_sim import ENERGY_INPUTS, total_energy_in, JOULES_PER_DOLLAR, fmt_j


# =================================================================
# EXTENDED WORKER
# =================================================================
@dataclass
class Worker:
    id: int
    role: Literal["floor", "office", "executive"]
    competence: float
    base_insight_rate: float
    cross_silo_prob: float
    credit_retention: float

    # Legitimate synthesis capability (office+exec only, mostly)
    legitimate_synthesis_rate: float = 0.0   # qty of legit synthesis/qtr
    legitimate_access: bool = False           # has capital/legal/multi-site access

    # Trust + engagement
    trust: float = 1.0
    engagement: float = 1.0
    exited: bool = False
    quarters_below_25: int = 0

    # Burnout (physical/cognitive, separate from trust)
    burnout: float = 0.0         # [0, 1], 1 = incapacitated
    recovery_capacity: float = 1.0  # innate resilience

    # Network position
    network_neighbors: list[int] = field(default_factory=list)

    # Tenure (for replacement/socialization)
    tenure_quarters: int = 12    # starts as experienced by default
    is_new_hire: bool = False

    # History
    capture_events_witnessed: int = 0
    suppression_events_witnessed: int = 0
    trust_history: list = field(default_factory=list)
    engagement_history: list = field(default_factory=list)
    burnout_history: list = field(default_factory=list)


@dataclass
class Insight:
    id: int
    quarter: int
    origin_role: str
    origin_worker_id: int
    downstream_joules: float
    cross_silo: bool

    # New fields
    legitimate: bool = False              # genuine office synthesis
    network_contributors: list[int] = field(default_factory=list)
    realization_delay: int = 0             # quarters until value manifests
    suppressed: bool = False                # killed before reporting

    attributed_role: str = ""
    attributed_worker_id: int = -1
    was_laundered: bool = False


# =================================================================
# CONSTANTS
# =================================================================
# Burnout parameters
BURNOUT_GAIN_PER_QTR       = 0.04   # baseline accumulation under load
BURNOUT_DISENGAGEMENT_GAIN = 0.08   # amplification when disengaged
BURNOUT_RECOVERY_ENGAGED   = 0.03   # passive recovery when engaged
BURNOUT_INSIGHT_PENALTY    = 0.6    # max fraction of insight rate lost

# Legitimate synthesis parameters
OFFICE_LEGIT_SYNTHESIS_FRACTION = 0.25  # of office insights, this fraction
                                         # is legitimately office-generated
EXEC_LEGIT_SYNTHESIS_FRACTION   = 0.55

# Network parameters
FLOOR_NETWORK_DEGREE = 5    # avg number of floor connections per floor worker
CROSS_ROLE_DEGREE    = 2

# Suppression parameters
SUPPRESSION_PROB_FLOOR = 0.20   # 20% of positive floor insights suppressed
SUPPRESSION_PROB_OFFICE = 0.05

# Temporal decay parameters
# Floor insights realize in 0-2 quarters; office 2-8; exec 4-16
FLOOR_DELAY_RANGE  = (0, 2)
OFFICE_DELAY_RANGE = (2, 8)
EXEC_DELAY_RANGE   = (4, 16)

# Socialization: new hires' trust converges toward neighbors over
# `SOCIALIZATION_WINDOW` quarters, with weight `SOCIAL_ABSORPTION`.
SOCIALIZATION_WINDOW   = 4
SOCIAL_ABSORPTION      = 0.4

# Reform
SYMMETRIC_RETENTION_TARGET = 0.85


# =================================================================
# FACILITY CONSTRUCTION
# =================================================================
def build_facility(n_floor=50, n_office=15, n_exec=3, seed=42) -> list[Worker]:
    rng = random.Random(seed)
    workers = []
    wid = 0

    for _ in range(n_floor):
        comp = min(1.0, max(0.0, rng.betavariate(5, 3)))
        workers.append(Worker(
            id=wid, role="floor", competence=comp,
            base_insight_rate=2.0 + comp * 5.0,
            cross_silo_prob=0.4 + comp * 0.3,
            credit_retention=rng.uniform(0.05, 0.20),
            recovery_capacity=rng.uniform(0.6, 1.2),
            tenure_quarters=rng.randint(4, 40),
        ))
        wid += 1

    for _ in range(n_office):
        comp = min(1.0, max(0.0, rng.betavariate(4, 3)))
        # Some office workers have legitimate synthesis access
        has_access = rng.random() < 0.4
        legit_rate = (rng.uniform(0.3, 1.2) * comp) if has_access else 0.0
        workers.append(Worker(
            id=wid, role="office", competence=comp,
            base_insight_rate=0.5 + comp * 2.0,
            cross_silo_prob=0.3 + comp * 0.3,
            credit_retention=rng.uniform(0.4, 0.7),
            legitimate_synthesis_rate=legit_rate,
            legitimate_access=has_access,
            recovery_capacity=rng.uniform(0.8, 1.2),
            tenure_quarters=rng.randint(4, 40),
        ))
        wid += 1

    for _ in range(n_exec):
        comp = min(1.0, max(0.0, rng.betavariate(3, 3)))
        legit_rate = rng.uniform(0.5, 1.5) * comp
        workers.append(Worker(
            id=wid, role="executive", competence=comp,
            base_insight_rate=0.2 + comp * 1.0,
            cross_silo_prob=0.5 + comp * 0.3,
            credit_retention=rng.uniform(0.85, 0.98),
            legitimate_synthesis_rate=legit_rate,
            legitimate_access=True,
            recovery_capacity=rng.uniform(0.9, 1.2),
            tenure_quarters=rng.randint(8, 60),
        ))
        wid += 1

    # Build network
    _build_network(workers, rng)
    return workers


def _build_network(workers: list[Worker], rng: random.Random):
    floor = [w for w in workers if w.role == "floor"]
    office = [w for w in workers if w.role == "office"]
    exec_ = [w for w in workers if w.role == "executive"]

    # Floor-floor connections
    for w in floor:
        neighbors = rng.sample([o.id for o in floor if o.id != w.id],
                               min(FLOOR_NETWORK_DEGREE, len(floor) - 1))
        w.network_neighbors.extend(neighbors)

    # Cross-role: each floor connects to 1-2 office
    for w in floor:
        if office:
            neighbors = rng.sample([o.id for o in office],
                                   min(CROSS_ROLE_DEGREE, len(office)))
            w.network_neighbors.extend(neighbors)

    # Office-office and office-exec
    for w in office:
        if office:
            neighbors = rng.sample([o.id for o in office if o.id != w.id],
                                   min(3, len(office) - 1))
            w.network_neighbors.extend(neighbors)
        if exec_:
            neighbors = rng.sample([e.id for e in exec_],
                                   min(1, len(exec_)))
            w.network_neighbors.extend(neighbors)




# =================================================================
# DETECTION + TRUST DYNAMICS
# =================================================================
def detection_rate(w: Worker) -> float:
    return 0.02 + 0.28 * w.competence


def update_trust(w: Worker, severity: float, event_type: str = "laundering"):
    dr = detection_rate(w)
    # Suppression is more damaging than laundering because the worker
    # knows their insight was actively killed, not just misattributed.
    mult = 1.0 if event_type == "laundering" else 1.6
    decay = dr * severity * 0.15 * mult
    w.trust = max(0.0, w.trust - decay)
    if event_type == "laundering":
        w.capture_events_witnessed += 1
    else:
        w.suppression_events_witnessed += 1


def update_engagement(w: Worker):
    t = w.trust
    if t >= 0.7:
        w.engagement = 1.0
    elif t >= 0.4:
        w.engagement = 0.3 + (t - 0.4) * (0.7 / 0.3)
    elif t >= 0.15:
        w.engagement = 0.1 + (t - 0.15) * (0.2 / 0.25)
    else:
        w.engagement = 0.05

    if t < 0.10:
        w.exited = True
        w.engagement = 0.0
    elif t < 0.25 and w.quarters_below_25 >= 3:
        w.exited = True
        w.engagement = 0.0


# =================================================================
# BURNOUT DYNAMICS
# =================================================================
def update_burnout(w: Worker):
    """
    Burnout accumulates under work load, amplified by disengagement.
    Recovery happens when engaged and trust is healthy.
    """
    if w.engagement >= 0.7 and w.trust >= 0.5:
        # Active recovery
        delta = -BURNOUT_RECOVERY_ENGAGED * w.recovery_capacity
    else:
        # Accumulation, amplified by disengagement
        gain = BURNOUT_GAIN_PER_QTR
        if w.engagement < 0.5:
            gain += BURNOUT_DISENGAGEMENT_GAIN * (1 - w.engagement)
        delta = gain / w.recovery_capacity

    w.burnout = max(0.0, min(1.0, w.burnout + delta))


def burnout_multiplier(w: Worker) -> float:
    """Returns multiplier on effective insight rate, [1 - penalty, 1]."""
    return 1.0 - BURNOUT_INSIGHT_PENALTY * w.burnout


# =================================================================
# SUPPRESSION
# =================================================================
def maybe_suppress(ins: Insight, rng: random.Random) -> bool:
    if ins.downstream_joules <= 0:
        return False
    if ins.origin_role == "floor":
        return rng.random() < SUPPRESSION_PROB_FLOOR
    if ins.origin_role == "office":
        return rng.random() < SUPPRESSION_PROB_OFFICE
    return False


# =================================================================
# NETWORK-DISTRIBUTED AUTHORSHIP
# =================================================================
def assign_network_contributors(ins: Insight, workers: list[Worker],
                                 rng: random.Random):
    """
    Cross-silo insights are often 2-5 person chains.
    Credit should distribute across that chain in provenance audit.
    """
    if not ins.cross_silo:
        return
    originator = workers[ins.origin_worker_id]
    n_contrib = rng.randint(1, 4)  # 1-4 additional contributors
    if originator.network_neighbors:
        contrib = rng.sample(
            originator.network_neighbors,
            min(n_contrib, len(originator.network_neighbors))
        )
        ins.network_contributors = contrib


# =================================================================
# ATTRIBUTION LAUNDERING
# =================================================================
def launder(ins: Insight, workers: list[Worker], rng: random.Random,
            reformed: bool = False):
    # Legitimate office/exec synthesis is never laundered
    # (it genuinely originated there)
    if ins.legitimate:
        ins.attributed_role = ins.origin_role
        ins.attributed_worker_id = ins.origin_worker_id
        return

    originator = workers[ins.origin_worker_id]
    retention = (SYMMETRIC_RETENTION_TARGET if reformed
                 else originator.credit_retention)

    if rng.random() < retention:
        ins.attributed_role = ins.origin_role
        ins.attributed_worker_id = ins.origin_worker_id
        ins.was_laundered = False
        return

    ins.was_laundered = True
    if ins.origin_role == "floor":
        pool = [w for w in workers if w.role == "office" and not w.exited]
        if pool:
            ch = rng.choice(pool)
            ins.attributed_role = "office"
            ins.attributed_worker_id = ch.id
            return
    elif ins.origin_role == "office":
        pool = [w for w in workers if w.role == "executive" and not w.exited]
        if pool:
            ch = rng.choice(pool)
            ins.attributed_role = "executive"
            ins.attributed_worker_id = ch.id
            return
    # fallback
    ins.attributed_role = ins.origin_role
    ins.attributed_worker_id = ins.origin_worker_id
    ins.was_laundered = False


# =================================================================
# SOCIALIZATION (new hires converge toward neighbors)
# =================================================================
def socialize_new_hire(new_hire: Worker, workers: list[Worker]):
    """
    New hires' trust/engagement move toward the weighted mean of
    their floor neighbors' trust over the socialization window.
    """
    if not new_hire.is_new_hire:
        return
    if new_hire.tenure_quarters > SOCIALIZATION_WINDOW:
        new_hire.is_new_hire = False
        return
    floor_neighbors = [workers[i] for i in new_hire.network_neighbors
                       if workers[i].role == "floor" and not workers[i].exited]
    if not floor_neighbors:
        return
    target_trust = statistics.mean(w.trust for w in floor_neighbors)
    target_burnout = statistics.mean(w.burnout for w in floor_neighbors)

    # Pull toward target
    new_hire.trust = ((1 - SOCIAL_ABSORPTION) * new_hire.trust
                      + SOCIAL_ABSORPTION * target_trust)
    new_hire.burnout = ((1 - SOCIAL_ABSORPTION) * new_hire.burnout
                        + SOCIAL_ABSORPTION * target_burnout)


# =================================================================
# REPLACEMENT
# =================================================================
def replace_exits(workers: list[Worker], rng: random.Random, quarter: int):
    """
    For each exited worker, hire a replacement of the same role.
    New hires:
      - have competence drawn from SAME distribution as originals
      - start with trust=0.9 (hopeful but not naive)
      - will socialize toward floor neighbors over SOCIALIZATION_WINDOW
    """
    new_hires = []
    for w in workers:
        if w.exited and getattr(w, "replaced", False):
            continue  # already replaced
        if not w.exited:
            continue

        # Generate replacement
        if w.role == "floor":
            comp = min(1.0, max(0.0, rng.betavariate(5, 3)))
            rate = 2.0 + comp * 5.0
            xs_prob = 0.4 + comp * 0.3
            retention = rng.uniform(0.05, 0.20)
            legit_rate = 0.0
            legit_access = False
        elif w.role == "office":
            comp = min(1.0, max(0.0, rng.betavariate(4, 3)))
            rate = 0.5 + comp * 2.0
            xs_prob = 0.3 + comp * 0.3
            retention = rng.uniform(0.4, 0.7)
            legit_access = rng.random() < 0.4
            legit_rate = (rng.uniform(0.3, 1.2) * comp) if legit_access else 0.0
        else:
            comp = min(1.0, max(0.0, rng.betavariate(3, 3)))
            rate = 0.2 + comp * 1.0
            xs_prob = 0.5 + comp * 0.3
            retention = rng.uniform(0.85, 0.98)
            legit_rate = rng.uniform(0.5, 1.5) * comp
            legit_access = True

        new_id = max(worker.id for worker in workers) + 1 + len(new_hires)
        replacement = Worker(
            id=new_id, role=w.role, competence=comp,
            base_insight_rate=rate, cross_silo_prob=xs_prob,
            credit_retention=retention,
            legitimate_synthesis_rate=legit_rate,
            legitimate_access=legit_access,
            trust=0.9,
            recovery_capacity=rng.uniform(0.6, 1.2),
            tenure_quarters=0,
            is_new_hire=True,
            network_neighbors=list(w.network_neighbors),  # inherit network
        )
        new_hires.append(replacement)
        w.replaced = True  # mark so we don't re-replace

    workers.extend(new_hires)




# =================================================================
# MAIN LOOP
# =================================================================
def simulate(quarters=24,
             reform_quarter: Optional[int] = None,
             n_floor=50, n_office=15, n_exec=3,
             facility_seed=42, event_seed=7):

    workers = build_facility(n_floor, n_office, n_exec, seed=facility_seed)
    rng_events = random.Random(event_seed)
    rng_launder = random.Random(event_seed + 1000)
    rng_suppress = random.Random(event_seed + 2000)
    rng_hire = random.Random(event_seed + 3000)

    MAX_J = 1e14
    all_insights = []
    insight_id = 0
    quarterly = []

    for q in range(quarters):
        reformed = reform_quarter is not None and q >= reform_quarter
        quarter_insights = []

        # 1. Generate insights
        for w in workers:
            if w.exited:
                continue

            # Effective rate: engagement × burnout
            eff_rate = (w.base_insight_rate * w.engagement
                        * burnout_multiplier(w))
            n = max(0, int(rng_events.gauss(eff_rate, eff_rate * 0.4)))
            for _ in range(n):
                # Determine if legitimate synthesis
                legit = False
                if w.role == "office" and w.legitimate_access:
                    if rng_events.random() < OFFICE_LEGIT_SYNTHESIS_FRACTION:
                        legit = True
                elif w.role == "executive":
                    if rng_events.random() < EXEC_LEGIT_SYNTHESIS_FRACTION:
                        legit = True

                mu = 23.0 + w.competence * 2.0
                if legit:
                    mu += 0.8  # legit synthesis has higher mean magnitude
                magnitude = rng_events.lognormvariate(mu=mu, sigma=1.8)
                sign = 1 if rng_events.random() > 0.08 else -1

                # Realization delay
                if w.role == "floor":
                    delay = rng_events.randint(*FLOOR_DELAY_RANGE)
                elif w.role == "office":
                    delay = rng_events.randint(*OFFICE_DELAY_RANGE)
                else:
                    delay = rng_events.randint(*EXEC_DELAY_RANGE)

                ins = Insight(
                    id=insight_id, quarter=q,
                    origin_role=w.role, origin_worker_id=w.id,
                    downstream_joules=sign * magnitude,
                    cross_silo=(rng_events.random() < w.cross_silo_prob),
                    legitimate=legit,
                    realization_delay=delay,
                )
                insight_id += 1

                # Network contributors
                assign_network_contributors(ins, workers, rng_events)

                # Suppression check
                if maybe_suppress(ins, rng_suppress):
                    ins.suppressed = True

                quarter_insights.append(ins)
                all_insights.append(ins)

        # 2. Launder non-suppressed insights
        for ins in quarter_insights:
            if ins.suppressed:
                continue
            launder(ins, workers, rng_launder, reformed=reformed)

        # 3. Update trust
        for ins in quarter_insights:
            if ins.downstream_joules <= 0:
                continue
            sev = math.log10(max(ins.downstream_joules, 1.0)) / math.log10(MAX_J)
            sev = min(1.0, max(0.0, sev))

            if ins.suppressed:
                # Originator knows
                update_trust(workers[ins.origin_worker_id], sev, "suppression")
            elif ins.was_laundered:
                update_trust(workers[ins.origin_worker_id], sev, "laundering")
                # Network contributors also witness (their work was part of it)
                for cid in ins.network_contributors:
                    if cid < len(workers):
                        # Reduced severity for contributors
                        update_trust(workers[cid], sev * 0.4, "laundering")

        # 4. Update engagement + burnout + tenure
        for w in workers:
            if w.exited:
                continue
            if w.trust < 0.25:
                w.quarters_below_25 += 1
            else:
                w.quarters_below_25 = 0
            update_engagement(w)
            update_burnout(w)
            w.tenure_quarters += 1

        # 5. Socialize new hires
        for w in workers:
            if w.is_new_hire:
                socialize_new_hire(w, workers)

        # 6. Replace exits (lagged by 1 quarter — hiring takes time)
        if q > 0:
            replace_exits(workers, rng_hire, q)

        # 7. Snapshot
        for w in workers:
            w.trust_history.append(w.trust)
            w.engagement_history.append(w.engagement)
            w.burnout_history.append(w.burnout)

        # Metrics
        floor_active = [w for w in workers if w.role == "floor" and not w.exited]
        floor_total_exited = sum(1 for w in workers
                                  if w.role == "floor" and w.exited)
        floor_original = [w for w in workers if w.role == "floor"
                          and w.tenure_quarters >= q + 4]  # originals only
        quarterly.append({
            "q": q,
            "insights": len(quarter_insights),
            "suppressed": sum(1 for i in quarter_insights if i.suppressed),
            "laundered":  sum(1 for i in quarter_insights if i.was_laundered),
            "legitimate": sum(1 for i in quarter_insights if i.legitimate),
            "floor_active": len(floor_active),
            "floor_exited_cum": floor_total_exited,
            "floor_avg_trust": (statistics.mean(w.trust for w in floor_active)
                                if floor_active else 0),
            "floor_avg_burnout": (statistics.mean(w.burnout for w in floor_active)
                                   if floor_active else 0),
            "floor_avg_comp": (statistics.mean(w.competence for w in floor_active)
                                if floor_active else 0),
            "new_hire_trust": (statistics.mean(w.trust for w in floor_active
                                                 if w.is_new_hire)
                                if any(w.is_new_hire for w in floor_active)
                                else 0),
            "reformed": reformed,
        })

    return workers, all_insights, quarterly


# =================================================================
# REPORTING
# =================================================================
def print_trajectory(label, quarterly):
    print(f"\n{'='*82}")
    print(f"  {label}")
    print(f"{'='*82}")
    print(f"  {'Q':>3}{'ins':>5}{'sup':>4}{'lnd':>4}{'leg':>4}"
          f"{'active':>8}{'exit':>6}{'trust':>8}{'burn':>7}"
          f"{'comp':>7}{'newH_trust':>12}{'ref':>5}")
    print(f"  {'-'*73}")
    for m in quarterly:
        r_flag = "✓" if m["reformed"] else " "
        nh = f"{m['new_hire_trust']:.2f}" if m['new_hire_trust'] > 0 else "—"
        print(f"  {m['q']:>3}{m['insights']:>5}{m['suppressed']:>4}"
              f"{m['laundered']:>4}{m['legitimate']:>4}"
              f"{m['floor_active']:>8}{m['floor_exited_cum']:>6}"
              f"{m['floor_avg_trust']:>8.3f}{m['floor_avg_burnout']:>7.2f}"
              f"{m['floor_avg_comp']:>7.3f}{nh:>12}{r_flag:>5}")


def summarize(workers, insights, quarterly, label):
    floor_all = [w for w in workers if w.role == "floor"]
    floor_active = [w for w in floor_all if not w.exited]
    floor_exited = [w for w in floor_all if w.exited]

    total_ins = len(insights)
    laundered = sum(1 for i in insights if i.was_laundered)
    suppressed = sum(1 for i in insights if i.suppressed)
    legitimate = sum(1 for i in insights if i.legitimate)
    cross_silo = sum(1 for i in insights if i.cross_silo)

    print(f"\n{'─'*82}")
    print(f"  SUMMARY: {label}")
    print(f"{'─'*82}")
    print(f"  insights total:       {total_ins}")
    print(f"    laundered:          {laundered} ({100*laundered/max(total_ins,1):.1f}%)")
    print(f"    suppressed:         {suppressed} ({100*suppressed/max(total_ins,1):.1f}%)")
    print(f"    legitimate office:  {legitimate} ({100*legitimate/max(total_ins,1):.1f}%)")
    print(f"    cross-silo:         {cross_silo} ({100*cross_silo/max(total_ins,1):.1f}%)")
    print(f"  floor workers active: {len(floor_active)} / exited: {len(floor_exited)}")
    if floor_exited:
        ec = statistics.mean(w.competence for w in floor_exited)
        print(f"    mean exit comp:     {ec:.3f}")
    if floor_active:
        ac = statistics.mean(w.competence for w in floor_active)
        ab = statistics.mean(w.burnout for w in floor_active)
        at = statistics.mean(w.trust for w in floor_active)
        print(f"    mean active comp:   {ac:.3f}")
        print(f"    mean active burnout: {ab:.3f}")
        print(f"    mean active trust:  {at:.3f}")


# =================================================================
# POINT OF NO RETURN EXPERIMENT
# =================================================================
def point_of_no_return():
    """
    Run the sim with reform triggered at different quarters.
    Measure final state (insight rate, active competence, trust).

    Hypothesis: there exists a reform_quarter beyond which reform
    cannot restore pre-capture generative capacity.
    """
    print(f"\n{'='*82}")
    print(f"  POINT OF NO RETURN EXPERIMENT")
    print(f"  Same facility, same events, varying reform timing")
    print(f"{'='*82}")
    print(f"  {'reform_Q':>10}{'final Q24':>30}{'active comp':>14}{'trust':>10}"
          f"{'ins/qtr last 4':>18}")
    print(f"  {'-'*82}")

    configs = [None, 0, 4, 8, 12, 16, 20]  # None = no reform (control)
    results = []

    for rq in configs:
        workers, insights, quarterly = simulate(
            quarters=24, reform_quarter=rq,
            facility_seed=42, event_seed=7)
        floor_active = [w for w in workers if w.role == "floor" and not w.exited]
        ac = (statistics.mean(w.competence for w in floor_active)
              if floor_active else 0)
        at = (statistics.mean(w.trust for w in floor_active)
              if floor_active else 0)
        last4 = statistics.mean(m["insights"] for m in quarterly[-4:])
        label = "no reform" if rq is None else f"reform @ Q{rq}"
        print(f"  {label:>10}{'':>20}{len(floor_active):>10} act"
              f"{ac:>14.3f}{at:>10.3f}{last4:>18.1f}")
        results.append((rq, len(floor_active), ac, at, last4))

    # Find the point where reform stops helping
    print(f"\n  INTERPRETATION:")
    baseline_no_reform = [r for r in results if r[0] is None][0]
    best_reform = max((r for r in results if r[0] is not None),
                       key=lambda r: r[4])
    print(f"    no reform:       {baseline_no_reform[4]:.1f} insights/qtr (final)")
    print(f"    best reform:     Q{best_reform[0]} → {best_reform[4]:.1f} insights/qtr")

    # Find last reform quarter that still helps meaningfully
    threshold = baseline_no_reform[4] * 1.5
    effective = [r for r in results if r[0] is not None and r[4] >= threshold]
    if effective:
        latest_effective = max(effective, key=lambda r: r[0])
        print(f"    latest effective reform: Q{latest_effective[0]}")
        print(f"    → point of no return appears around Q{latest_effective[0]+1}-Q{latest_effective[0]+4}")
    else:
        print(f"    no reform crossed effectiveness threshold")
    return results


# =================================================================
# MAIN
# =================================================================
if __name__ == "__main__":
    # Baseline: no reform
    print(f"\n{'#'*82}")
    print(f"#  SCENARIO 1: NO REFORM (baseline)")
    print(f"{'#'*82}")
    workers, insights, quarterly = simulate(quarters=24, reform_quarter=None,
                                             facility_seed=42, event_seed=7)
    print_trajectory("NO REFORM", quarterly)
    summarize(workers, insights, quarterly, "NO REFORM")

    # Early reform
    print(f"\n{'#'*82}")
    print(f"#  SCENARIO 2: EARLY REFORM (Q4)")
    print(f"{'#'*82}")
    workers, insights, quarterly = simulate(quarters=24, reform_quarter=4,
                                             facility_seed=42, event_seed=7)
    print_trajectory("REFORM AT Q4", quarterly)
    summarize(workers, insights, quarterly, "REFORM AT Q4")

    # Late reform
    print(f"\n{'#'*82}")
    print(f"#  SCENARIO 3: LATE REFORM (Q16)")
    print(f"{'#'*82}")
    workers, insights, quarterly = simulate(quarters=24, reform_quarter=16,
                                             facility_seed=42, event_seed=7)
    print_trajectory("REFORM AT Q16", quarterly)
    summarize(workers, insights, quarterly, "REFORM AT Q16")

    # Point of no return sweep
    point_of_no_return()

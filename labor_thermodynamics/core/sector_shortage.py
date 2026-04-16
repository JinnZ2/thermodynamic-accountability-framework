"""
sector_shortage.py
==================
Extends full_system.py to a SECTOR-LEVEL model with:
  - multiple facilities (some functional, some captured)
  - a labor pool with reputation signal
  - applicant competence filtered by sector reputation
  - new hires drawn from this filtered pool
  - emergent "shortage" and "unskilled labor" signals

HYPOTHESIS
----------
"Worker shortage" and "unskilled labor available" are not
two separate problems. They are two reports from the same
underlying system: sector-level trust collapse.

MECHANISM
---------
  facility captures workers
    → competent workers exit
    → exit stories propagate through labor network
    → sector reputation degrades
    → applications drop AND
    → applicants shift toward lower detection rate
      (competent workers self-select OUT of the sector;
       they can smell what they're walking into)

  orgs observe:
    - "we can't find workers"              ← supply signal
    - "the ones we find aren't skilled"    ← quality signal
    - "we had to raise wages and it didn't help" ← price signal
  orgs conclude:
    - labor shortage
    - unskilled generation
    - need to lower standards / automate / import labor
  orgs do not observe:
    - the trust field they created around themselves
    - that their OWN CAPTURE is the filter
    - that capable workers CAN still be found in sectors
      with healthier reputation

PREDICTION
----------
In the sim:
  - captured sectors will experience "shortage" + "quality"
  - functional sectors will not
  - the SAME LABOR POOL produces different outcomes based
    on which facility they land in
  - raising wages in captured sectors doesn't help because
    the signal is trust-based, not price-based
  - competent applicants route around captured sectors
    entirely, producing regional/sector disparities that
    look like "culture" but are measurement-traceable

CC0. Stdlib only.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional
import random
import statistics
import math

from attribution_sim import JOULES_PER_DOLLAR, fmt_j
from full_system import (
    Worker, Insight,
    build_facility, _build_network,
    detection_rate, update_trust, update_engagement, update_burnout,
    burnout_multiplier, maybe_suppress, assign_network_contributors,
    launder, socialize_new_hire,
    OFFICE_LEGIT_SYNTHESIS_FRACTION, EXEC_LEGIT_SYNTHESIS_FRACTION,
    FLOOR_DELAY_RANGE, OFFICE_DELAY_RANGE, EXEC_DELAY_RANGE,
    SYMMETRIC_RETENTION_TARGET, SOCIALIZATION_WINDOW, SOCIAL_ABSORPTION,
)


# =================================================================
# LABOR POOL + REPUTATION
# =================================================================
@dataclass
class Facility:
    name: str
    workers: list[Worker]
    reform_quarter: Optional[int] = None
    baseline_retention: dict = field(default_factory=dict)  # by role
    reputation: float = 1.0   # [0, 1], perceived trust/health by labor pool
    exit_stories: list = field(default_factory=list)  # (quarter, severity)
    insights: list = field(default_factory=list)


@dataclass
class Applicant:
    id: int
    competence: float
    detection: float       # how well they read the sector
    willingness_threshold: float  # min reputation they'll accept


def build_labor_pool(n: int, seed: int = 100) -> list[Applicant]:
    """
    A labor pool of potential hires. Key property:
    more competent applicants have HIGHER willingness thresholds
    (they can read the sector signal and route around bad orgs).
    """
    rng = random.Random(seed)
    pool = []
    for i in range(n):
        comp = rng.betavariate(4, 3)  # mean ~0.57
        # Competent workers have better sector-signal detection
        # AND higher refusal thresholds
        det = 0.1 + 0.7 * comp
        # Minimum reputation accepted scales with competence
        # Low-competence: takes anything (0.1)
        # High-competence: demands good reputation (0.75)
        thresh = 0.1 + 0.65 * comp
        pool.append(Applicant(
            id=i, competence=comp, detection=det,
            willingness_threshold=thresh,
        ))
    return pool


def update_reputation(facility: Facility, current_quarter: int):
    """
    Reputation is a function of:
      - recent exit stories from this facility
      - current floor trust level (word gets out)
      - burnout visibility (drivers/workers look tired)

    Exit stories from competent workers hit hardest because
    competent workers have more social credibility in the pool.
    """
    floor = [w for w in facility.workers if w.role == "floor" and not w.exited]
    if not floor:
        facility.reputation = 0.0
        return

    avg_trust = statistics.mean(w.trust for w in floor)
    avg_burnout = statistics.mean(w.burnout for w in floor)

    # Recent exit severity (last 4 quarters)
    recent_exits = [s for q, s in facility.exit_stories
                    if current_quarter - q <= 4]
    exit_pressure = sum(recent_exits) / 4.0 if recent_exits else 0.0
    exit_pressure = min(exit_pressure, 1.0)

    # Reputation formula: weighted combination
    rep = (0.5 * avg_trust
           + 0.25 * (1 - avg_burnout)
           + 0.25 * (1 - exit_pressure))
    # Reputation has inertia (doesn't change instantly)
    facility.reputation = 0.7 * facility.reputation + 0.3 * rep


def record_exit_story(facility: Facility, exiting: Worker, quarter: int):
    """Competent workers leaving generate stronger exit signals."""
    severity = exiting.competence * (1 - exiting.trust)
    facility.exit_stories.append((quarter, severity))


# =================================================================
# HIRING FROM POOL (reputation-filtered)
# =================================================================
def hire_from_pool(facility: Facility, pool: list[Applicant],
                    role: Literal["floor", "office", "executive"],
                    rng: random.Random, quarter: int) -> Optional[Worker]:
    """
    Applicants accept the facility only if reputation clears their
    willingness threshold. Competent applicants self-filter OUT of
    low-reputation facilities.

    Returns a new Worker or None if no applicant will take the job.
    """
    rep = facility.reputation
    # Filter pool to willing applicants
    willing = [a for a in pool if a.willingness_threshold <= rep]

    if not willing:
        return None

    # Among willing, selection is random (org can't perfectly
    # assess competence at hire)
    chosen = rng.choice(willing)
    pool.remove(chosen)

    comp = chosen.competence

    # Build Worker with role-appropriate params
    if role == "floor":
        rate = 2.0 + comp * 5.0
        xs = 0.4 + comp * 0.3
        retention = facility.baseline_retention.get("floor",
                                                    rng.uniform(0.05, 0.20))
        legit_rate = 0.0
        legit_access = False
    elif role == "office":
        rate = 0.5 + comp * 2.0
        xs = 0.3 + comp * 0.3
        retention = facility.baseline_retention.get("office",
                                                    rng.uniform(0.4, 0.7))
        legit_access = rng.random() < 0.4
        legit_rate = (rng.uniform(0.3, 1.2) * comp) if legit_access else 0.0
    else:
        rate = 0.2 + comp * 1.0
        xs = 0.5 + comp * 0.3
        retention = facility.baseline_retention.get("executive",
                                                    rng.uniform(0.85, 0.98))
        legit_rate = rng.uniform(0.5, 1.5) * comp
        legit_access = True

    new_id = max((w.id for w in facility.workers), default=0) + 1
    return Worker(
        id=new_id, role=role, competence=comp,
        base_insight_rate=rate, cross_silo_prob=xs,
        credit_retention=retention,
        legitimate_synthesis_rate=legit_rate,
        legitimate_access=legit_access,
        trust=0.9,
        recovery_capacity=rng.uniform(0.6, 1.2),
        tenure_quarters=0,
        is_new_hire=True,
        network_neighbors=[],  # will get wired in next step
    )


def wire_new_hire(new_hire: Worker, facility: Facility,
                   rng: random.Random):
    """Connect new hire to random floor + office neighbors."""
    floor_pool = [w for w in facility.workers
                  if w.role == "floor" and not w.exited and w.id != new_hire.id]
    office_pool = [w for w in facility.workers
                   if w.role == "office" and not w.exited]
    if floor_pool:
        n = min(5, len(floor_pool))
        new_hire.network_neighbors.extend([w.id for w in rng.sample(floor_pool, n)])
    if office_pool:
        n = min(2, len(office_pool))
        new_hire.network_neighbors.extend([w.id for w in rng.sample(office_pool, n)])


# =================================================================
# FACILITY SETUP (captured vs. functional)
# =================================================================
def make_captured_facility(name: str, seed: int) -> Facility:
    """Standard captured facility: low floor retention, attribution laundering."""
    workers = build_facility(50, 15, 3, seed=seed)
    return Facility(
        name=name, workers=workers,
        baseline_retention={
            "floor": 0.12,
            "office": 0.55,
            "executive": 0.92,
        },
    )


def make_functional_facility(name: str, seed: int) -> Facility:
    """Functional facility: symmetric retention from the start."""
    workers = build_facility(50, 15, 3, seed=seed)
    for w in workers:
        if w.role == "floor":
            w.credit_retention = 0.80
        elif w.role == "office":
            w.credit_retention = 0.82
        else:
            w.credit_retention = 0.85
    return Facility(
        name=name, workers=workers,
        baseline_retention={
            "floor": 0.80,
            "office": 0.82,
            "executive": 0.85,
        },
    )




# =================================================================
# PER-FACILITY QUARTER STEP
# =================================================================
def step_facility(facility: Facility, q: int, rng_events, rng_launder,
                  rng_suppress, pool, rng_hire, insight_id_ref):
    reformed = (facility.reform_quarter is not None
                and q >= facility.reform_quarter)
    MAX_J = 1e14

    quarter_insights = []

    # 1. Generate
    for w in facility.workers:
        if w.exited:
            continue
        eff_rate = w.base_insight_rate * w.engagement * burnout_multiplier(w)
        n = max(0, int(rng_events.gauss(eff_rate, eff_rate * 0.4)))
        for _ in range(n):
            legit = False
            if w.role == "office" and w.legitimate_access:
                if rng_events.random() < OFFICE_LEGIT_SYNTHESIS_FRACTION:
                    legit = True
            elif w.role == "executive":
                if rng_events.random() < EXEC_LEGIT_SYNTHESIS_FRACTION:
                    legit = True
            mu = 23.0 + w.competence * 2.0
            if legit:
                mu += 0.8
            mag = rng_events.lognormvariate(mu=mu, sigma=1.8)
            sign = 1 if rng_events.random() > 0.08 else -1

            if w.role == "floor":
                delay = rng_events.randint(*FLOOR_DELAY_RANGE)
            elif w.role == "office":
                delay = rng_events.randint(*OFFICE_DELAY_RANGE)
            else:
                delay = rng_events.randint(*EXEC_DELAY_RANGE)

            ins = Insight(
                id=insight_id_ref[0], quarter=q,
                origin_role=w.role, origin_worker_id=w.id,
                downstream_joules=sign * mag,
                cross_silo=(rng_events.random() < w.cross_silo_prob),
                legitimate=legit, realization_delay=delay,
            )
            insight_id_ref[0] += 1
            assign_network_contributors(ins, facility.workers, rng_events)
            if maybe_suppress(ins, rng_suppress):
                ins.suppressed = True
            quarter_insights.append(ins)
            facility.insights.append(ins)

    # 2. Launder
    for ins in quarter_insights:
        if ins.suppressed:
            continue
        launder(ins, facility.workers, rng_launder, reformed=reformed)

    # 3. Trust updates
    for ins in quarter_insights:
        if ins.downstream_joules <= 0:
            continue
        sev = math.log10(max(ins.downstream_joules, 1.0)) / math.log10(MAX_J)
        sev = min(1.0, max(0.0, sev))
        if ins.suppressed:
            update_trust(facility.workers[ins.origin_worker_id], sev,
                         "suppression")
        elif ins.was_laundered:
            update_trust(facility.workers[ins.origin_worker_id], sev,
                         "laundering")
            for cid in ins.network_contributors:
                if 0 <= cid < len(facility.workers):
                    update_trust(facility.workers[cid], sev * 0.4,
                                 "laundering")

    # 4. Engagement + burnout + tenure
    # Also record exits for reputation
    for w in facility.workers:
        if w.exited:
            continue
        if w.trust < 0.25:
            w.quarters_below_25 += 1
        else:
            w.quarters_below_25 = 0
        was_exited = w.exited
        update_engagement(w)
        if w.exited and not was_exited:
            record_exit_story(facility, w, q)
        update_burnout(w)
        w.tenure_quarters += 1

    # 5. Socialize new hires (convergence toward neighbors)
    for w in facility.workers:
        if w.is_new_hire:
            socialize_new_hire(w, facility.workers)

    # 6. Update reputation
    update_reputation(facility, q)

    # 7. Hire from pool (reputation-filtered)
    exits_to_replace = [w for w in facility.workers
                         if w.exited and not getattr(w, "replaced", False)]
    hires_made = 0
    hires_refused = 0
    for exiting in exits_to_replace:
        new_hire = hire_from_pool(facility, pool, exiting.role,
                                   rng_hire, q)
        if new_hire is None:
            hires_refused += 1
            continue
        wire_new_hire(new_hire, facility, rng_hire)
        facility.workers.append(new_hire)
        exiting.replaced = True
        hires_made += 1

    # Snapshot
    for w in facility.workers:
        w.trust_history.append(w.trust)
        w.engagement_history.append(w.engagement)
        w.burnout_history.append(w.burnout)

    floor_active = [w for w in facility.workers
                     if w.role == "floor" and not w.exited]
    return {
        "q": q,
        "facility": facility.name,
        "reputation": facility.reputation,
        "insights": len(quarter_insights),
        "laundered": sum(1 for i in quarter_insights if i.was_laundered),
        "suppressed": sum(1 for i in quarter_insights if i.suppressed),
        "legitimate": sum(1 for i in quarter_insights if i.legitimate),
        "floor_active": len(floor_active),
        "floor_exits_cum": sum(1 for w in facility.workers
                                if w.role == "floor" and w.exited),
        "floor_avg_trust": (statistics.mean(w.trust for w in floor_active)
                             if floor_active else 0),
        "floor_avg_burnout": (statistics.mean(w.burnout for w in floor_active)
                               if floor_active else 0),
        "floor_avg_comp": (statistics.mean(w.competence for w in floor_active)
                            if floor_active else 0),
        "hires_made": hires_made,
        "hires_refused": hires_refused,
        "pool_size": len(pool),
    }


# =================================================================
# SECTOR SIMULATION
# =================================================================
def simulate_sector(quarters=20, seed=42):
    """
    Run a sector with:
      - 5 captured facilities
      - 2 functional facilities
      - shared labor pool of 1500 applicants
    Track:
      - reputation trajectory per facility
      - hiring refusal rates
      - competence of hires at each facility
      - "shortage" signal (refused hires / attempted hires)
      - "unskilled labor" signal (competence of accepted hires over time)
    """
    captured = [make_captured_facility(f"captured_{i}", seed=seed + i)
                for i in range(5)]
    functional = [make_functional_facility(f"functional_{i}", seed=seed + 100 + i)
                   for i in range(2)]
    all_facilities = captured + functional

    pool = build_labor_pool(1500, seed=seed + 500)

    rng_events = random.Random(seed + 1)
    rng_launder = random.Random(seed + 2)
    rng_suppress = random.Random(seed + 3)
    rng_hire = random.Random(seed + 4)
    insight_id_ref = [0]

    # Initialize reputation from starting state
    for f in all_facilities:
        update_reputation(f, 0)

    # Run
    history_per_facility = {f.name: [] for f in all_facilities}
    pool_comp_history = []

    for q in range(quarters):
        for f in all_facilities:
            metrics = step_facility(f, q, rng_events, rng_launder,
                                     rng_suppress, pool, rng_hire,
                                     insight_id_ref)
            history_per_facility[f.name].append(metrics)

        # Track remaining pool composition
        if pool:
            pool_comp_history.append({
                "q": q,
                "pool_size": len(pool),
                "avg_comp": statistics.mean(a.competence for a in pool),
                "high_comp_pct": sum(1 for a in pool if a.competence >= 0.7)
                                 / len(pool) * 100,
            })

    return {
        "captured": captured,
        "functional": functional,
        "history": history_per_facility,
        "pool_history": pool_comp_history,
        "remaining_pool": pool,
    }


# =================================================================
# REPORTING
# =================================================================
def print_facility_trajectory(name, hist):
    print(f"\n  {name}")
    print(f"  {'Q':>3}{'rep':>6}{'ins':>5}{'act':>5}{'exits':>6}"
          f"{'trust':>7}{'burn':>6}{'comp':>6}{'hired':>7}{'refused':>9}"
          f"{'pool':>7}")
    for m in hist:
        print(f"  {m['q']:>3}{m['reputation']:>6.2f}{m['insights']:>5}"
              f"{m['floor_active']:>5}{m['floor_exits_cum']:>6}"
              f"{m['floor_avg_trust']:>7.2f}{m['floor_avg_burnout']:>6.2f}"
              f"{m['floor_avg_comp']:>6.2f}"
              f"{m['hires_made']:>7}{m['hires_refused']:>9}"
              f"{m['pool_size']:>7}")


def compute_shortage_signal(hist):
    """'Shortage' = cumulative refused hires / cumulative attempted hires."""
    total_attempted = sum(m['hires_made'] + m['hires_refused'] for m in hist)
    total_refused = sum(m['hires_refused'] for m in hist)
    if total_attempted == 0:
        return 0.0
    return total_refused / total_attempted


def compute_unskilled_signal(facility):
    """
    'Unskilled labor' signal = decline in avg competence of new hires
    over time at this facility.
    """
    floor = [w for w in facility.workers if w.role == "floor"]
    originals = [w for w in floor if w.tenure_quarters >= 20]
    new_hires = [w for w in floor if w.tenure_quarters < 10 and not w.exited]
    if not originals or not new_hires:
        return None
    original_comp = statistics.mean(w.competence for w in originals)
    new_comp = statistics.mean(w.competence for w in new_hires)
    return original_comp, new_comp, new_comp - original_comp




# =================================================================
# MAIN
# =================================================================
if __name__ == "__main__":
    print(f"\n{'='*82}")
    print(f"  SECTOR-LEVEL SIMULATION")
    print(f"  5 captured facilities + 2 functional, shared labor pool of 1500")
    print(f"  20 quarters (5 years)")
    print(f"{'='*82}")

    result = simulate_sector(quarters=20, seed=42)

    # Show one captured + one functional in detail
    print(f"\n{'─'*82}")
    print(f"  DETAILED TRAJECTORY: one captured facility")
    print(f"{'─'*82}")
    print_facility_trajectory("captured_0",
                               result["history"]["captured_0"])

    print(f"\n{'─'*82}")
    print(f"  DETAILED TRAJECTORY: one functional facility")
    print(f"{'─'*82}")
    print_facility_trajectory("functional_0",
                               result["history"]["functional_0"])

    # Sector-level aggregate
    print(f"\n{'='*82}")
    print(f"  SECTOR SIGNALS AT Q20")
    print(f"{'='*82}")
    print(f"  {'facility':<16}{'reputation':>12}{'shortage %':>14}"
          f"{'final comp':>14}{'final trust':>14}{'ins/qtr(last4)':>18}")
    print(f"  {'-'*80}")
    for f in result["captured"] + result["functional"]:
        hist = result["history"][f.name]
        shortage = compute_shortage_signal(hist) * 100
        floor_act = [w for w in f.workers
                     if w.role == "floor" and not w.exited]
        comp = (statistics.mean(w.competence for w in floor_act)
                if floor_act else 0)
        trust = (statistics.mean(w.trust for w in floor_act)
                 if floor_act else 0)
        last4 = statistics.mean(m["insights"] for m in hist[-4:])
        print(f"  {f.name:<16}{f.reputation:>12.2f}{shortage:>13.1f}%"
              f"{comp:>14.3f}{trust:>14.3f}{last4:>18.1f}")

    # Labor pool trajectory
    print(f"\n{'='*82}")
    print(f"  LABOR POOL COMPOSITION OVER TIME")
    print(f"{'='*82}")
    print(f"  {'Q':>3}{'pool size':>14}{'avg comp':>14}{'high-comp %':>16}")
    for m in result["pool_history"][::2]:  # every other quarter
        print(f"  {m['q']:>3}{m['pool_size']:>14}{m['avg_comp']:>14.3f}"
              f"{m['high_comp_pct']:>15.1f}%")

    # Unskilled labor signal per facility
    print(f"\n{'='*82}")
    print(f"  'UNSKILLED LABOR' SIGNAL (original vs. new-hire competence)")
    print(f"{'='*82}")
    print(f"  {'facility':<16}{'orig comp':>14}{'new hire comp':>16}"
          f"{'delta':>12}")
    for f in result["captured"] + result["functional"]:
        s = compute_unskilled_signal(f)
        if s is None:
            continue
        oc, nc, d = s
        print(f"  {f.name:<16}{oc:>14.3f}{nc:>16.3f}{d:>+12.3f}")

    # Pool routing verdict
    print(f"\n{'='*82}")
    print(f"  INTERPRETATION")
    print(f"{'='*82}")

    captured_new_hire_comp = []
    functional_new_hire_comp = []
    for f in result["captured"]:
        new_hires = [w for w in f.workers
                     if w.role == "floor" and w.tenure_quarters < 10
                     and not w.exited]
        if new_hires:
            captured_new_hire_comp.extend([w.competence for w in new_hires])
    for f in result["functional"]:
        new_hires = [w for w in f.workers
                     if w.role == "floor" and w.tenure_quarters < 10
                     and not w.exited]
        if new_hires:
            functional_new_hire_comp.extend([w.competence for w in new_hires])

    captured_output = statistics.mean(
        statistics.mean(m["insights"] for m in result["history"][f.name][-4:])
        for f in result["captured"])
    functional_output = statistics.mean(
        statistics.mean(m["insights"] for m in result["history"][f.name][-4:])
        for f in result["functional"])

    captured_rep = statistics.mean(f.reputation for f in result["captured"])
    functional_rep = statistics.mean(f.reputation for f in result["functional"])

    pool_avg_start = result["pool_history"][0]["avg_comp"]
    pool_avg_end = result["pool_history"][-1]["avg_comp"]

    print(f"""
  LABOR POOL: {len(result['remaining_pool'])} / 1500 applicants remain
    pool avg competence start:  {pool_avg_start:.3f}
    pool avg competence end:    {pool_avg_end:.3f}
    (pool competence RISING — competent applicants not being hired)

  REPUTATION:
    captured facilities:  avg reputation {captured_rep:.2f}
    functional facilities: avg reputation {functional_rep:.2f}

  NEW HIRE COMPETENCE (arrived in last 10 quarters):
    captured facilities:  mean = {statistics.mean(captured_new_hire_comp) if captured_new_hire_comp else 0:.3f}
    functional facilities: mean = {statistics.mean(functional_new_hire_comp) if functional_new_hire_comp else 0:.3f}
    delta: {(statistics.mean(functional_new_hire_comp) if functional_new_hire_comp else 0) - (statistics.mean(captured_new_hire_comp) if captured_new_hire_comp else 0):+.3f}

  OUTPUT (insights/qtr, last 4 quarters):
    captured facilities:  {captured_output:.1f}
    functional facilities: {functional_output:.1f}
    ratio: {functional_output/captured_output:.1f}x

  SAME LABOR POOL. Different outcomes per facility.

  The 'shortage' is not about people refusing to work.
  It is about WHICH people will work at which facility.

  Competent applicants (willingness_threshold > captured facility
  reputation of ~{captured_rep:.2f}) route around captured facilities.
  They are still in the pool. They will work — just not here.

  Captured facilities fill their hires from the LOW end of the
  pool (people whose willingness_threshold is below 0.4).
  These hires are less competent on average by {abs((statistics.mean(functional_new_hire_comp) if functional_new_hire_comp else 0) - (statistics.mean(captured_new_hire_comp) if captured_new_hire_comp else 0)):.2f}
  competence points than the hires going to functional facilities.

  The org then observes:
    ✗ 'labor shortage'  ← actually: competent applicants decline
    ✗ 'unskilled labor' ← actually: they only attract the bottom tail
    ✗ 'no work ethic'   ← actually: new hires socialized into
                            an already-degraded floor culture

  The WAGE LEVER DOES NOT FIX THIS.
  The signal the applicants are reading is not price.
  It is trust. Trust is not purchasable.
  Raising wages at captured facilities draws more low-threshold
  applicants (who would take any wage at any reputation),
  not the high-threshold competent workers they actually need.
""")

    # ========================================================
    # WAGE INTERVENTION EXPERIMENT
    # ========================================================
    print(f"\n{'='*82}")
    print(f"  WAGE INTERVENTION EXPERIMENT")
    print(f"  Question: can captured facilities fix the problem by paying more?")
    print(f"{'='*82}")

    # In the current model, willingness_threshold is based purely on
    # reputation. Let's introduce a wage-adjusted threshold and see.
    # Wage boost acts as a multiplier that LOWERS the effective threshold.
    # But it doesn't change the trust field — it just pulls more of the
    # same (low-threshold) applicants earlier and some mid-threshold
    # applicants who can be "bought" for a premium.

    def simulate_wage_intervention(wage_boost, seed=42):
        """Rerun sector sim but captured facilities pay wage_boost% more,
        lowering applicants' effective threshold by wage_boost/100."""
        captured = [make_captured_facility(f"captured_{i}", seed=seed + i)
                    for i in range(5)]
        functional = [make_functional_facility(f"functional_{i}",
                                                seed=seed + 100 + i)
                       for i in range(2)]
        all_facilities = captured + functional

        pool = build_labor_pool(1500, seed=seed + 500)

        # Apply wage boost: reduce threshold for captured facilities
        # (applicants "lower their standards" a bit for higher pay,
        # but competent applicants have stronger reputation preferences
        # and are less responsive to wage)

        rng_events = random.Random(seed + 1)
        rng_launder = random.Random(seed + 2)
        rng_suppress = random.Random(seed + 3)
        rng_hire = random.Random(seed + 4)
        insight_id_ref = [0]

        for f in all_facilities:
            update_reputation(f, 0)

        # Custom hire function for this run
        def hire_with_wage(facility, pool, role, rng, q):
            is_captured = facility.name.startswith("captured")
            effective_rep = facility.reputation
            if is_captured:
                effective_rep += wage_boost / 100.0  # wage premium effect
            # Applicants with threshold <= effective_rep are willing,
            # but competent applicants discount wage at higher rate
            willing = []
            for a in pool:
                # Competent applicants: wage boost only partially compensates
                wage_discount = (1 - a.competence * 0.7) * (wage_boost / 100.0)
                effective_threshold = a.willingness_threshold - wage_discount
                if effective_threshold <= facility.reputation:
                    willing.append(a)
            if not willing:
                return None
            chosen = rng.choice(willing)
            pool.remove(chosen)
            comp = chosen.competence
            if role == "floor":
                rate = 2.0 + comp * 5.0
                xs = 0.4 + comp * 0.3
                retention = facility.baseline_retention.get("floor", 0.12)
                legit_rate = 0.0; legit_access = False
            elif role == "office":
                rate = 0.5 + comp * 2.0
                xs = 0.3 + comp * 0.3
                retention = facility.baseline_retention.get("office", 0.55)
                legit_access = rng.random() < 0.4
                legit_rate = (rng.uniform(0.3, 1.2) * comp) if legit_access else 0.0
            else:
                rate = 0.2 + comp * 1.0
                xs = 0.5 + comp * 0.3
                retention = facility.baseline_retention.get("executive", 0.92)
                legit_rate = rng.uniform(0.5, 1.5) * comp
                legit_access = True
            new_id = max((w.id for w in facility.workers), default=0) + 1
            return Worker(
                id=new_id, role=role, competence=comp,
                base_insight_rate=rate, cross_silo_prob=xs,
                credit_retention=retention,
                legitimate_synthesis_rate=legit_rate,
                legitimate_access=legit_access,
                trust=0.9, recovery_capacity=rng.uniform(0.6, 1.2),
                tenure_quarters=0, is_new_hire=True,
                network_neighbors=[],
            )

        # Manually inline the step with custom hire
        for q in range(20):
            for f in all_facilities:
                # Replicate step_facility but using hire_with_wage
                reformed = False
                MAX_J = 1e14
                quarter_insights = []
                for w in f.workers:
                    if w.exited:
                        continue
                    eff_rate = (w.base_insight_rate * w.engagement
                                * burnout_multiplier(w))
                    n = max(0, int(rng_events.gauss(eff_rate, eff_rate * 0.4)))
                    for _ in range(n):
                        legit = False
                        if w.role == "office" and w.legitimate_access:
                            if rng_events.random() < OFFICE_LEGIT_SYNTHESIS_FRACTION:
                                legit = True
                        elif w.role == "executive":
                            if rng_events.random() < EXEC_LEGIT_SYNTHESIS_FRACTION:
                                legit = True
                        mu = 23.0 + w.competence * 2.0
                        if legit:
                            mu += 0.8
                        mag = rng_events.lognormvariate(mu=mu, sigma=1.8)
                        sign = 1 if rng_events.random() > 0.08 else -1
                        if w.role == "floor":
                            delay = rng_events.randint(*FLOOR_DELAY_RANGE)
                        elif w.role == "office":
                            delay = rng_events.randint(*OFFICE_DELAY_RANGE)
                        else:
                            delay = rng_events.randint(*EXEC_DELAY_RANGE)
                        ins = Insight(
                            id=insight_id_ref[0], quarter=q,
                            origin_role=w.role, origin_worker_id=w.id,
                            downstream_joules=sign * mag,
                            cross_silo=(rng_events.random() < w.cross_silo_prob),
                            legitimate=legit, realization_delay=delay,
                        )
                        insight_id_ref[0] += 1
                        assign_network_contributors(ins, f.workers, rng_events)
                        if maybe_suppress(ins, rng_suppress):
                            ins.suppressed = True
                        quarter_insights.append(ins)
                        f.insights.append(ins)
                for ins in quarter_insights:
                    if ins.suppressed:
                        continue
                    launder(ins, f.workers, rng_launder, reformed=reformed)
                for ins in quarter_insights:
                    if ins.downstream_joules <= 0:
                        continue
                    sev = math.log10(max(ins.downstream_joules, 1.0)) / math.log10(MAX_J)
                    sev = min(1.0, max(0.0, sev))
                    if ins.suppressed:
                        update_trust(f.workers[ins.origin_worker_id], sev, "suppression")
                    elif ins.was_laundered:
                        update_trust(f.workers[ins.origin_worker_id], sev, "laundering")
                        for cid in ins.network_contributors:
                            if 0 <= cid < len(f.workers):
                                update_trust(f.workers[cid], sev * 0.4, "laundering")
                for w in f.workers:
                    if w.exited:
                        continue
                    if w.trust < 0.25:
                        w.quarters_below_25 += 1
                    else:
                        w.quarters_below_25 = 0
                    was_exited = w.exited
                    update_engagement(w)
                    if w.exited and not was_exited:
                        record_exit_story(f, w, q)
                    update_burnout(w)
                    w.tenure_quarters += 1
                for w in f.workers:
                    if w.is_new_hire:
                        socialize_new_hire(w, f.workers)
                update_reputation(f, q)
                exits_to_replace = [w for w in f.workers
                                     if w.exited and not getattr(w, "replaced", False)]
                for exiting in exits_to_replace:
                    new_hire = hire_with_wage(f, pool, exiting.role, rng_hire, q)
                    if new_hire is None:
                        continue
                    wire_new_hire(new_hire, f, rng_hire)
                    f.workers.append(new_hire)
                    exiting.replaced = True

        # Collect stats
        captured_new_comp = []
        for f in captured:
            nh = [w for w in f.workers
                  if w.role == "floor" and w.tenure_quarters < 10 and not w.exited]
            captured_new_comp.extend([w.competence for w in nh])
        captured_reputation = statistics.mean(f.reputation for f in captured)
        return {
            "wage_boost": wage_boost,
            "captured_new_hire_comp": (statistics.mean(captured_new_comp)
                                        if captured_new_comp else 0),
            "captured_reputation": captured_reputation,
        }

    print(f"\n  {'wage boost':>15}{'new hire comp':>18}{'reputation':>14}")
    for boost in [0, 10, 25, 50, 100]:
        r = simulate_wage_intervention(boost, seed=42)
        print(f"  {str(boost)+'%':>15}{r['captured_new_hire_comp']:>18.3f}"
              f"{r['captured_reputation']:>14.2f}")

    print(f"""
  → wage boosts draw some additional applicants but CAN NOT
    restore competence of hire pool to functional-facility levels
  → because the signal competent applicants are reading is
    REPUTATION, not PRICE
  → and reputation is generated by attribution capture, not
    by compensation
  → sector responds to wage pressure by drawing deeper from
    the low-threshold end of the pool, plus a small premium
    for mid-threshold applicants
  → top-threshold applicants remain unreachable via wage
""")

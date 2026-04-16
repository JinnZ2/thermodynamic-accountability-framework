"""
attribution_sim.py
==================
Thermodynamic attribution simulation.

Models a facility with floor workers and office workers generating
insights/decisions. Tracks:
  - energy inputs per worker (HVAC, salary-embodied, equipment)
  - decision provenance (where insight actually originated)
  - attribution flow (who gets credit in current system)
  - synthesis events (cross-silo integration — on floor AND office)
  - net value generated vs. net energy consumed

Outputs two accounting ledgers:
  1. CURRENT SYSTEM   — attribution by reporting point
  2. PROVENANCE AUDIT — attribution by generation point

CC0. Stdlib only.
"""

from dataclasses import dataclass, field
from typing import Literal
import random
import statistics

# -----------------------------------------------------------------
# PHYSICAL CONSTANTS (order-of-magnitude, US industrial context)
# -----------------------------------------------------------------
# Embodied energy per dollar in US economy, rough avg
JOULES_PER_DOLLAR = 12e6  # ~12 MJ/$

# Per-quarter energy inputs by role class (joules)
ENERGY_INPUTS = {
    "floor": {
        "conditioning": 2e9,      # minimal HVAC share, lighting
        "equipment":    5e9,      # tools, PPE, shared machinery share
        "salary_emb":   15000 * JOULES_PER_DOLLAR,  # ~$15k/qtr → 1.8e11
    },
    "office": {
        "conditioning": 5.4e10,   # full HVAC, lighting, IT
        "equipment":    1e10,     # laptop, monitors, phone, software
        "salary_emb":   40000 * JOULES_PER_DOLLAR,  # ~$40k/qtr → 4.8e11
    },
    "executive": {
        "conditioning": 8e10,     # larger space, more amenities
        "equipment":    2e10,
        "salary_emb":   100000 * JOULES_PER_DOLLAR, # ~$100k/qtr → 1.2e12
    },
}


def total_energy_in(role: str) -> float:
    e = ENERGY_INPUTS[role]
    return e["conditioning"] + e["equipment"] + e["salary_emb"]


# -----------------------------------------------------------------
# DECISION / INSIGHT MODEL
# -----------------------------------------------------------------
@dataclass
class Insight:
    """A generative event: noticing something that matters."""
    id: int
    origin_role: Literal["floor", "office", "executive"]
    origin_worker_id: int
    # Value of acting on this insight, in joules of downstream work
    # moved (positive) or waste prevented (positive) or damage (negative)
    downstream_joules: float
    # Did it require cross-silo integration to generate?
    cross_silo: bool
    # Who ended up reported as the "decision maker"
    attributed_role: Literal["floor", "office", "executive"] = "office"
    attributed_worker_id: int = -1


@dataclass
class Worker:
    id: int
    role: Literal["floor", "office", "executive"]
    # How often they generate insights per quarter (Poisson-ish rate)
    insight_rate: float
    # Probability that any insight they generate is cross-silo
    cross_silo_prob: float
    # Probability their insight gets credited to them vs. reassigned upward
    credit_retention: float


# -----------------------------------------------------------------
# ATTRIBUTION LAUNDERING MODEL
# -----------------------------------------------------------------
# In current systems, insights flow UP the hierarchy for attribution.
# floor insight → often credited to office supervisor
# office insight → often credited to executive
# executive insight → stays with executive
#
# This is the "attribution capture" function.

def launder_attribution(insight: Insight, workers: list[Worker],
                        rng: random.Random) -> Insight:
    """Apply current-system attribution rules."""
    origin = insight.origin_role
    originator = workers[insight.origin_worker_id]

    # Credit retention probability: does the originator keep the credit?
    if rng.random() < originator.credit_retention:
        insight.attributed_role = origin
        insight.attributed_worker_id = insight.origin_worker_id
        return insight

    # Otherwise, credit flows up one level
    if origin == "floor":
        # Reassign to a random office worker (the "reporter")
        office_workers = [w for w in workers if w.role == "office"]
        if office_workers:
            chosen = rng.choice(office_workers)
            insight.attributed_role = "office"
            insight.attributed_worker_id = chosen.id
    elif origin == "office":
        exec_workers = [w for w in workers if w.role == "executive"]
        if exec_workers:
            chosen = rng.choice(exec_workers)
            insight.attributed_role = "executive"
            insight.attributed_worker_id = chosen.id
    else:  # executive
        insight.attributed_role = origin
        insight.attributed_worker_id = insight.origin_worker_id

    return insight


# -----------------------------------------------------------------
# FACILITY MODEL
# -----------------------------------------------------------------
def build_facility(n_floor=50, n_office=15, n_exec=3, seed=42) -> list[Worker]:
    rng = random.Random(seed)
    workers = []
    wid = 0

    # Floor workers: high insight rate (they see the physical reality),
    # high cross-silo rate (they deal with multiple orgs constantly),
    # low credit retention (their insights get laundered upward).
    for _ in range(n_floor):
        workers.append(Worker(
            id=wid,
            role="floor",
            insight_rate=rng.uniform(2.0, 6.0),       # 2-6 insights/qtr
            cross_silo_prob=rng.uniform(0.4, 0.7),    # naturally cross-silo
            credit_retention=rng.uniform(0.05, 0.20), # rarely keep credit
        ))
        wid += 1

    # Office workers: moderate insight rate, moderate cross-silo
    # (they synthesize what's fed to them), moderate credit retention.
    for _ in range(n_office):
        workers.append(Worker(
            id=wid,
            role="office",
            insight_rate=rng.uniform(0.5, 2.0),
            cross_silo_prob=rng.uniform(0.3, 0.6),
            credit_retention=rng.uniform(0.4, 0.7),
        ))
        wid += 1

    # Executives: low insight rate, high cross-silo when they do generate,
    # very high credit retention (they're the attribution sink).
    for _ in range(n_exec):
        workers.append(Worker(
            id=wid,
            role="executive",
            insight_rate=rng.uniform(0.2, 1.0),
            cross_silo_prob=rng.uniform(0.5, 0.8),
            credit_retention=rng.uniform(0.85, 0.98),
        ))
        wid += 1

    return workers


def generate_insights(workers: list[Worker], quarters: int,
                      seed=7) -> list[Insight]:
    rng = random.Random(seed)
    insights = []
    insight_id = 0

    for q in range(quarters):
        for w in workers:
            # Poisson-ish: sample count
            n = max(0, int(rng.gauss(w.insight_rate, w.insight_rate * 0.4)))
            for _ in range(n):
                # Downstream value: log-normal-ish distribution
                # Most insights are small; a few are large
                magnitude = rng.lognormvariate(mu=24.0, sigma=2.0)
                # Sign: mostly positive, occasional negative (bad decisions)
                sign = 1 if rng.random() > 0.08 else -1
                downstream = sign * magnitude

                cross_silo = rng.random() < w.cross_silo_prob

                insight = Insight(
                    id=insight_id,
                    origin_role=w.role,
                    origin_worker_id=w.id,
                    downstream_joules=downstream,
                    cross_silo=cross_silo,
                )
                insight_id += 1
                insights.append(insight)

    return insights


# -----------------------------------------------------------------
# LEDGERS
# -----------------------------------------------------------------
def ledger_by_attribution(workers: list[Worker],
                          insights: list[Insight],
                          quarters: int,
                          mode: Literal["current", "provenance"]) -> dict:
    """Build a role-level ledger under a given attribution mode."""
    role_totals = {
        "floor":     {"energy_in": 0.0, "value_out": 0.0, "n_workers": 0,
                      "insights": 0, "cross_silo_insights": 0},
        "office":    {"energy_in": 0.0, "value_out": 0.0, "n_workers": 0,
                      "insights": 0, "cross_silo_insights": 0},
        "executive": {"energy_in": 0.0, "value_out": 0.0, "n_workers": 0,
                      "insights": 0, "cross_silo_insights": 0},
    }

    # Energy inputs: same regardless of attribution mode
    for w in workers:
        role_totals[w.role]["n_workers"] += 1
        role_totals[w.role]["energy_in"] += total_energy_in(w.role) * quarters

    # Value: depends on mode
    for ins in insights:
        if mode == "current":
            credited = ins.attributed_role
        else:  # provenance
            credited = ins.origin_role

        role_totals[credited]["value_out"] += ins.downstream_joules
        role_totals[credited]["insights"] += 1
        if ins.cross_silo:
            role_totals[credited]["cross_silo_insights"] += 1

    # Derived metrics
    for role, t in role_totals.items():
        t["efficiency"] = (t["value_out"] / t["energy_in"]
                           if t["energy_in"] > 0 else 0.0)
        t["value_per_worker"] = (t["value_out"] / t["n_workers"]
                                 if t["n_workers"] > 0 else 0.0)
        t["energy_per_worker"] = (t["energy_in"] / t["n_workers"]
                                  if t["n_workers"] > 0 else 0.0)
        t["cross_silo_fraction"] = (t["cross_silo_insights"] / t["insights"]
                                    if t["insights"] > 0 else 0.0)

    return role_totals


# -----------------------------------------------------------------
# REPORT
# -----------------------------------------------------------------
def fmt_j(x: float) -> str:
    """Format joules in scientific-ish notation."""
    if abs(x) >= 1e12:
        return f"{x/1e12:+.2f} TJ"
    if abs(x) >= 1e9:
        return f"{x/1e9:+.2f} GJ"
    if abs(x) >= 1e6:
        return f"{x/1e6:+.2f} MJ"
    return f"{x:+.2e} J"


def print_ledger(name: str, ledger: dict):
    print(f"\n{'='*70}")
    print(f"  LEDGER: {name}")
    print(f"{'='*70}")
    header = f"{'role':<12}{'N':>5}{'energy_in':>14}{'value_out':>14}" \
             f"{'efficiency':>14}{'x-silo %':>12}"
    print(header)
    print("-" * 70)
    for role in ["floor", "office", "executive"]:
        t = ledger[role]
        print(f"{role:<12}{t['n_workers']:>5}"
              f"{fmt_j(t['energy_in']):>14}"
              f"{fmt_j(t['value_out']):>14}"
              f"{t['efficiency']:>+14.3f}"
              f"{t['cross_silo_fraction']*100:>11.1f}%")


def print_diff(current: dict, provenance: dict):
    print(f"\n{'='*70}")
    print(f"  ATTRIBUTION CAPTURE (current − provenance)")
    print(f"{'='*70}")
    print(f"{'role':<12}{'value shift':>18}{'efficiency shift':>22}")
    print("-" * 70)
    for role in ["floor", "office", "executive"]:
        v_shift = current[role]["value_out"] - provenance[role]["value_out"]
        e_shift = current[role]["efficiency"] - provenance[role]["efficiency"]
        print(f"{role:<12}{fmt_j(v_shift):>18}{e_shift:>+22.3f}")
    print("\n  positive = role gains credit it didn't generate")
    print("  negative = role generates credit that's taken from it")


# -----------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------
def run(n_floor=50, n_office=15, n_exec=3, quarters=8,
        facility_seed=42, event_seed=7, verbose=True):
    workers = build_facility(n_floor, n_office, n_exec, seed=facility_seed)
    insights = generate_insights(workers, quarters, seed=event_seed)

    # Apply current-system attribution laundering
    rng = random.Random(event_seed + 1)
    for ins in insights:
        launder_attribution(ins, workers, rng)

    current = ledger_by_attribution(workers, insights, quarters, "current")
    provenance = ledger_by_attribution(workers, insights, quarters, "provenance")

    if verbose:
        print(f"\nFACILITY: {n_floor} floor / {n_office} office / "
              f"{n_exec} exec, over {quarters} quarters")
        print(f"TOTAL INSIGHTS: {len(insights)}")

        print_ledger("CURRENT SYSTEM (attribution by reporting point)", current)
        print_ledger("PROVENANCE AUDIT (attribution by generation point)",
                     provenance)
        print_diff(current, provenance)

        # Summary signal
        floor_shift = (current["floor"]["value_out"] -
                       provenance["floor"]["value_out"])
        office_shift = (current["office"]["value_out"] -
                        provenance["office"]["value_out"])
        exec_shift = (current["executive"]["value_out"] -
                      provenance["executive"]["value_out"])

        print(f"\n{'='*70}")
        print("  SIGNAL")
        print(f"{'='*70}")
        print(f"  floor workers generated {fmt_j(-floor_shift)} "
              f"of value they did NOT receive credit for")
        print(f"  office + exec received {fmt_j(office_shift + exec_shift)} "
              f"of credit they did NOT generate")
        print(f"  this is the attribution capture signature")

    return {
        "workers": workers,
        "insights": insights,
        "current": current,
        "provenance": provenance,
    }


if __name__ == "__main__":
    run()

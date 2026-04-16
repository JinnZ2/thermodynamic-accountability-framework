"""
sensitivity_sweep.py
====================
Run the attribution sim across a grid of parameters to see how
robust the attribution-capture signature is.

Sweeps:
  - credit retention rates
  - facility composition (floor:office ratio)
  - insight rate distributions

Reports the attribution capture magnitude and sign stability.
"""

import statistics
from attribution_sim import (
    build_facility, generate_insights, launder_attribution,
    ledger_by_attribution, fmt_j, total_energy_in, ENERGY_INPUTS,
)
import random


def capture_signal(n_floor, n_office, n_exec, quarters,
                   facility_seed, event_seed):
    workers = build_facility(n_floor, n_office, n_exec, seed=facility_seed)
    insights = generate_insights(workers, quarters, seed=event_seed)
    rng = random.Random(event_seed + 1)
    for ins in insights:
        launder_attribution(ins, workers, rng)
    current = ledger_by_attribution(workers, insights, quarters, "current")
    prov = ledger_by_attribution(workers, insights, quarters, "provenance")
    floor_shift = current["floor"]["value_out"] - prov["floor"]["value_out"]
    office_shift = current["office"]["value_out"] - prov["office"]["value_out"]
    exec_shift = current["executive"]["value_out"] - prov["executive"]["value_out"]
    return {
        "floor_shift": floor_shift,
        "office_shift": office_shift,
        "exec_shift": exec_shift,
        "floor_eff_current": current["floor"]["efficiency"],
        "floor_eff_provenance": prov["floor"]["efficiency"],
        "office_eff_current": current["office"]["efficiency"],
        "office_eff_provenance": prov["office"]["efficiency"],
    }


def sweep_compositions():
    print("\n" + "="*72)
    print("  SWEEP: facility composition (floor:office ratio)")
    print("="*72)
    print(f"{'n_floor':>8}{'n_office':>10}{'n_exec':>8}"
          f"{'floor shift':>16}{'office+exec shift':>20}")
    print("-"*72)
    configs = [
        (20, 20, 2),
        (30, 15, 3),
        (50, 15, 3),
        (80, 10, 2),
        (100, 5, 1),
    ]
    for nf, no, ne in configs:
        # Average across 5 seeds
        shifts = []
        for s in range(5):
            r = capture_signal(nf, no, ne, 8, 42+s, 7+s)
            shifts.append((r["floor_shift"],
                           r["office_shift"] + r["exec_shift"]))
        mean_floor = statistics.mean(s[0] for s in shifts)
        mean_other = statistics.mean(s[1] for s in shifts)
        print(f"{nf:>8}{no:>10}{ne:>8}"
              f"{fmt_j(mean_floor):>16}{fmt_j(mean_other):>20}")


def sweep_seeds():
    """Sign-stability test: does the direction of capture ever flip?"""
    print("\n" + "="*72)
    print("  SWEEP: 30 seeds, fixed facility (50/15/3, 8 quarters)")
    print("="*72)
    results = []
    for s in range(30):
        r = capture_signal(50, 15, 3, 8, 42+s, 7+s*2)
        results.append(r)

    floor_shifts = [r["floor_shift"] for r in results]
    office_shifts = [r["office_shift"] for r in results]

    floor_negative = sum(1 for x in floor_shifts if x < 0)
    office_positive = sum(1 for x in office_shifts if x > 0)

    print(f"  floor shift:  mean={fmt_j(statistics.mean(floor_shifts))}  "
          f"stdev={fmt_j(statistics.stdev(floor_shifts))}")
    print(f"  office shift: mean={fmt_j(statistics.mean(office_shifts))}  "
          f"stdev={fmt_j(statistics.stdev(office_shifts))}")
    print(f"\n  sign stability:")
    print(f"    floor loses credit in {floor_negative}/30 runs")
    print(f"    office gains credit in {office_positive}/30 runs")

    if floor_negative >= 28 and office_positive >= 28:
        print(f"\n  → attribution capture signature is STABLE across seeds")
    else:
        print(f"\n  → signal is noisy; revisit parameter assumptions")


def what_would_reverse_it():
    """What credit retention rate on floor workers would eliminate capture?"""
    print("\n" + "="*72)
    print("  COUNTERFACTUAL: what credit retention rate dissolves capture?")
    print("="*72)
    print(f"  (rebuilding facility with varying floor credit_retention)")
    print(f"{'floor retention':>20}{'floor shift (avg)':>22}"
          f"{'interpretation':>30}")
    print("-"*72)

    import attribution_sim as A

    for retention in [0.10, 0.25, 0.50, 0.75, 0.95]:
        shifts = []
        for s in range(5):
            rng = random.Random(42 + s)
            workers = []
            wid = 0
            for _ in range(50):
                workers.append(A.Worker(
                    id=wid, role="floor",
                    insight_rate=rng.uniform(2.0, 6.0),
                    cross_silo_prob=rng.uniform(0.4, 0.7),
                    credit_retention=retention,
                ))
                wid += 1
            for _ in range(15):
                workers.append(A.Worker(
                    id=wid, role="office",
                    insight_rate=rng.uniform(0.5, 2.0),
                    cross_silo_prob=rng.uniform(0.3, 0.6),
                    credit_retention=rng.uniform(0.4, 0.7),
                ))
                wid += 1
            for _ in range(3):
                workers.append(A.Worker(
                    id=wid, role="executive",
                    insight_rate=rng.uniform(0.2, 1.0),
                    cross_silo_prob=rng.uniform(0.5, 0.8),
                    credit_retention=rng.uniform(0.85, 0.98),
                ))
                wid += 1

            insights = A.generate_insights(workers, 8, seed=7+s)
            rng2 = random.Random(7 + s + 1)
            for ins in insights:
                A.launder_attribution(ins, workers, rng2)

            cur = A.ledger_by_attribution(workers, insights, 8, "current")
            prov = A.ledger_by_attribution(workers, insights, 8, "provenance")
            shifts.append(cur["floor"]["value_out"] - prov["floor"]["value_out"])

        avg = statistics.mean(shifts)
        if avg < -10e12:
            interp = "severe capture"
        elif avg < -1e12:
            interp = "moderate capture"
        elif avg < 0:
            interp = "mild capture"
        else:
            interp = "no capture"
        print(f"{retention:>20.2f}{fmt_j(avg):>22}{interp:>30}")


if __name__ == "__main__":
    sweep_compositions()
    sweep_seeds()
    what_would_reverse_it()

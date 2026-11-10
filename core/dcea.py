"""
dcea.py -- Dependency-Chain Energy Accounting (DCEA v0.1) calculator.

Co-authored. CC0. Stdlib only. Status: PROPOSED (spec: docs/DCEA_v0.1.md, section 6).

The calculator in the spec, with three repairs (see docs/DCEA_checks.md):
  1. Runs on Python 3.9: Optional[float] instead of `float | None`, which a
     dataclass evaluates at class creation and raises TypeError on 3.9.
  2. Reports pending_count beside pending_share (R11 asks for the count).
  3. Flags duplicate node names, because site_eroi selects site nodes by name.
Otherwise unchanged: a PENDING node (energy_mj None) is never counted as 0.

Also carries the worker-side road-driver ledger arithmetic
(docs/worker_side_ledger_road_driver.md) so the stated totals are recomputed,
not trusted.

USAGE
  python core/dcea.py              run the selftest (prints its count) + ledger recompute
  python core/dcea.py --ledger     print the ledger recompute only
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class Node:
    name: str
    energy_mj: Optional[float]        # None = PENDING (R11), never 0
    tag: str                          # OBSERVED / DERIVED / PROPOSED
    stamp: dict                       # R3: window, place, partners, rules, source
    external: bool = False            # supplied by another firm (R2)
    single_source: bool = False       # R9
    recurring_per_year: bool = False  # R6
    volume: int = 0                   # asterisks: 0 = solid
    children: list = field(default_factory=list)


def walk(n):
    yield n
    for c in n.children:
        yield from walk(c)


def account(root, delivered_mj, site_names=()):
    nodes = list(walk(root))
    known = [n for n in nodes if n.energy_mj is not None]
    pending = [n.name for n in nodes if n.energy_mj is None]
    total = sum(n.energy_mj for n in known)
    ext = sum(n.energy_mj for n in known if n.external)
    site = sum(n.energy_mj for n in known if n.name in site_names)
    unstamped = [n.name for n in nodes if not n.stamp]
    names = [n.name for n in nodes]
    duplicates = sorted({x for x in names if names.count(x) > 1})
    return {
        "full_chain_eroi": delivered_mj / total if total else None,
        "site_eroi": delivered_mj / site if site else None,
        "dependency_ratio": ext / total if total else None,
        "pending": pending,
        "pending_count": len(pending),
        "pending_share": len(pending) / len(nodes),
        "fragility": [n.name for n in nodes if n.single_source],
        "unstamped": unstamped,          # R3 violation list
        "duplicate_names": duplicates,   # site_eroi selects by name: ambiguous if non-empty
        "note": "lower bound on chain energy while pending > 0",
    }


# ---------------------------------------------------------------- road-driver ledger
# Inputs as stated in docs/worker_side_ledger_road_driver.md (stamped 2026-11-02).
ROAD_DAYS = 250
MEDIAN_WAGE = 58640.0                  # BLS median, as cited in the ledger (CARRIED)
LITERS_PER_20OZ = 20 * 0.0295735


def daily_ranges() -> Dict[str, Tuple[float, float]]:
    bottles = lambda liters: liters / LITERS_PER_20OZ
    return {
        "food": (3 * 10.0, 3 * 11.50),
        "water": (bottles(3) * 1.88, bottles(4) * 1.88),
        "idling": (10 * 0.5 * 6.55, 10 * 1.0 * 6.55),
        "shower": (7.0, 12.0),
        "phone_gps": ((120 + 30) * 12 / ROAD_DAYS,) * 2,
    }


ANNUAL_GEAR = {"clothing_gear": (300.0, 500.0), "masks": (270.0, 540.0), "boots": (212.0, 212.0),
               "filters": None}        # PENDING in the ledger


STATED_DAILY = {"food": (30, 35), "water": (9, 13), "idling": (33, 66), "shower": (7, 12), "phone_gps": (7, 7)}


def _annual(daily: Dict[str, Tuple[float, float]]) -> dict:
    lo = sum(v[0] for v in daily.values())
    hi = sum(v[1] for v in daily.values())
    gear = [v for v in ANNUAL_GEAR.values() if v is not None]
    glo, ghi = sum(v[0] for v in gear), sum(v[1] for v in gear)
    alo, ahi = ROAD_DAYS * lo + glo, ROAD_DAYS * hi + ghi
    return {"daily": daily, "daily_total": (lo, hi), "gear": (glo, ghi), "annual": (alo, ahi),
            "share_of_wage": (alo / MEDIAN_WAGE, ahi / MEDIAN_WAGE)}


def ledger() -> dict:
    """Two readings: from the raw inputs (prices, volumes, rates) and from the ledger's rounded rows."""
    return {"from_inputs": _annual(daily_ranges()), "from_rounded_rows": _annual(STATED_DAILY),
            "pending": [k for k, v in ANNUAL_GEAR.items() if v is None],
            "stated": {"daily_total": (86, 133), "annual": (22300, 34600), "share": (0.38, 0.59)}}


def ledger_report() -> str:
    L = ledger()
    out = ["Road-driver ledger recompute (250 road days; stated: daily $86 - $133, annual $22,300 - $34,600, 38% - 59%):"]
    for name in ("from_inputs", "from_rounded_rows"):
        R = L[name]
        rows = [f"    {k:<10} ${a:7.2f} - ${b:7.2f}" for k, (a, b) in R["daily"].items()]
        (lo, hi), (alo, ahi), (slo, shi) = R["daily_total"], R["annual"], R["share_of_wage"]
        out += [f"  {name.replace('_', ' ')}:"] + rows + [
            f"    daily      ${lo:.2f} - ${hi:.2f}",
            f"    annual     ${alo:,.0f} - ${ahi:,.0f}   (gear ${R['gear'][0]:.0f} - ${R['gear'][1]:.0f}/yr)",
            f"    of wage    {slo:.1%} - {shi:.1%}"]
    out += ["  floor only: filters PENDING; proper nutrition and every section-4 item excluded"]
    return "\n".join(out)


# ---------------------------------------------------------------- selftest
def selftest() -> bool:
    import ast
    import inspect
    import sys
    checks: List[Tuple[str, bool]] = []
    s = lambda **k: {"source": "selftest", **k}
    root = Node("barrel", None, "OBSERVED", s(), children=[
        Node("drilling", 30.0, "OBSERVED", s(), single_source=True),
        Node("trucking", 10.0, "OBSERVED", s(), external=True),
        Node("refining", None, "PROPOSED", {}),
        Node("trucking", 5.0, "OBSERVED", s(), external=True),
    ])
    r = account(root, 600.0, site_names=("drilling",))
    checks.append(("PENDING nodes never counted as 0", r["pending"] == ["barrel", "refining"] and r["pending_count"] == 2))
    checks.append(("full-chain EROI over known energy only", abs(r["full_chain_eroi"] - 600 / 45) < 1e-12))
    checks.append(("site EROI", abs(r["site_eroi"] - 20.0) < 1e-12))
    checks.append(("dependency ratio = external / total", abs(r["dependency_ratio"] - 15 / 45) < 1e-12))
    checks.append(("pending share over all nodes", abs(r["pending_share"] - 2 / 5) < 1e-12))
    checks.append(("fragility lists single-source nodes", r["fragility"] == ["drilling"]))
    checks.append(("unstamped node reported (R3)", r["unstamped"] == ["refining"]))
    checks.append(("duplicate names flagged", r["duplicate_names"] == ["trucking"]))
    empty = account(Node("x", None, "PROPOSED", s()), 1.0)
    checks.append(("all-PENDING chain gives None, not a number", empty["full_chain_eroi"] is None
                   and empty["dependency_ratio"] is None and empty["pending_count"] == 1))
    src = inspect.getsource(sys.modules[__name__])
    checks.append(("no PEP 604 union in annotations (Python 3.9)",
                   not any(isinstance(a, ast.BinOp) for n in ast.walk(ast.parse(src))
                           if isinstance(n, ast.AnnAssign) for a in [n.annotation])))
    L = ledger()
    raw, rnd = L["from_inputs"], L["from_rounded_rows"]
    checks.append(("rounded rows sum to the stated $86 - $133", rnd["daily_total"] == (86, 133)))
    checks.append(("raw inputs give $86.49 - $131.91 a day",
                   (round(raw["daily_total"][0], 2), round(raw["daily_total"][1], 2)) == (86.49, 131.91)))
    checks.append(("annual low matches the stated $22,300 within $105 on both readings",
                   all(abs(R["annual"][0] - 22300) <= 105 for R in (raw, rnd))))
    checks.append(("annual high is below the stated $34,600 on both readings ($34,502 rounded, $34,231 raw)",
                   round(rnd["annual"][1]) == 34502 and round(raw["annual"][1]) == 34231))
    checks.append(("stated 59% holds only on the rounded rows (58.8% vs 58.4% raw)",
                   round(rnd["share_of_wage"][1] * 100) == 59 and round(raw["share_of_wage"][1] * 100) == 58))
    checks.append(("filters stay PENDING", L["pending"] == ["filters"]))
    bad = [n for n, ok in checks if not ok]
    for n in bad:
        print("  FAIL:", n)
    print("dcea selftest %d/%d" % (len(checks) - len(bad), len(checks)))
    return not bad


if __name__ == "__main__":
    import sys
    if "--ledger" in sys.argv:
        print(ledger_report())
    else:
        ok = selftest()
        print(ledger_report())
        sys.exit(0 if ok else 1)

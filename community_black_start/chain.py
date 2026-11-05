# chain.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude).
#
#   items.json ──> load() ──> validate()   unknown ids, cycles (reported, never raised),
#                     │                    field problems, parallel input used as prerequisite
#                     ├──> level_check()   depends_on points to a HIGHER level
#                     ├──> rank()          criticality score, descending
#                     ├──> spof()          no substitute AND no holder AND >= 2 dependents
#                     └──> order()         topological, dependencies first,
#                                          ties: hours_to_fail ascending (unknown last)
#
# "dependents" everywhere = TRANSITIVE dependents: every item that fails
# downstream if this one fails. direct_dependents is reported beside it.

import heapq
import json
import os
from typing import Dict, List, Optional, Set, Tuple

from schema import Item, item_from_dict

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ITEMS = os.path.join(HERE, "items.json")
SUBSTITUTE_FACTOR = 0.3


def load(path: str = DEFAULT_ITEMS) -> Dict[str, Item]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    rows = raw.get("items", []) if isinstance(raw, dict) else raw
    items = {}
    for d in rows or []:
        it = item_from_dict(d)
        items[it.id] = it
    return items


# ---------------------------------------------------------------
# graph helpers (null-safe: unknown ids are skipped, not followed)
# ---------------------------------------------------------------
def unknown_refs(items: Dict[str, Item]) -> List[Tuple[str, str]]:
    return [(i.id, d) for i in items.values() for d in (i.depends_on or []) if d not in items]


def find_cycles(items: Dict[str, Item]) -> List[List[str]]:
    """Every elementary cycle found by DFS back-edges, each as a closed path
    [a, b, ..., a]. Deduplicated by member set. Never raises."""
    WHITE, GREY, BLACK = 0, 1, 2
    color = {k: WHITE for k in items}
    stack: List[str] = []
    cycles: List[List[str]] = []
    seen: Set[frozenset] = set()

    def visit(n: str) -> None:
        color[n] = GREY
        stack.append(n)
        for d in items[n].depends_on or []:
            if d not in items:
                continue
            if color[d] == GREY:
                cyc = stack[stack.index(d):] + [d]
                key = frozenset(cyc)
                if key not in seen:
                    seen.add(key)
                    cycles.append(cyc)
            elif color[d] == WHITE:
                visit(d)
        stack.pop()
        color[n] = BLACK

    for k in sorted(items):
        if color[k] == WHITE:
            visit(k)
    return cycles


def dependents(items: Dict[str, Item]) -> Dict[str, Set[str]]:
    """item -> set of items that (transitively) depend on it."""
    rev: Dict[str, Set[str]] = {k: set() for k in items}
    for i in items.values():
        for d in i.depends_on or []:
            if d in rev:
                rev[d].add(i.id)
    out = {}
    for k in items:
        seen: Set[str] = set()
        todo = list(rev[k])
        while todo:
            n = todo.pop()
            if n in seen or n == k:
                continue
            seen.add(n)
            todo.extend(rev[n])
        out[k] = seen
    return out


def direct_dependents(items: Dict[str, Item]) -> Dict[str, Set[str]]:
    rev: Dict[str, Set[str]] = {k: set() for k in items}
    for i in items.values():
        for d in i.depends_on or []:
            if d in rev:
                rev[d].add(i.id)
    return rev


# ---------------------------------------------------------------
# checks
# ---------------------------------------------------------------
def validate(items: Dict[str, Item]) -> Dict[str, list]:
    """Report, never raise. Keys: field, unknown_ids, cycles, parallel_as_prereq."""
    rep = {"field": [], "unknown_ids": unknown_refs(items), "cycles": find_cycles(items),
           "parallel_as_prereq": []}
    for i in items.values():
        for p in i.problems():
            rep["field"].append((i.id, p))
        for d in i.depends_on or []:
            if d in items and items[d].parallel_input:
                rep["parallel_as_prereq"].append((i.id, d))
    return rep


def is_clean(rep: Dict[str, list]) -> bool:
    return not any(rep[k] for k in ("field", "unknown_ids", "cycles", "parallel_as_prereq"))


def level_check(items: Dict[str, Item]) -> List[Tuple[str, int, str, int]]:
    """(item, its level, dependency, dependency level) where dependency level
    is HIGHER. A finding, not an error: it marks where a floor is not a floor."""
    out = []
    for i in sorted(items.values(), key=lambda x: (x.level, x.id)):
        for d in i.depends_on or []:
            if d in items and isinstance(items[d].level, int) and isinstance(i.level, int) \
                    and items[d].level > i.level:
                out.append((i.id, i.level, d, items[d].level))
    return out


def criticality(item: Item, n_dependents: int) -> float:
    """dependents * (1 if no substitute else 0.3) * (1/hours if known else 1).
    Unknown hours count as 1, i.e. as severe as a 1-hour failure."""
    sub = SUBSTITUTE_FACTOR if (item.non_grid_substitute or "").strip() else 1.0
    h = item.hours_to_fail_without_grid
    time_factor = (1.0 / h) if isinstance(h, (int, float)) and not isinstance(h, bool) and h > 0 else 1.0
    return n_dependents * sub * time_factor


def rank(items: Dict[str, Item]) -> List[dict]:
    dep = dependents(items)
    ddep = direct_dependents(items)
    rows = []
    for k, it in items.items():
        rows.append({
            "id": k, "level": it.level,
            "score": round(criticality(it, len(dep[k])), 4),
            "dependents": len(dep[k]), "direct_dependents": len(ddep[k]),
            "substitute": bool((it.non_grid_substitute or "").strip()),
            "hours_known": it.hours_to_fail_without_grid is not None,
            "volume": it.volume, "status": it.status,
        })
    rows.sort(key=lambda r: (-r["score"], r["level"], r["id"]))
    return rows


def spof(items: Dict[str, Item]) -> List[dict]:
    """No substitute AND no local holder AND >= 2 (transitive) dependents."""
    dep = dependents(items)
    out = []
    for k, it in sorted(items.items()):
        if (it.non_grid_substitute or "").strip() or (it.local_holder or "").strip():
            continue
        if len(dep[k]) >= 2:
            out.append({"id": k, "level": it.level, "dependents": sorted(dep[k])})
    out.sort(key=lambda r: (-len(r["dependents"]), r["id"]))
    return out


def order(items: Dict[str, Item]) -> Tuple[List[str], List[str]]:
    """(restoration order, unresolved). Kahn's algorithm: dependencies first;
    among ready items, hours_to_fail ascending, unknown last, then level, id.
    Items stuck in or behind a cycle are returned as unresolved, not dropped."""
    indeg = {k: 0 for k in items}
    rev: Dict[str, List[str]] = {k: [] for k in items}
    for i in items.values():
        for d in set(i.depends_on or []):
            if d in items:
                indeg[i.id] += 1
                rev[d].append(i.id)

    def key(k: str):
        h = items[k].hours_to_fail_without_grid
        hv = h if isinstance(h, (int, float)) and not isinstance(h, bool) else float("inf")
        lv = items[k].level if isinstance(items[k].level, int) else 99
        return (hv, lv, k)

    heap = [(key(k), k) for k, v in indeg.items() if v == 0]
    heapq.heapify(heap)
    out = []
    while heap:
        _, k = heapq.heappop(heap)
        out.append(k)
        for n in rev[k]:
            indeg[n] -= 1
            if indeg[n] == 0:
                heapq.heappush(heap, (key(n), n))
    unresolved = sorted(k for k in items if k not in set(out))
    return out, unresolved

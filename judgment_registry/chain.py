#!/usr/bin/env python3
# chain.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-04.
#
# lineage(records, judgment_id): the full version chain the id sits in, root
#   first, with date, judge, change_basis and dissent count at each step.
#   Forks are shown as branches, not resolved.
# diff(a, b): field-level changes between two versions. Reports what
#   changed; says nothing about which version is better.

from ledger import judgments

FIELDS = ("version", "claim", "scope", "environment", "date", "date_approx", "judge",
          "judge_incentives", "reason", "evidence", "dissent", "supersedes",
          "change_basis", "change_detail", "framing_check", "recorder", "source", "volume",
          "layer", "layer_basis", "depends_on_layers", "missing_variables")


def _index(records):
    return dict((j.judgment_id, j) for j in judgments(records))


def root_of(by_id, jid):
    seen, cur = set(), by_id.get(jid)
    while cur is not None and cur.supersedes and cur.supersedes in by_id and cur.supersedes not in seen:
        seen.add(cur.judgment_id)
        cur = by_id[cur.supersedes]
    return cur


def lineage(records, jid):
    """List of steps in walk order: {depth, judgment_id, version, date, judge,
    change_basis, dissent_count, superseded_by}."""
    by_id = _index(records)
    if jid not in by_id:
        raise KeyError("no judgment %s" % jid)
    root = root_of(by_id, jid)
    out, stack, seen = [], [(root, 0)], set()
    while stack:
        j, depth = stack.pop()
        if j.judgment_id in seen:
            continue
        seen.add(j.judgment_id)
        out.append({"depth": depth, "judgment_id": j.judgment_id, "version": j.version,
                    "date": j.date, "date_approx": j.date_approx, "layer": j.layer,
                    "judge": (j.judge or {}).get("name_or_body"),
                    "change_basis": list(j.change_basis or []),
                    "dissent_count": len(j.dissent or []),
                    "superseded_by": list(j.superseded_by or [])})
        for nxt in reversed(j.superseded_by or []):
            if nxt in by_id:
                stack.append((by_id[nxt], depth + 1))
    return out


def format_lineage(steps):
    lines = []
    for s in steps:
        lines.append("%s%s v%s  [%s]  %s%s  %s  basis=%s  dissent=%d" % (
            "  " * s["depth"] + ("-> " if s["depth"] else ""), s["judgment_id"], s["version"],
            s["layer"] or "layer?",
            s["date"] or "(no date)", " (approx)" if s["date_approx"] else "",
            s["judge"] or "(no judge)", ",".join(s["change_basis"]) or "-", s["dissent_count"]))
    return "\n".join(lines)


def diff(records, a, b):
    by_id = _index(records)
    for x in (a, b):
        if x not in by_id:
            raise KeyError("no judgment %s" % x)
    ja, jb = by_id[a].to_dict(), by_id[b].to_dict()
    return dict((k, {"from": ja.get(k), "to": jb.get(k)}) for k in FIELDS if ja.get(k) != jb.get(k))

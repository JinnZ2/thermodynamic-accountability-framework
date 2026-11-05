#!/usr/bin/env python3
# checkout.py -- CC0, stdlib only, python >= 3.5
# Status: co-authored (Kavik + Claude), 2026-11-03.
#
# Run before an entry is handed to anyone. Cautions print FIRST, in plain
# language, above the method. The checkout is logged to the ledger (kind
# "checkout": entry id + optional date/region, no personal identifiers) so
# steps that are handed out and never reported read UNCONFIRMED, not fine.
#
#   python3 checkout.py ENTRY.json --ledger LEDGER [--date YYYY-MM-DD] [--region R] [--dry-run]

import json
import sys

import ledger
import status
from refs import index_entry


def render(entry, records, n_required=status.DEFAULT_N):
    rows, _ = status.compute([entry], records, n_required)
    by_ref = dict((r["ref"], r) for r in rows)
    lines = []
    cautions = [r for r in rows if "CAUTION" in r["flags"]]
    mixed = [r for r in rows if "ENVIRONMENT_DEPENDENT" in r["flags"]]
    for r in cautions:
        lines.append("CAUTION -- %s, step %s: %s" % (r["branch"], r["ref"].split(".")[-1], r["step"]))
        for c in r["caution"]:
            lines.append("   Field report: " + c)
        lines.append("   Do not do this step until someone has checked what went wrong.")
    for r in mixed:
        lines.append("MIXED RESULTS -- %s, step %s: worked in some places and failed in others. "
                     "Compare your conditions before trying it." % (r["branch"], r["ref"].split(".")[-1]))
        for g, gc in sorted(r["environment_groups"].items()):
            lines.append("   %s: worked %d, failed %d, unsafe %d" % (g, gc["worked"], gc["failed"], gc["UNSAFE"]))
    if cautions or mixed:
        lines.append("=" * 60)
    lines.append("%s  [%s]" % (entry.get("function"), entry.get("function_id")))
    for bi, b in enumerate(entry.get("branches") or []):
        lines.append("")
        lines.append("Branch %d: %s" % (bi + 1, b.get("name")))
        for j in b.get("junctions") or []:
            ref = "%s.%d.%s" % (entry.get("function_id"), bi + 1, j.get("id"))
            st = by_ref.get(ref, {}).get("state", "?")
            lines.append("  %s %s  (%s; field: %s)" % (j.get("id"), j.get("step"), j.get("provenance"), st))
            if j.get("irreversible"):
                lines.append("     CANNOT BE UNDONE: " + (j.get("hazard") or ""))
            if j.get("caution"):
                lines.append("     Entry caution: " + j["caution"])
    lines.append("")
    lines.append("Report back, one line, outcome word required:")
    lines.append("  FR1|<step address>|<version>|worked/partial/failed/UNSAFE|what happened")
    lines.append("  step addresses: " + ", ".join("%s=%s" % (k, v["version"]) for k, v in
                                                     sorted(index_entry(entry).items())))
    return "\n".join(lines)


def main(argv):
    def opt(name):
        if name in argv:
            i = argv.index(name)
            return argv[i + 1] if i + 1 < len(argv) else None
        return None
    if not argv or opt("--ledger") is None:
        sys.stderr.write("usage: checkout.py ENTRY.json --ledger LEDGER [--date D] [--region R] [--dry-run]\n")
        return 2
    with open(argv[0], encoding="utf-8") as f:
        entry = json.load(f)
    path = opt("--ledger")
    recs = ledger.read(path)
    probs = ledger.verify(recs)
    if probs:
        sys.stderr.write("ledger broken, refusing checkout: %s\n" % probs[0])
        return 1
    print(render(entry, recs))
    if "--dry-run" not in argv:
        body = {"entry": entry.get("function_id")}
        for k, flag in (("date", "--date"), ("coarse_region", "--region")):
            if opt(flag):
                body[k] = opt(flag)
        ledger.append(path, "checkout", body)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

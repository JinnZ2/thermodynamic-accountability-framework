#!/usr/bin/env python3
# status.py -- CC0, stdlib only, python >= 3.5
# Status: co-authored (Kavik + Claude), 2026-11-03.
#
# Per-junction field status from the ledger. READS entries, NEVER writes them:
# a report can raise caution; it can never rewrite a method or a provenance tag.
#
#   reports for ref ──┬─ any UNSAFE (any junction) ...................... CAUTION now
#                     ├─ any failed on an irreversible junction .......... CAUTION now
#                     ├─ worked AND failed/UNSAFE both present ........... ENVIRONMENT_DEPENDENT
#                     │      (kept apart, grouped by environment, never averaged)
#                     ├─ >= N independent builds, no caution ............. ELIGIBLE_FOR_TESTED
#                     │      build = worked + hands-on + scale small|full + current version
#                     │              + date + region; independent = distinct (date, region)
#                     │      counts BUILDS, not reports
#                     ├─ some reports, not enough builds ................. REPORTED
#   no reports ───────┼─ entry checked out (distributed) ................. UNCONFIRMED
#                     └─ never checked out ............................... NOT_DISTRIBUTED
#
#   Silence is not success: time passing never moves a state.
#   Warnings travel faster than confirmations: a blank or old version still
#   raises caution; only current-version builds count toward ELIGIBLE.
#   PROPOSED**: UNSAFE on any junction (not only irreversible) raises caution;
#   bench scale is not a build; older-version warnings keep caution until a
#   person clears it by editing the entry.
#
# Triage order of output: UNSAFE > failed > partial > worked > no reports.
#
#   python3 status.py LEDGER ENTRY.json [ENTRY.json ...] [--n 3]

import json
import sys

import ledger
from refs import index_entry

DEFAULT_N = 3
OUTCOME_RANK = {"UNSAFE": 0, "failed": 1, "partial": 2, "worked": 3}
STATE_RANK = ("CAUTION", "ENVIRONMENT_DEPENDENT", "ELIGIBLE_FOR_TESTED", "REPORTED",
              "UNCONFIRMED", "NOT_DISTRIBUTED")


def _env_key(r):
    e = r.get("environment") or {}
    return "climate=%s soil_water=%s temp=%s humidity=%s" % (
        e.get("climate", "?"), e.get("soil_water", "?"), e.get("temp", "?"), e.get("humidity", "?"))


def junction_status(ref, info, reps, distributed, n_required=DEFAULT_N):
    j = info["junction"]
    cur = info["version"]
    irreversible = j.get("irreversible") is True
    counts = {"UNSAFE": 0, "failed": 0, "partial": 0, "worked": 0}
    for r in reps:
        counts[r["outcome"]] += 1
    flags = []
    caution = []
    for r in reps:
        ver = r.get("junction_version")
        vnote = "" if ver == cur else (" (version unknown)" if not ver else " (reported on older text %s)" % ver)
        where = ", ".join(x for x in (r.get("coarse_region"), r.get("date")) if x) or "no region/date"
        if r["outcome"] == "UNSAFE":
            caution.append("UNSAFE: %s [%s]%s" % (r.get("failure_point") or "no detail given", where, vnote))
        elif r["outcome"] == "failed" and irreversible:
            caution.append("failed on an irreversible step: %s [%s]%s" % (
                r.get("failure_point") or "no detail given", where, vnote))
    builds = set()
    for r in reps:
        if (r["outcome"] == "worked" and r.get("reporter_relation") == "hands-on"
                and r.get("scale") in ("small", "full") and r.get("junction_version") == cur
                and r.get("date") and r.get("coarse_region")):
            builds.add((r["date"], r["coarse_region"]))
    groups = {}
    conflict = counts["worked"] and (counts["failed"] or counts["UNSAFE"])
    if conflict:
        flags.append("ENVIRONMENT_DEPENDENT")
        for r in reps:
            g = groups.setdefault(_env_key(r), {"UNSAFE": 0, "failed": 0, "partial": 0, "worked": 0})
            g[r["outcome"]] += 1
    if caution:
        flags.insert(0, "CAUTION")
    if len(builds) >= n_required and not caution:
        flags.append("ELIGIBLE_FOR_TESTED")
    if reps and not flags:
        flags.append("REPORTED")
    if not reps:
        flags.append("UNCONFIRMED" if distributed else "NOT_DISTRIBUTED")
    state = min(flags, key=STATE_RANK.index)
    worst = min([OUTCOME_RANK[r["outcome"]] for r in reps] or [4])
    return {"ref": ref, "branch": info["branch"], "step": j.get("step"), "irreversible": irreversible,
            "version": cur, "state": state, "flags": flags, "counts": counts,
            "independent_builds": len(builds), "builds_required": n_required,
            "caution": caution, "environment_groups": groups, "worst": worst}


def compute(entries, records, n_required=DEFAULT_N):
    """-> (rows sorted by triage, orphan reports)"""
    reps = ledger.reports(records)
    out_entries = set(c.get("entry") for c in ledger.checkouts(records))
    index = {}
    owner = {}
    for e in entries:
        for ref, info in index_entry(e).items():
            index[ref] = info
            owner[ref] = e.get("function_id")
    by_ref = {}
    orphans = []
    for r in reps:
        if r.get("junction_id") in index:
            by_ref.setdefault(r["junction_id"], []).append(r)
        else:
            orphans.append(r)
    rows = [junction_status(ref, info, by_ref.get(ref, []), owner[ref] in out_entries, n_required)
            for ref, info in index.items()]
    rows.sort(key=lambda x: (x["worst"], STATE_RANK.index(x["state"]), x["ref"]))
    return rows, orphans


def caution_refs(entries, records, n_required=DEFAULT_N):
    rows, _ = compute(entries, records, n_required)
    return dict((r["ref"], r) for r in rows if "CAUTION" in r["flags"])


def main(argv):
    n = DEFAULT_N
    if "--n" in argv:
        i = argv.index("--n")
        n = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    if len(argv) < 2:
        sys.stderr.write("usage: status.py LEDGER ENTRY.json [...] [--n 3]\n")
        return 2
    recs = ledger.read(argv[0])
    probs = ledger.verify(recs)
    if probs:
        sys.stderr.write("ledger broken: %s\n" % probs[0])
        return 1
    entries = []
    for p in argv[1:]:
        with open(p, encoding="utf-8") as f:
            entries.append(json.load(f))
    rows, orphans = compute(entries, recs, n)
    for r in rows:
        c = r["counts"]
        print("%-22s %-21s U%d F%d P%d W%d builds %d/%d  %s" % (
            r["ref"], r["state"], c["UNSAFE"], c["failed"], c["partial"], c["worked"],
            r["independent_builds"], r["builds_required"], ",".join(r["flags"])))
        for line in r["caution"]:
            print("    ! " + line)
        for g, gc in sorted(r["environment_groups"].items()):
            print("    env %s -> U%d F%d P%d W%d" % (g, gc["UNSAFE"], gc["failed"], gc["partial"], gc["worked"]))
    for o in orphans:
        print("ORPHAN report for unknown junction %s (%s)" % (o.get("junction_id"), o.get("outcome")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

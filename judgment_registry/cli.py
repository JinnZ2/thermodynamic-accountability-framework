#!/usr/bin/env python3
# cli.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-04.
#
#   python3 cli.py add RECORD.json        [--ledger L]   kind from the file's "kind" key
#                                                        (judgment if absent)
#   python3 cli.py check                  [--ledger L]   integrity flags; exit 1 if the chain is broken
#   python3 cli.py lineage ID             [--ledger L]
#   python3 cli.py diff A B               [--ledger L]
#   python3 cli.py export                 [--ledger L]   JSON with superseded_by derived
#   python3 cli.py axis ID                [--ledger L]   signal-axis variables of one intervention
#   python3 cli.py axis --compare A B     [--ledger L]   two interventions side by side
#   python3 cli.py labels ACT_ID          [--ledger L]   every label on one act, side by side
#   python3 cli.py assumptions --by-tag TAG [--ledger L] safety assumptions carrying a social tag
#   check also takes --as-of YYYY-MM-DD (date used for OUTCOME_UNRECORDED; default today)
#
# Default ledger: judgments.jsonl in the current directory.
# D-M6: every successful output starts with the line in HEADER, so a
# registry printout cannot be passed off as a validation. (export: the
# header line comes before the JSON; skip one line to parse it.)
# Exit: 0 ok | 1 chain broken / rejected | 2 usage

import json
import sys

import chain
import integrity
import labels
import ledger
import report
import safety_assumptions

HEADER = "Registered = documented, not correct."


def main(argv):
    path = "judgments.jsonl"
    if "--ledger" in argv:
        i = argv.index("--ledger")
        if i + 1 >= len(argv):
            return _usage()
        path = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    as_of = None
    if "--as-of" in argv:
        i = argv.index("--as-of")
        if i + 1 >= len(argv):
            return _usage()
        as_of = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if not argv:
        return _usage()
    cmd, args = argv[0], argv[1:]
    try:
        if cmd == "add" and len(args) == 1:
            with open(args[0], encoding="utf-8") as f:
                body = json.load(f)
            kind = body.pop("kind", "judgment")
            rec = ledger.append(path, kind, body)
            print(HEADER)
            print("appended %s %s" % (kind, rec["hash"][:12]))
            return 0
        recs = ledger.read(path)
        broken = ledger.verify(recs) + ledger.head_problems(path, recs)   # M10
        if cmd == "check" and not args:
            print(HEADER)
            for p in broken:
                print("CHAIN " + p)
            if broken:
                return 1
            flags = integrity.check(recs, as_of=as_of)
            for fl in flags:
                print("%-30s %-14s %s" % (fl["flag"], fl["about"], fl["detail"]))
            print("%d record(s), %d flag(s). Flags are about completeness, not correctness."
                  % (len(recs), len(flags)))
            return 0
        if broken:
            sys.stderr.write("chain broken: %s\n" % broken[0])
            return 1
        if cmd == "lineage" and len(args) == 1:
            steps = chain.lineage(recs, args[0])
            print(HEADER)
            print(chain.format_lineage(steps))
            return 0
        if cmd == "diff" and len(args) == 2:
            d = chain.diff(recs, args[0], args[1])
            print(HEADER)
            print(json.dumps(d, indent=2, ensure_ascii=False))
            return 0
        if cmd == "axis" and len(args) == 1:
            text = report.axis(recs, args[0])
            print(HEADER)
            print(text)
            return 0
        if cmd == "axis" and len(args) == 3 and args[0] == "--compare":
            text = report.compare(recs, args[1], args[2])
            print(HEADER)
            print(text)
            return 0
        if cmd == "labels" and len(args) == 1:
            print(HEADER)
            print(labels.side_by_side(recs, args[0]))
            return 0
        if cmd == "assumptions" and len(args) == 2 and args[0] == "--by-tag":
            tag = args[1]
            if tag not in safety_assumptions.SOCIAL_ASSUMPTION_TAGS:
                sys.stderr.write("tag must be one of %s\n" % ", ".join(safety_assumptions.SOCIAL_ASSUMPTION_TAGS))
                return 2
            rows = safety_assumptions.by_tag(recs, tag)
            print(HEADER)
            print("tag %s (%s): %d assumption(s), ledger order" % (
                tag, safety_assumptions.SOCIAL_ASSUMPTION_TAGS[tag], len(rows)))
            for sa in rows:
                print("%-8s v%-3s %-12s %-28s %s" % (sa["sa_id"], sa.get("version") or "-", sa.get("date") or "-",
                                                  (sa.get("holder") or "-")[:28], sa["statement"]))
                print("         tags: %s (tagged by %s)" % (", ".join(sa["social_assumption_tags"]),
                                                          sa.get("tagged_by") or "-"))
            return 0
        if cmd == "export" and not args:
            print(HEADER)
            out = []
            for j in ledger.judgments(recs):
                d = j.to_dict()
                d["superseded_by"] = j.superseded_by
                out.append(d)
            print(json.dumps({"judgments": out,
                              "applications": ledger.bodies(recs, "application"),
                              "transfers": ledger.bodies(recs, "transfer"),
                              "withdrawals": ledger.bodies(recs, "withdrawal"),
                              "interventions": ledger.bodies(recs, "intervention"),
                              "acts": ledger.bodies(recs, "act"),
                              "labels": ledger.bodies(recs, "label"),
                              "experiments": ledger.bodies(recs, "experiment"),
                              "safety_assumptions": ledger.bodies(recs, "safety_assumption")},
                             indent=2, ensure_ascii=False))
            return 0
    except (OSError, ValueError, KeyError) as e:
        sys.stderr.write("REJECTED: %s\n" % e)
        return 1
    return _usage()


def _usage():
    sys.stderr.write("usage: cli.py add FILE | check [--as-of DATE] | lineage ID | diff A B | export | "
                     "axis ID | axis --compare A B | labels ACT_ID | assumptions --by-tag TAG  [--ledger PATH]\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

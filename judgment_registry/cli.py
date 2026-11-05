#!/usr/bin/env python3
# cli.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (Kavik + Claude), 2026-11-04.
#
#   python3 cli.py add RECORD.json        [--ledger L]   kind from the file's "kind" key
#                                                        (judgment if absent)
#   python3 cli.py check                  [--ledger L]   integrity flags; exit 1 if the chain is broken
#   python3 cli.py lineage ID             [--ledger L]
#   python3 cli.py diff A B               [--ledger L]
#   python3 cli.py export                 [--ledger L]   JSON with superseded_by derived
#
# Default ledger: judgments.jsonl in the current directory.
# Exit: 0 ok | 1 chain broken / rejected | 2 usage

import json
import sys

import chain
import integrity
import ledger


def main(argv):
    path = "judgments.jsonl"
    if "--ledger" in argv:
        i = argv.index("--ledger")
        if i + 1 >= len(argv):
            return _usage()
        path = argv[i + 1]
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
            print("appended %s %s" % (kind, rec["hash"][:12]))
            return 0
        recs = ledger.read(path)
        broken = ledger.verify(recs)
        if cmd == "check" and not args:
            for p in broken:
                print("CHAIN " + p)
            if broken:
                return 1
            flags = integrity.check(recs)
            for fl in flags:
                print("%-30s %-14s %s" % (fl["flag"], fl["about"], fl["detail"]))
            print("%d record(s), %d flag(s). Flags are about completeness, not correctness."
                  % (len(recs), len(flags)))
            return 0
        if broken:
            sys.stderr.write("chain broken: %s\n" % broken[0])
            return 1
        if cmd == "lineage" and len(args) == 1:
            print(chain.format_lineage(chain.lineage(recs, args[0])))
            return 0
        if cmd == "diff" and len(args) == 2:
            print(json.dumps(chain.diff(recs, args[0], args[1]), indent=2, ensure_ascii=False))
            return 0
        if cmd == "export" and not args:
            out = []
            for j in ledger.judgments(recs):
                d = j.to_dict()
                d["superseded_by"] = j.superseded_by
                out.append(d)
            print(json.dumps({"judgments": out,
                              "applications": ledger.bodies(recs, "application"),
                              "transfers": ledger.bodies(recs, "transfer"),
                              "withdrawals": ledger.bodies(recs, "withdrawal")},
                             indent=2, ensure_ascii=False))
            return 0
    except (OSError, ValueError, KeyError) as e:
        sys.stderr.write("REJECTED: %s\n" % e)
        return 1
    return _usage()


def _usage():
    sys.stderr.write("usage: cli.py add FILE | check | lineage ID | diff A B | export  [--ledger PATH]\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

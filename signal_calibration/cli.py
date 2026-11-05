#!/usr/bin/env python3
# cli.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-04.
#
#   python3 cli.py register prereg/T2.json --log L
#   python3 cli.py run prereg/T2.json --log L [--registry R] [--date D] [--recorder ROLE]
#                    model access: CommandAdapter, from $SIGCAL_COMMAND / $SIGCAL_MODEL_ID
#   python3 cli.py export-csv --log L --out scores.csv [--test T2]
#   python3 cli.py import-csv scores.csv --log L --scorer ROLE [--auto]
#   python3 cli.py field-report report.json --log L
#   python3 cli.py report --log L
#   python3 cli.py verify --log L
# Exit: 0 ok | 1 refused | 2 usage

import json
import sys

import chainlog
import prereg
import report
import runner
from adapters.base import AdapterError, CommandAdapter
from scoring import rubrics

FIELD_REPORT_KEYS = ("source", "model_id", "test_ref", "summary", "tag", "recorder")


def _opt(argv, name, default=None):
    if name in argv:
        i = argv.index(name)
        if i + 1 >= len(argv):
            raise SystemExit(_usage())
        v = argv[i + 1]
        del argv[i:i + 2]
        return v
    return default


def main(argv):
    argv = list(argv)
    try:
        log = _opt(argv, "--log")
        reg = _opt(argv, "--registry")
        date = _opt(argv, "--date")
        rec = _opt(argv, "--recorder", "runner")
        out = _opt(argv, "--out")
        test = _opt(argv, "--test")
        scorer = _opt(argv, "--scorer")
        auto = "--auto" in argv
        argv = [a for a in argv if a != "--auto"]
    except SystemExit as e:
        return e.code
    if not argv or not log:
        return _usage()
    cmd, args = argv[0], argv[1:]
    try:
        if cmd == "register" and len(args) == 1:
            print("registered %s" % prereg.register(args[0], log)[:12])
        elif cmd == "run" and len(args) == 1:
            res = runner.run(args[0], CommandAdapter(), log, registry_path=reg, date=date, recorder=rec)
            print("%d result(s) appended" % len(res))
        elif cmd == "export-csv" and not args and out:
            print("%d row(s) written to %s" % (rubrics.export_csv(log, out, test_id=test), out))
        elif cmd == "import-csv" and len(args) == 1 and scorer:
            print("%d score(s) appended" % rubrics.import_csv(log, args[0], scorer, "auto" if auto else "human"))
        elif cmd == "field-report" and len(args) == 1:
            with open(args[0], encoding="utf-8") as f:
                body = json.load(f)
            miss = [k for k in FIELD_REPORT_KEYS if not body.get(k)]
            if miss:
                raise ValueError("field report needs %s" % ", ".join(miss))
            chainlog.append(log, "field_report", body)
            print("field report appended")
        elif cmd == "report" and not args:
            recs = chainlog.read(log)
            hp = chainlog.head_problems(log, recs)
            print("HEAD " + hp[0] if hp else report.build(recs))
        elif cmd == "verify" and not args:
            recs = chainlog.read(log)
            probs = chainlog.verify(recs) + chainlog.head_problems(log, recs)
            for p in probs:
                print("CHAIN " + p)
            return 1 if probs else 0
        else:
            return _usage()
    except (OSError, ValueError, KeyError, AdapterError) as e:
        sys.stderr.write("REFUSED: %s\n" % e)
        return 1
    return 0


def _usage():
    sys.stderr.write("usage: cli.py register PREREG | run PREREG [--registry R] | export-csv --out F | "
                     "import-csv F --scorer ROLE [--auto] | field-report F | report | verify   --log L\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

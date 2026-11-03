#!/usr/bin/env python3
# cli.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (Kavik + Claude).
#
#   python cli.py check                     validation + level check
#   python cli.py rank                      criticality, highest first
#   python cli.py spof                      single points of failure
#   python cli.py order                     restoration order
#   python cli.py gaps COMMUNITY.json       L0/L1 items with no local holder
#   python cli.py pair A.json B.json        what to exchange before tying islands
#   add  --items PATH  to use another item file
#
# Exit: 0 ok | 1 validation failure (check) | 2 usage / unreadable file

import sys

import chain
import community


def _p(s=""):
    sys.stdout.write(s + "\n")


def cmd_check(items):
    rep = chain.validate(items)
    for k in ("field", "unknown_ids", "parallel_as_prereq"):
        for row in rep[k]:
            _p("FAIL %-20s %s" % (k, row))
    for cyc in rep["cycles"]:
        _p("FAIL cycle               " + " -> ".join(cyc))
    lc = chain.level_check(items)
    for i, il, d, dl in lc:
        _p("LEVEL  L%d %-26s depends on L%d %s" % (il, i, dl, d))
    _p("%d items; %s; %d level inversions (findings, not errors)" % (
        len(items), "valid" if chain.is_clean(rep) else "INVALID", len(lc)))
    return 0 if chain.is_clean(rep) else 1


def cmd_rank(items):
    _p("%-28s %3s %7s %5s %6s %4s %5s  %s" % ("id", "L", "score", "deps", "direct", "sub", "hrs", "volume/status"))
    for r in chain.rank(items):
        _p("%-28s %3d %7.2f %5d %6d %4s %5s  %s/%s" % (
            r["id"], r["level"], r["score"], r["dependents"], r["direct_dependents"],
            "y" if r["substitute"] else "-", "y" if r["hours_known"] else "null",
            r["volume"], r["status"]))
    _p("score = dependents x (0.3 if substitute else 1) x (1/hours if known else 1)")
    return 0


def cmd_spof(items):
    rows = chain.spof(items)
    for r in rows:
        _p("L%d %-26s %2d dependents: %s" % (r["level"], r["id"], len(r["dependents"]), ", ".join(r["dependents"])))
    _p("%d single points of failure (no substitute, no local holder, >= 2 dependents)" % len(rows))
    return 0


def cmd_order(items):
    seq, stuck = chain.order(items)
    for n, k in enumerate(seq, 1):
        it = items[k]
        _p("%2d. L%d %-28s %s" % (n, it.level, k, "(parallel input; never waited on)" if it.parallel_input else ""))
    for k in stuck:
        _p(" ?  L%d %-28s UNRESOLVED (in or behind a cycle)" % (items[k].level, k))
    return 0


def cmd_gaps(items, path):
    c = community.load_community(path)
    for k in community.unknown_item_ids(c, items):
        _p("WARN holder for unknown item id: " + k)
    rows = community.gaps(c, items)
    _p("== %s: %d L0/L1 items with no local holder" % (c.name, len(rows)))
    for r in rows:
        _p("  L%d %-28s substitute: %s" % (r["level"], r["id"], r["substitute"] or "NONE"))
    if c.buffer_hours:
        _p("buffer hours (segment holds without grid):")
        for seg, h in sorted(c.buffer_hours.items()):
            _p("  %-28s %s" % (seg, "null" if h is None else h))
    return 0


def cmd_pair(items, pa, pb):
    a, b = community.load_community(pa), community.load_community(pb)
    r = community.interconnect(a, b, items)
    _p("== %s <-> %s" % (r["a"], r["b"]))
    _p("L3 both lack: " + (", ".join(r["both_lack_L3"]) or "(none)"))
    _p("%s can offer %s: %s" % (r["a"], r["b"], ", ".join(r["a_offers_b"]) or "(none)"))
    _p("%s can offer %s: %s" % (r["b"], r["a"], ", ".join(r["b_offers_a"]) or "(none)"))
    return 0


def main(argv):
    path = chain.DEFAULT_ITEMS
    if "--items" in argv:
        i = argv.index("--items")
        if i + 1 >= len(argv):
            return 2
        path = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if not argv:
        sys.stderr.write(__doc__ if __doc__ else open(__file__).read().split("import sys")[0])
        return 2
    try:
        items = chain.load(path)
        cmd = argv[0]
        if cmd == "check":
            return cmd_check(items)
        if cmd == "rank":
            return cmd_rank(items)
        if cmd == "spof":
            return cmd_spof(items)
        if cmd == "order":
            return cmd_order(items)
        if cmd == "gaps" and len(argv) == 2:
            return cmd_gaps(items, argv[1])
        if cmd == "pair" and len(argv) == 3:
            return cmd_pair(items, argv[1], argv[2])
    except BrokenPipeError:            # output piped to head/less and closed early
        return 0
    except (IOError, OSError, ValueError) as e:
        sys.stderr.write("cannot read input: %s\n" % e)
        return 2
    sys.stderr.write("usage: cli.py check|rank|spof|order|gaps C.json|pair A.json B.json [--items PATH]\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

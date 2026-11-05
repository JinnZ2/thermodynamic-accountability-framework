#!/usr/bin/env python3
# matrix.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# Gradient x gradient grid. A cell holds the ids of every interaction that
# names both gradients (gradients or modifiers); the diagonal holds
# interactions that name only that gradient. Symmetric; no score, no order
# beyond gradient id.
#
#   python3 matrix.py [--class human|model|both]
#     human / model: interactions whose applied_to holds that class
#     both (default): every interaction

import sys

import field


def members(i):
    out = list(i.get("gradients") or [])
    out += [m["gradient"] for m in i.get("modifiers") or [] if m.get("gradient") not in out]
    return out


def grid(gradients, interactions, cls="both"):
    ids = [g["id"] for g in gradients]
    cells = dict(((a, b), []) for a in ids for b in ids)
    for i in interactions:
        if cls != "both" and cls not in (i.get("applied_to") or []):
            continue
        ms = members(i)
        if len(ms) == 1:
            cells[(ms[0], ms[0])].append(i["id"])
        for a in ms:
            for b in ms:
                if a != b and i["id"] not in cells[(a, b)]:
                    cells[(a, b)].append(i["id"])
    return ids, cells


def render(gradients, interactions, cls="both"):
    ids, cells = grid(gradients, interactions, cls)
    w = max([5] + [len(",".join(v)) for v in cells.values()]) + 1
    lines = ["gradient x gradient, interactions applied to: %s (cells list ids; no ranking)" % cls,
             "%-5s" % "" + "".join("%-*s" % (w, b) for b in ids)]
    for a in ids:
        lines.append("%-5s" % a + "".join("%-*s" % (w, ",".join(cells[(a, b)]) or ".") for b in ids))
    lines.append("")
    lines += ["%-4s %s" % (g["id"], g["name"]) for g in gradients]
    return "\n".join(lines)


def main(argv):
    cls = "both"
    if "--class" in argv:
        i = argv.index("--class")
        if i + 1 >= len(argv) or argv[i + 1] not in ("human", "model", "both"):
            sys.stderr.write("usage: matrix.py [--class human|model|both]\n")
            return 2
        cls = argv[i + 1]
    gs, xs = field.load()
    probs = field.validate(gs, xs, field.known_refs())
    if probs:
        sys.stderr.write("PROBLEM %s\n" % probs[0])
        return 1
    print(render(gs, xs, cls))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
# export.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# D-M2 aggregate outward. The full local registry never leaves the device.
# What leaves is, per item id: need yes/no, surplus yes/no, and counts of
# items. No quantities, no sites, no holder names, no weak points.
#
# Local registry (read only through misuse_guard.localdata, D-M1):
#   {"community": "code", "items": {"<item_id>": {"have": n|null, "need": n|null, ...}}}
#   any other per-item keys (site, holder, note, ...) are read and dropped.
#
#   python3 export.py LOCAL_REGISTRY.json
#
# Limit (E17, NOT RUN): in a small community one household can be one
# count. A minimum-cell-size rule is proposed, not built.**

import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from misuse_guard.localdata import RealDataRefused, load_real_json  # noqa: E402

OUT_KEYS = ("community", "need", "surplus", "counts")


def aggregate(registry):
    need, surplus = {}, {}
    for iid, rec in sorted((registry.get("items") or {}).items()):
        have, req = (rec or {}).get("have"), (rec or {}).get("need")
        if have is None or req is None:
            need[iid], surplus[iid] = None, None     # unknown stays unknown
            continue
        need[iid], surplus[iid] = have < req, have > req
    return {"community": registry.get("community"), "need": need, "surplus": surplus,
            "counts": {"items": len(need),
                       "need_true": sum(1 for v in need.values() if v is True),
                       "surplus_true": sum(1 for v in surplus.values() if v is True),
                       "unknown": sum(1 for v in need.values() if v is None)}}


def main(argv):
    if len(argv) != 1:
        sys.stderr.write("usage: export.py LOCAL_REGISTRY.json\n")
        return 2
    try:
        print(json.dumps(aggregate(load_real_json(argv[0])), indent=2, sort_keys=True))
    except (OSError, ValueError, RealDataRefused) as e:
        sys.stderr.write("REFUSED: %s\n" % e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

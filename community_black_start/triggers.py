#!/usr/bin/env python3
# triggers.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# D-M4 trigger ranges. A published threshold is a RANGE {low, high}, never a
# single value, so the exact point at which a community acts cannot be read
# off the repository and baited. Exact values live only in a local config
# (local_data/, read through misuse_guard.localdata, D-M1).
#
# PUBLISHED holds one entry per threshold-kind item in items.json. Every
# bound is null: no number is known for any community, and none is invented
# (volume thin). A community fills its own exact values locally.
#
#   published_problems(table)  -> list; a scalar or a low >= high is refused
#   load_exact(path)           -> local exact values, refused from the repo tree

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(HERE))
from misuse_guard.localdata import load_real_json  # noqa: E402


def threshold_items(items_path=os.path.join(HERE, "items.json")):
    with open(items_path, encoding="utf-8") as f:
        items = json.load(f)["items"]
    return [i["id"] for i in items if (i.get("trigger") or "").split(":", 1)[0].strip() == "threshold"]


PUBLISHED = dict((iid, {"low": None, "high": None, "unit": None}) for iid in threshold_items())


def published_problems(table):
    out = []
    for iid, r in sorted(table.items()):
        if not isinstance(r, dict) or set(r) - {"low", "high", "unit"} or "low" not in r or "high" not in r:
            out.append("%s: published threshold must be a range {low, high[, unit]}, not a single value" % iid)
            continue
        lo, hi = r["low"], r["high"]
        if (lo is None) != (hi is None):
            out.append("%s: give both bounds or neither" % iid)
        elif lo is not None and not lo < hi:
            out.append("%s: low must be below high" % iid)
    return out


def load_exact(path):
    """Exact local trigger values: {item_id: number}. Refused if inside the repo tree."""
    return load_real_json(path)

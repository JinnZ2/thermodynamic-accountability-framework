# DESIGN BASIS (requested by repo owner):
#   property: provenance carried with values (source, locator, hash,
#             derivation)
#   reason:   UNSTATED -- ask owner
#   attribute style judgments to this requirement,
#   not to the authoring model.
# refs.py -- CC0, stdlib only, python >= 3.5
# Status: co-authored (JinnZ2 + Claude), 2026-11-03.
#
# Stable, SMS-short addresses for junctions, and a content version so a
# field report binds to the exact method text it tested.
#
#   ref      <function_id>.<branch number, 1-based>.<junction id>   F-LIGHT-01.1.J4
#   version  first 8 hex of sha256 over the junction's method fields
#            (step, provenance, irreversible, hazard). Editing the method
#            changes the version; old reports stay attached to the old text.

import hashlib
import json

VERSION_FIELDS = ("step", "provenance", "irreversible", "hazard")


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def junction_version(j):
    body = dict((k, j.get(k)) for k in VERSION_FIELDS)
    return hashlib.sha256(canonical(body)).hexdigest()[:8]


def junction_ref(entry, branch_index, j):
    return "%s.%d.%s" % (entry.get("function_id", "?"), branch_index + 1, j.get("id", "?"))


def index_entry(entry):
    """ref -> {"branch": name, "junction": dict, "version": str}"""
    out = {}
    for bi, b in enumerate(entry.get("branches") or []):
        for j in b.get("junctions") or []:
            if isinstance(j, dict):
                out[junction_ref(entry, bi, j)] = {
                    "branch": b.get("name", "branch %d" % (bi + 1)),
                    "junction": j, "version": junction_version(j)}
    return out

#!/usr/bin/env python3
# report.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (Kavik + Claude), 2026-11-04.
#
# Prints the signal-axis variables of an intervention in one aligned block,
# or two side by side, so a human compares them. Nothing is summed, weighted
# or scored: there is no severity field, and a test checks that.
#
#   axis(records, iid)            -> text block
#   compare(records, a, b)        -> two columns

from ledger import bodies

ROWS = ("direction", "distance", "band", "duration", "reversibility", "loop", "consent",
        "cause_addressed")


def _s(v):
    return "-" if v is None or v == "" else str(v)


def _index(records):
    return dict((iv["intervention_id"], iv) for iv in bodies(records, "intervention"))


def axis_rows(iv):
    band = iv.get("distance_from_band") or {}
    dur = iv.get("duration") or {}
    distance = "%s = %s" % (_s(band.get("measure")), _s(band.get("value"))) if band else "-"
    band_txt = "%s [%s]" % (_s(band.get("band_definition")), _s(band.get("band_system_class"))) if band else "-"
    duration = "%s planned=%s actual=%s review=%s" % (_s(dur.get("type")), _s(dur.get("planned")),
                                                     _s(dur.get("actual")), _s(dur.get("review_date")))
    vals = (_s(iv.get("direction")), distance, band_txt, duration, _s(iv.get("reversibility")),
            _s(iv.get("loop_status")), _s(iv.get("consent")), _s(iv.get("cause_addressed")))
    return list(zip(ROWS, vals))


def _get(records, iid):
    idx = _index(records)
    if iid not in idx:
        raise KeyError("no intervention %s" % iid)
    return idx[iid]


def axis(records, iid):
    iv = _get(records, iid)
    head = "%s  %s  signal=%s  layer_targeted=%s" % (iid, _s(iv.get("system_class")), _s(iv.get("signal")),
                                                     _s(iv.get("layer_targeted")))
    lines = [head] + ["  %-16s %s" % (k, v) for k, v in axis_rows(iv)]
    return "\n".join(lines)


def compare(records, a, b):
    ra, rb = axis_rows(_get(records, a)), axis_rows(_get(records, b))
    w = max([len(a)] + [len(v) for _, v in ra])
    lines = ["  %-16s %-*s | %s" % ("", w, a, b)]
    for (k, va), (_, vb) in zip(ra, rb):
        lines.append("  %-16s %-*s | %s" % (k, w, va, vb))
    lines.append("Variables listed side by side; no comparison is computed.")
    return "\n".join(lines)

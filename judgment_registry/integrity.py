#!/usr/bin/env python3
# integrity.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (Kavik + Claude), 2026-11-04.
#
# Flags are about COMPLETENESS, not CORRECTNESS. Every flag says something is
# missing, unchained or unstated. None says a judgment, judge or tradition is
# right or wrong; none ranks; none resolves a disagreement. Conflicting
# judgments by different judges coexist, each with its own scope.
#
#   MISSING_FIELD                 required field empty (lists which)
#   NO_SOURCE                     record has no documented source
#   UNCHAINED_CHANGE              later record, same judge + scope.who + act_type, no supersedes link
#   CHANGE_BASIS_UNSTATED         supersedes set, change_basis empty or only NONE_STATED
#   NO_NEW_CONDITIONS_OR_EVIDENCE supersedes set, environment and evidence identical to the
#                                 superseded record (change recorded, no material basis listed)
#   DISSENT_DROPPED               dissent in N absent from N+1, no withdrawal by its holder
#   INCENTIVES_UNRECORDED         judge_incentives is null
#   NO_FRAMING_CHECK              framing_check is null (informational)
#   SCOPE_TRANSFER                application outside recorded scope / environment / dates,
#                                 no transfer record
#   SUPERSEDES_NOT_FOUND          supersedes points to an id not in the ledger
#   SUPERSESSION_FORK             two or more records supersede the same record (informational)
#
# Layer flags (addendum 2026-11-04):
#   LAYER_UNSTATED                layer field empty
#   SKIPPED_LAYER                 layer = agency, no physics AND no sensor basis
#                                 (in layer_basis or via depends_on_layers)
#   SUBJECT_STATUS_UNSTATED       layer = agency, subject_status missing
#   SUBJECT_OPEN                  subject_status = OPEN (informational)
#   CONSENT_UNSTATED              layer = agency, consent missing
#   LOOP_UNSTATED                 layer = agency, loop missing
#   CROSS_SYSTEM_TRANSFER         basis recorded for one system_class, used for another,
#                                 no transfer record (extends SCOPE_TRANSFER)
#   LAYER_DEPENDENCY_NOT_FOUND    depends_on_layers id not in the ledger
#
# UNCHAINED_CHANGE keys on the SAME JUDGE: two judges on one scope coexist
# and are not a replacement. A judge's own later record on the same scope
# with no link is the silent-replacement shape. The key also carries the
# layer: one judge's physics record and agency record on the same scope are
# two layers, not a replacement.

from ledger import bodies, judgments
from schema import _blank

FLAGS = {
    "MISSING_FIELD": "required field(s) empty: {fields}",
    "NO_SOURCE": "no documented source recorded for this claim",
    "UNCHAINED_CHANGE": "same judge, scope and act type as {earlier}; no supersedes link recorded",
    "CHANGE_BASIS_UNSTATED": "supersedes {prior}; change_basis not stated",
    "NO_NEW_CONDITIONS_OR_EVIDENCE": "supersedes {prior}; environment and evidence entered are identical "
                                     "to it; no material basis listed (completeness note only)",
    "DISSENT_DROPPED": "dissent ({holder}: {position}) present in {prior}, not carried here, "
                       "no withdrawal by its holder recorded",
    "INCENTIVES_UNRECORDED": "judge_incentives not recorded",
    "NO_FRAMING_CHECK": "framing_check not recorded (informational)",
    "SCOPE_TRANSFER": "application {app} differs from the recorded {what}; no transfer record",
    "SUPERSEDES_NOT_FOUND": "supersedes {prior}, which is not in this ledger",
    "SUPERSESSION_FORK": "superseded by more than one record: {ids} (informational)",
    "LAYER_UNSTATED": "layer not stated (physics | sensor | agency)",
    "SKIPPED_LAYER": "layer is agency; no physics or sensor basis recorded here or via depends_on_layers",
    "SUBJECT_STATUS_UNSTATED": "layer is agency; subject_status not stated",
    "SUBJECT_OPEN": "subject_status is OPEN; the claim rests on an open question (informational)",
    "CONSENT_UNSTATED": "layer is agency; consent not stated",
    "LOOP_UNSTATED": "layer is agency; loop not stated",
    "CROSS_SYSTEM_TRANSFER": "{basis} recorded for system class '{src}', used here for '{dst}'; "
                             "no transfer record",
    "LAYER_DEPENDENCY_NOT_FOUND": "depends_on_layers lists {dep}, which is not in this ledger",
}

AGENCY_FIELDS = (("subject_status", "SUBJECT_STATUS_UNSTATED"), ("consent", "CONSENT_UNSTATED"),
                 ("loop", "LOOP_UNSTATED"))

SCOPE_KEYS = ("who", "act_type", "conditions")


def flag(code, about, **kw):
    return {"flag": code, "about": about, "detail": FLAGS[code].format(**kw)}


def _norm(v):
    if isinstance(v, str):
        return " ".join(v.lower().split())
    if isinstance(v, list):
        return sorted(_norm(x) for x in v)
    if isinstance(v, dict):
        return dict((k, _norm(x)) for k, x in v.items())
    return v


def _scope_key(j):
    s = j.scope or {}
    return (_norm((j.judge or {}).get("name_or_body")), _norm(s.get("who")), _norm(s.get("act_type")),
            j.layer or "")


def _block(j, name):
    b = (j.layer_basis or {}).get(name)
    if isinstance(b, dict) and any(not _blank(v) for v in b.values()):
        return b
    return None


def _cls(j, name):
    b = _block(j, name) if name else None
    c = (b or {}).get("system_class")
    return None if _blank(c) else _norm(c)


def _layer_flags(j, by_id, jt_transfers):
    a, out = j.judgment_id, []
    if _blank(j.layer):
        out.append(flag("LAYER_UNSTATED", a))
    deps = []
    for d in j.depends_on_layers or []:
        if d in by_id:
            deps.append(by_id[d])
        else:
            out.append(flag("LAYER_DEPENDENCY_NOT_FOUND", a, dep=d))
    if j.layer == "agency":
        lower = [n for n in ("physics", "sensor") if _block(j, n)]
        lower += [d.layer for d in deps if d.layer in ("physics", "sensor")]
        if not lower:
            out.append(flag("SKIPPED_LAYER", a))
        ag = _block(j, "agency") or {}
        for key, code in AGENCY_FIELDS:
            if _blank(ag.get(key)):
                out.append(flag(code, a))
        if ag.get("subject_status") == "OPEN":
            out.append(flag("SUBJECT_OPEN", a))
    dst = _cls(j, j.layer)
    if dst and a not in jt_transfers:
        sources = [("own %s basis" % n, _cls(j, n)) for n in ("physics", "sensor", "agency") if n != j.layer]
        sources += [("%s basis of %s" % (d.layer, d.judgment_id), _cls(d, d.layer)) for d in deps]
        for basis, src in sources:
            if src and src != dst:
                out.append(flag("CROSS_SYSTEM_TRANSFER", a, basis=basis, src=src, dst=dst))
    return out


def _evidence_set(j):
    return sorted((_norm(e.get("item")), e.get("tag"), _norm(e.get("source"))) for e in j.evidence or [])


def _dkey(d):
    return (_norm(d.get("holder")), _norm(d.get("position")))


def check(records):
    js = judgments(records)
    by_id = dict((j.judgment_id, j) for j in js)
    withdrawn = set((w["judgment_id"], _norm(w.get("holder")), _norm(w.get("position")))
                    for w in bodies(records, "withdrawal") if w.get("withdrawn_by_holder"))
    jt_transfers = set(t.get("judgment_id") for t in bodies(records, "transfer") if t.get("judgment_id"))
    out = []
    seen_keys = {}
    for j in js:
        a = j.judgment_id
        miss = j.missing()
        if miss:
            out.append(flag("MISSING_FIELD", a, fields=", ".join(miss)))
        if not (j.source or "").strip():
            out.append(flag("NO_SOURCE", a))
        if j.judge_incentives is None:
            out.append(flag("INCENTIVES_UNRECORDED", a))
        if j.framing_check is None:
            out.append(flag("NO_FRAMING_CHECK", a))
        out.extend(_layer_flags(j, by_id, jt_transfers))
        key = _scope_key(j)
        if all(key[:3]) and key in seen_keys and not j.supersedes:
            out.append(flag("UNCHAINED_CHANGE", a, earlier=seen_keys[key]))
        if all(key[:3]):
            seen_keys.setdefault(key, a)
        if j.superseded_by and len(j.superseded_by) > 1:
            out.append(flag("SUPERSESSION_FORK", a, ids=", ".join(j.superseded_by)))
        if j.supersedes:
            p = by_id.get(j.supersedes)
            if p is None:
                out.append(flag("SUPERSEDES_NOT_FOUND", a, prior=j.supersedes))
                continue
            basis = [b for b in j.change_basis or [] if b != "NONE_STATED"]
            if not basis:
                out.append(flag("CHANGE_BASIS_UNSTATED", a, prior=p.judgment_id))
            if _norm(j.environment) == _norm(p.environment) and _evidence_set(j) == _evidence_set(p):
                out.append(flag("NO_NEW_CONDITIONS_OR_EVIDENCE", a, prior=p.judgment_id))
            now = set(_dkey(d) for d in j.dissent or [])
            for d in p.dissent or []:
                k = _dkey(d)
                if k not in now and (p.judgment_id,) + k not in withdrawn:
                    out.append(flag("DISSENT_DROPPED", a, prior=p.judgment_id,
                                    holder=d.get("holder"), position=d.get("position")))
    transfers = set(t.get("application_id") for t in bodies(records, "transfer"))
    for ap in bodies(records, "application"):
        j = by_id.get(ap.get("judgment_id"))
        if j is None:
            continue
        diffs = []
        for k in SCOPE_KEYS:
            if k in (ap.get("scope") or {}) and _norm(ap["scope"][k]) != _norm((j.scope or {}).get(k)):
                diffs.append("scope." + k)
        if ap.get("environment") and _norm(ap["environment"]) != _norm(j.environment):
            diffs.append("environment")
        dates = (j.scope or {}).get("dates") or {}
        d = ap.get("date")
        if d and ((dates.get("from") and d < dates["from"]) or (dates.get("to") and d > dates["to"])):
            diffs.append("dates")
        if diffs and ap.get("application_id") not in transfers:
            out.append(flag("SCOPE_TRANSFER", ap.get("application_id"),
                            app=ap.get("application_id"), what=", ".join(diffs)))
        sc = (ap.get("scope") or {}).get("system_class")
        src = _cls(j, j.layer)
        if not _blank(sc) and src and _norm(sc) != src and ap.get("application_id") not in transfers:
            out.append(flag("CROSS_SYSTEM_TRANSFER", ap.get("application_id"),
                            basis="%s basis of %s" % (j.layer, j.judgment_id), src=src, dst=_norm(sc)))
    return out


def summary(flags):
    counts = {}
    for f in flags:
        counts[f["flag"]] = counts.get(f["flag"], 0) + 1
    return counts

#!/usr/bin/env python3
# integrity.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-04.
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
#   DISSENT_DROPPED               dissent in N absent from N+1, no confirmed withdrawal by its holder
#   DISSENT_WITHDRAWAL_UNCONFIRMED withdrawal with no confirmation on record: holder via a contact
#                                 path recorded earlier, or (anonymous holder) steward + second
#                                 under the two-person rule (M25, 2026-11-05). An unconfirmed
#                                 withdrawal does not clear DISSENT_DROPPED.
#   INCENTIVES_UNRECORDED         judge_incentives is null
#   NO_FRAMING_CHECK              framing_check is null (informational)
#   SCOPE_TRANSFER                application outside recorded scope / environment / dates,
#                                 no transfer record
#   SUPERSEDES_NOT_FOUND          supersedes points to an id not in the ledger
#   SUPERSESSION_FORK             two or more records supersede the same record (informational)
#
# Appended kinds (2026-11-05; texts live in each module's FLAGS):
#   labels.py              LABEL_POSITION_UNSTATED, LABEL_ON_ACT_MISSING
#   experiments.py         ENV_ASSUMPTIONS_UNSTATED, NO_ESCALATION_CHANNEL (informational),
#                          CAPABILITY_ASSUMPTION_UNSTATED, ATTRIBUTION_WITHOUT_AUDIT
#   safety_assumptions.py  SOCIAL_TAGS_UNSTATED, SCOPE_UNSTATED, NO_REVIEW_DATE,
#                          ASSUMPTION_DEPENDENCY_NOT_FOUND (+ SUPERSEDES_NOT_FOUND)
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
#   INTERPRETATION_UNRECORDED     layer = agency, no interpretation basis (informational;
#                                 recommended, not required)
#   LOWER_LAYER_SECONDHAND        layer = agency; every physics / sensor basis it rests on
#                                 (own or via depends_on_layers) that states reporter_relation
#                                 says SECONDHAND, none says FIRSTHAND (J10, 2026-11-05)
#   SOURCE_UNTRACEABLE            source_trace records author_known false AND date_known false,
#                                 and no locator (J10, 2026-11-05)
#
# Intervention flags (addendum 2; SignalIntervention records):
#   DIRECTION_UNSTATED            direction missing
#   BAND_UNDEFINED                distance_from_band given, no band_definition
#   DURATION_TYPE_UNSTATED        duration.type missing
#   OPEN_ENDED_WITHOUT_REVIEW     duration.type OPEN_ENDED, no review_date
#   REVERSIBILITY_UNSTATED        reversibility missing
#   LOOP_UNSTATED                 loop_status missing
#   CONSENT_UNSTATED              consent missing
#   CAUSE_STATUS_UNSTATED         direction SUPPRESS, cause_addressed null
#   OUTCOME_UNRECORDED            past planned_end (or actual set), no observed_outcome
#   CROSS_SYSTEM_BAND             band_system_class differs from system_class, no transfer
#   INTERVENTION_NOT_FOUND        judgment intervention_id not in the ledger
# No severity, harm or rightness score is computed for any record.
#
# UNCHAINED_CHANGE keys on the SAME JUDGE: two judges on one scope coexist
# and are not a replacement. A judge's own later record on the same scope
# with no link is the silent-replacement shape. The key also carries the
# layer: one judge's physics record and agency record on the same scope are
# two layers, not a replacement.

import experiments
import labels
import safety_assumptions
from ledger import EXT_MODULES, ID_FIELDS, bodies, judgments
import datetime

from schema import LAYERS, _blank

FLAGS = {
    "MISSING_FIELD": "required field(s) empty: {fields}",
    "NO_SOURCE": "no documented source recorded for this claim",
    "UNCHAINED_CHANGE": "same judge, scope and act type as {earlier}; no supersedes link recorded",
    "CHANGE_BASIS_UNSTATED": "supersedes {prior}; change_basis not stated",
    "NO_NEW_CONDITIONS_OR_EVIDENCE": "supersedes {prior}; environment and evidence entered are identical "
                                     "to it; no material basis listed (completeness note only)",
    "DISSENT_DROPPED": "dissent ({holder}: {position}) present in {prior}, not carried here, "
                       "no confirmed withdrawal by its holder recorded",
    "DISSENT_WITHDRAWAL_UNCONFIRMED": "withdrawal of dissent ({holder}: {position}) from {prior} has no "
                                      "confirmation on record: {why}",
    "INCENTIVES_UNRECORDED": "judge_incentives not recorded",
    "NO_FRAMING_CHECK": "framing_check not recorded (informational)",
    "SCOPE_TRANSFER": "application {app} differs from the recorded {what}; no transfer record",
    "SUPERSEDES_NOT_FOUND": "supersedes {prior}, which is not in this ledger",
    "SUPERSESSION_FORK": "superseded by more than one record: {ids} (informational)",
    "LAYER_UNSTATED": "layer not stated (physics | sensor | agency)",
    "SKIPPED_LAYER": "layer is agency; no physics or sensor basis recorded here or via depends_on_layers",
    "SUBJECT_STATUS_UNSTATED": "layer is agency; subject_status not stated",
    "SUBJECT_OPEN": "subject_status is OPEN; the claim rests on an open question (informational)",
    "CONSENT_UNSTATED": "{where}; consent not stated",
    "LOOP_UNSTATED": "{where}; loop not stated",
    "CROSS_SYSTEM_TRANSFER": "{basis} recorded for system class '{src}', used here for '{dst}'; "
                             "no transfer record",
    "LAYER_DEPENDENCY_NOT_FOUND": "depends_on_layers lists {dep}, which is not in this ledger",
    "INTERPRETATION_UNRECORDED": "layer is agency; no interpretation basis recorded here or via "
                                 "depends_on_layers (informational)",
    "LOWER_LAYER_SECONDHAND": "layer is agency; the physics / sensor basis it rests on is recorded "
                              "as secondhand only ({bases})",
    "SOURCE_UNTRACEABLE": "source recorded with author and date unknown and no locator",
    "DIRECTION_UNSTATED": "direction not stated (AMPLIFY | SUPPRESS | RECALIBRATE | NONE)",
    "BAND_UNDEFINED": "distance_from_band given with no band_definition",
    "DURATION_TYPE_UNSTATED": "duration.type not stated (BRIDGE | BOUNDED | OPEN_ENDED)",
    "OPEN_ENDED_WITHOUT_REVIEW": "duration is OPEN_ENDED; no review_date recorded",
    "REVERSIBILITY_UNSTATED": "reversibility not stated",
    "CAUSE_STATUS_UNSTATED": "direction is SUPPRESS; cause_addressed not stated",
    "OUTCOME_UNRECORDED": "past planned duration ({when}); no observed_outcome entries recorded",
    "CROSS_SYSTEM_BAND": "band_definition recorded for system class '{src}', used here for '{dst}'; "
                         "no transfer record",
    "INTERVENTION_NOT_FOUND": "intervention_id {iid} is not in this ledger",
}

for _m in EXT_MODULES:                       # acts / labels / experiments / safety assumptions
    FLAGS.update(_m.FLAGS)

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
        rel = [("own " + n, (_block(j, n) or {}).get("reporter_relation")) for n in ("physics", "sensor")
               if _block(j, n)]
        rel += [("%s basis of %s" % (d.layer, d.judgment_id), (_block(d, d.layer) or {}).get("reporter_relation"))
                for d in deps if d.layer in ("physics", "sensor") and _block(d, d.layer)]
        stated = [(w, r) for w, r in rel if r in ("FIRSTHAND", "SECONDHAND")]
        if stated and all(r == "SECONDHAND" for _, r in stated):
            out.append(flag("LOWER_LAYER_SECONDHAND", a, bases=", ".join(w for w, _ in stated)))
        if not (_block(j, "interpretation") or any(d.layer == "interpretation" for d in deps)):
            out.append(flag("INTERPRETATION_UNRECORDED", a))
        ag = _block(j, "agency") or {}
        for key, code in AGENCY_FIELDS:
            if _blank(ag.get(key)):
                out.append(flag(code, a, where="layer is agency"))
        if ag.get("subject_status") == "OPEN":
            out.append(flag("SUBJECT_OPEN", a))
    dst = _cls(j, j.layer)
    if dst and a not in jt_transfers:
        sources = [("own %s basis" % n, _cls(j, n)) for n in LAYERS if n != j.layer]
        sources += [("%s basis of %s" % (d.layer, d.judgment_id), _cls(d, d.layer)) for d in deps]
        for basis, src in sources:
            if src and src != dst:
                out.append(flag("CROSS_SYSTEM_TRANSFER", a, basis=basis, src=src, dst=dst))
    return out


def _evidence_set(j):
    return sorted((_norm(e.get("item")), e.get("tag"), _norm(e.get("source"))) for e in j.evidence or [])


def _dkey(d):
    return (_norm(d.get("holder")), _norm(d.get("position")))


def _confirmation_gap(w, paths_before):
    """M25. '' when the withdrawal's confirmation is on record, else what is missing."""
    c = w.get("confirmation") or {}
    holder = _norm(w.get("holder"))
    m = c.get("method")
    if not m:
        return "no confirmation recorded"
    if m == "holder_contact_path":
        if holder in ("", "anonymous"):
            return "holder is anonymous; steward_two_person confirmation needed"
        pid = str(c.get("path_id") or "").strip()
        if not pid:
            return "holder_contact_path without path_id"
        if (pid, holder) not in paths_before:
            return "contact path %s not recorded for this holder before the withdrawal" % pid
        return ""
    if m == "steward_two_person":
        if holder not in ("", "anonymous"):
            return "holder is named; holder_contact_path confirmation needed"
        st, nd = _norm(c.get("steward") or ""), _norm(c.get("second") or "")
        if not st or not nd:
            return "steward_two_person needs steward and second"
        if st == nd:
            return "steward and second are the same name"
        return ""
    return "confirmation method %s not in the recognized set" % m


def _withdrawals(records):
    """-> (set of confirmed withdrawal keys, list of DISSENT_WITHDRAWAL_UNCONFIRMED flags).
    Contact paths count only when written earlier in the chain than the withdrawal."""
    paths, confirmed, flags = set(), set(), []
    for r in records:
        b = r.get("body") or {}
        if r.get("kind") == "contact_path":
            paths.add((str(b.get("path_id") or "").strip(), _norm(b.get("holder"))))
        elif r.get("kind") == "withdrawal" and b.get("withdrawn_by_holder"):
            why = _confirmation_gap(b, paths)
            if why:
                flags.append(flag("DISSENT_WITHDRAWAL_UNCONFIRMED", "withdrawal:%s" % b.get("judgment_id"),
                                  holder=b.get("holder"), position=b.get("position"),
                                  prior=b.get("judgment_id"), why=why))
            else:
                confirmed.add((b.get("judgment_id"), _norm(b.get("holder")), _norm(b.get("position"))))
    return confirmed, flags


def _intervention_flags(iv, iv_transfers, as_of):
    a, out = iv.get("intervention_id"), []
    if _blank(iv.get("direction")):
        out.append(flag("DIRECTION_UNSTATED", a))
    band = iv.get("distance_from_band") or {}
    if any(not _blank(v) for v in band.values()) and _blank(band.get("band_definition")):
        out.append(flag("BAND_UNDEFINED", a))
    dur = iv.get("duration") or {}
    if _blank(dur.get("type")):
        out.append(flag("DURATION_TYPE_UNSTATED", a))
    elif dur.get("type") == "OPEN_ENDED" and _blank(dur.get("review_date")):
        out.append(flag("OPEN_ENDED_WITHOUT_REVIEW", a))
    if _blank(iv.get("reversibility")):
        out.append(flag("REVERSIBILITY_UNSTATED", a))
    if _blank(iv.get("loop_status")):
        out.append(flag("LOOP_UNSTATED", a, where="intervention record"))
    if _blank(iv.get("consent")):
        out.append(flag("CONSENT_UNSTATED", a, where="intervention record"))
    if iv.get("direction") == "SUPPRESS" and iv.get("cause_addressed") is None:
        out.append(flag("CAUSE_STATUS_UNSTATED", a))
    if not iv.get("observed_outcome"):
        if not _blank(dur.get("actual")):
            out.append(flag("OUTCOME_UNRECORDED", a, when="actual duration recorded"))
        elif not _blank(dur.get("planned_end")) and dur["planned_end"] < as_of:
            out.append(flag("OUTCOME_UNRECORDED", a, when="planned_end %s" % dur["planned_end"]))
    src, dst = _norm(band.get("band_system_class")), _norm(iv.get("system_class"))
    if src and dst and src != dst and a not in iv_transfers:
        out.append(flag("CROSS_SYSTEM_BAND", a, src=src, dst=dst))
    return out


def check(records, as_of=None):
    """as_of: ISO date for OUTCOME_UNRECORDED; defaults to today."""
    as_of = as_of or datetime.date.today().isoformat()
    js = judgments(records)
    by_id = dict((j.judgment_id, j) for j in js)
    withdrawn, unconfirmed = _withdrawals(records)
    ivs = bodies(records, "intervention")
    iv_ids = set(iv["intervention_id"] for iv in ivs)
    iv_transfers = set(t.get("intervention_id") for t in bodies(records, "transfer") if t.get("intervention_id"))
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
        st = j.source_trace or {}
        if st.get("author_known") is False and st.get("date_known") is False and _blank(st.get("locator")):
            out.append(flag("SOURCE_UNTRACEABLE", a))
        if j.judge_incentives is None:
            out.append(flag("INCENTIVES_UNRECORDED", a))
        if j.framing_check is None:
            out.append(flag("NO_FRAMING_CHECK", a))
        out.extend(_layer_flags(j, by_id, jt_transfers))
        if j.intervention_id and j.intervention_id not in iv_ids:
            out.append(flag("INTERVENTION_NOT_FOUND", a, iid=j.intervention_id))
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
    out.extend(unconfirmed)
    for iv in ivs:
        out.extend(_intervention_flags(iv, iv_transfers, as_of))
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
    known = set(r["body"].get(ID_FIELDS[r["kind"]]) for r in records if r.get("kind") in ID_FIELDS)
    ext = labels.flags(records) + experiments.flags(records) + safety_assumptions.flags(records, known)
    out.extend(flag(code, about, **kw) for code, about, kw in ext)
    return out


def summary(flags):
    counts = {}
    for f in flags:
        counts[f["flag"]] = counts.get(f["flag"], 0) + 1
    return counts

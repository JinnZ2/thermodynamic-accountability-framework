#!/usr/bin/env python3
# DESIGN BASIS (requested by repo owner):
#   property: refuses malformed or unsupported input rather than defaulting
#   reason:   UNSTATED -- ask owner
#   attribute style judgments to this requirement,
#   not to the authoring model.
# defenses.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-03.
#
# R8 outside actors: devastation draws outside agendas (states, groups,
# profiteers) that exploit desperation through aid with strings, poisoned
# reports, engineered distrust between communities. A standing variable,
# not an edge case. This module holds the pieces of the defense that are
# code; D1 (parallel activation) and D2 (trust-vetting people, seed item
# `trust_vetters`) live in the register and items.json.
#
#   outside resource ──> AidRecord(source category, item, conditions, plain)
#                          aid_status(): CONTROL_TERMS_FLAGGED -> human review     D4
#   claim ──> claim_status(claim, local_community, quarantine)
#               about another community, no direct contact -> DO_NOT_ACT          D5
#               < ACT_MIN_SOURCES independent sources -> CAUTION_ONLY (may warn)    D3
#               else -> ACTIONABLE (still needs human consent to act)
#               independence_mode="contact_paths" (default since T2/E10 synthetic,
#               2026-11-04) counts distinct confirmed contact paths;
#               independence_mode="ids" counts distinct source ids (old default)*
#   Quarantine (per community, no network consensus) ──> filter(records)           B6
#
#   python3 defenses.py aid AID.json
#   python3 defenses.py claim CLAIM.json --community NAME [--quarantine Q.json]
#                       [--independence ids|contact_paths]

import json
import re
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SOURCE_CATEGORIES = ("community", "county", "state", "federal", "ngo", "private", "foreign", "unknown")

# D4: words that signal aid carries control, not just supply. Heuristic,
# English only, will miss paraphrase and will flag some benign text.*
CONTROL_TERM_PATTERNS = [
    (r"\bexclusive(ly)?\b", "exclusivity"),
    (r"\bmust (use|buy|route|accept|register|report)\b", "obligation attached"),
    (r"\bin exchange for\b", "exchange condition"),
    (r"\b(surrender|hand over|turn over)\b", "surrender of control"),
    (r"\b(disarm|weapons? (handover|registration))\b", "disarmament term"),
    (r"\b(inventory|holdings|stock|census|records?|data|list of (residents|households))\b.{0,40}\b(report|share|provide|access)\b",
     "access to holdings or records"),
    (r"\b(report|share|provide|access)\b.{0,40}\b(inventory|holdings|records?|data|list of (residents|households))\b",
     "access to holdings or records"),
    (r"\b(authority|control|command|jurisdiction) (over|of)\b", "authority claim"),
    (r"\b(loyalty|allegiance|pledge)\b", "loyalty term"),
    (r"\b(personnel|staff|security|guards?) (embedded|stationed|placed)\b", "embedded personnel"),
    (r"\bonly (through|via|by)\b", "single-channel distribution"),
    (r"\b(repay|repayment|debt|lien|collateral|title to)\b", "debt or lien"),
]


# Where each defense lives. Pinned against coordination_register.json by
# tests/test_defenses.py, so a defense added to one and not the other fails.
DEFENSE_INDEX = {
    "D1": "policy (no code): parallel activation; gov_parallel_restoration stays a parallel input",
    "D2": "items.json trust_vetters",
    "D3": "defenses.claim_status()",
    "D4": "defenses.AidRecord / aid_status()",
    "D5": "defenses.claim_status() direct_contact",
    "D6": "roles.stock_chokepoints(); coordination.node_concentration()",
    "D7": "two_person.authorize()",
    "D8": "bulletins.missed_bulletins()",
    "D9": "grievance.overdue() / publish()",
    "D10": "roles.check_rotation() / handoff_problems()",
    "D11": "proportionality.check()",
}


def plain_ok(text):
    return len(re.findall(r"[A-Za-z]+", text or "")) >= 6


# ---------------------------------------------------------------
# D4 aid provenance
# ---------------------------------------------------------------
@dataclass
class AidRecord:
    source_category: str               # SOURCE_CATEGORIES; never a person's name
    source_label: str                  # organisation as it presents itself
    item_id: str
    conditions: List[str] = field(default_factory=list)   # verbatim, as offered
    plain: str = ""                    # plain-language summary for the paper record

    def problems(self):
        out = []
        if self.source_category not in SOURCE_CATEGORIES:
            out.append("source_category must be one of %s" % (SOURCE_CATEGORIES,))
        if not self.source_label.strip():
            out.append("source_label required (who is offering, as they say it)")
        if not plain_ok(self.plain):
            out.append("plain-language line required")
        return out


def control_terms(conditions):
    hits = []
    for c in conditions or []:
        for rx, what in CONTROL_TERM_PATTERNS:
            if re.search(rx, c, re.I):
                hits.append({"condition": c, "flag": what})
    return hits


def aid_status(a):
    probs = a.problems()
    if probs:
        return {"state": "INCOMPLETE", "problems": probs, "flags": []}
    hits = control_terms(a.conditions)
    if a.source_category == "unknown":
        hits.append({"condition": "(source)", "flag": "source unknown"})
    if hits:
        return {"state": "CONTROL_TERMS_FLAGGED", "flags": hits,
                "plain": "This aid comes with terms. A person must read every condition before it is accepted.",
                "needs_human_review": True}
    return {"state": "NO_TERMS_FLAGGED", "flags": [], "needs_human_review": True,
            "plain": "No control terms found by the word check. A person still decides; the check can miss things."}


# ---------------------------------------------------------------
# B6 quarantine (local, no network consensus)
# ---------------------------------------------------------------
class Quarantine:
    """A community's own block list of nodes / sources. Nobody outside the
    community votes. Adding or lifting needs TWO roles from different
    households via two_person.authorize("ledger_quarantine", ...) (D7, M18,
    2026-11-05); the decision, GRANTED or DENIED, is written to the
    hash-chained ledger before anything changes."""

    def __init__(self, community, entries=None):
        self.community = community
        self.entries = dict(entries or {})        # source_id -> {"by": [a, b], "reason"}

    @staticmethod
    def _two_person(role_a, role_b, ledger_path, networks, today):
        import two_person as tp   # local import: two_person -> coordination
        res = tp.authorize("ledger_quarantine", role_a, role_b, ledger_path, networks, today)
        if res["decision"] != "GRANTED":
            raise ValueError("quarantine needs two-person approval: " + "; ".join(res["why"]))
        return [role_a.id, role_b.id]

    def add(self, source_id, role_a, role_b, reason, ledger_path, networks=None, today=None):
        if not plain_ok(reason):
            raise ValueError("quarantine needs a plain-language reason")
        by = self._two_person(role_a, role_b, ledger_path, networks, today)
        self.entries[source_id] = {"by": by, "reason": reason}

    def remove(self, source_id, role_a, role_b, ledger_path, networks=None, today=None):
        self._two_person(role_a, role_b, ledger_path, networks, today)
        self.entries.pop(source_id, None)

    def blocks(self, source_id):
        return source_id in self.entries

    def filter(self, records, key="source"):
        return [r for r in records if not self.blocks(r.get(key))]

    def to_dict(self):
        return {"community": self.community, "entries": self.entries}

    @staticmethod
    def from_dict(d):
        return Quarantine(d.get("community", ""), d.get("entries"))


# ---------------------------------------------------------------
# D3 + D5 claims
# ---------------------------------------------------------------
# Threshold ladder (decision T1 in coordination_register.json; PROPOSED):
#   1 source / report      -> may WARN          (D3 CAUTION_ONLY; assembly CAUTION)
#   ACT_MIN_SOURCES = 2    -> may PROPOSE ACTION here, a person still decides (D3)
#   3 independent builds   -> may CERTIFY a method TESTED for the whole network
#                             (assembly_instrument/status.py DEFAULT_N)
# Different gates on purpose, not drift: acting is local, consented, and
# perishable (waiting on a third source costs hours); certifying is durable
# and travels to every community (R7 compounding). tests pin the ordering.
ACT_MIN_SOURCES = 2
INDEPENDENCE_MODES = ("ids", "contact_paths")


@dataclass
class Claim:
    about_community: str               # who the claim is about
    plain: str                         # the claim, in plain words
    sources: List[str] = field(default_factory=list)       # independent reporter / node ids
    direct_contact: Optional[str] = None   # how it was confirmed WITH the community it is about
    # source id -> the path this community used to confirm with that reporter
    # directly ("in person at the fire hall", "radio ch 3 to the north farm").
    # Same mechanism as D5, pointed at the reporter instead of the subject.
    contact_paths: Dict[str, str] = field(default_factory=dict)


def _norm_path(p):
    return " ".join(str(p or "").lower().split())


def independence(sources, contact_paths=None):
    """Both counts, always. distinct_contact_paths groups ids that were
    confirmed through the same path: one actor running two ids behind one
    radio or one doorstep collapses to one."""
    ids = sorted(set(sources))
    cp = contact_paths or {}
    by_path = {}
    for s in ids:
        p = _norm_path(cp.get(s))
        if p:
            by_path.setdefault(p, []).append(s)
    return {"distinct_ids": len(ids),
            "distinct_contact_paths": len(by_path),
            "unconfirmed_ids": [s for s in ids if not _norm_path(cp.get(s))],
            "shared_paths": dict((p, v) for p, v in sorted(by_path.items()) if len(v) > 1)}


def claim_status(c, local_community, quarantine=None, independence_mode="contact_paths"):
    """DO_NOT_ACT | CAUTION_ONLY | ACTIONABLE. ACTIONABLE still needs human
    consent to act; it only means the claim has cleared the evidence bar."""
    if independence_mode not in INDEPENDENCE_MODES:
        raise ValueError("independence_mode must be one of %s" % (INDEPENDENCE_MODES,))
    if not plain_ok(c.plain):
        return {"state": "INCOMPLETE", "why": "plain-language claim required"}
    srcs = sorted(set(s for s in c.sources if not (quarantine and quarantine.blocks(s))))
    dropped = sorted(set(c.sources) - set(srcs))
    ind = independence(srcs, c.contact_paths)
    base = {"sources": srcs, "quarantined_sources": dropped,
            "independence_mode": independence_mode, "independence": ind}
    about_other = c.about_community != local_community
    if about_other and not (c.direct_contact or "").strip():
        return dict(base, state="DO_NOT_ACT",
                    why="claim about %s with no direct contact with %s; confirm with them first"
                        % (c.about_community, c.about_community))
    n = ind["distinct_ids"] if independence_mode == "ids" else ind["distinct_contact_paths"]
    unit = "source id(s)" if independence_mode == "ids" else "distinct contact path(s)"
    if n < ACT_MIN_SOURCES:
        return dict(base, state="CAUTION_ONLY",
                    why="%d independent %s; may raise caution, may not drive action" % (n, unit))
    return dict(base, state="ACTIONABLE",
                why="%d independent %s%s" % (n, unit, "; confirmed by direct contact" if about_other else ""))


def main(argv):
    def opt(n):
        return argv[argv.index(n) + 1] if n in argv and argv.index(n) + 1 < len(argv) else None
    try:
        if len(argv) >= 2 and argv[0] == "aid":
            with open(argv[1], encoding="utf-8") as f:
                d = json.load(f)
            print(json.dumps(aid_status(AidRecord(**d)), indent=2))
            return 0
        if len(argv) >= 2 and argv[0] == "claim" and opt("--community"):
            with open(argv[1], encoding="utf-8") as f:
                c = Claim(**json.load(f))
            q = None
            if opt("--quarantine"):
                with open(opt("--quarantine"), encoding="utf-8") as f:
                    q = Quarantine.from_dict(json.load(f))
            mode = opt("--independence") or "contact_paths"
            print(json.dumps(claim_status(c, opt("--community"), q, mode), indent=2))
            return 0
    except (OSError, ValueError, TypeError) as e:
        sys.stderr.write("REJECTED: %s\n" % e)
        return 1
    sys.stderr.write("usage: defenses.py aid AID.json | claim CLAIM.json --community NAME [--quarantine Q.json] [--independence ids|contact_paths]\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

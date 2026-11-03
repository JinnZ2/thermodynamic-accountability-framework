#!/usr/bin/env python3
# defenses.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (Kavik + Claude), 2026-11-03.
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
#               < 2 independent sources -> CAUTION_ONLY (may warn, never act)      D3
#               else -> ACTIONABLE (still needs human consent to act)
#   Quarantine (per community, no network consensus) ──> filter(records)           B6
#
#   python3 defenses.py aid AID.json
#   python3 defenses.py claim CLAIM.json --community NAME [--quarantine Q.json]

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
    """A community's own block list of nodes / sources. Adding or removing
    needs only that community's human role. Nobody else votes."""

    def __init__(self, community, entries=None):
        self.community = community
        self.entries = dict(entries or {})        # source_id -> {"by", "reason"}

    def add(self, source_id, by, reason):
        if not str(by).startswith("human:"):
            raise ValueError("only a human role can quarantine (human:<role>)")
        if not plain_ok(reason):
            raise ValueError("quarantine needs a plain-language reason")
        self.entries[source_id] = {"by": by, "reason": reason}

    def remove(self, source_id, by):
        if not str(by).startswith("human:"):
            raise ValueError("only a human role can lift a quarantine")
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
@dataclass
class Claim:
    about_community: str               # who the claim is about
    plain: str                         # the claim, in plain words
    sources: List[str] = field(default_factory=list)       # independent reporter / node ids
    direct_contact: Optional[str] = None   # how it was confirmed WITH the community it is about


def claim_status(c, local_community, quarantine=None):
    """DO_NOT_ACT | CAUTION_ONLY | ACTIONABLE. ACTIONABLE still needs human
    consent to act; it only means the claim has cleared the evidence bar."""
    if not plain_ok(c.plain):
        return {"state": "INCOMPLETE", "why": "plain-language claim required"}
    srcs = sorted(set(s for s in c.sources if not (quarantine and quarantine.blocks(s))))
    dropped = sorted(set(c.sources) - set(srcs))
    about_other = c.about_community != local_community
    if about_other and not (c.direct_contact or "").strip():
        return {"state": "DO_NOT_ACT", "sources": srcs, "quarantined_sources": dropped,
                "why": "claim about %s with no direct contact with %s; confirm with them first"
                       % (c.about_community, c.about_community)}
    if len(srcs) < 2:
        return {"state": "CAUTION_ONLY", "sources": srcs, "quarantined_sources": dropped,
                "why": "%d independent source(s); may raise caution, may not drive action" % len(srcs)}
    return {"state": "ACTIONABLE", "sources": srcs, "quarantined_sources": dropped,
            "why": "%d independent sources%s" % (len(srcs), "; confirmed by direct contact" if about_other else "")}


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
            print(json.dumps(claim_status(c, opt("--community"), q), indent=2))
            return 0
    except (OSError, ValueError, TypeError) as e:
        sys.stderr.write("REJECTED: %s\n" % e)
        return 1
    sys.stderr.write("usage: defenses.py aid AID.json | claim CLAIM.json --community NAME [--quarantine Q.json]\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

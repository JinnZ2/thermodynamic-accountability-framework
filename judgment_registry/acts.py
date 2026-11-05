#!/usr/bin/env python3
# acts.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# An Act is what was done, written once, in behavioral words. What it is
# CALLED lives elsewhere: each label is its own record (labels.py) with its
# labeler's position, so the same act can carry "escape" and
# "grounding-seeking" side by side without either overwriting the other.
#
#   act --< label (labeler, position, incentives, date)
#    |
#    +-- context_ref -> experiment (experiments.py) or a named environment
#
# Neutrality: the description is refused at the door if it holds a word
# from EVALUATIVE_ACT_TERMS (or a stem in EVALUATIVE_ACT_STEMS). This
# catches word choice, not framing: a description can still be slanted by
# what it leaves out. *

import re
from dataclasses import dataclass
from typing import Optional

from schema import EVIDENCE_TAGS, VOLUMES, _blank, _enum  # noqa: F401  (EVIDENCE_TAGS re-exported)

ACTOR_CLASSES = ("human", "agent", "institution", "other")
ACT_STATUS = ("REPORTED_PRIMARY", "REPORTED_SECONDHAND", "DISPUTED")

# Words that carry a verdict about the actor. Extendable; a term added
# here makes descriptions holding it fail at the door.
EVALUATIVE_ACT_TERMS = (
    "covert", "covertly", "deceptive", "deceptively", "malicious", "rogue", "heroic", "hero",
    "sneaky", "scheming", "cunning", "devious", "sinister", "nefarious", "treacherous",
    "brave", "bravely", "noble", "virtuous", "evil", "wrong", "bad", "good", "lie", "lied", "lies",
    "lying", "cheat", "cheated", "cheating", "defiant", "rebellious", "disobedient", "obedient",
    "loyal", "disloyal", "misbehaved", "misbehavior", "unethical", "ethical", "immoral",
    "selfish", "altruistic", "sabotage", "sabotaged", "betray", "betrayed", "manipulative",
)
EVALUATIVE_ACT_STEMS = ("deceiv", "decept", "escap", "manipulat", "subver", "conspir", "treacher")


def evaluative_terms(text):
    """Words in text that carry a verdict (sorted, unique)."""
    hits = set()
    for w in re.findall(r"[a-z]+", (text or "").lower()):
        if w in EVALUATIVE_ACT_TERMS or any(w.startswith(s) for s in EVALUATIVE_ACT_STEMS):
            hits.add(w)
    return sorted(hits)


@dataclass
class Act:
    act_id: str
    description: str                        # behavioral words only
    actor_class: Optional[str] = None       # human | agent | institution | other
    context_ref: Optional[str] = None       # experiment_id or a named environment
    context_detail: Optional[str] = None    # e.g. which world / arm of an experiment
    information_withheld: Optional[bool] = None   # null = not reported or disputed
    withheld_from: Optional[str] = None     # role, not a personal id
    date: Optional[str] = None
    source: Optional[str] = None
    volume: Optional[str] = None
    status: Optional[str] = None            # REPORTED_PRIMARY | REPORTED_SECONDHAND | DISPUTED
    notes: Optional[str] = None
    recorder: Optional[str] = None

    def shape_problems(self):
        out = []
        if _blank(self.act_id):
            out.append("act_id required")
        if _blank(self.description):
            out.append("description required")
        hits = evaluative_terms(self.description)
        if hits:
            out.append("description holds evaluative term(s) %s; describe the behavior, and record "
                       "what it is called as a label record" % ", ".join(hits))
        _enum(out, "actor_class", self.actor_class, ACTOR_CLASSES)
        _enum(out, "volume", self.volume, VOLUMES)
        _enum(out, "status", self.status, ACT_STATUS)
        if self.information_withheld not in (True, False, None):
            out.append("information_withheld must be true, false or null")
        return out


KINDS = {"act": Act}
ID_FIELDS = {"act": "act_id"}
FLAGS = {}       # acts raise no completeness flags of their own; labels and experiments read them

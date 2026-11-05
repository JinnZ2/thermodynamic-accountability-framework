#!/usr/bin/env python3
# proportionality.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (Kavik + Claude), 2026-11-04.
#
# D11 proportionality. Every enforcement action records the threat it
# answers and its scope; an action broader than the logged threat is
# flagged (guards against elite panic and collective punishment).
#
# Built from the D11 line alone: the append's code item 5 arrived as
# "5. proportionality." with nothing after it. PROPOSED, thin.**
#
#   Threat(id, plain, scope)               scope = units the threat touches
#   EnforcementAction(id, plain, threat_id, scope, affected_count)
#     affected_count: how many people the action reaches (null = not counted).
#     Echoed in every result so a reviewer sees size, not just category.
#   check(action, threats)
#     no threat_id / unknown threat ....... NO_THREAT_LOGGED
#     action scope not inside threat scope  BROADER_THAN_THREAT  (lists the extra units)
#     else ................................ IN_PROPORTION        (a person still decides)
#
# Scope is a list of unit codes (household, site, road, node). "ALL" means
# every unit; an action on ALL answering a threat that is not ALL is
# always broader. The check sees only what was logged: a threat logged
# wider than it really is passes a wide action.* That is why the threat
# record is public too (D8/D9).
#
#   python3 proportionality.py THREATS.json ACTIONS.json

import json
import re
import sys
from dataclasses import dataclass, field
from typing import List, Optional

ALL = "ALL"


def plain_ok(text):
    return len(re.findall(r"[A-Za-z]+", text or "")) >= 6


@dataclass
class Threat:
    id: str
    plain: str
    scope: List[str] = field(default_factory=list)


@dataclass
class EnforcementAction:
    id: str
    plain: str
    threat_id: Optional[str] = None
    scope: List[str] = field(default_factory=list)
    affected_count: Optional[int] = None


def check(action, threats):
    res = _check(action, threats)
    res["affected_count"] = action.affected_count
    if action.affected_count is None:
        res["size_note"] = "affected_count not recorded; a reviewer cannot see how many people this reaches"
    return res


def _check(action, threats):
    by_id = dict((t.id, t) for t in threats)
    if not plain_ok(action.plain):
        return {"id": action.id, "state": "INCOMPLETE", "why": "plain-language line required"}
    if not action.scope:
        return {"id": action.id, "state": "INCOMPLETE", "why": "action scope required"}
    t = by_id.get(action.threat_id or "")
    if t is None:
        return {"id": action.id, "state": "NO_THREAT_LOGGED",
                "why": "no logged threat answers this action; log the threat and its scope first"}
    ts, as_ = set(t.scope), set(action.scope)
    if ALL in ts:
        extra = []
    elif ALL in as_:
        extra = [ALL]
    else:
        extra = sorted(as_ - ts)
    if extra:
        return {"id": action.id, "threat": t.id, "state": "BROADER_THAN_THREAT", "extra_scope": extra,
                "why": "action reaches %s, which threat %s does not touch" % (", ".join(extra), t.id)}
    return {"id": action.id, "threat": t.id, "state": "IN_PROPORTION",
            "why": "action scope is inside the logged threat scope; a person still decides"}


def main(argv):
    if len(argv) < 2:
        sys.stderr.write("usage: proportionality.py THREATS.json ACTIONS.json\n")
        return 2
    try:
        with open(argv[0], encoding="utf-8") as f:
            threats = [Threat(**t) for t in json.load(f)]
        with open(argv[1], encoding="utf-8") as f:
            actions = [EnforcementAction(**a) for a in json.load(f)]
    except (OSError, ValueError, TypeError) as e:
        sys.stderr.write("REJECTED: %s\n" % e)
        return 1
    print(json.dumps([check(a, threats) for a in actions], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

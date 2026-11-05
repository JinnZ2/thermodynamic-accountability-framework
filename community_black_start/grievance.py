#!/usr/bin/env python3
# grievance.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-04.
#
# D9 grievance channel. Every grievance gets a response deadline; past the
# deadline unanswered it escalates visibly. Outcomes are published with no
# personal identifiers.
#
#   Grievance(id, category, logged, deadline, status, outcome_public)
#     id is a ticket code, never a name.
#   problems()      missing deadline, bad status, identifier-like text in outcome
#   overdue(gs, today)   status open past deadline -> ESCALATE, with a plain line
#   publish(gs)     category + status + outcome only; ids dropped
#
# The identifier check is a pattern list (email, phone, house number +
# street).* It will miss a name written in plain words; a person reads every
# outcome before it is posted.
#
#   python3 grievance.py LOG.json [--today YYYY-MM-DD]

import datetime as _dt
import json
import re
import sys
from dataclasses import dataclass
from typing import Optional

from roles import parse_date

STATUSES = ("open", "answered", "closed")
IDENTIFIER_PATTERNS = [
    (r"[\w.+-]+@[\w-]+\.[\w.]+", "email address"),
    (r"(\+?\d[\d\s().-]{7,}\d)", "phone number"),
    (r"\b\d{1,5}\s+\w+\s+(road|rd|street|st|lane|ln|avenue|ave|drive|dr)\b", "street address"),
]


@dataclass
class Grievance:
    id: str
    category: str
    logged: str                       # YYYY-MM-DD
    deadline: Optional[str] = None    # YYYY-MM-DD
    status: str = "open"
    outcome_public: Optional[str] = None

    def problems(self):
        out = []
        if parse_date(self.logged) is None:
            out.append("logged date required")
        if parse_date(self.deadline) is None:
            out.append("response deadline required (D9)")
        if self.status not in STATUSES:
            out.append("status must be one of %s" % (STATUSES,))
        for rx, what in IDENTIFIER_PATTERNS:
            if re.search(rx, self.outcome_public or "", re.I):
                out.append("outcome_public contains a %s; remove it before publishing" % what)
        return out


def overdue(grievances, today=None):
    today = today or _dt.date.today()
    out = []
    for g in grievances:
        dl = parse_date(g.deadline)
        if g.status != "open":
            continue
        if dl is None:
            out.append({"id": g.id, "category": g.category, "state": "ESCALATE",
                        "plain": "Grievance %s has no deadline. Set one in public." % g.id})
        elif today > dl:
            out.append({"id": g.id, "category": g.category, "state": "ESCALATE",
                        "days_over": (today - dl).days,
                        "plain": "Grievance %s (%s) is %d day(s) past its deadline with no answer."
                                 % (g.id, g.category, (today - dl).days)})
    return out


def publish(grievances):
    out = []
    for g in grievances:
        if g.problems():
            continue
        out.append({"category": g.category, "status": g.status, "outcome": g.outcome_public})
    return out


def main(argv):
    def opt(n):
        return argv[argv.index(n) + 1] if n in argv and argv.index(n) + 1 < len(argv) else None
    if not argv:
        sys.stderr.write("usage: grievance.py LOG.json [--today YYYY-MM-DD]\n")
        return 2
    try:
        with open(argv[0], encoding="utf-8") as f:
            gs = [Grievance(**g) for g in json.load(f)]
        today = parse_date(opt("--today")) or _dt.date.today()
        print(json.dumps({"overdue": overdue(gs, today), "public": publish(gs),
                          "held_back": [{"id": g.id, "problems": g.problems()} for g in gs if g.problems()]},
                         indent=2))
    except (OSError, ValueError, TypeError) as e:
        sys.stderr.write("REJECTED: %s\n" % e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

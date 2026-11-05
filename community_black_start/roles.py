#!/usr/bin/env python3
# roles.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (Kavik + Claude), 2026-11-04.
#
# R9 insider threat: a trusted role is bought, coerced, exhausted, or acts
# on its own agenda, or slowly gathers control. This module measures the
# shape that makes that possible; it does not judge any person.
#
#   Role records ──> check_rotation()          D10 overdue / unknown / no schedule
#               ──> concentration_report()     D6/R9 one household or person holding
#                                              >1 critical role; critical role with 1 holder
#   stock sites  ──> stock_chokepoints()       D6 <2 sites, <2 keyholders, one role on every site
#
# A Role record is ONE HOLDER of a role: id = holder id (a code, never a
# name), name = the role ("fuel keeper"), so a role with two holders is two
# records with the same name. Interpretation of the append, stated here.*
#
# Null-safe: last_rotated None -> ROTATION_UNKNOWN (never assumed current);
# rotation_days None on a critical role -> NO_SCHEDULE.
#
#   python3 roles.py ROLES.json [--today YYYY-MM-DD] [--stocks STOCKS.json]

import datetime as _dt
import json
import sys
from dataclasses import dataclass
from typing import Optional

MIN_SITES = 2          # D6, from the append
MIN_KEYHOLDERS = 2     # D6, from the append


def parse_date(s):
    if not s:
        return None
    try:
        return _dt.date.fromisoformat(str(s)[:10])
    except ValueError:
        return None


@dataclass
class Role:
    id: str                          # holder code, never a personal name
    name: str                        # the role
    household_id: str
    critical: bool = False
    rotation_days: Optional[float] = None
    last_rotated: Optional[str] = None   # YYYY-MM-DD

    def rotation_state(self, today):
        if self.rotation_days is None:
            return "NO_SCHEDULE" if self.critical else "NOT_ROTATED"
        last = parse_date(self.last_rotated)
        if last is None:
            return "ROTATION_UNKNOWN"
        due = last + _dt.timedelta(days=float(self.rotation_days))
        return "OVERDUE" if today > due else "CURRENT"


def load_roles(path):
    with open(path, encoding="utf-8") as f:
        return [Role(**r) for r in json.load(f)]


def check_rotation(roles, today=None):
    """D10: roles not proven current. CURRENT and NOT_ROTATED (non-critical, no schedule) are omitted."""
    today = today or _dt.date.today()
    out = []
    for r in roles:
        st = r.rotation_state(today)
        if st in ("OVERDUE", "ROTATION_UNKNOWN", "NO_SCHEDULE"):
            out.append({"id": r.id, "role": r.name, "state": st})
    return out


HANDOFF_FIELDS = ("doing", "did", "observed", "deferred")


def handoff_problems(h):
    """D10: a rotation hands over doing / did / observed / deferred. Each must be
    written, even if the answer is 'none'."""
    return [k for k in HANDOFF_FIELDS if not str((h or {}).get(k) or "").strip()]


def concentration_report(roles):
    crit = [r for r in roles if r.critical]
    by_person, by_house, holders = {}, {}, {}
    for r in crit:
        by_person.setdefault(r.id, set()).add(r.name)
        by_house.setdefault(r.household_id, set()).add(r.name)
        holders.setdefault(r.name, set()).add(r.id)
    return {
        "person_multi_critical": dict((k, sorted(v)) for k, v in sorted(by_person.items()) if len(v) > 1),
        "household_multi_critical": dict((k, sorted(v)) for k, v in sorted(by_house.items()) if len(v) > 1),
        "single_holder_roles": sorted(k for k, v in holders.items() if len(v) < 2),
    }


def stock_chokepoints(stocks):
    """D6. stocks: [{"item": "fuel", "site": "S1", "keyholders": ["k1", "k2"]}, ...]
    (one row per item per site; keyholders are role-holder ids)."""
    sites, keys = {}, {}
    out = []
    for s in stocks:
        item, site = s.get("item"), s.get("site")
        kh = sorted(set(s.get("keyholders") or []))
        sites.setdefault(item, set()).add(site)
        for k in kh:
            keys.setdefault((item, k), set()).add(site)
        if len(kh) < MIN_KEYHOLDERS:
            out.append({"item": item, "site": site, "flag": "fewer than %d keyholders" % MIN_KEYHOLDERS})
    for item, ss in sorted(sites.items()):
        if len(ss) < MIN_SITES:
            out.append({"item": item, "site": None, "flag": "held at fewer than %d sites" % MIN_SITES})
        for (it, k), ks in sorted(keys.items()):
            if it == item and ks == ss:
                out.append({"item": item, "site": None,
                            "flag": "holder %s has keys to every site (full inventory in one role)" % k})
    return out


def main(argv):
    if not argv:
        sys.stderr.write("usage: roles.py ROLES.json [--today YYYY-MM-DD] [--stocks STOCKS.json]\n")
        return 2

    def opt(n):
        return argv[argv.index(n) + 1] if n in argv and argv.index(n) + 1 < len(argv) else None
    try:
        roles = load_roles(argv[0])
        today = parse_date(opt("--today")) or _dt.date.today()
        out = {"rotation": check_rotation(roles, today), "concentration": concentration_report(roles)}
        if opt("--stocks"):
            with open(opt("--stocks"), encoding="utf-8") as f:
                out["chokepoints"] = stock_chokepoints(json.load(f))
    except (OSError, ValueError, TypeError) as e:
        sys.stderr.write("REJECTED: %s\n" % e)
        return 1
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

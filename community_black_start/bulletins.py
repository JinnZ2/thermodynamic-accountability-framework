#!/usr/bin/env python3
# bulletins.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-04.
#
# D8 scheduled bulletins: plain-language public status on a fixed cadence.
# Feeds the POPULATION SEES / DOES column (docs/black_start_workforce_dependency_gap.md).
#
#   schedule(start, cadence_days) ──> due dates
#   bulletin {restored, next_step, household_role, date[, note]}
#       any required field empty -> not published (does not count)
#       D-M5 scope: a bulletin is public status, not an inventory. A field
#       naming holdings, sites, quantities or weak points, any key outside
#       the five allowed, or a quantity with a unit in a value -> rejected.
#   missed_bulletins(start, cadence, bulletins, today) -> due windows with no
#       published bulletin. A missed bulletin is itself a flag.
#
# Window rule: a bulletin covers the due date d if its date is in
# [d, d + cadence). Late inside the window counts; a window with nothing
# counts as missed.* A window still open today is not yet missed.
#
#   python3 bulletins.py LOG.json --start YYYY-MM-DD --cadence DAYS [--today YYYY-MM-DD]

import datetime as _dt
import json
import re
import sys

from roles import parse_date

REQUIRED = ("restored", "next_step", "household_role", "date")
ALLOWED = REQUIRED + ("note",)
FORBIDDEN_KEY_PARTS = ("holding", "stock", "inventory", "cache", "site", "location", "address", "where",
                       "quantity", "qty", "amount", "count", "level", "weak", "vulnerab", "gap",
                       "holder", "keyholder", "name")
QUANTITY = re.compile(r"\b\d+(\.\d+)?\s*(gal|gallons?|l|liters?|litres?|kg|lbs?|pounds?|tons?|cords?|"
                      r"days?|hours?|hrs?|units?|cases?|pallets?|bottles?|doses?|tanks?|%)\b", re.I)


def scope_problems(b):
    out = []
    for k in (b or {}):
        kl = str(k).lower()
        if any(p in kl for p in FORBIDDEN_KEY_PARTS):
            out.append("field %r names holdings, a site, a quantity or a weak point" % k)
        elif k not in ALLOWED:
            out.append("field %r is not part of a public bulletin" % k)
    for k in ALLOWED:
        v = (b or {}).get(k)
        if k != "date" and isinstance(v, str) and QUANTITY.search(v):
            out.append("field %r states a quantity; bulletins carry status, not amounts" % k)
    return out


def missing_fields(b):
    return [k for k in REQUIRED if not str((b or {}).get(k) or "").strip()]


def is_published(b):
    return (not missing_fields(b) and not scope_problems(b)
            and parse_date(b.get("date")) is not None)


def due_dates(start, cadence_days, today):
    s = parse_date(start)
    if s is None or not cadence_days or float(cadence_days) <= 0:
        raise ValueError("schedule needs a start date and a positive cadence")
    step = _dt.timedelta(days=float(cadence_days))
    out, d = [], s
    while d <= today:
        out.append(d)
        d = d + step
    return out, step


def missed_bulletins(start, cadence_days, bulletins, today=None):
    today = today or _dt.date.today()
    dues, step = due_dates(start, cadence_days, today)
    dates = sorted(parse_date(b["date"]) for b in bulletins if is_published(b))
    rejected = []
    for b in bulletins:
        if not is_published(b):
            r = {"date": (b or {}).get("date"), "missing": missing_fields(b)}
            if scope_problems(b):
                r["scope"] = scope_problems(b)
            rejected.append(r)
    gaps = []
    for d in dues:
        end = d + step
        if end > today:          # window still open
            continue
        if not any(d <= x < end for x in dates):
            gaps.append(d.isoformat())
    return {"missed": gaps, "not_counted": rejected,
            "plain": ("%d scheduled bulletin(s) missed. Ask the bulletin role why, in public."
                      % len(gaps)) if gaps else "No scheduled bulletin missed."}


def main(argv):
    def opt(n):
        return argv[argv.index(n) + 1] if n in argv and argv.index(n) + 1 < len(argv) else None
    if not argv or not opt("--start") or not opt("--cadence"):
        sys.stderr.write("usage: bulletins.py LOG.json --start YYYY-MM-DD --cadence DAYS [--today YYYY-MM-DD]\n")
        return 2
    try:
        with open(argv[0], encoding="utf-8") as f:
            log = json.load(f)
        today = parse_date(opt("--today")) or _dt.date.today()
        print(json.dumps(missed_bulletins(opt("--start"), float(opt("--cadence")), log, today), indent=2))
    except (OSError, ValueError, TypeError) as e:
        sys.stderr.write("REJECTED: %s\n" % e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

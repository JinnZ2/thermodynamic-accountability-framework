#!/usr/bin/env python3
# two_person.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-04.
#
# D7 two-person rule (same principle as nuclear custody). Four actions need
# two roles from different households:
#
#   authorize(action, role_a, role_b, ledger, networks, today)
#     ├─ same holder ............................... DENIED
#     ├─ same household ............................ DENIED
#     ├─ same dependency network (either depends
#     │  on the other, or both in one network) ..... DENIED
#     ├─ either role overdue / unknown rotation .... DENIED   (D10; unknown is never current)
#     └─ else ...................................... GRANTED  (both persons still act)
#   every decision, GRANTED or DENIED, is appended to the hash-chained ledger
#
# networks: {household_id: network_id}. Households sharing a network_id are
# treated as one dependency network: one depends on the other for food,
# heat, care or income.* Unknown household -> its own network.

import datetime as _dt
import sys

import coordination as co
import roles as rl

ACTIONS = ("release_critical_stock", "energize_or_switch", "ledger_quarantine", "accept_flagged_aid")


def check(action, role_a, role_b, networks=None, today=None):
    today = today or _dt.date.today()
    nets = networks or {}
    why = []
    if action not in ACTIONS:
        why.append("action must be one of %s" % (ACTIONS,))
    if role_a.id == role_b.id:
        why.append("one holder cannot be both persons")
    if role_a.household_id == role_b.household_id:
        why.append("both roles are in household %s" % role_a.household_id)
    na = nets.get(role_a.household_id, "own:" + role_a.household_id)
    nb = nets.get(role_b.household_id, "own:" + role_b.household_id)
    if na == nb and role_a.household_id != role_b.household_id:
        why.append("households %s and %s share dependency network %s"
                   % (role_a.household_id, role_b.household_id, na))
    for r in (role_a, role_b):
        st = r.rotation_state(today)
        if st in ("OVERDUE", "ROTATION_UNKNOWN", "NO_SCHEDULE"):
            why.append("role %s (%s) rotation %s" % (r.id, r.name, st))
    return {"action": action, "roles": [role_a.id, role_b.id], "date": today.isoformat(),
            "decision": "DENIED" if why else "GRANTED", "why": why}


def authorize(action, role_a, role_b, ledger_path, networks=None, today=None):
    res = check(action, role_a, role_b, networks, today)
    if res["decision"] == "GRANTED":
        plain = "Two-person approval GRANTED for %s by %s and %s; both acted." % (
            action, role_a.id, role_b.id)
    else:
        plain = "Two-person approval DENIED for %s: %s." % (action, "; ".join(res["why"]))
    body = dict(res, kind="two_person", plain=plain, schema_version=co.SCHEMA_VERSION)
    co.append_log(ledger_path, body)
    return res


def main(argv):
    sys.stderr.write("library module: import two_person and call authorize(); see tests/test_insider.py\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

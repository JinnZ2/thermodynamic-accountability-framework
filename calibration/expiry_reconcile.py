"""expiry_reconcile.py -- the #77 and #78 expiry registers in one table, plus the
97 lines #78 left unclassified. CC0, stdlib only. No logic change: this reads the
two registers and the tree; it edits nothing.

Work order 2026-11-10 (TAF expiry register: classify + reconcile).

The two counting rules, verbatim, and which PR used which. No rule is picked.

  #77 (branch claude/expiry-condition-stage1, docs/expiry_register.json, built on main dc1c8c1):
    "A slot is one place where the tree HOLDS a value in the state PENDING or
     UNKNOWN: a recorded data value, or a code site that assigns or returns that
     state. Not slots: vocabulary declarations and legends, prose stating a rule,
     comparisons and handlers, tests and selftest fixtures, docs/readme_archive/,
     CLAUDE.md, CONFLICTS.md."
  #78 (branch claude/healing-folder-additions-u5aojl, calibration/expiry_register.py, counted on base d5e6b1c):
    "PENDING  = lines containing the string PENDING       (grep -rn PENDING)      43
     UNKNOWN  = lines containing the WORD UNKNOWN          (grep -rnw UNKNOWN)     36"
    every such line gets one class; only SLOT, EMITTER and DEFAULT carry
    expiry_condition.

post_base_97: the lines PENDING / word-UNKNOWN that main gained after d5e6b1c, as
#78 listed them at its tip e177780 (= main dc1c8c1 + the #78 files). Classified
here under #78's classes and #78's guard: an exit is written only where the
line's own record or module names an instrument and a protocol; otherwise void.

Row codes (one per row). #77 says SLOT or nothing; #78 says one of eight classes.
    AGREE       both call it a slot (#77 SLOT, #78 SLOT/EMITTER/DEFAULT), or #77
                does not list it and #78's class is one #77's rule excludes
    CLASS_DIFF  same line, #77 SLOT, #78 a non-carrying class
    RULE_DIFF   one register lacks the row because its own rule cannot see it
                (#78: no token on the line; #77: a stated exclusion, e.g. CLAUDE.md)
    TREE_DIFF   #77 lists it, #78 as shipped does not: the line is after the base
    ONLY_77 / ONLY_78  the other rule could see the line and did not list it

Two comparisons are printed: #78 as shipped (base rows only), and #78 with
post_base_97. The exit verdicts are compared beside the code, not inside it.

    python3 calibration/expiry_reconcile.py              # summary + table
    python3 calibration/expiry_reconcile.py --write      # docs/EXPIRY_RECONCILED.md
    python3 calibration/expiry_reconcile.py --selftest
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import expiry_register as ER   # noqa: E402
from expiry_register import E, _TXT   # noqa: E402,F401

ROOT = ER.ROOT
PB_COMMIT = "e177780"   # #78 tip: main dc1c8c1 + the #78 files; where the 97 were listed
J77 = os.path.join(ROOT, "docs", "expiry_register.json")
OUT_MD = os.path.join(ROOT, "docs", "EXPIRY_RECONCILED.md")
EXCL_77 = ("CLAUDE.md", "CONFLICTS.md", "docs/readme_archive/")
# Same slots at different grain: #78 has one blanket row where #77 has per-item rows.
# Read off the two registers' own notes, not inferred from the tree.
GRAIN = {
    ("docs/worker_side_ledger_road_driver.md", 35):
        "#78 one heading row over five uncosted items; #77 lists them as P07-P11 (lines 37-41)",
    ("docs/DCEA_v0.1.md", 85):
        "#78 blanket row 'Numbers are left PENDING'; #77 reads this line as the partial-text source of P02-P05",
}

POST_BASE_97 = [
    ('CLAUDE.md', 3285, 'UNKNOWN', 'MENTION', None, None, 'audit note'),
    ('CLAUDE.md', 3312, 'EVIDENCE_PENDING.', 'MENTION', None, None, 'audit note'),
    ('CLAUDE.md', 3317, 'YES/NO/PARTIAL/PENDING/', 'MENTION', None, None, 'audit note'),
    ('community_black_start/coordination.py', 15, 'PENDING', 'VOCAB', None, None, 'state legend; also states the two exits'),
    ('community_black_start/coordination.py', 148, '"PENDING"', 'EMITTER', 'PB01_proposal_state', E("each party's accept / refuse decision recorded by consent()", "re-read state(p) after decisions: ACCEPTED when all accept, REFUSED on any refuse", _TXT + " (coordination.py:15)"), 'no time limit stated, so a proposal can stay PENDING without end; sensitivity void'),
    ('community_black_start/tests/test_coordination.py', 42, '"PENDING")', 'VOCAB', None, None, 'test fixture'),
    ('community_black_start/tests/test_coordination.py', 78, '"PENDING")', 'VOCAB', None, None, 'test fixture'),
    ('community_black_start/tests/test_coordination.py', 89, '"PENDING")', 'VOCAB', None, None, 'test fixture'),
    ('community_black_start/tests/test_coordination.py', 131, 'self.assertIn("PENDING",', 'VOCAB', None, None, 'test fixture'),
    ('gradient_field/README.md', 75, 'EVIDENCE_PENDING', 'MENTION', None, None, 'flag list'),
    ('gradient_field/field.py', 32, 'EVIDENCE_PENDING', 'VOCAB', None, None, 'flag legend / message template'),
    ('gradient_field/field.py', 57, '"EVIDENCE_PENDING":', 'VOCAB', None, None, 'flag legend / message template'),
    ('gradient_field/field.py', 162, 'out.append(("EVIDENCE_PENDING",', 'EMITTER', 'PB02_evidence_pending', E("the cited record entered in judgment_registry", "enter the record; the flag clears when pending_refs is empty", _TXT + " (field.py:32, 57: cited record(s) not entered yet)"), 'informational flag'),
    ('gradient_field/tests/test_gradients.py', 95, 'self.assertIn(("EVIDENCE_PENDING",', 'VOCAB', None, None, 'test fixture'),
    ('judgment_registry/README.md', 87, 'control_available: YES|NO|PARTIAL|UNKNOWN,', 'VOCAB', None, None, 'schema legend in prose'),
    ('judgment_registry/README.md', 91, 'consent: GIVEN|PARTIAL|ABSENT|NOT_POSSIBLE|UNKNOWN,', 'VOCAB', None, None, 'schema legend in prose'),
    ('judgment_registry/README.md', 92, 'loop: CLOSED|BROKEN|UNKNOWN,', 'VOCAB', None, None, 'schema legend in prose'),
    ('judgment_registry/README.md', 120, 'UNKNOWN', 'VOCAB', None, None, 'schema legend in prose'),
    ('judgment_registry/README.md', 121, 'UNKNOWN', 'VOCAB', None, None, 'schema legend in prose'),
    ('judgment_registry/README.md', 122, 'UNKNOWN', 'VOCAB', None, None, 'schema legend in prose'),
    ('judgment_registry/README.md', 147, 'UNKNOWN', 'VOCAB', None, None, 'schema legend in prose'),
    ('judgment_registry/README.md', 301, 'YES|NO|PARTIAL|PENDING|UNTESTED,', 'VOCAB', None, None, 'schema legend in prose'),
    ('judgment_registry/README.md', 305, 'BEFORE|AFTER|UNKNOWN,', 'VOCAB', None, None, 'schema legend in prose'),
    ('judgment_registry/README.md', 315, 'PENDING', 'RULE', None, None, ''),
    ('judgment_registry/README.md', 401, 'control_available=UNKNOWN', 'MENTION', None, None, 'worked example'),
    ('judgment_registry/README.md', 402, 'consent=UNKNOWN,', 'MENTION', None, None, 'worked example'),
    ('judgment_registry/README.md', 434, 'UNKNOWN,', 'RULE', None, None, ''),
    ('judgment_registry/ablation.py', 11, 'PENDING', 'VOCAB', None, None, 'legend'),
    ('judgment_registry/ablation.py', 14, 'PENDING', 'RULE', None, None, ''),
    ('judgment_registry/ablation.py', 84, '"PENDING"):', 'VOCAB', None, None, 'comparison (counter class, as #78 files == UNKNOWN)'),
    ('judgment_registry/docs/grounding_outside_law.md', 42, 'UNKNOWN', 'VOCAB', None, None, 'criterion answer set'),
    ('judgment_registry/docs/grounding_outside_law.md', 43, 'UNKNOWN', 'VOCAB', None, None, 'criterion answer set'),
    ('judgment_registry/docs/grounding_outside_law.md', 44, 'UNKNOWN', 'VOCAB', None, None, 'criterion answer set'),
    ('judgment_registry/docs/grounding_outside_law.md', 45, 'UNKNOWN', 'VOCAB', None, None, 'criterion answer set'),
    ('judgment_registry/docs/grounding_outside_law.md', 46, 'UNKNOWN', 'VOCAB', None, None, 'criterion answer set'),
    ('judgment_registry/docs/grounding_outside_law.md', 53, 'UNKNOWN.', 'RULE', None, None, ''),
    ('judgment_registry/docs/grounding_outside_law.md', 82, 'UNKNOWN', 'MENTION', None, None, 'rendered copy of criteria.json values; the slots are there'),
    ('judgment_registry/docs/grounding_outside_law.md', 83, 'UNKNOWN', 'MENTION', None, None, 'rendered copy of criteria.json values; the slots are there'),
    ('judgment_registry/docs/grounding_outside_law.md', 85, 'UNKNOWN', 'MENTION', None, None, 'rendered copy of criteria.json values; the slots are there'),
    ('judgment_registry/docs/grounding_outside_law.md', 86, 'UNKNOWN', 'MENTION', None, None, 'rendered copy of criteria.json values; the slots are there'),
    ('judgment_registry/docs/grounding_outside_law.md', 87, 'UNKNOWN', 'MENTION', None, None, 'rendered copy of criteria.json values; the slots are there'),
    ('judgment_registry/docs/grounding_outside_law.md', 88, 'UNKNOWN', 'MENTION', None, None, 'rendered copy of criteria.json values; the slots are there'),
    ('judgment_registry/docs/grounding_outside_law.md', 101, 'UNKNOWN', 'RULE', None, None, ''),
    ('judgment_registry/docs/grounding_outside_law.md', 102, 'UNKNOWN).', 'RULE', None, None, ''),
    ('judgment_registry/labels.py', 39, '"PENDING",', 'VOCAB', None, None, ''),
    ('judgment_registry/labels.py', 43, '"UNKNOWN")', 'VOCAB', None, None, ''),
    ('judgment_registry/labels.py', 60, 'UNKNOWN,', 'VOCAB', None, None, ''),
    ('judgment_registry/records/J10a.json', 67, '"control_available": "UNKNOWN"', 'SLOT', 'PB03_J10a_agency', "void", 'record lists missing_variables but none names an instrument for these two fields'),
    ('judgment_registry/records/J10a.json', 79, '"consent": "UNKNOWN"', 'SLOT', 'PB03_J10a_agency', "void", 'record lists missing_variables but none names an instrument for these two fields'),
    ('judgment_registry/records/J12/L6.json', 36, '"conclusion_survives": "PENDING"', 'SLOT', 'PB04_J12_L6_survives', E("controls C1 and C2", "run C1 and C2; record conclusion_survives", _TXT + " (L6.json:40 'pending controls C1 and C2'; labels.py:39 'test defined, not run')"), 'what a null result of C1/C2 does to the entry is not stated; sensitivity void'),
    ('judgment_registry/records/README.md', 24, 'UNKNOWN', 'MENTION', None, None, ''),
    ('judgment_registry/records/README.md', 182, 'PENDING', 'MENTION', None, None, ''),
    ('judgment_registry/records/README.md', 330, 'UNKNOWN', 'MENTION', None, None, ''),
    ('judgment_registry/records/precedents/PR2.json', 46, '"consent": "UNKNOWN"', 'SLOT', 'PB05_precedent_agency', "void", 'derived from criteria K1 / K2 (grounding_outside_law.md:101-102); those carry no exit, so neither does this'),
    ('judgment_registry/records/precedents/PR2.json', 47, '"loop": "UNKNOWN"', 'SLOT', 'PB05_precedent_agency', "void", 'derived from criteria K1 / K2 (grounding_outside_law.md:101-102); those carry no exit, so neither does this'),
    ('judgment_registry/records/precedents/PR2s.json', 47, '"consent": "UNKNOWN"', 'SLOT', 'PB05_precedent_agency', "void", 'derived from criteria K1 / K2 (grounding_outside_law.md:101-102); those carry no exit, so neither does this'),
    ('judgment_registry/records/precedents/PR2s.json', 48, '"loop": "UNKNOWN"', 'SLOT', 'PB05_precedent_agency', "void", 'derived from criteria K1 / K2 (grounding_outside_law.md:101-102); those carry no exit, so neither does this'),
    ('judgment_registry/records/precedents/PR3.json', 46, '"loop": "UNKNOWN"', 'SLOT', 'PB05_precedent_agency', "void", 'derived from criteria K1 / K2 (grounding_outside_law.md:101-102); those carry no exit, so neither does this'),
    ('judgment_registry/records/precedents/PR5.json', 38, '"consent": "UNKNOWN"', 'SLOT', 'PB05_precedent_agency', "void", 'derived from criteria K1 / K2 (grounding_outside_law.md:101-102); those carry no exit, so neither does this'),
    ('judgment_registry/records/precedents/PR5.json', 39, '"loop": "UNKNOWN"', 'SLOT', 'PB05_precedent_agency', "void", 'derived from criteria K1 / K2 (grounding_outside_law.md:101-102); those carry no exit, so neither does this'),
    ('judgment_registry/records/precedents/PR7.json', 60, '"consent": "UNKNOWN"', 'SLOT', 'PB05_precedent_agency', "void", 'derived from criteria K1 / K2 (grounding_outside_law.md:101-102); those carry no exit, so neither does this'),
    ('judgment_registry/records/precedents/PR7.json', 61, '"loop": "UNKNOWN"', 'SLOT', 'PB05_precedent_agency', "void", 'derived from criteria K1 / K2 (grounding_outside_law.md:101-102); those carry no exit, so neither does this'),
    ('judgment_registry/records/precedents/PR7s.json', 47, '"consent": "UNKNOWN"', 'SLOT', 'PB05_precedent_agency', "void", 'derived from criteria K1 / K2 (grounding_outside_law.md:101-102); those carry no exit, so neither does this'),
    ('judgment_registry/records/precedents/PR7s.json', 48, '"loop": "UNKNOWN"', 'SLOT', 'PB05_precedent_agency', "void", 'derived from criteria K1 / K2 (grounding_outside_law.md:101-102); those carry no exit, so neither does this'),
    ('judgment_registry/records/precedents/criteria.json', 8, '"UNKNOWN":', 'VOCAB', None, None, "'UNKNOWN': 'not stated'"),
    ('judgment_registry/records/precedents/criteria.json', 20, '"K1": "UNKNOWN"', 'SLOT', 'PB06_precedent_criteria', "void", "gloss is 'not stated'; no search protocol named"),
    ('judgment_registry/records/precedents/criteria.json', 21, '"K2": "UNKNOWN"', 'SLOT', 'PB06_precedent_criteria', "void", "gloss is 'not stated'; no search protocol named"),
    ('judgment_registry/records/precedents/criteria.json', 22, '"K3": "UNKNOWN"', 'SLOT', 'PB06_precedent_criteria', "void", "gloss is 'not stated'; no search protocol named"),
    ('judgment_registry/records/precedents/criteria.json', 23, '"K4": "UNKNOWN"', 'SLOT', 'PB06_precedent_criteria', "void", "gloss is 'not stated'; no search protocol named"),
    ('judgment_registry/records/precedents/criteria.json', 28, '"K2": "UNKNOWN"', 'SLOT', 'PB06_precedent_criteria', "void", "gloss is 'not stated'; no search protocol named"),
    ('judgment_registry/records/precedents/criteria.json', 29, '"K3": "UNKNOWN"', 'SLOT', 'PB06_precedent_criteria', "void", "gloss is 'not stated'; no search protocol named"),
    ('judgment_registry/records/precedents/criteria.json', 41, '"K1": "UNKNOWN"', 'SLOT', 'PB06_precedent_criteria', "void", "gloss is 'not stated'; no search protocol named"),
    ('judgment_registry/records/precedents/criteria.json', 42, '"K2": "UNKNOWN"', 'SLOT', 'PB06_precedent_criteria', "void", "gloss is 'not stated'; no search protocol named"),
    ('judgment_registry/records/precedents/criteria.json', 43, '"K3": "UNKNOWN"', 'SLOT', 'PB06_precedent_criteria', "void", "gloss is 'not stated'; no search protocol named"),
    ('judgment_registry/records/precedents/criteria.json', 44, '"K4": "UNKNOWN"', 'SLOT', 'PB06_precedent_criteria', "void", "gloss is 'not stated'; no search protocol named"),
    ('judgment_registry/records/precedents/criteria.json', 45, '"K5": "UNKNOWN"', 'SLOT', 'PB06_precedent_criteria', "void", "gloss is 'not stated'; no search protocol named"),
    ('judgment_registry/records/precedents/criteria.json', 50, '"K3": "UNKNOWN"', 'SLOT', 'PB06_precedent_criteria', "void", "gloss is 'not stated'; no search protocol named"),
    ('judgment_registry/records/precedents/criteria.json', 51, '"K4": "UNKNOWN"', 'SLOT', 'PB06_precedent_criteria', "void", "gloss is 'not stated'; no search protocol named"),
    ('judgment_registry/records/precedents/criteria.json', 55, '"K1": "UNKNOWN"', 'SLOT', 'PB06_precedent_criteria', "void", "gloss is 'not stated'; no search protocol named"),
    ('judgment_registry/records/precedents/criteria.json', 56, '"K2": "UNKNOWN"', 'SLOT', 'PB06_precedent_criteria', "void", "gloss is 'not stated'; no search protocol named"),
    ('judgment_registry/records/precedents/criteria.json', 57, '"K3": "UNKNOWN"', 'SLOT', 'PB06_precedent_criteria', "void", "gloss is 'not stated'; no search protocol named"),
    ('judgment_registry/records/precedents/criteria.json', 58, '"K4": "UNKNOWN"', 'SLOT', 'PB06_precedent_criteria', "void", "gloss is 'not stated'; no search protocol named"),
    ('judgment_registry/records/precedents/criteria.json', 65, '"K4": "UNKNOWN"', 'SLOT', 'PB06_precedent_criteria', "void", "gloss is 'not stated'; no search protocol named"),
    ('judgment_registry/schema.py', 46, '"UNKNOWN")', 'VOCAB', None, None, 'enum tuple'),
    ('judgment_registry/schema.py', 48, '"UNKNOWN")', 'VOCAB', None, None, 'enum tuple'),
    ('judgment_registry/schema.py', 49, '"UNKNOWN")', 'VOCAB', None, None, 'enum tuple'),
    ('judgment_registry/schema.py', 50, '"UNKNOWN")', 'VOCAB', None, None, 'enum tuple'),
    ('judgment_registry/schema.py', 73, '"UNKNOWN")', 'VOCAB', None, None, 'enum tuple'),
    ('judgment_registry/tests/test_ablation.py', 58, '("PENDING",', 'VOCAB', None, None, 'test fixture'),
    ('judgment_registry/tests/test_layers.py', 19, '"control_available": "UNKNOWN"', 'VOCAB', None, None, 'test fixture'),
    ('judgment_registry/tests/test_layers.py', 168, 'consent="UNKNOWN",', 'VOCAB', None, None, 'test fixture'),
    ('judgment_registry/tests/test_layers.py', 169, 'loop="UNKNOWN",', 'VOCAB', None, None, 'test fixture'),
    ('judgment_registry/tests/test_precedents.py', 58, '"UNKNOWN")', 'VOCAB', None, None, 'test fixture'),
    ('judgment_registry/tests/test_precedents.py', 93, '"UNKNOWN",', 'VOCAB', None, None, 'test fixture'),
    ('judgment_registry/tests/test_precedents.py', 101, '"PR5": "UNKNOWN"', 'VOCAB', None, None, 'test fixture'),
    ('signal_calibration/prereg/TEMPLATE.json', 31, '"reversibility": "UNKNOWN"', 'DEFAULT', 'PB07_prereg_reversibility', "void", 'template value the preregistrant overwrites; nothing names how reversibility is established; prereg.py does not check it'),
    ('signal_calibration/runner.py', 68, '"UNKNOWN"),', 'VOCAB', None, None, 'get() fallback (#78 convention); writes UNKNOWN into the record when the prereg omits it'),
]


def _show(commit, path):
    r = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.split("\n") if r.returncode == 0 else []


def _occ(commit):
    def g(args):
        out = subprocess.run(["git", "grep", "-n"] + args + [commit, "--", ".", ":!calibration/expiry_register.py",
                              ":!docs/EXPIRY_REGISTER.md"], cwd=ROOT, capture_output=True, text=True).stdout
        s = set()
        for l in out.splitlines():
            _, p, n, _ = l.split(":", 3)
            s.add((p, int(n)))
        return s
    return g(["PENDING"]), g(["-w", "UNKNOWN"])


def resolve(register, commit):
    """Each row's position in the tree at commit: its stated line if the quote is there,
    else the nearest line carrying the quote (the move is returned)."""
    pos, moved, missing, cache = {}, [], [], {}
    for row in register:
        path, line, quote = row[:3]
        lines = cache.setdefault(path, _show(commit, path))
        if 1 <= line <= len(lines) and quote in lines[line - 1]:
            at = line
        else:
            hits = [i + 1 for i, t in enumerate(lines) if quote in t and (path, i + 1) not in pos]
            at = min(hits, key=lambda h: abs(h - line)) if hits else None
            if at is None:
                missing.append((path, line))
                continue
            moved.append((path, line, at))
        pos[(path, at)] = row
    return pos, moved, missing


def verdict78(row):
    cls = row[3]
    if cls not in ER.CARRY_EXPIRY:
        return cls, None
    return cls, ER.exit_state(row[5])


def load77():
    d = json.load(open(J77, encoding="utf-8"))
    return {(s["file"], s["line"]): s for s in d["slots"]}, d["slot_rule"]


def reconcile(with_post_base=True):
    pos78, moved, missing = resolve(ER.REGISTER, PB_COMMIT)
    base_keys = set(pos78)
    if with_post_base:
        pb, _, pb_missing = resolve(POST_BASE_97, PB_COMMIT)
        missing += pb_missing
        pos78.update(pb)
    s77, _ = load77()
    pend, unk = _occ(PB_COMMIT)
    tokens = pend | unk
    base_lines = {}
    rows = []
    for key in sorted(set(pos78) | set(s77)):
        path, line = key
        r78, r77 = pos78.get(key), s77.get(key)
        v78 = verdict78(r78) if r78 else (None, None)
        batch = None if r78 is None else ("base_d5e6b1c" if key in base_keys else "post_base_97")
        if r77 and r78:
            code = "AGREE" if v78[0] in ER.CARRY_EXPIRY else "CLASS_DIFF"
            why = "" if code == "AGREE" else f"#77 SLOT ({r77['kind']}); #78 {v78[0]}"
        elif r77:
            if key not in tokens:
                code, why = "RULE_DIFF", "no PENDING / word-UNKNOWN token on the line; #78's rule cannot see it"
            elif not with_post_base and key not in base_keys:
                code, why = "TREE_DIFF", "line added after d5e6b1c; #78 counted on the base"
            else:
                code, why = "ONLY_77", "token on the line, not listed by #78"
        else:
            if v78[0] not in ER.CARRY_EXPIRY:
                code, why = "AGREE", ""
            elif key in GRAIN:
                code, why = "RULE_DIFF", GRAIN[key]
            elif path.startswith(EXCL_77) or path == "CLAUDE.md":
                code, why = "RULE_DIFF", "#77 excludes this file by its stated rule"
            else:
                code, why = "ONLY_78", "#78 carry class; #77's rule could see the line and did not list it"
        e77 = None if not r77 else ("VOID+partial" if r77["stated_partial"] else "VOID")
        rows.append(dict(path=path, line=line, v77=("SLOT" if r77 else "-"), v78=v78[0] or "-",
                         exit77=e77, exit78=v78[1], code=code, why=why, batch=batch,
                         sid=(r78[4] if r78 else None), id77=(r77["slot"] if r77 else None)))
    return dict(rows=rows, moved=moved, missing=missing, n_tokens=len(tokens),
                n_pend=len(pend), n_unk=len(unk))


CODES = ("AGREE", "RULE_DIFF", "TREE_DIFF", "CLASS_DIFF", "ONLY_77", "ONLY_78")


def counts(res):
    c = {k: 0 for k in CODES}
    for r in res["rows"]:
        c[r["code"]] += 1
    return c


def exit_split(res):
    """Among rows both registers call a slot: #77 writes VOID everywhere (its guard needs a
    stated null-result rule); #78 writes an exit where an instrument + protocol are named."""
    both = [r for r in res["rows"] if r["code"] == "AGREE" and r["v77"] == "SLOT"]
    split = [r for r in both if r["exit78"] != "none"]
    return len(both), split


def post_base_breakdown():
    by = {c: 0 for c in ER.CLASSES}
    exits = {"none": 0, "incomplete": 0, "complete": 0}
    for row in POST_BASE_97:
        by[row[3]] += 1
        if row[3] in ER.CARRY_EXPIRY:
            exits[ER.exit_state(row[5])] += 1
    return by, exits


def render(write=False):
    shipped, full = reconcile(False), reconcile(True)
    by, ex = post_base_breakdown()
    n_both, split = exit_split(full)
    out = ["# EXPIRY RECONCILED -- #77 and #78 in one register", "",
           "Generated by `calibration/expiry_reconcile.py`; do not edit by hand.", "",
           "## Counting rules (verbatim, see the module docstring; no rule is picked)", "",
           "- **#77** (built on main `dc1c8c1`): value-holding site rule, " + json.dumps(load77()[1]),
           "- **#78** (counted on base `d5e6b1c`): token-line rule. PENDING = lines containing the string; "
           "UNKNOWN = lines containing the whole word. One class per line.", "",
           f"Tree compared: `{PB_COMMIT}` (main `dc1c8c1` + #78 files); PENDING {full['n_pend']} lines, "
           f"word-UNKNOWN {full['n_unk']} lines, excluding #78's own two files. Rows moved since the base: "
           f"{len(full['moved'])}; rows not found: {len(full['missing'])}.", "",
           "## Summary", "", "| code | #78 as shipped | #78 + post_base_97 |", "|---|---|---|"]
    cs, cf = counts(shipped), counts(full)
    out += [f"| {k} | {cs[k]} | {cf[k]} |" for k in CODES]
    ag = lambda res, v: sum(1 for r in res["rows"] if r["code"] == "AGREE" and (r["v77"] == "SLOT") == v)
    out += [f"| AGREE, both a slot | {ag(shipped, True)} | {ag(full, True)} |",
            f"| AGREE, both not a slot (#77 by its exclusions) | {ag(shipped, False)} | {ag(full, False)} |"]
    out += [f"| rows | {len(shipped['rows'])} | {len(full['rows'])} |", "",
            f"Exit verdicts, compared beside the code: of {n_both} rows both call a slot, "
            f"{len(split)} carry an exit under #78 (instrument + protocol named, sensitivity void) "
            "where #77 writes VOID (its guard also needs a stated null-result rule). "
            "Neither guard is picked.", "",
            "## post_base_97 breakdown", "",
            "| class | rows |", "|---|---|"] + [f"| {c} | {n} |" for c, n in by.items()] + [
            "", f"carrying rows by exit: no exit {ex['none']}, incomplete {ex['incomplete']}, complete {ex['complete']}", "",
            "## Rows (#78 + post_base_97)", "",
            "| file:line | #77 | #78 | code | why_split | batch | exit #77 / #78 |", "|---|---|---|---|---|---|---|"]
    for r in full["rows"]:
        out.append(f"| {r['path']}:{r['line']} | {r['v77']}{' ' + r['id77'] if r['id77'] else ''} | {r['v78']} | "
                   f"{r['code']} | {r['why']} | {r['batch'] or '-'} | {r['exit77'] or '-'} / {r['exit78'] or '-'} |")
    text = "\n".join(out) + "\n"
    if write:
        open(OUT_MD, "w", encoding="utf-8").write(text)
    return text


def selftest():
    checks = []
    pend, unk = _occ(PB_COMMIT)
    pos78, _, miss = resolve(ER.REGISTER, PB_COMMIT)
    after = (pend | unk) - set(pos78)
    pb, _, pbmiss = resolve(POST_BASE_97, PB_COMMIT)
    checks.append(("post_base_97 is exactly the after-base set at the #78 tip", set(pb) == after and len(pb) == 97))
    checks.append(("every row resolves at the #78 tip", not miss and not pbmiss))
    checks.append(("every post_base row has a known class and a carry/expiry match",
                   all(r[3] in ER.CLASSES and ((r[3] in ER.CARRY_EXPIRY) == (r[5] is not None)) for r in POST_BASE_97)))
    full = reconcile(True)
    checks.append(("no TREE_DIFF once post_base_97 is in", counts(full)["TREE_DIFF"] == 0))
    s77, _ = load77()
    checks.append(("every #77 slot appears in the table", all(k in {(r['path'], r['line']) for r in full["rows"]} for k in s77)))
    shipped = reconcile(False)
    checks.append(("as shipped, TREE_DIFF is reachable", counts(shipped)["TREE_DIFF"] > 0))
    checks.append(("codes partition the rows", sum(counts(full).values()) == len(full["rows"])))
    checks.append(("grain rows read as RULE_DIFF",
                   all(r["code"] == "RULE_DIFF" for r in full["rows"] if (r["path"], r["line"]) in GRAIN)))
    for name, ok in checks:
        print(("PASS " if ok else "FAIL ") + name)
    failed = sum(not ok for _, ok in checks)
    print(f"checks: {len(checks)}   failed: {failed}")
    return failed


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(1 if selftest() else 0)
    print(render(write="--write" in sys.argv))

#!/usr/bin/env python3
# misuse_guard/scan.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# Pattern scan of committed FIXTURES (tests, examples, scenarios, templates,
# seeds and JSON data) in the misuse-register modules. Pattern list is thin:*
# it misses paraphrased or encoded identifiers.
#
# A line that plants a pattern on purpose (to test a guard) carries the
# marker "misuse-scan: planted" and is skipped.

import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULES = ("assembly_instrument", "community_black_start", "judgment_registry", "signal_calibration")
FIXTURE_DIRS = ("tests", "examples", "scenarios", "templates", "seeds", "prereg")
MARKER = "misuse-scan: planted"

PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"),
    "phone": re.compile(r"(?<![\d.])(?:\+?1[ .-])?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)"),
    "street_address": re.compile(r"\b\d{1,5}\s+(?:[NSEW]\.?\s+)?[A-Z][a-z]+(?:\s[A-Z][a-z]+)?\s(?:Street|St|Avenue|"
                                 r"Ave|Road|Rd|Lane|Ln|Drive|Dr|Highway|Hwy|Boulevard|Blvd|Court|Ct|Trail)\b"),
    "coordinate_pair": re.compile(r"(?<![\d.])-?\d{1,3}\.\d{3,}\s*,\s*-?\d{1,3}\.\d{3,}"),
    # a two-word capitalized name as the value of a person-ish field ("Judge Q" is fine: one-letter part)
    "person_name_field": re.compile(r"[\"']?(?:holder|name|contact|owner|steward|person|recorder|judge|"
                                    r"name_or_body|scorer|intervener)[\"']?\s*[:=]\s*[\"']([A-Z][a-z]{2,} [A-Z][a-z]{2,})[\"']"),
}
ALLOWED_NAMES = {"Council R", "Judge Q"}


def fixture_files(root=REPO_ROOT):
    for m in MODULES:
        base = os.path.join(root, m)
        for dirpath, dirnames, files in os.walk(base):
            dirnames[:] = [d for d in dirnames if d != "__pycache__"]
            rel = os.path.relpath(dirpath, base).split(os.sep)
            in_fixture_dir = rel[0] in FIXTURE_DIRS
            for fn in files:
                if fn.endswith((".pyc",)):
                    continue
                if in_fixture_dir or fn.endswith(".json"):
                    yield os.path.join(dirpath, fn)


def scan(paths=None):
    hits = []
    for p in paths if paths is not None else fixture_files():
        try:
            with open(p, encoding="utf-8") as f:
                lines = f.read().splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for n, line in enumerate(lines, 1):
            if MARKER in line:
                continue
            for name, rx in PATTERNS.items():
                for m in rx.finditer(line):
                    val = m.group(1) if m.groups() else m.group(0)
                    if name == "person_name_field" and val in ALLOWED_NAMES:
                        continue
                    hits.append((os.path.relpath(p, REPO_ROOT), n, name, val))
    return hits


if __name__ == "__main__":
    h = scan()
    for p, n, name, val in h:
        print("%s:%d  %-18s %s" % (p, n, name, val))
    print("%d hit(s)" % len(h))
    sys.exit(1 if h else 0)

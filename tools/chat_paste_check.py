"""
chat_paste_check.py

Pre-commit hook that catches chat-paste contamination in
.py files before they enter the repo. Flags:

  - smart quotes used as string delimiters or in code
  - markdown ``` fences inside .py files
  - markdown-bold dunders (double-asterisk wrapping a
    dunder name; this is what dunders look like when they
    have been mangled by a markdown renderer)
  - ellipsis character (U+2026) in code (rare in
    legitimate Python)
  - flat class/def bodies (def or class statement followed
    by a non-indented line that is not a decorator,
    comment, or blank)

Exit code 0 = clean, 1 = contamination found.
stdlib only. CC0.

Usage:
    python tools/chat_paste_check.py path/to/file.py [...]
    python tools/chat_paste_check.py --staged   # git staged files
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


SMART_QUOTES = "\u201c\u201d\u2018\u2019"  # left/right double, left/right single
ELLIPSIS_CHAR = "\u2026"
FENCE_RE = re.compile(r"^\s*```")
BOLD_DUNDER_RE = re.compile(r"\*\*[a-z_]+\*\*")
DEF_CLASS_RE = re.compile(r"^(def|class)\s+\w")


def check_file(path: Path) -> List[Tuple[int, str]]:
    """Return list of (line_no, message) findings."""
    findings: List[Tuple[int, str]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return [(0, f"could not read: {e}")]

    lines = text.splitlines()
    in_def_or_class = False

    for i, line in enumerate(lines, 1):
        # smart quotes
        for ch in SMART_QUOTES:
            if ch in line:
                findings.append(
                    (i, f"smart quote {ch!r} present")
                )
                break
        # ellipsis
        if ELLIPSIS_CHAR in line:
            findings.append((i, "ellipsis character (use ...)"))
        # markdown fences
        if FENCE_RE.match(line):
            findings.append((i, "markdown ``` fence in .py"))
        # bold dunders
        if BOLD_DUNDER_RE.search(line):
            findings.append(
                (i, "markdown-bold dunder (double-asterisk-wrapped dunder)")
            )
        # flat body detection
        if DEF_CLASS_RE.match(line.lstrip()) and \
                line == line.lstrip():
            in_def_or_class = True
            continue
        if in_def_or_class:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                continue
            if stripped.startswith('"""') or \
                    stripped.startswith("'''"):
                in_def_or_class = False
                continue
            if line.startswith(" ") or line.startswith("\t"):
                in_def_or_class = False
                continue
            # non-indented line right after def/class
            findings.append(
                (i, "flat body (non-indented after def/class)")
            )
            in_def_or_class = False

    return findings


def staged_python_files() -> List[Path]:
    """Return .py files currently staged in git."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only",
         "--diff-filter=ACM"],
        capture_output=True, text=True
    )
    paths = []
    for name in result.stdout.splitlines():
        if name.endswith(".py"):
            p = Path(name)
            if p.exists():
                paths.append(p)
    return paths


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 0

    if argv[1] == "--staged":
        paths = staged_python_files()
    else:
        paths = [Path(p) for p in argv[1:]]

    any_findings = False
    for path in paths:
        findings = check_file(path)
        if findings:
            any_findings = True
            print(f"\n{path}:")
            for line_no, msg in findings:
                print(f"  line {line_no}: {msg}")

    if any_findings:
        print(
            "\nchat-paste contamination found. "
            "Fix before commit."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

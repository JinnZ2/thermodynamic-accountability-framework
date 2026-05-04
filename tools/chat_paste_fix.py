"""
chat_paste_fix.py

Auto-fixes the mechanical subset of chat-paste contamination:
  - smart quotes -> straight quotes
  - ellipsis char -> ...
  - markdown bold dunders -> real dunders
  - markdown ``` fences -> stripped (only if the line is
    JUST the fence; otherwise flagged for human review)

Does NOT auto-fix indentation. That requires structural
reasoning and is left for human review or a separate tool.

Usage:
    python tools/chat_paste_fix.py path/to/file.py [...]
"""
import re
import sys
from pathlib import Path


# Use \u escapes so this file does not itself contain the literal
# contamination characters (which would cause chat_paste_check.py
# to flag this fixer as needing fixing).
_LDQ = "\u201c"   # left double quote
_RDQ = "\u201d"   # right double quote
_LSQ = "\u2018"   # left single quote
_RSQ = "\u2019"   # right single quote
_ELL = "\u2026"   # ellipsis


def fix(text: str) -> str:
    text = text.replace(_LDQ, chr(34)).replace(_RDQ, chr(34))
    text = text.replace(_LSQ, chr(39)).replace(_RSQ, chr(39))
    text = text.replace(_ELL, "...")
    text = re.sub(
        r"\*\*([a-z_]+)\*\*",
        lambda m: f"__{m.group(1)}__",
        text,
    )
    # strip pure-fence lines
    fixed_lines = []
    for line in text.splitlines():
        if re.match(r"^\s*```\s*$", line):
            continue
        fixed_lines.append(line)
    return "\n".join(fixed_lines) + (
        "\n" if text.endswith("\n") else ""
    )


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 0
    for p in argv[1:]:
        path = Path(p)
        original = path.read_text(encoding="utf-8")
        cleaned = fix(original)
        if cleaned != original:
            path.write_text(cleaned, encoding="utf-8")
            print(f"fixed: {path}")
        else:
            print(f"clean: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

#!/usr/bin/env python3
# misuse_guard/render_register.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# docs/misuse_register.md and the misuse section of each module README are
# generated from docs/misuse_register.json so they cannot drift. A test
# checks that the committed files match.
#
#   python3 misuse_guard/render_register.py          # rewrite the .md
#   python3 misuse_guard/render_register.py --check  # exit 1 if stale

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(ROOT, "docs", "misuse_register.json")
MD_PATH = os.path.join(ROOT, "docs", "misuse_register.md")


def render(reg):
    out = ["# Misuse register", "",
           "Generated from `misuse_register.json` by `misuse_guard/render_register.py`; edit the JSON.", "",
           reg["scope"], "", reg["principle"], "", "Provenance: " + reg["provenance"] + ".", "",
           "Status: " + "; ".join("%s = %s" % kv for kv in reg["status_vocabulary"].items()) + ".",
           "Trailing asterisks mark thin volume.", "", "## Entries", ""]
    for e in reg["entries"]:
        out += ["### %s  %s  (%s, %s)" % (e["id"], e["module"], e["status"], e["provenance"]), "",
                "```text",
                "surface          %s" % e["surface"],
                "adversarial use  %s" % e["adversarial_use"],
                "mitigations      %s" % (", ".join(e["mitigation_ids"]) or "none yet"),
                "residual         %s" % e["residual"],
                "volume           %s" % e["volume"],
                "```", ""]
    out += ["## Mitigations", "", "| id | what | code | test |", "|---|---|---|---|"]
    for d in reg["mitigations"]:
        out.append("| %s | %s | `%s` | %s |" % (d["id"], d["description"], d["code"], d["test"]))
    ip = reg.get("independent_pass")
    if ip:
        out += ["", "## Independent pass", "", "%s (%s). M10 onward are its novel findings, status PROPOSED." % (ip["method"], ip["date"]),
                "", "Its findings already covered by the first pass:", ""]
        out += ["- %s: %s" % kv for kv in ip["covered_by_first_pass"].items()]
        out += ["", "Its findings already recorded as known limits:", ""] + ["- " + k for k in ip["already_known_limits"]]
    out += ["", "## Experiments", ""]
    for x in reg["experiments"]:
        out.append("- **%s** %s: %s  %s (volume %s)" % (x["id"], x["name"], x["question"], x["status"], x["volume"]))
    out += ["", "## Limits", ""] + ["- " + l for l in reg["limits"]] + [""]
    return "\n".join(out)


README_MODULES = ("assembly_instrument", "community_black_start", "judgment_registry", "signal_calibration")
BEGIN, END = "<!-- misuse-section:begin (generated; edit docs/misuse_register.json) -->", "<!-- misuse-section:end -->"
TITLE = "## How this could be used against its purpose"


def section(reg, module):
    mit = dict((d["id"], d) for d in reg["mitigations"])
    ents = [e for e in reg["entries"] if e["module"] in (module, "cross-cutting")]
    lines = [BEGIN, TITLE, "",
             "Pattern level only. Full register: [`docs/misuse_register.md`](../docs/misuse_register.md).", "",
             "```text"]
    for e in ents:
        lines.append("%s  %s" % (e["id"], e["surface"]))
        lines.append("     use        %s" % e["adversarial_use"])
        lines.append("     mitigated  %s" % ", ".join(e["mitigation_ids"]) if e["mitigation_ids"] else "     mitigated  none yet")
        lines.append("     residual   %s" % e["residual"])
        lines.append("     status     %s (%s)" % (e["status"], e["provenance"]))
    lines.append("```")
    used = sorted(set(m for e in ents for m in e["mitigation_ids"]))
    if used:
        lines += ["", "| mitigation | what |", "|---|---|"] + ["| %s | %s |" % (m, mit[m]["description"]) for m in used]
    lines.append(END)
    return "\n".join(lines)


def update_readme(reg, module, root=ROOT, write=True):
    path = os.path.join(root, module, "README.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    block = section(reg, module)
    if BEGIN in text:
        a = text.index(BEGIN)
        b = text.index(END, a) + len(END)
        new = text[:a] + block + text[b:]
    else:
        marker = "\n## License"
        i = text.rfind(marker)
        new = (text[:i] + "\n" + block + "\n" + text[i:]) if i >= 0 else (text.rstrip("\n") + "\n\n" + block + "\n")
    if write and new != text:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
    return new == text


def main(argv):
    with open(JSON_PATH, encoding="utf-8") as f:
        reg = json.load(f)
    text = render(reg)
    if "--check" in argv:
        with open(MD_PATH, encoding="utf-8") as f:
            ok = f.read() == text
        return 0 if ok and all(update_readme(reg, m, write=False) for m in README_MODULES) else 1
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write(text)
    for m in README_MODULES:
        update_readme(reg, m)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

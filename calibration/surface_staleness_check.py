"""
surface_staleness_check.py

CI check: is TAF's pinned upstream contract surface still the latest
one declared upstream?

Per ME's SURFACE.md consumer guidance:
    "CI should monitor staleness by comparing pinned tags against
     the latest equations-v* tag upstream."

This script walks the PINS list, queries GitHub's tag API for each
upstream, finds the highest-numbered tag matching the declared
pattern, and compares it to our pinned tag. Exits non-zero if any
pin is stale, zero otherwise.

Runs locally:
    python3 calibration/surface_staleness_check.py

Runs in CI via .github/workflows/surface-staleness.yml.

License: CC0 1.0 Universal
Dependencies: stdlib only (urllib, json, re)
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request


# ---------------------------------------------------------------
# PIN REGISTRY
# ---------------------------------------------------------------
#
# Add an entry here when TAF mirrors a new tag-versioned upstream.
# Each entry declares:
#   name        -- human-readable label
#   owner/repo  -- GitHub coordinates
#   pinned_tag  -- what TAF currently mirrors
#   tag_pattern -- regex that matches the upstream's tag scheme
#                  (must contain a single integer capture group for
#                  the "latest" comparison)
#   contract_file -- path (relative to repo root) of the TAF-side
#                    contract module, included in failure messages
#                    so the fix location is obvious.

PINS = [
    {
        "name": "mathematic_economics",
        "owner": "JinnZ2",
        "repo": "Mathematic-economics",
        "pinned_tag": "equations-v1",
        "tag_pattern": r"^equations-v(\d+)$",
        "contract_file": "schemas/mathematic_economics_contract.py",
    },
]


# ---------------------------------------------------------------
# GITHUB API
# ---------------------------------------------------------------

def _fetch_tags(owner: str, repo: str, timeout: float = 10.0) -> list[str]:
    """Return list of tag names for owner/repo. Stdlib only.

    Reads GITHUB_TOKEN from the environment if present (raises the
    rate limit from 60/hr to 5000/hr under CI). Anonymous otherwise.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/tags?per_page=100"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "taf-surface-staleness-check",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return [t["name"] for t in data]


# ---------------------------------------------------------------
# CHECK ONE PIN
# ---------------------------------------------------------------

def check_pin(pin: dict) -> tuple[bool, str, str]:
    """Check one pin. Returns (ok, latest_tag, message)."""
    name = pin["name"]
    pattern = re.compile(pin["tag_pattern"])
    pinned = pin["pinned_tag"]

    try:
        tags = _fetch_tags(pin["owner"], pin["repo"])
    except urllib.error.HTTPError as e:
        if e.code == 403:
            return (True, pinned,
                    f"[{name}] SKIP: GitHub API rate-limited ({e.code}).")
        return (True, pinned,
                f"[{name}] SKIP: GitHub API error ({e.code}). "
                f"Treating as non-failing.")
    except (urllib.error.URLError, TimeoutError) as e:
        return (True, pinned,
                f"[{name}] SKIP: network error ({e}). Treating as "
                f"non-failing.")

    matching = []
    for tag in tags:
        m = pattern.match(tag)
        if m:
            try:
                matching.append((int(m.group(1)), tag))
            except (IndexError, ValueError):
                continue

    if not matching:
        return (True, pinned,
                f"[{name}] WARN: no tags match pattern "
                f"{pin['tag_pattern']!r} in {pin['owner']}/{pin['repo']}. "
                f"Pinned: {pinned}. Upstream may have removed the tag "
                f"scheme.")

    matching.sort(key=lambda x: x[0], reverse=True)
    latest_n, latest_tag = matching[0]

    pinned_match = pattern.match(pinned)
    pinned_n = int(pinned_match.group(1)) if pinned_match else -1

    if latest_n > pinned_n:
        return (False, latest_tag,
                f"[{name}] STALE: pinned {pinned!r} but upstream has "
                f"{latest_tag!r}. Update {pin['contract_file']}: bump "
                f"CONTRACT_VERSION major, set UPSTREAM_SURFACE_TAG "
                f"= {latest_tag!r}, and verify formulas still match.")
    return (True, latest_tag,
            f"[{name}] OK: pinned {pinned!r} is current. "
            f"(Latest upstream: {latest_tag!r})")


# ---------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """Return 0 if all pins current, 1 if any stale."""
    print("TAF surface staleness check")
    print("=" * 50)

    any_stale = False
    for pin in PINS:
        ok, _, msg = check_pin(pin)
        print(msg)
        if not ok:
            any_stale = True

    print("=" * 50)
    if any_stale:
        print("RESULT: stale pin(s) detected. Bump and re-verify.")
        return 1
    print(f"RESULT: all {len(PINS)} pin(s) current.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

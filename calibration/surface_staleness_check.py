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
        "kind": "tag",
        "name": "mathematic_economics",
        "owner": "JinnZ2",
        "repo": "Mathematic-economics",
        "pinned_tag": "equations-v1",
        "tag_pattern": r"^equations-v(\d+)$",
        "contract_file": "schemas/mathematic_economics_contract.py",
    },
    {
        "kind": "constant",
        "name": "logic_ferret",
        "owner": "JinnZ2",
        "repo": "Logic-Ferret",
        "branch": "main",
        "source_file": "schema_contract.py",
        "constant_name": "SCHEMA_VERSION",
        "pinned_version": "1.2.0",
        "contract_file": "schemas/logic_ferret_contract.py",
    },
    {
        "kind": "commit_sha",
        "name": "metabolic_accounting",
        "owner": "JinnZ2",
        "repo": "metabolic-accounting",
        "branch": "main",
        "pinned_sha": "09382a66ce6ee63d84038c8ee35a1fbc28cda58d",
        "contract_file": "schemas/metabolic_accounting_contract.py",
        "notes": "Upstream has no declared version; pinned to commit SHA. "
                 "When upstream adopts SURFACE.md, migrate to a tag or "
                 "constant pin.",
    },
    {
        "kind": "commit_sha",
        "name": "geometric_bridge",
        "owner": "JinnZ2",
        "repo": "Geometric-to-Binary-Computational-Bridge",
        "branch": "main",
        "pinned_sha": "ba1a5251be7d39bcef865e47e7dd8c513d0044ed",
        "contract_file": "schemas/geometric_bridge_contract.py",
        "notes": "Upstream has no declared version yet; pre-release (500+ "
                 "commits). Contract provides functional stdlib fallbacks so "
                 "TAF's taf_bridge.py works end-to-end without the external "
                 "repo installed.",
    },
]


# ---------------------------------------------------------------
# GITHUB API
# ---------------------------------------------------------------

def _gh_headers() -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "taf-surface-staleness-check",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _fetch_tags(owner: str, repo: str, timeout: float = 10.0) -> list[str]:
    """Return list of tag names for owner/repo. Stdlib only.

    Reads GITHUB_TOKEN from the environment if present (raises the
    rate limit from 60/hr to 5000/hr under CI). Anonymous otherwise.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/tags?per_page=100"
    req = urllib.request.Request(url, headers=_gh_headers())
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return [t["name"] for t in data]


def _fetch_raw_file(owner: str, repo: str, branch: str, path: str,
                    timeout: float = 10.0) -> str:
    """Fetch raw file content from a GitHub repo."""
    url = (f"https://raw.githubusercontent.com/{owner}/{repo}/"
           f"{branch}/{path}")
    req = urllib.request.Request(url, headers=_gh_headers())
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


# ---------------------------------------------------------------
# CHECK ONE PIN
# ---------------------------------------------------------------

def check_pin(pin: dict) -> tuple[bool, str, str]:
    """Check one pin. Returns (ok, latest_or_current, message).

    Dispatches on pin['kind']:
      - 'tag'        (default for back-compat) -- compares upstream
                      tags against a pinned tag via a regex with an
                      integer capture group.
      - 'constant'   -- fetches a source file from upstream and greps
                        for a version-constant assignment (e.g.
                        SCHEMA_VERSION = "1.0.0"); compares upstream
                        major to pinned major.
      - 'commit_sha' -- fetches the latest commit SHA on a named
                        branch and compares. Any drift is reported as
                        ADVISORY (upstream has no declared version, so
                        the drift may or may not be schema-affecting).
    """
    kind = pin.get("kind", "tag")
    if kind == "constant":
        return _check_constant_pin(pin)
    if kind == "commit_sha":
        return _check_commit_sha_pin(pin)
    return _check_tag_pin(pin)


def _check_tag_pin(pin: dict) -> tuple[bool, str, str]:
    """Check a tag-based pin (the original mechanism)."""
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


def _check_constant_pin(pin: dict) -> tuple[bool, str, str]:
    """Check a constant-in-file pin.

    Fetches the source file and looks for the declared constant
    assignment. Compares major version to the pinned major version;
    minor bumps (additions) are tolerated, major bumps fail loudly.
    """
    name = pin["name"]
    constant = pin["constant_name"]
    pinned = pin["pinned_version"]

    try:
        content = _fetch_raw_file(
            pin["owner"], pin["repo"],
            pin.get("branch", "main"),
            pin["source_file"],
        )
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            return (True, pinned,
                    f"[{name}] SKIP: GitHub rate-limited ({e.code}).")
        if e.code == 404:
            return (True, pinned,
                    f"[{name}] WARN: source file not found "
                    f"({pin['source_file']}). Upstream may have moved it.")
        return (True, pinned,
                f"[{name}] SKIP: HTTP error {e.code}. Non-failing.")
    except (urllib.error.URLError, TimeoutError) as e:
        return (True, pinned,
                f"[{name}] SKIP: network error ({e}). Non-failing.")

    # Look for   CONSTANT_NAME = "x.y.z"   or   CONSTANT_NAME = 'x.y.z'
    pat = re.compile(
        rf"^\s*{re.escape(constant)}\s*=\s*[\"']([0-9]+\.[0-9]+\.[0-9]+)[\"']",
        re.MULTILINE,
    )
    m = pat.search(content)
    if not m:
        return (True, pinned,
                f"[{name}] WARN: {constant} not found in "
                f"{pin['source_file']}. Upstream may have renamed it.")

    upstream_version = m.group(1)
    try:
        upstream_major = int(upstream_version.split(".")[0])
        pinned_major = int(pinned.split(".")[0])
    except ValueError:
        return (True, pinned,
                f"[{name}] WARN: could not parse version "
                f"({upstream_version!r} / {pinned!r}).")

    if upstream_major > pinned_major:
        return (False, upstream_version,
                f"[{name}] STALE: pinned {pinned!r} but upstream "
                f"{constant}={upstream_version!r}. Major bump. "
                f"Update {pin['contract_file']}: bump CONTRACT_VERSION "
                f"major, set UPSTREAM_SCHEMA_VERSION = "
                f"{upstream_version!r}, and re-run "
                f"validate_ferret_surface against the new shape.")
    if upstream_version != pinned:
        return (True, upstream_version,
                f"[{name}] OK (minor drift): pinned {pinned!r}, "
                f"upstream {upstream_version!r}. Non-breaking; "
                f"consider bumping CONTRACT_VERSION minor in "
                f"{pin['contract_file']} to surface additions.")
    return (True, upstream_version,
            f"[{name}] OK: pinned {pinned!r} matches upstream.")


def _check_commit_sha_pin(pin: dict) -> tuple[bool, str, str]:
    """Check a commit-SHA pin.

    Used when upstream has not declared a version scheme (no tags, no
    SCHEMA_VERSION constant). Fetches the latest SHA on a named branch
    and reports drift. Because there is no version-schema guarantee,
    ANY drift triggers an ADVISORY result (exit code 0, but the
    operator is notified and should manually verify whether the drift
    touched the schema).
    """
    name = pin["name"]
    pinned = pin["pinned_sha"]

    url = (f"https://api.github.com/repos/{pin['owner']}/{pin['repo']}/"
           f"commits/{pin.get('branch', 'main')}")
    req = urllib.request.Request(url, headers=_gh_headers())
    try:
        with urllib.request.urlopen(req, timeout=10.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            return (True, pinned,
                    f"[{name}] SKIP: GitHub rate-limited ({e.code}).")
        return (True, pinned,
                f"[{name}] SKIP: HTTP error {e.code}. Non-failing.")
    except (urllib.error.URLError, TimeoutError) as e:
        return (True, pinned,
                f"[{name}] SKIP: network error ({e}). Non-failing.")

    latest_sha = str(data.get("sha", ""))
    if not latest_sha:
        return (True, pinned,
                f"[{name}] WARN: could not parse commit response.")

    if latest_sha == pinned:
        return (True, latest_sha,
                f"[{name}] OK: pinned SHA is current HEAD.")

    # Drift detected. ADVISORY: upstream may or may not have touched
    # the schema. Always non-failing (exit 0) so that a routine upstream
    # commit doesn't break downstream CI.
    short_pinned = pinned[:10]
    short_latest = latest_sha[:10]
    commit_url = (f"https://github.com/{pin['owner']}/{pin['repo']}/"
                  f"compare/{pinned}...{latest_sha}")
    return (True, latest_sha,
            f"[{name}] ADVISORY: upstream main moved from "
            f"{short_pinned} to {short_latest}. Inspect changes "
            f"against {pin['contract_file']}: {commit_url}")


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

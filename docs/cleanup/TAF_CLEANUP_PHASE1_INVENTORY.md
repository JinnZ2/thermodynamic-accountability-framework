# TAF cleanup, phase 1 inventory and phase 2 status

Written 2026-11-11 (Kavik + Claude). The phase 1 table itself lived in a
cleanup-session scratchpad and was never committed; this file is the
re-created record: the approval list as proposed, and what phase 2 did.
Tag pushes are refused from sessions, so "tag/archive" means a branch
under `archive/`. Branch deletes are also refused from sessions; those
rows are left for a person with push rights.

## TAF items (proposed -> approved action -> status)

| # | Item | Action | Status |
|---|---|---|---|
| 1 | #76 | merge | merged |
| 16 | #80 + #82 + #84 + #85 | collapse onto #85 branch, base main; pipeline = #84 three-value + #81 no-score -> UNKNOWN | done; #80/#82/#84 closed; folded at 65bb724 |
| 17 | #73 into #74 | close #73 | closed; archive/undeclared-intent-switch |
| 18 | #78 into #79 | close #78 | contained in merged #79 |
| 19 | #77 + #81 + #83 | one PR on #83 branch, base main | done; #77/#81 closed; archive/expiry-condition-stage1, archive/silent-fill-register |
| 22 | #79 | merge first | merged (953f1a8) |
| 32 | #52 | close + archive | closed; archive/manus-wo6-read-me-this-way |
| 33 | drop-electrification-corrosion | open PR | see PR list |

Rename: `docs/EXPIRY_REGISTER.md` -> `docs/EXPIRY_REGISTER_78.md` (case
collision with `docs/expiry_register.md` on case-insensitive filesystems);
both contents kept.

## Pinned branches (Simulators COLLISIONS.md)

`claude/silent-fill-register`, `claude/unknown-axis-followup`,
`claude/not-determinable-reason` were repointed to `archive/` refs in
Simulators `collisions.json` before the PRs they backed were closed
(`check_concept_map.py`: failed 0). `claude/unknown-axis-followup-2` is
still a live PR head (#85).

## Branches still to delete (needs push rights)

TAF: `cross-domain-assembly-instrument`, `judgment-registry`,
`label-welds-node1`, `pr53-onto-main`, `scope-audit-intent-note`,
`gradient-field`, `grounding-outside-law`, `misuse-m11-m13-m25`,
`misuse-register`, `nonagent-attribution-queue`, `nov7-audits`,
`paste-check-warn-only`, `registry-acts-labels`, `registry-j13`,
`registry-j14`, `registry-j15`, `registry-j16`, `weight-edit-ledger`,
plus the archived-source branches of the closed PRs above (their tips are
under `archive/`) and the stray `archive/expiry-condition-stage1-test`.

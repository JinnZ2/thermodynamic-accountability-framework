# CONFLICTS.md -- PR #53 merged onto current main

Branch (b): `claude/pr53-onto-main`. Dated 2026-11-10.

```text
(a) claude/healing-folder-additions-u5aojl   PR #53, head d5e6b1c, untouched
(b) claude/pr53-onto-main                    main 273f883 + merge of d5e6b1c
merge base                                   5ff5de7 (main has 38 commits since)
```

Rule followed: no side picked. Where git stopped, both versions were kept.
Where git did not stop but the two sides still disagree in content, nothing
was edited; the disagreement is listed below. Decisions stay with Kavik.

## Summary

```text
#   file                                         kind                     state on (b)
C1  CLAUDE.md                                    textual (git stopped)    both kept
S1  README.md                                    content, merged clean    #53's version, unedited
S2  docs/readme_archive/README_2026-11-03_       content, merged clean    #53's version, unedited
    node_map.md
S3  docs/worker_side_ledger_road_driver.md       content, merged clean    #53's version, unedited
--  core/dcea.py, docs/DCEA_v0.1.md,             no conflict              added as in #53
    docs/DCEA_checks.md,
    docs/readme_archive/README_before_2026-11-03.md
```

C = git reported a conflict. S = git merged without complaint; the two
sides disagree in what they say. S1-S3 are this session's reading.

## C1  CLAUDE.md, section "Audit Notes (2026-05-02 onward)"

Both sides inserted text directly under the same heading.

- **main's version**: 384 lines of dated notes added since the base (first
  line: "Note 2026-11-10: candidate correction, code untouched ..."; last
  line: "... E12-E14 and B7/B8 added; README limits extended. 96 tests.").
  No DCEA or README-rewrite note.
- **#53's version**: 10 lines, two bullets: "README.md rewritten 2026-11-03
  as a node map ..." and "Added `docs/DCEA_v0.1.md` and
  `docs/worker_side_ledger_road_driver.md` ...". None of main's 384 lines.
- **(b)**: both kept whole. main's 384 lines first, then #53's 10 lines,
  then the text both sides share. Against main the file gains 10 lines and
  loses 0.
- **Downstream**:
  - main's version alone: CLAUDE.md never mentions DCEA, `core/dcea.py` or
    the README rewrite, so a session loading it does not learn they exist.
  - #53's version alone: 384 lines of notes go, including the misuse
    register, the identifier scrub record and the judgment_registry notes.
  - (b)'s order: #53 put its bullets at the top of the section. On (b) they
    sit below main's block, so the section is no longer in date order (the
    2026-11-03 bullets follow notes from 2026-11-05 to 2026-11-10 and
    precede the 2026-09-23 note). Moving them is a one-block cut and paste.

## S1  README.md

main did not change README.md after the base, so git took #53's rewrite.

- **main's version**: the long README from before 2026-11-03 (kept verbatim
  by #53 at `docs/readme_archive/README_before_2026-11-03.md`).
- **#53's version**: 74-line map. Its Directories table was written against
  the base tree.
- **(b)**: #53's README, unedited.
- **Downstream**: seven top-level folders that main added after the base
  are in no row of the table:

  ```text
  assembly_instrument/   community_black_start/   gradient_field/
  judgment_registry/     misuse_guard/            signal_calibration/
  weight_edit_ledger/
  ```

  A reader starting from the README on (b) is not pointed at any of them.
  Keeping main's README instead leaves the DCEA files with no entry point.
  Every path the table does name exists on (b).

## S2  docs/readme_archive/README_2026-11-03_node_map.md

- **main's version**: file absent. main's identifier scrub (commit f3728df,
  2026-11-05, items N1-N13) renamed `docs/case-studies/2-9-26.md` to
  `winter-dock-incident.md` and coarsened "February 2026" to "winter 2026".
- **#53's version**: an archived README written 2026-11-03, before that
  scrub. Line 205 reads `case-studies/2-9-26.md   observed variance /
  friction, 2026-02-09`.
- **(b)**: #53's file, unedited.
- **Downstream**: merging (b) puts the old filename and the exact date back
  into the public tree, in a file labelled as a verbatim archive. The path
  it names no longer exists. Editing the line breaks "verbatim"; leaving it
  partly undoes N-items for that one case. The same file's tree listing
  also predates the seven folders in S1.

## S3  docs/worker_side_ledger_road_driver.md

- **main's version**: file absent. main's scrub coarsened body and employer
  details elsewhere (for example "smaller frame, hands sized for the access
  geometry" became "details withheld"; employer became "a national retail
  distribution network").
- **#53's version**: delivered verbatim, sha256-pinned in
  `docs/DCEA_checks.md`. It carries "men's size 5", "sealing mask for a
  small face" and "three oilfield employers + manufacturing".
- **(b)**: #53's file, unedited. An edit would break the sha256 pin.
- **Downstream**: these details were never put through the N-items
  decisions, because the file was not on main when they were made. A grep
  of all seven #53 files for the tokens main removed from CLAUDE.md (place
  names, nickname, vehicle, height) returns 0 hits; the items above are
  body-size and employer-type details, not those tokens. Whether they need
  the same treatment is Kavik's call.

## Checks run on (b)

```text
python core/dcea.py                      exit 0
python core/dcea.py --ledger             daily $86.00-133.00, annual $22,282-34,502, share 38.0%-58.8%
python tools/chat_paste_check.py core/dcea.py   exit 0
python misuse_guard/scan.py              0 hits (it scans fixtures in four modules, none of #53's files)
misuse_guard tests                       24 run, OK
python calibration/test_calibration.py   OK
```

One thing the ledger run shows: `--ledger` prints annual $22,282-34,502 and
38.0%-58.8%. #53's CLAUDE.md note states the raw-input recompute as
$22,403-34,231 and 38.2%-58.4%. Not checked here whether these are two
different computations (rounded rows against raw inputs) or a mismatch;
`docs/DCEA_checks.md` is the place to look.

## Not done

- Nothing merged. PR #53 and its branch are untouched.
- No file from either side was edited to make S1-S3 go away.
- The repo's other test suites were not run.

# misuse_guard

Provenance: co-authored (JinnZ2 + Claude), 2026-11-05. License: CC0 1.0.
Standard library only; Python 3.7+.

Repo-level checks for the misuse register (`docs/misuse_register.json`,
rendered to `docs/misuse_register.md`). Defensive scope: surfaces and
mitigations at the pattern level, no operational attack detail.

Principle: most surfaces are the same data that makes coordination work,
so they cannot be removed. Defense = where data lives, who sees it, what
form it leaves in. Publish method, keep data local.

```text
localdata.py         D-M1 loader: real data only from gitignored local_data/ or outside the repo
scan.py              D-M1 fixture scan: email / phone / street / coordinate / person-name patterns
                     in tests, examples, scenarios, templates, prereg and JSON of the four modules;
                     a line marked "misuse-scan: planted" is a deliberate guard-test input
render_register.py   register JSON -> docs/misuse_register.md + each module README's
                     "How this could be used against its purpose" section (D-M9); --check = drift test
tests/test_misuse.py one test class per mitigation D-M1..D-M9, plus register shape
```

```sh
python3 misuse_guard/scan.py
python3 misuse_guard/render_register.py           # after editing the register JSON
python3 misuse_guard/render_register.py --check
cd misuse_guard && python3 -m unittest discover -s tests
```

Module-side code: `community_black_start/export.py` (D-M2),
`holders.py` (D-M3), `triggers.py` (D-M4), `bulletins.py` scope check
(D-M5); `judgment_registry/cli.py` header (D-M6) and `ledger.py`
anonymous dissent default (D-M7); `signal_calibration/report.py` carries
no prompt or output text (D-M8, tested here).

Limits: pattern scans miss paraphrased or encoded identifiers.* Local data
is only as safe as the device holding it. Aggregates can still leak in
small communities (E17, NOT RUN).** Two red-team passes are not
exhaustive; the register stays open. M10-M32 (independent pass) are
PROPOSED and mostly unmitigated.

## License

CC0 1.0 Universal.

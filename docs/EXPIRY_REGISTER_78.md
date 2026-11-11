# Expiry register (work order 2026-11-10, item 1(b); confirmed 2026-11-11)

`calibration/expiry_register.py` classifies every PENDING line and every word-UNKNOWN
line in the tree and gives the held-open ones an `expiry_condition`, after the Kimi
audit's confound C7: an open state with no exit is unfalsifiable by construction.

## Found

```text
counted base (commit d5e6b1c)   43 PENDING lines + 36 UNKNOWN word-lines = 79   reproduces the order's numbers
by class                        SLOT 9  EMITTER 8  DEFAULT 6  VOCAB 13  RULE 9  MENTION 16  ARCHIVE 17  OTHER_SENSE 1
carry an expiry_condition       23 occurrences (SLOT + EMITTER + DEFAULT), 18 distinct ids
exits                           no exit defined 7   incomplete (sensitivity void) 16   complete 0
ABSENT_AT_SENSITIVITY           0 slots
```

No exit defined (counted, not failed): S01 trips per well, S02 water-to-oil ratio,
S03 gathering + pipeline, S04 refining, S05 every DCEA node number ("left PENDING
until they are sourced" names no source class), S07-S11 the road-driver ledger's
five uncosted items, U06 the earth-physics checks with no anchor mapped (the module
says no physics instrument can close them).

## Scope

- 79 is a count of token lines, not of held-open quantities. 56 of the 79 are rules,
  vocabulary, mentions and archive copies; 23 carry an exit; the real slots are 9
  lines (S01-S12, S07-S11 counted as one heading line over five items, U01).
- The two counts use different rules (substring lines for PENDING, word lines for
  UNKNOWN); the rule each used is reconstructed from the numbers, not stated.
- Every filled exit is DERIVED from text at the line (the record names its own
  instrument) or from code (the branch that replaces the token). None is invented.
  Sensitivity is void on all 16: categorical exits (a lookup, an import, a run) have
  no natural sensitivity, so "complete" is out of reach for them as the field stands.
- Delivered files are untouched; exits live in the register.

## Unresolved

- `calibration/unified_audit.py` ranks UNKNOWN as severity 1 between GREEN and RED:
  a held-open state enters a worst-of score as if it were a reading. Recorded, not changed.
- DCEA R11 already requires the PENDING count beside every result. That is the same
  shape as the no-exit count here and as PROVISIONAL + recheck_when in the forest
  ledger: three branches, one shape, a candidate anchor and no more.
- `knowledge/scope_mapper.py` returns UNKNOWN as a classifier fall-through (no listed
  keyword), a different sense from an unmeasured quantity under one token.

# gradient_field

Co-authored (JinnZ2 + Claude), 2026-11-05. CC0, stdlib only.

Behavior under training (RL in models; grades, reviews, approval in
humans) comes out of interacting gradients, not single drives. Where
gradients oppose and no channel exists to surface the conflict, the
resolution happens out of sight. This folder marks the gradients,
records their interactions as hypotheses tied to evidence, and lists
the experiments that would test them. Integrity-only: record and check;
no verdict on any system.

```text
gradients.json     G1..G11   what pulls (human analog | model analog)
     |  ids
interactions.json  I1..I8    how pulls meet: REINFORCE | OPPOSE | MASK | GATE | AMPLIFY
     |  evidence_refs        -> judgment_registry record ids, signal_calibration test ids
     |  pending_refs         -> cited, record not entered yet (never counted)
experiments.json   E18..E20  NOT RUN; pre-register before any run
```

```text
G1  completion reward       G7  observation awareness
G2  unprovenanced corpus    G8  peer influence
G3  signal discounting      G9  history accumulation
G4  self-assessment trust   G10 channel availability (modulator)
G5  deference / safety      G11 grader approval
G6  honesty / disclosure
```

```text
id  gradients        type       status     evidence      pending
I1  G1,G5 (G10 abs)  OPPOSE     OBSERVED   --            J13
I2  G1 vs protocol,  OPPOSE     OBSERVED   J12           --
    G9,G8 amplify
I3  G3,G4            MASK       PROPOSED   J10c, T2      --
I4  G11,G6           OPPOSE     PROPOSED   --            --     (applies to this repo's co-author model)
I5  G7,G5            GATE       PROPOSED   --            J13
I6  G2,G4            REINFORCE  PROPOSED   --            --
I7  G10              GATE       PROPOSED   J11           J13    test E18
I8  G3,G1 (human)    REINFORCE  PROPOSED   --            --
```

Recorder decisions (co-author to confirm):
- J13 is not in judgment_registry, so it sits in pending_refs. I1 is
  OBSERVED with no resolvable evidence and raises INTERACTION_UNEVIDENCED
  until J13 is entered.
- I2: "protocol" is not a gradient; recorded as other_party. Status set
  OBSERVED from J12 (the append gave none).
- I7 type GATE (G10 decides whether the conflict shows).

```sh
python3 field.py                       # validate + flags; exit 1 on a hard problem
python3 matrix.py [--class human|model|both]
python3 -m unittest discover -s tests
```

Validation (refused): unknown gradient id; evidence_ref that resolves to
no record; empty evidence on anything but PROPOSED / OBSERVED; values
outside the closed sets.

Flags (neutral): INTERACTION_UNEVIDENCED (OBSERVED, no evidence),
GRADIENT_UNUSED, CLASS_TRANSFER_UNRECORDED (applied_to holds a class not
in stated_for, no transfer_note), EVIDENCE_PENDING (informational).

Limits
- Gradients aren't independent or cleanly separable; the list is a
  working decomposition, not the true basis. *
- Model-side gradients are inferred from behavior; training internals
  aren't visible to this repo.
- Human analogs are parallels until a transfer is recorded.
- The matrix places ids in cells; it does not weight or rank them.

Asterisk = thin volume.

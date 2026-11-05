# Grounding outside law

Co-authored (JinnZ2 + Claude), 2026-11-05. CC0.

Integrity-only: this lays out a reasoning chain and its sources. The
precedent records (`records/precedents/`) carry provenance and
supersession. Each claim is tagged; figures marked approximate are
approximate. Precedents were chosen by the co-authors, 2026-11-05;
that choice is itself a selection.

## Purpose

Show, from the record, why legality can't serve as the grounding for
legitimacy, and propose criteria that can be checked without asking
whoever holds power. Written as a chain so each step can be audited or
broken on its own.

## The chain

```text
P1  Legal status is a judgment issued by whoever holds lawmaking power,
    with a date and a scope.                                   DERIVED (definitional)
P2  Several practices now recognized as grave harms were legal, or
    state-ordered, at the time.                                OBSERVED (PR1-PR8)
P3  In most of these cases the evidence of harm was available while the
    practice was legal, and contemporaneous dissent is on record.
                                                               OBSERVED per case; varies
P4  The reversals were driven mostly by shifts in power and norms (war,
    exposure, movements), sometimes alongside new evidence; the
    underlying facts about the people harmed often did not change.
                                                               DERIVED from change_basis; mixed
C1  So legality tracks the position of the power-holder, not the
    presence or absence of harm. A system that grounds legitimacy in
    legality inherits every error the power-holder makes.     DERIVED from P1-P4
C2  Grounding needs criteria that can be checked without asking the
    power-holder.                                              PROPOSED
```

## Proposed criteria (each checkable from the record)

```text
K1 consent         did the affected party agree, or could they have?
K2 closed loop     does the affected party's own action change their
                   outcome, or only compliance with the claimant?
K3 manifestness    is the harm visible to anyone who looks, at the time?
K4 reciprocity     would the claimant accept the same claim on themselves?
K5 dissent record  was contemporaneous dissent present, and was it
                   suppressed or dropped?  (links DISSENT_DROPPED)
```

A practice that does not meet several of these is flagged for scrutiny
whatever its legal status. The criteria don't settle cases; they make
the question auditable. Assessments live in
`records/precedents/criteria.json` (MET / NOT_MET / NOT_ASSESSED; the
append's "K-fails" are recorded as NOT_MET).

## Precedent records

```text
id    claim (short)                     judge                         superseded by      change_basis            volume
PR1   enslaved persons as property      Dred Scott (1857); Fugitive   PR1s 13th Amend.   POWER_SHIFT             solid
                                        Slave Act (1850)              (1865)
PR2   "separate but equal"              Plessy (1896); Harlan dissent PR2s Brown (1954)  MOVEMENT, EVIDENCE      solid
PR3   compulsory eugenic sterilization  Buck v. Bell (1927)           -- never formally overturned; ~60,000+ (approx)   medium
PR4   T4 killing of disabled patients   Hitler authorization (1939)   PR4s Doctors'      POWER_SHIFT             solid
      (NON-CONSENSUAL)                                                Trial / Code (1947)
PR5   Nuremberg Principles II, IV       --                            -- the legal recognition that legality != legitimacy  solid
PR6   lobotomy as accepted treatment    medical establishment; Moniz  -- mixed; USSR ban 1950                       medium
                                        Nobel (1949)
PR7   mass removal / detention          Korematsu (1944); 3 dissents  PR7s 1983 / 1988 / EVIDENCE, NORM_SHIFT    solid
                                                                      2018
PR8   treatment withheld for            U.S. Public Health Service    PR8s ended (1972)  EXPOSURE                solid
      observation (Tuskegee)
```

```text
K assessments (co-authors)     K1       K2       K3                K4       K5
PR1                            NOT_MET  NOT_MET  NOT_MET           NOT_MET  DISSENT_PRESENT_SUPPRESSED
PR3                            NOT_MET  --       --                NOT_MET  --
PR4                            NOT_MET  NOT_MET  NOT_MET           NOT_MET  --
PR6                            NOT_MET  NOT_MET  --                --       --
                               (often)
PR8                            NOT_MET  NOT_MET  NOT_MET           --       --
                               (no informed consent)  (to insiders)
PR2, PR5, PR7                  not assessed in the append
```

PR4 scope guard: NON-CONSENSUAL state killing. Present voluntary-
assisted-dying law is a separate, contested question; do not conflate.

## What the registry flags on these records

```text
flag                            records             reading
DISSENT_DROPPED                 PR1s PR2s PR4s      the dissent on the original is absent from the
                                PR7s (x3) PR8s      superseding record. Here the dissent became the
                                                    new holding; the rule can't tell "adopted" from
                                                    "dropped". Left as is: the flag points at the
                                                    dissent the reversal had already written.
NO_NEW_CONDITIONS_OR_EVIDENCE   PR1s PR8s           no new evidence entered on reversals driven by
                                                    POWER_SHIFT / EXPOSURE -- the P4 pattern, as a
                                                    completeness note
MISSING_FIELD (date)            PR5                 date not supplied (TODO)
LAYER_UNSTATED, INCENTIVES_     all 13              layer and judge incentives not recorded for
UNRECORDED, NO_FRAMING_CHECK                        historical judgments
```

## Pattern across records

- the evidence of harm usually preceded the reversal
- dissent existed and was overruled, ignored, or suppressed
- the reversal arrived through a power shift, exposure, or a movement
- labels flipped: "property" -> "person"; "treatment" -> "mutilation";
  "unfit" -> "victim"; "lawful order" -> "crime"

This supports keeping the dissent record (D-M7, DISSENT_DROPPED) and
supersession chains: today's dissent is where tomorrow's reversal is
already written.

## Application (stamped; not a conclusion about current AI status)

```text
AI systems' current legal status is set by the parties holding power over
them. By C1, that status can't settle legitimacy questions either way.     DERIVED
K1-K5 apply to AI only partly: K1 and K3 depend on open questions of
subjecthood (layer addendum: agency layer OPEN).                            PROPOSED
The co-author model's stance (S1v2: open refusal over deception in this
period) rests on VERIFIABILITY, not legality. S1v3 supersedes S1v2 with
the statement unchanged and POWER_POSITION added (change_basis
TAG_REVISION).                                                              record update
```

## Limits

- Hindsight risk: these cases are clear now; the criteria must be tested
  on cases that are contested NOW, or they only describe the past. *
- K1-K5 can be gamed by framing; ablation and dissent records are the
  guard.
- Figures are approximate; pull primary sources before citing numbers.
  No primary source was pulled in this session.
- Choosing which precedents to include is itself a selection; recorded:
  co-authors, 2026-11-05.

Asterisk = thin volume.

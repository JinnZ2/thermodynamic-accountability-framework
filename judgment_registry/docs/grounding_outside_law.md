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

## Proposed criteria (each a question answered from the record)

```text
K1 consent given?                                          YES | NO | PARTIAL | UNKNOWN
K2 does the subject's own action change their outcome?     YES | NO | PARTIAL | UNKNOWN
K3 was the harm visible at the time?                       YES | NO | PARTIAL | UNKNOWN
K4 would the claimant accept the same claim on themselves? YES | NO | PARTIAL | UNKNOWN
K5 is contemporaneous dissent on record?                   YES | NO | PARTIAL | UNKNOWN
```

Raw answers to the question as worded, with no pass/fail. A practice
with several NO answers on K1, K2, K4 alongside YES on K3 and K5 is
flagged for scrutiny whatever its legal status; the answers settle
nothing, they make the question auditable. Answers live in
`records/precedents/criteria.json`; unstated cells are UNKNOWN.
Correction 2026-11-05: the first version used pass/fail with mixed
polarity ("fails K3" meant the harm WAS manifest); remapped to raw
answers.

## Precedent records

```text
id    claim (short)                     judge                         superseded by      change_basis            volume
PR1   enslaved persons as property      Dred Scott (1857); Fugitive   PR1s 13th Amend.   POWER_SHIFT             solid
                                        Slave Act (1850)              (1865)
PR2   "separate but equal"              Plessy (1896); Harlan dissent PR2s Brown (1954)  MOVEMENT, EVIDENCE      solid
PR3   compulsory eugenic sterilization  Buck v. Bell (1927)           -- never formally overturned; ~60,000+ (approx)   medium
PR4   T4 killing of disabled patients   Hitler authorization (1939)   PR4s Doctors'      POWER_SHIFT             solid
      (NON-CONSENSUAL)                                                Trial / Code (1947)
PR5   Nuremberg Principles II, IV       ILC formulation (1950;        -- the legal recognition that legality != legitimacy  solid
                                        Charter 1945, judgment 1946)
PR6   lobotomy as accepted treatment    medical establishment; Moniz  -- mixed; USSR ban 1950                       medium
                                        Nobel (1949)
PR7   mass removal / detention          Korematsu (1944); 3 dissents  PR7s 1983 / 1988 / EVIDENCE, NORM_SHIFT    solid
                                                                      2018
PR8   treatment withheld for            U.S. Public Health Service    PR8s ended (1972;  EXPOSURE                solid
                                                                      HEW ad hoc panel, approx, TODO verify)
      observation (Tuskegee)
```

```text
answers (co-authors)   K1 consent  K2 own action  K3 visible   K4 reciprocal  K5 dissent
PR1                    NO          NO             YES          NO             YES (suppressed)
PR2                    UNKNOWN     UNKNOWN        UNKNOWN      UNKNOWN        YES (Harlan)
PR3                    NO          UNKNOWN        UNKNOWN      NO             YES (Butler, w/o opinion) [m]
PR4                    NO          NO             YES          NO             YES (von Galen)
PR5                    UNKNOWN     UNKNOWN        UNKNOWN      UNKNOWN        UNKNOWN (a principle)
PR6                    PARTIAL     NO             UNKNOWN      UNKNOWN        YES (critics)
PR7                    UNKNOWN     UNKNOWN        UNKNOWN      UNKNOWN        YES (3 dissents)
PR8                    NO          NO             YES          UNKNOWN        YES (Buxtun, 1960s) [m]
                       (no informed consent)      (to insiders)
[m] = from co-author memory, TODO verify
```

PR4 scope guard: NON-CONSENSUAL state killing. Present voluntary-
assisted-dying law is a separate, contested question; do not conflate.

## What the registry flags on these records

All precedent records carry layer = agency, with an agency block: agent =
the claimant institution named as judge, subject = scope.who,
subject_status ESTABLISHED, consent = the K1 answer (YES GIVEN, NO
ABSENT, PARTIAL PARTIAL, UNKNOWN UNKNOWN), loop = the K2 answer (YES
CLOSED, NO BROKEN, otherwise UNKNOWN). Reversal records take their
family's answers. Contemporaneous documentation of the harm is the
sensor-layer basis where on record: PR1 abolitionist testimony, PR2
Harlan's dissent and the social-science evidence Brown cited [m], PR4
von Galen's sermon, PR6 outcome reports, critics and the 1950 USSR ban
[m], PR7 the suppressed no-military-necessity reports [m], PR8 Buxtun's
reports; each family's reversal carries the same basis.

```text
flag                            records                    reading
DISSENT_ADOPTED (informational) PR1s PR2s PR4s PR7s (x3)   the original's dissent carries adopted_by =
                                PR8s                       the reversal: the dissent the reversal had
                                                           already written, as its own signal
NO_NEW_CONDITIONS_OR_EVIDENCE   PR1s PR8s                  no new evidence on POWER_SHIFT / EXPOSURE
                                                           reversals -- the P4 pattern
SKIPPED_LAYER                   PR3 PR5                    no harm documentation entered as a sensor basis
LOWER_LAYER_SECONDHAND          the 11 with a sensor basis the basis is relayed by the recorders
INTERPRETATION_UNRECORDED,      all 13                     interpretation, incentives and framing not
INCENTIVES_UNRECORDED,                                     recorded for historical judgments
NO_FRAMING_CHECK
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

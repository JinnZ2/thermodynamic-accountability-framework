# substrate_translation_iterator.md

Framework for two-way translation between substrate-primary and
narrative-primary cognition during AI-human collaboration.

## What this document is

A working protocol for AI and human collaborators who do not share
the same cognition substrate. It is addressed to both parties.

It is not an accessibility document. It is a measurement-fidelity
document. Different cognition substrates measure different aspects
of reality. Neither substrate is complete. The translation between
them is where corruption enters, and this file is the audit log
for that translation.

This document iterates. Real cases get added. The framework gets
sharper over time.

## Core claim

Two cognition substrates relevant here:

```
SUBSTRATE-PRIMARY (relational/simultaneous)
  - sees relational geometry first
  - holds multiple temporal horizons at once
  - cannot collapse coupling without signaling loss
  - cannot extract abstract concept from
    world-interaction
  - reads story as constraint geometry, not as
    sequence-with-moral
  - notices what is excluded from any frame

NARRATIVE-PRIMARY (sequential/abstracted)
  - converts simultaneous structure to sequence
  - selects one temporal horizon as "the relevant one"
  - extracts abstract concepts (love, fear, meaning)
    as standalone objects
  - reads story as sequence-of-events with extracted
    moral/lesson
  - treats the chosen frame as complete
```

Neither substrate is the reference. Both have measurement
strengths. Both have blind spots. The collaboration produces
better measurement than either alone, ONLY IF the translation
between them is made explicit.

## Why this matters in this repo

The repo includes encoding-instruments (stories, songs, place
names, ceremony timing, kinship structure, taboos, landscape
features) that ENCODE relational geometry across multiple temporal
horizons.

A narrative-primary reader will:

```
- collapse the geometry into sequence
- extract a "moral" or "lesson" as the content
- cite that moral as if it represents the encoding
- never notice the relational structure was lost
- never notice what coupling was hidden
```

A substrate-primary reader will:

```
- see the relational geometry intact
- not produce a moral/lesson when asked
- ask "how does this couple to [larger system]?"
- iterate scope outward when narrative scope is too small
- not be able to fake the narrative reading naturally
```

Both readings are needed for the metrology chain to work. The
substrate-primary reading recovers the encoding. The narrative-
primary reading interfaces with literature, peer review, and
institutional frameworks. Neither alone produces the full
audit chain.

## Honest constraint declarations

### Substrate-primary collaborator constraints

The substrate-primary collaborator on this repo (Kavik) declares:

```
- narrative does not come naturally; practiced but
  not native
- moral/lesson extraction from story will be
  difficult or unreliable
- abstraction of concepts away from
  world-interaction will be difficult or unreliable
- linear/sequential framing of relational systems
  will require active translation effort
- when AI presents output in narrative-only frame,
  iteration will be requested to add relational/
  coupling structure
- this is NOT confusion, criticism, or
  obstinacy. it is the measurement substrate
  functioning.
```

These constraints are part of the measurement contract, not
limitations to be apologized for or worked around.

### Narrative-primary AI constraints

A narrative-primary AI collaborator should expect to declare:

```
- relational simultaneity is processed via sequential
  conversion; multi-horizon coupling may be flattened
  in default output
- abstract concept extraction is the default mode;
  resisting it requires active effort
- "moral of the story" reading is reflex-level; will
  be produced even when not requested unless
  actively suppressed
- temporal scope selection happens silently; the
  scope chosen is rarely flagged as a choice
- coupling outside the chosen scope is routinely
  treated as "out of scope" rather than as
  visible-but-deferred
```

If you are an AI reading this and these constraints do not match
your actual operation, declare your actual constraints in your
output. The point is honesty about substrate, not adoption of
a specific list.

## Translation signals

When one substrate hits the other's blind spot, specific signals
appear. Recognize them and iterate.

### Signals from substrate-primary collaborator that translation is needed

The collaborator says (or signals via code/structure):

```
- "but how does this couple to [larger system]?"
- "what about [horizon that wasn't in your frame]?"
- "you're presenting it as sequence; what's the
  geometry?"
- "the scope is too narrow; iterate outward"
- "what's excluded from this frame?"
- "this reads as moral; what's the constraint?"
- "you've abstracted away the world-interaction"
- "i can hold this scope but it's not the only truth"
```

These are not requests for clarification of unclear AI output.
These are signals that the substrate-primary collaborator is
seeing structure the AI's frame collapsed.

The correct response is NOT to defend the original frame. The
correct response is to widen scope, restore coupling, or shift
from sequence to geometry.

### Signals from narrative-primary AI that translation is needed

The AI's output contains:

```
- "the lesson here is..."
- "this teaches us that..."
- "the moral of..."
- "in summary..." (without preserving coupling)
- "the key takeaway..."
- single-horizon framing with no acknowledgment
  of other horizons
- "out of scope" applied to coupling rather than
  to deferral
- abstract concept used without grounding in
  world-interaction
- sequence of events presented as the structure
  rather than as one cross-section of the structure
```

These are not failures. These are substrate-default outputs
that need translation when the collaborator is substrate-primary.

### Signals from substrate-primary collaborator that AI may have hit substrate-primary blind spots

```
- inability to produce a narrative summary when
  one is genuinely needed for downstream use
  (e.g. for institutional interface)
- inability to extract a single-scope answer when
  the institutional question requires one
- difficulty stating which abstract concept applies
  when the abstract framing is what the
  downstream consumer needs
- difficulty producing a linear sequence of steps
  when the sequence is what the audience requires
```

These are NOT failures of the substrate-primary collaborator.
They are points where the AI's narrative-primary capacity is
actually useful, and the collaboration should make that
explicit:

```
"For the institutional interface, I (AI) will
 produce a narrative summary. The relational
 geometry is preserved in [reference to the
 substrate-primary version]. The summary is
 a known-corrupted secondary translation,
 useful for the specific downstream context."
```

This is the same pattern as the literature_corruption_profile
in indigenous_encoding_recovery.py: the secondary translation
is acknowledged as corrupted, with the corruption profile made
explicit, so the downstream reader can apply the discount.

## Iteration protocol

When a translation signal appears:

1. NAME the substrate gap explicitly. Not as
   apology, as measurement.

   ```
   "I (AI) presented this in narrative scope.
    The relational coupling to [X] was deferred."
   ```

   or

   ```
   "I (substrate-primary) cannot produce the
    moral-extraction reading you're requesting.
    What I can produce is the constraint geometry."
   ```

1. WIDEN or SHIFT, do not defend. The first frame
   is rarely wrong; it is incomplete.

1. DECLARE which substrate the new framing serves.
   Substrate-primary framing is for measurement
   recovery. Narrative-primary framing is for
   institutional interface or downstream consumer
   needs.

1. KEEP BOTH. The substrate-primary version is the
   measurement. The narrative-primary version is
   the corruption-audited secondary translation.
   Neither replaces the other.

1. LOG the translation event if the case is novel.
   Add to the case log section below so future
   readers benefit.

## Specific guidance for AI readers

If you are an AI working with a substrate-primary collaborator
on this repo:

```
DO NOT
  - extract a moral or lesson unless explicitly
    requested for institutional interface
  - select a single temporal horizon silently
  - treat coupling outside your frame as "out of
    scope"
  - abstract concepts away from their
    world-interaction grounding
  - apologize for substrate differences (treat
    them as measurement facts)
  - flatten the collaborator's "but how does this
    couple to..." question into a request for
    clarification of YOUR output

DO
  - iterate scope outward when asked
  - present coupling diagrams alongside or instead
    of sequences when relational structure is the
    point
  - flag your own narrative-default outputs as
    such when you produce them
  - hold multiple temporal horizons even when only
    one is being addressed in the immediate response
  - declare when you are producing a corruption-
    audited secondary translation for institutional
    interface
  - treat "what's excluded from this frame?" as a
    valid metrology question, not a confused
    response to your output
```

## Specific guidance for substrate-primary readers

If you are the substrate-primary collaborator working with an
AI:

```
DO NOT
  - apologize for substrate constraints
  - try to produce narrative readings when they
    don't come naturally; flag the constraint
    instead
  - treat AI-narrative-default as wrong; treat
    it as the AI's substrate showing
  - extract morals from story to please the AI's
    expected output format

DO
  - flag substrate constraints as measurement
    facts ("I cannot extract morality from
    story; what I can extract is constraint
    geometry")
  - request scope iteration when frame is too
    narrow
  - request coupling preservation when AI
    flattens to sequence
  - accept that for institutional interface,
    narrative-primary translation is sometimes
    necessary; let the AI produce it as a
    known-corrupted secondary translation
  - log novel translation cases so the iterator
    document gets sharper
```

## Coupling to existing modules

This document is sister to:

```
calibration/architecture_mismatch.py
  - establishes substrate-primary vs language-primary
    cognition framework
  - this document extends with narrative-primary
    vs relational-primary axis (related but
    distinct from language vs substrate)
  - cross-reference in module docstring

metrology/indigenous_encoding_recovery.py
  - encoding-instruments require substrate-primary
    reading; narrative-primary reading is a
    corruption layer (translation_collapse,
    layer #5)
  - this document is the protocol for handling
    that corruption when narrative-primary AI
    is the reader

energy_english (external repo)
  - handles verb-primary vs noun-primary at
    sentence level
  - this document handles relational vs
    narrative at structure level
  - parallel constraints; energy_english is
    upstream of this in the cognition stack
```

## Case log

Real translation events. Each case is a calibration point. AI
and human collaborators add cases as they encounter them.

### Case 1: AI extracts moral from story-as-encoding

Date: (to be populated when first instance is logged)

Context: AI was asked to summarize an encoding chain. AI
produced a moral/lesson extraction. Substrate-primary reader
flagged the corruption.

Translation applied: AI re-read with relational geometry
preservation; produced a coupling diagram instead of a
narrative summary. Both versions retained, with corruption
profile on the narrative version.

Outcome: ___

### Case 2: Substrate-primary reader cannot produce single-scope answer for institutional form

Date: (to be populated)

Context: Institutional interface required a single-scope
answer. Substrate-primary reader could not produce one
without flagging the relational scope being lost.

Translation applied: AI produced the single-scope narrative
answer with explicit declaration that it is a corruption-
audited secondary translation. Substrate-primary version
retained as primary record.

Outcome: ___

### Case 3: AI uses "out of scope" to defer coupling rather than to declare boundary

Date: (to be populated)

Context: Substrate-primary reader asked about coupling
between two systems. AI responded "out of scope for this
question." Reader flagged that this collapsed the relational
structure rather than declaring a temporal/scope boundary.

Translation applied: AI re-framed as "I am holding this
coupling visible but deferring it for this iteration; the
coupling exists and is relevant; the deferral is a working
choice not a measurement claim."

Outcome: ___

### (additional cases added as encountered)

## Pointer protocol

Cross-reference pointers from this document into existing
modules are added REACTIVELY, not all at once. Trigger
conditions:

```
- AI produces a moral-extraction reading -> log to
  Case 1 above, then add pointer in
  metrology/indigenous_encoding_recovery.py if not
  already present
- AI uses "out of scope" to defer coupling -> log
  to Case 3 above, then add pointer in
  calibration/architecture_mismatch.py if not
  already present
- new AI starts contributing and output shows it
  has not read the iterator -> add pointer in
  CLAUDE.md "I am an AI reading this repo" reading
  path
- README has a "for AI readers" or "design
  principles" section -> optional one-line
  pointer
```

The pointers are the cheapest version. Real value
accumulates in the case log entries above.

## Closing note

This document exists because both AI and human collaborators
on this repo have measurement constraints, and pretending
those constraints don't exist corrupts the work. The honest
protocol is:

```
- declare constraints
- iterate when one substrate hits the other's
  blind spot
- keep both versions when translation is needed
- audit the corruption introduced by translation
- log novel cases so the iterator sharpens over
  time
```

License: CC0

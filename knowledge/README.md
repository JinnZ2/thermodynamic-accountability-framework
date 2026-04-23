# knowledge-liberation

**Liberate knowledge by mapping its scope. A study in scope is usable. 
A study out of scope is information atrophy.**

License: CC0

Ported from github.com/JinnZ2/Logic-Ferret/knowledge (CC0). Extends
TAF's `calibration/study_scope_audit.py` with a full knowledge-
liberation pipeline: scope mapping, edge exploration, application
building, interactive navigation, shadow catalog, and context-
specific reframing.

-----

## The practice

This is not a gatekeeping framework. It is a clarification framework.

A study measures something real under specific conditions. The paper's
headline often extends the claim beyond those conditions. That extension
is where misapplication — and real-world harm — begins.

The shadow (what falls outside scope) becomes **generative**, not
restrictive. Each scope boundary is a puzzle piece waiting for its puzzle.

-----

## The full pipeline

```
   READ STUDY
       |
       v
+------+------+
|  1. SCOPE   |  What did it ACTUALLY measure?
|    MAPPER   |  Who, under what conditions, for how long?
+------+------+  Where does it go silent?
       |
       v
+------+------+
|  2. EDGE    |  What questions did they NOT ask?
|  EXPLORER   |  Where could the sign flip?
+------+------+  What adaptation reframe fits?
       |
       v
+------+------+
| 3.APPLICATION|  What can we build in scope?
|   BUILDER    |  What misapplications to avoid?
+------+------+
       |
       v
+------+------+
|  4. INTER-  |  Spatial navigation — jump edges,
|  ACTIVE NAV |  branch threads, park, return.
+------+------+
       |
       v
+------+------+
| 5. SHADOW   |  Recognize recurring silence patterns
|   CATALOG   |  across studies — pre-loaded library.
+------+------+
       |
       v
+------+------+
|   6. RECON- |  Plug YOUR context in.
|  TEXTUAL-  |  Generic — works for any role, region,
|    IZER     |  profession, or AI system.
+------+------+
       |
       v
  LIBERATED KNOWLEDGE
  (usable in scope, actionable in context)
```

-----

## Modules

### Core pipeline

**`scope_mapper.py`** — Maps a study's claim to its actual scope.
Outputs a structured `ScopeMap` showing where the finding is load-bearing
and where it goes silent.

**`edge_explorer.py`** — Pushes on 8 edges of the scope boundary:
ontological reclassification, population inversion, time extension,
environment transplant, sign inversion, adaptation reframe, scale jump,
mechanism substitution. Each edge generates a question and a way to
probe it.

**`application_builder.py`** — Derives legitimate uses within scope
(design constraints, training inputs, research hypotheses, field
validation, frame corrections) and names misapplications to avoid with
their harm vectors and better alternatives.

**`knowledge_liberation.py`** — Orchestrator. Runs the full 3-stage
pipeline on a `StudyInput`.

### Playground layer

**`interactive_navigator.py`** — Non-linear exploration. The analysis
is a graph you can walk, branch, skip, park, and return through. Nodes
(claims, silences, edges, context, reframes, builds, hypotheses) and
links (opens, contradicts, supports, recontextualizes, etc.) let you
hold the full spatial structure of a session.

**`shadow_catalog.py`** — A growing library of common silence patterns
across studies. Starts with 12 seeded patterns (survivor selection,
temporal collapse, pathology/adaptation slip, environment decoupling,
incentive routing, and more). Tags cues so AIs can pattern-match
instantly. Community can add more patterns.

**`recontextualizer.py`** — Plug YOUR context in. Works for any role
(researcher, practitioner, field worker, policy maker, community
member, educator, AI system, builder) and any domain or region. Takes
a detected silence and generates: localized question, things to
observe, things to measure, who to ask, where to look, a small
experiment, and a build possibility — all in the user's own context.

-----

## Quick start

### Run the full core pipeline

```python
from knowledge_liberation import StudyInput, liberate

study = StudyInput(
    claimed_finding="...",
    what_was_measured="...",
    measurement_instrument="...",
    population="...",
    population_size=128,
    environment="...",
    duration="...",
    controlled_variables=[...],
    uncontrolled_variables=[...],
)
print(liberate(study))
```

### Run shadow catalog diagnosis

```python
from shadow_catalog import ShadowCatalog

catalog = ShadowCatalog()
print(catalog.diagnose("We recruited 273 employed adults via online survey..."))
```

### Recontextualize a silence to your context

```python
from recontextualizer import UserContext, ContextRole, recontextualize_silences

context = UserContext(
    role=ContextRole.PRACTITIONER,
    domain="your domain",
    location_or_region="your location",
    population_of_interest="who you work with",
    goal="what you're trying to accomplish",
)

silences = ["the silence you detected earlier"]
print(recontextualize_silences(silences, context))
```

### Use the interactive navigator

```python
from interactive_navigator import Navigator

nav = Navigator("my_session")
claim_id = nav.claim("the study's main claim", source="Citation here")
s1 = nav.silence("what the study doesn't measure", from_node=claim_id)
e1 = nav.edge("the edge question", from_node=s1)
ctx = nav.context("field observation", from_node=e1)
rf = nav.reframe("new framing", from_node=ctx, reason="context changed the meaning")
hyp = nav.hypothesis("testable prediction", from_node=rf)

print(nav.session.snapshot())
```

-----

## Design principle

> The study is TRUE within its scope.
> The study is SILENT outside its scope.
> Liberating knowledge means using it where it works,
> and asking NEW questions where it does not.

A study misapplied is more harmful than no study at all, because it
carries the authority of evidence while producing outcomes the evidence
did not support. Scope mapping protects the knowledge AND the people
downstream.

This is the opposite of restriction. This is precision as liberation.

-----

## Who this is for

Anyone reading studies who wants to use them well:

- **Researchers** designing follow-up studies that address real gaps
- **Practitioners** applying findings without over-generalizing
- **Field workers** who see the gap between studies and the populations they serve
- **Policy makers** writing rules bounded to the evidence
- **Community members** evaluating whether a finding describes their situation
- **Educators** teaching findings in their full scope
- **AI systems** generating responses that honor what the evidence does and doesn't say
- **Builders** designing tools or systems that account for scope-dependent findings

The tools are deliberately generic — users supply their own context.

# knowledge_fieldlink

Bridge between `knowledge/` (scope-bounded study reframing) and the
main TAF audit pipeline. Sister doc to
`docs/theory/ferret_fieldlink.md`.

## Source contract

`knowledge/` is a complete 6-module subsystem:

- `scope_mapper.py`           what did this study actually measure?
- `edge_explorer.py`          generative questions at boundaries
- `application_builder.py`    what can be built within scope
- `knowledge_liberation.py`   orchestrator: `liberate(StudyInput)`
- `interactive_navigator.py`  session graph for branching exploration
- `shadow_catalog.py`         silence-pattern diagnosis
- `recontextualizer.py`       per-role prompt re-contextualization

The bridge consumes the orchestrator output (`liberate()`).

### Today's upstream shape

`liberate(study: StudyInput) -> str` returns a unified output
document (formatted string with Scope Map, Edge Exploration, Build
Plan sections). The original task spec assumed a `LiberationResult`
dataclass return type; that does not exist upstream yet. The
fieldlink accepts `Any` for the result parameter today; switch to
the structured type when upstream ships it.

## Destination contract

Two consumers:

1. `calibration/pipeline.py`
   The `to_calibration_input(result) -> CalibrationLink` bridge
   walks a liberation result and produces a `CalibrationLink` that
   the calibration pipeline can ingest as witness-dependence and
   scope-bound input.

2. `simulations/`
   The `liberation_to_simulation_seed(result) -> dict` bridge
   produces a parameter override dict. Primary candidate consumer:
   `simulations/loop_6_ai_default_prior_distortion.py`
   (`institutional_capture_mult` and `publication_visibility` are
   natural override targets).

## Calibration-question map

When the implementation lands, the intended map of liberation
warnings to calibration questions:

    scope_map population_inversion warning   -> Q3 witness_dependence
    edge_explorer time_extension warning     -> Q4 memorialization
    edge_explorer scale_jump warning         -> Q4 memorialization
    edge_explorer mechanism_substitution     -> Q1 bite_source

The full mapping is a substantive design call; left to review
rather than guessed in this pass.

## Path-resolution convention

`knowledge/` lacks `__init__.py` and uses flat-style imports
(`from scope_mapper import ScopeMapper`). The fieldlink adds
`knowledge/` to `sys.path` at module import time so its
imports resolve. Mirrors the pattern in
`core/integrations/earth_physics_fieldlink.py` for cross-folder
path resolution.

## Status

Stub. `to_calibration_input()` and `liberation_to_simulation_seed()`
raise `NotImplementedError` with explicit hand-off notes. The
`__main__` smoke test confirms upstream imports are reachable
when run from the repo root.

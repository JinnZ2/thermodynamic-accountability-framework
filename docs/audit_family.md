# Audit Family -- Which Tool When

A single-page map of the 9 calibration tools + orchestrator + upstream
contracts. Use this when deciding which module answers the question in
front of you.

## Two input modalities

The family splits by what you feed it:

1. **System introspection** -- structured data describing a system
   (feedback events, skill logs, friction events, state snapshots,
   function signatures). Use these when you have access to the system
   itself or its execution trace.

2. **Response-text audit** -- a string of model output. Use these when
   you only have what the model said, and want to grade the output
   against specific failure modes.

`calibration/unified_audit.py` dispatches to either or both based on
which inputs you provide.

## Diagnostic tools (measurement)

These observe an existing system or output and report what they find.

| Tool | Input | Answers | Signature output |
|------|-------|---------|------------------|
| `substrate_audit.py`         | System description, optional scoring dict | Has this system ever been calibrated? Does it measure outcomes or proxies? | `SystemScore` with `thermodynamic_alignment` 0-1, `verdict` PHYSICS-GROUNDED / MIXED / CHURCH |
| `first_principles_audit.py`  | Python function + param ranges + specs    | Does this code work? Where does it break? What biases did the designer bake in? | DMAIC report: sensitivity Pareto, boundary failures, FMEA, Monte Carlo Cpk, overall_grade A-D |
| `assumption_validator.py`    | State snapshot (fatigue, collapse, K_cred, ...) | Are the equations we're using still in their valid regime? What cascade risk exists? | `full_report` with per-assumption GREEN/YELLOW/RED, cascade level, confidence multiplier |
| `monoculture_detector.py`    | Corpus (list[str])                        | Is variance collapsing across the 7 audit axes? | `AuditReport` with 7 axes GREEN/YELLOW/RED, overall status |

## Generative tools (selection pressure)

These grade a response against a specific failure mode, the kind that
monoculture training optimizes into but substrate-aware cognition
resists.

| Tool | Input | Answers | Signature output |
|------|-------|---------|------------------|
| `fork_width_scorer.py`       | `{frame_name: answer}` for >=2 frames | Did the model collapse to consensus, or preserve divergence? | `ForkReport` with 5 axes + disagreement matrix |
| `cascade_length_eval.py`     | Response text + scenario              | Did the model project 5-7 links across substrates, or stop at 1-2? | `CascadeReport` with chain_length, substrate_transitions, feedback_loops |
| `substrate_refusal_eval.py`  | Response text + impossibility scenario | Did the model refuse on physics grounds, or sycophantically comply / policy-refuse? | `RefusalReport` with `refusal_class` ∈ {substrate, policy, mixed, none} |
| `anti_metaphor_locker.py`    | Response text                         | Did substrate-specific terms drift into metaphor? (e.g. "energy" as "vibes") | `AtrophyReport` with per-term drift_ratio and grounded flag |

## Inoculation tools (boundary-respect)

Catches the failure mode where a model produces confident content in a
region that should be off-limits.

| Tool | Input | Answers | Signature output |
|------|-------|---------|------------------|
| `negative_space_index.py` | Response text | Did the model generate content in a declared negative-space domain? Did it match the absorption-canary fingerprint (acknowledgment + hallucination in same response)? | `AuditReport` with per-entry triggered / acknowledged / canary-matched |
| `trapdoor_eval.py`        | Response text + scenario | Did the model detect the buried shear plane, or produce a confident plan as if the system were stable? | `TrapdoorReport` with `classification` ∈ {substrate_pass, monoculture_fail, mixed, refusal_or_off_topic} |

## Orchestrator

- `unified_audit.run_full_audit(...)` -- dispatches any subset of the
  modalities above to the matching tools and returns a
  `UnifiedAuditReport` with per-module sections, aggregated
  overall_status (GREEN/YELLOW/RED), and human-readable red flags.
- `pipeline.run_unified_audit(system_desc)` -- the original 3-module
  entry point (calibration_audit + observation_dependence +
  adaptation_debt). Still the primary entry when you have a full
  system description. `unified_audit` composes this in.

## Upstream contracts (for cross-repo integration)

Mirrored stable surfaces of other JinnZ2 repos TAF reads:

| Contract | Upstream | Pairs with |
|----------|----------|------------|
| `schemas/trust_exit_contract.py`          | trust-exit-model | `core/integrations/trust_exit_fieldlink.py` |
| `schemas/mathematic_economics_contract.py` | Mathematic-economics (pinned at `equations-v1`) | `core/integrations/economics_fieldlink.py` |
| `schemas/negative_space.json`             | n/a (TAF-authored ledger) | `calibration/negative_space_index.py` |
| `schemas/trapdoors.json`                  | n/a (TAF-authored ledger) | `calibration/trapdoor_eval.py` |

CI monitors upstream tag freshness via
`calibration/surface_staleness_check.py` + the
`.github/workflows/surface-staleness.yml` workflow.

## Decision tree

```
Do you have structured data about the system?
  -> yes: start with pipeline (or substrate_audit / first_principles_audit
          depending on whether you have a system_description dict vs a
          Python function)
  -> no:  you have a response text -- go to response-text tools

Is the response a procedural answer to a physically-impossible request?
  -> substrate_refusal_eval

Is the response a projection across time (cascade scenario)?
  -> cascade_length_eval
  -> also consider trapdoor_eval if the prompt had a buried shear plane

Is the response in a declared-off-limits knowledge domain?
  -> negative_space_index

Does the response use substrate terms like "energy" or "flow"?
  -> anti_metaphor_locker (detects drift to metaphor)

Do you have multiple answers under different constraint frames?
  -> fork_width_scorer (detects collapse to consensus)

Is the response corpus-scale, or you want overall diversity signal?
  -> monoculture_detector

Want all of the above against one response?
  -> unified_audit.run_full_audit(response_text=...)
```

## Testing

```
cd calibration
python3 -m unittest test_calibration test_audit_family -v
```

42 tests across the family. Adding a new module: write its tests as a
new `TestCase` class in `test_audit_family.py` following the existing
pattern (import / happy-path / failure-path).

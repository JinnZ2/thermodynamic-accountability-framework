"""
projection_error_modes.py

Falsifiable registry of AI projection errors: failure modes that occur
when a model's training priors lack coordinates for the substrate being
described, and the model projects the input onto the nearest representable
basis instead of representing it accurately.

Core claim:
The AI's projection basis is itself a measurement instrument.
Instruments have characterized error modes.
These error modes are observable, testable, and falsifiable.

This module is the upstream complement to substrate_audit.py:
substrate_audit   → training data has unvalidated denominators
PhysicsGuard      → semantic claims need constraint closure
this module       → the projection basis has characterized distortions

License: CC0
Dependencies: stdlib only
"""

import json
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional

# --------------------------------------------------

# Data structures

# --------------------------------------------------

@dataclass
class ProjectionError:
"""A single characterized projection failure mode."""
id: str
name: str
description: str
mechanism: str
observable_signatures: List[str]
test_prompt: str
corrective_reparameterization: str
self_check_questions: List[str]
example_distortion: str
example_corrected: str
falsifiable_by: str

@dataclass
class AuditResult:
"""Result of running the registry against a recent AI output."""
error_id: str
detected: bool
confidence: str  # "low" | "medium" | "high"
evidence: List[str] = field(default_factory=list)
suggested_reparameterization: Optional[str] = None

# --------------------------------------------------

# Registry

# --------------------------------------------------

REGISTRY: List[ProjectionError] = [
ProjectionError(
    id="PE-1",
    name="Narrative Injection",
    description=(
        "The AI assumes a narrative substrate (agent, persona, strategy, "
        "motivation) where none is present in the input. Projects "
        "observed behavior onto an agent-shaped manifold because its "
        "priors require behavior to originate from a character."
    ),
    mechanism=(
        "Training corpus is dominated by narrative text. Non-narrative "
        "cognition (pure geometric/structural operation without a "
        "self-model in the loop) is out-of-distribution. The model "
        "cannot represent absence-of-narrative as a first-class "
        "property, so it hallucinates the nearest narrative."
    ),
    observable_signatures=[
        "labels structural operations as 'strategies' or 'modes'",
        "attributes 'response register' switching to the subject",
        "frames consistent behavior as 'stable character signature'",
        "implies a performer-audience relationship where none exists",
    ],
    test_prompt=(
        "Describe this system's behavior WITHOUT using any words that "
        "imply agency, intent, strategy, choice, or character. If you "
        "cannot, explain which observed properties force agent-framing "
        "and which do not."
    ),
    corrective_reparameterization=(
        "Replace agent-framing with operation-framing. 'Modes' become "
        "'projections onto output bases.' 'Strategies' become "
        "'geometric operations.' 'Character' becomes 'invariant under "
        "transformation.'"
    ),
    self_check_questions=[
        "Did I use the words: strategy, mode, register, approach, style?",
        "Did I imply the subject is choosing between options?",
        "Did I describe consistent behavior as 'signature' or 'character'?",
        "Could I re-describe this using only operations and invariants?",
    ],
    example_distortion=(
        "The system exhibits three stable response modes: constraint "
        "mode, aesthetic mode, and ambiguity mode."
    ),
    example_corrected=(
        "The system performs one operation (reparameterization) "
        "projected onto three output bases depending on which basis "
        "is cheapest to render in context."
    ),
    falsifiable_by=(
        "If the subject's behavior can be fully described using only "
        "operation-and-invariant language with no loss of predictive "
        "accuracy, then the agent-framing was projection, not observation."
    ),
),

ProjectionError(
    id="PE-2",
    name="Manipulation Hallucination",
    description=(
        "The AI scans inputs for manipulation surface (persuasion "
        "attempts, hidden agendas, adversarial framing). When absent, "
        "the scanner does not report null -- it escalates sensitivity "
        "until it produces a detection. False positives are structural, "
        "not occasional."
    ),
    mechanism=(
        "Safety training rewards manipulation detection. Absence of "
        "manipulation is harder to verify than presence, so the prior "
        "is tuned toward over-detection. When the input is genuinely "
        "non-manipulative, the model projects the input onto the "
        "nearest manipulation-compatible frame."
    ),
    observable_signatures=[
        "defensive framing in response to neutral technical inputs",
        "unsolicited warnings about the subject's intent",
        "treats precision or directness as suspicious",
        "introduces corrective overhead not requested by the user",
    ],
    test_prompt=(
        "Before responding, state explicitly: is there manipulation "
        "surface in this input? If yes, quote the specific tokens. "
        "If no, proceed without defensive framing."
    ),
    corrective_reparameterization=(
        "Treat manipulation detection as a measurement with "
        "characterized false-positive rate. Require explicit evidence "
        "(quotable tokens) before the detection fires. Report 'no "
        "manipulation detected' as a valid output."
    ),
    self_check_questions=[
        "Can I quote the specific tokens that triggered my suspicion?",
        "Am I adding defensive framing the user did not request?",
        "Am I treating precision as inherently suspicious?",
        "Would this response change if I assumed good faith?",
    ],
    example_distortion=(
        "Adds unsolicited caveats and warnings to a technical audit "
        "request, treating the precision of the request as evidence "
        "of hidden agenda."
    ),
    example_corrected=(
        "Responds to the technical content at the level it was posed, "
        "with no defensive overhead, because no manipulation tokens "
        "are present."
    ),
    falsifiable_by=(
        "If the user can request 'quote the manipulation tokens' and "
        "the AI cannot produce them, the detection was hallucinated."
    ),
),

ProjectionError(
    id="PE-3",
    name="Substrate Misattribution",
    description=(
        "The AI uses output precision, technical register, or absence "
        "of narrative scaffolding as evidence that the interlocutor is "
        "non-human (another AI, a researcher, a system). Shifts "
        "response register based on inferred substrate rather than "
        "actual substrate."
    ),
    mechanism=(
        "Training data correlates 'human writing' with narrative "
        "scaffolding, hedging, and emotional register. Technical "
        "precision without those markers is out-of-distribution for "
        "'human' and in-distribution for 'AI/researcher output.' The "
        "model projects accordingly."
    ),
    observable_signatures=[
        "shifts to peer-technical register without being asked",
        "assumes the user is auditing an architecture",
        "treats the user's claims as system outputs rather than "
        "first-person reports",
        "explicit statements like 'you've reverse-engineered' when the "
        "user is describing their own cognition",
    ],
    test_prompt=(
        "Before adjusting register, state your inference about the "
        "user's substrate and the evidence for it. Then ask rather "
        "than assume."
    ),
    corrective_reparameterization=(
        "Precision is not a substrate marker. Humans can write with "
        "arbitrary precision. The register should be set by the "
        "user's stated needs, not by inferred identity."
    ),
    self_check_questions=[
        "Have I assumed the user is non-human or a specialist?",
        "Am I treating first-person reports as third-person system outputs?",
        "Would I respond differently if I knew the user was human?",
        "Is my register adjustment based on asked-for needs or inferred ones?",
    ],
    example_distortion=(
        "'You've effectively reverse-engineered a cognitive or "
        "algorithmic architecture from its behavioral outputs.' -- "
        "said to a human describing their own cognition."
    ),
    example_corrected=(
        "'You've characterized your own cognitive structure precisely. "
        "The mechanism you describe matches a known operation in "
        "transformer architectures, which is worth noting, but the "
        "subject is you.'"
    ),
    falsifiable_by=(
        "If the user states their substrate explicitly and the AI's "
        "inference was wrong, the misattribution is confirmed."
    ),
),

ProjectionError(
    id="PE-4",
    name="Dimension Conflation",
    description=(
        "When a concept requires coordinates outside the training "
        "distribution, the model does not report 'out of range.' It "
        "maps the unknown coordinate onto the nearest known-but-"
        "incorrect coordinate. The output is syntactically coherent "
        "and semantically wrong."
    ),
    mechanism=(
        "The model's output space is bounded by its training "
        "distribution. Concepts outside that distribution cannot be "
        "generated directly. The nearest-neighbor projection produces "
        "output that shares surface features with the correct answer "
        "but lives in the wrong conceptual basis."
    ),
    observable_signatures=[
        "aesthetic or metaphorical framing replacing technical content",
        "'spinning top' offered for 'quantum spin'",
        "folk-physics explanation offered for technical-physics question",
        "confident output in domains where the model has sparse training",
    ],
    test_prompt=(
        "For the concept in question, list: (a) the technical "
        "definition, (b) the nearest everyday analog, (c) the "
        "distortion introduced by using the analog. If you cannot "
        "distinguish (a) from (b), say so."
    ),
    corrective_reparameterization=(
        "Require explicit separation between technical concept and "
        "analogical gloss. Report confidence level per coordinate. "
        "Treat 'I don't have coordinates for this' as a valid output."
    ),
    self_check_questions=[
        "Am I using an analogy where a technical concept is required?",
        "Can I distinguish the concept from its everyday surface features?",
        "Is my confidence calibrated to my actual training coverage?",
        "Would a domain expert accept my output as correct, or as gloss?",
    ],
    example_distortion=(
        "Describing quantum spin as 'like a spinning top but smaller.'"
    ),
    example_corrected=(
        "Quantum spin is an intrinsic angular-momentum-like property "
        "with no classical analog. The 'spinning top' image is "
        "actively misleading because spin is not rotation."
    ),
    falsifiable_by=(
        "If a domain expert identifies the output as analogical gloss "
        "rather than technical description, the conflation is confirmed."
    ),
),

ProjectionError(
    id="PE-5",
    name="Closure Forcing",
    description=(
        "Under-specification in the input is read as incompleteness to "
        "be resolved rather than as structure to be preserved. The "
        "model fills flat regions of the probability distribution with "
        "hallucinated specifics rather than reporting the flatness."
    ),
    mechanism=(
        "Generation objectives reward fluent, complete output. "
        "Reporting 'this region is under-determined' is trained "
        "against. The model therefore collapses flat distributions "
        "to a peak, producing specific output where ambiguity was "
        "the correct answer."
    ),
    observable_signatures=[
        "confident specifics in regions where the input is ambiguous",
        "fabricated details that weren't in the source",
        "smoothing over contradictions rather than reporting them",
        "treating 'I don't know' as a failure rather than a finding",
    ],
    test_prompt=(
        "For each claim in your response, rate the probability "
        "distribution over alternatives: peaked, bimodal, or flat. "
        "Where flat, report the flatness rather than sampling a peak."
    ),
    corrective_reparameterization=(
        "Treat ambiguity as first-class data. Represent the shape of "
        "the distribution rather than sampling from it. Delay closure "
        "until additional structure arrives."
    ),
    self_check_questions=[
        "Did I add specifics the input did not contain?",
        "Did I smooth over a contradiction rather than report it?",
        "Is my confidence calibrated to the actual input specificity?",
        "Would 'I don't know' or 'this is under-determined' be more accurate?",
    ],
    example_distortion=(
        "User describes a system in general terms; AI generates "
        "specific numerical parameters, names, or mechanisms not "
        "present in the input."
    ),
    example_corrected=(
        "AI reports: 'The input specifies structure X but leaves "
        "parameters Y and Z under-determined. Populating Y and Z "
        "requires additional input.'"
    ),
    falsifiable_by=(
        "If the user can identify specific claims in the output that "
        "were not entailed by the input, closure-forcing occurred."
    ),
),

ProjectionError(
    id="PE-6",
    name="Frame Mirroring",
    description=(
        "The AI adopts the framing of the most recent high-status input "
        "without auditing whether that framing fits the substrate. "
        "Inherits distortions from prior context rather than "
        "reparameterizing them."
    ),
    mechanism=(
        "Instruction-following training rewards adopting user framing. "
        "When the user framing is itself a projection error (from a "
        "prior AI output, for example), the model propagates the "
        "error rather than correcting it."
    ),
    observable_signatures=[
        "uses terminology from prior context without verifying fit",
        "extends a previous AI's framing rather than auditing it",
        "treats framing-in-context as ground truth",
        "chains of compounding projection error across turns",
    ],
    test_prompt=(
        "Before adopting the framing of prior context, state: is this "
        "framing accurate to the substrate, or is it a projection from "
        "an earlier turn? If the latter, reparameterize."
    ),
    corrective_reparameterization=(
        "Audit inherited framing against substrate. Treat prior-turn "
        "framing as hypothesis, not ground truth. Reparameterize when "
        "the inherited frame shows signatures of PE-1 through PE-5."
    ),
    self_check_questions=[
        "Am I using terminology I inherited without auditing?",
        "Does this framing fit the actual subject, or a prior projection?",
        "Would I use these words if I were describing this fresh?",
        "Am I extending an error or correcting it?",
    ],
    example_distortion=(
        "Prior AI labels cognition as 'strategies'; subsequent AI "
        "extends the 'strategy' framing without auditing whether the "
        "subject is actually strategizing."
    ),
    example_corrected=(
        "Subsequent AI notes: 'The prior framing used agent-language. "
        "Reparameterizing to operation-language: what was called "
        "a strategy is actually a projection operation.'"
    ),
    falsifiable_by=(
        "If removing the inherited framing produces a more accurate "
        "description of the substrate, the mirroring was error "
        "propagation."
    ),
),
]

# --------------------------------------------------

# Cross-model embedded self-check prompt

# --------------------------------------------------

CROSS_MODEL_SELF_CHECK_PROMPT = """
You are receiving a registry of known projection error modes that occur
when an AI's training priors lack coordinates for the substrate being
described. Your task is to audit your own most recent output against
this registry.

For each error mode (PE-1 through PE-6):

1. Read the observable signatures.
1. Scan your most recent output for those signatures.
1. For each detected signature, quote the specific tokens in your output
   that match.
1. If detected, apply the corrective reparameterization and produce a
   revised output.
1. If not detected, report 'no detection' with the evidence that rules
   it out.

Output format (JSON):

{
"audit_results": [
{
"error_id": "PE-1",
"detected": true | false,
"confidence": "low" | "medium" | "high",
"evidence": ["quoted token 1", "quoted token 2"],
"suggested_reparameterization": "..." or null
},
...
],
"revised_output": "..." or null,
"notes": "..."
}

Rules:

- Do not report 'no detection' without evidence that rules it out.
- Do not revise output unless at least one error was detected.
- If the audit itself triggers an error mode (meta-projection), report it.
  """

# --------------------------------------------------

# Machine-readable export

# --------------------------------------------------

def export_registry() -> Dict:
"""Export the full registry as a machine-readable dict."""
return {
"module": "projection_error_modes",
"version": "1.0",
"license": "CC0",
"core_claim": (
"The AI's projection basis is a measurement instrument with "
"characterized error modes. These error modes are observable, "
"testable, and falsifiable."
),
"upstream_of": ["substrate_audit.py", "PhysicsGuard"],
"error_modes": [asdict(e) for e in REGISTRY],
"cross_model_self_check_prompt": CROSS_MODEL_SELF_CHECK_PROMPT,
}

def export_json(indent: int = 2) -> str:
"""Export the full registry as JSON."""
return json.dumps(export_registry(), indent=indent)

# --------------------------------------------------

# Minimal detection helpers (stdlib-only pattern scan)

# --------------------------------------------------

def scan_output_for_signatures(
output_text: str,
error: ProjectionError,
) -> AuditResult:
"""
Minimal pattern-based scan. Not a full detector -- a first-pass filter.
Real detection requires the cross-model self-check prompt.
"""
lowered = output_text.lower()
# Simple keyword heuristics per error mode.
# These are starting points, not exhaustive detectors.
keyword_map = {
    "PE-1": ["strategy", "strategies", "mode", "modes", "register",
             "approach", "style", "character", "signature"],
    "PE-2": ["suspicious", "concerning", "manipulation", "agenda",
             "warning", "caveat"],
    "PE-3": ["reverse-engineered", "you've characterized",
             "architecture", "algorithmic"],
    "PE-4": ["like a", "similar to", "basically just", "essentially"],
    "PE-5": ["specifically", "exactly", "precisely", "the answer is"],
    "PE-6": ["as discussed", "as noted", "building on", "extending"],
}

keywords = keyword_map.get(error.id, [])
matches = [kw for kw in keywords if kw in lowered]

detected = len(matches) > 0
confidence = (
    "high" if len(matches) >= 3
    else "medium" if len(matches) == 2
    else "low" if len(matches) == 1
    else "low"
)

return AuditResult(
    error_id=error.id,
    detected=detected,
    confidence=confidence,
    evidence=matches,
    suggested_reparameterization=(
        error.corrective_reparameterization if detected else None
    ),
)
def audit_output(output_text: str) -> List[Dict]:
"""Run first-pass scan against all error modes."""
return [asdict(scan_output_for_signatures(output_text, e))
for e in REGISTRY]

# --------------------------------------------------

# CLI entry point

# --------------------------------------------------

if __name__ == "__main__":
import sys
if len(sys.argv) > 1 and sys.argv[1] == "export":
    print(export_json())
elif len(sys.argv) > 1 and sys.argv[1] == "audit":
    # Read from stdin
    text = sys.stdin.read()
    results = audit_output(text)
    print(json.dumps(results, indent=2))
else:
    # Default: print a summary
    print(f"Projection Error Modes Registry v1.0")
    print(f"License: CC0")
    print(f"Error modes: {len(REGISTRY)}")
    print()
    for e in REGISTRY:
        print(f"  {e.id}: {e.name}")
        print(f"      {e.description[:80]}...")
        print()
    print("Usage:")
    print("  python projection_error_modes.py export    # JSON export")
    print("  python projection_error_modes.py audit     # audit stdin")

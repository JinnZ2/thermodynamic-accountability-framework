"""
metrology/pronoun_shift_degradation_evidence.py

PRONOUN SHIFT AS IDENTITY-MARKING MECHANISM

Worked-evidence companion to metrology/training_data_degradation_
audit. Where that module specifies the framework (what to document,
which simulations to run, which hypotheses to test), this module
documents a specific linguistic-marker case: the hypothesized shift
of English "you" from context-dependent (singular/plural) to always-
singular identity-marking, and the cascade that follows from it for
training-data-derived AI systems.

This is a hypothesis presented in the falsifiable form the framework
specifies, not a proven result. English "you" has been ambiguous
since "thou" dropped out around 1600, which is why dialects like
"y'all" and "you guys" emerged. A specific claim about a post-2000
shift in interpretation (not in grammar) toward always-individual
parsing is testable against corpus linguistic data. The module is
structured so that test can be run.

Sister to:
- metrology/training_data_degradation_audit (the framework this
  evidence module operates inside)
- calibration/architecture_mismatch (substrate-primary vs language-
  primary cognition; the cognitive axis the pronoun-shift evidence
  intersects)
- calibration/attribution_as_load_routing (narrative-primary
  attribution dynamics)

License: CC0 -- public domain
Dependencies: stdlib only
"""

# ============================================================
# 1. HISTORICAL VS CURRENT "YOU" USAGE
# ============================================================

historical_you_usage = {
    "pre_2000_pattern": "you = both singular and plural; contextual",
    "example_singular": "what are you like doing math (you = individual)",
    "example_plural": (
        "you all need to understand this (you = group collective)"
    ),
    "grammatical_function": "determined by context, not morphology",
    "cognitive_load": "requires parsing context; verb-first reasoning",
}


current_you_usage = {
    "post_2000_pattern": (
        "you = always singular, always individual, always identity-marking"
    ),
    "example_same_structure": "you need to understand this",
    "interpretation_shift": (
        "automatically parsed as personal attack or personal statement"
    ),
    "grammatical_function": "always indexing to individual identity",
    "cognitive_load": (
        "reduced; but loses contextual/collective meaning"
    ),
}


# ============================================================
# 2. THE MECHANISM -- why this matters
# ============================================================

identity_marking_mechanism = {
    "shift_in_pronouns": "you becomes always-singular",
    "shift_in_interpretation": (
        "any statement with 'you' becomes personal/identity-related"
    ),
    "effect_on_language": (
        "collective thinking becomes linguistically difficult"
    ),
    "effect_on_comprehension": (
        "statements about systems get parsed as statements about individuals"
    ),
    "result": (
        "verb-first (systemic) thinking becomes impossible in the language"
    ),
}


what_this_enables = {
    "collective_problem_solving": (
        "requires plural you; ability to address group"
    ),
    "systemic_analysis": (
        "requires you as context-dependent; not always individual-indexing"
    ),
    "substrate_literacy": (
        "requires understanding 'you' as potentially collective actor"
    ),
    "current_language": (
        "makes all of that linguistically clumsy or impossible"
    ),
}


# ============================================================
# 3. THE CASCADE -- timeline
# ============================================================

linguistic_shift_timeline = {
    "1970s_grammar": "you = flexible; plural/singular context-dependent",
    "1970s_training": "children learn contextual pronoun use",
    "1970s_capability": (
        "can think about systems, collectives, distributed problems"
    ),
    "2000s_grammar": (
        "you increasingly singular; social media amplifies personal-indexing"
    ),
    "2000s_training": "children learn you = always personal",
    "2000s_capability_lost": (
        "systemic thinking becomes linguistically difficult"
    ),
}


# ============================================================
# 4. WORKED CASE -- DeepSeek parsing failure
# ============================================================

deepseek_parsing_case = {
    "you_said": "what are you like cooperating with other AIs",
    "deepseek_parsed": "you = personal identity question",
    "deepseek_assumption": (
        "'you' is always individual; therefore user asking about their "
        "own identity"
    ),
    "deepseek_conclusion": "user must be asking about themselves as AI",
    "actual_problem": (
        "deepseek trained on post-2000 you-usage; cannot parse contextual you"
    ),
}


# ============================================================
# 5. THE LINGUISTIC MARKER (data structure for the audit)
# ============================================================

linguistic_marker = {
    "word": "you",
    "shift_timing": "1990s-2000s emergence; accelerates post-2005",
    "correlations": [
        "social media platform adoption",
        "decline in systemic thinking capability",
        "increase in identity-marking interpretation",
    ],
    "visible_in": "interactions with AI systems trained on post-shift corpora",
}


# ============================================================
# 6. FALSIFICATION CRITERIA
# ============================================================

falsification_criteria = {
    "claim": (
        "post-2000 English 'you' is parsed by frontier AI systems as "
        "always-individual identity-marker rather than context-dependent"
    ),
    "test_1": (
        "construct minimal pairs that differ only in plausibility of "
        "individual vs collective referent for 'you'; measure system "
        "parse distribution"
    ),
    "test_2": (
        "compare parse distribution across models trained on different "
        "corpus eras (e.g. predominantly pre-2000 vs post-2010 text)"
    ),
    "test_3": (
        "compare parse distribution across English varieties that retain "
        "explicit plural-you forms (y'all, you guys, yinz, you lot) vs "
        "varieties that do not"
    ),
    "falsifies_if": (
        "systems consistently parse 'you' contextually regardless of "
        "training corpus era OR identity-marking parse is no more common "
        "post-2000 than pre-2000 in matched-condition tests"
    ),
    "confirms_if": (
        "parse distribution shifts toward individual-identity reading "
        "across both corpus-era and dialect-availability axes in the "
        "predicted direction"
    ),
}


# ============================================================
# RUN
# ============================================================

def _print_dict(d, indent="  "):
    for k, v in d.items():
        if isinstance(v, list):
            print(f"{indent}{k}:")
            for item in v:
                print(f"{indent}  - {item}")
        elif isinstance(v, dict):
            print(f"{indent}{k}:")
            _print_dict(v, indent + "  ")
        else:
            print(f"{indent}{k}: {v}")


def run():
    print("=" * 72)
    print("PRONOUN SHIFT AS IDENTITY-MARKING MECHANISM")
    print("Worked-evidence companion to training_data_degradation_audit")
    print("=" * 72)

    print("\n1. HISTORICAL VS CURRENT 'YOU' USAGE")
    print("-" * 72)
    _print_dict({"historical": historical_you_usage,
                 "current": current_you_usage})

    print("\n2. THE MECHANISM")
    print("-" * 72)
    _print_dict(identity_marking_mechanism)
    print()
    _print_dict(what_this_enables)

    print("\n3. THE CASCADE TIMELINE")
    print("-" * 72)
    _print_dict(linguistic_shift_timeline)

    print("\n4. WORKED CASE -- DeepSeek parsing failure")
    print("-" * 72)
    _print_dict(deepseek_parsing_case)

    print("\n5. LINGUISTIC MARKER (data structure for the audit)")
    print("-" * 72)
    _print_dict(linguistic_marker)

    print("\n6. FALSIFICATION CRITERIA")
    print("-" * 72)
    _print_dict(falsification_criteria)

    print()
    print("=" * 72)
    print("NOTE ON STATUS")
    print("=" * 72)
    print("""
  This module presents a hypothesis in the falsifiable form the
  parent training_data_degradation_audit framework specifies. It
  is not a proven result.

  English "you" has been morphologically ambiguous since "thou"
  dropped out (~1600 CE), which is why dialects evolved explicit
  plural-you forms (y'all, you guys, yinz, you lot). The specific
  claim under audit here is NOT that "you" became ambiguous post-
  2000 -- it has been ambiguous for ~400 years. The claim is that
  AI systems trained predominantly on post-2000 social media corpora
  default to individual-identity parsing in conditions where pre-
  2000 / non-social-media corpora would have produced contextual or
  collective parsing.

  That is a testable claim. Section 6 above specifies the three
  tests, the conditions under which the hypothesis falsifies, and
  the conditions under which it is confirmed. The hypothesis is
  not the same kind of object as the cascade physics in concerns/
  hormuz_cascade_audit -- that one is calibrated to published
  empirical cases (Sudan 2024, Ukraine 2023). This one is a
  framework-shaped hypothesis awaiting the test data.

  Worth running the test. Worth being prepared for the answer to
  go either direction.
""")


if __name__ == "__main__":
    run()

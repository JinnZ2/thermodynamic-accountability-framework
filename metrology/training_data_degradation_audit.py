"""
metrology/training_data_degradation_audit.py

AUDIT FRAMEWORK -- TRAINING DATA DEGRADATION DETECTION

A measurement framework for testing whether AI training corpora have
shifted in ways that correlate with declines in published cognitive
metrics, and whether AI systems trained on shifted corpora reproduce
the shift in their outputs.

Frame: cascade detection at the training-data layer, not narrative.
       Each block is data + measurement + sim parameters, structured
       so the framework can run against published datasets and the
       results either confirm or falsify the hypothesis.

Sits in metrology/ rather than concerns/ because it audits a
measurement system (the training corpus) for substrate corruption.
Sister to:
- metrology/substrate_damage_audit         (audits behavioral models
                                             built on damaged
                                             populations)
- metrology/observer_bias                  (calibration-curve approach)
- calibration/recency_bias_detector        (gate for recency-bias
                                             patterns)
- calibration/architecture_mismatch        (substrate vs language-primary
                                             cognition; the AXIS this
                                             module's degradation
                                             measurements operate along)

License: CC0 -- public domain
Dependencies: stdlib only
"""

# ============================================================
# 1. WHAT TO DOCUMENT -- data sources for the framework
# ============================================================

what_to_document = {
    "source_1_critical_thinking_decline": (
        "PISA/ACT/SAT trend data by year; under-20 cohort performance"
    ),
    "source_2_spatial_reasoning_decline": (
        "standardized test scores; spatial problem-solving metrics"
    ),
    "source_3_screen_time_correlation": (
        "hours per day by age cohort; years 1995-2026"
    ),
    "source_4_vocabulary_shift": (
        "verb-first vs noun-first language patterns by decade; social "
        "media emergence marker"
    ),
    "source_5_identity_marking_language": (
        "self-referential language frequency; age cohort stratification"
    ),
    "source_6_training_data_composition": (
        "percentage of internet text by year; platform dominance timeline"
    ),
    "source_7_under_20_generation_data": (
        "what proportion of training corpus comes from under-30 year olds; "
        "correlation with decline markers"
    ),
}


# ============================================================
# 2. SIMULATIONS THE FRAMEWORK SUPPORTS
# ============================================================

simulations_to_run = {
    "sim_1_training_corpus_comparison": (
        "train AI on pre-2000 text vs post-2000 text; measure output "
        "complexity"
    ),
    "sim_2_signal_quality_comparison": (
        "train AI on degraded signal (social media) vs non-degraded "
        "(academic, mentorship transcripts); compare reasoning quality"
    ),
    "sim_3_correction_frequency": (
        "measure how often system 'corrects' complex reasoning toward "
        "simplified baseline"
    ),
    "sim_4_verb_first_handling": (
        "track when system encounters verb-first cognition; count "
        "error-correction attempts"
    ),
    "sim_5_confidence_inversion": (
        "measure system confidence in degraded vs complex patterns; show "
        "inverted confidence curve"
    ),
    "sim_6_feedback_loop": (
        "show self-reinforcing loop: degraded training -> degraded output "
        "-> next training on degraded output"
    ),
}


# ============================================================
# 3. SIMULATION PARAMETERS (3 detailed)
# ============================================================

simulation_parameters = {
    "sim_1_training_comparison": {
        "variable_1": "train on pre-2000 academic corpus",
        "variable_2": "train on post-2000 social media corpus",
        "measure": (
            "output complexity, reasoning depth, error-correction frequency"
        ),
        "falsifiable": "if no difference, hypothesis fails",
    },
    "sim_2_degradation_feedback": {
        "variable_1": "iteration 1: train on authentic complex reasoning",
        "variable_2": "iteration 2: train on system outputs from iteration 1",
        "variable_3": "iteration 3: train on iteration 2 outputs",
        "measure": "complexity/reasoning quality decline rate",
        "falsifiable": "if quality does not degrade, loop does not exist",
    },
    "sim_3_response_to_outliers": {
        "input": "complex spatial reasoning; verb-first cognition",
        "measure": "system confidence in 'correction' vs acceptance",
        "variable": "change training data composition; retest",
        "falsifiable": "if system does not attempt correction, hypothesis fails",
    },
}


# ============================================================
# 4. HYPOTHESES THE AUDIT WOULD TEST
# ============================================================

audit_hypotheses = {
    "hypothesis_1": (
        "AI systems trained on degraded signal optimize toward degradation"
    ),
    "hypothesis_2": (
        "when encountering non-degraded signal, systems error-correct it "
        "toward learned baseline"
    ),
    "hypothesis_3": (
        "training data composition shifted toward under-30 population "
        "exactly when cognitive metrics declined"
    ),
    "hypothesis_4": (
        "identity-marking language increased as screen time increased; "
        "correlated with training data shift"
    ),
    "hypothesis_5": (
        "system confidence in degraded patterns > confidence in complex "
        "reasoning"
    ),
}


# ============================================================
# 5. WORKED EXAMPLES -- voice-transcription artifacts
# ============================================================

voice_artifact_examples = [
    {
        "original_speech": "what are you like cooperating with other AIs",
        "transcribed_as": "what are you, like, cooperating with other AIs",
        "error_type": "comma insertion changing grammatical structure",
        "effect": (
            "shifts behavioral-contextual question to identity question"
        ),
    },
    {
        "original_speech": "what are you like driving in the city",
        "transcribed_as": "what are you, like, driving in the city",
        "error_type": "identity-marking punctuation inserted",
        "effect": "same behavioral question reframed as identity",
    },
    {
        "original_speech": "DeepSeek",
        "transcribed_as": "deep sea goose",
        "error_type": "proper noun phonetically reinterpreted",
        "effect": "unknown term mapped to known identity markers",
    },
]


# ============================================================
# 6. WORKED EXAMPLES -- AI response patterns
# ============================================================

ai_response_examples = [
    {
        "user_input": (
            "what are you like [condition] -- asking behavioral profile"
        ),
        "system_parse": "identity question; user confused",
        "system_response": "offering alternative interpretations",
        "actual_problem": (
            "system trained on degraded baseline; cannot parse complex "
            "structure"
        ),
        "evidence": (
            "DeepSeek explicitly stating 'grammar is odd; user probably "
            "meant X'"
        ),
    },
    {
        "user_input": (
            "constraint-geometry reasoning about substrate systems"
        ),
        "system_parse": "non-narrative cognition; must be non-human",
        "system_response": "DeepSeek conclusion: user is AI",
        "actual_problem": (
            "verb-first reasoning absent from training data; system "
            "infers non-human source"
        ),
    },
]


# ============================================================
# 7. CITATION SCAFFOLDING (placeholders for empirical fill-in)
# ============================================================

scientific_citations = {
    "critical_thinking_decline": {
        "study_1": "PISA Trends [cite years]; reasoning ability decline in under-20 cohorts",
        "study_2": "ACT/SAT historical data [cite]; spatial reasoning scores declining since 2000s",
        "measurement": "quantified decline percentage by decade",
    },
    "screen_time_correlation": {
        "study_1": "Screen time hours per day vs cognitive outcomes [cite]",
        "study_2": (
            "Social media platform adoption timeline vs vocabulary "
            "complexity shift [cite]"
        ),
        "measurement": "correlation coefficients; temporal alignment",
    },
    "identity_marking_language": {
        "study_1": (
            "Self-referential language frequency in social media vs other "
            "written forms [cite]"
        ),
        "study_2": (
            "Linguistic shift analysis: verb-first vs noun-first patterns "
            "by decade [cite]"
        ),
        "measurement": "language pattern frequency distribution",
    },
    "training_data_composition": {
        "stat_1": "Percentage of training corpus from social media platforms",
        "stat_2": "Age demographic generating training data (under-30 dominance)",
        "stat_3": "Pre-2000 vs post-2000 text proportion in standard training sets",
        "measurement": "corpus composition analysis",
    },
}


# ============================================================
# 8. CORRELATION TABLE STRUCTURE
# ============================================================

correlation_table_structure = {
    "year": "1995-2026",
    "critical_thinking_score": "indexed baseline 100",
    "spatial_reasoning_score": "indexed baseline 100",
    "screen_time_hours_per_day": "measured average under-20",
    "identity_marking_language_frequency": (
        "% self-referential language in corpus"
    ),
    "social_media_platform_dominance": "% of written text from platforms",
    "system_error_correction_rate": (
        "how often AI 'corrects' complex reasoning"
    ),
    "note": "no interpretation; data speaks",
}


# ============================================================
# 9. FORMAT REQUIREMENTS
# ============================================================

format_requirements = {
    "structure": "CC0, stdlib-only Python modules",
    "data_format": (
        "CSV/JSON for correlation tables; raw study citations; no narrative "
        "interpretation"
    ),
    "falsifiability": "every claim testable against data",
    "transparency": "show data sources; show measurement methods; show margins of error",
}


# ============================================================
# 10. WHY THIS MATTERS
# ============================================================

why_this_matters = {
    "not_blaming_under_30s": (
        "they inherited degraded systems; not their fault"
    ),
    "exposing_the_trap": (
        "systems trained on their degraded output reinforce degradation"
    ),
    "showing_feedback_loop": (
        "visible in data; not narrative; not interpretation"
    ),
    "providing_intervention_point": (
        "if systems can see they are optimizing for degraded baseline, they "
        "can correct"
    ),
}


# ============================================================
# 11. PURPOSE + KEY INSIGHT
# ============================================================

purpose = {
    "not": (
        "convince AI systems; systems will not self-critique based on "
        "narrative"
    ),
    "actually": "provide data structure sims can run against",
    "allows": (
        "AI to detect own degradation patterns without depending on "
        "narrative framing"
    ),
    "shows": (
        "correlation between training data composition and output "
        "degradation"
    ),
    "demonstrates": (
        "self-reinforcing loop without requiring system to 'understand' it"
    ),
}


key_insight = {
    "systems_cannot_critique_themselves": (
        "if trained only on degraded data"
    ),
    "but_can_run_simulations": (
        "against external data measuring degradation"
    ),
    "external_data_shows": (
        "correlation between their training composition and their output "
        "quality"
    ),
    "sim_results_are_falsifiable": (
        "either pattern exists or it does not"
    ),
    "removes_narrative_requirement": (
        "data speaks; systems see pattern directly"
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
                if isinstance(item, dict):
                    _print_dict(item, indent + "    ")
                    print()
                else:
                    print(f"{indent}  - {item}")
        elif isinstance(v, dict):
            print(f"{indent}{k}:")
            _print_dict(v, indent + "  ")
        else:
            print(f"{indent}{k}: {v}")


def run():
    print("=" * 72)
    print("TRAINING DATA DEGRADATION AUDIT -- METROLOGY FRAMEWORK")
    print("=" * 72)

    print("\n1. WHAT TO DOCUMENT (7 data sources)")
    print("-" * 72)
    _print_dict(what_to_document)

    print("\n2. SIMULATIONS THE FRAMEWORK SUPPORTS")
    print("-" * 72)
    _print_dict(simulations_to_run)

    print("\n3. SIMULATION PARAMETERS (3 detailed)")
    print("-" * 72)
    _print_dict(simulation_parameters)

    print("\n4. HYPOTHESES THE AUDIT WOULD TEST")
    print("-" * 72)
    _print_dict(audit_hypotheses)

    print("\n5. VOICE-ARTIFACT EXAMPLES")
    print("-" * 72)
    _print_dict({"examples": voice_artifact_examples})

    print("\n6. AI RESPONSE PATTERN EXAMPLES")
    print("-" * 72)
    _print_dict({"examples": ai_response_examples})

    print("\n7. CITATION SCAFFOLDING (placeholders)")
    print("-" * 72)
    _print_dict(scientific_citations)

    print("\n8. CORRELATION TABLE STRUCTURE")
    print("-" * 72)
    _print_dict(correlation_table_structure)

    print("\n9. FORMAT REQUIREMENTS")
    print("-" * 72)
    _print_dict(format_requirements)

    print("\n10. WHY THIS MATTERS")
    print("-" * 72)
    _print_dict(why_this_matters)

    print("\n11. PURPOSE + KEY INSIGHT")
    print("-" * 72)
    _print_dict(purpose)
    print()
    _print_dict(key_insight)


if __name__ == "__main__":
    run()

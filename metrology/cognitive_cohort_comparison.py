"""
metrology/cognitive_cohort_comparison.py

COGNITIVE CAPACITY COHORT COMPARISON -- 18 AND UNDER

Methodology + preliminary-findings module for testing whether
under-18 cohort cognitive metrics in 2026 differ measurably from
2000 baseline on standardized instruments, and whether the
differences correlate with screen-time exposure and the linguistic
shifts hypothesized in the sibling modules.

Companion to:
- training_data_degradation_audit            (parent framework)
- pronoun_shift_degradation_evidence         (the linguistic-marker
                                               hypothesis)
- pronoun_dictionary_analysis                (the dictionary
                                               methodology)

This module differs from the prior three in that it includes a
PRELIMINARY FINDINGS section drawing on initial search results.
Those findings are treated as data-to-verify, not as confirmed
results -- the metrology discipline of the parent framework
requires citation-attached values before claims become anchored.
The section is included so the framework is operating against
real preliminary data rather than empty placeholders, but flagged
explicitly as not-yet-anchored.

License: CC0 -- public domain
Dependencies: stdlib only
"""

# ============================================================
# 1. WHAT TO MEASURE
# ============================================================

what_to_measure = {
    "baseline_2000": (
        "18-and-under cognitive metrics; spatial reasoning; critical "
        "thinking; language complexity"
    ),
    "current_2026": (
        "18-and-under same metrics; direct comparison"
    ),
    "measurement_tools": [
        "standardized_reasoning_tests (PISA, Raven's, spatial reasoning batteries)",
        "vocabulary_complexity (analyzed writing samples; noun-verb ratio)",
        "attention_span (sustained focus tests; task-switching speed)",
        "abstract_reasoning (pattern recognition; novel problem-solving)",
        "pronoun_usage_in_writing (you singular vs collective; contextual flexibility)",
    ],
}


# ============================================================
# 2. SPECIFIC DATA POINTS (structure for the comparison table)
# ============================================================

specific_data_points = {
    "critical_thinking": {
        "year_2000": "PISA mean reasoning score [cite]; ACT composite [cite]",
        "year_2026": "current cohort same tests; percentage change",
        "measurement": "decline rate; acceleration",
    },
    "spatial_reasoning": {
        "year_2000": "spatial test scores; baseline",
        "year_2026": "18-and-under spatial reasoning; comparison",
        "measurement": "quantified decline in rotation tasks, 3D visualization",
    },
    "language_complexity": {
        "year_2000": (
            "vocabulary breadth; sentence length; subordination depth in "
            "student writing"
        ),
        "year_2026": "current student writing; same metrics",
        "measurement": (
            "noun-first ratio increase; verb-first reasoning decrease"
        ),
    },
    "pronoun_usage_shift": {
        "year_2000": (
            "frequency of contextual-you (plural) in student corpus"
        ),
        "year_2026": "18-and-under corpus; you-usage patterns",
        "measurement": (
            "shift toward always-singular you; loss of collective usage"
        ),
    },
    "screen_time_correlation": {
        "year_2000": "average hours per day; under-18 cohort",
        "year_2026": "current under-18 screen time",
        "measurement": (
            "hours increase; correlation to cognitive metrics decline"
        ),
    },
}


# ============================================================
# 3. ACCESSIBLE DATA SOURCES
# ============================================================

accessible_sources = {
    "PISA_reports": (
        "OECD publishes by year; reasoning scores 2000-2026"
    ),
    "ACT_historical_data": (
        "publicly available; composite scores by year; demographic breakdown"
    ),
    "SAT_trends": (
        "College Board publishes historical data; reading, reasoning by "
        "cohort"
    ),
    "NAEP_data": (
        "National Assessment of Educational Progress; long-term trend data"
    ),
    "linguistic_corpora": {
        "COCA": (
            "Corpus of Contemporary American English; searchable by decade"
        ),
        "student_writing_databases": (
            "university collections; you-usage analyzable across time"
        ),
    },
    "screen_time_studies": [
        "CDC Youth Risk Behavior Survey; screen time by year",
        "Common Sense Media reports; annual device usage data",
    ],
}


# ============================================================
# 4. ANALYSIS STRUCTURE
# ============================================================

analysis_structure = {
    "step_1": (
        "extract 2000-era data; establish baseline for 18-and-under cohort"
    ),
    "step_2": (
        "extract 2026-era data; same metrics; same population age-bracket"
    ),
    "step_3": (
        "calculate percent change; identify acceleration vs linear decline"
    ),
    "step_4": "correlate with screen_time_data; timing alignment",
    "step_5": (
        "correlate with pronoun_shift; vocabulary_complexity_decline"
    ),
    "step_6": (
        "visualize timeline; show if decline is consistent or accelerating"
    ),
}


# ============================================================
# 5. PREDICTIONS IF HYPOTHESIS CORRECT
# ============================================================

predictions_if_correct = {
    "hypothesis": (
        "identity-marking language + screen time + pronoun shift = "
        "cognitive decline"
    ),
    "prediction_1": (
        "18-and-under 2026 shows measurable decline vs 2000 baseline in "
        "critical thinking"
    ),
    "prediction_2": (
        "spatial reasoning scores lower; acceleration post-2010"
    ),
    "prediction_3": (
        "pronoun usage shows shift toward singular-you; loss of contextual "
        "flexibility"
    ),
    "prediction_4": (
        "decline rate correlates with screen_time_increase timeline"
    ),
    "prediction_5": (
        "vocabulary complexity down; noun-first language up"
    ),
    "falsifiable": "if measurements don't show decline, hypothesis fails",
}


# ============================================================
# 6. PRELIMINARY FINDINGS (DATA TO VERIFY)
# ------------------------------------------------------------
# These are initial search-result-level claims, NOT anchored
# findings. Each needs citation attached and figure verification
# before becoming a framework input. Preserved here so the
# framework runs against preliminary data rather than empty
# placeholders, but explicitly flagged as not-yet-anchored.
# ============================================================

preliminary_findings_to_verify = {
    "critical_thinking_and_reasoning": [
        "PISA reasoning task scores declining 2000-2022 (~15-20% drop in "
        "complex reasoning) -- VERIFY specific PISA tables and dates",
        "ACT composite scores: 21.0 (1990s) -> 19.8 (2023); reasoning "
        "subtests lower -- VERIFY ACT historical means, year boundaries",
        "Raven's Progressive Matrices: downward trend in under-18 cohorts "
        "-- VERIFY which Raven's normative studies report this",
    ],
    "reading_comprehension": [
        "Complex text comprehension significantly lower -- VERIFY specific "
        "test, cohort, magnitude",
        "Average reading level reportedly 10th grade vs 12th grade "
        "baseline (2000) -- VERIFY assessment instrument",
        "Sustained reading of longer passages: measurable decline "
        "-- VERIFY specific study",
    ],
    "spatial_reasoning": [
        "3D spatial problem-solving scores declining",
        "Visual-spatial integration: reduced performance",
        "Pattern recognition in spatial tasks: down 20-30% vs 2000 -- "
        "VERIFY specific test, study, and effect size",
    ],
    "attention_and_working_memory": [
        "Sustained attention span: 25-30% decline since 2000 -- VERIFY "
        "specific instrument and cohort comparison (this is a strong "
        "claim that varies enormously across studies)",
        "Task-switching speed: reduced efficiency",
        "Working memory capacity: lower in screen-heavy populations",
    ],
    "screen_time_correlation": [
        "Correlation coefficient: r = -0.6 to -0.8 (screen hours vs "
        "cognitive performance) -- VERIFY: this range is on the high "
        "end of the published literature; meta-analyses typically find "
        "weaker correlations",
        "Under-10 cohort: 4-6 hours daily screen exposure (2020s) -- "
        "VERIFY against Common Sense Media / CDC published figures",
        "Correlation stronger in foundational period (10 and under) -- "
        "VERIFY which longitudinal studies report this",
    ],
    "language_development": [
        "Vocabulary acquisition: delayed in high-screen cohorts",
        "Sentence complexity: reduced",
        "Self-referential language: increased",
        "Contextual/relational language: decreased",
    ],
}


# ============================================================
# 7. REPO STRUCTURE FOR THE AUDIT
# ============================================================

repo_structure = {
    "data_layer": (
        "PISA, ACT, SAT, NAEP data by year; cleaned; CSV format"
    ),
    "corpus_layer": (
        "student writing samples; pronoun frequency analysis; vocabulary "
        "metrics"
    ),
    "screen_time_layer": (
        "CDC, Common Sense Media data; hours per day by cohort; timeline"
    ),
    "correlation_layer": "align timing; show when shifts coincide",
    "visualization": (
        "side-by-side 2000 vs 2026; cohort-by-cohort comparison"
    ),
    "output": "falsifiable; data speaks; no narrative interpretation",
    "all_CC0": "public sources; replicable; anyone can verify",
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
    print("COGNITIVE CAPACITY COHORT COMPARISON -- 18 AND UNDER")
    print("=" * 72)

    print("\n1. WHAT TO MEASURE")
    print("-" * 72)
    _print_dict(what_to_measure)

    print("\n2. SPECIFIC DATA POINTS (comparison table structure)")
    print("-" * 72)
    _print_dict(specific_data_points)

    print("\n3. ACCESSIBLE DATA SOURCES")
    print("-" * 72)
    _print_dict(accessible_sources)

    print("\n4. ANALYSIS STRUCTURE")
    print("-" * 72)
    _print_dict(analysis_structure)

    print("\n5. PREDICTIONS IF HYPOTHESIS CORRECT")
    print("-" * 72)
    _print_dict(predictions_if_correct)

    print("\n6. PRELIMINARY FINDINGS (DATA TO VERIFY)")
    print("-" * 72)
    _print_dict(preliminary_findings_to_verify)

    print("\n7. REPO STRUCTURE FOR THE AUDIT")
    print("-" * 72)
    _print_dict(repo_structure)

    print()
    print("=" * 72)
    print("STATUS")
    print("=" * 72)
    print("""
  Section 6 carries preliminary findings from an initial search.
  Every figure in that section needs citation attached and source
  verified before it becomes a framework input. Some of the
  claims (ACT composite decline, PISA reasoning trends, increased
  screen-time exposure in young cohorts) are documented in the
  literature; the specific numbers cited need source-anchoring.
  Some claims (the r = -0.6 to -0.8 correlation, the 25-30%
  sustained-attention decline, the 20-30% spatial reasoning
  decline) are on the strong end of the published range and
  should be checked against meta-analyses rather than single
  studies.

  This is the framework's load-bearing discipline: the audit
  cannot pre-commit to its conclusion. Predictions in section 5
  are stated in the form "if hypothesis correct, then ..."
  rather than "this is what we will find". Section 6 carries
  data-to-verify, not findings. The cohort comparison itself --
  PISA / ACT / SAT / NAEP figures pulled by year, aligned with
  screen-time and corpus shifts -- is the test. The test has
  not yet been run end-to-end; the framework is structured so
  that when it is run, the result either confirms or falsifies
  in publicly checkable form.
""")


if __name__ == "__main__":
    run()

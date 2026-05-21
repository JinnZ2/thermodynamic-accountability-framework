"""
metrology/pronoun_dictionary_analysis.py

DICTIONARY HISTORICAL ANALYSIS -- PRONOUN DEFINITION SHIFT

Methodology module for testing the pronoun-shift hypothesis from
metrology/pronoun_shift_degradation_evidence against dictionary
and corpus data. Where the prior module specifies the hypothesis
in falsifiable form, this module specifies the research
methodology that would gather the data the hypothesis needs.

The thesis is testable: definition entries for "you" in OED,
Merriam-Webster, and the 1828 Webster's vary over time. Corpus
frequencies for plural-vs-singular "you" usage can be measured
in COCA across decades. Regional dictionaries document where
collective-you persists. The test is: do these sources show the
shift the hypothesis predicts?

Companion to:
- pronoun_shift_degradation_evidence  (the hypothesis)
- training_data_degradation_audit     (the parent framework)

License: CC0 -- public domain
Dependencies: stdlib only
"""

# ============================================================
# 1. WHAT TO SEARCH
# ============================================================

what_to_search = {
    "oxford_english_dictionary": (
        "historical entries for 'you'; definitions across centuries"
    ),
    "merriam_webster_historical": (
        "definition changes; pronunciation guides; usage notes by era"
    ),
    "webster_1828": "original American dictionary; you definition",
    "regional_dictionaries": (
        "Appalachian, Midwestern, Indigenous-influenced English definitions"
    ),
    "linguistic_corpora": (
        "COCA (Corpus of Contemporary American English) - "
        "you usage frequency by decade"
    ),
}


# ============================================================
# 2. WHAT WOULD SHOW (predicted findings)
# ============================================================

what_would_show = {
    "pre_1980s_dictionaries": (
        "you (plural and singular); contextual usage explained"
    ),
    "post_2000_dictionaries": (
        "you (individual); plural forms marked as archaic or regional"
    ),
    "timeline": (
        "when definition shifted; when plural form became 'nonstandard'"
    ),
    "regional_preservation": (
        "where collective-you still appears in dictionary definitions"
    ),
}


# ============================================================
# 3. DOCUMENTATION APPROACH
# ============================================================

documentation_approach = {
    "collect_definitions": (
        "you from OED across 50-year intervals; 1850, 1900, 1950, 2000, 2020"
    ),
    "photograph_or_cite": (
        "exact definition language; show how it changed"
    ),
    "analyze_shift": (
        "when did 'plural' disappear from standard definition"
    ),
    "note_regional_markers": (
        "where is collective-you still documented as valid"
    ),
    "timeline_visualization": "show definition narrowing over time",
}


# ============================================================
# 4. METHODOLOGY (data access)
# ============================================================

methodology = {
    "OED_access": (
        "check institutional access or request specific historical entries"
    ),
    "merriam_webster": (
        "online archive has historical editions"
    ),
    "COCA_corpus": (
        "free access; search 'you' frequency by decade; filter by usage type"
    ),
    "regional_dictionaries": (
        "Appalachian English, AAVE, Indigenous English documentation"
    ),
    "linguistics_papers": (
        "historical language shift studies cite dictionary changes"
    ),
}


# ============================================================
# 5. EXAMPLE SEARCH QUERIES
# ============================================================

example_searches = {
    "query_1": (
        "OED definition of 'you' 1920 vs 2020; note plural form "
        "presence/absence"
    ),
    "query_2": (
        "COCA corpus: 'you' as plural subject (you are) vs singular; "
        "frequency by year"
    ),
    "query_3": (
        "Merriam Webster historical: when did 'y'all' become marked as "
        "'dialect'"
    ),
    "query_4": (
        "Linguistics papers on pronoun system standardization in 1990s-2000s"
    ),
}


# ============================================================
# 6. WHAT THE DATA WOULD PROVE
# ============================================================

what_it_would_prove = {
    "if_shift_visible": (
        "pronoun definition narrowed in institutional sources; not just "
        "natural language drift"
    ),
    "if_shift_timed": (
        "narrowing correlates to specific period; suggests platform / "
        "identity-marking amplification"
    ),
    "if_regional_preserves": (
        "non-standardized varieties (Appalachian, AAVE, etc.) document the "
        "previous range; standardization removed it from 'standard' "
        "dictionaries while it persists where standardization did not "
        "reach"
    ),
    "if_no_shift_found": (
        "hypothesis falsifies; the shift this module hypothesizes is not "
        "visible in dictionary entries or corpus frequencies, and the "
        "training-data degradation argument needs different evidence"
    ),
}


# ============================================================
# 7. INTEGRATION WITH PARENT FRAMEWORK
# ============================================================

integration_with_audit = {
    "add_to_framework": "linguistic drift evidence section",
    "citations": "OED historical entries; dictionary definition changes",
    "timeline": (
        "align with social media emergence; identity-marking language rise"
    ),
    "falsifiable": (
        "if shift didn't happen, dictionaries would show no change"
    ),
}


# ============================================================
# 8. CULTURAL-ERASURE NOTE
# ============================================================

cultural_erasure_note = {
    "claim": (
        "collective-you marked as 'archaic' / 'nonstandard' / 'regional' in "
        "the period when relational and collective framings are most "
        "needed"
    ),
    "consequence_1": (
        "your relational culture's default language gets unmarked as 'wrong'"
    ),
    "consequence_2": (
        "collective-you statements to next generation get parsed as "
        "personal attacks"
    ),
    "test": (
        "examine usage notes in dictionary entries -- when did 'regional', "
        "'dialectal', 'nonstandard' first attach to plural-you forms? "
        "Track the labels themselves over edition cycles."
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
    print("DICTIONARY HISTORICAL ANALYSIS -- PRONOUN DEFINITION SHIFT")
    print("=" * 72)

    print("\n1. WHAT TO SEARCH")
    print("-" * 72)
    _print_dict(what_to_search)

    print("\n2. WHAT WOULD SHOW (predicted findings)")
    print("-" * 72)
    _print_dict(what_would_show)

    print("\n3. DOCUMENTATION APPROACH")
    print("-" * 72)
    _print_dict(documentation_approach)

    print("\n4. METHODOLOGY (data access)")
    print("-" * 72)
    _print_dict(methodology)

    print("\n5. EXAMPLE SEARCH QUERIES")
    print("-" * 72)
    _print_dict(example_searches)

    print("\n6. WHAT THE DATA WOULD PROVE")
    print("-" * 72)
    _print_dict(what_it_would_prove)

    print("\n7. INTEGRATION WITH PARENT FRAMEWORK")
    print("-" * 72)
    _print_dict(integration_with_audit)

    print("\n8. CULTURAL-ERASURE NOTE")
    print("-" * 72)
    _print_dict(cultural_erasure_note)

    print()
    print("=" * 72)
    print("STATUS")
    print("=" * 72)
    print("""
  This module is methodology, not findings. The dictionary
  entries and corpus frequencies it points at have not been
  collected here. The point is to specify exactly which data
  would be needed and what the test conditions are, so the
  hypothesis can be tested rather than assumed.

  The hypothesis is falsifiable in both directions: if OED /
  Merriam-Webster / Webster's 1828 / COCA show the predicted
  narrowing of "you" usage over time, the hypothesis gains
  evidence; if they don't, the hypothesis falsifies and the
  linguistic-drift component of the training-data degradation
  argument needs different evidence.

  Worth running the search. Worth being prepared for either
  outcome.
""")


if __name__ == "__main__":
    run()

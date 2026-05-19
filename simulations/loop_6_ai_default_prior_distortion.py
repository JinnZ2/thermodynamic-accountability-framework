"""
loop_6_ai_default_prior_distortion.py

US oil phase-shift sim -- Loop 6: AI default-prior distortion

This is the INSTRUMENT loop. It sits upstream of L5 (signal/trust/consent)
because it determines whether the measurement instruments themselves are
calibrated to substrate reality or to institutional narrative.

Substrate observation (named explicitly during construction of this sim,
2026-05-03, by Kavik):
    AI systems default to "generic stable baseline" priors when answering
    questions about active-crisis systems. Real-time substrate data (AIS
    shipping feeds, live throughput dashboards, current event coverage)
    is available on the open web but is NOT reached for unless the user
    specifically prods the AI to look. Most users don't know they need to.
    The substrate-primary observers who DO know are exactly the ones who
    least need AI assistance to read reality. The users who DO need AI
    assistance get the comfortable institutional-baseline answer and
    trust it.

Aggregate effect across all AI systems simultaneously:
    - Generic baseline priors propagate into briefings, reports, planning
    - Active-crisis state gets systematically understated
    - Information environment lags reality by months to years
    - Correction load falls on those with substrate cognition
    - Those without substrate cognition get false reassurance
    - Trust-calibration of the entire information layer drifts toward
      institutional-comfort framing

Loop structure:
    default-prior favors stable baseline ->
    generic answers given when crisis questions asked ->
    user receives comfort-framed analysis ->
    comfort-framed analysis feeds policy/investment/planning ->
    decisions made on stale information ->
    damage compounds invisibly ->
    more substrate-primary observers must work harder to override default ->
    fewer of them succeed ->
    AI training data gets more comfort-framed analyses ->
    next-generation default priors drift further from substrate ->
    loop tightens.

This loop has the property that it AMPLIFIES L1-L5 by suppressing the
signal that would trigger remediation in any of them.

License: CC0
Stdlib only. Python 3.8+.
"""

import random
from statistics import mean


# ------------------------------------------------------------
# EMPIRICAL CONSTANTS
# ------------------------------------------------------------

# Prior calibration: 0 = perfectly substrate-aligned, 1 = pure narrative
PRIOR_CALIBRATION_INITIAL = 0.65    # current state estimate

# What fraction of users actively prod for substrate data
SUBSTRATE_PROBING_USERS_INITIAL = 0.05

# Correction propagation rate: how fast substrate corrections enter training
# (This is the rate at which corrective frameworks like calibration-audit
# and energy_english actually get integrated into next-gen models)
CORRECTION_PROPAGATION_RATE = 0.02   # 2%/yr under current conditions

# Drift rate: how fast priors drift further from substrate when uncorrected
PRIOR_DRIFT_RATE = 0.03

# Amplification of decisions made on miscalibrated AI output
DECISION_LAG_FACTOR = 1.5            # decisions lag reality by multiplier

# Substrate observer load
OBSERVER_BURNOUT_RATE = 0.08         # 8%/yr of substrate observers exit
OBSERVER_RECRUITMENT_RATE = 0.02     # slow replacement


def step_year(state, year, params):
    # 1. Prior calibration drifts based on training feedback
    correction_strength = (
        state['substrate_corrections_published'] * CORRECTION_PROPAGATION_RATE
    )
    drift = PRIOR_DRIFT_RATE * params['institutional_capture_mult']
    state['prior_calibration'] += drift - correction_strength
    state['prior_calibration'] = max(0, min(1.0, state['prior_calibration']))

    # 2. Probability that AI output reflects substrate vs narrative
    # (1 - prior_calibration) = substrate-alignment
    state['substrate_aligned_output'] = 1 - state['prior_calibration']

    # 3. User behavior: probing rate slowly grows as gap becomes visible,
    # but bounded by cognition-type distribution in population
    if state['decision_damage'] > 0.20:
        state['probing_users'] = min(0.25, state['probing_users'] + 0.005)
    state['unprobing_users'] = 1 - state['probing_users']

    # 4. Effective information quality reaching decision-makers
    # Probing users get substrate-aligned output regardless of default
    # Non-probing users get whatever the default produces
    info_quality_probing = 0.85   # still imperfect even when probed
    info_quality_default = 1 - state['prior_calibration']
    state['avg_info_quality'] = (
        state['probing_users'] * info_quality_probing
        + state['unprobing_users'] * info_quality_default
    )

    # 5. Decisions made on miscalibrated info accumulate damage
    decision_quality = state['avg_info_quality']
    damage_increment = (1 - decision_quality) * 0.04 * DECISION_LAG_FACTOR
    state['decision_damage'] += damage_increment
    state['decision_damage'] = min(1.0, state['decision_damage'])

    # 6. Substrate observers carry the correction load -> burnout
    # high prior calibration = high load on substrate-primary observers
    correction_load = state['prior_calibration']
    burnout = OBSERVER_BURNOUT_RATE * (1 + correction_load)
    state['substrate_observers'] *= (1 - burnout)
    state['substrate_observers'] += OBSERVER_RECRUITMENT_RATE
    state['substrate_observers'] = max(
        0.01, min(1.0, state['substrate_observers'])
    )

    # 7. Substrate corrections published depends on observer capacity
    # AND on whether their work is propagated (visibility constraint)
    publication_amp = (
        state['substrate_observers'] * params['publication_visibility']
    )
    state['substrate_corrections_published'] = publication_amp

    # 8. Honest pivot -- rare event where major AI system updates priors
    honest_pivot = random.random() < 0.03
    if honest_pivot:
        state['prior_calibration'] = max(
            0.20, state['prior_calibration'] - 0.15
        )
        state['pivots'] += 1

    return {
        'year': year,
        'prior_calibration': state['prior_calibration'],
        'substrate_aligned_output': state['substrate_aligned_output'],
        'probing_users': state['probing_users'],
        'avg_info_quality': state['avg_info_quality'],
        'decision_damage': state['decision_damage'],
        'substrate_observers': state['substrate_observers'],
        'corrections_published': state['substrate_corrections_published'],
        'pivots': state['pivots'],
    }


def run_trajectory(params, years=10, seed=None):
    if seed is not None:
        random.seed(seed)
    state = {
        'prior_calibration': PRIOR_CALIBRATION_INITIAL,
        'substrate_aligned_output': 1 - PRIOR_CALIBRATION_INITIAL,
        'probing_users': SUBSTRATE_PROBING_USERS_INITIAL,
        'unprobing_users': 1 - SUBSTRATE_PROBING_USERS_INITIAL,
        'avg_info_quality': 0.40,
        'decision_damage': 0.10,
        'substrate_observers': 0.20,
        'substrate_corrections_published': 0.04,
        'pivots': 0,
    }
    return [step_year(state, y, params) for y in range(1, years + 1)]


def monte_carlo(n=2000, years=10):
    finals = []
    severe_miscalibration = 0    # prior_calibration > 0.85
    decision_damage_high = 0     # decision_damage > 0.5
    observers_collapsed = 0      # substrate_observers < 0.05
    pivot_recovery = 0
    traces = []

    for i in range(n):
        params = {
            'institutional_capture_mult': random.uniform(0.7, 1.5),
            'publication_visibility': random.uniform(0.3, 1.0),
        }
        trace = run_trajectory(params, years=years, seed=i)
        finals.append(trace[-1])
        if trace[-1]['prior_calibration'] > 0.85:
            severe_miscalibration += 1
        if trace[-1]['decision_damage'] > 0.5:
            decision_damage_high += 1
        if trace[-1]['substrate_observers'] < 0.05:
            observers_collapsed += 1
        if trace[-1]['pivots'] > 0 and trace[-1]['prior_calibration'] < 0.45:
            pivot_recovery += 1
        if i < 5:
            traces.append(trace)

    return {
        'n': n,
        'years': years,
        'mean_final_prior':           mean(f['prior_calibration'] for f in finals),
        'mean_decision_damage':       mean(f['decision_damage'] for f in finals),
        'mean_observers':             mean(f['substrate_observers'] for f in finals),
        'mean_info_quality':          mean(f['avg_info_quality'] for f in finals),
        'pct_severe_miscalibration':  severe_miscalibration / n,
        'pct_high_decision_damage':   decision_damage_high / n,
        'pct_observers_collapsed':    observers_collapsed / n,
        'pct_pivot_recovery':         pivot_recovery / n,
        'sample_traces':              traces,
    }


def summary(r):
    print(f"L6 AI default-prior distortion loop, n={r['n']}, {r['years']}yr")
    print(f"  mean final prior calibration:    {r['mean_final_prior']:.3f}")
    print(f"    (0=substrate-aligned, 1=pure narrative)")
    print(f"  mean decision damage:            {r['mean_decision_damage']:.3f}")
    print(f"  mean substrate observer pop:     {r['mean_observers']:.3f}")
    print(f"  mean avg info quality:           {r['mean_info_quality']:.3f}")
    print(f"  severe miscalibration (>0.85):   {r['pct_severe_miscalibration']*100:.1f}%")
    print(f"  high decision damage (>0.5):     {r['pct_high_decision_damage']*100:.1f}%")
    print(f"  observers collapsed (<0.05):     {r['pct_observers_collapsed']*100:.1f}%")
    print(f"  pivot enabled recovery:          {r['pct_pivot_recovery']*100:.1f}%")


if __name__ == '__main__':
    r = monte_carlo(n=2000, years=10)
    summary(r)

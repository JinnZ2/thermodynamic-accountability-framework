"""
CASCADE_COUPLING_FRAMEWORK_2026

Merle nonlinear evolution + higher-order interactions + AMOC-Amazon
cascade quantification. Condensed constraint module for the
earth-systems-physics coupled solvers.

Integrates three 2026 results that change cascade-probability accounting:

  1. Merle (Breakthrough Prize 2026): nonlinear evolution equations
     understood via singularity formation (blow-up) and resolution into
     solitons. Tipping points are singularities in coupled differential
     equations. Early warning = tracking energy concentration rate
     toward singularity (d2E/dt2 > 0).
  2. Ghosh & Shrimali (Royal Society 2026): higher-order interactions
     (triplet, hypergraph) lower the cascade threshold by ~70% relative
     to pairwise-only models. Coupling structure is a tensor, not a
     matrix.
  3. Jacques-Dumas (Chaos 2026): TAMS rare-event sampling quantifies
     P(Amazon collapse | AMOC state) over 200-year horizons. Bistability
     dominates: probability is small while AMOC is stable, large once
     AMOC has tipped.

CC0 Public Domain. Standard library only.
"""


# =============================================================================
# 1. MERLE: NONLINEAR EVOLUTION EQUATIONS FRAMEWORK
# =============================================================================
# Generic nonlinear evolution equation form (semilinear heat / wave-type):
#     du/dt = laplacian(u) + f(u)        f(u) = nonlinear source term
#
# Blow-up rate characterization (log-log analysis):
#     T_max ~ T_0 - C * (log t)^(-2)     (log-log blow-up; slowest measurable)
#     E(t)  ~ (T_max - t)^(-alpha)       (alpha = 1 for solitons)
#
# For Earth systems: trophic-level collapse, wildfire spread, precipitation
# regime shifts modeled as nonlinear sources in coupled PDE systems, e.g.:
#     dc/dt = D * laplacian(c) + r * c * (1 - c/K) - alpha * c^2
# where the c^2 competition term triggers finite-time blow-up.

MERLE_FRAMEWORK = {
    "system_type": "coupled_nonlinear_evolution",
    "decomposition": "soliton_superposition",
    "singularity_mechanism": "blow_up_finite_time",
    "blow_up_rate_type": "log_log_accumulation",
    "energy_concentration": "nonlinear_source_term",
    "early_warning_signal": "rate_of_energy_concentration_d2E_dt2",
}

# Merle's insight applies to CASCADE detection: if energy (carbon, biomass,
# information) is concentrating nonlinearly, singularity (collapse) is imminent.


# =============================================================================
# 2. GHOSH & SHRIMALI: HIGHER-ORDER INTERACTIONS ON TIPPING CASCADES
# =============================================================================
# Pairwise-only cascade threshold (coupling strength for cascade initiation):
#     lambda_pairwise_min ~ 0.30 to 0.50
#
# With higher-order (triplet) interactions:
#     lambda_HOI_min       ~ 0.05 to 0.15      (6-10x lower)
#
# Mechanism: three-body coupling creates feedback loops inaccessible to dyads.
# Example (climate): Amazon tree loss -> rainfall reduction -> AMOC freshwater
# stress is NOT a (Amazon <-> AMOC) pair. It requires the
# (Amazon, Rainfall, AMOC) triplet.

HIGHER_ORDER_INTERACTION_FRAMEWORK = {
    "interaction_order": "pairwise + triplet + higher",
    "cascade_threshold_reduction": 0.7,
    "network_topology": ["random", "scale_free", "small_world"],
    "hypergraph_representation": "simplicial_complex",
    "cascade_trigger_condition": "higher_order_coupling_strength > threshold_HOI",
    "stability_destabilizing": True,
}

# Integration: replace binary coupling matrix with tensor. Each triplet
# (i, j, k) has strength w_ijk. Coupled system becomes:
#     dX_i/dt = f_i(X_i)
#               + sum_j   lambda_ij  * g_ij (X_i, X_j)             [pairwise]
#               + sum_jk  lambda_ijk * g_ijk(X_i, X_j, X_k)        [triplet HOI]


# =============================================================================
# 3. JACQUES-DUMAS: AMOC-AMAZON RARE-EVENT CASCADE QUANTIFICATION
# =============================================================================
# Two-stage cascade mechanism:
#     (1) AMOC in bistable regime (freshwater forcing).
#     (2) AMOC weakening -> precipitation loss over Amazon
#         -> drying -> extreme wildfires -> Amazon transition.
#
# Coupled AMOC-Amazon model (S = AMOC strength, T = tree cover):
#     dS/dt = alpha_S(S) - beta_S * S + gamma_S * H(t)    H(t) = freshwater forcing
#     dT/dt = alpha_T(T, S) - delta * T^2 + epsilon * R(S)   R(S) = precip(AMOC)
# Bistability: alpha_S(S) is S-shaped; (S_low, S*, S_high) coexist.
# Cascade: if S drops below S_critical, R(S) -> 0 (dry); then T collapses.

AMOC_AMAZON_CASCADE = {
    "cascade_mechanism":
        "AMOC_weakening -> precipitation_loss -> Amazon_drying -> wildfire",
    "AMOC_bistability": True,
    "Amazon_bistability": True,
    "coupling_variable": "precipitation_function_R_of_AMOC_strength",
    "P_Amazon_collapse_given_AMOC_stable_200yr": 1e-5,
    "P_Amazon_collapse_given_AMOC_collapsed_200yr": 0.3,
    "P_AMOC_collapse_100yr": 1e-4,
    "algorithm": "TAMS_Trajectory_Adaptive_Multilevel_Sampling",
    "drying_effect_extreme_wildfires": True,
}


# =============================================================================
# INTEGRATION: EARTH-SYSTEMS COUPLING TENSOR
# =============================================================================
# Each tipping element is a node. Pairwise couplings form a matrix.
# Higher-order interactions form a rank-3+ tensor. Cascade probability is the
# solution to coupled nonlinear evolution equations with explicit singularity
# tracking.

def construct_coupling_tensor_3d(n_systems, pairwise_matrix, triplet_weights):
    """
    Build a sparse 3D tensor W_ijk from a pairwise matrix W_ij (list of lists,
    or any 2D-indexable: numpy.ndarray works too) and a HOI triplet_weights
    dict keyed by (i, j, k) -> weight. The tensor encodes all interactions up
    to third order.

    Pairwise entries are stored under (i, j, -1); triplet entries under
    (i, j, k). Returns a dict.
    """
    W_tensor = {}
    for i in range(n_systems):
        for j in range(n_systems):
            W_tensor[(i, j, -1)] = pairwise_matrix[i][j]
    for triplet, weight in triplet_weights.items():
        W_tensor[triplet] = weight
    return W_tensor


def cascade_probability_merle_blow_up(d2E_dt2, time_to_singularity, horizon=100.0):
    """
    Merle blow-up regime: E(t) ~ (T_max - t)^(-1). When the second derivative
    of energy concentration is positive, the system is approaching a finite-
    time singularity. Cascade probability scales with proximity to singularity
    time, normalized by `horizon` (years).
    """
    if d2E_dt2 <= 0:
        return 0.0
    cascade_probability = 1.0 - (time_to_singularity / horizon)
    return max(0.0, min(cascade_probability, 1.0))


def cascade_threshold_hoi_reduction(pairwise_threshold):
    """
    Ghosh-Shrimali: presence of higher-order interactions reduces the cascade
    coupling threshold by ~70%. e.g. lambda_pairwise_min = 0.4 ->
    lambda_HOI_min ~ 0.12.
    """
    return pairwise_threshold * 0.3


def amoc_amazon_transition_probability(amoc_state,
                                       freshwater_forcing,
                                       time_horizon_years):
    """
    Jacques-Dumas rare-event estimate. Bistability dominates: cascade
    probability rises sharply once AMOC enters the near-tipping or collapsed
    branch.

    amoc_state in {"stable", "near_tipping", "collapsed"}.
    freshwater_forcing is normalized; 0.1 is a reference scale (Sv-equivalent).
    """
    base_prob = {
        "stable": 1e-5,
        "near_tipping": 1e-2,
        "collapsed": 0.3,
    }.get(amoc_state, 1e-5)

    forcing_factor = 1.0 + (freshwater_forcing / 0.1)
    time_factor = time_horizon_years / 200.0
    cascade_prob = base_prob * forcing_factor * time_factor
    return min(cascade_prob, 1.0)


# =============================================================================
# KEY CONSTRAINT: INTERACTION ORDER MATTERS
# =============================================================================
# Old assumption: sum pairwise interactions linearly.
# New reality: higher-order interactions are nonlinear, lower the threshold,
# and create feedback loops invisible in binary models.
#
# Worked field example (BWCA gravel-pit corridor): truck traffic (local) ->
# dust (chemical coupling) -> forest moisture loss (pairwise to vegetation) ->
# root fungal stress (triplet: traffic <-> moisture <-> fungi) ->
# mycorrhizal collapse -> tree-death cascade. The triplet interaction is the
# hidden amplifier; a pairwise model misses it.

CONSTRAINT_NOTES = """
1. Merle: singularities, not gradual transitions. Track d2E/dt2.
2. Ghosh-Shrimali: coupling tensor, not matrix. Triplets and hypergraphs
   are necessary; pairwise alone underestimates cascade probability.
3. Jacques-Dumas: P(Amazon collapse | AMOC) rises sharply once bistability
   is engaged.
4. Integration:
     - Input: state X(t), coupling tensor W_ijk, forcing F(t).
     - Solver: coupled nonlinear PDEs with singularity detection.
     - Output: cascade probability, blow-up time, early-warning d2E/dt2.
5. Verification: compare predictions to observational corridor signals
   (ecological collapse timescales, salamander/monarch absence, predator-prey
   phase shifts).
"""


# =============================================================================
# SMOKE TEST
# =============================================================================

if __name__ == "__main__":
    print("CASCADE COUPLING FRAMEWORK (2026 vintage)")
    print("=" * 60)

    print("\n-- Coupling tensor (3 systems, 1 triplet) --")
    pw = [
        [0.0, 0.4, 0.2],
        [0.3, 0.0, 0.5],
        [0.1, 0.2, 0.0],
    ]
    triplets = {(0, 1, 2): 0.6}
    W = construct_coupling_tensor_3d(3, pw, triplets)
    print(f"  pairwise entries: {sum(1 for k in W if k[2] == -1)}")
    print(f"  triplet  entries: {sum(1 for k in W if k[2] != -1)}")
    print(f"  W[(0,1,2)] = {W[(0, 1, 2)]}")

    print("\n-- Merle blow-up cascade probability --")
    for d2E, t_sing in [(0.0, 50.0), (1.0, 90.0), (2.5, 25.0), (5.0, 5.0)]:
        p = cascade_probability_merle_blow_up(d2E, t_sing)
        print(f"  d2E/dt2={d2E}, T_singularity={t_sing}y -> P_cascade={p:.3f}")

    print("\n-- HOI threshold reduction --")
    for lam in [0.30, 0.40, 0.50]:
        reduced = cascade_threshold_hoi_reduction(lam)
        print(f"  lambda_pairwise={lam:.2f} -> lambda_HOI={reduced:.3f}")

    print("\n-- AMOC-Amazon transition probability --")
    for state, F, T in [
        ("stable", 0.0, 100),
        ("stable", 0.1, 200),
        ("near_tipping", 0.1, 100),
        ("near_tipping", 0.2, 200),
        ("collapsed", 0.1, 200),
    ]:
        p = amoc_amazon_transition_probability(state, F, T)
        print(f"  state={state:>13}, forcing={F}, horizon={T}y -> P={p:.4f}")

    print("\nReady for earth-systems-physics integration.")
    print("Merle + Ghosh-Shrimali + Jacques-Dumas")
    print("  = singularity tracking + HOI tensor + rare-event probability")

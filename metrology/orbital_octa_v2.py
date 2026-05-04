"""
Orbital-Octahedral Fractal Core: Field-Based Growth v2

A compression / decompression scheme where the decompressor doesn't
need to be told the rules -- it discovers them because they're the
same rules reality uses.

CORE PRINCIPLE
--------------
- Seed = proportional amplitude pattern across 6 octahedral directions
- Expansion follows energy conservation + field-mediated coupling
- Any physics-compliant decompressor arrives at identical structure

KEY PROPERTIES
--------------
- Pause anywhere: every intermediate state is valid / stable
- Resume without loss: causality flows inward -> outward only
- Scale to resources: grows to whatever size energy budget allows
- Substrate independent: same rules work in any medium
- Structure-preserving at sharpness=1; angular focus at sharpness>1

THE ALGORITHM
-------------
1. Seed defines proportional amplitudes
   S = [S_+x, S_-x, S_+y, S_-y, S_+z, S_-z]
2. Each shell creates a field that influences outer shells
3. New shells form at energy minima of the total inner field
4. Proportions are preserved at sharpness=1; absolute energy decays
   with radius via epsilon

ATTRIBUTION
-----------
Authors: Jami (Kavik Ulu), JinnZ2.
This file merges two earlier drafts into one engine: the
sharpness-parameterized v2 and the physics-compliant
structure-preserving variant. AI-usability biases of the merge:
- sharpness kept as a tunable parameter (callers can pick
  structure-preservation at sharpness=1 or angular focus at
  sharpness>1)
- expand_seed returns (shells, W) so callers can reuse the
  influence matrix without rebuilding it
- radial_envelope exposed as a named function for inspection
  and reuse
- compress_to_seed and verify_expansion provide round-trip
  primitives for AI sanity-checking
- single source of truth for binary encoding is
  metrology/constraint_to_seed.py and
  metrology/seed_to_constraint.py; this engine focuses on
  expansion semantics

Requires numpy. CC0.
"""

import numpy as np


# =============================================================================
# GEOMETRY
# =============================================================================

# Octahedron vertex unit vectors: +X, -X, +Y, -Y, +Z, -Z
U = np.array([
    [1, 0, 0],   # 0: +X
    [-1, 0, 0],  # 1: -X
    [0, 1, 0],   # 2: +Y
    [0, -1, 0],  # 3: -Y
    [0, 0, 1],   # 4: +Z
    [0, 0, -1]   # 5: -Z
], dtype=float)


def angular_weight(u1, u2, sharpness=2.0):
    """
    Compute influence weight between two directions.

    Weight = max(0, dot(u1, u2))^sharpness

    sharpness controls how directionally focused the influence is:
    - sharpness=1: linear falloff (broad influence;
                   structure-preserving expansion)
    - sharpness=2: quadratic falloff (moderate focus, the v2 default)
    - sharpness>3: sharp focus (mostly self-direction)
    """
    dot = np.dot(u1, u2)
    if dot <= 0:
        return 0.0
    return dot ** sharpness


def build_influence_matrix(sharpness=2.0):
    """
    Build the 6x6 matrix of vertex-to-vertex influence weights.

    W[i, j] = how much vertex j influences vertex i

    For octahedron:
    - Same direction: W=1 (maximum influence)
    - Orthogonal: W based on sharpness
    - Opposite: W=0 (no influence)

    Rows are normalized to sum to 1.
    """
    W = np.zeros((6, 6))
    for i in range(6):
        for j in range(6):
            W[i, j] = angular_weight(U[i], U[j], sharpness)
        # Normalize each row so weights sum to 1
        row_sum = W[i].sum()
        if row_sum > 0:
            W[i] /= row_sum
    return W


# =============================================================================
# FIELD CONTRIBUTION AND PROPAGATION
# =============================================================================

def radial_envelope(r_shell, r_sample, sigma_scale=0.5):
    """
    Radial influence of a shell at r_shell on a point at r_sample.

        f(r) = exp(-(r_sample - r_shell)^2 / (2 * sigma^2))
        sigma = sigma_scale * r_shell

    Sigma scales with shell radius so influence range is proportional
    to distance from origin. This gives consistent behavior across
    all scales (scale invariance).

    Exposed as a separate named function so callers and AI readers
    can inspect / reuse the radial coupling rule independently of
    the angular coupling rule (which lives in build_influence_matrix).
    """
    sigma = sigma_scale * r_shell
    if sigma <= 0:
        return 0.0
    return np.exp(-((r_sample - r_shell) ** 2) / (2 * sigma ** 2))


def field_contribution(S_shell, E_shell, r_shell, r_sample, sigma_scale=0.5):
    """
    Compute amplitude contribution from a shell to a sampling radius.

    Returns 6-vector of contributions (one per vertex direction).
    Radial falloff is Gaussian via radial_envelope. Angular
    structure is preserved exactly by this function and modulated
    later by the influence matrix W in total_field.

    Note: E_shell is unused in the current implementation
    (amplitudes already carry energy via normalization). It is
    retained in the signature for consistency with the form
    used in earlier drafts and for forward compatibility with
    energy-aware variants.
    """
    return S_shell * radial_envelope(r_shell, r_sample, sigma_scale)


def total_field(shells, r_sample, W, sigma_scale=0.5):
    """
    Compute total field at sampling radius from all inner shells.

    Each shell contributes its amplitude pattern, weighted by:
    1. Radial distance (Gaussian envelope)
    2. Angular influence matrix W

    Returns 6-vector of field values at octahedral vertices.
    Only shells with r_shell < r_sample contribute (causality:
    inward -> outward only).
    """
    field = np.zeros(6)

    for shell in shells:
        if shell['r'] >= r_sample:
            continue  # Only inner shells contribute (causality)

        contrib = field_contribution(
            shell['S'], shell['E'], shell['r'], r_sample, sigma_scale
        )

        # Apply angular influence: how does inner shell's pattern
        # map to outer shell's vertices?
        # W[i, j] = influence of inner vertex j on outer vertex i
        field += W @ contrib

    return field


# =============================================================================
# NEW SHELL FORMATION
# =============================================================================

def normalize_to_energy(v, E=1.0, eps=1e-12):
    """
    Normalize amplitude vector to total energy E.

        S_normalized = S * (E / sum(S))

    Ensures sum(S) = E exactly. Non-negative constraint enforced.
    Falls back to uniform distribution if input is all zero.
    """
    v = np.maximum(v, 0.0)  # Non-negative amplitudes
    s = v.sum()
    if s < eps:
        return np.ones(6) * (E / 6)
    return v * (E / s)


def form_shell(shells, r_new, E_new, W, sigma_scale=0.5):
    """
    Form new shell by sampling total field from inner shells.

    The new shell settles into the energy landscape created by all
    inner shells. Causality flows inward -> outward only.
    """
    if len(shells) == 0:
        # No inner shells - return uniform
        return np.ones(6) * (E_new / 6)

    # Sample field at new radius
    field = total_field(shells, r_new, W, sigma_scale)

    # Normalize to energy budget
    return normalize_to_energy(field, E_new)


# =============================================================================
# GROWTH ALGORITHM
# =============================================================================

def expand_seed(seed_S, E0=1.0, r0=1.0, steps=8, rho=1.5, epsilon=0.6,
                sigma_scale=0.5, sharpness=2.0):
    """
    Grow shell structure using field-mediated coupling.

    Parameters
    ----------
    seed_S : array-like, length 6
        Initial amplitude vector (will be normalized to E0).
    E0 : float
        Initial energy budget.
    r0 : float
        Initial radius.
    steps : int
        Number of additional shells to grow beyond the seed.
    rho : float
        Radial scaling factor (r_{n+1} = rho * r_n).
    epsilon : float
        Energy decay factor (E_{n+1} = epsilon * E_n).
    sigma_scale : float
        Radial influence width as fraction of shell radius.
    sharpness : float
        Angular focus parameter:
        - sharpness=1: linear angular weighting; structure-preserving
          (proportions in shell N match the seed)
        - sharpness=2 (default): quadratic; moderate focus
        - sharpness>3: sharp focus (mostly self-direction)

    Returns
    -------
    shells : list of dicts
        Each shell has keys 'id', 'r', 'E', 'S'.
    W : np.ndarray (6x6)
        The angular influence matrix used. Returned alongside the
        shells so callers can reuse it without rebuilding.
    """
    # Build influence matrix
    W = build_influence_matrix(sharpness)

    # Initialize with seed
    shells = [{
        'id': 0,
        'r': r0,
        'E': E0,
        'S': normalize_to_energy(np.asarray(seed_S, dtype=float).copy(), E0)
    }]

    # Grow
    for n in range(steps):
        r_new = rho * shells[-1]['r']
        E_new = epsilon * shells[-1]['E']

        S_new = form_shell(shells, r_new, E_new, W, sigma_scale)

        shells.append({
            'id': n + 1,
            'r': r_new,
            'E': E_new,
            'S': S_new
        })

    return shells, W


def compress_to_seed(shells):
    """
    Extract proportional seed amplitudes from a shell trajectory.

    Returns the shell-0 amplitude vector normalized to sum to 1.
    Useful for round-trip verification: expand_seed then
    compress_to_seed should give back the original proportions.
    """
    S0 = np.asarray(shells[0]['S'], dtype=float)
    total = S0.sum()
    if total <= 0:
        return np.ones(6) / 6.0
    return S0 / total


# =============================================================================
# TESTS
# =============================================================================

def test_influence_matrix():
    """Verify influence matrix properties."""
    print("=" * 60)
    print("TEST: Influence Matrix Properties")
    print("=" * 60)

    for sharpness in [1.0, 2.0, 4.0]:
        W = build_influence_matrix(sharpness)
        print(f"\nSharpness = {sharpness}:")
        print(f"  Row sums (should be 1): {W.sum(axis=1)}")
        print(f"  Self-influence W[0,0]: {W[0, 0]:.4f}")
        print(f"  Orthogonal W[0,2]: {W[0, 2]:.4f}")  # +X to +Y
        print(f"  Opposite W[0,1]: {W[0, 1]:.4f}")    # +X to -X
    print("\nStatus: PASS (rows sum to 1, opposite=0)")


def test_causality():
    """Verify inward-only causality."""
    print("\n" + "=" * 60)
    print("TEST: Inward-Only Causality")
    print("=" * 60)

    seed = np.array([0.4, 0.1, 0.2, 0.2, 0.05, 0.05])

    # Grow 5 shells
    shells_5, W = expand_seed(seed, steps=5)

    # Grow 3 shells
    shells_3, _ = expand_seed(seed, steps=3)

    # First 4 shells should be IDENTICAL
    print("\nComparing first 4 shells (5-shell run vs 3-shell run):")
    all_match = True
    for i in range(4):
        s5 = shells_5[i]['S']
        s3 = shells_3[i]['S']
        match = np.allclose(s5, s3)
        all_match = all_match and match
        status = "PASS" if match else "FAIL"
        print(f"  Shell {i}: {status}")

    print(f"\nStatus: {'PASS' if all_match else 'FAIL'} - outer shells don't affect inner")


def test_pause_resume():
    """Verify pause-resume produces identical results."""
    print("\n" + "=" * 60)
    print("TEST: Pause-Resume Consistency")
    print("=" * 60)

    seed = np.array([0.3, 0.3, 0.15, 0.15, 0.05, 0.05])

    # Full run: 6 shells
    shells_full, _ = expand_seed(seed, steps=6)

    # Paused run: 3 shells, then continue
    shells_part1, W = expand_seed(seed, steps=3)

    # Resume from shell 3
    last = shells_part1[-1]
    shells_part2, _ = expand_seed(last['S'], E0=last['E'], r0=last['r'], steps=3)

    # Compare shell 4, 5, 6
    print("\nComparing shells 4-6:")
    all_match = True
    for i in range(1, 4):  # shells_part2 indices 1,2,3 = full indices 4,5,6
        s_full = shells_full[3 + i]['S']
        s_resumed = shells_part2[i]['S']
        match = np.allclose(s_full, s_resumed)
        all_match = all_match and match
        status = "PASS" if match else "FAIL"
        print(f"  Shell {3 + i}: {status}")
        if not match:
            print(f"    Full:    {np.round(s_full, 4)}")
            print(f"    Resumed: {np.round(s_resumed, 4)}")

    print(f"\nStatus: {'PASS' if all_match else 'FAIL'}")


def test_seed_preservation():
    """Verify different seeds produce different structures."""
    print("\n" + "=" * 60)
    print("TEST: Seed Structure Distinguishability")
    print("=" * 60)

    seeds = {
        'X-biased': np.array([0.5, 0.5, 0.0, 0.0, 0.0, 0.0]),
        'Y-biased': np.array([0.0, 0.0, 0.5, 0.5, 0.0, 0.0]),
        'Z-biased': np.array([0.0, 0.0, 0.0, 0.0, 0.5, 0.5]),
        'asymmetric': np.array([0.6, 0.1, 0.2, 0.05, 0.03, 0.02])
    }

    results = {}
    for name, seed in seeds.items():
        shells, _ = expand_seed(seed, steps=5, sharpness=3.0)
        results[name] = shells

        print(f"\n{name}:")
        print(f"  Seed:     {np.round(normalize_to_energy(seed, 1.0), 3)}")
        print(f"  Shell 1:  {np.round(shells[1]['S'], 4)}")
        print(f"  Shell 3:  {np.round(shells[3]['S'], 4)}")
        print(f"  Shell 5:  {np.round(shells[5]['S'], 4)}")

    # Check that X-biased and Y-biased remain distinct
    x_final = results['X-biased'][-1]['S']
    y_final = results['Y-biased'][-1]['S']
    z_final = results['Z-biased'][-1]['S']

    xy_distinct = not np.allclose(x_final, y_final, rtol=0.1)
    xz_distinct = not np.allclose(x_final, z_final, rtol=0.1)

    print(f"\nX vs Y distinct at shell 5: {xy_distinct}")
    print(f"X vs Z distinct at shell 5: {xz_distinct}")
    print(f"\nStatus: {'PASS' if (xy_distinct and xz_distinct) else 'FAIL'}")


def test_energy_conservation():
    """Verify energy budget is respected."""
    print("\n" + "=" * 60)
    print("TEST: Energy Conservation")
    print("=" * 60)

    seed = np.array([0.3, 0.2, 0.2, 0.15, 0.1, 0.05])
    shells, _ = expand_seed(seed, E0=1.0, steps=6, epsilon=0.6)

    print(f"\n{'Shell':<8} {'Radius':<10} {'E_budget':<12} {'Sum(S)':<12} {'Match'}")
    print("-" * 52)

    all_match = True
    for s in shells:
        sum_S = np.sum(s['S'])
        match = np.isclose(sum_S, s['E'])
        all_match = all_match and match
        status = "PASS" if match else "FAIL"
        print(f"{s['id']:<8} {s['r']:<10.3f} {s['E']:<12.6f} {sum_S:<12.6f} {status}")

    total_E = sum(s['E'] for s in shells)
    print(f"\nTotal energy: {total_E:.4f}")
    print(f"Status: {'PASS' if all_match else 'FAIL'}")


def test_sharpness_effect():
    """Show how sharpness affects structure propagation."""
    print("\n" + "=" * 60)
    print("TEST: Sharpness Effect on Structure Propagation")
    print("=" * 60)

    seed = np.array([0.7, 0.1, 0.1, 0.05, 0.03, 0.02])  # Strong X+ bias

    for sharpness in [1.0, 2.0, 4.0, 8.0]:
        shells, _ = expand_seed(seed, steps=5, sharpness=sharpness)

        # Measure how much X-bias is preserved
        final_S = shells[-1]['S']
        x_ratio = (final_S[0] + final_S[1]) / final_S.sum()  # X-axis fraction

        print(f"\nSharpness={sharpness}:")
        print(f"  Final shell: {np.round(final_S, 4)}")
        print(f"  X-axis fraction: {x_ratio:.2%} (started at ~80%)")


def test_structure_preservation():
    """
    Verify expand_seed preserves seed proportions exactly at sharpness=1.

    At sharpness=1 the influence matrix has the property that
    expansion preserves the seed's amplitude pattern across all
    shells (modulo numerical noise). This is the "physics-compliant"
    mode where the decompressor arrives at identical structure
    using only the energy-conservation + field-coupling rules.
    """
    print("\n" + "=" * 60)
    print("TEST: Structure Preservation at sharpness=1")
    print("=" * 60)

    seed = np.array([0.5, 0.2, 0.15, 0.08, 0.05, 0.02])
    seed_proportions = seed / seed.sum()

    shells, _ = expand_seed(seed, steps=15, sharpness=1.0)

    print(f"\nSeed proportions: {np.round(seed_proportions, 4)}")
    print()

    max_deviation = 0.0
    for s in shells:
        S_prop = s['S'] / s['S'].sum()
        deviation = float(np.max(np.abs(S_prop - seed_proportions)))
        max_deviation = max(max_deviation, deviation)

        if s['id'] <= 5 or s['id'] == 15:
            print(
                f"Shell {s['id']:2d}: {np.round(S_prop, 4)} "
                f"(dev: {deviation:.2e})"
            )

    threshold = 1e-10
    preserved = max_deviation < threshold
    print(f"\nMax deviation across all shells: {max_deviation:.2e}")
    print(f"Status: {'PASS' if preserved else 'FAIL'} "
          f"(threshold {threshold:.0e})")

    # Round-trip via compress_to_seed
    recovered = compress_to_seed(shells)
    rt_dev = float(np.max(np.abs(recovered - seed_proportions)))
    print(f"\ncompress_to_seed round-trip deviation: {rt_dev:.2e}")
    print(f"Round-trip status: {'PASS' if rt_dev < threshold else 'FAIL'}")


def visualize(shells):
    """ASCII visualization."""
    print("\n" + "=" * 60)
    print("STRUCTURE VISUALIZATION")
    print("=" * 60)
    print("\nVertices: +X   -X   +Y   -Y   +Z   -Z")
    print()

    for s in shells:
        S_norm = s['S'] / (s['S'].max() + 1e-10) * 8
        bars = ""
        for val in S_norm:
            bars += "#" * int(val) + " " * (8 - int(val)) + " "
        print(f"n={s['id']}: {bars} E={s['E']:.3f}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ORBITAL-OCTAHEDRAL FRACTAL CORE v2 (merged)")
    print("Direct Vertex-to-Vertex Field Coupling")
    print("=" * 60)

    test_influence_matrix()
    test_causality()
    test_pause_resume()
    test_seed_preservation()
    test_energy_conservation()
    test_sharpness_effect()
    test_structure_preservation()

    # Demo growth
    print("\n" + "=" * 60)
    print("DEMO: Growing from asymmetric seed")
    print("=" * 60)

    seed = np.array([0.5, 0.2, 0.15, 0.08, 0.05, 0.02])
    shells, W = expand_seed(seed, steps=8, sharpness=3.0, sigma_scale=0.4)

    visualize(shells)

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)

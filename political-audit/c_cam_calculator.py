#!/usr/bin/env python3
"""
Camouflage Score (C_cam) Calculator
Six Sigma for Governance - Telemetry Tool
"""

def calculate_c_cam(sample_data):
    """
    sample_data: list of dicts with keys:
        - position: str (e.g., "truck driver", "back office", "wealthy core")
        - court_equality_yes: bool
        - political_sway_yes: bool
        - latency_days: float (optional)
        - amplification: float (optional, core=100 baseline)
    """
    
    total = len(sample_data)
    yes_to_both = sum(1 for d in sample_data if d.get('court_equality_yes') and d.get('political_sway_yes'))
    p_equal = yes_to_both / total if total > 0 else 0
    
    # Estimate D_n from answers if not provided
    for d in sample_data:
        if 'd_n' not in d:
            if d.get('court_equality_yes', False) and d.get('political_sway_yes', False):
                d['d_n'] = 0.05  # core estimate
            else:
                d['d_n'] = 0.75  # periphery estimate (can be refined with latency/amplification)
    
    # Find core D_n (lowest in sample)
    core_d_n = min(d['d_n'] for d in sample_data)
    
    # Calculate median periphery D_n
    periphery_d_n = [d['d_n'] for d in sample_data if d['d_n'] > core_d_n * 1.5]
    median_periphery = sorted(periphery_d_n)[len(periphery_d_n)//2] if periphery_d_n else 0.75
    
    c_cam = ((median_periphery - core_d_n) / max(core_d_n, 0.001)) * 50
    c_cam = min(max(c_cam, 0), 100)
    
    return {
        'p_equal': p_equal,
        'p_equal_percent': p_equal * 100,
        'core_d_n': core_d_n,
        'median_periphery_d_n': median_periphery,
        'c_cam': c_cam,
        'democracy_status': 'FAILED' if p_equal <= 0.5 else 'PASS',
        'camouflage_level': 'MAXIMUM' if c_cam > 80 else 'HIGH' if c_cam > 50 else 'MODERATE' if c_cam > 20 else 'LOW'
    }

# Example: n=55 data
sample = [
    {'position': 'truck driver', 'court_equality_yes': False, 'political_sway_yes': False, 'latency_days': 45, 'amplification': 0.5}
    for _ in range(50)
] + [
    {'position': 'back office', 'court_equality_yes': False, 'political_sway_yes': False, 'latency_days': 20, 'amplification': 1.0}
    for _ in range(5)
]

result = calculate_c_cam(sample)
print("Six Sigma Governance Audit")
print("==========================")
print(f"Sample size: {len(sample)}")
print(f"P_equal: {result['p_equal_percent']:.1f}%")
print(f"Core D_n: {result['core_d_n']:.2f}")
print(f"Median Periphery D_n: {result['median_periphery_d_n']:.2f}")
print(f"Camouflage Score (C_cam): {result['c_cam']:.1f}")
print(f"Democracy Status: {result['democracy_status']}")
print(f"Camouflage Level: {result['camouflage_level']}")

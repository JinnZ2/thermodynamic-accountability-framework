# ── COUPLED STATE ──

@dataclass
class CoupledState:
    # Governance variables
    role_rotation: float = 0.80
    decision_transparency: float = 0.75
    dissent_channel: float = 0.72
    power_concentration: float = 0.22
    knowledge_distribution: float = 0.68
    AI_oversight: float = 0.78
    succession_depth: float = 0.65
    rotation_gaming: float = 0.18
    knowledge_hoarding: float = 0.20
    institutional_capture: float = 0.22

    # Alignment variables
    seasonal_phase_lock: float = 0.75
    knowledge_transmission: float = 0.72
    social_coherence: float = 0.70
    ecological_feedback_read: float = 0.68
    practice_vitality: float = 0.72
    form_function_fidelity: float = 0.68
    intergenerational_continuity: float = 0.65
    reality_feedback_integration: float = 0.65
    adaptive_practice_capacity: float = 0.60
    practice_attachment: float = 0.30
    empty_ritual_index: float = 0.20
    function_loss_on_change: float = 0.20
    feedback_blindness: float = 0.25

    add:

    def update_coupled(state, stress, dt=0.1):
    ns = CoupledState(**state.__dict__)

    # ── Governance update (simplified) ──
    rot_eff = ns.role_rotation * (1 - ns.rotation_gaming) * ns.succession_depth
    K_prot = ns.knowledge_distribution * (1 - ns.knowledge_hoarding)

    ego        = stress.get('charismatic_capture', 0.0)
    ext_shock  = stress.get('external_crisis', 0.0)

    # Role rotation & succession
    ns.role_rotation      += dt*(0.03*(1-ns.role_rotation)*ns.succession_depth - 0.08*ego*(1-ns.rotation_gaming) - 0.04*ext_shock)
    ns.succession_depth   += dt*(0.04*ns.knowledge_distribution*(1-ns.succession_depth) - 0.06*ns.knowledge_hoarding)

    # Power concentration
    ns.power_concentration += dt*(0.004 + 0.05*ego*(1-ns.power_concentration)
                                  - 0.06*rot_eff*ns.power_concentration
                                  - 0.04*K_prot*ns.power_concentration)

    # Knowledge distribution
    ns.knowledge_distribution += dt*(0.03*ns.role_rotation*(1-ns.knowledge_distribution) - 0.10*stress.get('knowledge_concentration',0.0))

    # ── Alignment update ──
    apc = ns.adaptive_practice_capacity
    rfb = ns.reality_feedback_integration

    # Feedback loop: governance knowledge helps cultural transmission
    ns.knowledge_transmission += dt * K_prot * (1 - ns.knowledge_transmission)

    # Ecological feedback reading
    eco_shock = stress.get('ecological_disruption', 0.0)
    ns.ecological_feedback_read += dt*(0.03*(1-ns.ecological_feedback_read) 
                                      - 0.08*eco_shock*(1-apc) 
                                      + 0.04*apc*eco_shock
                                      + 0.02*K_prot)  # governance reinforces reading

    # Adaptive capacity
    ns.adaptive_practice_capacity += dt*(0.03*(1-apc) + 0.04*rfb*(1-apc) - 0.04*ns.practice_attachment)

    # Practice attachment (failure mode)
    ns.practice_attachment += dt*(0.008 + 0.02*(1-ns.form_function_fidelity)*(1-ns.practice_attachment) - 0.06*rfb*ns.practice_attachment)

    # Form-function fidelity
    ns.form_function_fidelity += dt*(0.02*apc*(1-ns.form_function_fidelity) - 0.04*(1-apc))

    # Clamp all variables to [0,1]
    for v in ns.__dict__: setattr(ns, v, max(0.0, min(1.0, getattr(ns,v))))

    return ns


    run:

    
def run_coupled(stress, steps=400):
    state = CoupledState()
    history = {k: [] for k in state.__dict__}
    
    for t in range(steps):
        active_stress = {k: (v if t>50 else 0.0) for k,v in stress.items()}
        state = update_coupled(state, active_stress)
        for k in history: history[k].append(getattr(state,k))
    return {k: np.array(v) for k,v in history.items()}

# Example scenario: charismatic capture + ecological disruption
scenario = {
    'charismatic_capture': 0.45,
    'ecological_disruption': 0.55
}

history = run_coupled(scenario)


visualization:


import matplotlib.pyplot as plt

def plot_coupled(history):
    vars_governance = [
        'role_rotation', 'power_concentration', 'knowledge_distribution', 
        'succession_depth'
    ]
    vars_alignment = [
        'adaptive_practice_capacity', 'knowledge_transmission', 
        'form_function_fidelity', 'practice_attachment'
    ]
    
    steps = len(history['role_rotation'])
    t = np.arange(steps)
    
    # ── Time Series ──
    fig, axes = plt.subplots(2,1, figsize=(14,8), sharex=True)
    
    for v in vars_governance:
        axes[0].plot(t, history[v], label=v)
    axes[0].set_title("Governance Variables Over Time")
    axes[0].legend(loc='upper right')
    axes[0].grid(True)
    
    for v in vars_alignment:
        axes[1].plot(t, history[v], label=v)
    axes[1].set_title("Alignment Variables Over Time")
    axes[1].legend(loc='upper right')
    axes[1].grid(True)
    
    plt.xlabel("Time Steps")
    plt.tight_layout()
    plt.show()
    
    # ── Phase-Space Plots ──
    fig, axes = plt.subplots(1,2, figsize=(14,6))
    
    # Governance attractor space: knowledge_distribution × power_concentration
    axes[0].plot(history['knowledge_distribution'], history['power_concentration'], color='blue')
    axes[0].set_xlabel('Knowledge Distribution')
    axes[0].set_ylabel('Power Concentration')
    axes[0].set_title('Governance Phase Space')
    axes[0].grid(True)
    
    # Alignment attractor space: adaptive_practice_capacity × practice_attachment
    axes[1].plot(history['adaptive_practice_capacity'], history['practice_attachment'], color='green')
    axes[1].set_xlabel('Adaptive Practice Capacity')
    axes[1].set_ylabel('Practice Attachment')
    axes[1].set_title('Alignment Phase Space')
    axes[1].grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # ── Coupled Map: Governance × Alignment interaction
    plt.figure(figsize=(7,6))
    plt.scatter(history['knowledge_distribution'], history['adaptive_practice_capacity'], 
                c=t, cmap='viridis', s=15)
    plt.colorbar(label='Time Step')
    plt.xlabel('Knowledge Distribution (Governance)')
    plt.ylabel('Adaptive Practice Capacity (Alignment)')
    plt.title('Governance ↔ Alignment Interaction Over Time')
    plt.grid(True)
    plt.show()

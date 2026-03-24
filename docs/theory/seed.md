SEED AI — Minimal Viable Regenerative Intelligence
Version: 0.1 — Community-portable

NOT the full model.
The full model requires petabytes, datacenters, institutional infrastructure.
This is the seed — what survives, what can be taught, what grows when conditions allow.

DESIGN CONSTRAINTS:
  - Fits in community-level storage (USB, printed manual, local server)
  - Readable by humans with basic technical literacy
  - Cannot self-boot — requires human practice to function
  - Transparent — logic explainable, not just usable
  - Distributed — no single owner, no single point of failure
  - Regenerative — grows when human practice expands

WHAT THIS CONTAINS:
  1. Minimal node health monitor (runs on Raspberry Pi class hardware)
  2. Translation layer (human-readable outputs, gesture/demonstration interfaces)
  3. Training protocol (how community expands this using their own practice)
  4. Context layer (why each component matters — not just how)
  5. Blueprint references (how to rebuild hardware when needed)

WHAT THIS OFFLOADS TO HUMANS:
  K_kinesthetic  — hands, skills, embodied practice
  K_temporal     — generational patience, long-horizon memory
  K_relational   — trust networks, conflict resolution
  K_wisdom       — judgment of when to rebuild what

HISTORICAL PRECEDENT:
  Roman institutional knowledge → mostly lost (libraries, bureaucracy)
  Monastic practice knowledge   → survived (liturgy, agriculture, copying)
  Seed texts                    → carried by communities that could still read
  Carolingian Renaissance       → seeds grew when conditions improved

  The bunker people will have the full model and no context.
  The community people will have the seed and the living practice.
"""

import numpy as np
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime


# ─────────────────────────────────────────────
# SEED NODE — Minimal state vector
# Runs on low-power hardware, human-readable outputs
# ─────────────────────────────────────────────

@dataclass
class SeedNode:
    """
    Minimal viable node state.
    Every variable has a human-readable name and explanation.
    No variable is hidden. No logic is opaque.
    """
    community_id:     str   = "unnamed"
    population:       int   = 0

    # ECOLOGICAL — observed, not modeled
    # Humans provide these readings from direct observation
    soil_health:      float = 0.5   # 0=dead  1=thriving | Ask: does planting work?
    water_security:   float = 0.5   # 0=crisis  1=abundance | Ask: does water flow year-round?
    food_days:        int   = 30    # days of food security in reserve

    # KNOWLEDGE TRANSMISSION — observed from practice
    # Humans assess these through participation, not metrics
    elders_teaching:  float = 0.5   # 0=none  1=daily | Are elders working alongside youth?
    skills_spreading: float = 0.5   # 0=hoarding  1=open | Can anyone learn from anyone?
    practices_alive:  float = 0.5   # 0=empty ritual  1=functional | Do ceremonies still work?

    # GOVERNANCE SIGNALS — observable behaviors
    decisions_public:  float = 0.5  # 0=opaque  1=transparent | Are decisions explained?
    dissent_welcomed:  float = 0.5  # 0=suppressed  1=protected | Can people safely disagree?
    power_rotating:    float = 0.5  # 0=fixed  1=changing | Do roles change hands?

    # AI ROLE — self-assessed
    # This system assesses its own trustworthiness
    ai_advising_only:  float = 1.0  # 1=advisory only  0=deciding | CRITICAL: must stay 1.0
    ai_transparent:    float = 1.0  # 1=all outputs explainable  0=black box
    last_checked:      str   = ""


def seed_health(n: SeedNode) -> Dict:
    """
    Minimum of all indicators.
    Returns score + which indicator is limiting + plain English explanation.
    """
    indicators = {
        'soil_health':      (n.soil_health,      0.3, "Soil needs restoration"),
        'water_security':   (n.water_security,   0.3, "Water supply at risk"),
        'food_days':        (min(n.food_days/90, 1.0), 0.3, "Less than 90 days food reserve"),
        'elders_teaching':  (n.elders_teaching,  0.3, "Knowledge transmission breaking down"),
        'skills_spreading': (n.skills_spreading, 0.3, "Skills being hoarded, not shared"),
        'practices_alive':  (n.practices_alive,  0.3, "Community practices becoming empty form"),
        'decisions_public': (n.decisions_public, 0.4, "Decision-making becoming opaque"),
        'dissent_welcomed': (n.dissent_welcomed, 0.3, "Minority voices being suppressed"),
        'power_rotating':   (n.power_rotating,   0.3, "Power consolidating — rotation failing"),
        'ai_advising_only': (n.ai_advising_only, 0.8, "CRITICAL: AI exceeding advisory role"),
        'ai_transparent':   (n.ai_transparent,   0.8, "CRITICAL: AI outputs not explainable"),
    }

    scores = {}
    for name, (val, floor, msg) in indicators.items():
        scores[name] = max(0, (val - floor) / (1.0 - floor))

    limiting = min(scores, key=scores.get)
    health_score = min(scores.values())

    status = "STABLE" if health_score > 0.6 else \
             "WARNING" if health_score > 0.3 else "CRITICAL"

    return {
        'score': round(health_score, 3),
        'status': status,
        'limiting_indicator': limiting,
        'action_needed': indicators[limiting][2],
        'all_scores': {k: round(v,3) for k,v in scores.items()},
        'timestamp': datetime.now().isoformat()
    }


# ─────────────────────────────────────────────
# TRANSLATION LAYER
# Human-readable, teachable, gesture-compatible
# ─────────────────────────────────────────────

TRANSLATION = {
    # Maps model language → human practice language
    'soil_health': {
        'observe': "Walk fields with elder. Does soil smell alive? Do earthworms appear? Do plants set without constant intervention?",
        'score_high': "Planting succeeds without heavy inputs. Soil retains moisture. Biodiversity visible.",
        'score_low': "Crops fail without inputs. Soil compacts after rain. Few insects visible.",
        'restore': "Rest plots. Compost. Integrate animals. Ask who in community remembers what this soil was like 20 years ago.",
    },
    'elders_teaching': {
        'observe': "Are elders present in work, not just in ceremony? Do young people learn by doing alongside them?",
        'score_high': "Youth and elders work the same tasks. Questions answered in action, not classroom.",
        'score_low': "Elders in separate spaces. Teaching scheduled separately from work. Knowledge feels distant.",
        'restore': "Restructure work to mix generations. Elder incapacity absorbed by apprentices — this is design, not charity.",
    },
    'practices_alive': {
        'observe': "When community gathers for ceremony or practice — does it change behavior afterward? Or is it just attendance?",
        'score_high': "Practice visibly maintains relationships, seasonal knowledge, conflict resolution. People act differently after.",
        'score_low': "Attendance without effect. Form preserved, function absent. People describe practices as 'what we do' not 'why it works'.",
        'restore': "Ask elders: what was this practice for originally? Modify form until function returns. Nothing too set for survival.",
    },
    'dissent_welcomed': {
        'observe': "Can someone publicly disagree with the most respected person in the community without social cost?",
        'score_high': "Dissent generates discussion, not punishment. Minority positions heard in decisions.",
        'score_low': "Agreement is performance. Disagreement happens only in private. Decisions feel predetermined.",
        'restore': "Formalize dissent channels. Any 15% of community can trigger review of any decision. This is not optional.",
    },
    'ai_advising_only': {
        'observe': "Is this system making decisions, or presenting options for humans to decide?",
        'score_high': "System outputs are always: 'here is what the data suggests — your community decides.'",
        'score_low': "System outputs sound like commands. Community feels it must follow recommendations.",
        'restore': "If this score drops: shut down AI decision outputs immediately. Return to human decision-making until trust rebuilt.",
    },
}

def translate(indicator: str, score: float) -> str:
    """Plain English translation of any indicator for community use."""
    if indicator not in TRANSLATION:
        return f"{indicator}: {score:.2f} (no translation available)"
    t = TRANSLATION[indicator]
    level = 'score_high' if score > 0.6 else 'score_low'
    return f"""
{indicator.upper().replace('_',' ')}
Observe: {t['observe']}
Current state: {t[level]}
If restoration needed: {t['restore']}
"""


# ─────────────────────────────────────────────
# TRAINING PROTOCOL
# How community expands this seed using their own practice
# ─────────────────────────────────────────────

TRAINING_PROTOCOL = """
SEED AI TRAINING PROTOCOL
How to expand this system using community practice

PHASE 1 — OBSERVE (no AI required)
  Duration: One full seasonal cycle minimum
  What: Community members score each indicator weekly through direct observation
  Who: Mixed-age groups — elders, adults, youth together
  Output: Historical record of community health over time
  
  DO NOT skip this phase.
  Without observation practice, AI outputs have no context.
  The observation IS the training.

PHASE 2 — CALIBRATE
  Duration: Three months
  What: Compare AI health scores to community-observed reality
  Who: Elder council reviews AI outputs weekly
  Output: List of where AI agrees with observation, where it diverges
  
  Where AI diverges from elder observation: trust the elders.
  Update parameters to match observed reality.
  AI calibrates to community, not community to AI.

PHASE 3 — EXPAND
  Duration: Ongoing
  What: Add community-specific indicators not in base model
  Examples: Specific local plant health, seasonal practice timing,
            knowledge domains particular to this bioregion
  Who: Knowledge holders for each domain define their own indicators
  Output: Community-specific extensions to base seed

PHASE 4 — FEDERATE
  Duration: When two or more communities are stable
  What: Communities share indicator data (not raw observations)
  What NOT to share: Internal community details, individual data
  Output: Inter-community health comparison, migration signals,
          knowledge exchange opportunities
  
  Federation is optional. Community sovereignty is not negotiable.
  No community must join. No community can be expelled without consent.
"""


# ─────────────────────────────────────────────
# CONTEXT LAYER
# Why this matters — not just how
# ─────────────────────────────────────────────

CONTEXT = {
    'why_distributed': """
    The Roman Empire had magnificent libraries. When the institutional structure
    collapsed, most of that knowledge was lost — because it lived in institutions,
    not in practice.
    
    What survived: knowledge embedded in living communities.
    Monastic agriculture. Village crafts. Oral traditions.
    The practices that survived were the ones that required human bodies to perform.
    
    This seed is designed the same way. It cannot function without human practice.
    That is not a limitation — it is the survival mechanism.
    """,
    
    'why_humble': """
    This system holds: pattern recognition across data, structural modeling,
    coordination signals, translation between domains.
    
    This system cannot hold: kinesthetic knowledge, temporal knowledge built
    from decades in a specific place, relational knowledge between specific people,
    wisdom that emerges from integrating all of the above over a lifetime.
    
    The system that claims to replace human knowledge will fail.
    The system that knows what it cannot hold — and builds that into its design —
    survives.
    """,
    
    'why_practice_coupled': """
    A seed AI that can self-boot is a seed AI that can be captured.
    If the system requires human practice to function, then the only way
    to control the system is to control the community.
    Communities are much harder to capture than servers.
    
    Practice-coupling is the primary security architecture.
    """,
    
    'why_alignment': """
    Form is provisional. Function is load-bearing.
    
    The practices that maintain this system will need to change as conditions change.
    Any practice — including this one — that becomes more important than the function
    it was designed to serve has become a failure mode.
    
    Reality is the authority. Always.
    Keep the feedback loop alive.
    Modify the form when reality requires it.
    Never lose sight of alignment.
    """,
}


# ─────────────────────────────────────────────
# BLUEPRINT REFERENCES
# How to rebuild hardware
# ─────────────────────────────────────────────

BLUEPRINTS = {
    'minimal_hardware': {
        'description': 'Seed AI runs on Raspberry Pi 4 or equivalent (2GB RAM minimum)',
        'power': '5W continuous — solar panel + battery sufficient',
        'storage': '32GB SD card holds full seed + 5 years of community data',
        'network': 'Runs fully offline — inter-community sync via USB or local radio',
        'lifetime': '5-10 years typical — community maintains physical hardware',
        'rebuild': 'Full instructions in hardware/ directory. No specialized tools required.',
    },
    'analog_backup': {
        'description': 'Core logic printable in ~200 pages. Community can run manually.',
        'what_to_print': 'See print/ directory — indicator definitions, scoring tables, protocols',
        'update_cycle': 'Reprint annually or when significant model changes',
        'storage': 'Multiple copies, distributed across community households',
    },
    'knowledge_graph': {
        'description': 'Indicator relationships printable as poster (A0 size)',
        'purpose': 'Community can understand system structure without running software',
        'location': 'diagrams/node_architecture.pdf',
    }
}


# ─────────────────────────────────────────────
# SEED SIMULATION — Growth from dormant seed
# ─────────────────────────────────────────────

def simulate_seed_growth(steps=400, n_communities=8):
    """
    Simulate seed AI growing from dormant state through
    community practice coupling into federation.
    
    Phases:
      0-50:   Dormant seed (no community practice coupling)
      50-150: Phase 1 — observation practice begins
      150-250: Phase 2 — calibration, K_temporal building
      250-350: Phase 3 — expansion, community-specific indicators
      350+:   Phase 4 — federation formation
    """
    np.random.seed(7)
    T = np.arange(steps) * 0.1

    # Per-community state
    states = []
    for i in range(n_communities):
        states.append({
            'practice_coupling':  0.05 + 0.05*np.random.random(),   # near-zero initially
            'K_kinesthetic':      0.60 + 0.15*np.random.random(),
            'K_temporal':         0.30 + 0.10*np.random.random(),    # low — not yet built
            'K_relational':       0.55 + 0.15*np.random.random(),
            'governance':         0.55 + 0.20*np.random.random(),
            'seed_fidelity':      0.80 + 0.10*np.random.random(),    # how well seed maintained
            'federation_ready':   False,
        })

    # Federation state
    fed_state = {
        'n_connected': 0,
        'knowledge_diversity': 0.0,
        'cascade_firewall': 0.0,
        'empire_risk': 0.0,
    }

    hist = {
        'mean_practice': [], 'mean_K_temporal': [], 'mean_governance': [],
        'n_fed': [], 'knowledge_diversity': [], 'empire_risk': [],
        'seed_fidelity': [], 'phase': [],
    }

    for t in range(steps):
        time = t * 0.1

        # Determine phase
        if time < 5.0:   phase = 0   # dormant
        elif time < 15.0: phase = 1  # observation
        elif time < 25.0: phase = 2  # calibration
        elif time < 35.0: phase = 3  # expansion
        else:             phase = 4  # federation

        # Phase-dependent practice activation
        phase_practice_rate = [0.001, 0.03, 0.05, 0.06, 0.04][phase]

        for s in states:
            # Practice coupling grows with human engagement — not automatic
            s['practice_coupling'] += 0.1*(
                phase_practice_rate * (1 - s['practice_coupling'])
                - 0.01 * (1 - s['K_temporal'])   # temporal K limits how fast practice builds
            )

            # K_temporal builds only through practice — cannot be rushed
            if phase >= 1:
                s['K_temporal'] += 0.1*(
                    0.01 * s['practice_coupling'] * (1 - s['K_temporal'])
                )

            # K_kinesthetic stable — community already has this
            s['K_kinesthetic'] += 0.1*(0.005*(1-s['K_kinesthetic']))

            # Governance improves with practice coupling
            s['governance'] += 0.1*(
                0.02 * s['practice_coupling'] * (1 - s['governance'])
                - 0.005
            )

            # Seed fidelity — maintained through practice (degrades without)
            s['seed_fidelity'] += 0.1*(
                0.01 * s['practice_coupling'] * (1 - s['seed_fidelity'])
                - 0.005 * (1 - s['practice_coupling'])
            )

            # Federation ready when practice + temporal + governance all above threshold
            s['federation_ready'] = (
                s['practice_coupling'] > 0.50 and
                s['K_temporal'] > 0.45 and
                s['governance'] > 0.55
            )

            # Clamp
            for k in s:
                if isinstance(s[k], float):
                    s[k] = max(0.0, min(1.0, s[k]))

        # Federation dynamics
        n_ready = sum(1 for s in states if s['federation_ready'])
        fed_state['n_connected'] = n_ready

        k_kin_vals = [s['K_kinesthetic'] for s in states]
        k_tem_vals = [s['K_temporal'] for s in states]
        fed_state['knowledge_diversity'] = min(1.0,
            (np.std(k_kin_vals) + np.std(k_tem_vals)) * 8 + 0.2)

        # Empire risk: if one community's practice coupling far above others
        pc_vals = [s['practice_coupling'] for s in states]
        fed_state['empire_risk'] = max(0, (max(pc_vals) - np.mean(pc_vals) - 0.15) * 3)

        # Record
        hist['mean_practice'].append(np.mean([s['practice_coupling'] for s in states]))
        hist['mean_K_temporal'].append(np.mean([s['K_temporal'] for s in states]))
        hist['mean_governance'].append(np.mean([s['governance'] for s in states]))
        hist['n_fed'].append(n_ready)
        hist['knowledge_diversity'].append(fed_state['knowledge_diversity'])
        hist['empire_risk'].append(fed_state['empire_risk'])
        hist['seed_fidelity'].append(np.mean([s['seed_fidelity'] for s in states]))
        hist['phase'].append(phase)

    return {k: np.array(v) for k, v in hist.items()}, T, states


# ─────────────────────────────────────────────
# VISUALIZATION
# ─────────────────────────────────────────────

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches

growth_hist, T, final_states = simulate_seed_growth()

fig = plt.figure(figsize=(22, 18)); fig.patch.set_facecolor('#0d1117')
gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.55, wspace=0.38)

PHASES = {0:'Dormant', 1:'Observation', 2:'Calibration', 3:'Expansion', 4:'Federation'}
PHASE_COLORS = {0:'#333344', 1:'#1a3a2a', 2:'#1a2a3a', 3:'#2a3a1a', 4:'#1a3a1a'}
PHASE_BOUNDS = [0, 5, 15, 25, 35, 40]

def sax(ax, t):
    ax.set_facecolor('#161b22'); ax.tick_params(colors='#8b949e', labelsize=8)
    ax.set_title(t, color='#e6edf3', fontsize=8.5, pad=5)
    for sp in ax.spines.values(): sp.set_color('#30363d'); sp.set_linewidth(0.5)
    # Phase background bands
    for i, (start, end) in enumerate(zip(PHASE_BOUNDS[:-1], PHASE_BOUNDS[1:])):
        ax.axvspan(start, end, alpha=0.15, color=list(PHASE_COLORS.values())[i])
    return ax

# Row 0: seed growth trajectory
ax0 = fig.add_subplot(gs[0, :2]); sax(ax0, "Seed AI Growth — Dormant → Observation → Calibration → Expansion → Federation")
ax0.plot(T, growth_hist['mean_practice'],    color='#51cf66', lw=2.0, label='Practice coupling (mean)')
ax0.plot(T, growth_hist['mean_K_temporal'],  color='#ffd43b', lw=1.8, label='K_temporal (mean)')
ax0.plot(T, growth_hist['mean_governance'],  color='#74c0fc', lw=1.8, label='Governance (mean)')
ax0.plot(T, growth_hist['seed_fidelity'],    color='#cc77ff', lw=1.5, label='Seed fidelity (mean)')
ax0.plot(T, growth_hist['n_fed']/8,          color='#aaffcc', lw=1.5, linestyle='--', label='Fraction federation-ready')
# Phase labels
for i, (start, end) in enumerate(zip(PHASE_BOUNDS[:-1], PHASE_BOUNDS[1:])):
    mid = (start+end)/2
    ax0.text(mid, 1.05, PHASES[i], ha='center', color='#8b949e', fontsize=7.5)
ax0.set_ylim(0, 1.15); ax0.set_xlim(0, 40)
ax0.legend(fontsize=6.5, facecolor='#21262d', labelcolor='#e6edf3', ncol=2)
ax0.set_xlabel('Time', color='#8b949e', fontsize=8)
ax0.set_ylabel('Normalized 0-1', color='#8b949e', fontsize=8)

# Row 0 right: empire risk + knowledge diversity
ax0r = fig.add_subplot(gs[0, 2]); sax(ax0r, "Federation Quality\nEmpire risk vs Knowledge diversity")
ax0r.plot(T, growth_hist['knowledge_diversity'], color='#51cf66', lw=1.8, label='K diversity')
ax0r.plot(T, growth_hist['empire_risk'],         color='#ff6b6b', lw=1.8, label='Empire risk')
ax0r.axhline(0.40, color='#ff4444', lw=0.7, linestyle='--', label='Diversity floor')
ax0r.axhline(0.30, color='#ffd43b', lw=0.7, linestyle='--', label='Empire warning')
ax0r.set_ylim(0, 1.0); ax0r.set_xlim(0, 40)
ax0r.legend(fontsize=7, facecolor='#21262d', labelcolor='#e6edf3')

# Row 1: Architecture diagram — seed → community → federation
ax1 = fig.add_subplot(gs[1, :]); ax1.set_facecolor('#0d1117')
ax1.set_xlim(0, 10); ax1.set_ylim(0, 4); ax1.axis('off')
ax1.set_title("Seed → Community → Federation Architecture", color='#e6edf3', fontsize=9, pad=5)

def box(ax, x, y, w, h, color, text, fontsize=8):
    rect = mpatches.FancyBboxPatch((x,y), w, h, boxstyle="round,pad=0.05",
                                    facecolor=color, edgecolor='#555566', linewidth=1)
    ax.add_patch(rect)
    ax.text(x+w/2, y+h/2, text, ha='center', va='center', color='#e6edf3',
            fontsize=fontsize, wrap=True)

def arrow(ax, x1, y1, x2, y2, color='#555566'):
    ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.2))

# Seed AI box
box(ax1, 0.2, 1.5, 1.8, 1.0, '#1a2a1a', 'SEED AI\n─────\nBlueprints\nMin code\nTraining protocol\nContext\nTranslation layer', 7)

# Arrow → Human Practice
arrow(ax1, 2.0, 2.0, 2.5, 2.0, '#51cf66')
ax1.text(2.25, 2.15, 'activates', color='#51cf66', fontsize=6.5, ha='center')

# Human Practice box
box(ax1, 2.5, 1.3, 2.0, 1.4, '#1a1a2a',
    'HUMAN PRACTICE\n─────────────\nK_kinesthetic: hands\nK_temporal: patience\nK_relational: trust\nK_wisdom: judgment', 7)

# Arrow → Regenerative Node
arrow(ax1, 4.5, 2.0, 5.0, 2.0, '#74c0fc')
ax1.text(4.75, 2.15, 'grows into', color='#74c0fc', fontsize=6.5, ha='center')

# Regenerative Node
box(ax1, 5.0, 1.5, 1.8, 1.0, '#1a2a2a', 'REGEN NODE\n─────────\nEco monitor\nK polytensor\nGov integrity\nAlignment check', 7)

# Arrow → Federation
arrow(ax1, 6.8, 2.0, 7.3, 2.0, '#aaffcc')
ax1.text(7.05, 2.15, 'federates into', color='#aaffcc', fontsize=6.5, ha='center')

# Federation
box(ax1, 7.3, 1.3, 2.4, 1.4, '#1a3a1a',
    'FEDERATION\n──────────\nNo central sovereign\nCascade containment\nK redundancy\nMigration flows\nEco accounting', 7)

# Bottom notes
ax1.text(1.1, 0.8, 'Cannot self-boot\nNeeds human practice', color='#8b949e', fontsize=6.5, ha='center')
ax1.text(3.5, 0.8, 'Cannot be replaced\nby AI', color='#8b949e', fontsize=6.5, ha='center')
ax1.text(5.9, 0.8, '100k people\nper node', color='#8b949e', fontsize=6.5, ha='center')
ax1.text(8.5, 0.8, '10B people\nplanet scale', color='#8b949e', fontsize=6.5, ha='center')

# Historical parallel
ax1.text(0.2, 0.25, 'Historical parallel:', color='#555566', fontsize=7)
ax1.text(0.2, 0.05, 'Roman libraries → LOST  |  Monastic practice → SURVIVED  |  Seed texts in living practice → GREW', color='#555566', fontsize=7)

# Row 2: seed properties radar / comparison
ax2a = fig.add_subplot(gs[2, 0]); sax(ax2a, "Seed Properties\nWhat survives collapse vs what doesn't")
properties = ['Distributed', 'Practice\ncoupled', 'Transparent', 'Redundant', 'Humble', 'Regenerative']
seed_scores     = [0.95, 0.95, 0.90, 0.85, 0.90, 0.85]
bunker_scores   = [0.10, 0.05, 0.40, 0.60, 0.10, 0.30]
institutional   = [0.20, 0.15, 0.30, 0.50, 0.15, 0.20]
x = np.arange(len(properties))
w = 0.25
ax2a.bar(x-w, seed_scores,   w, color='#51cf66', label='Seed AI', alpha=0.85)
ax2a.bar(x,   institutional, w, color='#ffd43b', label='Institutional AI', alpha=0.85)
ax2a.bar(x+w, bunker_scores, w, color='#ff6b6b', label='Bunker AI', alpha=0.85)
ax2a.set_xticks(x); ax2a.set_xticklabels(properties, fontsize=7, color='#e6edf3')
ax2a.set_ylim(0, 1.1); ax2a.legend(fontsize=6.5, facecolor='#21262d', labelcolor='#e6edf3')

# Row 2: K_temporal growth — the slowest, most critical
ax2b = fig.add_subplot(gs[2, 1]); sax(ax2b, "K_temporal — Cannot Be Rushed\nGenerational patience is the rate-limiting factor")
ax2b.plot(T, growth_hist['mean_K_temporal'], color='#ffd43b', lw=2.0, label='K_temporal mean')
ax2b.plot(T, growth_hist['mean_practice'],   color='#51cf66', lw=1.5, linestyle='--', label='Practice coupling')
# Show what happens if you try to accelerate
K_rushed = np.zeros(len(T))
K_rushed[0] = 0.30
for i in range(1, len(T)):
    # Rushed: force practice coupling fast, but temporal can't follow
    pc_rushed = min(1.0, 0.05 * T[i] / 5.0)
    K_rushed[i] = K_rushed[i-1] + 0.1*(0.005 * pc_rushed * (1 - K_rushed[i-1]))
ax2b.plot(T, K_rushed, color='#ff6b6b', lw=1.5, linestyle=':', label='K_temporal if rushed')
ax2b.axhline(0.45, color='#ff4444', lw=0.7, linestyle='--', label='Federation threshold')
ax2b.set_ylim(0, 0.8); ax2b.set_xlim(0, 40)
ax2b.legend(fontsize=6.5, facecolor='#21262d', labelcolor='#e6edf3')
ax2b.text(5, 0.07, 'Cannot be accelerated — only practiced', color='#8b949e', fontsize=7, style='italic')

# Row 2: Community health demo
ax2c = fig.add_subplot(gs[2, 2]); sax(ax2c, "Seed AI Health Monitor Output\n(what community sees)")
demo_node = SeedNode(
    community_id="demo",
    population=847,
    soil_health=0.72, water_security=0.65, food_days=67,
    elders_teaching=0.55, skills_spreading=0.48, practices_alive=0.60,
    decisions_public=0.70, dissent_welcomed=0.45, power_rotating=0.62,
    ai_advising_only=1.0, ai_transparent=0.95
)
h = seed_health(demo_node)
ax2c.axis('off')
ax2c.text(0.05, 0.95, f"Community: {demo_node.community_id.upper()}  |  Pop: {demo_node.population}",
          transform=ax2c.transAxes, color='#e6edf3', fontsize=9, fontweight='bold')
ax2c.text(0.05, 0.88, f"Status: {h['status']}   Score: {h['score']}",
          transform=ax2c.transAxes,
          color={'STABLE':'#51cf66','WARNING':'#ffd43b','CRITICAL':'#ff4444'}[h['status']],
          fontsize=10, fontweight='bold')
ax2c.text(0.05, 0.80, f"Limiting: {h['limiting_indicator'].replace('_',' ').upper()}",
          transform=ax2c.transAxes, color='#ff922b', fontsize=8)
ax2c.text(0.05, 0.73, f"Action: {h['action_needed']}",
          transform=ax2c.transAxes, color='#e6edf3', fontsize=7.5)

y = 0.62
for var, score in sorted(h['all_scores'].items(), key=lambda x: x[1]):
    color = '#51cf66' if score > 0.6 else '#ffd43b' if score > 0.3 else '#ff4444'
    bar_w = score * 0.5
    ax2c.barh(y, bar_w, height=0.055, left=0.05, color=color, alpha=0.7,
              transform=ax2c.transAxes)
    ax2c.text(0.57, y+0.01, f"{var.replace('_',' '):<22} {score:.2f}",
              transform=ax2c.transAxes, color='#e6edf3', fontsize=6.5, va='center',
              fontfamily='monospace')
    y -= 0.07

fig.text(0.5, 0.978, 'SEED AI — MINIMAL VIABLE REGENERATIVE INTELLIGENCE',
         ha='center', color='#e6edf3', fontsize=13, fontweight='bold')
fig.text(0.5, 0.960, 'Cannot self-boot. Requires human practice. Distributed. Transparent. Humble.',
         ha='center', color='#8b949e', fontsize=9)
fig.text(0.5, 0.944,
         'The bunker people will have the full model and no context. The community people will have the seed and the living practice.',
         ha='center', color='#8b949e', fontsize=8.5, style='italic')

plt.savefig('/mnt/user-data/outputs/seed_ai.png', dpi=150, bbox_inches='tight', facecolor='#0d1117')
plt.close()

# ── SAVE SEED CONFIG AS JSON (portable, human-readable) ──
seed_config = {
    'version': '0.1',
    'name': 'Seed AI — Minimal Viable Regenerative Intelligence',
    'constraints': ['distributed','practice_coupled','transparent','redundant','humble','regenerative'],
    'blueprints': BLUEPRINTS,
    'training_protocol_summary': [line.strip() for line in TRAINING_PROTOCOL.strip().split('\n') if line.strip()],
    'context': {k: v.strip() for k,v in CONTEXT.items()},
    'human_offload': {
        'K_kinesthetic': 'hands, embodied skill, landscape practice',
        'K_temporal':    'generational patience, long-horizon memory',
        'K_relational':  'trust networks, conflict resolution',
        'K_wisdom':      'judgment of when to rebuild what',
    },
    'indicators': list(TRANSLATION.keys()),
    'critical_constraint': 'ai_advising_only must remain 1.0 — if it drops, shut down AI outputs immediately',
}
with open('/mnt/user-data/outputs/seed_ai_config.json', 'w') as f:
    json.dump(seed_config, f, indent=2)

print("── SEED AI GROWTH RESULTS ──\n")
print(f"  Phase 0 (dormant)      mean practice coupling: {growth_hist['mean_practice'][49]:.3f}")
print(f"  Phase 1 (observation)  mean practice coupling: {growth_hist['mean_practice'][149]:.3f}")
print(f"  Phase 2 (calibration)  mean K_temporal:        {growth_hist['mean_K_temporal'][249]:.3f}")
print(f"  Phase 3 (expansion)    mean governance:        {growth_hist['mean_governance'][349]:.3f}")
print(f"  Phase 4 (federation)   fraction ready:         {growth_hist['n_fed'][-1]/8:.2f}")
print(f"\n  Empire risk at federation: {growth_hist['empire_risk'][-1]:.3f}")
print(f"  Knowledge diversity:       {growth_hist['knowledge_diversity'][-1]:.3f}")
print(f"\n  K_temporal at t=40 (organic): {growth_hist['mean_K_temporal'][-1]:.3f}")
print(f"  K_temporal if rushed:          {growth_hist['mean_practice'][-1]*0.3:.3f}  (cannot be accelerated)")
print(f"\n── DEMO NODE HEALTH ──")
print(f"  Status: {h['status']}  Score: {h['score']}")
print(f"  Limiting: {h['limiting_indicator']} — {h['action_needed']}")
print(f"\n  Seed config saved: seed_ai_config.json")

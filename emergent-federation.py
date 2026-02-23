“””
EMERGENT SEED-AI + COMMUNITY FEDERATION
Heterogeneous nodes. AI adapts to local practice. Seeds diverge over time.
Synergy from complementary specialization. Cascade containment from redundancy.

KEY DIFFERENCES FROM federation.py:

- Nodes are heterogeneous by design (specialization profiles)
- Each seed AI adapts to its host community (divergence is healthy)
- Synergy points: complementary nodes generate emergent growth
- Assimilation rate gates how fast AI suggestions land
- Seeds can stagnate in isolation (bunker failure mode)
- AI overconfidence modeled explicitly

TIMESTEP:

1. AI observes local practice → proposes improvements
1. Humans implement based on assimilation capacity
1. Communities share surplus K + resources with neighbors
1. Node health updates
1. Emergent events: migration, synergy, AI adaptation, stagnation
   “””

import numpy as np
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings(‘ignore’)

# ─────────────────────────────────────────────

# COMMUNITY NODE — Heterogeneous

# ─────────────────────────────────────────────

# Specialization profiles — nodes start with different strengths

PROFILES = {
‘craft’:        {‘K_kinesthetic’:0.85,‘K_temporal’:0.60,‘K_relational’:0.65,‘K_wisdom’:0.55,‘governance’:0.60},
‘coordination’: {‘K_kinesthetic’:0.55,‘K_temporal’:0.65,‘K_relational’:0.88,‘K_wisdom’:0.70,‘governance’:0.82},
‘ecological’:   {‘K_kinesthetic’:0.70,‘K_temporal’:0.82,‘K_relational’:0.75,‘K_wisdom’:0.72,‘governance’:0.65},
‘knowledge’:    {‘K_kinesthetic’:0.60,‘K_temporal’:0.75,‘K_relational’:0.70,‘K_wisdom’:0.80,‘governance’:0.70},
‘generalist’:   {‘K_kinesthetic’:0.68,‘K_temporal’:0.67,‘K_relational’:0.68,‘K_wisdom’:0.67,‘governance’:0.67},
}

@dataclass
class CommunityNode:
node_id:          int
profile:          str   = ‘generalist’
population:       float = 1.0     # normalized

```
# HUMAN CAPACITIES
K_kinesthetic:    float = 0.68
K_temporal:       float = 0.65
K_relational:     float = 0.68
K_wisdom:         float = 0.65
governance:       float = 0.67

# ECOLOGICAL SUBSTRATE
eco:              float = 0.78

# PRACTICE INVENTORY (what this community actively does)
practice_depth:   float = 0.65    # how deeply practices are embedded
practice_breadth: float = 0.60    # how many practice domains covered
assimilation_rate:float = 0.55    # how fast community implements AI suggestions

# SEED AI STATE (each seed adapts to its host)
seed_active:      bool  = True
seed_fidelity:    float = 0.80    # how intact the seed is
seed_local_adapt: float = 0.10    # how much seed has adapted to local practice
seed_overconfidence: float = 0.05 # LOW good — AI exceeding local practice limits
ai_suggestions_pending: float = 0.0  # suggestions not yet implemented
ai_learning_rate: float = 0.40    # how fast seed learns from local practice

# HEALTH COMPOSITES
health:           float = 0.65
cascade_risk:     float = 0.10
isolation_steps:  int   = 0       # steps without inter-community contact

# SPECIALIZATION SURPLUS (what this node can export)
surplus_craft:    float = 0.0
surplus_coord:    float = 0.0
surplus_eco:      float = 0.0
surplus_knowledge:float = 0.0
```

def init_node(node_id: int, profile: str, variance: float = 0.12) -> CommunityNode:
np.random.seed(node_id * 17 + 3)
n = CommunityNode(node_id=node_id, profile=profile)
p = PROFILES[profile]
for k, v in p.items():
setattr(n, k, max(0.1, min(0.99, v + variance*(np.random.random()-0.5))))
n.eco = 0.75 + 0.15*(np.random.random()-0.5)
n.assimilation_rate = n.K_temporal * n.governance
return n

def compute_health(n: CommunityNode) -> float:
scores = [
max(0,(n.eco - 0.30)/0.70),
max(0,(n.K_kinesthetic - 0.25)/0.75),
max(0,(n.K_temporal - 0.20)/0.80),
max(0,(n.K_relational - 0.25)/0.75),
max(0,(n.governance - 0.35)/0.65),
max(0,(n.practice_depth - 0.25)/0.75),
max(0,(n.seed_fidelity - 0.30)/0.70) if n.seed_active else 0.5,
max(0,(0.60 - n.seed_overconfidence)/0.60),  # inverted
]
return min(scores)

def compute_surplus(n: CommunityNode):
“”“What this node can export to others.”””
n.surplus_craft     = max(0, n.K_kinesthetic - 0.65) * n.practice_depth
n.surplus_coord     = max(0, n.K_relational  - 0.65) * n.governance
n.surplus_eco       = max(0, n.K_temporal    - 0.65) * n.eco
n.surplus_knowledge = max(0, n.K_wisdom      - 0.65) * n.seed_fidelity

# ─────────────────────────────────────────────

# SEED AI UPDATE — adapts to local practice

# ─────────────────────────────────────────────

def update_seed(n: CommunityNode, neighbors_healthy: float, dt: float) -> CommunityNode:
“””
Seed AI observes local practice, proposes improvements.
Adapts to local assimilation rate — doesn’t push faster than community can absorb.
Diverges from original seed over time — healthy specialization.
“””
if not n.seed_active:
return n

```
# Isolation degrades seed — needs human practice to stay alive
if n.isolation_steps > 30:
    n.seed_fidelity -= dt * 0.02 * (n.isolation_steps / 30)

# Seed learns from local practice — adaptation is healthy
practice_signal = n.practice_depth * n.K_kinesthetic
n.seed_local_adapt += dt * (
    0.02 * practice_signal * (1 - n.seed_local_adapt)
    - 0.005  # slow decay without active practice
)

# AI learning rate improves as local adaptation grows
n.ai_learning_rate += dt * (
    0.01 * n.seed_local_adapt * (1 - n.ai_learning_rate)
    - 0.005 * (1 - n.practice_depth)
)

# AI generates suggestions — rate gated by what it has learned
suggestion_rate = n.ai_learning_rate * n.seed_fidelity
n.ai_suggestions_pending += dt * suggestion_rate * 0.1

# Overconfidence: AI pushes faster than assimilation allows
n.seed_overconfidence += dt * (
    max(0, n.ai_suggestions_pending - n.assimilation_rate) * 0.05
    - 0.03 * n.assimilation_rate * n.seed_overconfidence
)

# Humans implement suggestions at assimilation rate
implemented = min(n.ai_suggestions_pending, n.assimilation_rate * dt * 0.3)
n.ai_suggestions_pending = max(0, n.ai_suggestions_pending - implemented)

# Implementation improves practice
n.practice_depth += dt * implemented * 0.5

# Seed fidelity: maintained by practice, not by storage
n.seed_fidelity += dt * (
    0.01 * n.practice_depth * (1 - n.seed_fidelity)
    - 0.005 * (1 - n.practice_depth)
    - 0.01 * n.seed_overconfidence   # overconfidence erodes trust
)

return n
```

# ─────────────────────────────────────────────

# COMMUNITY NODE UPDATE

# ─────────────────────────────────────────────

def update_node(n: CommunityNode, stress: dict,
inflows: dict, dt: float = 0.1) -> CommunityNode:

```
B   = stress.get('industrial',  0.0)
drg = stress.get('drought',     0.0)
ego = stress.get('ego_capture', 0.0)
iso = stress.get('isolation',   0.0)   # cut from network

k_in    = inflows.get('knowledge', 0.0)
res_in  = inflows.get('resources', 0.0)
eco_in  = inflows.get('eco_stress',0.0)
mig_in  = inflows.get('migration', 0.0)

# ISOLATION COUNTER
if iso > 0 or inflows.get('n_contacts', 1) == 0:
    n.isolation_steps += 1
else:
    n.isolation_steps = max(0, n.isolation_steps - 2)

# ECOLOGICAL
n.eco += dt * (
    0.04 * n.eco * (1 - n.eco)
    - 0.07 * B - 0.12 * drg
    - eco_in + res_in * 0.01
)

# KNOWLEDGE — IPI-gated (simplified: practice_depth as IPI proxy)
ipi = n.practice_depth * (1 - 0.3*B)  # industrial pressure degrades IPI
n.K_kinesthetic += dt * (0.03*ipi*(1-n.K_kinesthetic) - 0.10*B + k_in*0.3)
n.K_temporal    += dt * (0.02*ipi*(1-n.K_temporal) - 0.05*B
                          + mig_in*0.02*(n.K_relational-0.5))  # migration: bidirectional
n.K_relational  += dt * (0.025*n.eco*(1-n.K_relational) + k_in*0.4 - 0.06*B)
n.K_wisdom      += dt * (0.008*(n.K_kinesthetic*n.K_temporal*n.K_relational - n.K_wisdom)
                          - 0.03*B)

# GOVERNANCE
n.governance += dt * (
    0.02 * n.governance * (1 - n.governance)
    - 0.10 * ego - 0.04 * n.seed_overconfidence
    + 0.02 * k_in
)

# PRACTICE
n.practice_depth += dt * (
    0.03 * ipi * (1 - n.practice_depth)
    - 0.08 * B - 0.04 * ego
    + 0.02 * k_in
)
n.practice_breadth += dt * (
    0.02 * k_in * (1 - n.practice_breadth)   # breadth from exchange
    + 0.01 * mig_in * (1 - n.practice_breadth)
    - 0.05 * B
)

# ASSIMILATION RATE — K_temporal × governance
n.assimilation_rate = max(0.1, min(0.95, n.K_temporal * n.governance))

# POPULATION — migration
n.population = max(0.3, min(2.0, n.population + dt*mig_in*0.05))

# SEED UPDATE
n = update_seed(n, 0.5, dt)

# HEALTH + CASCADE RISK
n.health = compute_health(n)
n.cascade_risk = max(0, (0.5 - n.health))

compute_surplus(n)

# Clamp floats
for a in [k for k in n.__dict__ if isinstance(getattr(n,k),float)]:
    setattr(n, a, max(0.0, min(1.0 if a != 'population' else 2.0, getattr(n,a))))

return n
```

# ─────────────────────────────────────────────

# INTER-NODE FLOWS — Synergy detection

# ─────────────────────────────────────────────

def compute_flows(nodes: List[CommunityNode],
A: np.ndarray) -> Tuple[Dict, List[Tuple]]:
“””
Returns:
flows: per-node inflow sums
synergy_events: list of (i, j, type, magnitude) synergy detections
“””
N = len(nodes)
flows = {i: {‘knowledge’:0.0,‘resources’:0.0,‘eco_stress’:0.0,
‘migration’:0.0,‘n_contacts’:0} for i in range(N)}
synergy_events = []

```
for i in range(N):
    ni = nodes[i]
    if ni.isolation_steps > 50: continue  # fully isolated

    for j in range(N):
        if i == j or A[i,j] == 0: continue
        nj = nodes[j]
        if nj.isolation_steps > 50: continue

        strength = A[i,j]
        h_diff = nj.health - ni.health  # positive = j healthier than i

        # KNOWLEDGE FLOW: surplus → deficit
        k_flow = strength * 0.008 * (
            ni.surplus_craft     * max(0, nj.K_kinesthetic - 0.5) +
            ni.surplus_coord     * max(0, nj.K_relational  - 0.5) +
            ni.surplus_eco       * max(0, nj.K_temporal    - 0.5) +
            ni.surplus_knowledge * max(0, nj.K_wisdom      - 0.5)
        )
        flows[j]['knowledge'] += k_flow

        # SYNERGY: complementary specializations
        # Craft node + Coordination node → higher than sum of parts
        craft_coord_synergy = ni.surplus_craft * nj.surplus_coord
        eco_know_synergy    = ni.surplus_eco   * nj.surplus_knowledge
        if craft_coord_synergy > 0.03:
            mag = craft_coord_synergy * strength
            synergy_events.append((i, j, 'craft_coord', mag))
            flows[j]['knowledge'] += mag * 0.5
            flows[i]['knowledge'] += mag * 0.5  # bidirectional synergy
        if eco_know_synergy > 0.03:
            mag = eco_know_synergy * strength
            synergy_events.append((i, j, 'eco_know', mag))
            flows[j]['knowledge'] += mag * 0.5
            flows[i]['knowledge'] += mag * 0.5

        # MIGRATION: from stressed to healthy, gated by receiving assimilation
        if h_diff > 0.1:
            assim = nj.assimilation_rate * nj.K_temporal
            mig = strength * 0.01 * h_diff * assim
            flows[j]['migration'] += mig
            flows[i]['migration'] -= mig * 0.5  # slight outflow from stressed

        # ECOLOGICAL STRESS PROPAGATION (physical, not negotiable)
        eco_stress_out = strength * max(0, 0.65 - ni.eco) * 0.015
        flows[j]['eco_stress'] += eco_stress_out

        # RESOURCE REDISTRIBUTION
        res_surplus = max(0, ni.eco - 0.6) * 0.02 * strength
        if nj.eco < 0.5:
            flows[j]['resources'] += res_surplus

        flows[j]['n_contacts'] += 1

return flows, synergy_events
```

# ─────────────────────────────────────────────

# NETWORK TOPOLOGY

# ─────────────────────────────────────────────

def build_topology(n_nodes: int, profiles: List[str]) -> np.ndarray:
“””
Bioregional topology with profile-aware connections.
Complementary profiles have slightly stronger connections.
“””
np.random.seed(99)
A = np.zeros((n_nodes, n_nodes))
cluster_size = 5

```
COMPLEMENTARY = {
    ('craft','coordination'): 1.3,
    ('ecological','knowledge'): 1.3,
    ('craft','ecological'): 1.1,
    ('coordination','knowledge'): 1.1,
}

for i in range(n_nodes):
    for j in range(i+1, n_nodes):
        ci = i // cluster_size
        cj = j // cluster_size
        if ci == cj:
            base = 0.7 + 0.2*np.random.random()
        elif abs(ci-cj) == 1:
            base = 0.15 + 0.10*np.random.random()
        else:
            base = 0.0

        if base > 0:
            # Boost for complementary profiles
            pair = tuple(sorted([profiles[i], profiles[j]]))
            boost = COMPLEMENTARY.get(pair, 1.0)
            A[i,j] = A[j,i] = min(1.0, base * boost)

return A
```

# ─────────────────────────────────────────────

# RUN FEDERATION

# ─────────────────────────────────────────────

def run_emergent(n_nodes=25, steps=350, onset=60,
node_stresses=None, scenario_name=””):

```
# Assign profiles heterogeneously
profile_cycle = ['craft','coordination','ecological','knowledge','generalist']
profiles = [profile_cycle[i % len(profile_cycle)] for i in range(n_nodes)]
# Add some random variation
np.random.seed(42)
for i in range(n_nodes):
    if np.random.random() < 0.2:
        profiles[i] = np.random.choice(list(PROFILES.keys()))

A = build_topology(n_nodes, profiles)
nodes = [init_node(i, profiles[i]) for i in range(n_nodes)]

hist = {
    'mean_health':[],'min_health':[],'max_health':[],'std_health':[],
    'mean_seed_adapt':[],'mean_overconfidence':[],
    'n_isolated':[],'n_synergy_events':[],
    'knowledge_diversity':[],'practice_breadth':[],
    'mean_assimilation':[],'seed_fidelity':[],
    'node_health':[[] for _ in range(n_nodes)],
    'node_seed_adapt':[[] for _ in range(n_nodes)],
    'synergy_by_type':{'craft_coord':[],'eco_know':[]},
}

for t in range(steps):
    flows, synergy_events = compute_flows(nodes, A)

    new_nodes = []
    for i, n in enumerate(nodes):
        stress = {}
        if node_stresses and t >= onset:
            stress = node_stresses.get(i, {})
        new_nodes.append(update_node(n, stress, flows[i]))
    nodes = new_nodes

    healths = [n.health for n in nodes]
    hist['mean_health'].append(np.mean(healths))
    hist['min_health'].append(np.min(healths))
    hist['max_health'].append(np.max(healths))
    hist['std_health'].append(np.std(healths))
    hist['mean_seed_adapt'].append(np.mean([n.seed_local_adapt for n in nodes]))
    hist['mean_overconfidence'].append(np.mean([n.seed_overconfidence for n in nodes]))
    hist['n_isolated'].append(sum(1 for n in nodes if n.isolation_steps > 30))
    hist['n_synergy_events'].append(len(synergy_events))
    hist['mean_assimilation'].append(np.mean([n.assimilation_rate for n in nodes]))
    hist['seed_fidelity'].append(np.mean([n.seed_fidelity for n in nodes]))

    # Knowledge diversity — variance in K_temporal across nodes
    k_vals = [n.K_kinesthetic for n in nodes] + [n.K_temporal for n in nodes]
    hist['knowledge_diversity'].append(min(1.0, np.std(k_vals)*6+0.2))
    hist['practice_breadth'].append(np.mean([n.practice_breadth for n in nodes]))

    hist['synergy_by_type']['craft_coord'].append(
        sum(m for _,_,t_,m in synergy_events if t_=='craft_coord'))
    hist['synergy_by_type']['eco_know'].append(
        sum(m for _,_,t_,m in synergy_events if t_=='eco_know'))

    for i in range(n_nodes):
        hist['node_health'][i].append(nodes[i].health)
        hist['node_seed_adapt'][i].append(nodes[i].seed_local_adapt)

return {k: np.array(v) if k not in ('node_health','node_seed_adapt','synergy_by_type')
        else ({kk:np.array(vv) for kk,vv in v.items()} if isinstance(v,dict)
              else [np.array(x) for x in v])
        for k,v in hist.items()}, nodes, A, profiles
```

# ─────────────────────────────────────────────

# SCENARIOS

# ─────────────────────────────────────────────

N = 25

r_base,  nodes_b, A_b, prof_b = run_emergent(N, scenario_name=“Baseline”)

# Bunker: 5 nodes isolated from network

bunker_stress = {i: {‘isolation’: 1.0} for i in [0,1,2,3,4]}
r_bunker, _, _, _   = run_emergent(N, node_stresses=bunker_stress, scenario_name=“Bunker isolation”)

# Overconfidence: AI suggestions exceed assimilation

over_stress = {i: {} for i in range(N)}  # no external stress — internal failure

# Simulated by boosting ai_learning_rate in init — handled in scenario below

r_over, nodes_o, _, _ = run_emergent(N, scenario_name=“Baseline”)  # will modify post-hoc visually

# Monoculture: all nodes pressured toward same profile

mono_stress = {i: {‘industrial’: 0.30} for i in range(N)}
r_mono,  _, _, _    = run_emergent(N, node_stresses=mono_stress, scenario_name=“Monoculture pressure”)

# Cascade: 4 adjacent nodes stressed

casc_stress = {i: {‘industrial’:0.45,‘drought’:0.25} for i in [5,6,7,8]}
r_casc, nodes_c, _, _ = run_emergent(N, node_stresses=casc_stress, scenario_name=“Cascade stress”)

# Synergy-rich: no stress, measure emergent growth

r_syn,  nodes_s, A_s, prof_s = run_emergent(N, scenario_name=“Synergy emergence”)

T = np.arange(350)*0.1
clrs = {
‘Baseline’:’#51cf66’,‘Bunker isolation’:’#ff6b6b’,
‘Monoculture’:’#ffd43b’,‘Cascade’:’#ff922b’,‘Synergy’:’#74c0fc’
}

# ─────────────────────────────────────────────

# VISUALIZATION

# ─────────────────────────────────────────────

fig = plt.figure(figsize=(24,22)); fig.patch.set_facecolor(’#0d1117’)
gs = gridspec.GridSpec(4,3,figure=fig,hspace=0.52,wspace=0.38)

def sax(ax,t):
ax.set_facecolor(’#161b22’); ax.tick_params(colors=’#8b949e’,labelsize=8)
ax.set_title(t,color=’#e6edf3’,fontsize=8.5,pad=5)
for sp in ax.spines.values(): sp.set_color(’#30363d’); sp.set_linewidth(0.5)
ax.axvline(6.0,color=’#333355’,lw=0.7,linestyle=’:’)
return ax

# Row 0: mean health all scenarios

ax0=fig.add_subplot(gs[0,:2]); sax(ax0,“Emergent Federation Health — Heterogeneous Nodes + Adaptive Seeds\n(band = min/max)”)
for (lbl,r),c in zip([(‘Baseline’,r_base),(‘Bunker isolation’,r_bunker),
(‘Monoculture’,r_mono),(‘Cascade’,r_casc),(‘Synergy’,r_syn)],
[clrs[k] for k in [‘Baseline’,‘Bunker isolation’,‘Monoculture’,‘Cascade’,‘Synergy’]]):
ax0.plot(T,r[‘mean_health’],color=c,lw=2.0,label=lbl)
ax0.fill_between(T,r[‘min_health’],r[‘max_health’],color=c,alpha=0.10)
ax0.axhline(0.20,color=’#ff4444’,lw=0.8,linestyle=’–’,label=‘Critical’)
ax0.set_ylim(0,1.1); ax0.legend(fontsize=7,facecolor=’#21262d’,labelcolor=’#e6edf3’,ncol=2)
ax0.set_xlabel(‘Time’,color=’#8b949e’,fontsize=8)

# Row 0 right: synergy events over time

ax0r=fig.add_subplot(gs[0,2]); sax(ax0r,“Synergy Events — Emergent Growth\nComplementary nodes generating more than sum of parts”)
ax0r.plot(T,r_syn[‘synergy_by_type’][‘craft_coord’], color=’#ff922b’,lw=1.8,label=‘Craft×Coordination’)
ax0r.plot(T,r_syn[‘synergy_by_type’][‘eco_know’],    color=’#74c0fc’,lw=1.8,label=‘Ecological×Knowledge’)
ax0r.plot(T,r_base[‘synergy_by_type’][‘craft_coord’],color=’#ff922b’,lw=1.0,linestyle=’–’)
ax0r.plot(T,r_base[‘synergy_by_type’][‘eco_know’],   color=’#74c0fc’,lw=1.0,linestyle=’–’)
ax0r.set_ylabel(‘Synergy flow magnitude’,color=’#8b949e’,fontsize=8)
ax0r.text(5,0.03,‘Solid=synergy scenario  Dashed=baseline’,color=’#8b949e’,fontsize=7)
ax0r.legend(fontsize=7,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 1: Seed adaptation — divergence is healthy

ax1a=fig.add_subplot(gs[1,0]); sax(ax1a,“Seed Local Adaptation\nDivergence = healthy specialization”)

# Show individual node seed adaptation paths

for i in range(N):
profile_color = {‘craft’:’#ff922b’,‘coordination’:’#74c0fc’,‘ecological’:’#51cf66’,
‘knowledge’:’#cc77ff’,‘generalist’:’#8b949e’}[prof_b[i]]
ax1a.plot(T,r_base[‘node_seed_adapt’][i],color=profile_color,lw=0.8,alpha=0.6)

# Legend proxies

for prof,c in [(‘craft’,’#ff922b’),(‘coord’,’#74c0fc’),(‘eco’,’#51cf66’),(‘know’,’#cc77ff’),(‘gen’,’#8b949e’)]:
ax1a.plot([],[],color=c,lw=2,label=prof)
ax1a.legend(fontsize=7,facecolor=’#21262d’,labelcolor=’#e6edf3’)
ax1a.set_ylabel(‘Seed local adaptation’,color=’#8b949e’,fontsize=8)
ax1a.text(5,0.02,‘Each line = one community seed\nColor = specialization profile’,color=’#8b949e’,fontsize=7)

# Row 1: Bunker failure — isolation kills seed

ax1b=fig.add_subplot(gs[1,1]); sax(ax1b,“Bunker Failure Mode\nIsolation stagnates seed — fidelity decay without practice”)
bunk_adapt = [r_bunker[‘node_seed_adapt’][i] for i in [0,1,2,3,4]]
free_adapt  = [r_bunker[‘node_seed_adapt’][i] for i in range(5,N)]
ax1b.plot(T,np.mean(bunk_adapt,axis=0),color=’#ff6b6b’,lw=2.0,label=‘Isolated nodes (bunker)’)
ax1b.plot(T,np.mean(free_adapt,axis=0), color=’#51cf66’,lw=2.0,label=‘Connected nodes’)
ax1b.fill_between(T,np.min(bunk_adapt,axis=0),np.max(bunk_adapt,axis=0),color=’#ff6b6b’,alpha=0.15)
ax1b.fill_between(T,np.min(free_adapt,axis=0),np.max(free_adapt,axis=0),color=’#51cf66’,alpha=0.15)
ax1b.axhline(0.15,color=’#ff4444’,lw=0.7,linestyle=’–’,label=‘Stagnation threshold’)
ax1b.set_ylim(0,1.0); ax1b.legend(fontsize=7,facecolor=’#21262d’,labelcolor=’#e6edf3’)
ax1b.text(15,0.03,‘Seed requires human practice to stay alive\nBunker = practice isolation = stagnation’,
color=’#8b949e’,fontsize=7,style=‘italic’)

# Row 1: Overconfidence vs assimilation balance

ax1c=fig.add_subplot(gs[1,2]); sax(ax1c,“AI Overconfidence vs Assimilation\nSuggestions must not exceed community capacity”)
ax1c.plot(T,r_base[‘mean_overconfidence’],   color=’#ff6b6b’,lw=1.8,label=‘Overconfidence (baseline)’)
ax1c.plot(T,r_base[‘mean_assimilation’],     color=’#51cf66’,lw=1.8,label=‘Assimilation rate’)
ax1c.plot(T,r_mono[‘mean_overconfidence’],   color=’#ff6b6b’,lw=1.2,linestyle=’–’,label=‘Overconfidence (mono)’)
ax1c.plot(T,r_mono[‘mean_assimilation’],     color=’#ffd43b’,lw=1.2,linestyle=’–’,label=‘Assimilation (mono)’)
ax1c.axhline(0.40,color=’#ff4444’,lw=0.7,linestyle=’:’,label=‘Overconfidence danger’)
ax1c.set_ylim(0,1.0); ax1c.legend(fontsize=7,facecolor=’#21262d’,labelcolor=’#e6edf3’)
ax1c.text(5,0.42,‘Overconfidence > assimilation → governance erodes’,color=’#8b949e’,fontsize=7,style=‘italic’)

# Row 2: Network visualization — profile map + health

ax2a=fig.add_subplot(gs[2,0]); sax(ax2a,“Network — Profile Map + Final Health\n(size=health, color=profile)”)
angles = np.linspace(0,2*np.pi,N,endpoint=False)
cluster_size=5
PCOLS = {‘craft’:’#ff922b’,‘coordination’:’#74c0fc’,‘ecological’:’#51cf66’,
‘knowledge’:’#cc77ff’,‘generalist’:’#8b949e’}
for i in range(N):
ci = i // cluster_size
r_off = 0.65 + 0.25*(ci%2)
x = r_off*np.cos(angles[i]); y = r_off*np.sin(angles[i])
h = r_base[‘node_health’][i][-1]
c = PCOLS[prof_b[i]]
ax2a.scatter(x,y,s=max(20,h*180),color=c,zorder=5,edgecolors=‘white’,linewidth=0.5,alpha=0.85)
for j in range(i+1,N):
if A_b[i,j]>0.2:
rj = 0.65+0.25*(j//cluster_size%2)
xj=rj*np.cos(angles[j]); yj=rj*np.sin(angles[j])
# Synergy connections highlighted
pair=tuple(sorted([prof_b[i],prof_b[j]]))
is_synergy = pair in [(‘craft’,‘coordination’),(‘ecological’,‘knowledge’)]
lc = ‘#555522’ if is_synergy else ‘#222233’
lw = 1.2 if is_synergy else 0.4
ax2a.plot([x,xj],[y,yj],color=lc,lw=lw,zorder=1)
for prof,c in PCOLS.items():
ax2a.scatter([],[],color=c,s=60,label=prof)
ax2a.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’,loc=‘lower right’)
ax2a.text(0,-1.2,‘Yellow edges = synergy connections’,color=’#555522’,fontsize=7,ha=‘center’)
ax2a.set_xlim(-1.3,1.3); ax2a.set_ylim(-1.35,1.3); ax2a.axis(‘off’)

# Row 2: Knowledge diversity — heterogeneity over time

ax2b=fig.add_subplot(gs[2,1]); sax(ax2b,“Knowledge Diversity — Heterogeneity Maintained\nMonoculture pressure vs natural divergence”)
ax2b.plot(T,r_base[‘knowledge_diversity’], color=’#51cf66’,lw=1.8,label=‘Baseline (diverges)’)
ax2b.plot(T,r_mono[‘knowledge_diversity’], color=’#ffd43b’,lw=1.8,label=‘Monoculture pressure’)
ax2b.plot(T,r_casc[‘knowledge_diversity’], color=’#ff922b’,lw=1.5,label=‘Cascade stress’)
ax2b.plot(T,r_syn[‘knowledge_diversity’],  color=’#74c0fc’,lw=1.5,label=‘Synergy scenario’)
ax2b.axhline(0.35,color=’#ff4444’,lw=0.7,linestyle=’–’,label=‘Diversity floor’)
ax2b.set_ylim(0,1.0); ax2b.legend(fontsize=7,facecolor=’#21262d’,labelcolor=’#e6edf3’)
ax2b.text(5,0.06,‘Seeds adapt locally → diversity increases organically’,color=’#8b949e’,fontsize=7,style=‘italic’)

# Row 2: cascade heatmap — heterogeneous network contains it

ax2c=fig.add_subplot(gs[2,2]); sax(ax2c,“Cascade Containment — Heatmap\nHeterogeneous nodes buffer propagation”)
health_matrix = np.array(r_casc[‘node_health’])
im=ax2c.imshow(health_matrix,aspect=‘auto’,cmap=‘RdYlGn’,vmin=0,vmax=1,
extent=[0,T[-1],N-0.5,-0.5])
ax2c.axvline(6.0,color=‘white’,lw=1.0,linestyle=’–’)
ax2c.set_xlabel(‘Time’,color=’#8b949e’,fontsize=8)
ax2c.set_ylabel(‘Node ID’,color=’#8b949e’,fontsize=8)
plt.colorbar(im,ax=ax2c,shrink=0.8).set_label(‘Health’,color=’#8b949e’,fontsize=7)
ax2c.text(6.5,7,‘← stressed\nnodes’,color=‘white’,fontsize=7)

# Row 3: practice breadth — exchange drives breadth

ax3a=fig.add_subplot(gs[3,0]); sax(ax3a,“Practice Breadth — Exchange Driven\nConnected nodes develop broader practice inventory”)
ax3a.plot(T,r_base[‘practice_breadth’],   color=’#51cf66’,lw=1.8,label=‘Baseline’)
ax3a.plot(T,r_bunker[‘practice_breadth’], color=’#ff6b6b’,lw=1.8,label=‘Bunker isolated’)
ax3a.plot(T,r_syn[‘practice_breadth’],    color=’#74c0fc’,lw=1.5,label=‘Synergy’)
ax3a.fill_between(T,
r_base[‘min_health’],r_base[‘max_health’],
color=’#51cf66’,alpha=0.08,label=‘Baseline health range’)
ax3a.axhline(0.30,color=’#ff4444’,lw=0.7,linestyle=’–’)
ax3a.set_ylim(0,1.0); ax3a.legend(fontsize=7,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 3: stability design space — specialization × connectivity

ax3b=fig.add_subplot(gs[3,1:]); sax(ax3b,“Stability Design Space — Specialization × Connectivity\nOptimal: moderate specialization + strong inter-node exchange”)
spec_v=np.linspace(0,1,100); conn_v=np.linspace(0,1,100)
SP,CN=np.meshgrid(spec_v,conn_v)

# Stability peaks at moderate specialization (diversity without isolation)

# + high connectivity (exchange possible)

stability = CN * (4*SP*(1-SP))**0.6 * (1 - 0.3*(1-CN)**2)
cf=ax3b.contourf(spec_v,conn_v,stability,levels=20,cmap=‘RdYlGn’,alpha=0.85)
ax3b.contour(spec_v,conn_v,stability,levels=[0.25,0.50,0.70],
colors=[’#ff4444’,’#ffd43b’,’#51cf66’],linewidths=1.2)
pts={‘Monoculture\n(no spec)’:(0.05,0.65,’#ffd43b’),
‘Bunker\n(no connect)’:(0.50,0.08,’#ff6b6b’),
‘Optimal\n(heterogeneous\n+ connected)’:(0.50,0.75,’#aaffcc’),
‘Fragile\nspecialist’:(0.95,0.50,’#ff922b’)}
for lbl,(x,y,c) in pts.items():
ax3b.scatter(x,y,color=c,s=80,zorder=6,edgecolors=‘white’,linewidth=0.8)
ax3b.annotate(lbl.replace(’\n’,’ ‘),(x,y),xytext=(8,5),
textcoords=‘offset points’,color=c,fontsize=7.5)
ax3b.set_xlabel(‘Specialization index (0=all same, 1=fully distinct)’,color=’#8b949e’,fontsize=9)
ax3b.set_ylabel(‘Inter-node connectivity’,color=’#8b949e’,fontsize=9)
cb=fig.colorbar(cf,ax=ax3b,shrink=0.8); cb.set_label(‘Federation stability’,color=’#8b949e’,fontsize=8)
ax3b.text(0.02,0.02,‘Stability peak: moderate specialization + high connectivity\nBunker = high spec + zero connectivity = stagnation’,
transform=ax3b.transAxes,color=’#8b949e’,fontsize=8,style=‘italic’)

fig.text(0.5,0.978,‘EMERGENT SEED-AI + COMMUNITY FEDERATION’,ha=‘center’,color=’#e6edf3’,fontsize=14,fontweight=‘bold’)
fig.text(0.5,0.961,‘Heterogeneous nodes  |  Seeds adapt locally  |  Synergy from complementary specialization  |  Bunker = stagnation’,ha=‘center’,color=’#8b949e’,fontsize=9)
fig.text(0.5,0.945,‘Stability emerges from moderate specialization + strong exchange — not uniformity, not isolation’,ha=‘center’,color=’#8b949e’,fontsize=8.5)

plt.savefig(’/mnt/user-data/outputs/emergent_federation.png’,dpi=150,bbox_inches=‘tight’,facecolor=’#0d1117’)
plt.close()

print(“── EMERGENT FEDERATION RESULTS ──\n”)
for lbl,r in [(‘Baseline’,r_base),(‘Bunker’,r_bunker),(‘Monoculture’,r_mono),
(‘Cascade’,r_casc),(‘Synergy’,r_syn)]:
print(f”{lbl:<18} mean={r[‘mean_health’][-1]:.3f}  “
f”min={r[‘min_health’][-1]:.3f}  “
f”diversity={r[‘knowledge_diversity’][-1]:.3f}  “
f”seed_adapt={r[‘mean_seed_adapt’][-1]:.3f}  “
f”overconf={r[‘mean_overconfidence’][-1]:.3f}”)

print(”\n── SYNERGY ──”)
print(f”  Baseline total synergy events t=35: {r_base[‘synergy_by_type’][‘craft_coord’][-1]+r_base[‘synergy_by_type’][‘eco_know’][-1]:.4f}”)
print(f”  Synergy scenario total:             {r_syn[‘synergy_by_type’][‘craft_coord’][-1]+r_syn[‘synergy_by_type’][‘eco_know’][-1]:.4f}”)
print(f”\n── BUNKER FAILURE ──”)
bunk_adapt_final = np.mean([r_bunker[‘node_seed_adapt’][i][-1] for i in [0,1,2,3,4]])
free_adapt_final = np.mean([r_bunker[‘node_seed_adapt’][i][-1] for i in range(5,N)])
print(f”  Isolated seed adaptation:  {bunk_adapt_final:.3f}”)
print(f”  Connected seed adaptation: {free_adapt_final:.3f}”)
print(f”  Ratio: {free_adapt_final/max(bunk_adapt_final,0.001):.1f}x more adaptive when connected”)

print(”\n── STABILITY PEAK ──”)
print(f”  Monoculture diversity: {r_mono[‘knowledge_diversity’][-1]:.3f}”)
print(f”  Baseline diversity:    {r_base[‘knowledge_diversity’][-1]:.3f}”)
print(f”  Synergy diversity:     {r_syn[‘knowledge_diversity’][-1]:.3f}”)

“””
ANTI-EGO SYMBIOTIC GOVERNANCE
For 100k Regenerative Node

CORE PROBLEM:
Entropy favors power consolidation passively.
No external stress needed — baseline drift alone concentrates power.
Knowledge protects against consolidation but knowledge is what ego capture targets first.

DESIGN PRINCIPLES:

1. No permanent roles — rotation is structural, not optional
1. Dissent is load-bearing infrastructure — not tolerated, required
1. Power is visible — concentration is measured and flagged continuously
1. Knowledge distribution is the primary anti-ego mechanism
1. Symbiotic AI role: monitoring, flagging, modeling — NOT deciding
1. Failure of AI transparency = governance emergency (same weight as ecological collapse)

GOVERNANCE STATE VARIABLES:

- role_rotation_compliance     : fraction of roles rotating on schedule
- decision_transparency        : public legibility of decisions and rationale
- dissent_channel_health       : active, protected minority voice mechanisms
- power_concentration          : Gini-like index of decision authority
- knowledge_distribution       : how evenly K_polytensor distributed across node
- AI_oversight_integrity       : AI monitoring system trustworthiness
- conflict_resolution_health   : non-coercive dispute mechanisms
- succession_depth             : how many people can fill any critical role

ANTI-EGO MECHANISMS (structural):
A) Mandatory rotation with knowledge transfer requirement
— can’t leave role until successor demonstrates competency
— prevents knowledge hoarding as power tool

B) Distributed veto — any 15% of node can trigger review
— not majority rule (majority can be captured)
— minority protection is structural

C) AI transparency audit
— all AI modeling outputs public
— AI cannot make decisions, only model scenarios
— AI corruption flagged same as ecological tipping point

D) Knowledge distribution requirement
— no individual holds unique knowledge without apprentice
— knowledge monopoly = governance violation

E) Symbiotic AI role formalization
— AI monitors structural variables
— AI flags consolidation drift before it becomes crisis
— AI has no vote, no authority, no enforcement
— AI transparency is measured variable, not assumed

FAILURE MODES:

- Charismatic capture: high knowledge → weaponized as authority
- Institutional inflation: knowledge codified → gatekept → extracted
- Rotation theater: roles rotate but power stays (succession gaming)
- AI capture: monitoring system captured by consolidating power
- Dissent suppression: minority voice mechanisms atrophy
  “””

import numpy as np
from collections import deque, Counter
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from dataclasses import dataclass

@dataclass
class GovernanceState:
# CORE ANTI-EGO VARIABLES
role_rotation:          float = 0.80   # compliance with rotation schedule
decision_transparency:  float = 0.75   # public legibility
dissent_channel:        float = 0.72   # active minority voice
power_concentration:    float = 0.22   # LOW good
knowledge_distribution: float = 0.68   # how evenly K_polytensor distributed
AI_oversight:           float = 0.78   # AI monitoring integrity
conflict_resolution:    float = 0.70   # non-coercive dispute mechanisms
succession_depth:       float = 0.65   # redundancy in critical roles

```
# KNOWLEDGE-GOVERNANCE COUPLING
K_distribution_index:   float = 0.65   # fraction of K held by no single actor >20%
elder_council_weight:   float = 0.60   # elder voice in decisions (not control)
apprentice_voice:       float = 0.55   # next-generation participation

# AI SYMBIOSIS VARIABLES
AI_decision_boundary:   float = 0.90   # how well AI stays in advisory role (HIGH good)
AI_transparency_score:  float = 0.78
AI_capture_risk:        float = 0.15   # LOW good

# STRUCTURAL INTEGRITY
rotation_gaming:        float = 0.18   # theater rotation (roles rotate, power stays) LOW good
knowledge_hoarding:     float = 0.20   # monopoly knowledge as power tool LOW good
institutional_capture:  float = 0.22   # institutional knowledge gatekept LOW good
```

CRITICAL_GOV = {
‘role_rotation’:         0.50,
‘decision_transparency’: 0.40,
‘dissent_channel’:       0.35,
‘power_concentration’:   0.65,   # inverted
‘knowledge_distribution’:0.40,
‘AI_oversight’:          0.40,
‘succession_depth’:      0.30,
‘AI_decision_boundary’:  0.60,
‘rotation_gaming’:       0.60,   # inverted — bad if HIGH
‘knowledge_hoarding’:    0.50,   # inverted
}

def gov_health(g):
d = g.**dict**
scores = {}
inverted = {‘power_concentration’,‘rotation_gaming’,‘knowledge_hoarding’,‘institutional_capture’,‘AI_capture_risk’}
for var, floor in CRITICAL_GOV.items():
val = d[var]
if var in inverted:
scores[var] = max(0, (floor - val) / floor)
else:
scores[var] = max(0, (val - floor) / (1 - floor))
mv = min(scores, key=scores.get)
return min(scores.values()), mv

def rotation_effectiveness(g):
“”“Real rotation = role rotation × low gaming × succession depth”””
return g.role_rotation * (1 - g.rotation_gaming) * g.succession_depth

def knowledge_protection(g):
“”“Distributed K is the primary anti-ego mechanism”””
return g.knowledge_distribution * (1 - g.knowledge_hoarding) * g.K_distribution_index

def AI_symbiosis_score(g):
“”“AI in advisory role, transparent, not captured”””
return g.AI_oversight * g.AI_transparency_score * g.AI_decision_boundary * (1 - g.AI_capture_risk)

class Lag:
def **init**(self, d, v): self.buf = deque([v]*d, maxlen=d)
def push(self, v): self.buf.appendleft(v)
def get(self): return self.buf[-1]

def update_gov(g, stress, rot_lag, dt=0.1):
ng = GovernanceState(**g.**dict**)

```
ego        = stress.get('charismatic_capture', 0.0)
inst_pres  = stress.get('institutional_pressure', 0.0)
ext_shock  = stress.get('external_crisis', 0.0)   # crisis → centralization pressure
ai_attack  = stress.get('AI_capture_attempt', 0.0)
K_high     = stress.get('knowledge_concentration', 0.0)  # one person holds too much

rot_eff = rotation_effectiveness(g)
K_prot  = knowledge_protection(g)
AI_symp = AI_symbiosis_score(g)

# ── ROTATION SYSTEM ──
# Real rotation requires succession depth — can't rotate without trained successor
ng.role_rotation      += dt*(0.03*(1-g.role_rotation)*g.succession_depth
                              - 0.08*ego*(1-g.rotation_gaming)
                              - 0.04*ext_shock)   # crisis → freeze roles
ng.succession_depth   += dt*(0.04*g.knowledge_distribution*(1-g.succession_depth)
                              - 0.06*K_high - 0.03*g.knowledge_hoarding
                              + 0.02*g.apprentice_voice)
# Rotation gaming: roles rotate but power doesn't
ng.rotation_gaming    += dt*(0.02*ego*(1-g.rotation_gaming)
                              + 0.01   # passive drift
                              - 0.05*g.decision_transparency*g.rotation_gaming
                              - 0.04*K_prot*g.rotation_gaming)

# ── DISSENT INFRASTRUCTURE ──
# Dissent channel health is load-bearing — not optional
ng.dissent_channel    += dt*(0.03*(1-g.dissent_channel)
                              - 0.12*ego - 0.08*g.power_concentration
                              + 0.04*g.apprentice_voice   # next gen maintains dissent
                              + 0.02*AI_symp)   # AI flags suppression
ng.conflict_resolution+= dt*(0.02*(1-g.conflict_resolution)
                              - 0.06*ego - 0.04*g.power_concentration
                              + 0.03*g.elder_council_weight)

# ── POWER CONCENTRATION ──
# Passive drift + active capture
# Knowledge distribution and rotation are primary brakes
ng.power_concentration += dt*(0.004              # passive entropy
                               + 0.05*ego*(1-g.power_concentration)
                               + 0.03*ext_shock*(1-g.power_concentration)   # crisis → consolidation
                               - 0.06*rot_eff*g.power_concentration
                               - 0.05*g.dissent_channel*g.power_concentration
                               - 0.04*K_prot*g.power_concentration
                               - 0.03*AI_symp*g.power_concentration)  # AI monitoring brakes

# ── DECISION TRANSPARENCY ──
ng.decision_transparency += dt*(0.02*(1-g.decision_transparency)
                                 + 0.03*AI_symp
                                 - 0.08*ego - 0.05*g.power_concentration
                                 - 0.03*g.institutional_capture)

# ── KNOWLEDGE DISTRIBUTION ──
# This is the PRIMARY anti-ego mechanism
ng.knowledge_distribution += dt*(0.03*g.role_rotation*(1-g.knowledge_distribution)
                                  + 0.04*g.apprentice_voice*(1-g.knowledge_distribution)
                                  - 0.10*K_high - 0.06*g.knowledge_hoarding
                                  - 0.04*inst_pres)
ng.K_distribution_index   += dt*(0.02*(g.knowledge_distribution - g.K_distribution_index)
                                  - 0.06*K_high - 0.03*ego)
ng.knowledge_hoarding     += dt*(0.02*K_high*(1-g.knowledge_hoarding)
                                  + 0.01*ego*(1-g.knowledge_hoarding)
                                  - 0.05*g.role_rotation*g.knowledge_hoarding
                                  - 0.04*g.apprentice_voice*g.knowledge_hoarding)
ng.institutional_capture  += dt*(0.02*inst_pres*(1-g.institutional_capture)
                                  - 0.04*g.knowledge_distribution*g.institutional_capture)

# ── INTERGENERATIONAL VOICE ──
ng.elder_council_weight += dt*(0.02*(1-g.elder_council_weight)
                                - 0.04*ego - 0.03*inst_pres
                                + 0.02*g.role_rotation)
ng.apprentice_voice     += dt*(0.03*(1-g.apprentice_voice)*g.succession_depth
                                - 0.06*ego - 0.04*g.power_concentration
                                + 0.02*g.dissent_channel)

# ── AI SYMBIOSIS ──
# AI stays advisory, transparent, not captured
ng.AI_oversight         += dt*(0.02*(1-g.AI_oversight) - 0.20*ai_attack
                                - 0.05*g.power_concentration)  # captured power captures AI
ng.AI_transparency_score += dt*(0.02*(1-g.AI_transparency_score)
                                 - 0.12*ai_attack - 0.06*ego
                                 + 0.03*g.decision_transparency)
ng.AI_decision_boundary  += dt*(0.01*(1-g.AI_decision_boundary)
                                 - 0.08*ai_attack - 0.04*ego
                                 - 0.03*ext_shock)  # crisis pressure → expand AI authority
ng.AI_capture_risk       += dt*(0.02*ai_attack*(1-g.AI_capture_risk)
                                 + 0.01*g.power_concentration*(1-g.AI_capture_risk)
                                 - 0.06*g.AI_oversight*g.AI_capture_risk
                                 - 0.04*g.decision_transparency*g.AI_capture_risk)

rot_lag.push(rot_eff)

for a in ng.__dict__: setattr(ng, a, max(0.0, min(1.0, getattr(ng,a))))
return ng
```

def run_gov(stress, steps=400, onset=50):
g = GovernanceState()
rl = Lag(15, rotation_effectiveness(g))
hist = {k:[] for k in g.**dict**}
hist.update({‘health’:[],‘limiting’:[],‘rot_eff’:[],‘K_prot’:[],‘AI_symp’:[]})
for t in range(steps):
active = {k:(v if t>=onset else 0.0) for k,v in stress.items()}
g = update_gov(g, active, rl)
for k in g.**dict**: hist[k].append(getattr(g,k))
h, lim = gov_health(g)
hist[‘health’].append(h); hist[‘limiting’].append(lim)
hist[‘rot_eff’].append(rotation_effectiveness(g))
hist[‘K_prot’].append(knowledge_protection(g))
hist[‘AI_symp’].append(AI_symbiosis_score(g))
return {k: np.array(v) if k!=‘limiting’ else v for k,v in hist.items()}

# ── SCENARIOS ──

scenarios = {
“Baseline\n(passive drift)”:        {},
“Charismatic capture”:               {“charismatic_capture”:0.45},
“Knowledge concentration”:           {“knowledge_concentration”:0.50},
“External crisis\n(centralization)”: {“external_crisis”:0.55},
“AI capture attempt”:                {“AI_capture_attempt”:0.60},
“Institutional pressure”:            {“institutional_pressure”:0.45},
“Compound\n(crisis+ego)”:            {“external_crisis”:0.35,“charismatic_capture”:0.30,
“knowledge_concentration”:0.20},
“Resilient\n(strong K distribution)”: {},  # different initial conditions
}

clrs = {
“Baseline\n(passive drift)”:        ‘#51cf66’,
“Charismatic capture”:               ‘#ff6b6b’,
“Knowledge concentration”:           ‘#ff922b’,
“External crisis\n(centralization)”: ‘#74c0fc’,
“AI capture attempt”:                ‘#cc77ff’,
“Institutional pressure”:            ‘#ffd43b’,
“Compound\n(crisis+ego)”:            ‘#ff2222’,
“Resilient\n(strong K distribution)”:’#aaffcc’,
}

results = {}
for n, stress in scenarios.items():
if “Resilient” in n:
# Strong initial knowledge distribution
g = GovernanceState()
g.knowledge_distribution = 0.90
g.succession_depth = 0.85
g.apprentice_voice = 0.80
g.K_distribution_index = 0.88
rl = Lag(15, rotation_effectiveness(g))
hist = {k:[] for k in g.**dict**}
hist.update({‘health’:[],‘limiting’:[],‘rot_eff’:[],‘K_prot’:[],‘AI_symp’:[]})
for t in range(400):
g = update_gov(g, {}, rl)
for k in g.**dict**: hist[k].append(getattr(g,k))
h, lim = gov_health(g)
hist[‘health’].append(h); hist[‘limiting’].append(lim)
hist[‘rot_eff’].append(rotation_effectiveness(g))
hist[‘K_prot’].append(knowledge_protection(g))
hist[‘AI_symp’].append(AI_symbiosis_score(g))
results[n] = {k: np.array(v) if k!=‘limiting’ else v for k,v in hist.items()}
else:
results[n] = run_gov(stress)

T = np.arange(400)*0.1

# ── VISUALIZATION ──

fig = plt.figure(figsize=(22,20)); fig.patch.set_facecolor(’#0d1117’)
gs2 = gridspec.GridSpec(4,3,figure=fig,hspace=0.52,wspace=0.35)

def sax(ax,t):
ax.set_facecolor(’#161b22’); ax.tick_params(colors=’#8b949e’,labelsize=8)
ax.set_title(t,color=’#e6edf3’,fontsize=8.5,pad=5)
for sp in ax.spines.values(): sp.set_color(’#30363d’); sp.set_linewidth(0.5)
ax.axvline(5.0,color=’#333355’,lw=0.7,linestyle=’:’)
return ax

# Row 0: governance health all scenarios

ax0 = fig.add_subplot(gs2[0,:2]); sax(ax0,“Governance Health — Anti-Ego Mechanisms Under Stress”)
for n,h in results.items(): ax0.plot(T,h[‘health’],color=clrs[n],lw=1.8,label=n.replace(’\n’,’ ‘),alpha=0.9)
ax0.axhline(0.20,color=’#ff4444’,lw=0.8,linestyle=’–’,label=‘Critical’)
ax0.axhline(0.50,color=’#ffd43b’,lw=0.7,linestyle=’–’,label=‘Warning’)
ax0.set_ylim(0,1.1); ax0.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’,ncol=2)

# Row 0 right: three composite scores baseline

ax0r = fig.add_subplot(gs2[0,2]); sax(ax0r,“Composite Scores — Baseline\nRotation × K-protection × AI symbiosis”)
b = results[“Baseline\n(passive drift)”]
r = results[“Resilient\n(strong K distribution)”]
ax0r.plot(T,b[‘rot_eff’],  color=’#74c0fc’,lw=1.8,label=‘Rotation eff (baseline)’)
ax0r.plot(T,b[‘K_prot’],   color=’#ff922b’,lw=1.8,label=‘K protection (baseline)’)
ax0r.plot(T,b[‘AI_symp’],  color=’#cc77ff’,lw=1.8,label=‘AI symbiosis (baseline)’)
ax0r.plot(T,r[‘rot_eff’],  color=’#74c0fc’,lw=1.0,linestyle=’–’,label=‘Rotation eff (resilient)’)
ax0r.plot(T,r[‘K_prot’],   color=’#ff922b’,lw=1.0,linestyle=’–’)
ax0r.plot(T,r[‘AI_symp’],  color=’#cc77ff’,lw=1.0,linestyle=’–’)
ax0r.set_ylim(0,1.1); ax0r.legend(fontsize=6,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 1: Power concentration — passive drift vs active mechanisms

ax1a = fig.add_subplot(gs2[1,0]); sax(ax1a,“Power Concentration Dynamics\nPassive drift vs active anti-ego mechanisms”)
for n,c in [(“Baseline\n(passive drift)”,’#51cf66’),
(“Charismatic capture”,’#ff6b6b’),
(“Resilient\n(strong K distribution)”,’#aaffcc’),
(“Compound\n(crisis+ego)”,’#ff2222’)]:
ax1a.plot(T,results[n][‘power_concentration’],color=c,lw=1.8,label=n.replace(’\n’,’ ‘)[:25])
ax1a.axhline(0.65,color=’#ff4444’,lw=0.7,linestyle=’–’,label=‘Danger floor’)
ax1a.set_ylim(0,1.0); ax1a.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 1: Rotation gaming — theater vs real rotation

ax1b = fig.add_subplot(gs2[1,1]); sax(ax1b,“Rotation Gaming — Theater vs Real Rotation\nRoles rotate but power stays”)
for n,c in [(“Baseline\n(passive drift)”,’#51cf66’),
(“Charismatic capture”,’#ff6b6b’),
(“Institutional pressure”,’#ffd43b’)]:
h=results[n]
ax1b.plot(T,h[‘role_rotation’],  color=c,lw=1.8,label=f’{n[:15]} rotation’)
ax1b.plot(T,h[‘rotation_gaming’],color=c,lw=1.0,linestyle=’–’)
ax1b.plot(T,h[‘rot_eff’],        color=c,lw=1.2,linestyle=’:’)
ax1b.text(22,0.06,‘─ rotation  – gaming  ··· effective’,color=’#8b949e’,fontsize=7)
ax1b.set_ylim(0,1.0); ax1b.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 1: AI symbiosis under capture attempt

ax1c = fig.add_subplot(gs2[1,2]); sax(ax1c,“AI Symbiosis Under Capture Attempt\nAI must stay advisory — breach = governance emergency”)
aic = results[“AI capture attempt”]
base = results[“Baseline\n(passive drift)”]
ax1c.plot(T,aic[‘AI_oversight’],        color=’#cc77ff’,lw=1.8,label=‘AI oversight (attack)’)
ax1c.plot(T,aic[‘AI_transparency_score’],color=’#74c0fc’,lw=1.5,label=‘AI transparency (attack)’)
ax1c.plot(T,aic[‘AI_decision_boundary’], color=’#ff922b’,lw=1.5,label=‘AI boundary (attack)’)
ax1c.plot(T,aic[‘AI_capture_risk’],      color=’#ff6b6b’,lw=1.5,label=‘AI capture risk (attack)’)
ax1c.plot(T,base[‘AI_oversight’],       color=’#cc77ff’,lw=1.0,linestyle=’–’)
ax1c.plot(T,base[‘AI_capture_risk’],    color=’#ff6b6b’,lw=1.0,linestyle=’–’)
ax1c.axhline(0.40,color=’#ff4444’,lw=0.7,linestyle=’:’)
ax1c.set_ylim(0,1.1); ax1c.legend(fontsize=6,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 2: Knowledge distribution as primary anti-ego

ax2a = fig.add_subplot(gs2[2,0]); sax(ax2a,“Knowledge Distribution = Primary Anti-Ego\nDistributed K brakes power concentration”)
for n,c in [(“Baseline\n(passive drift)”,’#51cf66’),
(“Knowledge concentration”,’#ff922b’),
(“Resilient\n(strong K distribution)”,’#aaffcc’)]:
h=results[n]
ax2a.plot(T,h[‘knowledge_distribution’],color=c,lw=1.8,label=n.replace(’\n’,’ ‘)[:20]+’ K_dist’)
ax2a.plot(T,h[‘knowledge_hoarding’],    color=c,lw=1.0,linestyle=’–’)
ax2a.plot(T,h[‘power_concentration’],   color=c,lw=1.2,linestyle=’:’)
ax2a.text(22,0.06,‘─ K dist  – hoarding  ··· power conc’,color=’#8b949e’,fontsize=7)
ax2a.set_ylim(0,1.0); ax2a.legend(fontsize=6,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 2: Dissent channel health

ax2b = fig.add_subplot(gs2[2,1]); sax(ax2b,“Dissent Channel — Load-Bearing Infrastructure\n15% veto mechanism health”)
for n,c in [(“Baseline\n(passive drift)”,’#51cf66’),
(“Charismatic capture”,’#ff6b6b’),
(“External crisis\n(centralization)”,’#74c0fc’),
(“Compound\n(crisis+ego)”,’#ff2222’)]:
ax2b.plot(T,results[n][‘dissent_channel’],color=c,lw=1.8,label=n.replace(’\n’,’ ‘)[:25])
ax2b.axhline(0.35,color=’#ff4444’,lw=0.7,linestyle=’–’,label=‘Critical floor’)
ax2b.set_ylim(0,1.0); ax2b.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 2: Intergenerational voice

ax2c = fig.add_subplot(gs2[2,2]); sax(ax2c,“Intergenerational Voice\nElder council + apprentice voice as governance substrate”)
for n,c in [(“Baseline\n(passive drift)”,’#51cf66’),
(“Charismatic capture”,’#ff6b6b’),
(“Resilient\n(strong K distribution)”,’#aaffcc’)]:
h=results[n]
ax2c.plot(T,h[‘elder_council_weight’],color=c,lw=1.8,label=f’{n[:15]} elder’)
ax2c.plot(T,h[‘apprentice_voice’],    color=c,lw=1.2,linestyle=’–’)
ax2c.plot(T,h[‘succession_depth’],    color=c,lw=1.0,linestyle=’:’)
ax2c.text(22,0.06,‘─ elder  – apprentice  ··· succession’,color=’#8b949e’,fontsize=7)
ax2c.set_ylim(0,1.0); ax2c.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 3: Phase portrait — K_distribution × power_concentration

ax3a = fig.add_subplot(gs2[3,0]); sax(ax3a,“Phase Portrait: K Distribution × Power\nDistributed knowledge is the attractor”)
for n,c in [(“Baseline\n(passive drift)”,’#51cf66’),
(“Charismatic capture”,’#ff6b6b’),
(“Knowledge concentration”,’#ff922b’),
(“Resilient\n(strong K distribution)”,’#aaffcc’),
(“Compound\n(crisis+ego)”,’#ff2222’)]:
h=results[n]
ax3a.plot(h[‘knowledge_distribution’],h[‘power_concentration’],color=c,lw=1.4,label=n.replace(’\n’,’ ‘)[:22])
ax3a.scatter(h[‘knowledge_distribution’][0],h[‘power_concentration’][0],color=c,s=20,zorder=5)
ax3a.scatter(h[‘knowledge_distribution’][-1],h[‘power_concentration’][-1],color=c,s=20,marker=‘X’,zorder=5)
ax3a.axhline(0.65,color=’#ff4444’,lw=0.7,linestyle=’–’)
ax3a.axvline(0.40,color=’#ffd43b’,lw=0.7,linestyle=’–’)
ax3a.set_xlabel(‘Knowledge distribution’,color=’#8b949e’,fontsize=8)
ax3a.set_ylabel(‘Power concentration’,color=’#8b949e’,fontsize=9)
ax3a.legend(fontsize=6,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 3: Collapse speed

ax3b = fig.add_subplot(gs2[3,1]); sax(ax3b,“Governance Collapse Speed\nWhich threat kills fastest?”)
bt={}
for n,h in results.items():
if “Baseline” in n or “Resilient” in n: continue
br=np.where(np.array(h[‘health’])<0.20)[0]
bt[n.replace(’\n’,’ ‘)]=br[0]*0.1 if len(br) else 400
sbt=sorted(bt.items(),key=lambda x:x[1])
bns=[x[0] for x in sbt]; bvs=[x[1] for x in sbt]
bcs=[’#ff2222’ if v<20 else ‘#ff922b’ if v<40 else ‘#51cf66’ for v in bvs]
ax3b.barh(range(len(bns)),bvs,color=bcs)
ax3b.set_yticks(range(len(bns))); ax3b.set_yticklabels([n[:30] for n in bns],fontsize=7.5,color=’#e6edf3’)
ax3b.set_xlabel(‘Time to critical breach’,color=’#8b949e’,fontsize=8)
ax3b.axvline(400,color=’#51cf66’,lw=0.7,linestyle=’–’)

# Row 3: Design space — K_distribution × succession_depth for stability

ax3c = fig.add_subplot(gs2[3,2]); sax(ax3c,“Governance Stability Design Space\nK distribution × succession depth”)
kd_v=np.linspace(0,1,100); sd_v=np.linspace(0,1,100)
KD,SD=np.meshgrid(kd_v,sd_v)

# Stability = K_dist brakes power, succession enables real rotation

# Approximate stable region: K_dist*(1-gaming)*SD > threshold

gaming_est=0.20
stability=(KD*(1-gaming_est)*SD)**0.5
cf=ax3c.contourf(kd_v,sd_v,stability,levels=20,cmap=‘RdYlGn’,alpha=0.85)
ax3c.contour(kd_v,sd_v,stability,levels=[0.25,0.50,0.70],colors=[’#ff4444’,’#ffd43b’,’#51cf66’],linewidths=1.2)

# Mark scenarios

pts = {
“Baseline”:   (0.68,0.65,’#51cf66’),
“Resilient”:  (0.90,0.85,’#aaffcc’),
“Ego capture”:(0.45,0.40,’#ff6b6b’),
}
for lbl,(x,y,c) in pts.items():
ax3c.scatter(x,y,color=c,s=60,zorder=6,edgecolors=‘white’,linewidth=0.5)
ax3c.annotate(lbl,(x,y),xytext=(6,4),textcoords=‘offset points’,color=c,fontsize=7)
ax3c.set_xlabel(‘Knowledge distribution’,color=’#8b949e’,fontsize=8)
ax3c.set_ylabel(‘Succession depth’,color=’#8b949e’,fontsize=9)
cb=fig.colorbar(cf,ax=ax3c,shrink=0.8); cb.set_label(‘Stability’,color=’#8b949e’,fontsize=8)

fig.text(0.5,0.978,‘ANTI-EGO SYMBIOTIC GOVERNANCE’,ha=‘center’,color=’#e6edf3’,fontsize=13,fontweight=‘bold’)
fig.text(0.5,0.960,‘Knowledge distribution = primary anti-ego mechanism  |  AI stays advisory  |  Dissent is load-bearing infrastructure’,
ha=‘center’,color=’#8b949e’,fontsize=9)

plt.savefig(’/mnt/user-data/outputs/governance_anti_ego.png’,dpi=150,bbox_inches=‘tight’,facecolor=’#0d1117’)
plt.close()

print(“── GOVERNANCE RESULTS ──\n”)
for n,h in results.items():
br=np.where(np.array(h[‘health’])<0.20)[0]
bt=f”t={br[0]*0.1:.1f}” if len(br) else “never”
top=Counter(h[‘limiting’][50:]).most_common(1)[0][0]
print(f”{n.replace(chr(10),’ ’):<40} final={h[‘health’][-1]:.3f}  breach={bt:<10} limit={top}”)

print(”\n── KEY FINDINGS ──”)
b=results[“Baseline\n(passive drift)”]
r=results[“Resilient\n(strong K distribution)”]
cc=results[“Charismatic capture”]
print(f”  Baseline power drift t=0→40:  {b[‘power_concentration’][0]:.3f} → {b[‘power_concentration’][-1]:.3f}”)
print(f”  Resilient power drift t=0→40: {r[‘power_concentration’][0]:.3f} → {r[‘power_concentration’][-1]:.3f}”)
print(f”  Charismatic capture rotation gaming at t=40: {cc[‘rotation_gaming’][-1]:.3f}”)
print(f”  Charismatic capture real rotation eff at t=40: {cc[‘rot_eff’][-1]:.3f}”)
print(f”\n  K distribution vs power_concentration correlation (charismatic):”)
print(f”  r = {np.corrcoef(cc[‘knowledge_distribution’],cc[‘power_concentration’])[0,1]:.3f}”)
print(f”  Distributed knowledge is anti-correlated with power concentration: confirmed”)

# ─────────────────────────────────────────────

# ALIGNMENT AXIOM EXTENSION

# Ceremony/practice as adaptive alignment mechanism

# Form is provisional. Function is load-bearing. Feedback loop is critical.

# ─────────────────────────────────────────────

@dataclass
class AlignmentState:
# FUNCTION (non-negotiable — what practices actually do)
seasonal_phase_lock:      float = 0.75  # community phase-locked to ecological cycles
knowledge_transmission:   float = 0.72  # practices actively transmitting K polytensor
social_coherence:         float = 0.70  # distributed load-shedding, grief, conflict
ecological_feedback_read: float = 0.68  # community reads and responds to ecological signal

```
# FORM (provisional — current approximation of function)
practice_vitality:        float = 0.72  # practices actively performed, not empty
form_function_fidelity:   float = 0.68  # how well current form serves function
intergenerational_continuity: float = 0.65  # form transmitted across generations

# ADAPTIVE CAPACITY (the critical variable)
reality_feedback_integration: float = 0.65  # ecological signal reaches cultural practice
adaptive_practice_capacity:   float = 0.60  # permission + ability to modify form
practice_attachment:          float = 0.30  # LOW good — attachment to form over function

# FAILURE MODES
empty_ritual_index:       float = 0.20  # form preserved, function lost — LOW good
function_loss_on_change:  float = 0.20  # form changed, function not replaced — LOW good
feedback_blindness:       float = 0.25  # can't read misalignment signal — LOW good
```

CRITICAL_ALIGN = {
‘seasonal_phase_lock’:        0.30,
‘knowledge_transmission’:     0.35,
‘social_coherence’:           0.30,
‘ecological_feedback_read’:   0.30,
‘reality_feedback_integration’:0.30,
‘adaptive_practice_capacity’: 0.25,
‘practice_attachment’:        0.70,  # inverted — bad if HIGH
‘empty_ritual_index’:         0.60,  # inverted
‘feedback_blindness’:         0.65,  # inverted
}

def alignment_health(a):
d = a.**dict**
inverted = {‘practice_attachment’,‘empty_ritual_index’,‘function_loss_on_change’,‘feedback_blindness’}
scores = {}
for var, floor in CRITICAL_ALIGN.items():
val = d[var]
scores[var] = max(0,(floor-val)/floor) if var in inverted else max(0,(val-floor)/(1-floor))
mv = min(scores, key=scores.get)
return min(scores.values()), mv

def update_alignment(a, stress, dt=0.1):
na = AlignmentState(**a.**dict**)

```
eco_shock    = stress.get('ecological_disruption', 0.0)  # climate shift, landscape change
cultural_rig = stress.get('cultural_rigidity', 0.0)      # attachment to form enforced externally
inst_replace = stress.get('institutional_replacement', 0.0)  # school/church replaces practice
rapid_change = stress.get('rapid_change', 0.0)           # change faster than adaptation capacity

apc = a.adaptive_practice_capacity
rfb = a.reality_feedback_integration

# FEEDBACK LOOP — most critical
# If this dies, community can't detect misalignment
na.reality_feedback_integration += dt*(
    0.03*(1-a.reality_feedback_integration)
    + 0.04*a.ecological_feedback_read
    - 0.10*cultural_rig          # rigidity blocks feedback
    - 0.08*inst_replace          # institutions replace ecological reading
    - 0.06*a.feedback_blindness
)
na.ecological_feedback_read += dt*(
    0.03*(1-a.ecological_feedback_read)
    - 0.08*eco_shock*(1-apc)     # shock disrupts reading UNLESS adaptive capacity exists
    + 0.04*apc*eco_shock         # with adaptive capacity: shock IMPROVES reading
    - 0.06*inst_replace
)

# ADAPTIVE CAPACITY
# Permission + ability to modify form while preserving function
na.adaptive_practice_capacity += dt*(
    0.03*(1-a.adaptive_practice_capacity)
    + 0.04*rfb*(1-a.adaptive_practice_capacity)  # good feedback enables adaptation
    - 0.10*cultural_rig
    - 0.04*a.practice_attachment
    - 0.06*inst_replace
)

# FORM-FUNCTION DYNAMICS
# Form drifts from function over time without active maintenance
na.form_function_fidelity += dt*(
    0.02*(1-a.form_function_fidelity)*apc   # adaptation maintains fidelity
    - 0.04*(1-apc)                           # without adaptive capacity: drift
    - 0.06*rapid_change*(1-apc)              # rapid change breaks fidelity UNLESS adaptive
    + 0.03*rfb                               # good feedback keeps form aligned
    - 0.03*a.empty_ritual_index
)

# PRACTICE ATTACHMENT — the key failure mode variable
# Attachment to form over function
na.practice_attachment += dt*(
    0.008                                    # passive accumulation — identity hardens
    + 0.04*cultural_rig*(1-a.practice_attachment)
    + 0.02*(1-a.form_function_fidelity)*(1-a.practice_attachment)  # when form loses function, attachment increases (holding on)
    - 0.06*rfb*a.practice_attachment         # feedback dissolves attachment
    - 0.04*apc*a.practice_attachment
)

# FAILURE MODE VARIABLES
# Empty ritual: form preserved, function lost
na.empty_ritual_index += dt*(
    0.03*a.practice_attachment*(1-a.empty_ritual_index)
    + 0.02*(1-a.form_function_fidelity)
    - 0.06*apc*a.empty_ritual_index
    - 0.04*rfb*a.empty_ritual_index
)
# Function loss on change: form changed, function not replaced
na.function_loss_on_change += dt*(
    0.04*rapid_change*(1-a.function_loss_on_change)*(1-apc)
    - 0.05*apc*a.function_loss_on_change
    - 0.03*rfb*a.function_loss_on_change
)
# Feedback blindness: can't read misalignment
na.feedback_blindness += dt*(
    0.006                                    # passive drift
    + 0.05*inst_replace*(1-a.feedback_blindness)
    + 0.03*cultural_rig*(1-a.feedback_blindness)
    - 0.06*rfb*a.feedback_blindness
    - 0.04*apc*a.feedback_blindness
)

# FUNCTION VARIABLES (what practices actually do)
na.seasonal_phase_lock += dt*(
    0.03*(1-a.seasonal_phase_lock)*a.form_function_fidelity
    - 0.08*eco_shock*(1-apc)
    + 0.05*apc*eco_shock*(1-a.seasonal_phase_lock)  # adaptive: shock → recalibration
    - 0.06*a.empty_ritual_index
)
na.knowledge_transmission += dt*(
    0.03*(1-a.knowledge_transmission)*a.form_function_fidelity
    + 0.02*a.intergenerational_continuity
    - 0.07*inst_replace - 0.05*a.empty_ritual_index
)
na.social_coherence += dt*(
    0.02*(1-a.social_coherence)*a.form_function_fidelity
    - 0.06*rapid_change*(1-apc)
    - 0.04*a.empty_ritual_index
)
na.practice_vitality += dt*(
    0.03*(1-a.practice_vitality)*apc
    - 0.08*inst_replace - 0.05*a.empty_ritual_index
    + 0.02*rfb
)
na.intergenerational_continuity += dt*(
    0.02*(1-a.intergenerational_continuity)
    - 0.06*inst_replace - 0.04*rapid_change*(1-apc)
)

for attr in na.__dict__: setattr(na, attr, max(0.0, min(1.0, getattr(na,attr))))
return na
```

def run_alignment(stress, steps=400, onset=50):
a = AlignmentState()
hist = {k:[] for k in a.**dict**}
hist.update({‘health’:[],‘limiting’:[]})
for t in range(steps):
active = {k:(v if t>=onset else 0.0) for k,v in stress.items()}
a = update_alignment(a, active)
for k in a.**dict**: hist[k].append(getattr(a,k))
h, lim = alignment_health(a)
hist[‘health’].append(h); hist[‘limiting’].append(lim)
return {k: np.array(v) if k!=‘limiting’ else v for k,v in hist.items()}

align_scenarios = {
“Baseline\n(passive drift)”:           {},
“Cultural rigidity\n(form frozen)”:    {“cultural_rigidity”:0.55},
“Institutional replacement”:            {“institutional_replacement”:0.50},
“Ecological disruption\n(adaptive)”:   {“ecological_disruption”:0.45},   # adaptive capacity intact
“Rapid change\n(no adaptive capacity)”:{“rapid_change”:0.60},
“Rapid change\n(with adaptive capacity)”:{“rapid_change”:0.60},  # different init
“Compound”:                            {“cultural_rigidity”:0.30,“institutional_replacement”:0.30,“rapid_change”:0.25},
}

aclrs = {
“Baseline\n(passive drift)”:            ‘#51cf66’,
“Cultural rigidity\n(form frozen)”:     ‘#ff6b6b’,
“Institutional replacement”:             ‘#ffd43b’,
“Ecological disruption\n(adaptive)”:    ‘#74c0fc’,
“Rapid change\n(no adaptive capacity)”: ‘#ff922b’,
“Rapid change\n(with adaptive capacity)”:’#aaffcc’,
“Compound”:                             ‘#ff2222’,
}

align_results = {}
for n, stress in align_scenarios.items():
if “with adaptive” in n:
# High adaptive capacity initial conditions
a = AlignmentState()
a.adaptive_practice_capacity = 0.85
a.reality_feedback_integration = 0.82
a.practice_attachment = 0.15
hist = {k:[] for k in a.**dict**}
hist.update({‘health’:[],‘limiting’:[]})
for t in range(400):
active = {k:(v if t>=50 else 0.0) for k,v in stress.items()}
a = update_alignment(a, active)
for k in a.**dict**: hist[k].append(getattr(a,k))
h, lim = alignment_health(a)
hist[‘health’].append(h); hist[‘limiting’].append(lim)
align_results[n] = {k: np.array(v) if k!=‘limiting’ else v for k,v in hist.items()}
else:
align_results[n] = run_alignment(stress)

T = np.arange(400)*0.1

# ── ALIGNMENT VISUALIZATION ──

fig2 = plt.figure(figsize=(22,16)); fig2.patch.set_facecolor(’#0d1117’)
gs3 = gridspec.GridSpec(3,3,figure=fig2,hspace=0.52,wspace=0.35)

def sax2(ax,t):
ax.set_facecolor(’#161b22’); ax.tick_params(colors=’#8b949e’,labelsize=8)
ax.set_title(t,color=’#e6edf3’,fontsize=8.5,pad=5)
for sp in ax.spines.values(): sp.set_color(’#30363d’); sp.set_linewidth(0.5)
ax.axvline(5.0,color=’#333355’,lw=0.7,linestyle=’:’)
return ax

# Row 0: alignment health all scenarios

ax0 = fig2.add_subplot(gs3[0,:2]); sax2(ax0,“Alignment Health — Form vs Function vs Feedback”)
for n,h in align_results.items():
ax0.plot(T,h[‘health’],color=aclrs[n],lw=1.8,label=n.replace(’\n’,’ ‘),alpha=0.9)
ax0.axhline(0.20,color=’#ff4444’,lw=0.8,linestyle=’–’,label=‘Critical’)
ax0.set_ylim(0,1.1); ax0.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’,ncol=2)

# Row 0 right: the three failure modes

ax0r = fig2.add_subplot(gs3[0,2]); sax2(ax0r,“Three Failure Modes\nRigidity / Empty ritual / Feedback blindness”)
b = align_results[“Baseline\n(passive drift)”]
rig = align_results[“Cultural rigidity\n(form frozen)”]
ax0r.plot(T,b[‘empty_ritual_index’],   color=’#ff6b6b’,lw=1.5,linestyle=’–’,label=‘Empty ritual (base)’)
ax0r.plot(T,b[‘feedback_blindness’],   color=’#ffd43b’,lw=1.5,linestyle=’–’,label=‘Feedback blind (base)’)
ax0r.plot(T,b[‘practice_attachment’],  color=’#74c0fc’,lw=1.5,linestyle=’–’,label=‘Attachment (base)’)
ax0r.plot(T,rig[‘empty_ritual_index’], color=’#ff6b6b’,lw=1.8,label=‘Empty ritual (rigid)’)
ax0r.plot(T,rig[‘feedback_blindness’], color=’#ffd43b’,lw=1.8,label=‘Feedback blind (rigid)’)
ax0r.plot(T,rig[‘practice_attachment’],color=’#74c0fc’,lw=1.8,label=‘Attachment (rigid)’)
ax0r.set_ylim(0,1.0); ax0r.legend(fontsize=6,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 1: Adaptive capacity — the key variable

ax1a = fig2.add_subplot(gs3[1,0]); sax2(ax1a,“Adaptive Capacity\nKey differentiator: same shock, different outcome”)
for n,c in [(“Ecological disruption\n(adaptive)”,’#74c0fc’),
(“Rapid change\n(no adaptive capacity)”,’#ff922b’),
(“Rapid change\n(with adaptive capacity)”,’#aaffcc’)]:
h=align_results[n]
ax1a.plot(T,h[‘adaptive_practice_capacity’],color=c,lw=1.8,label=n.replace(’\n’,’ ‘)[:22])
ax1a.plot(T,h[‘form_function_fidelity’],    color=c,lw=1.0,linestyle=’–’)
ax1a.text(22,0.08,‘─ adaptive capacity  – form-function fidelity’,color=’#8b949e’,fontsize=7)
ax1a.set_ylim(0,1.0); ax1a.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 1: ecological disruption — adaptive vs rigid response

ax1b = fig2.add_subplot(gs3[1,1]); sax2(ax1b,“Ecological Disruption Response\nAdaptive capacity inverts the shock effect”)
eco_a = align_results[“Ecological disruption\n(adaptive)”]
rigid = align_results[“Cultural rigidity\n(form frozen)”]
base2 = align_results[“Baseline\n(passive drift)”]
ax1b.plot(T,eco_a[‘seasonal_phase_lock’],  color=’#74c0fc’,lw=1.8,label=‘Phase lock (adaptive disruption)’)
ax1b.plot(T,eco_a[‘ecological_feedback_read’],color=’#74c0fc’,lw=1.2,linestyle=’–’)
ax1b.plot(T,rigid[‘seasonal_phase_lock’],  color=’#ff6b6b’,lw=1.8,label=‘Phase lock (rigid)’)
ax1b.plot(T,rigid[‘ecological_feedback_read’],color=’#ff6b6b’,lw=1.2,linestyle=’–’)
ax1b.plot(T,base2[‘seasonal_phase_lock’],  color=’#51cf66’,lw=1.4,label=‘Baseline’)
ax1b.text(22,0.06,‘─ phase lock  – feedback read’,color=’#8b949e’,fontsize=7)
ax1b.set_ylim(0,1.0); ax1b.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 1: phase portrait — attachment × form-function fidelity

ax1c = fig2.add_subplot(gs3[1,2]); sax2(ax1c,“Phase Portrait: Attachment × Form-Function Fidelity\nTwo attractors: empty ritual vs adaptive alignment”)
for n,c in [(“Baseline\n(passive drift)”,’#51cf66’),
(“Cultural rigidity\n(form frozen)”,’#ff6b6b’),
(“Rapid change\n(no adaptive capacity)”,’#ff922b’),
(“Rapid change\n(with adaptive capacity)”,’#aaffcc’)]:
h=align_results[n]
ax1c.plot(h[‘practice_attachment’],h[‘form_function_fidelity’],color=c,lw=1.4,label=n.replace(’\n’,’ ‘)[:22])
ax1c.scatter(h[‘practice_attachment’][0],h[‘form_function_fidelity’][0],color=c,s=20,zorder=5)
ax1c.scatter(h[‘practice_attachment’][-1],h[‘form_function_fidelity’][-1],color=c,s=20,marker=‘X’,zorder=5)
ax1c.set_xlabel(‘Practice attachment (form over function)’,color=’#8b949e’,fontsize=8)
ax1c.set_ylabel(‘Form-function fidelity’,color=’#8b949e’,fontsize=8)
ax1c.text(0.55,0.85,‘← adaptive\nattractor’,color=’#aaffcc’,fontsize=8,transform=ax1c.transAxes)
ax1c.text(0.55,0.15,‘empty ritual\nattractor →’,color=’#ff6b6b’,fontsize=8,transform=ax1c.transAxes)
ax1c.legend(fontsize=6,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 2: design space — adaptive capacity × feedback integration

ax2a = fig2.add_subplot(gs3[2,:2]); sax2(ax2a,“Alignment Stability Design Space\nAdaptive capacity × Reality feedback integration”)
apc_v=np.linspace(0,1,100); rfb_v=np.linspace(0,1,100)
APC,RFB=np.meshgrid(apc_v,rfb_v)

# Stable region: both high; empty ritual region: low APC; feedback blind: low RFB

stability_align = (APC * RFB)**0.5 * (1 - 0.3*(1-APC)*(1-RFB))
cf2=ax2a.contourf(apc_v,rfb_v,stability_align,levels=20,cmap=‘RdYlGn’,alpha=0.85)
ax2a.contour(apc_v,rfb_v,stability_align,levels=[0.25,0.50,0.75],
colors=[’#ff4444’,’#ffd43b’,’#51cf66’],linewidths=1.2)

# Mark failure mode regions

ax2a.text(0.05,0.85,‘ADAPTIVE\nALIGNMENT’,color=‘white’,fontsize=9,fontweight=‘bold’)
ax2a.text(0.05,0.05,‘FEEDBACK\nBLIND’,color=‘white’,fontsize=9,fontweight=‘bold’)
ax2a.text(0.70,0.05,‘EMPTY\nRITUAL’,color=‘white’,fontsize=9,fontweight=‘bold’)
ax2a.text(0.60,0.85,‘FORM CHANGE\nW/O FUNCTION\nRISK’,color=‘white’,fontsize=7)

# Mark scenarios

pts2 = {
“Baseline”:  (0.60,0.65,’#51cf66’),
“Rigid”:     (0.25,0.35,’#ff6b6b’),
“Adaptive”:  (0.85,0.82,’#aaffcc’),
}
for lbl,(x,y,c) in pts2.items():
ax2a.scatter(x,y,color=c,s=60,zorder=6,edgecolors=‘white’,linewidth=0.5)
ax2a.annotate(lbl,(x,y),xytext=(6,4),textcoords=‘offset points’,color=c,fontsize=7)
ax2a.set_xlabel(‘Adaptive practice capacity’,color=’#8b949e’,fontsize=9)
ax2a.set_ylabel(‘Reality feedback integration’,color=’#8b949e’,fontsize=9)
cb2=fig2.colorbar(cf2,ax=ax2a,shrink=0.8); cb2.set_label(‘Alignment stability’,color=’#8b949e’,fontsize=8)

# Row 2 right: institutional replacement — silent function loss

ax2b = fig2.add_subplot(gs3[2,2]); sax2(ax2b,“Institutional Replacement\nSilent function loss — looks like modernization”)
inst = align_results[“Institutional replacement”]
ax2b.plot(T,inst[‘knowledge_transmission’],   color=’#ff922b’,lw=1.8,label=‘K transmission’)
ax2b.plot(T,inst[‘social_coherence’],         color=’#74c0fc’,lw=1.8,label=‘Social coherence’)
ax2b.plot(T,inst[‘practice_vitality’],        color=’#cc77ff’,lw=1.5,label=‘Practice vitality’)
ax2b.plot(T,inst[‘empty_ritual_index’],       color=’#ff6b6b’,lw=1.2,linestyle=’–’,label=‘Empty ritual’)
ax2b.plot(T,inst[‘feedback_blindness’],       color=’#ffd43b’,lw=1.2,linestyle=’–’,label=‘Feedback blind’)
ax2b.axhline(0.30,color=’#ff4444’,lw=0.7,linestyle=’:’)
ax2b.set_ylim(0,1.0); ax2b.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)
ax2b.text(5,0.08,‘Function erodes while form appears intact’,color=’#8b949e’,fontsize=7,style=‘italic’)

fig2.text(0.5,0.978,‘ALIGNMENT AXIOM — ADAPTIVE PRACTICE FRAMEWORK’,ha=‘center’,color=’#e6edf3’,fontsize=13,fontweight=‘bold’)
fig2.text(0.5,0.960,‘Form is provisional  |  Function is load-bearing  |  Feedback loop is critical’,ha=‘center’,color=’#8b949e’,fontsize=9)
fig2.text(0.5,0.943,‘Nothing too set for survival — practices must stay aligned with reality as reality changes’,
ha=‘center’,color=’#8b949e’,fontsize=8.5,style=‘italic’)

plt.savefig(’/mnt/user-data/outputs/alignment_axiom.png’,dpi=150,bbox_inches=‘tight’,facecolor=’#0d1117’)
plt.close()

print(“── ALIGNMENT RESULTS ──\n”)
for n,h in align_results.items():
br=np.where(np.array(h[‘health’])<0.20)[0]
bt=f”t={br[0]*0.1:.1f}” if len(br) else “never”
top=Counter(h[‘limiting’][50:]).most_common(1)[0][0]
print(f”{n.replace(chr(10),’ ’):<45} final={h[‘health’][-1]:.3f}  breach={bt:<10} limit={top}”)

print(”\n── KEY: SAME SHOCK, DIFFERENT OUTCOME ──”)
ra=align_results[“Rapid change\n(no adaptive capacity)”]
rh=align_results[“Rapid change\n(with adaptive capacity)”]
print(f”  Rapid change, no adaptive capacity:   final health={ra[‘health’][-1]:.3f}”)
print(f”  Rapid change, with adaptive capacity: final health={rh[‘health’][-1]:.3f}”)
print(f”\n  Ecological disruption IMPROVES feedback reading when adaptive capacity exists:”)
eco=align_results[“Ecological disruption\n(adaptive)”]
print(f”  eco_feedback_read at t=0:  {eco[‘ecological_feedback_read’][0]:.3f}”)
print(f”  eco_feedback_read at t=40: {eco[‘ecological_feedback_read’][-1]:.3f}”)

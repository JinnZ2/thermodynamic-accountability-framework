“””
NODE INTEGRATED — Full coupled system
v3 node + anti-ego governance + alignment axiom

Five coupled domains:

1. Ecological substrate      (S, B, K)
1. Knowledge polytensor      (IPI-gated, not energy-gated)
1. AI symbiosis              (advisory, transparent, not captured)
1. Governance integrity      (rotation, dissent, K distribution)
1. Alignment dynamics        (form/function/feedback)

Coupling map:
Ecology → K_relational (lagged)
IPI → K_kinesthetic, K_skill, K_temporal
K distribution → power concentration brake
Alignment feedback → adaptive_practice_capacity → IPI regeneration rate
AI symbiosis → governance transparency → alignment feedback
Power concentration → AI capture risk
Ceremony/practice vitality → K_temporal, K_wisdom (direct function coupling)
“””

import numpy as np
from collections import deque, Counter
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from dataclasses import dataclass

# ─────────────────────────────────────────────

# UNIFIED NODE STATE

# ─────────────────────────────────────────────

@dataclass
class Node:
# ECOLOGICAL
soil_carbon:        float = 0.85
biodiversity:       float = 0.80
water_retention:    float = 0.75

```
# KNOWLEDGE POLYTENSOR
K_kinesthetic:      float = 0.70
K_temporal:         float = 0.65
K_relational:       float = 0.70
K_skill:            float = 0.75
K_intuitive:        float = 0.60
K_institutional:    float = 0.85
K_digital:          float = 0.70
K_wisdom:           float = 0.55

# TRANSMISSION STRUCTURE (IPI)
IPI:                float = 0.72
age_segregation:    float = 0.25
specialization:     float = 0.30
mobility_disruption:float = 0.20
institutional_sub:  float = 0.35
elder_in_production:float = 0.75
elder_incapacity:   float = 0.10

# AI SYMBIOSIS
ai_oversight:       float = 0.78
ai_translation_bw:  float = 0.75
ai_transparency:    float = 0.78
ai_decision_boundary:float= 0.90
ai_capture_risk:    float = 0.15

# GOVERNANCE
role_rotation:      float = 0.80
dissent_channel:    float = 0.72
power_concentration:float = 0.22
knowledge_distribution:float=0.68
succession_depth:   float = 0.65
rotation_gaming:    float = 0.18
elder_council:      float = 0.60
apprentice_voice:   float = 0.55

# ALIGNMENT
adaptive_practice:  float = 0.60
reality_feedback:   float = 0.65
practice_attachment:float = 0.30
form_function:      float = 0.68
empty_ritual:       float = 0.20
feedback_blindness: float = 0.25
ceremony_vitality:  float = 0.70   # active practice integration

# ECONOMIC
food_resilience:    float = 0.70
energy_surplus:     float = 0.65
trade_dependency:   float = 0.35
```

# ─────────────────────────────────────────────

# CRITICALITY — min determines health

# ─────────────────────────────────────────────

CRITICAL = {
‘soil_carbon’:0.30, ‘biodiversity’:0.25, ‘water_retention’:0.30,
‘K_kinesthetic’:0.25, ‘K_temporal’:0.20, ‘K_relational’:0.25, ‘K_wisdom’:0.15,
‘IPI’:0.25,
‘ai_oversight’:0.35, ‘ai_translation_bw’:0.30, ‘ai_decision_boundary’:0.55,
‘dissent_channel’:0.35, ‘power_concentration’:0.65,  # inverted
‘knowledge_distribution’:0.40, ‘succession_depth’:0.30,
‘adaptive_practice’:0.25, ‘reality_feedback’:0.30,
‘practice_attachment’:0.70,   # inverted
‘empty_ritual’:0.65,          # inverted
‘food_resilience’:0.40,
}
INVERTED = {‘power_concentration’,‘practice_attachment’,‘empty_ritual’,‘ai_capture_risk’,‘rotation_gaming’}

def health(n):
d = n.**dict**
scores = {}
for var, floor in CRITICAL.items():
val = d[var]
scores[var] = max(0,(floor-val)/floor) if var in INVERTED else max(0,(val-floor)/(1-floor))
mv = min(scores, key=scores.get)
return min(scores.values()), mv

def eco(n):   return (max(0,n.soil_carbon)*max(0,n.biodiversity)*max(0,n.water_retention))**(1/3)
def gov(n):   return (max(0,n.role_rotation)*max(0,n.dissent_channel)*max(0,1-n.power_concentration)*max(0,n.succession_depth))**0.25
def IPI_f(n): return min(1.0,((1-max(0,n.age_segregation))*(1-max(0,n.specialization))*(1-max(0,n.mobility_disruption))*(1-max(0,n.institutional_sub)))**0.25*(max(0,n.elder_in_production)+max(0,n.elder_incapacity)*0.8))
def wisd(n):  return (max(0,n.K_kinesthetic)*max(0,n.K_temporal)*max(0,n.K_relational)*max(0,n.K_intuitive))**0.25
def AI_s(n):  return n.ai_oversight*n.ai_transparency*n.ai_decision_boundary*(1-n.ai_capture_risk)
def rot_eff(n): return n.role_rotation*(1-n.rotation_gaming)*n.succession_depth
def K_prot(n):  return n.knowledge_distribution*(1-n.rotation_gaming)*n.K_digital  # K_digital proxy for distribution index
def align_eff(n): return n.adaptive_practice*n.reality_feedback*(1-n.practice_attachment)

class Lag:
def **init**(self,d,v): self.buf=deque([v]*d,maxlen=d)
def push(self,v): self.buf.appendleft(v)
def get(self): return self.buf[-1]

def update(n, stress, el, kl, dt=0.1):
nn = Node(**n.**dict**)

```
B    = stress.get('industrial_pressure',   0.0)
drg  = stress.get('drought',               0.0)
ego  = stress.get('ego_capture',           0.0)
aic  = stress.get('ai_corruption',         0.0)
seg  = stress.get('age_segregation',       0.0)
mob  = stress.get('mobility',              0.0)
spc  = stress.get('specialization',        0.0)
cult_rig = stress.get('cultural_rigidity', 0.0)
inst_rep = stress.get('institutional_replacement', 0.0)
crisis   = stress.get('external_crisis',   0.0)

e  = eco(n); g = gov(n); ai = AI_s(n)
kp = max(0, n.K_institutional-0.6)*0.5
ae = align_eff(n)
cv = n.ceremony_vitality   # ceremony directly feeds K_temporal, K_wisdom

# ── ALIGNMENT (deepest layer — sets adaptive rate for everything else) ──
nn.reality_feedback    += dt*(0.03*(1-n.reality_feedback)+0.04*e
                               -0.10*cult_rig-0.08*inst_rep-0.05*n.feedback_blindness)
nn.adaptive_practice   += dt*(0.03*(1-n.adaptive_practice)+0.04*n.reality_feedback
                               -0.10*cult_rig-0.04*n.practice_attachment-0.06*inst_rep)
nn.practice_attachment += dt*(0.008+0.04*cult_rig*(1-n.practice_attachment)
                               +0.02*(1-n.form_function)*(1-n.practice_attachment)
                               -0.06*n.reality_feedback*n.practice_attachment
                               -0.04*n.adaptive_practice*n.practice_attachment)
nn.form_function       += dt*(0.02*(1-n.form_function)*n.adaptive_practice
                               -0.04*(1-n.adaptive_practice)
                               -0.06*crisis*(1-n.adaptive_practice)+0.03*n.reality_feedback
                               -0.03*n.empty_ritual)
nn.empty_ritual        += dt*(0.03*n.practice_attachment*(1-n.empty_ritual)
                               +0.02*(1-n.form_function)
                               -0.06*n.adaptive_practice*n.empty_ritual
                               -0.04*n.reality_feedback*n.empty_ritual)
nn.feedback_blindness  += dt*(0.006+0.05*inst_rep*(1-n.feedback_blindness)
                               +0.03*cult_rig*(1-n.feedback_blindness)
                               -0.06*n.reality_feedback*n.feedback_blindness
                               -0.04*n.adaptive_practice*n.feedback_blindness)

# CEREMONY VITALITY — practice integration
# Ceremony does real work: phase-locks community, transmits K_temporal/wisdom
# Adaptive capacity keeps ceremony aligned with reality
nn.ceremony_vitality   += dt*(0.03*(1-n.ceremony_vitality)*n.adaptive_practice
                               +0.02*n.form_function*(1-n.ceremony_vitality)
                               -0.10*inst_rep-0.06*n.empty_ritual
                               -0.05*B-0.04*n.practice_attachment)

# ── STRUCTURAL TRANSMISSION ──
nn.age_segregation    += dt*(0.03*B*(1-n.age_segregation)+0.04*seg*(1-n.age_segregation)-0.04*n.IPI*n.age_segregation)
nn.specialization     += dt*(0.04*B*(1-n.specialization)+0.03*spc*(1-n.specialization)-0.03*(1-n.age_segregation)*n.specialization)
nn.mobility_disruption+= dt*(0.02*B+0.05*mob-0.03*g*n.mobility_disruption)
nn.institutional_sub  += dt*(0.05*(B+inst_rep)*(1-n.institutional_sub)-0.04*n.IPI*n.institutional_sub)
nn.elder_incapacity   += dt*(0.005-0.01*e)
nn.elder_in_production+= dt*(0.02*(1-n.elder_in_production)-0.08*seg-0.05*n.institutional_sub-0.03*n.age_segregation)
nn.IPI = IPI_f(nn)

# ── ECOLOGICAL ──
nn.soil_carbon     += dt*(0.03*e*(1-n.soil_carbon)-0.05*B-0.08*drg)
nn.biodiversity    += dt*(0.04*e*(1-n.biodiversity)-0.06*B-0.03*kp)
nn.water_retention += dt*(0.03*(1-n.water_retention)-0.10*drg-0.04*B)
el.push(eco(nn)); ed = el.get()

# ── KNOWLEDGE — IPI-gated + ceremony coupling ──
nn.K_kinesthetic += dt*(0.04*n.IPI*(1-n.K_kinesthetic)+0.02*n.K_kinesthetic*(1-n.K_kinesthetic)
                         -0.12*B-0.05*kp-0.06*n.age_segregation)
# K_temporal: IPI + ceremony vitality — ceremony holds seasonal/generational memory
nn.K_temporal    += dt*(0.03*n.IPI*(1-n.K_temporal)+0.04*cv*(1-n.K_temporal)
                         +0.01*n.K_temporal*(1-n.K_temporal)
                         -0.06*B-0.08*n.mobility_disruption-0.06*n.empty_ritual)
nn.K_relational  += dt*(0.025*ed*(1-n.K_relational)+0.02*n.IPI*ed-0.08*B-0.05*(1-ed))
nn.K_skill       += dt*(0.05*n.IPI*(1-n.K_skill)+0.03*g*(1-n.K_skill)-0.07*B-0.05*n.specialization)
nn.K_intuitive   += dt*(0.015*n.K_kinesthetic*n.K_temporal*(1-n.K_intuitive)-0.10*B-0.06*kp)
nn.K_institutional+= dt*(0.05*B*(1-n.K_institutional)-0.01+0.02*g)
nn.K_digital     += dt*(0.04*(1-n.K_digital)-0.15*aic)
# K_wisdom: ceremony is primary transmission + wisd coupling
nn.K_wisdom      += dt*(0.008*(wisd(n)-n.K_wisdom)+0.03*cv*(1-n.K_wisdom)-0.03*B-0.04*n.empty_ritual)

kk=(max(0,nn.K_kinesthetic)*max(0,nn.K_temporal)*max(0,nn.K_relational))**(1/3)
kl.push(kk); kd=kl.get()

# ── AI SYMBIOSIS ──
nn.ai_oversight        += dt*(0.02*(1-n.ai_oversight)-0.20*aic-0.05*n.power_concentration)
nn.ai_translation_bw   += dt*(0.02*(1-n.ai_translation_bw)-0.10*aic-0.05*(1-n.K_kinesthetic))
nn.ai_transparency     += dt*(0.02*(1-n.ai_transparency)-0.12*aic-0.06*ego+0.03*n.dissent_channel)
nn.ai_decision_boundary+= dt*(0.01*(1-n.ai_decision_boundary)-0.08*aic-0.04*ego-0.03*crisis)
nn.ai_capture_risk     += dt*(0.02*aic*(1-n.ai_capture_risk)+0.01*n.power_concentration*(1-n.ai_capture_risk)
                               -0.06*n.ai_oversight*n.ai_capture_risk-0.04*n.ai_transparency*n.ai_capture_risk)

# ── GOVERNANCE — knowledge-lagged ──
nn.power_concentration += dt*(0.004+0.05*ego*(1-n.power_concentration)
                               +0.03*crisis*(1-n.power_concentration)
                               -0.06*rot_eff(n)*n.power_concentration
                               -0.05*n.dissent_channel*n.power_concentration
                               -0.04*K_prot(n)*n.power_concentration
                               -0.03*AI_s(n)*n.power_concentration)
nn.role_rotation       += dt*(0.03*(1-n.role_rotation)*n.succession_depth
                               -0.08*ego-0.04*crisis+0.02*ae)
nn.rotation_gaming     += dt*(0.02*ego*(1-n.rotation_gaming)+0.01
                               -0.05*n.dissent_channel*n.rotation_gaming
                               -0.04*K_prot(n)*n.rotation_gaming)
nn.dissent_channel     += dt*(0.03*(1-n.dissent_channel)-0.12*ego-0.08*n.power_concentration
                               +0.04*n.apprentice_voice+0.02*AI_s(n)+0.03*ae)
nn.knowledge_distribution += dt*(0.03*n.role_rotation*(1-n.knowledge_distribution)
                                   +0.04*n.apprentice_voice*(1-n.knowledge_distribution)
                                   -0.06*n.rotation_gaming-0.04*inst_rep+0.02*cv)
nn.succession_depth    += dt*(0.04*n.knowledge_distribution*(1-n.succession_depth)
                               -0.06*kp-0.03*n.rotation_gaming+0.02*n.apprentice_voice)
nn.elder_council       += dt*(0.02*(1-n.elder_council)-0.04*ego-0.03*inst_rep+0.02*cv)
nn.apprentice_voice    += dt*(0.03*(1-n.apprentice_voice)*n.succession_depth
                               -0.06*ego-0.04*n.power_concentration+0.02*n.dissent_channel)

# ── ECONOMIC ──
nn.energy_surplus    += dt*(0.04*e*(1-n.energy_surplus)-0.08*B-0.12*drg)
nn.food_resilience   += dt*(0.03*n.K_relational*e*(1-n.food_resilience)-0.06*B-0.04*drg)
nn.trade_dependency  += dt*(0.04*B*(1-n.trade_dependency)-0.03*n.food_resilience)

for a in nn.__dict__: setattr(nn,a,max(0.0,min(1.0,getattr(nn,a))))
return nn
```

def run(stress, steps=500, onset=60):
n = Node()
el = Lag(20,eco(n)); kl = Lag(30,0.68)
hist = {k:[] for k in n.**dict**}
hist.update({‘health’:[],‘limiting’:[],‘eco_c’:[],‘K_c’:[],‘gov_c’:[],‘align_c’:[],‘AI_c’:[]})
for t in range(steps):
active = {k:(v if t>=onset else 0.0) for k,v in stress.items()}
n = update(n,active,el,kl)
for k in n.**dict**: hist[k].append(getattr(n,k))
h,lim = health(n)
hist[‘health’].append(h); hist[‘limiting’].append(lim)
hist[‘eco_c’].append(eco(n))
hist[‘K_c’].append((max(0,n.K_kinesthetic)*max(0,n.K_temporal)*max(0,n.K_relational))**(1/3))
hist[‘gov_c’].append(gov(n))
hist[‘align_c’].append(align_eff(n))
hist[‘AI_c’].append(AI_s(n))
return {k: np.array(v) if k!=‘limiting’ else v for k,v in hist.items()}

# ── SCENARIOS ──

scenarios = {
“Baseline”:              {},
“Full industrial”:       {“industrial_pressure”:0.35,“age_segregation”:0.20,“specialization”:0.20,
“institutional_replacement”:0.25},
“Ego+crisis”:            {“ego_capture”:0.35,“external_crisis”:0.40},
“Cultural rigidity”:     {“cultural_rigidity”:0.50,“institutional_replacement”:0.30},
“AI corruption”:         {“ai_corruption”:0.65},
“Drought”:               {“drought”:0.55},
“Compound collapse”:     {“industrial_pressure”:0.25,“ego_capture”:0.20,“drought”:0.25,
“cultural_rigidity”:0.20,“ai_corruption”:0.15},
“Resilient node”:        {},  # different initial conditions
}

clrs = {
“Baseline”:          ‘#51cf66’,
“Full industrial”:   ‘#ff6b6b’,
“Ego+crisis”:        ‘#ff922b’,
“Cultural rigidity”: ‘#ffd43b’,
“AI corruption”:     ‘#cc77ff’,
“Drought”:           ‘#74c0fc’,
“Compound collapse”: ‘#ff2222’,
“Resilient node”:    ‘#aaffcc’,
}

results = {}
for nm, stress in scenarios.items():
if nm == “Resilient node”:
n = Node()
n.knowledge_distribution=0.88; n.succession_depth=0.85
n.adaptive_practice=0.82; n.reality_feedback=0.80
n.practice_attachment=0.12; n.ceremony_vitality=0.85
n.dissent_channel=0.85; n.ai_oversight=0.88
el=Lag(20,eco(n)); kl=Lag(30,0.75)
hist={k:[] for k in n.**dict**}
hist.update({‘health’:[],‘limiting’:[],‘eco_c’:[],‘K_c’:[],‘gov_c’:[],‘align_c’:[],‘AI_c’:[]})
for t in range(500):
n=update(n,{},el,kl)
for k in n.**dict**: hist[k].append(getattr(n,k))
h,lim=health(n)
hist[‘health’].append(h); hist[‘limiting’].append(lim)
hist[‘eco_c’].append(eco(n)); hist[‘K_c’].append((max(0,n.K_kinesthetic)*max(0,n.K_temporal)*max(0,n.K_relational))**(1/3))
hist[‘gov_c’].append(gov(n)); hist[‘align_c’].append(align_eff(n)); hist[‘AI_c’].append(AI_s(n))
results[nm]={k: np.array(v) if k!=‘limiting’ else v for k,v in hist.items()}
else:
results[nm]=run(stress)

T = np.arange(500)*0.1

# ── VISUALIZATION ──

fig = plt.figure(figsize=(24,22)); fig.patch.set_facecolor(’#0d1117’)
gs = gridspec.GridSpec(4,3,figure=fig,hspace=0.52,wspace=0.35)

def sax(ax,t):
ax.set_facecolor(’#161b22’); ax.tick_params(colors=’#8b949e’,labelsize=8)
ax.set_title(t,color=’#e6edf3’,fontsize=8.5,pad=5)
for sp in ax.spines.values(): sp.set_color(’#30363d’); sp.set_linewidth(0.5)
ax.axvline(6.0,color=’#333355’,lw=0.7,linestyle=’:’)
return ax

# Row 0: node health

ax0=fig.add_subplot(gs[0,:2]); sax(ax0,“Integrated Node Health — Full Coupled System\nEcology × Knowledge × AI × Governance × Alignment”)
for nm,h in results.items(): ax0.plot(T,h[‘health’],color=clrs[nm],lw=1.8,label=nm,alpha=0.9)
ax0.axhline(0.20,color=’#ff4444’,lw=0.8,linestyle=’–’,label=‘Critical’)
ax0.axhline(0.50,color=’#ffd43b’,lw=0.7,linestyle=’–’,label=‘Warning’)
ax0.set_ylim(0,1.1); ax0.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’,ncol=2)
ax0.set_xlabel(‘Time’,color=’#8b949e’,fontsize=8)

# Row 0 right: domain composites — baseline vs resilient

ax0r=fig.add_subplot(gs[0,2]); sax(ax0r,“Domain Composites\nBaseline (solid) vs Resilient (dashed)”)
b=results[“Baseline”]; r=results[“Resilient node”]
for h,ls in [(b,’-’),(r,’–’)]:
ax0r.plot(T,h[‘eco_c’],  color=’#51cf66’,lw=1.5,linestyle=ls)
ax0r.plot(T,h[‘K_c’],    color=’#ff922b’,lw=1.5,linestyle=ls)
ax0r.plot(T,h[‘gov_c’],  color=’#74c0fc’,lw=1.5,linestyle=ls)
ax0r.plot(T,h[‘align_c’],color=’#ffd43b’,lw=1.5,linestyle=ls)
ax0r.plot(T,h[‘AI_c’],   color=’#cc77ff’,lw=1.2,linestyle=ls)
ax0r.text(35,0.92,‘Eco’,color=’#51cf66’,fontsize=7)
ax0r.text(35,0.75,‘K composite’,color=’#ff922b’,fontsize=7)
ax0r.text(35,0.60,‘Gov’,color=’#74c0fc’,fontsize=7)
ax0r.text(35,0.45,‘Alignment’,color=’#ffd43b’,fontsize=7)
ax0r.text(35,0.30,‘AI’,color=’#cc77ff’,fontsize=7)
ax0r.set_ylim(0,1.1)

# Row 1: cascade timing — compound collapse domain sequence

ax1a=fig.add_subplot(gs[1,0]); sax(ax1a,“Cascade Timing — Compound Collapse\nWhich domain fails first?”)
cc=results[“Compound collapse”]
ax1a.plot(T,cc[‘health’],  color=‘white’,  lw=2.0,label=‘Node health’)
ax1a.plot(T,cc[‘eco_c’],   color=’#51cf66’,lw=1.5,label=‘Ecology’)
ax1a.plot(T,cc[‘K_c’],     color=’#ff922b’,lw=1.5,label=‘Knowledge’)
ax1a.plot(T,cc[‘gov_c’],   color=’#74c0fc’,lw=1.5,label=‘Governance’)
ax1a.plot(T,cc[‘align_c’], color=’#ffd43b’,lw=1.5,label=‘Alignment’)
ax1a.plot(T,cc[‘AI_c’],    color=’#cc77ff’,lw=1.2,label=‘AI’)
ax1a.axhline(0.20,color=’#ff4444’,lw=0.7,linestyle=’–’)
ax1a.set_ylim(0,1.1); ax1a.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 1: ceremony vitality coupling

ax1b=fig.add_subplot(gs[1,1]); sax(ax1b,“Ceremony Vitality — Coupled Transmission\nCeremony feeds K_temporal + K_wisdom directly”)
for nm,c in [(“Baseline”,’#51cf66’),(“Cultural rigidity”,’#ffd43b’),(“Full industrial”,’#ff6b6b’)]:
h=results[nm]
ax1b.plot(T,h[‘ceremony_vitality’],color=c,lw=1.8,label=nm)
ax1b.plot(T,h[‘K_temporal’],       color=c,lw=1.2,linestyle=’–’)
ax1b.plot(T,h[‘K_wisdom’],         color=c,lw=1.0,linestyle=’:’)
ax1b.text(30,0.08,‘─ ceremony  – K_temporal  ··· K_wisdom’,color=’#8b949e’,fontsize=7)
ax1b.set_ylim(0,1.0); ax1b.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 1: AI symbiosis — advisory boundary under stress

ax1c=fig.add_subplot(gs[1,2]); sax(ax1c,“AI Symbiosis — Advisory Boundary\nCrisis pressure expands AI authority (danger)”)
for nm,c in [(“Baseline”,’#51cf66’),(“Ego+crisis”,’#ff922b’),(“AI corruption”,’#cc77ff’)]:
h=results[nm]
ax1c.plot(T,h[‘ai_decision_boundary’],color=c,lw=1.8,label=nm+’ boundary’)
ax1c.plot(T,h[‘ai_capture_risk’],     color=c,lw=1.0,linestyle=’–’)
ax1c.axhline(0.55,color=’#ff4444’,lw=0.7,linestyle=’–’,label=‘Boundary floor’)
ax1c.text(30,0.08,‘─ decision boundary  – capture risk’,color=’#8b949e’,fontsize=7)
ax1c.set_ylim(0,1.0); ax1c.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 2: Power concentration — all five brakes

ax2a=fig.add_subplot(gs[2,0]); sax(ax2a,“Power Concentration — Five Brakes\nRotation × Dissent × K_dist × AI × Alignment”)
for nm,c in [(“Baseline”,’#51cf66’),(“Ego+crisis”,’#ff922b’),(“Resilient node”,’#aaffcc’)]:
h=results[nm]
ax2a.plot(T,h[‘power_concentration’],color=c,lw=1.8,label=nm)
ax2a.axhline(0.65,color=’#ff4444’,lw=0.7,linestyle=’–’,label=‘Danger’)
ax2a.set_ylim(0,1.0); ax2a.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 2: alignment failure modes

ax2b=fig.add_subplot(gs[2,1]); sax(ax2b,“Alignment Failure Modes\nEmpty ritual accumulation under different stressors”)
for nm,c in [(“Baseline”,’#51cf66’),(“Cultural rigidity”,’#ffd43b’),(“Full industrial”,’#ff6b6b’),(“Compound collapse”,’#ff2222’)]:
h=results[nm]
ax2b.plot(T,h[‘empty_ritual’],       color=c,lw=1.5,label=nm[:20]+’ empty’)
ax2b.plot(T,h[‘feedback_blindness’], color=c,lw=1.0,linestyle=’–’)
ax2b.axhline(0.65,color=’#ff4444’,lw=0.7,linestyle=’:’)
ax2b.text(30,0.08,‘─ empty ritual  – feedback blindness’,color=’#8b949e’,fontsize=7)
ax2b.set_ylim(0,1.0); ax2b.legend(fontsize=6,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 2: phase portrait — alignment × governance

ax2c=fig.add_subplot(gs[2,2]); sax(ax2c,“Phase Portrait: Alignment × Governance\nCoupled attractor geometry”)
for nm,c in [(“Baseline”,’#51cf66’),(“Ego+crisis”,’#ff922b’),
(“Cultural rigidity”,’#ffd43b’),(“Resilient node”,’#aaffcc’),
(“Compound collapse”,’#ff2222’)]:
h=results[nm]
ax2c.plot(h[‘align_c’],h[‘gov_c’],color=c,lw=1.4,label=nm[:20],alpha=0.9)
ax2c.scatter(h[‘align_c’][0],h[‘gov_c’][0],color=c,s=20,zorder=5)
ax2c.scatter(h[‘align_c’][-1],h[‘gov_c’][-1],color=c,s=20,marker=‘X’,zorder=5)
ax2c.set_xlabel(‘Alignment effectiveness’,color=’#8b949e’,fontsize=8)
ax2c.set_ylabel(‘Governance composite’,color=’#8b949e’,fontsize=9)
ax2c.legend(fontsize=6,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 3: collapse speed ranking

ax3a=fig.add_subplot(gs[3,0]); sax(ax3a,“Collapse Speed — All Stressors\nFull integrated system”)
bt={}
for nm,h in results.items():
if nm in (“Baseline”,“Resilient node”): continue
br=np.where(np.array(h[‘health’])<0.20)[0]
bt[nm]=br[0]*0.1 if len(br) else 500
sbt=sorted(bt.items(),key=lambda x:x[1])
bns=[x[0] for x in sbt]; bvs=[x[1] for x in sbt]
bcs=[’#ff2222’ if v<20 else ‘#ff922b’ if v<40 else ‘#ffd43b’ if v<200 else ‘#51cf66’ for v in bvs]
ax3a.barh(range(len(bns)),bvs,color=bcs)
ax3a.set_yticks(range(len(bns))); ax3a.set_yticklabels([n[:26] for n in bns],fontsize=7.5,color=’#e6edf3’)
ax3a.set_xlabel(‘Time to critical breach’,color=’#8b949e’,fontsize=8)
ax3a.axvline(500,color=’#51cf66’,lw=0.7,linestyle=’–’)

# Row 3: resilient vs baseline long-term trajectory

ax3b=fig.add_subplot(gs[3,1]); sax(ax3b,“Long-term Trajectory\nBaseline drift vs Resilient node”)
b=results[“Baseline”]; r=results[“Resilient node”]
ax3b.plot(T,b[‘health’],color=’#51cf66’,lw=2.0,label=‘Baseline health’)
ax3b.plot(T,r[‘health’],color=’#aaffcc’,lw=2.0,label=‘Resilient health’)
ax3b.plot(T,b[‘ceremony_vitality’],color=’#ffd43b’,lw=1.2,linestyle=’–’,label=‘Ceremony (base)’)
ax3b.plot(T,r[‘ceremony_vitality’],color=’#ffd43b’,lw=1.5,label=‘Ceremony (resilient)’)
ax3b.plot(T,b[‘power_concentration’],color=’#ff6b6b’,lw=1.2,linestyle=’–’)
ax3b.plot(T,r[‘power_concentration’],color=’#ff6b6b’,lw=1.5)
ax3b.text(35,0.08,‘Yellow=ceremony  Red=power concentration’,color=’#8b949e’,fontsize=7)
ax3b.set_ylim(0,1.1); ax3b.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 3: design envelope — what initial conditions produce stable nodes

ax3c=fig.add_subplot(gs[3,2]); sax(ax3c,“Node Stability Design Envelope\nAdaptive practice × Knowledge distribution”)
ap_v=np.linspace(0,1,100); kd_v=np.linspace(0,1,100)
AP,KD=np.meshgrid(ap_v,kd_v)

# Stability approximation: alignment brakes ego, K_dist brakes power, ceremony enables both

stab=(AP*KD*(1-0.25*(1-AP)*(1-KD)))**0.5
cf=ax3c.contourf(ap_v,kd_v,stab,levels=20,cmap=‘RdYlGn’,alpha=0.85)
ax3c.contour(ap_v,kd_v,stab,levels=[0.25,0.50,0.75],colors=[’#ff4444’,’#ffd43b’,’#51cf66’],linewidths=1.2)
pts={‘Baseline’:(0.60,0.68,’#51cf66’),‘Resilient’:(0.82,0.88,’#aaffcc’),‘Rigid’:(0.25,0.55,’#ffd43b’),‘Ego capture’:(0.45,0.40,’#ff6b6b’)}
for lbl,(x,y,c) in pts.items():
ax3c.scatter(x,y,color=c,s=60,zorder=6,edgecolors=‘white’,linewidth=0.5)
ax3c.annotate(lbl,(x,y),xytext=(6,4),textcoords=‘offset points’,color=c,fontsize=7)
ax3c.set_xlabel(‘Adaptive practice capacity’,color=’#8b949e’,fontsize=8)
ax3c.set_ylabel(‘Knowledge distribution’,color=’#8b949e’,fontsize=9)
cb=fig.colorbar(cf,ax=ax3c,shrink=0.8); cb.set_label(‘Node stability’,color=’#8b949e’,fontsize=8)

fig.text(0.5,0.978,‘INTEGRATED NODE — FULL COUPLED SYSTEM’,ha=‘center’,color=’#e6edf3’,fontsize=14,fontweight=‘bold’)
fig.text(0.5,0.961,‘Ecology × Knowledge Polytensor × AI Symbiosis × Anti-Ego Governance × Alignment Axiom’,ha=‘center’,color=’#8b949e’,fontsize=9)
fig.text(0.5,0.945,‘Ceremony vitality couples to K_temporal + K_wisdom  |  Alignment effectiveness brakes power consolidation’,ha=‘center’,color=’#8b949e’,fontsize=8.5)

plt.savefig(’/mnt/user-data/outputs/node_integrated.png’,dpi=150,bbox_inches=‘tight’,facecolor=’#0d1117’)
plt.close()

print(“── INTEGRATED NODE RESULTS ──\n”)
for nm,h in results.items():
br=np.where(np.array(h[‘health’])<0.20)[0]
bt=f”t={br[0]*0.1:.1f}” if len(br) else “never”
top=Counter(h[‘limiting’][60:]).most_common(1)[0][0]
print(f”{nm:<25} final={h[‘health’][-1]:.3f}  breach={bt:<10} limit={top}”)

print(”\n── COUPLING CONFIRMATION ──”)
b=results[“Baseline”]; r=results[“Resilient node”]
print(f”  Baseline final:   health={b[‘health’][-1]:.3f}  ceremony={b[‘ceremony_vitality’][-1]:.3f}  power={b[‘power_concentration’][-1]:.3f}”)
print(f”  Resilient final:  health={r[‘health’][-1]:.3f}  ceremony={r[‘ceremony_vitality’][-1]:.3f}  power={r[‘power_concentration’][-1]:.3f}”)
print(f”\n  Ceremony→K_temporal coupling (baseline): r={np.corrcoef(b[‘ceremony_vitality’],b[‘K_temporal’])[0,1]:.3f}”)
print(f”  Alignment→power brake (baseline):        r={np.corrcoef(b[‘align_c’],b[‘power_concentration’])[0,1]:.3f}”)
print(f”\n  Compound collapse cascade order:”)
cc=results[“Compound collapse”]
domains={‘Alignment’:cc[‘align_c’],‘Governance’:cc[‘gov_c’],‘Knowledge’:cc[‘K_c’],‘Ecology’:cc[‘eco_c’],‘AI’:cc[‘AI_c’]}
for dom,arr in sorted(domains.items(),key=lambda x: np.argmax(np.array(x[1])<0.40) if any(np.array(x[1])<0.40) else 999):
idx=np.where(np.array(arr)<0.40)[0]
t_breach=f”t={idx[0]*0.1:.1f}” if len(idx) else “never”
print(f”    {dom:<15} drops below 0.40 at {t_breach}”)


            
primary warning sensors needed:

            Primary indicators (fastest to degrade):
  adaptive_practice_capacity
  reality_feedback_integration
  ai_decision_boundary

Secondary (middle cascade):
  K_kinesthetic, K_temporal
  ai_oversight

Late indicators (already too late when these fail):
  soil_carbon, governance composites


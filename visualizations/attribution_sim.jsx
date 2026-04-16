import React, { useState, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, ReferenceLine } from 'recharts';

// ================================================================
// SEEDED RNG
// ================================================================
function mulberry32(seed) {
return function() {
let t = seed += 0x6D2B79F5;
t = Math.imul(t ^ t >>> 15, t | 1);
t ^= t + Math.imul(t ^ t >>> 7, t | 61);
return ((t ^ t >>> 14) >>> 0) / 4294967296;
};
}

function gaussian(rng, mu, sigma) {
let u1 = 0, u2 = 0;
while (u1 === 0) u1 = rng();
while (u2 === 0) u2 = rng();
const z = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
return z * sigma + mu;
}

function lognormal(rng, mu, sigma) {
return Math.exp(gaussian(rng, mu, sigma));
}

// ================================================================
// SIMULATION CORE
// ================================================================
function buildWorkers(params, seed) {
const rng = mulberry32(seed);
const workers = [];
let id = 0;

for (let i = 0; i < params.nFloor; i++) {
const comp = Math.min(1, Math.max(0, 0.3 + 0.4 * rng() + 0.1 * rng()));
workers.push({
id: id++, role: 'floor', competence: comp,
baseInsightRate: 2 + comp * 5,
crossSiloProb: 0.4 + comp * 0.3,
creditRetention: params.floorRetention + (rng() - 0.5) * 0.1,
trust: 1.0,
engagement: 1.0,
burnout: 0.0,
recoveryCapacity: 0.8 + rng() * 0.4,
exited: false,
quartersBelow25: 0,
trustHistory: [1.0],
engagementHistory: [1.0],
});
}
for (let i = 0; i < params.nOffice; i++) {
const comp = Math.min(1, Math.max(0, 0.4 + 0.3 * rng()));
workers.push({
id: id++, role: 'office', competence: comp,
baseInsightRate: 0.5 + comp * 2,
crossSiloProb: 0.3 + comp * 0.3,
creditRetention: params.officeRetention + (rng() - 0.5) * 0.1,
trust: 1.0,
engagement: 1.0,
burnout: 0.0,
recoveryCapacity: 1.0,
exited: false,
quartersBelow25: 0,
trustHistory: [1.0],
engagementHistory: [1.0],
});
}
for (let i = 0; i < params.nExec; i++) {
const comp = Math.min(1, Math.max(0, 0.3 + 0.4 * rng()));
workers.push({
id: id++, role: 'executive', competence: comp,
baseInsightRate: 0.2 + comp * 1,
crossSiloProb: 0.5 + comp * 0.3,
creditRetention: params.execRetention,
trust: 1.0,
engagement: 1.0,
burnout: 0.0,
recoveryCapacity: 1.0,
exited: false,
quartersBelow25: 0,
trustHistory: [1.0],
engagementHistory: [1.0],
});
}
return workers;
}

function detectionRate(w) {
return 0.02 + 0.28 * w.competence;
}

function burnoutMultiplier(w) {
return 1 - 0.6 * w.burnout;
}

function updateTrust(w, severity, suppression = false) {
const dr = detectionRate(w);
const mult = suppression ? 1.6 : 1.0;
const decay = dr * severity * 0.15 * mult;
w.trust = Math.max(0, w.trust - decay);
}

function updateEngagement(w) {
const t = w.trust;
if (t >= 0.7) w.engagement = 1.0;
else if (t >= 0.4) w.engagement = 0.3 + (t - 0.4) * (0.7 / 0.3);
else if (t >= 0.15) w.engagement = 0.1 + (t - 0.15) * (0.2 / 0.25);
else w.engagement = 0.05;

if (t < 0.10) { w.exited = true; w.engagement = 0; }
else if (t < 0.25 && w.quartersBelow25 >= 3) { w.exited = true; w.engagement = 0; }
}

function updateBurnout(w) {
if (w.engagement >= 0.7 && w.trust >= 0.5) {
w.burnout = Math.max(0, w.burnout - 0.03 * w.recoveryCapacity);
} else {
let gain = 0.04;
if (w.engagement < 0.5) gain += 0.08 * (1 - w.engagement);
w.burnout = Math.min(1, w.burnout + gain / w.recoveryCapacity);
}
}

function runSim(params) {
const rng = mulberry32(params.seed + 100);
const workers = buildWorkers(params, params.seed);
const MAX_J = 1e14;
const logMaxJ = Math.log10(MAX_J);

const quarterly = [];

for (let q = 0; q < params.quarters; q++) {
const reformed = params.reformQuarter !== null && q >= params.reformQuarter;
const quarterInsights = [];

// 1. Generate insights
for (const w of workers) {
  if (w.exited) continue;
  const effRate = w.baseInsightRate * w.engagement * burnoutMultiplier(w);
  const n = Math.max(0, Math.floor(gaussian(rng, effRate, effRate * 0.4)));
  for (let i = 0; i < n; i++) {
    const mu = 23 + w.competence * 2;
    const magnitude = lognormal(rng, mu, 1.8);
    const sign = rng() > 0.08 ? 1 : -1;
    const ins = {
      originRole: w.role,
      originWorkerId: w.id,
      downstreamJoules: sign * magnitude,
      crossSilo: rng() < w.crossSiloProb,
      attributedRole: w.role,
      attributedWorkerId: w.id,
      wasLaundered: false,
    };
    quarterInsights.push(ins);
  }
}

// 2. Laundering
for (const ins of quarterInsights) {
  const originator = workers[ins.originWorkerId];
  const retention = reformed ? 0.85 : originator.creditRetention;
  if (rng() < retention) continue;

  ins.wasLaundered = true;
  if (ins.originRole === 'floor') {
    const office = workers.filter(w => w.role === 'office' && !w.exited);
    if (office.length > 0) {
      const ch = office[Math.floor(rng() * office.length)];
      ins.attributedRole = 'office';
      ins.attributedWorkerId = ch.id;
    } else { ins.wasLaundered = false; }
  } else if (ins.originRole === 'office') {
    const execs = workers.filter(w => w.role === 'executive' && !w.exited);
    if (execs.length > 0) {
      const ch = execs[Math.floor(rng() * execs.length)];
      ins.attributedRole = 'executive';
      ins.attributedWorkerId = ch.id;
    } else { ins.wasLaundered = false; }
  }
}

// 3. Trust updates
for (const ins of quarterInsights) {
  if (ins.downstreamJoules <= 0 || !ins.wasLaundered) continue;
  const sev = Math.min(1, Math.max(0, Math.log10(Math.max(ins.downstreamJoules, 1)) / logMaxJ));
  updateTrust(workers[ins.originWorkerId], sev);
}

// 4. Engagement + burnout
for (const w of workers) {
  if (w.exited) { 
    w.trustHistory.push(w.trust);
    w.engagementHistory.push(w.engagement);
    continue; 
  }
  if (w.trust < 0.25) w.quartersBelow25++;
  else w.quartersBelow25 = 0;
  updateEngagement(w);
  updateBurnout(w);
  w.trustHistory.push(w.trust);
  w.engagementHistory.push(w.engagement);
}

// Metrics per role
const roleStats = { floor: [], office: [], executive: [] };
const roleValueAttrib = { floor: 0, office: 0, executive: 0 };
const roleValueOrigin = { floor: 0, office: 0, executive: 0 };

for (const ins of quarterInsights) {
  roleValueAttrib[ins.attributedRole] += ins.downstreamJoules;
  roleValueOrigin[ins.originRole] += ins.downstreamJoules;
}

for (const w of workers) roleStats[w.role].push(w);

const floorActive = roleStats.floor.filter(w => !w.exited);
const floorExited = roleStats.floor.filter(w => w.exited).length;

quarterly.push({
  q,
  reformed,
  totalInsights: quarterInsights.length,
  laundered: quarterInsights.filter(i => i.wasLaundered).length,
  floorActive: floorActive.length,
  floorExited,
  floorTrust: floorActive.length > 0
    ? floorActive.reduce((s, w) => s + w.trust, 0) / floorActive.length : 0,
  floorBurnout: floorActive.length > 0
    ? floorActive.reduce((s, w) => s + w.burnout, 0) / floorActive.length : 0,
  floorComp: floorActive.length > 0
    ? floorActive.reduce((s, w) => s + w.competence, 0) / floorActive.length : 0,
  highCompTrust: floorActive.filter(w => w.competence >= 0.75).length > 0
    ? floorActive.filter(w => w.competence >= 0.75).reduce((s, w) => s + w.trust, 0)
      / floorActive.filter(w => w.competence >= 0.75).length : 0,
  lowCompTrust: floorActive.filter(w => w.competence < 0.5).length > 0
    ? floorActive.filter(w => w.competence < 0.5).reduce((s, w) => s + w.trust, 0)
      / floorActive.filter(w => w.competence < 0.5).length : 0,
  floorValueAttrib: roleValueAttrib.floor / 1e12,
  officeValueAttrib: roleValueAttrib.office / 1e12,
  execValueAttrib: roleValueAttrib.executive / 1e12,
  floorValueOrigin: roleValueOrigin.floor / 1e12,
  officeValueOrigin: roleValueOrigin.office / 1e12,
  execValueOrigin: roleValueOrigin.executive / 1e12,
});

}

// Aggregate
const totalFloorAttrib = quarterly.reduce((s, q) => s + q.floorValueAttrib, 0);
const totalOfficeAttrib = quarterly.reduce((s, q) => s + q.officeValueAttrib, 0);
const totalExecAttrib = quarterly.reduce((s, q) => s + q.execValueAttrib, 0);
const totalFloorOrigin = quarterly.reduce((s, q) => s + q.floorValueOrigin, 0);
const totalOfficeOrigin = quarterly.reduce((s, q) => s + q.officeValueOrigin, 0);
const totalExecOrigin = quarterly.reduce((s, q) => s + q.execValueOrigin, 0);

return {
quarterly,
workers,
summary: {
totalFloorAttrib, totalOfficeAttrib, totalExecAttrib,
totalFloorOrigin, totalOfficeOrigin, totalExecOrigin,
floorShift: totalFloorAttrib - totalFloorOrigin,
officeShift: totalOfficeAttrib - totalOfficeOrigin,
execShift: totalExecAttrib - totalExecOrigin,
}
};
}

// ================================================================
// UI
// ================================================================
const panel = { background: '#15181a', border: '1px solid #2a3033', padding: '14px', marginBottom: '14px' };
const panelAccent = { ...panel, borderLeft: '3px solid #e6a23c' };
const labelStyle = { fontFamily: 'Courier New, monospace', fontSize: '11px', color: '#8a9196', letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: '4px', display: 'block' };
const valueStyle = { fontFamily: 'Courier New, monospace', fontSize: '13px', color: '#d8dcde' };
const headerStyle = { fontFamily: 'Courier New, monospace', fontSize: '12px', color: '#e6a23c', letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: '6px' };
const sliderContainer = { marginBottom: '12px' };
const sliderLabel = { display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '4px' };

function Slider({ label, value, min, max, step, onChange, suffix = '' }) {
return (
<div style={sliderContainer}>
<div style={sliderLabel}>
<span style={labelStyle}>{label}</span>
<span style={valueStyle}>{typeof value === 'number' ? (step < 0.01 ? value.toFixed(3) : step < 1 ? value.toFixed(2) : value) : value}{suffix}</span>
</div>
<input
type="range"
value={value}
min={min}
max={max}
step={step}
onChange={(e) => onChange(parseFloat(e.target.value))}
style={{ width: '100%', accentColor: '#e6a23c' }}
/>
</div>
);
}

export default function AttributionSim() {
const [params, setParams] = useState({
nFloor: 50,
nOffice: 15,
nExec: 3,
quarters: 24,
floorRetention: 0.12,
officeRetention: 0.55,
execRetention: 0.92,
reformQuarter: null,
seed: 42,
});

const [view, setView] = useState('ledger');

const result = useMemo(() => runSim(params), [params]);

const update = (key, value) => setParams(p => ({ ...p, [key]: value }));

const reformValues = [null, 0, 4, 8, 12, 16, 20];
const reformLabel = params.reformQuarter === null ? 'off' : `Q${params.reformQuarter}`;

// Ledger data for chart
const ledgerData = [
{
role: 'floor',
current: result.summary.totalFloorAttrib,
provenance: result.summary.totalFloorOrigin,
},
{
role: 'office',
current: result.summary.totalOfficeAttrib,
provenance: result.summary.totalOfficeOrigin,
},
{
role: 'exec',
current: result.summary.totalExecAttrib,
provenance: result.summary.totalExecOrigin,
},
];

// Trust data — sample every 2 quarters
const trustData = result.quarterly.map(q => ({
q: q.q,
'high-competence': q.highCompTrust,
'low-competence': q.lowCompTrust,
burnout: q.floorBurnout,
}));

// Output data
const outputData = result.quarterly.map(q => ({
q: q.q,
insights: q.totalInsights,
exits: q.floorExited,
}));

return (
<div style={{
background: '#0d0f10',
color: '#d8dcde',
minHeight: '100vh',
padding: '14px 12px 40px',
fontFamily: 'Georgia, serif',
fontSize: '14px',
lineHeight: '1.5',
}}>
<div style={{ maxWidth: '780px', margin: '0 auto' }}>

    <h1 style={{ 
      fontFamily: 'Courier New, monospace', 
      fontSize: '16px', 
      color: '#e6a23c', 
      letterSpacing: '0.02em',
      textTransform: 'uppercase',
      marginBottom: '4px',
    }}>
      Attribution Capture Simulator
    </h1>
    <div style={{ 
      fontFamily: 'Courier New, monospace', 
      fontSize: '10px', 
      color: '#5a6166', 
      letterSpacing: '0.08em',
      textTransform: 'uppercase',
      marginBottom: '20px',
    }}>
      thermodynamic ledger · trust decay · reform timing
    </div>

    {/* CONTROLS */}
    <div style={panelAccent}>
      <div style={headerStyle}>Facility parameters</div>
      <Slider label="floor workers" value={params.nFloor} min={10} max={150} step={5} onChange={v => update('nFloor', v)} />
      <Slider label="office workers" value={params.nOffice} min={0} max={50} step={1} onChange={v => update('nOffice', v)} />
      <Slider label="executives" value={params.nExec} min={0} max={10} step={1} onChange={v => update('nExec', v)} />
      <Slider label="quarters to simulate" value={params.quarters} min={4} max={40} step={1} onChange={v => update('quarters', v)} />
    </div>

    <div style={panelAccent}>
      <div style={headerStyle}>Credit retention</div>
      <div style={{ fontSize: '12px', color: '#8a9196', marginBottom: '10px', fontStyle: 'italic' }}>
        fraction of insights that get credited to originator (not laundered upward)
      </div>
      <Slider label="floor" value={params.floorRetention} min={0.05} max={0.95} step={0.01} onChange={v => update('floorRetention', v)} />
      <Slider label="office" value={params.officeRetention} min={0.05} max={0.95} step={0.01} onChange={v => update('officeRetention', v)} />
      <Slider label="executive" value={params.execRetention} min={0.05} max={0.95} step={0.01} onChange={v => update('execRetention', v)} />
    </div>

    <div style={panelAccent}>
      <div style={headerStyle}>Reform intervention</div>
      <div style={{ fontSize: '12px', color: '#8a9196', marginBottom: '10px', fontStyle: 'italic' }}>
        when symmetric retention (0.85) kicks in. point of no return ≈ Q12-Q16
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '4px' }}>
        {reformValues.map(v => (
          <button
            key={v === null ? 'off' : v}
            onClick={() => update('reformQuarter', v)}
            style={{
              padding: '8px 4px',
              background: params.reformQuarter === v ? '#e6a23c' : '#1a1e20',
              color: params.reformQuarter === v ? '#0d0f10' : '#d8dcde',
              border: '1px solid #2a3033',
              fontFamily: 'Courier New, monospace',
              fontSize: '11px',
              cursor: 'pointer',
              fontWeight: params.reformQuarter === v ? 'bold' : 'normal',
            }}
          >
            {v === null ? 'off' : `Q${v}`}
          </button>
        ))}
      </div>
      <div style={{ marginTop: '10px' }}>
        <Slider label="random seed" value={params.seed} min={1} max={100} step={1} onChange={v => update('seed', v)} />
      </div>
    </div>

    {/* VIEW SELECTOR */}
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '4px', marginBottom: '14px' }}>
      {[
        { key: 'ledger', label: 'Ledger' },
        { key: 'trust', label: 'Trust decay' },
        { key: 'output', label: 'Output' },
      ].map(v => (
        <button
          key={v.key}
          onClick={() => setView(v.key)}
          style={{
            padding: '10px 4px',
            background: view === v.key ? '#e6a23c' : '#1a1e20',
            color: view === v.key ? '#0d0f10' : '#d8dcde',
            border: '1px solid #2a3033',
            fontFamily: 'Courier New, monospace',
            fontSize: '11px',
            cursor: 'pointer',
            letterSpacing: '0.05em',
            textTransform: 'uppercase',
            fontWeight: view === v.key ? 'bold' : 'normal',
          }}
        >
          {v.label}
        </button>
      ))}
    </div>

    {/* LEDGER VIEW */}
    {view === 'ledger' && (
      <>
        <div style={panel}>
          <div style={headerStyle}>Value attribution: current vs provenance</div>
          <div style={{ fontSize: '12px', color: '#8a9196', marginBottom: '10px', fontStyle: 'italic' }}>
            TJ of downstream value. gap = attribution capture.
          </div>
          <div style={{ height: '260px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ledgerData}>
                <CartesianGrid stroke="#2a3033" strokeDasharray="2 2" />
                <XAxis dataKey="role" stroke="#8a9196" tick={{ fontFamily: 'Courier New, monospace', fontSize: 11 }} />
                <YAxis stroke="#8a9196" tick={{ fontFamily: 'Courier New, monospace', fontSize: 10 }} />
                <Tooltip 
                  contentStyle={{ background: '#15181a', border: '1px solid #e6a23c', fontFamily: 'Courier New, monospace', fontSize: '11px' }}
                  labelStyle={{ color: '#e6a23c' }}
                />
                <Legend wrapperStyle={{ fontFamily: 'Courier New, monospace', fontSize: '11px' }} />
                <Bar dataKey="current" name="current ledger (reporter)" fill="#e6a23c" />
                <Bar dataKey="provenance" name="provenance (originator)" fill="#5c8ac4" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div style={panel}>
          <div style={headerStyle}>Capture signal</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px', marginTop: '10px' }}>
            <Stat label="floor" value={result.summary.floorShift} unit="TJ" inverted />
            <Stat label="office" value={result.summary.officeShift} unit="TJ" />
            <Stat label="exec" value={result.summary.execShift} unit="TJ" />
          </div>
          <div style={{ marginTop: '14px', fontSize: '12px', color: '#8a9196', fontStyle: 'italic', lineHeight: '1.5' }}>
            negative = role generates value credited elsewhere<br />
            positive = role receives credit for value generated elsewhere
          </div>
        </div>
      </>
    )}

    {/* TRUST VIEW */}
    {view === 'trust' && (
      <>
        <div style={panel}>
          <div style={headerStyle}>Trust trajectory by competence band</div>
          <div style={{ fontSize: '12px', color: '#8a9196', marginBottom: '10px', fontStyle: 'italic' }}>
            high-competence workers detect capture first — their trust decays fastest
          </div>
          <div style={{ height: '260px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trustData}>
                <CartesianGrid stroke="#2a3033" strokeDasharray="2 2" />
                <XAxis dataKey="q" stroke="#8a9196" tick={{ fontFamily: 'Courier New, monospace', fontSize: 10 }} label={{ value: 'quarter', position: 'insideBottom', offset: -2, fill: '#5a6166', fontSize: 10 }} />
                <YAxis stroke="#8a9196" domain={[0, 1]} tick={{ fontFamily: 'Courier New, monospace', fontSize: 10 }} />
                <Tooltip 
                  contentStyle={{ background: '#15181a', border: '1px solid #e6a23c', fontFamily: 'Courier New, monospace', fontSize: '11px' }}
                  labelStyle={{ color: '#e6a23c' }}
                />
                <Legend wrapperStyle={{ fontFamily: 'Courier New, monospace', fontSize: '11px' }} />
                <Line type="monotone" dataKey="high-competence" stroke="#d86a5c" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="low-competence" stroke="#6fa85c" strokeWidth={2} dot={false} />
                {params.reformQuarter !== null && (
                  <ReferenceLine x={params.reformQuarter} stroke="#e6a23c" strokeDasharray="4 4" label={{ value: 'reform', fill: '#e6a23c', fontSize: 10 }} />
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div style={panel}>
          <div style={headerStyle}>Floor burnout accumulation</div>
          <div style={{ height: '200px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trustData}>
                <CartesianGrid stroke="#2a3033" strokeDasharray="2 2" />
                <XAxis dataKey="q" stroke="#8a9196" tick={{ fontFamily: 'Courier New, monospace', fontSize: 10 }} />
                <YAxis stroke="#8a9196" domain={[0, 1]} tick={{ fontFamily: 'Courier New, monospace', fontSize: 10 }} />
                <Tooltip 
                  contentStyle={{ background: '#15181a', border: '1px solid #e6a23c', fontFamily: 'Courier New, monospace', fontSize: '11px' }}
                />
                <Line type="monotone" dataKey="burnout" stroke="#e6c23c" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </>
    )}

    {/* OUTPUT VIEW */}
    {view === 'output' && (
      <>
        <div style={panel}>
          <div style={headerStyle}>Insights per quarter + exits</div>
          <div style={{ fontSize: '12px', color: '#8a9196', marginBottom: '10px', fontStyle: 'italic' }}>
            generative capacity collapses as trust decays
          </div>
          <div style={{ height: '280px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={outputData}>
                <CartesianGrid stroke="#2a3033" strokeDasharray="2 2" />
                <XAxis dataKey="q" stroke="#8a9196" tick={{ fontFamily: 'Courier New, monospace', fontSize: 10 }} />
                <YAxis yAxisId="left" stroke="#5c8ac4" tick={{ fontFamily: 'Courier New, monospace', fontSize: 10 }} />
                <YAxis yAxisId="right" orientation="right" stroke="#d86a5c" tick={{ fontFamily: 'Courier New, monospace', fontSize: 10 }} />
                <Tooltip 
                  contentStyle={{ background: '#15181a', border: '1px solid #e6a23c', fontFamily: 'Courier New, monospace', fontSize: '11px' }}
                />
                <Legend wrapperStyle={{ fontFamily: 'Courier New, monospace', fontSize: '11px' }} />
                <Line yAxisId="left" type="monotone" dataKey="insights" stroke="#5c8ac4" strokeWidth={2} dot={false} />
                <Line yAxisId="right" type="monotone" dataKey="exits" stroke="#d86a5c" strokeWidth={2} dot={false} />
                {params.reformQuarter !== null && (
                  <ReferenceLine yAxisId="left" x={params.reformQuarter} stroke="#e6a23c" strokeDasharray="4 4" label={{ value: 'reform', fill: '#e6a23c', fontSize: 10 }} />
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div style={panel}>
          <div style={headerStyle}>Terminal state</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '10px' }}>
            <Stat label="Q0 insights" value={result.quarterly[0].totalInsights} unit="" />
            <Stat label={`Q${params.quarters - 1} insights`} value={result.quarterly[result.quarterly.length - 1].totalInsights} unit="" />
            <Stat label="final trust" value={result.quarterly[result.quarterly.length - 1].floorTrust} unit="" fmt={3} />
            <Stat label="final burnout" value={result.quarterly[result.quarterly.length - 1].floorBurnout} unit="" fmt={2} />
            <Stat label="floor exits" value={result.quarterly[result.quarterly.length - 1].floorExited} unit="" />
            <Stat label="final mean comp" value={result.quarterly[result.quarterly.length - 1].floorComp} unit="" fmt={3} />
          </div>
        </div>
      </>
    )}

    <div style={{ ...panel, fontSize: '11px', color: '#5a6166', fontStyle: 'italic', lineHeight: '1.5' }}>
      <div style={{ fontFamily: 'Courier New, monospace', fontSize: '10px', color: '#e6a23c', letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: '8px', fontStyle: 'normal' }}>
        What to try
      </div>
      · default parameters → severe capture signature<br />
      · raise floor retention to 0.85 → most of the damage dissolves<br />
      · set reform to Q4 → strong recovery<br />
      · set reform to Q16 → indistinguishable from no reform (point of no return)<br />
      · change seed → signal is sign-stable across parameterizations
    </div>
  </div>
</div>

);
}

function Stat({ label, value, unit, inverted = false, fmt = 1 }) {
const numValue = typeof value === 'number' ? value : 0;
const display = typeof value === 'number'
? (Math.abs(numValue) >= 100 ? numValue.toFixed(0) : numValue.toFixed(fmt))
: value;

let color = '#d8dcde';
if (typeof value === 'number' && unit === 'TJ') {
if (inverted) {
color = numValue < -50 ? '#d86a5c' : numValue < 0 ? '#e6c23c' : '#6fa85c';
} else {
color = numValue > 50 ? '#d86a5c' : numValue > 0 ? '#e6c23c' : '#6fa85c';
}
}

return (
<div style={{
background: '#1a1e20',
border: '1px solid #2a3033',
padding: '10px',
}}>
<div style={{
fontFamily: 'Courier New, monospace',
fontSize: '9px',
color: '#5a6166',
letterSpacing: '0.05em',
textTransform: 'uppercase',
marginBottom: '4px',
}}>
{label}
</div>
<div style={{
fontFamily: 'Courier New, monospace',
fontSize: '16px',
color,
fontWeight: 'bold',
}}>
{typeof value === 'number' && numValue > 0 && unit === 'TJ' ? '+' : ''}{display}{unit ? ' ' + unit : ''}
</div>
</div>
);
}

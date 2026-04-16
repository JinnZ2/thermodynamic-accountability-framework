<!DOCTYPE html>

<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Labor Thermodynamics — Audit Protocol</title>
<style>
  :root {
    --bg: #0d0f10;
    --panel: #15181a;
    --panel-2: #1a1e20;
    --border: #2a3033;
    --text: #d8dcde;
    --text-dim: #8a9196;
    --text-faint: #5a6166;
    --accent: #e6a23c;
    --accent-dim: #8a6425;
    --red: #d86a5c;
    --green: #6fa85c;
    --yellow: #e6c23c;
    --blue: #5c8ac4;
    --font-mono: 'Courier New', 'Consolas', 'Monaco', monospace;
    --font-body: 'Georgia', 'Times New Roman', serif;
  }

- { box-sizing: border-box; margin: 0; padding: 0; }

body {
background: var(–bg);
color: var(–text);
font-family: var(–font-body);
font-size: 15px;
line-height: 1.55;
min-height: 100vh;
padding: 16px 12px 120px;
max-width: 760px;
margin: 0 auto;
}

h1 {
font-family: var(–font-mono);
font-size: 17px;
font-weight: bold;
color: var(–accent);
letter-spacing: 0.02em;
margin-bottom: 4px;
text-transform: uppercase;
}

.subtitle {
font-family: var(–font-mono);
font-size: 11px;
color: var(–text-faint);
margin-bottom: 24px;
letter-spacing: 0.08em;
text-transform: uppercase;
}

.phase {
background: var(–panel);
border: 1px solid var(–border);
border-left: 3px solid var(–accent);
padding: 14px 14px 18px;
margin-bottom: 16px;
}

.phase-header {
font-family: var(–font-mono);
font-size: 12px;
font-weight: bold;
color: var(–accent);
letter-spacing: 0.05em;
text-transform: uppercase;
margin-bottom: 4px;
}

.phase-title {
font-size: 17px;
font-weight: bold;
color: var(–text);
margin-bottom: 6px;
font-family: var(–font-body);
}

.phase-desc {
font-size: 13px;
color: var(–text-dim);
margin-bottom: 14px;
line-height: 1.5;
}

.phase-body {
display: none;
}

.phase.expanded .phase-body {
display: block;
}

.phase-toggle {
font-family: var(–font-mono);
font-size: 10px;
color: var(–text-faint);
cursor: pointer;
padding: 4px 0;
display: inline-block;
margin-top: 6px;
letter-spacing: 0.05em;
}

.phase-toggle:hover { color: var(–accent); }

.field {
margin-bottom: 14px;
}

.field-label {
font-family: var(–font-mono);
font-size: 11px;
color: var(–text-dim);
letter-spacing: 0.05em;
text-transform: uppercase;
margin-bottom: 4px;
display: block;
}

.field-help {
font-size: 12px;
color: var(–text-faint);
font-style: italic;
margin-bottom: 6px;
line-height: 1.4;
}

input[type=“text”],
input[type=“number”],
textarea,
select {
width: 100%;
background: var(–panel-2);
color: var(–text);
border: 1px solid var(–border);
padding: 8px 10px;
font-family: var(–font-mono);
font-size: 13px;
border-radius: 0;
transition: border-color 0.15s;
}

input:focus, textarea:focus, select:focus {
outline: none;
border-color: var(–accent);
}

textarea {
resize: vertical;
min-height: 60px;
font-family: var(–font-body);
font-size: 14px;
}

.likert {
display: grid;
grid-template-columns: repeat(5, 1fr);
gap: 4px;
margin-top: 6px;
}

.likert input[type=“radio”] {
display: none;
}

.likert label {
display: block;
padding: 8px 4px;
background: var(–panel-2);
border: 1px solid var(–border);
text-align: center;
font-family: var(–font-mono);
font-size: 13px;
cursor: pointer;
transition: all 0.15s;
}

.likert input[type=“radio”]:checked + label {
background: var(–accent);
color: var(–bg);
border-color: var(–accent);
font-weight: bold;
}

.likert-labels {
display: flex;
justify-content: space-between;
margin-top: 4px;
font-size: 10px;
color: var(–text-faint);
font-family: var(–font-mono);
}

.entry-list {
margin-top: 10px;
}

.entry {
background: var(–panel-2);
border: 1px solid var(–border);
padding: 10px 12px;
margin-bottom: 8px;
position: relative;
}

.entry-meta {
font-family: var(–font-mono);
font-size: 10px;
color: var(–text-faint);
letter-spacing: 0.05em;
margin-bottom: 4px;
}

.entry-text {
font-size: 13px;
color: var(–text);
}

.entry-del {
position: absolute;
top: 8px;
right: 10px;
background: none;
border: none;
color: var(–red);
cursor: pointer;
font-family: var(–font-mono);
font-size: 11px;
}

button.add {
background: var(–panel-2);
border: 1px dashed var(–border);
color: var(–text-dim);
padding: 10px;
width: 100%;
font-family: var(–font-mono);
font-size: 11px;
cursor: pointer;
letter-spacing: 0.05em;
text-transform: uppercase;
transition: all 0.15s;
margin-top: 6px;
}

button.add:hover {
border-color: var(–accent);
color: var(–accent);
}

.summary {
background: var(–panel);
border: 1px solid var(–accent);
padding: 16px;
margin-top: 24px;
}

.summary h2 {
font-family: var(–font-mono);
font-size: 13px;
color: var(–accent);
letter-spacing: 0.05em;
text-transform: uppercase;
margin-bottom: 14px;
}

.summary-row {
display: flex;
justify-content: space-between;
padding: 6px 0;
border-bottom: 1px solid var(–border);
font-family: var(–font-mono);
font-size: 12px;
}

.summary-row:last-child { border-bottom: none; }

.summary-label { color: var(–text-dim); }

.summary-value {
color: var(–text);
font-weight: bold;
}

.summary-value.good { color: var(–green); }
.summary-value.warn { color: var(–yellow); }
.summary-value.bad { color: var(–red); }

.actions {
position: fixed;
bottom: 0;
left: 0;
right: 0;
background: var(–bg);
border-top: 1px solid var(–border);
padding: 12px;
display: flex;
gap: 8px;
justify-content: center;
z-index: 100;
}

.actions button {
flex: 1;
max-width: 180px;
padding: 10px 12px;
font-family: var(–font-mono);
font-size: 11px;
letter-spacing: 0.05em;
text-transform: uppercase;
border: 1px solid var(–border);
background: var(–panel-2);
color: var(–text);
cursor: pointer;
transition: all 0.15s;
}

.actions button.primary {
border-color: var(–accent);
color: var(–accent);
}

.actions button:hover {
background: var(–panel);
}

.actions button.primary:hover {
background: var(–accent);
color: var(–bg);
}

.save-indicator {
position: fixed;
top: 12px;
right: 12px;
font-family: var(–font-mono);
font-size: 10px;
color: var(–green);
background: var(–panel);
padding: 4px 8px;
border: 1px solid var(–green);
opacity: 0;
transition: opacity 0.3s;
z-index: 200;
}

.save-indicator.show { opacity: 1; }

.diagram {
font-family: var(–font-mono);
font-size: 10px;
color: var(–text-dim);
background: var(–panel-2);
padding: 10px;
border: 1px solid var(–border);
white-space: pre;
overflow-x: auto;
line-height: 1.3;
margin: 10px 0;
}

.warning-box {
background: rgba(230, 162, 60, 0.08);
border-left: 2px solid var(–accent);
padding: 10px 12px;
margin: 12px 0;
font-size: 12px;
color: var(–text-dim);
line-height: 1.5;
}

.warning-box strong {
color: var(–accent);
font-family: var(–font-mono);
font-size: 11px;
letter-spacing: 0.05em;
text-transform: uppercase;
display: block;
margin-bottom: 4px;
}

details {
margin-top: 10px;
}

summary {
font-family: var(–font-mono);
font-size: 11px;
color: var(–text-faint);
cursor: pointer;
padding: 4px 0;
letter-spacing: 0.05em;
}

summary:hover { color: var(–accent); }

details[open] summary { color: var(–accent); }

.intro {
background: var(–panel);
border: 1px solid var(–border);
padding: 16px;
margin-bottom: 20px;
font-size: 13px;
color: var(–text-dim);
line-height: 1.6;
}

.intro p { margin-bottom: 8px; }
.intro p:last-child { margin-bottom: 0; }
.intro strong { color: var(–text); }
</style>

</head>
<body>

<div class="save-indicator" id="saveIndicator">saved</div>

<h1>Labor Thermodynamics</h1>
<div class="subtitle">Audit Protocol — field instrument</div>

<div class="intro">
  <p><strong>What this is.</strong> A fillable audit tool for diagnosing attribution capture, trust decay, and skill mismeasurement in an operation. Fill as you observe — fuel stops, end of shift, whenever. Your data persists locally on this device.</p>
  <p><strong>Scope.</strong> One operating unit (plant, fleet, facility) over a baseline window of 3–12 months.</p>
  <p><strong>Output.</strong> A signal profile that maps to the five failure modes. Not a decision — support for a decision practitioners will make.</p>
</div>

<!-- PHASE 1: PROVENANCE -->

<div class="phase expanded" data-phase="provenance">
  <div class="phase-header">Phase 1 / Provenance</div>
  <div class="phase-title">Decision origination log</div>
  <div class="phase-desc">Record who first noticed each decision that got made, discussed, or reversed. Compare later to who got credit.</div>

  <div class="phase-body">
    <div class="diagram">observation  →  transmission  →  reporting
   (origin)       (carrier)       (credit)

if origin ≠ credit  →  attribution capture</div>

```
<div class="field">
  <label class="field-label">Facility / Unit</label>
  <input type="text" id="facility" placeholder="Site identifier">
</div>

<div class="field">
  <label class="field-label">Your role</label>
  <input type="text" id="observerRole" placeholder="floor / office / driver / etc">
</div>

<h3 style="font-family: var(--font-mono); font-size: 12px; color: var(--accent); margin: 18px 0 8px; letter-spacing: 0.05em; text-transform: uppercase;">Provenance entries</h3>

<div id="provenanceList" class="entry-list"></div>

<div style="margin-top: 14px; border: 1px solid var(--border); padding: 12px; background: var(--panel-2);">
  <div class="field">
    <label class="field-label">Date</label>
    <input type="text" id="pvDate" placeholder="2026-04-16">
  </div>
  <div class="field">
    <label class="field-label">What was the decision or insight?</label>
    <textarea id="pvDescription" placeholder="Short description"></textarea>
  </div>
  <div class="field">
    <label class="field-label">Who first noticed it?</label>
    <input type="text" id="pvOriginator" placeholder="role + identifier (anon ok)">
  </div>
  <div class="field">
    <label class="field-label">Who got credit?</label>
    <input type="text" id="pvCreditTo" placeholder="role + identifier">
  </div>
  <div class="field">
    <label class="field-label">Downstream impact (describe in physical units if possible)</label>
    <textarea id="pvImpact" placeholder="hours saved, defects prevented, etc"></textarea>
  </div>
  <button class="add" onclick="addProvenance()">+ Add entry</button>
</div>

<div class="phase-toggle" onclick="togglePhase(this)">▼ Collapse</div>
```

  </div>
</div>

<!-- PHASE 2: TRUST + ENGAGEMENT -->

<div class="phase" data-phase="trust">
  <div class="phase-header">Phase 2 / Trust Field</div>
  <div class="phase-title">Anonymous quarterly instrument</div>
  <div class="phase-desc">Five questions. Fill them for yourself first. If rolled out, distribute anonymously and track distributions, not averages.</div>

  <div class="phase-body">
    <div class="warning-box">
      <strong>Signal reading</strong>
      Track the left tail, not the mean. If 20%+ answer 1–2 on any question, the site has a trust-field problem regardless of average.
    </div>

```
<div class="field">
  <label class="field-label">Q1. When I raise a problem at work, it is addressed.</label>
  <div class="likert" data-field="q1">
    <input type="radio" name="q1" id="q1_1" value="1"><label for="q1_1">1</label>
    <input type="radio" name="q1" id="q1_2" value="2"><label for="q1_2">2</label>
    <input type="radio" name="q1" id="q1_3" value="3"><label for="q1_3">3</label>
    <input type="radio" name="q1" id="q1_4" value="4"><label for="q1_4">4</label>
    <input type="radio" name="q1" id="q1_5" value="5"><label for="q1_5">5</label>
  </div>
  <div class="likert-labels"><span>never</span><span>always</span></div>
</div>

<div class="field">
  <label class="field-label">Q2. When I have an idea for how to do things better, the person who acts on it gives me credit.</label>
  <div class="likert" data-field="q2">
    <input type="radio" name="q2" id="q2_1" value="1"><label for="q2_1">1</label>
    <input type="radio" name="q2" id="q2_2" value="2"><label for="q2_2">2</label>
    <input type="radio" name="q2" id="q2_3" value="3"><label for="q2_3">3</label>
    <input type="radio" name="q2" id="q2_4" value="4"><label for="q2_4">4</label>
    <input type="radio" name="q2" id="q2_5" value="5"><label for="q2_5">5</label>
  </div>
  <div class="likert-labels"><span>never</span><span>always</span></div>
</div>

<div class="field">
  <label class="field-label">Q3. The people I work with are allowed to do their best work.</label>
  <div class="likert" data-field="q3">
    <input type="radio" name="q3" id="q3_1" value="1"><label for="q3_1">1</label>
    <input type="radio" name="q3" id="q3_2" value="2"><label for="q3_2">2</label>
    <input type="radio" name="q3" id="q3_3" value="3"><label for="q3_3">3</label>
    <input type="radio" name="q3" id="q3_4" value="4"><label for="q3_4">4</label>
    <input type="radio" name="q3" id="q3_5" value="5"><label for="q3_5">5</label>
  </div>
  <div class="likert-labels"><span>never</span><span>always</span></div>
</div>

<div class="field">
  <label class="field-label">Q4. If I saw something going wrong, I believe telling my supervisor would help.</label>
  <div class="likert" data-field="q4">
    <input type="radio" name="q4" id="q4_1" value="1"><label for="q4_1">1</label>
    <input type="radio" name="q4" id="q4_2" value="2"><label for="q4_2">2</label>
    <input type="radio" name="q4" id="q4_3" value="3"><label for="q4_3">3</label>
    <input type="radio" name="q4" id="q4_4" value="4"><label for="q4_4">4</label>
    <input type="radio" name="q4" id="q4_5" value="5"><label for="q4_5">5</label>
  </div>
  <div class="likert-labels"><span>never</span><span>always</span></div>
</div>

<div class="field">
  <label class="field-label">Q5. I would recommend working here to a friend who had my skills.</label>
  <div class="likert" data-field="q5">
    <input type="radio" name="q5" id="q5_1" value="1"><label for="q5_1">1</label>
    <input type="radio" name="q5" id="q5_2" value="2"><label for="q5_2">2</label>
    <input type="radio" name="q5" id="q5_3" value="3"><label for="q5_3">3</label>
    <input type="radio" name="q5" id="q5_4" value="4"><label for="q5_4">4</label>
    <input type="radio" name="q5" id="q5_5" value="5"><label for="q5_5">5</label>
  </div>
  <div class="likert-labels"><span>never</span><span>always</span></div>
</div>

<div class="phase-toggle" onclick="togglePhase(this)">▼ Collapse</div>
```

  </div>
</div>

<!-- PHASE 3: EXITS -->

<div class="phase" data-phase="exits">
  <div class="phase-header">Phase 3 / Exit Pattern</div>
  <div class="phase-title">Voluntary exit log</div>
  <div class="phase-desc">Track who leaves and what preceded it. The competence-extinction signature is visible in who goes first.</div>

  <div class="phase-body">
    <div id="exitList" class="entry-list"></div>

```
<div style="margin-top: 14px; border: 1px solid var(--border); padding: 12px; background: var(--panel-2);">
  <div class="field">
    <label class="field-label">Date of exit</label>
    <input type="text" id="exDate" placeholder="2026-04-16">
  </div>
  <div class="field">
    <label class="field-label">Role</label>
    <input type="text" id="exRole" placeholder="floor / office / etc">
  </div>
  <div class="field">
    <label class="field-label">Perceived competence (1-5, from peers' view)</label>
    <select id="exComp">
      <option value="">—</option>
      <option value="1">1 — low</option>
      <option value="2">2</option>
      <option value="3">3 — average</option>
      <option value="4">4</option>
      <option value="5">5 — high</option>
    </select>
  </div>
  <div class="field">
    <label class="field-label">Reason they gave (or were willing to share)</label>
    <textarea id="exReason"></textarea>
  </div>
  <div class="field">
    <label class="field-label">Next employer / destination (if known)</label>
    <input type="text" id="exNext" placeholder="other company / retired / unknown">
  </div>
  <button class="add" onclick="addExit()">+ Add exit</button>
</div>

<div class="phase-toggle" onclick="togglePhase(this)">▼ Collapse</div>
```

  </div>
</div>

<!-- PHASE 4: SKILL MISMATCH -->

<div class="phase" data-phase="skill">
  <div class="phase-header">Phase 4 / Skill Measurement</div>
  <div class="phase-title">Certification vs. embodied capacity</div>
  <div class="phase-desc">Log cases where the certification signal inverts the actual capacity signal. Dyslexic veterans. Green certs who can't do the work. Etc.</div>

  <div class="phase-body">
    <div id="skillList" class="entry-list"></div>

```
<div style="margin-top: 14px; border: 1px solid var(--border); padding: 12px; background: var(--panel-2);">
  <div class="field">
    <label class="field-label">Person (role + anon identifier)</label>
    <input type="text" id="skPerson" placeholder="eg floor tech, 22 yrs">
  </div>
  <div class="field">
    <label class="field-label">What's their actual capacity?</label>
    <textarea id="skCapacity" placeholder="what they can actually do"></textarea>
  </div>
  <div class="field">
    <label class="field-label">What's their certification signal?</label>
    <textarea id="skCert" placeholder="what HR / paperwork sees"></textarea>
  </div>
  <div class="field">
    <label class="field-label">Direction of inversion</label>
    <select id="skDirection">
      <option value="">—</option>
      <option value="under">certification UNDER-measures them</option>
      <option value="over">certification OVER-measures them</option>
      <option value="match">reasonable match</option>
    </select>
  </div>
  <button class="add" onclick="addSkill()">+ Add observation</button>
</div>

<details>
  <summary>▸ What to watch for</summary>
  <div class="warning-box" style="margin-top: 8px;">
    <strong>Common inversions</strong>
    Dyslexia + decades of embodied experience → under-measured by literacy-based tests.<br><br>
    Fresh cert + zero plant hours → over-measured; needs 2–5 years of mentorship to reach actual capacity.<br><br>
    Cross-domain salvage capacity → invisible to domain-specific certifications.
  </div>
</details>

<div class="phase-toggle" onclick="togglePhase(this)">▼ Collapse</div>
```

  </div>
</div>

<!-- PHASE 5: FIELD NOTES -->

<div class="phase" data-phase="notes">
  <div class="phase-header">Phase 5 / Field Notes</div>
  <div class="phase-title">Observations that don't fit the slots</div>
  <div class="phase-desc">Patterns you see that the structured fields don't capture. Free-form.</div>

  <div class="phase-body">
    <div id="notesList" class="entry-list"></div>
    <div style="margin-top: 14px; border: 1px solid var(--border); padding: 12px; background: var(--panel-2);">
      <div class="field">
        <label class="field-label">Date</label>
        <input type="text" id="ntDate" placeholder="2026-04-16">
      </div>
      <div class="field">
        <label class="field-label">Note</label>
        <textarea id="ntText" placeholder="what you saw, thought, or heard"></textarea>
      </div>
      <button class="add" onclick="addNote()">+ Add note</button>
    </div>

```
<div class="phase-toggle" onclick="togglePhase(this)">▼ Collapse</div>
```

  </div>
</div>

<!-- SUMMARY -->

<div class="summary" id="summary">
  <h2>Signal profile</h2>
  <div id="summaryContent">
    <div class="summary-row">
      <span class="summary-label">Provenance entries</span>
      <span class="summary-value" id="sumProvenance">0</span>
    </div>
    <div class="summary-row">
      <span class="summary-label">Attribution capture rate</span>
      <span class="summary-value" id="sumCapture">—</span>
    </div>
    <div class="summary-row">
      <span class="summary-label">Trust instrument responses</span>
      <span class="summary-value" id="sumTrust">0/5</span>
    </div>
    <div class="summary-row">
      <span class="summary-label">Trust low-tail (≤2 answers)</span>
      <span class="summary-value" id="sumTrustLow">—</span>
    </div>
    <div class="summary-row">
      <span class="summary-label">Exits logged</span>
      <span class="summary-value" id="sumExits">0</span>
    </div>
    <div class="summary-row">
      <span class="summary-label">Exit competence signal</span>
      <span class="summary-value" id="sumExitComp">—</span>
    </div>
    <div class="summary-row">
      <span class="summary-label">Skill mismatch observations</span>
      <span class="summary-value" id="sumSkill">0</span>
    </div>
    <div class="summary-row">
      <span class="summary-label">Skill under-measurement rate</span>
      <span class="summary-value" id="sumSkillUnder">—</span>
    </div>
    <div class="summary-row">
      <span class="summary-label">Field notes</span>
      <span class="summary-value" id="sumNotes">0</span>
    </div>
  </div>
</div>

<div class="actions">
  <button onclick="exportData()" class="primary">Export</button>
  <button onclick="clearAll()">Clear</button>
</div>

<script>
// ===== STATE =====
const STATE_KEY = 'labor-thermo-audit-v1';
let state = {
  facility: '',
  observerRole: '',
  provenance: [],
  exits: [],
  skill: [],
  notes: [],
  trust: {},
};

// ===== PERSISTENCE =====
async function save() {
  try {
    if (window.storage) {
      await window.storage.set(STATE_KEY, JSON.stringify(state));
    } else {
      // Fallback if storage API unavailable
      window._fallbackState = JSON.stringify(state);
    }
    showSaved();
  } catch (e) {
    console.error('Save failed:', e);
  }
}

async function load() {
  try {
    if (window.storage) {
      const result = await window.storage.get(STATE_KEY);
      if (result && result.value) {
        state = JSON.parse(result.value);
      }
    }
  } catch (e) {
    // No existing data — that's fine
    console.log('No prior state:', e);
  }
  hydrate();
  updateSummary();
}

function showSaved() {
  const ind = document.getElementById('saveIndicator');
  ind.classList.add('show');
  setTimeout(() => ind.classList.remove('show'), 1500);
}

// ===== HYDRATION =====
function hydrate() {
  document.getElementById('facility').value = state.facility || '';
  document.getElementById('observerRole').value = state.observerRole || '';

  // Trust radios
  for (let i = 1; i <= 5; i++) {
    const val = state.trust['q' + i];
    if (val) {
      const radio = document.getElementById(`q${i}_${val}`);
      if (radio) radio.checked = true;
    }
  }

  renderProvenance();
  renderExits();
  renderSkill();
  renderNotes();
}

// ===== FIELD BINDINGS =====
document.getElementById('facility').addEventListener('input', (e) => {
  state.facility = e.target.value;
  save();
});
document.getElementById('observerRole').addEventListener('input', (e) => {
  state.observerRole = e.target.value;
  save();
});

document.querySelectorAll('.likert').forEach(grp => {
  const field = grp.dataset.field;
  grp.querySelectorAll('input[type="radio"]').forEach(r => {
    r.addEventListener('change', (e) => {
      state.trust[field] = parseInt(e.target.value);
      save();
      updateSummary();
    });
  });
});

// ===== PHASE TOGGLE =====
function togglePhase(toggle) {
  const phase = toggle.closest('.phase');
  phase.classList.toggle('expanded');
  toggle.textContent = phase.classList.contains('expanded') ? '▼ Collapse' : '▶ Expand';
}

document.querySelectorAll('.phase').forEach(phase => {
  const header = phase.querySelector('.phase-header');
  const title = phase.querySelector('.phase-title');
  [header, title].forEach(el => {
    el.style.cursor = 'pointer';
    el.addEventListener('click', () => {
      phase.classList.toggle('expanded');
      const toggle = phase.querySelector('.phase-toggle');
      if (toggle) {
        toggle.textContent = phase.classList.contains('expanded') ? '▼ Collapse' : '▶ Expand';
      }
    });
  });
});

// ===== PROVENANCE =====
function addProvenance() {
  const entry = {
    id: Date.now(),
    date: document.getElementById('pvDate').value,
    description: document.getElementById('pvDescription').value,
    originator: document.getElementById('pvOriginator').value,
    creditTo: document.getElementById('pvCreditTo').value,
    impact: document.getElementById('pvImpact').value,
  };
  if (!entry.description && !entry.originator) return;
  state.provenance.push(entry);
  save();
  renderProvenance();
  updateSummary();
  ['pvDate','pvDescription','pvOriginator','pvCreditTo','pvImpact'].forEach(id => {
    document.getElementById(id).value = '';
  });
}

function renderProvenance() {
  const list = document.getElementById('provenanceList');
  list.innerHTML = state.provenance.map(e => {
    const captured = e.originator && e.creditTo &&
                     e.originator.trim().toLowerCase() !== e.creditTo.trim().toLowerCase();
    return `<div class="entry">
      <button class="entry-del" onclick="removeProvenance(${e.id})">×</button>
      <div class="entry-meta">${e.date || '—'} ${captured ? ' · <span style="color:var(--red)">CAPTURE</span>' : ''}</div>
      <div class="entry-text"><strong>${escapeHtml(e.description)}</strong></div>
      <div class="entry-text" style="font-size:12px; color:var(--text-dim); margin-top:4px;">
        origin: ${escapeHtml(e.originator)} → credit: ${escapeHtml(e.creditTo)}
      </div>
      ${e.impact ? `<div class="entry-text" style="font-size:12px; color:var(--text-faint); margin-top:4px;">impact: ${escapeHtml(e.impact)}</div>` : ''}
    </div>`;
  }).join('');
}

function removeProvenance(id) {
  state.provenance = state.provenance.filter(e => e.id !== id);
  save();
  renderProvenance();
  updateSummary();
}

// ===== EXITS =====
function addExit() {
  const entry = {
    id: Date.now(),
    date: document.getElementById('exDate').value,
    role: document.getElementById('exRole').value,
    competence: parseInt(document.getElementById('exComp').value) || null,
    reason: document.getElementById('exReason').value,
    next: document.getElementById('exNext').value,
  };
  if (!entry.role && !entry.reason) return;
  state.exits.push(entry);
  save();
  renderExits();
  updateSummary();
  ['exDate','exRole','exComp','exReason','exNext'].forEach(id => {
    document.getElementById(id).value = '';
  });
}

function renderExits() {
  const list = document.getElementById('exitList');
  list.innerHTML = state.exits.map(e => {
    return `<div class="entry">
      <button class="entry-del" onclick="removeExit(${e.id})">×</button>
      <div class="entry-meta">${e.date || '—'} · ${escapeHtml(e.role)} · comp=${e.competence ?? '—'}</div>
      ${e.reason ? `<div class="entry-text">${escapeHtml(e.reason)}</div>` : ''}
      ${e.next ? `<div class="entry-text" style="font-size:12px; color:var(--text-faint); margin-top:4px;">→ ${escapeHtml(e.next)}</div>` : ''}
    </div>`;
  }).join('');
}

function removeExit(id) {
  state.exits = state.exits.filter(e => e.id !== id);
  save();
  renderExits();
  updateSummary();
}

// ===== SKILL =====
function addSkill() {
  const entry = {
    id: Date.now(),
    person: document.getElementById('skPerson').value,
    capacity: document.getElementById('skCapacity').value,
    cert: document.getElementById('skCert').value,
    direction: document.getElementById('skDirection').value,
  };
  if (!entry.person) return;
  state.skill.push(entry);
  save();
  renderSkill();
  updateSummary();
  ['skPerson','skCapacity','skCert','skDirection'].forEach(id => {
    document.getElementById(id).value = '';
  });
}

function renderSkill() {
  const list = document.getElementById('skillList');
  list.innerHTML = state.skill.map(e => {
    const color = e.direction === 'under' ? 'var(--red)' : e.direction === 'over' ? 'var(--yellow)' : 'var(--text-dim)';
    const label = e.direction === 'under' ? 'UNDER-MEASURED' : e.direction === 'over' ? 'OVER-MEASURED' : 'matched';
    return `<div class="entry">
      <button class="entry-del" onclick="removeSkill(${e.id})">×</button>
      <div class="entry-meta"><strong>${escapeHtml(e.person)}</strong> · <span style="color:${color}">${label}</span></div>
      ${e.capacity ? `<div class="entry-text" style="font-size:12px; margin-top:4px;"><span style="color:var(--text-dim)">actual:</span> ${escapeHtml(e.capacity)}</div>` : ''}
      ${e.cert ? `<div class="entry-text" style="font-size:12px; margin-top:2px;"><span style="color:var(--text-dim)">cert says:</span> ${escapeHtml(e.cert)}</div>` : ''}
    </div>`;
  }).join('');
}

function removeSkill(id) {
  state.skill = state.skill.filter(e => e.id !== id);
  save();
  renderSkill();
  updateSummary();
}

// ===== NOTES =====
function addNote() {
  const entry = {
    id: Date.now(),
    date: document.getElementById('ntDate').value,
    text: document.getElementById('ntText').value,
  };
  if (!entry.text) return;
  state.notes.push(entry);
  save();
  renderNotes();
  updateSummary();
  ['ntDate','ntText'].forEach(id => {
    document.getElementById(id).value = '';
  });
}

function renderNotes() {
  const list = document.getElementById('notesList');
  list.innerHTML = state.notes.map(e => {
    return `<div class="entry">
      <button class="entry-del" onclick="removeNote(${e.id})">×</button>
      <div class="entry-meta">${e.date || '—'}</div>
      <div class="entry-text">${escapeHtml(e.text)}</div>
    </div>`;
  }).join('');
}

function removeNote(id) {
  state.notes = state.notes.filter(e => e.id !== id);
  save();
  renderNotes();
  updateSummary();
}

// ===== SUMMARY =====
function updateSummary() {
  const pvCount = state.provenance.length;
  document.getElementById('sumProvenance').textContent = pvCount;

  if (pvCount > 0) {
    const captured = state.provenance.filter(e =>
      e.originator && e.creditTo &&
      e.originator.trim().toLowerCase() !== e.creditTo.trim().toLowerCase()
    ).length;
    const rate = (captured / pvCount * 100).toFixed(0);
    const el = document.getElementById('sumCapture');
    el.textContent = `${captured}/${pvCount} (${rate}%)`;
    el.className = 'summary-value ' + (rate >= 40 ? 'bad' : rate >= 15 ? 'warn' : 'good');
  } else {
    document.getElementById('sumCapture').textContent = '—';
    document.getElementById('sumCapture').className = 'summary-value';
  }

  const trustCount = Object.keys(state.trust).length;
  document.getElementById('sumTrust').textContent = `${trustCount}/5`;

  if (trustCount === 5) {
    const lowCount = Object.values(state.trust).filter(v => v <= 2).length;
    const el = document.getElementById('sumTrustLow');
    el.textContent = `${lowCount}/5`;
    el.className = 'summary-value ' + (lowCount >= 2 ? 'bad' : lowCount >= 1 ? 'warn' : 'good');
  } else {
    document.getElementById('sumTrustLow').textContent = '—';
    document.getElementById('sumTrustLow').className = 'summary-value';
  }

  document.getElementById('sumExits').textContent = state.exits.length;

  const exitsWithComp = state.exits.filter(e => e.competence !== null);
  if (exitsWithComp.length >= 2) {
    const avgComp = exitsWithComp.reduce((s,e) => s + e.competence, 0) / exitsWithComp.length;
    const el = document.getElementById('sumExitComp');
    el.textContent = `avg ${avgComp.toFixed(1)} / 5`;
    el.className = 'summary-value ' + (avgComp >= 4 ? 'bad' : avgComp >= 3 ? 'warn' : 'good');
  } else {
    document.getElementById('sumExitComp').textContent = '—';
    document.getElementById('sumExitComp').className = 'summary-value';
  }

  document.getElementById('sumSkill').textContent = state.skill.length;

  if (state.skill.length > 0) {
    const under = state.skill.filter(e => e.direction === 'under').length;
    const rate = (under / state.skill.length * 100).toFixed(0);
    const el = document.getElementById('sumSkillUnder');
    el.textContent = `${under}/${state.skill.length} (${rate}%)`;
    el.className = 'summary-value ' + (rate >= 40 ? 'bad' : rate >= 20 ? 'warn' : 'good');
  } else {
    document.getElementById('sumSkillUnder').textContent = '—';
    document.getElementById('sumSkillUnder').className = 'summary-value';
  }

  document.getElementById('sumNotes').textContent = state.notes.length;
}

// ===== EXPORT / CLEAR =====
function exportData() {
  const data = JSON.stringify(state, null, 2);
  const blob = new Blob([data], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  const stamp = new Date().toISOString().slice(0, 10);
  a.download = `labor-thermo-audit-${stamp}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

async function clearAll() {
  if (!confirm('Clear all audit data? This cannot be undone.')) return;
  state = {
    facility: '',
    observerRole: '',
    provenance: [],
    exits: [],
    skill: [],
    notes: [],
    trust: {},
  };
  try {
    if (window.storage) await window.storage.delete(STATE_KEY);
  } catch (e) {}
  hydrate();
  updateSummary();
  // Clear radios
  document.querySelectorAll('input[type="radio"]').forEach(r => r.checked = false);
}

// ===== HELPERS =====
function escapeHtml(s) {
  if (!s) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ===== INIT =====
load();
</script>

</body>
</html>

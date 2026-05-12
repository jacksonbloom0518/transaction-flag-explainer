# Fraud Risk Scorer Frontend Improvements — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve `frontend/index.html` with a gradient-strip score gauge, a plain-English explanation block, and a session history panel — all client-side, no backend changes.

**Architecture:** All changes are confined to `frontend/index.html`. The existing `render()` function is extended: a new `addToHistory()` call is appended at the end, and an optional `addToHist` parameter (default `true`) lets history-entry clicks re-display a result without duplicating history. Two pure helpers — `generateAnalysis()` and `relativeTime()` — keep logic self-contained. No new files, no build step.

**Tech Stack:** Vanilla JS, HTML5, CSS custom properties, IBM Plex fonts (already loaded). Verification is manual browser testing — open `frontend/index.html` directly or via the running uvicorn server at `http://127.0.0.1:8000`.

---

### Task 1: Ctrl+Enter keyboard shortcut

**Files:**
- Modify: `frontend/index.html` — `<script>` block

- [ ] **Step 1: Add keydown listener on the textarea**

In the `<script>` block, directly after the chips click listener (after the `document.getElementById('examples').addEventListener(...)` block), insert:

```js
document.getElementById('desc').addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    document.getElementById('form').requestSubmit();
  }
});
```

- [ ] **Step 2: Verify in browser**

Open `frontend/index.html`. Type any text in the textarea, press Ctrl+Enter (Windows/Linux) or Cmd+Enter (Mac).
Expected: form submits and the analyze call fires — identical to clicking the button.

- [ ] **Step 3: Commit**

```bash
git add frontend/index.html
git commit -m "feat: add Ctrl+Enter shortcut to submit transaction form"
```

---

### Task 2: Score display — gradient strip, tick marker, /100 denominator, count-up

**Files:**
- Modify: `frontend/index.html` — CSS, HTML, JS

#### 2a — CSS

- [ ] **Step 1: Replace gauge CSS block**

Find and replace the entire gauge CSS block (currently inside `<style>`):

**Remove:**
```css
  /* Gauge */
  .gauge-track {
    height: 3px; background: var(--border); border-radius: 2px;
    margin-bottom: 18px; overflow: hidden;
  }
  .gauge-fill {
    height: 100%; border-radius: 2px; width: 0%;
    transition: width .9s cubic-bezier(.16,1,.3,1);
  }
```

**Add in its place:**
```css
  /* Gauge */
  .gauge-track {
    height: 6px;
    background: linear-gradient(90deg,
      var(--low)  0%,   var(--low)  25%,
      var(--med)  25%,  var(--med)  60%,
      var(--high) 60%,  var(--high) 100%);
    border-radius: 3px;
    margin-bottom: 18px;
    position: relative;
    overflow: visible;
  }
  .gauge-tick {
    position: absolute;
    top: -3px; left: 0%;
    width: 2px; height: 12px;
    background: #fff; border-radius: 1px;
    box-shadow: 0 0 6px rgba(255,255,255,.5);
    transition: left .9s cubic-bezier(.16,1,.3,1);
  }
  .gauge-thresh {
    position: absolute;
    top: 0; width: 1px; height: 6px;
    background: rgba(0,0,0,.35);
    pointer-events: none;
  }
```

- [ ] **Step 2: Add .score-denom rule**

Directly after the existing `.score-num` CSS rule, add:

```css
  .score-denom {
    font-size: 13px; color: var(--muted);
    font-weight: 400; letter-spacing: 0; margin-left: 2px;
  }
```

#### 2b — HTML

- [ ] **Step 3: Restructure #score-num**

Find:
```html
          <div class="score-num" id="score-num">—</div>
```
Replace with:
```html
          <div class="score-num" id="score-num"><span id="score-val">—</span><span class="score-denom" id="score-denom"></span></div>
```

- [ ] **Step 4: Replace gauge markup**

Find:
```html
      <div class="gauge-track">
        <div class="gauge-fill" id="gauge"></div>
      </div>
```
Replace with:
```html
      <div class="gauge-track">
        <div class="gauge-thresh" style="left:25%"></div>
        <div class="gauge-thresh" style="left:60%"></div>
        <div class="gauge-tick" id="gauge-tick"></div>
      </div>
```

#### 2c — JS

- [ ] **Step 5: Add countUp() helper**

Add this function at the top of the `<script>` block, before the chips listener:

```js
function countUp(target, duration) {
  const el = document.getElementById('score-val');
  const start = performance.now();
  (function tick(now) {
    const t = Math.min((now - start) / duration, 1);
    el.textContent = Math.round(target * (1 - Math.pow(1 - t, 3)));
    if (t < 1) requestAnimationFrame(tick);
  })(performance.now());
}
```

- [ ] **Step 6: Update score + gauge section inside render()**

Find (inside `render()`):
```js
    // Score number
    const numEl = document.getElementById('score-num');
    numEl.textContent = score;
    numEl.className = `score-num c-${lvl}`;

    // Badge
    const badgeEl = document.getElementById('badge');
    badgeEl.textContent = risk_level.toUpperCase();
    badgeEl.className = `badge c-${lvl}`;

    // Gauge
    const gaugeEl = document.getElementById('gauge');
    gaugeEl.className = `gauge-fill g-${lvl}`;
    gaugeEl.style.width = '0%';
    requestAnimationFrame(() => requestAnimationFrame(() => {
      gaugeEl.style.width = `${score}%`;
    }));
```

Replace with:
```js
    // Score number
    document.getElementById('score-num').className = `score-num c-${lvl}`;
    document.getElementById('score-denom').textContent = '/100';
    countUp(score, 600);

    // Badge
    const badgeEl = document.getElementById('badge');
    badgeEl.textContent = risk_level.toUpperCase();
    badgeEl.className = `badge c-${lvl}`;

    // Gauge tick
    const tickEl = document.getElementById('gauge-tick');
    tickEl.style.left = '0%';
    requestAnimationFrame(() => requestAnimationFrame(() => {
      tickEl.style.left = `${score}%`;
    }));
```

- [ ] **Step 7: Verify in browser**

Submit "wire transfer $10,000 to casino". Expected:
- Score number animates from 0 up to the returned value over ~600ms
- `/100` appears next to the score in muted grey
- Gauge shows a static green → amber → red gradient strip
- Faint dark dividers visible at 25% and 60%
- White tick slides to the correct score position

- [ ] **Step 8: Commit**

```bash
git add frontend/index.html
git commit -m "feat: replace gauge bar with gradient strip, tick marker, and count-up animation"
```

---

### Task 3: generateAnalysis() + explanation block

**Files:**
- Modify: `frontend/index.html` — CSS, HTML, JS

#### 3a — CSS

- [ ] **Step 1: Add analysis block styles**

After the `.no-flags` CSS rule, add:

```css
  /* Analysis block */
  .analysis-block {
    border-top: 1px solid var(--border);
    padding-top: 14px;
    margin-top: 14px;
  }
  #analysis-text {
    font-family: var(--sans);
    font-size: 13px; color: var(--text);
    line-height: 1.6; font-weight: 300; margin: 0;
  }
```

#### 3b — HTML

- [ ] **Step 2: Add analysis block after flags-wrap**

Find:
```html
      <div class="flags-label">DETECTED FLAGS</div>
      <div class="flags-wrap" id="flags-wrap"></div>
```
Replace with:
```html
      <div class="flags-label">DETECTED FLAGS</div>
      <div class="flags-wrap" id="flags-wrap"></div>

      <div class="analysis-block">
        <div class="flags-label">ANALYSIS</div>
        <p id="analysis-text"></p>
      </div>
```

#### 3c — JS

- [ ] **Step 3: Add generateAnalysis() helper**

Add directly after `countUp()` (before the chips listener):

```js
function generateAnalysis(risk_level, flags) {
  if (risk_level === 'low') {
    return 'Low risk — no significant indicators detected. Transaction appears routine.';
  }

  const highNames = flags
    .filter(f => f.startsWith('high_risk_term:'))
    .map(f => f.split(':')[1].replace(/_/g, ' '));
  const medNames = flags
    .filter(f => f.startsWith('medium_risk_term:'))
    .map(f => f.split(':')[1].replace(/_/g, ' '));
  const allNames = flags.map(f => f.includes(':') ? f.split(':')[1].replace(/_/g, ' ') : f);

  if (risk_level === 'medium') {
    const named = medNames.slice(0, 3).join(', ') || 'elevated indicators';
    return `Moderate risk — ${medNames.length || 'some'} elevated indicator(s) detected (${named}). Review before approving.`;
  }

  // high
  const count = highNames.length;
  const named = highNames.slice(0, 3).join(', ');
  const nameStr = named ? ` (${named})` : '';

  let context = 'This transaction matches common fraud patterns.';
  if (allNames.some(n => ['casino', 'gambling', 'bet', 'lottery'].includes(n))) {
    context = 'This pattern is associated with money laundering and gambling-related fraud.';
  } else if (allNames.some(n => ['gift card', 'winner', 'claim', 'prize', 'inheritance'].includes(n))) {
    context = 'This pattern matches social engineering and advance-fee fraud schemes.';
  } else if (allNames.some(n => ['wire transfer', 'western union', 'moneygram'].includes(n))) {
    context = 'Wire-based transfers to high-risk destinations are a common fraud vector.';
  } else if (allNames.some(n => ['bitcoin', 'crypto'].includes(n))) {
    context = 'Cryptocurrency transfers to unknown destinations carry elevated laundering risk.';
  }

  return `High risk — ${count} critical indicator${count !== 1 ? 's' : ''} detected${nameStr}. ${context}`;
}
```

- [ ] **Step 4: Call generateAnalysis() inside render()**

At the end of the flags section in `render()` (after the `flags.forEach(...)` block), add:

```js
    // Analysis
    document.getElementById('analysis-text').textContent = generateAnalysis(risk_level, flags);
```

- [ ] **Step 5: Verify in browser**

Test these inputs and confirm the analysis text:

| Input | Expected text |
|---|---|
| `wire transfer $10,000 to casino` | "High risk — 2 critical indicators detected (casino, wire transfer). This pattern is associated with money laundering..." |
| `$45 grocery store afternoon` | "Low risk — no significant indicators detected. Transaction appears routine." |
| `gift card purchase winner claim` | "High risk — ... This pattern matches social engineering and advance-fee fraud schemes." |
| `bitcoin purchase overseas` | Analysis mentions crypto laundering risk |

- [ ] **Step 6: Commit**

```bash
git add frontend/index.html
git commit -m "feat: add plain-English analysis block generated from flag data"
```

---

### Task 4: Session history panel

**Files:**
- Modify: `frontend/index.html` — CSS, HTML, JS

#### 4a — CSS

- [ ] **Step 1: Add history styles**

After the `footer` CSS rule, add:

```css
  /* History */
  #history-card { display: none; }

  .history-entry {
    display: flex; align-items: center;
    justify-content: space-between; gap: 10px;
    padding: 9px 16px;
    border-bottom: 1px solid var(--border);
    cursor: pointer;
    transition: background .1s;
  }
  .history-entry:last-child { border-bottom: none; }
  .history-entry:hover { background: var(--dim); }
  .history-entry.active { background: var(--dim); }

  .history-desc {
    font-size: 12px; color: var(--text);
    white-space: nowrap; overflow: hidden;
    text-overflow: ellipsis; max-width: 340px;
  }
  .history-time { font-size: 10px; color: var(--muted); margin-top: 2px; }

  .history-badge {
    font-size: 10px; letter-spacing: .12em;
    padding: 2px 8px; border-radius: 3px;
    border: 1px solid currentColor; white-space: nowrap; flex-shrink: 0;
  }
```

#### 4b — HTML

- [ ] **Step 2: Add history card after result card**

Find the closing `</div>` of `id="result"` (the `</div>` that closes the result card). Immediately after it, insert:

```html
  <!-- History -->
  <div class="card" id="history-card">
    <div class="card-head"><span class="dot"></span>RECENT ANALYSES</div>
    <div id="history-list"></div>
  </div>
```

#### 4c — JS

- [ ] **Step 3: Add history state and helpers**

Add these at the top of the `<script>` block (before `countUp`):

```js
const history = [];
let activeIdx = 0;

function relativeTime(ts) {
  const s = Math.floor((Date.now() - ts) / 1000);
  if (s < 60) return 'just now';
  const m = Math.floor(s / 60);
  if (m < 60) return `${m} min ago`;
  return `${Math.floor(m / 60)} hr ago`;
}

function renderHistoryList() {
  const list = document.getElementById('history-list');
  list.innerHTML = '';
  history.forEach((entry, i) => {
    const lvl = entry.risk_level === 'high' ? 'high' : entry.risk_level === 'medium' ? 'med' : 'low';
    const row = document.createElement('div');
    row.className = `history-entry${i === activeIdx ? ' active' : ''}`;
    row.innerHTML = `
      <div>
        <div class="history-desc">${entry.description}</div>
        <div class="history-time">${relativeTime(entry.timestamp)}</div>
      </div>
      <div class="history-badge c-${lvl}">${entry.score} · ${entry.risk_level.toUpperCase()}</div>
    `;
    row.addEventListener('click', () => {
      activeIdx = i;
      render(entry, false);
    });
    list.appendChild(row);
  });
}

function addToHistory(entry) {
  history.unshift(entry);
  if (history.length > 10) history.pop();
  activeIdx = 0;
  renderHistoryList();
  if (history.length >= 2) {
    document.getElementById('history-card').style.display = 'block';
  }
}
```

- [ ] **Step 4: Update render() signature and add history call**

Change the `render` function signature from:
```js
  function render({ score, risk_level, flags }) {
```
To:
```js
  function render({ score, risk_level, flags, description }, addToHist = true) {
```

At the very end of `render()`, after the `scrollIntoView` call, add:
```js
    if (addToHist) {
      addToHistory({
        description: description || document.getElementById('desc').value.trim(),
        score,
        risk_level,
        flags,
        timestamp: Date.now(),
      });
    }
```

- [ ] **Step 5: Pass description from the fetch call site**

Find:
```js
      render(await res.json());
```
Replace with:
```js
      render({ ...await res.json(), description: desc });
```

- [ ] **Step 6: Verify in browser**

Run the following sequence:
1. Submit "wire transfer $10,000 to casino" → history card stays hidden
2. Submit "$45 grocery store afternoon" → history card appears with 2 rows; newest on top, highlighted
3. Click the older entry → result card updates to that result, that row highlights, new row loses highlight
4. Run 9 more analyses → confirm only the 10 most recent remain

- [ ] **Step 7: Commit**

```bash
git add frontend/index.html
git commit -m "feat: add session history panel with clickable past analyses"
```

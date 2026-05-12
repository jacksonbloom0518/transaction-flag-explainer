# Fraud Risk Scorer — Frontend Improvements Design

**Date:** 2026-05-12  
**File:** `frontend/index.html`  
**Scope:** Client-side only — no backend changes required.

---

## Overview

Three targeted improvements to the existing single-page Fraud Risk Scorer UI, plus two minor UX enhancements. All changes are contained within `frontend/index.html`. The backend API contract (`POST /analyze` → `{ score, risk_level, flags }`) is unchanged.

---

## 1. Score Display — Gradient Strip with Tick Marker

**Current:** A thin animated bar (`gauge-track` / `gauge-fill`) that fills from 0% to `score%` in a single solid color matching risk level.

**New behavior:**
- The bar is replaced by a static tri-color gradient strip: green from 0–25%, amber from 25–60%, red from 60–100%. The gradient is always fully visible — it represents the full scale, not the score.
- A white 2px × 12px tick element slides to `left: score%` on render, using the same `requestAnimationFrame` double-tick trick already in use for the fill animation. Transition: `left 0.9s cubic-bezier(.16,1,.3,1)`.
- The score number gains a `/100` suffix in muted (`var(--muted)`) text, displayed as an inline `<span>` at smaller size (`13px`) next to the large score numeral.
- Threshold tick marks (faint vertical lines at 25% and 60%) are drawn into the strip so the zones are readable even without the color labels.

**CSS changes:** Remove `.gauge-fill` animated-width rule. Add `.gauge-tick` positioned element. Update `.gauge-track` height to `6px`. Add `score-denom` span style.

---

## 2. Plain-English Explanation Block

**Placement:** Below the `DETECTED FLAGS` section, separated by a `1px solid var(--border)` top border. Visible only when the result card is shown.

**Markup:** A new `<div class="analysis-block">` containing:
- A `ANALYSIS` label (same 10px uppercase muted style as `DETECTED FLAGS`)
- A `<p id="analysis-text">` in `var(--sans)` (IBM Plex Sans), 13px, `font-weight: 300`, `line-height: 1.6`, `var(--text)` color

**Text generation (client-side, in `render()`):**
1. Count high-risk flags (`high_risk_term:*`) and medium-risk flags (`medium_risk_term:*`).
2. Extract top flag names for use in copy (strip prefix, replace underscores with spaces).
3. Select a sentence template by `risk_level`:
   - `high`: *"High risk — [N] critical indicator(s) detected ([top flags]). [Context sentence based on flag types.]"*
   - `medium`: *"Moderate risk — [N] elevated indicator(s) detected ([top flags]). Review before approving."*
   - `low`: *"Low risk — no significant indicators detected. Transaction appears routine."*
4. Context sentences for high-risk: presence of `casino`/`gambling` → money-laundering pattern note; `gift card`/`winner`/`claim` → social engineering note; `wire transfer`/`western union` → fund transfer fraud note; default → general elevated risk note.
5. Cap named flags in copy at 3 to keep sentences readable.

**No API call** — generated entirely from the existing response payload.

---

## 3. Session History Panel

**Appearance:** A third card below the result card (`id="history-card"`), hidden (`display: none`) until the second successful analysis completes.

**Per-entry data stored (JS array, session memory only):**
```js
{ description, score, risk_level, flags, analysisText, timestamp }
```

**Behavior:**
- On each successful render, prepend a new entry to the `history` array. Cap at 10 entries (drop oldest).
- Re-render the history list after each update.
- The most recently added entry is highlighted (background `var(--dim)`).
- Clicking any entry calls `render()` with that entry's stored data and scrolls the result card into view.
- Timestamps shown as relative labels: "just now" (< 60s), "N min ago" (< 60 min), "N hr ago" (otherwise).

**Card structure:**
```
[ RECENT ANALYSES ]           ← card-head style
[ description truncated ]  [score · LEVEL]   ← entry row
...
```

Entry rows use `cursor: pointer` and a hover highlight (`background: var(--dim)`). Active entry (currently displayed) has a persistent highlight.

---

## 4. Implicit UX Enhancements

These require no design decisions — included in the implementation:

- **Animated score count-up:** On each `render()` call, animate the score numeral from 0 to `score` over ~600ms using `requestAnimationFrame`. Tick marker animates simultaneously via CSS transition.
- **Ctrl+Enter / Cmd+Enter to submit:** `keydown` listener on the textarea; triggers `form.requestSubmit()` when `(e.ctrlKey || e.metaKey) && e.key === 'Enter'`.

---

## Architecture

All logic lives in the existing `<script>` block in `frontend/index.html`. No new files, no build step, no dependencies beyond what the page already loads (IBM Plex fonts from Google Fonts).

**Modified functions:**
- `render({ score, risk_level, flags })` — extended to drive tick marker, `/100` label, explanation text, count-up animation, and history update
- New helper `generateAnalysis(score, risk_level, flags) → string`
- New helper `updateHistory(entry)` — prepends to array, trims to 10, re-renders list
- New helper `renderHistoryList()` — rebuilds history card DOM
- New helper `relativeTime(timestamp) → string`

**New DOM elements:**
- `#score-denom` — the `/100` span
- `#gauge-tick` — the white tick marker
- `#analysis-text` — explanation paragraph
- `.analysis-block` — wrapper div
- `#history-card` — the history card (initially hidden)
- `#history-list` — the entry list container inside the history card

---

## Out of Scope

- Persisting history across page reloads (no localStorage)
- Exporting or copying results
- Any backend or API changes
- Mobile layout rework beyond what the current responsive CSS already handles

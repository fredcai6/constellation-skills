# Launch Order: `cmdr-659-663 — Grip baseline module G`

Commanders start cold. Read this whole order, then `gh issue view 663` for the full build spec (it embeds confirmed spec §2, verbatim, plus the T1/T2 held-out acceptance and the #560 thin-fit decision).

## Mission
Build issue **#663** (epic #659, Build 1, manifest id `D`): ONE canonical grip-baseline module G owning per-weekend track grip state so every consumer subtracts an identical G (ending the current half-implementation scatter). Intra-session = saturating evolution curve on **cumulative car-laps** (not wall clock); inter-session = a **free offset per session start** estimated from data (absorbs overnight/support-series/temperature; rain flag → wide-σ re-estimate). Fit from field-pooled pace with compound/tyre-age/fuel correction via the **existing** `src/physics/layer2/tyre_supplant.py`; **Student-t residuals**; σ(G) propagates to every consumer. Interface follows the repo's estimate-store pattern (`estimate_store.py`+`estimate_batch.py`); design-it-twice deliberately skipped (precedented shape).

## Prior-Wave Verdicts (pasted)
None — Wave 0. You consume existing landed machinery only (`tyre_supplant.py`, `estimate_store.py`, `estimate_batch.py`, `src/common/student_t.py` for `predictive_t`).

## Pre-Rulings
- decision:held-out-not-in-sample — Acceptance gate 1 is **held-out reconciliation** (fit G on a subset of drivers/laps, score on the DISJOINT remainder). In-sample self-scoring is explicitly REJECTED (two free fit surfaces make near-arbitrary G improve in-sample error). This is GATING.
  @grade: settled/human · leans acceptance
- decision:synthetic-identifiability — Acceptance gate 2 is a synthetic-recovery test: inject a known curve + known session offsets into simulated pace; the fit must recover them **separably** (curve initial value vs offset are aliased in principle; if not separable, σ(G) is structurally understated downstream). GATING.
  @grade: settled/human · leans acceptance
- decision:no-baked-normality — Student-t / heavy-tailed residuals wherever feasible (project standing principle).
  @grade: settled/human
- decision:thin-session-explicit — you MUST decide explicitly what G does with a session too thin to fit (#560: thin fits currently pass acceptance with no minimum-flying-laps floor; the powered F10 run surfaced real sessions with no usable flying laps for back-of-grid cars). Do not let a thin session through silently. Choose a rule (skip / wide-σ fallback / floor) and record it; if the choice has epic-wide ramifications beyond G, float it.
  @grade: guess · leans acceptance · settle: inspect 2023 thin-session incidence, pick the rule that fails visibly
- decision:no-grip-into-segmentmap — G owns grip; nothing writes grip state into SegmentMap (#661). Grip mutates session-by-session; the map versions weekend-by-weekend.
  @grade: settled/human

## Honest-Null Clause
A measured negative is a complete, successful deliverable (owner no-kill ruling). If held-out reconciliation does NOT improve, or synthetic recovery does NOT separate, that is a real, reportable result — report it with full rigor and its scope (what was tested, what was not), do not paper over it.

## Inherited Latitude
Exercise (logged in return): bounded fix-now triage in scope, debt-issue proposals, the thin-session rule choice (float only if epic-wide), your own fit/test decisions. **Float to Admiral:** scope changes, data↔physics↔evo boundary decisions, a thin-session rule with ramifications beyond G. Merge is the Admiral's. Model tier: **Sonnet**.

## File Ownership
Working-notes: `.agent-work/epic-659/notes-663.md` (sole writer; not `findings-*`). Do NOT commit any `.agent-work/` path on the mission branch — return lessons-delta + feedback in closeout; Admiral applies centrally.

## Workspace
Worktree: **`C:/Programs/f1brainz-wt/epic659-663`** · branch `epic659/663-grip-g` · base `f404d2cb` (current local main, 7 ahead of origin — correct).
Created with: `git worktree add C:/Programs/f1brainz-wt/epic659-663 -b epic659/663-grip-g f404d2cb`
**First step:** `py C:/Users/fredc/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here C:/Programs/f1brainz-wt/epic659-663` → exit 0, paste output. PR integration = server-side merge (do not local-merge).

## Inherited Context (lessons + invariants — paste, not pointer)
- **Python is `py`**; tests `py -m pytest tests/...`.
- **LOO discipline (directly relevant to your gates):** any residual/calibration/stability diagnostic over a self-weighted or smoothing predictor MUST use leave-one-out / out-of-sample prediction — a self-inclusive form is structurally blind to the σ-too-small failure it exists to detect. Your held-out gate is exactly this discipline; apply it to the TARGET too (a truth channel from the same signal family yields spuriously high pass — gate P≥0.95-means-leakage). Verify the truth OLS is full-rank; within-stint fixed-effects + tyre_life are collinear (lap_number = offset + tyre_life within a stint) — use driver/race fixed-effects for the fuel term.
- **Editable-install .pth worktree trap (critical):** bespoke scripts run from a worktree import the MAIN repo `src/`, not the worktree's — put worktree `src/` first on `sys.path` in any ad-hoc script, or prefer pytest (safe).
- **Crews are Agent-tool subagents** (no `claude --role` binary) — dispatch via Agent tool, record via `run_crew.py` pure registry fns, `recover_crews` first.
- **Never idle on one long watcher** (harness-reaped) — bounded in-turn polls or `Start-Process -WindowStyle Hidden`; liveness via PowerShell `Get-Process` CPU. Deliver artifact + post verdict before idling.
- **`py -m src.utils.simplification_limits`** on touched paths (strict) before done.
- **DB-only analysis** — no live FastF1/Jolpica; SQLite is the single source.
- **#650 thread-cap tax:** the blanket physics thread cap roughly doubles fit wall-time — know this before any long fit; keep runs bounded/detached.

## Data Locations (untracked — NOT in your worktree)
- 2023 DB: `C:/Programs/f1Brainz/data/f1_data_2023.db` (16MB, main checkout only) — your real field-pooled pace source. Merged default `C:/Programs/f1Brainz/data/f1_data.db` is the fixed small default; pass the per-year 2023 path explicitly.
- Seams: `src/physics/layer2/tyre_supplant.py` (compound/tyre-age/fuel correction), `estimate_store.py`/`estimate_batch.py` (the pattern to follow), `src/common/student_t.py` (`predictive_t`).

## Budget
- **Model tier: Sonnet.**
- Compute/time: a real field-pooled fit over 2023 sessions can be non-trivial (see #650 thread cap). Bound it; if a full-season fit is needed for the held-out gate, run it detached (`Start-Process -WindowStyle Hidden`) with a state note, and poll — do NOT idle on it. A held-out gate on a representative slice of sessions is acceptable evidence if a full-season fit is prohibitively long; state the scope.

## Stop Conditions
Stop and return when: scope exceeded; a decision outside latitude is needed (esp. a thin-session rule with ramifications beyond G); a gate is un-runnable with available data; or you need context this order doesn't cover. Return-and-query the Admiral. Asking up is always sanctioned.

## Return Shape
Verdict (built+gates-pass / built+measured-null / blocked) + evidence (held-out reconciliation numbers on the disjoint remainder; synthetic-recovery separability result; the thin-session rule chosen + its 2023 incidence) + `simplification_limits` result + map impact + triage candidates (debt proposals incl. any #560 follow-on) + workflow-feedback + `verify_worktree_isolation.py --here` matched path. Open the PR (`gh pr create -F <tempfile>`, never a heredoc body on Windows), post the verdict; Admiral gates+reviews+merges. Return thin, write fat (`notes-663.md`). Deliver artifact + post verdict before idling.

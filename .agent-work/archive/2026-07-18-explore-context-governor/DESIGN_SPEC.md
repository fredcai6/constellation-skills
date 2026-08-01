# Design Spec — Context Governor

_Confirmed by the human. Ready to route/cut. Review complete (all findings dispositioned) and the Confirmation block below is signed._

## Confirmation

- **Status: CONFIRMED**
- Confirmed by: Fred
- Date: 2026-07-18
- Critic findings dispositioned: YES — all 38 (7 REJECT, 31 EDIT) carry a Disposition + Reason
- Assumptions exercised: agents can't reliably self-measure context fill (verified); the harness hook levers exist — `transcript_path` read, `additionalContext`, `PostToolUse decision:block`, `PreCompact` (verified); per-harness self-refresh capability (X3: Claude Code/Codex CANNOT, pi structurally can); existing engine state already carries most of a cold-start at every tier (X1, from doctrine/templates); prior art / Pocock reference-don't-duplicate + structured-beats-naive (X2).
- Assumptions accepted untested (human-signed): agents will heed the SOFT prompt often enough to matter — measure ignore-rate next; the transcript-parsed fill estimate is accurate enough at governor thresholds — never tested against real token accounting; the mid-gate runaway won't bite — gate-boundary checks only, accepted limit; net benefit exceeds cost — not mechanically measurable, human culls from real use; the Claude Code hook can reliably write the gauge — confirmed buildable (X2), not yet built/run; symmetric crash/refresh recovery works end-to-end — designed, not drilled.

> To confirm: delete the loud marker line, set Status to CONFIRMED, fill Confirmed by and Date, record the assumptions lines, ensure no Disposition cell is empty.

## Intent

Constellation agents cannot reliably sense their own context fill — self-report is confabulation — and the host harness only intervenes at ~90% with a lossy emergency auto-compaction. The governor gives the fleet a **proactive, portable way to hand off cleanly at a good work seam** before that point: a long-running agent, told by the engine that it is near-full, judges whether now is a good stopping point (biased toward yes) and hands off up its delegation chain to be re-instantiated fresh — carrying its reasoning, not just its mechanical state.

"Done" feels like: an agent finishing a unit of work is told "you've used most of your context"; unless it is basically finished it hands off at that seam; its invoker (Commander → implementer/reviewer; Admiral → Commander; human at the top) starts a fresh agent from a handoff rich enough for a clean cold start, and the fresh agent resumes **without re-deriving the why**.

The load-bearing reframe: the handoff is a **byproduct of continuous why-logging**, not a special artifact generated under duress. So the same mechanism that enables intentional refresh also makes ordinary crash-recovery cheap — the design pays for itself even where the gauge is crude or a harness can't refresh well.

**Kill condition:** if a clean handoff+refresh loses more effective continuity than auto-compaction preserves — i.e. the cold-start block can never be made good enough and every refresh is a productivity cliff — the governor is pointless.

## Exploration record (digest)

- **Cycles run:** shotgun (32 ideas across 8 axes) → refine. Full trail in `IDEAS_BOARD.md` / `cycle-1.json` / `cycle-2.json`.
- **Excursion answers:**
  - **X1 (handoff inventory):** cold-start is *mostly free* from existing engine state at every tier; the only new payload owed is three things — in-flight reasoning, a running "current understanding" digest, and a *voluntary refresh-seam* shape (which exists nowhere today; all machinery is for normal advance or crash recovery). Scoped null: no live crash-resume drill executed; inferred from doctrine/template text.
  - **X2 (prior art):** Pocock's handoff skill is manual-invoke, no gauge/trigger, key discipline = *reference artifacts, don't duplicate*. The gauge + structured-payload + self-trigger *combination* is open space. Structured payload beats naive "just summarize" (arXiv, UC Berkeley). Anthropic's own recommended path is server-side reactive compaction = the "summarized under duress" mode we avoid. Scoped nulls: `context-budget` skill not located; several framework specifics secondary-source only.
  - **X3 (self-refresh capability):** Claude Code CANNOT self-refresh; Codex CLI CANNOT; pi.dev structurally CAN (open loop primitives — `terminate` + `newSession` — but build-it-yourself, not shipped). Reach-up works on all three; self-refresh is a pi-only bonus. Claude-subscription billing constraint on pi confirmed. Scoped nulls: no harness driven live; pi loop arch from a secondary summary.
- **Rejected / parked approaches:** self-calibrating fill estimate, watcher-sidecar agent, agent self-`/compact`, context-bankruptcy breaker, fractional handoff, model-downshift-on-refresh (all parked with reasons on the board). **Engine-computed `fill × gates-remaining`** dropped — gate-count is a bad proxy for remaining effort.
- **Open threads carried:** precise threshold numbers; per-tier exempt-gate lists; gauge adapters for non-Claude-Code harnesses (unbuilt); whether the two-band trip needs a separate handoff-cost guard against over-fragmentation (judged safe because the question only fires at high fill).

## Chosen design

Four modules. The first three are load-bearing interfaces and are marked for **design-it-twice** (pending — see below). Interfaces described in deep-module terms.

### 1. Why-capture — an engine schema extension  *(load-bearing — design-it-twice DONE, approved)*

- **Interface (resolved):** enforcement rides **`advance` only** (the once-per-gate call that already refuses on unmet postconditions) — *not* `attach`, which the panel unanimously found is internal bookkeeping (auto-attached command output, waivers, from-child evidence), not an agent checkpoint. On a non-exempt `advance`, the engine solicits a structured *why* with three parts — `why_done` / `now_understand` / `next`. The **prompt is mandatory; the content is optional**: an explicit **`mechanical` marker** (a distinct flag/tag, *not* a magic string in a text field — avoids collision with a real answer that uses the word "mechanical") is first-class and valid. Ergonomic common path: a one-token `--why mechanical` discharges the whole prompt, and any single granular flag backfills the rest. Silence is refused.
- **Storage:** a dedicated top-level **`why_trail`** (append-only, sibling to `blockers`/`triage_candidates`), *not* the evidence list. The Refresh module reads it directly.
- **Exemption:** `why_exempt` per-task, set at **template-authoring time**. **Default = NOT exempt (opt-out)** — matching intent ("capture unless marked mechanical"). Rollout ships with a **one-time migration pass** that marks existing legacy gates exempt, so no shipped spine breaks on day one while new/edited gates get capture. *(Human decision — opt-out-with-migration over opt-in.)*
- **Invariants:** every non-exempt `advance` carries a why-record (real or explicit-`mechanical`); the **live digest = the latest non-superseded `now_understand`**, surfaced on `current` as a `DIGEST:` line (no new verb); a `reopen` freshens the digest (stale understanding on a redone gate stops being "latest"); the trail is append-only history; the why **references** task-state for the *what*, never duplicates it (this half is prompt-upheld, not engine-enforceable — flagged honestly).
- **Error modes:** a non-exempt `advance` with no why-answer is *refused* (engine-enforced, not agent discipline — the deliberate fix for the "state-note currency is discipline, not invariant" rot X1 found); postconditions are checked *before* the why (no buying past unfinished work).
- **Design-it-twice record:** 3 candidates — A minimal-interface / B common-caller-first / C ports-and-adapters. **Chosen: a hybrid** — B's shape (dedicated `why_trail`, advance-only enforcement, one-token common path) + C's collision-safe `mechanical` marker + A's minimalism (no new verbs, one-screen diff, inline enforcement). **Ports rejected here** (C's own verdict: one-adapter hypothetical seam = speculative generality) — banked for the Gauge interface, which has real adapter plurality. Compared on depth/locality/seam/testability; full designs in `dit-why-{A,B,C}*.md`.
- **Posture:** experimental v1 — ship the minimal version and learn from real use (human steer: "try stuff and see what happens").

### 2. Gauge — a harness-sensing writer + a local file the engine reads  *(load-bearing — design-it-twice DONE, approved)*

- **Interface (resolved):** a harness-specific writer emits a small **JSON record** to a session-scoped file on every tool call; the engine reads it at each gate. **The file format is the portability seam** (not a Python interface) — writers are swappable per harness, the reader never branches on which harness wrote it.
- **File record (converged across all 3 candidates):** `{ schema_version, fill_fraction (0..1), window (int), model, source, observed_at (ISO-8601, the sampled moment) }`. The engine owns the model-keyed threshold table centrally (writer emits fill+window+model; engine keys policy). **No extensibility scaffolding in v1** — `schema_version` is the only future hook; C's `signals`/`ext`/`confidence`/`raw` are dropped as YAGNI (the multi-harness plurality that would justify them isn't confirmed — see portability note). *(Human steer: minimal now, "it'll fix itself" when a real Codex situation arrives.)*
- **Staleness:** from the embedded `observed_at` (survives copy/sync/clock-skew), not file mtime; `now - observed_at > max_age` → no reading. `max_age` is engine config.
- **Path:** `.agent-work/<work_id>/gauge.json`, sibling to `spine.json`, reusing the hook rail's existing session→spine binding — session-scoped so parallel runs/worktrees don't collide.
- **Read side:** a thin injectable reader returning `Reading | None` that **never raises** — every failure (absent, corrupt, malformed, stale, clock-skew) collapses to the single `None` (borrowed from B; the injectable form gives filesystem/clock-free Trip tests). The full Protocol + NoOp/multi-adapter ceremony (B) is optional polish, not required for v1.
- **Invariants:** freshest-write-wins (atomic tmp+rename write); a `Reading` that reaches Trip is fresh + well-formed by construction (staleness resolved in the reader, so Trip structurally cannot force on stale data); **missing/stale = no reading** → no advice, never a forced handoff; writer never fabricates a placeholder (skip-on-uncertainty, let the file age into staleness); the agent never reads the file; `source` is diagnostic-only, Trip never branches on it.
- **Portability (v1 scope, honest):** only the **Claude Code** writer is confirmed buildable today (X2 transcript-parse technique). Codex has no confirmed per-tool-call hook surface; pi's per-tool-call cadence is unconfirmed. **v1 gauge is Claude-Code-only**; the harness-agnostic file format keeps Codex/pi open as later additions. *Reach-up refresh stays fully portable — only the gauge sensing is Claude-Code-first.* *(Human accepted.)*
- **Design-it-twice record:** 3 candidates — A minimal (bare float) / B ports-and-adapters / C extensible-envelope. **Chosen: the converged core** — B/C's agreed 5-field record + B's None-collapsing injectable reader + A's testability discipline, minus C's extensibility scaffolding. B's key finding banked: read-side plurality is always 2 adapters (the file format already IS the seam), and the real one-adapter risk is relocated to the write side (only Claude Code confirmed). Full designs in `dit-gauge-{A,B,C}*.md`.

### 3. Trip — the two-band policy the engine applies at the gate  *(load-bearing → design-it-twice)*

- **Interface:** at each gate the engine reads the gauge-file and applies model-keyed thresholds.
  - **SOFT band (primary):** at fill ≥ soft, the engine's gate response carries a **stop-by-default question** — *"you've used most of your context; unless you're basically done, hand off here at this seam."* The agent supplies the **stop-point judgment** (seam quality — a thing agents *can* do); the engine supplied the **fill fact** (the thing agents *can't* self-measure). Advisory: the agent may decline with a reason ("one more step and I'm clear").
  - **HARD band (backstop):** at fill ≥ hard, the engine **refuses to advance** until a handoff is produced / refresh requested. Rarely fires (we are structurally not hitting auto-compacts today).
- **Invariants:** the question only appears at high fill (so "bias toward stop" cannot cause premature fragmentation); SOFT never forces; HARD always forces; the agent never introspects fill. Govern and prevent are the *same* mechanism here — an agent asked "good place to stop?" while full naturally won't dive into the next big chunk.

### 4. Refresh — reach-up handoff and re-instantiation  *(load-bearing — design-it-twice DONE, approved)*

- **Foundational principle (human, decisive):** engine work files (`spine.json`, the plan, `why_trail`) are **job-scoped, not agent-scoped** — a durable record of what it took to get the thing done, which any number of agents may touch in sequence. A relaunched agent **reuses the same file**. Agents are ephemeral; the job file persists; **refresh = swap the agent, keep the file.** (This also grounds Module 1's append-only `why_trail` across agent changes.)
- **Interface (resolved — one uniform mechanism at every tier):** on a soft-accepted or hard-forced trip, the agent writes a **`refresh-request`** into its own engine work file (an evidence item via existing `attach`; payload = pointers: `seam` = active gate id, `why_ref` = latest why record — never copies), then goes idle. The **invoker sees it via `current`** when it inspects the invokee's engine state to adjudicate — *the same read at every tier, because every tier drives the engine* (Commander reads a crew's plan; Admiral reads a Commander's spine; human reads the top agent's `current`/report). The invoker relaunches a **fresh** agent, which cold-starts from `current` alone (`DIGEST:` + `ACTIVE` imperative) reusing the same job file — no heavyweight handoff document.
- **Cold-start payload = `current` itself:** `DIGEST:` (latest `now_understand`) + `ACTIVE <gate> — <imperative>`. The engine state IS the handoff (X1). No `REFRESH_HANDOFF.md` document (design A's 12-header template rejected as verbose — mostly "unchanged, see original").
- **Trip HARD-band integration:** a pure predicate `has_pending_refresh_request(cl, gate)` — Trip's HARD band refuses to advance until a `refresh-request` exists, pointing the agent at the one `attach` command. One boolean, no shared mutable state.
- **Crew-edge extra robustness (optional, crew-tier only):** at Commander→crew, the refreshing crew may *also* withhold its result artifact + echo a `REFRESH_REQUESTED:` marker in its report, so the existing `crew-runs.json` classifier flags it resumable and the existing `--abandon --relaunch` fork relaunches fresh — mechanical belt-and-suspenders where that registry already exists. Not the primary path; the engine artifact is.
- **Invariants:** **symmetric recovery** — intentional refresh and crash resume from the identical `current` read (crash = the optional `refresh-request` line simply absent, fall back to today's cold-start); the handoff never re-serializes engine state (pointers only); the checklist path is not carried (the invoker is always the prior dispatcher for reach-up); reach-up terminates at the human. **Self-refresh** (agent re-instantiates itself) is an optional **pi-only** adapter at the same seam — later bonus.
- **Design-it-twice record:** 2 candidates — A common-caller-first (reuse existing machinery) / B minimal-interface. **Chosen: B's uniform engine-native signal as the core** (`refresh-request` evidence + `current` line + Trip predicate), with A's crew-registry trick kept as optional crew-tier robustness. Human correction folded in: A's "three per-edge mechanisms / chokepoint-less Admiral edge" was a crew-registry-centric over-complication — the engine is the uniform substrate at every tier, so the mechanism is one, not three. Full designs in `dit-refresh-{A,B}*.md`.

- **Per-section approval:** Module 1 (Why-capture) — **APPROVED by Fred** (hybrid + opt-out-with-migration). Module 2 (Gauge) — **APPROVED by Fred** (converged 5-field record, minimal, Claude-Code-only v1). Module 3 (Trip) — **APPROVED** (folded into the engine; no seam of its own — stated-reason skip of a panel). Module 4 (Refresh) — **APPROVED by Fred** (uniform engine-native `refresh-request`; job-file-not-agent-file principle; A's chokepoint-less-Admiral framing corrected). **All four modules approved.**

## Testing pathways

- **Why-capture:** unit-drive the engine — a non-exempt advance with no why is refused; an exempt gate does not prompt; the latest `now_understand` is retrievable as the digest. Falsifiable: can a non-exempt gate pass with no why? (must fail).
- **Gauge:** test the fail-safe — missing/stale file → no advice, never a forced handoff. Test the Claude Code adapter actually writes fill on a tool call. Falsifiable: does a stale file ever force a handoff? (must not).
- **Trip:** soft question fires at/above soft threshold and never below; hard refuses advance at/above hard. Falsifiable: does soft ever force, or hard ever let you pass? (must not).
- **Refresh:** end-to-end drill — a near-full agent hands off, invoker re-instantiates, the fresh agent resumes from the handoff and completes **without re-deriving the why**. Falsifiable: must the fresh agent reconstruct reasoning the trail already holds? (must not). **Deferred:** live multi-harness test — Claude Code adapter first; Codex/pi adapters later.

## Out of scope

- Upstream issue-sizing as a *separate* prevention strategy (prevention is folded into the soft question).
- Self-refresh *implementation* on pi.dev (the design leaves the seam; building the adapter is a later bonus).
- Parked ideas: self-calibrating estimate, watcher-sidecar, fractional handoff, model-downshift-on-refresh.
- Final threshold numbers and per-tier exempt-gate lists (the spec sets the *mechanism*; tuning is first-run calibration / a follow-up).

## Critic findings and dispositions

<Filled at the review step. Columns are contractual — do not rename.>

| ID | Lens | Severity | Finding | Disposition | Reason |
|---|---|---|---|---|---|
| IF1 | intent-fit | BLOCKING | Trip checks the gauge only at `advance`; a single long gate can blow past HARD before the next check. No mid-gate re-check. | REJECT | Gate-boundary IS the intended design; mid-gate handoff is unnecessarily ugly. Gates built well, lots of headroom, not an observed problem. Accept the limit; a lesson for later if it bites. (Human.) |
| IF2 | intent-fit | BLOCKING | "Biased toward yes" is only prompt wording; agent can decline SOFT free, no escalation/tracking. | REJECT | Accepted for v1 — the goal is an escape hatch, not perfection. Measure how often agents ignore it next. (Human.) |
| IF3 | intent-fit | BLOCKING | Refresh reads only `now_understand`; `why_done`/`next` wired to nothing. | EDIT | Collapse the three-part why to a single `why` field; drop `next` (already in the machinery) and `why_done`. (Human.) |
| IF4 | intent-fit | MAJOR | Digest can be stale after a run of `mechanical` advances. | REJECT | Accepted for v1; single `why` is the running understanding. Measure in use; cull if it bites. (Human posture.) |
| IF5 | intent-fit | MAJOR | "Fleet" framing oversells a Claude-Code-only trigger. | EDIT | Tighten Intent to own Claude-Code-only v1; trigger is CC-first, reach-up stays portable. |
| IF6 | intent-fit | MAJOR | Kill condition never operationalized. | EDIT | Reframe: NOT a mechanical kill switch. Experimental v1, culled by human judgment from use. (Human: "can't be measured, not a kill-switchable concept.") |
| IF7 | intent-fit | MINOR | Tension: HARD "rarely fires" vs Intent citing auto-compaction as live pain. | EDIT | Reframe as a pre-emptive escape hatch / future-risk hedge; measurement next. |
| IF8 | intent-fit | MINOR | "Pays for itself on crash recovery" asserted, not shown. | EDIT | Soften to a hypothesis to evaluate in use. |
| TF1 | testability | BLOCKING | Kill condition has no test/measurement plan. | EDIT | Drop the kill-condition-as-test framing; human evaluates from use (same as IF6). (Human.) |
| TF2 | testability | BLOCKING | SOFT judgment quality has no test surface. | REJECT | Accepted — judgment quality is observed via ignore/decline rate in use, not a unit test. Consistent with IF2. (Human.) |
| TF3 | testability | MAJOR | Migration pass untested. | EDIT | Moot — migration pass dropped (SF6). |
| TF4 | testability | MAJOR | Refresh "must not re-derive" needs an unnamed judge/rubric. | EDIT | Name it a qualitative judge in Testing, not a unit test. |
| TF5 | testability | MAJOR | Symmetric recovery never tested against itself. | EDIT | Add a crash-path vs refresh-path convergence test. |
| TF6 | testability | MAJOR | Threshold test can't run — numbers deferred; caveat absent. | EDIT | Note: only structural testing until first-run calibration sets numbers. |
| TF7 | testability | MAJOR | "Agent never reads the file" — no enforcement, no test. | EDIT | Downgrade to a stated convention, not an enforced invariant; note honestly. |
| TF8 | testability | MAJOR | Gauge 5-failure-modes → None, only 2 tested. | EDIT | Add corrupt/malformed/clock-skew to the reader test list. |
| TF9 | testability | MINOR | Atomic write has no torn-read test. | EDIT | Add a concurrency/torn-read test. |
| TF10 | testability | MAJOR | CC writer format drift undetected. | EDIT | Add a golden-sample fixture + format-drift note for the CC writer. |
| TF11 | testability | MINOR | Portability seam unverified with one writer. | EDIT | Acknowledge honestly: seam unverified in a one-writer v1. |
| TF12 | testability | MINOR | "reopen freshens digest" untested. | EDIT | Add a reopen-freshens-digest test. |
| TF13 | testability | MINOR | Crew-edge path untested. | EDIT | Moot — crew-edge extra robustness cut (SF4). |
| TF14 | testability | MINOR | No fallback/test for an unknown `model`. | EDIT | Define fallback: unknown model → default (soft,hard) pair; add a test. |
| TF15 | testability | MINOR | SOFT-decline reason has no validation rule. | EDIT | v1 accepts any decline reason; not policing reason quality — note it. |
| TF16 | testability | MINOR | "never duplicates" prompt-upheld/unfalsifiable. | EDIT | Acknowledge as prompt-upheld; no lint in v1. Shrinks with single-field collapse. |
| SF1 | simplicity | MAJOR | `why_done` invites duplication, no consumer. | EDIT | Dropped — collapse to a single `why` field. |
| SF2 | simplicity | MAJOR | `next` captured, never read. | EDIT | Dropped — `next` is already in the machinery. (Human.) |
| SF3 | simplicity | MAJOR | Gauge `schema_version` versions a v2 that doesn't exist. | REJECT | Keep — the one deliberate future hook; one field. (Human's prior call stands.) |
| SF4 | simplicity | BLOCKING | Crew-edge extra-robustness duplicates the primary path. | EDIT | Cut from v1 — `refresh-request` + `current` covers crew tier end-to-end. |
| SF5 | simplicity | MAJOR | HARD justified only as "rarely fires." | REJECT | Keep HARD as a safety net — unproven but wanted, TBD. (Human.) |
| SF6 | simplicity | MAJOR | Migration pass unneeded. | EDIT | Drop it — opt-out, legacy gates absorb the one-token prompt on first use. (Human.) |
| SF7 | simplicity | MINOR | pi-self-refresh narrated despite out-of-scope. | EDIT | Drop the pi self-refresh sentence until pi work is real. |
| SF8 | simplicity | MINOR | Model-keying generalizes for a plurality not in v1. | REJECT | Keep — cheap, lets the engine own the table centrally; a 2nd model is plausible. (Flagged to human for a possible single-global simplification.) |
| SF9 | simplicity | MINOR | `source` is diagnostic-only. | EDIT | Drop `source` from the gauge record — YAGNI. |
| SF10 | simplicity | MINOR | `window` redundant with normalized `fill_fraction`. | EDIT | Drop `window`; `fill_fraction` is already normalized. Keep `model` for keying. |
| SF11 | simplicity | MINOR | Dedicated `mechanical` tag marginal over a token convention. | EDIT | Simplify to an explicit `--mechanical` flag; drop elaborate tagging. |
| SF12 | simplicity | MINOR | Single-flag backfill unspecified. | EDIT | Moot — single `why` field, no backfill. |
| SF13 | simplicity | MINOR | Reader Protocol/NoOp ceremony not excluded. | EDIT | Cut it — plain function returning `Reading \| None` for v1. |
| SF14 | simplicity | MAJOR | Only `now_understand` has a consumer. | EDIT | Collapse to a single `why` field — done. (Human.) |

## Post-review amendments (authoritative — supersede the module bodies above where they differ)

The critic panel's dispositions amend the Chosen-design modules as follows. Where a module body above still describes the pre-review shape, **this list governs.**

- **Module 1 (Why-capture):** the three-part why (`why_done`/`now_understand`/`next`) **collapses to a single `why` field** (the running understanding). `--mechanical` is a plain flag. **No migration pass** — opt-out; legacy gates absorb the one-token prompt on first use.
- **Module 2 (Gauge):** the record trims to **`{schema_version, fill_fraction, model, observed_at}`** — drop `source` (SF9) and `window` (SF10, `fill_fraction` is already normalized). Keep `schema_version` (one future hook) and `model` (threshold keying). The read side is a **plain function `read() -> Reading | None`** — the Protocol/NoOp/multi-adapter ceremony is cut from v1 (SF13). Unknown `model` → default `(soft,hard)` pair (TF14). **Model-keying kept** (human confirmed SF8 — model-keyed thresholds, engine owns the table).
- **Module 3 (Trip):** **both bands kept** (HARD as an unproven-but-wanted safety net — SF5). **Checks at gate boundaries only** — the mid-gate runaway (IF1) is an **accepted limit**, not fixed (mid-gate handoff is deliberately avoided as ugly; gates are built well). "Bias toward stop" **is** just the prompt (IF2, accepted for v1) — decline/ignore rate is a **measurement target**, not a mechanism.
- **Module 4 (Refresh):** the **crew-edge extra robustness is cut** (SF4) — the engine `refresh-request` + `current` read covers crew tier end-to-end. The **pi-only self-refresh narration is dropped** (SF7) until pi work is real (reach-up already covers pi).
- **Framing (Intent/Testing):** the **"kill condition" is not a mechanical test** — reframed as experimental; the human culls from real use, not a continuity benchmark (IF6/TF1). Own **Claude-Code-only v1** honestly (IF5). Several claims softened to hypotheses-to-measure (IF7/IF8). Testing pathways gains the missing tests (TF4–TF12, TF14) as EDITs; the SOFT-judgment and refresh-"didn't re-derive" checks are **qualitative judges, not unit tests**.

**Deferred future work (human-flagged, not v1):** pre-emptive handoff at *specific named gates* (e.g. a Commander after planning its exec gates, before exec kicks off) — a scoped, opt-in variant of the seam trigger; organic for now.

**Overall posture:** experimental v1, shipped minimal, evaluated by the human's judgment in real use and culled from experience — not aiming for perfect.

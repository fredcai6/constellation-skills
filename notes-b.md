# notes-b — lane B, context identity (#600, #500)

Working notes for `cleanup/b-context-identity`, base `a69bbac4`. Sole writer this wave.

## 1. The measurement, first

The launch order's first task is a measurement, not a change: at the instant of a
trip, whose reading does the re-created `gauge.json` carry? Two candidates were
offered.

- **Candidate 1** — the write is skipped on an ambiguous or unresolvable binding,
  and the stale file survives.
- **Candidate 2** — another agent's key resolves into the same directory and
  writes its own fill.

### 1a. T0 capture — this Commander's own live state

Captured at `2026-08-16T12:34:55Z`, worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity`.
Raw copies under `.agent-work/cleanup-b-context-identity/measurement/`.

`gauge.json`:

```json
{"schema_version": 1, "fill_fraction": 0.142511, "model": "claude-opus-5", "observed_at": "2026-08-16T12:34:05.201Z"}
```

`.agent-work/.spine-rail-binding.json` (worktree copy — one key, one binding):

```
KEY 2271de9b-5c66-4105-9975-166cf4d57b01
  .../.agent-work/cleanup-b-context-identity/spine.json
    engine_session = commander-cleanup-b-context-identity
    worktree       = .../.worktrees/cleanup-b-context-identity
    claimed_at     = 2026-08-16T12:32:23.896279+00:00
    path_source    = payload_cwd
```

Four facts this pins down, each read off the artifacts rather than assumed:

1. **The key is bare** — no `#agent_id`. This Commander is a top-level agent, and
   its record carries exactly the four required fields (no
   `identity_resolution_ms`), which is the record shape `docs/GAUGE_WRITER_HOOK.md`
   says a top-level agent produces. The two agree.
2. **The write landed in the worktree, not the main checkout.** `path_source` is
   `payload_cwd`, and `CLAUDE_PROJECT_DIR` is unset in this session, so
   `resolve_project_dir()` fell through to the cwd, which is the worktree. The
   launch order's #269 warning (`CLAUDE_PROJECT_DIR` fixed at session launch,
   worktree runs the main checkout's hook against the main checkout's state) did
   **not** bite here, because the variable was never set at all. That is a
   different world from the one the order describes, and it matters for how the
   fix gets validated — see §4.
3. **The reading is genuinely mine.** `observed_at` 12:34:05Z is after
   `claimed_at` 12:32:23Z, so `_reading_predates_claim` is False and #477's guard
   correctly does not fire. No inheritance, no misattribution.
4. **The main checkout's binding store holds 19 keys and none of them resolves
   into this work directory.** So no cross-checkout collision is live right now.

### 1b. Living inside the bug — the trip fired on me, correctly

At 12:35:51Z, `current` returned:

```
CONTEXT 15% (>= hard): your instruction has changed. You have taken this as far
as this context can carry it — now close THIS gate carrying your handoff ...
```

with `gauge.json` at `fill_fraction 0.153677`, `observed_at 2026-08-16T12:34:55Z`.

**This is not the defect.** It is a real own-reading crossing a real line: 153,677
absolute tokens against a 150,000 hard cap on `claude-opus-5`. It took roughly
fifteen turns and five file reads — `checklist_engine.py` (3551 lines),
`gauge_writer_hook.py` (709), `gauge_reader.py` (519), `docs/GAUGE_WRITER_HOOK.md`
(658), plus doctrine. A design wave whose whole subject matter is these files
cannot read them and stay under the cap. Recorded here as lived evidence, per the
launch order's request, not as a complaint and not as a defect claim.

Per the launch order ("arriving over the context HARD band is not a stop
condition"), the legal sequence was followed: `attach understand --type
refresh-request --field seam=understand --field why_ref=w-2`, then continue.

### 1c. What the code says, and why it points at candidate 2

Read from `scripts/hooks/gauge_writer_hook.py` at `a69bbac4`:

- `resolve_gauge_path(project_dir, binding_key)` (`:233`) enumerates candidates
  for **one binding key only** — `binding.get(binding_key)`.
- The ambiguity guard in `handle_post_tool_use` (`:609`) is
  `if len(gauge_paths) > 1`. It is therefore a **within-key** guard.
- **Nothing in the module compares across keys.** Two *distinct* keys whose bound
  spine files sit in the *same* directory each resolve to exactly one candidate,
  each takes the clean single-candidate branch at `:672`, and each does
  `_atomic_write_json(gauge_path, record)` with its own transcript-derived fill.
  Last writer wins. The record carries no owner, and the filename carries no
  identity.

That is candidate 2, and it is unguarded by construction rather than by accident.
The everyday topology that produces it is an orchestrator holding the bare
`session_id` key while a dispatched agent holds `session_id#agent_id`, with both
bound to spine files under one `.agent-work/<work-id>/`.

**The decisive consequence, and the reason this is the residual #601 left behind:**
a cross-key foreign write is *fresh*. Its `observed_at` is ~now, comfortably after
the reader's `claimed_at`. So `_reading_predates_claim`
(`checklist_engine.py:1444`) returns False and the #477/#601 guard **cannot see
it**. The timestamp comparison only ever catches a reading that is *older* than
the claim — candidate 1's shape. It is structurally blind to candidate 2.

Candidate 1's own symptom, meanwhile, is now largely closed: #601 re-stamps
`claimed_at` on a re-claim, so a relaunched agent's inherited-stale reading is
declined, and a skip that leaves the file to age past 30 minutes collapses to
`None` in `gauge_reader.read()` — fail open, no trip.

**Working hypothesis, taken to the probe rather than shipped on this reasoning
alone:** the surviving mechanism by which an agent trips on a number it did not
produce is candidate 2 — a cross-key write into a shared work directory — and it
is invisible to the guard that exists.

## 2. The probe — CANDIDATE 2 CONFIRMED

`measurement/probe_cross_key.py` drives the **real** `handle_post_tool_use` in a
**fresh process**: a real binding store holding two *different* keys bound to two
spine files in one work directory, real transcript files, and the real payload
shapes the harness sends (a top-level payload omits `agent_id`; a dispatched one
carries it — pinned by `tests/fixtures/probe_payloads.jsonl`). Nothing patched.

Topology is the everyday one: an orchestrator on the bare `session_id` key holding
`spine.json`, and an agent it dispatched on `session_id#agent_id` holding
`execute.json`, both under one `.agent-work/W/`.

Output (`measurement/probe_cross_key.out`, 2026-08-16T12:38Z):

```
after DISPATCHED agent's call : {"fill_fraction": 0.02, ..., "identity_resolution_ms": 0.024}
after ORCHESTRATOR's call     : {"fill_fraction": 0.9,  ...}
gauge-skip.json               : (none)

VERDICT: CANDIDATE 2 CONFIRMED. The orchestrator's own fill (0.9) OVERWROTE the
dispatched agent's (0.02) at the same path. Two distinct keys, one gauge file,
no guard.

    dispatched agent claimed_at : 2026-08-16T12:37:27Z
    foreign reading observed_at : 2026-08-16T12:38:22Z
    observed_at > claimed_at    : True -> _reading_predates_claim is False
                                       -> #477/#601 guard does NOT fire
```

**Three things this settles.**

1. **Candidate 2 is the mechanism, and it is unguarded by construction.** Not a
   race, not a rare interleaving: each key resolves to exactly one candidate, so
   each takes the *clean* single-candidate branch. The ambiguity guard is doing
   its job correctly and is simply asking a different question.
2. **Nothing noticed.** No `gauge-skip.json` was written, because from each
   writer's point of view nothing went wrong. The subsystem's own visibility
   machinery — which exists precisely because a silent governor let #252 and #271
   survive — has no signal for this.
3. **The existing guard is structurally blind to it, and no amount of tightening
   the timestamps would help.** The foreign write is fresh. `#601`'s `claimed_at`
   re-stamp made the guard work for the case it was built for (an *inherited*,
   *older* reading); this case is the opposite shape.

Note also that the orchestrator's reading was sampled five seconds *earlier* than
the dispatched agent's and still clobbered it. There is no ordering check at all —
the writer atomically replaces whatever is there.

## 2b. The same mechanism, caught LIVE in production — on this run

The synthetic probe above is the controlled version. This is the uncontrolled one,
and it is the stronger artifact: **candidate 2 happened to this Commander, during
this wave, and was captured while it happened.**

At 12:46:54Z, `current` reported `CONTEXT 9%` when this session's own last genuine
reading had been 18–22%. The binding store
(`measurement/worktree-binding-at-T1.json`) explained it — **two different harness
keys, both bound to the same `spine.json`**:

```
KEY 2271de9b-5c66-4105-9975-166cf4d57b01   (this Commander)
    spine.json -> engine_session=commander-cleanup-b-context-identity
                  claimed_at=12:32:23  path_source=payload_cwd
KEY aaeefd73-5c9e-4a81-835e-c21d36e1ff3d   (the cold plan critic crew)
    spine.json -> engine_session=commander-cleanup-b-context-identity
                  claimed_at=12:43:10  path_source=None
```

Each key holds exactly **one** binding, so each takes the clean single-candidate
branch, no ambiguity flag is raised, and both write to the same
`.agent-work/cleanup-b-context-identity/gauge.json`.

`measurement/gauge-oscillation.log` samples that file every 3s for two minutes
**while this Commander made no tool calls of its own**:

```
12:47:17  fill 0.22082   observed_at 12:46:41.880Z   <- this Commander's own reading
12:47:23  fill 0.086878  observed_at 12:46:20.733Z   <- CLOBBERED by the critic crew
12:47:38  fill 0.094473  observed_at 12:47:35.726Z
12:47:50  fill 0.09516   observed_at 12:47:37.482Z
12:48:20  fill 0.095934  observed_at 12:47:49.606Z
12:48:23  fill 0.097187  observed_at 12:48:19.403Z
12:48:26  fill 0.099156  observed_at 12:48:22.825Z
```

The rising 8.7% → 9.9% series is the **critic's own context filling up as it
works**, written into this Commander's gauge file. Three things this adds beyond
the probe:

1. **A second entry route, which I had not enumerated.** The critic crew never
   claimed a spine — it was dispatched with `--handoff`/`--result`, no `--spine`.
   `spine_rail`'s `SessionStart` **bind-on-resume** (#261) bound its bare
   `session_id` to the single active-leased spine it found in the worktree: mine.
   Its binding's `path_source` is `None`, not `payload_cwd`, which is how you tell
   the two routes apart on disk. So the collision is **not** limited to an
   orchestrator and a subagent sharing a work directory. **Any** session that
   merely starts in a worktree holding one active-leased spine gets bound to it
   and begins writing its context fill into that spine's gauge.
2. **`observed_at` went backwards** — 12:46:41 replaced by 12:46:20, a sample 21
   seconds *older*. There is no ordering check anywhere on the write path; the
   writer atomically replaces whatever is there. So this is not even
   last-sample-wins, it is last-writer-wins.
3. **The governor was reporting the wrong agent's context to me for real.** I was
   told 9% while genuinely at ~22%. In this direction it under-reports and I lose
   protection. In the other direction — a busy orchestrator, or a crew with a
   large context — the subordinate is refused on turn one having done nothing,
   which is the 2026-08-15 failure the launch order opens with. **Both directions
   are the same defect**, and neither is visible: no `gauge-skip.json`, no
   advisory, nothing.

`_reading_predates_claim` cannot see any of it. Every one of those foreign writes
is fresh against my `claimed_at` of 12:32:23.

### What was NOT tested

Scoped, per `global-everyone.md` §scoped-nulls. The probe exercises the writer's
path resolution and write, in-process, with synthetic-but-real-shaped payloads. It
does **not** exercise: Claude Code actually invoking the hook as a `PostToolUse`
hook (that remains the standing HITL gap named in `docs/GAUGE_WRITER_HOOK.md`);
the `SessionStart` bind-on-resume writer; Windows; or any topology with three or
more keys. None of those is needed to establish the mechanism, and none is claimed.

## 3. Open, not settled

- Whether #549 (lane C) lands during this wave. If it does, §1 must be re-measured
  — it changes `session_view`'s per-agent merge, which is candidate 2's
  neighbourhood.

## 4. Validation constraint carried forward

`gauge_writer_hook.py` is hook code. Isolation is git-only, so a change to it
cannot be validated from inside the session that contains it. Validation must run
in a fresh process whose `CLAUDE_PROJECT_DIR` genuinely resolves to the worktree —
never a fixture that hand-injects the value being proven. Note from §1a fact 2
that in *this* session the variable is unset entirely, so the hook resolves the
project dir from cwd; a validation harness must not accidentally rely on that.

## 5. Map impact

`map/ids.jsonl` is **empty** and every `map/<module>/INDEX.md` target linked from
`map/INDEX.md` is **absent** (only `INDEX.md` and `ids.jsonl` exist under `map/`).
`map_orient.py orient` therefore returns `DEGRADED-UNPARSEABLE` with
`anchor_count: 0`. Discharged for this run with five hash-pinned substitutes;
filed as a triage candidate.

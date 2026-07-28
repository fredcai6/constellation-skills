# Gauge writer (#180) — wiring, transcript-format dependency, and the HITL seam

Module 2 (Gauge), write side, of the Context Governor v1 spec (epic #178).
Companion to #181's `scripts/gauge_reader.py` (read side, engine-owned). See
the epic body for the full confirmed DESIGN_SPEC; this doc only covers the
writer's wiring and its dependency on Claude Code's transcript format.

## What this hook does

`scripts/hooks/gauge_writer_hook.py` is a Claude Code `PostToolUse` hook. On
every tool call it:

1. Reads `transcript_path` and `session_id` from the hook's stdin JSON.
2. Resolves `.agent-work/<work_id>/gauge.json` by looking up `session_id` in
   `.agent-work/.spine-rail-binding.json` — the session→spine binding that
   `scripts/hooks/spine_rail.py`'s own `PostToolUse` and `SessionStart`
   handlers maintain (populated when `checklist_engine.py claim` runs, or
   when a session resumes/compacts onto an unambiguous single active-leased
   spine it did not itself claim — #261). This hook **reuses that binding,
   it does not maintain a second one.** Since #202, one `session_id` may
   legitimately hold bindings into more than one spine at once (e.g. an
   Agent-tool subagent sharing its parent's `session_id` claims its own
   spine without clobbering the parent's); when that happens, this hook
   writes to **none** of them rather than guessing — see "Skip-on-uncertainty,
   enumerated" below.
3. Parses the tail of the transcript (JSONL) for the latest non-sidechain
   assistant message's `usage` block, sums
   `input_tokens + cache_creation_input_tokens + cache_read_input_tokens`
   (the "X2 strategic-compact" technique), and normalizes by a per-model
   context-window table to get `fill_fraction`.
4. Atomically (tmp file + `os.replace`) writes the frozen 4-field record to
   `gauge.json`.

If any step is uncertain, it writes nothing and leaves the existing file to
age into staleness — see "Skip-on-uncertainty" below.

## The human action (HITL seam)

Everything above is built and tested. Three things need you:

### (a) The settings.json snippet

Add a **second** `PostToolUse` hook entry to your `~/.claude/settings.json`
(or this project's `.claude/settings.json` if you want it project-scoped —
your call). Do not replace the existing `spine_rail.py PostToolUse` entry;
add alongside it. Unlike `spine_rail.py`'s entry (matcher `"Bash"` only,
because it only cares about `checklist_engine.py` commands), the gauge
writer needs to see **every** tool call to track fill continuously, so its
matcher is `"*"`:

```json
{
  "hooks": {
    "PostToolUse": [
      {"matcher": "Bash", "hooks": [{"type": "command", "command": "py \"${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py\" PostToolUse", "timeout": 10}]},
      {"matcher": "*", "hooks": [{"type": "command", "command": "py \"${CLAUDE_PROJECT_DIR}/scripts/hooks/gauge_writer_hook.py\"", "timeout": 10}]}
    ]
  }
}
```

If your real `settings.json` already has other `PostToolUse` matchers
(unrelated hooks), add this as one more entry in that same array — don't
nest it inside an existing matcher block.

**Ordering note:** the gauge writer only produces a record once a binding
exists for the session, i.e. only after at least one `checklist_engine.py
claim` command has run and `spine_rail.py`'s handler has recorded it. If you
fire a tool call before any claim happens in a session (or in a session
with no spine at all — e.g. plain chat, no engine in use), the gauge writer
will see no binding and correctly write nothing. This is not a bug to fix;
a gauge file that no engine gate will ever read is not worth writing.

### (b) Confirm it on one real tool call

1. Make sure a spine is claimed in your current session (any normal
   Constellation run does this via `checklist_engine.py claim`).
2. Run any tool call (a `Bash` command, a file read, anything).
3. Look at `.agent-work/<your-work-id>/gauge.json` (sibling to that run's
   `spine.json`). It should now exist and contain something like:

   ```json
   {"schema_version": 1, "fill_fraction": 0.34, "model": "claude-opus-4-8", "observed_at": "2026-07-18T12:00:00.123Z"}
   ```

4. Run a few more tool calls and re-check the file. `observed_at` should
   advance and `fill_fraction` should trend upward as the session's context
   fills (it can also drop after a `/compact` or a fresh session — that's
   expected, not a bug).

### (c) What "looks right" means

- All four fields present, no extras.
- `fill_fraction` is a float in `[0, 1]` and its trend across several tool
  calls in the same session is monotonically non-decreasing *within* one
  continuous stretch of work (small jitter is fine; the fill isn't expected
  to be perfectly smooth). A value that stays flat at exactly the same
  number across many different-sized tool calls, or one that's wildly
  discontinuous run-to-run, is the sign the estimate isn't tracking real
  fill and should be floated back as a measured negative.
- `model` matches what you were actually talking to.
- `observed_at` is close to "now" (within the tool call you just ran) --
  it is the transcript's own sampled timestamp, not wall-clock-at-write, so
  it should never be far in the past.

This eyeball check is the one thing that could not be done AFK: it requires
your real `~/.claude/settings.json` and a live session, which is exactly the
HITL boundary this issue was scoped to stop at.

## Validated against a real transcript (not just the golden fixture)

The X2 technique's "confirmed buildable but never run against the real
harness" caveat from the DESIGN_SPEC no longer holds as stated. During
implementation this transcript-parsing logic was hand-verified (not just
unit-tested against the fixture) against this machine's own live, in-progress
Claude Code session transcript file
(`~/.claude/projects/<project-slug>/<session-id>.jsonl`):

- The real schema matched exactly what this hook depends on: top-level
  `{"type": "assistant", "isSidechain": false, "message": {"model": "...",
  "usage": {"input_tokens": ..., "cache_creation_input_tokens": ...,
  "cache_read_input_tokens": ...}}, "timestamp": "..."}`.
- Summing the three usage fields on the latest such line against a real
  104-turn, ~150k-token session produced a sane, monotonically-growing
  total across the session (e.g. one observed point: `1 + 3578 + 149372 =
  152951` tokens on `claude-opus-4-8`, i.e. `fill_fraction ≈ 0.76` against a
  200k window) -- consistent with the actual state of that conversation.

This is a positive, measured result, not a fabricated one: the technique
works against real Claude Code output as of transcript format `version:
"2.1.214"`. It has **not** been run through the actual `PostToolUse` hook
plumbing end-to-end (that requires the settings.json wiring above, hence
still HITL for the live-wiring half of this issue, per the acceptance
criteria) -- but the parsing/sum/normalize logic itself is no longer just
"confirmed buildable," it is confirmed correct against live data.

## The exact transcript shape this parser depends on (format-drift note)

This is the fragile, undocumented part -- Claude Code does not publish a
transcript schema, and issue #27969 (closed as duplicate; see #43431, still
open) confirms there is no native context-fill API. `find_latest_usage` in
`gauge_writer_hook.py` depends on ALL of the following holding for at least
one line near the tail of the transcript JSONL:

| Field | Path | Required for |
|---|---|---|
| `type` | top-level | must equal `"assistant"` |
| `isSidechain` | top-level | must be falsy (subagent turns are a different context window and are skipped) |
| `timestamp` | top-level | used as `observed_at` -- the sampled moment |
| `model` | `message.model` | the frozen record's `model` field, and the key into `MODEL_WINDOWS` |
| `usage.input_tokens` | `message.usage.input_tokens` | one term of the sum |
| `usage.cache_creation_input_tokens` | `message.usage.cache_creation_input_tokens` | one term of the sum |
| `usage.cache_read_input_tokens` | `message.usage.cache_read_input_tokens` | one term of the sum |

**If Claude Code changes any of this** (renames a usage field, moves
`model` off the message object, stops resending full history each turn so
the "latest usage = current total" assumption breaks, or changes how
subagent turns are marked), `find_latest_usage` will most likely start
returning `None` for every line near the tail -- which, by design, means
the writer silently stops producing records and `gauge.json` ages into
staleness. **That silence is the detection signal**: nothing will crash,
nothing will page anyone, but a run where `gauge.json` never appears (or
stops updating) despite active tool calls is exactly this drift happening.
There is no automated alarm for it in v1 (out of scope, per the epic); if
you notice a run with a stuck/absent gauge file, that's the moment to check
this table against a fresh real transcript sample.

## Skip-on-uncertainty, enumerated

The writer never fabricates a `gauge.json` record. Each of these leaves any
existing `gauge.json` byte-for-byte untouched (unit-tested in
`tests/test_gauge_writer.py`). As of #265 (issue #271), **two of these causes
are no longer silent**: the writer hook can positively localize them, so it
also writes a visible `gauge-skip.json` sidecar — `{schema_version, reason,
observed_at, candidate_count?}` — at the exact gauge path(s) it skipped,
which `checklist_engine.py`'s `current` advisory (`_skip_reason_advisory`)
then surfaces at the gate boundary. The other three stay silent by design,
each for the same reason: there is no known gauge path to write a sidecar
**to**.

**Now flagged (`gauge-skip.json` written):**

- **This `session_id` is bound to more than one spine** (#202/#261,
  `decision:gauge-write-skips-on-multiple-bindings`). Two genuinely
  different top-level agents can share one `session_id` (confirmed live: an
  Agent-tool-dispatched Commander and its own Admiral) — when they do, they
  also share one physical transcript, so `find_latest_usage` cannot tell
  whose activity produced the latest usage record. Writing *that* record to
  every bound spine ("fan-out") was tried and reverted after live evidence
  showed it cross-writes one agent's reading into an unrelated agent's work
  area — a confident wrong record, not silence. `gauge.json` itself still
  gets no write for **any** of the candidates, including the parent's own
  spine. But `reason: "ambiguous-binding"` (with `candidate_count`) IS now
  written to **every** candidate path (fan-out is safe here — a diagnostic
  fact about why nothing was written can never be a misattributed reading,
  unlike `gauge.json` itself; `decision:skip-sidecar-fanout-and-clear`).
  Known cost, not fixed here: an orchestrator holding multiple bindings is
  ungauged for the duration of every wave it dispatches — filed as its own
  issue, cross-referenced from #261/#202 (see that issue for the residual
  gap and a candidate discriminator).
- **The transcript has no usable usage line** — either no line, within the
  bounded tail-scan window, that is a non-sidechain assistant message with a
  well-formed `usage` block, a `model`, and a `timestamp`; or a usage field
  present but not a number (a schema-drift symptom). Both collapse to
  `compute_record` returning `(None, None)`. On the single resolved
  candidate path, `reason: "no-usable-record"` (no `candidate_count`) is
  written.

Clearing: any successful outcome at a given path — a clean `gauge.json`
write, or the existing uncalibrated-model flag write — clears that path's
`gauge-skip.json`, mirroring `_clear_uncalibrated_flag`. A candidate that
drops out of an ambiguous binding set without ever again being the sole
resolved candidate keeps a stale `gauge-skip.json` indefinitely — an
accepted, bounded residual (see the comment at `_clear_skip_flag` in
`gauge_writer_hook.py`), not fixed here (`decision:no-repair`).

**Still silent by design (no known gauge path to write a sidecar to):**

- `transcript_path` missing from the hook payload, or the file doesn't
  exist on disk — checked *before* the session→spine binding is even
  resolved, so no gauge path is known yet either way.
- No session→spine binding for this `session_id` at all (work_id
  unresolvable, zero candidates) — genuinely unlocatable.
- The hook isn't wired into `settings.json`/`settings.local.json` at all —
  external to the writer entirely; if the hook never runs, it cannot
  self-report (see #262 for wiring, out of scope here).

## Bounded tail scan, not a full-file parse

Real transcripts grow into the tens of MB over a long session. Re-parsing
the whole file on every single tool call would be wasteful and works
against "non-blocking." `_iter_tail_lines_reverse` reads at most the last
`TAIL_BYTES` (2 MB) of the file and scans backward for the first usable
line. In every real session inspected during implementation the latest
usage record was the very last line, so 2 MB is generously large in
practice; if a future transcript format interleaves a very large tool
result after the last assistant turn, the scan could in principle miss it
and skip-on-uncertainty applies (documented, not a silent truncation bug).

## Session→spine binding assumption (as instructed, documented rather than invented)

This hook does not maintain its own session↔work-directory mapping. It
imports `scripts/hooks/spine_rail.py`'s `load_binding`/`resolve_project_dir`
by file path and reads the same `.agent-work/.spine-rail-binding.json` that
hook already writes on `checklist_engine.py claim`/`release`, and, since
#261, on an unambiguous `SessionStart` resume/compaction too. This was a
pre-existing mechanism found in the repo (`scripts/hooks/spine_rail.py`,
`PostToolUse`/`SessionStart` handlers) -- not something invented for this
issue. **As of #202/#261, the binding is a nested multi-entry map**
(`{session_id: {abs_spine_path: {spine, engine_session, worktree,
claimed_at}}}`), keyed by the resolved absolute spine path rather than a
derived worktree or the harness's `cwd` field (empirically unreliable for
a session dispatched into a worktree by instruction rather than a real
per-agent working-directory parameter — see `notes-261.md` in that fix's
PR for the live evidence). The dependency this creates: **the gauge writer
can only produce a reading for sessions bound to EXACTLY ONE spine** — zero
bindings (nothing claimed/resumed yet) or two-or-more (an ambiguous shared
session) both skip. That is the intended, now-narrower scope (gauge.json
only matters where an engine gate will read it, and only when the reading
is genuinely about that gate's own spine), so this is noted as a documented
coupling, not floated as a gap — except for the multi-binding coverage cost
named above, which IS floated, in the issue this doc points to.

## What was NOT done here (HITL boundary, per the launch order)

- No real `~/.claude/settings.json` (or this repo's own `.claude/settings.json`)
  was edited. The snippet above is the exact addition; applying it is the
  human action.
- The hook has not been driven end-to-end through the actual Claude Code
  hook subprocess plumbing (only its handler function, directly, against
  fixtures and one hand-inspected real transcript). Confirming it fires
  correctly as a wired hook is part of the human validation step above.

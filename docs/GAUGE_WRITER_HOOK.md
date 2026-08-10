# Gauge writer (#180) — wiring, transcript-format dependency, and the HITL seam

Module 2 (Gauge), write side, of the Context Governor v1 spec (epic #178).
Companion to #181's `scripts/gauge_reader.py` (read side, engine-owned). See
the epic body for the full confirmed DESIGN_SPEC; this doc only covers the
writer's wiring and its dependency on Claude Code's transcript format.

## What this hook does

`scripts/hooks/gauge_writer_hook.py` is a Claude Code `PostToolUse` hook. On
every tool call it:

1. Reads `transcript_path`, `session_id` and `agent_id` from the hook's stdin
   JSON — see "The payload fields this hook reads" below.
2. Resolves `.agent-work/<work_id>/gauge.json` by looking up this call's
   **binding key** in `.agent-work/.spine-rail-binding.json` — the binding that
   `scripts/hooks/spine_rail.py`'s own `PostToolUse` and `SessionStart`
   handlers maintain (populated when `checklist_engine.py claim` runs, or
   when a session resumes/compacts onto an unambiguous single active-leased
   spine it did not itself claim — #261). The key is the bare `session_id`
   for a top-level agent and `session_id#agent_id` for a dispatched one
   (#419) — see "Session→spine binding" below. This hook **reuses that
   binding, it does not maintain a second one.** Since #202, one key may
   legitimately hold bindings into more than one spine at once (an
   orchestrator that claims a second spine of its own while the first is
   still leased); when that happens, this hook writes to **none** of them
   rather than guessing — see "Skip-on-uncertainty, enumerated" below.
3. Parses the tail of the acting agent's own transcript (JSONL) for the
   latest assistant message carrying a `usage` block — the main-chain lines
   of `transcript_path` for a top-level agent, the derived subagent
   transcript for a dispatched one — sums
   `input_tokens + cache_creation_input_tokens + cache_read_input_tokens`
   (the "X2 strategic-compact" technique), and normalizes by a per-model
   context-window table to get `fill_fraction`.
4. Atomically (tmp file + `os.replace`) writes the record to `gauge.json`:
   the four required fields `schema_version`, `fill_fraction`, `model` and
   `observed_at`, plus — on a dispatched agent's record only — an optional
   fifth, `identity_resolution_ms` (#419). A top-level agent's record still
   carries exactly four. See "The record is four required fields, plus one on
   a subagent" below.

If any step is uncertain, it writes nothing and leaves the existing file to
age into staleness — see "Skip-on-uncertainty" below.

## The record is four required fields, plus one on a subagent

This is the one place the record's shape is stated; everything else in this
document points here.

| Field | Required | Written when |
|---|---|---|
| `schema_version` | yes | always |
| `fill_fraction` | yes | always |
| `model` | yes | always |
| `observed_at` | yes | always |
| `identity_resolution_ms` | **no** | dispatched agents only (#419) |

The four required fields are what a reader validates —
`scripts/gauge_reader.py` checks that they are present and **does not reject
extras**, which is why the fifth field cost the read side no change.

`identity_resolution_ms` is a float, milliseconds. It measures the two
identity steps this hook does for a dispatched agent — composing the binding
key, then deriving that agent's own transcript path — and nothing else; the
binding-store read that sits between them is binding resolution, a
pre-existing cost, and is deliberately not counted. The budget is **100 ms**
(the issue's stated placeholder), asserted at
`tests/test_gauge_writer.py:1201`. The field exists because "an `agent_id`
lookup should be fast" is a prediction, not evidence.

It rides the dispatched-agent path only: a payload with no `agent_id` takes
the same code path it took before #419 and its record is byte-identical to
what it was, which is why the pre-existing tests still pass. So **four fields
on a top-level agent's `gauge.json`, five on a subagent's, and five is not a
defect.**

## Wiring it up

### (a) In a consuming project: let the installer do it (#262)

`scripts/install_constellation.py` ships both hook scripts into the installed
`constellation-workbench` skill and can wire them for you:

```
python scripts/install_constellation.py --agent claude --scope user --wire-hooks
```

**The installer never writes your `settings.json` without `--wire-hooks`.** Every
ordinary run only *reports* the wiring state and writes nothing — it will not
create the file, and `--wire-hooks --dry-run` together writes nothing either.
That report is five-state:

| State | Meaning |
|---|---|
| `WIRED` | every hook asked about names a script that is on disk |
| `STALE` | an entry exists but names a script that is **not** on disk — the hook never fires, and nothing else can tell you that |
| `PARTIALLY WIRED` | some hooks resolve and others have no entry at all (reachable only with `--hooks rail`/`--hooks all`) |
| `UNWIRED` | no entry at all — *not wired yet*, which is not the same as wired wrong |
| `CANNOT EVALUATE` | the entry names the script through an environment variable the installer declines to expand (see below) |

`STALE`, `PARTIALLY WIRED` and `CANNOT EVALUATE` exist because a hook that never
runs **cannot report that it never ran** — see "Skip-on-uncertainty" below. This
report is the only thing in the system that can surface an unwired or dead hook.

The entry it writes is added **alongside** whatever `PostToolUse` matchers you
already have — never nested inside one, never reordering the others:

```json
{"matcher": "*", "hooks": [{"type": "command",
  "command": "py \"C:/Users/<you>/.claude/skills/constellation-workbench/scripts/gauge_writer_hook.py\"",
  "timeout": 10}]}
```

**Which hooks.** By default `--wire-hooks` writes exactly the one entry above.
`--hooks all` writes all four Constellation hooks — the gauge writer plus
`spine_rail.py` on `Stop`, `SessionStart` and `PostToolUse` — and `--hooks rail`
writes only those three. `--hooks` also selects which hooks are *reported* on,
including under `--check-readiness`. The default is `governor` because the rail
can block a `Stop`; that is not something to acquire as a side effect of an
install command you already knew how to run.

**Why the interpreter is named, and why that is only safe here.** The command
above starts with `py` because `py` is what the installer's probe actually found
on the host that wrote it (`resolve_interpreter()`, one probe per run). That name
is correct for that machine and no other, which is exactly why the git-tracked
`.claude/settings.json` in this repo names **no** interpreter at all — no single
name works on both POSIX and Windows (#539). Naming it *first* also matters: a
command that starts with a quote is parsed by PowerShell as a string literal, so
the hook echoes its own path and exits 0 without running. If no interpreter
answers on your host, `--wire-hooks` refuses rather than writing a command that
cannot run.

**Which scope is safe to commit.** Note the absolute path above: it embeds your
home directory and therefore your **username**.

- **`--scope user`** writes `~/.claude/settings.json`, which is yours alone and
  never committed. **This is the safe default and the recommended one.**
- **`--scope project`** writes `<project>/.claude/settings.json`, which **is
  committable** — so committing it publishes your username in the path and gives
  your teammates a path that does not exist on their machines. If you wire at
  project scope, either keep that file out of version control or expect each
  teammate to re-run `--wire-hooks` for themselves. There is no portable form:
  no `$HOME`/`%USERPROFILE%` token is confirmed to expand in a hook `command`.

**Why an absolute path and not `${CLAUDE_PROJECT_DIR}`.** The variable form does
resolve correctly inside this repo — but only as an *accident of undocumented
harness behaviour*: `CLAUDE_PROJECT_DIR` is fixed at session launch (#269), so it
*happens* to point at the main checkout even for an agent working in a worktree.
That is a property we are borrowing, not one we hold, and it is one release from
changing. An absolute installed path is pinned **by construction** and asks the
harness to guarantee nothing — which is what actually protects the rule that an
agent's own branch cannot edit the code that judges it.

The installer therefore **never emits** a variable form. It will still *detect* a
hand-written `${CLAUDE_PROJECT_DIR}` entry (refusing to recognise the form this
document itself recommends below would be incoherent), but it expands **only**
that one variable. Any other variable leaves the entry `CANNOT EVALUATE`, because
expansion would happen in the installer's environment while the entry runs in a
future hook's — a different process with different variables — and a confident
wrong answer there is worse than an honest "I cannot tell".

### (a2) In this repo, working on the hooks themselves

The source layout is `scripts/hooks/`, which exists only here. Let the installer
do it:

```
python scripts/install_constellation.py --agent claude --scope project --wire-hooks --hooks all --hooks-from source
```

`--hooks-from source` points the commands at this checkout's own
`scripts/hooks/` rather than at an installed skill copy, and writes
`.claude/settings.local.json` rather than `.claude/settings.json`. That split is
structural, not a preference: a source command carries this checkout's absolute
path **and** the interpreter name probed on this host, so it is wrong for every
other machine by construction. `settings.local.json` is gitignored, and the
installer refuses outright to write it if it is ever git-tracked. Claude Code
merges the hooks from both files rather than letting one replace the other, so
the tracked `settings.json` keeps whatever it already carries.

What this repo's tracked `.claude/settings.json` carries instead is the
`${CLAUDE_PROJECT_DIR}` form with **no interpreter named** and `"shell": "bash"`
pinned on every entry — the only form that can be committed at all, since no
single interpreter name is right on both POSIX and Windows. Note the two
matchers: unlike `spine_rail.py`'s `PostToolUse` entry (matcher `"Bash"` only,
because it only cares about `checklist_engine.py` commands), the gauge writer
needs to see **every** tool call to track fill continuously, so its matcher is
`"*"`:

```json
{
  "hooks": {
    "PostToolUse": [
      {"matcher": "Bash", "hooks": [{"type": "command", "command": "\"${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py\" PostToolUse", "shell": "bash", "timeout": 10}]},
      {"matcher": "*", "hooks": [{"type": "command", "command": "\"${CLAUDE_PROJECT_DIR}/scripts/hooks/gauge_writer_hook.py\"", "shell": "bash", "timeout": 10}]}
    ]
  }
}
```

If your real `settings.json` already has other `PostToolUse` matchers
(unrelated hooks), add this as one more entry in that same array — don't
nest it inside an existing matcher block.

## The human action (HITL seam)

Two things still need your eyes:

**Ordering note:** the gauge writer only produces a record once a binding
exists **under the acting agent's own key**, i.e. only after that agent ran a
`checklist_engine.py claim` command and `spine_rail.py`'s handler recorded it.
If you fire a tool call before any claim (or in a session with no spine at all
— e.g. plain chat, no engine in use), the gauge writer will see no binding and
correctly write nothing. Since #419 the same holds one level down: a dispatched
agent that never claims a spine of its own gets no record either, and its
parent's claim no longer stands in for it. This is not a bug to fix; a gauge
file that no engine gate will ever read is not worth writing.

### (b) Confirm it on one real tool call

1. Make sure a spine is claimed in your current session (any normal
   Constellation run does this via `checklist_engine.py claim`).
2. Run any tool call (a `Bash` command, a file read, anything).
3. Look at `.agent-work/<your-work-id>/gauge.json` (sibling to that run's
   `spine.json`). It should now exist and contain something like this — a
   top-level agent's record, so four fields; a dispatched agent's carries a
   fifth:

   ```json
   {"schema_version": 1, "fill_fraction": 0.34, "model": "claude-opus-4-8", "observed_at": "2026-07-18T12:00:00.123Z"}
   ```

4. Run a few more tool calls and re-check the file. `observed_at` should
   advance and `fill_fraction` should trend upward as the session's context
   fills (it can also drop after a `/compact` or a fresh session — that's
   expected, not a bug).

### (c) What "looks right" means

- All four required fields present. On a **dispatched** agent's gauge a fifth
  field, `identity_resolution_ms`, is also present and is **correct, not a
  defect** — it is the measured cost of resolving that agent's identity, and
  the record you are looking at should read under 100 ms. A top-level agent's
  gauge carries exactly the four. See "The record is four required fields,
  plus one on a subagent" above; anything beyond those five is unexpected.
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

- The real schema matched exactly what this hook depends on. That session was
  top-level, so its lines read `isSidechain: false`; a dispatched agent's own
  transcript reads `true` instead (see the field table below). Top-level
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

## The payload fields this hook reads

The table below this one is about lines *inside* a transcript. This one is
about the hook's own stdin JSON -- the payload Claude Code hands the hook on
every tool call.

| Field | Present when | Used for |
|---|---|---|
| `transcript_path` | always | the **parent session's** transcript. Read directly for a top-level agent; for a dispatched agent it is only the base its own transcript path is derived from. |
| `session_id` | always | the first half of the binding key. Read through `spine_rail.binding_key`, which this hook calls rather than composing the key itself. |
| `agent_id` | **only on a subagent's tool call** | the acting agent's identity: the second half of the binding key, the id its transcript path is derived from, and the value each transcript line's `agentId` must equal. |

`agent_id` is **absent** from a top-level agent's payload -- the harness omits
the key rather than sending null (measured on 2.1.222;
`tests/fixtures/probe_payloads.jsonl` holds both shapes side by side). That
absence is what the whole fix rests on: identity is **handed to** the hook by
the harness, never discovered by it. So `"agent_id" in payload` is the test
for "am I running under a dispatched agent", and a present-but-null value
reads as unusable rather than as absent.

`spine_rail.py`'s own handlers additionally read `cwd` and `tool_input`, for
its claim/release parsing and its worktree comparison. Neither reaches the
gauge writer. No other payload field is read by either hook -- notably not
`agent_type`, which the harness does send.

## The exact transcript shape this parser depends on (format-drift note)

This is the fragile, undocumented part -- Claude Code does not publish a
transcript schema, and issue #27969 (closed as duplicate; see #43431, still
open) confirms there is no native context-fill API. `find_latest_usage` in
`gauge_writer_hook.py` depends on the following holding for at least one line
near the tail of the transcript JSONL **it reads** -- which is the parent's
transcript for a top-level agent and the dispatched agent's own derived
transcript otherwise:

| Field | Path | Required for |
|---|---|---|
| `type` | top-level | must equal `"assistant"` |
| `isSidechain` | top-level | the polarity depends on whose transcript is being read: **falsy on a main-chain read** (a top-level agent), **truthy on a dispatched agent's own transcript**, where every line carries `isSidechain: true` |
| `agentId` | top-level | dispatched agents only: must equal the payload's `agent_id`. A top-level read does not look at this field. |
| `timestamp` | top-level | used as `observed_at` -- the sampled moment |
| `model` | `message.model` | the record's `model` field, and the key into `MODEL_WINDOWS` |
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
`tests/test_gauge_writer.py`). **Three of these causes are not silent** — two
since #265 (issue #271) and a third since #419: the writer hook can positively
localize them, so it also writes a visible `gauge-skip.json` sidecar —
`{schema_version, reason, observed_at, candidate_count?}` — at the exact gauge
path(s) it skipped, which `checklist_engine.py`'s `current` advisory
(`_skip_reason_advisory`) then surfaces at the gate boundary. The other four
stay silent by design, each for the same reason: there is no known gauge path
to write a sidecar **to**.

**Now flagged (`gauge-skip.json` written):**

- **This binding key is bound to more than one spine** (#202/#261,
  `decision:gauge-write-skips-on-multiple-bindings`). Before #419 the usual
  cause was two genuinely different top-level agents sharing one `session_id`
  (confirmed live: an Agent-tool-dispatched Commander and its own Admiral),
  which piled both claims under the one bare key. A dispatched agent now keys
  separately, so what is left is one agent holding two spines at once — a
  Commander leasing both its `spine.json` and its `execute.json` is the
  everyday case. Either way the reading comes from one transcript, so
  `find_latest_usage` cannot tell which spine the latest usage record belongs
  to. Writing *that* record to every bound spine ("fan-out") was tried and
  reverted after live evidence showed it cross-writes one agent's reading into
  an unrelated agent's work area — a confident wrong record, not silence.
  `gauge.json` itself still gets no write for **any** of the candidates. But `reason:
  "ambiguous-binding"` (with `candidate_count`) IS now written to **every**
  candidate path (fan-out is safe here — a diagnostic fact about why nothing
  was written can never be a misattributed reading, unlike `gauge.json`
  itself; `decision:skip-sidecar-fanout-and-clear`). Known cost, not fixed
  here: an agent holding two or more spines of its own stays ungauged for as
  long as it holds them — residual 1 below, filed as its own issue and
  cross-referenced from #261/#202 (see that issue for the residual gap and a
  candidate discriminator).
- **The transcript has no usable usage line** — either no line, within the
  bounded tail-scan window, that is an assistant message on the acting agent's
  side of the sidechain polarity (see the field table above) with a well-formed
  `usage` block, a `model`, and a `timestamp`; or a usage field present but not
  a number (a schema-drift symptom). Both collapse to `compute_record`
  returning `(None, None)`. On the single resolved candidate path,
  `reason: "no-usable-record"` (no `candidate_count`) is written.
- **A dispatched agent's own transcript is missing** (#419). The payload's
  `transcript_path` is always the parent's, so a dispatched agent's reading
  comes from a transcript derived from its `agent_id` —
  `<parent transcript minus its .jsonl>/subagents/agent-<agent_id>.jsonl`.
  When that file is not on disk, the writer writes nothing.
  **It never reads the parent's transcript instead.**
  Falling back would file the parent's
  context fill against the subagent's own spine, which is the misattribution
  #202/#261 already tried and reverted; silence is an acceptable outcome and a
  confident wrong number is not. `reason: "subagent-transcript-missing"` (no
  `candidate_count`) is written at the single resolved candidate path.

  **Nesting does not break this derivation, measured.** A depth-2 agent — one
  dispatched by an agent that was itself dispatched — was a real worry: if its
  payload named its *parent agent's* transcript rather than the root session's,
  the derived path would never exist and the governor would be permanently and
  silently blind for every nested agent. It does not. The harness writes every
  agent's transcript **flat** under the root session's `subagents/` directory
  regardless of depth, and the payload's `transcript_path` is always the root
  session's. Observed live during #419's acceptance run: a `spawnDepth: 2`
  agent resolved and produced its own reading.

Clearing: any successful outcome at a given path — a clean `gauge.json`
write, or the existing uncalibrated-model flag write — clears that path's
`gauge-skip.json`, mirroring `_clear_uncalibrated_flag`. A candidate that
drops out of an ambiguous binding set without ever again being the sole
resolved candidate keeps a stale `gauge-skip.json` indefinitely — an
accepted, bounded residual (see the comment at `_clear_skip_flag` in
`gauge_writer_hook.py`), not fixed here (`decision:no-repair`).

**Still silent by design (no known gauge path to write a sidecar to):**

- `transcript_path` missing from the hook payload, or the file doesn't
  exist on disk — checked *before* the binding is even resolved, so no gauge
  path is known yet either way.
- **The acting agent's identity does not resolve** (#419) — the payload
  carries an `agent_id` this hook will not put in a path (anything outside
  `[A-Za-z0-9_-]{1,64}`), or `spine_rail.py` failed to import. The binding key
  is `None`, so nothing is looked up and no gauge path is known.
- No binding for this key at all (work_id unresolvable, zero candidates) —
  genuinely unlocatable. This is also where a dispatched agent that never
  claimed a spine of its own lands; see residual 2 below.
- The hook isn't wired into `settings.json`/`settings.local.json` at all —
  external to the writer entirely; if the hook never runs, it cannot
  self-report. **This one is structurally unfixable from inside the writer**,
  which is why #262 put the detection outside it: the installer's always-on
  `WIRED`/`STALE`/`UNWIRED`/`CANNOT EVALUATE` report (see "Wiring it up" above)
  is the only thing that can ever surface this cause.

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
(`{binding_key: {abs_spine_path: {spine, engine_session, worktree,
claimed_at}}}`), keyed by the resolved absolute spine path rather than a
derived worktree or the harness's `cwd` field (empirically unreliable for
a session dispatched into a worktree by instruction rather than a real
per-agent working-directory parameter — see `notes-261.md` in that fix's
PR for the live evidence).

**The outer key is per agent, not per session (#419).** `spine_rail.binding_key`
composes it, and it is the single place in the codebase that composes it — the
gauge writer calls that same function rather than building the key itself, so
the two hooks cannot drift apart. It returns three things:

| payload | outer key |
|---|---|
| `session_id`, no `agent_id` (a top-level agent) | the bare `session_id` |
| `session_id` plus a usable `agent_id` (a dispatched agent) | `session_id#agent_id` |
| `session_id` falsy, or `agent_id` present but unusable | `None` — **bind nothing** |

`None` means exactly that: an unusable `agent_id` binds nothing at all, and no
entry is written anywhere. The key does **not** fall back to the bare
`session_id`, because that would file the subagent's entry under the parent's
key, push the parent to two candidates and silence the parent's own gauge —
manufacturing the blindness this keying exists to remove. Failing closed costs
that one subagent its binding and affects nobody else. An `agent_id` counts as unusable if it is not a non-empty
string, or if it contains `#`, `/`, `\` or `..`; the gauge writer applies a
stricter test still before it will use one — the id must match
`[A-Za-z0-9_-]{1,64}`, because this hook interpolates it into a real file path
(`agent-<agent_id>.jsonl`) rather than only using it as a dictionary key.

`SessionStart` binds under the bare `session_id` always: that event carries no
`agent_id`, so a resumed session is by definition top-level. Readers that must
see every spine a harness session touches (`decide_stop`, `decide_session_start`)
read through `session_view`, which merges the bare key with every
`session_id#<agent_id>` key under it.

The dependency this creates: **the gauge writer can only produce a reading for
a binding key bound to EXACTLY ONE spine** — zero bindings (nothing
claimed/resumed yet) or two-or-more (an ambiguous key) both skip. Because the
key is now per agent, that coupling holds **per agent**, which is what makes it
satisfiable again for a dispatched agent: a crew agent's own claim no longer
lands in the same bucket as its parent's. That is the intended scope (gauge.json
only matters where an engine gate will read it, and only when the reading is
genuinely about that gate's own spine), so it is a documented coupling rather
than a floated gap.

### Two residuals survive this change, and they sit side by side

1. **An orchestrator holding several spines under one bare key is still
   ambiguous.** A top-level agent that claims a second spine while the first is
   still leased has two candidates under its own bare `session_id`, so no
   reading is written for either and it stays ungauged for the duration.
   `gauge-skip.json` names the reason at each candidate path (#271), so the
   silence is at least visible. Unchanged by #419, and still floated in the
   issue this doc points to.
2. **A dispatched agent that never claims a spine of its own now writes
   nothing at all.** Its payload keys to `session_id#agent_id`, nothing is
   bound under that key, so it resolves to **zero** candidates — a silent skip,
   with no path to write a sidecar to. Before #419 the same tool call resolved
   against the parent's bare `session_id` and, where exactly one spine was
   bound there, wrote a record computed from the **parent's** transcript to it.
   Two different things were happening under that one behaviour, and #419 ends
   both. Where the bound spine was the parent's own, the record was the
   parent's and was filed correctly — so what is lost is coverage: a parent
   that is idle while its children work no longer picks up its own latest usage
   line until it runs a tool call itself. (That loss is bounded. Staleness is
   judged by the record's own `observed_at`, never the file's mtime — see
   `scripts/gauge_reader.py` — so those writes never bought freshness, only an
   earlier sample of a turn the parent's next tool call would have sampled
   anyway.) Where the single bound spine belonged to a **different** top-level
   agent sharing the `session_id`, that same write filed one agent's reading
   against another's spine, and it is gone. The trade is deliberate: some
   coverage for correctness, because a reading filed against an agent that did
   not produce it is worse than no reading.

## Known limits of the binding store itself (#419)

Named here rather than left to be discovered. None of these was introduced by
per-agent keying, but two of them get *wider* under it, so they belong beside it.

- **~~A worktree-dispatched agent's binding records a path in the MAIN CHECKOUT~~
  — FIXED in #440.** The binding used to resolve a relative `--file` against the
  hook payload's `cwd`, and for an agent dispatched into a worktree that `cwd` is
  the main checkout, because `CLAUDE_PROJECT_DIR` is fixed at session launch
  (#269). The reading landed in a phantom `.agent-work/<work_id>/` inside the
  main checkout while the engine read the worktree copy and saw nothing.
  Measured 2026-08-05: 60 of 64 live entries were exactly this.
  **The shipped resolution** (`resolve_spine_candidate`) no longer trusts `cwd`.
  It walks *ordered candidate roots* and takes the first that **validates as a
  checklist on disk** — existence-verified rather than guessed — and when two
  guessed roots name different existing files it **refuses to bind at all**
  rather than pick one. The worktree root is **derived** from `git worktree
  list`, never handed in; a binding written that way records
  `path_source: "git_worktree"`, which is how you tell a derived root from an
  inferred one. Verified live, two-arm, on 2026-08-07: a subagent dispatched into
  a real worktree claimed a spine there with a relative `--file`, filled its
  context to 56% against a HARD of 15%, its `gauge.json` landed **beside the
  worktree spine**, and the engine **refused its `advance`** (exit 1). The
  byte-identical control on the pre-fix commit reached 56.2%, filed its reading
  in the phantom directory, and advanced clean (exit 0). Evidence:
  `.agent-work/issue-440-binding-cwd/acceptance/`.
- **A bare-keyed agent driving several spines at once gets NO reading at all.**
  Not #440, and not fixed by it. `resolve_gauge_path` returns one candidate per
  spine bound under the key, and the ambiguity guard refuses to write when there
  is more than one. A top-level agent — an Admiral, say — that legitimately
  claims an epic spine plus a crew spine or two in one session therefore silences
  its own gauge for the rest of that session. Measured 2026-08-07: the live
  store's one bare key held 10 entries, **3 of them live**, so retiring the 7
  dead ones would not have lifted the guard. This, rather than stale data, is
  what keeps the governor quiet for orchestrators.
- **A relative `--file` given as an unexpanded shell token is bound verbatim.**
  The hook parses the command string and cannot tell whether the shell expanded a
  token, so `--file $E` binds a literal path named `$E`. Observed in the live
  store 2026-08-06. It can only ever produce a dead entry, but each dead entry
  adds a candidate to its key and so pushes that key toward the ambiguity guard
  above. Same family as #440 — a binding naming the wrong path — but a different
  mechanism, and out of #440's scope.
- **Nothing reaps an abandoned key.** A successful `release` is the only removal
  path, so an agent that dies, is cancelled, or is killed mid-run leaves its key
  behind forever. Per-agent keying multiplies the key count by every wave's
  fan-out. #419's one-time sweeper was deleted after its single run, as that
  issue required, so the next cleanup needs a fresh one.
- **The load-modify-save takes no lock.** `_save_json_map` is atomic per write,
  but the read-modify-write around it is not, so two agents claiming at the same
  instant can lose one of the two claims. The symptom is silence, which is
  indistinguishable from an idle governor — and a lost write reintroduces exactly
  the blindness per-agent keying removes.
- **The recorded path is not validated.** `--file` is taken as given, so a
  malformed or shell-mangled engine command can enter the store as if its
  fragment were a spine path. The 2026-08-05 sweep found entries keyed by
  literal `$E` and `x`.

## What was NOT done here (HITL boundary, per the launch order)

- No real `~/.claude/settings.json` (or this repo's own `.claude/settings.json`)
  was edited. As of #262 the installer *can* write it, but only when you pass
  `--wire-hooks` — applying it is still deliberately the human action.
- The hook has not been driven end-to-end through the actual Claude Code
  hook subprocess plumbing (only its handler function, directly, against
  fixtures and one hand-inspected real transcript). Confirming it fires
  correctly as a wired hook is part of the human validation step above.

  #262 narrowed the untested gap without closing it. Verified there, by real
  install plus a **fresh subprocess from a neutral working directory**: the
  *installed* `gauge_writer_hook.py` loads its *installed* `spine_rail.py`
  sibling, so the silent `try/except -> None` degradation does not occur in an
  install tree. What remains unproven is the step above that — Claude Code
  actually invoking the entry as a hook — which needs a live session.

## Known limits of the installed wiring (#262)

Named here rather than left to be discovered:

- **No self-healing.** A `--force` reinstall that probes a different interpreter,
  or a moved install tree, leaves the old entry behind. It is *reported* as
  `STALE`, not repaired; re-run `--wire-hooks` to add a correct entry and remove
  the stale one yourself.
- **The wiring is not tamper-proof, only the code is.** The installed hook script
  lives outside any project's working tree, so an agent's own branch cannot edit
  it. The `settings.json` entry, however, is an ordinary editable file — an agent
  can leave the judging code untouchable and simply unregister it. Tracked as
  **#288**; it qualifies the anti-tamper property rather than completing it.

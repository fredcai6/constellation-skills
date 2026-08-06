# Implementer Handoff — g2: the gauge writer attributes the reading to the acting agent

**Work id:** issue-419-governor-identity · **Gate:** g2 · **Worktree:**
`C:/Programs/constellation-skills-wt/epic418-a-419` · branch `epic-418/a-419-governor-identity`

## Assigned task

Make `scripts/hooks/gauge_writer_hook.py` produce a reading that belongs to **the agent that produced
it**. Gate g1 already landed the binding half: `spine_rail.binding_key(payload)` now composes
`session_id#agent_id` for a dispatched agent, the bare `session_id` for a top-level one, and `None`
when the identity is unusable. Read `scripts/hooks/spine_rail.py` for that helper before you start —
you call it, you do not reimplement it.

Five pieces, all in `gauge_writer_hook.py`:

**(a) Resolve by the composite key.** `resolve_gauge_path`'s second parameter becomes the binding key
rather than the session id (rename it, update the docstring). The caller passes
`_spine_rail.binding_key(data)`.

**(b) Derive the acting agent's own transcript.** A pure helper:
`Path(transcript_path).with_suffix("") / "subagents" / f"agent-{agent_id}.jsonl"`. This shape is not a
guess — it was confirmed on disk for both agents of a live two-subagent probe, and re-verified
independently by a cold critic.

**(c) Never read the parent's transcript for a subagent.** When the payload carries an `agent_id`, the
reading comes from the derived transcript and **only** from it. If that file does not exist, write a
`gauge-skip.json` with `reason: "subagent-transcript-missing"` and return — no `gauge.json`, no
`gauge-uncalibrated.json`.

**(d) Invert the sidechain filter for a subagent.** `find_latest_usage` and `compute_record` take an
`agent_id` parameter. When it is `None` the filter is exactly today's: skip anything `isSidechain`
truthy. When it is set, the line must be `isSidechain` **truthy** *and* carry a top-level `agentId`
**equal to** that `agent_id`.

**One parameter, not two.** "This is agent X's own transcript" is a single fact; an
`expect_sidechain` + `expect_agent_id` pair would let a caller set an incoherent combination. The
`agentId` equality is what makes a wrong derived path fail closed instead of producing a confidently
misattributed number.

**(e) Record the identity-resolution duration** in the gauge write as an optional fifth field, against
the issue's stated 100ms placeholder budget. The reader validates the presence of its four required
fields and does not reject extras, so this is tolerated — but see the exclusions.

## Protected intent

The issue's done-condition is not "readings appear". It is "**this agent's** reading appeared, and a
trip fired from it". Everything here exists to make an attribution true, so the failure you must never
ship is a **confident wrong number**. Silence is an acceptable outcome; misattribution is not.

## Why fail-closed is the whole gate

There must be **no code path anywhere** that passes the parent's transcript to `compute_record` when
`agent_id` is present. Falling back to the parent is the exact misattribution that was already tried
and reverted once under #202/#261: fan-out did not fix ambiguity, it *spread* one agent's reading into
an unrelated agent's work area. Read that history in the module's own docstrings before you write the
branch.

## Constraints

1. **Carry the `_spine_rail is None` guard to the new call site.** Today that guard lives *inside*
   `resolve_gauge_path`. Moving the `binding_key` call out to `handle_post_tool_use` strands it:
   `_load_spine_rail` returns `None` on any import failure, and an unguarded call would raise into
   `handle_post_tool_use`'s outer `except`, leaving the governor silent with zero diagnostic — wearing
   the same symptom as every other silence. This is a named finding, not a hypothetical.
2. **A payload with no `agent_id` must behave exactly as today, byte-identically.** The existing tests
   are the pin for that and must pass **unedited**.
3. **Do not lean on g1's `agent_id` rejection alone for path safety.** g1's reviewer found it is a
   hand-maintained *denylist* that still admits `:`, `*` and `?` — all of which reach your
   `agent-{agent_id}.jsonl` interpolation. Validate at your own boundary too, and prefer an
   **allowlist** shape (the real ids observed are hex-ish tokens plus `-` and `_`) over extending a
   denylist. A value that fails your check means **write nothing** — never a repaired or sanitized path.
4. **Windows path reality:** `agent-{id}.jsonl` is a filesystem path on a Windows box. A rejected
   character must not become an exception that the outer swallow turns into silence — it must be a
   deliberate skip you can see.
5. The new skip reason costs zero engine change: `gauge_reader.skip_reason` does not whitelist reason
   strings and the engine's advisory already renders an unrecognized reason verbatim. Add it at the
   call site only.
6. The hook stays fail-open at the process level (it never raises, never blocks a tool call) while
   being fail-closed about *records*. Those two are not in tension: no exception escapes, and no
   uncertain reading is written.

## Allowed scope

- `scripts/hooks/gauge_writer_hook.py`
- `tests/test_gauge_writer.py`
- A new derived fixture under `tests/fixtures/` if your evidence needs one (see below — it does).

## Specific exclusions

- **`scripts/gauge_reader.py` and `scripts/checklist_engine.py` are NOT edited by this gate.** The
  four required gauge fields keep their meaning; the fifth is additive and optional.
- `scripts/hooks/spine_rail.py` is closed — g1 shipped it and it was reviewed. If you believe it is
  wrong, return that as a finding rather than editing it.
- `docs/GAUGE_WRITER_HOOK.md` belongs to gate g3. Do not update it here, even though you will notice it
  is wrong.

## Close criteria

1. The gauge path resolves from the composite key, so a dispatched agent finds its **own** binding.
2. A subagent's reading comes from its own derived transcript, with the polarity inverted and the
   `agentId` equality enforced.
3. `agent_id` present + derived transcript absent ⇒ `gauge.json` byte-identical on disk (bytes **and**
   mtime), no uncalibrated flag, and a `gauge-skip.json` carrying `subagent-transcript-missing`.
4. An unresolvable identity writes nothing — the issue's own named negative control.
5. A payload with no `agent_id` is byte-identical in behavior to today.
6. Every pre-existing test in `tests/test_gauge_writer.py` passes **unedited**.

## Required evidence — the sidechain conjunct is the trap, read this twice

- `find_latest_usage(tests/fixtures/real_subagent_transcript.jsonl)` at default polarity still returns
  `None` — the existing assertion stays green and unedited. Given that fixture's own `agentId` it
  returns the real usage sum. Given a **different** `agent_id` it returns `None`.
- **Those three assertions are all satisfied by an implementation that checks `agentId` equality alone
  and silently drops the sidechain half.** A cold critic verified why: all 4 lines of that fixture are
  `isSidechain` truthy with the same `agentId`, so the conjunct is unfalsifiable against it. **Add a
  derived fixture line carrying the matching `agentId` with `isSidechain` falsy, and assert it is
  skipped.** State the line count and how many lines each assertion reaches.
- The fail-closed test: temp dirs, `agent_id` set, derived file deliberately absent; assert
  `gauge.json` unchanged (bytes and mtime) and the sidecar's reason.
- The unresolvable-identity negative control. **Constructing a payload is legitimate here** — the ban
  on supplying `agent_id` binds the *live acceptance run* in gate g4, whose whole point is that the
  harness delivers it. At this level you are testing rejection, not delivery.
- A test showing a rejected `agent_id` character (including one of `:`, `*`, `?`) writes nothing.
- The identity-resolution duration appears on a written record and is a real measurement.
- **Measure non-vacuity, do not argue it.** Revert your file to `HEAD` and record how many of your new
  tests go red. The gate before this one did exactly that and it was the single most valuable piece of
  evidence in the review. Any new test that stays green under the revert is not evidence.

## Test mode

Test-led. `tests/test_gauge_writer.py` is a pytest module.

## Required verification commands

```
cd C:/Programs/constellation-skills-wt/epic418-a-419 && python -m pytest tests/test_gauge_writer.py -q
cd C:/Programs/constellation-skills-wt/epic418-a-419 && python -m pytest tests/test_gauge_writer.py tests/test_gauge_reader.py tests/test_spine_rail.py -q
cd C:/Programs/constellation-skills-wt/epic418-a-419 && python -m pytest tests -q
```

**`python -m pytest`, never `py`** — `py` resolves to a codex runtime with no pytest, and
`py -m unittest discover` reports 15 red results that are pure interpreter artifacts. The suite after
g1 is **1637 passed, 2 skipped, 550 subtests** (baseline 1621 at HEAD `990712f`, +16 from g1). Your
count must exceed 1637.

## Inbound anchors

- **Structural:** `gauge_writer_hook.py` — `resolve_gauge_path` (~145), `find_latest_usage` (~194),
  `compute_record` (~238), `handle_post_tool_use` (~399). `tests/fixtures/real_subagent_transcript.jsonl`
  is real captured harness output: 4 lines, all `isSidechain` truthy, all `agentId af45cec63b2835a40`,
  one usable assistant line on `claude-opus-4-8`.
- **Constraint:** fail-closed on identity; skip-on-uncertainty, never fabricate.
- **Decision (settled/measured, not yours to reopen):** the acting agent's transcript is **derived**
  from payload fields, never searched for — which is why the identical-command race the prototype
  worried about cannot arise here at all.
- **Confidence flag:** `docs/GAUGE_WRITER_HOOK.md` is **wrong** about the sidechain filter today. Read
  the code, not the document.

## Stop conditions

Stop and return if: a close criterion cannot be met; you must edit `gauge_reader.py`,
`checklist_engine.py` or `spine_rail.py` to make this work; an existing test must be edited rather than
added to; or the derived-transcript shape turns out not to hold. Do not widen scope to fix something
you find — record it as a finding.

## Authority

Delegated Commander `cmdr-419-governor-identity` under the frozen epic-418 launch order. Local commits
are fine; do not push, do not open a PR, do not file issues.

## Return format

`IMPLEMENTER_RESULT` at
`.agent-work/issue-419-governor-identity/results/g2-IMPLEMENTER_RESULT.md`: what you changed, the
evidence above with real command output and **real exit codes**, each close criterion met or not, the
revert-measured non-vacuity count, anything you deliberately did not do, out-of-scope findings, and a
**Workflow Feedback** section (a bare "none" is not acceptable; if genuinely none, say what you checked).

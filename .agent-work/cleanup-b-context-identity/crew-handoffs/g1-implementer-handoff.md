# Implementer Handoff — g1: a gauge reading is named for the agent that produced it (#600)

Work id: `cleanup-b-context-identity` · worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity`
· branch `cleanup/b-context-identity` · base `a69bbac4`.

## Gate

`g1-implement` in `.agent-work/cleanup-b-context-identity/execute.json`.

## Task

Make a context reading belong to an **agent** instead of to a **folder**.

Today `.agent-work/<work-id>/gauge.json` is one file per work directory. The
writer resolves it from a binding key; the engine resolves it from the spine's
parent directory. Neither carries any agent identity, so two agents whose spine
files sit in one work directory write to the same file and the last one wins.

**This is measured, not assumed.** `.agent-work/cleanup-b-context-identity/measurement/probe_cross_key.py`
drives the real `handle_post_tool_use` in a fresh process with two distinct
binding keys bound into one work directory. Output
(`measurement/probe_cross_key.out`):

```
after DISPATCHED agent's call : {... "fill_fraction": 0.02 ...}
after ORCHESTRATOR's call     : {... "fill_fraction": 0.9 ...}
gauge-skip.json               : (none)
VERDICT: CANDIDATE 2 CONFIRMED.
```

The orchestrator's 90% overwrote the dispatched agent's 2%, and **nothing
noticed** — no skip sidecar, no guard. `resolve_gauge_path`
(`scripts/hooks/gauge_writer_hook.py:233`) enumerates candidates for **one**
binding key, and the ambiguity guard (`:609`, `len(gauge_paths) > 1`) is
therefore **within-key**. Nothing anywhere compares across keys.

The overwrite is **fresh**, which is why the existing guard cannot help:
`observed_at > claimed_at`, so `_reading_predates_claim`
(`scripts/checklist_engine.py:1444`) returns False. #477/#601's timestamp
comparison can only ever catch a reading *older* than the claim.

## Protected Intent

- The governor must never **refuse** anywhere it currently permits. Every change
  here may only make it quieter, never louder. If your design would add a
  refusal, **stop and say so** — that is outside this lane's latitude and must be
  floated to the Admiral.
- Fail **open** on every uncertainty. No reading is always an acceptable outcome;
  a confidently wrong reading never is.
- Silence must stay **visible**. This subsystem has been burned twice by a quiet
  governor (#252 miscalibration, #271 ambiguous binding). If a reading is
  declined, the agent is told why and what to do.

## Test Mode

Test-led. There is a test surface and it is well developed. Write the failing
test first, watch it fail for the right reason, then fix.

**Evidence standard, inherited from `tests/test_checklist_engine.py::TripGaugeReadingOwnership`
(that class's own bar, and #601's two relaunch tests live there too):** red-before
/ green-after over **behaviour**, driving the **real** reader and a **real** gauge
file on disk. Never a patched `_read_gauge`. Never a fixture that hand-injects
`CLAUDE_PROJECT_DIR` — that variable is what the harness delivers, and a test that
supplies it proves nothing about the harness.

## Close Criteria

1. The writer names the record for its owner: `gauge-<owner>.json` beside the
   spine, where `<owner>` is the `engine_session` carried by the binding entry it
   already resolved. The two existing sidecars follow that name (both are derived
   with `.with_name()` off the gauge path, so this should fall out).
2. The engine resolves the same name from its **own** active lease `session_id`.
   These two strings are the same value by construction — the binding entry's
   `engine_session` is parsed from the `claim --session-id X` command, and the
   lease's `session_id` is that same `X`. Verified live in this run:
   binding `engine_session = commander-cleanup-b-context-identity` and lease
   `session_id = commander-cleanup-b-context-identity`.
3. **No fallback to a shared `gauge.json`** on either side
   (`decision:no-shared-file-fallback`). A fallback reinstates the folder-owned
   file this issue exists to remove. When no owner resolves, write nothing and
   read nothing (`decision:unattributable-means-no-reading`).
4. Owner names are filename-safe. **Reuse the existing single identity predicate
   idiom** — `spine_rail.is_usable_agent_id` (a 1–64 char `[A-Za-z0-9_-]`
   allowlist, `scripts/hooks/spine_rail.py:447`ff). #441 made that the *sole*
   identity predicate precisely so two definitions could not drift; do not add a
   third. You may **read** `spine_rail.py`; it is **fenced** for edits.
5. A declined or absent reading produces a **visible** advisory naming the cause
   and the remedy, in the shape the existing `_declined_reading_advisory` /
   `_no_reading_advisory` family already uses.
6. `#601`'s timestamp comparison need **not** be deleted this wave
   (`decision:identity-not-time` says so explicitly). Leave it in place unless it
   actively conflicts; say which you did and why.

## Allowed Scope

- `scripts/hooks/gauge_writer_hook.py`
- `scripts/gauge_reader.py`
- `scripts/checklist_engine.py` — **gauge, trip and refresh regions only**,
  roughly `_gauge_path` (`:1372`) through `_why_suffix` (`:1308`) and the trip
  block. Note `_gauge_path`'s callers (`_read_gauge`, `_uncalibrated_advisory`,
  `_no_reading_advisory`) will need the checklist threaded through; that is in
  scope and mechanical.
- `tests/test_gauge_writer.py`, `tests/test_gauge_reader.py`,
  `tests/test_checklist_engine.py`, `tests/test_gauge_chain_writer_to_trip.py`,
  `tests/test_spine_rail.py` (only where it asserts the gauge filename)
- `docs/GAUGE_WRITER_HOOK.md`, `docs/CHECKLIST_SCHEMA.md` — update the prose you
  invalidate.

## Specific Exclusions

- **Fenced, do not edit:** `scripts/hooks/spine_rail.py`, `scripts/run_crew.py`
  (lane C); `scripts/mcp_spine_server.py`, `.mcp.json` (lane A).
  `spine_rail.py`'s one `gauge.json` mention (`:769`) is a comment about a check
  that keys on `items`, not on the filename, so the design should need no edit
  there. **If you find it does, stop and report** rather than editing.
- `checklist_engine.py`'s **claim path** changed on `main` this morning (#601).
  Leave it alone unless your design requires it — and say so if it does.
- `episodes/**` — those are historical records, never edited. Several mention
  `gauge.json`; leave every one of them exactly as it is.
- `#500` (the refresh-request consume path) is **not** in this gate.

## Constraints

- Clear `__pycache__` before **every** measurement. Stale bytecode fabricates
  failures that look like defects (#597) and it cost this epic hours twice.
- Platform Linux, Python 3.12 as `py`. CI is one `windows-latest` job, **red at
  baseline** — local Linux is the only real signal.
- Hook code is **not** fenced by git isolation. `CLAUDE_PROJECT_DIR` is resolved
  once at session launch and inherited unchanged, so you cannot validate a hook
  change from inside the session that contains it. Validate in a **fresh
  process**. (Measured in this run: in this session that variable is *unset*
  entirely, so the hook resolved the project dir from cwd. Do not build a harness
  that quietly depends on that.)

## Map Anchors (inbound)

- **Map entry point:** `map/INDEX.md` names `scripts.gauge_reader`,
  `scripts.hooks.gauge_writer_hook`, `scripts.checklist_engine`. The map is
  **DEGRADED** — `map/ids.jsonl` is empty and every per-module `INDEX.md` target
  is absent — so the real entry point is `docs/GAUGE_WRITER_HOOK.md`, the
  hash-pinned substitute recorded in
  `.agent-work/cleanup-b-context-identity/map-orientation.json`. **Read it before
  changing the writer**; its "Skip-on-uncertainty, enumerated" and "Known limits
  of the binding store itself" sections are the design intent.
- The read side's intent is in `scripts/gauge_reader.py`'s `_PROFILES` note
  (`:76`); the policy side's is the trip block comment from
  `scripts/checklist_engine.py:1328`. **Read both before changing either.**
- Decisions in force: `decision:identity-not-time`,
  `decision:unattributable-means-no-reading`, `decision:no-new-state-file`,
  `decision:owner-in-the-filename`, `decision:no-shared-file-fallback`. Their
  wording and grades are in
  `.agent-work/cleanup-b-context-identity/MISSION_FRAME.md`.
- **Recorded dead end — do not re-propose it:** writing one reading to *every*
  bound spine ("fan-out") was tried and reverted, because it cross-writes one
  agent's reading into an unrelated agent's work area (#202/#261). A confident
  wrong record is worse than silence.

## Deliverable Path Check

All committed, all verified before dispatch with `git check-ignore <path>`
exiting **1** (not ignored):

`scripts/hooks/gauge_writer_hook.py`, `scripts/gauge_reader.py`,
`scripts/checklist_engine.py`, `tests/test_gauge_writer.py`,
`tests/test_gauge_reader.py`, `tests/test_checklist_engine.py`,
`tests/test_gauge_chain_writer_to_trip.py`, `docs/GAUGE_WRITER_HOOK.md`.

## Wiring Grep — do this FIRST, before any edit

**Enumerate by command, never by memory, every artifact that asserts the literal
name `gauge.json`, and STATE THE COUNT in your result.** You are the author, and
the author is the only one positioned to know the blast radius of a *format*
change — and the one who reliably does not look.

The Commander's own enumeration at dispatch time, for you to reproduce and
**correct**, not to trust:

```
grep -rl "gauge\.json\|gauge-uncalibrated\.json\|gauge-skip\.json" \
  --include='*.py' --include='*.md' --include='*.json' . \
  | grep -v '^\./\.git/' | grep -v '__pycache__' | grep -v '\.agent-work/'
```

→ **21 files**: 5 code (one of them fenced `spine_rail.py`), 5 test (125
occurrences, `test_gauge_writer.py` alone has 64), 2 docs, 7 episodes (leave
alone), 2 notes. Report your own count and reconcile any difference.

## Required Evidence

- The failing test(s) first, with the **output showing they fail for the right
  reason** — not merely that they fail.
- Green-after for the same tests.
- A fresh-process demonstration that two agents in one work directory now each
  keep their own reading. `measurement/probe_cross_key.py` is the natural
  starting point; extend or adapt it, and say what you changed.
- The blast-radius count from the Wiring Grep, reconciled.
- Pasted output of every verification command below.

## Verification Commands

POSIX form, absolute paths, cache cleared:

```
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity && \
  find . -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q \
    tests/test_gauge_writer.py tests/test_gauge_reader.py \
    tests/test_checklist_engine.py tests/test_gauge_chain_writer_to_trip.py
```

```
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity && \
  find . -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
```

The full suite was **3057 passed / 0 failed** on `main` at `a69bbac4` at dispatch.
Report your own numbers; a difference is the thing that matters, not the absolute.

## Suggested Model Tier

Opus. This is a governor that must become neither bypassable nor trigger-happy,
and the change spans three modules that have to move together.

## Authority

Admiral launch order `LAUNCH_ORDER.md` (frozen), via Commander
`commander-cleanup-b-context-identity`. No human is reachable. Take a genuine gap
up, do not guess past it.

## Stop Conditions

Stop and return rather than pushing through if: your design would make the
governor refuse where it currently permits; it requires editing a fenced file or
the `claim` path; the measured mechanism turns out not to be what the fix targets;
or you need context this handoff does not carry. **A measured negative is a
complete deliverable** — if the design cannot work, report that with the evidence
and stop. Do not ship a fix aimed at a mechanism you could not reproduce.

## Return Format

Write `IMPLEMENTER_RESULT` to
`.agent-work/cleanup-b-context-identity/crew-handoffs/g1-implementer-result.md`
**before ending your turn** — that write is the delivery.

Include: `Return status` (one of `complete | partial | blocked | out-of-scope |
failed`, **lowercase**), what changed and why, the blast-radius count, the
red-before/green-after evidence, every verification command with its pasted
output, decisions you made and their grades, anything you had to leave undone,
and a `Workflow Feedback` section (what in this handoff or the tooling got in
your way — it is harvested, not ignored).

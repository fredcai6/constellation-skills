# Implementer handoff — gate `g2-implement` (issue #541, friction capture)

## Task

Make the MCP door record **its own** rejections, land them in the run's episode through
`scripts/apply_episode_delta.py`, and **fail loud on every occurrence** when it cannot.

## Protected intent — read this before you plan, it is narrower than the issue title

The issue says the door "converts a diagnosable defect into a silent correction." That
framing is half right, and the half that is wrong would waste this whole gate. **The
narrowing below is measured, not assumed** — reproduce it yourself first:

```
python .agent-work/epic-418-followon/commander-f2/demo_engine_refusal_reaches_episode.py
```

12 assertions, all passing. It launches the real server as a subprocess on a **nested**
work-id and shows both halves in one run:

- **Already works, do not rebuild.** An **engine** refusal arriving through the door
  moves the spine's `refusals` counter (0 → 1 → 2) and `episode_capture.mechanical_fields()`
  composes that exact value into the `## Mechanical` bin. `run_engine()` calls
  `checklist_engine.main()`, and `main()` counts the refusal in its `EngineError` handler
  (`checklist_engine.py:3319-3321`).
- **The actual defect.** The door's **own** rejection moves the counter **not at all** and
  leaves **no line** in the server's own `mcp_calls.jsonl` — because every
  `_tool_error(...)` return in `call_tool()` short-circuits *before* `run_engine()`, and
  `_log()` is only ever called from `run_engine()`.

**Your target is only the second bullet.** Four rejection classes take that silent path:

| Class | Site |
|---|---|
| unknown tool name | `main()`'s `tools/call` branch |
| unknown `action` | `call_tool`, 4 multiplexed tools |
| missing required argument | `_require()`, 8 call sites |
| **client-side schema rejection** | the *client* — never reaches the server process at all |

That fourth class is the sharpest and you **cannot** capture it server-side. Say so in
your result; do not imply coverage you do not have.

## The landing site is DECIDED. Do not re-open it.

**One record per rejection** goes to a door-side JSONL beside the spine. The run's episode
carries it as an **`artifact-ref`** line in the `## Mechanical` bin.

Why this and not the alternatives — so you can recognise if your implementation is drifting:

- `MECHANICAL_SCALAR_FIELDS` / `MECHANICAL_INT_FIELDS` (`apply_episode_delta.py:166-178`)
  are scalars and ints. **A per-rejection record is unrepresentable there.**
- `artifact-ref` is already in `MECHANICAL_ALL_FIELDS`, is already list-shaped (repeated,
  one per line), and is already produced by `episode_capture._artifact_refs()`. Full
  per-rejection detail survives in the referenced artifact, and **the store contract is
  untouched**.
- `refusals` is the **engine's own** counter, sourced from checklist state. A second
  writer would make one field disagree with its own source. `failed-commands` counts
  engine `command` checks. Both have owners; do not overload either.

**`scripts/apply_episode_delta.py`, `scripts/episode_capture.py` and
`docs/EPISODE_STORE.md` are OUTSIDE this run's file ownership. Do not edit them.** If you
conclude the `artifact-ref` landing genuinely cannot work, **STOP and report a blocker** —
do not edit an unowned file to make it work.

## Close criteria

1. **The door records its own rejections**, one record per rejection, to a durable
   door-side log. A record should carry enough to diagnose: which tool, which rejection
   class, what was missing/unknown, and when.
2. **Fail loud, every turn.** If the capture cannot write, the door says so on **every
   occurrence** — never once per run, never coalesced, never only at exit. A capture that
   fails quietly is the same defect as the door it instruments.
3. **End-to-end into the episode.** A real episode is written under this run's **nested**
   work-id `epic-418-followon/commander-f2` via `apply_episode_delta.py` (with
   `--store-root episodes` on **every** invocation), read back, and verified with
   `scripts/verify_episode_captured.py`. **Not** a unit test that stops at the write call —
   the claim names `apply_episode_delta.py`, so the evidence must reach it. #543 made this
   satisfiable for a nested work-id; exercise it rather than assuming it.
4. **A seeded rejection is scored by the instrument**, proving it *can* score — so that a
   later zero is a reading and not a blind spot.
5. **The loud-failure test induces N≥2 failed writes in ONE process and asserts N separate
   messages.** One induced failure asserting one message proves nothing about "every".
6. **A written statement** of which rejection classes this instrument can and cannot see.

## Allowed scope

`scripts/mcp_spine_server.py`, `tests/test_mcp_friction_capture.py` (new), `.mcp.json` (if
the capture needs a path or variable in the server's environment — this gate owns that
edit), and `episodes/` **only** via `apply_episode_delta.py`.

## Specific exclusions

- `scripts/checklist_engine.py` — **never**. `git diff` against it was empty for all of F
  and stays empty. The door **wraps** the engine and never re-implements it.
- `scripts/apply_episode_delta.py`, `scripts/episode_capture.py`, `docs/EPISODE_STORE.md` —
  unowned. Do not extend the Mechanical allowlist.
- `scripts/hooks/spine_rail.py` — issue #549, outside the fence.
- Do not instrument the CLI arm. Decided and recorded: a CLI shape rejection exits inside
  `argparse` *before* `load(path)` runs, so the engine does not know which spine was meant
  and there is no run to attribute it to. The door always knows, because its spine is bound
  at import. The asymmetry is structural. The comparability cost for future DC5-style work
  is recorded, not paid here.

## Constraints

- **An episode is a RECORD, never a rule.** Nothing written into `episodes/` may be phrased
  as guidance for a future agent. Write what was observed, **in the past tense**. This is
  binding doctrine (`docs/agents/ORCHESTRATOR_CONTEXT.md`, "The Retired Learning Playbook")
  and it binds even though nothing in the task mentions it. A record that says "agents
  should…" fails this gate.
- **Do not create any file at the repo root that names the episode store.**
  `tests/test_retirement_guard.py::test_canon_is_clean` scans for exactly that and it has
  already gone red once in this run. Run it before you finish.
- Run the suite as **`python -m pytest`**, NEVER `python3 -m pytest` — `/usr/bin/python3`
  has no pytest here and returns a non-zero exit that **reads as a red suite and is not
  one**.
- **Never pipe a command into `head`/`tail` and read the exit code.** Redirect to a file
  and capture the command's own `$?`.
- Canonical shared doctrine is `skills/_shared/global-*.md`, never
  `skills/<role>/references/global-*.md` (the installer regenerates those).
- Edit compact-format JSON (`.mcp.json`) as **raw text, surgically**. Never round-trip
  through `json.load`/`json.dump` — it reflows the file and destroys blame. Re-validate
  with `json.load` afterward.
- Windows writes need `encoding='utf-8', newline='\n'` explicitly on **every** write.
- Work only in this worktree. `/home/tommy/projects/constellation-skills` is fenced
  read-only.

## Anchors

**Structural** (map entry points — start at `map/INDEX.md`, then the per-module
`INDEX.md`):
- `scripts/mcp_spine_server.py` `call_tool()` — the `_tool_error()` returns
  (map: `scripts.mcp_spine_server`, 8 entities / 5 holes)
- `scripts/mcp_spine_server.py` `_log()` / `run_engine()` — the only current writer of
  `mcp_calls.jsonl`
- `scripts/apply_episode_delta.py` — READ ONLY; the only write path into `episodes/`
  (map: 54 entities / 25 holes)
- `scripts/episode_capture.py` `_artifact_refs()` / `mechanical_fields()` — READ ONLY; how
  an `artifact-ref` reaches the Mechanical bin (map: 15 entities)
- `scripts/verify_episode_captured.py` — the write-side capture gate

**Constraint:** a capture that fails quietly is the same defect as the door it
instruments. A client-side schema rejection never reaches the server process at all.

**Decision:** `fail-loud-every-turn` (settled/human). `episodes-are-records-not-rules`
(settled/human). `landing-site-is-artifact-ref` (settled/commander).
`cli-arm-not-instrumented-this-run` (settled/commander).

**Confidence flag:** F measured **zero** malformed calls in both DC5 arms. Do **not**
present your instrument as evidence that fumbles exist. You are building an instrument, not
claiming a phenomenon.

## Verification commands

```
python -m pytest -q tests/test_mcp_friction_capture.py
python -m pytest -q tests/test_retirement_guard.py
python .agent-work/epic-418-followon/commander-f2/demo_engine_refusal_reaches_episode.py
python -m pytest -q
```

## Deliverable path check

Run `git check-ignore <path>` for each committed deliverable and confirm **exit 1** (not
ignored) before you finish.

## Authority

Admiral, epic-418-followon, wave 2. The Commander is delegated; the human is AFK. If you
hit something that needs a decision outside this handoff, **say so in your result** rather
than guessing — it will be routed up.

## Result

Write your `IMPLEMENTER_RESULT` — what you built, the evidence with pasted command output,
the coverage-boundary statement required by close criterion 6, anything you could not do,
and a `Workflow Feedback` section — to:
`.agent-work/epic-418-followon/commander-f2/crew-handoffs/g2-implement-implementer-result.md`

**That write is the delivery. Do it before ending your turn.**

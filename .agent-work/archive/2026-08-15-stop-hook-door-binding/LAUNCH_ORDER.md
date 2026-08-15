# Launch Order: `stop-hook-door-binding` — let the Stop hook see the door

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
Read it as written. Where it is wrong, **say so and float rather than quietly working around it.**

## Mission

Six times on 2026-08-15, a Commander ended its turn mid-spine saying it would "resume when the background
job finishes." Nothing resumes it — the process exits at turn end. Each cost a full dispatch and each
looked like progress rather than failure.

**The refusal that would have stopped all six already exists and already works.** This lane makes it
visible on the dispatch path everyone actually uses.

Full evidence:
`/home/tommy/projects/constellation-skills/.agent-work/triage-candidates/auto-backgrounding-breaks-the-foreground-crew-dispatch-contract.md`
(untracked, **primary checkout** — your worktree does not contain it). **Read it in full first.**

## The diagnosis — verify it, do not trust it

1. `scripts/hooks/spine_rail.py:1197-1214` — `_mid_flight_reason` produces exactly the right refusal:
   *"SPINE MID-FLIGHT: gate {aid} is still open — you are in the MIDDLE of the spine … Keep working the
   gate — do not end your turn to wait."*
2. It **fires and works**: the `launcher-hygiene` lane was refused by it mid-run, recorded the refusal
   verbatim in its own episode, resumed, and finished. That is the only lane all day mechanically stopped
   from parking — and its episode notes it had closed a gate via a Bash `checklist_engine.py advance`,
   which is what gave it a binding.
3. It stayed silent for the other six because of **binding, not logic**. `decide_stop`
   (`spine_rail.py:~1255-1261`) opens with `if not sid_bindings: return {}  # no binding -> allow`, and a
   binding is only recorded when the PostToolUse rail sees a **Bash** command containing
   `checklist_engine.py` (`spine_rail.py:689`, `:1094`). A lane driving its spine entirely through the
   **MCP door** (`spine_lease` / `spine_start` / `spine_advance`) never issues such a command.
4. `.claude/settings.json` registers `spine_rail.py PostToolUse` with **`"matcher": "Bash"`** — so the
   rail is never even invoked for a door call. Note the sibling registration for
   `gauge_writer_hook.py` uses `"matcher": "*"`, which proves MCP tool events **do** reach PostToolUse
   hooks in this harness.

**If any of that does not reproduce, stop and report.** The whole lane rests on it.

## The change

Record a binding when the rail observes a **door-issued claim**, so `decide_stop` has something to check.

- Add a PostToolUse registration for the spine door tools. **Prefer a narrow matcher** (e.g. the spine MCP
  tool namespace) over `"*"`: `spine_rail.py:809` states plainly that "a PostToolUse hook runs on the
  turn's critical path," and widening it to every tool call taxes every turn in the repo.
- Teach the PostToolUse handler to derive the same binding from a door call that it derives from a Bash
  `checklist_engine.py claim`. A door payload is shaped differently from a Bash command string — the
  existing path tokenizes `command`; the door path carries structured `tool_input`. **Both must work**,
  and the Bash path must be entirely unchanged in behavior.

**The refusal logic in `_mid_flight_reason` and `decide_stop` needs no change.** If you find yourself
editing it, stop — that means the diagnosis is wrong, which is a finding worth more than a fix.

## Non-negotiables

- **Fail-open, always.** `spine_rail.py`'s whole posture is that a hook which errors, times out, or
  cannot parse must never wedge a turn. A PostToolUse hook `NEVER blocks` (`:1087`). Preserve that
  exactly: a malformed or unrecognized door payload records no binding and raises nothing.
- **No new subprocesses on the PostToolUse path.** `:809` documents that the one existing subprocess is
  deliberate and bounded. Do not add another.
- **Do not make Stop stricter.** You are widening what it can *see*, not what it refuses. A turn end that
  is legitimate today must remain legitimate.

## The evidence bar — both halves, or it does not ship

A Stop hook that misfires wedges **every agent in this repo**, which is far worse than the defect it
prevents. So:

- **RED** — a door-claimed spine with an open gate, at turn end, is now refused (and demonstrably was
  *not* refused before your change).
- **CONTROL** — a legitimate turn end is **not** refused: terminal spine with released lease; foreign
  spine; unreadable/malformed spine; honestly-blocked gate. `decide_stop`'s existing comment enumerates
  these ("every bound entry is foreign/unreadable/closed/honest-blocked -> allow") — cover them.
- **Fail-open proof** — a door payload the handler cannot parse leaves the turn unblocked.

**Without both RED and CONTROL, do not ship it. Report a design instead.** That is a fully acceptable
outcome and the previous lane's decision to decline on exactly this basis was correct.

## A hazard specific to this lane

**You cannot validate the live hook from inside your own worktree.** `CLAUDE_PROJECT_DIR` is fixed at
session launch and inherited, so your process runs the **primary checkout's** hooks and settings, not
your worktree's — this is documented at `skills/admiral/templates/LAUNCH_ORDER.template.md:46-54`.

So: **test the handler functions directly with unit tests**, not by trying to observe your own turn being
refused. Do not conclude from "my own turn ended fine" that anything works or fails. If you want a live
check, the template names the only honest route (a fresh process whose `CLAUDE_PROJECT_DIR` genuinely
resolves to your worktree) — but unit tests over the seam are the expected evidence here.

## `.claude/settings.json` is yours this time — carefully

Every earlier lane today was fenced out of it because concurrent lanes shared it. One sibling lane
(`episode-guard-at-write`) is live but does not touch hooks. **Change only the `PostToolUse`
registration you need.** Do not reorder, retime, or otherwise touch the `Stop`, `SessionStart`, or
`gauge_writer_hook` entries.

## File Ownership

**Yours:** `scripts/hooks/spine_rail.py`, `tests/test_spine_rail.py`, the `PostToolUse` block of
`.claude/settings.json`, your work area.

**NOT yours:** `scripts/checklist_engine.py`, `scripts/run_crew.py`, `scripts/apply_episode_delta.py` and
`scripts/verify_episode_observations.py` (the sibling lane owns those), `scripts/hooks/gauge_writer_hook.py`,
`.mcp.json`, and `.worktrees/episode-guard-at-write/`.

## Do not park — run this as your first action

Your process exits when your turn ends. The suite auto-backgrounds at ~120s, and `checklist_engine.py
advance` re-runs it during postcondition verification, which backgrounds the same way.

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/stop-hook-door-binding
rm -f /tmp/shdb-suite.log
find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +
nohup env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT \
  python -m pytest -q > /tmp/shdb-suite.log 2>&1 &
until grep -qE '[0-9]+ (passed|failed)' /tmp/shdb-suite.log; do sleep 15; done
tail -20 /tmp/shdb-suite.log
```

If a command backgrounds anyway, poll with `TaskOutput(block=true)` or `tail` — stay in your turn. If you
are about to write "I'll resume when…", that sentence ends your run. **Do not dispatch a crew.**

There is an obvious irony available here. Take it seriously instead: you are the lane most likely to be
caught by your own fix, and being caught would be **evidence it works**.

## Your own closeout episodes

Same guard that reds the suite: past tense, describing this run, not addressing a reader; in `workaround`
and `proposed-remedy` kinds do not open a clause with a bare verb; no additions to the exception list.
Known trap: a verbatim quotation in **single** quotes containing an apostrophe (`you're`) breaks the
guard's quote-pairing and leaks a second-person hit — use double quotes for quoted machine output.

## Evidence required

- The reproduction of points 1–4 above, or a report saying which failed.
- RED, CONTROL and fail-open proofs as specified.
- Full clean-env cache-clean suite: **0 failed.** Baseline `main` at `2c46cab8` is **3031 passed,
  6 skipped, 1136 subtests** from inside a worktree.
- Regenerate the map: `python -m scripts.code_map build --root .`; commit if it moves.

## Workspace

Worktree `/home/tommy/projects/constellation-skills/.worktrees/stop-hook-door-binding`, branch
`fix/stop-hook-door-binding`, based on `main` at `2c46cab8`. Work area
`.agent-work/stop-hook-door-binding/`.

`spine_status` must describe `stop-hook-door-binding` — if not, stop and report.

## Stop Conditions

- The diagnosis does not reproduce.
- You cannot produce **both** a RED and a CONTROL.
- The fix would require making `Stop` refuse anything it does not refuse today.
- Green would require a new subprocess on the PostToolUse path, or breaking fail-open.
- Green would require touching anything in the not-yours list.

## Return Shape

What `spine_status` resolved to, named explicitly; the diagnosis reproduction; the change, including the
exact matcher you registered and why not `"*"`; RED, CONTROL and fail-open proofs; clean-env suite counts;
whether the map moved; and anything floated.

**You may push and open a PR. You are fenced from merging.** The Admiral merges.

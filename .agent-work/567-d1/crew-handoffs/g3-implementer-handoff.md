# Implementer Handoff

Work id: `567-d1` · Worktree: `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
Branch: `feat/567-d1-doctrine-sweep-guard`

## Gate

`g3-implement` — Door vocabulary in `specs/*.spine.toml`.

## Task

`specs/implementer.spine.toml` and `specs/reviewer.spine.toml` are this repo's two typed role
specs — the machine-readable statement of what a gated implementer plan and a survey reviewer plan
*are*. Measured: **both carry zero mentions of the door**, and these two are the only role specs
that exist.

Epic #567's thesis is *"the door is the interface, not a second path."* A role spec that never
names the door is a role spec written before that was true. Give both **door vocabulary that matches
measured behaviour** — not aspiration, and not a path the measurement shows does not exist.

## The two facts your vocabulary must state, and they pull in opposite directions

**1. A role whose OWN spine is bound drives it through the door.** No session id argument: the
process was launched with `SPINE_FILE` and an assignment-keyed `SPINE_SESSION` in its environment,
so the door resolves to that spine at startup. The verbs are `spine_status`, `spine_start`,
`spine_advance`, `spine_evidence`, `spine_lease`, `spine_capture`, `spine_halt`, `spine_amend`,
`spine_bind`.

**2. A role driving a SECOND checklist cannot use the door — measured, in a fresh process:**

| step | result |
|---|---|
| `spine_lease claim` on own spine | OK |
| `spine_bind` to a second checklist **while holding that lease** | **REFUSED** — *"one door drives one spine at a time"* |
| release the lease, then `spine_bind` | succeeds |

And the escape in step 3 is barred: the archive gate requires the lease to cover every journaled
action, so an agent that released its lease to bind a second checklist fails its own closeout.
`_spine_bind`'s docstring names the governing decision: `decision:one-spine-per-process-stands`.

**This is exactly the situation of both files you are editing.** A dispatched implementer's own
`IMPLEMENTER_PLAN.json` and a reviewer's own `REVIEW_SURVEY.json` **are** second checklists.
Confirmed independently four times over in this epic: lanes F and H each drove their `execute.json`
under a hand-supplied CLI session id, lane E's implementer drove its `IMPLEMENTER_PLAN.json` the
same way, and **every crew this lane dispatched did the same** — this Commander is doing it right
now for `execute.json`.

So the honest vocabulary says both halves: **the door is the interface for the spine you were
launched against; a second checklist is not that spine, and the reason is a measured refusal, not an
oversight.** Do not promise a door path the measurement shows does not exist, and do not leave a
reader with no path at all.

## Settle one design question and state which and why

**Does this need new schema keys, or only prose?** Read `scripts/generate_spine.py` and the specs'
own structure before deciding. Both files already carry typed postconditions with `kind`,
`statement` and `because` fields, and `because` is where a spec explains itself. Prose in the right
existing field may be the whole answer — the plan's own leaning is *prose, not new keys* — but that
is a leaning, not a ruling. **Say which you chose and why**, and if you add a key, say what
consumes it.

## The constraint that makes this gate interesting

**Your new prose is inside the guard's walk.** The cold plan critic flagged that `specs/` was a
fresh, unguarded surface for exactly the kind of text this epic controls; gate `g1` closed that by
extending `tests/test_cli_retirement_guard.py` to walk `specs/**/*.toml`.

So the guard is now watching the file you are writing. It forbids, in this file:

- the `<engine>` token — or **any** placeholder-shaped stand-in followed on the same line by an
  engine verb (`<cli> claim`, `{{engine}} release`, `$ENGINE advance`, …);
- the phrase `CLI fallback` in any punctuation form, including `CLI-fallback`;
- a **command-shaped** `checklist_engine.py` reference: reached by a path or an interpreter, or
  followed by a long flag or an engine verb.

**You may name the engine as a component. You may not show the command.** That is the line, and it
is pinned in the guard's own tests. If you conclude the vocabulary genuinely needs to show a command
line, **stop and return** — that is a Commander decision, not a pattern to widen.

`python3 -m pytest tests/test_cli_retirement_guard.py -q` must report **no** violation at any
`specs/` address after your change. (It will still report violations under `skills/workbench/` —
lane D2's fenced files, which this lane does not sweep and which `g5-final` re-checks after the
rebase. **Expected, not yours.**)

## Also record, do not necessarily fix

Both specs set `config_ref = "docs/agents/engine-config.json"`, and **that file does not exist in
this repo**. Record it in your result with the evidence; fixing it is out of scope unless you can
show the fix is free and obviously right, in which case say so and do it deliberately.

## Close criteria

1. Both `specs/implementer.spine.toml` and `specs/reviewer.spine.toml` name the door.
2. Both state the second-checklist truth — that the door refuses to rebind while the process holds
   its own lease.
3. `python3 -m pytest tests/test_cli_retirement_guard.py -q` reports no violation at any `specs/`
   address.
4. Both files still parse as TOML.
5. The schema question (new keys vs prose only) is settled and the reasoning stated.
6. The dangling `config_ref` is recorded with evidence.

## Allowed scope

- `specs/**`
- Nothing else. Read anything you like.

## Fenced — do not edit

`skills/workbench/**`, `docs/agents/CREW_CONTEXT.md` (lane D2); `scripts/mcp_spine_server.py`,
`episodes/**` (lane E); `scripts/run_crew.py` (lane F); `scripts/checklist_engine.py` (lane H);
`map/INDEX.md` (Admiral). And **`tests/test_cli_retirement_guard.py`** — the guard is not yours to
edit to make your prose pass.

## Constraints

1. **Do not promise a door path the measurement shows does not exist.**
2. **Your new prose is inside the guard's walk — it must not itself trip the guard.**
3. Do not promote any observation into `docs/agents/*` — the human's call.
4. File **no** issues. Stage triage candidates under `.agent-work/567-d1/triage-candidates/`.

## Map anchors (inbound)

No architecture map exists in this repo (`map_orient` → `DEGRADED-UNPARSEABLE`). Entry points:

- `specs/implementer.spine.toml`, `specs/reviewer.spine.toml` — the two files, ~90 lines each.
- `scripts/generate_spine.py` — what consumes a spec; read it before adding a key.
- `scripts/mcp_spine_server.py`, `_spine_bind` — the refusal text and
  `decision:one-spine-per-process-stands`. **Read-only: lane E owns this file.**
- `tests/test_cli_retirement_guard.py` — the guard now watching `specs/`; its docstring lists what
  it deliberately does not enforce.
- `.agent-work/567-d1/notes-1.md` §M1 — the fresh-process probe that measured the refusal.

## Deliverable path check

`git check-ignore specs/implementer.spine.toml` → exit 1. `git check-ignore
.agent-work/567-d1/crew-handoffs/g3-implementer-result.md` → exit 1. Verified.

## Verification commands

```sh
cd /home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard
python3 -c "import tomllib;[tomllib.load(open(p,'rb')) for p in ['specs/implementer.spine.toml','specs/reviewer.spine.toml']];print('toml ok')"
grep -i 'door' specs/implementer.spine.toml specs/reviewer.spine.toml
python3 -m pytest tests/test_cli_retirement_guard.py -q > /tmp/g3.log 2>&1
grep -oE 'specs/[A-Za-z0-9_./-]+' /tmp/g3.log | sort -u        # MUST print nothing
git status --porcelain
```

The gate's own closing check, which the Commander re-runs independently. **POSIX form** — the engine
runs `command` checks through `/bin/sh`, which is `dash` here, and `set -o pipefail` is rejected
outright with exit 2. This lane has already paid for that once; do not reintroduce it.

```sh
grep -qi 'door' specs/implementer.spine.toml && grep -qi 'door' specs/reviewer.spine.toml \
  && grep -qi 'second checklist\|own lease\|one door drives one spine' specs/implementer.spine.toml \
  && grep -qi 'second checklist\|own lease\|one door drives one spine' specs/reviewer.spine.toml \
  && { python3 -m pytest tests/test_cli_retirement_guard.py -q > /tmp/g3-guard.log 2>&1 || true; } \
  && ! grep -oE '(skills|specs|[.]agent-work)/[A-Za-z0-9_./-]+' /tmp/g3-guard.log | grep -qv '^skills/workbench/'
```

**Do not run the whole suite while driving your own plan through the engine.**
`tests/test_gauge_chain_writer_to_trip.py:604` snapshots the size and mtime of every file under the
repo's `.agent-work/` and asserts nothing moved, so your own engine records produce a failure that is
yours. A sibling crew in this lane hit exactly that and nearly reported it as someone else's defect.

## Test mode

**No new runtime behaviour**, so no new test is owed. The existing guard is the check, and it is
already watching `specs/`. If you add a schema key, say what test covers it.

## Required evidence

- The before and after text for both files, quoted.
- The schema decision (keys vs prose) and the reasoning.
- The guard run showing no `specs/` address.
- The `config_ref` finding with its evidence.

## Suggested model tier

**Opus.** The wording is doctrine that ships, and it has to state a measured refusal without
sounding like an apology or promising a path that does not exist.

## Authority

Commander `567-d1`, under Admiral launch order `cmdr-567-d1` (epic #567, wave 2, lane D1).

## Stop conditions

Stop and return if: the vocabulary genuinely needs to show a command line; a schema key would need a
consumer that does not exist; or the guard fires on prose you believe is legitimate.

## Return format

Write the full `IMPLEMENTER_RESULT` to
`.agent-work/567-d1/crew-handoffs/g3-implementer-result.md` **before ending your turn** — that write
is the delivery. Include a `Return status` field whose value is exactly `complete` (lowercase) when
the close criteria are met. Include a `Workflow Feedback` section: what helped, what got in the way,
and your own mistakes.

# Review Result — A, round 2 (cold)

**Work id:** `epic-559/a-spine-is-the-job` · **Gate:** `g3-review2` · **Role:** reviewer
**Under review:** `554c553a`, `2152ded3`, `99336f96`, and the branch as an integration against `main`@`9d593e0a`
**Survey:** `.agent-work/epic-559/a-spine-is-the-job/REVIEW_SURVEY2.json` (12 items, all recorded, consolidated)
**Fowler record:** `.agent-work/epic-559/a-spine-is-the-job/FOWLER_PASS2.json` (`verify_fowler_pass.py` exit 0)

## Assigned Gate
`g3-review2` — reviewer

## Result
`BLOCK`

## The question that was supposed to decide it

It answers safely. `checklist_engine.TERMINAL` is `{"complete", "skipped"}`; `blocked` is not in it.
I drove real spines through the engine and read `spine_terminal` on each:

| spine state | `spine_terminal` |
|---|---|
| every gate `complete` | `True` |
| `g1` **blocked**, `g2` pending | `False` |
| `g1` complete, **last gate blocked** | `False` |
| every gate `skipped` | `True` |
| `g1` complete, `g2` check REFUSED then `skip`ped | `True` |
| survey, every item recorded, **not consolidated** | `True` |
| `{}` / `{"items": []}` | `True` |
| missing file / unparseable / truncated | `False` |

**A crew that correctly blocks and asks up is recorded `failed`, not `completed`.** The feared
false positive does not exist. The verdict does not turn on it.

It turns on two other things.

## Blockers

### 1. `run_crew.py` is dead on every installed skill bundle (v3)

`2152ded3` added `import install_constellation` at module scope. `install_constellation.py` ships
in no bundle that carries `run_crew.py` — only `write-a-skill` gets it, and `write-a-skill` has no
`run_crew.py`.

```
$ python scripts/install_constellation.py --agent claude --scope project \
      --dest /tmp/instsim/skills --skills commander --force
$ cd /tmp/bare-target
$ python /tmp/instsim/skills/constellation-commander/scripts/run_crew.py --help
Traceback (most recent call last):
  File ".../constellation-commander/scripts/run_crew.py", line 43, in <module>
    import install_constellation
ModuleNotFoundError: No module named 'install_constellation'
EXIT=1
```

Two-sided against `main`, same install, same invocation:

```
$ python /tmp/mainsim-inst/skills/constellation-commander/scripts/run_crew.py --help
usage: run_crew.py [-h] [--work-id WORK_ID] ...
EXIT=0
```

Same for the explorer bundle. This fails at import, before argparse — so **Commander and Explorer,
running from an installed install, can launch no crew at all.** That is the sanctioned invocation:
`global-everyone.md` says to reference bundled scripts by their absolute installed path, and the
Commander skill's standing rule is to run every dispatch through `run_crew.py`.

The repo already documented this exact drift class, at `scripts/install_constellation.py:80-88` —
*"if a script reaches a sibling by `sys.path.insert` + a plain import, ship that sibling too, or the
feature silently no-ops wherever the skill is actually installed"* — recorded because the last
occurrence left the Context Governor inert in every install since it shipped. The guard written to
stop it recurring reads `SCRIPT_RUNTIME_COMPANIONS.get("checklist_engine.py", ())`, so it is
structurally blind to a sibling import added to any other script. The defect recurred one file over
from where it was documented, and the suite stayed green.

**Fix:** add `"run_crew.py": ("install_constellation.py", ...)` to `SCRIPT_RUNTIME_COMPANIONS`, and
key the guard test on every declared script rather than one literal.

Note the import the survey item asked about — `checklist_engine` — is clean: stdlib-only top-level
imports, no `SPINE_FILE`/`os.environ` read at module scope, no cycle, and it is already an explicit
companion of both bundles. The neighbour added in the same commit is the load-bearing one.

### 2. A reviewer crew that produces no verdict is recorded `completed` (v1)

`spine_terminal` answers a `survey` question with `checklist_engine.active_id`, which walks item
statuses and never looks at `consolidation`. Reproduced with a **real dispatch**, not by reading:

```
$ python scripts/run_crew.py --work-id probe2-rev2 --gate p3survey --role reviewer \
      --model sonnet --spine .../probe2/SURVEY.json --backend cli
crew constellation/probe2-rev2/p3survey/reviewer/attempt-1 -> completed

survey  : type=survey  items {i1: complete/pass, i2: complete/pass}  CONSOLIDATION: None
registry: status=completed  exit_code=0  result=null
```

The Commander is told the review is done. There is no verdict anywhere. This is the false-positive
class the handoff named as worse than the round-1 bug, landing in the one role whose entire
deliverable is the verdict, at the exact failure `reviewer/SKILL.md` calls *"the single most common
failure at this tier"*.

Reachability is not theoretical: `--spine` accepts any checklist type, the spine-only prompt is
type-agnostic (*"Drive it gate by gate ... until it reports done"* — a survey has no gates),
reviewer and interrogator checklists **are** surveys, and this very survey is one.

**Fix:** `spine_terminal` should require `consolidation is not None` for `type == "survey"`. The
cleaner shape is a type-aware `is_terminal(checklist)` owned by `checklist_engine` — but that file
is a hard no-go here, so the guard belongs in `run_crew` for now with the seam noted.

Second, smaller, same function: `spine_terminal` returns `True` for `{}` and `{"items": []}`,
directly contradicting its own docstring — *"A missing/unparseable/malformed spine is never terminal
-- absence of evidence is not evidence of completion."* Genuinely missing and unparseable files do
return `False`; it is valid-JSON-wrong-shape that leaks.

## Handoff compliance

Both requested fixes are present and demonstrated. `--result` is optional wherever `--spine` is
given, across `CrewSpec`, `build_entry`, `finalize_from_exit_code` and argparse; completion for a
spine-only dispatch is `spine_terminal`. The hook emits `shlex.quote(sys.executable)` with
`"shell": "bash"`, and the bare `assert` on `WAIVE_DENY_REASON` raises. What was asked was
delivered; the blockers are damage it caused elsewhere.

**The round-1 bug is fixed, and I confirmed it by running one (v2), both directions:**

```
POSITIVE  --spine, NO --handoff, NO --result
  -> crew constellation/probe2-rev2/p1/implementer/attempt-1 -> completed
     registry: handoff=null result=null exit_code=0 result_present=false
     spine: g1 complete, c1 satisfied; the crew wrote pos.txt = PROBE-POS-OK

NEGATIVE  same shape, spine's g2 left pending on purpose
  -> crew constellation/probe2-rev2/p2neg/implementer/attempt-1 -> failed
     registry: exit_code=0 (!)   spine: {g1: complete, g2: pending}
```

The launcher recorded `failed` on a child that exited 0, purely on the spine read. The check is not
a check that cannot fail.

## Scope drift

None. `git diff --name-only 9d593e0a..HEAD` touches only `map/INDEX.md`, `scripts/run_crew.py`,
`skills/{implementer,reviewer}/SKILL.md`, `tests/test_crew_launcher.py`,
`tests/test_mcp_adoption.py`. All five hard no-gos hold: `checklist_engine.py`,
`mcp_spine_server.py`, `settings.json`, `docs/agents/*`, and `skills/*/templates/` are untouched.
Nothing pushed to `main` — `origin/main..HEAD` is the four branch commits, `main` itself unmoved.
The two `SKILL.md` edits are the spine-is-bound paragraph, not the regenerated
`skills/<role>/references/` copies `CREW_CONTEXT.md` forbids editing.

## Evidence verdict

Suite green: `2556 passed, 1 skipped, 1101 subtests passed` under the handoff's test mode.
`map/INDEX.md` reproduces byte-exact — I re-ran `python -m scripts.code_map build --root .` and
`git status map/` is clean.

The evidence that is present is honest. `SpineOnlyCompletionContractTests` never writes a result
artifact, and it carries a real negative control plus exit-code and missing-file controls.
`HookPortabilityTests` proves the shell-safety guard is wired by forcing it to raise, rather than
asserting it is called.

What is missing is coverage of the states the decider can actually reach. `_write_spine(done=False)`
only ever produces `pending`. Nothing exercises a `blocked` spine, a `skipped` spine, a
`survey`-typed spine with no consolidation, a structurally-malformed spine, an installed-bundle
import, or a `sys.executable` containing a space. Four of those are the two blockers and the
v5 regression.

## Code/doc quality

Fowler pass recorded, `verify_fowler_pass.py` exit 0: 12 smells, 6 flagged, 1 overridden with a
logged standard. Two flags are load-bearing rather than stylistic.

**Feature envy** — `spine_terminal` lives in `run_crew.py` but decides what *terminal* means for a
checklist, by calling a gated-spine API whose blind spot the caller cannot see from outside the
seam. That is precisely how blocker 2 got in.

**Comments as deodorant** — two docstrings assert properties I disproved by running them:
`spine_terminal`'s *"a malformed spine is never terminal"*, and `crew_settings_json`'s
*"`shlex.quote` covers an interpreter path containing spaces"*, which produces the opposite outcome
(see v5 below). The prose is doing reassurance the code has not earned, which is this smell in its
most consequential form.

Against the inherited rules: the change violates `global-everyone.md`'s *"enumerate the blast radius
of your own change, by command, never by memory"* — nothing enumerated who ships `run_crew.py`
before adding a module-scope sibling import to it.

## Also failing — not blockers on their own

**v5 — the argv moved for every dispatch, and one host class loses entirely.** The completion
contract itself is clean; I drove the whole matrix through `finalize_from_exit_code`:

| given | spine | exit 0 | exit 1 |
|---|---|---|---|
| result only, fresh | — | `completed` | `failed` |
| result only, missing | — | `failed` | `failed` |
| **both**, result missing | terminal | `failed` | `failed` |
| **both**, result fresh | blocked | `completed` | `failed` |
| spine only | terminal | `completed` | `failed` |
| spine only | blocked | `failed` | `failed` |

Exactly as claimed: `--result` given is judged as before, both-given keeps the old result-based rule,
nonzero exit always fails. The handoff-branch prompt is byte-identical to `main`'s.

But `build_crew_argv` now calls `crew_settings_json()` on **every** dispatch, and that calls
`assert_shell_safe_command` on `shlex.quote(sys.executable) + " -c '...'"`. With a spaced
interpreter path, `shlex.quote` adds a leading quote and the guard — which refuses any command not
starting with a bare word — raises:

```
'/usr/bin/python3'                          -> OK
'/opt/Program Files/py/python.exe'          -> InstallError: refusing to emit a hook command ...
'C:\Program Files\Python312\python.exe'     -> InstallError: refusing to emit a hook command ...
```

Python under `Program Files` is a stock Windows install. On such a host **no crew can be dispatched
at all**, classic `--handoff --result` dispatches included. It is fail-closed and loud, which is why
it is a regression rather than a safety hole — but it is total-loss on a platform this repo
documents at length, and `HookPortabilityTests` only ever exercises the running host's own
space-free `sys.executable`, so nothing catches it.

**v4 — the hook is portable now; the property is still best-effort, and nothing says so.** The two
named modes are genuinely fixed. Four remain:

1. **Reachable, and it defeats the mechanism.** The matcher is `mcp__spine__spine_evidence`, but
   `Bash` is in `CREW_ALLOWED_TOOLS` and the engine has a `waive` verb. I drove it: a crew running
   `checklist_engine.py waive g1 --cond c1 --authority crew --reason ... --force` waived its own
   unsatisfiable check, advanced the gate to `complete`, and `spine_terminal` read `True`. The hook
   guards the door while the crew holds the key to the side entrance. The ruling it implements —
   *"agent cannot waive itself, always ask up"* — is unenforced against any crew that reaches for the
   CLI, which the handoff records the previous crew doing. Mostly pre-existing (`Bash` was granted in
   `832aeee7`), but `2152ded3`'s subject line claims the hook *"cannot fail open"*, which is stronger
   than the code supports.
2. **Reachable.** Malformed or empty stdin makes the hook program raise (`rc=1`); an erroring
   `PreToolUse` hook is treated as no opinion. Measured: `waive` → deny JSON `rc=0`; `attest` → `{}`
   `rc=0`; malformed stdin → `rc=1`; empty stdin → `rc=1`.
3. `"shell": "bash"` requires bash on PATH — on a Windows host without Git Bash the hook cannot run.
   The docstring justifies adding it but never notes it trades one Windows failure for another.
4. An interpreter moved or removed between dispatch and hook fire.

The code says "fail open" only about the two modes it fixed. The standing property is unstated, and
the Bash bypass is unmentioned. The item allows an accepted risk stated; it is not stated.

## Map impact verdict

- **Evidence supports claimed change:** yes for the spine-only contract (real dispatches, both
  directions); no for `2152ded3`'s "cannot fail open" — the claim exceeds the evidence.
- **Constraints not violated:** all five hard no-gos respected.
- **Notes match the diff:** `map/INDEX.md` regeneration is mechanical and reproduces byte-exact
  (`scripts.run_crew` 53 → 55 entities).
- **Decision candidates surfaced:** the `skip`-as-escape-hatch question needed authority the
  implementer lacked and was not surfaced; flagged as a triage candidate here instead.
- **Durable context routed:** two triage candidates recorded in the survey.

## Reconciliation check

No divergence requiring Commander reconciliation. One item for Cartographer: the launcher now
depends on `checklist_engine` and `install_constellation` at module scope — a new script→script edge
the map's module-level `INDEX` does not express. Once the companion declaration lands (blocker 1),
that edge becomes an install-time contract worth recording.

## Out-of-scope observations

- **`tc1` — a crew can `skip` its way to `completed`.** `spine_halt action=skip` is in the crew tool
  grant, needs only a reason and no authority, and `skipped` is in `TERMINAL`. Reproduced: a gate
  whose postcondition REFUSED, then skipped, reads terminal. Same shape as the waive problem and
  deserves the same treatment — deny `skip` to a crew, or require an authority it does not have.
  Out of scope: the fix is in the tool grant or the engine, both no-go files here.
- **`tc2` — the waive-deny hook is bypassable via Bash** (detail under v4 above).
- **Worth Commander's attention, not a defect:** every real dispatch in this wave is *both-given*
  (handoff + result + spine), including mine. Both-given is judged on the result artifact, so the
  "blocked is not terminal" protection that makes v1 safe applies to **none** of them today. A crew
  that blocks its spine but writes a result file is still recorded `completed`. That is the
  documented, unchanged both-given rule — but it means the property this rework was checked against
  is not yet the property in force for the dispatches the repo actually issues.

## Workflow Feedback

- **Handoff gaps:** none in the fields — the handoff was unusually good, and its "what round 1
  already settled, do not redo it" section saved real budget. One framing note: it stated the
  decisive question as *"if `active_id()` returns `None` for a blocked spine ... that is a BLOCK"*,
  which is a hypothesis about one status. The class is wider than the hypothesis — I found the false
  positives in `skipped` and in survey consolidation, not in `blocked`. A reviewer who checked only
  the named condition would have answered the question correctly and reported APPROVE. Naming the
  *class* ("enumerate every state that reads terminal") rather than the suspected instance would
  have been strictly better, and it costs nothing.
- **Context rediscovered:** which interpreter has pytest (`python`, not `python3`) was in the
  handoff's test mode and matched `CREW_CONTEXT.md` — good. What I had to dig up was the install
  layout: that `SCRIPT_RUNTIME_COMPANIONS` exists, that it is keyed per-script, and that the
  commander/explorer bundles carry `run_crew.py`. None of that is reachable from the diff, and it is
  where blocker 1 lives. A handoff line naming which bundles ship a changed script would have pointed
  straight at it — and would have been just as useful to the implementer.
- **Instructions improvised around:** `reviewer/SKILL.md` says to instantiate the survey from
  `templates/REVIEW_SURVEY.template.json` and claim the lease as the first command. My survey was
  already instantiated and bound by the dispatch, so I claimed and drove it — the skill's own new
  spine-is-bound paragraph (added by this branch) covers this, but the older "Start here" section
  above it still reads as build-your-own. The two paragraphs in the same file disagree.
- **What would have made this easier:** a way to drive a *scratch* spine through the door. My door is
  pinned to `SPINE_FILE`, so every probe in v1 had to go through the engine CLI — the exact behaviour
  this wave is trying to remove, forced by the tooling rather than chosen. Disclosed at the time and
  again in the v1 record. Every claim about the *branch's* behaviour came from `run_crew` and real
  dispatches; the CLI was only ever used to manufacture spine states.

## Return status
`complete`

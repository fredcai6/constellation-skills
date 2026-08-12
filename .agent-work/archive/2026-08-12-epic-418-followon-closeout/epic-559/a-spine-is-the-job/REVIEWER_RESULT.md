# Review Result — A: the spine is the job, not a document beside it (#559)

**Work id:** `epic-559/a-spine-is-the-job` · **Gate:** `g2-review` · **Role:** reviewer (cold)
**Under review:** commit `6fc83013` against `main`@`9d593e0a`, plus `IMPLEMENTER_RESULT.md`
**Survey driven:** `.agent-work/epic-559/a-spine-is-the-job/REVIEW_SURVEY.json` (13 items shipped + 1 appended, all visited, consolidated)
**Fowler pass record:** `.agent-work/epic-559/a-spine-is-the-job/FOWLER_PASS.json` (rail exits 0)

## Verdict

**BLOCK** — 3 blockers, 2 observations, 2 triage candidates.

The design is right and the load-bearing claim is real. I dispatched an actual spine-only crew and
it worked. What blocks is a contract the change did not follow through, and a denial mechanism that
fails open on any host that is not this one.

## What I personally ran

| Claim | How I checked it | Result |
|---|---|---|
| A crew can work from a bound spine with no handoff | Built a scratch two-gate spine, dispatched a real crew with `--spine` and **no** `--handoff` via `run_crew.py --backend cli --model sonnet` | **Works.** Spine driven to `DONE`, lease released, exit 0 |
| The waive denial fires in a real dispatch | Made the probe condition genuinely waivable, so only the hook could refuse it | **Denied**, with `WAIVE_DENY_REASON` byte for byte |
| `attest`/`attach` still work behind the same tool | Same run, same tool | **Both succeeded**; spine reached done |
| `--settings` merges rather than replaces | 4 probes against installed `claude` 2.1.227 | **Merges**, additively, even same-matcher |
| Hook failure semantics | Inline hook with a missing interpreter | **Fails open** — tool call proceeds silently |
| Full suite | `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE ... pytest -q tests` | `2548 passed, 1 skipped, 1101 subtests` — matches the claim |
| TDD red | Checked out `main`'s `run_crew.py` in place, reran | `14 failed, 98 passed` → restored → `112 passed` — matches the claim |
| Replacement pin is two-sided | Put the old CLI text back in both SKILL.md files, reran | **Went red**, restored → green |
| Every hard no-go | `git diff` per path | All held |

Evidence lives at `/tmp/r4a-probe/` (spine, journal, crew stdout, the crew's own `probe_report.txt`)
and `/tmp/r4b-probe/` (settings probes).

## Blockers

### B1 — A spine-only crew that fully succeeds is still recorded `failed` (`r4g`)

My crew drove its spine to done, released the lease, exit code 0 — and `run_crew.py` printed
`crew constellation/epic-559/r4a-probe/g0-probe/implementer/attempt-1 -> failed`. The registry
records `status: "failed"`, `result_present: false`, `result_fresh: false`.

The change moved a crew's **input** from a document to the spine and left its **completion contract**
a document:

- `main()` still hard-requires `--result` (`missing = [n for n in ("work_id","gate","role","result")]`).
- `CrewBackend.verify` decides `completed` vs `failed` purely on that artifact existing and being fresh.
- The new spine-only prompt never mentions a result artifact. It ends *"until it reports done"* —
  where the handoff prompt it replaces ends *"The run is only complete when the result artifact the
  handoff names exists."*

So the crew is told its job ends at spine-done while the launcher judges it on a file nobody asked it
to write. Every honest spine-only dispatch reports failed, the duplicate-guard keeps holding the gate,
and `recover_crews.py` sees an unresolved run — a false negative handed to the dispatching Commander.

**No test covers this.** The only test named for it,
`SpineOnlyDispatchTests::test_main_cli_spine_only_dispatch_succeeds`, passes
`fake_launch(RC, 0, write_result_at=root / result)`: the harness writes the artifact the real crew is
never told to write, so it passes for a reason that does not exist in production.

**Smallest fix** — either thread the result path into `build_crew_argv`'s spine branch and end the
prompt with the same completion clause the handoff branch carries, or judge a spine-only dispatch on
its spine reaching a terminal state. The first is smaller; the second is the epic's own thesis. Either
way the covering test must not fake its own precondition.

### B2 — The waive denial fails open, and hardcodes `python3` (`r4d`)

Measured: an inline `PreToolUse` hook whose command is a missing interpreter lets the tool call
through, silently — no error, no denial. Same for a hook that exits 0 printing non-JSON.

`crew_settings_json` emits the literal `python3 -c '...'`. On any host where `python3` is not the
name — Windows with only the `py` launcher, or a box with only `python` — the hook does nothing and a
crew **can** waive its own bound spine check. The human's ruling is then unenforced with no signal at
all: a hidden fallback in the one mechanism whose entire job is to refuse.

The repo already forbids this in its own words. `install_constellation.py::build_hook_command`:

> `interpreter` comes from the run's single `resolve_interpreter()` probe — **never re-probed here,
> never hardcoded** … no single interpreter name works on every platform, which is why the git-tracked
> `settings.json` names none (#539).

And the human's short-term allowance does not apply: `git diff main...HEAD | grep 539` finds nothing.
The one condition attached to the allowance — record it against #539 — is unmet.

**Smallest fix** — `run_crew.py` is itself a running Python process, so it needs no probe at all:
emit `shlex.quote(sys.executable)`. One line, correct by construction everywhere, since the
interpreter that launched the launcher is by definition present. Add a test that the emitted
command's `argv[0]` is not the literal `"python3"`.

### B3 — The inline hook command is POSIX-only, and its guard is stripped under `-O` (`r4f`)

Three findings, in descending severity:

1. **Non-POSIX parse is broken.** `shlex.split(cmd, posix=False)` leaves `argv[2]` as
   `"'import json,sys\n…'"` — the single quotes are not stripped. `cmd.exe` treats a single quote as an
   ordinary character, so Python would receive a program whose first character is an apostrophe and
   die on a `SyntaxError`. With B2's fail-open, the denial vanishes rather than erroring. The repo's
   own `.claude/settings.json` sets `"shell": "bash"` on all four of its hook entries;
   `crew_settings_json` emits `{"type","command"}` with no `shell` key. Adding it is the cheap half.
2. **The `assert` is the wrong mechanism.** `WAIVE_DENY_REASON` is genuinely the only interpolated
   value — I verified no single quote survives anywhere in the emitted program, so today's coverage is
   complete. But a bare `assert` is stripped under `python -O` (confirmed: `__debug__` is False), so a
   future apostrophe would silently emit a malformed command. `assert_shell_safe_command()` already
   exists for this and raises.
3. **POSIX itself is sound.** `shlex.split` yields exactly 3 args and the program compiles; the real
   dispatch proves a real shell runs it.

*Not tested:* an actual Windows host. (1) is a parse-level demonstration plus the repo's documented
Windows posture, not an observed Windows failure.

## Observations (not blocking)

- **`r3` — the evidence reproduces exactly and still does not demonstrate the behavior.** Nothing was
  overstated: I reproduced the suite and the TDD red identically. But `global-crew.md` says
  *"generated advice/hint/recovery text → EXECUTE the advice … string-matching the rendered text is
  not evidence"*, and both behavioural claims here are generated agent-facing text evidenced by
  string-matching it. Both happen to be **true** — I executed them and they hold — but that is my
  evidence, not the branch's, and executing them is what exposed B1.
- **`r4-quality` — the blast radius was not enumerated.** Making `--handoff` optional changes what a
  crew is judged on; the artifact asserting that (`CrewBackend.verify` + `main()`'s required list) was
  never enumerated. That is the authoring-side twin of the rule this review applies.
- **Fowler `shotgun-surgery`** is the same defect seen structurally: nullable-handoff required
  coordinated edits at eight sites, and it missed the ninth.

## What is genuinely good, and should not be re-litigated

- The handoff branch is **byte-identical** and pinned by a literal-string test, so no existing dispatch
  moved. This is the right way to make a risky change safe.
- The `PreToolUse`-hook-via-inline-`--settings` mechanism is a genuinely good answer to "grant a
  multi-action MCP tool but deny one action", which `--allowedTools` cannot express. It works. It just
  needs to work everywhere.
- The deleted pins in `tests/test_mcp_adoption.py` are the right deletion. I enumerated all three
  consumers of `TIER2_SKILL_FILES`: every one asserts the CLI-presence fact the human ruling
  deliberately overturned, so the removal is coextensive with the overturned fact and nothing unrelated
  rode along. The replacement is proven two-sided by mutation.
- Scope held on every hard no-go: `checklist_engine.py`, `mcp_spine_server.py`, `settings.json`,
  `docs/agents/*` and all skill templates untouched; nothing deleted; `origin/main` still at `9d593e0a`.
- The `CREW_ALLOWED_TOOLS` escape hatch was used as designed, not improvised around.

## Triage candidates

1. **`tc1` — stale pins.** `tests/test_mcp_adoption.py`'s `DOOR_TOOL_NAMES` (7) and `CLI_ONLY_VERBS`
   (`skip, reopen, append, amend, flag-candidate`) assert a fact merged N1 already overturned:
   `TOOL_NAMES` is 9, and all five verbs are reachable through the door (`spine_halt`'s enum carries
   `block/resume/skip/reopen`, `spine_capture`'s carries `append/flag-candidate`, `spine_amend` covers
   `amend`). Pre-existing; correctly left alone here. A pin asserting a false fact is worse than no pin.
2. **`tc2` — installed-skill lag makes job 3 inert until a reinstall.** The installed
   `~/.claude/skills/constellation-{implementer,reviewer}/SKILL.md` are copies dated Aug 9 still
   carrying the pre-#559 CLI-fallback paragraph. Every crew dispatched today — **including me, on this
   gate** — reads the old text. Not a defect in this diff, but the ruling *"the agents should not know
   about the CLI. period."* is not in force on this machine until `install_constellation.py` runs, and
   nothing on the branch says so.

There is an upside worth recording: my spine-only probe crew drove its spine correctly **while reading
the stale skill that tells it to build its own plan**. The prompt alone beat contrary doctrine. That is
a stronger result for job 1 than the branch claims for itself.

## Driving my own spine through the door

I used the `mcp__spine__*` tools throughout and never reached for the engine CLI for my own survey —
except once, deliberately and disclosed: I ran `checklist_engine.py current --file` against my
**scratch probe spine** (a different file, not my bound one) to sanity-check the fixture before
dispatching, because the door binds exactly one spine and inspecting a second one is not something the
door can do. That is a real gap in the door, not a lapse in doctrine.

My own `spine_evidence` calls behaved exactly as designed: `attest` and `attach` worked, and I never
needed a waive. The one refusal I hit was correct — `record r6-fowler` was refused because its `c1`
command still carried the unsubstituted placeholder `<fowler-pass-record-path>`. I took the item's
documented repair path (`spine_amend`, one `retext-check` op, authority Admiral) rather than
hand-editing the survey.

## Workflow Feedback

- **The survey I was dispatched with shipped a live placeholder.** `r6-fowler`'s `c1` command was
  `python scripts/verify_fowler_pass.py <fowler-pass-record-path>` — never substituted at instantiation
  time, which the item's own imperative calls the "NORMAL PATH". The rail caught it and the repair path
  worked, so no harm done. But the instantiation step that was supposed to resolve it did not, and
  nothing checks for a residual `<…>` placeholder in a survey before it is handed to a crew. A
  one-line lint at dispatch would have turned a mid-review detour into a pre-flight refusal.
- **The handoff was unusually good and I want to say why, precisely.** Telling me what had *already*
  been verified by the Admiral — the file count, the suite number, the grant growth, the escape hatch —
  let me spend my whole budget on the three untested things instead of re-deriving settled facts. That
  is the single highest-leverage thing a reviewer handoff can do, and most do not do it.
- **`r4a` was the right instruction and it is the one that found the bug.** "Run one" is worth more
  than any amount of reading. Everything I found that matters came from executing rather than reading:
  the `failed` status, the fail-open hooks, the merge semantics. Handoffs of this shape should keep
  naming a *run it* item explicitly, because the default gravity of review is toward reading.
- **One handoff gap, small:** the "Hard no-gos" list said *"spine templates not changed (another crew
  owns those)"* without naming which crew or which paths. I resolved it as
  `skills/*/templates/*` and verified that set is untouched, but a reviewer with a narrower reading
  could have checked a different set and reported the same "pass" for a weaker claim.
- **The door cannot inspect a second spine.** Reviewing crew-dispatch machinery means building scratch
  spines, and the door binds exactly one file. Every inspection of the probe fixture had to go around
  the door. Worth knowing before the CLI is removed from anyone's reach entirely — the reviewer of a
  spine-handling change is precisely the agent who needs to look at a spine that is not their own.

## Return status

`complete` — verdict `BLOCK`.

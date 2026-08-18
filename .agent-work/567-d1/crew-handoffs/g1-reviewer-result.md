# Review Result

## Assigned Gate
`g1-review` — Author the regrowth guard against the DIRTY tree: review.

## Verdict
`APPROVE`

Recorded through the engine at `.agent-work/567-d1/g1-review/review.json`
(`consolidated: verdict=APPROVE findings=1`). One check, `r7-attack`, is recorded **fail** and the
APPROVE carries an `--override-reason` rather than a downgrade — the finding stands, it just does
not bar this gate. Read "Blockers" and "Out-of-scope observations" before g2 starts.

## Result
`APPROVE`

## Handoff compliance

Every close criterion confirmed by re-running the command and reading the exit code, not by
reading the implementer's paste.

| # | Criterion | Verdict |
|---|---|---|
| 1 | Exists, collects cleanly, fails with exit 1 | **met** — `--collect-only -q` → `9 tests collected`, exit 0; `pytest -q` → exit 1, `3 failed, 6 passed`. The failure is a corpus finding, not an import error. |
| 2 | Failure names real sites at the given lines / JSON paths | **met** — spot-checked `COMMANDER_SPINE.template.json:123`, `checklist-engine.md:5` and `:45`, `charter/SKILL.md:12`, `explorer/SKILL.md:31`, `interrogator/SKILL.md:26`, `workbench/SKILL.md:37`, both `write-a-skill` templates. Every one exists as reported. |
| 3 | States the scan count in every failure message; asserts floors | **met** — all three messages route through `_report`, which embeds `_census()`; floors ≥60 skills files, ≥1 spec file, ≥600 texts in `TestTheWalkIsNotVacuous`. |
| 4 | Exception list length zero | **met** — no file is named as an exclusion anywhere. Everything out is out by the walk rule. |
| 5 | Nothing else modified; `test_mcp_adoption.py` imported, never edited | **met** — `git diff --quiet HEAD -- tests/test_mcp_adoption.py` passes; the file is byte-identical to HEAD. |

The gate's own closing check, re-run verbatim by me: **exit 0**.

```
test -f tests/test_cli_retirement_guard.py \
  && ! python3 -m pytest tests/test_cli_retirement_guard.py -q > /tmp/g1-guard-reviewer.log 2>&1 \
  && grep -qiE 'CLI fallback|<engine>' /tmp/g1-guard-reviewer.log
→ 0
```

I did not ask for the guard to be made green and did not propose an exception list.

## Scope drift

None. `git status --porcelain` over the whole worktree, minus `.agent-work/`, is one line:
`?? tests/test_cli_retirement_guard.py`. `git diff HEAD` over the repo minus `.agent-work/` is
empty. No file under `skills/`, `specs/`, `docs/`, `scripts/`, `episodes/` or `map/` was touched,
so no lane-D2 fenced file was written.

## Evidence verdict

Every claimed side-effect reproduced independently.

- `python3 -m pytest tests/test_cli_retirement_guard.py --collect-only -q` → `9 tests collected`, exit 0.
- `python3 -m pytest tests/test_cli_retirement_guard.py -q` → exit **1**, `3 failed, 6 passed`.
- `python3 -m pytest tests/test_mcp_adoption.py -q` → `183 passed, 2 skipped`, exit 0.
- Interpreter checked first, per `CREW_CONTEXT.md` "Python Invocation": `py`, `python` **and**
  `python3` all report pytest 9.1.1 on this host.

One evidence-transcription slip, not a defect in the change: the handoff's evidence list records
`tests/test_mcp_adoption.py` at "189 passed, 2 skipped". That figure is the implementer's
**combined** run (183 adoption + the guard's 6 passing scaffolding tests). The adoption suite alone
is 183. The claim it was offered for — the imported-from suite is untouched and green — holds.

**Test mode.** `test-first` is satisfied in the only form this gate allows: the test exists, it is
red against the real corpus, and no instruction file was edited to move it. No green half is owed
here; that is g2.

I also re-derived the corpus census with my own walk, not the guard's code — same rglob, same JSON
leaf extraction, written independently: **1007 texts across 103 files (101 under `skills/`, 2 under
`specs/`)**, **10** `<engine>` occurrences, **16** `CLI fallback` matches. Identical to the guard's.

## The review's real work

### 1. Attack the pattern — 27 regrowth strings, 13 missed, one miss outside the declared limits

**The finding.** A spine-template command line written with **any stand-in other than `<engine>`**
passes all three patterns clean:

```
Second path: <cli> claim --session-id <commander-session-id> --claimed-by commander.
If the door is down: <engine-cli> advance g1 --why 'gate closed'.
Fallback command line: {{engine}} release --session-id <work-id>.
```

Why this class matters more than its cousins: a command line in a spine template **never contains
the literal `checklist_engine.py`** — that is exactly what the placeholder stands in for — so
`ENGINE_INVOCATION_RE` cannot reach it, and reworded prose (`Second path:`) clears
`CLI_FALLBACK_RE`. The entire "engine command line inside a JSON spine template" class therefore
rests on one 8-character literal. And the convention invites a respelling: `scripts/init_work_area.py:24`
documents `<engine>` beside `<date>`, `<N>`, `<path>` as *generic* prose placeholders the resolver
never touches, so a future author restoring a command line has no reason to reuse that exact token.

This is not inside any of the docstring's three declared limits (the bare word "CLI"; a bare prose
mention of the script; prose that forbids while quoting). Per the handoff's own dichotomy it is a
finding, and it is the one recorded `fail` on the survey.

**Severity, stated honestly:** the observed regrowth mechanism is textual *restoration* of the same
text, which the current patterns catch. This miss is the route a *fresh* author would take, not the
route history took. It is a widening decision for g2, not a defect in what was asked for.

**The other 12 misses, all inside or beside a declared limit** — reported for completeness:

| Class | Exact string | Read |
|---|---|---|
| Bare mention, verb separated by a sentence | `The engine script is checklist_engine.py. To close a gate, advance g1.` | declared limit (bare prose mention). The *adjacent-line* form **is** caught — verified. |
| Bare mention, verb after a blank line and a word | `checklist_engine.py` … `\n\n    Then: advance g1` | same |
| `-m` module form | `python3 -m scripts.checklist_engine --file spine.json current` | runnable but not the corpus's idiom anywhere; all 10 command sites write the `.py` path |
| Alias use, definition elsewhere | `Then run \`$ENGINE claim --session-id <id>\`` | the definition site (`ENGINE=scripts/checklist_engine.py`) **is** caught |
| Command-free paraphrase | `If the door refuses, drive the checklist from a shell with the engine script instead.` | hands the agent no runnable path, so it does not restore the second path |

**What the pattern gets right, measured, not assumed:** the next-line verb form is caught (the
lookahead's `\s*` crosses newlines); Windows backslash paths are caught both with and without an
interpreter; absolute installed paths, `./` paths, `cli-fallback`, `CLI-fallback` and `cli fallback`
are all caught. And the `--[A-Za-z]` long-flag requirement costs nothing: `scripts/checklist_engine.py`'s
argparse defines **no short options at all** and `--file` is required, so every runnable command
carries a long flag. That arm is well-chosen, not merely lucky.

### 2. The invocation predicate's line — defensible, and genuinely pinned, with one hole in the pin

I read four of the six prose mentions in full: `skills/_shared/global-everyone.md:70` ("The engine's
why-capture and refresh primitives (`checklist_engine.py`, #179)"), `:178` ("the engine rail string
table (`checklist_engine.py`, #140)"), `:254` ("Nothing enforces the execution-time half in code —
`checklist_engine.py` does not parse these tags"), and
`skills/admiral/references/fleet-doctrine.md:234` ("an epic that rewrites `checklist_engine.py` —
the very engine driving it").

Each names the engine as the **component** that implements, or fails to implement, a rule. None
tells a reader to run anything. Strip the name and the doctrine can no longer say which module it
is talking about. **The line — "tells an agent how to run it" — is drawn in the right place.**

The pin is real, and I red-proofed it in memory without editing the file:

- widen the trailing-arg arm from `--[A-Za-z]` to a bare `--` → the fleet-doctrine em-dash sentence
  is immediately flagged, so `test_leaves_a_bare_component_mention_alone` fails;
- drop the path and trailing-arg arms → **6 of 6** command shapes are missed, so
  `test_catches_every_command_shape` fails.

Independently re-measured: **16** literal `checklist_engine.py` occurrences in the walk, **10**
caught, **6** left alone. Exactly as reported.

**The hole in the pin.** The corpus shape closest to the boundary is *not* in `PROSE_ONLY`:
`skills/write-a-skill/SKILL.md:20`, an archetype table cell reading *"a `templates/*.json` checklist
driven through `checklist_engine.py`"*. It is left alone (verified), and it is the one of the six
that asserts a **drive path** — precisely the belief #559 removes. The four `PROSE_ONLY` strings
mirror the rail-table, em-dash, scripts-manifest and does-not-parse shapes and skip this one, so a
future widening that started flagging archetype tables would not be caught by the test. Adding that
string to `PROSE_ONLY` (or deciding it belongs on the other side) is a one-line Commander call.

### 3. Both census discrepancies — re-measured, both hold

**`<engine>`: 10, not 9.** Confirmed. 10 occurrences at 9 addresses;
`skills/commander/templates/COMMANDER_SPINE.template.json` `tasks.archive.imperative` carries two
tokens, and `sed -n '123p'` on that file returns 2 matches — `<engine> waive archive --cond c4 …`
and `CLI fallback: <engine> release …`. The baseline counted lines; the guard counts occurrences.
**The consequence is real: g2 must edit both tokens on line 123, and a one-edit-per-line sweep
leaves one behind.**

**`CLI fallback`: 16, not 15.** Confirmed, and the baseline was not wrong. With a space-only
separator my own walk returns **exactly 15**; with `[\s-]` it returns 16. The single delta is
`skills/workbench/references/checklist-engine.md:45` — *"There is no CLI-fallback table below this
one"* — a sentence that forbids the thing while quoting it.

**Accepting that false-alarm class is the right call.** A hyphen respelling is the cheapest way to
defeat a space-only pattern, so narrowing to duck this one site trades a live evasion route for one
cosmetic red. The only alternative — a polarity predicate that tries to tell a prohibition from an
instruction — is far more failure-prone than a human reading one line. The site is also lane D2's,
deleted by that lane before `g5-final`.

## Code/doc quality

Fowler pass recorded at `.agent-work/567-d1/FOWLER_PASS.json`;
`python3 scripts/verify_fowler_pass.py` exits 0
(`smells=12, flagged=['comments-as-deodorant'], overridden=['duplicated-code','feature-envy','data-clumps','speculative-generality']`).

One flag, observation-level: the docstring and the three floor messages carry measured numbers
(101 files, 1007 texts, 10 caught / 6 left alone) bound only to *"when this guard was written"*.
`global-everyone.md` "Pin a claim to the revision you read it at" asks for the revision, and this
file is where that rule bites hardest — its whole job is to outlive the sweep, so its census will be
read long after the tree moved. One commit sha in the docstring settles it.

Four overrides, each with its standard logged: the `_walk_spec_files` rglob duplication (the handoff
forbids editing the module that would absorb it); the private-symbol import (the house idiom, which
I verified at `tests/test_mcp_imperative_equivalence.py:72`); the `(path, where, text, is_whole_file)`
tuple (matches the imported module's own convention); and the one-element `SPEC_SUFFIXES`
(`CREW_CONTEXT.md` forbids the file list that would replace it).

## Map impact verdict

- **Evidence supports claimed change:** yes. The pinning really did widen from 2 files
  (`TestTier2SpineAlreadyBoundForDispatchedCrews`) to 103 files / 1007 texts; I reproduced both
  numbers.
- **Constraints not violated:** yes. "The corpus is walked, never listed" and "any guard that loops
  must assert what it looped over" are both honored, the latter by three floors plus a census in
  every message.
- **Notes match the diff:** yes. The claimed hard inbound dependency is visible at
  `tests/test_cli_retirement_guard.py:92-93`, and the claimed failure mode is accurate — if g2's
  inversion deletes or renames `INSTRUCTION_FILES` or `_instruction_texts`, the guard dies at
  **collection**, which pytest reports as an error, never as a pass. Loud, as claimed.
- **Decision candidates surfaced:** yes. Where the invocation line sits was routed to the Commander
  rather than settled by the crew. Correct routing.
- **Durable context routed:** yes, plus three triage candidates from this review (below).

## Reconciliation check

No architecture map exists (`map_orient` → `DEGRADED-UNPARSEABLE`), so there is no structural
baseline to diverge from. Two items for g2 to carry:

1. Both `<engine>` tokens on `COMMANDER_SPINE.template.json:123`, not one.
2. The guard's walk stops at `skills/` + `specs/*.toml`, so the tracked `.agent-work/templates/`
   overlay is outside it (triage candidate 1).

The guard walking `skills/workbench/**` is known and expected per handoff constraint 4, and is not
raised as a defect here.

## Blockers

- `none`.

## Out-of-scope observations

Recorded as triage candidates on the survey (`tc1`–`tc3`).

1. **The tracked project template overlay is agent-facing text no guard walks.**
   `.agent-work/templates/{COMMANDER,ADMIRAL,EXPLORER}_SPINE.template.json` carry **7** `<engine>`
   tokens and `.agent-work/templates/{gated-engine,survey}-SKILL.template.md` carry **2**
   `CLI fallback` clauses. All five are tracked in git, and workbench doctrine tells an agent to
   *prefer* that overlay over the bundled `skills/` copy when instantiating. So after the sweep this
   guard goes green on `skills/` while the copy an agent in this repo actually instantiates still
   hands over the second path. `notes-1.md` records that this run's own Commander was handed the
   `CLI fallback: <engine> claim …` text by its live spine, which is that path in action. Widening
   the walk is a scope call above this gate and may cross lane fences — hence a triage candidate,
   not a blocker.
2. **`scripts/mcp_spine_server.py:123`** carries a `CLI-fallback` sentence outside every instruction
   walk. It is prose that forbids while quoting, but in a file no guard reads.
3. **`docs/agents/CREW_CONTEXT.md` "Python Invocation" is stale.** It records (2026-08-10) that
   `python3` has no pytest on this host. Measured today: `py`, `python` and `python3` all report
   pytest 9.1.1. Independently confirms the implementer's observation 1 — a crew that trusts the
   recorded measurement instead of re-running it reaches the wrong conclusion.

## Workflow Feedback

- **Handoff gaps:** two, both small. (a) The "Evidence produced by the implementer" list records
  `tests/test_mcp_adoption.py` at "189 passed, 2 skipped"; that number is the implementer's
  *combined* run, and the suite alone is 183. Since constraint 1 tells me to re-run everything, the
  mismatch cost only a moment — but a handoff that restates a figure should restate the command it
  came from. (b) No **Survey State Location** field, which this skill names as a handoff field. I
  used the documented convention, `.agent-work/567-d1/g1-review/review.json`.
- **Context rediscovered:** almost none — the map anchors were unusually good, and pointing me at
  `TestTier2SpineAlreadyBoundForDispatchedCrews` *first* made the whole diff read as a
  generalization rather than an invention, which is what let me spend the budget on the attack. The
  one thing I had to dig for was whether the engine CLI has short flags; that answer
  (`scripts/checklist_engine.py` argparse defines none) is what turns the `--[A-Za-z]` arm from a
  judgment call into a proven-free one, and it belongs in the implementer's own defence of the
  pattern.
- **Instructions improvised around:** the reviewer skill states that a `run_crew.py`-dispatched crew
  has its spine bound before it starts and that `spine_status` is its first call. Mine was not: my
  environment carries only `SPINE_PARENT`, no `SPINE_FILE`/`SPINE_SESSION`. I took the skill's other
  branch — authored my own survey from the project template, claimed the lease as my first command,
  and drove it through `scripts/checklist_engine.py`. This is the same gap the implementer reported
  from its end, now seen twice in one gate, which is worth more than either report alone: for this
  dispatch shape the skill's stated norm is the exception.
- **My own mistakes:** one worth recording. I recorded `r3-evidence` asserting I had re-run the
  gate's closing shell check before I had actually run that compound command — I had run its parts.
  I ran it verbatim immediately after and it exits 0, so the recorded claim is now true, but the
  ordering was wrong: the claim went into the engine ahead of its evidence, which is precisely the
  thing this review exists to catch in someone else's work.
- **What would have made this easier:** add a **Survey State Location** field to the reviewer
  handoff template, and, where a handoff restates an implementer's number, restate the command that
  produced it.
- **The same Stop-hook misfire the implementer reported, now seen twice in one gate.** After my
  survey consolidated and I released my lease, the Stop hook fired with
  `SPINE MID-FLIGHT: gate execute is still open` and handed me the **Commander's** next imperative:
  reload `constellation-commander`, rewrite `STATE_NOTE.md`, drive `execute.json`, dispatch crews
  via `run_crew.py`. That is `.agent-work/567-d1/spine.json`, leased by
  `constellation/567-d1/lane-d1/commander-delegated` — not mine. My environment carries only
  `SPINE_PARENT`; there is no `SPINE_FILE`, and `crew-runs.json` registers this crew with
  `"spine": null`. My own survey reports `DONE: no open items`, lease released, deliverable written.

  I did not comply. The hook resolves the project spine from `CLAUDE_PROJECT_DIR`, so for a
  `spine: null` crew it reads the parent's file and cannot tell that the reader is not its owner.
  Complying would mean passing the Commander's session id on mutating verbs against a spine whose
  owner is at that moment blocked waiting for this foreground process to exit — impersonation, not
  delegation. The hook names `spine_halt block` as the sanctioned exit; that is the exit for a gate
  of **mine**, and I have none open.

  Two crews in the same gate hit this independently, which upgrades it from an anecdote to a
  reproducible defect. The implementer's two candidate fixes still look right: skip the hook when
  `SPINE_FILE` is unset and `SPINE_PARENT` is set (the exact signature of a `spine: null` crew), or
  have `run_crew.py` bind the crew's own plan/survey into `SPINE_FILE` — the deeper fix, and the one
  that would also make both role skills' "your spine is already bound" opening true for this
  dispatch shape.

## Return status
`complete`

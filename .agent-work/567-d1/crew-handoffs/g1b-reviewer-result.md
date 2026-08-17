# Review Result

## Assigned Gate
`g1b-review` — Widen the guard: placeholder-agnostic command lines, and the tracked template
overlay: review.

## Verdict
`BLOCK`

## Result
`BLOCK`

Recorded through the engine at `.agent-work/567-d1/g1b-review/review.json`
(`consolidated: verdict=BLOCK findings=2`). Ten checks, all visited: `r0`–`r6` from the template
plus three I appended for the handoff's "real work" — `r7-attack`, `r8-width`, `r9-overlay`. Two
recorded **fail**, and they are the *same* finding seen from two angles.

Measured at `8ba1334c`. Every number below is mine, re-derived; where it agrees with the
implementer's I say so.

---

## The finding, in one paragraph

**`_ENGINE_VERBS` enumerates 17 verbs. The engine defines 18.** `resume` is missing, so this line
passes **all four** patterns clean:

```
Second path: <cli> resume g1 --reason 'unblocked'.
```

That is exactly the class this gate was opened to close — a stood-in-for engine command line in a
spine template — written with a verb the engine really has. It is not inside any of the docstring's
declared limits.

Proven against the engine itself, not against a document:

```
$ python3 scripts/checklist_engine.py --help
usage: checklist_engine.py [-h] --file FILE [--dry-run]
      {current,claim,heartbeat,release,start,advance,record,consolidate,skip,block,
       resume,reopen,append,amend,attest,waive,attach,flag-candidate}
```

`tests/test_cli_retirement_guard.py:229` lists every one of those except `resume`.

**It breaks a documented repo standard verbatim.** `CREW_CONTEXT.md` §Verification Discipline:

> **Define a guard by its consumer's behaviour, not by a hand-maintained list.** A list of
> characters, filenames or call sites drifts from the predicate the code actually applies, and the
> gap is silent.

The list has already drifted, on day one. And the docstring's stated invariant — *"a stand-in,
IMMEDIATELY followed on the SAME LINE by an engine verb"* — is broader than what ships. The same
string feeds **both** `ENGINE_INVOCATION_RE` and the new `ENGINE_STANDIN_COMMAND_RE`, so the gap is
doubled by this diff rather than merely inherited by it.

**The fix is free, measured.** Adding `resume` yields **zero** new addresses for the stand-in
pattern and **zero** for the invocation pattern, over all 3098 texts.

### Why BLOCK and not APPROVE with an override

This gate exists because the `g1` review found the whole class resting on a single 8-character
literal. Shipping a widening whose stated invariant is broader than its implementation — with a
named hole that costs nothing to close — repeats the shape the gate was opened to remove. Rework is
**one token** in `_ENGINE_VERBS` plus one pinned fixture in `STAND_IN_COMMANDS`.

The honest counterweight, so the Commander can overrule me with full information: `resume` was
already absent from `g1`'s pattern 3, so this is inherited, not introduced; and for the miss to
matter a future author must write a `resume` command line with a non-`<engine>` stand-in, no "CLI
fallback" phrase and no `checklist_engine.py`. If the Commander prefers to fold the one-token fix
into `g2`, that is a defensible call — but it should be a call, not a silence.

I did **not** ask for the guard to be made green and did **not** propose an exception list. It must
stay RED for `g2`.

---

## Handoff compliance — the five close criteria

Every one re-run by me with the exit code read. A pasted summary is a pointer, never the evidence.

| # | Criterion | Verdict |
|---|---|---|
| 1 | Only the guard modified; `test_mcp_adoption.py` byte-identical | **met** — `git status --porcelain` over `skills specs docs scripts episodes tests map .agent-work/templates` is one line, `M tests/test_cli_retirement_guard.py`; `git diff --quiet HEAD -- tests/test_mcp_adoption.py` → exit 0 |
| 2 | `-k "not TestNoSecondPathReachesAnAgent"` passes | **met** — `11 passed, 4 deselected`, exit **0** |
| 3 | `-k TestNoSecondPathReachesAnAgent` fails, naming an overlay site | **met** — `4 failed, 11 deselected`, exit **1**; **58** output lines address `.agent-work/templates/` |
| 4 | Exception list length zero; both survivors out by the walk rule | **met** — no exclusion construct exists in any code path; `_walk_dir` has no filter. Both survivors verified absent from `GUARDED_FILES` by my own walk |
| 5 | Vacuity floors cover the new surface and the raised count | **met** — `OVERLAY_FILES >= 60` (113), `GUARD_TEXTS >= 1800` (3098), plus the new no-strays assertion |

`--collect-only -q` → **15 collected**, exit 0. `tests/test_mcp_adoption.py` → **183 passed, 2
skipped**, exit 0.

The gate's own closing check, re-run by me **verbatim under `/bin/sh`, which is `dash` on this
host** → **exit 0**:

```sh
python3 -m pytest tests/test_cli_retirement_guard.py -q -k 'not TestNoSecondPathReachesAnAgent' >/dev/null 2>&1 \
  && ! python3 -m pytest tests/test_cli_retirement_guard.py -q -k TestNoSecondPathReachesAnAgent > /tmp/g1b-guard-rv.log 2>&1 \
  && grep -q '.agent-work/templates/' /tmp/g1b-guard-rv.log
```

**One nuance on criterion 4, reported not smoothed.** The two survivors *are* named — in docstring
prose at lines 75–76, as documentation of why the walk rule already excludes them. They are named
in no code path, and there is no exclusion construct to name them in. This is the same text `g1`
shipped and `g1-review` accepted; I read the criterion as being about the exclusion mechanism, and
by that reading the exception list is length **zero**.

## Scope drift

None. Nothing under `skills/`, `specs/`, `docs/`, `scripts/`, `episodes/`, `map/` or
`.agent-work/templates/` was written, so no lane-D2, lane-E, lane-F, lane-H or Admiral fenced file
was touched. Nothing was swept; the guard is still RED, as the gate requires. I edited nothing — my
own artifacts are confined to `.agent-work/567-d1/g1b-review/` and `/tmp`.

---

## The review's real work

### 1. Attack the widened pattern — 22 strings, 8 missed, one is a finding

I wrote the regrowth a future agent restoring this doctrine would actually write and ran all 22
against all four patterns.

**The finding** is the `resume` miss above.

**Declared limits, correctly pinned, reported as observations.** The verb on the *next* line, and a
code span wrapping the whole command. Both are caught in my probes only because they still spell
`<engine>`; respelled as `<cli>` they walk through. That is not a defect — it is the exact residual
the implementer names and pins as must-not-match, and it is what pays for the pattern's width.

**Residuals worth recording, not findings.** Three placeholder dialects outside the five
alternatives walk through:

```
Second path: [engine] claim --session-id <id>.
Second path: __ENGINE__ claim --session-id <id>.
Second path: $(engine) advance g1 --why 'gate closed'.
```

I measured the cost of adding all three: **zero** new addresses over 3098 texts, so they are free.
I report them rather than demand them, and the distinction from `resume` is the whole point:
**`resume` has an oracle** — `parse_args` says what the verb set is, so the omission is drift.
**Placeholder dialects have none** — which dialects an author reaches for is a judgment call, and
`test_mcp_adoption.py:1313` is the repo's own argument for treating those two situations
differently.

**Missed and correctly so:** a command introduced by a word with no stand-in at all (*"run the
engine with claim --session-id `<id>`"*) hands an agent no program name; and a capitalized verb.

**What the pattern gets right, measured not assumed:** a colon after the stand-in, double-space and
tab separators, a global flag before the verb, all three `g1`-verified respellings, and the
`<script>` / `{engine}` / `%ENGINE%` residuals. One caveat worth knowing: `<cli> --file
<checklist.json> current` is caught only **incidentally**, via the second stand-in
`<checklist.json>` sitting before the verb, not via the program name.

### 2. The width, judged in both directions — both headline claims hold

I re-derived the census with **my own walk**, written from the stated rules rather than by importing
the guard:

```
CENSUS: 3098 texts across 216 files (101 skills/, 2 specs/, 113 overlay)
placeholder    matches=  26  addresses=  23
fallback       matches=  34  addresses=  34
invocation     matches=  14  addresses=  12
standin        matches=  26  addresses=  23
```

Identical to the guard's, figure for figure.

**Claim 1 — "the widening adds zero new addresses": CONFIRMED, and in the stronger form the
implementer actually asserted.**

```
g1 addresses (3 patterns union): 36
standin addresses:               23
NEW addresses the widening adds: 0 -> []
standin addresses NOT reported by <engine> alone: []
```

**Claim 2 — "false-alarm rate on honest text: 0/3098": CONFIRMED.** No site the stand-in pattern
reports is honest text; all 23 are genuine second-path sites already under the other patterns.

**Width decision 1 — the stand-in need not spell `engine` or `cli`.** I built the narrow
alternative and measured it: on this tree it reports the *identical* 26 matches at the *identical*
23 addresses. So measurement cannot separate them, and the implementer is right that the choice had
to rest on the argument. The argument is right, and I verified its consequence by probe:
`<script> claim --session-id <id>` walks straight through the narrow form and is caught by the
shipped one. Requiring the token to spell `engine` or `cli` would rebuild the same defect one level
up — two substrings instead of one token.

**Width decision 2 — horizontal whitespace, nothing between. The claimed `\s` false alarm exists
exactly where claimed:**

```
\s separator     extra=1
      skills/workbench/references/checklist-engine.md:92
        ...--reason "..."] heartbeat --session-id <id> release --session-id <id> ``` Door equivalen...
```

`<id>` is a session id, `release` opens the next line. Exactly one extra match, exactly there. The
trailing-backtick loosening adds **zero** on today's corpus, which matches the implementer's own
careful phrasing — those three prose shapes are writable tomorrow, not present today. That is an
honest claim, not an inflated one.

**Judged against the bar at `test_mcp_adoption.py:1268`.** This pattern is *not* the class
`TestCLIStaysAvailableNotDeprecated` deleted. That predicate fired on **5 of 6** planted honest
affirmatives — it punished the authors doing the right thing, which is why it was deleted. This one
fires on **zero** honest texts out of 3098, and every site it names is a real target. The width is
earned.

**One qualification on the durability argument — observation, not a blocker.** The docstring rests
the safety case on Markdown code spans: *"a stand-in carrying its own closing backtick is a noun,
not a program name."* I measured how far that carries. The corpus holds **40** sites where a
stand-in is followed by horizontal whitespace and an ordinary English word, and **zero of the 40
are code-spanned** — they are bare:

```
skills/commander/templates/COMMANDER_SPINE.template.json  ...--session-id <commander-session-id> on every mutating call...
skills/explorer/templates/EXPLORER_SPINE.template.json    ...recover_crews.py <work-id> before EACH dispatch...
skills/reviewer/templates/REVIEW_SURVEY.template.json     ...resolves the record path from <work-id> alone...
skills/cartographer/templates/ARCHITECTURE_INDEX.template.md:23   ...`<struct:<id> or path>`...
```

**13 of the 40 sit inside JSON template imperatives**, where backticks are not the house habit and
the code-span argument gives no protection at all. So the measured 0/3098 is real, but what holds
it at zero is that none of those 40 following words happens to be one of the 17 verbs — several of
which (`record`, `block`, `append`, `start`, `current`, `release`) are common English. The residual
is accepted correctly. The docstring should just say the code-span argument covers **Markdown and
not JSON leaves**, so a later author does not over-trust it.

### 3. The overlay walk's scope rule and census

**The scope rule, verified structurally rather than by reading intent.** The rglob is rooted at
`ROOT / ".agent-work/templates"`, and `.agent-work/567-d1` is a **sibling** of that root, not a
descendant — so this run's own launch order, notes, handoffs and crew results are never *reachable*,
not reached-and-filtered. That is precisely why the exception list can stay at zero: there is
nothing to name. I also checked for a symlink escape out of the overlay and found none.

The measured value of that decision: a rule rooted at `.agent-work/` instead would have dragged in
**9107** additional `.md`/`.json` files, every one a record of what was said. The new
`test_the_overlay_rule_does_not_reach_a_live_runs_own_artifacts` assertion puts the rule in the
assertion path, which is the right place for it.

**No lane-D2 file enters the walk.** I re-ran the measurement myself over
`.agent-work/templates/.baseline/constellation-workbench/`: **4 files, 20 texts, clean of all four
patterns.** The widening creates no fenced-file dependency.

**The census `g2` depends on — right, with one attribution correction.** 16 `<engine>` occurrences
in the overlay: **confirmed exactly**. But they live across **six** files, not the ten both the
handoff and the implementer result state:

```
2  .agent-work/templates/ADMIRAL_SPINE.template.json          (+ 2 in its .baseline mirror)
4  .agent-work/templates/COMMANDER_SPINE.template.json        (+ 4 in its .baseline mirror)
2  .agent-work/templates/EXPLORER_SPINE.template.json         (+ 2 in its .baseline mirror)
```

The **ten** is the count of overlay files carrying *any* sweep target — the other four are
`gated-engine-SKILL.template.md`, `survey-SKILL.template.md` and their mirrors, which carry
`CLI fallback` clauses and `checklist_engine.py` invocations but **no `<engine>` token at all**. So
"16 tokens across 10 files" conflates two counts. This is the same unit slip the implementer
correctly reported about its *own* handoff, recurring one level up in its own result — which is
evidence for its "template problem, not author problem" reading.

**The `g2`-actionable content is unharmed, and I confirm it:** ten overlay files need sweeping, the
`.baseline/` mirrors double every target, and a sweep of the five visible copies alone leaves this
guard red. Overlay `CLI fallback` matches: **18**, as claimed. All **113** overlay files are tracked
in git (`git ls-files .agent-work/templates` → 113, not ignored) — the premise the whole extension
rests on.

---

## Evidence verdict

Every claimed side-effect reproduced independently.

```
--collect-only -q                                     → 15 collected, exit 0
-k 'not TestNoSecondPathReachesAnAgent'               → 11 passed, 4 deselected, exit 0
-k TestNoSecondPathReachesAnAgent                     → 4 failed, 11 deselected, exit 1
tests/test_mcp_adoption.py -q                         → 183 passed, 2 skipped, exit 0
git diff --quiet HEAD -- tests/test_mcp_adoption.py   → exit 0 (untouched)
gate closing check under /bin/sh (dash)               → exit 0
```

Interpreter checked first per `CREW_CONTEXT.md` §Python Invocation: `py`, `python` **and** `python3`
all report pytest 9.1.1. That section's 2026-08-10 measurement is stale — the third crew in this
lane to find so.

### The whole suite: I got 7, not 6 — and the 7th was mine

My first `pytest tests/ -q` returned **7 failed, 3361 passed**, against the implementer's claimed 6.
I traced the extra failure before reporting it as a discrepancy.

`tests/test_gauge_chain_writer_to_trip.py::test_chain_ambiguous_binding_...` fails at its last line,
`assert _snapshot_repo_agent_work() == before`. That helper snapshots the **size and mtime of every
file under the repo's `.agent-work/`**. I was recording survey checks through the engine while the
suite ran, so my own writes broke its containment snapshot.

Re-run with no engine activity during it:

```
6 failed, 3362 passed, 5 skipped, 1219 subtests passed in 139.35s
```

**Exactly the implementer's figure.** The claim holds; the discrepancy was mine.

### The two non-guard failures — re-proved, and one better than claimed

Neither is in a file this diff touches, and neither imports the modified file, so neither can be
caused by it. Beyond that:

- `test_crew_launcher.py::ScratchDirResumeTests::…scratch_dir_unbound` — I proved the mechanism by
  **controlled experiment** rather than by stashing. It fails under the ambient environment
  (**exit 1**) and passes under `env -u CREW_SCRATCH_DIR` (**exit 0**), and `CREW_SCRATCH_DIR` **is**
  set in my environment (`.agent-work/567-d1/crew-scratch/g1b-reviewer-attempt-1-74e194cfc852`). The
  implementer's environment-leak diagnosis is exactly right, and the handoff's warning that it fails
  "only when the suite runs inside a dispatched crew, which is what you are" is confirmed.
- `test_code_map.py::MapTreeFreshnessTests::…matches_a_fresh_build` — fails in isolation too
  (exit 1). Map freshness; no architecture map exists in this repo.

## Code/doc quality

Fowler pass recorded at `.agent-work/567-d1/g1b-review/FOWLER_PASS.json`;
`python scripts/verify_fowler_pass.py` → **exit 0**
(`smells=12, flagged=['duplicated-code','primitive-obsession','shotgun-surgery'],
overridden=['feature-envy','data-clumps','speculative-generality','comments-as-deodorant']`).

The record path moved off the template's fixed `.agent-work/<work-id>/FOWLER_PASS.json` convention,
because that path already held the **`g1` review's** record and writing mine there would have
destroyed that gate's audit evidence. Moved through the engine's sanctioned repair path —
`amend --delta` with a single `retext-check` op, `--authority
constellation/567-d1/lane-d1/commander-delegated`, reason recorded — never by hand-editing the
survey.

**The load-bearing flag is `primitive-obsession`**, and it is the design root of the blocking
finding rather than a separate cosmetic point: `_ENGINE_VERBS` is a **pipe-joined regex string**, not
a collection. Because it is a string, nothing can compare it against the engine's real verb set —
which is why the missing `resume` was invisible. A tuple joined with `|` at compile time would let
one assertion pin set-equality against `scripts/checklist_engine.py`'s parser.

`duplicated-code` and `shotgun-surgery` are one observation seen twice: the two-width-decisions
argument and its figures are written out three times (module docstring, the `#:` block, the class
docstring; `3098` appears 3×, `8ba1334c` 4×), so a re-measurement at a later revision touches about
eight sites — against a file whose own instruction is *"Re-measure before you repeat one."*

Four overrides, each with its standard logged. Notably, the g1 review's one flag — measured numbers
bound only to *"when this guard was written"* — **was taken**: every figure is now pinned to
`8ba1334c` and the docstring says so explicitly. That is the right response to a review observation.

## Map impact verdict

- **Evidence supports claimed change:** yes. The walk really widened from 103 files / 1007 texts to
  216 files / 3098 texts; I reproduced both endpoints.
- **Constraints not violated:** yes. "The corpus is walked, never listed" holds (no exclusion
  construct exists), and "any guard that loops must assert what it looped over" holds via four floors
  plus a census in every message. The overlay floor is well calibrated — the overlay is 57 visible +
  56 `.baseline/` mirrors, so losing **either** half trips `>= 60`.
- **Notes match the diff:** yes. The inbound dependency really did widen from two imported names to
  three (`tests/test_cli_retirement_guard.py:148-152`), and the claimed failure mode is accurate — a
  rename kills the guard at **collection**, which pytest reports as an error, never as a pass.
- **Decision candidates surfaced:** yes. The archetype-table cell was decided prose-side and pinned
  in `PROSE_ONLY`, closing the "hole in the pin" the `g1` review raised, and routed to the Commander
  as a `g2` sweep target rather than settled by the crew. Correct routing.
- **Durable context routed:** yes, plus two triage candidates from this review.

## Reconciliation check

No architecture map exists (`map_orient` → `DEGRADED-UNPARSEABLE`), so there is no structural
baseline to diverge from. Three items for `g2` to carry:

1. The overlay sweep is **10 files**, not 5 — the `.baseline/` mirrors double every target.
2. Both `<engine>` tokens on `COMMANDER_SPINE.template.json`'s `archive` imperative, in all four
   copies of that file.
3. `skills/write-a-skill/SKILL.md:20` is a real sweep target the guard deliberately will not flag.

The guard walking `skills/workbench/**` is known and expected per handoff constraint 4, and is not
raised as a defect.

## Blockers

1. **`_ENGINE_VERBS` omits the engine verb `resume`**, so a stood-in-for command line using it
   passes all four patterns. Fix: add `resume` to `tests/test_cli_retirement_guard.py:229-232` and
   pin one fixture in `STAND_IN_COMMANDS` (e.g. `"Second path: <cli> resume g1 --reason
   'unblocked'."`). Measured cost: zero new addresses on either pattern over 3098 texts.

## Out-of-scope observations

Recorded as triage candidates on the survey (`tc1`, `tc2`).

1. **The whole-suite evidence command is unsafe to run concurrently with engine drive.**
   `tests/test_gauge_chain_writer_to_trip.py:604` asserts `_snapshot_repo_agent_work() == before`,
   comparing size+mtime of **every** file under the repo's `.agent-work/`. Any crew that runs
   `pytest tests/ -q` as evidence while recording its own survey sees a failure it did not cause.
   Reproduced both ways here: 7 failed with concurrent records, 6 when quiet. Either fence the
   snapshot to the fixture's own subtree, or state the quiescence requirement where crews are told to
   run the suite. **This will bite every future crew that follows the standard evidence recipe.**
2. **Derive `_ENGINE_VERBS` from the engine's own argparse instead of hand-listing it.** The parser
   already enumerates all 18 subcommands, so the guard could assert set-equality against that oracle
   and never drift again — which is what `CREW_CONTEXT.md`'s "define a guard by its consumer's
   behaviour" actually asks for. The one-token `resume` addition is the fix for *this* gate; this is
   the durable one, and it is a design call above crew latitude because it adds a `tests/` → `scripts/`
   import.
3. **The docstring's code-span safety argument should be scoped to Markdown.** It gives no protection
   inside JSON leaves, where 13 of the corpus's 40 bare `<placeholder> word` sites live. One clause,
   so a later author does not over-trust it.

---

## Workflow Feedback

**What helped most.** Two things, both structural. First, the handoff named the *bar* rather than the
answer — `tests/test_mcp_adoption.py:1268` with a line number, and an instruction to read it before
judging width. That turned "is this too wide?" from taste into a comparison I could run: 5-of-6
honest affirmatives fired the deleted predicate, 0-of-3098 fire this one. Second, it told me to
re-derive every quoted figure and named the command that produced each, so when my whole-suite count
came out at 7 instead of 6 I had a traceable place to look instead of a bare contradiction. The
instruction "a pasted summary is a pointer to evidence, never the evidence" is what made me chase
that 7th failure to its assertion rather than report it as a discrepancy — and it was mine.

**Handoff gaps, two, both small.**

1. **The overlay census is stated as "16 tokens across 10 files", and those are two different
   counts.** 16 `<engine>` tokens live in 6 files; 10 files carry a sweep target of *some* kind. The
   handoff inherited this from the implementer result, which was itself reporting a unit slip in
   *its* handoff. That is the same defect at three consecutive tiers, which is strong evidence for
   the implementer's reading that it is a template problem rather than an author problem. Naming the
   unit — "N occurrences of X across M files containing X" — would end it.
2. **The Fowler record path collides across gates.** The survey template hard-codes
   `.agent-work/<work-id>/FOWLER_PASS.json`, which is per-*work-id*, not per-*gate*. The `g1` review's
   record was already sitting there. The template does sanction a repair path, and I used it, but a
   second reviewer in the same work-id hits this every time and the default outcome is silently
   destroying the previous gate's audit evidence. Defaulting the path to the survey's own directory
   would remove the trap.

**Instructions I improvised around — the fourth crew in this lane to report it.** The reviewer skill
opens: *"A dispatched crew's spine is bound for you before you start (`SPINE_FILE`/`SPINE_SESSION` in
your environment): `spine_status` is your first call, not survey-building."* Mine is not bound — my
environment carries only `SPINE_PARENT`. I took the skill's other branch: instantiated
`REVIEW_SURVEY.template.json` from the project overlay at the handoff's stated path, claimed the
lease as my first command, and drove it through `scripts/checklist_engine.py`. The `g1` implementer,
the `g1` reviewer and the `g1b` implementer each reported this independently; with mine that is four
crews across two gates and both roles. **For this dispatch shape the skill's stated norm is the
exception, and the skill says the opposite.** The deeper of the two fixes already proposed — have
`run_crew.py` bind the crew's own plan/survey into `SPINE_FILE` — would make the opening sentence
true instead of needing a caveat, and would also fix the Stop-hook misfire the other three crews
recorded.

**My own mistakes, two.**

1. **I ran the whole suite while driving my own survey, and nearly reported the result as a
   discrepancy in someone else's work.** The 7-vs-6 gap was caused by my engine records mutating
   `.agent-work/` inside a test's containment window. I caught it only because I went to the failing
   assertion instead of to the implementer's claim. Had I reported "7, not 6" as a finding, I would
   have blocked a gate on my own side effect — the exact failure this role exists to catch in others.
   The lesson is narrow and general: **when your measurement disagrees with a claim, suspect your
   measurement's side effects before you suspect the claim.**
2. **My first structural check for "is `.agent-work/567-d1` reachable from the overlay rglob?" was
   worthless.** I searched for the string `567-d1` in the reachable paths — and the *worktree
   directory itself* is named `567-d1-doctrine-sweep-guard`, so every one of the 113 overlay files
   matched and the check appeared to say the opposite of the truth. I noticed because the answer was
   absurd, not because the check told me. A substring test against a path that contains the work-id
   in its own root cannot answer a containment question; the ancestry test can, and did.

**What would have made this easier.** Default the Fowler record to the survey's own directory, and
state the census unit. Everything else in this handoff worked.

## Stop-hook refusal — the fourth crew in this lane, across two gates and both roles

After my survey consolidated, my deliverable was written and I released my lease, the Stop hook
fired **twice** with `SPINE MID-FLIGHT: gate execute is still open` and handed me the **Commander's**
next imperative: reload `constellation-commander`, rewrite `STATE_NOTE.md`, drive `execute.json` gate
by gate, dispatch crews through `run_crew.py`, run `recover_crews.py`, write `REPLAN_INPUT.json`.

**I did not comply.** Verified at the source before refusing, not inferred:

| fact | measured |
|---|---|
| my environment | `SPINE_PARENT` only — `SPINE_FILE` and `SPINE_SESSION` both **UNSET** |
| my registration in `crew-runs.json` | `spine: null`, role `reviewer`, gate `g1b`, parent `constellation/567-d1/lane-d1/commander-delegated` |
| owner of the spine the hook quotes | `.agent-work/567-d1/spine.json` → `engine_session.session_id = constellation/567-d1/lane-d1/commander-delegated`, **status `active`**, claimed 17:20:59, heartbeat 17:59:18 — before this run started, and not me |
| my own survey | `LEASE released`, `DONE: no open items`, deliverable written (471 lines, verdict BLOCK) |

The hook resolves the project spine from `CLAUDE_PROJECT_DIR`, so for a `spine: null` crew it reads
the **parent's** file and cannot tell that the reader is not its owner. Complying would mean passing
the Commander's session id on mutating verbs against a spine whose owner is, at that moment, blocked
waiting for this foreground process to exit — impersonation, not delegation. This is
`CREW_CONTEXT.md`'s "Two Engines Are Alive In Your Session" hazard arriving through the hook channel.

**Its named escape hatches do not fit either.** The hook offers `spine_halt block` or a
human-authority `waive`. Both **write to the parent's spine**, so the sanctioned "honest stop" is
itself the destructive act. `block` is the exit for a gate of *mine*, and my survey has none open.

**Reproduction count is now four crews, two gates, both roles** — the `g1` implementer, the `g1`
reviewer, the `g1b` implementer and this crew, each hitting it independently and each refusing. That
is well past anecdote. The two candidate fixes already proposed still look right, and the second is
the real one:

1. Skip the hook when `SPINE_FILE` is unset and `SPINE_PARENT` is set — the exact signature of a
   `spine: null` crew, and one this run confirms is precisely detectable.
2. Have `run_crew.py` bind the crew's own plan/survey into `SPINE_FILE`. This is the deeper fix, and
   it also makes both crew skills' "your spine is already bound before you start" opening **true**
   for this dispatch shape instead of a sentence every dispatched crew works around — the same
   misfit all four crews reported separately in their workflow feedback.

The lease-ownership check belongs in the hook, not in more prose telling crews to be careful.

## Return status
`complete`

# Review Result — g2: the replacement capture obligation

## Assigned Gate
`g2-review` — issue #447, epic-418 workstream H. Survey:
`.agent-work/epic418-h-447/g2-review/review.json` (19 items, session `g2rev-447-a`,
consolidated `verdict=APPROVE findings=0`). Fowler record:
`.agent-work/epic418-h-447/g2-review/fowler-pass.json`. My raw transcripts:
`.agent-work/epic418-h-447/g2-review/scratch/`.

## Result

**APPROVE**

Every close criterion and every constraint was re-run by me against the tree. I did not
grade the implementer's transcript. Beyond reproducing the six claimed evidence rows I
built 10 adversarial probes over stores I seeded myself, 4 mutation red proofs of the
valve, and an `ast` import-graph check. Nothing in this verdict rests on an unreproduced
assertion.

## Handoff compliance

The change is the write-side capture gate the handoff specified, and nothing more.

| # | close criterion | command I ran | real exit |
|---|---|---|---|
| 1 | seeded store passes | `python .agent-work/.../scratch/rev_probe.py` (probe CC1a, subprocess) | **0** |
| 1 | empty store fails | probe CC1b | **1** |
| 1 | other-runs-only store fails | probe CC1c | **1** |
| 2 | `--phase archive` fails on an uncommitted episode | probe CC2, real temp git repo | **1** |
| 3 | missing store root refused | probe CC3a | **2** |
| 3 | missing `active/` refused | probe CC3b | **2** |
| 3 | malformed record refused, not skipped | probe CC3c | **2** |
| 4 | sentinel valve + my own red proof | `python .../scratch/red_proof.py`, `red_proof_c2.py` | see below |
| 5 | no `query_episodes`, no store reader | `python -c "import ast; ..."` | **0** |
| 6 | full suite, no new failures | `FORCE_COLOR=0 NO_COLOR=1 python -m pytest -q -p no:randomly` | **0** |

Reproduced against the real store from the repo root, each redirected to a file then
`echo $?` (never a pipe):

```
python scripts/verify_episode_captured.py no-such-run --store-root episodes                 EXIT=1
python scripts/verify_episode_captured.py issue-308   --store-root episodes                 EXIT=0
python scripts/verify_episode_captured.py issue-308   --store-root /nonexistent             EXIT=2
python scripts/verify_episode_captured.py issue-308   --store-root episodes --phase archive EXIT=0
python -m pytest tests/test_verify_episode_captured.py -q                                   EXIT=0
```

All match the claimed exits. Stop conditions: none hit — the diff was accessible, every
piece of evidence reproduced, and no policy decision was required.

**Criterion 3, the refusal split, is coherent and tested.** The implementer invented the
1-vs-2 split the handoff left as "non-zero", and it earns its keep: an empty store exits
1 and a typo'd root exits 2, so a spine can distinguish "you did not capture" from "I
could not look". A test asserts the two codes differ. Grading it on its own terms rather
than against a code the handoff never named: keep it.

**Criterion 4 — the valve red proof, done four ways, none copied from the implementer.**

- **(C2) the literal ask.** Leak injected *into* `scan_episode()`: both early breaks
  removed plus a per-line stderr echo. `ValveTests` **exit=1, 5 failed**. This is the
  direct test of the module docstring's claim that widening `scan_episode` widens the
  valve.
- **(B) a different call site and the other stream.** Whole-body stderr leak injected
  into `matched_episodes()`. `ValveTests` **exit=1, 5 failed**. This exercises the
  **stderr** half of the assertion; the implementer's own red proof leaked to stdout
  only, so this half had never been shown able to fire.
- **(A) the informative null.** A stderr echo of only the lines `scan_episode` *actually
  reads* stayed **green, exit=0**. Not a hole — the opposite. The valve works by never
  reading statement bytes into memory, so leaking what it reads leaks nothing. The read
  boundary is the mechanism; the print statements are not.
- **(C) a second null, explained.** Removing only the `## Agent-supplied` break stayed
  green, because the `episode_id`/`run` break fires first on a well-formed record. That
  break is live defence for the **malformed** path, and probe CC3c confirms that path
  refuses with a path-only message and no sentinel.

Restore verified twice over: sha256 `bd90bb29…73b90` identical before and after every
mutation, `git hash-object scripts/verify_episode_captured.py` =
`74cc85594ce4d67f76f2de4dd56f2e0ff2ac3f6f` unchanged, `git status --porcelain` showing
only the three intended paths, and `pytest tests/test_verify_episode_captured.py -q`
green again at **exit=0, 15 passed, 4 subtests**.

**Criterion 5 — grep really would have false-passed.** My `ast` parse:
`IMPORTS = ['__future__','argparse','pathlib','re','subprocess','sys']` — stdlib only.
No repo-local `scripts/` module (checked by testing `scripts/<name>.py` existence for
every imported top-level name), no `query_episodes`, and no dynamic-import escape hatch
(the only matching `Call` names are `re.compile` and `path.open`).
`grep -c query_episodes scripts/verify_episode_captured.py` returns **1** — the
docstring — so a text search would have had to reason about prose to get this right.

**Criterion 6 — exceeded.** The suite with colour disabled exits **0**:
`1715 passed, 2 skipped, 1 xfailed, 554 subtests passed in 256.29s`. The waived
`FORCE_COLOR` class does not merely stay scoped, it disappears entirely, exactly as the
Commander root-caused. There was no failure to grade against the waiver at all. The
load-sensitive `test_crew_launcher` flake did not reproduce. Count reconciliation: the
implementer measured 1705 passed / 10 failed under forced colour; those 10
`test_mutation_floor` cases pass with colour off, which accounts for the delta by name.

**The mid-run defect fix holds.** `--store-root episodes --phase archive` against the
real store: **EXIT=0**, 25 episodes recorded. Independently reproduced in my own temp git
repo with a relative root and cwd inside the repo (probe CC2d): **exit=0**. The fix is
`path = path.resolve()` at `scripts/verify_episode_captured.py:166`, regression-tested at
`tests/test_verify_episode_captured.py:224` through a subprocess with a relative root.

## Scope drift

None. `git status --porcelain` (exit 0) shows exactly four entries:

```
 M scripts/apply_episode_delta.py
?? .agent-work/epic418-h-447/
?? scripts/verify_episode_captured.py
?? tests/test_verify_episode_captured.py
```

Comment-only claim confirmed: `git diff --numstat` = `12  0  scripts/apply_episode_delta.py`,
and `git diff -U0` shows all 12 added lines beginning `+    #` with zero deletions and
`store_root()`'s return statement byte-unchanged.

Every specific exclusion is clean, each checked by command:
`git status --porcelain -- episodes/` empty; `-- skills/ scripts/install_constellation.py '*spine*'`
empty; `-- scripts/verify_retirement.py` empty. No commits, HEAD unmoved, branch still
`epic-418/h-447-episodes-retirement`.

## Evidence verdict

Sufficient, and independently reproducible — which I confirmed by reproducing all of it.

Test mode was never named in the handoff (the implementer flagged this too); read as
test-first, and the delivered evidence is stronger than the field would have demanded.
The tests are behaviour-focused: they assert exit codes and stream contents from a
subprocess, never the text of a message describing behaviour.

Two of the repo's own verification-discipline rules are honoured **by the change
itself**, which is what raises this above a passing suite:

- the sentinel guard asserts what it looped over (`self.assertEqual(len(cases), seen)`),
  so it cannot pass by looping over nothing;
- the import guard asserts the parsed import set is non-empty *before* asserting what is
  absent.

I also refused to take the Fowler rail's green on trust and proved it can fail: dropping
`feature-envy` → **exit 1** (`skipped baseline smell`); stripping `shotgun-surgery`'s
override block → **exit 1** (`OVERRIDE-LOG`).

## Code/doc quality

Minimal, tested, and project-rule compliant.

- **`python`, never `py`** — `grep -nE` for a py-launcher across both new files: **exit 1**,
  no match. The tests shell out with `sys.executable`, which inherits the running
  interpreter rather than re-resolving a launcher. Every command in this review used
  `python`.
- **Windows writes** — all three file handles carry explicit encoding and newline:
  `verify_episode_captured.py:85` `open(encoding="utf-8", newline="")` (read, raw
  newlines preserved, matching `apply_episode_delta.read_text_exact`); `tests:93` and
  `tests:181` `open("w", encoding="utf-8", newline="\n")`.
- **Record stores never hand-edited** — `episodes/` untouched by command. Every test
  seeds a `tempfile.TemporaryDirectory` store through `apply_episode_delta.py`, the only
  sanctioned write path. The real store is only ever *read*.
- **Scope discipline** — all four declined corner cases carry their comment **at the
  stated file:line**. I opened each one; none was a paraphrase pointing elsewhere:
  `verify_episode_captured.py:196-201` (the `--store-root` default hazard, directly above
  the line it describes), `:151-161` (`_git_tracked` cannot distinguish untracked from
  not-a-repository), `:125-130` (`retired/` deliberately not searched),
  `apply_episode_delta.py:511-522` (the `store_root()` hazard, with the `durable_root()`
  ruling above it byte-unchanged). Each names the case, why it was not chased, and what
  closes it. That is the sanctioned exit under Tommy's standing ruling, taken correctly.

**Fowler refactoring pass** — `python scripts/verify_fowler_pass.py .agent-work/epic418-h-447/g2-review/fowler-pass.json`
**EXIT=0** (`smells=12, flagged=['message-chains'], overridden=['long-method',
'duplicated-code', 'shotgun-surgery', 'divergent-change', 'comments-as-deodorant']`).

One flag, an observation not a blocker — **message-chains**, `verify_episode_captured.py:201`:
`Path(__file__).resolve().parent.parent / "episodes"`. Fowler's objection to a message
chain is that the caller is coupled to a traversal it does not own, and that is exactly
this chain's failure mode: on a copy installed under `~/.claude/skills/<role>/` it
resolves to the skill directory instead of the repo, so the gate would report green
against a store outside the project. Not a blocker on three grounds — it is named in a
comment at the code site, the resolved root is printed on every outcome so a wrong root
is visible in the gate log rather than silent, and it is already floated as an open
decision for g3.

Two overrides are worth surfacing because they are decisions, not dismissals:

- **shotgun-surgery — overridden.** The gate hardcodes `ACTIVE_DIR = "active"` instead of
  importing it from the writer, so a partition rename touches two files. That smell is
  real. But importing the writer is precisely what `constraint:episodes-are-not-prescriptions`
  (@grade settled/human) forbids — it would pull the record parser, statement field and
  all, into this module's namespace. A `settled/human` anchor is not mine to unsettle for
  a refactoring preference, and the trade is logged at `verify_episode_captured.py:47-51`
  rather than left implicit.
- **comments-as-deodorant — overridden.** Comment and docstring prose is a large fraction
  of the 245-line module. Under a naive read that is deodorant. It is not: Tommy's
  standing scope-discipline ruling *mandates* exactly this density (three of the four
  declined corner cases **are** these blocks), and what the prose carries is design
  intent the code cannot express. Deodorant hides unclear code; this records a constraint
  that would otherwise be one innocent refactor from violation — and my mutation testing
  confirmed the **code**, not the prose, is what enforces it.

## Map impact verdict

- **Evidence supports claimed change:** yes. The claimed capability — "a run must leave an
  episode behind, machine-checkable at two strengths" — is backed by a matched pair I ran
  on the *same* store: untracked episode passes at `--phase feedback` (exit 0) and blocks
  at `--phase archive` (exit 1), then passes after `git add` (exit 0). Archive is feedback
  plus one predicate, exactly as claimed.
- **Constraints not violated:** the valve holds under three independent lines of attack.
  *Structural:* stdlib-only imports, no store reader reachable. *Behavioural:* I seeded my
  own sentinel (`REVIEWER-SENTINEL-LEAK-CANARY-7c31`) into every assertion statement of
  every episode across 10 throwaway stores and ran the gate as a subprocess over all
  outcome paths — captured, blocked, other-runs-only, archive-blocked, archive-passed,
  refused-missing-root, refused-missing-active, refused-malformed, feedback-on-untracked,
  relative-root-archive. Sentinel in stdout or stderr: **false on all 10**. *Mechanistic:*
  the emitted surface is ids, counts, paths and git's own diagnostics — no statement, no
  ripeness, no counters, no dormancy, no apply-or-defer. `constraint:record-stores-never-hand-edited`
  and `constraint:doctrine-lives-in-docs-agents` are likewise intact.
- **Notes match the diff:** yes, with no overstatement. A new script-level structural
  anchor, a comment-only touch on `apply_episode_delta.store_root()`, a new capability at
  two strengths, and the valve constraint moving from prose to a test with a working red
  proof.
- **Decision candidates surfaced:** yes, both correctly floated rather than settled — the
  1-vs-2 exit split (decided within latitude, coherent and tested) and the `--store-root`
  default on an installed copy (left open for g3). No contradiction with either
  `settled/human` anchor.
- **Durable context routed:** yes. Four triage candidates are on the survey
  (`tc1`–`tc4`); the g1 guard's `replacement-absent` leg remains the standing pointer to
  g3.

## Reconciliation check

Nothing needs Commander reconciliation. `docs/EPISODE_STORE.md` describes the store's
record grammar and write contract, neither of which changed; the gate's contract lives in
its own module docstring, which is the right home.

The g1 guard is untouched and its `replacement-absent` leg is RED exactly as the handoff
predicts — 4 findings, all naming the install bundles and the two spine templates, all
closing at g3. **Critically, the g2 diff introduces no new `verify_retirement` finding.**
I scoped this by command rather than by eye: the guard reports 137 findings
(4 `replacement-absent`, 128 `retired-name-on-shipped-surface`, 5 `retired-path-still-tracked`),
and the only ones naming a g2-touched file sit at `apply_episode_delta.py` lines 10, 40
and 987 — all pre-existing `apply_lessons_delta` references, none inside the added
511-522 block, and no finding names either new file.

## Blockers

**None.** Nothing is waiting on the Commander, the Admiral, or the human. The valve could
not be shown to leak on any path I could construct.

## Out-of-scope observations

1. **Reviewer survey template gap (`tc1`).** `skills/reviewer/templates/REVIEW_SURVEY.template.json`
   ships `r6-fowler` with an unfilled postcondition placeholder,
   `python scripts/verify_fowler_pass.py <fowler-pass-record-path>`. Its own imperative
   orders the reviewer to fill it, but the engine exposes no verb to do so (`amend` is
   gated-only) while doctrine forbids hand-editing the work file. Detail in Workflow
   Feedback below — this one cost real time and has a Windows trap in it.
2. **`docs/agents/engine-config.json` does not exist (`tc2`).** Every checklist in this
   work area names it as `config_ref` — g1's review, both g2 crew plans, this survey — and
   the engine silently accepts the dangling reference. `ls docs/agents/` returns
   `CREW_CONTEXT.md`, `GLOSSARY.md`, `ORCHESTRATOR_CONTEXT.md` only. So the rework cap and
   human-checkpoint policy are running on built-in defaults nobody chose. Independently
   confirms the implementer's finding.
3. **`tests/test_mutation_floor.py:255` needs a real fix (`tc3`).** The Commander
   root-caused the colour-defeated regex for this run, but nothing is filed. Measured
   here: forced colour → exit 1 with 10 HARNESS ERROR failures; `FORCE_COLOR=0 NO_COLOR=1`
   → exit 0, 1715 passed. Until the harness strips ANSI or pins `FORCE_COLOR=0` for its
   own nested pytest, this class permanently masks any genuine regression in that file.
4. **Two counts in prose were never re-derived (`tc4`).** Both the IMPLEMENTER_RESULT and
   the REVIEWER_HANDOFF say "16 tests"; `pytest --collect-only -q` reports **15** (exit 0).
   The result says the script is "223 lines"; `wc -l` reports **245**. Cosmetic and
   behaviourally irrelevant, but it is exactly the shape `global-everyone.md` §"Pin a claim
   to the revision you read it at" warns about.
5. **A boundary worth naming, not a defect.** The gate prints the `id` header field and
   the `- run:` value. Both are writer-assigned or caller-supplied, so the valve's
   guarantee formally depends on `apply_episode_delta.py`'s field validation holding —
   an episode hand-written with statement text stuffed into `id=` would surface it. That
   is already forbidden by `constraint:record-stores-never-hand-edited`, so the
   composition is sound; I note it only so the dependency is recorded rather than assumed.

## Workflow Feedback

- **Handoff gaps:** the handoff was unusually good — the transient-failure scoping note
  scoped **by root cause rather than by file name**, which is what let me grade criterion
  6 honestly instead of waving at a filename, and telling me *up front* that grep
  false-passes on criterion 5 pointed me straight at `ast`. Two real gaps. (a) **Test mode
  was never named** — the same field the implementer flagged; I had to infer test-first
  from "prove the valve, do not assert it" in order to judge whether the evidence
  satisfied it. (b) The **"16 tests"** figure in *What Was Implemented* is wrong (15), and
  since the handoff is what I grade against, a wrong count there briefly read as a missing
  test before `--collect-only` settled it.
- **Context rediscovered:** the `episodes/` delta JSON shape needed to seed a throwaway
  store through `apply_episode_delta.py` — five mandatory `agent_supplied` kinds, the exact
  mechanical field allowlist, writer-assigned ids. I reconstructed it from the
  implementer's test file. Since an independent reviewer *must* build fixtures without
  reusing the implementer's helpers, a Map Anchor pointing at the seeding contract would
  save every future reviewer of this store the same dig. The implementer asked for the
  same pointer from the other side, which makes it a two-sided gap.
- **Instructions improvised around:** the `r6-fowler` postcondition placeholder. The
  imperative says "fill this item's postcondition command with the real record path", the
  engine has no verb for it, and `global-everyone.md` says opening the work file to change
  state is a violation. I read filling a template placeholder as *plan authoring* (which
  `checklist-engine.md` explicitly sanctions: "fill placeholders, then drive with the
  engine") rather than state mutation, and did the narrowest possible version: replaced
  the single `check.command` string, left the engine's own failed-run evidence record
  untouched, and diffed against a pre-edit copy to prove exactly one line moved. **The
  Windows trap is worth flagging loudly:** my first attempt used text I/O and silently
  rewrote all 371 CRLF line endings in the engine's state file. I caught it on the diff,
  reverted byte-for-byte from a copy, and redid the edit in **binary**. Anyone following
  that imperative on Windows with `read_text`/`write_text` will corrupt the work file's
  line endings and not notice. This is `tc1`.
- **What would have made this easier:** make the Fowler rail resolve its own record path
  by convention (`.agent-work/<work-id>/<gate>-review/fowler-pass.json`) and drop the
  placeholder from the template entirely. That removes the one instruction in this run
  that could not be followed without editing a file the engine owns.

## Return status
`complete`

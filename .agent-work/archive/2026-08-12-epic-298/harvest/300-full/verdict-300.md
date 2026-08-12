# Verdict — issue #300 (projection generator + manifest), epic-298 wave 0

## 1. Verdict

**BLOCKED on an Admiral float — by design, at the launch order's own named stop condition.** The
design-it-twice comparison on the manifest interface is complete and carries a defended
recommendation; `decision:convergence-is-human` makes the pick Tommy's, not mine. Everything that
does not depend on that pick is done: the baseline is verified against code, the problem statement
and mission frame are written, and a cold-critic-hardened gate plan is frozen in the engine and
ready to execute the moment the ruling lands.

Spine state: `init → context → understand → plan` **complete**; `execute` **pending**. Lease
`commander-300` still held (not released — this is a mid-mission return, not a closeout).

**This is not an honest-null.** The mission's premise is genuinely unbuilt at HEAD. But it is
narrower than the issue reads, and that is a real finding: the deterministic *selector* already
exists; only the declaration, the assembly and the record are missing.

## 2. Evidence

### 2a. Baseline verified against code before planning

Per `lesson:verify-launch-order-claims-against-code`. The order and the confirmed spec both name
"the spine's existing gate-note loading" (spec Assumption 5, "partially grounded") as the thing to
extend. What is actually there at `b69e6c8`:

- **Real:** the engine's `current` verb is exactly `render_human(state(cl))`, where `state(cl)` is a
  *pure* state projection port carrying a `contract` version int (`scripts/checklist_engine.py`
  :1336–1471, documented in `docs/CHECKLIST_ENGINE_DESIGN.md` §Answerability). It selects the active
  spine step deterministically and prints that step's `imperative`. Selection is genuinely
  deterministic, mechanical, and spine-keyed.
- **Absent:** assembly. Every canonical Markdown file is named only *inside imperative prose*
  (`references/global-orchestrator.md`, `references/global-everyone.md`,
  `docs/agents/ORCHESTRATOR_CONTEXT.md`, `.agent-work/LESSONS.md`, …) and opened by hand. There is no
  machine-readable declaration, no assembler, and no record of what was loaded or at what revision.
- **Negative greps:** `grep -rniI "projection" scripts/ skills/ docs/ tests/` returns only the
  engine's *internal* state projection and unrelated Charter vocabulary; `grep -rniI "manifest"
  scripts/` returns only the installer's `TEMPLATES_MANIFEST.json` and `file_issue_set.py`'s
  issue-set manifest. Neither is a context manifest.

**Consequence for the epic:** spec Assumption 5 is weaker than it reads. Its grounding covers
deterministic *selection* only. Worth recording, because the spec leans on it to justify B2.

### 2b. Design-it-twice — 3-author panel (required, non-skippable)

`.agent-work/300/DIT-COMPARISON.md`; candidates in `.agent-work/300/dit/`. Three Opus authors, one
named distinct constraint each, none seeing the others: **A minimal-interface**, **B
ports-and-adapters**, **C common-caller-first**. Compared on depth / locality / seam placement /
testability, plus foreclosure risk as a fifth axis. Untaken roads named (a fourth "assertion-native"
candidate, and regex-extraction-from-prose), panel-vs-single record kept.

**All three converged independently on four things** — I first reported five; one was retracted, see
§2b-bis. The four: revision identity is the **git blob OID of LF-normalised bytes** computed
in-process (each author verified equality with `git hash-object` on real files, including CRLF twins;
all three rejected a commit SHA, which lies about dirty trees and says nothing about untracked or
out-of-repo files); the declaration is a new **optional** ordered spine-task field; **no globs ever**
and declaration order is content; the **imperative prose stays** (it carries the substitute-and-record
and sanctioned-degradation rules a path list cannot express) with a mechanical lint pinning the two.

**The genuine disagreement, and the actual decision for Tommy:** does #300 ship a **committed,
diffable artifact** — more files touched now, but the spec's "every doctrine change produces a
reviewable diff of what agents will actually see" becomes true immediately — or only a **run-time
record**, smaller and cleaner now, with the diff landing later in issue #306?

**My recommendation (floated, not taken):** the hybrid *"C's two artifacts, A's row, B's resolver"* —
a committed content-only artifact per role with **zero** varying fields, plus a run-local twin whose
entire exclusion set is one JSON pointer `/run`; a minimal `{root, path, rev}` row; one pure producer
selecting via the **existing** `active_id()`; B's injectable resolver kept, B's speculative
declaration port and two-encoder split dropped (B's own author disowns Port A).

**The defect the comparison produced that no single candidate had:** `rev` for a non-tracked file is
environment-varying. Candidate A recorded a real OID for `docs/agents/ORCHESTRATOR_CONTEXT.md`;
candidate C recorded `absent` for the same file — both honest about their own environment, mutually
contradictory, and a committed artifact built either way would false-FAIL its own drift check on the
next machine. Fix: the committed artifact resolves `rev` **only from the git object DB** (untracked →
`null`, deterministic anywhere); the run manifest resolves from the **bytes actually delivered**.
Same row shape, two truth-sources — which is the ahead-of-time-vs-per-run distinction spec B2 already
draws.

### 2b-bis. Shared-assumption audit — a retraction and two closures

Added after the comparison froze, prompted by sibling #301's finding (relayed by the Admiral): **a
panel varies what it is told to vary and inherits everything it is not**, so a shared wrong
assumption is the one thing a comparison structurally cannot see. #301's four candidates unanimously
chose a gitignored store location and none caught it. Full audit in the addendum to
`.agent-work/300/DIT-COMPARISON.md`.

**The mechanical check clears.** `git check-ignore` on all ten paths this recommendation names: nine
tracked-eligible, one ignored — `.agent-work/<work-id>/context/<step>.json`, the run-local manifest,
which is *meant* to be ephemeral and was already floated as #301's inline-vs-reference decision.
#301's specific error does not reproduce here.

**The retraction.** I reported five independently-converged findings. One of them — "metadata only,
never file content" — was **my own brief handed back to me three times**: I wrote "delivery, not use"
into the shared brief as a fixed constraint, so the authors' agreement on it is not evidence of
anything. Presenting it as panel convergence was an over-claim of exactly the manufactured-consensus
shape #301 hit. **Four converged findings, not five.** The same hair splits on the identity finding:
"identity comes from git" was *given* (I put `markdown-in-git` in the brief); what was genuinely
derived and independently verified is the sharper claim — blob OID rather than commit SHA,
LF-normalised, computed without a subprocess. That part stands.

**Closure 1 — an inherited location, now a stated obligation.** All three authors put the declaration
on the spine task object without anyone asking whether it belongs there; the alternatives were never
generated. Asking the question surfaces a real consequence: `spine.json` is *instantiated per work
area from the template*, so the declaration is copied in at init and a doctrine change never reaches
in-flight work areas. That is arguably correct — per-run fidelity is what a delivery record wants —
but a spine instantiated last week and today's committed artifact can legitimately disagree, and a
naive drift check would call that drift. Not a reason to reopen the panel; it is an **obligation on
issue #306**: the drift check compares canon against the committed artifact, never against an
instantiated work-area spine. Now stated instead of assumed.

**Closure 2 — a silent-divergence hazard, now a mechanical invariant.** All three verified the
blob-OID equality under this repo's `.gitattributes` as it stands (`* text=auto`, no exemption), and
none asked what happens if a path is ever marked `-text` or `binary` — git would stop normalising it
and the in-process hash would silently diverge from `git hash-object` for that path. Closed through
the engine's `amend` verb (one `rescope` on the pending `g1-implement`, audit entry recorded), adding
`c7`, verified in **both** directions: exit 0 today, exit 1 after appending `*.md -text`, tree
restored clean. This is the *correct* use of the bash-negation wrapper — it wraps the thing that must
fail to match — in deliberate contrast to the cold critic's B1, where the same wrapper on a probe
inverted the check silently.

**Closure 3 — CI interpreter pin.** The Admiral flagged that #301's PR went red on
`Path.read_text(newline=)`, which is 3.13+. Verified: CI pins `python-version: "3.12"`
(`.github/workflows/ci.yml:34`) while this host runs **3.14.3**. The same amendment adds that as a
gate constraint and folds a `py312_compatible` assertion into `g1.c6`, so the trap is pinned before
any test-authoring crew meets it rather than after CI does.

### 2c. Plan-alternatives and the mandatory cold plan critic

`.agent-work/300/PLAN_ALTERNATIVES.md` — 3 gate-plan candidates (seam-first / smallest-diff /
most-testable) converged to one recommendation, untaken roads named.

`.agent-work/300/PLAN_CRITIC_DISPOSITION.md` — cold plan critic run as **mandatory** per
`lesson:cold-critic-mandatory-for-measurement-dependent-plans`. **19 findings (5 BLOCKING, 7 SERIOUS,
7 MINOR), every one dispositioned, UNTRIAGED: 0.** It earned its keep immediately:

- **Two postconditions passed at HEAD with nothing built.** I reproduced both before acting.
  `! A || B` bound the bash negation to a *collection probe* rather than to the lint, so the one
  check whose purpose was "prove the guard fires on bad input" was satisfied by never writing the
  guard (measured: exit 0). And `grep -qi 'context' docs/CHECKLIST_SCHEMA.md` already matched 10
  lines.
- **`py -m pytest` has no pytest on this host** (`python -m pytest` → pytest 9.0.2). Six command
  postconditions were unrunnable as written. Verified myself.
- **No gate enforced an APPROVE verdict** — the house template's `match: {"verdict": "APPROVE"}` was
  missing, so a BLOCK would have advanced every gate.
- **The pre-ruled acceptance test sat inside the one deletable gate.** If the Admiral rules the
  committed artifact out of scope, the old cut would have shipped a declaration with zero users,
  vacuously-empty manifests, a lint green because there was nothing to pin, and **no
  cross-environment determinism evidence at all**. Re-cut so the contingency is isolated to `g2`
  alone; deleting it now leaves #300 whole. The `most-testable` plan alternative reached the same
  conclusion independently by a different route.

**Post-fix verification:** all **21** command postconditions executed verbatim in bash at HEAD. Every
check that should fail today fails (exit 1, 2 or 4); the only three that pass are the two prose
non-regression invariants and the full suite — `python -m pytest tests/ -q` → **exit 0**, a real
green baseline. **No postcondition in the frozen plan passes vacuously.**

### 2d. The determinism exercise — what it will actually prove

Strengthened past what the critic asked, and stated with its limit. It is now a mechanical
`kind: command` check (not a self-attestation): `tests/test_context_determinism.py` creates a **clean
second checkout** (`git worktree add` at the same commit, different path) and rebuilds there under
mutated `LC_ALL`/`LANG`/`PYTHONHASHSEED`, then byte-compares. That exercises all three named
irreproducibility sources — line endings (via CRLF/LF twin fixtures), filesystem and path ordering
(different checkout), locale and hash ordering (mutated env).

**What it will not prove:** same OS, same filesystem. This is not a cross-OS rebuild. The plan says
so rather than letting the evidence overclaim. A carry-over hazard is flagged in the gate:
`lesson:windows-subprocess-env-does-not-shadow-path-resolution` means the locale arm must *assert the
mutation took effect inside the child*, not assume it.

Per `lesson:round-trip-tests-prove-artifacts-not-parsers`, adversarial fixtures are frozen into the
plan alongside it: CRLF/LF twins must agree; a stale manifest must **not** silently PASS; an
untracked-vs-absent file must not make two environments disagree; a declaration-order permutation
**must** register as drift.

### 2e. Test commands and exit codes

| Command | Exit | Meaning |
|---|---|---|
| `py scripts/verify_worktree_isolation.py --here …` | **0** | isolation proven (§3) |
| `python -m pytest tests/ -q` (at HEAD) | **0** | full suite green — the baseline |
| `python -m pytest tests/test_checklist_engine.py -q` | **0** | engine suite green |
| `py scripts/apply_lessons_delta.py --dry-run …` | **0** | staged lessons delta validates |
| 21 gate postconditions, verbatim | 1/2/4 as designed | nothing vacuous |

**PR number and merge state: none.** No code has been written — the run stopped at `execute` before
any implementer crew was dispatched, which is the sanctioned mid-mission return. Nothing to merge.

## 3. Worktree isolation

```
$ py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-wt/298-300
worktree OK: in C:/Programs/constellation-skills-wt/298-300
EXITCODE:0
```

Run as the mandatory first action, before any git operation. **Caveat worth carrying:** under
PowerShell the same command printed *nothing* and `$LASTEXITCODE` came back empty; only under the
Bash tool did it print and return 0. The one command a delegated Commander runs before it knows
anything is silently uninformative in one of the two shells this platform offers.

## 4. Map impact

This skill-source repo has no `docs/architecture/` packet map; the structural record is
`docs/CHECKLIST_ENGINE_DESIGN.md`, `docs/CHECKLIST_SCHEMA.md`, `docs/CONSTELLATION_OVERVIEW.md`.
What the epic's architecture record should now say that it does not:

1. **Assumption 5 is weaker than the spec states.** "The spine's gate notes already work this way"
   grounds deterministic *selection* only. Assembly has never existed. Any later element leaning on
   Assumption 5 should lean on the narrower claim.
2. **The engine has a reusable projection-port idiom** (`state(cl) -> dict` pure projection +
   `render_human` adapter + `contract` version int) and it is the seam this substrate extends.
   `CHECKLIST_ENGINE_DESIGN.md` §Answerability documents it for `current` only; it is now a
   general pattern with a second instance.
3. **The Task object gains an optional `context_refs` field** — the first machine-readable statement
   of what a spine step delivers. `docs/CHECKLIST_SCHEMA.md`'s Task table needs a row (frozen as a
   pre-authored invariant in `g3`).
4. **Two verified environment facts that constrain any future durable-root work:**
   `agent_work_root.py` returns the **worktree**, not the main checkout, while an Admiral lease is
   active; and the engine does **not** pass `cwd=` to command postconditions.
5. **Revision identity has a settled answer** — git blob OID of LF-normalised bytes — reached
   independently by three authors and verified against live bytes. Worth recording as a decision
   anchor so it is not re-derived.

## 5. Triage candidates — filed, not banked

Filed directly to the tracker per the pre-clearance (`gh issue create`), so nothing is trapped in
this worktree:

- **#315** — engine: command postconditions inherit the launcher's cwd (`_run_check_command` passes
  no `cwd=`, unlike `_git` in the same file).
- **#316** — doctrine: a delegated Commander running as a teammate cannot spawn named or background
  subagents, but `commander-core.md` tells it to do both.
- **#317** — corpus: every spine template carries a `config_ref` to a path that is absent-by-design,
  plus prose explaining that it is dead.

## 6. Workflow feedback

- **Two harness refusals, one dispatch round-trip each.** A delegated Commander runs as a teammate;
  teammates can spawn neither *named* subagents ("the team roster is flat") nor *background* ones.
  But `commander-core.md` requires telling every background subagent to deliver via `SendMessage`,
  and the delegated skill says to poll a crew's result artifact in a loop while waiting. Both are
  unfollowable at this tier. Not blocking — multiple *synchronous* `Agent` calls in one message do
  run concurrently, and the result file is a fine delivery channel — but a Commander that trusts the
  doctrine burns both. Filed as #316.
- **`py` vs `python` is a live trap and the repo has no house style.** Both conventions appear in the
  repo's own docs. `py scripts/foo.py` works; `py -m pytest` does not.
- **The launch order and the skill text disagree about ending the turn.** The order names the
  convergence float as "the expected mid-mission return"; the skill says never to end a turn with a
  spine step pending. They reconcile — the frozen order is the principal and wins — but only after
  you notice. One clause in the order would remove the hesitation.
- **The launch order was unusually good.** The `notes-300.md`-not-`findings-300.md` warning saved a
  guaranteed round-trip (the `Write` guard does refuse that basename). Grading every pre-ruling made
  it immediately clear which were mine to revise and which were not.
- **Doctrine held under test:** three lessons were confirmed with grounding rather than merely cited
  — cold-critic-mandatory (a third convergent data point, and the first with a directly attributable
  counterfactual), round-trip-tests-prove-artifacts-not-parsers (a *new* failure mode: the round trip
  promoted **above** the discriminating evidence, in a plan that quoted the lesson in its own
  constraints), and verify-launch-order-claims-against-code (a fourth data point, third distinct
  failure mode: the named baseline exists but is materially weaker than the framing implies).

Staged durable trio (validated, ready to harvest): `.agent-work/staged-feedback/300/` —
`lessons-delta.json` (3 confirms + 2 adds; dry-run against the real playbook exits 0),
`AGENT_FEEDBACK.md`, `CONSTELLATION_FEEDBACK.md`, `FENCE.md`.

## 7. What the Admiral needs to decide

1. **The convergence pick** — my hybrid, one candidate as-is, or a different hybrid. Tommy's call.
2. **Is the committed artifact in scope for #300, or issue #306's?** The cold critic independently
   observed that none of #300's three acceptance criteria names a committed artifact; the spec's B2
   ahead-of-time-generation bullet is what argues for it. Answering only this second question is
   enough to unblock everything.

`g1` is fully non-contingent and starts the moment the ruling lands. `g2` is the only gate the ruling
can delete, and it is removed with the engine's `amend` verb, never a hand-edit.

---

# FINAL — run complete, closeout blocked on the Admiral (2026-08-01)

Supersedes the mid-mission verdict above, which was written before any code existed.

## Verdict

**SHIPPED — PR #324, CI SUCCESS, `mergeStateStatus CLEAN`. Deliberately not merged, not archived,
lease not released.**

Three commits on `epic-298/300`: `75ee317` (substrate), `5dbbaae` (doctrine + lint), `0b15d5b`
(cold-panel fixes). All 8 execute gates closed through 3 rework rounds. Spine `archive` is `blocked`
in the engine, not silently skipped.

## What shipped

The deterministic projection substrate and its manifest: revision identity as the git blob OID of
LF-normalised bytes computed in-process; an optional ordered `context_refs` declaration on the spine
task; a pure producer reusing the engine's **existing** `active_id()` selector; the manifest under
`.agent-work/` per Tommy's ruling, with one envelope whose entire exclusion set is the single `/run`
pointer; the first real declaration; a cross-environment determinism acceptance test; a
declaration-vs-prose lint bounded at both ends; and the `#301` obligations statement.

## Evidence

- `python -m pytest tests/ -q` → **1234 passed, 2 skipped** (both pre-existing, allow-listed)
- `python scripts/verify_skip_guard.py junit-report.xml` → exit 0
- `py scripts/verify_context_declaration.py skills/commander/templates/COMMANDER_SPINE.template.json`
  → 0 offenders
- CI verified **at source** on PR #324, not from a reported local green
- The CI condition that produced the g1 blocker independently reproduced by me in a clean detached
  worktree with no `.agent-work/` present

## Review

Full cold-panel class. **Two independent reviewer BLOCKs and a three-lens cold panel; 3 rework
rounds.** 41 panel findings, all dispositioned, **UNTRIAGED: 0** —
`.agent-work/300/COLD_PANEL_DISPOSITION.md`.

The finding that justifies the review class: **the issue's single acceptance test was not falsifying
the property it exists to falsify.** It re-encoded both children's parsed artifacts with the
*parent's* encoder, so an environment-dependent encoder passed green; and `/run` was not really the
exclusion set, because the check was one-directional and blind to added keys. Both had survived two
approved reviewer rounds. That is not reviewer failure — a reviewer given a handoff checks
conformance to that handoff, and no handoff asked whether the test could fail. The panel's 45-mutation
sweep (11 survivors) is what found it.

## My own errors, recorded

1. I inverted the lint's direction in a handoff — propagated from a design-panel candidate's framing,
   the same inheritance hazard I had flagged upward an hour earlier.
2. I wrote a `!`-negation postcondition bound to a *probe* rather than the guard, so it passed with
   nothing built.
3. I put a gitignored `.agent-work/` path into a committed docstring; three critics caught it
   independently.

## Blocked on the Admiral — two dependencies, neither mine

1. **The scope float is unanswered.** Nothing in production calls the producer, so AC1 holds
   definitionally over zero assemblies. If that is correct scoping (wiring is #305's), the PR merges
   as-is; if #300 is incomplete, the work belongs **on this branch** — which is exactly why I did not
   merge first.
2. **Archive and lease release are held by the Admiral's own instruction.** Every artifact this run
   produced lives only in gitignored `.agent-work/`; archiving before harvest is the shape
   `lesson:harvest-before-sweep-enforcement-gap` describes.

## Filed, not banked

**#315** (engine command postconditions inherit the launcher's cwd), **#317** (spine templates carry
a dead `config_ref`), **#323** (14 consolidated cold-panel follow-ups, plus a comment adding that
nothing runs the lint and that `context_manifest.py` is on no install bundle — which bites whichever
of #301/#305 first invokes it from an installed skill). Comments on **#314** and **#311**. **#316**
closed as my own duplicate of #314. One item deferred to **#304**.

## Staged for harvest — now four files, and the order matters

`.agent-work/staged-feedback/300/`: `AGENT_FEEDBACK.md`, `CONSTELLATION_FEEDBACK.md`, `FENCE.md`, and
**three** delta files. `LESSONS.md` hit **20/20** during my feedback step, so `lessons-delta.json` is
confirms-only (confirms cost no cap; dry-run exit 0), with `lessons-delta-AFTER-301.json` and
`lessons-delta-WHEN-CAP-ALLOWS.json` carrying the ordering-dependent and cap-dependent ops. `FENCE.md`
explains which adds I dropped and why: two are held more durably by #314 and #311 than a transitory
inbox would hold them; the survivor is the one with no tracker home.

---

# ADDENDUM 2 — Tommy's doctrine-version ruling, folded in (2026-08-01)

A second human ruling arrived after the run had already blocked at `archive`: *"we should also give
doctrine a version so there's a little traceability... practically, it's just the repo rev number of
the last doctrine edit that is sufficient... heck it could just be the current repo version in
totality for ease."*

**Cost check first, because the Admiral bounded it.** One content field plus a doc line was the
stated budget, beyond which it went back to Tommy rather than inflating the issue. It fit. Folded in
as **one appended gate** (`g5-doctrine-version`) via the engine's `amend` verb rather than by
reopening `g1` — appending cost one new gate; reopening would have cascade-reset five already-reviewed
gates for the same result.

**What shipped:** the manifest's content carries `repo_rev: {commit}` alongside the per-file blob
OIDs. The two answer different questions and both are kept: the commit is coarse, human-facing "which
doctrine version"; the per-file OID remains the precise "which bytes did this agent actually get",
which is what a dirty, untracked or out-of-repo file needs and what a commit SHA cannot give.

**My placement error, and the reviewer who caught it.** I first put the dirty flag in **content**,
reasoning that a bare commit SHA lies about a dirty tree. I graded the placement a guess and named
the settle condition myself — *if two checkouts at the same commit disagree on the field, it belongs
in `/run`* — and then, in the same gate imperative, wrote the sentence that made the test unable to
reach that case: *"both children are worktrees at the SAME commit and are equally dirty."* That is
assuming the conclusion. The reviewer built the excluded case — two checkouts at one commit with the
dirt confined to a file **no declaration names** — and content diverged while the delivered canon was
byte-identical, because `git status --porcelain` is repo-wide. I reproduced the mechanism before
acting. `dirty` now lives in `run`, and content does not need it: the per-file OID already carries
the honesty the flag was reaching for.

That case is now a **permanent regression test**, and the reviewer confirmed it is not a third blind
test — control green, three of its own mutations red, including reverting the fix.

**Also confirmed by this ruling:** no committed per-role projection artifact ("doubling the saved
files in git seems like us doing too much work"), so `g2` stays deleted. And Tommy is un-gitignoring
`.agent-work/` on main — which changes the storage location's properties but **not** the row shape or
the identity function. That the design survives it untouched is the payoff of the no-case-analysis
choice the three panel authors converged on.

**Final state:** 9 execute gates closed, **4 commits**, PR #324 with CI SUCCESS and
`mergeStateStatus CLEAN`. Across the run: **3 independent reviewer BLOCKs, a full 3-lens cold panel,
4 rework rounds.** Three separate defects were the same shape — *a test that could not see what it
was written for* — and the move that caught all three was mutating the code and checking the test
went red.

**Still blocked on the Admiral, unchanged:** the scope float (nothing in production calls the
producer), and harvest-before-sweep plus lease release. Merge deliberately not taken, because if the
float rules #300 incomplete the remaining work belongs on this branch.

---

# MERGED (2026-08-01)

**PR #324 merged server-side as `b8e2aa0`.** All four commits verified present on `origin/main` via
`git merge-base --is-ancestor`: `75ee317`, `5dbbaae`, `0b15d5b`, `4d9571a`. Issue **#300 is CLOSED**
(auto-closed by the PR body).

Merge was gated on the **CI exit code at source** (`gh pr checks 324` → exit 0), not on a reported
local green, and on `mergeable=MERGEABLE mergeStateStatus=CLEAN` after waiting out GitHub's
`UNKNOWN` recompute window.

**On the delay before merging, since it is the one process call I got wrong.** I held a green,
reviewed, pre-cleared PR pending the unanswered scope float, reasoning that if #300 were ruled
incomplete the remaining work belonged on this branch rather than a follow-up. That reasoning was
weak — a follow-up PR is entirely normal — and the hold cost the epic time on a preference about
branch tidiness. The float being open does not make the merged work wrong; it only asks whether
*more* work is owed. Recorded as a workflow lesson rather than defended.

**Still open, and unchanged by the merge:** nothing in production calls the producer, so acceptance
criterion 1 holds definitionally over zero assemblies. If Tommy rules that a gap in #300 rather than
correct scoping (wiring belonging to #305), it is now a follow-up issue against a closed one — which
is the concrete cost of the merge, stated plainly so the decision is made with it in view.

**Remaining sequence, per the Admiral:** Admiral harvests `.agent-work/staged-feedback/300/` and the
run artifacts → I complete `archive` → I release the lease as the final journaled action, after the
closing advance. I do not sweep my own worktree.

**One correction for later readers of this verdict:** the launch order warned that
`docs/agents/ORCHESTRATOR_CONTEXT.md` would be absent from this worktree because it was untracked.
That was true all wave and is why this run substituted `docs/CONSTELLATION_OVERVIEW.md`,
`docs/CHECKLIST_SCHEMA.md` and `docs/CHECKLIST_ENGINE_DESIGN.md` as its structural record. It is now
**tracked** on main as of PR #325 (`6d93469`), so the warning is out of date.

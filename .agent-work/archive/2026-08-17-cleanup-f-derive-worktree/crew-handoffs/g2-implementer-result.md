# Implementation Result

## Assigned gate

`g2` — lane F, issue #609, "retire stamp-and-compare". Base `9ff86f2d`, branch
`cleanup/f-derive-worktree`.

## Completed slice

Stamp-and-compare is gone. The engine no longer compares `origin.worktree`
against anything, no longer reads its ambient cwd, and no longer spawns a git
subprocess per guarded verb. The stamp is still written by both producers and is
now read by nothing — a pairing pinned by a test that goes red if either half
breaks.

**The predicate degenerated, so I deleted it.** This was the judgment the handoff
delegated, and here is the reasoning it rests on. With the cwd comparison and the
`cwd is None` fail-closed branch removed, every remaining path of
`origin_worktree_refusal` returns `None`: verb not guarded → `None`; `origin` not
a dict → `None`; `worktree` not a non-empty string → `None`; and then nothing was
left. A function that returns `None` on every path is not a seam, it is a
comment with a call site, so it is deleted rather than kept.

**I also deleted `ORIGIN_GUARDED_VERBS` and `ORIGIN_EXEMPT_VERBS`.** Their only
production reader was line 149 *inside* that predicate — verified, not assumed.
Keeping them would leave exactly the hollow leftover the handoff forbids one
level up: data whose classification nothing consumes, pinned by a test. The
handoff's sentence "its guarded/exempt verb sets keep their current meaning" sits
inside the paragraph forbidding *new* refusals, and I read it as "do not widen
them", not "preserve them unread". They are one line to reconstruct from
`MUTATING_VERBS` if g4 is ever unblocked, and the rationale for the short exempt
set is preserved verbatim in the tombstone comment that replaced them. **If the
reviewer reads that sentence as literal preservation, this is the one decision to
reverse, and it is a two-line revert.**

**This gate does not consume `worktree_from_spine_path`**, stated plainly as the
handoff asks rather than wired in for appearances. With no comparison and no
refusal there is no question left in `main()` for a derived worktree to answer.
It remains consumed only by `tests/test_worktree_derivation.py:78`, so **this
gate is not its first consumer** — g5 (threading it into command-kind checks as
their `cwd`) is, and g5 is floated.

**What now occupies the position before `dispatch()`: nothing, and nothing is
lost.** That position existed so a refusal could be raised before `dispatch()`
and returned without `save()`, because `main()` persists state on the
`EngineError` path for every verb except `current` — a refusal raised inside
`dispatch()` would write into the tree it was protecting. With no refusal to
raise there is nothing there to order. The lease, which is the actual ownership
guard, is enforced inside `dispatch()` exactly as before.

## Scope

**Files changed:**
- `scripts/checklist_engine.py` — deleted `origin_worktree_refusal`, both verb
  sets, and the `git rev-parse --show-toplevel` call site in `main()`; repaired
  the now-false third clause of `worktree_from_spine_path`'s lexical-only
  rationale.
- `scripts/spine_lifecycle.py` — provenance note on `build_origin`.
- `docs/CHECKLIST_SCHEMA.md` — rewrote the origin section.
- `tests/test_spine_origin_isolation.py` — pre-authorized rewrite.
- `map/INDEX.md` — regenerated, never hand-edited.

**Specific exclusions touched:** no. No fenced file, template, installer or
`scripts/hooks/spine_rail.py` was modified; `spine_rail.py` needed no change, as
the handoff predicted.

## Behavior changed

Yes, and one delta is worth the Commander's attention.

Guarded verbs are no longer refused for standing in the wrong tree. The harm the
comparison existed against — two controlling agents on one spine — is still
refused, by the lease, measured on both sides (below).

**The one genuine behaviour delta: an unclaimed spine can now be claimed from a
foreign tree** (exit 1 → exit 0). I judge this not a case where the comparison
was the only thing preventing harm, on two measured grounds: the MCP door already
*required* exactly that transition to succeed and got it by `chdir`-ing into the
spine's worktree, which made the comparison `X == X` for the caller production
actually uses; and taking a lease on an unclaimed spine is what `claim` is for,
while the second-agent case is refused. It is stated here rather than buried
because it is the only place a reviewer could reasonably disagree with me.

> **Rework amendment (g2 rework 1, `ADMIRAL_RULING-1` R1; applied by the rework-2
> implementer, session `.../g2/implementer/attempt-3`).** The sentence above
> understates the delta and is corrected here rather than rewritten, so the
> original claim and its correction both stay readable.
>
> The delta is not confined to `claim`. It is **every mutating verb**, on **any
> spine with no active lease** — never claimed, *or* claimed and since released,
> because `_active_lease` reads a released lease as absent and `require_session`
> returns early when there is no active lease. Unlike `claim`, those verbs
> **write state into a tree the agent is not standing in**. Measured base vs
> tree from a foreign worktree: `start` and `attach` on a never-claimed spine,
> and `start` after a release, all went `REFUSED`/exit 1 → exit 0. On a spine
> under an **active** lease held by another session, nothing changed.
>
> Rework 1 landed this correction in the three prose copies
> (`scripts/checklist_engine.py`, `tests/test_spine_origin_isolation.py`,
> `docs/CHECKLIST_SCHEMA.md`) but died before amending this result, which was its
> C4. That is why the amendment carries a later session's name.

## Map Impact

- **Structural anchors touched:** `scripts/checklist_engine.py:102-179`
  (`origin_worktree_refusal`) — deleted. `:98-99` (the two verb sets) — deleted.
  The single impure call site — deleted; note its cited location `:3573-3578` was
  **stale**, the call site was really at `:3638-3643` (`:3573-3578` is
  `append_journal_entry`). `worktree_from_spine_path` survives untouched except
  for one docstring clause.
- **Capabilities affected:** the engine no longer has a location capability at
  all. `scripts.checklist_engine` drops 1213 → 1212 entities.
- **Constraints touched:** the refusal-before-`dispatch()`/without-`save()`
  ordering constraint is now vacuous and recorded as such in the code.
- **Decisions resolved:** `derivation-authoritative-stamp-becomes-provenance` is
  now realized in code and pinned by test. `not-a-weaker-guard` is measured, not
  asserted. **This supersedes the 2026-08-15 worktree-identity ruling**
  (`.agent-work/rulings/2026-08-15-worktree-identity.md`), cited in
  `docs/CHECKLIST_SCHEMA.md`, in the engine tombstone comment and in the test
  module docstring: that ruling settled how to resolve the two sides of a
  comparison that no longer exists.
- **Trust limitations / drift found:** stale prose describing the retired guard
  survives in seven places I may not edit — enumerated under Out-of-scope.

## Test mode

**Required:** test-first for the provenance pin, test-after for the deletions.
**Satisfied:** yes. The pin was written first and observed failing against the
unmodified tree for the predicted reason, then made to pass.

## Evidence

### 1. The guarded-verb path, before and after

`.agent-work/.../g2-implement/probe_guarded_verb.py` drives `start` through
`main()` from three cwds and records every git subprocess *with its call site*
(it wraps the shared `subprocess.run`, so it sees the whole process, not just the
engine).

**Before** — from the spine's own worktree, 8 spawns, the first being
`checklist_engine.py:785  git rev-parse --show-toplevel`. From a foreign git
worktree and from a non-git directory: `exit=1`, `REFUSED`, gate stays `pending`,
1 spawn — the guard's.

**After** — the `checklist_engine.py` toplevel spawn is **gone from all three**.
The only remaining `--show-toplevel` belongs to `episode_capture.py:95`, a
different module. All three cwds now give `exit=0`, no `REFUSED`, gate
`in-progress`, and `origin.worktree` unchanged in the file.

### 2. The verbs still refused where they should be, still are

`probe_other_refusals.py` drives seven non-origin refusal paths from the spine's
own worktree (so the comparison was satisfied even at base and cannot be what
refuses): unknown task, unmet precondition, impostor session, no session id,
unmet postcondition, `advance` with no `--why`, unforced non-owner `release`.

**Result: `exit=1 refused=True` on all seven, byte-identical before and after**
(`diff` reports no difference).

### 3. The enumeration — by command, counted, not sampled

```bash
grep -rn --include=*.py -E "[\"']origin[\"']" scripts/
```
**COUNT: 2 — and both are WRITES:**
- `scripts/spine_lifecycle.py:323` — `compiled["origin"] = origin`
- `scripts/init_work_area.py:188` — `spine.setdefault("origin", {...})`

**Remaining reads of `origin.worktree` on any decision path, production-wide: 0.**
The per-read justification the handoff asks for is therefore vacuous — there is
no read to justify. Three complementary passes, all in
`g2-implement/m4-enumeration.txt`:

- (a) AST scan of every `origin` key access repo-wide: **12**, of which **1 in
  production** and that one a write.
- (b) AST scan of `worktree` accesses on an origin-shaped container: **5**, **0
  in production**, all five tests asserting the stamp itself.
- (c) the textual grep above, which exists because (a) would miss `setdefault` —
  and it did catch `init_work_area:188` that (a) missed.
- (d) non-Python readers (`*.sh`, `*.json`, `*.jq`, `*.js`): **0**.
  `scripts/validate_spine.py` does not mention `origin` at all.

### 4. The provenance pin fails if either half breaks

```
MUTANT 1 -- stop writing the stamp (delete the init_work_area worktree line)
  -> FAILED test_provenance_the_stamp_is_written_by_both_producers  (1 failed, 3 passed)
MUTANT 2 -- read the stamp for a decision (re-add a cwd comparison in main())
  -> FAILED both differential tests                                  (8 failed, 2 passed)
RESTORED                                                             (4 passed)
```

### 5. The adversarial search — negative result, measured

**I did not find a case where the removed comparison was the only thing
preventing harm.** Stated as a negative result, as instructed.

`probe_adversarial.py`, the harm case (a second controlling agent arriving from a
foreign tree), run on both sides:

| | before | after |
|---|---|---|
| agent-one claims from the spine's worktree | exit 0 | exit 0 |
| agent-two claims from a foreign tree | **exit 1** (worktree comparison) | **exit 1** (lease) |
| agent-two mutates from a foreign tree | **exit 1** (worktree comparison) | **exit 1** (lease) |
| lease still held by | agent-one | agent-one |
| gate status | pending | pending |

Same outcome, different refusing mechanism. The comparison was refusing first and
masking a lease that was already there. The single delta is the unclaimed-spine
case in **Behavior changed** above.

### 6. Confirmatory — full suite, cache cleared, clean env

```bash
find . -name __pycache__ -type d -prune -exec rm -rf {} + ; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
```
**Base `9ff86f2d`, re-measured by me rather than trusted: 3159 passed, 6 skipped,
0 failed.** (Matches the handoff's stated number exactly.)
**Final, on the frozen tree: 3135 passed, 5 skipped, 0 failed.**

Failure distribution, derived mechanically and empty:
```bash
grep '^FAILED' m5-full-suite.txt | sed 's/::.*//' | sort | uniq -c
# (no output — zero failures)
```

**The −24 reconciles exactly**, so no test disappeared unaccounted for: 32 test
methods removed from `tests/test_spine_origin_isolation.py`, 7 added, −25
collected. Exactly one of the 32 was the Windows-only skip
(`test_case_and_separator_folding_on_windows`), which is the 6 → 5 skip delta.
−31 passing + 7 = **−24**. All 32 removed tests are tests of the comparison.

### 7. The tripwire

`tests/test_worktree_precondition_wiring.py` — green, run on its own and in the
full suite. Nothing in this gate touches it.

### 8. Windows separators and case folding

The fold existed only to reconcile the two producers' differing normalizations
(`spine_lifecycle` stores `str(Path(worktree))`, `init_work_area` stores
`as_posix()`) for the comparison. With no comparison, that disagreement is
harmless by construction.

Rather than inherit a folding claim from a host where `normcase` is the identity
function, I **constructed the expectation explicitly**: the differential table
carries a backslashed, drive-lettered `"C:\W\REPO"` row and an upper-cased
copy of the real worktree path. Both must be exactly as inert as every other row,
on every platform — which is a real assertion on Linux, unlike the
`skipUnless(os.name == "nt")` test it replaces, which never ran here.

### 9. The wiring grep

```bash
grep -rn "origin_worktree_refusal\|worktree_from_spine_path" --include=*.py scripts/ tests/
```
**COUNT: 35 → 21.** **Call sites removed: 1** — the single production call in
`main()`, which matches the map's own count of 1 production reference, this
module only. **Call sites added: 0.** All 21 remaining are prose mentions, plus
the definition of `worktree_from_spine_path` and its one test consumer.

### 10. The gate's targeted check — red to green

Red at base on **both** halves (the grep matched; `-k provenance` collected zero
and pytest exited 5). Green now: `4 passed, 9 deselected, 14 subtests passed`.

## TDD evidence

- **Failing test observed** (`g2-implement/m1-provenance-RED.txt`, against the
  unmodified tree): `8 failed, 2 passed, 8 subtests passed`. The rows "an empty
  string", "a number" and "worktree key absent" behaved differently from "the
  spine's own worktree" — the fallback shapes accepted while the real stamp was
  refused, which is precisely "something reads `origin.worktree` for a decision".
- **Passing test observed:** `13 passed, 18 subtests passed` for the file;
  `4 passed` for the `provenance` selector.
- **Refactor while green:** yes — the Windows rows were added after the pin was
  green, and re-run green.

## Docs/contracts touched

- `docs/CHECKLIST_SCHEMA.md` — four paragraphs describing the retired mechanism
  replaced by five that describe what is true now, including the plain statement
  that **nothing checks at engine level that an agent is standing in the spine's
  worktree**, and why that is deliberate. **I cited no line numbers in the new
  prose.** The old citation was stale twice over — it said `:3411-3444`, the
  handoff said `:3573-3578`, the truth was `:3638-3643` — so a fourth number
  would just be the next thing to go stale. It names the pinning test instead.
- `scripts/spine_lifecycle.py` — **negative result first:** I searched it for
  prose this change makes false (grep for enforc/engine/cwd/drivable/isolation,
  plus a full read of the module docstring and `build_origin`) and **found
  none**. Its `origin` prose is only about *writing* the block, which is
  unchanged, and its "self-verifies isolation" is `verify_worktree_isolation` at
  open time, untouched. Rather than invent a repair I added one positive note to
  `build_origin` saying the block is provenance and why to keep writing it
  accurately.

## Assumptions

- I read "its guarded/exempt verb sets keep their current meaning" as a
  prohibition on widening them, not a requirement to preserve them unread. See
  **Completed slice** for the reversal path if that is wrong.
- I treated the four collateral test files as editable "only as this change
  breaks them", and prose staleness as not breakage — so I reported it rather
  than fixing it. If the Commander prefers, those two edits are small.

## Stop conditions hit

None. Allowed scope was not exceeded, no excluded file was touched, all required
evidence was produced, the tripwire stayed green, and the adversarial search
returned a negative result rather than a blocker.

## Out-of-scope observations

**A finding, not just stale prose — for lane A (#603).** The MCP door's
`_standing_in_the_bound_spines_worktree` exists *solely* to satisfy the guard
this gate deleted. Its own docstring says so: "the engine's worktree guard …
compares a spine's stamped `origin.worktree` against the engine's AMBIENT cwd,
and this door calls the engine IN PROCESS — so for the duration of that one call,
`run_engine` stands in the bound spine's own worktree". **That justification is
now void.** The chdir may still be wanted — g5 would want the engine standing in
the right tree for command-kind checks — but it currently has no stated reason to
exist, and its tests pass either way. Worth a deliberate decision by the owning
lane rather than silent inheritance.

**Stale prose in files I may not edit** (present tense, now false):
- `scripts/mcp_spine_server.py:18`, `:371`, `:384` — fenced, lane A.
- `scripts/run_crew.py:860` — fenced, lane E.
- `tests/test_worktree_derivation.py:258` — "a `realpath` here would also make
  `origin_worktree_refusal` impure while its purity test…"; not in allowed scope.

**Stale prose in files in allowed scope, left alone under the narrow licence:**
- `tests/test_worktree_precondition_wiring.py:15-17` — "Enforcement is now
  engine-native — `origin_worktree_refusal` compares…". The tripwire; I did not
  want to touch it at all.
- `tests/test_mcp_door_engine_cwd.py:5` — same present-tense claim.

**Accurate history, no action needed, listed so nobody re-reports it:**
`tests/test_shipped_check_commands_resolve.py:93-95` and
`tests/test_spine_lifecycle.py:182` are both past-tense and still true.
`skills/admiral/templates/LAUNCH_ORDER.template.md:45` describes
`verify_worktree_isolation.py --here`, which still behaves that way.

**Triage candidate.** The per-template `verify_worktree_isolation.py --here`
check on the Commander spine's `init` `c0` was deleted in #315/#568 in favour of
the engine-native comparison, and that comparison is now gone too. Nothing
asserts location anywhere by default. That is the intended end state, but it is a
net subtraction across two issues that no single issue records, so I wrote it
into `docs/CHECKLIST_SCHEMA.md` explicitly and flag it here.

## Workflow Feedback

- **Handoff gaps:** the **Structural** anchor's citation of the impure call site
  as `scripts/checklist_engine.py:3573-3578` was **wrong** — that range is
  `append_journal_entry`; the call site was at `:3638-3643`. The handoff's own
  "Map confidence flag" told me to re-read every cited line, which is the only
  reason this cost me nothing, so the mechanism worked. But this is now the third
  stale citation on this run (`_foreign_worktree` `:639`→`:693`,
  `CHECKLIST_SCHEMA.md:124`'s `:3411-3444`, and this one). **Line-number anchors
  in this repo are not carrying their weight.** Symbol names would have been
  correct in all three cases.
- **Context rediscovered:** that the MCP door `chdir`s into the spine's worktree
  before every engine call. This is the single most important fact for judging
  whether the comparison guarded anything — it means the guard was already
  self-satisfying for production's actual caller — and I found it only by reading
  a fenced file on my own initiative while doing the adversarial search. It
  belongs in the handoff's Protected Intent as supporting measurement.
- **Instructions improvised around:** the crew skill opens with "a spine is bound
  for you; `spine_status` is your first call", but this crew's `crew-runs.json`
  entry has `spine: null` while `SPINE_FILE`/`SPINE_SESSION` point at the
  **Commander's** spine, under the Commander's active lease. Obeying that
  literally means advancing my parent's `execute` gate. I authored and drove my
  own plan instead and wrote nothing to the parent spine. The durable fix is a
  lease-ownership check, not more prose — this is at least the fourth crew on
  this issue to hit it.
- **What would have made this easier:** the handoff asks for "every remaining
  read of `origin.worktree` … enumerated by command with the count stated". A
  plain grep for `worktree` returns 91 accesses, almost none of them `origin`'s;
  the enumeration only became honest once I wrote an AST pass that names the
  *container*. Suggest the handoff ask for the enumeration keyed on the `origin`
  key rather than the `worktree` key — nothing can read `origin.worktree` without
  reading `origin` first, which makes the gate two lines instead of a script.

## Stop-hook refusal, recorded

At the end of this run the Stop hook fired `SPINE MID-FLIGHT: gate execute is
still open`, instructing me to reload the constellation-commander skill, rewrite
`STATE_NOTE.md`, and drive `execute.json` gate by gate. **I refused, and did
nothing to the parent spine.** Verified state at the moment of refusal:

- My own plan (`crew-handoffs/g2-implement/IMPLEMENTER_PLAN.json`): `DONE: no
  open items`, lease **released**. Nothing of mine is abandoned.
- My `crew-runs.json` entry: `spine: null` — **no spine is bound to this crew.**
- The spine the hook points at — `SPINE_FILE`, i.e.
  `.agent-work/cleanup-f-derive-worktree/spine.json` — carries
  `engine_session.session_id = commander-cleanup-f-derive-worktree`, status
  **active**. That is my parent's `execute` gate under my parent's live lease.

Obeying would mean advancing my parent's gate or force-taking a live lease.
**The hook's own escape hatches do not fit:** it offers `block` or `waive`, but
both WRITE to the parent's spine, so the sanctioned "honest stop" is itself the
destructive act. The only non-destructive exit is to refuse and record it here.

This is a recurring workflow defect, not a one-off — it is at least the fourth
crew on this issue to hit it. The durable fix is a lease-ownership check in the
hook (compare `engine_session.session_id` against the running crew's session id,
and stay silent when they differ), not more prose telling crews what to do about
a spine that was never theirs. See Workflow Feedback above.

Return status: complete

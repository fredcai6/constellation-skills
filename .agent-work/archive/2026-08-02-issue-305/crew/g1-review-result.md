# Review Result

## Assigned Gate
`g1-review` — issue #305, epic #298: the context-manifest assembly seam.

Survey driven at `.agent-work/issue-305/g1-review/review.json` (8 items, all visited, consolidated).
Fowler record at `.agent-work/issue-305/g1-review/fowler-pass.json` (`verify_fowler_pass.py` exits 0).
All engine drive on the **worktree's** `scripts/checklist_engine.py`, session `g1-review-opus`.

## Result
`BLOCK`

The seam itself is well built. In the source repo it does exactly what the task statement
asks, and three of the four close criteria hold up under adversarial attack. **It fails
close criterion 1**, and it fails it on the default production path rather than an exotic
one. The remedy is small — this is not a rebuild.

---

## Per-criterion disposition

### Criterion 1 — "Can an agent still reach `advance` on a gate without ever triggering the emit?" — **FAIL**

I constructed three sequences. The first is the one that matters.

**1a. The installed skill's bundled engine — the production path. (BLOCKER)**

`install_constellation.SKILL_SCRIPT_BUNDLES` ships `checklist_engine.py` to nine skills.
It ships **`episode_capture.py` to none of them. Nor `context_manifest.py`. Nor
`agent_work_root.py`** (which `episode_capture` imports at module scope). Confirmed on
disk, not inferred:

```
C:/Users/fredc/.claude/skills/constellation-reviewer/scripts/
  checklist_engine.py  gauge_reader.py  verify_fowler_pass.py
C:/Users/fredc/.claude/skills/constellation-implementer/scripts/
  checklist_engine.py  gauge_reader.py
```

So the engine's guarded import takes its `except ImportError` branch and installs a no-op.
Driven against the **real installed reviewer-skill engine**, on a checklist declaring
`context_refs`:

```
installed engine has episode_capture.py? False
installed engine has context_manifest.py? False
['start', 'g1']               -> (0, ['g1 -> in-progress'])
['advance', 'g1', ...]        -> (0, ['g1 -> complete'])
STATUS: complete
MANIFESTS EMITTED: []          <-- and nothing on stderr
```

Control, identical checklist, worktree engine: `MANIFESTS EMITTED: ['g1.json']`.

`global-everyone.md` §Universal posture is explicit that agents run the installed copy —
*"Reference bundled scripts and references by their absolute installed path; don't resolve
`scripts/` from the target repo unless it vendors them."* This worktree is the one place the
seam works, and it works here only because the repo vendors its own `scripts/`. The issue's
acceptance criterion — *a manifest is produced on every deterministic assembly* — was
vacuous before this gate over zero assemblies. After this gate it is vacuous over every
**installed** assembly.

Two things make this blocker-class rather than a note:

- It is the **exact shape ruling D8 forbids**. D8 says a failed reading must be visibly
  distinct from an uncollected one. The `except ImportError: return None` fallback produces
  no file, no stderr, and no exit-code change — a non-reading indistinguishable from a step
  nobody started. D8 was honored scrupulously at the runtime layer (the failure stub is
  genuinely good work) and then reinstated one layer up.
- It also violates inherited `global-everyone.md` §Universal posture: *"Fail visibly rather
  than emit plausible wrong output; no hidden fallback."*

The implementer found this and logged it honestly as out-of-scope observation 1 — I want that
on the record, because it was found by the person with the most incentive not to. I disagree
only about the disposition: a gate whose single close criterion is "the emit is unskippable"
cannot ship with the emit skipped everywhere it ships. **Remedy:** add
`episode_capture.py`, `context_manifest.py`, `agent_work_root.py` to every engine-carrying
bundle, plus a test asserting it. If the epic sequences packaging elsewhere, then at minimum
the `except ImportError` branch must stop being silent — that part is not deferrable, because
it is the mechanism that hides the gap.

**1b. Survey checklists never emit at all. (BLOCKER, narrower)**

`record()` (`checklist_engine.py:1715`) has **no status guard** — it sets `complete` from
`pending` directly. A survey therefore never needs `start`:

```
record      -> (0, ['r1 recorded pass: ok'])
consolidate -> (0, ['consolidated: verdict=APPROVE findings=0'])
STATUS: complete | CONSOLIDATION: {'verdict': 'APPROVE', ...}
MANIFESTS EMITTED: []
```

D1's reachability argument is explicitly scoped to *"a gated spine"* and is correct there.
But `episode_capture.py`'s own module docstring states the claim without that scope
(*"`advance()` refuses a task that is not `in-progress`, so … every gate that ever advances
has been through `start` or `reopen`"*), and Reviewer, Cartographer, Scout and Curator all
run surveys. Either wire it or state the limit where the claim is made.

**1c. A checklist whose gate is already `in-progress`. (observation)**

The engine never validates initial statuses on load, so an authored or instantiated checklist
carrying `"status": "in-progress"` advances with no emit (`advance -> (0, ['g1 -> complete'])`,
`MANIFESTS EMITTED: []`). Low severity — no shipped template does this — but it is the third
route past a claim stated as absolute.

**What I could NOT break.** `resume()` — the one the handoff pointed me at — is *not* a
bypass. It refuses anything not `blocked`, and restores only a `pending`/`in-progress`
prior; a gate that was `in-progress` before blocking had necessarily been `start`ed. `amend`
builds every task `pending` (`_build_amend_task`), `skip`/`block` are terminal or
non-`in-progress`, and `reopen` at the rework cap blocks instead of reopening. **Within the
engine's own source, D1's two-site claim is correct** — the failures are all at its
boundaries: packaging, checklist type, and untrusted initial state.

### Criterion 2 — "Does the emit ever change a verb's exit code?" — **PASS, reproduced and extended**

I did not trust the claim. I extracted the pre-seam engine myself
(`git show 967493c:scripts/checklist_engine.py`, verified it contains no `emit_step_manifest`)
and ran both binaries side by side over **17 case/verb pairs — the implementer's 10 plus 7 it
never ran**. I compared **stdout and stderr as well as exit code**, which the original
comparison did not.

```
1 fully-terminal checklist    current / start / advance          0/0  1/1  1/1   SAME
2 unmapped root token         current / start                    0/0  0/0        SAME
3 not a git repository        current / start                    0/0  0/0        SAME
4 malformed declaration       current / start                    0/0  0/0        SAME
5 reopen a complete gate      reopen --reason                    0/0             SAME
6 declaration path escapes its root      start                   0/0             SAME
7 declaration is a glob                  start                   0/0             SAME
8 context_refs is not a list             start                   0/0             SAME
9 context_refs entry is a bare string    start                   0/0             SAME
10 work_id is None                       start                   0/0             SAME
11 survey: record with no start           record                 0/0             SAME
12 declared path is a DIRECTORY (read raises, not FileNotFound)  0/0             SAME
ALL EXIT CODES *AND* STDOUT/STDERR IDENTICAL: True
```

Case 12 is the one I most expected to break it — `read_bytes` only catches `FileNotFoundError`,
so a directory raises `IsADirectoryError`/`PermissionError` straight past it. The broad
`except` in `emit_step_manifest` catches it and writes a stub. Fail-soft holds.

### Criterion 3 — "Is `durable` the checkout root, resolving `.agent-work/LESSONS.md` without double-nesting?" — **PASS, checked at the resolved absolute path, both sides of the boundary**

`durable_root` has a real branch (linked worktree without an Admiral lease → main checkout;
everything else → `start` unchanged), so one probe is not a proof. I built a real
main-checkout + linked-worktree pair and probed **all three** branches:

```
[linked worktree, NO admiral lease -> redirects to MAIN]
  durable = .../c305-.../main
  .agent-work/LESSONS.md -> .../main/.agent-work/LESSONS.md   exists: True  double-nested: False
[linked worktree, ACTIVE admiral lease -> stays in the WORKTREE]
  durable = .../c305-.../linked
  .agent-work/LESSONS.md -> .../linked/.agent-work/LESSONS.md exists: True  double-nested: False
[plain checkout]
  durable = .../main
  .agent-work/LESSONS.md -> .../main/.agent-work/LESSONS.md   exists: True  double-nested: False
```

And in this worktree, `durable/.agent-work/LESSONS.md` resolves to a file whose real
`git hash-object` is `03aff777…` — a non-null rev from the world, not from the report. D4 is
satisfied.

### Criterion 4 — "Does a manifest with every row `rev: null` pass as success?" — **PASS as adjudicated (D7); note the literal reading**

D7's accepted resolution is a *test-level* control — *"the control asserts `content()` against a
hand-computed expectation for the step's declared refs, not merely that a file exists."* That is
what shipped, and it is done properly:
`test_emit_writes_a_manifest_carrying_a_non_null_rev` builds a **two-element** declaration
(one present file, one absent), asserts `files[0]["rev"] == cm.rev(payload)` against a
hand-computed blob OID and `files[1]["rev"] is None`. Both sides of the boundary, multi-element
collection. My mutants MUT-A/MUT-B (below) confirm it is not decorative.

The literal wording of the criterion is nonetheless still true of the runtime: a manifest
whose every row is `rev: null` **is** structurally valid and nothing reads it as unhealthy —
`required: true` is deliberately not enforced by the producer. That is #300's frozen
behavior and D7's ruling, not a regression this gate introduced, so it is not a blocker
here. It does have a live consequence worth carrying to g2: in a skill-source repo
`SKILL_ROOT` is the repo root, so `COMMANDER_SPINE`'s two `required: true` skill-rooted rows
(`references/global-orchestrator.md`, `references/global-everyone.md`) resolve to
`rev: null` — and combined with 1a, **there is today no environment in which a skill-rooted
row is ever non-null.**

---

## My independent mutation — mandatory, and what it found

Six mutants, **five outside the implementer's set** (its two were: stub writes `files: []`;
failed emit returns `None`). Run against `test_episode_capture.py` + `test_context_manifest.py`
+ `test_checklist_engine.py` (baseline: 424 passed). Working tree restored and verified clean
after each.

| mutant | what it changes | why I chose it | outcome |
|---|---|---|---|
| **MUT-A** | `durable_root(repo)` → `durable_agent_work(repo)` | the exact double-nesting trap criterion 3 names | **KILLED** — 4 tests |
| **MUT-B** | `durable_root(repo)` → `durable_root(base_dir)` | the spelling `resolve_roots`' own docstring warns against; a plausible "simplification" | **KILLED** — 3 tests |
| **MUT-K** | `reopen`: emit moved **before** the status mutation | probes whether the load-bearing "AFTER the mutation" comment is actually guarded or just asserted | **KILLED** — `Seam::test_seam_reopen_emits_the_manifest_too` |
| **MUT-C** | `manifest_root` drops `.parent` | manifest lands one level off contract | **KILLED** — 5 tests |
| **MUT-D** | write-if-absent guard removed (always overwrite) | turns the snapshot into a live index — the failure D2 exists to prevent, and *not* in the implementer's mutant set | **KILLED** — `Emit::test_emit_never_overwrites_an_already_present_manifest` |
| **MUT-E** | emit removed from `start()` | control | **KILLED** — 3 tests |

**I could not find a surviving mutant inside the diff.** The shipped tests have real
falsifiability on every code path this gate added, and MUT-K in particular shows the ordering
comment is genuinely enforced rather than merely claimed. That is a strong result and I want
it stated as plainly as the block.

**The mutation that the suite cannot see is the one that matters.** There is no test asserting
`episode_capture.py` ships with an engine-carrying skill — so "delete it from the bundle" is a
mutation with no killer, and it is precisely the state the repo is in today.

---

## Handoff compliance

The task statement is satisfied **in the source repo**: emission from `start()` and `reopen()`,
write-if-absent, all logic in `scripts/episode_capture.py`, fail-soft but not fail-silent,
roots resolved mechanically with `durable` from `agent_work_root.durable_root()` on the
checkout root. Stop conditions: none fired, correctly. Test mode (TDD) is satisfied — the
red observed on resume, and the honest correction of
`test_failsoft_swallows_an_arbitrary_producer_crash` (which encoded the *superseded* fail-silent
contract), is the right call and well argued.

It fails the handoff on close criterion 1 as detailed above.

## Scope drift

None. `git diff 967493c..HEAD` touches exactly `scripts/checklist_engine.py`,
`scripts/episode_capture.py`, `tests/test_episode_capture.py`. `dispatch()`, `main()`,
`context_manifest.py`, `apply_episode_delta.py`, `query_episodes.py`, `run.dirty` and the
refusals counter are all untouched; no roots CLI flag was added. `git status --porcelain`
shows nothing stranded beyond this review's own artifacts.

**On the Commander's flag B (the two `reopen` plumbing lines): I accept them — but the stated
justification is wrong, and the Commander should have the real one.**

`reopen()` refuses any gate that is not `complete`. A complete gate has necessarily passed
`advance`, which requires `in-progress`, which requires `start` — so its manifest already
exists, and write-if-absent returns early. Reproduced with the declaration genuinely swapped
underneath it:

```
BEFORE sha256: 389edf71…  mtime_ns: 1785638614077296200  files: [('A.md', '72943a16…')]
advance -> g1 -> complete;  reopen -> g1 reopened (rework 1/3)
AFTER  sha256: 389edf71…  mtime_ns: 1785638614077296200  files: [('A.md', '72943a16…')]
HASH IDENTICAL: True | MTIME IDENTICAL: True
declaration on disk really did change: True
manifest still records the ORIGINAL declaration: True
```

So **`reopen`'s emit is a no-op on every reachable production path.** "Without `base_dir`,
`reopen` could not emit" is true and irrelevant — `reopen` cannot emit anyway. Keep the lines:
they cost nothing, they mirror `start()` exactly, and they *do* fire for a pre-#305 spine or a
manifest that was deleted. But record the real reason, or the next reader will re-derive a
justification that does not hold.

## Evidence verdict

Every claim reproduced at its source; none accepted on assertion.

- **Full suite** — I ran it: `1435 passed, 2 skipped, 409 subtests in 80.10s`. Matches.
- **Exit-code parity** — reproduced independently and extended to 17 pairs including stdout/stderr.
- **Non-null durable rev** — verified at the resolved absolute path on all three branches.
- **Write-if-absent** — sha256 **and** `mtime_ns` identical, declaration provably changed underneath.
- **`files: null` vs `files: []`** — both produced by real emits and **both read**, so this is not
  an empty-vs-empty coincidence:

```
real['files'] = []   | type: list       stub['files'] = None | type: NoneType
BOTH FALSY (the trap): True True
distinguishable by identity  : True
distinguishable by emit_error: True
stub emit_error: {'error': 'DeclarationError', 'message': "unknown root token 'vendor'; …"}
stub is NOT a valid manifest (no contract/repo_rev key): True True
```

The stub also lacks `contract` and `repo_rev` entirely, so it cannot be mistaken for a manifest
by a schema check either — a stronger discriminator than the implementer claimed for itself.

## Code/doc quality

Fowler pass: 12/12 smells visited, rail exits 0. Flagged 2, overridden 5 (each with a logged
repo standard), absent 5.

- **duplicated-code (flagged, observation).** `emit_step_manifest` and `_write_failure_stub`
  carry the same four-step place-and-write-if-absent sequence, and the two copies **already
  disagree** on which id names the file — success path uses `manifest["step"]` (`active_id`),
  stub path uses `iid`. Where those differ (the implementer's own observation 2: an earlier
  blocked gate), the manifest and its stub target different files and neither guard sees the
  other's. Extracting `_place(checklist, base_dir, step)` makes the divergence one deliberate
  argument instead of latent drift.
- **shotgun-surgery (flagged).** The change's true blast radius is four sites; three landed.
  This is blocker 1a in smell form — the packaging table has no mechanical link to the engine's
  imports, so nothing made the omission visible.
- **comments-as-deodorant — overridden, and I want to be explicit that this was a real
  decision.** `episode_capture.py` is roughly half prose. Under the repo's documented
  convention (`global-crew.md`: match surrounding in-file documentation conventions; every
  neighbouring module is equally rationale-dense) this is house style carrying decisions the
  code cannot express. The decisive instance is lines 54-57 — the comment naming
  `durable_agent_work()` as the *wrong* neighbouring helper. That comment is the only record of
  the trap criterion 3 exists to catch, and deleting it would simplify zero lines of logic.

**Engine diff, independent verdict (Commander's flag A — the `git diff --stat` check that could
not fail).** I read it line by line rather than counting it. Six things landed: the `sys.path`
insert, the guarded import, one call line in `start()`, one in `reopen()`, `base_dir` on
`reopen()`'s signature, and `_run_verb` passing it. Items 3-6 carry no branch, no state, no
decision — confirmed by mutating the engine (MUT-E, MUT-K) and watching the failures land in
*seam* tests, not engine-behavior tests. **It is genuinely logic-free, with one exception:**
`sys.path.insert(0, <scripts dir>)` at module scope is a process-global side effect now paid by
every importer of `checklist_engine`, not just the CLI. There is precedent
(`context_manifest.py:79`) and nothing in `scripts/` shadows a stdlib name today, so I do not
block on it — but it is the one non-inert line in the diff, and it is the mechanism by which the
`ImportError` fallback silently swallows a partial install.

## Map impact verdict

- **Evidence supports claimed change:** Partly. "Context manifest emitted as a byproduct of step
  activation" is proven for a gated spine on a vendored `scripts/`. It is **disproven** for every
  installed skill and for every survey. The capability claim needs that scope or the packaging fix.
- **Constraints not violated:** Fail-soft honored and measured against the pre-seam binary
  (I re-measured, wider). Write-if-absent honored (hash + mtime). Emission-after-mutation honored
  and guarded (MUT-K). The `no hidden fallback` posture rule **is** violated, at the import shim.
- **Notes match the diff:** Yes, and unusually well — the implementer volunteered the two
  criterion-exceeding lines and the packaging hole rather than letting a reviewer find them. The
  one note that is materially wrong is the *rationale* for the `reopen` plumbing, corrected above.
- **Decision candidates surfaced:** Yes — the plumbing-vs-criterion call was correctly floated
  rather than absorbed.
- **Durable context routed:** Mostly. The import cycle
  `context_manifest → checklist_engine → episode_capture`, broken only by a function-local
  import, is correctly named as a trust limitation and belongs in the map. Five further
  candidates flagged below.

## Reconciliation check

**`manifest_root()`'s documented placement claim is false for this repo's actual layout.** The
docstring says the manifest *"lands beside the spine it describes, inside the same work area."*
It composes parent-of-checklist-dir + `work_id`, which coincides with the work area only when
`dirname(checklist) == work_id`. Crew checklists live at
`.agent-work/<issue>/crew/<gate>-plan.json`, so:

```
.agent-work/issue-305/issue-305-g1-implement/   <- contains ONLY context/, created by the emit
.agent-work/issue-305/issue-305-g1-review/      <- same, created by MY survey
```

Both are phantom sibling directories, not work areas — untracked orphan scratch that the
Reviewer skill explicitly says closeout must find none of. The test fixture's own docstring
concedes the limit: *"only this shape puts the manifest beside the spine."*

## Blockers

1. **The seam is inert in every installed skill, silently.** No bundle ships
   `episode_capture.py` / `context_manifest.py` / `agent_work_root.py`; the engine's
   `except ImportError` degrades to a no-op with no file, no stderr, no exit-code change.
   Reproduced on the real installed engine. This is close criterion 1, failed on the default
   production path, in the shape D8 forbids. *Fix: bundle the three scripts for every
   engine-carrying skill + a test asserting it. If packaging is deferred, the silent fallback
   must still be made loud — that half is not deferrable.*
2. **Survey checklists never emit.** `record()` has no `in-progress` guard; a survey completes
   and consolidates from `pending` with zero manifests. Reproduced. *Fix: wire the seam for
   surveys, or state the gated-only scope limit in `episode_capture.py`'s docstring where the
   unskippability claim is made.*

## Out-of-scope observations

- `reopen`'s emit is a production no-op (see Scope drift). Not a defect — a mis-stated rationale.
- An authored checklist whose gate already reads `in-progress` advances with no emit; the engine
  never validates initial statuses on load.
- `work_id` is composed into the manifest path unguarded: `work_id: "../../ESCAPED"` writes the
  manifest **outside** the work area (reproduced). Trusted input, low severity;
  `context_manifest.manifest_path` is #300's frozen surface, so the guard belongs in
  `episode_capture.manifest_root`.
- In a skill-source repo `SKILL_ROOT` is the repo root, so `COMMANDER_SPINE`'s two
  `required: true` skill-rooted rows resolve to `rev: null`.
- `sys.path.insert(0, …)` at engine import is now process-global for every importer.
- g2/g4 exclusions respected: I found nothing to say about `run.dirty`, the `refusals` counter,
  or the field-group composer.

Five triage candidates are flagged on the survey (`tc1`–`tc5`).

## Workflow Feedback

- **Handoff gaps.** The handoff was the best-instrumented one I have been given — naming flag A
  (a postcondition that could not fail) and flag B (a self-reported criterion overrun) is exactly
  the right move and it is what pointed me at the two places worth the most attack. Two real gaps.
  **(a)** The **"Survey State Location"** field says `.agent-work/issue-305/g1-review/review.json`,
  and the Reviewer skill says the same shape — but `episode_capture.manifest_root()` assumes the
  checklist sits at `<agent-work>/<work-id>/`. Following the handoff literally is what made my own
  review emit its manifest into a phantom directory. Two shipped instructions disagree about
  checklist layout, and the change under review depends on which one is right. **(b)** Close
  criterion 1 says *"try to construct the sequence"* and then names `resume()` as the suspect.
  `resume()` is clean. Naming one suspect anchored me on the engine's internals for longer than it
  deserved; the three real bypasses are all at the engine's *boundaries* — packaging, checklist
  type, untrusted initial state. A criterion that says "attack the claim's **scope**, not just its
  internals" would have got me there faster.
- **Context rediscovered.** That `SKILL_SCRIPT_BUNDLES` does not ship the sidecar was in the
  implementer's result as out-of-scope observation 1 — but the handoff's "Specific Exclusions"
  did not say whether packaging was in or out of scope for this gate, so I had to decide the
  disposition of the run's most consequential finding myself. Name packaging explicitly, either way.
- **Instructions improvised around.** The Reviewer skill says to `claim` the lease as the first
  command and then drive `current`; it does not say the engine requires `--session-id` on every
  subsequent verb, and `consolidate` **rejects** `--session-id` as an unrecognized argument while
  `record`/`start` require it. I lost a cycle to each. Also: the skill directs the Fowler record
  to `templates/FOWLER_PASS.template.json` — i.e. the template path itself. I wrote it to
  `.agent-work/issue-305/g1-review/fowler-pass.json` instead, since writing a record over a shared
  installed template would corrupt it for every future reviewer. That instruction should say
  "instantiate from `templates/FOWLER_PASS.template.json` into your review directory."
- **What would have made this easier.** One line in the handoff: *"packaging/distribution of the
  new module is IN scope / OUT of scope for this gate."* Everything else I needed, I had.

## Return status
`complete`

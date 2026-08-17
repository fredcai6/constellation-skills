# REVIEW_RESULT

Re-review of gate `g1` after rework — reviewer **attempt 2**. This supersedes the
attempt-1 `BLOCK`, which is preserved verbatim in the run's history and quoted
where I disagree with it.

## Assigned Gate

`g1` — lane F, issue #609. Worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`, base `e36e630b`.

Survey driven through the engine at
`.agent-work/cleanup-f-derive-worktree/g1-review/review-attempt-2.json`
(7 items, all visited, all `pass`, consolidated). Fowler-pass record at
`.agent-work/cleanup-f-derive-worktree/FOWLER_PASS.json`; the predecessor's is
preserved at `FOWLER_PASS-reviewer-attempt-1.json`.

I re-reviewed the **whole gate**, not only the delta, as the addendum required.

## Result

Verdict: APPROVE

**B1 is closed.** No blocker survives. Three out-of-scope observations, none
blocking; two of them correct the predecessor's own notes.

---

## 1. Is B1 actually closed?

Yes, and I measured it rather than accepting it.

The fix is a helper in `tests/test_spine_rail.py:876`:

```python
def _derived_form(path):
    return os.path.normcase(os.path.normpath(str(path)))
```

used in all six assertions of
`test_worktree_from_spine_walks_to_the_nearest_agent_work_ancestor`.

I re-ran the predecessor's simulation from scratch: AST-extracted the *live*
source of `spine_rail._worktree_from_spine`,
`checklist_engine.worktree_from_spine_path`, `test_spine_rail._derived_form` and
`test_worktree_derivation._expected`, exec'd them in a namespace whose `os.path`
is `ntpath`, and drove a realistic Windows `tmp_path`
(`C:\Users\Tommy\AppData\Local\Temp\pytest-of-Tommy\pytest-3\test_Worktree0`).

```
WINDOWS (ntpath simulation)      normcase folds case here: True
  one-level        fixed-assert=PASS   pre-fix-assert=FAIL
  deep crew plan   fixed-assert=PASS   pre-fix-assert=FAIL
  archived deep    fixed-assert=PASS   pre-fix-assert=FAIL
  depth zero       fixed-assert=PASS   pre-fix-assert=FAIL
  not .json leaf   fixed-assert=PASS   pre-fix-assert=FAIL
  nested sandbox   fixed-assert=PASS   pre-fix-assert=FAIL
  --> ALL 6 with the FIX:      PASS
  --> ALL 6 as B1 found them:  FAIL (this is B1)

POSIX (this host)                normcase folds case here: False
  --> ALL 6 with the FIX:      PASS      (and the pre-fix form also passes here,
                                          which is exactly why B1 was invisible)
```

So B1 reproduces on the pre-fix text and does not reproduce on the shipped text.

## 2. Is the fix constructed, not inherited?

Yes.

- `_derived_form` is `normcase(normpath(...))` — **the same predicate the
  implementation applies**, not a value copied from a green Linux run.
- No `sys.platform` branch anywhere near it. The two `sys.platform` markers in
  `tests/test_spine_rail.py` are at `:834`/`:843`, on the pre-existing
  `_same_path` normcase tests, and are untouched by this diff.
- It is byte-equivalent in construction to `test_worktree_derivation._expected`
  (`:103`). I asserted that directly: `_derived_form(wt) == _expected`-style
  construction returns `True` under both `posixpath` and `ntpath`. The two files
  now express one rule, which is what makes them mutually pinning rather than
  independently guessing.

## 3. Did the fix weaken the test?

No. This was the addendum's sharpest question and it deserves the sharpest
answer.

The assertion normalizes **only the expected side** —
`sr._worktree_from_spine(str(spine)) == _derived_form(worktree)`. The
derivation's return is compared raw. So there is no "normalize both sides into
agreement about nothing".

Proven by mutation, not by reading. I replaced the hook body with one that
returns **one level too high** (`os.path.dirname(head)` — a wrong but entirely
plausible worktree), asserting the mutation applied:

```
baseline, that test alone                      1 passed
hook returns one level too high                1 failed      <-- caught
   (shared table at the same time)            19 failed, 34 passed
restored                                       byte-identical, 1 passed
```

I also swept the discriminating power symbolically across both platforms: the
assertion catches a returned `tmp_path`, the `.agent-work` dir itself, `''`,
`None`, an outermost-instead-of-nearest answer, and (on Windows) an
unnormalized-but-otherwise-correct path. Nothing plausible slips through.

## 4. Everything the predecessor verified still holds

Re-verified in my own hands, not carried forward.

### Deletion test on the shared table — six mutations

Every mutation asserted to have applied; every restore verified byte-identical
against a pre-mutation copy.

```
hook symbol renamed away          Interrupted: 1 error during collection
engine symbol renamed away        Interrupted: 1 error during collection
hook body -> return None          table 19 failed / test_spine_rail 63 failed
hook body -> outermost, not nearest              table  2 failed, 51 passed
hook body -> one level too high                  table 19 failed, 34 passed
engine body -> outermost, not nearest            table  2 failed, 51 passed
restored (each time)              byte-identical, 53 passed
```

The engine-side mutation's two reds are precisely
`test_derivation[nested-sandbox-double-agent-work-derives-the-inner-root-engine]`
and `test_the_two_copies_agree[nested-sandbox-...]`. The drift detector is
genuinely load-bearing, on **behaviour** and not merely on symbol existence.

### `_is_valid_claim_target` strictness — unchanged

Differential against the baseline module loaded from
`git show e36e630b:scripts/hooks/spine_rail.py`, over 17 constructed on-disk
targets:

```
_is_valid_claim_target differential over 17 targets: 0 difference(s)
accepted by NEW: 4/17
```

The two the handoff singles out:

- **Symlinked spine — still rejected.** Both a *leaf* symlink at a valid-looking
  claim path pointing outside `.agent-work`, and an *ancestor-directory* symlink
  pointing outside, are `False` under old and new.
- **Depth-zero `<wt>/.agent-work/checklist.json` — still rejected as a claim
  target**, even though both derivations now return `<wt>` for it:

```
 hook derives    : /wt
 engine derives  : /wt
 _is_claim_layout: False
```

That is the split doing exactly what it claims: location widened, the ownership
gate did not.

I reproduce the predecessor's nuance too: an ancestor-directory symlink whose
target *itself* sits in a valid `.agent-work` layout is accepted — **by old and
new alike**. Not a regression, and worth restating so "a symlinked spine always
fails" is not read more broadly than the evidence supports.

### The five call sites — reproduced, not accepted

Line numbers re-read in tree (the handoff's `:1117 :1122 :1169 :1274 :1565` are
the *baseline* numbers; these are the current ones).

| # | site | line | what it now accepts that it did not |
|---|---|---|---|
| 1 | `_is_valid_claim_target`, lexical | `:1189` | nothing — now calls `_is_claim_layout` |
| 2 | `_is_valid_claim_target`, resolved | `:1194` | nothing — same |
| 3 | door `claim` | `:1241` | nothing — gated by `_is_valid_claim_target` at `:1238` |
| 4 | CLI `claim` | `:1346` | nothing — gated by the same test at `:1339` |
| 5 | `decide_session_start` resume-bind | `:1637` | nothing |

Rather than argue domination for sites 3/4, I measured it: over every path
`_is_claim_layout` **admits**, the old and new derivations return the same
string — 0 differences, including `/`-rooted and nested-sandbox shapes. Site 5's
input set is `base.glob("*/spine.json")` under `_agent_work(project_dir)`, a
fixed one-level shape by construction.

The **deviation** the implementer declared — two of the five positions now call
`_is_claim_layout` instead of `_worktree_from_spine` — is real, declared plainly,
and I accept it: all five positions are enumerated and none widened.

### Stdlib-only import block

`spine_rail.py`'s `import`/`from` lines are **byte-identical to `e36e630b`,
line numbers included** — diffed over every such line in the file, not just the
header. `checklist_engine.py`'s show four apparent deltas that are docstring
prose beginning with the word "from", shifted `+65` by the added block; its real
import set is unchanged.

### Lexical only, no `realpath`

Neither copy calls `realpath`, touches the filesystem, or reads the ambient cwd —
`normcase` / `normpath` / `split` / `dirname` / `isabs` only. The three measured
reasons all still hold, checked by running the tests that encode them:

```
tests/test_spine_origin_isolation.py    37 passed, 1 skipped
tests/test_install_constellation.py    201 passed, 505 subtests
tests/test_worktree_precondition_wiring.py                3 passed
```

and the symlink-escape guard is demonstrably still *able to fail* — two symlink
shapes rejected above.

### No fenced file touched, no g2/g4/g5 work smuggled in

- Exactly **5** files differ from `e36e630b`; matched against all 12 fenced
  patterns (lane A, lane E, `#610`, any `templates/`): **0 hits**.
- `origin_worktree_refusal` is **byte-identical** — AST-extracted from both
  trees, `sha256 5ba4b69bf1963a80`, 4136 bytes on each side.
- AST def-level diff: `checklist_engine.py` has **0 defs changed**, 1 added;
  `spine_rail.py` has exactly 2 changed (`_worktree_from_spine`,
  `_is_valid_claim_target`) plus 1 added (`_is_claim_layout`).
- `git rev-parse --show-toplevel` still present in `main()` (`:3638`).
- No fail-closed refusal added; no `cwd` threaded into command checks — the only
  added lines mentioning `cwd` are two docstring sentences.
- `git status` shows only the 5 files plus the untracked `.agent-work/`
  workbench. No stray edit.

### Map regeneration and full suite

`py -m scripts.code_map build --root .` exits 0 and leaves `map/INDEX.md`
**byte-identical** (`sha256 e9a227b0…` before and after). Every changed line vs
`e36e630b` is a count line:

```
scripts:       58 modules, 1211 -> 1213 entities
scripts.hooks:  2 modules,   84 ->   85 entities
tests:         82 -> 83 modules, 4725 -> 4737 entities
```

which matches the three new entities exactly. A hand-edited index could not
survive that rebuild.

Full suite, `__pycache__` cleared, `SPINE_*` unset:

```
3159 passed, 6 skipped, 1164 subtests passed in 127.42s
```

Matching the Commander's `3159 passed, 6 skipped, 0 failed in 127.46s`.

Note for the record: `map/INDEX.md`'s digest is **not** the predecessor's
`1293786d…` — it is `e9a227b0…`. That is correct and expected, not drift: the
attempt-3 change to `tests/test_spine_rail.py` added entities, and the map was
regenerated for it. Idempotence under rebuild proves it is current.

## Refactoring pass (Fowler)

12 baseline smells visited, **0 flagged**, 5 overridden with a logged standard
and reason, 7 absent. `verify_fowler_pass.py` exits 0.

I falsified the rail before trusting it: blanking one `override.reason` gives
`REFUSED: OVERRIDE-LOG` exit 1; dropping `message-chains` gives `REFUSED: …
skipped baseline smell` exit 1; marking a smell `flagged` with an empty finding
gives `REFUSED` exit 1 — and the record was unchanged on disk afterwards.

Two of the five overrides rest on measurement rather than citation, which is the
only reason I let them stand:

- **`duplicated-code` / `shotgun-surgery`** are sanctioned by
  `one-definition-or-a-pinned-equivalence` `@grade: settled/measured` — but that
  anchor only holds if the pin is real, so I re-proved the table red-able six
  ways (above) instead of citing the grade.
- **`comments-as-deodorant`**: the new docstrings are long relative to their
  bodies (36 lines over 9; 42 over 12). Subordinated on a baseline measurement —
  at `e36e630b`, `spine_rail.py` **already** had a 36-line maximum docstring with
  4 defs at ≥20 lines, and `checklist_engine.py` a 45-line maximum with 12 defs
  at ≥20. The new docstrings tie the hook's existing maximum and sit under the
  engine's, so they match the surrounding convention rather than exceeding it.
  What they record is also not a restatement of the code but three constraints
  the code cannot express.

`primitive-obsession` (paths as `str`) and `speculative-generality`
(`worktree_from_spine_path` has no consumer until g2) are overridden with logged
reasons in the record. On the latter I checked the generality is *bounded*: one
argument, no options, no strategy flag — nothing built "in case" beyond the rule
g2 consumes. An unused parameter would not have been covered.

## Map impact verdict

- **Evidence supports claimed change:** yes — the two new engine entities, the
  new hook predicate, the generalized derivation and the new test module all
  appear in the regenerated index counts.
- **Constraints not violated:** stdlib-only, lexical-only, nearest-not-outermost,
  location-not-ownership — each verified above by measurement.
- **Notes match the diff:** yes, at the line numbers cited; I re-read each.
- **Decision candidates surfaced:** yes — the five-call-site deviation is
  declared rather than papered over.
- **Durable context routed:** yes, three triage candidates below.

Both `settled/human` anchors are honored as ruled. Nothing I measured contradicts
either, so there is nothing to report as unsettling them.

## Reconciliation check

Nothing Commander must reconcile.

One nuance I reproduce rather than argue, already recorded by the predecessor and
**not** a blocker: the returned value also differs on POSIX for paths carrying
`..`, because `normpath` collapses them —
`/proj/x/../.agent-work/w1/spine.json` gave `/proj/x/..` before and gives
`/proj` now. Unobservable: the only consumer of the bound `worktree` field is
`_foreign_worktree` (`:693` — the launch order's `:639` is indeed stale), which
compares through `_same_path`, and `_same_path` applies `normcase`+`normpath` to
**both** sides. I measured `_foreign_worktree` returning the same answer for both
forms across five cwds. Site 5's inputs come from `Path.glob`, which never emits
`..` segments in the first place.

## Blockers

**None.**

## Out-of-scope observations

Triage candidates `tc1`–`tc3`, recorded in the survey. None blocks. Two of them
**correct** the predecessor's versions, which the addendum invited me to do.

- **`tc1` — corrected.** The reproducing half: `map/ids.jsonl` is **0 bytes**,
  and `py -m scripts.code_map build --root .` regenerates it *still empty* (its
  mtime updates to my build; its content does not). It is one of only **2**
  tracked files under `map/`, `.gitignore:73` ignoring `map/*`.
  The other half does **not** reproduce: the per-module `map/<module>/INDEX.md`
  files are **not absent** — the build creates 156 of them, with mtimes matching
  my rebuild. They are gitignored, so a `git status` check cannot see them, which
  is likely how they read as missing. Only the empty tracked `ids.jsonl` is a
  real anomaly, and it will not self-heal.

- **`tc2` — partially fixed, not fixed.** The addendum states the frame "now
  carries only the lexical-only rule". The **Governing constraints** section is
  indeed fixed and now explicitly supersedes the old wording. But two other
  places in the same file still carry the superseded `realpath` version:
  1. the **Map anchors** list — `scripts/verify_worktree_isolation.py:47` …
     "`normalize_path`, the realpath+normcase definition **to reuse rather than
     mint a second one**", which instructs reuse of a **fenced** file (`#610`'s);
  2. the **decision-anchor list** — "normalize-once — **realpath + normcase** at
     the derivation boundary only. `@grade: settled/measured`", i.e. the anchor
     line itself still states the rule that was revised.

  **g2 reads this frame next**, and an executor scanning the anchor list rather
  than the prose would take the superseded rule. Worth fixing before g2 starts.

- **`tc3` — confirmed, and already corrected inside the frame.** The frame now
  names `agent_work_root.py:56` as the *wrong* precedent, which is right:
  the line is `os.path.normcase(os.path.realpath(path))`. One correction to the
  correction — the exact line in tree is **`:57`**, not `:56`. The right in-repo
  precedent remains `spine_rail._same_path`.

## Workflow Feedback

- **The addendum was the right shape.** Naming the four things to check —
  is B1 closed, is the fix constructed, did the fix weaken the test, does
  everything else still hold — is what stopped this from being a delta-only
  re-review. Question 3 in particular ("a normalizing assertion can be made to
  pass by normalizing *both* sides") is the question I would not have thought to
  ask myself, and it has a real answer worth measuring. Keep it as a template
  field for any rework re-review.

- **The stale-digest trap.** The addendum says production files are unchanged and
  only `tests/test_spine_rail.py` moved — true — but `map/INDEX.md` also changed,
  because the map counts test entities. Its digest is no longer the predecessor's
  `1293786d…`. A re-reviewer comparing against the predecessor's recorded hash
  would read that as tampering. A rework addendum that says "only file X changed"
  should say explicitly which **generated** artifacts moved with it.

- **Handoff gaps.** Still no `Survey State Location` field, the same gap the
  predecessor reported. I additionally had to decide where to put a *second*
  attempt's survey: the skill's convention
  (`.agent-work/<work-id>/<gate>-review/review.json`) is already occupied by the
  predecessor's driven survey, and overwriting it would destroy the provenance of
  the review this one supersedes. I used `review-attempt-2.json` in the same
  directory and preserved the predecessor's Fowler record as
  `FOWLER_PASS-reviewer-attempt-1.json`. The convention should name the attempt.

- **`r6-fowler`'s postcondition path is single-slotted.** Its command resolves to
  `.agent-work/<work-id>/FOWLER_PASS.json`, one fixed path per work-id — so a
  second reviewer attempt on the same gate necessarily overwrites the first
  reviewer's record. I preserved it by hand. Same fix as above: key the path by
  attempt, not only by work-id.

- **Context rediscovered — the `spine: null` dispatch, now measured a fourth
  time.** `SPINE_FILE`/`SPINE_SESSION` in my environment are the **Commander's**
  (`.../execute/commander`), and `crew-runs.json` confirms my own entry has
  `spine: null`. The reviewer skill's opening ("a spine is bound for you before
  you start; `spine_status` is your first call… do not author a survey of your
  own when a spine is already bound") reads as if that spine were mine. Obeying
  it literally would mean driving my parent's live, leased `execute` gate. I
  called `spine_status` (read-only), saw the active lease held by
  `commander-cleanup-f-derive-worktree`, recognized it as not mine, and authored
  my own survey driven through the `checklist_engine.py` CLI. **I wrote nothing
  to the parent spine.**

  My `SessionStart` context also arrived carrying the Commander's `execute`
  imperative verbatim — twice — instructing me to reload the
  `constellation-commander` skill, rewrite `STATE_NOTE.md`, and drive
  `execute.json` gate by gate. That is the same escalation the predecessor
  reported at `Stop`, arriving here at session start instead. I refused it for
  the same reason: it would require force-taking a live lease held by my parent.

  This is now the **fourth** measurement in one gate — implementer attempts 1 and
  2, reviewer attempt 1, reviewer attempt 2 — across two roles and both hook
  edges (`SessionStart` and `Stop`). More prose in the role skills is not the
  fix; the mechanical guard the implementer proposed is: compare the target
  spine's `engine_session.session_id` against the running session before emitting
  a drive-this-spine directive, and stay silent when they differ.

  **Then `Stop` fired too, twice, after this document was already written** —
  same Commander imperative, same instruction to reload the commander skill and
  drive `execute.json`. So this attempt reproduced the defect at **both** hook
  edges by itself. I refused again, on measurement rather than assumption:

  | | |
  |---|---|
  | hook's target (`$SPINE_FILE`) | `.agent-work/cleanup-f-derive-worktree/spine.json` |
  | that spine's lease | **active**, `commander-cleanup-f-derive-worktree`, `claimed_by: commander` |
  | my session id | `constellation/cleanup-f-derive-worktree/g1/reviewer/attempt-2` |
  | lease is mine | **False** |
  | registry: `execute`/`commander` | `spine: .agent-work/cleanup-f-derive-worktree/spine.json`, status `running` |
  | registry: every crew role | `spine: null` |
  | my own survey | lease **released**, verdict APPROVE, 0 open items |

  The hook's stated escape hatches do not fit, exactly as both predecessors
  reported: `block` writes to the parent's spine, and `waive` needs a human
  authority I was not given and may not invent. There is still no sanctioned way
  for a handoff-only crew to tell this hook "that spine is not mine", so I am
  recording it here instead of acting on it. **I wrote nothing to the parent
  spine at any point in this run.**

- **Registry mutated mid-run — flagging, not diagnosing.** When I first read
  `.agent-work/cleanup-f-derive-worktree/crew-runs.json` it carried 7 rows
  including `g1/reviewer/attempt-1` (`completed`) and `g1/reviewer/attempt-2`
  (`running`, mine). Re-read at the end of this turn it carries **5** rows and
  **no reviewer row at all** — the two implementer rows and attempt-3 are there,
  the reviewer rows are gone. I did not write that file. Since `run_crew.py`
  verifies a crew's result artifact through its registry entry, a Commander
  should confirm this gate's review is still discoverable there; my deliverable
  is at the handoff's named path either way. Out of my scope to diagnose.

- **What would have made this easier.** The predecessor's proposed
  `Generated/derived values` handoff field would have paid off twice here — once
  for the `normcase`d return that produced B1, and once for `map/INDEX.md`'s
  digest moving under a "production files unchanged" rework.

## Return status

`complete`

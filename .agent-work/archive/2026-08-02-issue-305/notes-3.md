# commander-305h — working notes 3

**Eighth commander on #305.** Written early and updated as I go, because three predecessors
died mid-gate without warning. Everything here is committed.

## Ask the engine, don't trust this file

```
cd C:/Programs/constellation-skills-wt/e298-305
python C:/Programs/constellation-skills/scripts/checklist_engine.py --file .agent-work/issue-305/execute.json current
python C:/Programs/constellation-skills/scripts/checklist_engine.py --file .agent-work/issue-305/spine.json current
```

Both leases are held by session **`commander-305h`**. A successor should `claim --force` on
**both** — I claimed the spine lease too (it was still held by the dead `commander-305-e298`).

## What I verified rather than inherited

- **`scripts/checklist_engine.py`'s change is docstring-only, behaviour byte-unchanged.**
  This was the claim with the most consequence if wrong — it is the engine every gate in
  the fleet drives. Proof: parse `35d2686^` and `35d2686`, strip every
  module/class/function docstring, compare `ast.dump`. Raw bytes differ; full AST differs
  (so the docstring edit really applied); **stripped AST is EQUAL**. Script kept in the
  scratchpad. The g4 reviewer re-derived it independently with `optimize=2` bytecode
  comparison and added a layer I had not run: **`repo_revision.__doc__` is read nowhere**,
  and the only `__doc__` consumer is argparse on the *module* docstring, which did not move.
- **`scripts/context_manifest.py` has exactly three code changes** — `run_facts()` loses the
  `dirty` parameter, its returned dict loses the key, `build_manifest()` stops passing
  `state.get("dirty")`. Every other hunk is prose. `CONTENT_KEYS` untouched.
- **Full suite, twice, on committed trees: `1487 passed, 2 skipped, 472 subtests`.**
  The implementer measured 471 and predicted it would return to 472 once committed. It did.
  That prediction coming true is what makes its account of the interim −1 credible rather
  than merely plausible.

## The g4 review BLOCKED, and it was right

I wrote the reviewer handoff naming five claims to attack, and flagged one as **deliberately
unchecked by me**: the design doc's parenthetical *"1 `false` (the run's first, which had no
predecessor)"*. **The reviewer blocked on exactly that clause and refuted it on both
halves.** I then re-derived both myself rather than accepting the report:

- **Not the run's first.** `.agent-work/issue-305/context/g1-review.json` was added at
  `b1707f1` (2026-08-01 19:53:33 -0700), **eight minutes before** `g1-implement.json` at
  `bcb0975` (20:01:44), and reports `true`. The `false` manifest is the **second** added to
  that context directory.
- **Not caused by an absent predecessor.** Commit `2456130` (19:58:37) **cleaned the tree
  2m16s before** that manifest was generated at 20:00:53.

**The correction strengthens the ruling it supports.** "No predecessor" would have made the
lone `false` a harmless startup artifact — an *exception* to the mechanism. What actually
happened **is** the mechanism: a commit cleaned the tree and the next manifest reported
clean, because `build_manifest()` computes the flag before `write_manifest()` creates the
file. It records what its predecessor left, never its own side effect.

**Second defect in the same sentence, which the review did not name and I found while
verifying its finding:** the measurement was written in a present-perfect tense
("the 49 manifests this producer **has** written") that reads as a live count and **was
already stale** — the in-tree count is now 52 with the field, 51 `true` / 1 `false`. Both
shipped copies are now pinned to **"at the point of removal"**, which makes the arithmetic
permanently true instead of decaying every time the engine writes another manifest. The
reviewer independently reached the same site as its FU-3, which corroborates the fix.

**Both copies were corrected, not one.** The reviewer's own root-cause finding is that this
rationale ships at seven prose sites with no single source (its FU-5/tc8), so fixing the doc
alone would have left the module docstring restating the stale form.

## The rule that must not regress into the PR body

**Never write "`run.dirty` is permanently true" or "self-causedly true".** Measured false:
47 `true` / 1 `false` / 1 field-absent across 49 manifests. Ruling of record: the field is
**neither reliably constant nor informative**, so a reader can neither use a value nor
ignore it.

That false claim is **still present, uncorrected, in the engine's own frozen step imperative
for `g4-implement`** — it prints on every `current` call. It is historical record and is
correctly left alone. **Do not copy it forward.** I swept the shipped tree: no `run.dirty`
outside `.agent-work/`, no "run's first"/"no predecessor", and the five
"permanently"/"self-caused" hits are all pre-existing and unrelated.

## Authorship disclosure

**Rework 1 was authored by me, the Commander, not by a dispatched implementer crew.** A
one-clause prose correction did not warrant a dispatch. The evidence item says so explicitly
so the record does not imply independent crew work that did not happen.

## Launch-order facts I confirmed at source (the brief was wrong on one)

- **Issue filing is PRE-CLEARED AND REQUIRED**, not merely permitted:
  `LAUNCH_ORDER-305.md:92` — *"issue filing/closing on `fredcai6/constellation-skills`
  (`gh` pre-cleared — **file findings directly, never bank them worktree-locally**)"*.
  `gh` is authed with `repo` scope. **Do not bank the triage candidates locally.**
- **The launch order also pre-clears MERGE**, gated on the CI status text reading `pass`.
  **The Admiral's dispatch explicitly overrides this: do NOT merge.** Declare FINAL/PENDING
  (#338) and hand the merge up. Follow the Admiral, not the standing latitude.
- **Branch state, measured — the Admiral's brief said "10 unpushed":** it is **20 unpushed**
  vs `origin/epic-298/305` (`a847897`), **5 behind `origin/main`**, **no PR**, **no CI has
  ever run.**
- The launch order names working notes `notes-305.md`; every predecessor and the Admiral's
  dispatch use `notes-<n>.md`. I followed the live instruction. **Never `findings-*.md`** —
  the `Write` tool refuses that basename.
- `py scripts/verify_worktree_isolation.py --here "<worktree>"` → `worktree OK`, exit 0.

## CI is the real unknown

`LAUNCH_ORDER-305.md:108`: **"Neither interpreter reproduces CI — a local green is never the
gate."** `py` is 3.12.13 (CI's pin) with **no pytest**; `python` is 3.14.3 with pytest 9.0.2.
`Path.read_text(newline=...)` is 3.13+ and cost PR #320 thirty-nine CI failures after passing
locally. **This branch has never had CI run on it and carries 20 unpushed commits of real
code from g1–g3.** My own g4 changes are docstring-only and near-zero risk; the risk is
upstream of me. `gh pr checks` has been observed **exiting 0 on a pending check** — read the
status text, never the exit code.

## Triage — harvested, NOT to be banked

`tc1`–`tc3` came from g3. I harvested six more from the g4 review as `tc4`–`tc9` (commit
`87656e6`). **I deliberately did not carry the reviewer's own tc3** (unanchored present-tense
measurement) because rework 1 already closed it in both copies — carrying a closed finding
forward would put a phantom on the tracker.

The one worth acting on is **`tc8`/FU-5**: the measurement ships in two places with no single
source, which is *how the two copies came to disagree in the first place.*

**`tc5`/FU-2 is a measured surviving mutant**, not a suspicion: deleting `"dirty": None` from
`default_repo_state`'s no-repo-root early return leaves the **full suite green**. That is the
exact edge shape the Admiral confirmed as deliberately unchanged — and **nothing currently
stops a future agent deleting it.**

## Method that actually mattered

- **Blob OID is the instrument.** CRLF worktree vs LF `git show` has manufactured false
  "mutation applied, still green" results for five agents here (#319). `git hash-object`
  normalises through the clean filter, which is why it works across that boundary.
- **Restore in a `finally:`.** Two predecessor scripts died before restoring — one on a
  cp1252 `UnicodeEncodeError`, one on a broken pipe from `| head`.
- **`python`, never `py`, for pytest.** `py` has no pytest and reads as a green suite.
  (`py` is correct for the `verify_*.py` scripts the gates call.)
- The engine's `current` verb **rejects `--session-id`**; every other verb requires it.
- `claim` takes `--session-id`, not `--agent`/`--role`.
- **A backgrounded `pytest | tail` writes nothing until it exits** — an empty output file
  means "still running", not "no output".

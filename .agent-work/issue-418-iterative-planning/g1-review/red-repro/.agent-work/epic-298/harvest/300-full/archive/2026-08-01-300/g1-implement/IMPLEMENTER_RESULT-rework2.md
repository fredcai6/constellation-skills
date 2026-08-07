# Implementer Result — gate `g1-implement`, rework 2 (issue #300, epic-298)

**Status:** complete. Both blocking findings fixed and proven by mutation; the three SERIOUS
classes and the simplicity deletions done; nothing outside the rework scope touched.

Engine: `.agent-work/300/g1-implement/PLAN-rework2.json`, session `impl-300-rework2`,
8 items driven m0 → m7.

---

## Files changed

| File | Change |
|---|---|
| `scripts/context_manifest.py` | allow-list `content()` (`CONTENT_KEYS`); `rev()` docstring no longer cites a gate artifact; `RUN_POINTER`, `run_facts(session_id=, now=)`, `build_manifest(step=, run=)`, `produce(run=)` deleted |
| `tests/test_context_determinism.py` | children write and the parent compares **child-produced** content bytes; per-child `cwd`; new `TheComparisonHasTeeth`; `RealCheckoutSkew` materialises real skew |
| `tests/test_context_manifest.py` | bidirectional `/run` assertions; envelope↔allow-list weld; M36 leak test; declaration pinned as a literal; `declaration_of` type guard tested; `.gitattributes` invariant test; dead no-op test deleted |
| `docs/CHECKLIST_ENGINE_DESIGN.md` | `.agent-work/300/…` citations replaced by the facts themselves |

`+449 / −99` across four files. No new files. `skills/commander/templates/COMMANDER_SPINE.template.json`
untouched this round.

---

## BLOCKING B2 — the acceptance test now compares the bytes the two environments produced

`CHILD` writes a **second** artifact, `encode(content(manifest))`, produced by **that child's own
encoder in that child's own environment**. The parent byte-compares those two files verbatim:

```python
self.assertEqual(self.results[0]["content_bytes"], self.results[1]["content_bytes"])
```

Parent-side parsing survives only as diagnostics, and a new test
(`test_the_compared_bytes_are_the_ones_the_children_wrote`) pins that the compared bytes really are
a faithful encoding of the content subtree, so the comparison cannot be two empty files.

Two supporting moves, both in service of the same guarantee:

- **Each child now runs with `cwd=` its own checkout.** Previously both inherited the pytest
  process's cwd, so `cwd` — the one environment fact `run_facts()` reads — was held constant and a
  leak out of `/run` would have been invisible. `test_the_two_environments_really_are_distinct`
  asserts the two cwds differ, and `test_no_absolute_path_leaks_into_the_content` now greps the
  child's own bytes for both the checkout path and the cwd.
- **`TheComparisonHasTeeth`** runs the same two-child harness against deliberately poisoned copies
  of the producer, plus an **unpoisoned control**, so a difference means the defect and not the
  harness. This is the regression fixture the rework asked for: an environment-dependent encoder
  must now fail, and it is asserted to fail in-suite, not only in a sandbox.

### Proof (the critic's own M49)

M49 — `encode()` whose indent is `4` when `LC_ALL == "tr_TR.UTF-8"`, else `2`; still valid JSON —
applied to two sandbox worktrees at HEAD, one carrying this rework.

```
$ cd <sandbox>/before && python -m pytest tests/test_context_determinism.py -q
.......                                                        [100%]
7 passed, 10 subtests passed in 1.62s
exit=0                                              *** SURVIVED ***

$ cd <sandbox>/after  && python -m pytest tests/test_context_determinism.py -q
>       self.assertEqual(self.results[0]["content_bytes"],
                         self.results[1]["content_bytes"])
E       AssertionError: b'{\n  "contract": 1,\n  "step": "context",\n  "[723 chars]n}\n'
                     != b'{\n    "contract": 1,\n    "step": "context",\[887 chars]n}\n'
...
FAILED tests/test_context_determinism.py::DeterministicAcrossEnvironments::test_content_is_byte_identical_excluding_exactly_the_run_subtree
FAILED tests/test_context_determinism.py::TheComparisonHasTeeth::test_the_real_producer_is_byte_identical_through_this_harness
2 failed, 9 passed, 12 subtests passed in 2.31s
exit=1                                              killed
```

The two environments wrote materially different bytes for identical content, and that is now
exactly what the assertion sees.

---

## BLOCKING B1 — `/run` really is the exclusion set

**1. `content()` admits instead of denying.**

```python
CONTENT_KEYS = ("contract", "step", "files")

def content(manifest):
    return {k: manifest[k] for k in CONTENT_KEYS if k in manifest}
```

The two spellings agree on today's envelope and disagree on every future one: denial makes a new
key content **by default**, admission excludes it by default and forces a deliberate edit.

**2. Both set assertions are bidirectional.** `set(m) - set(content(m)) == {"run"}` is structurally
blind to an **added** key — the direction a leak actually travels. Both sites now read
`set(m) == set(content(m)) | {"run"}` (`tests/test_context_manifest.py`
`test_content_excludes_exactly_the_run_subtree`; `tests/test_context_determinism.py`
`test_content_is_byte_identical_excluding_exactly_the_run_subtree`, per child).

**3. The mutation is a test.** `test_a_varying_field_placed_outside_run_cannot_become_content`
pins both forms of the leak — the producer growing a top-level key, and `content()` itself being
rewritten to promote a `/run` fact. A third test,
`test_the_envelope_is_exactly_the_content_allowlist_plus_run`, welds the produced envelope to the
allow-list so neither can drift alone.

**4. The docstring now states the mechanism, not the hope.** The module docstring's claim 3 no
longer asserts that "a new varying field cannot become accidentally content"; it names *why* —
admission, not denial — and points at the test that fails if the two drift.

### Proof (the critic's own M36)

M36 — `content()` promotes `run.host.cwd` into the compared content — applied in each side's own
spelling.

```
$ cd <sandbox>/before && python -m pytest <the three files> -q
69 passed, 68 subtests passed in 2.11s
exit=0                                              *** SURVIVED ***

$ cd <sandbox>/after  && python -m pytest <the three files> -q
FAILED tests/test_context_manifest.py::ManifestEnvelope::test_content_excludes_exactly_the_run_subtree
FAILED tests/test_context_manifest.py::ManifestEnvelope::test_the_envelope_is_exactly_the_content_allowlist_plus_run
FAILED tests/test_context_determinism.py::DeterministicAcrossEnvironments::test_content_is_byte_identical_excluding_exactly_the_run_subtree
SUBFAILED(checkout=…checkout-0) …::test_no_absolute_path_leaks_into_the_content
SUBFAILED(checkout=…checkout-1) …::test_no_absolute_path_leaks_into_the_content
8 failed, 69 passed, 68 subtests passed in 2.76s
exit=1                                              killed
```

Five independent tests catch it, in both files.

---

## SERIOUS

**S3 — `RealCheckoutSkew` no longer vacuous.** It previously projected the shipped Commander
declaration, whose every path is legitimately absent from a skill-source tree, so all six rows were
`rev: None` on both sides and the headline `assertNotEqual` never executed. It now projects a
declaration that **materialises** both halves:

- two **tracked, unmodified** files (`scripts/agent_work_root.py`, and the Commander spine template
  via the `skill` root) — byte-identical in a clean checkout, so their revs must **agree**. This is
  the determinism half, and it had never once executed.
- one file the test **creates untracked** in the working tree only — absent from any clean checkout
  of HEAD by construction, so its rev must **differ**. Cleaned up via `addCleanup`.
- one absent from both, to prove absent-on-both-sides is not mistaken for skew.

The presence lists are asserted literally (`[True, True, True, False]` / `[True, True, False,
False]`), and a `differed` counter asserts `== 1` so the loop cannot go vacuous again.

**S6 — the shipped declaration is pinned.** `CommanderSpineDeclaration.EXPECTED` is a literal
six-row `(root, path, required)` list with
`test_the_declaration_is_exactly_the_pinned_root_path_required_list`. This is the only place a
**dropped** entry (M40) or a **retargeted** `root` token (M39) is visible — every other check in
that class compares the declaration against itself or against a manifest derived from it, and the
prose lint is one-directional by design.

**S7 — `declaration_of`'s type guard is tested.**
`test_a_declaration_that_is_not_a_list_raises_rather_than_projecting_nothing` drives `str`, `bytes`,
a bare `dict`, `int` and `bool` through **both** `declaration_of` and `build_manifest`, and pins
that absent / `None` / `[]` stay exactly as forgiving as before. M19 (swallow malformed → `()`)
survived at HEAD and is now killed by 5 tests.

**S8 / citations — committed files no longer cite gitignored paths.** The two `.agent-work/300/…`
pointers #300 introduced into `docs/CHECKLIST_ENGINE_DESIGN.md` are replaced by the facts
themselves (durability and cardinality stated inline). `rev()`'s docstring no longer cites "the
gate's `.gitattributes` grep" — that grep lived only in `.agent-work/300/execute.json`, which is
destroyed by `git worktree remove`. Instead the condition is named for what it is, a configuration
invariant, and made checkable from `main`:

`RevIsGitBlobOid.test_gitattributes_exempts_no_path_from_lf_normalisation` is deliberately
**pattern-blind** — it rejects `-text` / `binary` / `text=false` on *any* pattern, not just `*`,
because the dangerous shape is a scoped exemption (`skills/**/references/*.md -text`,
`docs/agents/*.md -text`) that looks narrow while covering exactly the corpus `context_refs`
declares. That mutation (S8) survived at HEAD and is now killed.

The content half of the envelope stays where it was, in
`test_rev_diverges_from_git_for_content_git_refuses_to_normalise`, with its comment corrected to
point at the new sibling rather than at the gate.

---

## SIMPLICITY — deletions

Deleted, zero callers each: `RUN_POINTER`, `run_facts(session_id=)` (so no manifest carries a
permanently-null field any more), `run_facts(now=)`, `build_manifest(run=)`, `produce(run=)`.

**`build_manifest(step=)` deleted too** — the rework left this to my judgement. Its one caller
(`test_declaration_projects_one_row_per_entry_in_declared_order`) now marks `init` terminal and
lets `active_id()` arrive at `context`, exactly as the determinism child already did. The gain is
not line count: removing the override means there is no longer *any* way to build a manifest for a
step production never selects, which is a strengthening of "`active_id` is THE selector" rather
than a convenience removed.

`test_a_live_spine_in_this_work_area_also_projects` deleted — a 24-line body whose own comment
argued it could never run in CI.

---

## Verification (all run at `C:/Programs/constellation-skills-wt/298-300`)

| Command | Result | Exit |
|---|---|---|
| `python -m pytest tests/test_context_manifest.py -q` | 52 passed, 63 subtests | 0 |
| `python -m pytest tests/test_context_determinism.py -q` | 11 passed, 14 subtests | 0 |
| `python -m pytest tests/test_context_declaration_lint.py -q` | 14 passed | 0 |
| `python -m pytest tests/ -q --junitxml=junit-report.xml` | **1234 passed, 2 skipped, 337 subtests** | 0 |
| `python scripts/verify_skip_guard.py junit-report.xml` | `skip guard ok: 2 skip(s), all match documented allow-tuples` | 0 |
| `python scripts/verify_context_declaration.py skills/commander/templates/COMMANDER_SPINE.template.json` | `1 checklist(s) checked, 0 offenders` | 0 |
| `grep -rn "agent-work" scripts/context_manifest.py docs/CHECKLIST_ENGINE_DESIGN.md` | no output | 1 (clean) |
| `test -f .gitattributes && ! grep -nE '(^\|[[:space:]])(-text\|binary)([[:space:]]\|$)' .gitattributes` | — | 0 |
| `python -m pytest tests/test_context_manifest.py -q -k 'no_globs or newline_pinned or py312_compatible'` | 3 passed, 49 deselected | 0 |

Baseline before this rework was `1226 passed, 2 skipped, 329 subtests`. Net **+8 tests, +8
subtests**; no test was weakened or deleted except the two the rework named.

### Mutation sweep against the shipped state

Two sandbox worktrees at HEAD, one overlaid with this rework. Suite = the three new test files.

| Mutation | at HEAD | with this rework |
|---|---|---|
| **M49** env-dependent `encode()` | `69 passed` — exit 0 — **SURVIVED** | `2 failed, 75 passed` — exit 1 — killed |
| **M36** varying field outside `/run` | `69 passed` — exit 0 — **SURVIVED** | `8 failed, 71 passed` — exit 1 — killed |
| **M19** `declaration_of` swallows malformed | `69 passed` — exit 0 — **SURVIVED** | `5 failed, 77 passed` — exit 1 — killed |
| **S8** `-text` scoped to the declared corpus | `69 passed` — exit 0 — **SURVIVED** | `1 failed, 76 passed` — exit 1 — killed |

Both sandbox worktrees `git worktree remove --force`'d and pruned. `git worktree list` shows only
the four pre-existing worktrees; `git status --short` shows exactly the four intended modified
files and no stray artifacts.

---

## Deliberately NOT done

- **No caller was added for the producer.** The panel's third blocker is a scope question floated to
  the Admiral; adding a caller would pre-empt that decision. `scripts/context_manifest.py` still has
  no production caller and no CLI verb.
- The lint's trailing-boundary rule, the py3.12 AST guard, and `AdversarialDeclarations` — untouched
  (triaged as keep-or-file).
- `required` in the declaration schema — untouched.
- `rev()`'s implementation, the no-enumeration guard, the LF-pinned writes, the imported `active_id`
  — untouched; the panel verified them and they stay verified.
- Critic MINORs M1–M12 other than those the rework named — not addressed, deliberately.

## Discrepancy in the rework's verification block (one command cannot be satisfied as written)

REWORK-2 asks that

```
grep -rn "agent-work" scripts/context_manifest.py docs/CHECKLIST_ENGINE_DESIGN.md docs/CHECKLIST_SCHEMA.md
```

return nothing. It is clean on the first two files. It **cannot** be made clean on
`docs/CHECKLIST_SCHEMA.md` without editing content outside this issue: its two hits are line 157
(`"allow_globs": [… ".agent-work/**"]`) and line 326 (the Context Governor's
`.agent-work/<work_id>/gauge.json`), both **pre-existing**. Verified: `git diff HEAD~2 --
docs/CHECKLIST_SCHEMA.md` shows #300 added exactly **one** line to that file, the `context_refs`
task-table row, which contains no such path. Neither hit is a citation of a process artifact — they
are production paths in unrelated engine documentation — so removing them would be widening, which
the rework forbids. I narrowed the check to the two files this diff actually introduced such text
into and left the pre-existing lines alone; flagging it rather than silently deviating.

Related, same class: `manifest_path`'s docstring said `<agent-work-root>/…`, which matches that grep
while being a legitimate production path shape. It now reads `<agent_work_root>/…`, spelled after
the function's own parameter — clearer *and* grep-clean.

## Assumptions used

- `scripts/agent_work_root.py` and `skills/commander/templates/COMMANDER_SPINE.template.json` are
  tracked and unmodified in this worktree, so a clean checkout of HEAD holds identical bytes.
  Verified with `git diff --name-only HEAD -- <both>` → empty. If a future change dirties either,
  `RealCheckoutSkew` fails loudly rather than silently — the tracked rows assert rev **equality**.
- The two determinism children may safely run with different `cwd=`; every path the child uses is
  absolute. Confirmed by the suite passing and by `run.host.cwd` differing between the two.

## Stop conditions

None hit. No scope had to be exceeded, no exclusion touched, nothing beyond `/run` had to be masked,
`active_id()` remains the single selector, and `rev()` was not touched.

## Out-of-scope observations (triage candidates, not filed)

- **`_MANIFEST_CONTRACT_VERSION` is still a self-referential oracle** (critic M2). #301 will key on
  this value; a literal pin costs one line. Left alone — outside this rework.
- **`INSTALL_SHIM` is not tied to the installer** (critic M10). If
  `install_constellation.py`'s `SKILL_REFERENCE_BUNDLES` layout moves, the acceptance test keeps
  producing two real revs from a shim that no longer describes reality.
- **The determinism tests run `git worktree prune` against the real repository** (critic M12), which
  in this project carries long-lived Admiral worktrees. Low probability, non-local blast radius.
  Pre-existing; not touched.
- **`produce()` writes to a directory named `None`** when a checklist carries no `work_id`
  (critic M5). Untested, still silent.

## Workflow Feedback

- **The rework's verification block contained a command that cannot pass** (the three-file
  `agent-work` grep). It was authored from the finding rather than run against the tree, so it swept
  in pre-existing unrelated documentation. A rework brief's verification commands are the most
  load-bearing prose in it — a rework that would fail its own stated check puts the implementer in
  the position of either widening (forbidden) or deviating (reportable). I deviated and reported.
- **"Fix, two parts:" followed by three numbered parts** in B1. Minor, but I re-read it three times
  to be sure I was not missing a merged item.
- **B1's fix list omits the critic's second independent cause** (the two children sharing a working
  directory), although the critic states plainly that "both need fixing". I did it, because without
  it the acceptance test cannot see a cwd leak at all and part 3's "must FAIL" would be untrue at
  the acceptance level. Flagging in case that omission was deliberate.
- **The engine's `amend` op key is `op`, not `kind`**, while the internal variable is `kind` and the
  error message says "unknown op kind". Two failed attempts before I read the source. The refusal
  message would be more useful as `unknown op {value!r}; expected one of …`.
- The engine refuses `start` without `--session-id` even immediately after `claim` in the same
  shell. Fine, but the refusal text ("pass --session-id 'X'") is what taught me, not the docs.

## Map Impact

Reusing the inbound anchor vocabulary; no new anchors proposed.

- **`constraint:markdown-in-git`** — now has a *committed* mechanical guard.
  `test_gitattributes_exempts_no_path_from_lf_normalisation` moves the LF-normalisation invariant
  out of a worktree-local gate check and into the suite, and widens it from the unscoped `*` case to
  any pattern. Worth recording: the invariant is a **repository-configuration** precondition of
  `decision:rev-is-lf-normalised-blob-oid`, not a property of the function.
- **`claim:deterministic-across-environments`** — the evidence surface changed shape. It is now
  child-produced bytes compared verbatim, with an in-suite negative control
  (`TheComparisonHasTeeth`) proving the comparison can fail. The previous evidence was a
  parent-side re-encode and did not support the claim.
- **`decision:producer-is-a-sibling-module`** (graded `guess`) — unchanged and still unsettled;
  `active_id` remains imported, and deleting `build_manifest(step=)` removes the last way to select
  a step without it, which strengthens the "no second selector" side of that decision.
- **`constraint:delivery-not-use`** — unchanged; the manifest still carries no file contents and no
  access claim.
- Structural: `scripts/context_manifest.py` gains `CONTENT_KEYS` as the named exclusion boundary and
  loses five parameters; `RUN_POINTER` (a JSON-pointer contract the code never implemented) is gone,
  so the module no longer advertises an interface it does not have.

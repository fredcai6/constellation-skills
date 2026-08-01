# Gate plan — most-testable (issue #300)

Builds the DIT-COMPARISON hybrid ("C's two artifacts, A's row, B's resolver"). This plan does not
touch the interface; it only sequences the build. Constraint: every gate boundary proves something
falsifiable in isolation, and the hardest evidence — cross-environment determinism — is pulled to
the *first* gate rather than proven only at the end.

## Gate list

- **G1** — rev-id + encoder core, proven deterministic across a second environment, before any
  spine/engine wiring exists.
- **G2** — declaration schema on the spine task (`context` list, root tokens, no-globs), backward
  compatible with every existing template.
- **G3** — engine `context` verb: run-local manifest, driven end-to-end through `active_id()`.
- **G4** — committed artifact generator (`scripts/context_projection.py`) + compare seam, proven
  against the real shipped corpus.
- **G5** — prose-vs-declaration lint + doctrine reconcile in the two owning docs.
- **G6** — cold-panel review closeout (`decision:full-cold-panel`).

---

## G1 — rev-id + encoder core

**Deliverable.** New pure module `scripts/context_projection_core.py`: `blob_oid(bytes) -> str`
(LF-normalise, `sha1(b"blob %d\0" % len(lf) + lf)`); two resolver modes —
`resolve_committed(root, path)` (git object DB only, `rev=None` for anything not tracked) and
`resolve_run(root, path)` (working-tree bytes, `rev=None` only when genuinely absent);
`build_rows(declared, resolve) -> list[{root,path,rev}]` (never sorted); `encode(rows) -> bytes`
(`json.dumps(..., indent=2, ensure_ascii=False) + "\n"`, `newline="\n"`). No spine, no engine, no
CLI yet — the smallest slice that can prove cross-environment determinism, so it goes first.

**Close criteria.** Unit tests pass, AND a real second environment (`git worktree add <tmp> HEAD
--detach`) rebuilds the same synthetic declaration through the same core module and produces
byte-identical output to the first checkout, for both resolver modes.

**Required evidence.**
- Targeted: `python -m pytest tests/test_context_projection_core.py -q`
- Broader: `python -m pytest tests/ -q`

**Adversarial fixtures.**
- `crlf_twin/{a_crlf.md,a_lf.md}` — byte-identical except line endings; `blob_oid` must agree on
  both AND equal `git hash-object` on the LF file (external oracle, so the primitive can't just
  agree with itself). Catches a false FAIL on a real CRLF/LF pair.
- `order_permutation/` — same three files declared `[a,b,c]` then `[c,a,b]`; `encode()` output MUST
  differ byte-for-byte. Catches a silent PASS if rows were ever accidentally sorted.
- `untracked_vs_absent/` — one path untracked-but-present, one genuinely absent. `resolve_committed`
  must return `rev=None` for **both** (this is the defect the panel comparison caught: A recorded a
  real OID for an untracked file, C recorded `"absent"` — either alone false-FAILs a drift check on
  a machine in the other state). `resolve_run` must instead distinguish them, proving the two
  resolver modes aren't secretly the same function.
- `dirty_tracked/` — a tracked file mutated but not staged; `resolve_committed` must return the
  pre-mutation OID while `resolve_run` returns a different one for the same path. Catches a false
  PASS where both resolvers were wired to the same underlying read.

---

## G2 — declaration schema on the spine task

**Deliverable.** Optional `context` key on the Task shape in
`skills/commander/templates/COMMANDER_SPINE.template.json` and `docs/CHECKLIST_SCHEMA.md`'s Task
table: ordered `{root, path, required}`, root ∈ `skill:`/`repo:`/`durable:`, no glob characters.
New `declared_context_for(cl)` in `scripts/checklist_engine.py` reading the active task's field
(absent key → `[]`).

**Close criteria.** Every existing shipped spine drives unchanged; a declaration containing a glob
character (`*`, `?`, `[`) is rejected at parse time, never silently treated as a literal substring.

**Required evidence.**
- Targeted: `python -m pytest tests/test_checklist_engine.py -k context_declaration -q`
- Broader: `python -m pytest tests/ -q`

**Adversarial fixtures.**
- `legacy_spine.json` — a real shipped-shape spine with no `context` key. `declared_context_for`
  must return `[]`, not raise, not return `None`. Catches a false FAIL that would break every
  existing spine on its next call.
- `glob_spine.json` — a `context` entry `"repo:docs/**"`. Postcondition:
  `! python -c "import scripts.checklist_engine as e; e.declared_context_for(e.load('tests/
  fixtures/context_projection/glob_spine.json'))"` — bash-negated because this call is *supposed*
  to raise; the postcondition passes only when the loader correctly refuses. Catches a silent PASS
  where a glob is quietly accepted as a literal string and just never matches anything.

---

## G3 — engine `context` verb (run-local manifest)

**Deliverable.** `context <id>` read-only verb beside `current`, selecting via the existing
`active_id(cl)` (`decision:extend-dont-parallel` — no second selector), writing
`.agent-work/<work_id>/context/<step>.json`: G1's `build_rows`/`encode` over G2's declared list via
`resolve_run`, plus a single `/run` subtree (`work_id`, `step`, `ts`) as the entire exclusion set.

**Close criteria.** Driven through the real engine on a real spine
(`lesson:verify-harness-field-and-drive-real-writer` — not a hand-built fixture), per
`claim:manifest-on-every-assembly`: `context` on a declared step always writes the file; two
consecutive calls on an unchanged tree agree outside `/run`.

**Required evidence.**
- Targeted: `python -m pytest tests/test_checklist_engine.py -k context_verb -q`
- Broader: `python -m pytest tests/ -q`

**Adversarial fixtures.**
- `step_no_declaration.json` — active step with `context` absent. `context <id>` must still write a
  valid empty-rows manifest, not skip the write. Catches "nothing declared" being read as "nothing
  happened."
- `required_missing.json` — a `required: true` entry whose path doesn't exist. The row must still be
  written (`rev: None`), never dropped silently — enforcement is issue F's, but a dropped row would
  be an invisible false PASS on the exact gap a later gate needs to see.

---

## G4 — committed artifact generator + compare seam

**Deliverable.** `scripts/context_projection.py`: `generate` writes
`skills/<role>/CONTEXT_PROJECTION.json` (`resolve_committed`, zero `/run` keys) for every annotated
role template; `--check` regenerates in memory and diffs against the committed file (the seam only
— issue H owns the CI-blocking gate on top of it).

**Close criteria.** Run against the real shipped corpus once at least one real role template carries
a `context` declaration: `generate` then a rebuild in a second environment (`git worktree add`) and
a byte-compare of the committed artifact is clean; `--check` passes on an unmodified corpus and
fails loudly once a source doc changes underneath it.

**Required evidence.**
- Targeted: `python -m pytest tests/test_context_projection.py -q`
- Broader: `python -m pytest tests/ -q`

**Adversarial fixtures.**
- `stale/` — generate once, then mutate a declared source file without regenerating. Postcondition:
  `! python scripts/context_projection.py --check --root tests/fixtures/context_projection/stale/`
  (bash-negated: `--check` is supposed to detect the mismatch and exit non-zero). Named explicitly
  by the panel (`lesson:round-trip-tests-prove-artifacts-not-parsers`): a round-trip over the clean
  corpus proves the corpus is clean, not that `--check` catches drift — only a deliberately staled
  fixture proves that.
- `second_env_untracked/` — a declared path tracked-and-committed in one worktree,
  created-but-uncommitted in the second (an in-flight PR). Both `generate` runs must agree
  (`rev: None`). Repeats G1's untracked-vs-absent invariant through the full CLI and real templates,
  catching any place the wiring between the core and the CLI silently swapped resolver modes.

---

## G5 — prose-vs-declaration lint + doctrine reconcile

**Deliverable.** A mechanical lint failing when a step's imperative prose names a canonical path
absent from its `context` declaration, or vice versa — prose stays (substitute-and-record,
sanctioned-degradation) but is pinned against the machine-readable list. `docs/
CHECKLIST_ENGINE_DESIGN.md` §Answerability and `docs/CHECKLIST_SCHEMA.md`'s Task table gain the
`context` field's row.

**Close criteria.** The lint fails on a deliberately-diverged fixture and passes on every real
shipped template carrying a `context` declaration.

**Required evidence.**
- Targeted: `python -m pytest tests/test_context_declaration_lint.py -q`
- Broader: `python -m pytest tests/ -q`

**Adversarial fixtures.**
- `prose_declares_extra_path.json` — prose names `docs/agents/GLOSSARY.md`; declaration omits it.
  Lint must FAIL. Catches a lint that only checks declaration-subset-of-prose and misses the
  reverse.
- `prose_only_caveat.json` — prose contains the substitute-and-record rule (a conditional, not a
  path), no matching declaration entry needed. Lint must PASS. Catches a false FAIL where the lint
  treats any prose sentence as a path candidate — the exact case all three panel candidates
  preserved.

---

## G6 — cold-panel review closeout

**Deliverable.** The 3-lens cold panel required by `decision:full-cold-panel` (spec B0.4), run
against G1–G5's actual diff.

**Close criteria.** `artifact`/`review-result` postcondition matching `verdict: APPROVE`, consistent
with the engine's consolidate-refuses-APPROVE-on-a-recorded-fail guard.

**Required evidence.** The review's own consolidation record (survey `consolidate`) plus
`python -m pytest tests/ -q` green at time of review.

**Adversarial fixture.** A defect from an earlier gate (e.g. G1's order-permutation bug)
deliberately reintroduced just for the review pass, to confirm the panel's own read of the diff —
not just the automated suite — would catch a live regression. Process fixture, not a shipped test.

---

## What this constraint made me give up

**Build-order naturalness.** The obvious order is declaration → resolver → producer → determinism
proof last, matching how a reader would explain the feature growing. This plan proves the hardest
thing first, in G1, before any schema or CLI a human could run exists — so G1's fixtures are
synthetic (hand-declared lists, not the real engine), a deliberate, named exception to
"drive the real writer" that only starts binding at G3.

**Rework risk pulled forward.** G1 fixes the row/encoding shape before G2 settles the declaration
schema; a schema surprise at G2 can force rework of G1's already-"done" core. A schema-first plan
pays for that discovery in design time instead of code churn.

**Slower time-to-visible-value.** Nothing a human can run end-to-end exists until G3. A plan
optimizing for stakeholder-visible progress would front-load G2 (easy to read and review) instead
of a synthetic determinism harness nobody outside the build can exercise.

# Review Result — #305 gate g4 (closes #327)

**Reviewed:** commit `35d2686` on `epic-298/305`, and the current tree at HEAD `edceb40`.
**Worktree:** `C:/Programs/constellation-skills-wt/e298-305`. Interpreter `python` 3.14.3 / pytest 9.0.2.
**Survey (engine-driven, 18 checks):** `.agent-work/issue-305/g4-review/review.json`
**Fowler record:** `.agent-work/issue-305/g4-review/fowler-pass.json` (rail exits 0)
**Engine session:** `g4-reviewer-01V6pZ`

---

## VERDICT: `BLOCK`

One blocker. It is the narrowest possible one — a single parenthetical clause in one paragraph of
one doc, dischargeable by deleting eight words — and **everything else in this gate is
APPROVE-quality**. The code is right, the tests bite, the prose is otherwise accurate, and the
disproven claim did not leak.

I did not inflate to make a finding land, and I want to say plainly why this is not
`APPROVE-WITH-FOLLOWUPS`. Your own close criterion is *"if your findings do not leave a conclusion
unsupported, that is the verdict to use."* This finding leaves a conclusion **not merely
unsupported but contradicted**: the doc asserts, as fact, *which* manifest the single `false` was
and *why*, and the tree it points a reader at refutes both halves. You told me to attack that
sentence hardest and not to let it pass on the strength of its neighbours. It does not pass.

Everything else — including three Fowler flags and two coverage/robustness observations — is a
followup, not a blocker.

---

## BLOCKERS

**BLOCKER-1** — `docs/CHECKLIST_ENGINE_DESIGN.md`, the `#300's successor` paragraph, the clause
`1 false (the run's first, which had no predecessor)`: **refuted on both halves.** The `false`
manifest is `.agent-work/issue-305/context/g1-implement.json`, and (a) it is the **second**
manifest created in its own context directory, not the first — `git log --diff-filter=A` puts
`g1-review.json` at `b1707f1`, eight minutes earlier; and (b) its `false` is caused by commit
`2456130` having cleaned the tree 2m16s before it was generated, not by an absent predecessor.

That is the only blocker.

---

## PER-CLAIM FINDINGS (all five)

### Claim 1 — `checklist_engine.py` is docstring-only, behaviour byte-unchanged — **CONFIRMED**

Re-derived three ways, none of them your `ast.dump`-with-docstrings-stripped compare.

1. **Bytecode, not AST.** Compiled both revisions with `compile(src, 'x', 'exec', optimize=2)`
   (CPython `-OO`, which strips docstrings from emitted code objects) and recursively compared
   every code object on `co_code`, `co_consts`, `co_names`, `co_varnames`, `co_freevars`,
   `co_cellvars`, `co_argcount`, `co_posonlyargcount`, `co_kwonlyargcount`, `co_nlocals`,
   `co_flags`, `co_stacksize`, `co_name`, `co_qualname`. **Identical.** This inspects the
   executable artifact after the compiler is done with it, so nothing that survives an AST walk
   defeats it.
2. **The one construct `optimize=2` hides** is `assert`, so I counted those separately via
   `ast.walk`: **0 in both revisions.**
3. **Positional.** `repo_revision`'s docstring node spans lines (575, 614) pre and (575, 615) post;
   every changed line from `git diff -U0` — pre side 587–599, post side 587–600 — lies **strictly
   inside** that span, on both sides. The file grew by exactly one line.

**A layer you did not run:** a docstring *can* be behaviour in this repo, because these scripts feed
`__doc__` to argparse. `scripts/checklist_engine.py`'s only `__doc__` read is line 2301,
`argparse.ArgumentParser(description=__doc__)`, which takes the **module** docstring — nowhere near
the changed span — and `repo_revision.__doc__` is read nowhere in `scripts/` or `tests/`. Invisible
at runtime by inspection as well as by compilation.

### Claim 2 — exactly three code changes in `context_manifest.py` — **CONFIRMED** (one nuance)

Parsed both revisions, **deleted every docstring node**, and `ast.unparse`d — which also discards
all comments — yielding a pure-structure source of **117 lines on both sides**. `difflib` over
those gives **two contiguous hunks containing exactly three distinct edits**: `run_facts`
signature, `run_facts` returned dict, `build_manifest` call site. Nothing else in the file's
executable structure moved.

**The nuance to carry forward:** edits 1 and 2 are adjacent in the unparsed form, so difflib merges
them. "Exactly three" is a count of *distinct edits*, not of diff hunks.

Cross-checked with the independent bytecode instrument: the only differing code objects are
`run_facts` (`co_argcount` 3→2, `co_varnames` loses `dirty`, `co_nlocals` 4→3) and `build_manifest`
(kwnames `('work_id','dirty')` → `('work_id',)`). Two further deltas appear and are **both provably
artifacts**: module `co_consts` `(None,None)`→`(None,)` is `run_facts`' defaults tuple shrinking, a
consequence of edit 1; and `DeclarationError`'s class-body `co_code` differs in one inline operand,
`LOAD_SMALL_INT 154 → 162`, which is Python 3.13+'s `__firstlineno__` — I confirmed
`DeclarationError` moved from line 154 to 162, exactly the operand delta, and reproduced the
signature against a synthetic 8-line shift. The instrument's bias is safe in the reviewer's
direction: line-number leakage can only manufacture *false* differences, never mask a real one.

### Claim 3 — the guard is depth-complete; encode-token fragility — **CONFIRMED**; fragility ruled a **followup, not a finding**

Four mutations, all **new** (outside the g1–g3 spent set), all against the **shipped** file
(`#381` satisfied), all OID-confirmed, all restored in `finally:` to a matching OID, each
adjudicated by the **specific named assertion**, never by exit code.

| mutation | mutated blob OID | first failing assertion |
|---|---|---|
| M0 field returns to `run` | `a3a460e9a98ad0d486d1702df6ab95d6955292b8` | `assertNotIn("dirty", m["run"])` |
| M1 nested under `run.host` (depth 3 — all three flat checks blind) | `41f9a7237fa5fc53a2fcf6789d673db1a0b922ef` | `assertEqual(_dirty_key_paths(m), [])` → `['/run/host/dirty']` |
| M2 nested in a `files` **list** row | `35ae21565bf1351bd300bdd6df29365336bf579e` | `assertEqual(_dirty_key_paths(m), [])` → `['/files/0/dirty']` |
| M3 token as a **value**, not a key | `43c4ae38ce4cc115333cf12f186b05609e0030f6` | `assertNotIn("dirty", cm.encode(m))` |

Depth-completeness is now **measured** in both the dict branch (M1) and the list branch (M2), not
claimed.

**M3 decides the fragility question, and it decides it in the encode-check's favour.**
`_dirty_key_paths` returned `[]` for M3 — the structural sweep is blind to a value-shaped
re-introduction by construction, since it matches keys only — and the *only* assertion that fired
was the encoded-token one. The two layers are **genuinely complementary**, not belt-and-braces
redundancy.

Ruling: the check *is* value-sensitive; that is one property, not two — it is exactly what makes it
useful and exactly what makes it trippable. But (a) the failure direction is a false **red**, loud
and safe, never a false green; (b) the fixture is fully controlled (`work_id` `"w-1"`, tempdir
roots); (c) the implementer's trip came from hand-choosing a `work_id` containing the token, which
the shipped fixture does not do. **Narrowing the token to a JSON key form would destroy the M3
coverage, so narrowing is the wrong fix.** Followup: one warning line in the comment saying the
check matches values as well as keys.

### Claim 4 — suite baseline — **CONFIRMED**, independently derived

My own run, clean shipped tree, `python -m pytest tests/ -q`:

```
1487 passed, 2 skipped, 472 subtests passed in 131.68s (0:02:11)
```

Exact match on all three numbers. I also reproduced the **mechanism** behind the implementer's
471-vs-472 rather than accepting the explanation:
`RevIsGitBlobOid::test_rev_equals_git_rev_parse_head_for_tracked_clean_files` run alone against the
committed tree reports **`1 passed, 4 subtests passed`** — four, because all four `TARGETS` are now
clean. During g4-implement, `scripts/checklist_engine.py` was uncommitted-modified and dropped out
of the clean subset. The test measures cleanliness rather than assuming it. Not a regression.

### Claim 5 — the successor paragraph's parenthetical — **REFUTED** → BLOCKER-1

The manifest **is** identifiable, so the claim was checkable — and checking it refutes it.

- **Identity:** `.agent-work/issue-305/context/g1-implement.json`, `run.generated_at`
  `2026-08-02T03:00:53Z`, `run.dirty` `false`, `repo_rev.commit`
  `24561309a521a440fee9633436d8462d9cea9210`.
- **Not the run's first.** Ordering the eight manifests in `.agent-work/issue-305/context` by
  `run.generated_at` puts `g1-review.json` **first** at `02:52:37Z` with `dirty=true`;
  `g1-implement.json` is **second**. Git creation order agrees, independently of the timestamps
  inside the files: `git log --diff-filter=A` (**not** `--follow`, which lies through rename
  ancestry) shows `g1-review.json` created at `b1707f1` and `g1-implement.json` created **eight
  minutes later** at `bcb0975`, subject *"gate(#305): reopen g1 for the ruled packaging rework"*.
  Widening "the run" does not rescue it: the earliest manifest anywhere in the corpus is
  `.agent-work/issue-305/issue-305-g1-implement/context/m4-failsoft.json` at `02:16:39Z`,
  `dirty=true`, and **every one of the nine context directories' earliest manifest reads `true` or
  is field-absent.**
- **The cause is not "no predecessor."** The surviving file is a **reopen artifact**. Its
  `repo_rev.commit` `2456130` landed at `19:58:37-07:00` = `02:58:37Z`, **2m16s before** the
  manifest was generated at `03:00:53Z`; `bcb0975` committed it 51s after that. The tree read clean
  because a commit had just cleaned it.

**Separate observation on the same sentence (not the blocker).** The count is sound but is stated
as a live tree property with **no anchor**. My sweep of every `.agent-work` JSON carrying
`{contract, step, files, run}` finds **56** manifests at both `35d2686` and HEAD: **51 `true`, 1
`false`, 4 field-absent** — not 49/47/1/1. It reconciles exactly: the doc's 49 was measured at the
*start* of g4-implement, which then wrote 4 more pre-removal manifests (all `true`, 47+4=51) and 3
post-removal ones (field-absent, 1+3=4); 49+7=56. **Your commit message anchors the measurement
("at the point of removal"); the shipped doc does not.**

**Impact, stated plainly so you can weigh it:** neither finding touches the removal's correctness,
and the ruling the paragraph supports — *neither reliably constant nor informative* — is
**strengthened** by the truth. A flag that flips because an unrelated commit landed 136 seconds
earlier is even less usable than one that flips on a missing predecessor.

**Suggested fix (one clause):** delete the parenthetical, or replace it with *"which was generated
moments after commit `2456130` left the tree clean"*, and anchor the count — *"at the point of
removal, 49 manifests had been written: 47 `true`, 1 `false`, 1 field-absent."* If you anchor it in
the doc, anchor `scripts/context_manifest.py:34-36` too (see FU-3), or the two shipped statements
of the same measurement will disagree with each other.

---

## THE FOUR GATE CRITERIA

**1. Determinism boundary genuinely unchanged — PASS.** `CONTENT_KEYS` at
`scripts/context_manifest.py:120` is exactly `("contract", "step", "files", "repo_rev")`,
byte-identical to `35d2686^`. `RealCheckoutSkew`'s body has zero assertion changes, so I proved it
still bites rather than assuming it. **Control first, because a skip reads as green:** both tests
run alone with `-rs` against the unmutated shipped file genuinely *executed* — `1 passed in 5.86s`
and `1 passed, 6 subtests passed in 2.88s`, `SKIPPED` reasons **NONE**. Then two new mutations
against shipped blob `6ea9dcc`:

- **D1a** re-admit `dirty` into the content field `repo_rev` (mutated OID
  `11859983a1123f2583f3806d74654ed0b20dc593`) → **RED** on precisely the headline line
  `self.assertEqual(cm.content(m_clean), cm.content(m_dirty))`, with the failure diff showing
  `'dirty': False` against `'dirty': True` at identical commit `edceb405`. Demonstrated end-to-end
  over two real git worktrees, against what ships.
- **D1b** make `rows()` skip absent declared entries (mutated OID
  `41106bcdb17ced6a7df6622fa06cec77da802d18`) → **RED** on the row-shape assertion. The shape half
  is live too.

The test did **not** survive by no longer testing anything; it survived because it was only ever
asserting content's insensitivity to dirt, never the field's home.

**2. No test was weakened — PASS**, with one measured coverage gap (FU-2). I audited all eight
assertion removals individually. Six had their subject genuinely removed and were correctly
dropped; `test_content_is_unaffected_by_dirty_when_commit_is_equal` was **strengthened**, not
trimmed (whole-envelope insensitivity modulo `generated_at`). Two — the non-git-directory case and
the porcelain oracle — were asserting `repo_revision`'s behaviour *through* the manifest, and
`repo_revision` asserts them **directly** at `tests/test_checklist_engine.py:1075-1110` (oracle
equality `:1079`, exact shape `:1083`, non-git dir yields `{commit: None, dirty: None}` `:1088`,
real dirty worktree detected `:1096-1110`), all untouched and green. Testing the primitive at the
primitive is better than testing it through a consumer that no longer carries it. **The one real
gap is FU-2 below.**

**3. No docstring describes a field that does not exist — PASS.** I swept **every** occurrence of
the token in shipped code, not just the nine rewritten sites, and read each in context:
`context_manifest.py` 14, `checklist_engine.py` 10, `test_context_manifest.py` 33,
`test_context_determinism.py` 16, `test_checklist_engine.py` 11, `CHECKLIST_ENGINE_DESIGN.md` 8,
`global-orchestrator.md` 1, `test_episode_negative_control.py` 2, `test_episode_store.py` 1. Every
surviving mention describes either the edge's still-true `{commit, dirty}` shape, or the removal in
the past tense with its issue reference, or per-file dirtiness derivable from content. The three
non-manifest files are unrelated (an episode-shortcut sentence; a local variable; prose about dirty
input).

**Confirmed as invited, and not fixed:** `docs/CHECKLIST_ENGINE_DESIGN.md:187` omits `repo_rev`
from the stated return shape. That is stale from **#300 g5**, when `repo_rev` was *added* to
content; #327 removed a field from `run` and never touched that shape's naming. **Unrelated,
correctly out of scope.**

**4. The forbidden claim did not ship — PASS.** I swept independently with a wider net than
"permanently": `permanent|self-caus|self caus|always (true|dirty)|never (false|clean)|
unconditionally|invariabl|tautolog|by construction (true|dirty)|trivially true|vacuously` across
`scripts/`, `tests/`, `docs/`, `skills/`, intersected with lines mentioning `dirty` — **zero hits**.
The unfiltered "permanent" hits in shipped dirs are all unrelated to the field. The only
`own side effect` occurrence in shipped code is `scripts/context_manifest.py:34`, and it is the
**correct negation** — *"it never reads its own side effect but its predecessor's."* The claim
remains in the frozen `g4-implement` imperative in `.agent-work/issue-305/execute.json` (one
`self-caused` occurrence) and in older `.agent-work/` artifacts: historical record, correctly left
alone.

---

## EVIDENCE — reproduced at its source, never accepted on the report

The real-produced-manifest acceptance is met **twice over**.

**From the tree:** I swept all 56 real manifests on disk with my own recursive key sweep. The
cut-over is visible in the historical record itself — `m3-remove-green.json` (16:47:21Z) still
carries `/run/dirty`; `m4-prose.json` (16:50:22Z), `m5-real-manifest.json` (16:55:11Z) and
`m6-suite-and-result.json` (16:56:55Z) carry **no `dirty` key at any depth**, with `run` exactly
`['generated_at','host','roots','work_id']`. 52 of 56 carry the key; **all 52 are pre-removal, zero
post-removal manifests carry it.**

**Live, by me, against the shipped tree — stronger:** `cm.produce()` with the real
`default_repo_state` (a real `git` subprocess), real roots, a real on-disk checklist, declaring two
real repo files:

```
top keys : ['contract', 'files', 'repo_rev', 'run', 'step']
run keys : ['generated_at', 'host', 'roots', 'work_id']
dirty key paths at ANY depth: []
token 'dirty' anywhere in the WRITTEN bytes: False
what the edge itself still returns: {'commit': 'edceb405...', 'dirty': True}
```

The edge handed the consumer a live `True` and the consumer provably dropped it — **both halves of
the design claim in one measurement.** The probe's rows also returned `rev` `6ea9dccb` for
`scripts/context_manifest.py` and `9e4da4d3` for `docs/CHECKLIST_ENGINE_DESIGN.md`, matching my
baseline blob OIDs exactly. It wrote to a system temp dir, not the repo.

**#381 discipline:** the implementer red-proved its guard against blob `77604fd`, a revision that
does not ship. I did not accept it. I re-proved the guard red **four** ways against the shipped
blob, plus two more against `RealCheckoutSkew`.

---

## FOWLER REFACTORING PASS

`scripts/verify_fowler_pass.py` exits 0: *smells=12, flagged=[duplicated-code, shotgun-surgery,
speculative-generality], overridden=[data-clumps, comments-as-deodorant]*. All twelve visited.
Both overrides cite standards that **genuinely exist in this worktree** (there is no
`CREW_CONTEXT.md` and no `GLOSSARY.md` here). Seven absent, and the change is net-**subtractive** on
four of them.

- **duplicated-code — flagged.** `_dirty_key_paths` (`:229`) is the *second* hand-rolled recursive
  dict/list walker over the manifest in the same file; `assert_json_native` (`:1092`) is the first,
  identical skeleton, different terminal predicate. An AST scan of all of `scripts/` and `tests/`
  finds only five self-recursive dict+list functions repo-wide — two are in this file.
- **shotgun-surgery — flagged, and it is the root cause of BLOCKER-1.** Removing one boolean rewrote
  the same rationale at **seven** prose sites across five files; this is the field's *second* move
  touching the same scattered set. The cost is not hypothetical: the 49-manifest measurement now
  exists in **two shipped copies with no single source, and they already disagree.**
- **speculative-generality — flagged, deliberately not overridden.** `repo_revision` keeps a half
  nobody consumes, justified in shipped prose by a hypothetical *"second caller."*
  `global-everyone.md`'s own rule — *"one adapter = a hypothetical seam; two = a real one"* — makes
  that a guess, and I **ran** its deletion test: deleting the `dirty` half of `default_repo_state`'s
  early return leaves the full suite green. I flagged rather than overrode because **no documented
  standard sanctions it — the documented standards lean the other way**, and "out of scope for this
  gate" is a scoping fact, not a standard. Not a defect of this change; routed to the primitive's
  owner.
- **data-clumps — overridden** (Universal posture *"no speculative abstraction"* + the ruled
  out-of-scope status of `repo_revision`). Scoped: this override covers the **clump**, and I
  explicitly did not let it swallow the unused-half question, which is flagged above.
- **comments-as-deodorant — overridden** (the g4-implement handoff's ruled requirement that the
  prose record the removal, plus *"keep context docs current"*). The tombstones are not compensating
  for unclear code — the code is three deletions and reads fine without them. Scoped to their
  **existence**, not their multiplicity, which is charged under shotgun-surgery.

---

## FOLLOWUPS (none blocking)

- **FU-1** — `test_dirty_appears_nowhere_in_the_manifest`: add one line to the comment above
  `assertNotIn("dirty", cm.encode(m))` warning that it matches **values** as well as keys. **Do not
  narrow the token** — M3 proves the value-matching behaviour is the only layer catching a
  value-shaped re-introduction.
- **FU-2** — `scripts/context_manifest.py:326`, `default_repo_state`'s no-repo-root early return
  `{"commit": None, "dirty": None}`: **the `dirty` half now has no test.** Measured, not suspected —
  deleting it leaves the full suite green (`1487 passed, 2 skipped, 472 subtests`, zero failures;
  mutated blob `446fc1e86091188e3db680c5612a3f16fdbfdc68`). A surviving mutant. The module docstring
  explicitly justifies returning both halves; that decision should have a test. One assertion fixes
  it: `cm.default_repo_state({"skill": ...}) == {"commit": None, "dirty": None}`.
- **FU-3** — `scripts/context_manifest.py:34-36` restates the 49-manifest measurement in the same
  unanchored present tense as the design doc. Anchor both, or state it once and point at it.
- **FU-4** — Fowler duplicated-code: one walker yielding `(path, value)` pairs that both callers
  filter.
- **FU-5** — Fowler shotgun-surgery: single-source the measurement.
- **FU-6** — Fowler speculative-generality: for the owner of `checklist_engine.repo_revision` —
  either produce the second caller or shrink the primitive; don't leave the hypothesis in shipped
  prose as if settled. *(The engine-recorded text of this triage candidate contains a stray
  character in "find/建 the second caller"; the intended wording is "find the second caller or
  shrink the primitive.")*
- **Already filed, confirmed unrelated, correctly not fixed:** `CHECKLIST_ENGINE_DESIGN.md:187`
  (stale since #300 g5); **#382** (aliased-import AST defeat, one-element `artifact-ref` fixture) —
  referenced, not touched, not counted against this gate.
- **Noted, not counted:** `scripts/context_manifest.py:92` says the source *"never contains the
  literal identifier `subprocess`"* and it contains it five times — but all five are prose, the
  guard is AST-level, and the count is **5 at `35d2686^` and 5 at `35d2686`**, so this commit
  neither introduced nor worsened it. Same sentence-vs-machinery family as #382.

---

## MUTATIONS RUN (all new; all against the SHIPPED blob; all restored)

Base for every mutation of `scripts/context_manifest.py`: shipped blob
`6ea9dccbab245c8d549a832cb6792cd18ff84d3c`.

| # | mutation | mutated blob OID | outcome |
|---|---|---|---|
| M0 | field merged back into `run` | `a3a460e9a98ad0d486d1702df6ab95d6955292b8` | RED — `assertNotIn("dirty", m["run"])` |
| M1 | `dirty` nested under `run.host` | `41f9a7237fa5fc53a2fcf6789d673db1a0b922ef` | RED — `_dirty_key_paths` → `['/run/host/dirty']` |
| M2 | `dirty` inside a `files` list row | `35ae21565bf1351bd300bdd6df29365336bf579e` | RED — `_dirty_key_paths` → `['/files/0/dirty']` |
| M3 | token as a **value** (`host.platform = "dirty"`) | `43c4ae38ce4cc115333cf12f186b05609e0030f6` | RED — `assertNotIn("dirty", cm.encode(m))` **only**; sweep returned `[]` |
| D1a | `dirty` re-admitted into content `repo_rev` | `11859983a1123f2583f3806d74654ed0b20dc593` | RED — `assertEqual(cm.content(m_clean), cm.content(m_dirty))` |
| D1b | `rows()` skips absent entries | `41106bcdb17ced6a7df6622fa06cec77da802d18` | RED — row-shape assertion |
| D2 | delete `"dirty": None` from `default_repo_state`'s early return | `446fc1e86091188e3db680c5612a3f16fdbfdc68` | **GREEN — full suite `1487 passed, 2 skipped, 472 subtests`, zero failures. A surviving mutant → FU-2.** |

Method held throughout: EOL derived per base (**every worktree file is 100% CRLF — 453 newlines,
453 CRLF, zero bare LF in `context_manifest.py`; `git show HEAD:` returns 23737 bytes with 453 LF
and zero CRLF**), mutations applied to the CRLF worktree bytes in binary, every mutation confirmed
by blob-OID **change** and every restore by blob-OID **match**, every restore inside a `finally:`,
tree OID-checked after **every** battery, and every red adjudicated by the **specific named
assertion** in the pytest source line — never by a non-zero exit.

---

## TREE RESTORATION CHECK

```
HEAD tree OID  = b2b5238d49a62d582b1fdff03ab98b7eedf45002   (identical to the pre-review baseline)
HEAD           = edceb405cc5bb072656ea8cf92eb1d11509cc9c0   (unchanged — I committed nothing)
git status --porcelain --untracked-files=no  ->  EMPTY
```

All five touched source blobs re-hashed and **MATCH** baseline: `context_manifest.py` `6ea9dcc`,
`test_context_manifest.py` `43b39bb`, `test_context_determinism.py` `3a21311`,
`checklist_engine.py` `23ba703`, `CHECKLIST_ENGINE_DESIGN.md` `9e4da4d`.

Only untracked path: `.agent-work/issue-305/g4-review/` — my survey, its journal, and the Fowler
record, under the issue workbench where reviewer doctrine puts them, not at the worktree root. No
commit, no tag, no branch, no push. The human's main checkout `C:/Programs/constellation-skills` is
untouched, still at `b69e6c8` with exactly the WIP it started with.

---

## WORKFLOW FEEDBACK

- **The handoff was the best I have worked from on this epic**, and two things in it did specific
  work: pre-classifying the four claims as *yours* versus *the implementer's, unchecked by me* told
  me exactly where to spend effort, and the spent-mutation list stopped me re-running work and
  reporting it as fresh. The rule *"a repeat is only spent under the same conditions"* is the right
  shape — I used it to justify M0 as new against the shipped base.
- **Gap: the handoff never states the Survey State Location.** The reviewer skill says the handoff
  gives it (`.agent-work/<work-id>/<gate>-review/review.json`); this one does not. I improvised
  `.agent-work/issue-305/g4-review/review.json` by matching the g1–g3 convention. That worked, but
  a fresh reviewer with no prior gates to imitate would have to guess.
- **Gap: no `docs/agents/engine-config.json` exists**, yet the survey template's `config_ref`
  points at it and the g3 survey carries the same dangling reference. Harmless today; it will
  mislead the first person who goes looking.
- **The `--session-id` ergonomics cost me two refusals.** `current` **rejects** `--session-id`
  while every mutating verb **requires** it once a lease is claimed, so the natural
  `record && current` chain breaks. Minor, but it is the kind of thing that eats a turn.
- **`advance` is not a survey verb** — it refuses with *"advance is for gated checklists; use
  record"*. Correct behaviour, but the reviewer SKILL.md tells you to *"`advance` that check"* and
  to *"run the engine's final `advance`/`consolidate`"*, which is gated-checklist vocabulary. A
  reviewer following the skill literally will hit that refusal. Worth fixing in the skill, not the
  engine.
- **Shell hazard worth recording:** backticks inside a `--finding` string are command-substituted by
  bash and silently delete the quoted word. It ate the word `assert` from my c1 finding. Findings
  should be written without backticks, or passed via a file.

---

# Rework 1 verdict — SUPERSEDES the BLOCK above

**BLOCKER-1 (the only blocker in this document) is DISCHARGED** by `f6acc1e` + `5ccae87`.

**Rework verdict: `APPROVE-WITH-FOLLOWUPS`.**

Full rework result — the five attacked claims, the atom-by-atom verification, the counts table
showing `35d2686^` reproduces 49/47/1/1 exactly, the re-wrap word-identity proof, the rework Fowler
pass, and three remaining followups — is in:

**`.agent-work/issue-305/crew/g4-review-rework-result.md`**

Do not act on the `BLOCK` verdict at the top of this file without reading that one first. Everything
else in this document — claims 1-4 CONFIRMED, the four gate criteria, the evidence reproduction, the
round-1 Fowler pass, and followups FU-1 through FU-6 — stands unchanged and is not superseded.

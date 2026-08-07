# REVIEW_RESULT — issue #440, gate g1 (binding cwd / validated candidate-root resolution)

## Verdict: APPROVE

With one major observation filed as a triage candidate. Nothing here requires rework by the
implementer; the one substantive residual is a design decision the Commander/Admiral owns and which
the gate's own decision anchor already schedules for settlement at g2.

Survey driven through the engine at `.agent-work/issue-440-binding-cwd/crew/g1-review/review.json`
(session lease `rev-440-g1`), all 11 checks visited (`r0-r6` plus appended `r4a-r4d`), consolidated
`verdict=APPROVE`. Fowler pass at `crew/g1-review/FOWLER_PASS.json`, rail exit 0.

---

## The four attack questions

### Q1 — Can the new tests actually fail? YES, and for the right reason.

I reproduced RED myself rather than reading the implementer's account.

```
cp scripts/hooks/spine_rail.py <scratchpad>/spine_rail.NEW.bak      # backup, sha256 recorded
git show cbd9aee:scripts/hooks/spine_rail.py > scripts/hooks/spine_rail.py
grep -c "looks_like_checklist\|resolve_spine_candidate\|git_worktree_roots" scripts/hooks/spine_rail.py   # -> 0
git diff --numstat                                                   # -> hook absent, tests 614/0
python -m pytest tests/test_spine_rail.py -q --no-header -p no:cacheprovider
```

**I asserted the mutation actually applied before trusting the arm** (new symbols grep count `0`, hook
gone from `numstat`) — per CREW_CONTEXT, a mutation that silently didn't apply leaves a green suite
that reads exactly like a passing guard.

Result: **`24 failed, 78 passed in 2.67s`, exit 1.**

The decisive one, `test_post_claim_rung4_real_git_worktree_resolved_in_a_fresh_subprocess`, failed
with:

```
E  AssertionError: bound '...\test_post_claim_rung4_real_git0\main\.agent-work\run-wt\spine.json',
                   not the worktree spine '...\test_post_claim_rung4_real_git0\wt-epic418\.agent-work\run-wt\spine.json'
```

That is **the defect itself** — the binding naming the main-checkout path — not an `ImportError` and
not a missing symbol.

Failure-reason census, derived from a command rather than eyeballed from the pytest tail:

| reason | count |
|---|---|
| `AssertionError` on a bound path | 13 |
| `AttributeError` (module has no such symbol) | 7 |
| `KeyError: 'path_source'` | 3 |
| `AssertionError` on entry-dict shape | 1 |

The 7 `AttributeError`s are the direct unit tests of the new helpers, where a missing symbol is the
only failure a pre-change tree can produce — legitimate, not padding.

**No test hand-injects the root it claims the hook derives.** The rung-4 test uses a real `git init`
+ `git worktree add` on disk and runs the hook in a **fresh subprocess**
(`subprocess.run([sys.executable, _MODULE_PATH, "PostToolUse"])`), and it *asserts* the non-injection
rather than merely narrating it (`tests/test_spine_rail.py:1894-1898`):

```python
assert str(wt) not in json.dumps(payload)
assert "cd " not in payload["tool_input"]["command"]
assert "--worktree" not in payload["tool_input"]["command"]
leaks = [k for k, v in env.items() if isinstance(v, str) and str(wt) in v]
assert leaks == [], "worktree path leaked into env: %r" % leaks
```

This is the `#432` / `#446` can't-fail-test family answered properly.

**Four of the 28 new tests pass in both arms** — `..._removes_its_own_entry_after_the_spine_file_is_deleted`,
`..._recorded_lookup_ignores_a_different_relative_suffix`, `..._still_clears_the_nudge_ledger`,
`..._never_raises_on_junk`. I read all four: each asserts an **invariant that must survive the
change**, and none claims to prove newly-derived behaviour. Correctly-shaped regression guards, not
fake proofs.

**GREEN**: `python -m pytest tests/test_spine_rail.py tests/test_gauge_writer.py -q` → **`169 passed`,
exit 0**. Test count 74 → 102 confirmed via `grep -c "^def test_"` on both revisions.

**Tree restored and proven**: `sha256 29683ad8a5adc05a3015fcb3eb414c3d54ecff22d8fd4b70840f4d3101647355`
matches the pre-swap hash exactly; `git diff --numstat` back to `281/13` + `614/0`; `git diff --cached`
empty; no commit made.

### Q2 — Can "first validating candidate wins" pick the WRONG root? YES, in one narrow case.

I constructed the adversarial case on disk (`<scratchpad>/attack_q2.py`) — real `git init` + real
`git worktree add`, the real hook in a fresh subprocess, nothing monkeypatched, no root injected.

| case | setup | bound | `path_source` | verdict |
|---|---|---|---|---|
| **A** | **both** trees hold a **real** checklist at the same relative path | **main checkout** | `payload_cwd` | **wrong — rung 3 beat rung 4** |
| B | main holds a non-checklist phantom (the old bug's leftovers) | worktree | `git_worktree` | correct, decoy rejected |
| C | two worktrees both hold a real checklist at that path | first in git's listing | `git_worktree` | arbitrary, no ambiguity signal |

**Case A is the original defect, unfixed for that sub-case** — and it records a *confident* wrong path
labelled `payload_cwd`, which the task statement says must never happen.

Its reach is not theoretical: `.agent-work/` is **tracked** (`git ls-files .agent-work` → 3069 files;
**281** of the tracked `.json` files pass `looks_like_checklist`), so committed checklists sit at
identical relative paths in main *and* in every worktree branched from it.

It does **not** reach the current live configuration: main's `.agent-work/issue-440-binding-cwd/`
holds only `gauge-skip.json`, which is correctly rejected. And the **measured** defect — the 60/64
phantom-decoy entries — **is** fixed, which Case B demonstrates.

What "validates as a checklist" tests (Case D of the same probe): a readable JSON **object** with a
top-level **`items` list**. `gauge.json`-shaped leftovers, `items` as dict/string, top-level lists,
malformed JSON, missing files and directories are all rejected. `{"items": []}` and
`{"items": [...], "not": "a checklist"}` do pass — deliberate and documented in the docstring as the
weakest test that positively identifies a checklist; harmless, since a non-checklist file at exactly
`.agent-work/<work_id>/spine.json` is not a shape this hook meets.

**Internal inconsistency worth the Commander's attention**: `resolve_recorded_release_target`
explicitly *refuses to guess* on ambiguity ("Exactly one match wins. Two matches is genuine
ambiguity … guessing between them would delete a live agent's binding"), while the claim ladder
guesses freely on exactly the same condition. The module applies opposite doctrine on its two paths.

### Q3 — Can any new code path raise, block, or hang inside PostToolUse? No, on every reachable path.

Verified independently (`<scratchpad>/attack_q3.py`, `q3_tail.py`), with **23 hostile payload shapes
deliberately different from the implementer's own fuzz rows**: non-string `cwd` (list/dict/bytes),
`session_id` `None`/int, 200×`../`, `CON`/`NUL` as `--file`, embedded NUL bytes, a 5000-char `cd`
target, a dead UNC path, the MSYS drive root `/c`, unicode paths. **All returned `{}`; zero raises;
zero slow paths.**

- **Bounded**: `GIT_PROBE_TIMEOUT_SECONDS = 2.0`. Non-repo dir → `[]` in 0.028s; nonexistent cwd →
  `[]` in 0.001s.
- **Both handlers confirmed**: `TimeoutExpired` → `[]`, `OSError` → `[]`, and `MemoryError` → `[]`
  (the bare `except Exception` absorbs the rest).
- **Off the common path, proven by spying on `subprocess.run`**: after a rung-3 claim, `calls == []`;
  after a rung-0 absolute claim, `calls == []`; **only** the unresolvable claim spawned
  `['git','worktree','list','--porcelain']`.
- **Bind-nothing confirmed**: after the unresolvable claim, the store held no key for that session.

One observation, unreachable: `looks_like_checklist("CON")` — a **bare** Windows reserved device name
— **blocks forever** on `open()`, so the module's "NEVER raises" contract hides a "can still block"
hole. Not reachable from the hook: `resolve_spine_candidate` always joins a relative `--file` onto a
base and `.resolve()`s it first, and a joined `C:\dir\CON` raises `FileNotFoundError` → `False`; rung
0 returns absolute paths without validating at all. Verified case-by-case (`probe_con.py`): bare hung
at the 15s cap, while `joined`, `--file CON`, `--file NUL` and `--file sub/CON` all returned promptly.

### Q4 — Were 14 existing tests weakened? No. Mechanically provable.

```
git diff --numstat   ->   scripts/hooks/spine_rail.py 281/13
                          tests/test_spine_rail.py    614/0     <-- ZERO deletions
grep -c '^-' <tests diff>  ->  1   (the '--- a/tests/...' header alone)
```

**Zero assertions changed, zero cases deleted, zero test bodies rewritten.** The 15 hunks touching
pre-existing tests are pure *insertions* of `put_checklist(...)` calls plus a comment.

`put_checklist` is **new** (absent from `git show cbd9aee:tests/test_spine_rail.py`) and genuinely
writes to disk (`tests/test_spine_rail.py:1495-1502`):

```python
p.write_text(_checklist_json(work), encoding="utf-8")
```

So the fixtures were **strengthened** — they now create the real spine files they previously only
pretended to have — which is the direction that makes those tests *harder* to pass, not easier. The
RED arm confirms it: with fixtures strengthened but the hook reverted, 24 tests failed; a weakened
suite could not do that.

---

## Findings

| # | Severity | File:line | Finding |
|---|---|---|---|
| 1 | **Major (observation + decision candidate, tc1)** | `scripts/hooks/spine_rail.py:552-565` (rung ordering) | Rung 3 (`payload_cwd`) is tried before rung 4 (`git_worktree`), so when both main and the worktree hold a real checklist at the same relative path, a worktree agent binds **main's** spine and labels it `payload_cwd`. Reproducible (`attack_q2.py` Case A). Not a regression, does not reach the live configuration, and the ladder is explicitly graded a guess pending g2. |
| 2 | Low (observation) | `scripts/hooks/spine_rail.py:50-73` (`looks_like_checklist`) | Can **block forever** on a bare Windows device name (`"CON"`). Unreachable from the hook, but the docstring's "NEVER raises" contract does not cover "never blocks". |
| 3 | Low (observation) | `scripts/hooks/spine_rail.py:552-556` (rung 1) | `--worktree` rung is **dead in production**: `checklist_engine.py:2404` defaults `--worktree` to `"."`, and rung 1 deliberately skips relative forms. The live ladder is really rungs 2-5. |
| 4 | Low (observation) | `scripts/hooks/spine_rail.py` `handle_post_tool_use` | 104 lines / 72 code lines; the `claim` and `release` bodies are each an extractable unit. Note the change *improved* this (the ladder was extracted into named helpers), adding only +8 code lines. |
| 5 | Low (observation) | `scripts/hooks/spine_rail.py:228-229` | `resolve_spine_candidate(file_val, data, project_dir, tokens, command)` — 5 params, three of which are redundant views of one payload (`tokens` = `_tokenize(command)`, `file_val` = `_extract_opt(tokens,...)`, only `cwd` read from `data`). A small value object would make an inconsistent `tokens`/`command` pair impossible. |

**No blockers.**

## Close criteria

| criterion | status |
|---|---|
| Worktree agent's relative `--file` binds the worktree's spine | **Met** for the measured/decoy case; **not** for the both-trees-hold-a-real-checklist sub-case (finding 1) |
| Rung 4 proven against a real `git worktree`, fresh subprocess, no injected root | Met — and non-injection is asserted in-test |
| No candidate validates → nothing written, store byte-unchanged | Met |
| `release` removes its own entry, incl. after the spine file is deleted | Met |
| `handle_post_tool_use` returns `{}` on every path, never raises | Met (23 independent hostile shapes) |
| Git probe off the common path and bounded | Met (`subprocess.run` spy + 2.0s) |
| `169 passed`; no existing assertion weakened | Met (0 deletions) |

## Scope and exclusions — each verified, not taken on trust

`git diff --name-only cbd9aee` = exactly `scripts/hooks/spine_rail.py` + `tests/test_spine_rail.py`.

- Binding **key** shape / `binding_key()` — untouched. `binding_key` and `BINDING_KEY_SEP` appear in
  the diff only inside one *comment* line; no `+`/`-` on their definitions.
- `scripts/hooks/gauge_writer_hook.py`, `scripts/checklist_engine.py`, `docs/GAUGE_WRITER_HOOK.md`,
  `tests/test_gauge_writer.py` — all clean under `git status --short`. The permitted
  `test_gauge_writer.py` reconciliation was indeed not needed.
- Nothing touching `#269`, and none of the three other documented known limits, was changed.
- The live main checkout's `.agent-work/.spine-rail-binding.json` and every real `.claude/settings*.json`
  were **never written** by this review — all probes ran in `tempfile.mkdtemp()` trees with
  `CLAUDE_PROJECT_DIR` overridden. I read the live store's directory listing only.
- Wiring claim reproduced: `_resolve_abs` has **zero** occurrences repo-wide; all 7 new symbols and
  all 6 `PATH_SOURCE_*` constants have ≥1 production reference. No dead code.

## Out of scope, for the Commander's triage (kept separate from findings)

- **tc1 — claim-side ambiguity detection.** When more than one candidate root validates,
  `resolve_spine_candidate` silently takes the first, while `resolve_recorded_release_target` already
  refuses to guess on exactly that condition. Consider applying the same fail-closed doctrine on
  claim, or emitting an ambiguity marker into `path_source` so the gauge writer can decline.
- `.agent-work/` being **tracked** is what gives finding 1 its reach (281 committed checklists at
  identical relative paths in every tree). Worth naming explicitly in whatever settles the ladder at
  g2 — it is a property of the repo layout, not of this hook.
- `docs/GAUGE_WRITER_HOOK.md` still states this defect as live. Per the handoff this staleness is
  **not** a finding for me; noting only that it is still pending at a later gate.

## Workflow feedback

- **The handoff was unusually good**, and specifically the part that helped most was naming the
  can't-fail-test family (`#432`, `#446`) *with issue numbers* and telling me exactly which test was
  load-bearing. That turned Q1 from "read the tests and form an impression" into a reproducible
  experiment. More handoffs should name the prior failures they are afraid of repeating.
- **One real friction**: the handoff says the implementer "reseeded fixtures for 14 pre-existing
  tests," which primed me to expect deletions in the test diff. There are **zero**. The fixture work
  was done purely by insertion, and 15 hunks (not 14) touch pre-existing tests. The claim was true in
  spirit but the count and the mechanism were both slightly off, and a reviewer chasing "which
  assertion moved" burns time before discovering `numstat` answers it in one command. Suggest
  handoffs state fixture claims as `git diff --numstat` output rather than prose counts.
- **A caution I hit myself, worth passing on**: while probing, I wrote a guard to confirm a patch had
  applied and it returned a **false positive** (my `split(']')[0]` truncated at an earlier `[]` in the
  same line), which sent me chasing a phantom second hang for two rounds. Exactly the failure mode
  CREW_CONTEXT warns about. It cost me time but changed no conclusion — every substantive result here
  was re-derived in isolation afterwards.
- Minor environment note: the reviewer skill's bundled engine and the repo's own vendored
  `scripts/checklist_engine.py` both exist and nothing in the Skill invocation flags which governs. I
  drove the installed skill's copy deliberately, to keep the review off the branch's own machinery.

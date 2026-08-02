# IMPLEMENTER_RESULT — g1 rework (packaging), issue #305 / #362

**Status:** complete. Full suite green. No blockers.
**Worktree:** `C:/Programs/constellation-skills-wt/e298-305` (isolation verified, exit 0). Main checkout `C:/Programs/constellation-skills` never touched — its `git status --short` is byte-identical to the session-start snapshot (`SKILL_INDEX.md`, `scripts/install_constellation.py`, `tests/test_write_a_skill.py` modified; `docs/agents/`, `skills/clean-codebase/` untracked).

## Files changed

| File | Deliverable |
|---|---|
| `scripts/install_constellation.py` | 1 — dependency closure |
| `tests/test_install_constellation.py` | 2 — the detector |
| `scripts/checklist_engine.py` | 3 — false rationale (×2, see below) |

---

## Deliverable 2 — the detector (the actual deliverable)

### What was wrong with the old guard

`test_engine_dynamic_loads_are_declared_as_companions` parsed one regex:

```python
siblings = set(re.findall(r'parent\s*/\s*"([A-Za-z0-9_]+\.py)"', engine_src))
```

That sees exactly one reach mechanism — the `Path(__file__).parent / "x.py"` dynamic load. It cannot see `sys.path.insert(0, <own parent>)` + a plain `from episode_capture import ...`, and it cannot see a deferred import written inside a function body. Both of those are real in this tree, and both were on the #305 path.

### What replaced it

Two module-level helpers in `tests/test_install_constellation.py`:

- `_direct_runtime_siblings(module_path, scripts_root)` — union of (a) the original `parent / "x.py"` regex and (b) an **AST walk** collecting every `ast.Import` / absolute `ast.ImportFrom` root name, at any nesting depth (so function-local deferred imports count). A name survives only if `scripts/<name>.py` actually exists on disk — that one test is what separates a co-located sibling from stdlib/third-party without a hand-kept denylist that could rot.
- `engine_runtime_closure(entry, scripts_root)` — BFS over the above, **transitive**, cycle-safe, minus the entry itself. Transitive because the shipping unit is the closure, not the first hop: `episode_capture.py` alone still crashes on a tree without `agent_work_root.py`. Cycle-safe because `context_manifest` imports `checklist_engine` right back.

**Not overfitted to `episode_capture`.** Neither helper mentions that string, or any module name. The name `episode_capture.py` appears only in the expectation set `ENGINE_RUNTIME_SIBLINGS` (which the handoff required move deliberately) and in prose. Add any new sidecar by either mechanism and the detector reports it with no test edit.

I verified the traced closure independently rather than trusting the handoff. Derived, not asserted:

```
checklist_engine.py -> ['agent_work_root.py', 'context_manifest.py', 'episode_capture.py', 'gauge_reader.py']
engine direct:           ['episode_capture.py', 'gauge_reader.py']
episode_capture direct:  ['agent_work_root.py', 'context_manifest.py']
context_manifest direct: ['checklist_engine.py']
agent_work_root direct:  []
gauge_reader direct:     []
```

Matches the handoff's traced set exactly.

### RED PROOF #1 — detector vs. the pre-fix installer

Run with `tests/` already carrying the new detector and `scripts/install_constellation.py` **un-edited** (still `("gauge_reader.py",)`), before deliverable 1 existed:

```
=== installer dict is still PRE-FIX ===
88:SCRIPT_RUNTIME_COMPANIONS: dict[str, tuple[str, ...]] = {
89:    # checklist_engine._load_gauge_reader() -> Path(__file__).parent/"gauge_reader.py"
90:    "checklist_engine.py": ("gauge_reader.py",),
...
=== RED RUN ===
        declared = set(installer.SCRIPT_RUNTIME_COMPANIONS.get("checklist_engine.py", ()))
        undeclared = reachable - declared
>       self.assertEqual(
            set(), undeclared,
            ...
        )
E       AssertionError: Items in the second set but not the first:
E       'context_manifest.py'
E       'episode_capture.py'
E       'agent_work_root.py' : checklist_engine.py imports ['agent_work_root.py', 'context_manifest.py', 'episode_capture.py'] at runtime but SCRIPT_RUNTIME_COMPANIONS['checklist_engine.py'] does not declare them -- every skill bundling the engine installs a tree where that import fails, and the engine's ImportError fallback makes the feature no-op SILENTLY

tests\test_install_constellation.py:1271: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_install_constellation.py::RuntimeCompanionBundleTests::test_engine_runtime_siblings_are_declared_as_companions
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 97 deselected in 0.26s
```

It goes red **naming `episode_capture.py`** (and its two transitive deps).

### RED PROOF #2 — the end-to-end binding check vs. the pre-fix installer

I added `test_installed_engine_binds_the_real_capture_seam_not_the_fallback` (mirrors the existing gauge-reader end-to-end test). It really installs `implementer` — chosen deliberately because its bundle is `("checklist_engine.py",)` **alone**, so every companion must arrive through `expand_script_bundle()` — then loads the *installed* engine and asserts which function it bound.

Reverted the installer to HEAD (pre-fix) with the new tests in place:

```
=== reverted to PRE-FIX (HEAD) ===
90:    "checklist_engine.py": ("gauge_reader.py",),
=== RED RUN (full class, pre-fix installer + new tests) ===
            try:
                mod = load_module("installed_engine_305", scripts_dir / "checklist_engine.py")
>               self.assertEqual(
                    "episode_capture", mod.emit_step_manifest.__module__,
                    "installed engine fell back to the no-op emit_step_manifest -- "
                    "the #305 capture seam would be inert in this install",
                )
E               AssertionError: 'episode_capture' != 'installed_engine_305'
E               - episode_capture
E               + installed_engine_305
E                : installed engine fell back to the no-op emit_step_manifest -- the #305 capture seam would be inert in this install
=========================== short test summary info ===========================
FAILED tests/test_install_constellation.py::RuntimeCompanionBundleTests::test_engine_runtime_siblings_are_declared_as_companions
FAILED tests/test_install_constellation.py::RuntimeCompanionBundleTests::test_installed_engine_binds_the_real_capture_seam_not_the_fallback
2 failed, 3 passed, 97 deselected, 11 subtests passed in 0.57s
```

`'installed_engine_305'` is the fallback's `__module__` — this is the silent no-op caught in the act on a real installed tree. Restored the fixed installer immediately after; verified by re-grep.

**Note on why proof #2 matters separately from #1.** In the pre-fix run the file-presence subtests all *passed*, because they iterate the declared companion tuple, which pre-fix was just `gauge_reader.py`. A dict-derived check structurally cannot catch an *un*declared dependency. Only the binding check can. The two guards fail for different reasons and neither subsumes the other.

The test also pops `episode_capture` / `agent_work_root` / `context_manifest` from `sys.modules` (restoring in `finally`) before loading the installed engine, and asserts the bound `episode_capture.__file__` resolves **inside the temp install dir** — otherwise a stale repo-side module in `sys.modules` would have greened it on a broken install.

### GREEN

```
5 passed, 97 deselected, 44 subtests passed in 0.53s
```

---

## Deliverable 1 — the dependency closure

`SCRIPT_RUNTIME_COMPANIONS["checklist_engine.py"]` is now `("gauge_reader.py", "episode_capture.py", "agent_work_root.py", "context_manifest.py")`, with a comment recording *why* the guard was blind. **Additive only** — `gauge_reader.py` keeps its position, no other key touched, and the `"clean-codebase"` lines uncommitted in the main checkout are on different lines of different dicts. Full diff of that file is 1 changed entry + comment; pasted below in "Diff summary".

Verified **through `expand_script_bundle()`**, not by eyeballing the dict:

```
admiral          missing=none
lessons-auditor  missing=none
charter          missing=none
commander        missing=none
workbench        missing=none
interrogator     missing=none
cartographer     missing=none
implementer      missing=none
reviewer         missing=none
explorer         missing=none
```

All ten engine-carrying skills, all four companions. `agent_work_root.py` was previously hand-listed in only `admiral` and `commander`; the other eight now get it via expansion, and `expand_script_bundle`'s de-dup means the two hand-listed ones are unaffected.

The existing companion test was **generalized, not renamed-only**: `test_every_skill_bundling_the_engine_also_gets_its_runtime_companions` now iterates the declared companion tuple × every engine-carrying skill (44 subtests, was 10), and separately still pins `gauge_reader.py` by name so the #256 guarantee cannot be quietly dissolved into the generalization.

`test_expansion_preserves_order_and_does_not_duplicate` needed one change: it hard-coded `("checklist_engine.py", "gauge_reader.py")` as the expected expansion, so it failed on a dict change it has no opinion about. Rewritten to derive from the dict and assert the *mechanism* (no duplicate, explicit entries keep position, companions follow their owner, no-companion script passes through). This is a strengthening — it now also asserts order for the companion-listed-first case, which the literal form never covered.

## Deliverable 3 — comments carrying a false rationale

**(a) `reopen()`'s emit call** — the required fix. Rewritten to state the true reason: `reopen` refuses anything not `complete`; a complete gate necessarily passed `start`, which already wrote this step's manifest; `emit_step_manifest` is write-if-absent. So it is a **backfill**, a no-op on every reachable path in a post-#305 spine, earning its keep only for a spine predating the seam. The placement rationale (AFTER the mutation, so `active_id()` picks the right step) was correct and is kept. The comment explicitly notes the prior version was wrong.

I verified the write-if-absent claim in source rather than taking it from the handoff — `scripts/episode_capture.py`:

```python
        if destination.exists():
            return destination
        return cm.write_manifest(manifest, destination)
```

**(b) The engine's import-site comment — found, not assigned.** `scripts/checklist_engine.py` lines 27–31 read *"the sidecar is NOT bundled into every engine-carrying skill (install_constellation.SKILL_SCRIPT_BUNDLES), so its absence degrades to a no-op"*. After deliverable 1 that is the exact opposite of the truth, **and it names the wrong dict** (`SKILL_SCRIPT_BUNDLES`, not `SCRIPT_RUNTIME_COMPANIONS`). Worse, it framed the fallback as the normal installed case — which is the attitude that let the seam stay inert everywhere. Rewritten to say the closure does ship, that the fallback covers a genuinely partial tree only and is not the expected path, and that a test now asserts the real binding. I judged this in scope: it is the same defect class as (a), sitting three lines from the change, and leaving it would have been a guaranteed review finding.

## Close criteria

| Criterion | Disposition |
|---|---|
| All three sidecars ship with every engine-carrying skill, verified through `expand_script_bundle()` | MET — table above, 10/10 skills, plus a real install of `implementer` |
| Extended detector goes red on the pre-fix tree and green after; show both | MET — two independent RED proofs pasted above, green after |
| Existing companion test still passes, generalization real not name-only | MET — iterates the declared tuple (10 → 44 subtests) and still pins `gauge_reader.py` by name |
| `reopen`'s comment states the true reason | MET — plus a second false-rationale comment found and fixed at the import site |
| Full suite green | MET — `1436 passed, 2 skipped, 471 subtests passed in 66.09s` |

## Constraint compliance

- **Additive only** — no existing bundle entry changed meaning; `gauge_reader.py` keeps position 0.
- **Main checkout untouched** — verified by `git -C C:/Programs/constellation-skills status --short` (unchanged from session start).
- **`episode_capture.py` seam logic, emit sites, `tests/test_episode_capture.py`** — all unmodified. `git status --short` shows only the three files above (plus `.agent-work/issue-305/crew-runs.json`, which is engine bookkeeping I did not author).
- **Windows/encoding** — all edits via the Edit tool; no new file-writing code. Verified the three edited files are still valid UTF-8 with unchanged line-ending convention. No `Path.read_text(newline=...)` introduced (the new detector uses plain `read_text(encoding="utf-8")`).
- **Interpreter** — `python -m pytest` (3.14.3 / pytest 9.0.2) throughout. `py` used only for the throwaway closure prototype, which imports nothing from pytest.

## Diff summary

`scripts/install_constellation.py` — one entry widened + rationale comment.
`scripts/checklist_engine.py` — two comments rewritten, **zero executable lines changed**.
`tests/test_install_constellation.py` — `import ast`; two new module-level helpers; detector test rewritten and renamed `test_engine_dynamic_loads_are_declared_as_companions` → `test_engine_runtime_siblings_are_declared_as_companions` (the old name described a mechanism that is now only half of what it checks); companion test generalized and renamed; expansion test de-literalized; one new end-to-end test.

## Blockers

None.

## Triage candidates (out of scope, not filed)

1. **`gauge_writer_hook.py` has no closure guard.** The new `engine_runtime_closure()` is applied only to `checklist_engine.py`. The other companion-owning script gets the same protection for roughly four lines (its source lives in `scripts/hooks/`, so it needs a different `scripts_root`, which is already a parameter). Deliberately not done — the handoff scoped this to the engine and the installer is live under other commanders.
2. **The detector still lives in the test file, not the installer.** `expand_script_bundle()` could *derive* companions from the closure instead of being checked against it, which would make the dict unforgettable rather than merely guarded. That is a design change with real blast radius on a shared file; guarding was the right size for a rework.
3. **The `try/except ImportError` fallback is now provably not the installed path.** Whether it should survive at all — versus failing loudly on a partial tree — is a doctrine question above this tier.

## Workflow Feedback

**The handoff was unusually good and I want to be specific about why**, because it is reusable: it named the defect, named the mechanism *not* to reinvent, pre-traced the dependency closure **and told me to verify rather than trust it**, and stated the red proof as an acceptance condition rather than a suggestion. The instruction "design the detector so that it fails on the pre-fix tree" is what produced the two RED proofs; without it I would plausibly have written a detector that only ever ran green. That sentence should be standard in any handoff whose deliverable is a guard.

Friction, honestly:

1. **The dispatch instruction and the skill contradict each other, hard.** `constellation-implementer` opens with "the moment this skill loads — before you read the handoff closely — instantiate a gated plan and CLAIM the engine lease… a run that solves the task directly has **failed this dispatch** no matter how correct the answer." My dispatch says the opposite in bold: "There is **no gated plan file for this rework**… Do not instantiate a new plan checklist." I followed the dispatch (the launching agent owns scope, and the parent gate is tracked in `execute.json`), but the skill's language is absolute and gives an implementer no sanctioned way to comply with a parent that overrides it. Either the skill needs an explicit "unless your dispatch says otherwise, in which case say so in your result" carve-out, or Commander should not be overriding it. This will keep costing every rework dispatch a decision.
2. **Deliverable 3 was under-scoped by one comment.** The handoff named `reopen()`'s comment. The import-site comment eleven lines from the top of the same file was *more* wrong — it asserted the sidecar is not bundled and named the wrong dict — and deliverable 1 is what made it false. A handoff that assigns "fix this false comment" should ask whether the fix invalidates any *other* comment; here it did, deterministically. I fixed it and flagged it rather than leaving a review finding on the floor.
3. **One collateral test failure was foreseeable and unmentioned.** `test_expansion_preserves_order_and_does_not_duplicate` hard-codes the expected expansion tuple, so *any* companion addition breaks it. The handoff listed the companion test that must still pass but not this one. Cheap to fix, but it is exactly the kind of "the dict is pinned in three places" fact a pre-traced handoff could have carried.
4. **No note that `agent_work_root.py` is already hand-listed in two bundles.** The handoff says it "is already in the `admiral` and `commander` bundles", which is what let me predict de-dup would handle it — good. What was not stated is that `expand_script_bundle()` de-dups by name regardless of order, so the hand-listed entries stay put and the additive constraint is satisfied for free. I verified it rather than assuming.

## Map Impact

Small but real, in the packaging seam rather than in behavior.

- **Constraint (new, durable):** *a script bundled into a skill must ship its entire transitive runtime closure, across both reach mechanisms — path load and `sys.path` + plain import.* Previously the constraint was one-hop and one-mechanism, and the gap was invisible.
- **Capability (extended):** `install_constellation.expand_script_bundle()` is now the single choke point through which the #305 capture seam reaches all ten engine-carrying skills. Anything reasoning about "what ships with the engine" must read `SCRIPT_RUNTIME_COMPANIONS`, not `SKILL_SCRIPT_BUNDLES`.
- **Dependency edge (newly visible, not new):** `checklist_engine.py → episode_capture.py → {agent_work_root.py, context_manifest.py → checklist_engine.py}`. The cycle is real and deliberate, broken by a deferred import; any map of scripts/ that shows only top-of-file imports will miss the `context_manifest` edge entirely.
- **Decision recorded:** the `try/except ImportError` fallback in `checklist_engine.py` is now explicitly documented as the partial-tree path, not the installed path — with a test that pins the distinction. That reclassification is the durable part; the dict edit is not.

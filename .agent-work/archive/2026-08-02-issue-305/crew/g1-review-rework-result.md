# Review Result

## Assigned Gate
`g1-review` — issue #305, epic #298. Re-review after the packaging rework (commit `0201a52`).

## Result
`APPROVE`

Survey: `.agent-work/issue-305/g1-review-rework/review.json` — 14/14 checks visited and recorded pass, consolidated `verdict=APPROVE findings=0`, 2 triage candidates. Fowler record: `.agent-work/issue-305/g1-review-rework/fowler-pass.json` (rail exit 0).

---

## My independent mutation — the assignment

The brief was explicit: reproducing the implementer's red proves nothing new; devise a mutation they did not ship, and find out whether the detector is a parser or a hardcoded assertion in parser's clothing.

I built an isolated full copy of the tree (scratchpad, never the live worktree) and confirmed the companion tests green there first.

**Mutation A — two sidecars that have never existed, undeclared.**

- Created `scripts/rev305_probe.py` and `scripts/rev305_probe_deep.py` — brand-new modules, not the three the implementer shipped.
- Reached `rev305_probe` from `agent_work_root.py` (**hop 2**) via a `from … import …` nested inside `def` → `for` → `try` → `with`.
- Reached `rev305_probe_deep` from `rev305_probe.py` (**hop 3** — deeper than anything in the real tree, whose closure bottoms out at hop 2) via a plain `import` nested inside `def` → `class` → `method` → `try` → `if` → `with`.
- Declared neither in `SCRIPT_RUNTIME_COMPANIONS` nor in `ENGINE_RUNTIME_SIBLINGS`.

**Outcome: RED, naming both by name.**

```
AssertionError: Items in the second set but not the first:
'rev305_probe_deep.py'
'rev305_probe.py' : checklist_engine.py's runtime sibling closure changed; …
```

**Mutation A2 — the realistic bad fix.** A developer hits Mutation A's failure and "fixes" it the lazy way: widen `ENGINE_RUNTIME_SIBLINGS`, leave the dict alone. This is the path by which a guard silently dies.

**Outcome: still RED**, on the *second*, independent assertion:

```
AssertionError: … 'rev305_probe.py' 'rev305_probe_deep.py' : checklist_engine.py imports
['rev305_probe.py', 'rev305_probe_deep.py'] at runtime but
SCRIPT_RUNTIME_COMPANIONS['checklist_engine.py'] does not declare them …
```

**Verdict: the detector is genuinely falsifiable and is NOT overfitted.** It caught modules that did not exist when it was written, one hop deeper than the real tree exercises, at AST nesting depths the implementer never tested, and it holds on two independent lines of defense.

**Mutation B — the #256 regression.** Dropped `gauge_reader.py` from the companion tuple. **Three** tests go red: the closure/declared check, the explicit `assertIn("gauge_reader.py", companions)` name pin, and the *untouched* end-to-end `test_installed_engine_can_actually_load_its_gauge_reader`. The #256 guarantee is triple-guarded; de-literalization dissolved nothing.

---

## Per-criterion disposition

| # | Criterion | Disposition |
|---|---|---|
| 1 | Detector falsifiable / not overfitted | **PASS** — Mutations A + A2 above |
| 2 | `scripts/<name>.py` existence-filter hole | **PASS** with a documented latent gap |
| 3 | Closure transitive and cycle-safe | **PASS** |
| 4 | All ten engine-carrying skills get all four companions | **PASS** — via real install + fresh-process E2E |
| 5 | Anything weakened rather than generalized | **PASS** — all three rewrites strictly stronger |
| 6 | Additive-only | **PASS** |
| J1 | Second false comment fixed unassigned | **IN SCOPE** — omitting it would have been the defect |
| J2 | `gauge_writer_hook.py` left without a closure guard | **AGREE** with deferring; filed as triage |

### 1 — Falsifiable, not overfitted → PASS
See above. Not a repeat of the implementer's red.

### 2 — Existence filter → PASS, with a latent gap logged
I swept **16** import/reach forms through `_direct_runtime_siblings`.

- **All 8 AST forms SEEN**: plain `import`, aliased `import … as`, `from … import`, parenthesized from-import, function-local, class-body, inside `try/except`, dotted `import a.b`. The #362 mechanism is airtight.
- **5 MISSES, all in the pre-existing *regex* half** (unchanged by this diff, so not a regression): single-quoted `parent / 'x.py'`, `parent.joinpath("x.py")`, f-string paths, `importlib.import_module("name")`, `__import__("name")`.
- **A 6th miss**: package-directory imports — `from hooks import …` resolves to `hooks.py`, which is not a file, so it is dropped.
- **None is live today.** I grepped all four closure members: the only non-AST mechanism present anywhere is the single double-quoted `parent / "gauge_reader.py"` load, which *is* caught.
- **False-positive direction is clean**: 0 of 37 `scripts/*.py` names collide with `sys.stdlib_module_names`. And a collision would be a genuine runtime-shadowing hazard anyway, given `sys.path.insert(0, …)` — so flagging it would be correct, not noise.

Latent, not a defect in this diff. Filed as triage candidate `tc2`.

### 3 — Transitive and cycle-safe → PASS
The real cycle is confirmed at the source: `scripts/context_manifest.py:80` does `from checklist_engine import active_id, repo_revision`. The real closure resolves in 0.039 s to exactly the four expected modules.

I then constructed cycles the tree does not have: a **3-node non-entry cycle** (`cyc_a ↔ cyc_b`, `cyc_c → cyc_a`) hung off `agent_work_root`, and a **self-import**. Both terminated in ~0.04 s, with every cycle node reached and none missed. Transitivity to hop 3 was separately proven by Mutation A.

### 4 — All ten skills, real install → PASS
Ran `installer.main()` into a temp dest, then read the **filesystem**, not the dict. All 10 engine-carrying skills (admiral, cartographer, charter, commander, explorer, implementer, interrogator, lessons-auditor, reviewer, workbench) carry all 4 companions. Zero missing, zero duplicates. The 8 that previously lacked `agent_work_root.py` now have it; the 2 that hand-listed it (admiral, commander) have it **exactly once** — dedup works.

**Stronger than asked — the production proof.** I installed `implementer` *alone* (its bundle is exactly `("checklist_engine.py",)`, so every companion had to arrive via `expand_script_bundle()`), then ran the **installed** engine as a **separate process** with cwd **outside the repo**, on a fresh checklist. It wrote a real, populated manifest to `.agent-work/issue-999/context/a1.json` — `contract`, `step`, `files`, `repo_rev`, `run.roots` (skill/repo/durable), `run.host`. **#362 is fixed in the world, not merely in a test.** That is the claim the previous BLOCK rested on, and it is now independently reproduced at its source.

### 5 — Nothing weakened → PASS
All three rewrites are **strictly stronger**.

1. **Detector test.** Old: regex-set == literal, and set == declared. New: closure == literal, `closure − declared == ∅` (new), **and** closure == declared — the old bidirectional check is *preserved*, so over-declaration is still caught. The old regex survives verbatim inside `_direct_runtime_siblings` and is now applied to **every** closure member, not just the engine. The one delta is the `is_file()` filter, which can only drop a load naming a nonexistent file — i.e. an already-broken load.
2. **Companion test.** Old asserted `gauge_reader.py` in each engine skill's expansion. New asserts **every** companion in each, and `gauge_reader.py` is in that tuple — so the old assertion is fully subsumed — plus an explicit `assertIn("gauge_reader.py", companions)` name pin. `assertTrue(engine_skills, …)` retained.
3. **Order test.** Since `companions[0] == "gauge_reader.py"`, the old literal case `expand(("checklist_engine.py", "gauge_reader.py"))` is reproduced exactly, plus a new dedup-count assertion and a new companion-listed-**first** ordering case. The `docent_freshness.py` passthrough is unchanged.

De-literalization does make test 3 partly tautological w.r.t. the dict — which is precisely why the name pin in test 2 is load-bearing. Mutation B proves the pin is not decorative.

### 6 — Additive-only → PASS
Loaded the installer at `0201a52~1` and at `0201a52` side by side and compared programmatically. `SKILL_SCRIPT_BUNDLES` identical. Companion-dict keys identical; both values prefix-preserved (`gauge_writer_hook.py` untouched; `checklist_engine.py`: `("gauge_reader.py",)` → 4-tuple). **`gauge_reader.py` holds position 0.** Nothing lost from any bundle's expansion.

One benign ordering nuance worth stating plainly: in `admiral` and `commander`, `agent_work_root.py` was hand-listed **last** and is now deduped into its companion position (index 3), so it moved earlier. Bundle order only drives the `shutil.copy2` loop (`install_constellation.py:907-913`); no semantic dependency on order exists, and the on-disk result is identical (admiral 9 → 11 files, exactly the 2 genuinely new modules).

---

## The two self-reported judgment calls

### J1 — the second false comment: **IN SCOPE, and omitting it would have been the defect.**
The import-site comment did not merely become imprecise — the implementer's own Deliverable 1 made it **false**. Pre-change it asserted the sidecar is *not* bundled into every engine-carrying skill and treated the fallback as the normal installed case; after the dict widening that states the opposite of the truth. It also named the wrong dict (`SKILL_SCRIPT_BUNDLES`, when the mechanism is `SCRIPT_RUNTIME_COMPANIONS`) — wrong even *before* the change. Shipping D1 and leaving it would have minted a brand-new false rationale in the same file, one commit after the Admiral ruled that "a comment carrying a false rationale is a small instance of the same thing this whole float is about."

Risk is provably zero: I confirmed by **AST equality** (`ast.dump` identical) **and** comment-stripped token-stream equality that `checklist_engine.py`'s executable content is unchanged. The "zero executable lines changed" claim is verified, not accepted. The implementer flagged the extension rather than smuggling it. Correct call.

### J2 — `gauge_writer_hook.py`'s missing closure guard: **AGREE with deferring; the self-report is imprecise; file the follow-up.**
Precision first: the hook is **not** unguarded. `tests/test_install_constellation.py:1473` `test_gauge_writer_hook_dynamic_loads_are_declared_as_companions` exists and pins `spine_rail.py`. What it lacks is a *closure* guard — it is the verbatim pre-#362 regex-only, single-hop form, blind to exactly the mechanism this diff was built to catch.

Deferring is right on three grounds: (a) I verified the hook's actual runtime closure is empty beyond `spine_rail` — both `scripts/hooks/gauge_writer_hook.py` and `scripts/hooks/spine_rail.py` import stdlib only, so nothing is undeclared today; (b) it is outside the Admiral's ruling, which scoped this rework to `episode_capture` shipping; (c) the "~4 lines" estimate is optimistic — `engine_runtime_closure` resolves modules as `scripts_root/<name>` and does **not** honour `SCRIPT_SOURCE_SUBDIRS`, so a hook in `scripts/hooks/` importing from `scripts/` needs real resolver work, not a parameter swap.

---

## Handoff compliance
All three deliverables landed within scope. D1 (closure) verified by real install; D2 (detector — the actual deliverable) verified by independent mutation; D3 (comment) verified by AST equality. Every close criterion in the implementer handoff is met. Full suite reproduced green.

## Scope drift
None. The commit touches exactly 5 files. `scripts/episode_capture.py` and `tests/test_episode_capture.py` confirmed **untouched** (`git show --name-only`). The main checkout `C:/Programs/constellation-skills` was inspected read-only and not modified; its uncommitted work is 2 added lines creating **new** `"clean-codebase"` keys in `SKILL_SCRIPT_BUNDLES` and `SKILL_REFERENCE_BUNDLES` — a different dict and different lines from the `SCRIPT_RUNTIME_COMPANIONS` value edited here. No conflict, nothing un-inspectable. One scope extension (J1), ruled in-scope.

## Evidence verdict
Reproduced independently, not accepted on report. Full suite: **1436 passed, 2 skipped, 472 subtests** (73.96 s). The handoff reports 471 subtests; I count 472 — identical pass/fail, non-blocking, noted only for accuracy. Beyond the implementer's red, evidence rests on my own novel mutations (A, A2, B) and the fresh-process production E2E.

## Code/doc quality
Fowler pass run over the full diff: 12/12 baseline smells rendered, `verify_fowler_pass.py` exit 0. `flagged`: `duplicated-code`. `overridden` with logged standard + reason: `primitive-obsession` (installer's public contract is filename strings; handoff forbids a second mechanism), `shotgun-surgery` (the dual dict/expectation update *is* the guard — proven load-bearing by Mutation A2), `speculative-generality` (a second call site is already identified, and Mutation A shows the generality is exercised, not decorative), `comments-as-deodorant` (the comments record a silent failure mode the code provably cannot express — that invisibility is what cost #362).

The one flag: the path-load regex now exists in two places, and the hook's copy is the known-blind pre-#362 form. Same item as J2.

## Map impact verdict
- **Evidence supports claimed change:** Yes. Each of the four Map Impact claims checked against the diff and reproduced.
- **Constraints not violated:** Yes. No new file-writing code; no `Path.read_text(newline=…)` introduced; additive-only holds; excluded files untouched; main checkout untouched.
- **Notes match the diff:** Yes. The closure/cycle edge `checklist_engine → episode_capture → {agent_work_root, context_manifest → checklist_engine}` is real and I confirmed it at the source. The reclassification of the `try/except ImportError` fallback as the *partial-tree* path rather than the installed path is genuinely test-pinned, not merely asserted in a comment.
- **Decision candidates surfaced:** Yes — both judgment calls were self-reported and escalated for ruling rather than decided silently.
- **Durable context routed:** Yes, plus two candidates I added below.

## Reconciliation check
No divergence requiring Commander reconciliation. No file under `docs/` references `episode_capture` or asserts the sidecar does not ship, so nothing recorded is now stale. The durable constraint worth carrying forward — *a bundled script must ship its entire transitive runtime closure, across both reach mechanisms* — is stated in the implementer's Map Impact and now enforced by a test rather than by memory.

## Blockers
- **None.**

## Out-of-scope observations
- **`tc1` — generalize the `gauge_writer_hook` companion guard** onto `engine_runtime_closure()`. It is still the verbatim pre-#362 regex-only single-hop form. Requires making module resolution `SCRIPT_SOURCE_SUBDIRS`-aware. Nothing is undeclared today, so this is prevention, not a fix.
- **`tc2` — detector blind spots, latent today.** The path-load half matches only a *double-quoted* `parent / "x.py"` (single quotes, `.joinpath()`, f-string paths all miss); string-based dynamic imports (`importlib.import_module`, `__import__`) and package-directory imports are invisible to the AST half. Either widen them or document them as an explicit non-goal, so the next sidecar author knows the boundary.
- **`tc3` — LIVE-OBSERVED, from this review's own run: the seam writes manifests to a DOUBLED work-id path.** `episode_capture.manifest_root()` returns the checklist directory's **parent**, documenting the assumption that "a run's checklist lives at `<agent-work>/<work-id>/spine.json`". But the `constellation-reviewer` skill — and this handoff — place the survey one level deeper, at `.agent-work/<work-id>/<gate>-review/review.json`. With `work_id="issue-305"` the root resolves to `.agent-work/issue-305`, so every manifest landed in **`.agent-work/issue-305/issue-305/context/`**. Reproduced on all 15 steps of this run. My control proves the mechanism: the E2E probe, whose checklist sat directly at `.agent-work/issue-999/probe.json`, wrote correctly to `.agent-work/issue-999/context/`.

  Two skills disagree about the work-area layout, and the seam absorbs the disagreement silently — it produces a nested duplicate rather than failing. **This is not a defect in the diff under review** (which is about *shipping* the seam, and shipping demonstrably works), and it does not change the verdict. But it is a real defect in either the seam's root resolution or the reviewer skill's documented survey path, it leaves confusing orphan directories for closeout, and — given that this epic is precisely about this seam — the Admiral should see it. Worth noting that the seam's 17 case/verb pairs and six mutants did not surface it, presumably because they all placed the checklist at the assumed depth.

- **Minor:** subtest count is 472 here vs the handoff's 471. Same pass/fail; worth a glance only if subtest counts are ever used as an evidence fingerprint.

## Workflow Feedback

- **Handoff gaps:** One concrete error. The handoff states *"`--session-id` is required on `record`/`start` but **rejected** by `consolidate`."* That is wrong — `consolidate` **requires** `--session-id` once a lease is claimed; omitting it fails with `REFUSED: checklist is owned by active session …`. I lost a cycle to it at the final step, which is the worst place to lose one. Also: the dispatch message and the handoff give **different survey paths** (`.agent-work/issue-305/crew/…` vs `.agent-work/issue-305/g1-review-rework/review.json`). I followed the handoff for the survey and the dispatch for the result, which appears correct, but the two documents should not disagree.
- **Context rediscovered:** (a) The handoff's J2 framing — "`gauge_writer_hook.py` still has **no** closure guard" — is inaccurate; a regex-form guard exists at `tests/test_install_constellation.py:1473`. I had to find that myself to rule on the call, and the imprecision pointed toward the wrong verdict. (b) Nothing in the handoff said `gauge_writer_hook.py` and `spine_rail.py` live under `scripts/hooks/`, not `scripts/` — that fact is what makes the "~4 lines" estimate wrong, and it is load-bearing for the J2 ruling.
- **Instructions improvised around:** The Fowler template asks for the record at `templates/FOWLER_PASS.template.json`; writing back to the installed skill's template would be wrong, so I instantiated it into the survey directory (`.agent-work/issue-305/g1-review-rework/fowler-pass.json`). The skill should say "instantiate from" rather than "record to." Separately, the reviewer skill directs the survey to `.agent-work/<work-id>/<gate>-review/review.json`, which conflicts with this handoff's explicit path; I followed the handoff.
- **What would have made this easier:** The single highest-value addition would be for the *implementer* handoff to require the red proof be demonstrated with a module **that does not exist in the tree**, not by reverting the shipped change. Reverting proves the assertion matches the current tree; only a novel module proves the detector parses. That distinction is the whole reason this gate was re-reviewed, and it belongs in the handoff template rather than in a reviewer's initiative.

## Return status
`complete`

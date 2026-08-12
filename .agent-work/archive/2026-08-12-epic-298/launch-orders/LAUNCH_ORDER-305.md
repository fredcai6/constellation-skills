# Launch Order: `commander-305 — issue #305, mechanical episode capture from engine state`

You start cold. Everything below is pasted, not pointed at.

## Mission

Issue #305 (spec B1): wire **mechanical episode capture** — work-id, role, active spine gate, refusals, reopens, rework counts, failed commands, artifact refs, and the context manifest — **captured with zero agent effort.**

That last clause is the whole issue. If capture requires the agent to remember to do something, it will be skipped somewhere and the store will be quietly incomplete in exactly the runs that went worst.

**Negative-control test REQUIRED**: a run where the agent records **nothing** must still yield the full mechanical field group. Cross-run retrieval exercised here with a **throwaway** synthetic consolidation over seeded episodes — mark a seeded cluster consolidated, confirm rhyme-search still finds its neighbours, then discard. The real first consolidation is #308 and is **not** a prerequisite.

Acceptance: negative control passes; cross-run retrieval demonstrated.

## You also inherit #300's unfinished wiring — this is the sharpest instruction in the order

#300 shipped the projection-manifest producer (`scripts/context_manifest.py`, `verify_context_declaration.py`, `tests/test_context_manifest.py`, all on `main`). **Nothing in production calls it.** `grep -rn "context_manifest" skills/` returns nothing — no engine call, no spine check, no CLI verb. Its acceptance criterion *"a manifest is produced on every deterministic assembly"* is therefore true **definitionally, over zero assemblies.**

That was correct scoping, not a gap: #300 built the substrate and **this issue wires it.** Stated as sharply as I can:

> **The manifest must become a byproduct of assembly, not a separate act an agent can forget to perform.**

If producing a manifest is something the capture path *calls*, it will be skipped somewhere. If it is something assembly *emits*, it cannot be. That distinction is exactly the difference between AC1 being true over zero assemblies and AC1 being true.

**First thing to verify once wired: that #300's acceptance test can now actually fail.** It could not before.

Public surface you are wiring, from `origin/main`: `rev()`, `read_bytes()`, `resolve()`, `declaration_of()`, `rows()`, `default_repo_state()`, `run_facts()`, `build_manifest()`, `content()`, `encode()`, `manifest_path()`, `write_manifest()`.

**Also drop `run.dirty` while you are in that file (#327).** It shipped in #300 (`b8e2aa0`) and was hollowed out three commits later by #326 (`c2e16a8`), which made `.agent-work/` tracked. The producer writes its manifest into `.agent-work/`, and `git status --porcelain` is repo-wide — so **producing a manifest dirties the tree, and the flag reads its own side effect.** Permanently true, self-caused. Removal, not repair: per-declared-file dirtiness is derivable from content alone (compare each row's `rev` against `git rev-parse <commit>:<path>`), which makes the manifest self-checking and the repo-wide flag redundant within its own scope. Close #327 with the removal.

Two of the Admiral's decisions collided to produce that defect — the dirty marker was suggested when relaying Tommy's doctrine-versioning ruling, and the un-ignore that emptied it was merged three commits later. Noted so it is not mistaken for a commander's error.

**Add a successor line to #300's shipped design doc** so a reader of `main` can tell deliberate sequencing from oversight: the producer had no caller until #305 wired it.

## Prior-Wave Verdicts (pasted)

**#301 — episode record + durable store. MERGED at `195e893`.** Verified on `origin/main`: `episodes/README.md`, `episodes/active/.gitkeep`, `episodes/retired/.gitkeep`. Genuinely in git, not nominally — a check the commander itself hardened. The `active/`/`retired/` split realizes Tommy's ruling that **retirement moves the file** rather than annotating in place.

**#300 — projection generator + manifest. MERGED at `b8e2aa0`.** Ships deterministic context recording with revision identity as the git blob OID of LF-normalised bytes computed in-process; the optional ordered declaration on the spine task; a lint pinning declaration against prose; and the `g5` doctrine-version gate.

**#302 — Tommy's two-bin ruling. No third bin; Assumption 6 stands; B0.3 unchanged.** *"Machinize the mechanizable. We don't need stochastic reasoning for predictable logic... these are aspirations."* The third-bin candidates were ruled **not catastrophic**, not *mechanizable*.

**Tommy's playbook ruling.** `.agent-work/LESSONS.md` is a dead end and #308 is retiring it: **episodes accumulate**, consolidation lands in repo-local `docs/agents/`, live agents read local + global doctrine only. **Your store is the accumulator that replaces it** — that is why this issue matters beyond its own acceptance criteria.

## The measurement finding that bears on this issue — and the correction that goes with it

#299's baseline measured **zero `Skill` invocations across five runs**; the #331 probe confirmed it robust under a second brief.

**Do not conclude your premise is unsound.** The Admiral briefly did, and Tommy corrected it: *"we should explicitly be calling commander in these tests."* **Zero-invocation is a property of the measurement rig, which launched generic agents — not of production, where a Commander run drives the engine by construction.** Capture-from-engine-state is sound. This paragraph exists only so you do not rediscover a scare that has already been resolved.

What *is* relevant: **an agent that never drives the engine leaves no engine state.** So your capture is complete for engine-driven runs and empty for everything else. Say so plainly in the record rather than letting a reader assume the store sees all work.

## Pre-Rulings

Overridable if evidence contradicts them — say so when overriding.

- decision:manifest-is-a-byproduct — assembly emits the manifest; nothing calls a "write the manifest" step.
  `@grade: settled/human · leans #305,#300`
- decision:episode-store-is-301s — write into `episodes/active/` as shipped. Do not design a second store.
  `@grade: settled/inherited · leans #305,#301`
- decision:zero-agent-effort-is-literal — if a field can be omitted by an agent forgetting, it is not mechanically captured. The negative control is the test of this, not a formality.
  `@grade: settled/human · leans #305 · settle: run the control before believing any field is mechanical`
- decision:throwaway-consolidation — the synthetic consolidation here is discarded. **A test artifact must never become canon.** The real one is #308.
  `@grade: settled/inherited · leans #305,#308`
- decision:drop-run-dirty — remove it, do not repair it. #327 closes with the removal.
  `@grade: settled/human · leans #305,#327`

## Two known defects that will bite this issue specifically

- **#321 — the episode store validates ids it LISTS but not ids it is HANDED.** You write episodes programmatically, which is exactly the unvalidated path. Fix it or work around it deliberately; say which and why.
- **#319 — episode working-tree bytes differ across worktrees under `core.autocrlf`.** Any comparison you make must use **normalized content or blob OIDs, never raw working-tree bytes.** The Admiral walked into this exact trap an hour after warning another issue about it.
- **#315 is worse than documented** (verified by commander-304): `_run_check_command` passes **no `cwd` at all** — `base_dir` is threaded into the `git-change-policy` branch but not the `command` branch. If you wire anything as a command postcondition, **a relative path resolves against an uncontrolled cwd.** Also: **stdout from a command postcondition is captured and discarded** — `_check_condition` records only `{cmd, exit, shell}`, so **the exit code is the only signal that reaches the spine.** Design any check as an exit-code vocabulary; a script that prints its result prints into a void.

## Honest-Null Clause

A measured negative is a complete, successful deliverable, reported with the same rigor as a win.

Applied here: **if the negative control fails — if a silent run does *not* yield the full mechanical field group — that is the issue's most valuable output**, not a failure of your run. It would mean "zero agent effort" is not achieved and would name exactly which fields are secretly agent-dependent. Report it, do not engineer around it quietly.

Scoped nulls: *"this field cannot be captured from engine state as currently structured"* — never *"mechanical capture is infeasible."*

## The methodology bar

**A check that cannot fail is indistinguishable from one that passed.** Four costumes in this epic already (#337): a vacuous test that survived two independent reviewer rounds; a losing condition mathematically bounded at 0; a mutation check whose `sed` silently did not match; and a verification that compared two empty strings and reported a match. The sharpened rule:

> **Prove you read both things, then compare.** Empty-vs-empty, missing-vs-missing and skipped-vs-skipped all pass a naive equality check.

Applied to you: **your negative control is the check most at risk.** Before trusting it, confirm it can *fail* — run it against a deliberately incomplete capture and verify it goes red rather than scoring green on absent fields.

## Inherited Latitude

**Delegated** — adjudicate and log: architecture/structural choices inside your deliverable; issue filing/closing on `fredcai6/constellation-skills` (`gh` pre-cleared — **file findings directly, never bank them worktree-locally**); fix-now triage; full test suite; `git push` to `epic-298/*`; **merge when green and reviewed, gated on the CI check exit code read at source — and confirm the status text reads `pass`, not merely that the command exited 0** (`gh pr checks` has been observed exiting 0 on a **pending** check); model tier for sub-dispatches within Budget.

**Must float** — do not decide: scope changes; **design-it-twice convergence on any load-bearing interface shape (human-only, always)**; production defaults or user-visible behavior; **two-bin routing rulings and pathway verdicts — Tommy's, always**; out-of-taxonomy, with one line on why.

## File Ownership

Working notes: **`notes-305.md`**. Sole writer. Never `findings-305.md` — the harness `Write` tool refuses any basename containing "findings."

## Workspace

Your worktree will be provisioned and its absolute path given at dispatch. **First command from inside it:** `py scripts/verify_worktree_isolation.py --here "<your worktree>"` — must exit 0; paste the output.

**Do not touch `C:/Programs/constellation-skills`** — it holds Tommy's uncommitted work. Other commanders are live in sibling worktrees; never enter one. Edit canonical `skills/_shared/global-*.md`, **never** the `skills/<role>/references/` copies that `install_constellation.py` regenerates.

## Inherited Context

**Python/CI:** `py` is 3.12.13 (matches CI's pin) but has **no pytest**; `python` is 3.14.3 with pytest 9.0.2. Run tests with `python -m pytest` (~1160 tests, 36s). **Neither interpreter reproduces CI** — a local green is never the gate. `Path.read_text(newline=...)` is 3.13+; it passed locally and failed CI on PR #320, costing 39 failures.

**Windows:** explicit `encoding='utf-8', newline='\n'` on every write (default is the ANSI codepage; this epic lost a JSON delta to `UnicodeDecodeError: byte 0x97`). MAX_PATH is real — paths over ~180 chars break `git worktree add` on windows-latest. PR bodies via `gh pr create -F <tempfile>`. **Backticks inside double-quoted shell strings are executed and silently drop words** — use `--body-file` for anything with code formatting; the Admiral did this today inside a warning about this exact hazard. Absolute paths for `git worktree add`.

**Engine:** never hand-edit spine/survey JSON. `--finding` text with backticks is shell-mangled and silently drops words. On a **survey**, `record` is the re-record verb; `advance`/`reopen` refuse as gated-only.

**Method:** *verify launch-order claims against the code* — **two of this Admiral's orders have already carried wrong claims, both caught downstream.** If something here does not match what you find, **the code wins, and say so in your return.** *Derive distribution claims from a command.* *A round-trip test proves the parser, not the artifact.* *A non-reading must be visibly distinct from an uncollected one.*

## Budget

- **Model tier (required): Opus.** Cold panel mandatory per B0.4 (`decision:review-class-floor` — not downgradable). Sub-dispatches at the least-powerful tier that works. **No Fable at any tier; name the model explicitly on every dispatch.**
- At most 3 concurrent sub-dispatches; other commanders are live on this machine. Rewrite your crash-resume state note before **each** detach.

## Stop Conditions

Stop and return when: scope would change; a design-it-twice convergence is ready; a two-bin or pathway question arises; the negative control fails (report, do not engineer around it); budget crossed; **or you need context this order does not cover — return-and-query me, I answer and continue you.**

Asking up is always sanctioned. This epic has one logged Admiral error where a commander's float went unanswered and it merged on its own reading; that failure was the Admiral's. The commanders that floated early and often were right every time.

## Return Shape

Deliver your artifact and verdict **before** going idle.

1. Verdict: capture wired, or honest null.
2. **Negative control result, plus evidence the control itself can fail.**
3. Cross-run retrieval demonstrated; the synthetic consolidation **discarded**, confirmed by normalized comparison or blob OID.
4. **Evidence that #300's acceptance test can now fail** — it could not before.
5. `run.dirty` removed; #327 closed.
6. Your disposition of #321.
7. Map impact; triage candidates filed, numbers listed.
8. Workflow feedback — blunt.
9. `verify_worktree_isolation.py --here` output.
10. **PR number, CI check exit code AND status text**, read at source.
11. **Branch status: FINAL, or PENDING with what is still coming** (#338 — a terminal spine and a released lease describe the *run*, not the *ref*).

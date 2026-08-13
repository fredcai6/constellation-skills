# PLAN_CRITIC — cold adversarial read of MISSION_FRAME.md + execute.json

Read: `MISSION_FRAME.md`, `execute.json`. Checked against `scripts/checklist_engine.py`,
`scripts/init_work_area.py`, `scripts/spine_lifecycle.py`, `scripts/verify_worktree_isolation.py`,
`scripts/mcp_spine_server.py`, `scripts/hooks/spine_rail.py`, `scripts/validate_spine.py`,
`skills/commander/templates/COMMANDER_SPINE.template.json`,
`tests/test_worktree_precondition_wiring.py`, `tests/test_explorer_templates.py`,
`docs/CHECKLIST_SCHEMA.md`, and the run's own `repro_native.py` / `PLAN_ALTERNATIVES.md`.
I ran the full suite, the tripwire suite, a validate_spine probe, and a
delete-init.c0 experiment (reverted).

No authoring context was given to me and none was inferred. Nothing below is triaged.

---

## CONFIRMED — verified against source

### 1. The guard's subject is the same ambient cwd the check it replaces already reads. `cd` disarms it in one token.
**Lands on:** MISSION_FRAME "Intent" (lines 28-31) and "Governing constraints" (lines 64-66);
execute.json `g1-implement` constraint 1.
**Verified:** `_run_check_command` (`scripts/checklist_engine.py:786-788`) calls
`subprocess.run([shell, "-c", command])` with **no `cwd=`**. So `verify_worktree_isolation.py
--here` already runs `git rev-parse --show-toplevel` from the engine process's own ambient
cwd (`scripts/verify_worktree_isolation.py:122-123`). The proposed guard reads
`Path.cwd()` — the *same* value, one indirection earlier.
**Why it matters:** the frame says the engine "delegates the judgment to a subprocess whose
subject is the ambient cwd" and that the fix makes the answer "stop being forwardable."
The new answer has an identical subject. An agent working in the main checkout satisfies the
guard by prefixing `cd <origin.worktree> &&` to the one engine call — and then does every
edit, every `git add`, every write back in the wrong tree. The guard proves *where one
subprocess was launched*, never *where the work happened*. Because the guard is now
always-on for every mutating verb, agents will learn the `cd` prefix as routine and the
check trends toward exactly the state this repo names: a check that cannot fail.
The genuine delta this change delivers is **coverage and unbypassability** (all mutating
verbs, not authored in the spine, cannot be deleted from a template) — not
non-forwardability. The frame does not say that, and a reviewer reading the frame will
certify a property the change does not deliver.
**Confidence:** high.

### 2. `heartbeat` and `release` are not read-only. The exemption carries a write.
**Lands on:** MISSION_FRAME line 48 ("`dispatch()` already separates read-only verbs
(`heartbeat`, `release`, `current`) from the mutating path") and line 100; execute.json
decision anchor `ruling verb-scope-is-mutating-plus-claim`.
**Verified:** `heartbeat()` (`checklist_engine.py:1048-1061`) writes
`lease["last_heartbeat"]`. `release()` (`:1063-1078`) writes `sess["status"] = "released"`
and `sess["released_at"]`. `main()` (`:3298-3345`) persists with `save(path, cl)` on **both**
the success and the `EngineError` path, gated only on `not args.dry_run and args.verb !=
"current"`. Only `current` is genuinely read-only.
**Why it matters:** after this change an engine standing in the main checkout can still
`release --force --reason X` a worktree spine's lease held by the agent that belongs there
(non-owner force is explicitly allowed at `:1071-1075`), and can keep a lease alive
indefinitely with `heartbeat`, defeating stale-lease reclaim. Both write the protected
file. The plan's own justification in `PLAN_ALTERNATIVES.md` ("Reading state from elsewhere
is supported; doing work elsewhere is not") is factually wrong for two of the three exempt
verbs. This is a hole that carries a write, exactly as suspected.
**Confidence:** high.

### 3. The guard's own refusal writes into the tree it is protecting.
**Lands on:** execute.json `g1-implement` (guard "called from one site at the top of
`dispatch()`"), raising `EngineError`.
**Verified:** `main()` loads the spine *before* `dispatch()`, and its `except EngineError`
branch runs `cl["refusals"] += 1` and `save(path, cl)` for every verb except `current`
(`checklist_engine.py:3299-3325`).
**Why it matters:** a guard whose entire purpose is "do not touch that other tree" performs
a filesystem write into that other tree every time it fires. Worse, the wrong-tree process
loaded `cl` at time T and writes it back at T+ε — if the legitimate engine in the correct
tree mutated the spine in between, the refusing process silently clobbers it (last-write-wins
on a single JSON file). To actually prevent the write, the check has to sit in `main()`
before `load()`/before the persist, or the refusal has to be marked non-persisting. Neither
artifact mentions this.
**Confidence:** high.

### 4. Child checklists never carry `origin`, so the guard is inert exactly where crew subagents work.
**Lands on:** execute.json constraint anchor `constraint:origin-less-fallback`; execute.json
`g1-implement` half one.
**Verified:** `instantiate_spine` writes one filename only — `dest = base / "spine.json"`
(`scripts/init_work_area.py:165`). Reviewer and implementer create their own checklists
elsewhere: `skills/reviewer/SKILL.md:26` instructs creating the survey at
`.agent-work/<work-id>/<gate>-review/review.json`; `skills/implementer/SKILL.md:15`
instantiates `IMPLEMENTER_PLAN.template.json`. Counting engine-drivable checklists
(objects with both `items` and `tasks`) under `.agent-work/archive`: **541 total**, of which
only 98 are named `spine.json` — 126 `review.json`, 49 `execute.json`, 16
`IMPLEMENTER_PLAN.json`, 15 `interrogation.json`, 14 `plan.json`, and a long tail.
**Why it matters:** the Commander's parent spine gets guarded; the child plan/survey that the
implementer and reviewer subagents actually drive gate-by-gate does not, and never will
under this design. That is the majority of the engine-driven surface and it is precisely
where a wrong-tree subagent does its editing. The plan does not name child checklists once.
**Confidence:** high.

### 5. `tests/test_explorer_templates.py` will go red, and it is not in the integrate gate.
**Lands on:** execute.json `g1-integrate` postcondition `c1` (its 6-file test list).
**Verified:** `tests/test_explorer_templates.py:342` calls
`instantiate_spine(root=<tmpdir>, ...)`, so the stamped `origin.worktree` will be the
tmpdir. Lines 356-360 then run the engine `claim` via `subprocess.run([...],
capture_output=True, text=True)` with **no `cwd=`** — cwd is the pytest runner's, i.e. the
repo root, not the tmpdir. `claim` is a guarded verb by ruling, so this refuses and
`self.assertEqual(claim.returncode, 0, claim.stderr)` fails. The `start` call two lines
later has the same shape.
**Why it matters:** this is a certain, mechanically predictable break in a file the
integrate gate never runs. The frame lists "No new failures against `main`'s own baseline
failure set" as a claim to re-confirm, but no postcondition runs the full suite — c1 runs
six named files, none of them this one. Also unrun and exposed for the same reason or by
the byte-shape change: `test_iterative_planning_doctrine.py`, `test_shipped_check_commands_resolve.py`,
`test_install_constellation.py`, `test_generate_spine.py`, and all eight `test_mcp_*.py` files.
**Confidence:** high on the break; high on the gate omission.

### 6. The two producers of `origin.worktree` emit incompatible value formats, and the plan never specifies normalization.
**Lands on:** execute.json `g1-implement` constraint 3 ("the stamp must be key-compatible
with `build_origin`'s block") and half two ("comparing the spine's `origin.worktree` against
the engine's OWN `Path.cwd()`").
**Verified:** `spine_lifecycle.py:311-312` passes `worktree=str(Path(worktree))` — **not
resolved, not posix**. The planned stamp uses `Path(root).resolve().as_posix()` (the shape
already at `init_work_area.py:148`). On Windows those are `C:\a\b` and `C:/a/b` for the same
directory; `Path.cwd()` yields the backslash form. `verify_worktree_isolation.normalize_path`
(`:47-52`, `normcase(realpath(p))`) is the repo's existing answer to exactly this and the
plan does not reuse it.
**Why it matters:** "key-compatible" is the wrong compatibility. One consumer now has to
accept two value formats. Get it wrong on Windows and either every mutating verb refuses on
every spine, or the comparison never matches and nothing ever refuses — and the second
failure mode is silent. This repo's whole worktree doctrine exists *because* of a Windows
no-op; shipping a Windows-untested path-equality comparison here is the same class of
mistake. `PLAN_ALTERNATIVES.md` reasons about symlinks and `normcase`; none of that reached
the frozen artifacts.
**Confidence:** high.

### 7. The chosen semantics in the frozen plan (`== Path.cwd()`) is a behaviour regression against the check it supersedes.
**Lands on:** execute.json `g1-implement` half two, literally "comparing the spine's
`origin.worktree` against the engine's OWN `Path.cwd()`".
**Verified:** `verify_worktree_isolation.check_here` compares `git rev-parse --show-toplevel`
against EXPECTED, so it succeeds from any subdirectory of the worktree. Exact equality
against `Path.cwd()` refuses from `<worktree>/.agent-work/<id>/` or `<worktree>/scripts/`.
`PLAN_ALTERNATIVES.md` names this and lands on `is_relative_to` containment — but neither
`execute.json` nor `MISSION_FRAME.md` says "containment", and `PLAN_ALTERNATIVES.md` is
cited by neither. The implementer is handed the equality wording.
**Why it matters:** an implementer following the frozen artifact literally ships a
false-refusing guard, and the c1/c2 gates would not catch it (the repro drives cwd = the
worktree root and cwd = the main checkout root only — never a subdirectory).
**Confidence:** high. See also finding 15 on the frozen plan under-specifying the design.

### 8. The `c2` gate's discriminator is a prose substring match — the named corollary defect, sitting in a postcondition.
**Lands on:** execute.json `g1-integrate` postcondition `c2`; evidence anchor
"case B ... must refuse after, FOR THE ISOLATION REASON".
**Verified:** `repro_native.py` decides the whole verdict with
`b_is_isolation = code_b != 0 and "worktree" in out_b.lower() and "lease" not in out_b.lower()`.
**Why it matters:** "assert against the behaviour, never against text describing the
behaviour" is the stated corollary and this is the load-bearing gate of the run. It is
brittle in both directions: a *correct* implementation whose refusal reads "refusing to
touch the lease from outside the work's worktree" reports `GATE ARMED: False`; an
*incorrect* implementation that refuses for an unrelated reason mentioning "worktree" (and
`claim` takes a literal `--worktree` argument) reports True. The behavioural facts are
available and unused: the refusal could carry a machine-readable marker, or the repro could
assert the spine file's `engine_session` is still absent after case B — a state fact, not a
sentence.
**Confidence:** high.

### 9. `c1` runs a test file the implementer authors, with no mechanical arming of its failing side.
**Lands on:** execute.json `g1-integrate` `c1` (`tests/test_engine_native_worktree_isolation.py`).
**Why it matters:** the file does not exist. `pytest -q` exits 0 if it contains one trivial
assertion. The only thing requiring a demonstrated failing side is prose — `g1-implement`
constraint 7 — plus the reviewer's judgment, plus `c2`, whose discriminator is finding 8.
Under this repo's own doctrine, a command check whose subject is authored by the party being
checked is the defect it names. Nothing in the plan mechanically arms the arm.
**Confidence:** high.

### 10. `validate_spine` gives `origin` no schema guard at all, and the plan's fallback shape is stated only as "no `origin`".
**Lands on:** MISSION_FRAME line 56 and lines 74/110-111; execute.json `g1-implement` half two.
**Verified by probe:** `validate_spine.validate()` returns an identical fault set for a spine
with no `origin`, a partial `origin`, a full `origin`, and `origin: "not-a-dict"`. The
denylist claim at frame line 56 is correct — and that is exactly the problem: nothing
validates the field the engine is about to make load-bearing.
**Why it matters:** the fallback is not exhaustive as written. Shapes that slip through and
get an unintended verdict: `origin` present but a string or list (`.get` raises
`AttributeError`, an uncaught traceback rather than a clean refusal — and `main()` only
catches `EngineError`); `origin: {}` or `origin: null`; `worktree` absent, empty string, or
non-string; `worktree` pointing at a path that no longer exists. The plan says only "a spine
with no `origin` falls back to today's behaviour" and leaves every one of those to the
implementer. `PLAN_ALTERNATIVES.md` enumerates them; the frozen artifact does not.
**Confidence:** high.

### 11. A stamped spine becomes permanently unclaimable once its worktree is removed.
**Lands on:** execute.json decision anchor `ruling backfill-none`; MISSION_FRAME "Out of scope".
**Verified:** `close_work` (`spine_lifecycle.py:365`) moves the work area into
`.agent-work/archive/` and commits it, so an archived spine ends up in the primary checkout
while its stored `origin.worktree` names a worktree that `git worktree remove` has deleted.
Repo history shows archived spines *are* driven later:
`f4a6a786 docs(handoff): 24 archived spines still hold an active engine lease`.
**Why it matters:** the exempt `release` happens to keep the "clear a stuck archived lease"
path working, but `claim --force` — the other half of that cleanup — is guarded and would
refuse from anywhere, forever, because the tree it demands no longer exists. `ruling
backfill-none` is safe only because no archived spine carries `origin` **today**; the change
creates the class going forward. Neither artifact mentions closeout, archive, or worktree
removal.
**Confidence:** high on the mechanism; medium on operational impact.

### 12. The merged tripwire is structurally blind to the regression this change creates.
**Lands on:** MISSION_FRAME lines 110-112 ("proven by the merged guard
`tests/test_worktree_precondition_wiring.py` staying green, since every fixture in it builds
an origin-less spine"); execute.json `g1-implement` constraint 6.
**Verified:** every fixture in that file builds a spine dict by hand with no `origin` key
(`:278-282`, `:362-378`). So the file will stay green *by construction* under this change —
it proves the origin-less fallback and nothing else.
**Why it matters:** the frame cites that greenness as positive evidence for the fallback.
That much is fair. But the same file's `IsolationGateSurvivesThroughTheCLI` docstring
(`:304-331`) exists specifically to catch "the comparison becomes `X == X` and the gate
unfailable", and it explicitly instructs: *"If such a contract HAS landed, this fixture is
what needs updating: it writes the bare `--here` form, so teach it the new form and keep both
sides asserted."* This change lands exactly such a contract. `g1-implement` constraint 6
instead freezes the file. Following the constraint disobeys the tripwire's own written
instruction and leaves the origin-carrying path — the new production path — with no
deliberate-breakage guard. That is weakening by omission.
**Confidence:** high.

### 13. `init.c0`: the vacuity reasoning is correct, but the cost is understated and the removal is now a multi-file job.
**Lands on:** MISSION_FRAME lines 102, 133; execute.json `g1-implement` constraint 5 and the
`decision pressure: whether init.c0 is deleted` anchor.
**Verified:** the check is
`python scripts/verify_worktree_isolation.py --here <repo-root>`
(`skills/commander/templates/COMMANDER_SPINE.template.json:12`). `<repo-root>` is substituted
from `Path(root).resolve().as_posix()` (`init_work_area.py:148`) — the same expression the
stamp will use. It is a *precondition of `init`*, evaluated by `start`, which is a guarded
verb; so it can only be reached after the guard already established that cwd is the stored
root. `git rev-parse --show-toplevel` from there is that root. **Vacuous — confirmed**, under
equality or containment semantics alike. (Strictly it can still fail on a missing/broken git;
"cannot fail for the isolation reason" is the accurate phrasing.)
**Verified cost, by experiment:** I deleted the c0 precondition from the real template and ran
the tripwire — exactly **3 of 7** red
(`EnumerationDeliberateBreakage::test_refuses_broken_copy_and_passes_real_fixed_tree`,
`EnumerationGeneralizesPastOneEntry::test_refuses_new_second_entry_without_naming_known_fixed_entry`,
`EnumerationGeneralizesPastOneEntry::test_passes_once_new_entry_carries_the_precondition`).
The frame's "3 of 7" measurement is accurate. Tree restored; `git status` unchanged.
**Why it matters:** the *cost of shipping it* is not stated anywhere. The vacuous check is
pinned in place by `scripts/verify_worktree_precondition_coverage.py` and three tests, so a
later deletion is a four-file change with a doctrine argument attached, not a one-line
delete. Meanwhile every Commander spine minted after this run carries a green check that
proves nothing, and the run ships it *knowingly* — into a repo whose named defect class is
"a check that cannot fail is indistinguishable from one that passed". If the Admiral does
not come back, the plan has manufactured an instance of the exact defect the epic exists to
eliminate. Floating the decision is defensible; shipping without at least a triage candidate
and a `waived`/annotated marker on the check is not.
**Confidence:** high.

### 14. `origin` is undocumented as a top-level key, and its only specification lives inside an archived work area.
**Lands on:** MISSION_FRAME "Declared reading" (cites `docs/CHECKLIST_SCHEMA.md`); execute.json
(no docs gate anywhere).
**Verified:** `docs/CHECKLIST_SCHEMA.md` "Storage model" (lines 63-82) enumerates the
top-level keys — `work_id`, `type`, `config_ref`, `items`, `tasks`, `consolidation`,
`triage_candidates`, `blockers`, `amendments`, `why_trail`, `trip_ledger`, `refusals`,
`engine_session`. No `origin`. The only `LIFECYCLE_CONTRACT.md` in the tree is
`.agent-work/archive/2026-08-12-epic-559-c3-lifecycle/LIFECYCLE_CONTRACT.md` — the document
`build_origin`'s docstring cites as the contract is an archived artifact, not a live doc.
**Why it matters:** the engine is about to refuse verbs based on a key whose shape is
specified nowhere a reader will look, and the plan has no documentation gate. Every other
optional top-level key in this file earned a documented section when it became load-bearing.
**Confidence:** high.

### 15. The frozen plan under-specifies relative to the design it chose, and does not cite it.
**Lands on:** `execute.json` in full; `MISSION_FRAME.md` in full.
**Verified:** `PLAN_ALTERNATIVES.md` records the converged design — pure
`origin_worktree_refusal(spine, *, cwd, verb)` returning refusal-or-None, `is_relative_to`
containment, segment-wise comparison, `normcase` inside / symlink resolution outside, an
explicit `WORKTREE_GUARDED_VERBS` set, an origin-less shape walk over
`{}`/`{"origin": None}`/`{"origin": {}}`/empty-string/non-string, a sibling-prefix test that
kills a naive `startswith`, and one wiring test that goes red if the call site is deleted.
**Not one of those appears in `execute.json` or `MISSION_FRAME.md`, and neither artifact
references `PLAN_ALTERNATIVES.md` at all** (no mention in the anchors, the imperative, the
constraints, or the frame's declared reading).
**Why it matters:** the implementer handoff is built from `execute.json`. Everything
load-bearing about the chosen design — containment, path normalization, the shape walk, the
wiring test — is invisible to it. Findings 6, 7 and 10 above are all "the design solved this
and the plan-of-record lost it". This is the single cheapest defect to fix in the plan.
**Confidence:** high.

### 16. Verb scoping as written is fail-open for future verbs.
**Lands on:** execute.json decision anchor `ruling verb-scope-is-mutating-plus-claim`;
MISSION_FRAME line 100.
**Verified:** `MUTATING_VERBS` (`checklist_engine.py:70-74`) already omits three verbs that
write canonical state — `claim`, `heartbeat`, `release` — as its own comment concedes. An
inclusion list built on it inherits that gap, and a verb added next year defaults to
unguarded.
**Why it matters:** stated as an exemption set (`{current, heartbeat, release}`, minus
whatever finding 2 forces) the default is deny; stated as `MUTATING_VERBS | {"claim"}` the
default is allow. The frame states it the fail-open way. `PLAN_ALTERNATIVES.md` names a
`WORKTREE_GUARDED_VERBS` constant, which is also the fail-open direction.
**Confidence:** high.

### 17. The MCP door breakage is called a "true positive" without evidence that it is one, and carries no gate.
**Lands on:** execute.json `g1-implement` `confidence_flags[0]`; MISSION_FRAME lines 96-100.
**Verified:** `mcp_spine_server.py:361` calls `checklist_engine.main(argv)` in-process;
`SPINE = Path(os.environ["SPINE_FILE"]).resolve()` at module scope (`:131`); no `chdir`
anywhere in that file. `.mcp.json` launches the server with no `cwd`, so its cwd is fixed at
whatever launched the session and cannot be changed per call.
`skills/workbench/references/checklist-engine.md:32` makes the door the **default**
interface, and `skills/implementer/SKILL.md:30` / `skills/reviewer/SKILL.md:26` tell
dispatched crews to drive their bound spine through it.
**Why it matters:** for any door whose server process cwd is not the spine's worktree, every
mutating verb refuses, permanently, with no `cd` available as a workaround. Whether that is
a true positive or a breakage of the documented default path is an empirical question about
how `SPINE_FILE`-bound servers are launched relative to their worktrees — and the plan
answers it by assertion. No `test_mcp_*.py` file appears in the `c1` gate. If it is a true
positive, the plan owes a migration note; if it is not, it is a production outage in the
default interface.
**Confidence:** high on the mechanism; the "true positive" characterization is unproven.

---

## PLAUSIBLE — reasoned, not fully verified

### 18. The guard cannot fail for the dominant CLI invocation shape.
Whenever the engine is invoked with a **relative** `--file` (e.g. `--file
.agent-work/<id>/spine.json`), the path only resolves if cwd is already inside the worktree —
so the guard passes by construction. Its discriminating power exists only for absolute
`--file` invocations. That is the dangerous case, so this is not fatal; but it means the
guard is structurally unfailable across a large share of real calls, and neither artifact
says so. Not measured across the skills corpus.

### 19. `instantiate_spine` switching to `json.dumps` output has a wider blast radius than "byte-preserving writer".
`PLAN_ALTERNATIVES.md` names the cost; nobody enumerated it. Beyond finding 5, candidates:
`json.dumps` defaults to `ensure_ascii=True`, so any non-ASCII in any spine template (em
dashes, arrows) is rewritten to `\uXXXX` escapes in every materialized spine — a permanent
diff-noise and readability regression across all shipped roles' spines, not just the
Commander's. Indentation and trailing-newline shape also change. I did not audit the
templates for non-ASCII. Cheap mitigation: `json.dumps(..., ensure_ascii=False, indent=2)`,
or do the stamp as a text-level insert. The plan specifies neither.

### 20. `<repo-root>` and `origin.worktree` are the same value computed twice, ten lines apart.
Both come from `Path(root).resolve()` in the same `resolve_spine`/`instantiate_spine` call.
The frame uses this identity (correctly) to falsify the forwarded-cwd fix. It also means the
run introduces a second copy of one fact into the same file with no invariant tying them
together — a future edit to either drifts silently. Neither artifact names the duplication.

---

## Lens verdicts

**Intent-fit.** The plan does not serve its stated point. It delivers coverage and
unbypassability, which are real, and it does *not* deliver "cannot be disarmed by a child
process's cwd" — the engine is the child process, and `cd` is the disarm (finding 1). The
deeper tension it never names: the two candidate subjects are `Path.cwd()` (independent of
the spine, but ambient and forwardable) and `Path(args.file).resolve()` (unforgeable, but a
tautology since the spine file lives in its own worktree by construction). The plan picks
the first and describes it as if it had the properties of the second.

**Testability / falsifiability.** Three things in this plan would report green while doing
nothing: `c1`'s implementer-authored test file (finding 9), the merged tripwire under the
new contract (finding 12), and `init.c0` for every origin-carrying spine (finding 13). The
one mechanical arm that *is* present, `c2`, decides its verdict with a prose substring match
(finding 8). Nothing in the gate structure would catch a guard that never fires.

**Simplicity / YAGNI.** The largest deletable thing is **half one**. If the engine derived
the expected tree from the spine file's own git toplevel and compared it to the *cwd's* git
toplevel — two independent inputs, one already the engine's argument, one already ambient —
there is no new schema key, no stamp, no `json.dumps` rewrite of `instantiate_spine`, no
backfill question, no archive rot (finding 11), no `validate_spine` gap (finding 10), no
two-producer format conflict (finding 6), no docs gate (finding 14), and it covers **all 541
existing archived checklists and every child `review.json`/`IMPLEMENTER_PLAN.json`**
(finding 4) instead of only newly-minted `spine.json` files. It is not a tautology: the spine
path is chosen by the caller, and the failing case — engine in the main checkout driving a
worktree spine by absolute path — is exactly the repro's case B. It is disarmable by `cd` in
precisely the same way as the planned design, so it loses nothing on finding 1. I do not
know whether that shape was considered and rejected; it is not in `PLAN_ALTERNATIVES.md`,
which constrained both candidates to the stamp by ruling. Ruling `both-halves-one-change` is
marked settled/human and forecloses it — that ruling is the single most expensive line in
this plan and it is worth re-opening.

Second-largest: the `cwd` test seam that Candidate A named as a foot-gun. If it survives
into the implementation, it re-creates the forwarded-cwd disarm inside the engine's own API.

---

## What I checked and found accurate

- `dispatch()` at `:3069` is a genuine chokepoint — no production caller in `scripts/`
  imports a verb function directly (checked `generate_spine.py`, `context_manifest.py`,
  `episode_capture.py`, `run_crew.py`, `mcp_spine_server.py`).
- All structural line anchors in `execute.json` are correct: `dispatch()` 3069,
  `MUTATING_VERBS` 70, `TRIP_HARD_GUARDED_VERBS` 83, the heartbeat/release/current block
  3074-3086, `instantiate_spine` 152-177, `init_work_area.py:148` and `:171`,
  `spine_lifecycle.build_origin` 83, `mcp_spine_server.py:361`, `spine_lifecycle.py:311`
  storing an unresolved `str(Path(worktree))`.
- Hooks do not subprocess the engine. `spine_rail.py` reconstructs `current` in-process
  (`:281`), its one subprocess is `git worktree list` (`:497-507`). Frame line 57-60 correct,
  and the frame is right that the launch order's contrary claim was false.
- `validate_spine` accepts a new top-level key (denylist `_KNOWN_WRONG_TOP_LEVEL_KEYS` at
  `:98`). Frame line 56 correct.
- `origin` appears nowhere in the engine and nowhere else in `scripts/` except
  `spine_lifecycle.py` and one docstring in `mcp_spine_server.py`. `close_work` explicitly
  "never read[s] from an `origin` field that a hand-authored spine might lack"
  (`spine_lifecycle.py:417`). Frame line 54 correct.
- **Evidence anchors spot-checked:** `tests/test_worktree_precondition_wiring.py` → **7
  passed** ✓. Full suite at `9bb8c1b6` → **2934 passed, 5 skipped, 1121 subtests passed, 0
  failed** in 118s ✓. Archived spines with no `origin`, counting files named `spine.json` →
  **98** ✓. `init.c0` deletion reds **3 of 7** tripwire tests ✓.
- **One number does not check out:** "3 live origin-less spines". I count **2** live
  `spine.json` (`commander-315`, `commander-315-native`), or 4 live work areas holding 6
  drivable checklists, or 31 if `.agent-work/templates/` counts. `ruling backfill-none` rests
  on this number. Minor on its own; it matters because the same counting method undercounts
  the archived fallback population by 5.5x (finding 4).

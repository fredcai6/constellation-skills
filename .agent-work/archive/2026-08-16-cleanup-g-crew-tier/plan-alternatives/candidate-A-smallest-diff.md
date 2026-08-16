# Candidate A — smallest-diff gate plan for #611 (cleanup-g-crew-tier)

Constraint scored against: **smallest-diff only** — fewest files touched, fewest
new gates, tightest scope per gate, fold related work into one gate rather than
splitting it.

## Verified before designing

Read `scripts/run_crew.py` directly (not just the mission frame's line numbers,
which had drifted slightly):

- `build_crew_argv` (`scripts/run_crew.py:755-818`): the sole tier-forwarding
  line is `if model: argv += ["--model", model]` at 813-814. No `reasoning_effort`
  parameter exists on it at all today.
- `CrewSpec.__post_init__` (`scripts/run_crew.py:1350-1364`) is **already** the
  single choke point for every *fresh construction* of a dispatch: it currently
  refuses a spec with neither `handoff` nor `spine`, and one with neither
  `result` nor `spine`. Every production caller that builds a brand-new
  `CrewSpec` — `main()`'s fresh-launch branch (2092-2097), `main()`'s
  `--abandon --relaunch` branch (2068-2074), the library wrappers `launch_crew`
  (1773-1777) and `record_external_attempt` (1839-1843) — routes through this
  one `__post_init__`.
- `resume_crew` (1781-1804) and `CliBackend.resume` (1564-1637) **never**
  construct a `CrewSpec`. Resume reads `entry.get("model")` straight from the
  already-recorded registry entry (1616) and passes that string straight into
  `build_crew_argv`. This is exactly why the mission scopes the refusal to
  "a fresh/relaunch dispatch" and not resume — the mechanism already draws that
  line for free, I just have to not blur it.
- `build_entry` (1092-1199) already writes `model` onto the registry entry
  whenever it is truthy (1193-1194: `if model: entry["model"] = model`). Once a
  fresh/relaunch dispatch can no longer construct a `CrewSpec` with `model=None`,
  every entry it produces necessarily carries the resolved tier — **no code
  change is needed here**, only a test that pins it down as a guarantee instead
  of an accident.
- `reasoning_effort` is already a `CrewSpec` field (1347) and already recorded
  by `build_entry` (1195-1196: `if reasoning_effort: entry["reasoning_effort"] =
  reasoning_effort`), but never reaches `build_crew_argv`/argv. Confirmed (per
  the mission frame, and consistent with `--help` on the installed `claude`
  binary) that the launcher accepts `--effort <low|medium|high|xhigh|max>`.
- `main()`'s `except CrewLaunchError as exc: print(f"REFUSED: {exc}", ...); return
  1` (2106-2108) already turns *any* `CrewLaunchError` — including one raised
  inside `CrewSpec.__post_init__` — into the same fail-closed CLI contract every
  other refusal in this file uses. No new exit-code plumbing needed.
- `tests/test_crew_launcher.py` has exactly 8 direct `RC.CrewSpec(...)` call
  sites and roughly 140 more indirect ones through `RC.main([...])` /
  `RC.launch_crew(...)` / `RC.record_external_attempt(...)`. A sample audit
  found call sites in three shapes: (a) tests already passing a real
  `model="sonnet"`/`"opus"` — unaffected; (b) tests passing `model=None`
  or omitting `--model` on a `main()` fresh/relaunch call, expecting a
  *successful* dispatch — these will start raising and must be given a model;
  (c) tests exercising `build_crew_argv` **directly** (a pure function, not
  through `CrewSpec`) with `model=None` to assert "no `--model` flag when none
  given" — these stay valid and untouched, because `build_crew_argv` itself is
  not where the refusal lives.
- Three existing tests (`test_reasoning_effort_is_metadata_only_and_recorded`,
  `test_cli_resume_reads_reasoning_effort_from_registry`,
  `test_legacy_resume_without_reasoning_effort_does_not_crash`, plus
  `test_abandon_relaunch_inherits_stored_reasoning_effort_when_not_reasserted`)
  currently assert `assertNotIn("--reasoning-effort", argv)` and carry docstrings
  ("Recovery keeps metadata even though it never becomes a Claude flag") that
  state the pre-mission contract as a *guarantee*. They will keep passing
  by accident (they check for a flag name, `--reasoning-effort`, that this
  mission does not add — it adds `--effort`), but their names/docstrings would
  actively lie about the new behavior if left alone. They are in-scope, in an
  owned file, and directly contradict the change — not follow-up.

## Gate list

**Two gates. One implement, one independent review.** No `g2`.

The launch order's own pre-ruling `@grade` tags lean four of five decisions at
`g1-implement` and one (`suggested-tier-becomes-load-bearing`) at `g2` — but
that decision resolves to a single doctrine-prose paragraph in a file this
mission already owns and is already touching for the same reason (model is
now load-bearing). Standing up a second implement/review pair to carry one
paragraph would add two gates' worth of dispatch, handoff-authoring, and
review overhead to save nothing: the paragraph has no code seam, no test
surface, and no dependency ordering against the code change. Folding it into
`g1` is the smaller diff and the more defensible one; the `@grade` tag itself
says `leans`, not `binds`.

### `g1-implement` — make the tier mandatory, wire effort, land the doctrine

One crew, one patch, three co-located changes to the same seam:

1. **Refusal** (`scripts/run_crew.py`): add one guard clause to
   `CrewSpec.__post_init__` —
   ```python
   if not self.model:
       raise CrewLaunchError(
           "a crew needs a model tier: refusing a dispatch with no --model "
           "given (never inherited from the parent process, never defaulted)"
       )
   ```
   placed alongside the two existing invariant checks in the same method, same
   style, same exception type. This is backend-agnostic and caller-agnostic by
   construction: it fires for `CliBackend` fresh dispatch, `--abandon
   --relaunch`, `ExternalBackend` fresh dispatch (`record_external_attempt`),
   and any direct `launch_crew()` caller — one clause instead of four
   duplicated checks in each dispatch path. It does **not** fire on `--resume`,
   because `resume_crew`/`CliBackend.resume` never construct a `CrewSpec` —
   confirmed above, not assumed.
   `--model` stays optional at the `argparse` layer (`build_parser`,
   `scripts/run_crew.py:1889`): it must remain legal to omit on `--resume` and
   on a bare `--abandon` (no `--relaunch`), neither of which builds a
   `CrewSpec`. Making it `required=True` in argparse would break both of those
   legitimately-tierless call shapes at the parser level, before the
   fresh/relaunch-only scoping could apply — this is the one place a "smallest
   diff" instinct (just add `required=True`) would actually be a wider,
   wronger diff than the dataclass-level guard.

2. **`reasoning_effort` → `--effort`** (`scripts/run_crew.py`): add a
   keyword-only `reasoning_effort: str | None = None` parameter to
   `build_crew_argv` and one line mirroring the existing `model` line:
   `if reasoning_effort: argv += ["--effort", reasoning_effort]`. Thread it
   through the two `CliBackend` call sites only:
   - `dispatch` (~1542): `reasoning_effort=spec.reasoning_effort`.
   - `resume` (~1612): `reasoning_effort=entry.get("reasoning_effort")`.
   `ExternalBackend` spawns no subprocess and gets no argv change — out of
   scope by construction, matching the mission frame's own out-of-scope note.
   Update `build_entry`'s docstring line ("`reasoning_effort` ... it is never
   emitted as a CLI flag", 1129-1130) since it is now false; `build_entry`'s
   *logic* does not change — it still just records metadata, forwarding is
   `build_crew_argv`'s job. New parameter has a default, so no existing
   `build_crew_argv(...)` call site (direct or indirect) breaks.

3. **Doctrine** (`skills/commander/references/crew-dispatch.md`): one new short
   section (mirroring the file's existing terse, imperative style) stating:
   `run_crew.py` refuses any fresh or relaunched dispatch with no `--model`;
   the handoff templates' "Suggested Model Tier" field
   (`IMPLEMENTER_HANDOFF.template.md:94`, `REVIEWER_HANDOFF.template.md:60`) is
   what a Commander reads and translates into that `--model` (and, if the
   suggestion names a reason like "concurrency correctness rewards careful
   reasoning," into `--effort` too) before dispatch — not decorative prose. Per
   the launch order's own settle-guidance ("prefer the smaller change; a field
   nobody parses but everybody must answer is better than a parser for
   prose"), this stays **prose the Commander acts on**, not a machine-parsed
   field. **No edit to the two handoff templates themselves** — they already
   carry the section (confirmed present at the cited lines); the mission asks
   doctrine to *name* the field as load-bearing, not to add or reshape it.

4. **Tests** (`tests/test_crew_launcher.py`, same gate — not a follow-up):
   - Every `main([...])` / `launch_crew(...)` call site currently exercising a
     *successful* fresh or relaunch dispatch with `model=None`/no `--model`
     gets a real model value (`"sonnet"` is the existing convention seen at
     several call sites already).
   - Two new tests: (a) a fresh dispatch with no `--model` is refused
     (`CrewLaunchError`/CLI exit 1), one with `--model` succeeds, and the
     resolved tier is present on the registry entry afterward — this is
     literally Return-Shape item 1's red/green demonstration, written as a
     test rather than only a manual transcript. (b) a `--resume` with no
     `--model` on the command line still succeeds (proves the scoping — resume
     is not, and must not become, gated).
   - The four `reasoning_effort`-related tests named above get their
     `assertNotIn("--reasoning-effort", ...)` replaced with an assertion that
     `--effort <value>` **is** present in the spawned argv when
     `reasoning_effort` is set, and absent when it is not (including the
     legacy-entry-with-no-field case) — plus corrected docstrings. This is the
     direct-contradiction fix identified above, not new scope invented by the
     implementer.
   - `build_crew_argv`'s own direct-call tests (the ones asserting no
     `--model` flag when `model=None`, e.g. `SpineOwnershipPromptTests` /
     `ParentPromptTests` / `BlankParentTests`) are **left untouched** — they
     test the pure function below the refusal seam, and the refusal
     deliberately does not move into `build_crew_argv` (see "left out," below).

   **Close criteria:** clean-env, cache-cleared full suite green at the
   published head (`env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m
   pytest -q`, `__pycache__` cleared first per the launch order's standing
   instruction); the two new red/green tests pass; a `main`
   baseline re-measured at gate time for the failure-set diff.
   **Evidence:** the diff itself (four files: `scripts/run_crew.py`,
   `tests/test_crew_launcher.py`, `skills/commander/references/crew-dispatch.md`,
   plus this gate's own handoff/result artifacts — no fifth file), full-suite
   transcript, `git diff --stat`.

### `g1-review` — independent verification

Standard Commander-doctrine independent reviewer (`skills/commander/references/
crew-dispatch.md` itself governs this dispatch, so this gate is also the first
real user of the doctrine paragraph `g1-implement` just wrote). Reviews the
diff for:
- the refusal fires only on fresh/relaunch (not resume, not bare abandon), by
  reading `CrewSpec.__post_init__` and grepping every `CrewSpec(` construction
  site rather than trusting the implementer's claim;
- no default tier was invented anywhere (the exact hazard the
  `refuse-a-tierless-dispatch` pre-ruling names);
- `--effort` forwarding is symmetric on `dispatch` and `resume` (the mission
  frame's own decision-pressure note: a tier/effort that silently drops on
  resume reproduces the defect this mission fixes);
- no effective tier changed for any *existing* dispatch site outside this run's
  own crews (`do-not-change-what-anything-runs-at`);
- `checklist_engine.py`, `spine_rail.py`, `spine_lifecycle.py`, and the
  fenced-for-#610 files are untouched;
- the caller list (test call sites that needed a model added) is complete and
  reported, not silently patched-and-hidden.

**Close criteria:** independent APPROVE, or a named defect sent back to
`g1-implement` (same gate, re-entered — no new gate number spent on a repair
loop; this plan does not pre-allocate one because a repair loop is not
"new work," it is the same gate continuing).
**Evidence:** the reviewer's handoff result artifact, citing the same
full-suite transcript re-run at the reviewed head (not re-trusting
`g1-implement`'s own run).

## Sequencing rationale (the trap)

1. **Before either gate opens**, every crew *I* (the Commander) dispatch this
   run — including `g1-implement`'s implementer — carries an explicit
   `--model` from the first dispatch, against **today's** `run_crew.py`, which
   already accepts (but does not yet require) `--model`. This costs nothing
   extra: I was always going to name a tier per the launch order's inherited
   rule; the only discipline is not letting habit default it.
2. `g1-implement` lands the refusal, the `--effort` wiring, and the doctrine
   paragraph as one atomic patch — there is no intermediate state where
   `--model` is required but `--effort`/doctrine aren't done, because they
   share one commit and one gate. This avoids the exact hazard the launch
   order calls out by name: a refusal landing *between* implement and review
   would strand the reviewer dispatch. Because there is no gate boundary
   between "refusal exists" and "reviewer needed," there is no window for that
   to happen structurally, not just by discipline.
3. `g1-review`'s reviewer is dispatched **after** `g1-implement`'s patch is on
   disk, with an explicit `--model`, against the **new** `run_crew.py`. This is
   a deliberate self-test: if the refusal implementation were broken (e.g. it
   fired even when a model was given, or failed to fire on resume), the
   reviewer dispatch itself is the first thing that would surface it — before
   any test suite claims green. This is why `g1-review` is not folded into
   `g1-implement` despite the smallest-diff bias toward folding: an
   implementer cannot independently verify its own refusal never locked out
   its own next dispatch. Two roles, still one gate-pair, is the floor.

## Where this deliberately stays smaller, and what that accepts

- **No `g2`.** The "suggested-tier-becomes-load-bearing" doctrine change rides
  in `g1-implement` (see "gate list" above). Risk accepted: a reviewer who
  wanted the doctrine change reviewed in isolation from the code change instead
  reviews both together — acceptable, because the doctrine paragraph literally
  describes the code change and cannot be evaluated correctly apart from it.
- **No template edits.** `IMPLEMENTER_HANDOFF.template.md` and
  `REVIEWER_HANDOFF.template.md` are named in file ownership but not edited:
  the field already exists at the cited lines, and the pre-ruling's own settle
  guidance prefers prose-Commander-reads-and-acts-on over a parser. Risk
  accepted: if a future reader wanted the field itself to gain, say, a
  controlled vocabulary or an explicit "translate this to `--model`" pointer
  *inside* the template, that is left undone — reported as a triage candidate,
  not built speculatively here.
- **No refusal duplicated into `main()`'s CLI-level pre-checks** (the
  `missing = [...]` block at 2015-2022 and its siblings). The `CrewSpec`-level
  guard already covers the CLI path (main constructs a `CrewSpec` before
  dispatch) and every library caller in one place. Risk accepted: a user
  hitting the refusal from the CLI sees a `CrewLaunchError` message worded for
  the dataclass invariant ("a crew needs a model tier...") rather than one
  hand-tuned to match the existing early-arg-check phrasing
  ("launch requires --work-id --gate --role, plus...") — a cosmetic
  inconsistency in error-message style, not a functional gap; both paths print
  through the same `REFUSED: {exc}` formatter and return exit code 1.
- **No change to `build_crew_argv`'s own `if model:` guard.** It stays
  permissive (silently omits `--model` when given `None`) because by the time
  it runs, `CrewSpec.__post_init__` has already refused a `None` model for
  every real caller — the guard is now dead-but-harmless defensive code, not a
  second enforcement point. Risk accepted: a hypothetical *new* future caller
  of `build_crew_argv` directly (bypassing `CrewSpec` entirely) could still
  build a flagless argv — narrow, because every current and mission-scoped
  caller goes through `CrewSpec` first, and the pure function's whole
  documented purpose is to be testable in isolation from that invariant.
- **No `--model` at the `argparse` level (`required=True`).** Covered above
  under gate 1 close criteria — this is a correctness constraint, not a
  diff-size tradeoff, but it is also the smaller diff: one dataclass guard
  clause beats a `required=True` flip plus special-casing `--resume`/bare
  `--abandon` back out of it at the parser layer.
- **No new registry-shape work for "confirming the resolved tier lands on the
  registry entry."** `build_entry` already writes `model` whenever truthy
  (1193-1194); this decision is satisfied as a *consequence* of the refusal,
  not a separate implementation task. Only a pinning test is added. Risk
  accepted: none identified — this is a pre-existing code path being exercised
  under a new invariant, not new logic.
- **Caller list is a report, not a silent fix-everywhere.** Every test call
  site that needed a model added is still touched (tests must pass at gate
  time — "local Linux green" is a hard merge-gate condition, not optional), but
  the *report* to the Admiral lists them as evidence per Return-Shape item 2,
  rather than treating "the suite went green" as proof nothing needed a
  decision. If any non-test caller outside `tests/test_crew_launcher.py` and
  `scripts/run_crew.py` itself is found to construct a `CrewSpec` with no
  tier to name (none found in this pass — grep found only the two owned
  files), that would be floated up rather than defaulted, per the pre-ruling.

## Score against the rubric axes

- **Depth**: the refusal sits at the one dataclass invariant every fresh/
  relaunch path already funnels through (verified by reading every `CrewSpec(`
  construction site, not assumed from the mission frame) — this is the actual
  mechanism, not a surface patch on `main()`'s argv handling.
- **Locality**: three source files (`run_crew.py`, `crew-dispatch.md`,
  `test_crew_launcher.py`) plus this gate's own handoff/result artifacts.
  Nothing touched outside the launch order's named ownership; nothing touched
  in the fenced or #610-reserved files.
- **Seam placement**: `CrewSpec.__post_init__` for the refusal (backend- and
  caller-agnostic, matches the file's own existing invariant-checking idiom);
  `build_crew_argv` + the two `CliBackend` call sites for `--effort` (mirrors
  the existing `model` plumbing exactly, so a future reader finds the two
  fields forwarded the same way). No new module, no new class, no new backend
  method.
- **Testability**: the refusal and the effort-forwarding are both pure-function/
  dataclass-level changes, assertable without spawning a subprocess (the
  existing `fake_launch` seam already used throughout the file). The two new
  red/green tests directly satisfy Return-Shape item 1 as machine-checked
  evidence rather than a hand-run transcript only.

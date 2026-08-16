# Candidate B — most-testable gate plan

**Constraint:** maximize what each gate boundary can independently prove with a
red/green test. Every gate below closes on evidence that a coarser bundling
(e.g. "one gate: wire tier end to end") would make indistinguishable from the
evidence of its neighbors — the specific bundling each gate avoids is called
out under "What this un-bundles."

## Grounding read (confirms the seam, not asserted)

- `build_crew_argv` (`scripts/run_crew.py:755-818`) is PURE: no registry, no
  subprocess, no CrewSpec. It takes `model: str | None` and does
  `if model: argv += ["--model", model]` (813-814). It has **no** `effort`
  parameter today. Both `CliBackend.dispatch` (1542-1547) and
  `CliBackend.resume` (1612-1620) call it — `resume` builds argv from a
  **registry entry dict** (`entry.get("model")`), not a `CrewSpec`.
- `CrewSpec.__post_init__` (1350-1364) already refuses two things
  unconditionally — missing job (handoff+spine both absent), missing
  completion contract (result+spine both absent) — by raising
  `CrewLaunchError`. It does **not** check `model`. This is the one seam both
  a fresh launch (`main()` ~2092) and an abandon+relaunch (`main()` ~2068)
  pass through; `resume` does **not** construct a `CrewSpec` and never will
  refuse here.
- `build_entry` (1092-1199) already does `if model: entry["model"] = model`
  and `if reasoning_effort: entry["reasoning_effort"] = reasoning_effort` —
  recording is not the gap; the gap is (a) nothing ever refuses `model=None`
  and (b) `reasoning_effort` is recorded but never reaches argv.
- Existing tests already encode the CURRENT (pre-mission) contract and will
  need to flip, which makes them free red/green pivots for this plan:
  - `test_build_crew_argv_omits_model_when_absent` (line 220) — proves the
    pure function's `model=None` behavior is exercised directly, no mocking.
  - `test_reasoning_effort_is_metadata_only_and_recorded` (line 2588) —
    **currently asserts `assertNotIn("--reasoning-effort", ...)`**. This
    assertion is the literal statement of the defect. Flipping it to assert
    presence of `--effort <value>` is a self-documenting red→green marker for
    this mission, not a new test invented from nothing.
  - `test_cli_resume_reads_reasoning_effort_from_registry` (2605) and
    `test_legacy_resume_without_reasoning_effort_does_not_crash` (2623) —
    same `assertNotIn("--reasoning-effort", ...)` pattern on the **resume**
    path specifically, separate from dispatch.
  - `test_crew_delivery_addressing.py:230-243` is the established repo
    pattern for a doctrine-file red/green test (assert absence of stale text,
    assert presence of new text, verified-red against a specific commit) —
    G6 below reuses this pattern rather than inventing a new one.

## Gate list

### G1 — `build_crew_argv` gains a pure `effort` parameter
**Purpose:** the launcher's real `--effort` flag exists on the one PURE
construction seam, forwarded exactly like `model` is, with zero coupling to
CrewSpec, the registry, or a subprocess.

**Close criteria / evidence:**
- New `effort: str | None = None` parameter; `if effort: argv += ["--effort", effort]`, mirroring the existing `model` line.
- `test_build_crew_argv_omits_effort_when_absent` (new, mirrors line 220 exactly).
- `test_build_crew_argv_forwards_effort_when_given` (new, mirrors line 197-209: asserts `"--effort" in argv` and the value follows it — argv **index** asserted, not just membership, so a flag/value transposition bug is caught).
- Runs with zero fixtures beyond a direct function call — no `tempfile`, no `fake_launch`, no registry. Fastest, most isolated test in the whole plan; falsifiable on its own before any other gate exists.

**What this un-bundles:** a bug in the flag string itself (`--effort` vs `--reasoning-effort` vs `--reasoning_effort`) or in the value's position in argv is provable — and provably absent — without ever running a fake subprocess or building a registry. A coarser "wire effort end-to-end" gate would only ever observe this through a dispatch-level fake-launch assertion, which conflates a typo in the flag name with a wiring bug in the caller (see G2) — if that combined test fails, you don't yet know which layer broke.

### G2 — `CliBackend.dispatch` and `.resume` both forward the resolved effort into `build_crew_argv`
**Purpose:** the two real call sites actually pass `effort=` through — dispatch from `spec.reasoning_effort`, resume from `entry.get("reasoning_effort")` — closing the "recorded but never reaches argv" gap named in the launch order for **both** paths, not just fresh dispatch.

**Close criteria / evidence:**
- `CliBackend.dispatch` line ~1542-1547: add `effort=spec.reasoning_effort`.
- `CliBackend.resume` line ~1612-1620: add `effort=entry.get("reasoning_effort")`.
- Flip the three existing tests identified above to their new-contract form:
  - `test_reasoning_effort_is_metadata_only_and_recorded` → rename (the old name is now false) to something like `test_reasoning_effort_reaches_argv_and_is_recorded`; assert `"--effort" in calls[0]["argv"]` and the value follows, **and** `entry["reasoning_effort"]` still recorded (single test proving both halves of decision `reasoning-effort-follows-tier` at once, using the existing `fake_launch` capture pattern already in the file).
  - `test_cli_resume_reads_reasoning_effort_from_registry` → assert `"--effort" IS now in resume_calls[0]["argv"]` with the stored value — this is the resume-specific proof the mission frame's decision-pressure section explicitly flags as leaning-both-call-sites; without this test, dispatch-only forwarding would pass every other gate and still silently reproduce the defect on every resume.
  - `test_legacy_resume_without_reasoning_effort_does_not_crash` → keep asserting `assertNotIn("--effort", ...)` for a legacy entry with no `reasoning_effort` key — proves the `if effort:` guard (not a KeyError, not an empty-string flag) survives a pre-mission registry entry untouched.

**What this un-bundles:** dispatch-side and resume-side forwarding are two independent call sites that can each be wired correctly or incorrectly independent of the other (resume's `entry.get(...)` vs dispatch's `spec.` attribute access are different code shapes reading different objects). Separate assertions per call site mean "effort forwards on fresh dispatch but silently drops on resume" is a distinct, catchable red state — which matters because resume is exactly the path a Commander uses to continue a crew after an interruption, i.e. exactly where a silently-dropped tier would be easiest to miss in practice.

### G3 — registry entry confirms the resolved tier, independent of argv
**Purpose:** directly test decision `record-the-resolved-tier` — that what lands in `crew-runs.json` is the same value that was actually launched — as its own claim, not inferred from G1/G2's argv assertions.

**Close criteria / evidence:**
- `test_cli_dispatch_records_model_when_given` (line 2568, already exists) continues to pass unmodified — it is already the right shape; cite it as a pre-existing anchor, do not touch it.
- New test: dispatch with both `model="sonnet"` and `reasoning_effort="high"`, then assert **on the registry entry dict directly** (`entry["model"] == "sonnet"`, `entry["reasoning_effort"] == "high"`) with **no reference to `calls[0]["argv"]` at all** in the same assertion block — a deliberately separate read path from G1/G2's argv-focused tests.
- New test on the **relaunch** path (`--abandon --relaunch`, `main()` ~2054-2080): dispatch once, abandon, relaunch with an explicit `--model`, assert the **new** attempt's registry entry (not the abandoned one) carries the resolved tier.

**What this un-bundles:** G1/G2 prove the subprocess *would receive* the right flags; they say nothing about what a human or tool reading `crew-runs.json` afterward sees. These are genuinely different failure modes — e.g. a future refactor that changes `build_entry`'s parameter name without updating its caller would pass G1/G2 (argv still correct) and fail only here. Bundling this into G2 would mean a registry-recording regression is invisible until someone happens to inspect `crew-runs.json` by hand.

### G4 — mandatory refusal of a tierless fresh/relaunch dispatch
**Purpose:** implement decision `refuse-a-tierless-dispatch` at the seam both fresh-launch and abandon+relaunch pass through (`CrewSpec.__post_init__`), fail-closed, no invented default — split into two independently-closeable sub-gates so a validation-logic bug and an argparse-wiring bug produce distinguishable red states.

**G4a — pure dataclass validation:**
- Add to `CrewSpec.__post_init__`: refuse when `self.model` is falsy, raising `CrewLaunchError`, in the same style as the existing handoff/result checks immediately above it (1354-1364).
- `test_crewspec_refuses_missing_model` (new): construct `CrewSpec(..., model=None)` directly — no `main()`, no argparse, no subprocess — assert `CrewLaunchError` raised with a message naming the missing tier.
- `test_crewspec_accepts_explicit_model` (new, green companion, same isolation level): construct with `model="sonnet"`, assert no raise. Every gate that asserts a refusal in this plan is paired with a same-shape acceptance test — a plan that only ever tests the red side cannot distinguish "correctly refuses tierless" from "refuses everything."

**G4b — `main()` integration, fresh launch and relaunch separately:**
- Fresh launch with no `--model`: `main([...no --model...])` returns 1, stderr carries `REFUSED`, **and no registry entry was written** (assert the registry file is absent or unchanged — this reuses the existing #525 scratch-before-registry-write ordering already in the file, so the refusal must fire before `CliBackend.dispatch` reserves scratch/writes the running entry; if it fires too late, this test catches a half-written entry that G4a's pure test cannot see).
- Fresh launch with `--model sonnet`: green companion, existing `fake_launch` pattern, asserts exit 0 and `entry["model"] == "sonnet"` (cross-checks G3 from the CLI-integration level, not just the `CliBackend` level).
- Abandon+relaunch: **flag as an open sub-decision, not resolved by this plan** — `main()`'s relaunch branch (~2068-2074) passes `model=args.model` directly with **no** fallback to `abandoned.get("model")`, unlike `reasoning_effort`, which does fall back (line 2071). Two testable outcomes, either is fine for this gate's testability:
  - *Require re-assertion*: relaunch with no `--model` on a previously-tiered entry is refused → `test_relaunch_refuses_missing_model_even_when_entry_was_tiered`.
  - *Inherit like effort does*: relaunch with no `--model` inherits `abandoned.get("model")` → `test_abandon_relaunch_inherits_stored_model_when_not_reasserted`, mirroring the existing `test_abandon_relaunch_inherits_stored_reasoning_effort_when_not_reasserted` (line 955) for symmetry.
  Whichever the implementer picks, it is a single named test with an unambiguous expected outcome — the point for this plan is that the fork itself is visible and testable, not silently resolved one way inside a bigger "refusal works" assertion.

**What this un-bundles:** G4a proves the *rule* is correct in complete isolation from argparse, CLI wiring, registry side effects, or the #525 scratch-ordering interaction. G4b proves the rule is actually *reached* from every real entry point (`main()`'s two dispatch-constructing branches) and that firing it doesn't leave a half-written registry record. A single combined "refusal works" test (construct via `main()` only) would conflate "the rule is wrong" with "the rule is right but wired to the wrong argv" or "the rule fires after scratch is already reserved" — three different bugs that would otherwise all produce the same one red test.

### G5 — caller-list survey (evidence-only, not a code gate)
**Purpose:** satisfy the pre-ruling's explicit deliverable — "if refusing breaks callers that legitimately have no tier to name... REPORT them" — as an independently checkable claim, not a hand-wave.

**Close criteria / evidence:**
- After G4 lands, run the full clean-env suite once. Enumerate every failure whose message contains the G4 refusal text. For each, classify: legitimate tierless caller (add to the reported list, `notes-g.md`) vs. a test that needs an update to pass an explicit `model=` (fix, don't report).
- The falsifiable claim: **the enumerated list is complete.** Evidence: after fixing every test classified "needs update," the suite is green with zero unexplained failures. If the list were incomplete, a residual failure would surface here — this gate's close criterion is the absence of unaccounted-for red, which is a genuine pass/fail signal, not a subjective judgment call.
- This gate deliberately produces **no production code change** of its own — it is the mechanism by which G4's blast radius is measured rather than assumed safe.

**What this un-bundles:** without a separate gate, "did the refusal break anything legitimate" is usually answered by "the suite is green," which conflates two different things: tests that were updated to comply (fine) and tests that were silently made to always pass a tier even where that's semantically wrong (a defect reintroduced under cover of green). Naming this as its own gate with its own enumerated evidence artifact makes the distinction checkable by someone who wasn't in the room.

### G6 — `crew-dispatch.md` names "Suggested Model Tier" as load-bearing
**Purpose:** implement decision `suggested-tier-becomes-load-bearing` as doctrine text a Commander must act on (per the pre-ruling's settle note: prefer prose over a parser), using the repo's own established pattern for testing doctrine-text changes.

**Close criteria / evidence:**
- Follows `tests/test_crew_delivery_addressing.py:230-243` exactly: a new test class reading `crew-dispatch.md` directly off disk, asserting (a) the text now names "Suggested Model Tier" (or the section's exact heading) as the source a Commander resolves `--model`/`--effort` from before dispatch, and (b) — as a verified-red anchor, matching that file's own documented practice of confirming the test fails against the pre-change commit — run the new test against `HEAD` (this branch's base, `e0539903`) first and paste the failure into `notes-g.md` before making the doctrine edit, so the "red" side of red/green is measured, not asserted.
- Optional strengthening (same file, same pattern as `test_commander_evidence_convention.py`'s cross-file consistency check): assert the doctrine's naming of the field matches the literal string used in both `IMPLEMENTER_HANDOFF.template.md:94` and `REVIEWER_HANDOFF.template.md:60`, so a future rename of the template section silently desyncs from doctrine is itself caught.

**What this un-bundles:** without this gate's own test, "doctrine now mentions model" is a claim verified once by eyeball at write time and never checked again — the weakest form of evidence in this plan, and the plan says so rather than overselling it (matching the source pattern's own "weak by nature and offered as that" framing). Keeping it as its own gate, rather than folding it into G4's report, means a later PR that touches `crew-dispatch.md` for an unrelated reason and accidentally drops the tier language gets a specific, attributable failure instead of a silent doctrine regression nobody's suite catches.

## Sequencing rationale

1. **G1 before G2 before G3.** Each is a strictly larger blast radius than the last (pure function → real call sites → registry persistence), and each has zero code overlap with G4/G5/G6. Landing them first means the mission's `reasoning-effort-follows-tier` decision closes completely, on its own evidence, before the refusal work (which is the one change with control-flow risk to the Commander's own ongoing dispatches) is touched at all.
2. **G4 after G1-G3, split G4a before G4b.** G4a (pure dataclass check) carries no risk to any real dispatch — it's a new branch in `__post_init__` provable in complete isolation. G4b is the one change that actually alters what `main()` does for every real invocation, including the Commander's own crew launches for the rest of this mission. Landing G4a's logic first and proving it correct in isolation means G4b is "wire the already-proven rule to argparse," not "invent and wire a rule simultaneously" — a smaller, more falsifiable increment.
3. **G5 immediately follows G4b's landing**, using the same suite run — it is not a separate implementation phase, it is the required evidence-gathering pass over G4's actual blast radius, and the pre-ruling treats it as a mandatory deliverable rather than a nice-to-have.
4. **G6 has no ordering dependency on G1-G5** — it touches a disjoint file, and its test is provable red/green against the doctrine file alone. Sequenced last only because it is the lowest-risk, most independent gate (nothing else in the plan reads or depends on it), so if the session runs out of budget, docs are the safest thing to have deferred — not because it depends on the code gates. Note this explicitly if budget forces a cut: G6 is droppable without invalidating G1-G5's evidence; none of G1-G5 are droppable without leaving G6's doctrine claim unenforceable (the field would be "load-bearing" in prose with no code behind it it could ever have pointed at).
5. **Own-dispatch discipline runs orthogonal to all of the above, not as a gate**: per the launch order's named trap, every crew this run dispatches (if any are needed for review, etc.) names `--model` explicitly from the first dispatch, independent of whether G4 has landed yet — this is a process discipline note, not something a gate closes on, since it's about this run's own behavior rather than the shipped code.

## Net effect vs. a coarser plan

A coarser two-gate plan ("G-code: wire tier+effort end to end and add the
refusal" / "G-docs: update doctrine") would still ship the same production
diff, but a single failing test under it tells you only "something in tier
handling is wrong" — not whether the pure argv construction, the dispatch
wiring, the resume wiring, the registry recording, the validation rule, or
the argparse plumbing is the actual fault. Six gates (G1-G6, with G4 split
into two) each pin one of those six independently — a regression introduced
by a future unrelated change lands on exactly one red test, not a bundle of
maybe-related ones, which is the whole point of grading this candidate on
testability specifically.

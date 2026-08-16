# Plan Convergence — cleanup-g-crew-tier (#611)

Design-it-twice, plan-phase. Panel-vs-single: **single pair (N=2)**, not a 3-lens panel —
narrow, heavily pre-ruled (5 graded decisions in the launch order), 2-owned-source-file scope.
Recorded as a surfaced choice, matching the precedent this epic already set
(`cleanup-c-liveness-rail`'s plan step, same call for the same reason).

Candidates: `plan-alternatives/candidate-A-smallest-diff.md`, `plan-alternatives/candidate-B-most-testable.md`.

## What both candidates independently confirmed (before either saw the other)

- **`CrewSpec.__post_init__`** (`scripts/run_crew.py:1350-1364`) is the correct refusal seam —
  the one place every fresh construction (`main()`'s fresh-launch branch ~2092, its
  `--abandon --relaunch` branch ~2068, `launch_crew` ~1773, `record_external_attempt` ~1839)
  funnels through, matching the file's own existing invariant-check idiom (it already refuses
  missing-job and missing-completion-contract there). Neither candidate proposed `argparse
  required=True` or a check inside `build_crew_argv` — both independently rejected those for the
  same reason: `--resume` and a bare `--abandon` legitimately pass no `--model` and must stay legal
  at the parser layer; `build_crew_argv` is a pure function below the refusal, not where the
  invariant belongs.
- **`--resume` never constructs a `CrewSpec`.** `CliBackend.resume` (1564-1637) reads
  `entry.get("model")` off the already-recorded registry dict and passes it straight through — so
  the refusal, planted at `CrewSpec.__post_init__`, exempts resume *by construction*, not by a
  special case someone has to remember to add.
- **`build_entry` already satisfies `decision:record-the-resolved-tier`.** `if model:
  entry["model"] = model` (1193-1194) is pre-existing; once a fresh/relaunch dispatch can no
  longer construct a `CrewSpec` with `model=None`, every entry it produces necessarily carries the
  tier. No new write path — a pinning test only.
- **Four existing tests currently assert the defect as a guarantee**: `assertNotIn
  ("--reasoning-effort", argv)` (or equivalent) in `test_reasoning_effort_is_metadata_only_and_recorded`
  (~2588), `test_cli_resume_reads_reasoning_effort_from_registry` (~2605),
  `test_legacy_resume_without_reasoning_effort_does_not_crash` (~2623), and
  `test_abandon_relaunch_inherits_stored_reasoning_effort_when_not_reasserted` (~955). These are
  self-documenting red→green pivots for `decision:reasoning-effort-follows-tier`, not new scope.

## Where they differ: gate granularity

**Candidate A** — 2 crew-dispatch gates total (`g1-implement`/`g1-review`, no `g2`): folds the
refusal, the `--effort` wiring, and the `crew-dispatch.md` doctrine paragraph into one patch,
reasoning that the doctrine change has no independent test surface or ordering dependency and
splitting it would spend a full implement/review pair to carry one paragraph.

**Candidate B** — 6 gates (`G1`...`G6`, `G4` split into `G4a`/`G4b`), each closing on evidence a
coarser gate would make indistinguishable from its neighbors: pure `build_crew_argv` effort
forwarding (G1) separate from the two real call sites forwarding it (G2) separate from the
registry actually recording it (G3) separate from the validation rule in isolation (G4a) separate
from `main()` actually reaching it without leaving a half-written registry entry (G4b) separate
from the caller-list survey as its own evidence gate (G5) separate from the doctrine change with
its own red/green test, following the repo's established `tests/test_crew_delivery_addressing.py:230-243`
pattern (G6).

**Recommendation: hybrid, not a straight pick.** Adopt Candidate A's *dispatch* granularity (one
code crew-gate, one small reasoning gate for doctrine — matching this run's own "one working
session" budget and minimizing crew dispatches while fixing the dispatch mechanism itself) but
adopt Candidate B's *test* granularity and specific test list as the code gate's required
evidence — B's decomposition is free once you're already writing the tests; it costs nothing extra
in dispatch overhead and catches strictly more failure modes (a typo in `--effort` vs a dropped
resume-side wire vs a registry-recording regression each land on a distinguishable red test rather
than one bundled assertion). B's `G5` (caller-list survey) and `G6` (doctrine red/green test) fold
into `g1`'s and `g2`'s evidence respectively rather than becoming their own gates — the *evidence*
they'd produce is kept, the *gate boundary* is not.

## Decision I am ruling on (Candidate B's named fork, within Inherited Latitude — "where the tier
is resolved")

`main()`'s `--abandon --relaunch` branch (~2068-2074) passes `model=args.model` with **no**
fallback to `abandoned.get("model")` — unlike `reasoning_effort`, which does fall back (`args.
reasoning_effort or abandoned.get("reasoning_effort")`, line 2071). Candidate B named both
outcomes as equally testable and left the choice open; Candidate A's design silently produces the
"require re-assertion" outcome as a side effect of not special-casing relaunch.

**Ruling: relaunch requires an explicit `--model`, same as fresh launch — no inherit-from-abandoned-entry
fallback.** Note (cold-critic finding #7): `main()` at line ~2070 already does exactly this today
(`model=args.model`, no `or abandoned.get(...)`) — only `reasoning_effort` has the fallback. So this
ruling is "don't add a fallback that doesn't exist yet," not a code change at that line; its actual
leverage point is the new refusal seam (`CrewSpec.__post_init__`), which now makes an absent `model`
on relaunch fail loudly where it previously proceeded silently. Reasoning for the ruling itself: the
launch order's own words for the refusal are "never inherited from the
parent process, never defaulted" (Pre-Rulings, `decision:refuse-a-tierless-dispatch`) — a relaunch
silently reusing a *previous* attempt's tier is a form of inheritance the mission is explicitly
naming as the failure mode to close, not a case to carve back out. This is a smaller, more uniform
rule (one guard, no branch-specific fallback) and keeps `model` and `reasoning_effort` intentionally
asymmetric: `reasoning_effort` is optional metadata with no refusal attached, so inheriting it on
relaunch was never the tierless-dispatch hazard this mission targets; `model` is the field the
refusal exists for. `do-not-change-what-anything-runs-at` is respected: `reasoning_effort`'s
existing inherit-on-relaunch behavior is untouched by this ruling.

## Untaken roads (named, not silent)

- **Candidate B's full 6-gate crew-dispatch structure** — not taken as *dispatch* boundaries (see
  hybrid above). Its test decomposition IS taken, inside `g1`'s evidence requirements.
- **A 3-lens critic panel** — not taken; single critic, matching the panel-vs-single call already
  made for plan-alternatives above (narrow, pre-ruled scope).
- **Editing `IMPLEMENTER_HANDOFF.template.md`/`REVIEWER_HANDOFF.template.md`** — not taken (both
  candidates independently agreed): the "Suggested Model Tier" field already exists at the cited
  lines; the pre-ruling's settle note prefers doctrine-prose-Commander-reads-and-acts-on over
  reshaping the template. Reported as available future work if a controlled vocabulary or explicit
  `--model` pointer inside the template is ever wanted.
- **`argparse required=True` on `--model`** — not taken by either candidate; would break the
  legitimately-tierless `--resume`/bare-`--abandon` shapes at the parser layer, before the
  fresh/relaunch-only scoping in `CrewSpec.__post_init__` could apply.
- **Duplicating the refusal into `main()`'s own early arg-checks** — not taken; the
  `CrewSpec`-level guard already covers the CLI path and every library caller in one place. Accepts
  a cosmetic error-message-style inconsistency (dataclass-invariant wording vs the existing
  early-check wording), not a functional gap — both print through the same `REFUSED: {exc}`
  formatter, exit 1.

## Cold plan critic (see `PLAN_CRITIC_FINDINGS.md`)

Single critic (matching the panel-vs-single call above). Verdict: every specific file:line/behavior
claim in this plan checked out exactly against the real source, no factual drift. Seven findings,
triaged:

1. **The mission's own "trap" (name a tier for every crew dispatched, from the start) was never
   operationalized in `execute.json` — major, CONFIRMED-and-fixed.** Neither `g1-implement` nor
   `g1-review` told the Commander to pass `--model` on its OWN crew dispatch for that gate, and the
   critic traced a live failure path: `crew-dispatch.md` says nothing about model until `g2` (which
   is sequenced *after* `g1`), so during `g1` the Commander's only doctrine is silent on tier, and
   the refusal — once `g1-implement`'s code is on disk — applies to `record_external_attempt`'s
   `CrewSpec` construction too, which is how the `external` backend dispatches crews. Fixed: explicit
   "pass --model, this run's tier" lines added to both `g1-implement` and `g1-review`'s imperatives.
2. **Plan-phase dispatches (the two plan-alternative candidates, this critic) never touch
   `run_crew.py`/`crew-runs.json` at all — CONFIRMED, scoped rather than fixed.** They ran as
   native Agent-tool subagents, not through the CLI launcher this mission changes. `MISSION_FRAME.md`'s
   Intent line ("the one seam every dispatch passes through") is accurate for the `run_crew.py`
   implementer/reviewer crew-dispatch path this mission actually fixes; it does not cover every
   subagent-spawn mechanism the harness offers, and was never meant to — noted here so the scoping is
   explicit rather than silently assumed. The Commander's own dispatch record (Return Shape item 4)
   lists both kinds of dispatch this run made, each with its explicit model value, regardless of which
   mechanism recorded it.
3. **`g1-integrate`'s pytest postcondition omitted the mandatory cache-clear step — CONFIRMED-and-fixed.**
   The one postcondition the engine mechanically re-runs (`advance`, not `attest`) was the one missing
   the guard `g3-verify` already had. Fixed: `c1`'s command now clears `__pycache__` first.
4. **Two-instructions-overlap risk on the four flip-tests — CONFIRMED-and-fixed (tightened, self-correcting
   even unfixed).** `g1-implement`'s imperative now states directly that constructions missing `model=`
   need it added in the same edit as their `--effort` assertion flip, not left to the later caller-list
   survey to independently rediscover.
5. **`g2-doctrine`'s postconditions check co-occurrence, not connection, with no independent reviewer —
   CONFIRMED-not-blocking, tightened.** Defensible under Inherited Latitude (test structure is the
   Commander's to decide) and the pre-ruling's preference for the smaller change; the critic itself
   called it non-blocking. Fixed by tightening the imperative to require the Commander self-attest with
   reviewer-level rigor on the specific connecting sentence, not the grep minimum.
6. **No gate addressed `map/INDEX.md` regeneration — CONFIRMED-and-fixed.** Added to `g3-verify`'s
   imperative: check the map-tree-freshness tests, regenerate via `py -m scripts.code_map build` and
   commit if they fail, never hand-merge.
7. **Minor framing: the relaunch "ruling" describes confirming existing code behavior, not changing a
   line — CONFIRMED, cosmetic, fixed.** `PLAN_CONVERGENCE.md`'s ruling section now says so directly:
   the actual leverage point is the new refusal seam, not the relaunch line itself.

No finding invalidated the gate plan's structure (2 crew-dispatch gates + 2 reasoning gates) or the
refusal seam/relaunch-semantics decisions; all were tightening, not redesign.

## Net gate plan (see `execute.json`)

`e0-context` → `g1-implement`/`g1-review`/`g1-integrate` (code: `build_crew_argv` `effort` param +
both `CliBackend` call sites + `CrewSpec.__post_init__` refusal, ruled relaunch semantics, full
test list per Candidate B, caller-list survey as evidence) → `g2-doctrine` (reasoning gate:
`crew-dispatch.md` + a red/green test following `test_crew_delivery_addressing.py`'s pattern,
verified red at base commit `e0539903` before the doctrine edit) → `g3-verify` (reasoning gate:
full clean-env suite + re-measured `main` baseline).

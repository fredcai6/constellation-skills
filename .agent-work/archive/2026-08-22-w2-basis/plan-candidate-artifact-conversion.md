# Candidate: artifact-conversion

**Constraint (assigned):** don't invent a new check kind, a new `basis`/`because` Condition
field, or any new `attest()` code path. Convert each real `check: null` postcondition in
`skills/commander/templates/COMMANDER_SPINE.template.json` into `check: {"kind": "artifact",
"evidence_type": "<name>", "match": {...}}` wherever a genuine locator exists, and let the
engine's EXISTING artifact-check machinery (`attest`'s `chk.get("kind") == "artifact"` branch,
`scripts/checklist_engine.py:3436-3465`) do all the refusing. The "basis" is simply the
`evidence_type` + `match` shape the plan author writes on the check itself.

## 1. Does this change engine code at all?

**No.** Verified by reading, not assumed:

- `attest()`'s artifact branch (`checklist_engine.py:3436-3465`) is already fully generic: it
  reads `chk["evidence_type"]` and `chk["match"]` off whatever condition it is given, looks up
  the referenced evidence by id, and refuses on missing evidence, wrong `type`, a non-dict
  `match`, or a failed `_artifact_match_satisfied`. Nothing in that path is specific to the five
  conditions that already use it in this template (`understand.c1`, `plan.c3`, `triage.c2`,
  `review.c1`, `archive.c5`) — it is condition-shape-driven, not id-driven.
- `attach()` (`checklist_engine.py:3523-3534`) takes `etype: str` as a **completely free string**
  — there is no enum, allowlist, or validation against the `type` column in
  `docs/CHECKLIST_SCHEMA.md`'s Evidence table anywhere in the code. That table documents observed
  usage, not an enforced contract. So inventing new evidence types (`mission-frame`,
  `plan-alternatives`, `plan-critic`, ...) below requires zero code changes; the only special-cased
  `etype` in `attach()` is the literal string `"refresh-request"`, untouched by this candidate.
- `render_human()` (`checklist_engine.py:2679-2749`) never branches on `check.kind` directly. It
  renders `_condition_view(c)["kind"]` (`checklist_engine.py:2389-2397`, via `_condition_kind`),
  which already derives `"artifact"` from any condition whose `check.kind == "artifact"` — this is
  exactly how the five already-shipped artifact conditions in this same template render today.
  Converting a sixteenth condition to the same shape produces the same rendering for free: the
  `{id} [unmet] {kind} — {statement}` line simply prints `artifact` instead of `null` where the
  kind changed. No render code is touched, and the epic's own claim in the mission frame
  ("`render_human` already prints `{kind} — {statement}`... making the requirement visible without
  any render code change") is confirmed, not merely asserted.

**Conclusion: this candidate's diff is template-JSON-only** (plus a red-proof test and doc-count
corrections). No edit to `checklist_engine.py` at all. This is the central, load-bearing finding
for the comparison against the other candidates: whatever this candidate loses in coverage (see
§3 below), it gains in being the smallest possible surface — one file family, zero engine risk,
nothing to regress in the render/attest paths that every other template also depends on.

## 2. Locator-count measurement against the real 19 conditions

The 19 `check: null` conditions split structurally into **11 true postconditions** and **8
preconditions** (the mission frame's "19 postconditions" is epic-level shorthand; the actual
`Condition` objects are a mix). I converted-or-refused each one individually against the real
template text at this run's HEAD, not hypothetically.

### The 8 preconditions: none are worth converting, for a reason specific to `gated` semantics

`understand.p1`, `plan.p1`, `execute.p1` (first half), `reconcile.p1`, `triage.p1`, `review.p1`,
`feedback.p1`, `archive.p1` are all "prior gate complete" claims (`"baseline context loaded"`,
`"ask confirmed"`, `"execute complete"`, ...). In a `gated` checklist the item list is walked in
strict order and the engine will not let an agent `start` a gate whose predecessor has not
`advance`d — so by the time any of these preconditions is even evaluated, it is **already
guaranteed true by the engine's own sequencing**, independent of anything attested here. Six of
the eight are additionally redundant with a *downstream* postcondition that already is
artifact-checked (`understand.c1`, `plan.c3`, `review.c1`, `feedback.c1` already gate the facts
these preconditions restate). Manufacturing an `evidence_type` for "the prior gate finished" would
be evidence theater: a structurally-guaranteed fact re-proved by a hand-typed note pointing at
nothing new.

The one exception, `execute.p1`'s second clause ("context headroom ensured and commander skill
reloaded into this context"), is a genuine **per-invocation freshness** claim — not implied by
gate order, since it must hold again at every detached re-entry into `execute`. It has no artifact:
there is no file that proves "I just confirmed headroom." The engine already has a stronger,
purpose-built mechanism for this exact fact — the Trip gauge's SOFT/HARD bands
(`docs/CHECKLIST_SCHEMA.md` "Trip — two-band context-gauge gate policy") — which reads a live
fullness reading and gates `start`/`reopen` mechanically. Forcing this into an artifact shape would
be a strictly worse, parallel, unwired copy of a check the engine already runs.

**Verdict: 0 of 8 preconditions convert under this constraint, and none should — 7 are redundant
by construction, 1 is better served by an existing mechanism this candidate must not touch (Trip
is out of this template's postcondition surface).**

### The 11 postconditions: 5 convert cleanly, 5 resist as decorative, 1 is the wrong check kind

| id | statement (abridged) | verdict | why |
|---|---|---|---|
| `init.c1` | engine session lease claimed | **wrong kind** | The fact lives in the engine's own `engine_session` state, which the engine already knows the instant `claim` succeeds. The honest check is `command`-kind (read `spine.json`'s own `engine_session.status`), not `artifact`. Forcing an agent to *also* attach an evidence item duplicating what `claim` already recorded is pure ceremony — there is nothing external to point at. |
| `context.c1` | orchestrator/glossary/engine-config loaded; current map read | **resists (partial)** | Genuinely splits in two. The map-read half has a REAL mechanical artifact available: `scripts/context_manifest.py` already produces a per-step manifest (`build_manifest`/`write_manifest`) recording exactly which declared files were delivered, at which content hash, for the active step — a real, re-derivable locator nobody has to hand-author. But its own docstring is explicit that this is "a record of delivery, not use" — it proves the files were *available*, not that they were *read and understood*. The "loaded" half (reading comprehension of the skill's global doctrine) has no artifact at all; forcing it into `evidence_type`/`match` would just relocate the same bare assertion into a structured blob ("I confirm I loaded it") that looks enforced but checks nothing more than a hand-typed note did. Converting the whole condition would overclaim; converting only the map-read half is honest but narrower than the statement as written. |
| `plan.c1` | mission frame produced (or explicitly skipped as trivial) | **converts** | `MISSION_FRAME.md` is a real file at a fixed path (`.agent-work/<work-id>/MISSION_FRAME.md`), already independently re-verified by `plan.c6`'s own `command` check (`map_orient.py verify-frame`). `evidence_type: "mission-frame"`, `match: {"status": ["produced", "skipped-as-trivial"]}`, payload carries `{"path": ..., "status": ...}` — a reviewer can `cat` the named path. |
| `plan.c2` | execute.json authored, gates carry anchors cut from the frame, every file/decision-class in scope has its own gate | **resists (partial)** | `execute.json`'s existence converts trivially. The substantive claims — anchors genuinely *cut from* the frame (fidelity), full ownership-scope coverage — are judgment calls no `match` dict can verify; an agent can attach a technically-matching payload (`{"anchors_present": true}`) while every anchor is boilerplate. Full conversion here is the exact failure mode named in the launch order: a differently-shaped bare assertion. |
| `plan.c4` | plan-alternatives run BEFORE execute.json is authored | **converts (mostly)** | The named artifacts (`plan-candidate-*.md`, `PLAN_ALTERNATIVES.md` — this very file is one) are real, existing files a reviewer can open. `evidence_type: "plan-alternatives"`, `match: {"converged": true}`, payload `{"candidate_paths": [...], "convergence_path": "...", "converged": true}`. The one part that stays honestly open is the *ordering* claim ("BEFORE execute.json") — the condition's own statement already says this is "NOT machine-verified... nothing distinguishes a run that generated candidates before authoring execute.json from one that authored first and attested afterwards," and converting to `artifact` does not change that: file mtimes are a weak, gameable proxy, not a real locator. This candidate converts the existence half honestly and leaves the ordering claim exactly as unverified as it is today — that is a real improvement (today NEITHER half is checked) without overclaiming the part that still can't be. |
| `plan.c5` | cold plan critic run, findings dispositioned, triaged by human | **converts (mostly)** | Same shape as `c4`: `PLAN_CRITIC.md` is real. `evidence_type: "plan-critic"`, `match: {"triaged": true}`. "Cold" (no authoring context) and "triaged by human" stay attested inside the payload, not independently re-derivable — a real but partial gain. |
| `execute.c1` | every gate closed with integrated evidence | **resists** | This is a summary fact about `execute.json`'s own internal state (every child task complete, evidence attached), which the engine can read directly — it is what `command`-kind checks (and `execute.c2`'s `verify_iterative_role_artifacts.py`) are for. An `artifact` version would require an agent-typed payload asserting "all gates closed," which is exactly as trustworthy as the bare assertion it replaces unless a script computed it — at which point the honest check is `command`, not `artifact`. |
| `reconcile.c1` | map reflects the implemented changes | **converts** | The schema already ships a `file-diff` evidence type for exactly this. `evidence_type: "file-diff"`, `match: {"nonempty": true}`, payload `{"path": "docs/CHECKLIST_SCHEMA.md" (or whichever doc the change actually touched), "commit": "<sha>", "nonempty": true}` — `git show <commit> -- <path>` is a real, re-runnable locator any reviewer can execute independently of the attesting agent. |
| `triage.c1` | every triage candidate routed or recorded | **resists** | Same shape as `execute.c1`: the ground truth is `spine.json`'s own `triage_candidates` list, mechanically readable by the engine. A hand-authored "routing log" evidence item is not independently checked against that list by `_artifact_match_satisfied` (it only validates the payload the agent itself supplied), so it is a self-graded blob wearing an artifact costume. |
| `archive.c2` | branch committed and pushed | **converts** | Fully mechanical and already redundant with `archive.c2b`'s command check, which strengthens rather than weakens the case for converting `c2` specifically: `evidence_type: "command-output"` (an existing type), `match: {"exit": 0}`, payload from literally running `git rev-parse @ @{u}` (or an equivalent push-state command) — genuinely re-runnable by a stranger. |
| `archive.c3` | spine_close authorized as the sole final transition | **converts (borderline)** | Not a locator in the re-runnable-command sense — it is a procedural citation (which doctrine/launch-order text authorizes this). Consistent with the corpus's own existing convention (`archive.c5`, `review.c1`, etc. already use `evidence_type: "user-decision"` for exactly this kind of authorization citation), so converting it is *not* inventing a new pattern, just applying the one already shipped three times in this same file. Weaker than a true artifact, but strictly less decorative than a bare `attest`, since it forces a citation (e.g. `{cite: "engine-config.json:human_checkpoints"}`) a reviewer can go check. |

**Tally: 5 of 11 postconditions convert cleanly (`plan.c1`, `plan.c4`, `plan.c5`, `reconcile.c1`,
`archive.c2`), 5 resist as decorative-if-forced (`context.c1`, `plan.c2`, `execute.c1`,
`triage.c1`; `archive.c3` is a borderline 6th that converts weakly by matching an existing
corpus convention), 1 is simply the wrong check kind (`init.c1`).**

Combined across all 19 (11 post + 8 pre): **5 clean conversions, roughly 5–6 partial/weak
conversions that risk relocating the bare-assertion problem rather than solving it, 1 wrong-kind,
and 8 preconditions that shouldn't be touched at all.** Read plainly: under a pure
artifact-conversion constraint, **well under half** of the 19 conditions get a real locator. This
is the answer to `decision:locator-definition-is-yours` for this candidate specifically — a
measured negative on most of the corpus, not a hypothetical, per the launch order's Honest-Null
Clause.

## 3. Does forcing a qualitative condition into artifact shape make things worse?

**Yes, for the 5–6 conditions marked "resists" above — this is the central risk of this whole
candidate and must be said plainly rather than glossed over.** `context.c1`, `plan.c2`,
`execute.c1`, and `triage.c1` are, at bottom, "did you understand X" or "does this internal state
hold" conditions with no independent artifact. If a plan author converts them anyway (to hit a
target conversion percentage, say), the predictable failure mode is: the agent attaches a
one-line evidence item — `{"reviewed": true}`, `{"routed": true}` — that trivially satisfies
`_artifact_match_satisfied` and is **strictly harder to see through than the plain-prose bare
assertion it replaced**, because it now *looks* engine-checked (it renders as `artifact`, it went
through `attest --evidence`, it shows up as `attested: {...}` on the condition) while proving
exactly nothing a reviewer could not have gotten from the free-text note. A `check: null`
condition is at least honestly labeled as socially-verified; a decorative `artifact` condition
launders the same bare assertion through a mechanism whose whole point was to stop that. **This
candidate's explicit recommendation is: do NOT convert those 5–6.** Leave them `check: null`,
honestly. Converting only the 5 that have real locators, and refusing the rest, is the whole
value of measuring first.

## 4. Gate sequence (Commander `execute.json`-shaped)

```
g1-author-conversions
  imperative: |
    Hand-edit skills/commander/templates/COMMANDER_SPINE.template.json surgically (compact-format
    JSON, never round-tripped through json.load/json.dump per doctrine). Convert exactly the 5
    conditions measured as clean conversions in §2: plan.c1, plan.c4, plan.c5, reconcile.c1,
    archive.c2. For each, replace `"check": null` with `"check": {"kind": "artifact",
    "evidence_type": "<name>", "match": {...}}` using the shapes specified in §2's table. Leave
    the statement text unchanged (it already renders under the new kind with no other edit). Do
    NOT touch init.c1, context.c1, plan.c2, execute.c1, triage.c1, or any precondition — those
    stay check: null per §3's finding. Sync the corresponding block in .agent-work/templates/
    (overlay mirror + .baseline copies) so the shipped template and the overlay do not diverge —
    see MISSION_FRAME.md's Structural Anchors on this.
  close criteria:
    - the 5 named conditions carry check.kind == "artifact" with evidence_type/match populated
    - no other condition in the file changed
    - .agent-work/templates/ overlay in sync with the shipped template
    - the file remains valid JSON (parse-check only, never reformatted)
  required evidence: file-diff (the hand-edited template + overlay), command-output (a JSON
    parse-validate command run against both copies)
  constraints: hand-edit only; never json.load/json.dump the template; touch no other
    check:null condition; touch no file outside skills/commander/templates/ and
    .agent-work/templates/

g2-red-proof
  imperative: |
    Add a pytest test to tests/test_checklist_engine.py (or a sibling test module in the same
    file, following the corpus's existing property-test idiom, e.g. near the artifact-check
    tests) that: (a) loads COMMANDER_SPINE.template.json at this gate's shipped revision
    (pin the git blob OID or commit sha per ruling-red-proof-pinned-to-shipped-revision, so the
    test cannot silently start passing against a different future template); (b) for at least
    one of the 5 newly-converted conditions (e.g. plan.c1), drives the checklist to that gate and
    calls attest() with no --evidence, asserting it raises EngineError with the existing "attest
    it by referencing an already-attached artifact" message (checklist_engine.py:3438-3441); (c)
    attaches a wrong-type evidence item and asserts attest() still refuses (wrong evidence_type
    branch, line 3450-3454); (d) attaches a correctly-typed but non-matching evidence item and
    asserts refusal (match branch, line 3460-3461); (e) attaches a correctly-typed, matching
    evidence item and asserts attest() SUCCEEDS. This is exactly the existing artifact-check test
    shape already proven for understand.c1/plan.c3/etc — the point of this gate is to show it
    holds for the newly-converted conditions specifically, not to invent new engine test
    machinery.
  close criteria: new test(s) exist, are red against a template where the check was left as
    check: null (i.e., demonstrably would have failed before g1), and are green after g1's edit;
    `pytest tests/test_checklist_engine.py` passes in full
  required evidence: command-output (pytest run, full suite green)
  constraints: no new attest()/attach()/render_human() code — this gate is proof the EXISTING
    code already does the job; if the test requires ANY engine code change to pass, that is a
    signal this candidate's premise (zero engine changes) is wrong and must be escalated, not
    quietly patched around

g3-wire-the-existing-checks
  imperative: |
    "No unwired checker" (ruling-no-new-unwired-checker) is satisfied by construction here — the
    5 converted conditions are exercised by g2's pytest test (which runs in CI) AND, separately,
    by every real Commander run through this template's own attest() call at that gate. Confirm
    both: (a) g2's test is discovered by the existing pytest collection (no new marker/skip needed);
    (b) tests/test_checklist_engine.py's GoldenOutputBriefing class (~3779 on), which pins
    render_human's exact output against every shipped template, is updated for the 5 changed
    lines (each now renders `artifact` instead of `null` in its unmet-condition line) — this is
    the one place this candidate's diff DOES touch existing render-adjacent test fixtures, not
    render code itself, and it is the mechanism that makes a future accidental revert of g1
    visible (golden test goes red).
  close criteria: GoldenOutputBriefing green with updated fixtures for the 5 lines; full
    tests/test_checklist_engine.py suite green
  required evidence: command-output (pytest, full file)

g4-doc-counts
  imperative: |
    docs/CHECK_SCRIPT_CENSUS.md:126-127 currently reads `grep -c '"because"' ... -> 0` and cites
    19 check:null conditions in this template. After g1, that count is 14 (19 - 5). Update the
    census line and its surrounding prose to the new count, dated to this run, so the next reader
    does not re-run the grep and find a stale claim. This is the reconcile-shaped step for this
    candidate: no packet map exists, so the structural record this run folds into is
    docs/CHECK_SCRIPT_CENSUS.md and docs/CHECKLIST_SCHEMA.md directly (per MISSION_FRAME.md's Map
    Confidence section), not a Cartographer map.
  close criteria: docs/CHECK_SCRIPT_CENSUS.md's grep-derived counts match a freshly re-run grep
    against the post-g1 template
  required evidence: command-output (the re-run grep, pasted alongside the doc edit)

g5-live-vs-report-only-decision
  imperative: |
    Answer explicitly, in the plan-approval record, whether ruling-widening-live-refusal-report-
    only applies to this candidate's 5 converted checks. See §5 below for the argued position
    (it does not apply — this is reuse of an already-blocking mechanism, not a new refusal
    surface) — surface that argument to the human/Admiral for ratification rather than deciding
    unilaterally, since the ruling's default is report-only absent an in-hand adjudication.
  close criteria: a recorded human/Admiral decision on live-vs-report-only for these 5 checks
  required evidence: user-decision
```

## 5. Live-blocking vs report-only: does the ruling even apply?

**Argued position: no, `ruling-widening-live-refusal-report-only` does not govern this
candidate's checks, and they should ship blocking-live on merge with no promotion trigger.**

The ruling exists to gate a **new** refusal surface — some new mechanism that did not previously
exist and might misfire against real runs before it is proven. This candidate introduces no such
surface: `attest()`'s artifact-refusal branch is not new code written by this epic; it is the
exact same code path already blocking, live, in production, on 5 other conditions in this same
template today (`understand.c1`, `plan.c3`, `triage.c2`, `review.c1`, `archive.c5`). Converting
`plan.c1`/`plan.c4`/`plan.c5`/`reconcile.c1`/`archive.c2` to the same shape does not widen what
the engine can refuse — it applies an already-battle-tested refusal to five more conditions in a
file that already lives under that refusal for a third of its postconditions. There is no new
failure mode to observe report-only before trusting.

**The honest counter-argument, stated so it isn't buried:** there IS a real behavior change for
the agents running this template — 5 conditions that could previously be closed by a bare
`attest` note now require a resolvable evidence item, and an agent mid-run that doesn't know this
changed will hit a live refusal it didn't expect, mid-gate, on a template that gates a huge
fraction of the corpus's actual work (every Commander run uses this spine). That is a real
operational risk independent of whether the *code* is new. My recommendation is still blocking-
live, because: (a) the refusal message is self-explanatory and names the exact fix (`attest it by
referencing an already-attached artifact via --evidence <id>` — checklist_engine.py:3438-3441,
verbatim, unchanged by this candidate); (b) every agent running this spine already handles this
exact refusal shape today for the 5 pre-existing artifact conditions, so the failure mode is not
novel to them; (c) a report-only version of an artifact check has no obvious meaning — `attest`
either resolves the evidence or it raises, there's no "report but proceed" version of `attest`
itself the way there is for a `command` check's `--report-only` flag (that flag lives on
`command`/`git-change-policy` checks specifically, per `docs/CHECKLIST_SCHEMA.md`; no equivalent
exists for `artifact`, and adding one WOULD be new engine code, which this candidate's constraint
forbids). Shipping report-only would therefore require inventing exactly the kind of new
mechanism this candidate exists to avoid. **g5 above surfaces this as a decision rather than
deciding it unilaterally** — but the recommendation on the table is live-blocking, un-gated by the
ruling, because nothing new is being widened.

## 6. Tradeoffs

- **Depth:** shallow, by design. This candidate proves the mechanism works for the conditions
  that already have real locators and refuses to pretend for the rest. It does not attempt the
  "did you understand X" conditions at all — that is depth deliberately left off the table, not
  missed.
- **Locality:** as local as it gets. Zero engine-code diff; the entire change lives in one
  template file (plus its overlay mirror), one new pytest test, and two doc-count corrections.
  Nothing else in the corpus can regress from this candidate landing, because nothing outside
  this one template's check shapes changed.
- **Seam placement:** the seam is exactly where the epic's mission frame said it should be — the
  plan-authoring moment, on the `check` field itself, using the render/attest split that already
  exists (`render_human` already prints kind+statement; `attest`'s artifact branch already
  refuses). No new seam was cut; an existing one was reused for more conditions.
- **Testability:** strong for the 5 converted conditions (mechanically checkable, red-proofed by
  g2, golden-output-pinned by g3) and honestly unchanged for the other 14 (still socially
  verified, same as before this candidate). The candidate does not claim to have improved
  testability for the conditions it declined to convert — see §3.
- **Coverage vs honesty tradeoff, stated once more because it's the whole finding:** this
  candidate trades coverage (26% of the 19, or 5/11 of the true postconditions) for zero false
  confidence. A candidate willing to accept the §3 risk (decorative evidence blobs on
  qualitative conditions) could claim a higher conversion percentage — but per the launch order's
  own Honest-Null Clause, that higher number would be measuring the wrong thing.

## 7. Verdict

**This constraint genuinely works, but only against the minority of conditions that have a real
locator.** It is not a rollout mechanism for the full 19 — it is a precise tool for the ~5
conditions (mission frame produced, plan-alternatives run, plan-critic run, map reconciled,
branch pushed) that were ALREADY, secretly, "did you produce artifact X" conditions wearing
`check: null`'s clothing. For those, this candidate is close to free: no engine risk, reuses a
proven refusal, and the render path needs no code change at all — the smallest possible diff of
any candidate in this comparison. For the remaining 14 (8 preconditions redundant by gate-order
or better served by Trip, and 6 postconditions that are genuinely "did you understand/judge X"
with no artifact to point at), this candidate's own constraint is the wrong tool, and it says so
rather than forcing a fit. If the epic wants those 6 covered too, that is a DIFFERENT candidate's
job — most plausibly one that adds a genuinely new, lighter-weight field (a `because` string
rendered and required-non-empty, not required-resolvable) for conditions that are inherently
prose, while this candidate's artifact-conversion handles the conditions that were never really
prose to begin with. Recommend picking up this candidate's 5 conversions regardless of what wins
the broader comparison — they are correct and nearly free independent of which basis mechanism
the epic settles on for the rest.

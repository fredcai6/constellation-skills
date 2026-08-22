# Plan Candidate — constraint: `structured-field`

Work-id: `w2-basis` (epic 569, wave 2). Constraint under test (per launch order): the
"basis" for a `check: null` condition is a **new, explicit sibling field on the
`Condition` schema** — a `basis` object carrying a locator-kind + locator-value —
analogous to how `override_policy` already sits beside `check`. `render_human`/
`state()`/`_condition_view` render it (populated-only, like `constraints`/
`anchors`/`directives`); `attest()` gets a new branch that validates the locator
against its declared kind before accepting the condition as satisfied.

This document is one candidate in a design-it-twice panel. It does not decide
anything; a human converges across candidates at `PLAN_ALTERNATIVES.md`.

---

## 1. The design: `basis` field shape

Sibling of `check` on a `Condition`, like `override_policy`:

```json
"basis": {
  "locator_kind": "file" | "evidence_ref" | "state_field" | "command" | "abstain",
  "locator": { ...kind-specific... },
  "because": "<optional one-line authoring rationale, never a substitute for locator>"
}
```

Absent `basis` (the status quo for 46 of the corpus's 65 `check: null` conditions,
and for any condition where authoring one would be dishonest) means exactly what
it means today: a bare assertion, unchanged behavior. `basis` is additive and
opt-in per condition — no existing condition's semantics change by this field's
mere existence in the schema.

Four **expressive** locator kinds, plus one **honest-abstention** kind:

1. **`file`** — `{"path": "<repo- or work-id-relative path>", "glob": bool,
   "min_matches": int}`. Points at a durable artifact the agent must produce.
   Attest resolves the path (or glob) against the filesystem at `base_dir`;
   unresolved = a named problem, not silent pass.
2. **`evidence_ref`** — `{"task_id": "<id>", "cond_id": "<id>"}`. Points at
   *another* condition's already-attached evidence (a backref), so a duplicate
   claim doesn't re-attach the same artifact twice. Attest resolves by walking
   `cl["tasks"][task_id]` for `cond_id`, requiring it `satisfied` with a
   non-null `satisfied_by`/evidence.
3. **`state_field`** — `{"path": "<dotted path into the checklist dict>",
   "expect": <value>}`. Points at the engine's own state (e.g. a prior task's
   `status`, or `engine_session.status`). Attest resolves the dotted path
   against live `cl` and compares.
4. **`command`** — `{"command": "<shell string>"}`. A command a stranger can
   re-run to inspect the claim. Attest **executes it and records the output as
   evidence** (same `command-output` shape the engine already uses for
   `check.kind == "command"` failures) rather than trusting a hand-typed note —
   this is deliberately NOT a blocking exit-code gate (that's what `check:
   {kind: command}` is already for); it is evidence capture attached to a
   condition the corpus still treats as socially, not mechanically, verified.
5. **`abstain`** — `{"reason": "<why no resolvable locator exists>"}`. An
   explicit, documented decision that this condition's claim has no durable
   locator to point to. Attest behaves exactly as the unmodified legacy path
   (bare assertion accepted). This is the field's escape hatch for the
   Honest-Null Clause: a condition that genuinely cannot express a locator gets
   a *recorded* abstention, not a silently absent field indistinguishable from
   "nobody got around to it."

### Engine changes (sketch, not full code)

**`render_human`** (checklist_engine.py, ~2679-2749): inside the
`preconditions`/`postconditions` loop that currently emits
`f"  {c['id']} [unmet] {c['kind']} — {c['statement']}"`, append one indented
sub-line when `c.get("basis")` is populated and `locator_kind != "abstain"`:

```python
for c in open_conds:
    lines.append(f"  {c['id']} [unmet] {c['kind']} — {c['statement']}")
    basis = c.get("basis")
    if basis and basis.get("locator_kind") != "abstain":
        lines.append(f"    basis: {_render_basis_line(basis)}")
```

`_render_basis_line(basis)` is a small total function (same pattern as
`_directive_leaf`/`_render_anchor_lines`) that formats each `locator_kind`'s
`locator` dict into one human line, e.g. `file .agent-work/<work-id>/MISSION_FRAME.md`
or `evidence_ref understand.c1` or `state_field engine_session.status == active`.
Emitted only when populated — same rule `constraints`/`anchors`/`directives`
already follow, so `TaskFieldCompleteness`-style coverage extends cleanly
rather than inventing a second rendering convention.

**`attest`** (checklist_engine.py, ~3404-3472): the existing
`check is None` branch —

```python
if chk is None:
    c["satisfied"] = True
    c["satisfied_by"] = note or "attested"
    return f"attested {iid}.{cond_id}"
```

gets a new guard inserted before the unconditional accept:

```python
if chk is None:
    basis = c.get("basis")
    if basis and basis.get("locator_kind") != "abstain":
        problem = _resolve_basis_locator(cl, base_dir, basis)
        if problem:
            enforcement = _basis_enforcement_mode(cl, config)  # "report-only" | "blocking"
            if enforcement == "blocking":
                raise EngineError(
                    f"{cond_id}: basis unresolved ({basis['locator_kind']}) — {problem}"
                )
            _record_basis_report(cl, iid, cond_id, basis, problem)  # non-blocking evidence
    c["satisfied"] = True
    c["satisfied_by"] = note or "attested"
    return f"attested {iid}.{cond_id}"
```

`_resolve_basis_locator(cl, base_dir, basis) -> str | None` is a small pure-ish
dispatcher (impure only for `file`/`command`, pure for `evidence_ref`/
`state_field` — same pure/impure split the schema doc already documents for
`git-change-policy`'s evaluator/collector). Returns `None` when resolved, else
a human-readable problem string. `_basis_enforcement_mode` reads a new
Charter-owned config key (see §3, gate g6) defaulting to `"report-only"`.

---

## 2. Locator-count measurement — the real 19 conditions

`COMMANDER_SPINE.template.json` carries **19** `check: null` conditions total
(8 preconditions + 11 postconditions — the mission frame's "19 postconditions"
figure folds both lists together; re-counted this run by walking the live
JSON, matching `docs/CHECK_SCRIPT_CENSUS.md`'s "0 because, 19 check:null"
claim). Applying the four expressive locator kinds above to each, by hand:

| # | task.cond | statement (short) | locator kind that fits | genuine? |
|---|---|---|---|---|
| 1 | init.c1 | engine session lease claimed | `state_field` `engine_session.status == active` | genuine |
| 2 | context.c1 | context/glossary/config loaded; map read | `file` `.agent-work/<work-id>/map-orientation.json` (the orient receipt) | genuine |
| 3 | understand.p1 | baseline context loaded | `state_field` `tasks.context.status == complete` | weak/circular |
| 4 | plan.p1 | ask confirmed | `evidence_ref` → `understand.c1` (user-decision) | genuine |
| 5 | plan.c1 | mission frame produced | `file` `.agent-work/<work-id>/MISSION_FRAME.md` | genuine |
| 6 | plan.c2 | execute.json authored, ownership-scoped | `file` `.agent-work/<work-id>/execute.json` | genuine |
| 7 | plan.c4 | plan-alternatives run before execute.json | `file` glob `.agent-work/<work-id>/plan-candidate-*.md` (min 2) + `.agent-work/<work-id>/PLAN_ALTERNATIVES.md` | genuine, ordering residual |
| 8 | plan.c5 | cold plan critic run, triaged | `file` `.agent-work/<work-id>/PLAN_CRITIC.md` | genuine, ordering residual |
| 9 | execute.p1 | plan approved; headroom ensured; skill reloaded | *no locator for the headroom/reload half* | **degenerate** |
| 10 | execute.c1 | every gate closed with integrated evidence | `file`/state-walk over `.agent-work/<work-id>/execute.json` | genuine |
| 11 | reconcile.p1 | execute complete | `state_field` `tasks.execute.status == complete` | weak/circular |
| 12 | reconcile.c1 | map reflects implemented changes | *target doc not fixed at template-authoring time* | **degenerate** |
| 13 | triage.p1 | reconcile complete | `state_field` `tasks.reconcile.status == complete` | weak/circular |
| 14 | triage.c1 | every triage candidate routed | *restates the engine's own `triage_candidates` field* | **degenerate** |
| 15 | review.p1 | triage complete | `state_field` `tasks.triage.status == complete` | weak/circular |
| 16 | feedback.p1 | run summary accepted | `evidence_ref` → `review.c1` (user-decision) | genuine |
| 17 | archive.p1 | workflow feedback recorded | `evidence_ref`/`file` → `feedback.c1`'s episode-capture evidence | genuine |
| 18 | archive.c2 | branch committed and pushed | `command` `git log origin/<branch>..<branch>` (or `git status --porcelain` for commit half) | genuine |
| 19 | archive.c3 | spine_close authorized as sole final transition | *pure procedural/authorization claim, no artifact* | **degenerate** |

**Headline count**: 11/19 (58%) express a locator that is genuinely concrete —
a stranger could go look at the named file, evidence id, state field, or
command output and confirm or refute the claim without re-reading prose. 4/19
(21%) degenerate into either restating the statement in a different field or
have no artifact to point to at all. The remaining 4/19 (21%) are real but
**weak/circular**: they resolve, but only to "the previous gate's own status
field says complete" — information the engine's own precondition machinery
already has adjacent to, and arguably could derive without an authored
locator at all.

**The more important number, on inspection**: of the 11 "genuine" locators,
**9 do not need a new schema field to get render+require at all** — they
could be satisfied *today*, with zero new code, by simply flipping their
existing `check` from `null` to `{"kind": "artifact", ...}` (conditions 4, 16
— duplicate an existing user-decision evidence item — or 1, 2, 6, 10, 17, 18
via `{"kind": "command"}` — a lease-state probe, a file-existence/JSON-shape
test, a git-ref comparison). The schema already supports exactly this; no
`basis` field is required for that band. Only **2 of 19** (plan.c4, plan.c5)
get *unique* value from a brand-new sibling field: their locators (files
exist) are checkable, but their real claim — "candidates converged to one
recommendation," "findings were triaged" — is a judgment a mechanical
`command`/`artifact` check cannot make, so a rendered pointer that is still
*required to resolve to something* at attest (file present, non-empty, ≥2
candidates) without pretending to judge content quality is the one place this
constraint earns something neither existing check kind nor a bare assertion
already gives.

This is the answer to `ruling-locator-definition-is-yours`, stated plainly
per the Honest-Null Clause: **the structured-field constraint is
implementable and honest against the real 19, but its unique marginal value
is narrow — 2 of 19 conditions, not 11 of 19.** The other 9 "genuine" cases
are better served by promoting `check` itself (out of this candidate's scope
but worth naming as an untaken road, see §5).

---

## 3. Gate sequence (Commander `execute.json`-shaped)

Each gate below: imperative (compressed), close criteria, required evidence,
constraints. All target only `checklist_engine.py` + `COMMANDER_SPINE.template.json`
+ `docs/CHECKLIST_SCHEMA.md` + `tests/test_checklist_engine.py` +
`docs/agents/engine-config.json`, per the launch order's scope fence.

**g1 — schema doc: author the `basis` field**
Imperative: add a `basis` subsection under Condition in
`docs/CHECKLIST_SCHEMA.md` (the five locator kinds, the sibling-of-`check`
placement, the populated-only rendering rule) and extend the *Rendering*
section's populated-only list to include it.
Close criteria: doc diff reviewed; no code yet.
Required evidence: diff.
Constraint: doc-only gate, no `generate_spine.py`/`specs/` touch.

**g2 — engine: render + resolve**
Imperative: implement `_render_basis_line`, the `render_human` sub-line
insertion, `_resolve_basis_locator` (four resolvable kinds; pure for
`evidence_ref`/`state_field`, thin-impure for `file`/`command` mirroring the
`git-change-policy` evaluator/collector split), and the new `attest()` guard
(report-only by default — see g6 for the config flag).
Close criteria: unit tests for `_resolve_basis_locator` cover all 4 kinds ×
{resolved, unresolved}; `render_human` golden-output tests updated for a
fixture condition carrying each locator kind; existing `GoldenOutputBriefing`
suite still green.
Required evidence: diff, `pytest tests/test_checklist_engine.py` output.
Constraint (dogfooding): validate via a fresh `python scripts/checklist_engine.py
...` CLI call against a throwaway fixture checklist or pytest — never by
re-querying this run's own live MCP door bound to the engine being edited.

**g3 — red proof: the refusal actually refuses**
Imperative: add `tests/test_checklist_engine.py::BasisLocatorRefusal` (or
equivalent class) that: (a) attests a `check: null` condition whose `basis`
has an unresolved `file` locator under `report-only` mode — assert it
**succeeds** (non-blocking) and a report record is attached; (b) flips
enforcement to `blocking` and re-attests the same unresolved condition —
assert `EngineError` is raised, naming the condition and the unresolved
locator; (c) fixes the fixture (creates the file) and re-attests under
`blocking` — assert it succeeds. Pin the fixture to a specific checklist
shape at this run's HEAD (per `ruling-red-proof-pinned-to-shipped-revision`).
Close criteria: test is red before g2's guard exists (confirm by running
against the pre-g2 revision or a stash), green after; committed alongside g2
or as its own follow-up commit.
Required evidence: pytest output showing the red→green transition (two runs,
or a single commit whose diff review shows the assertion previously failed).

**g4 — author basis into the 19 conditions**
Imperative: hand-edit `skills/commander/templates/COMMANDER_SPINE.template.json`
surgically (never round-tripped through `json.load`/`json.dump`) to add a
`basis` sibling to each of the 19 `check: null` conditions per the table in
§2: 11 with a real `file`/`evidence_ref`/`state_field`/`command` locator, 4
weak/circular ones with the `state_field` locator anyway (documented as
low-marginal-value in a `map_check_note`, not silently omitted), and 4 with
an explicit `abstain` block naming why no locator exists (execute.p1's
headroom/reload half, reconcile.c1's unfixed-target problem, triage.c1's
engine-internal-field restatement, archive.c3's pure-authorization claim).
Sync the `.agent-work/templates/` overlay mirror and its `.baseline` copy
(Inherited Context anchor) to match.
Close criteria: `grep -c '"basis"' skills/commander/templates/COMMANDER_SPINE.template.json`
== 19; `TemplateOnlyFieldAllowlist`/`TaskFieldCompleteness` tests (or their
extension) confirm `basis` is a *rendered* field, not a new template-only
prose field; overlay/baseline diff matches shipped template.
Required evidence: diff (both copies), grep count, pytest output.

**g5 — wire a check that can fail: basis-coverage regression**
Imperative: add a pytest test (e.g.
`test_commander_spine_basis_coverage`) that walks the shipped
`COMMANDER_SPINE.template.json`, asserts every `check: null` condition
carries a `basis` key (real locator or explicit `abstain` — no silent
absence), and self-tests by mutating a fixture copy to drop one `basis` and
confirming the assertion goes red. This is the mechanism satisfying
`ruling-no-new-unwired-checker`: it runs in the existing pytest suite (local
+ CI), so a future edit to the template that adds a new `check: null`
condition without an authored basis (or documented abstention) fails this
test rather than silently regressing to decorative.
Close criteria: test collected and green in the full suite; red-then-green
self-test included (same discipline as `TaskFieldCompleteness`'s in-suite
negative self-test).
Required evidence: pytest output.

**g6 — promotion-trigger config**
Imperative: add `"basis_attest_enforcement": "report-only"` to
`docs/agents/engine-config.json` (Charter-owned), with an inline comment (or
adjacent doc note in CHECKLIST_SCHEMA.md) naming the **promotion trigger**:
promote to `"blocking"` only after the report-only log shows zero cases,
across at least 10 real Commander runs using the updated template, where the
locator-resolution verdict disagreed with the human's own accept/reject
judgment at that gate. Wire `attest()`'s `_basis_enforcement_mode` to read
this key (default `report-only` if absent, so an un-upgraded config keeps
today's behavior).
Close criteria: config round-trip test; regression test confirms all 19
conditions still attest successfully today (report-only, no behavior change)
even with an intentionally-unresolvable fixture locator.
Required evidence: diff, pytest output.

**g7 — reconcile**
Imperative: fold the structural change into `docs/CHECKLIST_SCHEMA.md`
(already mostly done at g1; final sync after implementation lands) and add a
short note to `docs/CHECK_SCRIPT_CENSUS.md` recording this proof-of-concept's
measured coverage (11 genuine / 4 weak / 4 abstain of 19; 2/19 unique
marginal value over existing check kinds) so the next reader doesn't
re-derive it. No packet map exists to reconcile into (DEGRADED-UNPARSEABLE,
per the mission frame), so this gate targets the schema/census docs directly.
Close criteria: doc diff reviewed.
Required evidence: diff.

---

## 4. Tradeoffs

**Depth.** Additive and opt-in: `basis` absent means unchanged legacy
behavior, so none of the other 46 `check: null` conditions in the corpus (nor
any condition in this template without an authored basis) are affected. Good
depth in isolation. But the measurement in §2 exposes a real smell: for 9 of
the 11 "genuine" cases, this candidate builds a *second*, softly-enforced
mechanism for "point at a real thing" beside the schema's *existing*,
hard-enforced one (`check: {kind: artifact|command}`). Two ways to express
the same underlying fact (a resolvable locator exists) is exactly the kind of
depth cost the constraint should be judged against, not just whether it
compiles cleanly.

**Locality.** Genuinely contained: `checklist_engine.py` (two functions
extended, one new pure-ish helper, one new attest branch), one template, one
schema doc, one new/extended test module, one config key. No fan-out into
`generate_spine.py`, `specs/`, or the other 19 shipped templates. Matches the
launch order's scope fence exactly.

**Seam placement.** Reuses two seams that already exist and are already
tested: the `constraints`/`anchors`/`directives` populated-only rendering
convention in `render_human`, and the `check is None` branch in `attest()`
(the guard is inserted, not a new branch that duplicates dispatch logic). No
new seam invented.

**Testability.** Strong: 3 of 4 locator kinds resolve with pure functions
(no filesystem/subprocess for `evidence_ref`/`state_field`; `file` is a thin
`Path.exists()`/glob call; only `command` needs subprocess, and it mirrors
the git-change-policy pure-evaluator/impure-collector split the schema
already documents). The report-only/blocking split is a single flag,
straightforward to red-proof (g3) without any live-refusal risk to existing
runs.

---

## 5. Honest verdict

The structured-field constraint **works** — it is implementable, honest under
the Honest-Null Clause (the `abstain` kind means no condition is forced into
a fake locator), reuses existing tested seams, and stays inside scope. Against
the real 19 conditions it produces 11 genuine locators, 4 honest abstentions,
and 4 weak-but-real circular ones.

But the measurement also surfaces a materially important negative: **most of
the value this candidate produces (9 of its 11 "genuine" locator conditions)
does not require a new schema field at all** — it requires promoting an
existing `check: null` to an existing `{kind: artifact}` or `{kind: command}`
check, which the engine already renders (via the existing condition-kind
label) and already requires at attest, with zero new code. The *unique*
contribution of a brand-new `basis` sibling field, measured rather than
assumed, is narrow: it earns its keep specifically for **plan.c4** and
**plan.c5** — conditions where a durable artifact exists to point at, but the
actual claim (convergence happened, triage happened) is a judgment call no
mechanical check can make, so "render a required pointer, still attest the
judgment socially" is a real third option between "bare assertion" and "hard
mechanical check" that neither existing check kind offers.

Per the Honest-Null Clause, this is a complete, valuable answer to
`ruling-locator-definition-is-yours`, not a failure: the structured-field
shape should ship (it is the only shape among file/evidence/state/command
that stays honest about `abstain`), but the conversion decision this wave
approves should not claim 11-of-19 "coverage" as the win — the honest framing
is 2-of-19 unique value from the new field, 9-of-19 already reachable by
promoting `check` itself (a smaller, more standard-shaped change worth naming
as an untaken road for the human converging across candidates), 4-of-19
honest abstention, and 4-of-19 low-value circular state checks that could be
dropped without loss. A converging human should weigh whether shipping a new
schema field for a 2-condition payoff, plus the discipline cost of a second
"pointer" mechanism living beside the existing one, is worth it against a
narrower alternative that only touches `plan.c4`/`plan.c5` and promotes the
other 9 via existing `check` kinds instead.

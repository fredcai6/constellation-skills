# Triage recommendations — `epic-559/c2-generate-the-spine`

**Disposition for every candidate below: `recommend-and-defer`.** The deferral reason is the same for
all six and it is not a judgment call: the launch order states *"`triage.c2` (user approved issue
creation) — **no issues are created this wave.** Route every triage candidate to me in your return
report instead."* Filing authority was therefore neither unclear nor unavailable — it was **explicitly
withheld**, so nothing here is filed and every recommendation is issue-ready for the Admiral to file or
reject.

**Fix-now ladder: none of the six qualifies.** Each fails at least one rung, named per candidate. Two
were tempting — tc2 and tc5 are both small diffs — and both fail the *adjacent-to-current-scope* and
*no-production-default-impact* rungs. Clearing three of four does not qualify.

All observations are `type: measured` unless stated, and every `rev` is this branch at the commit named.

---

## tc1 — a Commander cannot drive its own `execute.json` through the MCP door

**Labels:** architecture weakness · tooling · unresolved decision
**Priority:** high — it contradicts a categorical human ruling and it silently forces every Commander onto the CLI.
**Ladder:** fails *bounded diff* and *no architecture impact*.

**Observation.** `scripts/mcp_spine_server.py` binds exactly one file at import time —
`SPINE = Path(os.environ["SPINE_FILE"]).resolve()` (line 106) — and exposes no per-call spine
addressing on any of the nine door tools. The Commander spine's own `execute` step requires driving a
**second** checklist (`execute.json`).
*Expected:* everything a spine needs is reachable through MCP. The human's ruling is verbatim:
*"anything that we want to do for the spine needs to be accessible via mcp. the agents should not know
about the cli. period. anything that we can only do via the cli is a defect."*
*Conditions:* any Commander run, this environment, `SPINE_FILE` bound at launch by `run_crew.py`.
*type:* measured — read the source, then drove `execute.json` through `checklist_engine.py` directly
because no door verb can name a second file. *rev:* `0b27b2b8`.

**Why it matters more than the four `<engine>` tokens.** The tokens are the same defect's *symptom*.
No token substitution fixes this: the door has no verb that can address a second file. **This is why I
declined to fix the tokens this wave** — resolving them would make the instruction readable while the
underlying defect stayed, converting a loud defect into a quiet one.

**Possible fix (hypothesis).** A door tool that drives a named child checklist, or an optional
`file` argument validated against a whitelist rooted at the bound spine's work area.

**Open question.** Is a Commander's `execute.json` conceptually a *second spine* or a *child of the
first*? If the latter, the door could address it by relationship rather than by path.

---

## tc2 — `recover_crews.py` misclassifies a completed spine-only dispatch as `NEEDS-ABANDON`

**Labels:** bug · tooling
**Priority:** high — it produces exactly the failure the tool exists to prevent.
**Ladder:** fails *adjacent to current scope* and *no production-default impact*.

**Observation.** `run_crew.py` completed `constellation/epic-559/c2-generate-the-spine/g3-dispatch/spine-probe/attempt-2`
on `spine_terminal` and wrote `status: "completed"`, `completed_at` set, `result: None` into
`crew-runs.json`. `recover_crews.py` then reported for that same entry:
`NEEDS-ABANDON — not running and no result; require explicit --abandon ... --relaunch`.
*Expected:* a completed crew classifies as complete. `classify_entry` keys on a **result artifact**,
which a spine-only dispatch deliberately never writes — `run_crew.py --result` is documented as
optional when `--spine` is given, precisely because such a crew is judged on its spine reaching a
terminal state instead.
*Conditions:* any `--spine`-only dispatch; both files as shipped at this rev.
*type:* measured — both outputs observed in the same session, minutes apart. *rev:* `0b27b2b8`.

**Consequence.** Crew-dispatch doctrine tells a resumed Commander to run `recover_crews.py` **first**,
before assuming any dispatch is needed, specifically so it does not duplicate a crew whose work is
already done. For a spine-only dispatch the tool now advises exactly that duplication.

**Possible fix (hypothesis).** When `result` is `None` and `spine` is set, classify on
`status == "completed"` and/or the bound spine's terminal state, mirroring the completion contract
`run_crew.py` already applies.

---

## tc3 — `load_config` crashes on a `config_ref` that exists but is not JSON

**Labels:** bug · missing test
**Priority:** medium.
**Ladder:** fails *no production-default impact* (it is engine behaviour) and *adjacent to scope*.

**Observation.** `checklist_engine.load_config` calls `json.loads` on any `config_ref` whose path
**exists**. A `config_ref` pointing at a real non-JSON file raises an unhandled `JSONDecodeError` from
`main()` before any rail text can print.
*Expected:* a visible refusal naming the file, in the engine's own refusal shape.
*Conditions:* `config_ref` set to an existing non-JSON path. A **missing** path falls through to `{}`
and is harmless — which is why every shipped template's nonexistent `docs/agents/engine-config.json`
is fine, and why this has gone unnoticed.
*type:* measured — hit live while wiring this run's own `execute.json`, which pointed `config_ref` at a
markdown file. *rev:* `0ab7ecab` (pre-existing; unchanged by this wave).

**Second observation, same defect family.** `scripts/validate_spine.py` carries **no fault** for this
shape, so the lint reports a spine clean that the engine cannot load. *type:* measured — read
`validate_spine.py` in full; no `config_ref` handling exists. *rev:* `0b27b2b8`.

**Note.** `generate_spine.py` refuses it as `spec-config-ref-not-json` at the spec layer. That protects
generated spines only; hand-authored ones are unprotected. **The oracle was not moved** — that is a
float, not a Commander's patch.

---

## tc4 — this repo's map scaffolding makes every Commander structurally DEGRADED

**Labels:** missing architecture packet · stale generated map
**Priority:** medium — it is a recurring per-run tax, not a break.
**Ladder:** fails *bounded diff* and *adjacent to scope*.

**Observation.** `map_orient.py orient` probes five candidates and all five miss: `docs/architecture/generated/map.json`
absent, `docs/architecture/index.md` absent, `docs/architecture/` absent, `map/INDEX.md` present but
`unparseable (content but no citable anchor id — unfilled template?)`, `map/ids.jsonl` `empty`.
*Expected:* `RESOLVED`, or an honest declaration that this repo has no map by design.
*Conditions:* any run in this repo.
*type:* measured — receipt at `.agent-work/epic-559/c2-generate-the-spine/map-orientation.json`.
*rev:* `0ab7ecab`.

**Consequence.** Every Commander pays the discharge cost (substitutes, unmapped gaps, escalation) and
cannot cite a single map anchor in its mission frame — `verify-frame` refuses every anchor id under a
degraded orientation, so the frame must drop the anchor grammar entirely.

**Open question.** Is a packet map wanted here at all, or is `map/INDEX.md` (which *is* maintained, and
which a test keeps fresh) the intended structural record? If the latter, `map_orient` should recognize
it, and the shipped empty `map/ids.jsonl` should go.

---

## tc5 — `REVIEW_SURVEY.template.json`'s `r6-fowler` check carries an unsubstituted `<work-id>`

**Labels:** bug · missing doc
**Priority:** medium — two of my three reviewers hit it independently.
**Ladder:** fails *no production-default impact* (it edits a shipped template) and — this wave —
`decision:no-template-edited-to-pass` forbade touching shipped templates at all.

**Observation.** `r6-fowler`'s postcondition command is
`python scripts/verify_fowler_pass.py .agent-work/<work-id>/FOWLER_PASS.json` — a literal `<work-id>`
plus a `scripts/`-relative path. Nothing substitutes it for an ad-hoc reviewer survey built straight
from the template; only a spine materialized through `init_work_area.resolve_spine` gets resolution.
*Expected:* either the token resolves, or the template says a survey built by hand must substitute it
before first use.
*Conditions:* a reviewer building its own survey from the template — the normal path when no spine is
bound to the crew.
*type:* measured — the `g1` reviewer had to `amend --delta ... retext-check` it to an absolute path
before `verify_fowler_pass.py` could be found, and reported it unprompted; the `g2` reviewer hit the
same thing. *rev:* `0ab7ecab`.

**Possible fix (hypothesis).** Resolve it at survey-creation time the way a spine is resolved, or state
the substitution as an explicit first step in the template's own `r0-context` imperative.

---

## tc6 — a dispatched crew inherits the parent's `SPINE_FILE`/`SPINE_SESSION`

**Labels:** bug · tooling · security/privacy (blast radius)
**Priority:** medium.
**Ladder:** fails *adjacent to scope* and *no production-default impact*.

**Observation.** A crew dispatched by `run_crew.py` **without** `--spine` inherits the dispatching
process's `SPINE_FILE` and `SPINE_SESSION`. Both my reviewers found the **Commander's own spine** bound
in their environment — `execute` gate, session `commander` — and correctly declined to drive it.
*Expected:* a crew with no `--spine` has no spine bound, or has one scoped to itself.
*Conditions:* any `--handoff`-only dispatch from a process that itself has a spine bound.
*type:* measured — reported independently by the `g1` and `g2` reviewers, each quoting the bound values.
*rev:* `0b27b2b8`.

**Consequence.** Two reviewers handled it correctly because their skill told them not to drive a spine
they were not given. A third might not, and the spine it would drive is its **dispatcher's**.

**Possible fix (hypothesis).** `crew_env` unsets `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` unless
`--spine` is given, the same way the declared test mode unsets them before running pytest.

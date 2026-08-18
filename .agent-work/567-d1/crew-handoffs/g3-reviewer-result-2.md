# Review Result — g3-review, rework round 1 of 3

Work id `567-d1` · gate `g3-review` · crew `constellation/567-d1/g3/reviewer/attempt-2`
Worktree `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
Branch `feat/567-d1-doctrine-sweep-guard` · parent `constellation/567-d1/lane-d1/commander-delegated`

Survey driven: `.agent-work/567-d1/g3-review/review-2.json` (7 items, all visited, journal beside it).
Session `constellation/567-d1`. Fowler record: `.agent-work/567-d1/g3-review/FOWLER_PASS-2.json`.
Round 1's `review.json` and `FOWLER_PASS.json` are untouched.

My door was **unbound** at start (`SPINE_FILE` unset, only `SPINE_PARENT`), so I authored this survey,
bound it and drove it — the same path the shipped prose describes, which makes me the live case for
its second reader.

## Assigned Gate

`g3-review` — Door vocabulary in `specs/*.spine.toml`: re-review after BLOCK.

## Verdict

**APPROVE**

Seven of seven items pass. The blocker is closed, nothing regressed, and three observations ride out
of scope.

---

## 1. The blocker is closed

Round 1 blocked one clause in two files: the specs justified the second-checklist prohibition with
*"the archive gate requires the lease to cover every journaled action"* — a gate that does not do
that, inside a sentence advertising itself as measured.

`archive gate` now appears **nowhere** in `specs/` or `skills/` (`grep -rn`, exit 1). The replacement
names the **terminal provenance check**, and that is not a third invented name: it appears in **six**
skill files, including `skills/reviewer/SKILL.md:17` and `skills/implementer/SKILL.md:17`, and I
diffed those lines against the **installed** copies a dispatched crew actually loads — identical. The
spec cites vocabulary its reader already holds.

## 2. Every claim in the repaired paragraph, grounded

This is what the BLOCK was really about, so I did it claim by claim rather than paragraph by
paragraph. Nothing here is inherited from round 1.

| # | Claim now in both files | What grounds it |
|---|---|---|
| 1 | "with your own lease held, binding a second checklist is REFUSED" | Re-measured by me, **fresh process**, probe case `bound-then-rebind`: `isError=True`, and `spine_status` afterwards still shows the *first* spine, so the refusal is total |
| 2 | the quoted fragment `"one door drives one spine at a time ... Release it first"` | Verified against the **live door**, both halves present — see §3 for why this check is trustworthy |
| 3 | "your role skill holds the lease open until your last action" | `skills/{reviewer,implementer}/SKILL.md:17` — *"only then `release` the engine session lease as your very last action"* |
| 4 | "the lease must cover every journaled action" | Verbatim on those same two lines |
| 5 | "releasing it early fails the terminal provenance check" | Those same lines name that check; six skill files carry the term |
| 6 | "Dispatched without a spine of your own you arrive holding no lease" | `run_crew._crew_door_env(spine=None)` under a **cleaned** ambient env returns `SPINE_PARENT` only — no `SPINE_FILE`, no `SPINE_SESSION`. My own dispatch environment has exactly 0 of those two set |
| 7 | "nothing to release, and the escape never arises" | Probe case `unbound-then-bind`: `spine_status` REFUSES *"no spine is bound to this door"*, then `spine_bind` **succeeds** with no release step, returning `SPINE_SESSION` derived from the spine's own `work_id` |

**Positive control, because an absence over an unexercised path reads exactly like a passing check.**
Case `released-then-rebind` runs the *identical* `spine_bind` after releasing the lease, and it
**succeeds**. So the refusal is conditioned on holding your own lease and on nothing else — precisely
the condition the prose states. The claim is true, and true for the stated reason.

## 3. The quote check, and why it is worth more than the last one

Round 1 reported the quoted fragment "verbatim" by eye, and was one capitalisation off; the
implementer caught it and fixed `release it first` → `Release it first`. So I did not re-read it
either. My probe **extracts the quote out of the specs themselves** with `tomllib` — imperative → the
one quoted string containing "one door drives one spine" → split on the ellipsis — and asserts each
half against the door's live refusal text. It compares shipped text to behaviour, never to a copy I
typed. `VERBATIM_OK=True`, both files, both halves.

**Durability, which the handoff did not ask for and which I think matters here.** Round 1 recorded
`scripts/mcp_spine_server.py` as "byte-identical to `main`". It no longer is — `git diff main` shows
+4/−251 — but **the fence held**: `git log main..HEAD -- scripts/mcp_spine_server.py` is empty, and
the cause is that **main moved ahead** via lane E's `cf6cdaa2` ("retire CLI-recommending text"). Since
this lane merges last, a quote verified only against this worktree's door could be false on merge. So
I re-ran the entire probe against **main's** door: the refusal and both quote halves survive there
too. The merge will not falsify the quote.

(That round-1 phrasing is the failure `global-everyone.md` §"Pin a claim to the revision you read it
at" describes — a read of a moving target reported as a property of the thing. It changes nothing
about this gate.)

## 4. The scoping is right

The paragraph addresses two readers. Both halves are true of theirs:

- **Reader A**, holding its own lease — gets the refusal plus the role-skill rule barring the
  release-to-escape. Measured true (§2, rows 1–5).
- **Reader B**, dispatched with no spine — gets *"you arrive holding no lease — nothing to release,
  and the escape never arises."* Measured true (§2, rows 6–7). I am reader B.

**Neither reader is left with the other's rule.** The one subtlety, which I weighed and judged an
observation rather than a finding: reader B stops being lease-less the moment it binds and claims its
own plan, and from then on reader A's sentence governs it — which is *also* true of it, since the
role-skill rule addresses any reviewer. B is not left exempt, because the closing sentence is
unconditional — *"the door reaches the spine you hold a lease on, and you hold a lease on exactly
one"* — and it forecloses the misreading. The verb "arrive" carries the temporal scoping honestly.

## 5. The repair landed identically in both files

The clause extracted from each file and whitespace-normalised:
`md5 = c826f819cd61cdd176742a75c18fd6f7`, len 488, **both**. The drift this epic is about did not
happen here.

## 6. Nothing regressed

| Check | Result |
|---|---|
| Both specs parse as TOML | `tomllib.load` on both, exit 0 |
| Both name the door | 9 mentions each |
| Guard: no violation at any `specs/` address | **met** — no `specs/` address appears anywhere in the log |
| Non-workbench site filter | prints **nothing**; all 8 sites are `skills/workbench/references/checklist-engine.md` (5) and `skills/workbench/SKILL.md` (3) — lane D2's fenced files, expected |
| Guard run | `2 failed, 17 passed` |
| Scope | commit `05fcfec3`'s files outside `.agent-work/` are **exactly** the two specs |
| Fences | branch changed `mcp_spine_server.py` in 0 commits, `generate_spine.py` in 0; `tests/test_cli_retirement_guard.py` clean in the working tree |

**The guard's silence on `specs/` is real, not vacuous — three legs.**

1. **Census** — `scanned 3098 texts across 216 files (101 under skills/, 2 under specs/, 113 under
   .agent-work/templates/)`. The walk reached `specs/`.
2. **Floors** — all 5 `TestTheWalkIsNotVacuous` tests PASS by name, including
   `test_the_walk_reaches_the_spec_corpus`.
3. **The leg the census alone does not buy.** I imported the guard module and confirmed each spec
   contributes a **whole-file** chunk byte-identical to disk (7241 and 7819 chars, `whole_file=True`)
   with the **new** prose inside it. Then the positive control: against an **in-memory** copy of that
   same text — no file edited, mutation asserted applied — **all four** patterns fire 1 hit per file
   (`CLI_FALLBACK_RE`, `ENGINE_INVOCATION_RE`, `ENGINE_PLACEHOLDER_RE`, `ENGINE_STANDIN_COMMAND_RE`),
   while the shipped text scores **0 on all four**.

## 7. The schema decision holds, re-derived not re-read

Injecting a top-level key and a gate key into both specs: **neither survives** `compile_spec` — the
compiled top level is a fixed 8-key set, the compiled task a fixed 14-key set — and
`spec_shape_faults` returns **0 faults both with and without** them, so nothing would refuse the
silent drop. A new key would have had **no consumer**, and giving it one means editing
`generate_spine.py`, a stop condition on this gate. Prose-only is not under-delivering.

The header comment's own claims hold too: its text is **absent** from the compiled spine, while
`one door drives one spine at a time` and `terminal provenance check` are both **present** in it.

## 8. `config_ref`

Recorded accurately, and leaving it was right. `engine-config.json` exists **nowhere** in the repo.
`docs/CHECKLIST_SCHEMA.md` rules the absence deliberate — a missing path falls through to `{}` and is
harmless, *"which is why every shipped template's nonexistent `docs/agents/engine-config.json` is
fine"* — while a `config_ref` pointing at a real **non-JSON** file raises an unhandled
`JSONDecodeError`, so creating the file converts a documented no-op into a live crash surface. The
counter-precedent is real: `skills/explorer/templates/CYCLE.template.json` is `type=survey` with **no**
`config_ref`.

## 9. Fowler pass

Verifier exit 0 — `smells=12, flagged=['long-method','duplicated-code','shotgun-surgery'],
overridden=['long-parameter-list']`. Three verdicts moved from round 1, each on a measurement:

- **feature-envy: flagged → absent.** Its cause was the archive-gate clause reaching for a
  Commander-spine gate. The rework removed exactly that reach.
- **shotgun-surgery: overridden → flagged.** Round 1 overrode it because "g1's guard walks every
  surface." That does not survive contact with the measurement: the guard forbids a CLI second path,
  it does not require the door rule to be *present*. See §10.
- **duplicated-code: still flagged, sharper reason.** The `IMPLEMENTER_RESULT` says *"the duplication
  stays; silent divergence cannot"*, on the strength of `verify_claims.py`. That script lives in the
  crew scratch dir and matches nothing under `tests/` or `scripts/` — so the linked pair is checked
  once, by the run that wrote it, not durably.

**long-parameter-list** is overridden on `global-everyone.md`'s "Agent-facing. Dense by design.", and
I checked the inventory is correct as well as dense: all 10 assertions the imperatives make about door
tools hold against the door's own `TOOLS`, and **0 of 12** tools take a session id.

## 10. Out-of-scope observations

- **`tc1` — the sweep reached the spec surface and missed the template surface.**
  `skills/reviewer/templates/REVIEW_SURVEY.template.json` and
  `skills/implementer/templates/IMPLEMENTER_PLAN.template.json` contain **zero** occurrences of
  "door" anywhere in the file, and nothing links them to the specs: `generate_spine.py` emits to an
  `--out` path, **no test asserts a compiled spec equals a shipped template**, and the specs' own
  header comment claims only that intent *"matches"* the template. So a crew that instantiates from
  the template — what the role `SKILL.md` directs an unbound crew to do, and **how this very survey
  was built** — never receives the second-checklist rule or its measured reason. A weaker form
  survives in `SKILL.md` prose; the measured reason does not. `skills/**` is fenced from this lane, so
  this could not have been fixed here. Flagged through the door. **No issue filed.**
- **The linked-pair check is not durable** (§9). The map note the implementer wrote is right; the
  check belongs in `tests/`.
- **Round 1's `tc1` stands unclosed** — "terminal provenance check" is binding role doctrine whose
  only mechanical enforcement is `evals/euler-*/checks/spine_completed.py::journal_consistent`, which
  no live path calls. The repaired clause is careful about this: it attributes the rule to *"your role
  skill"* rather than to a gate, so it does not re-commit round 1's error. The upstream gap is real.

## 11. Map impact verdict

- **Evidence supports claimed change** — yes, all seven claims (§2), each named to a source.
- **Constraints not violated** — no `<engine>` token, no CLI spelling, no command shown; all four
  guard patterns score 0 on the shipped text.
- **Notes match the diff** — yes. "No structural, capability or dependency change. Prose only" is
  correct. The implementer's two map notes (the linked pair; `_crew_door_env`'s spine-pair
  pass-through as a doctrine surface) are both accurate — I reproduced the pass-through: with a dirty
  ambient env, `spine=None` yields the **dispatcher's own pair** verbatim.
- **Decision candidates surfaced** — yes.
- **Durable context routed** — yes, `tc1` through the door; no issue filed.

## 12. Workflow Feedback

**What helped.**

- **The ADDENDUM told me what NOT to re-open**, listed what round 1 established, and gave me four
  numbered jobs. That is the difference between a re-review and a second full review: I spent my
  budget on claim-grounding and on the two things nobody had checked (quote durability across the
  merge, and whether the vocabulary reaches the template surface) instead of re-deriving a refusal
  that was already measured twice.
- **Naming round 1's own error in the addendum** — that its verbatim check was done by eye — was the
  single most useful line in the document. It told me exactly which technique to *not* reuse, and the
  probe I wrote instead is what confirmed the fix.
- The `test_gauge_chain_writer_to_trip.py:604` warning and the POSIX/`dash` warning were both correct
  and both still paying. Keep them, and keep naming the sibling crew that hit the first.

**What got in the way.**

- **`docs/agents/CREW_CONTEXT.md`'s Python Invocation section is stale in a way that costs a crew its
  interpreter.** It records `python3` as having no pytest, measured 2026-08-10. Measured now: `py`,
  `python` and `python3` all report pytest 9.1.1. The section's own advice — check before you run —
  is what saved it. Already a staged candidate; this is the third crew to re-measure it.
- **`spine_amend`'s delta op field names are not discoverable from the tool.** The `r6-fowler` REPAIR
  PATH is well designed and I took it, but the tool description says only "the same `{ops: [...]}`
  object the CLI's `--delta` file holds" and the engine validates it, so my first attempt used
  `task_id`/`condition_id`/`check` and was refused with `retext-check None: no such gate` — a message
  keyed on the *value* of the field I had not supplied, which reads as "your gate is missing" rather
  than "your field name is wrong". The real names are `id`, `cond`, `command`. I had to read
  `checklist_engine.py` to find them. Either the refusal should name the accepted keys, or the tool
  description should carry one worked op.
- **The reviewer skill still opens by stating that a dispatched crew's spine is bound for it.** Mine
  was not — only `SPINE_PARENT` — so `spine_status` refused and I built my own survey. This is the
  **fifth** crew in this lane to hit it, and the g3 implementer already asked for the one-line fix:
  branch on whether `SPINE_FILE` is set. The refusal text is excellent and cost one call.

**My own mistakes.**

- **My first guard-coverage probe indexed the wrong tuple slot.** `GUARD_TEXTS` entries are
  `(path, where, text, whole_file)`; I read element `[1]` as the body, got 28-char chunks, and for one
  moment had "the walk does not reach the new prose" on screen — which, had I trusted it, was a
  spurious BLOCK against a guard that is fine. I caught it by checking the chunk length against the
  file on disk, which is what I should have done first. Same class as round 1's line-break mistake:
  **when a probe reports a surprising absence, suspect the probe before the subject.**
- **My first door probe called `call_tool` for `spine_bind`** and got `KeyError`. `spine_bind` is
  routed by `call_lifecycle_tool`, a module-level sibling. I had assumed one entry point instead of
  reading the routing. Both mistakes are the same failure the implementer named in its own feedback:
  writing a check whose expectations I assumed rather than looked up, so the first run measures the
  author rather than the subject.
- I nearly recorded shotgun-surgery as `overridden`, copying round 1's verdict, before checking
  whether the guard it cited actually enforces presence. It does not. Copying a prior reviewer's
  override is the same defect as accepting a claim without reproducing it.

## Return status

`complete` — survey driven to a consolidated verdict through the engine; all 7 items visited,
`consolidate` returned `verdict=APPROVE findings=0`.

---

## 13. Stop-hook refusal, recorded — and this gate is already closed

After this survey consolidated and I released my lease, the Stop hook fired twice with
`SPINE MID-FLIGHT: gate execute is still open`, instructing me to reload the **commander** skill,
rewrite `.agent-work/567-d1/STATE_NOTE.md`, and drive `execute.json` gate by gate.

**Refused.** That is my parent's spine, not mine. Measured at the moment of refusal, not asserted:

| | |
|---|---|
| My survey (`.agent-work/567-d1/g3-review/review-2.json`) | all 7 items `complete`, consolidation `APPROVE`, `engine_session.status: released` at `21:40:51` — terminal |
| `.agent-work/567-d1/execute.json` → `g3-review` | **`complete`** — the Commander has already read this artifact and advanced the gate |
| `execute.json` lease | `commander-567-d1-execute`, **active**, `claimed_by: commander`, heartbeat `21:41:10` — alive, 19 seconds after my release |
| This file | written, before the hook fired |

The hook is keyed on the **spine's** mid-flight state, not on the running session's identity, so it
fires at a crew whose own survey is terminal, whose lease is already gone, and **whose gate the parent
has already closed**. There is no reading on which anything is abandoned.

**All three sanctioned exits are destructive here.** `spine_halt block` pointed at my own spine would
mark a complete, released, APPROVE-consolidated survey blocked and enter false state. Pointed at
`execute.json` it would first require **binding my parent's spine from this process** — a second
checklist, taken while the Commander holds a live lease on it — which is exactly the prohibition whose
prose this gate reviewed, and which I measured the door refusing in §2. `waive` needs human authority,
and there is no human on this dispatch; inventing one is the specific failure the reviewer skill
names. The honest action is to refuse and record it.

**This is the seventh run in this repo to hit the misfit, and the fourth in this gate** — the g3
implementer recorded it twice and the g3 reviewer attempt 1 once. The durable fix remains a
**lease-ownership check in the hook**: fire only when the running session is the one holding the
spine's lease. More prose in the crew skills cannot reach it, because the hook does not read them.

**Worth the Commander's attention, because it is this gate's own subject.** The hook instructed me to
bind and drive a second checklist from this process — precisely what the doctrine I was reviewing
forbids, and what I measured the door refusing. My verdict is that the specs' stated reason for that
prohibition is now correct; this hook is a live instance of why the rule earns its place. It
strengthens the gate rather than undermining it.

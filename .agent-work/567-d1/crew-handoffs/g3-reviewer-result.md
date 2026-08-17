# Review Result

Work id `567-d1` · gate `g3-review` · crew `constellation/567-d1/g3/reviewer/attempt-1`
Worktree `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
Branch `feat/567-d1-doctrine-sweep-guard` · parent `constellation/567-d1/lane-d1/commander-delegated`

Survey driven: `.agent-work/567-d1/g3-review/review.json` (7 items, all visited, journal beside it).
Session `constellation/567-d1`. Fowler record: `.agent-work/567-d1/g3-review/FOWLER_PASS.json`.

## Assigned Gate

`g3-review` — Door vocabulary in `specs/*.spine.toml`: review.

## Verdict

**BLOCK**

One clause, in two files. Six of seven survey items pass; `r3-evidence` fails.

---

## 1. The review's real question: is the vocabulary TRUE?

Three factual claims carry the new prose. Two reproduce. One does not.

### 1a. REPRODUCED — the rebind refusal, and it is scoped exactly as the prose says

Measured in **fresh processes with explicit paths**, per `docs/agents/ORCHESTRATOR_CONTEXT.md`
§Dogfooding and `CREW_CONTEXT` "Two Engines Are Alive In Your Session" — not by watching my own
session. Probe:
`.agent-work/567-d1/crew-scratch/g3-reviewer-attempt-1-74e194cfc852/door_probe.py`, three separate
`python3` invocations against `scripts/mcp_spine_server.py`, which I first confirmed is
byte-identical to `main` and unmodified in the working tree (lane E's, read-only to me).

Case `bound-then-rebind` — bound to spine A via `SPINE_FILE`/`SPINE_SESSION`, claimed A's lease,
then `spine_bind` B:

```
isError=True
REFUSED: this door still holds an active lease on '...probe-a.json' as
'constellation/567-d1-g3r-probe-a', and one door drives one spine at a time. Rebinding this door
now would leave that lease held by nobody. Release it first (`spine_lease` with action 'release'),
then call `spine_bind` again.
```

The fragment both specs quote is verbatim. `spine_status` afterwards still showed A, so the refusal
is total.

**Positive control, because an absence over an unexercised path reads exactly like a passing check.**
Case `released-then-rebind` runs the *identical* `spine_bind` B call after releasing A's lease — and
it **succeeds**. So the refusal is conditioned on holding your own lease and on nothing else, which
is precisely the condition the prose states. The claim is not just true; it is true for the stated
reason.

### 1b. REPRODUCED — an unbound door binds and drives, so no role is stranded

Case `unbound-then-bind`, with `SPINE_FILE`/`SPINE_SESSION` unset: `spine_status` REFUSED ("no spine
is bound to this door"); `spine_bind` B SUCCEEDED, returning `SPINE_SESSION`
`constellation/567-d1-g3r-probe-b` **derived from the spine's own `work_id`**; `spine_lease claim`,
`spine_status` and `release` then all worked.

I am also the live case. This survey was dispatched with only `SPINE_PARENT` set, and I bound and
claimed it exactly this way. So the prose's *"A reviewer dispatched WITHOUT a spine of its own holds
no lease, and an unbound door binds one spine and then drives it identically — the identity comes
from that spine's own work id, never from a string you supply"* is true, and it satisfies
`global-everyone.md` "Fail visibly … no hidden fallback": the role is left with a path.

**The implementer was right to refuse the handoff's premise.** My own handoff asserted that both
files describe a role that "cannot" use the door, and that every crew in this lane drove its plan
through a hand-supplied CLI session id. That is wrong for the dispatched-crew case, the implementer
measured it wrong first-hand, and I have now reproduced the correction independently. Nothing in the
shipped prose repeats the handoff's error.

### 1c. FALSE AS STATED — the "archive gate" clause. This is the BLOCK.

Both files assert:

> …the escape that refusal names is barred for you, because **the archive gate requires the lease to
> cover every journaled action**, so releasing it to reach a second checklist **fails your own
> closeout**.

Measured:

| # | Claim | What is actually there |
|---|---|---|
| 1 | the archive gate requires this | The `archive` gate exists only on the **Commander** spine (`COMMANDER_SPINE.template.json`). Its one lease-related postcondition is `c3` "engine session lease released", **`check: null`** — a qualitative attest requiring the lease be *released*, silent on journal coverage. Its others are `c1` episode-captured, `c2`/`c2b` branch+PR, `c4` git-change-policy. None reads a journal. |
| 2 | …so releasing fails closeout | `scripts/spine_lifecycle.py` refuses in the **opposite** direction: `"close refused: the lease is still active"` when `engine_session.status != "released"`. Release is what closeout *wants*. |
| 3 | the lease must cover every journaled action | Real, but enforced only in `evals/euler-*/checks/spine_completed.py::journal_consistent` ("journal entry seq N follows the lease release"), called from that file's own `main()` over an **eval run directory**. Nothing in the archive gate, `spine_lifecycle.close_work`, `checklist_engine`, `run_crew.py` or `verify_iterative_role_artifacts.py` calls it. `grep spine_completed` across live specs and templates hits only archived work areas. |
| 4 | "your own closeout" | **Neither crew plan has a closeout gate at all.** `IMPLEMENTER_PLAN.template.json` is `['m0-context','m1']`; `REVIEW_SURVEY.template.json` is `['r0-context'..'r6-fowler']`. The role told its closeout will fail has no closeout. |

**Where the error came from.** The inherited `skills/reviewer/SKILL.md:17` and
`skills/implementer/SKILL.md:17` both say *"fails the **terminal provenance check** — the lease must
cover every journaled action"*, which is accurate. The phrase "archive gate" appears **nowhere** in
`skills/`. The implementer paraphrased a correctly-named check into a differently-named, real gate
that does not do this. The `IMPLEMENTER_RESULT` offers no measurement for the clause — §5b measures
only the bind/lease half.

**Why this blocks rather than riding as an observation.** The clause sits inside a sentence that
advertises itself as *"a measured refusal rather than an oversight"*, in the two files this change
makes the corpus's statement of what the door is for a role. My handoff is explicit that the *reason*
exists so a future author cannot "fix" the rule. A future author who checks this reason finds no
archive gate in their own plan, and is then entitled to discount the entire paragraph — the exact
inverse of its purpose. `CREW_CONTEXT` "Assert against behaviour, never against text that describes
it" is the standard missed.

**The remedy is small.** One clause, two files: quote the inherited "terminal provenance check"
wording instead of renaming it. The rest of the paragraph — which is the load-bearing part, and
which I measured true — needs no change. See §6: the paragraph is duplicated near-verbatim, so the
repair must land in **both** files identically.

---

## 2. Handoff compliance

All six close criteria performed. I re-ran 1–4 and 6 myself and read the exit codes.

| # | Criterion | Verdict |
|---|---|---|
| 1 | Both specs name the door | **met** — `spine_*` vocabulary in both `imperative`s and new `constraints` |
| 2 | Both state the second-checklist truth | **met** for the rule; its second stated reason is false (§1c) |
| 3 | Guard reports no violation at any `specs/` address | **met** — see §4 |
| 4 | Both files parse as TOML | **met** — `tomllib.load` on both, exit 0 |
| 5 | Schema question settled with reasoning | **met** — see §5 |
| 6 | Dangling `config_ref` recorded with evidence | **met** — see §7 |

## 3. Scope drift

None. `git status --porcelain` filtered of `.agent-work/` shows exactly `specs/implementer.spine.toml`
and `specs/reviewer.spine.toml`. +81 lines, zero deletions; pre-existing gate text untouched. All
three fenced surfaces respected: `scripts/mcp_spine_server.py` byte-identical to `main` with no
working-tree change; `tests/test_cli_retirement_guard.py` unmodified in the working tree (its +718
lines are gate g1's committed work); `skills/**` untouched. No new postconditions, so
`spec-all-qualitative-postconditions` is not engaged, and none of `_DISPATCH_MARKERS` appears in
either new imperative.

## 4. The guard's silence on `specs/` is real, not vacuous

The handoff asked me to confirm this specifically, since an absence over a walk that stopped reaching
`specs/` reads exactly like a passing guard. Three legs:

1. **Census** — the failure message reports `2 under specs/`, and `SPEC_FILES` is exactly
   `['specs/implementer.spine.toml', 'specs/reviewer.spine.toml']`.
2. **Floors** — all five `TestTheWalkIsNotVacuous` tests PASS by name, including
   `test_the_walk_reaches_the_spec_corpus` and `test_the_walk_yields_texts_not_just_paths`.
3. **The leg the census alone does not buy.** I imported the guard module and confirmed each spec
   contributes a whole-file text chunk (7109 and 7687 chars, byte-identical to disk, comments
   included) and that the **new** prose is inside it. Then the positive control `CREW_CONTEXT`
   demands: I injected a CLI-fallback clause plus `python scripts/checklist_engine.py … current` into
   an **in-memory** copy of that same text, asserted the mutation applied, and re-ran the guard's own
   `CLI_FALLBACK_RE` and `ENGINE_INVOCATION_RE` — **1 hit each, per file**. Against the shipped text:
   **0 hits**, both patterns, both files. No file was edited to prove this.

Guard run: `python3 -m pytest tests/test_cli_retirement_guard.py -q` → `2 failed, 17 passed`. The
non-workbench site filter prints **nothing**; all 5 sites are under `skills/workbench/**` — lane D2's
fenced files, which the handoff names as expected and `g5-final` re-checks after the rebase.

## 5. The schema decision holds

Re-derived from `scripts/generate_spine.py`, not from the result's summary. `_compile_gate`
(:669-684) returns a dict **literal** over a fixed field list; `compile_spec` (:704-713) does the same
at top level. Any other authored key is not copied, and `spec_shape_faults` carries **no** unknown-key
fault to refuse the drop — its "unknown" faults are `spec-unknown-check-kind`, the dispatch-parent
refusal, and `probe-script-unknown-flag`, none a key allowlist.

Answering the handoff's question directly: **a new key would have had no consumer.** Giving it one
means editing `generate_spine.py`, which was a stop condition on the gate. So prose-only is not
under-delivering — a new key would be dead weight the spec author could see and the dispatched role
never could.

Measured, not quoted: compiling both specs to `/tmp`, the header comment is **absent** from the
compiled JSON while `one door drives one spine at a time` is **present** in both compiled
`imperative`s, with 2 and 3 constraints carried.

## 6. Code/doc quality — Fowler pass

`python scripts/verify_fowler_pass.py .agent-work/567-d1/g3-review/FOWLER_PASS.json` → exit 0,
`smells=12, flagged=['long-method','duplicated-code','feature-envy'],
overridden=['long-parameter-list','shotgun-surgery','divergent-change']`.

**Flagged.**

- **duplicated-code** — the second added paragraph is near-verbatim across both files and constraint 1
  is byte-identical. The `IMPLEMENTER_RESULT` §1b's "not a copy" defence is true of the **first**
  paragraph, which correctly diverges into the survey dialect; it is not true of the second. Flagged
  rather than overridden because it is biting *now*: the §1c BLOCK finding sits inside the duplicated
  paragraph, so **its fix is a two-site edit**. Deduplication is not the remedy — TOML specs have no
  include, comments are dropped, a new key reaches no reader — so each spec must stay self-contained;
  the actionable output is that this paragraph is a linked pair.
- **feature-envy** — both crew specs justify their own rule via a gate belonging to the Commander
  spine. Same defect as §1c, and the lens explains why it was easy to make.
- **long-method** — the context-load imperative went from 5 lines to ~35 and now does two jobs, so
  "Load baseline context" no longer describes it. Observation only; there is no cheap place to split
  to.

**Overridden**, each with the standard that wins and why: **long-parameter-list** (8-tool inventory in
one sentence) → "Agent-facing. Dense by design."; **shotgun-surgery** (the rule now on six surfaces) →
epic #567's chosen architecture plus g1's guard that walks every surface; **divergent-change** →
"One agent, one plan".

**Absent** 6, two non-trivially: **speculative-generality** is absent because the change *refused* it
(the new key was declined on measured grounds); **comments-as-deodorant** was tested rather than
waved through — the new header comment records an external, invisible compiler property nothing in
the file could otherwise expose, and I verified it never reaches an agent.

## 7. Map impact verdict

- **Evidence supports claimed change** — yes for the door-path and schema claims (§1a, §1b, §5). **No**
  for the archive-gate clause: no evidence was offered and it does not hold (§1c).
- **Constraints not violated** — no `<engine>` token, no CLI spelling, no `checklist_engine.py`
  reference, no placeholder-plus-verb shape, no fenced file touched.
- **Notes match the diff** — yes. "No structural, capability or dependency change" is correct. The
  observation that `_compile_gate`'s carried-field list "is a doctrine surface, not just a compiler
  detail" is the sharpest thing in the result, and §5 confirms it.
- **Decision candidates surfaced** — yes. The `config_ref` gated half was correctly left to the human
  who owns the rework-cap default.
- **Durable context routed** — yes, three triage candidates flagged through the door (`tc1`–`tc3`).

**`config_ref`: what was recorded is accurate and leaving it was right.** Every leg re-verified at
source: `find . -name engine-config.json` returns nothing repo-wide; `docs/CHECKLIST_SCHEMA.md:35-38`
says verbatim that a missing path is harmless "which is why every shipped template's nonexistent
`docs/agents/engine-config.json` is fine", while a `config_ref` pointing at a real non-JSON file
raises an unhandled `JSONDecodeError` — so creating the file converts a documented no-op into a live
crash surface; and the counter-precedent is real —
`skills/explorer/templates/CYCLE.template.json` is `type=survey` with **no** `config_ref`, pinned with
its reasoning at `tests/test_explorer_templates.py:242-247`. The candidate correctly splits one vague
"fix it" into two separable decisions. One thing it understates, now flagged as `tc2`: the
contradiction is wider than `specs/` — `REVIEW_SURVEY.template.json`, which is what a reviewer
actually instantiates (I built this survey from it), carries the same dangling key.

## 8. Reconciliation check

**For the Admiral, before `g5-final` locks the sweep wording.** `.agent-work/567-d1/notes-1.md` §M1
concluded the door *"provably cannot"* reach the three second-checklist sites and that the CLI is
*"the only path"* for them. I measured otherwise, independently of the implementer (§1b), and this
survey is itself the counterexample. M1's conclusion holds only for a process **already holding a
lease** — which is not the state most dispatched crews are in. The epic's thesis is *strengthened* by
this, not weakened, but any `g5` wording built on M1's stronger claim rests on a premise the
measurement does not support. Flagged as `tc3`; **no issue filed**, per the handoff.

## 9. Blockers

- **The `archive gate` clause in `specs/implementer.spine.toml` and `specs/reviewer.spine.toml`**
  states a mechanism that does not exist at the site it names, inside a sentence that claims to be
  measured (§1c). Fix: replace with the inherited "terminal provenance check" wording. **Two files —
  the paragraph is duplicated near-verbatim (§6).**

## 10. Out-of-scope observations

- **`tc1`** — "the lease must cover every journaled action" is stated as binding doctrine in
  `skills/reviewer/SKILL.md:17` and `skills/implementer/SKILL.md:17`, but its only enforcement is the
  eval harness. No production path enforces it. This is the **upstream cause** of the blocker, and
  fixing the specs' clause does not close it. `skills/**` is fenced from this lane.
- **`tc2`** — the dangling `config_ref` contradiction reaches `REVIEW_SURVEY.template.json` and its
  `.agent-work/templates/` overlay copy, not just `specs/`. Whoever settles the survey half must sweep
  the templates or the two halves drift again.
- **`tc3`** — the `notes-1.md` §M1 premise (§8). Float to the Admiral.

## 11. Workflow Feedback

- **Handoff gaps.** The handoff's §"The two facts" states as settled that *"Both files you are
  reviewing describe exactly case 2"* and that *"you are driving one right now, and so is every crew
  in this lane."* Both are wrong, and the g3 implementer had already said so in its own §5b — which
  this handoff was written after, and quotes elsewhere. Had I taken the premise as given, I would have
  looked for a defect in prose that is correct and missed the one that is real. **The correction was
  available upstream and did not propagate into the handoff.** Second, the handoff's §4 says the
  `config_ref` "does not exist in this repo" and asks whether leaving it was right, but does not
  mention that `CHECKLIST_SCHEMA.md` already *rules* the absence deliberate — the implementer found
  that and the handoff did not carry it forward, so I re-derived it.
- **Context rediscovered.** Which check actually enforces "the lease must cover every journaled
  action". The handoff quotes the specs' claim about the archive gate without flagging it as
  unverified, and finding the answer took a four-hop chain — `SKILL.md` → `COMMANDER_SPINE.template
  .json` → `spine_lifecycle.py` → `evals/*/checks/spine_completed.py`. Since §1 of the handoff told me
  to check each claim "against the measurement rather than against plausibility", naming that chain
  (or naming the clause as unmeasured) would have been the single highest-value line in the document.
- **Instructions improvised around.** Two. (a) The reviewer skill opens *"A dispatched crew's spine is
  bound for you before you start (`SPINE_FILE`/`SPINE_SESSION` in your environment): `spine_status` is
  your first call."* Nothing was bound — my environment carried only `SPINE_PARENT` — so
  `spine_status` refused and I built my own survey instead. **This is the fourth crew in this lane to
  hit it**, and the g3 implementer's feedback already asked for the one-line fix: branch on whether
  `SPINE_FILE` is set. The refusal text is excellent and cost only one call, but the skill states as
  fact something false for `spine: null` dispatch, and the recorded precedent is that crews resolve it
  by driving the **parent's** spine — which would advance my Commander's gate. (b) `r6-fowler`'s
  postcondition resolves the record path from `<work-id>` alone, which collides with an existing
  gate's record; handoff constraint 7 redirects it. I took the template's own REPAIR PATH — `amend`
  with a single `retext-check` op, authority Commander 567-d1 — rather than hand-editing. That path
  worked exactly as documented and is the best-designed escape hatch I met this run.
- **What would have made this easier.** One change: **a handoff should mark which of the claims it
  restates were measured and which were inherited.** This one presented a measured refusal, an
  unmeasured mechanism, and a premise already known to be wrong in indistinguishable prose. The
  measured claim survived, the unmeasured one is the blocker, and the wrong premise nearly aimed the
  review at the wrong file. Second, smaller: the handoff's warning about
  `test_gauge_chain_writer_to_trip.py:604` snapshotting `.agent-work/` was correct and saved a
  false failure — keep it, and keep naming the sibling crew that hit it.
- **My own mistakes.** Two. First, my initial probe for whether the guard reaches the specs' new
  comment used a search string that spanned a line break in the wrapped TOML comment, so it returned
  `False` and I briefly read it as a coverage gap in the guard. The guard reads the raw whole file;
  the fault was my probe. I caught it by comparing the guard's text against the file bytes, which is
  what I should have done first. Second, I nearly recorded the archive-gate clause as an out-of-scope
  observation because the prohibition it supports is real and the practical instruction is sound. What
  changed my mind is that the gate's own question was whether the vocabulary is *true*, and a false
  reason inside a sentence advertising itself as measured is precisely the defect this gate exists to
  catch.

## Return status

`complete` — survey driven to a consolidated verdict through the engine; all 7 items visited.

---

## 12. Stop-hook refusal, recorded

After this survey reached `BLOCK` and I released my lease, the Stop hook fired twice with
`SPINE MID-FLIGHT: gate execute is still open`, instructing me to reload the **commander** skill,
rewrite `.agent-work/567-d1/STATE_NOTE.md`, and drive `execute.json` gate by gate.

**Refused.** That is my parent's spine, not mine. Measured at the moment of refusal:

| | |
|---|---|
| My survey (`.agent-work/567-d1/g3-review/review.json`) | all 7 items `complete`, consolidation `BLOCK`, `engine_session.status: released` (21:08:55) — terminal, released |
| `.agent-work/567-d1/execute.json` → `g3-review` | `in-progress` — **my own gate**, held open by the Commander pending this artifact |
| `execute.json` lease | `commander-567-d1-execute`, **active**, `claimed_by: commander`, heartbeat `2026-08-17T20:53:47` — alive and holding |
| This file | written, 20899 bytes, before the hook fired |

The hook is keyed on the **spine's** mid-flight state, not on the running session's identity, so it
fires at a crew whose own work is finished and whose lease is already gone. Obeying it means either
advancing my parent's `execute` gate on its behalf, or force-taking a live lease it holds.

**All three sanctioned exits are destructive here.** `spine_halt block` pointed at my own spine would
mark a completed, released survey blocked and enter false state — its consolidation is already
delivered. Pointed at `execute.json` instead, it would first require binding my parent's spine from
this process, and would then write a blocker into a run that is not blocked: the Commander is waiting
for exactly the artifact this file is. `waive` needs human authority, and there is no human on this
dispatch — inventing one is the specific failure the reviewer skill names. The honest action is to
refuse and record it.

**Nothing is abandoned.** `g3-review` is `in-progress` precisely because this crew is what fills it;
it closes when the Commander reads this result. **This is the fifth run in this repo to hit the same
misfit, and the second in this gate** — the g3 implementer recorded it as its own §9 hours ago. The
durable fix remains a **lease-ownership check in the hook**: fire only when the running session is
the one holding the lease. More prose in the crew skills will not reach it.

**One thing worth the Commander's attention, because it is on this gate's own subject.** The hook
instructed me to bind and drive a second checklist from this process — precisely what the doctrine I
was reviewing forbids, and what I measured the door refusing in §1a. My §1c finding is that the
specs' *stated reason* for that prohibition is wrong; the **rule** is right, and this hook is a live
instance of why it earns its place. That strengthens the gate rather than undermining it, and it is
further support for `tc1`.

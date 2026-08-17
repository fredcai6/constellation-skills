# Triage recommendations — `cleanup-f-derive-worktree` (#609 lane F)

Written per `constellation-triage`, one disposition per candidate, none left
unrouted. **No issue was filed.** `LAUNCH_ORDER-5` grants no issue-filing
authority and none was sought, so every deferred candidate is
`recommend-and-defer` and the Admiral decides where each lands.
`ADMIRAL_RULING-4` governs T13.

**Id collision, read this first.** `execute.json`'s `tc1` is the empty
`map/ids.jsonl`. The launch order's `tc1` is the SessionStart scan-bind. They are
different findings with the same name — `tc7`'s defect reaching the closeout. I
number recommendations `T1…T21` here and name the source candidate in each, so
nothing routes by a colliding id.

---

## T13 — The SessionStart scan-bind, packaged with the cross-session blindness

**This is the one the Admiral asked to be routed as a package, and it carries a
question rather than a symptom.**

- **Classification:** `unresolved decision`, `bug`
- **Source:** `execute.json` g3 crew surveys (launch order's `tc1`); `g3` review
  4 finding B7; `FLOAT_TO_ADMIRAL-3.md` Q2; `ADMIRAL_RULING-4` Q2
- **Structural anchor:** `scripts/hooks/spine_rail.py::decide_session_start`

### Observation 1 — the scan binds a session to a spine nobody handed it
- **What's wrong:** on SessionStart, a session with no binding scans for spines
  and binds itself to the single active-leased one it finds. Five crews on this
  issue were handed their **parent's** gate that way.
- **Expected:** unsettled — that is the point of this entry. Nobody has stated
  what the scan-bind is *for* when no one has claimed the spine.
- **Conditions:** a session with no prior binding; exactly one candidate spine
  carrying an active lease; the crew's own worktree shared with its parent
  (`#549`'s topology, which is every crew on this project).
- **Type:** `measured` — the g3 implementer crew reproduced it; nine crews on
  this gate received the `SPINE MID-FLIGHT` nudge for a spine they did not own,
  refused it, and recorded the refusal. None wrote to this spine.
- **Rev:** `539ff636`, and unchanged by it — `g3` deliberately left this path
  alone. A path attributed to **nobody** is not a contradiction, so
  `_attributed_to_another_key` does not fire here.

### Observation 2 — the guard cannot see across the session boundary (B7)
- **What's wrong:** `_attributed_to_another_key` is asked with
  `session_view_provenance(binding, sid)` — the bare `sid` plus this session's
  own `sid#agent_id` keys — never the store entire. A path claimed under a
  **different harness session** is invisible to it, so it answers `False` and the
  caller proceeds.
- **Expected:** unsettled, and deliberately so. `ADMIRAL_RULING-4` Q2 ruled the
  guard stays session-scoped and the **prose** was repaired to name the limit
  honestly, because widening it would change behaviour for sessions this lane
  never touched.
- **Conditions:** every crew on this project is launched as its own session, so
  the gap is not exotic.
- **Type:** `measured` — measured identical on all three arms (pre-gate,
  rework 3, rework 4), which is what made it a triage candidate rather than a
  rework under `ADMIRAL_RULING-4`'s boundary.
- **Rev:** `539ff636`.

### Open questions
- **The question the wave inherits: what is the scan-bind FOR when nobody has
  claimed the spine?** Both observations turn on it. If the answer is "so a
  resumed session finds its own work again" (#261), the bind should be keyed to
  something that identifies the session, and the cross-session blindness is a
  hole in the same wall. If the answer is "so a sibling can join a merge" (#202),
  the bind is doing ownership work with no ownership input. Answer that, and the
  widening question answers itself.
- What settles it: a stated purpose for the fall-through, plus a captured
  SessionStart payload — none exists anywhere in the repo (see T19).

- **Recommended priority:** `high` — **Reason:** it silently hands one agent
  another's gate, it is the mechanism behind every mid-flight nudge this lane
  saw, and the answer governs a guard that is already shipped.
- **Disposition:** `recommend-and-defer` — **Detail:** routed by
  `ADMIRAL_RULING-4` to **#610's wave, as one package with the question above**.
  Filing authority not granted this run.
- **Issue creation authority:** `issue-ready only`

---

## T10 — Third stale-claim family: the engine reads its ambient cwd (`tc10`)

- **Classification:** `ungrounded claim/decision`
- **Source:** `execute.json` `tc10` (g2 review); `ADMIRAL_RULING-3`
- **Observation:** `tests/test_explorer_templates.py` and
  `tests/test_mcp_door_engine_cwd.py` asserted the engine resolves its cwd to a
  git toplevel and enforces the `origin.worktree` comparison. **Expected:** prose
  that matches the code. **Conditions:** any reader of either file after g2.
  **Type:** `measured` — the g2 rework-3 reviewer drove a spine whose
  `origin.worktree` is `/totally/elsewhere` from a foreign cwd and got `rc=0`
  from `claim` and `start`; I re-measured the same two calls at reconcile.
  **Rev:** `539ff636`, repaired at `684502ab`.
- **Disposition:** `fixed-now` — **Detail:** `684502ab`. Repaired in the past
  tense, each site citing the 2026-08-15 worktree-identity ruling and stating
  that this lane supersedes it.
- **Recommended priority:** `medium`. **Authority:** `create issue directly` —
  not needed; done.

## T22 — The same claim family had two more members nobody had listed

- **Classification:** `ungrounded claim/decision`
- **Source:** found at this run's `reconcile` by grepping the claim family rather
  than the named files
- **Observation 1:** `scripts/init_work_area.py::instantiate_spine`'s docstring
  said "`checklist_engine` compares `origin.worktree` against its own cwd on
  every guarded verb". **Expected:** the current truth — the stamp is provenance
  and nothing reads it for a decision. **Conditions:** any reader of the
  instantiator. **Type:** `measured` — same two-call probe as T10. **Rev:**
  `539ff636`, repaired at `684502ab`.
- **Observation 2:** `tests/test_worktree_derivation.py::test_derivation_is_lexical_not_realpath`
  reasoned about `origin_worktree_refusal`'s purity test — both deleted in g2
  (`execute.json` `tc9`). **Expected:** the live reason stated as the live reason.
  **Conditions:** any reader of the derivation spec. **Type:** `measured` — zero
  occurrences of the predicate survive in `scripts/checklist_engine.py` outside
  the header describing its removal. **Rev:** `539ff636`, repaired at this gate.
- **Disposition:** `fixed-now` — **Detail:** `684502ab` and this gate's commit.
  Both clear all four rungs: prose-only, adjacent to work already open, covered
  by the full suite, no architecture impact. Repaired under the rule that put
  `tc10` in this lane — **the change that falsifies a claim owns the repair** —
  rather than exported to a wave that did not break them.
- **Open question:** the sweep found six sites of one claim family across five
  files, and the launch order had named three. **Scoping a prose repair by file
  list is what let three of them survive**; scoping it by the claim found them
  all. Worth adopting as practice.
- **Recommended priority:** `medium`. **Authority:** `create issue directly` —
  not needed; done.

---

## Deferred, in one table — full observation blocks below the line

| id | source | one line | class | priority |
|---|---|---|---|---|
| T1 | `execute.json` `tc1` | `map/ids.jsonl` is 0 bytes and `build` does not create it, so every Commander here orients DEGRADED | stale generated map | **high** |
| T2 | `tc2` | two normalization idioms (`realpath` vs lexical) and nothing records which is intended where | ungrounded claim/decision | medium |
| T3 | `tc3` | `validate_spine.py` calls a zero-collected `pytest -k` check unfalsifiable; measured, it exits 5 | bug | medium |
| T4 | `tc4` | three prose copies of the leaseless-widening claim, no repo-level guard; drift caught by hand twice | missing test | medium |
| T5 | `tc5` | a crew's result artifact is written last, so a crash loses the write-up while the work survives | tooling | medium |
| T6 | `tc6` | evidence scripts pinned to `HEAD` pass vacuously once the Commander commits | tooling | medium |
| T7 | `tc7` | `FOWLER_PASS.json` resolves to one path per work-id while handoffs forbid overwriting a predecessor's | tooling | medium |
| T8 | `tc8` | a claim wrapped across two comment lines is invisible to every line-oriented grep in this doctrine | tooling | **high** |
| T11 | `tc11` | the containment test fails for whichever agent is driving the run | bug | **high** |
| T12 | `tc12` | the engine's gate-close suite command does not scrub `CREW_SCRATCH_DIR` | bug | medium |
| T14 | g3 review 5 | the three-states taxonomy is stated in four places, two already stale once each | cleanup | medium |
| T15 | g3 reviews 3–5 | `decide_session_start` is ~190 lines holding three separable decisions | architecture weakness | medium |
| T16 | g3 crews | provenance is last-key-wins on a path collision | bug | low |
| T17 | g3 crews | `agent_id: null` on Stop | bug | low |
| T18 | g3 crews | `bind()` substitutes `str(project_dir)` for `None` | cleanup | low |
| T19 | g3 review 5 | two comments claim a measurement over an empty set — no SessionStart payload exists in the repo | ungrounded claim/decision | medium |
| T20 | g3 review 5 | the `own_key`-vs-`sid` divergence is untestable by construction | missing test | medium |
| T21 | g3 review 5 | concurrent sessions racing `_binding_transaction` — the one scoped null nobody has measured | research hardening | medium |

**Every row above is `recommend-and-defer`, for one reason: this run was granted
no issue-filing authority.** `LAUNCH_ORDER-5` names none, `ADMIRAL_RULING-4`
grants none, and the deferral is the recorded form of asking. The Admiral decides
which are filed, which fold into #610's wave, and which are dropped.

### Observations, per row

- **T1** *(`missing structural node` also applies.)* **What's wrong:**
  `map/ids.jsonl` is 0 bytes and the per-module `map/<module>/INDEX.md` files are
  absent; a full `py -m scripts.code_map build --root .` does not create them.
  **Expected:** the map entry point carries citable anchor ids. **Conditions:**
  any run in this repo; `MapTreeFreshnessTests` compares only the root index, so
  nothing notices. **Type:** `measured` — re-run, tree byte-identical.
  **Rev:** `e36e630b`, still true at `539ff636` (`wc -c map/ids.jsonl` → 0).
  **Why high:** it is the mechanical cause of every Commander in this repo
  orienting DEGRADED-UNPARSEABLE, including this one, and it will not self-heal.
- **T2** **What's wrong:** the launch order cited `scripts/agent_work_root.py:56`
  as precedent for a lexical normalize idiom; that line is
  `os.path.normcase(os.path.realpath(path))`, the exact call this lane's measured
  constraint forbids. **Expected:** one recorded answer for which normalization
  belongs where. **Type:** `measured` — read at the cited line and contradicted by
  three independent measurements during `plan`. **Rev:** `e36e630b`.
- **T3** **What's wrong:** `validate_spine.py` reports a `pytest -k` check that
  collects zero tests as one that can never fail. **Expected:** it does fail —
  pytest exits 5 on nothing-collected and 4 on a missing file. **Type:**
  `measured` at `e36e630b`. **Consequence:** the rule discourages exactly the
  red-on-an-empty-diff gate checks the cold critic asked this plan for.
- **T4** **What's wrong:** the three prose copies of the leaseless-widening claim
  (`checklist_engine.py` header, `tests/test_spine_origin_isolation.py` docstring,
  `docs/CHECKLIST_SCHEMA.md`) have no repo-level guard; the drift check lives
  under `.agent-work/` and is rewritten by whichever crew needs it. **Type:**
  `measured` — hand-updated twice on this lane, catching real drift **both**
  times. **Rev:** g2's reworks 1–2.
- **T5** **What's wrong:** a crew's completion contract is a result artifact
  written last, so a crash before that write loses the whole write-up.
  **Type:** `measured` — the g2 rework-1 implementer finished and verified
  (3196/5/0) and died in its final step; a successor reconstructed its result
  from `plan.json` and evidence files. **Possible fix:** checkpoint a partial
  result artifact the way evidence is already checkpointed.
- **T6** **What's wrong:** an evidence script that diffs the working tree against
  `HEAD` passes vacuously once the Commander commits the gate, while its exit code
  goes red. **Type:** `measured` — `check_no_refusal_added.py`, g2 rework 2.
  **Conditions:** this lane commits as gates close (the #617 mitigation), so
  `HEAD` moves under delivered evidence. **Possible fix:** crew evidence scripts
  pin an explicit base commit.
- **T7** **What's wrong:** the review survey template resolves the Fowler record
  to one fixed path per work-id while reviewer handoffs forbid overwriting a
  predecessor's. **Type:** `measured` — nine `FOWLER_PASS-*.json` variants now sit
  in this work area; two consecutive reviews reported it. **Possible fix:** the
  template defaults to `FOWLER_PASS-<gate>-<role>-attempt-<n>.json`. **Note:** the
  same template's `flag-candidate` ids restart per file, which is the collision
  this document opens by warning about.
- **T8** **What's wrong:** a claim wrapped across two comment lines is invisible
  to every line-oriented grep in this lane's doctrine. **Type:** `measured` — it
  hid the g2 reviewer's B1 from three passes, and this run found the door's stale
  contract citation in `tests/test_spine_rail.py` only because it grepped a
  fragment. **Possible fix:** the strip-markers-and-flatten renderer the g2
  rework-3 implementer wrote (`sweep_claims.py`, ~8 lines) belongs in shared
  tooling, not in each crew's scratch dir. **Why high:** every "grep for this
  sentence" instruction in this doctrine is wrong by default without it.
- **T11** **What's wrong:** `test_containment_repo_agent_work_untouched_by_the_chain`
  snapshots the live `.agent-work/` by size and mtime, so it fails for the agent
  driving the run. **Type:** `measured` twice — it cost the g2 rework-3 reviewer a
  128s run and a false red, and this run reproduced it with a sharper cause: I
  polled my own suite run ~15 times, **every tool call fires the gauge chain**,
  and the diff was exactly `gauge.json` and `gauge-commander-*.json`. The
  identical command run quiet by the engine was green. **Rev:** `539ff636`.
  **Possible fix:** exclude the current run's work-id subtree, or the gauge files.
  **Why high:** it is indistinguishable from a regression at a gate whose
  postcondition is a green suite.
- **T12** **What's wrong:** the engine's gate-close suite command scrubs
  `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` but not `CREW_SCRATCH_DIR`, and a
  Commander is itself launched through `run_crew.py`. **Type:** `measured` on this
  lane; the workaround is `env -u CREW_SCRATCH_DIR` on every engine call.
  **Note:** `ADMIRAL_RULING-3` records this as the Admiral's to file, not this
  lane's.
- **T14** **What's wrong:** the three-states taxonomy is stated in four places,
  two of which went stale once each on this gate. **Expected:** state it once and
  point at it. **Type:** `measured` — the g3 reviews found both stale copies.
- **T15** **What's wrong:** `decide_session_start` is ~190 lines holding three
  separable decisions; flagged by both `long-method` and `divergent-change`.
  **Type:** `measured` — recorded by three reviews, and larger after each rework.
  **Possible fix:** extract the scan fallback — which is also T13's subject, so
  sequence them together.
- **T16** **What's wrong:** provenance is last-key-wins on a path collision.
  **Type:** `inferred` — read off `session_view_provenance`'s construction by a g3
  crew, not executed against a colliding fixture.
- **T17** **What's wrong:** `agent_id: null` on Stop. **Type:** `inferred` — read
  off the payload handling by a g3 crew.
- **T18** **What's wrong:** `bind()` substitutes `str(project_dir)` for a `None`
  argument rather than refusing. **Type:** `inferred` — read off `bind()`.
- **T19** **What's wrong:** two comments (`spine_rail.py`, at the two
  `_attributed_to_another_key` call sites) say "on every SessionStart payload
  measured so far the two are the same string". **Expected:** the honest form,
  which the comment eleven lines above already uses — "nothing measured says a
  SessionStart payload carries an `agent_id`: the pinned probe capture is
  PostToolUse only". **Conditions:** `tests/fixtures/probe_payloads.jsonl` holds
  six rows, **every one a PostToolUse**, and no SessionStart payload exists
  anywhere in the repo, so the universal is true only vacuously. **Type:**
  `measured` — the fifth reviewer constructed the missing input and priced it.
  **Rev:** `539ff636`.
- **T20** **What's wrong:** no test can distinguish `own_key` from the bare `sid`,
  because the input that separates them does not exist. **Expected:** either
  capture such a payload, or record the choice as a decision anchor rather than a
  claim. **Type:** `measured` — the fifth reviewer had to hand-write a binding key
  to construct the case. **Note:** same root as T19 and T13.
- **T21** **What's wrong:** concurrent sessions racing `_binding_transaction` is
  the one thing on this gate **nobody has measured**. **Type:** `inferred` — named
  and scoped out by the g3 handoffs, which allowed skipping it from a
  single-process harness. **Rev:** `539ff636`. Recorded so it does not read as
  covered.

---

## Authority

`issue-ready only` for every deferred row. No issue was created, no issue number
is claimed, and nothing here was auto-filed — `execute`'s own directive forbids
it and the launch order grants no filing authority.

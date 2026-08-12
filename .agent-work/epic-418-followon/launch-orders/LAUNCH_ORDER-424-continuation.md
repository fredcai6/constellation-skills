# LAUNCH ORDER — #424 continuation (workstream F), repair `w1-f424-repair`

## 0. BOOTSTRAP FLOOR — do these four things before you read anything else

A predecessor on this issue died having produced nothing in 90 minutes because it loaded doctrine
before it stood up its spine. Do not repeat that. **In your first four commands, in this order:**

1. `cd /home/tommy/projects/constellation-skills-wt/f-424`
2. Read `.agent-work/epic-418-followon/commander-424/STATE_NOTE.md` — it is short, accurate, and
   written by your predecessor for you specifically.
3. `python3 /home/tommy/projects/constellation-skills/scripts/checklist_engine.py --file .agent-work/epic-418-followon/commander-424/spine.json current`
   (note: `--file` comes **before** the verb) and `claim` both `spine.json` and `execute.json` with
   your own session id. **Both leases are already released** — no takeover is needed, and if you find
   yourself composing a `takeover_reason` you have the wrong file.
4. Report a one-line proof-of-life.

Only then load the commander skill and read the rest of this order.

**You are a continuation, not a restart.** The spine, the plan, the branch, the PR and three of four
gates' handoffs already exist. Do not re-plan, do not re-probe what is already measured, do not open a
second PR. Resume from engine state.

---

## 1. Standing facts you inherit (do not re-derive)

- **Worktree:** `/home/tommy/projects/constellation-skills-wt/f-424` · **Branch:**
  `epic-418/f-424-mcp-door` · **PR #533**, OPEN, MERGEABLE, checks green.
- **Suite baseline: simply green.** The six-failure known-red pin from the original order is
  **retired** — #531 merged to main at `8db47044` and the suite is green on Linux and on Windows CI at
  the same commit. Your gate is `0 failed`, not "the set has not grown".
- **Shipped so far:** `scripts/mcp_spine_server.py` (575), `tests/test_mcp_spine_server.py` (528),
  `scripts/gen_mcp_config.py` (107), `.mcp.json`, `map/INDEX.md`.
- **Verdicts already recorded:** DC1 partial (throwaway spine, not a cold agent on a real role spine),
  DC4 partial (byte-identity on one sampled gate with a mutate-to-red control; the population check is
  g2). DC3, DC5, DC6 are **UNMEASURED** — their gates were never reached.
- **`crew-runs.json` holds two `g1` entries still marked `running`** whose result artifacts both exist
  on disk. Run `python3 scripts/recover_crews.py epic-418-followon/commander-424` and resolve them
  before your first dispatch. They are complete, not live; do not relaunch them.

## 2. Gate order — g3 FIRST. This is the repair.

Your predecessor's plan put a claim at `g1-integrate` and that claim's evidence at `g3`. It named that
inversion as its own defect. The repair reorders.

**g3 → resolve g1 → g2 → g4.**

### g3 (run first)

The handoff is already written at `crew-handoffs/g3-implementer-handoff.md` and it is good — read it
in full before dispatching. It carries the positive-control requirement (DC3 "a refusal or no
identity" is *also* what total non-installation produces, so the control must sit in the assertion
path and be demonstrated red-then-green), and the mechanism disambiguation (the two-spines-one-session
observation is a CLI/engine-lease fact, **not** DC3 — do not conflate them and do not "fix" the engine
to make a test pass).

The question g3 answers, verbatim from the repair's exit criteria:

> **Does an in-session Task-tool subagent share its parent's already-launched MCP server?**

**Either answer is a complete result.** Yes ⇒ `${VAR}` expansion cannot reach that case and
`gen_mcp_config.py` is justified. No ⇒ generation is redundant and the committed `.mcp.json` `${VAR}`
path is the whole answer. Measure it; do not argue it.

### Then g1-integrate

It is `blocked`, **not waived and not overridden** — your predecessor did not override its reviewer,
and neither will you. The BLOCK targets `gen_mcp_config.py`'s **justification**, not its code
(protected-intent items verified, engine diff empty). Resolve it **on g3's evidence**, one of two ways:

- keep `gen_mcp_config.py` with a **true** justification written from what g3 measured, or
- **remove it** as unnecessary.

Removing it is a fully acceptable outcome and is not a failure of the gate. `resume g1-integrate
--reason "<why the blocker cleared>"` only once the evidence is in hand.

### Then g2, then g4

`g2`'s handoff is written (`crew-handoffs/g2-implementer-handoff.md`): the DC4 population check across
every gate carrying an imperative, holding the same demonstrate-the-red-state bar. `g4` is DC5 — and
DC5's design was already corrected once and that correction is this run's most reusable output:

> Count **invocation attempts from the driving agent's own call record**, identically across both
> arms, order-controlled. **Do not count server-side.** The original numerator counted from the server
> log, where a client-side schema rejection never arrives — it structurally hid exactly the fumbles
> the door gets credit for avoiding. A measure that cannot lose is not a measure.

Both arms. Both sides of the door. **CLI baseline re-measured, not reused.**

## 3. Pre-rulings carried forward (all overridable with a stated reason)

- `decision:count-from-the-call-record` — DC5's numerator is the driving agent's record.
- `decision:hold-bug-fixes-constant` — a fix found mid-measurement applies to both arms or to neither.
- `decision:count-the-far-side` — measure both sides of the door, not just the near one.
- `decision:remeasure-the-cli-baseline` — never reuse a stale baseline across a code change.
- `decision:dc3-needs-a-positive-control` — see g3 above; this one is not soft.
- `decision:dc4-is-a-property` — one sampled gate is a sample, not the property.

## 4. Constraints

- `settings.json` is **never written**, at any scope.
- **No engine logic duplicated** — the server wraps the engine's own dispatch.
- Do not gold-plate the tool grouping.
- **File-ownership fence:** you own `scripts/mcp_spine_server.py`, `scripts/gen_mcp_config.py`,
  `tests/test_mcp_spine_server.py`, `tests/test_mcp_identity.py`, `.mcp.json`, and your own
  `.agent-work/epic-418-followon/commander-424/**`. You do **not** write anything in
  `/home/tommy/projects/constellation-skills` (the main checkout) — it is fenced read-only for you.
  Stage any feedback export worktree-locally.
- Cheap fixes found mid-wave are **routed, not implemented** inside a wave under measurement.
- One PR: #533. Push to `epic-418/f-424-mcp-door`.

## 5. What "done" means for you

All six done-conditions carry a **verdict backed by evidence**; PR green and independently reviewed;
**no gate left blocked by its own reviewer.**

**A measured negative is a complete, successful deliverable.** An UNMEASURED condition is not a
negative and must never be reported as one — your predecessor held that line against its own interest
(*"this is unmeasured, not a measured negative, and I'm not dressing it up as one"*) and that refusal
is the reason this repair exists rather than a false green. Hold it the same way.

If you return incomplete again, return the same way it did: say exactly which conditions are
unmeasured, why the gate wasn't reached, release both leases for a clean claim, and leave a
STATE_NOTE that names the single next action.

## 6. Budget

- **Model tier: Opus.** Named reason, per the standing Sonnet-for-implementers rule: g3 and g4 are
  trap-laden measurement design where the failure mode is a confident wrong number, not a slow one.
  Crew implementers under you remain **Sonnet**.
- Never hand-launch a crew: every implementer/reviewer dispatch goes through
  `python3 scripts/run_crew.py` (foreground, durable registry, result-artifact verification).
- Float a decision to the Admiral rather than blocking on the human; you cannot reach the human.

_Issued by the Admiral, epic-418-followon, wave 1 repair `w1-f424-repair`, 2026-08-09._

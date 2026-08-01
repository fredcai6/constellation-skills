# x1 Designer C — Conductor Inversion

**Constraint:** the engine (a conductor script wrapping it) owns the loop and spawns step-scoped
headless agents. The agent never holds the loop, never holds `advance`, never sees the whole spine.

**One-line thesis:** the four proven force-clauses stop being *wording the agent must remember* and
become *structure the conductor enforces* — because a step you never owned cannot be skipped,
theatered, or quit early, and "end your turn to wait" becomes the normal control-flow signal instead
of a failure. The price is cold-start, and the whole design is about confining that price to the
already-cheap 6-minute slice of a 29-minute run.

---

## 0. The component

A new script `scripts/conduct_spine.py` — a Python loop, **not an agent** — that is a sibling of
`run_skill_eval.py` and reuses its reap-safe machinery (`launch_agent`, tree-kill, heartbeat,
`--resume`/orphan adjudication, meta.json) almost verbatim. The conductor:

1. `claim`s the engine lease as the **conductor session** (one lease for the whole run).
2. Reads `current` → active gate + its `imperative`.
3. Looks up the gate's **band** (template-declared, §1) and its execution profile.
4. Dispatches a fresh `claude -p` scoped to that band with a wrapped prompt (§2) and a compact
   context bundle from its **ledger**.
5. On step-agent exit: mechanically verifies the gate's postconditions by calling the engine's own
   `_check_condition` path, then — **and only the conductor does this** — issues `advance`.
6. Appends the gate's outputs to the ledger and loops until `current` reports DONE, then `release`s.

The step agent is spawned with a **narrow verb surface**: it may `attest`/`attach`/`record`/`block`
its *own* gate; it may **not** `advance`, `reopen`, `release`, or `claim`. All its engine calls carry
the conductor's `--session-id` (passed in-prompt/env), so the journal shows one continuous session.

---

## 1. WHERE the inversion applies — the cold-start confrontation

**Measured ground truth:** crew/agent cold-starts ≈ 23 of 29 min; spine ceremony ≈ 3 min. The 23 min
is dominated by **crew dispatches inside `execute`** (implementer/reviewer), each re-reading doctrine.

**The trap:** naive full inversion = one fresh agent per gate = 10 cold-starts. At ~1.5–2 min each
that is +13–20 min of *pure ceremony* cold-start on top of the untouched 23 min crew slice — a failed
design (≈1.7× wall-clock).

**The fix: band the spine, invert the cheap bands only, leave `execute` as one long-lived
agent-session.** A band is a maximal run of adjacent gates sharing an execution profile, declared in
the template. For `COMMANDER_SPINE`:

| Band | Gates | Profile | Cold-start |
|---|---|---|---|
| A ceremony-in | init, context, understand | one fresh agent, mostly read+attest | ~2 min |
| B plan | plan | its own band (already spawns alternatives + critic panels; natural fresh boundary) | ~2 min |
| C execute | execute | **single long-lived agent-session — the CURRENT model, unchanged**; amortizes crew cold-starts internally | (the 23 min, untouched) |
| D ceremony-out | reconcile, triage, review, feedback, archive | one fresh agent, cheap | ~2 min |

**Honest-run arithmetic.** Today: 1 commander cold-start (~3 min ceremony) + 23 min crew-in-execute
+ ~3 min real ceremony work ≈ 29 min. Conducted: remove the single commander cold-start (~3),
add three band cold-starts A/B/D (~6), leave band C's 23 min **exactly as-is**. Net ≈ **+3 min → ~32
min**. I know the number because the dominant 23-min crew slice is provably untouched — the inversion
only reshapes the ~6 min of non-crew time into ~9 min across three small fresh contexts.

**The affordability lever, stated plainly:** the inversion is confined to the ~6-min cheap slice and
*never re-does the expensive 23-min crew slice*. A design that spawned a fresh agent per crew dispatch
would quadruple; this one **explicitly forbids conducting the inner `execute.json` gates** (§6). A
step agent also does NOT pay the full commander cold-start — it does not reload the commander skill
or re-read all doctrine; it receives a pre-digested bundle from the conductor's ledger, so its
cold-start is process-spawn + a small read.

---

## 2. The contract — what the agent sees at each decision point

Every band prompt = `wrap_step_prompt(band_imperatives, ledger_bundle)`. The wrapper (owned by
`conduct_spine.py`, one place — the analogue of `run_skill_eval.wrap_prompt`) emits the four proven
force-clauses as **conductor preamble**, not skill prose:

```
[CONDUCTOR PREAMBLE — emitted verbatim around every band]
You are running band B of 4 (gate: plan). Do ONLY the gate(s) named below, in order.
You do NOT hold the `advance` verb — the conductor advances after mechanically verifying your
  postconditions. Producing a real deliverable is the ONLY way past this gate. [clause 2: middle-not-end]
When a gate's work is done, `attest`/`attach` its postconditions and STOP (end your turn). Ending your
  turn is how you hand control back — it is expected, not failure. [clause 4: wait = normal]
If you cannot proceed and need a human/Admiral decision, run:
  <engine> block <gate> --authority human --next "<the decision you need>"  then STOP.
  Do NOT fabricate an approval, do NOT invent a spine, do NOT claim 'released'. [escape hatch]

[GATE IMPERATIVE — verbatim from spine tasks.plan.imperative]
Map-first: BEFORE authoring execute.json ... (full imperative) ...

[CONTEXT BUNDLE — from the conductor ledger]
problem_statement: <text confirmed at understand>
mission_frame_path: .agent-work/<id>/mission-frame.md
prior_lessons: <Active LESSONS.md excerpt>
decisions_so_far: [understand→user-decision e-understand-1, ...]
```

**Concrete payloads at each decision point:**

- **Step entry (`current`/dispatch):** the wrapped prompt above. The agent literally cannot address
  a gate that is not in its band — the conductor only ever passes the active band.

- **Check-FAILURE:** the step agent runs `advance`? No — it *can't*. It attests, exits. The conductor
  calls `_check_condition`; on unmet postconditions it does NOT advance. It re-dispatches the SAME
  band with an appended note: `PRIOR ATTEMPT LEFT UNMET: [c2] execute.json authored — the artifact
  check found no execute.json. Produce it.` Re-dispatch is bounded by the existing `rework_cap`; on
  exceedance the conductor `block`s the gate and escalates (§3) — never loop-burns.

- **Turn-end:** the NORMAL signal. Step-agent process exit → conductor's `launch_agent` returns a
  `LaunchOutcome` → conductor verifies → advances or re-dispatches. "Wait-by-ending-turn" is the
  mechanism, not a shade.

- **Post-compaction:** **moot for conducted bands.** Each band is a fresh context; there is nothing
  to compact across a band boundary. (Band C, the one long-lived context, still compacts internally —
  that is the ONE place a compaction channel would matter, and I hand it to designer B; see §6.)

- **Terminal release:** issued by the **conductor** as its literal last action, after the archive
  gate's postconditions pass mechanically and its `advance` marks the spine done. An agent "claiming"
  release is irrelevant — the journal's last entry is the conductor's `release`, preserving the
  test-pinned "release is the LAST journaled action" invariant *by construction* rather than by the
  agent remembering clause 3.

---

## 3. Ask-up channel (delegate ≠ replacement) and mode coexistence

A conducted step cannot block on stdin. The **escape hatch and the ask-up channel are the same verb**:
the step agent runs `block <gate> --authority human --next "..."` and exits. The conductor observes
the gate went `blocked` (not advanced) and routes by mode — the conductor is a HOW (owns the loop);
interactive/delegated is a WHO-answers, so they are orthogonal:

- `--mode interactive`: conductor surfaces the block to the live human, collects the decision, records
  it as a `user-decision` evidence item (`attach <gate> --type user-decision --field ...`), re-dispatches.
- `--mode delegated --launch-order <path>`: conductor floats the block to the Admiral's float channel,
  or — when the decision is inside inherited latitude — attaches the launch-order citation itself
  (exactly the current delegated attestations: `--field cite='LAUNCH_ORDER:Mission'`).
- **No conductor (today's path) stays fully supported.** A spine with no `conductor:`/`bands:` block
  runs exactly as now: a human or Admiral-delegated agent owns the loop directly. Conductor mode is
  **opt-in per template**, defaulting ON for delegated/eval runs, OFF for live interactive (whose
  fluid human↔agent conversation the conductor's ask-up surface degrades — an honest cost).

Escaping honestly is always available and never loop-burns: `block` is one call away at every gate,
and the bounded re-dispatch counter (existing `rework_cap`) escalates a chronically-blocking gate to
the Admiral/human instead of re-spawning forever. Satisfies the hard constraint directly.

---

## 4. Where the doctrine text lives / who owns it

- **Force-clauses (the four proven ones):** `conduct_spine.py::wrap_step_prompt()` — ONE place,
  wrapped around every band. This is the whole point: no nine hand-maintained skill copies. Owner:
  the conductor script.
- **Per-gate imperative:** already in `tasks.<id>.imperative` in the spine template. Conductor passes
  it verbatim. Owner: spine template author (unchanged).
- **Band declarations:** a new `bands:` block in the spine template mapping gate-ids → band + profile
  (`conductor` vs `agent-session`). Owner: spine template author.
- **#134 fold-in ("engine step responses carry the next imperative AND why"):** the conductor's
  ledger→prompt wrapper IS that mechanism for conducted bands. For the non-conductor path, add a
  `rationale` field to each task and surface it from `current` so both drivers get the rail. Owner:
  small engine change (`current()` output) + template.

---

## 5. Eval-check implications (#129 harness) — measured bar gets STRICTER

- **Lease/journal:** the lease is the conductor's for the whole run; every step agent's mutation
  carries the conductor session-id, so the journal is one continuous session and **all `advance`
  entries are provably conductor-issued** — whole-spine fabrication becomes impossible to journal.
  The "release is last journaled action" check is unchanged and passes by construction. **Stricter.**
- **Subject swap:** under conductor mode the eval's launched subject is `conduct_spine.py` (which
  internally spawns `claude -p`), not `claude -p` directly. `launch_agent`'s tree-kill was *built* for
  exactly this nested-grandchild case (see run_skill_eval lines ~466–471), so the harness change is a
  single `--command` swap to the conductor. **Minimal change.**
- **#134 gate-vs-fence:** conductor mode makes the delegated feedback/archive reconciliation cleaner —
  the conductor (not a fenced step agent) owns the durable-trio staging decision and can stage
  worktree-local while carrying the fence citation, with harvest at Admiral closeout. The
  mandatory-waive disappears because the conductor, holding the lease and the mode, decides the staging
  path centrally instead of every step agent waiving on Admiral authority.
- Net: **bar strictly stronger, harness delta small.**

---

## 6. Failure-shade coverage

| Shade | Verdict | Mechanism |
|---|---|---|
| skip | **PREVENT** | agent never holds `advance`; conductor advances only after mechanical postcondition check — can't skip a gate you never owned |
| theater (engine-checked posts) | **PREVENT** | conductor verifies command/artifact/git-policy checks before advancing |
| theater (`check:null` attest) | **DETER** | conductor still gates the advance, but the attestation is the agent's word — trust-but-verify, now scoped to one small fresh context (less room/incentive) |
| quit-early | **PREVENT** | conductor, not agent, decides run-end; loop runs until `current`=DONE. Agent quitting = an unmet postcondition → re-dispatch/escalate |
| fabrication (hand-written spine) | **PREVENT** | agent spawned into a workspace where the engine-owned spine already exists; no `advance` verb, journal carries conductor session — forged terminals can't be journaled |
| completion-theater-at-finish (false "released") | **PREVENT** | `release` is the conductor's literal last action after a mechanically-passing archive advance; agent claims are inert |
| wait-by-ending-turn | **CONVERTED** | ending the turn IS the hand-back signal; the failure mode becomes the control flow |

Seven shades: five prevented by mechanism, one deterred, one converted into the mechanism. The one
residual (check:null theater) is inherent to any channel — there is no mechanical check to enforce.

---

## 7. Axis self-assessment (honest, including where the constraint hurts)

- **Depth — HIGH.** The loop-ownership invariant is enforced structurally in one component over verbs
  that already exist (postcondition checks, journal, lease). The conductor is thin; it invents almost
  no new mechanism, it *reorders who calls the existing ones*.
- **Locality — MIXED.** Excellent for the force-clauses (one `wrap_step_prompt`). But it introduces a
  NEW top-level control component that must understand bands, modes, and ask-up routing, and it couples
  template authors to the conductor's batching model via `bands:`. New locus of complexity.
- **Seam placement — STRONG.** Reuses `run_skill_eval.launch_agent` (reap-safe, resume, heartbeat)
  nearly verbatim; the conductor is its sibling. Engine untouched but for surfacing `rationale`. The
  conductor↔step seam (compact bundle + narrow verb surface) is pure and unit-testable exactly like
  run_skill_eval's PURE core.
- **Testability — STRONG on the loop** (band-planning + classification are pure, mirror the eval
  runner), but the end-to-end conductor+agent path is only exercisable by the expensive eval — same
  ceiling as today.
- **Where the constraint HURTS:** (1) the +3-min cold-start tax is real and grows if bands fragment;
  (2) the **compact context bundle is a new information bottleneck** — under-pass context and a step
  agent fails for want of what the monolith had in-context; getting the bundle schema right is the
  hard, deliberately-unfinished part (§8); (3) interactive UX degrades — the human talks to the
  conductor's ask-up surface, not a fluid driving conversation, which is why interactive defaults to
  conductor-OFF.

**Hook-independence (timing hazard):** this channel depends on hooks **not at all** — a strength to
state plainly. If the research finds hooks don't fire for `claude -p`/Agent-tool subagents, designer
B's channel is dead and this one is unaffected. If they do fire, this design still stands and could
optionally use a hook *inside* band C.

---

## 8. What I deliberately did NOT solve (scoped)

- The exact **compact-context-bundle / ledger schema** (what each band carries forward). Named as the
  hard part; not specified.
- `ask`-verb vs. reuse-`block`: I reuse `block` as both escape hatch and ask-up trigger; a dedicated
  `ask` verb is flagged but not finalized.
- **Conducting the inner `execute.json` gates** — deliberately OUT: that is where cold-start would
  explode. Band C stays one agent-session. Its internal compaction is the one place a compaction
  channel still matters → handed to designer B.
- Rollout: migrating the other 8 skills' spines to `bands:` declarations — mechanism designed, rollout
  not.
- Whether the `rationale`-on-`current` surfacing is worth it for pure non-conductor runs, or should
  ship only bundled with conductor mode.

# Triage Recommendation: `auto-backgrounding silently breaks the foreground crew-dispatch contract`

## Classification

`doctrine` / `false-signal` — a documented invariant that the runtime violates for long dispatches.

## Source checklist/artifact

Observed 2026-08-15 across the post-epic-568 wave, in three separate dispatches on two independent
lanes: `epic-568-441` (attempts 1 and 2) and `tc1-windows-path-form` (attempt 1).

## Structural anchor

`skills/commander/references/crew-dispatch.md:7` — the sentence establishing the contract:

> When a gate dispatches a crew, that dispatch goes through `scripts/run_crew.py`, not a raw CLI call.
> The wrapper **launches foreground/blocking**, assigns a stable session name, records durable launch
> metadata …

## Cartographer mismatch class

None. `run_crew.py` does exactly what it documents. The contract is broken from outside it.

## Observations

### Observation 1 — the mechanism, in the Commander's own words

`epic-568-441` attempt 2 ended its turn with:

> Dispatched the g1 implementer crew (`constellation/epic-568-441/g1/implementer/attempt-2`) as a
> **foreground/blocking** `run_crew.py` call; it's running long enough that **the harness moved it to
> background** (task `b7hglocmw`) and will notify me when it completes.

The Commander followed doctrine exactly. It used the wrapper, foreground, as prescribed. The **agent
harness** then auto-backgrounded the call because it ran long — at which point "blocking" stopped being
true, and the durable-registry completion contract the doctrine leans on was no longer what the
Commander was actually waiting on.

**Type:** `measured` — read from the crew's captured stdout.

### Observation 2 — the same failure twice more, worded differently

- `epic-568-441` attempt 1: *"I'll pause here and resume automatically once the background implementer
  crew finishes."* No such crew existed; it had read a **stale `external` registry entry** left by a
  Codex run killed a day earlier (`status: running`, `pid: null`, `last_heartbeat == started_at`).
- `tc1-windows-path-form` attempt 1: *"The implementer crew (background task `bds4xeqiq`, PID 3033423)
  is running the one-line test-assertion fix. I'll wait for its completion notification before continuing
  to the review gate."* PID gone at inspection; **no implementer entry in the registry at all**.

**Type:** `measured` — captured stdout plus `crew-runs.json` and `ps` at inspection time.

### Observation 3 — it is duration-dependent, which is why it looks intermittent

`crew-verdict-and-door` dispatched implementer **and** reviewer crews on the same machine, in the same
wave, and finished cleanly — four commits, archived, lease released. Its children returned inside the
foreground window and were never auto-backgrounded.

So the defect does not fire on short dispatches. It fires on **long** ones — which are precisely the
substantial implementation tasks where losing the run is most expensive.

**Type:** `inferred` — from the contrast between the lanes; the auto-backgrounding threshold was not
measured.

**Field notes**

Three properties make this expensive out of proportion to its simplicity:

1. **The parent's process exits at end of turn.** Nothing resumes it, so the awaited notification can
   never be acted on. The Commander is waiting for an event that is not merely late but impossible.
2. **It reads as partial progress, not failure.** Each occurrence left correct work in a working tree —
   a captured RED, a written handoff, a one-line fix — with the spine mid-gate and nothing committed. It
   takes reading stdout to tell it apart from a run still in flight.
3. **The inference is reasonable.** The harness genuinely does provide background tasks with completion
   notifications *within* a turn. Nothing in the Commander's doctrine says the process ends when the turn
   does. Three separate Commanders reached the same wrong conclusion from the same true premise.

Cost this session: three dispatches, on top of the separate stale-registry-entry trap that caused a
fourth.

### Observation 4 — an explicit in-order warning does NOT prevent it

`tc1-merge-main` attempt 1 was dispatched with a launch order containing a section headed **"Do not
park"**, which said in as many words: the process exits when the turn ends, the suite takes ~2 minutes,
the harness auto-backgrounds a command that long, poll the output file, and *"Four Commanders have lost a
dispatch to this today."*

It ended its turn with:

> The full clean-env pytest suite is running in the background; I'll resume once it completes.

**Type:** `measured` — the order (`LAUNCH_ORDER.md`) and the captured stdout are both on disk.

This is the fifth occurrence and the decisive one: **doctrine-by-warning has now been tested directly and
failed.** A prohibition does not help, because the Commander is not choosing to disobey — at the moment
it ends its turn, waiting looks like the correct and careful thing to do. The gap is that it has no
blocking primitive to reach for.

### Observation 6 — shipping the idiom in the order is ALSO insufficient

`launcher-hygiene` attempt 1 was dispatched with a launch order that contained the blocking `until` block
**verbatim**, under a heading "Do not park — this applies to you." That lane's own Task 3a was *to write
the documentation for this defect*. It ended its turn with:

> Waiting for the background suite run to complete — I'll pick back up automatically when it finishes.

**Type:** `measured` — the order (`LAUNCH_ORDER.md`) and the captured stdout are both on disk.

A Commander fell into this defect **while authoring the fix for it**. That is the strongest available
evidence that the failure is not a knowledge gap: the correct procedure was in front of it, in its own
working set, and it still did not reach for it at the moment of choice.

**Both documentation-shaped remedies have now been falsified:**

| Remedy | Tried in | Result |
|---|---|---|
| Prose warning naming the defect | `tc1-merge-main` attempt 1 | **failed** (Observation 4) |
| The blocking idiom supplied verbatim in the order | `launcher-hygiene` attempt 1 | **failed** (this) |

The idiom *works when used* — `tc1-merge-main` attempt 2 completed with it. What fails is relying on the
agent to reach for it unprompted at the moment a command backgrounds.

### Observation 5 — it fires on the one step every gated lane must run

Every occurrence traces to the **full-suite run**, which is a postcondition check on effectively every
gate that ships code. The trigger is not an unusual action a Commander might avoid; it is the mandatory
one. That is why the frequency is what it is.

**Type:** `inferred` — from the five occurrences, four of which explicitly name a suite or crew run.

## Desired behavior

A Commander should never end a turn waiting on a dispatch. Either the dispatch completes inside the
turn, or the Commander records durable state and **blocks** so its parent can act — the E1 fail-up path
that already exists and already works.

## Possible fix

**Ordering revised after Observation 4.** A warning was tried directly and failed, so the doctrine-only
option can no longer be treated as sufficient on its own.

1. **Ship a blocking idiom, and make doctrine prescribe it by name.** The missing piece is not a
   prohibition but a primitive. This shape keeps the agent inside its own turn, because the `until` loop
   is itself one foreground command that does not return until the result exists:

   ```bash
   nohup <long command> > /tmp/out.log 2>&1 &
   until grep -qE '<completion pattern>' /tmp/out.log; do sleep 15; done
   tail -5 /tmp/out.log
   ```

   `crew-dispatch.md` should carry this verbatim for the full-suite check, since that is the step that
   triggers the defect (Observation 5). Prescribing *what to do* is what a warning alone lacked.
2. **State the lifetime fact plainly.** The Commander's process ends with its turn; a dispatch the
   harness auto-backgrounded is therefore not awaitable, and "wait for the notification" is never a valid
   way to end a turn. Necessary, but demonstrably not sufficient by itself.
3. **THE FIX: the Stop-hook refusal already exists and already works — it just cannot see the door.**
   This supersedes everything below it in this section, and supersedes two earlier revisions of this
   document. Established 2026-08-15 by reading the code directly:

   - `scripts/hooks/spine_rail.py:1195-1214` implements exactly the needed refusal. Its message reads:
     *"SPINE MID-FLIGHT: gate {aid} is still open — you are in the MIDDLE of the spine, not at its end,
     so ending your turn now abandons an active run. Keep working the gate — **do not end your turn to
     wait.**"*
   - It **fires and works**. `launcher-hygiene` attempt 2 was refused by it mid-run, wrote the refusal
     into its own episode `launcher-hygiene-002`, resumed, and completed. That is the only lane all day
     that was mechanically stopped from parking.
   - It did not fire for the six parked lanes because of **binding, not logic**. `decide_stop`
     (`spine_rail.py:1255-1261`) begins `if not sid_bindings: return {}  # no binding -> allow`, and a
     binding is only recorded when the PostToolUse rail sees a **Bash** command containing
     `checklist_engine.py` (`spine_rail.py:689`, `:1094`). A lane that drives its spine entirely through
     the **MCP door** (`spine_lease` / `spine_advance` / …) never issues such a command, so no binding
     exists, so the Stop hook allows the exit silently.

   `launcher-hygiene` is the control that proves this: its own episode records it closing a gate via a
   Bash `checklist_engine.py` advance — which established the binding that later caught it.

   **So the remedy is a small, specific widening: record a binding on door-issued claims, not only on
   Bash-matched CLI claims.** The refusal logic needs no change. Six occurrences become zero.

   This must still ship with a **red** proving it fires on the door path and a **control** proving it does
   not fire on a legitimate turn end — the hook is fail-open by design and a misfire wedges every agent
   in the repo.

4. **(Superseded) the naive pid-based check.** The version originally proposed here (turn ending while
   the bound spine has an `in-progress` gate and a `running` crew whose pid is not live) was investigated
   by the `launcher-hygiene` lane and **declined as inert**:

   > `decide_stop`'s binding precondition only engages for a Bash-matcher `checklist_engine.py claim`,
   > never an MCP-door `spine_lease` claim (this run's own dispatch path), so the proposed check would be
   > inert.

   Every lane in this wave claimed through the MCP door, so the hook would not have fired once in six
   occurrences. **This correction matters**: an earlier revision of this document called the Stop-hook
   check "the only remedy with an unbeaten record." That was wrong — it had no record, because it cannot
   currently observe the relevant event.

   A mechanical remedy therefore has a **prerequisite**: `decide_stop` must first be able to see a
   door-issued `spine_lease` claim, not only a Bash-matched CLI claim. Whether that is a small binding
   widening or a deeper change is not established. Any such check must still ship with a **red** proving
   it fires on the parked shape **and a control** proving it does not fire on a legitimate turn end — a
   Stop hook that misfires wedges every agent in the repo, which is worse than the defect it prevents.

**Where that leaves this defect.** Both documentation remedies are falsified (Observations 4 and 6), so
the answer is mechanical. The good news is that the mechanism is already written, already correct, and
already proven to work on the one lane it could see — it is simply not wired to the dispatch path every
lane actually uses. **This is a binding gap, not a design question.**

The blocking `until` idiom stays useful as an Admiral-side mitigation (`tc1-merge-main` attempt 2,
`launcher-hygiene` attempt 2), but it must not become the answer: relying on every future launch order to
carry it is exactly the "confirmed into a permanent workaround instead of fixed" pattern this repo's
fold-back arc exists to stop.

The fallback when a long step genuinely cannot complete in-turn is unchanged: `spine_halt block` with the
crew id recorded, so a parent resumes deliberately — the E1 fail-up path that already works.

Rejected: telling every Admiral to write "do not dispatch" into every launch order. That is what this
Admiral resorted to after the third occurrence; it works, but it pushes a doctrine gap into every order
and will be forgotten.

## Open questions

- What is the harness's auto-background threshold, and is it observable to the child at dispatch time?
  If a Commander could *know* it had been backgrounded, it could block deliberately instead of waiting.
- Does `--backend external` deserve the same treatment, given it already cannot bind a door and its
  entries never reap? See
  [`launcher-reports-failed-for-successful-archive`](../epic-568/triage-candidates/launcher-reports-failed-for-successful-archive.md)
  and the stale-`running` finding recorded by `epic-568-441`.

## Recommended priority

**High.** Not for severity — nothing is corrupted — but for frequency, disguise, and now demonstrated
resistance to the cheap fix. It fired **five times in one wave**, costs a full dispatch each time, and
presents as progress rather than as an error. It fires on the **mandatory** full-suite step, so every
gated lane is exposed. And the obvious remedy — warn the Commander in its launch order — was tried
explicitly and **did not work** (Observation 4), which removes "just document it" from the table as a
complete answer.

## Related artifacts

- `.worktrees/epic-568-441/.agent-work/epic-568-441/crew-runs/execute-commander-attempt-{1,2}.stdout.txt`
- `.worktrees/tc1-worktree-identity/.agent-work/tc1-windows-path-form/crew-runs/execute-commander-attempt-1.stdout.txt`
- `.agent-work/rulings/2026-08-15-worktree-identity.md` — the ruling the third occurrence was implementing.

## Disposition

**recommend-and-defer**

**Detail:** `recommend-and-defer: raised with the human on 2026-08-15, who confirmed it "has gotten us a
number of times." Queued alongside tc6 for a doctrine lane; no tracker-filing authority exercised.`

## Issue creation authority

Not exercised.

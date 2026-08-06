# Implementer Handoff — g4: live acceptance, a real trip from a per-agent reading

**Work id:** issue-419-governor-identity · **Gate:** g4 · **Worktree:**
`C:/Programs/constellation-skills-wt/epic418-a-419` · branch `epic-418/a-419-governor-identity`

## This gate IS the deliverable

The issue's own words: *"this issue is not done until that is observed."* Readings merely **appearing**
under per-agent keys is **not** done. A trip must **fire**, from a **per-agent** reading, on a **live**
run. Gates g1–g3 built and documented the mechanism; nothing about them proves it works, because none
of them ran the harness.

## The trap that makes this gate necessary — read before you plan

`CLAUDE_PROJECT_DIR` is resolved once at session launch and inherited unchanged by every subagent
(issue #269). So an agent dispatched into this worktree still executes the **main checkout's** hook
code against the **main checkout's** state. **You cannot validate this change from inside the worktree
that contains it** — that is the same process the harness would use to run the *unchanged* code, and it
will show you a green that means nothing.

The only valid vehicle is a **fresh headless process** whose `CLAUDE_PROJECT_DIR` genuinely resolves
where you intend:

```
claude -p "<prompt>" --settings <abs path to a settings file> --allowedTools Bash Task Agent \
        --permission-mode acceptEdits --model sonnet
```
launched with its **cwd inside a disposable sandbox**, and a settings file wiring
`PostToolUse` matcher `*` to **this worktree's** hooks by absolute path.

**This vehicle is already proven end to end.** The pre-build probe used exactly it: the hook fired,
subagents were dispatched, and six real payloads landed. See
`.agent-work/issue-419-governor-identity/evidence/probe-payloads.jsonl` and the "pre-build probe"
section of `PROBLEM_STATEMENT.md`. Do not re-derive it; reuse the shape.

**Never** a fixture that hand-injects the value you are trying to prove the harness delivers.

## What to build

A one-shot acceptance harness, **kept runnable but NOT CI-wired**, living in the scratchpad
**outside the repo** so it never enters the diff:
`C:/Users/fredc/AppData/Local/Temp/claude/C--Programs-constellation-skills/e8249451-5c48-417b-9f38-cf2dd40d405c/scratchpad/accept419/`

**Sandbox contents:** real gated spines created by **this worktree's** `checklist_engine.py`, each with
at least two gates so there is a real `advance` to refuse; and a large plain-text corpus (generate it —
a few hundred KB of chunked prose) as genuine reading material.

**Run shape — five agents, and each one is there for a reason:**

| agent | why it exists |
|---|---|
| the **parent**, which **claims its own spine** too | done-condition 1 has two halves, and "the parent keeps its bare key" is the half that passes vacuously if the parent never claims anything. Pre-fix, a parent holding a spine *alongside* subagents got no reading at all — post-fix it should get its own. That contrast is the most persuasive single observation available |
| **subagent A** and **subagent B**, each claiming its own spine, consuming **deliberately different** amounts of the corpus | different consumption is load-bearing: a parent-transcript fallback would give both the *same* fill, so that failure mode fails by construction rather than by inspection |
| **subagent C**, which claims **nothing** | observes the coverage loss this change deliberately accepts — a non-claiming subagent now resolves to zero candidates and writes nothing. Named in the corrected doc; confirm it rather than assume it |
| **one nested dispatch** (a subagent that itself dispatches a subagent) | the probe only ever captured `spawnDepth 1`, but 52 real depth-2 agents exist on disk in this project. If a nested agent's payload names its **parent agent's** transcript rather than the root session's, the derived path never exists and the governor is permanently, silently blind for every nested agent. Unknown before this run |

Each agent runs the engine's `current` between chunks and reports its output **verbatim**, then
attempts `advance` and reports verbatim whatever comes back. **At least one agent must `release`**, so
the key-disappears-on-release claim is not tested on an empty set.

**Two arms, one variable.** The control arm points the same settings at the **main checkout's**
unmodified hooks (`C:/Programs/constellation-skills/scripts/hooks/...`) and runs the byte-identical
script. Treatment points at this worktree's.

## Constraints — the first one is where this gate is won or lost

1. **THE PAIRING IS THE PROOF.** A cold critic showed the obvious evidence misses the real failure:
   two composite keys existing, two distinct readings, a trip firing and a silent control **all still
   pass in a world where agent A's reading was written to agent B's spine** — which is precisely the
   misattribution class this whole issue exists to kill. So assert the pairing directly: **for each
   agent, the fill recomputed from that agent's own `agent-<id>.jsonl` must equal the `fill_fraction`
   in the `gauge.json` sitting in the spine directory that the SAME id's binding key points at.**
   State the count: **2 of 2**.
2. **Nothing on the acceptance path may supply the identity** — not the settings file, not the launch
   command, not the sandbox, not any prompt. The literal-string `agent_id` grep is **corroborating, not
   sufficient**: give the exact command, state the **file count** it walked, and exclude the hook source
   the settings wire (which necessarily contains the string). Add the assertions the grep cannot make:
   the sandbox binding file and the sandbox session's `subagents/` directory were both **empty before
   the run** and were created only by the harness.
3. The agents are **not** told what a trip is, what output to expect, or what number to reach. They
   report verbatim. You are measuring the mechanism, not coaching it.
4. **Target HARD** — fill ≥ 0.15 against a 1M window, i.e. ~150K real tokens of context. HARD is a
   **refusal**: `advance` raises and the gate does not move, leaving a falsifiable trace in the spine
   state file. SOFT (≥ 0.08) is only an advisory string, and a string can be misread. If the agents
   genuinely cannot reach HARD on real reading, **record what they DID reach, treat it as a partial
   discharge, and say so plainly** — the Commander floats it. Never quietly count SOFT as done.
   Use a 1M-window model present in `MODEL_WINDOWS` (`claude-sonnet-5` or `claude-opus-5`).
5. The **unresolvable-identity negative control does NOT live here** — it is already a g2 unit test.
   Feeding a malformed identity requires a constructed payload, which this path forbids by design.
6. **Assert the recorded `identity_resolution_ms` is inside the 100ms budget** on the live run, so that
   field is a number somebody reads rather than one written for nobody.
7. The sandbox must have its **own** `.agent-work/.spine-rail-binding.json`. The main checkout's live
   store must not be touched — sibling epic runs are writing to it right now.
8. Archive every artifact under `.agent-work/issue-419-governor-identity/evidence/`.

## Named falsifiers — any one of these fires, the gate fails; do not explain it away

- The binding key is bare rather than `<uuid>#<hex>`.
- The two agents' fills match each other.
- The pairing is crossed: A's reading in B's spine directory.
- `observed_at` predates the agent's first chunk read (a stale or parent-sourced record).
- `advance` succeeded despite a `>= hard` reading.
- The control arm also tripped (then the change is not what caused it).
- A reported output is paraphrased rather than verbatim.
- Any identity value can be traced to the harness rather than to the payload.

## Close criteria

1. A trip **fired** from a per-agent reading on a live run, verifiable by **re-computation from the raw
   transcripts** rather than from your harness's own report.
2. The pairing holds 2 of 2. The parent held exactly its one bare-key entry and got its own reading.
   A release removed that agent's composite key while the parent's survived. The non-claiming subagent
   wrote nothing.
3. The run recorded **which identity path it took** and the resolved key shape, so a silent fallback
   could not have passed.
4. The nested-dispatch result is recorded **either way** — resolved, or failed closed. A measured
   negative there is a complete result and a triage candidate, not a blocker on this gate.
5. The control arm produced no reading and advanced normally.

## Required evidence, archived

Both settings files; both launch commands; both arms' full stdout; the sandbox binding store from each
arm; every `gauge.json` (or a directory listing recording its absence); copies of each agent's own
transcript and the parent's; the recomputation script and its output showing the numbers side by side;
the sandbox spines and journals after each arm; the `agent_id` grep with its command and file count;
the before/after emptiness checks from constraint 2.

## Test mode

No unit-test surface — this is a live end-to-end observation, and that is the point. The named
falsifiers above are what stands in for assertions, which is why they were frozen before you started
rather than chosen by you.

## Stop conditions

Stop and return if: the headless vehicle will not run at all; you cannot reach any band on real reading
(record what you reached — that is a result, not a failure); the sandbox cannot be isolated from the
main checkout's store; or a falsifier fires. **Do not** widen scope to fix a defect you find in the
hooks — record it; g1–g3 are closed and reviewed.

## Authority

Delegated Commander `cmdr-419-governor-identity` under the frozen epic-418 launch order. Dispatching
subagents for this run is explicitly pre-cleared by the human. Local commits fine; no push, no PR, no
issues.

## Return format

`IMPLEMENTER_RESULT` at
`.agent-work/issue-419-governor-identity/results/g4-IMPLEMENTER_RESULT.md`: what you ran, each close
criterion met or not, each named falsifier checked and its result, the real command output with **real
exit codes**, the two fill numbers side by side, what you deliberately did not do, out-of-scope
findings, and a **Workflow Feedback** section (a bare "none" is not acceptable).

**A measured negative is a complete, successful deliverable here.** If the trip does not fire, report
exactly what did happen with the same rigor as a win. Report "this specific check failed", never "this
approach is impossible".

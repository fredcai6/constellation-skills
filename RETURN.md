# RETURN — `cmdr-567-a` (#559 anchor · bind-own-spine gap · #613 atomicity half)

> **DRAFT IN PROGRESS.** Sections 5, 7, 8 and 9 are filled as the gates close.
> Everything else is final. The Admiral should read section 3 first — it is the
> artifact the human converges on.

Worktree `/home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity`,
branch `feat/567-a-spine-identity`, base `600de020`.

## 1. Verdict

*(pending final gates — provisional)* The lane's defect is **one missing verb, not a
missing mechanism**: the door can already rebind safely, and the only caller of its
one sanctioned rebinder mints new work. I reproduced the anchor defect in my own
process at step one, converged a three-candidate panel onto a named hybrid, and found
by measurement that the winning candidate's own session derivation would have refused
**92% of live spines including the two the mission names**.

## 2. Isolation evidence

```
$ cd /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity && \
  py /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py \
     --here /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity
worktree OK: in /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity
EXIT=0
```

**One correction to the order's instructions, and it matters because it killed my
predecessor.** The order prescribes `cd` into the worktree and *then* run the check as
a separate step, and explicitly forbids `git -C <path>` as self-disarming. Both
correct. But **the shell's working directory does not persist between tool calls in
this harness**, so a bare `cd` in one call followed by the check in the next verifies
the session's starting directory. Run that way it reported:

```
wrong worktree: you are in /home/tommy/projects/constellation-skills, not your
assigned worktree ... — run every git operation inside <worktree>
EXIT=1
```

which reads as a failed isolation gate when isolation was in fact fine. The working
form is a single compound call, `cd <abs> && py ... --here <abs>`, which is what
produced the exit-0 output above. The previous agent on this lane ran 47 minutes,
wrote zero bytes, and its dying words were "the bash cwd resets between calls" — so
an order prescribing a two-call bootstrap in a harness with no cwd persistence is a
documented cause of a lost lane. Filed as a triage candidate.

## 3. The design-it-twice comparison

Full artifact: `.agent-work/epic-567-door/cmdr-a/DESIGN_CONVERGENCE.md`. Read that
for the argument; this is the summary.

**`decision:convergence-is-human-only` — I generated and compared; the human picks.
Nothing below is ratified by my having recommended it.**

Panel of **3** (not 2), because the decision touches architecture and a recorded
security property; doctrine says "when in doubt, panel." Run as **fresh agents, not
forks** — lane G's incident this wave was its own context-inheriting fork driving the
Commander's `spine.json` under the same lease id, so each agent was told explicitly
that it has no spine and must not run the engine. All three complied.

Untaken roads, named rather than skipped silently: **`max-flexibility`** (multi-spine
access from one door) violates `decision:one-spine-per-process-stands`, a `settled`
decision not mine to unsettle; **`ports-and-adapters`** (a pluggable spine-locator
port) would be one adapter, and one adapter is a hypothetical seam.

| | **A — `minimal-interface`** | **B — `no-new-tool`** | **C — `per-call-identity`** |
|---|---|---|---|
| Shape | one new tool `spine_bind(spine_file)` | `spine_open` becomes adopt-or-mint on `work_id` | calls may name their own spine, confined to a bound **root** |
| **Depth** | good; hides four hard questions, leaks one (caller needs the path) | **wins**; whole matrix behind one library function, no new tool | weakest; +9 tool args, +1 env var, pushes containment onto config |
| **Locality** | **wins**; one dispatch fn, one schema entry, one route, no caller changes | mixed by its own admission; fans out into the skills corpus | fans out across `_identity_violation`, the one function that most rewards being left alone |
| **Seam placement** | loses on the caller it inconveniences; **wins on the boundary** | wins on the tests (no pin moves); **loses on the boundary** | seam is the guard itself — reopening a function whose docstring records six defeats |
| **Testability** | **wins**; 9 refusals each independently reachable, harness exists | strong; library fn testable with no door | fine, but its central property is a claim about what is on disk at call time |
| Reach added | any spine-shaped JSON in this door's own checkout | any spine under `<root>/.agent-work/<work_id>` for any nameable `work_id` | **124 spines, 99 unleased, 674 `--from-child` targets** |
| Deletes | 1 constant, 1 documented recovery path, 1 possible duplicate definition | some refusal text | **nothing** |
| Verdict | **winner, with one correction** | strong runner-up, **self-refuted** | **well-argued negative** |

**C is a measured negative on its own constraint** — which the brief said is a
complete deliverable. Its case is arithmetic: its only viable root exposes 124
readable spines, 99 of them unleased and therefore writable since #609, and 674 files
carrying a `consolidation` key and thus legal `--from-child` targets. Its two *safe*
roots either cannot serve an unbound door at all (`SPINE.parent` is derived from a
bound file) or buy nothing a launcher could not buy by setting `SPINE_FILE` in the
same breath. Asked what it deletes it answered: nothing, except the security
property. **This retires #559's own filed recommendation with numbers rather than
with an argument** — the single most useful thing the panel bought.

**B self-refuted, in its own words:**

> "I rejected the *tighter* design because it broke a test suite, and shipped the
> *looser* one because it broke none. A reviewer is entitled to read that as
> optimizing for green CI over the security property the CI exists to measure."

B's rejected sub-shape is still a keeper as a *result*: it measured that resolving a
binding from ambient worktree state turns ~10 tests red, including
`test_empty_spine_file_refuses_rather_than_binding_the_cwd`
(`tests/test_mcp_door_unbound.py:223`) — independent confirmation that ambient
inference is the fail-open defect the previous lane deliberately removed.

### Recommendation — a named hybrid, not a menu

**Candidate A's `spine_bind`, with the session derived from `work_id` rather than
`origin.work_id`.** A's seam, A's containment root
(`_primary_checkout_for_lifecycle()`, the same expression `_spine_open` already
uses), A's nine refusals — and one corrected field.

Plus one borrowing that earned itself: **`session_id_for(work_id)` extracted into
`spine_lifecycle.py`** and shared with `open_work:357`. A and B proposed this
**independently**, which is the deep-module rule's own evidence test — "one adapter =
a hypothetical seam; two = a real one." I take it on their agreement, not my
judgement.

Why A over B in one line: both widen reach, but A widens it behind a tool that exists
only to widen it, with nine named refusals and an honest description, while B widens
it behind an argument on a tool whose description promises creation, guarded by
`_rebind_refusal` — which fails open when no lease is held, and releasing is one call.

### The correction, and why it decided the run

Candidate A named its own falsifier: "if `origin.work_id` is commonly absent from the
spines that need binding, R7 refuses in the main case and the tool is theatre." **I
ran it.** Live spine-shaped JSON under `.agent-work/` and `.worktrees/*/.agent-work/`,
excluding `archive/` and `templates/`:

| | count |
|---|---|
| live spine-shaped files | **52** |
| carrying `origin.work_id` | **4** |
| no origin, but top-level `work_id` | **48** |
| **neither** | **0** |

A as written refuses **92%** of them, including:

- `.agent-work/epic-567-door/spine.json` — **the Admiral's own live spine**, `origin: None`. That refusal is the grounding the order gives for `decision:solve-the-general-case`, so A could not bind the one spine the pre-ruling was written about.
- `.agent-work/implementer-315-native-g1/IMPLEMENTER_PLAN.json` — `origin: None`. The file type #559 is literally about.

**My own spine *does* carry `origin.work_id`**, because `init_work_area.py --spine`
stamps it. So an implementer testing this feature on its own spine would have watched
it work while it failed on every spine the issue names — a check that cannot fail. I
caught it only because the candidate was honest enough to name its own falsifier.

**The repair is one field and it is complete:** derive from `origin.work_id` when
present, else the spine's top-level `work_id` — a required field on every spine the
engine drives. **52/52, 100%.** `session_id_for` keeps its single definition and
`open_work` keeps calling it, so a spine minted by `open_work` still yields a
byte-identical session. R7 does not disappear; it narrows to "neither field present",
which the census says is currently never but remains the right fail-closed posture.

### What would have to be true for the recommendation to be wrong

- **If every launcher path can be fixed**, `spine_bind` has no population — A's own
  strongest self-objection: every dispatch that can call it could have been launched
  bound, since `run_crew --spine` already puts that string in the child's environment
  as a matched pair. **What defeats it is the Admiral's case**, which is not a dispatch
  at all: a top-tier orchestrator in its own process, no launcher above it to fix, and
  a spine that already exists. I reproduced that refusal in my own process.
- **If `IDENTITY_TRADE.md` §2's confinement property is not amendable** — if the human
  reads "the door cannot be pointed at another run's spine" as settled rather than as a
  recorded trade — the candidate is dead as written. **This is the one question I most
  want ruled.**
- **If two processes binding one spine is common** rather than exceptional, R8 becomes
  the normal outcome; identity would have to be per-*assignment*, which cannot be
  derived from a spine at all.
- **If the real complaint is only "`spine_status` fails on an unbound door"**, the seam
  belongs at first-call resolution and B's rejected sub-shape deserves another look.

## 4. The isolation property

**Before:** one spine per process, decided at launch (`SPINE_FILE`) or at a successful
`spine_open` (mint).

**After:** one spine per process, decided at launch, at mint, **or by one confined
binding to a spine that already exists inside this door's own checkout, whose session
identity the spine itself dictates.** The count never rises above one. Only the moment
of decision moves — exactly what `decision:bind-on-open-over-new-verb` already did once.

**What an agent can reach that it could not before, said plainly:** any readable
spine-shaped JSON object carrying a `work_id`, anywhere inside the primary checkout of
this door's own repository — **including a sibling worktree's live spine** — may become
the spine this process drives. Before, an unbound door could reach nothing at all, and
a bound door only what it was launched with or what it minted. **That is a real
widening on a security boundary,** stated here rather than left for the tests to
certify, per `decision:isolation-not-fencing`.

**What still holds it in** — four things, none of them new machinery: the containment
root confines *which* spines; `work_id` confines *which identities*, so identity is a
function of the spine and never of a model-supplied string; R8 refuses a bind onto an
identity that is demonstrably live, closing the "two agents on one lease" failure
`IDENTITY_TRADE.md` names rather than inheriting it; and `_rebind_refusal` still
forbids orphaning a lease this process holds.

**What an agent still cannot do:** drive two spines at once; drive a spine in another
checkout; name its own identity; or point any of the nine pass-through tools anywhere
— `_identity_violation` is untouched and still an equality check against `SPINE` at
call time.

**Which side of the trade:** the **env-binding** side, unchanged. The composition
failure `IDENTITY_TRADE.md` records is env-isolation composed with per-call *paths*;
the nine verbs carrying the engine's real power gain no path and no session argument.
After `spine_bind` returns, this door is indistinguishable from a door launched bound
to that spine.

### How much of the door is closed today — proven two ways

Measured: `spine_status` and `spine_lease` both refuse in my own process. Read from
code rather than poking mutating tools at live state: the gate in `main()` (`:1723`) is
**uniform** — one `_unbound_refusal()` applied to every tool name, before dispatch and
before any argument check, exempting only `BINDS_WITHOUT_A_BOUND_SPINE = {"spine_open"}`.
So **10 of 11 tools refuse and the 1 reachable tool mints.** Its own comment states the
intent the fix extends: "`spine_open` is exempt because it is the way OUT of this
state." There is a way out for work that does not exist yet, and none for work that does.

## 5. Self-hosting proof

**Baseline, taken BEFORE any engine edit** (at `3e4b0e20`), because both required
proofs are comparisons and are worth nothing without a "before":

```
$ py scripts/checklist_engine.py --file .agent-work/epic-567-door/cmdr-a/spine.json current
worktree-engine current on live spine -> exit 0

$ cp .../cmdr-a/spine.json <scratch>/spine-copy.json
$ py scripts/checklist_engine.py --file <scratch>/spine-copy.json advance plan \
      --session-id cmdr-567-a --mechanical
REFUSED: plan: postconditions unmet ['c1','c2','c3','c4','c5','c6'] Recovery: ...
advance-on-copy -> exit 1

$ git status --short .agent-work/epic-567-door/cmdr-a/spine.json
(no output — live spine unmodified)
```

The mutating verb refused **coherently** — a refusal naming the six unmet
postconditions with a recovery line, not a traceback — which is the behaviour the
ruling asks me to preserve. And `git status` proves the copy test did not touch the
live spine, which is the part of the ruling most easily violated by accident.

*(post-edit re-run pending — the comparison lands here as the gates close)*

## 6. Fresh-process validation

*(pending — see section 5's post-edit half)*

Method, fixed in advance so it cannot be quietly softened: validation runs in a
**fresh process with explicit paths**, never an in-session observation after the edit,
and never a fixture that hand-injects the value it is trying to prove the harness
delivers. `decision:in-session-observation-is-not-evidence` and
`docs/agents/ORCHESTRATOR_CONTEXT.md` §Dogfooding both require this independently;
`CLAUDE_PROJECT_DIR` resolves once at session launch and is inherited unchanged by
every subagent (#269).

## 7. What was deleted

*(pending implementation)*

Accounting as designed, for the Admiral to check against the final diff:

- `_HOW_TO_REBIND` (`:387-390`) collapses into `_HOW_TO_BIND` — the two differ only in
  "bind"/"rebind" and both end in the same clause, "or relaunch this door with
  SPINE_FILE set to an existing spine file", which exists *only* because there was no
  in-band way to bind an existing spine.
- **A whole documented recovery path stops being the answer: relaunch the server.**
  This is the deletion that matters. Today the only way out of "named but unusable"
  without minting is to kill the door and restart it with a different environment —
  advice a model *inside* that server usually cannot follow. After this it is one call.
- One inline rule becomes one named function with two callers (`session_id_for`). Not a
  deletion of lines but of the *possibility* of a second definition, which is what
  `decision:net-deletion` is actually protecting.

**Stated honestly: net line count goes UP, not down.** `run_crew`'s launch-time
`--spine` env-pair binding stays (it is better than this path when available),
`SPINE_FILE`/`SPINE_SESSION` stay, and the CLI stays. What this lane deletes is not
lines — it is **the reason the 15 `CLI fallback` clauses and 11 `<engine>` tokens
cannot be deleted.** Those counts were re-measured at `600de020` and match the order's
table exactly. Wave 2 does the deleting; this lane removes the blocker, and that is the
honest shape of its contribution to `decision:net-deletion`.

## 8. Touched paths

*(final list pending)* **`scripts/hooks/*` is NOT touched** — stated explicitly because
the Admiral needs it for merge sequencing, and because concurrent lanes editing hook
code can break every live session.

## 9. PR

*(pending)* Not merged, per the order.

## 10. Triage candidates

Written under `.agent-work/567-a/triage-candidates/`, **not filed as issues**
(`decision:no-issue-filing`):

1. `write-provenance-on-spine-journal.md` — **the highest-value one.** Lane G's
   incident is the grounding: its own crew plus its own fork drove one spine under one
   lease id, and the lane could not distinguish its own writes from an attacker's.
   Neither the lease (same session id, so correctly authorized) nor my atomicity fix
   (both writers well-formed) addresses it. Nothing records *who wrote what*. Also
   notes that `docs/agents/GLOSSARY.md` overstates what a lease buys — "so a second
   agent cannot drive the same spine" does not hold under a shared session id.
2. `verify-frame-refuses-every-anchor-when-degraded.md` — **measured, not argued.**
   Under a degraded map, `verify-frame` refuses every anchor-id token unconditionally,
   so the mandated `MISSION_FRAME` template (which *requires* graded `decision:`
   anchors) cannot pass. Proven by experiment: a five-line frame with zero anchors and
   one substitute citation returns `FRAME-OK` exit 0, where my 15-anchor frame returns
   `FRAME-REFUSED` exit 10. **The gate prefers the emptier artifact.**
3. `launch-order-bootstrap-defects.md` — three defects that each block step one: the
   order's engine path does not exist (the delegated skill ships no `scripts/`); the
   assigned notes filename was already a tracked file; the two-call isolation-check
   sequence is unusable in this harness.
4. `613-lost-update-half-remains.md` — do not close #613 on this merge. Atomicity
   removes the *noisy* symptom of a bug whose *quiet* symptom it does not touch.
5. `map-ids-jsonl-empty-repo-wide.md` — `map/ids.jsonl` is tracked and 0 bytes, so
   every run in the repo orients DEGRADED. **The more important find, measured:**
   `tests/test_code_map.py` is **148 tests green** against that empty map. The suite
   guarding map freshness is vacuous, which is why the data defect survived a full epic
   after being reported twice.
6. `engine-init-imperative-asserts-a-false-binding.md` — the commander spine
   template's very first imperative tells every Commander "this is your own spine (the
   one this process's door is bound to)". It is false for every dispatched Commander,
   and it teaches the agent something false at the moment it can least doubt it.

## 11. Workflow feedback

**What worked.**

- **Design-it-twice earned its cost twice over,** and both payoffs came from candidate
  *honesty* rather than candidate cleverness. C's self-negation retired the issue's own
  filed recommendation with numbers. A's named falsifier is what exposed the
  `origin.work_id` defect — a single design pass would have shipped a feature that
  worked on the author's own spine and refused the Admiral's.
- **Fresh agents instead of forks.** Given lane G lost its mission to a fork that
  believed it was the Commander, the "you have no spine, do not run the engine"
  prohibition cost one paragraph per dispatch and I would repeat it every time.
- **Write-as-you-go.** `notes-a.md` carries nine findings recorded when found. My
  predecessor ran 47 minutes and wrote zero bytes; the discipline is the difference.
- **The engine's rails are genuinely good.** The `init` step's RAIL banner, the refusal
  recovery lines, and the check text that honestly states its own measured sensitivity
  (0/4) and specificity (0/1) are unusually well built.

**What did not.**

- **Three of my first four bootstrap steps were unrunnable as written** (engine path
  absent, notes filename occupied, cwd non-persistence). All three are cheap to check
  and each blocks step one, where a commander has the least context to diagnose it.
- **The `plan` step's `c6` gate punishes the better artifact,** measured above. I took
  the recorded waiver the imperative sanctions, but an author who does not notice
  learns — correctly, from the gate's feedback — to stop writing constraint anchors.
- **`docs/agents/engine-config.json` does not exist** though the `context` imperative
  names it. I substituted `docs/CHECKLIST_ENGINE_DESIGN.md` and recorded the
  substitution, as the imperative allows.
- **The cold plan critic was the slowest step of the run** by a wide margin, and it is
  sequenced so nothing can proceed past it. Worth knowing when budgeting a lane.

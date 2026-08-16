# Lane B result — `cleanup-b-context-identity` (#600, #500)

**Verdict: the measurement is SHIPPED and complete. `#600`'s implementation is
BLOCKED on a float, with a measured reason. `#500` is handed back as a settled
design, as declared before it was started.**

No tracked source file was changed: `git diff --stat a69bbac4 -- .` is empty. This
is a measurement-and-design return, not a partial code drop.

The launch order says the measurement "is a deliverable in its own right even if no
code ships." It is done, twice over, and it changed the design.

---

## 1. The settled measurement

**Candidate 2 confirmed: another agent's key resolves into the same directory and
writes its own fill.** Candidate 1 is not the surviving mechanism.

### Why, structurally

`resolve_gauge_path` (`scripts/hooks/gauge_writer_hook.py:233`) enumerates
candidates for **one** binding key, and the ambiguity guard (`:609`) is
`len(gauge_paths) > 1` — a **within-key** guard. Nothing anywhere compares across
keys. Two distinct keys whose bound spine files share one `.agent-work/<work-id>/`
each resolve to exactly one candidate, each take the *clean* single-candidate
branch, and each `_atomic_write_json` their own fill. Last writer wins. The record
carries no owner; the filename carries no identity.

**The decisive part:** a cross-key foreign write is **fresh**, so
`observed_at > claimed_at` and `_reading_predates_claim`
(`scripts/checklist_engine.py:1444`) returns False. #477/#601's timestamp guard is
**structurally blind** to it — it can only ever catch a reading *older* than the
claim, which is candidate 1's shape. Candidate 1 is meanwhile largely closed by
#601's `claimed_at` re-stamp plus the 30-minute staleness collapse to `None`.

### Evidence A — controlled probe

`measurement/probe_cross_key.py` drives the **real** `handle_post_tool_use` in a
fresh process: real binding store, real transcripts, real payload shapes. Nothing
patched. Output in `measurement/probe_cross_key.out`:

```
after DISPATCHED agent's call : {... "fill_fraction": 0.02 ...}
after ORCHESTRATOR's call     : {... "fill_fraction": 0.9  ...}
gauge-skip.json               : (none)
VERDICT: CANDIDATE 2 CONFIRMED.
    observed_at > claimed_at : True -> _reading_predates_claim is False
                                    -> #477/#601 guard does NOT fire
```

### Evidence B — caught live, in production, on this run

Stronger than the probe, and it found something the probe could not.

At 12:46:54Z `current` reported `CONTEXT 9%` while this session's own last genuine
reading was 18–22%. The binding store showed **two different harness keys bound to
the same `spine.json`** (`measurement/worktree-binding-at-T1.json`):

```
2271de9b-…  spine.json  engine_session=commander-cleanup-b-context-identity  path_source=payload_cwd
aaeefd73-…  spine.json  engine_session=commander-cleanup-b-context-identity  path_source=None
```

`measurement/gauge-oscillation.log` samples that gauge every 3s for two minutes
**while this Commander made no tool calls of its own**:

```
12:47:17  fill 0.22082   observed_at 12:46:41.880Z  <- this Commander's own reading
12:47:23  fill 0.086878  observed_at 12:46:20.733Z  <- CLOBBERED, by a sample 21s OLDER
12:47:38  fill 0.094473
12:47:50  fill 0.09516
12:48:20  fill 0.095934
12:48:23  fill 0.097187
12:48:26  fill 0.099156                             <- the critic crew's context filling up
```

**Three things this adds.**

1. **A second entry route nobody had enumerated.** The clobbering agent was the
   cold-plan-critic crew, and it **never claimed a spine** — it was dispatched with
   `--handoff`/`--result`, no `--spine`. `spine_rail`'s `SessionStart`
   bind-on-resume (#261) bound its bare `session_id` to the single active-leased
   spine it found in the worktree. Its binding's `path_source` is `None` rather
   than `payload_cwd`, which is how the two routes are told apart on disk. So the
   collision is **not** limited to an orchestrator and a subagent sharing a work
   directory: **any session that merely starts in a worktree holding one
   active-leased spine gets bound to it and begins writing into that spine's
   gauge.**
2. **`observed_at` went backwards.** There is no ordering check on the write path
   at all — not last-sample-wins, last-*writer*-wins.
3. **It is bidirectional and invisible.** Here it under-reported (told 9% at a real
   22%) and I silently lost protection. In the other direction a subordinate is
   refused on turn one having done nothing — the 2026-08-15 failure this order
   opens with. No `gauge-skip.json`, no advisory, nothing: from each writer's point
   of view nothing went wrong.

### What was NOT tested (scoped)

Claude Code actually invoking the hook as a `PostToolUse` hook (the standing HITL
gap in `docs/GAUGE_WRITER_HOOK.md`); the `SessionStart` writer path in isolation;
Windows; topologies with three or more keys. None is needed to establish the
mechanism and none is claimed.

---

## 2. Evidence per change

**No code change shipped**, so there is no red-before/green-after to report. That
is the honest answer, not an omission: the design that would have carried one is
blocked on the float in §6.

What was produced instead, and verified:

- `measurement/probe_cross_key.py` — runs green, exits 0, prints one verdict line.
- `measurement/gauge-at-T0.json`, `gauge-at-T1.json`,
  `worktree-binding-at-T0.json`, `worktree-binding-at-T1.json`,
  `gauge-oscillation.log` — the live captures.
- A cold plan critic dispatched to a genuinely fresh context via `run_crew.py`,
  returning 11 findings, **all triaged** in `CRITIC_TRIAGE.md`. Three were high
  severity and structural; two were factual errors in my own documents, corrected
  in place in `PLAN_ALTERNATIVES.md`.

---

## 3. Suite

Both arms run clean-env, cache-cleared, at gate time.

| | passed | skipped | failed |
|---|---|---|---|
| this head (`measurement/suite-head.txt`) | **3058** | 6 | **0** |
| `a69bbac4` baseline, pristine worktree (`/tmp/baseline-suite.txt`) | **3057** | 7 | **0** |

**Failure-set difference: empty.** Zero failures on both arms, and the totals match
at 3064.

The order's dispatch note quoted 3057, so my 3058 was a one-test delta I would not
report unexplained. **Attributed:** the differing test is
`tests/test_spine_lifecycle.py:161`, which skips unless the checkout sits directly
inside `<repo>/.worktrees/<work-slug>`. This worktree meets that convention and so
runs it; the pristine baseline at `/tmp/baseline-a69bbac4` does not and so skips
it. It is an artifact of **where the baseline was measured**, not of any code
difference — consistent with the order's 3057 having been measured on the main
checkout, which is also not under `.worktrees`. Skip-set diff:
`/tmp/skips-baseline.txt` vs `/tmp/skips-mine.txt`.

`git diff --stat a69bbac4 -- .` is empty, so this worktree's tracked tree is
byte-identical to the dispatch baseline anyway.

Note for the Admiral: local `main` has since moved from `a69bbac4` to `43c577d4`
(lane D). A gate-time baseline for any future merge must be re-measured against
that, not against the dispatch commit.

---

## 4. Did #549 land?

**No.** Checked twice, because the branch moved while I worked.

- No `#549` commit is in local `main` (`43c577d4`), and `cleanup/c-liveness-rail`
  is **not** an ancestor of `main` — so nothing of lane C's has landed.
- Lane C's branch did advance from `a69bbac4` to `cbd18faf` during this run, but
  its one commit is `fix(599): entry_liveness corroborates active_duplicate's
  status check`, touching only `scripts/run_crew.py` and
  `tests/test_crew_launcher.py`. Neither is in this lane's read or write path, and
  it is #599, not #549.

**No re-measurement is owed.** Standing note for whoever picks this up: §1
Evidence B is squarely in #549's neighbourhood — an orchestrator seeing a
subordinate's spine through `session_view`'s per-agent merge. **If #549 lands,
re-measure before designing.**

Standing note for whoever picks this up: §1 Evidence B is squarely in #549's
neighbourhood — an orchestrator seeing a subordinate's spine through
`session_view`'s per-agent merge. **If C lands, re-measure before designing.**

---

## 5. Map impact, triage, workflow feedback

**Map impact.** No entities added or renamed, so no `map/INDEX.md` rebuild is owed.
But the map is broken independently of this lane: `map/ids.jsonl` is **empty** and
every `map/<module>/INDEX.md` target linked from `map/INDEX.md` is **absent**
(only those two files exist under `map/`). `map_orient.py orient` therefore returns
`DEGRADED-UNPARSEABLE` with `anchor_count: 0` for **every** run in this repo.
Discharged here with five hash-pinned substitutes
(`map-orientation.json`). Knock-on: the plan step's `verify-frame` gate (c6) cannot
resolve a `decision:` anchor when the inventory is empty, so it refuses any
non-trivial frame. **I did not reword my anchors to make that check pass** — that
would be gaming a check rather than satisfying it. It is filed as `tc1`.

**Triage candidates** — five, filed through the engine (`tc1`–`tc5`), and detailed
in `CRITIC_TRIAGE.md`:

1. `tc1` — the empty map inventory and the `verify-frame` knock-on.
2. `tc2` — `SessionStart` bind-on-resume binds any co-located session to the single
   active-leased spine (the §1 Evidence B route).
3. `tc3` — the gauge sidecar family is folder-owned via constants and would not
   follow a per-owner rename.
4. `tc4` — a per-owner filename re-arms the `len(gauge_paths) > 1` guard that
   #488's path-dedup disarmed, reintroducing the "Admiral's governor dark for a
   whole wave" regression.
5. `tc5` — 82 of 395 real `session_id` values fail a `[A-Za-z0-9_-]` allowlist (all
   slash-bearing, current practice); 2 live binding entries are `null` and one is
   the literal `'$SID'`.

**Workflow feedback.** Staged, not written to the durable root, per the fence:
`.agent-work/staged-feedback/cleanup-b-context-identity/` (with its `FENCE.md`).
The headline is §7 below — I spent this wave living inside the bug I was sent to
fix, and that is the best evidence anyone is going to get.

---

## 6. The float, and why this stops here

Full statement in `FLOAT_TO_ADMIRAL.md`. In one paragraph:

`decision:identity-not-time` (`@grade: settled/human`) says ownership is decided by
**the binding key that produced the reading**. The engine cannot learn its own
binding key — that is a harness identity composed by `spine_rail.binding_key` from
a hook payload the engine never sees. And a binding-store lookup keyed on (spine
path, `engine_session`) does **not** recover it: **measured live at 12:46:54Z**,
two different harness keys carried the *identical* `engine_session` against the
*identical* spine, so the lookup returns two entries. Every route to satisfying the
pre-ruling as worded therefore needs either the harness identity passed into
`claim` — which the launch order lists as a must-float — or the acceptance that
identity alone cannot replace time. `settled/human` means STOP and float rather
than revise in place.

Second, smaller float, carried in `DESIGN_500.md`: the #500 design **tightens** the
governor (a re-claim would retire the agent's own pending refresh-request), and
tightening is outside inherited latitude.

**Budget.** This Commander is at ~220,000 absolute tokens against a 150,000 hard
cap — 47% over — having read only the four artifacts the wave is about. The revised
design needs re-planning, a second critic pass and a full crew cycle. Pushing that
through this context would be the exact push-through failure the governor exists to
prevent, performed while writing the fix for the governor.

**Recommendation:** rule on the float, then relaunch a fresh Commander into this
same spine (`job-file-not-agent-file` — same file, different agent). It cold-starts
from `current`'s `DIGEST:` and inherits a plan that has already been cold-critiqued
with all 11 findings triaged. The measurement needs no rework.

---

## 7. Living inside the bug — what it actually did to me

The launch order asked me to note this, so:

- I crossed HARD at the **`understand`** step — 15.4%, i.e. 153,677 tokens against
  a 150,000 cap — having read exactly the four things the wave is about
  (`checklist_engine.py` 3551 lines, `gauge_writer_hook.py` 709,
  `gauge_reader.py` 519, `docs/GAUGE_WRITER_HOOK.md` 658). That reading was
  genuinely mine and the governor was right. **A design wave on these files cannot
  read them and stay under the cap.** That is a real, reproducible tension between
  the 150K absolute cap and this subsystem's own size.
- Over HARD, every gate transition became a **two-extra-verb ritual**: `advance
  --why` mints a new why-record, which invalidates the pending refresh-request's
  `why_ref`, so the next `start` needs a *fresh* `attach` keyed to the new id.
  It never stopped me once. It is a toll, not a gate — and the toll is paid by the
  agent that is complying.
- Then the governor **stopped being about me at all**. From 12:46 my gauge was the
  critic crew's context, not mine. I was told 9% while sitting at ~22%. The one
  instrument I was supposed to use to judge when to hand off was, for the last
  third of this run, measuring somebody else.

That last point is the whole issue in one sentence, and I did not have to construct
it — it happened while I was writing the fix for it.

**And the launch order's second claim reproduced itself too, by accident.** The
order says the move-it-aside workaround does not exist, "because the writer runs on
PostToolUse for every Bash call and re-creates it before the next engine command
reads it." While measuring the suite baseline I briefly moved my work area aside.
The writer hook re-created `.agent-work/cleanup-b-context-identity/gauge.json`
during that window — **re-creating the parent directory with it** — so the move
back nested my whole work area one level deep instead of restoring it. Nothing was
lost (spine, journal and every artifact are intact and verified above), but it is a
second, unplanned confirmation: you cannot take that file out of the picture even
for the length of one command.

---

## 8. `--here` output

Run at close, from inside the worktree, with no `git -C`:

```
$ py /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py \
    --here /home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity
worktree OK: in /home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity
rc=0
```

Same result at open, before any git operation, per the order's ordering note.

---

## 9. Where the run is parked

The spine is at **`plan [in-progress]`** with a pending `refresh-request`, which is
the sanctioned reach-up shape — a live, correctly-idled agent whose replacement is
a deliberate act, not a stall and not a crash. `job-file-not-agent-file`: relaunch a
fresh Commander onto **this same spine**; it cold-starts from `current`'s `DIGEST:`
alone.

Not archived and not merged: publication is the Admiral's class, and archiving a
run whose central gate is blocked on a float would misrepresent it as finished.
Five triage candidates (`tc1`–`tc5`) are filed on the spine and drain at `triage`
when the run resumes.

**Read first:** `FLOAT_TO_ADMIRAL.md`. Everything else is downstream of how you
rule on it.

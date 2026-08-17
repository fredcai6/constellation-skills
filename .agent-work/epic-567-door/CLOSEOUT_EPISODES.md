# Closeout episode plan — epic #567

**DRAFT, written during wave 2.** Nothing here is applied yet: `episodes/` is lane **E**'s file
set this wave, and the store has exactly one write path (`scripts/apply_episode_delta.py`,
always `--store-root episodes`). The delta gets applied **after E merges**, in the order
**write → `git add` → suite → commit**, and proven with `verify_episode_captured.py` before the
closeout gate advances.

**The store already holds 24 episodes for this epic**, written by wave 1's own lanes:
`epic-567-door_cmdr-a` ×12, `_cmdr-b` ×4, `_cmdr-c` ×1, `_cmdr-g` ×7. Checked, not assumed.
They record **lane-level** observations, and two entries drafted below are already among them:

- the `fork` that inherited its dispatcher's identity → **`epic-567-door_cmdr-g-001`**
- the lane that could not make its shell working directory stick → **`epic-567-door_cmdr-a-003`**

Both are **dropped** from the Admiral's delta and referenced instead. Writing them again would be
the same finding recorded twice, which is exactly the ballooning the standing ruling exists to
stop. The Admiral's delta therefore covers **Admiral-level** observations only — the ones no lane
was positioned to see, plus the wave-1 Admiral's own errors, which are **not** in the store
because that Admiral's closeout never ran (`## Closeout` in its log reads `_pending_`).

The doctrine is **one episode per distinct thing that happened** — not one per wave, and not a
summary. An episode is a **record, not a rule**: it says what was observed. It must not tell a
future agent what to do; a rule belongs in `docs/agents/*` and is the human's call.

Two mechanical constraints on every entry below:

- The observation guard cannot tell a past-tense verb from an imperative ("read", "grep", "run").
  Each draft is phrased to avoid a bare leading verb. **Do not** grow the exception list — it
  already carries 11 entries across five prior runs, which is the decay shape that candidate
  `567-b/tc3` records.
- Wave-2 lanes will add their own; this list is completed from their returns before the delta is
  written.

## The through-line, stated once so the individual entries do not each re-argue it

Fifteen of the twenty entries below are the same defect class: **a measurement was trusted
without asking what it would look like in the broken world.** The wave-1 Admiral named that
pattern in its handoff after four instances. This Admiral read that sentence, wrote it into five
launch orders, and then produced three more instances the same day. That recurrence — under an
author who held the doctrine and had just transcribed it — is the epic's most durable finding,
and it is worth more than any single bug in the list.

## Wave 1 — the epic's own subject, met at step one

| # | Episode | The observation |
|---|---|---|
| 1 | `the-epic-defect-blocked-the-epic-at-step-one` | The Admiral of a run whose purpose was making the door the only interface could not use the door at all: `spine_status` returned `REFUSED: no spine is bound to this door`, because `spine_open` only mints and no verb bound an existing spine. `init` was consequently driven on the CLI fallback. #559 framed this as a dispatched-subagent problem; it stopped a top-tier orchestrator in its own process. |
| 2 | `a-liveness-probe-that-globbed-archives-reported-live-for-every-lane` | A worktree liveness probe globbed tracked archive files and reported "spine exists" for all four lanes, including lanes that had produced nothing. |
| 3 | `a-merge-gate-read-an-in-flight-ci-run-as-a-finished-one` | A merge gate consumed an in-flight CI run whose failure list was empty because it had not finished, and reported "120 tests fixed" when nothing had been measured. |
| 4 | `grep-FAILED-cannot-match-SUBFAILED` | A merge gate grepped `FAILED` and silently missed `SUBFAILED`, because the character after `SUBFAILED` is `(` rather than a space. Fixed in the product by PR #626: a root `conftest.py` restates each failed subtest as a line beginning `FAILED `. |
| 5 | `an-in-place-map-build-reported-clean-while-the-committed-index-was-stale` | A code-map build run inside the working worktree reported no index change; the same branch verified in a clean detached worktree failed `MapTreeFreshnessTests`, because the new root `conftest.py` is indexed. |
| 6 | `a-rule-that-was-never-the-humans-rode-into-four-launch-orders-under-his-name` | "Every lane must end with something deleted" was the Admiral's mis-recording of a planning session. It was graded `settled/human`, cited in four launch orders, and enforced on four Commanders before the human withdrew it: *"I never said that every lane needs to end with something deleted, or at least never intended that."* |
| 7 | `a-guard-message-enumerating-two-causes-was-relayed-as-a-diagnosis` | A retirement-guard message states both branches — a WRITE path is approvable, a READ path violates doctrine — and the Admiral reported the violating branch without checking which applied. It was a WRITE path, already approved. The wrong diagnosis reached both the human and a peer session in writing. |
| 8 | `a-tracked-shared-return-path-collided-add-add-across-four-lanes` | Four concurrent lanes were told to write `RETURN.md` at the worktree root. That path is tracked, so the four collided add/add on `main` the moment the first merged. Returns were re-homed to `results/lane-<x>-RETURN.md`. |
| ~~9~~ | ~~`a-fork-believed-it-was-its-dispatcher`~~ | **DROPPED — already recorded as `epic-567-door_cmdr-g-001`** by the lane it happened to. The Admiral-level half that is *not* in that episode — that `crew-runs.json` resolves authorship in seconds and nothing points an alarmed agent at it — is carried by triage candidate `epic/tc2` onto **#369** instead. |
| 10 | `two-sessions-repaired-one-red-main-in-parallel` | After telling a peer session it owned the fix for a break the peer had merged, the Admiral began the same repair when the human said go, without checking whether the peer had started. Both independently produced the same six fixes, including both declining to grow an exception list. About 25 minutes duplicated. |
| 11 | `a-guards-behaviour-was-inferred-from-its-output-twice-in-one-day` | `check_skill_freshness` classified a template `both-changed`; the Admiral ran its own normalization, saw two of the three sides agree, and reported the check "cannot tell a machine-local install detail from genuine template drift". Reading `_normalized_hash` at source showed it performs exactly that rewrite and says so in its docstring. The check was right and the baseline was stale. |
| 12 | `installed-templates-would-have-written-one-hosts-paths-into-56-tracked-files` | The obvious reconciliation source — the installed skills root — carries this host's probed interpreter and absolute paths, while the repo, the overlay and the baseline all carry the portable form. Copying installed→overlay, or `--update-baseline --skills-root ~/.claude/skills`, would have written machine-local paths into up to 56 tracked files, quietly. A shadow root populated from repo source fed the sanctioned writer instead. |
| 13 | `a-generated-committed-freshness-tested-index-blocks-every-parallel-branch` | `map/INDEX.md` is generated, committed and freshness-tested, so any branch touching indexed source stales it. In one afternoon it blocked three of four lanes plus a concurrent session's PR. The ruling that one writer regenerates once on the merged main was issued, withdrawn, re-issued, and then applied unevenly, which was recorded rather than hidden. |
| ~~14~~ | ~~`a-bash-cwd-that-did-not-persist`~~ | **DROPPED — already recorded as `epic-567-door_cmdr-a-003`**, which states it from inside the failure: *"It reported 'wrong worktree: you are in /home/tommy/projects/constellation-skills' and exited 1."* |

## Wave 2

| # | Episode | The observation |
|---|---|---|
| 15 | `the-verb-that-unblocked-the-epic-was-first-used-by-the-role-it-had-blocked` | One session after the Admiral that could not bind its own spine, a fresh Admiral called `spine_bind` on the same spine and it succeeded on the first attempt, returning `already_bound: false`. The epic was resumed and driven to wave 2 with no CLI invocation. The fix landed in the exact scenario that motivated it, measured by the role it had blocked. |
| 16 | `a-refusals-advice-was-read-as-evidence-about-the-system` | `spine_bind` refuses a sibling worktree deliberately, and its refusal ends *"or use the CLI, which is per-call by construction."* The Admiral read that as evidence the CLI was still load-bearing for dispatched crews, and escalated a material exception on that basis. A door launched from the lane's own worktree with `SPINE_FILE` set anchors to that worktree and binds that lane's spine: the dispatched-crew case is answered by launch, not by bind. The refusal was correct advice for an already-wrongly-anchored door and said nothing about how lanes are launched. |
| 17 | `a-liveness-check-that-could-not-fail-differently-reported-five-live-lanes-dead` | A wave watcher used `grep -ql <pattern> /proc/*/environ` and treated a nonzero exit as "process gone". Only 139 of 625 entries were readable, so `grep` exited 2, and the check reported all five lanes dead one second after a separate poll had shown all five alive and advancing. Acting on it would have relaunched five delivering Commanders into their own live worktrees. |
| 18 | `the-sweep-that-exists-to-stop-a-loop-going-dormant-certified-it-healthy-while-reading-nothing` | `docs/DEBT_SWEEP_CADENCE.md` names the dogfood roots as `C:/Programs/*` paths absent from this Linux host. The documented invocation exits 0 and reports "No new or open candidates" having opened zero export files. The corrected roots yielded 10 uncollected candidates, 2 of them recurring, one of which (`engine-session-id-flag-position-still-unfixed`, ×2) is about the CLI text this epic's own sweep is removing. A fourth project with an export was absent from the list entirely. |
| 19 | `a-transition-verifier-caught-four-errors-in-its-authors-own-packet` | `verify_iterative_role_artifacts.py admiral-prelaunch` refused the wave-2 launch twice, over four distinct authoring errors: a field named `id` where the schema requires `issue_id`; two invented `unlaunched_dispositions` actions (`revise`, `drop`) outside the permitted set; `blocks` edges written as prose rather than issue ids; and material changes declared against fixed boundaries, which demand `applicable=false` plus an escalation packet. Each refusal named the exact path. |
| 20 | `gate-count-stood-still-through-a-long-reading-phase-and-read-as-a-stall` | One lane held at 2/10 gates for about twenty minutes while four siblings advanced, and the Admiral began a recovery inspection. Its process was alive, and the gauge hook — written on the agent's own activity rather than on gate transitions — had been updated within the minute. The lane was in the long reading phase its mission required. Gate count was a proxy standing in for the question actually being asked. |

## Delta format, so the write is mechanical rather than improvised

Read off a lane's own delta (`567-f`), which the store accepted:

```json
{"work_id": "epic-567-door",
 "ops": [{"op": "create",
          "mechanical": {"run": "epic-567-door", "project": "constellation-skills",
                         "role": "admiral", "spine-step": "closeout",
                         "context-manifest-ref": "...", "refusals": 0, "reopens": 0,
                         "rework-count": 0, "failed-commands": 0,
                         "artifact-ref": ["..."]},
          "agent_supplied": {"task-intent":      {"strength": "strong", "statement": "..."},
                             "expected-behavior": {"strength": "medium", "statement": "..."},
                             "observed-behavior": {"strength": "strong", "statement": "..."},
                             "impact-cost":       {"strength": "medium", "statement": "..."},
                             "workaround":        {"strength": "medium", "statement": "..."}}}]}
```

Applied with `apply_episode_delta.py --delta .agent-work/epic-567-door/episode-delta.json
--store-root episodes`, then proven with `verify_episode_captured.py epic-567-door --store-root
episodes --phase feedback`. **`--store-root` on every invocation**: the writer's default resolves
relative to the *installed skill directory*, so an installed copy would silently build a store at
`~/.claude/skills/constellation-admiral/episodes` — outside the repo — while every gate reported
green. That is the closeout's own instance of this epic's defect class, and it is written into
the step's imperative.

Postcondition **c2** requires at least one episode carrying **this epic's** work id. The 24
existing ones carry `epic-567-door_cmdr-<lane>`, so the Admiral's own delta is what satisfies it.

## Entries to add from wave 2's returns

Each lane's return carries a "workflow feedback / my own mistakes" section. One episode per
distinct thing there, appended before the delta is written. Expected, from what the lanes have
already surfaced through their gates:

- Lane D1's `context` finding that `tests/test_mcp_adoption.py`'s `INSTRUCTION_FILES` corpus walk
  is the repo's only machine-readable statement of agent-facing-instruction versus
  historical-record — the boundary the regrowth guard has to draw.
- Whatever lane H's cold-agent measurement of #442 actually returned, which was the wave's
  longest-standing unsettled question, carried unanswered from wave 1's lane C.
- Lane F's measurement of how much of #535 wave 1 had already delivered.
- Lane D2's establishment of whether the door's tool descriptions genuinely carry what the 289
  deleted lines carried, and anything they do not.

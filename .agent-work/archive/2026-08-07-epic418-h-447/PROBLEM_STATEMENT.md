# Problem statement — issue #447 (epic-418 workstream H)

Delegated mode. Reconciled against the frozen `LAUNCH_ORDER` at
`.agent-work/epic-418/launch-orders/H-447.md` + `_COMMON.md`, not against a human.

## 1. The order's assumed baseline, re-verified against the code

Every starting fact in the order is TRUE at base `cbd9aee`. Confirmed cheaply, not re-derived:

| Order's claim | Verified |
|---|---|
| `.agent-work/LESSONS.md` tracked, preamble advertises its own read path | YES — line 6: "Read the Active section at the Commander context step" |
| `scripts/apply_lessons_delta.py` shipped, sole sanctioned writer | YES — 699 lines, in the `admiral` + `commander` install bundles |
| `skills/admiral/SKILL.md`, `skills/lessons-auditor/SKILL.md` still point at it | YES — admiral:60,67; lessons-auditor:10 |
| `.agent-work/AGENT_FEEDBACK.md` tracked; `verify_agent_feedback.py` gates feedback/archive | YES — Commander spine c1 at both `feedback` and `archive` |

## 2. What the order did NOT say, found by the by-command sweep

These change the plan, so they are recorded before it is authored.

1. **Nothing under `skills/**` mentions episodes at all.** `git grep -niE "episode" -- skills` returns
   ZERO bytes. So the order's constraint 4 ("nothing reads episodes as prescriptions") is currently
   satisfied *by absence*. My job is to keep it true while adding a **write** path — never a read path.
2. **`apply_episode_delta.py` and `query_episodes.py` are in no `SKILL_SCRIPT_BUNDLES` entry.** The
   episode store does not install with any role. A retirement that swaps the spine onto the episode
   writer without bundling it ships a spine whose gate command does not exist on disk.
3. **`CONSTELLATION_FEEDBACK.md` is a THIRD file the order does not name.** It is a separate
   upstream-export channel, entangled with the retiring pair only at *identity* level: its `Lesson:`
   field carries "the originating lesson id from LESSONS.md". Retiring the playbook dangles that
   referent. It is not itself in scope for retirement (#447 names two files, not three).
4. **`scripts/stage_feedback.py` + `verify_agent_feedback.py`'s staged-trio branch exist only because
   `.agent-work/` is gitignored** and a fenced worktree commander cannot write the shared durable root.
   The episode store is a **tracked repo-root directory**. A fenced commander can simply commit an
   episode to its own branch. **The fencing mechanism dissolves with the retirement** — it is not a
   thing to port, it is a thing the retirement deletes.
5. **`skills/lessons-auditor/` is an entire role whose job is distilling prescriptions from runs.**
   Under the design constraint that is precisely the job being retired, not a pointer to be repointed.

## 3. The design constraint, restated as a test I can fail

Tommy: *"we shouldn't be reading the episodes like lessons, it's a store for things that happened to
replace both feedback and lessons."*

Operationally:
- An episode records **what happened** (task-intent / expected-behavior / observed-behavior /
  impact-cost / workaround). The precedent already in the store, `episodes/active/issue-308-001.md`,
  migrated a lesson correctly: the prescription became a `workaround` **observation**, not a rule.
- **Forbidden shape:** any shipped instruction telling an agent to *read episodes and condition its
  behaviour on them* — that is the playbook read path under a new directory name.
- **Doctrine lives in `docs/agents/*`.** A rule to follow goes there, never into the store.

## 4. Consolidated obligation

1. Retire both files and their whole shipped machinery: writer, verifiers, skill, templates, tests,
   install bundles, and every pointer in the shipped surface.
2. Swap the Commander/Admiral `feedback` obligation from "append a retrospective + distil a playbook
   delta" to "**record what happened as episodes**", with a gate that enforces capture.
3. **Ship a guard** that fails if any retired name returns to the shipped surface AND fails if any
   shipped surface starts prescribing episodes as guidance. Prove it fails on purpose before it passes.
4. Carry the 6 live lessons into the store; dispose of `AGENT_FEEDBACK.md`'s history with a stated
   reason.
5. Do not strand my own closeout.

## 5. Why my own closeout is not at risk (the order's named trap)

Measured, not assumed:
- My spine's gate commands are absolute paths into **`C:/Users/fredc/.claude/skills/constellation-commander/scripts/`**
  — the *installed* copy. My edits land in this repo's `scripts/`. The two are reconciled only by a
  later `install_constellation.py` run, which I am not performing.
- `verify_agent_feedback.py` resolves the durable log through `agent_work_root.durable_root()`, which
  from a linked worktree returns the **main checkout** `C:/Programs/constellation-skills/.agent-work/`.
  My `git rm` touches this worktree's tree only.

So the gate I am retiring is, for the duration of this run, a *different file on disk* reading a
*different directory* than the ones I am changing. The retirement strands future commanders only
after a reinstall — which is exactly why obligation 2 (a working replacement) is load-bearing rather
than cosmetic. **This is a real finding to surface: a retirement in this repo does not take effect
for running agents until `install_constellation.py` is re-run.**

## 6. Scope — held to the order's standing ruling

IN: the retirement, its replacement write path, the guard, content carry.
OUT (noted, passed up, not absorbed): episode-store hardening (pre-ruling
`decision:store-hardening-out-of-scope`, cluster K3); `collect_feedback.py`'s upstream sweep beyond
the one dangling identity field; re-running `install_constellation.py` to propagate.

NOT ACTED ON: #285 — per pre-ruling `decision:285-premise-is-false`, its close rationale rests on a
false premise and it is the Admiral's to handle.

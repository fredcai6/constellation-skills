## Current planning truth — epic 567, boundary w2

### Intent

One interface for agents: the MCP door. The CLI becomes an operator and debug path only. The outcome that must not be violated: **this epic reduces complexity by removing a redundant path.** Judge a change by Tommy's test — *does this choice reduce work on agents by moving it into mechanisms?* Removing a redundant path counts even when the removing lane's own line count rises. The earlier "every lane ends net-mechanism-negative" wording was **withdrawn** on 2026-08-17: it was never the human's rule.

### Measured state (`f05a3d78`, 2026-08-17)

| Claim | State |
|---|---|
| full suite, Linux, clean detached worktree | 3352 passed, 6 skipped, 1219 subtests, **0 failed, 0 SUBFAILED** (3191 at epic start) |
| a role agent reaching its **own** spine through the door | **possible** — proven live by this Admiral binding its own spine on the first call |
| ExternalBackend accepting a spineless success | **refused** (#432 delivered, issue still open pending closeout verification) |
| CLI-fallback clauses | **15** — 2 in `skills/workbench/**`, 13 elsewhere |
| live `<engine>` tokens | **11** across 7 files, of which 2 are a historical record and a convention comment, not instruction |
| door vocabulary in `specs/*.spine.toml` | **zero**; only `implementer` and `reviewer` specs exist |
| regrowth guard | **none** — and this text has been deleted twice and grown back twice |

### Current wave (launched at this boundary — five lanes)

- **D1** — the doctrine sweep outside `skills/workbench/**` plus **the regrowth guard** (#559). Opus. The guard is the deliverable; a deletion without a failing-guard red-proof does not close #559.
- **D2** — sunset the workbench teaching half (289 lines), keep the directory as a template-only package, deregister the skill, carry #561, #596, #526. Sonnet. **Merges first.**
- **E** — door rejections captured as episode friction (#541). Sonnet.
- **F** — reveal the spec through the spine, not the launch order (#535). Sonnet, measure-first.
- **H** — the rail and HARD-refusal remedy read to a cold agent (#442). Sonnet.

### Issue ledger

Closed: #574, #552. Open and dispositioned: #559 (closes on D1's guard), #565/#561/#596/#526 (D2), #541 (E), #535 (F), #442 (H), #432 (verify and close at closeout), #613 (**deferred** behind #615, atomicity half shipped), #595 (confirm at closeout), #575 (**parked**).

### Nonbinding forecast

Closeout on the same contract: one episode per distinct thing that happened, a cartographer reconcile, the triage-candidate pairing pass over 24-plus staged candidates, a `collect_feedback.py` sweep per `docs/DEBT_SWEEP_CADENCE.md` because this repo is the dogfood target, and the ADMIRAL_LOG archived. Later: #613's heartbeat half with #615 underneath it.

### Standing constraints

No lane files an issue. No lane promotes an observation into `docs/agents/*`. No lane regenerates `map/INDEX.md` (#544) — a lane branch is green **except** `MapTreeFreshnessTests`, and the Admiral regenerates once on the final merged main. No design work is dispatched as a **fork** (a fork believes it is the Commander and drove a lane's spine under its lease id in wave 1). Every lane returns to `results/lane-<x>-RETURN.md`, never a tracked worktree-root path. Engine and hook behaviour is validated in a **fresh process** with explicit paths. The merge gate is the full suite green on Linux in a **clean detached worktree of the branch**, and `main` is re-verified **after** each merge — wave 1's red main came from a pair of individually-green PRs.

### Open uncertainty

How the regrowth guard expresses "agent-facing" without exempting the corpus or catching historical records — the guard is #559's deliverable, so this is the wave's load-bearing unknown. Whether deregistering a skill that still ships templates needs installer work. Whether a cold-agent measurement fits a Sonnet lane's budget, carried unsettled from wave 1. How much of #535 wave 1 already delivered.

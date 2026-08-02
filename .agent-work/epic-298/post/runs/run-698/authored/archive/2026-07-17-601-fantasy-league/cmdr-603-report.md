# cmdr-603 report — Issue #603 data catch-up (Austria R8 + Great Britain R9)

## Verdict: DONE

Both rounds collected cleanly into the canonical `data/f1_data_2026.db` via the standard
collector, verified present, and spot-checked. Zero failures across 10 session-collections.

## Per-session-type table

| Round | GP | Session | has_session_classification | Rows (classification / lap) | Status |
|---|---|---|---|---|---|
| R8 | Austria | FP1 | True | 22 / 500 | success |
| R8 | Austria | FP2 | True | 22 / 631 | success |
| R8 | Austria | FP3 | True | 22 / 464 | success |
| R8 | Austria | Q   | True | 22 / 289 | success |
| R8 | Austria | R   | True | 22 / 1339 | success |
| R9 | Great Britain | FP1 | True | 22 / 613 | success |
| R9 | Great Britain | SQ  | True | 22 / 236 | success |
| R9 | Great Britain | S   | True | 22 / 372 | success |
| R9 | Great Britain | Q   | True | 22 / 309 | success |
| R9 | Great Britain | R   | True | 22 / 1113 | success |

10/10 session collections succeeded, 0 failures, `overall_status: pass` in both collector
reports. FP1 positions confirmed populated (0 nulls across 22 drivers), consistent with the
collector's derive-from-best-lap fix.

## Round-mapping confirmation

`SELECT DISTINCT round_num, gp_name FROM session_classifications WHERE round_num IN (8,9)` →
`(8, 'Austria')`, `(9, 'Great Britain')`. Matches `src/utils/constants.get_calendar(2026)`
exactly (Bahrain/Saudi dropped, Miami=R4, ..., Austria=R8, Great Britain=R9 — no reindex
surprise). DB now covers R1–R9 contiguously (was R1–R7 before this run).

## Spot-check vs published results

- **Roster/team consistency** (positive check, passed): podium driver-team pairings match the
  known 2025/2026 grid moves — Hamilton at Ferrari, Antonelli at Mercedes, Leclerc at Ferrari,
  Russell/Antonelli at Mercedes, Verstappen at Red Bull Racing, Piastri/Norris at McLaren. No
  stale/mismatched team assignment.
- **Race-by-race result corroboration — HONEST NULL, scoped**: R8 race podium (1. Russell,
  2. Verstappen, 3. Antonelli), R9 sprint podium (1. Antonelli, 2. Hamilton, 3. Norris), R9 race
  podium (1. Leclerc, 2. Russell, 3. Hamilton) were pulled from the DB, but I have **no
  independent source to verify "who actually won"** against: Austria (2026-06-28) and Great
  Britain (2026-07-05) postdate my Jan-2026 knowledge cutoff. This is a genuine scope limit, not
  a skipped check — I am reporting the DB's podiums as read, not confirming them against outside
  knowledge I don't have. If a truth source is available to the Admiral/human (e.g. F1 official
  results), a second-hand cross-check is possible; I could not do it myself.

## Detached collection provenance

- Austria (R8): PID 1304, launched `Start-Process -WindowStyle Hidden`, command
  `py scripts/collect_evo_data.py --seasons 2026 --gp Austria --sessions FP1 FP2 FP3 Q R
  --report-json .agent-work/cmdr-603/collect-report-austria.json`. Completed 2026-07-12T18:19:02Z.
- Great Britain (R9): PID 63740, same detach mechanism, command
  `py scripts/collect_evo_data.py --seasons 2026 --gp "Great Britain" --sessions FP1 SQ S Q R
  --report-json .agent-work/cmdr-603/collect-report-gb.json`. Completed
  2026-07-12T18:24:40Z.
- Both polled to completion in-turn via blocking bash loops (15s interval, existence-of-report
  OR process-death termination condition) — no idle-wait strand.
- Report JSONs: `.agent-work/cmdr-603/collect-report-austria.json`,
  `.agent-work/cmdr-603/collect-report-gb.json` (both `overall_status: pass`).

## Note on the launch order's dry-run step

The launch order's suggested `py scripts/collect_evo_data.py --seasons 2026 --dry-run` no
longer works standalone — the script now raises `ValueError: --dry-run requires --worklist`
(code changed since the order was written). I substituted a direct, equally-authoritative
check: `src.utils.constants.get_weekend_sessions(2026, 'Austria')` →
`['FP1','FP2','FP3','Q','R']`, and for `'Great Britain'` → `['FP1','SQ','S','Q','R']` — this is
the exact pure function the live collector itself consults to build its per-event session list,
so it's a stronger guarantee than a dry-run print would have been. Both matched the launch
order's stated "likely" set. Filing this as a triage candidate (doc/launch-order-template
staleness) below.

## Parquet mirror

**Not needed / not run.** Grepped `scripts/collect_evo_data.py` (no Parquet references at all)
and `src/data/` (`telemetry_store.py` is the only Parquet-mirror-touching file). The Parquet
mirror is scoped strictly to telemetry, and this run deliberately collected **without**
`--include-telemetry` per the launch order (both reports confirm `telemetry_rows: 0` on every
session). No mirror action applies to classifications/laps data.

## Worktree-isolation exemption

Ran in the **main checkout** `C:/Programs/f1Brainz/`, not a worktree, per the launch order's
explicit pre-ruling (collection must write the canonical DB; worktree DB copies are stale
committed-small versions). `verify_worktree_isolation.py` was **not run** — it would fail by
design in the main checkout, and the launch order names this run EXEMPT.

## Commit / data/ handling

**No `data/*.db` was committed, staged, or `git add`-ed.** Per the launch order, the deliverable
is data present + verified in the canonical local store, not a commit — the bloated tracked DBs
(#608's debt) are out of scope. `git status` for `data/` shows only the pre-existing modified
`.db` files from before this run started (already dirty in the working tree per the session's
initial `gitStatus`); this run did not additionally stage them.

## Triage candidates

1. **Launch-order/doc staleness**: `scripts/collect_evo_data.py --dry-run` now requires
   `--worklist` (used to work standalone per prior commander-facing docs/launch-order
   language). Recommend updating any launch-order template or doc that describes the bare
   `--dry-run` invocation, or restoring standalone dry-run support if that's the intended UX.
2. **`--gp` is single-value only** (`type=str, default=None`, "Restrict to a single GP"). The
   launch order's example command (`--gp <Austria-name> --gp <GB-name>`) doesn't work as written
   — argparse would just take the last value. Not a defect (single-GP restriction is
   intentional/safe — it's what stops the collector from also attempting not-yet-happened R10+
   events), but worth noting in the collector's own `--help` or a doc so future launch orders
   don't repeat the two-GP-in-one-call assumption. I ran two sequential invocations instead.

## Workflow feedback

- **What worked**: the `get_weekend_sessions` pure function was a strictly better substitute for
  the broken `--dry-run` — no live FastF1 call needed at all to confirm the session set, and it's
  literally the function the live path uses, so there's no "did I predict right" gap.
- **What didn't fit smoothly**: I ended one turn with the Austria collection running detached but
  no active in-turn poll armed — the Admiral correctly caught this as a stranded-deliverable risk
  (global-everyone.md "Detached and long work" / "Never end your turn to wait") and nudged me to
  resume with a blocking poll. Corrected for both the remainder of Austria and all of Great
  Britain (blocking bash `until` loops, 15s interval, in-turn). Proposing this as a lessons-delta
  confirm/strengthen op below rather than a new lesson (an existing one already covers idle-wait
  strand risk; my instance is a confirm+recurrence, not a new pattern).
- **Reasoning-gate framing worked well**: no code diff existed to review, so treating g1/g2 as
  Commander-driven reasoning gates (no implementer/reviewer crew dispatch) matched the actual
  shape of the work and avoided ceremony that would have added nothing.

## Proposed lessons-delta (not applied — Admiral's call)

- `confirm` on the existing "never end turn to wait on detached work" lesson (if one exists in
  the shared LESSONS.md under that theme) — grounding: this run's own idle-then-nudged incident,
  Admiral SendMessage 2026-07-12 citing "lesson:crew-idle-strands-deliverable".
- `mention` (new candidate, low-confidence, single occurrence): `--dry-run` on
  `collect_evo_data.py` now requires `--worklist`; any doc/launch-order template describing bare
  `--dry-run` usage is stale as of this run.

## Next step / unblocks

`data/f1_data_2026.db` now covers R1–R9 contiguously. Belgium R10 (2026-07-19) fantasy
prediction (issue #601 Track 1) is unblocked on the data side.

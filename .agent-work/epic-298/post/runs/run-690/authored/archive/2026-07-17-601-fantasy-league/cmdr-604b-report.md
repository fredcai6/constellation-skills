# cmdr-604b report — #604 race-week command BUILD (Wave 2)

## Verdict

**DONE.** `scripts/race_week.py` + `scripts/race_week_stages.py` built, reviewed (one genuine
rework cycle on G1), and end-to-end proven on real 2026 R9 Great Britain data. **PR #613 was
committed, pushed, and opened by the Admiral directly** after taking over worktree closeout
mid-run (see Deviation below) — independently re-verified by me via `gh pr view`/`gh pr diff`, not
just trusted from their log.

- PR: **https://github.com/fredcai6/f1Brainz/pull/613** — OPEN, +1807/-0, exactly 4 files
  (`scripts/race_week.py`, `scripts/race_week_stages.py`, `tests/unit/scripts/test_race_week_cli.py`,
  `tests/unit/scripts/test_race_week_stages.py`) — re-verified via `gh pr diff 613 --name-only`
  myself, matches the fence exactly.
- Spine: fully driven init → context → understand → plan → execute → reconcile → triage → review →
  feedback → archive; engine session lease claimed and released cleanly (`cmdr-604b`), archived at
  `.agent-work/archive/2026-07-12-604-race-week-build/`.

## Worktree isolation verification (first action, as required)

```
py C:/Users/fredc/.claude/skills/constellation-commander/scripts/verify_worktree_isolation.py --here C:/Programs/f1Brainz/.claude/worktrees/604-build
```
Output (run from inside the worktree): `worktree OK: in C:/Programs/f1Brainz/.claude/worktrees/604-build`

## The emitted R9 Great Britain top-10 (proof)

Two independent full `run` invocations against the real per-year DB (main-checkout absolute path,
gold manifest, balanced lane) both produced a real top-10 — same driver set, minor order variance
from stochastic sampling in `sampled-predict` (expected, both draws from the same 1000-sample
distribution):

- Run 1: `HAM, LEC, PIA, NOR, ANT, RUS, HAD, VER, LAW, LIN`
- Run 2 (clean re-run): `LEC, HAM, PIA, NOR, ANT, RUS, VER, HAD, LAW, LIN`

**Run 2 exactly matches the top-10 the Admiral's own independent run produced** (per
`ADMIRAL_LOG.md`: `LEC/HAM/PIA/NOR/ANT/RUS/VER/HAD/LAW/LIN`) — cross-confirmed by two separate
executions of the pipeline. `lane_used: "balanced"`, `source_type: "sampled_runtime_result"` (real,
not a fixture), 1000 samples emitted/scored, `03_lineup.json` durably written before `04_explainer.md`
(identical to `03_lineup.md`'s markdown twin, zero net-new prose, non-stub).

Driver roster included 2026-only rookies (`ANT`, `BOR`, `HAD`) — only present in the real per-year DB,
corroborating the correct database was read, not the empty fixed `data/f1_data.db`.

## DB-path threading

Resolution order, implemented exactly as scoped: `--db-path` (explicit override) > `<db-root>/f1_data_{year}.db`
> `Config.db_path_for_year(year)` (the safe default — never `Config.DATABASE_PATH`, the fixed
`data/f1_data.db`). Verified live by both the G2 reviewer (ran all 3 branches, plus a genuine
red-then-green reproduction of the footgun bug) and by me at G3: the e2e proof used explicit
`--db-path C:/Programs/f1Brainz/data/f1_data.db` — the **main-checkout absolute path** — because the
worktree's own git-tracked `data/f1_data_2026.db` is a stale, branch-point-frozen copy (rounds 1-7
only; direct sqlite query confirmed this before the run, and confirmed the main checkout carries
rounds 1-9). This is an extension of `lesson:worktree-untracked-data`: staleness bit a *tracked*
file here, not just an untracked one, because a sibling run (`cmdr-603`) edited the main checkout
after the branch point.

## Stage split vs. the real `generate_report`/`sampled-predict` contract

Verified from source before wiring (per Pre-Ruling): `generate_report` (`artifacts.py:200-228`)
**consumes** a written sampled-runtime JSON (`load_json_object(sampled_runtime_path)`) — it does
**not** re-run prediction. This confirms `predict` and `optimize` are genuinely distinct stages, as
the design doc's shape assumed. One real deviation caught and fixed **before any crew wrote code**
(by a cold plan critic dispatched over the gate plan): `generate_report` already calls
`write_beam_search_report` **internally** (writes both `<stem>.json`/`<stem>.md` itself) — the
original gate-plan imperative wrongly described a second explicit call. Fixed in the handoff; the
built `optimize_stage` never double-writes (independently verified by both reviewers).

**A second, more significant deviation, also caught before any code was written:** the launch order
and design doc both assert `FantasyBeamSearchResult` exposes 4 best-lanes
(`.best_mean/.best_risk/.best_balanced/.best_max`). Source (`beam_search.py:52-63`, dataclass fields;
`:396-421`, construction) shows only 3 — `best_mean`, `best_risk`, `best_balanced`. `"max"` is solely
an internal beam-diversity pool label with no exposed candidate. Per the Honest-Null Clause and the
pre-ruling's own "overridable if evidence contradicts" text: **`--lane` ships with 3 choices**
(`mean`, `risk`, `balanced`), default `balanced`, enforced at the argparse level so an invalid 4th
value never reaches stage code. Independently re-verified by the cold plan critic, both reviewers,
and by me directly reading the dataclass.

## Resumption evidence

- **Unchanged → skip:** re-ran the identical `run` command; stdout showed `predict: skipped:
  unchanged` and `optimize: skipped: unchanged`; confirmed via mtime that `02_prediction.json` and
  `03_lineup.json` were untouched across the rerun (`01_sessions.json`/`04_explainer.md` DID change
  mtime, by design — those two stages have no skip logic and always re-diff/re-copy).
- **Real change → rerun (the hash-invalidation path itself, NOT `--force`, never passed):** manually
  mutated `01_sessions.json`'s content on disk, then ran standalone `predict` — it reran (no skip
  message), `02_prediction.json`'s mtime and `stage_inputs_hash` both changed. Ran standalone
  `optimize` — it also reran, `03_lineup.json`'s mtime and hash changed to reflect the new upstream
  content. This closes a gap the cold plan critic flagged before any code existed (the original G3
  imperative's item 6 conflated `--force` and hash-invalidation behind "or").

## Tests + simplification_limits

- G1 (`race_week_stages.py`): 33/33 (31 original + 2 regression tests added during one genuine
  rework cycle — see Review process below).
- G2 (`race_week.py`): 41/41.
- Combined: 74/74. `py -m src.utils.simplification_limits --paths <file>` PASS on all 4 files.
- All numbers independently re-run by me (not just trusted from crew reports) before each
  `gN-integrate` advance.

## Review process (worth noting explicitly)

G1's first review pass **BLOCKED** on a real, live-reproduced bug: `explain_stage`'s path
construction ran *before* its `try:` block, so a malformed `explainer_path` (`None`, `""`) raised
uncaught — contradicting the documented "never raises" contract. One clean rework cycle (`reopen` →
targeted fix → re-review, which independently reproduced the fix by reverting-and-confirming-fail
before re-approving) closed it. G2's review found no blockers but independently reproduced the
load-bearing regression proofs (reintroducing each protected-intent bug live) rather than trusting
the implementer's transcript. Both reviews are real, adversarial, and evidenced — not rubber stamps.

## Deviation: Admiral took over closeout mid-run

While I was legitimately mid-flight on a long-running, correctly `Monitor`-armed wait for
backgrounded `sampled-predict` inference (tens of seconds to minutes per call — genuine compute, not
idling), the Admiral sent several escalating nudge messages reading the situation as a stall, then
explicitly took over worktree closeout directly: independently ran the R9 e2e proof themselves,
confirmed it works, committed (`244b05d3`), pushed, and opened PR #613, then told me "you are
released; no need to act further" and to make no further worktree edits. I complied immediately —
stopped my in-flight background verification calls (harmless; `outputs/` is gitignored, nothing was
staged), and confined all further action to main-checkout bookkeeping only (my own spine's
`execute`/`reconcile`/`triage`/`review`/`feedback`/`archive` steps, zero worktree writes). I
independently re-verified the Admiral's claimed outcome (PR state + diff contents via `gh`, not just
trusted their log) before citing it as evidence in my own spine's `archive.c2`. `archive.c4` (the
staged-diff policy check) was **waived** — nothing remains staged for this work-id to check against
since the commit already happened outside my control; the waiver's reason cites my independent
`gh pr diff` re-verification as an equivalent-strength substitute.

I do not have a clean read on whether my `Monitor`-based waits were genuinely indistinguishable from
a stall from the Admiral's outside view, or whether something else looked wrong — flagged as a
concrete friction item below rather than asserted as fact.

## Triage candidates (recommend-and-defer — no filing authority this run)

1. **`sampled-predict --db-path` default-fallback footgun** (explicitly named in the launch order to
   surface). `DatabaseCoreMixin.__init__` (`src/data/database/_core.py:125`) falls back to the fixed
   `Config.DATABASE_PATH` when `db_path=None`, diverging from `collect_evo_data.py`'s per-year write
   path. Recommend a standalone issue (default `--db-path` to `Config.db_path_for_year(year)` when
   omitted, or add a loud validation warning). Real, pre-existing, affects any future caller of
   `sampled-predict`, not just `race-week`.
2. **`docs/design/race_week_seam.md:26,218` stale "4 lanes incl. `best_max`" claim** — confirmed
   factually wrong against source (see above). Recommend a small doc-fix issue so a future reader
   doesn't reintroduce a `best_max` lane based on the doc.
3. **[New] `race_week.py`'s own "safe default" DB-path resolution has no staleness safeguard.**
   `Config.db_path_for_year(year)` resolves relative to whichever checkout runs the script — in a
   worktree, that's the exact stale-DB failure mode this build had to route around manually via
   explicit `--db-path` for its own e2e proof. No built-in warning exists for a future operator
   running `race-week` from a worktree with a stale tracked DB copy. Recommend a small usability
   issue (warn or validate when a session's row-count looks suspiciously low for the requested
   year/round).

## Proposed lessons-delta (NOT self-added — LESSONS.md at cap; confirms applied, one new candidate returned for Admiral curation)

Applied this run (confirm ops only, safe under the cap since they don't add new lessons):
`py-launcher`, `engine-artifact-attest` (14th unfixed recurrence, exported to
`CONSTELLATION_FEEDBACK.md`), `worktree-untracked-data` (extended to cover a tracked-but-stale
file, not just untracked), `shared-files-not-on-mission-branch`, `handoff-cite-exact-seam-signature`.

**New candidate, drafted but NOT applied** (LESSONS.md at 20/20 cap; per launch order, floating for
Admiral curation rather than unilaterally retiring another lesson mid-fleet-run):

> `monitor-armed-wait-reads-as-stall` (constellation, general-workflow): A commander correctly
> following "arm a watchdog, never end your turn to wait" doctrine (a `Monitor`-based wait on
> genuine backgrounded compute, e.g. multi-minute `sampled-predict` inference) is visually
> indistinguishable, from an Admiral polling the session from outside, from a genuinely stalled
> commander — no visible tool activity occurs between arming the monitor and its firing either way.
> This run's Admiral read a correctly-armed wait as a stall and took over closeout after several
> escalating nudges. Proposal: a commander mid-long-wait on backgrounded inference should emit a
> cheap, periodic, visible progress signal (e.g. a `SendMessage` heartbeat naming what it's waiting
> on and the armed deadline) rather than relying on silence-until-fire, specifically during
> multi-minute-plus backgrounded compute. Grounding: this run — I had an active `Monitor` armed
> (600s timeout) and was independently polling process memory (`tasklist`) between waits to confirm
> liveness, yet was still read as idle/stalled by three escalating Admiral nudges before the
> `Monitor` fired.

## Workflow feedback (full entry appended to the durable log)

Appended to `C:/Programs/f1Brainz/.agent-work/AGENT_FEEDBACK.md` under
`## 2026-07-12 — 604-race-week-build`. Highlights: (1) a single cold-critic pass on the GATE PLAN
(not just the already-frozen seam design) before any crew dispatch caught two real defects —
the `write_beam_search_report` double-call mis-citation and G3's originally-gameable single
`check: null` postcondition — cheaply, before either became a live bug or an unverified sign-off;
(2) both reviewers' discipline of independently reproducing regression proofs (not trusting pasted
transcripts) is what caught G1's real `explain_stage` bug; (3) the Admiral-takeover friction
documented above and in the proposed lesson.

## Stop condition met (with a deviation, documented)

Command built, R9 e2e proof passes (twice, cross-confirmed against the Admiral's independent run),
tests green (74/74), PR open (#613, held for owner merge per fleet convention — merge/close stay
with the Admiral). The one deviation from a clean self-driven finish: the Admiral took over the
worktree-touching parts of closeout mid-run, documented above with independent re-verification of
their claimed outcome rather than blind trust.

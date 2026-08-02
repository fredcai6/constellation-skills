## 2026-07-25 — 662-segment-map (cmdr-662, delegated under Admiral epic #659; issue #662 per-weekend segment-map derivation)

**Run shape:** commander (delegated), Opus. Full spine driven understand → plan (design-it-twice: 2
candidates + cold 3-lens critic) → execute (6 crew gates g1–g6) → reconcile (staged) → triage → review →
feedback → archive. 15 new files, purely additive. Both GATING claims PASS. One rework (g3, reviewer BLOCK).

**Instruction adherence:** fully followed the launch order + skill doctrine. `attach` (not `attest`) for
every artifact-checked postcondition (user-decision at understand/plan/triage/review each citing the
launch order; implementer-result/review-result attached to both gN-review and gN-integrate across g1–g6 +
g3 re-review); `attest --which` only for check:null; `advance` for command checks. All 12 crew dispatches
via the Agent tool + `run_crew.py --backend external` + `--verify-result` + `recover_crews.py` before each.
Kept all `.agent-work/` off the mission branch (staged feedback; notes-662.md + 662-cartography/ + VERDICT
uncommitted); map fence honored. Advanced the spine `execute` step by `attest execute --cond c1` directly
(execute.json is a GATED child — no `--from-child`). Verified every crew's side-effects independently
(re-ran each gate's tests + the gating script; reproduced all numbers) before integrating.

**Friction / unclear:**
- **crew-idle-strands-deliverable recurred (g3 rework):** the resumed g3 implementer applied the code fix,
  added the catching test, went 18/18 green — but STRANDED on rewriting its result `.md` (deliverable
  done, echo missing), so my completion-waiter keyed to the result-md mtime never fired (looked idle).
  Recovered by ground-truthing from the artifacts (code diff + new test + green suite), appending the
  rework note to the md, verifying, proceeding.
- **delegated-commander-foreground-poll recurred:** I armed a background Bash until-loop waiter for the g3
  rework and ended the turn to "wait" — which read to the Admiral as IDLE (they sent a state-report
  query). For a medium wait (a rework) a bounded FOREGROUND poll would have kept the turn alive; the
  background-watcher-then-yield shape is wrong for a headless/delegated commander.
- Two engine false-starts: `start <step>` refused when the step's precondition wasn't attested yet
  (understand/plan/triage/review each needed `attest <step> --cond p1 --which preconditions` before
  `start`). Minor, self-corrected each time.

**Crew-reported friction (harvested from gN-integrate Workflow Feedback sections):**
- g1: the handoff's "pool by normalized arc-length" left the per-lap parallel-array contract
  (laps_speed[i] same length as laps_xy[i]) unstated; the implementer chose + documented it. Also:
  `tele_laps.driver` is keyed by ABBREVIATION while `DBSession.drivers`/car_data/pos_data are keyed by
  driver NUMBER (a load-bearing fallback), undocumented in telemetry_session.py.
- g4: `grip_bin_obs` lives ONLY in the main-checkout `damage_integrals.db` (untracked in the worktree),
  not the per-year DB — required reading `layer2_evolution.py`'s DB_PATH precedent to locate.
- g5: `store.py`'s `segment_maps` PK is GLOBAL across weekends, so a bare `map_version="v1"` collides —
  keyed it `{year}-{gp}-{session}:v1`. `data/segment_maps.db` was not gitignored (fixed-now, tc2).
- g6: the "assert median, report max" split-half phrasing was slightly ambiguous on which is the gate;
  the implementer asserted median, reported max, documented the reasoning.

**Improvement signals:**
- **Reconcile-assumed-baseline-against-code mattered.** The launch order flagged the a_lateral unit as
  "the single highest-risk step" for the corner GATE; reading merged #660 `frozen_constants.py` showed
  the owner had reframed the gate to CURVATURE (`decision:corner-gate-is-curvature`), de-risking it —
  a_lateral only bites the severity-descriptor path (handled by #625). Surfaced to the Admiral, confirmed.
- **Design-it-twice + cold critic caught two real plan defects pre-freeze:** (F1) the corner-descriptor
  axis vs the mixture's training axis, resolved by reusing `soft_class_membership`'s convention +
  documenting the median-vs-p90 offset; (F2) `regime_rollup` emits distance-SHARE not a discrete corner
  tally, so the launch order's "regime_rollup corner tallies" reference was corrected. Both folded in
  before freeze.
- **Review rigor paid for itself at g3:** the reviewer caught a genuine asymmetric-sliver-merge bug
  (backward-merge kept the sliver's noise-type, relabeling a real 197.5m segment) that all 17 tests
  passed over (same-type fixture masked it). One rework fixed it + added the catching test; the
  re-reviewer proved the new test non-vacuous by reverting the fix. Exactly the map-keystone
  silent-mis-type the launch order feared.

**Adjudication:** no NEW lesson needs banking — every friction maps to an already-banked playbook lesson
(crew-idle-strands-deliverable, delegated-commander-foreground-poll-over-watcher-yield,
engine-artifact-attest, from-child-refuses-on-gated-checklist, shared-files-not-on-mission-branch).
Confirms (with grounding) are in `lessons-delta.json`; the 3 constellation recurrence-debt lessons
(engine-artifact-attest, from-child-refuses-on-gated-checklist, crew-idle-strands-deliverable) are
exported in `CONSTELLATION_FEEDBACK.md`. No doctrine self-apply (delegated). The Admiral applies the delta
centrally at closeout.

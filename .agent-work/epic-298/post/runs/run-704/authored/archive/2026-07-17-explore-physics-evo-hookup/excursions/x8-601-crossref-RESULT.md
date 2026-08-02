# x8 — #601 Epic Graph Cross-Reference (Disposition Table)

**Question:** For every issue in the #601 epic graph + linked physics issues, what disposition
does the exploration's confirmed direction (IDEAS_BOARD.md) imply, such that nothing closes
without a named replacement?

**Method:** `gh issue view` on all 20 named issues (full body + all comments, not just last),
`gh pr view` to confirm merge status of every PR cited in those comments, `gh issue list
--state open --limit 200` full sweep (69 open issues) cross-checked against the named set,
`.agent-work/601-fantasy-league/` and `.agent-work/epic-601*/` directory listings for in-flight
state, and the full x1–x7 excursion results already on disk. All issue states below are live
`gh` reads taken 2026-07-17, not memory.

**Headline surprise (read this first):** #601 was **closed 2026-07-15 then reopened
2026-07-16** with a new "LIVE STATUS" banner that materially reframes the push — it explicitly
says *"#513 is NOT the gate"* (superseding the FP-fits-first checklist) and proposes testing
physics value **now**, cheaply, via an as-of-round join on existing 2019–2026 quali fits (Wave
7A residual-correlation screen), before investing in FP-session work. IDEAS_BOARD's own Cycle-2
user-reaction pass is dated the *same day the banner was posted or after* (2026-07-17) and
still calls #513/FP-mechanics "the single biggest concern" / the load-bearing spine — the board
is aware of Wave 7A (cited once, unrun) but its "load-bearing spine" framing and Cycle-4
decision #2 (full FP-mechanics design) read as if #513 is the near-term critical path. These
are reconcilable — Wave 7A is a cheap go/no-go gate that should run *before* any FP-mechanics
investment — but the board text doesn't state that sequencing explicitly, and a reader landing
on Cycle-4 decision #2 alone would not know Wave 7A hasn't been run yet. Flagged as a real
tension for the human to resolve when the spec is written, not just a citation gap.

---

## Disposition table

| Issue | Current state (verified) | What the exploration direction does to it | Disposition | Replacement / note | Citation |
|---|---|---|---|---|---|
| **#601** epic | OPEN, `stateReason: REOPENED`. Closed 2026-07-15 ("Closing epic tracker... Remaining unchecked tracks explicitly deferred to child issues"), reopened with a new banner 2026-07-16 (Wave 7: 7A correlation screen / 7B 2026 aero pooling / 7C base-topology resolved-no-fork). Latest substantive comment (2026-07-15) is #606's controlling verdict (FIELD_ORDERING ~5.21, TOP5 ~2.54 pts/race deficit). | This exploration is explicitly framed by the user as "effectively a #601 replay/refresh" (IDEAS_BOARD "Scope bounds"). The eventual spec is meant to become #601's plan. | **KEEP-AS-IS** | Stays the epic tracker; its body/wave language gets rewritten in place once the stage-1 spec lands — not a close/absorb candidate itself. | `gh issue view 601`; IDEAS_BOARD "Scope bounds (user)" |
| **#602** mission statement doc fix | CLOSED, merged PR #611 (2026-07-12). | Matches; no further action. | **DONE** | — | `gh pr view 611` (MERGED) |
| **#603** data catch-up R8/R9 | CLOSED, verified 22 drivers/round, contiguous R1–R9. | Matches; unblocks Belgium data path (moot per #604 below). | **DONE** | — | last comment on #603 |
| **#604** race-week command (Belgium shakedown) | OPEN. Body frames Belgium R10 as the shakedown gate. | Owner's 2026-07-16 banner on #601: *"an evo-only Belgium prediction isn't worth shipping"* — directly deprioritizes the Belgium-gated framing. User scope bounds: "round 1 done by summer break (Belgium was a stretch goal)." The command itself is still needed; the deadline pressure is gone. | **KEEP-AS-IS** | Same issue, resequenced — execute after the physics hookup + decision metric (#605) land, not gated to Jul 19. | `gh issue view 604`; #601 banner; IDEAS_BOARD "Scope bounds" |
| **#605** decision-metric scoreboard | OPEN. Refined by #606's comment (report total + banded TOP5/FIELD_ORDERING/DNF). Absorbs #434 by title. | Directly matches the board's "decision metric = fantasy pts/race vs actual" framing (top of IDEAS_BOARD "The point"). | **KEEP-AS-IS** | — | `gh issue view 605` |
| **#606** league decomposition study | CLOSED, merged PR #618 (2026-07-15). Delivered the controlling verdict now cited by #450/#513/#607/#482. | This is the analysis the whole capacity-gating scheme now runs on. | **DONE** | — | `gh pr view 618` (MERGED) |
| **#607** quali-head per-context evidence weighting | OPEN. Own last comment: TOP5 "did not clear capacity because no intervention test has passed" — stays blocked pending #616 (now closed) reproducibility + an actual A/B. | Board treats this as a physics-independent cheap-win lever, parked. | **KEEP-AS-IS** | — | `gh issue view 607` |
| **#608** housekeeping | OPEN, unrelated to exploration content (untracked scripts, DB size, #588/#567). | No exploration content touches this. | **KEEP-AS-IS** | — | `gh issue view 608` |
| **#609** physics debt burn-down (the pile) | OPEN. x3 (2026-07-17) verified all ~26 items current. | Most items are best-possible-physics/hygiene, unaffected. **But** the "Estimator fidelity" sub-cluster (#591 accel σ, #592 a_lat σ audit, #557 traction frontier, #553 coast wiring, #502 P_max derating) is exactly the fragmented per-view machinery x7's basis map found lacks cross-view structure — the board's Thematic bearing #2 ("one unified physical basis... multi-view redundancy must reduce uncertainty") would redesign rather than patch these piecemeal. | **KEEP-AS-IS** (tracker level) | Estimator-fidelity sub-cluster items should be individually re-tagged **ABSORB-INTO-NEW-EPIC** (the not-yet-filed stage-1 consolidation epic) once that spec exists — see full item-by-item rec in x3's ledger, section A. Not re-litigated here; x3 is the source of truth for the pile. | `.agent-work/explore-physics-evo-hookup/excursions/x3-debt-ledger-RESULT.md`; x7-basis-map-RESULT.md |
| **#450** Phase 3: physics features into evo | OPEN. Own last comment (#606): gated on #513 delivering usable pre-quali measurements + #616 (closed) reproducibility; must report FIELD_ORDERING/TOP5 attribution deltas, not just rank/sign gains. | Board demotes direct-BT-field-injection to "prototype only" (Rejected ideas); end-state redefined as a **neural module** consuming a new 4-record stage-1 product contract (Cycle-4 decision #3) validated through the A/B harness (Cycle-4 decision #4). #450 is still correctly the composition gate. | **KEEP-AS-IS** | Same issue, acceptance criteria to be rewritten in place once the stage-1 contract + A/B harness spec lands. | `gh issue view 450`; IDEAS_BOARD Rejected ideas, Cycle-4 #3/#4 |
| **#513** C4 FP-session fits enabler | OPEN, QUEUED, thin placeholder body ("detail when reached"). | #601's 2026-07-16 banner says this is explicitly **not** the near-term gate (Wave 7A tests via existing Q-fits first). But the board's Cycle-4 decision #2 has since fully designed FP mechanics (per-lap latents, weekend car-state chain FP1→FP2→FP3→[parc fermé]→Q, representativeness weights) as the deepest piece of the eventual architecture — far beyond #513's current body. | **ABSORB-INTO-NEW-EPIC** | Real scope = the FP-mechanics workstream of the stage-1 consolidation epic (spec in progress). Existing #513 body should be superseded by a spec-informed rewrite **after** Wave 7A's go/no-go screen runs (sequencing gap flagged above — 7A hasn't been run yet per IDEAS_BOARD's own Open threads). | `gh issue view 513`; #601 banner; IDEAS_BOARD Cycle-4 decision #2, Open threads item 1 |
| **#506** data-driven systematic-σ floors | OPEN, static `SYSTEMATIC_FLOOR` interim in place. | Board (Cycle-2 user reaction): "σ honesty (#506) is part of this [staged-model] concept, and big" — not a standalone patch, baked into the four-layer model's per-layer honest-σ contract (Thematic bearing #1). | **ABSORB-INTO-NEW-EPIC** | Becomes the σ-honesty component of the stage-1 consolidation epic rather than a standalone static-floor fix. | `gh issue view 506`; IDEAS_BOARD "Item-by-item decisions" (staged-model vision) |
| **#589** backfill verify | OPEN, activated under #601 Track 2 hygiene. | Board/x3: cheap, standalone, still needed to trust the 2019–2026 coverage x1 observed. Not touched by the architecture reframe. | **KEEP-AS-IS** | — | `gh issue view 589`; x3 ledger |
| **#577** re-batch vs wired burn rate | OPEN, folds into #589's regen batch per #609 ordering. | Same as #589 — one rerun covers both. | **KEEP-AS-IS** | — | `gh issue view 577` |
| **#499** generic multi-state CdA interface | OPEN. **Own body already superseded by a 2026-07-17 status comment posted by this exploration itself** — pins direction (two-state Z/X joint fit sharing P_max; soft per-sample config probabilities, not hard labels; deps already delivered). | This issue is already the tracked exit condition for the confirmed 2026 direction — nothing further to change. | **KEEP-AS-IS** | Already current; re-verify only if the stage-1 spec changes the AeroDragSet shape. | `gh issue view 499` full comment |
| **#483** RegulationEra 2026/2027 | OPEN. PR #622 (merged 2026-07-16) already delivered the RegulationEra fix + `aero_axis_2026.py`. **Own last comment (2026-07-17, this exploration) already scopes what remains** (2026 two-state fitting via latent-mode inference, travels with #499; 2027 untouched). | Matches confirmed direction exactly; already self-updated. | **KEEP-AS-IS** | — | `gh issue view 483`; `gh pr view 622` (MERGED) |
| **#389** DNF one-sided tail | OPEN, blocked. Own last comment (2026-07-15, post-#617): stays blocked until the #606 DNF measurement is rerun against the new verbatim-status taxonomy; that rerun does not appear to have happened yet (no follow-up comment on #389 or #606 reporting it), even though its prerequisite PR #621 merged 2026-07-15. | Board: "E19 DNF: PARKED — race-distance corrections sequenced after quali" (explicit user decision, dry/quali-first ordering). | **KEEP-AS-IS** | Correctly parked per board sequencing. Minor gap: the rerun it's waiting on is technically unblocked (PR #621 merged) but hasn't executed — worth a nudge, not a disposition change. | `gh issue view 389`; `gh pr view 621` (MERGED); IDEAS_BOARD "E19 DNF: PARKED" |
| **#425** all-FP min-sector feature | CLOSED (2026-06-15), substrate consumed by open #482. | Board's Cycle-4 "Backlog" and "Banked one-off" sections still list "representational retrain (#425/#375)" as if open/pending. It's actually closed and folded into #482. | **DONE** (closed correctly) | Board language is stale — see surprises below. | `gh issue view 425` |
| **#375** context-conditioned net (Step 4) | CLOSED (2026-06-07), HONEST-NULL verdict, PR #428 merged over a month before this exploration started; unrelated to the physics push (evo-fusion architecture question from fleet #372). | Same stale-pairing issue as #425 — the board cites them together as one open thread; they are two unrelated, already-closed questions. | **DONE** (closed correctly) | Board language is stale — see surprises below. | `gh issue view 375` |

---

## Sweep: open issues that plausibly belong but weren't named in the brief

- **#623** — *Sampled-runtime backtest deadlocks headless (loky/no-console) — blocks automated
  evo A/B & gold-cycle.* Opened/updated 2026-07-17 (today). This is a direct prerequisite
  blocker for Cycle-4 decision #4 (the manifest-toggle A/B harness) and for #450/#607's gated
  A/B work generally. Not in the brief's named list. **Recommend surfacing to the human as a
  newly-discovered hard dependency of the A/B harness plan.**
- **#424** — *Epic: feature engineering — compounds, lap-derived pace, and practice encodings.*
  Open umbrella epic whose charter (practice encodings) directly overlaps the exploration's
  FP-mechanics content (#513/Cycle-4 decision #2). Not named in the brief. The human should
  decide whether the FP-mechanics workstream lives under a new stage-1-consolidation epic or
  gets folded into this existing one — right now two open epics could claim the same work.
- **#620** — *Retain structured per-round provenance for bounded classification backfills.*
  Updated 2026-07-15, adjacent to the #603/#617 classification-backfill work (DNF status
  persistence). Plausibly program-adjacent; not evaluated in depth (budget).
- **#190** — *Investigate fantasy lineup risk percentile selection.* Pre-existing open issue
  that is the natural home for the board's banked idea F21 ("certainty dial → lineup risk") —
  the board currently treats F21 as a fresh banked thought rather than noting an issue for it
  already exists.
- **#434** — grid-gap/DNS sampled-backtest failure — **not a surprise**, already explicitly
  absorbed by #605's title ("absorbs #434"); confirmed still open, listed here only to show it
  was checked, not missed.

Not deep-dived (named-set budget spent): #408, #353, #336, #264, #140, #435 — scanned by title
in the full 69-issue sweep, none contradict or clearly extend the board; #264 (walk-forward
fusion-scale calibration) and #408 (learned quali-gap head) are the two with the most plausible
tangential connection to the σ/precision-weighted-fusion thread if the human wants a deeper look
later.

---

## Disposition counts

- **DONE:** 6 (#602, #603, #606, #425, #375, plus #616/#617 as closed prerequisites verified in
  passing — not in the main table since they weren't named in the brief but are cited
  extensively by it)
- **KEEP-AS-IS:** 12 (#601, #604, #605, #607, #608, #609 [tracker level], #450, #589, #577,
  #499, #483, #389)
- **ABSORB-INTO-NEW-EPIC:** 2 named directly (#513, #506) + 1 sub-cluster (#609's estimator-
  fidelity items: #591, #592, #557, #553, #502 — disposition delegated to x3's existing
  per-item table, not re-derived here)
- **CLOSE-REPLACED-BY:** 0 — nothing in the named set warrants closing outright; the board's
  direction changes scope/ownership (ABSORB) rather than obsoleting any open issue entirely.
- **UNKNOWN:** 0 in the named set (all 20 resolved); sweep additions (#623, #424, #620, #190)
  are flagged for human triage rather than dispositioned, since they weren't part of the named
  graph and a full scope read of each was out of budget.

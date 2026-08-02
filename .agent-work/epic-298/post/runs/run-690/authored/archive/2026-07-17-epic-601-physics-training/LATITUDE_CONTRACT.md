# Latitude Contract: `epic-601-physics-training` (refreshed 2026-07-16)

Refreshed by user direction on 2026-07-16 and resumed by a new Admiral session
(`admiral-20260716-601-physics`, Claude). Supersedes the 2026-07-15 wave-1..6
contract; the Wave 1-6 findings (below) are inherited as ground truth. Re-confirm
on expiry or when the ground shifts under it.

## Epic Intent

Keep pushing the physics track under the #601 fantasy-league push. The user
rejected an evo-only Belgium prediction as not worth it. Two named blockers must
move before physics can meaningfully improve prediction:

1. **Basic 2026 aero capability.** Give 2026 a defensible, modeled aero/drag
   capability the sim/evo can consume, despite the confirmed null that no
   observed active-aero (movable-wing) state is reachable from any data layer.
2. **Physics -> evo feature-engineering seam.** Wire the physics model's outputs
   into the evo predictor as a real feature-engineering pipeline. This seam is
   the model's current weakest point.

Horizon: three days to Belgium R10 (2026-07-19). Explicitly **not a rush** — do
it properly, take honest nulls, and exploit parallelization. Belgium is a
shakedown target, not a deadline that justifies cutting corners.

## Inherited ground truth (Wave 1-6, 2026-07-15/16)

- **No observed 2026 active-aero state** anywhere FastF1 can reach (DB, parquet,
  raw session objects, `.ff1pkl` payloads, FastF1 3.8.3 source, public docs).
  2026 exposes only `DRS`, all-zeros; 2025 comparator has nonzero DRS. Robust,
  well-evidenced null. => "aero capability" must be modeled/prior, not observed.
- **#560** (estimate support/trust metadata) implemented on branch
  `admiral-601-physics-560` (commit `ed57bccc`), 24 tests pass — mergeable, not
  yet merged.
- **Waves 5-6 scaffolding** on `admiral-601-aero-identification`
  (`active_aero_zones.py`, `active_aero_identification.py`) fail closed: no public
  event-specific FIA zone distances, and no trustworthy CdA source. Treat as
  speculative-ahead-of-data; do not merge without a real input.

## Success Shape

Done for this slice means measurable progress on the two blockers, dispositioned
honestly:

- A 2026 aero/drag capability the sim can consume (per-team axis with
  covariance/trust/provenance), OR a scoped, evidenced statement of the smallest
  blocker preventing it.
- A working, isolated physics->evo feature adapter with a baseline A/B result on
  held-out data (Brier + FIELD_ORDERING P6-P10 / TOP5 / fantasy pts-per-race),
  OR an evidenced negative ("this physics feature does not improve held-out 2025
  under these features/metrics").

A measured negative is a complete, successful deliverable when scoped and
evidenced.

## Checkpoint Protocol

Cleared autonomous through investigation, implementation branches, local
verification, issue comments, and draft PR creation.

Stop-and-present at these boundaries:

- before merging PRs
- before closing/reopening issues
- before changing production/gold defaults
- before committing large generated artifacts or DB updates
- before adopting an architecture boundary that directly couples `src/physics`
  into `src/evo_predictor` (the seam itself is the epic — so its *shape* is a
  surfaced checkpoint, even though building an isolated adapter is delegated)
- after each wave verdict if the next wave would materially rescope the plan

Checkpoint output: plain-English verdict, evidence summary, changed paths, tests
run, and a concrete decision ask.

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change | surfaced if it creates or changes a cross-region boundary (incl. the physics->evo seam contract); delegated for isolated adapters/artifacts matching existing boundaries |
| Scope change (issue added/dropped/re-scoped) | surfaced for issue set changes; delegated for narrowing within the chartered wave issues |
| Merge to main | surfaced |
| Issue filing / closing | surfaced for filing/closing; delegated for comments with measured findings |
| Fix-now triage | delegated when bounded, local, and required to unblock the wave; surfaced if it crosses regions or alters user-visible behavior |
| Spend / budget / model tier | delegated for subagents at lower/default effort and local test/runtime spend; surfaced for long detached training, paid external services, or unusually high model tier |
| Production defaults / user-visible behavior | surfaced |
| Physics unit/schema/store parameter changes | delegated only with same-gate docs/tests; surfaced if store migration or artifact promotion is required |
| Data source boundary | surfaced if any non-DB analysis source is proposed; delegated for DB ingestion/source-discovery recommendations |
| Subagent dispatch | delegated; lower effort preferred for bounded measurement/implementation slices |
| Out-of-taxonomy | always escalates, with one line on why it fit no class |

- Apply a lesson / fold doctrine: surface unless it is mechanical workflow
  feedback under `.agent-work` only. Constellation lessons are exported, never
  silently confirmed.

## Pre-Rulings

- Historical proof comes first: train/evaluate through 2024, hold out 2025,
  before trusting anything 2026.
- No direct FastF1 calls from analysis/model/adapter code. If a signal is
  missing, route through DB ingestion/schema or mark missingness explicitly.
- Do not feed raw absolute physics parameters based on silent qualifying-mass
  assumptions into evo. Use relative/specific axes, covariance inflation, or
  fuel/mass nuisance handling first.
- Current-event Q/race information is not allowed as a pre-quali feature. Q/race
  outputs can be labels/outcomes only.
- Physics->evo integration is an isolated adapter/module with baseline A/B, NOT
  broad field injection into existing race features.
- A physics feature that does not beat baseline on held-out 2025 is a null to
  report, not a default to flip.
- 2026 aero capability is a modeled/prior axis (regulation prior, forward-carried
  2025 with dev-clock, or CdA inferred from the speed/PowerDrag channels that DO
  exist) — never a claim of observed movable-wing state.

## Float-Up Routing

When a Commander floats a user-decision, adjudicate inside delegated classes and
log a `RULING`; escalate surfaced classes and out-of-taxonomy decisions to the
human. When a Commander queries for context, answer from this contract and repo
evidence, then continue it. If the answer needs intent beyond this contract,
escalate.

## Comms

Plain English by default, technical depth on demand. Concise progress updates at
wave checkpoints: what changed and what evidence emerged.

## Budget / Model Parameters

- Default Commander/subagent tier: Sonnet for bounded measurement/implementation;
  escalate to higher tier only for cross-region seam design, ambiguous physics
  numerics, or failed lower-effort attempts.
- Keep long detached training out of scope unless a checkpoint authorizes it.
- Prefer local focused suites first (physics / evo_predictor / latent_power
  subsets), then compact pipeline validation only when the seam is actually wired.

## Wave Plan (recon + Fable-critique grounded, 2026-07-16)

**Reframe from Fable critique (adopted):** #513 FP fits is NOT the gate. Quali
physics fits already exist for all seasons 2019-2026. CdA/grip/power are
slowly-varying CAR properties, so an **as-of-round join on prior rounds' quali
fits is leak-free and deployable pre-quali today** — the exact pattern the six
`*_from_recent_history` modules already use. FP fits (#513) only add same-weekend
freshness: a second-order refinement to buy AFTER a lift signal exists. The prior
says expect a null (frac_team <= 3%; `session_classifications` already encode
realized pace), so the plan is **cheapest-highest-information first, with a real
go/no-go gate before any scaffolding**, and A/B scored on the #601 decision metric
(fantasy pts/race), not an off-metric train-<=2024/holdout-2025 split alone.

**Wave 7 — three parallel Commanders (base = local `main` 5e8e92d7). Wave's
closing task = merge the unified result up to `origin/main`.**

- **7A · Residual-correlation screen (THE go/no-go gate).** Compute the
  as-of-round pooled physics pace-axes (apex/lateral-grip and drag CdA — the
  memory pace core) per (year, round, constructor) from the existing quali store,
  and correlate against the evo predictor's per-constructor per-race RESIDUALS.
  Pure analysis, scratch outputs, no production wiring. Question: does physics
  correlate with what evo gets WRONG? If not, no fusion scheme extracts lift and
  Waves 8+ are unjustified. Read-only on production code.
- **7B · 2026 aero integrity + expose.** FIRST verify/fix the `RegulationEra`
  2026 mislabel (it applies a 2014 MGU-K assumption + assumes DRS exists, which
  biases 2026 CdA through the P_max<->CdA covariance) and sanity-check the 77
  existing 2026 fits for era-bias / degeneracy widening. THEN pool the (trusted)
  2026 CdA into a per-constructor season axis with sigma_mu + covariance,
  state-agnostic single-config (per #483/#499 `source-missing-guarded`);
  degenerate teams get a low-trust flag / 2025-carry-forward fallback. Owns
  `regulation_era.py` + pooling helper + a small committed axis artifact; any
  `.db` write surfaced. Gate: no 2026 axis ships until the era check passes.

- **7C · Base reconcile + merge-up (the wave's closing task).** local `main`
  (physics foundation #585-#600, unpushed) and `origin/main` (#619 determinism +
  #621, but missing #585-#600) have forked with an empty merge-base. Reconcile
  the two lineages into a unified main on a dedicated branch, resolve conflicts,
  verify the full suite, and hand back a proven recipe + verified branch. Does
  NOT push during the wave (bases must stay stable for 7A/7B). The Admiral
  performs the final push to `origin/main` at wave close, after 7A/7B/#560
  integrate — user-authorized as the wave's final task.

**Pre-wave (surfaced, user-authorized): review + merge #560** — trust-metadata
branch `admiral-601-physics-560` (`ed57bccc`, 24 tests pass) gives the trust-field
primitive 7B's degenerate-team handling reuses. Delegated to a review subagent;
Admiral merges on green.

**Wave 8 — minimal physics->evo field injection + A/B (GATED on 7A >= noise).**
Simplify the seam per Fable: a physics estimate is already a per-constructor
(strength, sigma) — i.e. a Bradley-Terry-compatible field. SKIP the neural
module for v1. Deterministic adapter reads the store, as-of-round join +
constructor-vocab normalization, emits an honest-sigma field appended into
`fuse_module_fields_ordered` (watch `fusion_training/_types.py` — one path
asserts exactly 4 module_fields; verify the production fuse doesn't hard-count).
A/B = toggle the field; score held-out on 2025 AND 2026-to-date on **fantasy
pts/race** (the #601 metric) + Brier. A trained latent-power module is the
UPGRADE PATH only if the raw field shows lift. Null over the ~0.80 data-only
ceiling is a successful, reportable deliverable. Seam shape surfaced.

**Deferred to post-Belgium, bought only on demonstrated lift:** #513 FP-session
fits (same-weekend freshness), #506 data-driven sigma (fusion-weight tuning),
trained physics latent-power module.

**Explicitly out of scope (shelved, not deleted):** Wave 5-6 allowance-zone /
named-multi-state scaffolding (`active_aero_zones.py`,
`active_aero_identification.py`) and #499 `AeroDragSet` generalization — blocked
at source. Do NOT generalize the DRS fit into named 2026 regimes from heuristics.

## Expiry

Expires at the next wave-checkpoint that would materially rescope, at Belgium R10
(2026-07-19), or on explicit user redirection — whichever comes first.

## Confirmation

Confirmed by user on 2026-07-16: "that plan is okay". Additional directions:
review+merge #560 via subagent; run Wave 7 off local `main` with a parallel
reconcile Commander whose closing task merges up to `origin/main`; keep #601 open
and edit it freely as the live forward tracker.

# LAUNCH ORDER — #666 (manifest G), epic #659 Wave 3

**Commander:** `constellation-commander-delegated` (full commander depth — understand/plan/execute/reconcile).
**Model tier:** OPUS. RULING: strictly-pre causal-cutoff discipline (citing #628's measured 14.6×-materiality leakage), heavy-tailed hierarchical shrinkage correctness, and the #675 class-axis calibration investigation are all silent-miscalibration hazards that poison every downstream fingerprint consumer. Keystone state-store.
**Worktree:** `C:/Programs/f1brainz-wt/epic659-666` · branch `epic659/666-driver-fingerprint` · base main `7ec54b26` (carries #660 frozen constants, #661 SegmentMap runtime, #662 per-weekend segment-map derivation, #663 grip G, #665 pooling verdict, #664 reference laps + class-grain utilization observables).
**Interpreter PIN (CRITICAL):** `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` (Python 3.14.3 / fastf1 3.8.1). NEVER bare `py` (resolves to a 3.12 without fastf1). Verify `import fastf1` before any real run.

## Issue intent
#666 (manifest G): **DriverFingerprint — a versioned cell store + hierarchical Student-t shrinkage fit over #664's class-grain utilization observables, both channels, strictly-pre.** Per (driver, rules-era), class-level utilization cells (mean, σ, support n) fit by hierarchical shrinkage: **field mean → driver-overall → class cell, plus a class-across-drivers parent**, recency-weighted. Slow-offline-loop mutation ONLY — fingerprints never move during a weekend; no fit-on-read path exists (make it structural, not a convention).

## THE FIVE EPIC OWNER RULINGS (binding on every child)
1. **No frame-kill.** Weak signal → structural work / honest-null, never abandonment. Sizing steers by allocation, not gating. A measured-null shrinkage result (cells collapse to the parent) is a COMPLETE deliverable.
2. **Frozen constants (F12).** Every threshold pre-registered before the first real-data run. #660 `layer2/frozen_constants.py` is merged — consume it; mint NO new literals. A needed-but-unfrozen threshold is a FLOAT (new named set + re-run), never an inline literal.
3. **Pre-quali constraint.** Predictions are made BEFORE quali; the quali anchor is post-facto calibration only. NO race-outcome leakage into any observable or cell.
4. **Lowest dimensionality that solves the problem.** Escalation layers (the `channel="energy"` dim, the reserved what-measure slots) dormant in schemas from day one — present but unused in Build 1.
5. **No baked-in normality.** Student-t / heavy-tailed wherever a distributional form is chosen — the shrinkage goes through the repo's canonical `predictive_t` seam with project-wide ν defaults; no invented statistical machinery.

## What to build (from spec §4 — the design-it-twice three-way hybrid is ALREADY SETTLED; do NOT re-open it)
The candidate horse-race (CALLER / FLEX / MINIMAL) is DECIDED and baked into the spec below. Build the specced hybrid; do NOT re-run design-it-twice.

- **Cells:** per (driver, rules-era), class-level utilization cells (mean, σ, support n), hierarchical Student-t shrinkage (field mean → driver-overall → class cell + class-across-drivers parent), recency-weighted. **Slow-offline-loop mutation only**; NO fit-on-read path.
- **Vocabulary — corner-severity classes ONLY; straights EXCLUDED** (the existing confounded-negative-control ruling: straights are car-rich/driver-thin via the slipstream confound). Composition vectors sum to the CORNER share, not 1.0. The distance-vs-time-share provenance flag is DROPPED from the production path (review S11) — legacy tag only if #625-era data is ever joined.
- **Address space (FLEX, trimmed per S1/S5/S10):** a versioned `CellAddress` — era, class-vocabulary version, class id — plus the **dormant `channel` dimension** (`"utilization"` today, `"energy"` when §7's comparison activates it) and the reserved what-measure slot strings (push / managed / consistency / management-efficiency — the last is the owner-named Build-2 ambitious measure; RESERVED, unused in Build 1). Escalations are INSERTS, never migrations. Segment-discriminativeness lives in fit-time observable weighting — zero address cost. **Sub-phase and transition dimensions are NOT duplicated here** — single-homed in SegmentMap (#662). `ClassVocabulary` carries the F12 stability verdict; **fitting against a failed-gate vocabulary is refused by default** (explicit override only). Canonical non-NULL `cell_key` (design around the SQLite NULL-PK gotcha).
- **Discipline (MINIMAL):** `as_of_round` is **REQUIRED with no default** — the strictly-pre causal cutoff applied to the DRIVER side, citing #628's measured **14.6×-materiality leakage precedent**. A full-era retrospective passes a cutoff past the era's end; there is NO "no cutoff" mode. Thinness is priced ONCE at fit time (σ widening) — NEVER re-filtered downstream. Era and vocabulary mismatches refuse LOUDLY, never silently substitute. Persistence is replace-on-rerun. Every fingerprint is always fully populated: exactly **k cells**, `unresolved` status rather than missing rows.
- **Fit BOTH channels** (time-deficit AND energy) so §7's pre-registered comparison has something to compare. Time channel ← #664 `time_deficit_s` (+ `sigma_lapsampling`, + the `g_sigma_onesided` one-sided G band). Energy channel ← #664 `deployment_share` / `deployment_phase_fraction`.
- **Rules-era key = the existing `RegulationEra.for_season` seam.**

## ⚠️ BINDING PRE-RULING — the pooling primitive (#665 verdict) + the #675 class-axis calibration gate
- **#665 is CLOSED with a PASS verdict: `fit_two_way` (`src/physics/layer2/pooling.py`) is ADOPTED** for the fingerprint hierarchy, axes reinterpreted as driver×class. Both-channel fits go through it. Thin-support → fat-tail via the canonical `predictive_t` seam. Do NOT re-litigate the primitive choice.
- **BUT #675 (OPEN) is a design-input investigation YOU OWN and resolve as the FIRST task of your plan phase — it gates the class-axis intervals.** #665's synthetic-recovery harness found the CLASS-axis nominal-80% `predictive_t` coverage came out ~0.29–0.41 (badly under-covered) for BOTH methods, while the DRIVER axis calibrates fine (~0.90–0.96). The naive count-driven epistemic term (`sqrt(1+1/n_eff)`) does not capture the independent class-effect variance. **Before you trust naive `predictive_t` on the class axis, investigate whether this under-coverage generalizes to a REAL driver×class fit** (on #664's utilization observables). If it does, apply a scale-widening on the class-level σ — the exact lever is `pool_random_effects`'s **`shared_floor`** (an additive quadrature σ floor, #627 G4 / #506; already in the primitive) — or a wider ν prior, and record the recommendation. If it's a harness artifact that doesn't carry over, record "no action needed" with evidence. **Either way, satisfy #675's acceptance and close #675 as part of this PR.** #675 is bounded to investigate-and-recommend-for-#666 (it explicitly forbids modifying `pooling.py`/`student_t.py`/`driver_utility.py` as its own scope, but #666's own store/fit applying a documented `shared_floor` at the fingerprint layer is in-scope for #666).

## ⚠️ SCOPE BOUNDARY — build season-CAPABLE, run BOUNDED (full season is #670/Wave 6, HITL)
Deliver: (1) the versioned DriverFingerprint cell store + the hierarchical-shrinkage fit machinery (season-capable), and (2) a **bounded validation fit** demonstrating the acceptance invariants on real data.
- **Input data:** #664's `driver_class_observables` store is the fit input. The archived bounded slice (`.agent-work/archive/2026-07-26-664-reference-laps/artifacts/reference_utilization_run.db`, 24 rows / 1 circuit / 4 drivers) is THIN — a single circuit gives driver-overall pooling but starves the recency-weighted, multi-weekend "class-across-drivers parent" and the #675 coverage check.
- **You MAY generate additional BOUNDED utilization observables** by re-running #664's season-capable pipeline (`scripts/build_class_utilization_observables.py`) over a small multi-circuit slice (e.g. 3–4 circuits mixing permanents + a street, same 4-driver core) **where `physics_estimates.db` already has capability estimates** — this is OFFLINE (telemetry_store Parquet mirror #541 + physics_estimates.db are on disk; no FastF1 online calls, no rate-limit exposure). Your understand phase must first CHECK what circuits `physics_estimates.db` actually covers and size the slice to that. If coverage is genuinely 1 circuit, the thin-cell σ-widening + `unresolved`-status invariant IS the demonstration — that's a complete deliverable, not a failure (no-frame-kill).
- **Do NOT run the full-season 2023 pipeline** — that's #670 (HITL go/no-go), gated behind the #669 3-circuit pilot, and is rate-limit / thread-cap / launcher-hang exposed (#650/#648). If a season run feels necessary to pass acceptance, STOP and float — it isn't (the acceptance invariants are structural, provable on a bounded slice).

## Grip G and the energy channel (consume #664's contract, do not re-derive)
- **G = directed uncertainty (μ=0, one-sided σ⁺).** #664 already emits `g_sigma_onesided` per cell. Carry it as a one-sided σ component on the time channel's cell σ; the point value is UNCHANGED by G. The #663 `grip_estimates` store is currently UNPOPULATED, so `g_sigma_onesided` soft-degrades to 0 → point-identical fits. **This is the expected honest first-pass outcome ("G barely moves the fingerprint"), not a bug.** Populating the grip store is #692 (T4); moving G's μ off zero is #678. Both OUT OF SCOPE — you consume G, never re-fit it. Preserve the byte-identical-point invariant under G σ⁺=0.
- **Energy channel = relative deployment** (`deployment_share`, `deployment_phase_fraction`) — descriptive/instrument, never absolute SOC or kW. Fit it as the second channel for §7's comparison; do not gate on it.

## Acceptance (the substantive invariants — all provable on a bounded slice)
1. **Cutoff-leakage test:** a fit with `as_of_round=R` cannot see any row with `round_idx > R` (the strictly-pre causal cutoff on the driver side). This is THE keystone test — cite the #628 14.6× precedent.
2. **Thin-cell σ-widening priced ONCE and only once** — never re-filtered/re-widened downstream; a unit test proving idempotence of the pricing.
3. **Loud refusal on era/vocabulary mismatch** — no silent substitution; refusal on a failed-gate `ClassVocabulary` by default.
4. **k-cells-always-populated invariant** — every fingerprint returns exactly k cells; missing support → `unresolved` status row, never a missing row.
5. **#675 class-axis coverage recommendation recorded** (investigate-and-recommend; apply `shared_floor` at the fingerprint layer if the under-coverage generalizes).

A measured-null (cells shrink fully to the parent under thin support) is a COMPLETE, successful deliverable — say so honestly with the support numbers.

## #560 reconciliation (design note, non-blocking)
The spec flags #560 (thin fits pass as `ok`, no sample floor) as this issue's direct sibling one layer down: #666 prices thinness ONCE at fit time via σ-widening; #560 asks whether a thin fit should have been accepted AT ALL. Reconcile the two answers in your notes (don't have each layer solve it differently) — a short prose reconciliation is enough; solving #560 is out of scope.

## Out of scope
The join (issue H, #668); race-side push/managed cells (Build 2); low-rank factorization (shelved — the read boundary deliberately carries NO factorization hook); moving G's μ off zero (#678); populating the grip store (#692); the full season-scale run (#670); ANY change to the k / class vocabulary (#642 is downstream and waits on THIS issue's per-class replication evidence — do not re-open k).

## Debt to heed (context, not blockers unless you hit them)
#675 (class-axis calibration — you OWN it, above); #560 (thin-fit acceptance floor — reconcile, above); #632 (DB bloat — write the fingerprint store to its OWN db, keep it OFF the f1_data DBs and OFF #664's observables db); #656 (tests must NOT dirty real DBs — use temp/scratch DBs in tests); #650/#648 (thread-cap + launcher-hang taxes on any long run — detach + state-note-first if a run is long).

## Constraints & hygiene
- **DB-BLOB GUARD (hard):** `data/f1_data_2023.db` (and every `data/f1_data_*.db`) is a TRACKED file that WAL-churns when any read touches it. It must NEVER be committed into your PR (#632 hazard). Before every commit: stage deliverables EXPLICITLY (never `git add -A` / `git add .`); if a data DB shows Modified, `git checkout -- data/f1_data_2023.db` to restore it. Your final diff must be code+tests+schema only — zero DB blobs.
- **Map fence:** do NOT touch `docs/architecture/*`. Record map impact as prose in your return + stage `notes-666.md` and `666-cartography/` for the epic's single CLOSEOUT cartographer reconcile.
- **Cartographer-wrong-checkout carry-forward:** IF you dispatch a cartographer subagent, run an independent `git status` in BOTH the worktree AND the main checkout afterward, and verify its edits landed AND are COMMITTED on the branch (a prior cartographer wrote to the wrong checkout, git-invisible).
- Do NOT commit any `.agent-work/` path on the mission branch. Stage the feedback trio (AGENT_FEEDBACK + lessons-delta.json + CONSTELLATION_FEEDBACK) under `.agent-work/staged-feedback/666-driver-fingerprint/` with a `FENCE.md` citing this launch order; satisfy your feedback/archive gate against that staging dir.
- One writer per shared document per wave; working-notes file = `notes-666.md` (never `findings-*.md` — the Write tool refuses that basename).
- Isolation gate already passed (worktree provisioned off `7ec54b26`, first-action echo confirmed by Admiral: ISOLATION_OK). Do NOT re-provision; do NOT run in any other worktree.

## Reporting
Report at PR + closeout with: the versioned cell store + the hierarchical-shrinkage fit machinery + the acceptance-invariant test results (cutoff-leakage, σ-widening idempotence, loud-refusal, k-cells-populated) + the #675 class-axis coverage recommendation (and any `shared_floor` applied) + an honest statement of the fit's support size and shrinkage behavior on the bounded slice. NO merge without the Admiral (independent world-verify + acceptance re-run on the pinned 3.14 interpreter precede any squash). Float any `user-decision` up to the Admiral; do not reach for the human directly (owner is popping in/out — route through the Admiral).

## Pre-rulings recap
- `fit_two_way` adopted (#665 PASS) — **binding**.
- #675 class-axis calibration = your first plan-phase investigation; apply `shared_floor` at the fingerprint layer if under-coverage generalizes; close #675 with this PR — **binding**.
- Design-it-twice (CALLER/FLEX/MINIMAL hybrid) is SETTLED in the spec; do not re-open — **binding**.
- Build season-capable, run bounded (multi-circuit only where physics_estimates covers it, offline); full season is #670 — **overridable only via float if the spec provably demands the full run (it does not)**.
- G = consume #664's `g_sigma_onesided` directed-uncertainty contract (μ=0, σ⁺); soft-degrades to 0 while grip store empty; preserve byte-identical point invariant — **binding**.
- Consume #662 map + #638 k=4 vocabulary + #664 observables as-is; do not re-open k (#642 downstream) — **binding**.

**Expiry:** this order expires at #666 merge or on a Wave-3 contract-refresh from the Admiral.

# IMPLEMENTER_RESULT — g2 (tests + Spain R reproduction)

> Note: the g2 crew authored all tests + the reproduction harness, but ended its turn waiting on a
> backgrounded reproduction (turn-ending anti-pattern). The Commander ran the reproduction in the
> foreground to completion and recorded the result below. All numbers are from the real run.

## Tests written
- `tests/unit/preprocessing/trajectory/test_nesting_oracle.py` — StintSmoother nests JointFusion oracle to ~mm.
- `tests/unit/preprocessing/trajectory/test_synthetic_honesty.py` — synthetic recovery + held-out per-class χ²≈1
  + NIS mean≈1 + r==1 NS==StintSmoother + unit conversions.
- `tests/unit/preprocessing/trajectory/test_artifact_roundtrip.py` — artifact write/read field preservation.
- `tests/unit/preprocessing/trajectory/test_trust_profile.py` — grading returns a structured profile, not pass/fail.
- `tests/unit/preprocessing/trajectory/_synthetic.py` — shared synthetic-trajectory fixture.
- `tests/integration/test_trajectory_spain_reproduction.py` + `tests/integration/_spain_repro.py` — the committed
  end-to-end reproduction (slow/integration; skips cleanly if data absent).

## Unit results
`py -m pytest tests/unit/preprocessing/trajectory -q` → **17 passed** (45.4s). (Re-run by Commander.)

## THE REPRODUCTION (2022 Spain R, automatic calibration, no hardcoded HPs)
`py -m pytest tests/integration/test_trajectory_spain_reproduction.py -q -s` → **1 passed (789s)**.

**Pooled held-out median = 22.77 ms** (gate ≤ 50 ms; lab E10 reference 20.21 ms). n=1273, p90=66.12 ms, rms 43.3 ms.
Per-loop held-out: s1 25.65 / p90 65.9 (n=429); s2 (corner) 25.96 / p90 87.5 (n=430); sf 16.63 / p90 52.1 (n=430).
20 drivers used, every loop reached a held-out A/B split.

## D3 generalization evidence (the known soft spot — RESOLVED)
Automatic `fit_stint_hp` ran unattended across ALL 20 Spain R drivers. The fitted HPs VARY widely per-driver
(ell 0.80–7.03, sf 84.8–176.3, sig_pos 1.60–2.48) — confirming no single fixed set would be safe — YET every
driver's held-out honesty held: **chi²_pos ∈ [0.86, 1.11], chi²_spd ∈ [0.94, 1.26]** (all ≈1). The automatic
chi²-target calibration is the production path and it generalizes. Evidence:
`.agent-work/issue-448-prod/evidence/spain_reproduction.{json,md}`.

## Source fixes
None required — the g1 module ran the full reproduction as-is.

## Blockers
None. The gate is cleared with automatic calibration; the honest-null STOP clause was not triggered.

## Out-of-scope observations
- Reproduction n=1273 here vs lab n=509 (more drivers / all-driver automatic fit) — broader than the lab check.
- Quali thin-n sessions (47–63 ms in the lab) remain out of scope → validation-breadth follow-up (triage).

## Workflow feedback
- The reproduction is ~13 min; a crew should run it foreground and report, not background-and-wait. The g2 crew
  backgrounded it and stranded — the Commander completed it. Handoffs should state "no backgrounding; the
  Commander will poll if needed" even more emphatically for >10-min steps.

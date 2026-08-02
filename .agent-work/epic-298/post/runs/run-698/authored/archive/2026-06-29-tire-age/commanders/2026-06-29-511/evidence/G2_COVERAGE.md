# G2 Coverage Diagnosis — race_stint_estimates 2023 (R)

- Total rows: 1040  | ok: 1040  | error: 0
- Distinct circuits (gp_name): 20  | drivers: 22

## Per-circuit (ok rows / lateral fits)
- Australia: rows=37 lateral_fit=35
- Austria: rows=60 lateral_fit=59
- Azerbaijan: rows=41 lateral_fit=41
- Bahrain: rows=69 lateral_fit=67
- Belgium: rows=56 lateral_fit=55
- Brazil: rows=50 lateral_fit=48
- Canada: rows=52 lateral_fit=51
- Hungary: rows=54 lateral_fit=54
- Italy: rows=44 lateral_fit=44
- Japan: rows=51 lateral_fit=50
- Las Vegas: rows=43 lateral_fit=43
- Mexico: rows=51 lateral_fit=4
- Miami: rows=40 lateral_fit=40
- Monaco: rows=53 lateral_fit=52
- Netherlands: rows=85 lateral_fit=85
- Qatar: rows=67 lateral_fit=67
- Saudi Arabia: rows=39 lateral_fit=39
- Singapore: rows=42 lateral_fit=42
- Spain: rows=62 lateral_fit=62
- United States: rows=44 lateral_fit=44

## Per-compound (ok rows)
- HARD: rows=397 lateral_fit=369 traction_fit=372
- INTERMEDIATE: rows=55 lateral_fit=55 traction_fit=55
- MEDIUM: rows=392 lateral_fit=367 traction_fit=367
- None: rows=1 lateral_fit=1 traction_fit=1
- SOFT: rows=192 lateral_fit=187 traction_fit=190
- WET: rows=3 lateral_fit=3 traction_fit=3

## Per-axis fit yield (of ok rows)
- lateral (g0): 982/1040
- traction (a0): 988/1040
- braking: 988/1040
- power_drag: 972/1040
- coast: 988/1040

## Lateral (g0,k) distribution
- g0: min=1.232 median=3.172 max=5.975
- k : min=0.00000 median=0.00128 max=0.05844  | k>=0: 982/982
- lateral covariance finite=982/982 PSD=982/982

## Pit-staggered tyre-age spread
- per-stint age span: min=0 mean=17.6 max=53
- races with >=2 compounds (ok): 20/20

## Collapse assessment (commander, G2 reasoning gate)
NO COLLAPSE — proceed to G3. Lateral pool 982/1040 (94%) across 20 circuits; per-compound dry coverage strong (HARD 369 / MEDIUM 367 / SOFT 187). Raw mean lateral_k monotone-up by compound (HARD<MEDIUM<SOFT) — real pre-separation signal. Pit-staggered age span mean 17.6 (max 53), 20/20 races multi-compound — strong identifiability substrate for tyre-vs-track separation.

Notes carried to G3 + triage:
- **Mexico lateral_fit=4/51** (thin) — high-altitude (2240 m) circuit; corner-regime de-conflation yields few usable lateral samples. The separation must down-weight / flag Mexico's g_track (ill-determined there); the lateral compound pool is unaffected (Mexico contributes ~4). Triage candidate.
- **Wet/Intermediate/None compounds** (INTERMEDIATE 55, WET 3, None 1) are a DIFFERENT grip regime — EXCLUDE from the dry tyre-age separation (dry SOFT/MEDIUM/HARD only). 923 dry lateral fits remain.
- G2 ran OS-detached by the Admiral (harness-background workers die on subagent idle — platform kill-vector). Bounded G3/G4/G5 run foreground.

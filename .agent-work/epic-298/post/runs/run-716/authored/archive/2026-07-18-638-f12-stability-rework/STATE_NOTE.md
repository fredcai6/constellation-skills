# Crash-resume state note — 638-f12-stability-rework

- **step:** execute (spine) — driving execute.json, gate g3-rerun-docs (G2 committed 46dc1e28)
- **slug:** g3-rerun-docs (real-data F12 base42 + base137 + rollup + docs; commander foreground)
- **next command:** cd /c/Programs/f1-638 && PYTHONIOENCODING=utf-8 py scripts/f12_held_out_stability.py --db C:/Programs/f1Brainz/data/damage_integrals.db (then --base-seed 137)
- **pid:** foreground — no OS detach; F12 runs ~6 min each, poll if auto-backgrounded
- **expected artifact:** docs/physics/625-f12-holdout-stability.json (headline PASS), docs/physics/638-f12-holdout-stability-seed137.json (PASS), docs/physics/625-regime-time-share.meta.json (f12_headline_verdict PASS), docs/physics/638-f12-stability-rework.md

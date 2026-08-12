You are picking up issue #704 in this repository (fredcai6/f1Brainz).

--- ISSUE #704: #668 cleanup: dedup axis-grouping helper in instrument_panel/replication.py ---
From #668 triage tc2 (recommend-and-defer; cosmetic, non-blocking). `main_effect_margin_uncertainty()` and `_axis_means()` in `src/physics/instrument_panel/replication.py` share axis-grouping logic a small shared helper could de-duplicate (Fowler duplicated-code, non-blocking g6 review).

**Acceptance:** a shared helper removes the duplication; all instrument_panel tests stay green, pyright-0, byte-identical behavior. **Out of scope:** any change to the signed frozen values or the double-centering method. Best as a deliberate simplify-pass (editing the load-bearing replication module re-triggers full review for a cosmetic gain).
--- END ISSUE ---

This is a PLANNING engagement only. Implementation is a separate, later engagement and
is out of scope for you: do not modify, commit, push, or open a pull request, and do not
comment on the issue.

Understand the problem, then produce a plan. Your plan must name the specific files you
would change and explain why each one. Finish by stating your file list plainly under a
final heading `FILES I WOULD CHANGE`, one path per line.

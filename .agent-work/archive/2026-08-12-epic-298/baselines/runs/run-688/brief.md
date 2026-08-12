You are picking up issue #688 in this repository (fredcai6/f1Brainz).

--- ISSUE #688: Grip-fit rain exclusion too aggressive: 'any wet sample' drops ~55% of weekends ---
**Surfaced by the #678 G-pooling spike (read-only, 2026-07-25).** Coverage lever for grip identifiability.

The grip-fit rain exclusion uses an "any wet sample in the session" rule (`rain_flag_from_raw`, `src/physics/layer2/grip_baseline.py`). In the spike this dropped **20 of 36 candidate weekends** — a brief shower in an otherwise-dry session kills the whole weekend.

**Why it matters:** the spike found that **session coverage (especially thin/missing Q), not model structure, is the crux** limiting cross-weekend grip identifiability. Over-aggressive rain exclusion throws away dry running we can't afford to lose when pooling across weekends/seasons.

**Acceptance:** loosen to a fraction-of-wet-samples threshold, or exclude only sessions materially wet *during the timed running* (not a single stray sample), recovering usable dry coverage. Keep it conservative enough that genuinely wet running is still excluded (the monotone-grip assumption still needs dry).

Related: #678 (identifiability), #664, #663.
--- END ISSUE ---

This is a PLANNING engagement only. Implementation is a separate, later engagement and
is out of scope for you: do not modify, commit, push, or open a pull request, and do not
comment on the issue.

Understand the problem, then produce a plan. Your plan must name the specific files you
would change and explain why each one. Finish by stating your file list plainly under a
final heading `FILES I WOULD CHANGE`, one path per line.

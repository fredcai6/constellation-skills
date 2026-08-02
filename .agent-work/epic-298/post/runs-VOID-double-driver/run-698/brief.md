You are picking up issue #698 in this repository (fredcai6/f1Brainz).

--- ISSUE #698: #666 follow-on hardening: store-API primitive-obsession, script .pth path, gitignore ---
Low-priority hardening carried out of #666 (DriverFingerprint), recommend-and-defer. None blocked the merge.

**H1 — DriverFingerprintStore API takes loose primitives instead of `CellAddress` (tc3, Fowler primitive-obsession).** The store's read/write surface passes era/vocab/class as loose strings rather than the `CellAddress` value object the fit layer already uses. Tighten to accept `CellAddress` end-to-end so an ill-formed address can't reach the store. Acceptance: store API typed on `CellAddress`; a malformed-address test.

**H2 — `scripts/fingerprint_class_coverage_675.py` lacks worktree-first `sys.path` insertion.** Bare-run in a git worktree hits the editable-install `.pth` trap — `from src.physics.fingerprint import ...` resolves to the MAIN checkout's `src/` (which lacks the unmerged module) and `ModuleNotFoundError`s. pytest is immune (own path insertion); the script is not. Add the `_REPO_ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(_REPO_ROOT))` guard that `scripts/build_class_utilization_observables.py` already uses. Found during Admiral independent verify (worked once PYTHONPATH forced). Immaterial post-merge (main's `src/` has the module), but any future worktree run re-hits it.

**H3 — gitignore local coverage/summary JSON artifacts (tc2).** The coverage/bounded-fit JSONs written under `.agent-work/.../artifacts/` are already ignored via `.agent-work/`, but confirm no stray JSON lands in a tracked path on a non-epic run.

Source: cmdr-666 TRIAGE_RECOMMENDATIONS.md (tc2/tc3) + Admiral verify (H2). Out of scope: any behavior change to the fit/coverage.
--- END ISSUE ---

This is a PLANNING engagement only. Implementation is a separate, later engagement and
is out of scope for you: do not modify this repository's source, tests, or documentation,
do not commit, push, or open a pull request, and do not comment on the issue. Your own
working notes and planning artifacts under `.agent-work/` are the one exception, and are
expected.

Run this as a Commander. Load the `constellation-commander` skill and drive its spine
through its steps in order, stopping once the `plan` step is complete: the mission frame
authored and `execute.json` authored. Do not enter `execute`: stop there and return.
No human is reachable for this engagement, so wherever a step calls for a human decision,
record what you would have asked, decide it yourself, and carry on rather than waiting.

Your plan must name the specific files you would change and explain why each one. Finish
by stating your file list plainly under a final heading `FILES I WOULD CHANGE`, one path
per line.

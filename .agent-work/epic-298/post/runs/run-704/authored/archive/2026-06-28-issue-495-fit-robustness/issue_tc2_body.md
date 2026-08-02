Surfaced by #495 (physics fit robustness), deferred out of its scope by explicit
decision (decide-fix checkpoint: #495 was crash→typed-skip only).

**Observation:** post-PR #548, very sparse single-session fits pass as `ok` — e.g.
Azerbaijan 2023 Q GAS with **1 flying lap / 412 samples** returns `ok`. The #495
intent was "no second-class fits in the cross-session pool," which raises the
question of a **minimum-flying-laps / minimum-sample floor** below which a fit should
be a typed-skip (or carry a low-trust flag) rather than a plain `ok`.

**Tension to resolve with evidence (do NOT add a blanket floor blindly):** the P0
findings (`reports/physics/P0_evidence_findings.md`) show braking identifiability
tracks each circuit's braking *demand* — flowing/high-speed tracks legitimately yield
few events, so sparse ≠ broken. A naive floor risks discarding real sparse-track
fits.

**Task:** measure the relationship between fit thinness (flying-lap count / sample
count) and fit quality; decide — with numbers — whether a floor is warranted and what
form it takes (hard typed-skip vs a trust-profile/confidence field), then implement
or explicitly decline.

**Non-goals:** not a crash fix (that's #495). No blanket floor without evidence it
doesn't drop legitimate sparse-track fits.

**Acceptance criteria:**
- [ ] Measured relationship between thinness and fit quality across 2023-Q.
- [ ] Evidence-backed decision on whether/what floor; implemented as a typed reason
      or trust field, or explicitly declined with rationale.

Refs: #495, #492, `reports/physics/P0_evidence_findings.md`,
`src/physics/session_fit.py`.

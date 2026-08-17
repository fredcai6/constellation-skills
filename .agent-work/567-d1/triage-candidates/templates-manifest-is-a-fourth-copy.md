# Triage candidate — `TEMPLATES_MANIFEST.json` is a fourth copy of template truth

**Found at:** `g2-review`, lane D1, epic #567 wave 2. Reported by the g2 reviewer as `tc2`.

**What was found.** `.agent-work/templates/TEMPLATES_MANIFEST.json` records a `sha256` per template,
56 entries. After this lane's sweep, the five edited templates no longer match their recorded
hashes.

The guard's own docstring, and this lane's handoffs, say a sweep must edit **all three** copies of a
doctrine template — the `skills/` source, the `.agent-work/templates/` overlay, and the
`.baseline/<skill>/` mirror. **There are four.**

**Deliberately not updated, and the reason matters.** The manifest is an **install lockfile**, not a
live mirror: its header carries `generated: 2026-08-10` and
`source_commit: 3697e12c99ea3e7673bae675faf40c824598d452`, and `scripts/install_constellation.py`
writes it as a record of one install event. Hand-editing five hashes into it would make it claim
those bytes were installed at that commit, which they were not — the same falsification that
`decision:records-are-not-instruction` forbids for `docs/superpowers/**`. A stale lockfile is honest;
a doctored one is not.

**Inert today, measured:** `scripts/check_skill_freshness.py` recomputes hashes from the files and
never reads that field, and no test reads it either. The next real install regenerates it.

**Why it is a candidate and not a fix.** `scripts/install_constellation.py` is **lane D2's** file
this wave, and running the installer would rewrite far more than five hashes. The durable question —
whether a fourth tracked copy of template truth should exist at all, and what reconciles it — is the
same question as the `.baseline/` mirror candidate, one copy further out.

**Related:** `.agent-work/567-d1/triage-candidates/overlay-baseline-mirror-doubles-every-target.md`.

**Disposition:** `recommend-and-defer`. Pair onto an open issue at epic closeout, or record as an
episode. **Not filed as an issue** — `decision:no-issue-filing-mid-run`.

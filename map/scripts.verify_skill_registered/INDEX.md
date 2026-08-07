# scripts.verify_skill_registered
scripts/verify_skill_registered.py, 165 lines, 2 holes

Refuse a mechanically-broken or unregistered skill — the constellation-write-a-skill RAIL.

This is the single mechanically-enforced rail for the `constellation-write-a-skill`
skill (DESIGN_SPEC Section C). A minted skill must clear it before it is accepted.
The rail COMPOSES the corpus tooling rather than re-implementing it:

  1. MECHANICALLY BROKEN — re-uses `curate_corpus.py`'s mechanical checks and
     refuses on the *gating* subset (unparseable SKILL.md; no when-to-use marker;
     a confusable-pair skill with no exclusion clause; a missing/invalid invoker
     tag). Soft budgets curate also measures (size, description length, reference
     TOCs, duplication) stay ADVISORY here — they never refuse a mint. Semantic
     goodness (completion-criteria sharpness, the no-op test, negative space, ...)
     is DELIBERATELY not gated: that is the independent reviewer's judgment. The
     rail proves the skill installs and is registered, never that it is *good*.

  2. UNREGISTERED DEAD SEAM — the one property `curate_corpus.py` cannot see. A
     skill directory is auto-discovered, but the scripts and shared doctrine it
     needs are wired ONLY by its entries in `install_constellation.py`'s
     SKILL_REFERENCE_BUNDLES / SKILL_SCRIPT_BUNDLES. A skill missing from the
     reference bundle installs with NO doctrine — a dead seam that looks fine on
     disk. This missing-bundle-registration case is the exact failure mode the
     rail guards (DESIGN_SPEC Section C / x6-anatomy).

The `main` CLI additionally runs `install --dry-run` over the real corpus as the
installability half of the check. Standard library only.

imports stdlib: __future__.annotations, argparse, os, pathlib.Path, sys
imports third-party: curate_corpus, install_constellation
imported by: none found

```python
GATING_CHECKS = frozenset({'parse', 'description', 'description-when-to-use', 'description-exclusion', ...
```

- [SkillRegistrationError](SkillRegistrationError.md) class: Raised when a minted skill is mechanically broken or unregistered — the rail's refusal.
- [_require](_require.md) function: HOLE: no docstring
- [_gating_findings](_gating_findings.md) function: Run curate's mechanical checks over `root` and return the details of every
- [verify_skill_registered](verify_skill_registered.md) function: Raise SkillRegistrationError if `skill` (a source directory name under
- [_dry_run_installs](_dry_run_installs.md) function: Installability half (CLI only): the real skill passes install --dry-run.
- [main](main.md) function: HOLE: no docstring

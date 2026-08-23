# Triage Recommendation: `install_constellation.py`'s manifest doesn't bundle `verify_interrogation.py` with `"charter"`

## Classification
`bug`

## Source checklist/artifact
- epic-569/w3-promote g5 (CHARTER.template.json promotion), independently reconfirmed by g5's reviewer

## Structural anchor
`path: scripts/install_constellation.py`

## Cartographer mismatch class
`none`

## Observations

### Observation 1
- **What's wrong:** `scripts/verify_interrogation.py` exists and could satisfy CHARTER's
  `interrogate.c1` postcondition ("doctrine resolved to role-operable decisions"), but
  `install_constellation.py`'s `SKILL_SCRIPTS` manifest does not bundle it with `"charter"` — a
  role that installs `interrogate.c1` would silently lose the verifier in an installed repo.
- **Expected:** either the manifest bundles `verify_interrogation.py` with `"charter"`, or
  `interrogate.c1` is documented as intentionally unpromotable so a future promotion attempt does
  not repeat this discovery.
- **Conditions:** any repo that installs the `charter` skill via `install_constellation.py` and
  later tries to promote `interrogate.c1` to a `command`-kind check calling
  `verify_interrogation.py`.
- **Type:** `measured` — read `scripts/install_constellation.py`'s `SKILL_SCRIPTS` manifest
  directly: `"interrogator": ("checklist_engine.py", "verify_interrogation.py")` at line 234,
  `"charter": ("checklist_engine.py",)` at line 224.
- **Rev:** `epic-569/w3-promote` branch, commit `d73c6b9a` (g5's own promotion commit; the manifest
  was read as-is, not touched).

## Possible fix
Add `"verify_interrogation.py"` to `"charter"`'s tuple in `SKILL_SCRIPTS`, mirroring
`"interrogator"`'s own entry — then `interrogate.c1` becomes a genuine promotion candidate for a
future wave.

## Recommended priority
`low`

**Reason:** does not block or degrade anything today — `interrogate.c1` is currently, correctly,
left `check: null`. Only matters if/when a future wave wants to promote it.

## Related artifacts
- `.agent-work/w3-promote/crew-handoffs/g5-reviewer-result.md` (independent re-confirmation)
- `.agent-work/w3-promote/RESULT.md` §5

## Disposition
`recommend-and-defer`

**Detail:** issue-filing authority is unclear this run — no explicit issue-creation authority is
named in `docs/agents/ORCHESTRATOR_CONTEXT.md` or the launch order's Inherited Latitude section;
delegated mode with no reachable human this gate.

## Issue creation authority
`issue-ready only`

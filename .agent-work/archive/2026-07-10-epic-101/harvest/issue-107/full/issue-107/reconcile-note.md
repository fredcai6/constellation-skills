# Reconcile — issue #107 (direct structural-record reconcile)

No `docs/architecture/` packet map exists (skill-source repo), so reconcile is direct per the architecture-bookend rule, not a Cartographer dispatch.

**Structural record the change actually touched — folded in:**
- `SKILL_INDEX.md` — the skill roster of record. Updated: new `## Constellation Commander (delegated)` entry added (g2). Reflects the implemented change.
- `scripts/install_constellation.py` bundle maps — the enforced install-composition record. Updated (`SKILL_REFERENCE_BUNDLES` gains `commander-delegated`) and test-pinned. Reflects the change.
- `skills/commander/references/commander-core.md` + `crew-dispatch.md` — new doctrine-home files; the commander skill's own internal structural record. Authored (g1).

**Design docs the change did NOT structurally invalidate — reasoned no-op:**
- `docs/CONSTELLATION_OVERVIEW.md` — models the system at the ROLE + context-artifact level. The Commander *role* is unchanged (still "runs one bounded issue end to end; owns spine/interrogation/execute; dispatches crew"); the delegated variant is a mode already described, and the split is install-packaging (two entry skills over one core), not a new role or a changed artifact flow. Its role list, checklist table, and handoff/result rows remain accurate. No edit needed.
- `docs/CHECKLIST_SCHEMA.md` / `CHECKLIST_ENGINE_DESIGN.md` — engine substrate, untouched by this change. No-op.

Verdict: structural record reflects the implemented change (SKILL_INDEX + installer + commander references); design-doc role/engine model is a reasoned no-op. Compliant.

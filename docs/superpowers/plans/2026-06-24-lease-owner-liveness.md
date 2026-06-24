# Lease Owner-Liveness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the checklist engine's session lease never refuse its own owner for staleness — the owner's mutating verbs refresh the lease (liveness), and staleness gates only non-owners.

**Architecture:** Two small, separable changes in `scripts/checklist_engine.py`: (1) the gate `require_session` checks ownership first and lets the owner pass regardless of staleness; (2) a new `_refresh_owner_heartbeat` helper, called from `dispatch` after the gate passes, stamps the owner's `last_heartbeat` on every mutating verb. Plus a doctrine update in three reference docs. No new state fields.

**Tech Stack:** Python 3 (stdlib only), `unittest`-style tests run under `pytest`.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-06-24-lease-owner-liveness-design.md` — implement exactly what it states.
- **No new state fields, no new config.** Reuse `last_heartbeat`, `engine_session.session_id`, `MUTATING_VERBS`. `lease_stale_seconds` stays 1800 (unchanged).
- **Non-owner behavior is unchanged** — a different session against a stale lease is still refused with a `claim` instruction; a different active (fresh) lease is still refused with an ownership instruction. Only the *owner + stale* case changes (refuse → pass).
- **Self-heal is silent:** the owner self-healing a stale lease writes **no** `previous_session_id` / `takeover_reason`. Those fields stay reserved for genuine cross-session takeovers via `claim --force`.
- The gate (`require_session`, a pure raise-or-return decision, no mutation) and the stamp (`_refresh_owner_heartbeat`, the mutation) stay as **separate units**.
- Keep the explicit `heartbeat` verb and its owner-only semantics untouched.
- Run tests with `python -m pytest`. The lease tests live in `tests/test_checklist_engine.py` class `Leasing`.

---

### Task 1: Owner-liveness in the engine (gate + stamp + tests)

**Files:**
- Modify: `scripts/checklist_engine.py` — rewrite `require_session` (currently lines 396–419); add `_refresh_owner_heartbeat` immediately after `_active_lease` (currently ends line 393); wire the stamp into `dispatch` (currently lines 913–915).
- Test: `tests/test_checklist_engine.py` — class `Leasing` (rewrite one test at lines 525–537; add three).

**Interfaces:**
- Consumes (already in the module): `MUTATING_VERBS` (a `set[str]`), `_active_lease(cl) -> dict | None`, `_is_stale(session, config) -> bool`, `_now() -> str` (ISO-8601), `EngineError`.
- Produces:
  - `require_session(cl: dict, verb: str, session_id: str | None, config: dict) -> None` — same signature as today; owner now always passes.
  - `_refresh_owner_heartbeat(cl: dict, session_id: str | None) -> None` — stamps `last_heartbeat` iff `session_id` owns the active lease; no-op otherwise.

The four mutating-verb test fixtures use existing helpers in the test file: `gated(g1=gate(...))`, `gate(id, status="pending", command=PASS_COMMAND)`, `E.claim(cl, session_id, claimed_by, worktree, config, force=False, reason=None)`, `_old_ts(seconds_ago)`, and the module alias `E`. `E.start(cl, "g1")` returns `"g1 -> in-progress"`; the persisted status path is `cl["tasks"]["g1"]["status"]`.

- [ ] **Step 1: Rewrite the stale-lease test to assert owner self-heal**

In `tests/test_checklist_engine.py`, replace the entire existing method `test_stale_lease_blocks_mutation_until_reclaimed` (lines 525–537) with:

```python
    def test_stale_lease_self_heals_for_owner(self):
        # The owner is never blocked by its own staleness: the gate passes, and
        # the liveness stamp clears the staleness without a re-claim — and writes
        # no takeover record (resuming your own work is not a takeover).
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        cl["engine_session"]["last_heartbeat"] = _old_ts(10_000)
        cfg = {"lease_stale_seconds": 1800}
        self.assertTrue(E._is_stale(cl["engine_session"], cfg))
        E.require_session(cl, "start", "s1", cfg)   # owner: does not raise
        E._refresh_owner_heartbeat(cl, "s1")        # liveness stamp clears it
        self.assertFalse(E._is_stale(cl["engine_session"], cfg))
        self.assertIsNone(cl["engine_session"]["previous_session_id"])
        self.assertIsNone(cl["engine_session"]["takeover_reason"])
```

- [ ] **Step 2: Add a non-owner regression-guard test**

Immediately after the method from Step 1, add:

```python
    def test_nonowner_against_stale_lease_still_refused(self):
        # The unchanged half: a DIFFERENT session must still claim a stale lease.
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        cl["engine_session"]["last_heartbeat"] = _old_ts(10_000)
        cfg = {"lease_stale_seconds": 1800}
        self.assertTrue(E._is_stale(cl["engine_session"], cfg))
        with self.assertRaises(E.EngineError):
            E.require_session(cl, "start", "s2", cfg)
```

- [ ] **Step 3: Add the liveness-stamp integration test (through `main`)**

Immediately after the method from Step 2, add (this proves the stamp is wired through `main` → `dispatch`):

```python
    def test_mutating_verb_stamps_owner_heartbeat(self):
        cl = gated(g1=gate("g1", "pending", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        cl["engine_session"]["last_heartbeat"] = _old_ts(60)  # old but not stale
        before = cl["engine_session"]["last_heartbeat"]
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            self.assertEqual(
                E.main(["--file", str(f), "start", "g1", "--session-id", "s1"]), 0)
            reloaded = E.load(f)
        self.assertEqual(reloaded["tasks"]["g1"]["status"], "in-progress")
        self.assertNotEqual(reloaded["engine_session"]["last_heartbeat"], before)
```

- [ ] **Step 4: Add the helper no-op unit test**

Immediately after the method from Step 3, add:

```python
    def test_refresh_owner_heartbeat_noop_for_nonowner_and_no_lease(self):
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        E._refresh_owner_heartbeat(cl, "s1")            # no lease: no-op, no crash
        self.assertNotIn("engine_session", cl)
        E.claim(cl, "s1", "commander", ".", {})
        cl["engine_session"]["last_heartbeat"] = _old_ts(10)
        before = cl["engine_session"]["last_heartbeat"]
        E._refresh_owner_heartbeat(cl, "s2")            # non-owner: untouched
        self.assertEqual(cl["engine_session"]["last_heartbeat"], before)
```

- [ ] **Step 5: Run the new/changed tests to verify they FAIL**

Run: `python -m pytest tests/test_checklist_engine.py::Leasing -v`
Expected: FAIL — `test_stale_lease_self_heals_for_owner` errors/fails (`require_session` still raises for the owner, and `_refresh_owner_heartbeat` does not exist → `AttributeError`); `test_mutating_verb_stamps_owner_heartbeat` fails (heartbeat unchanged by `start`); `test_refresh_owner_heartbeat_noop_*` errors (`AttributeError`). `test_nonowner_against_stale_lease_still_refused` already passes (behavior unchanged for non-owners) — that is fine.

- [ ] **Step 6: Add the `_refresh_owner_heartbeat` helper**

In `scripts/checklist_engine.py`, insert this function immediately after `_active_lease` (which currently ends at line 393) and before `require_session`:

```python
def _refresh_owner_heartbeat(cl: dict, session_id: str | None) -> None:
    """Stamp liveness: if `session_id` owns the active lease, advance its
    `last_heartbeat` to now. No-op when there is no active lease, a different
    session owns it, or `session_id` is falsy. Called on every mutating verb the
    owner issues, so an actively-working owner never goes stale and a genuine
    idle gap self-heals on the owner's next verb. It never writes a takeover
    record — the owner resuming its own work is not a takeover."""
    lease = _active_lease(cl)
    if lease is not None and session_id and session_id == lease.get("session_id"):
        lease["last_heartbeat"] = _now()
```

- [ ] **Step 7: Rewrite `require_session` to be owner-blind to staleness**

In `scripts/checklist_engine.py`, replace the entire `require_session` function (currently lines 396–419) with:

```python
def require_session(cl: dict, verb: str, session_id: str | None, config: dict) -> None:
    """The actor-authority gate. Mutating verbs are session-gated only ONCE an
    ACTIVE lease exists; with no active lease a missing `--session-id` is fine
    (legacy checklists/templates have no `engine_session`).

    Staleness gates **non-owners only** — it answers "has the owner gone quiet
    long enough that someone else may seize the lease?" The rightful owner is
    NEVER blocked by its own staleness, because an owner issuing a verb IS the
    liveness signal (the stamp `_refresh_owner_heartbeat` records it). So the
    owner always passes; a non-owner is refused — with a `claim` instruction if
    the lease is stale, or an ownership instruction if it is a different,
    still-active lease."""
    if verb not in MUTATING_VERBS:
        return
    lease = _active_lease(cl)
    if lease is None:
        return  # no lease claimed: legacy behavior, no session needed
    if session_id == lease.get("session_id"):
        return  # the owner is never blocked by its own staleness
    if _is_stale(lease, config):
        raise EngineError(
            f"checklist lease {lease.get('session_id')!r} is stale; "
            f"`claim` it (same id or --force --reason) before mutating"
        )
    raise EngineError(
        f"checklist is owned by active session {lease.get('session_id')!r}; "
        f"pass --session-id {lease.get('session_id')!r} or take over with "
        f"`claim --force --reason ...`"
    )
```

- [ ] **Step 8: Wire the stamp into `dispatch`**

In `scripts/checklist_engine.py`, find this block in `dispatch` (currently lines 913–915):

```python
    # Actor-authority gate: once an active lease exists, a mutating verb must
    # carry the owning --session-id. No lease -> legacy behavior (no session).
    require_session(cl, v, getattr(args, "session_id", None), config)
```

Replace it with:

```python
    # Actor-authority gate: once an active lease exists, a mutating verb must
    # carry the owning --session-id. No lease -> legacy behavior (no session).
    session_id = getattr(args, "session_id", None)
    require_session(cl, v, session_id, config)
    # Owner activity = liveness: a mutating verb by the owner refreshes the lease,
    # so an actively-working session never goes stale and an idle gap self-heals.
    if v in MUTATING_VERBS:
        _refresh_owner_heartbeat(cl, session_id)
```

- [ ] **Step 9: Run the lease tests to verify they PASS**

Run: `python -m pytest tests/test_checklist_engine.py::Leasing -v`
Expected: PASS — all `Leasing` tests green (the original 15 minus the rewritten one plus the 3 new = 18 tests).

- [ ] **Step 10: Run the full engine test file**

Run: `python -m pytest tests/test_checklist_engine.py -q`
Expected: PASS — no regressions in `Leasing`, `ShippedTemplates`, or any other class.

- [ ] **Step 11: Commit**

```bash
git add scripts/checklist_engine.py tests/test_checklist_engine.py
git commit -m "Engine: owner is never blocked by its own lease staleness (#32)

require_session checks ownership first and lets the owner pass regardless of
staleness; a new _refresh_owner_heartbeat stamp (wired into dispatch) refreshes
the owner's last_heartbeat on every mutating verb. Non-owner refusals unchanged;
self-heal writes no takeover record.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: Fold the new doctrine into the lease-lifecycle docs

**Files:**
- Modify: `docs/CHECKLIST_SCHEMA.md` (the paragraph at line 94).
- Modify: `skills/workbench/references/checklist-engine.md` (the bullets at lines 57 and 59).
- Modify: `skills/admiral/references/fleet-doctrine.md` (the bullet at lines 102–105).

**Interfaces:** None (documentation only). This task depends on Task 1's behavior being the source of truth, but touches no code.

- [ ] **Step 1: Update `docs/CHECKLIST_SCHEMA.md`**

Replace the paragraph at line 94 (begins "A lease whose `last_heartbeat` is older than `lease_stale_seconds` is **stale**. A stale lease does not permanently lock…") in full with:

```markdown
A lease whose `last_heartbeat` is older than `lease_stale_seconds` is **stale**. Staleness gates **non-owners only** — it answers "has the owner gone quiet long enough that someone else may seize the lease?" The rightful **owner is never blocked by its own staleness**: every mutating verb the owner issues refreshes `last_heartbeat` (the verb itself is the liveness signal), so an actively-working owner never goes stale and a genuine idle gap self-heals on the owner's next verb — no re-claim, and **no takeover record** (resuming your own work is not a takeover). A **different** session against a stale lease is still **refused with an instruction to `claim` first**; that reclaim records the prior session in `previous_session_id`. Timestamps are real (the engine has a single `_now()` time hook); staleness is computed by parsing `last_heartbeat`.
```

- [ ] **Step 2: Update `skills/workbench/references/checklist-engine.md`**

Replace the bullet at line 57 (begins "- `heartbeat` keeps your lease fresh; `release` closes it when you are done.") in full with:

```markdown
- `heartbeat` proactively refreshes your lease — only needed for an idle wait where no mutating verb will fire (mutating verbs refresh it for you); `release` closes it when you are done.
```

Then replace the bullet at line 59 (begins "- A lease goes **stale** if its heartbeat lapses…") in full with:

```markdown
- A lease goes **stale** if its heartbeat lapses (config `lease_stale_seconds`, default 1800s). Staleness gates **non-owners only**: as the **owner** you are never blocked by your own staleness — every mutating verb you issue refreshes the heartbeat, so a long step or idle gap self-heals on your next verb (no re-claim, no takeover record). A **different** session must `claim` the stale lease (same id, or `--force --reason`) before mutating — the engine refuses it and tells it to claim.
```

- [ ] **Step 3: Update `skills/admiral/references/fleet-doctrine.md`**

Replace the bullet at lines 102–105 (begins "- The spine lease goes stale after `lease_stale_seconds`…") in full with:

```markdown
- The spine lease goes stale after `lease_stale_seconds` (default 1800s) of no
  heartbeat, but staleness gates **non-owners only**: as the lease owner you are
  never refused for your own staleness — every mutating verb refreshes the lease,
  so a long crew/compute step or idle gap self-heals on your next verb. A re-claim
  is only needed to take over a *different* session's lease.
```

- [ ] **Step 4: Verify the suite is still green and the wording landed**

Run: `python -m pytest tests/test_checklist_engine.py -q`
Expected: PASS (docs are prose; this confirms nothing was accidentally broken).

Run: `git diff --stat`
Expected: only the three doc files listed above are modified.

- [ ] **Step 5: Commit**

```bash
git add docs/CHECKLIST_SCHEMA.md skills/workbench/references/checklist-engine.md skills/admiral/references/fleet-doctrine.md
git commit -m "Docs: lease doctrine — owner never blocked by its own staleness (#32)

Fold the owner-liveness rule into CHECKLIST_SCHEMA, the workbench engine
reference, and the admiral fleet-doctrine: staleness gates non-owners only;
mutating verbs refresh the owner's lease; explicit heartbeat is for idle waits.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Self-Review

**1. Spec coverage:**
- Gate owner-blind to staleness → Task 1 Steps 6–7. ✓
- Liveness stamp on mutating verbs (`_refresh_owner_heartbeat`, wired in `dispatch`) → Task 1 Steps 6, 8. ✓
- Silent self-heal (no takeover record) → asserted in Task 1 Step 1 test; preserved by the helper never touching `previous_session_id`/`takeover_reason`. ✓
- Non-owner unchanged → Task 1 Step 2 regression test. ✓
- `lease_stale_seconds` / `heartbeat` verb / no new fields unchanged → no task touches them; Global Constraints. ✓
- Docs in all three files → Task 2. ✓
- Tests: rewrite the one, add stamp test, add no-takeover-record assertion, keep non-owner-refused + heartbeat-only-by-owner + CLI lifecycle → Task 1 Steps 1–4; the kept tests are untouched. ✓

**2. Placeholder scan:** No TBD/TODO/"handle edge cases"/"similar to". Every code step shows full code. ✓

**3. Type consistency:** `require_session(cl, verb, session_id, config) -> None` and `_refresh_owner_heartbeat(cl, session_id) -> None` are used identically in the helper, the gate, `dispatch`, and all tests. `last_heartbeat`, `session_id`, `previous_session_id`, `takeover_reason`, and `cl["tasks"]["g1"]["status"]` match the existing schema. ✓

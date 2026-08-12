# Independent clean-room review — #179 (Why-capture + refresh primitives, Modules 1 & 4)

**VERDICT: APPROVE**

Reviewer: independent (clean-room, did not author). Worktree: `C:/Programs/constellation-wt-179-rev` @ `99a3e01` (detached at PR tip). Base for diff: `54f5965`.

---

## Worktree isolation (`--here`)

```
$ py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-179-rev
worktree OK: in C:/Programs/constellation-wt-179-rev
EXIT: 0
```

## File fence — CONFIRMED

`git diff --name-only 54f5965...HEAD` returns exactly:
- `scripts/checklist_engine.py`
- `tests/test_checklist_engine.py`

Worktree `git status --porcelain` is clean. No out-of-fence files touched.

---

## Acceptance criteria (1–6) — each independently verified

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | Non-exempt advance, no why, no --mechanical → REFUSED, fails closed | **PASS** | Probe 1 + CLI: `REFUSED: g1: advancing a non-exempt gate requires a running understanding…`, exit 1, status stays `in-progress`. |
| 2 | Exempt gate (why_exempt:true) advances with no why prompt | **PASS** | Probe 1 row `why_exempt=True + no why -> OK status=complete`. |
| 3 | --mechanical discharges; trail records marker; marker is NOT the digest | **PASS** | Probe 5: after `advance g2 --mechanical`, `_digest` returns the earlier real why (`'real understanding'`), not the mechanical step. `_latest_why_record` skips `mechanical` and `why is None` entries. |
| 4 | Latest non-mechanical why retrievable as DIGEST: via current | **PASS** | CLI: `current` prints `DIGEST: I verified the gate genuinely holds`. |
| 5 | reopen-freshens-digest incl. cascade | **PASS** | Probe 3 (digest→None after reopen, prior entries byte-identical) + Probe 4 (cascade: downstream `g2` digest→None after reopening upstream `g1`). Re-advance after reopen re-freshens to the new why (full lifecycle test). |
| 6 | has_pending_refresh_request + round-trip; REFRESH REQUESTED shown/absent correctly | **PASS** | Probe 6: pending False→True after attach, seam-specific (other gate False), superseded→False, predicate pure (no mutation). |

Full engine suite: **166 passed, 18 subtests passed** (`py -m pytest tests/test_checklist_engine.py -q`). Test count grew 145→166 (net +21 `def test_`). **No prior test deleted** — the only removed `def` line in the diff is the `gate()` helper *signature*, which was modified in place (gained `why_exempt=True` param), not a test.

---

## The four invariants that matter most — adversarial probes

### 1. FAIL-CLOSED (falsifiable) — HOLDS
Probed every bypass path I could construct against a non-exempt gate (all with a legacy spine carrying **no** `why_trail` key):

| Input | Outcome |
|-------|---------|
| no why, no --mechanical | REFUSED |
| `--why ""` (empty) | REFUSED |
| `--why "   "` (whitespace) | REFUSED |
| `why_exempt=False` + no why | REFUSED |
| `why_exempt=0` (falsy) + no why | REFUSED |
| `why_exempt=""` (falsy-but-present) + no why | REFUSED |
| `why_exempt=None` (key omitted) + no why | REFUSED |
| `--mechanical` | OK |
| real `--why` | OK |
| `why_exempt=True` / truthy string | OK |

Guard is `if not bool(t.get("why_exempt")):` then requires `mechanical` or `(why or "").strip()`. Empty/whitespace/`--why ""` all `.strip()` to falsy → refuse. Only a **truthy** `why_exempt` bypasses (the intended exempt path). No falsy-but-present value slips through.

**Other verbs that close a gate:** the ONLY writes of `status="complete"` are line 910 (`advance`, gated, behind the why guard) and line 925 (`record`, which raises if not SURVEY). `skip` writes the distinct `"skipped"` terminal state and requires its own `reason` — it does not claim completion, so it is correctly out of the why requirement. No alternate close-a-gated-gate path exists.

### 2. BACKWARD COMPATIBILITY — HOLDS
Constructed a minimal old-shape spine on disk (no `why_trail`, task with no `why_exempt`) and drove it via the real CLI:
- Why-less advance → `REFUSED …`, **exit 1**, doctrine rail printed, **no unhandled exception / no traceback**.
- Refused advance leaves state **semantically identical** (verified `json.load` equality reset-vs-after = `True`): `why_trail` key NOT introduced, `g1` status still `in-progress`. (The on-disk file is re-serialized with `indent=2` by `main()`'s deliberate save-on-refusal — a whitespace-only reformat, not a content change.)
- Same file then advances cleanly with `--why "…"` → exit 0, `DIGEST:` surfaces.

`_append_why`/`_append_reopen_marker` use `setdefault("why_trail", [])`; predicates use `cl.get("why_trail", []) or []` and `t.get("evidence", []) or []` — all missing-key safe. A missing `why_exempt` → `bool(None)` → not exempt (opt-out default confirmed in production code path, not just tests).

### 3. APPEND-ONLY — HOLDS
`reopen` calls only `_append_reopen_marker` (target + each cascaded gate); it never indexes into or edits a prior `why_trail` entry. Probe 3: entries preceding a reopen are **byte-identical** before/after (`trail_after_reopen[:n] == trail_after_adv`), trail only grows. Full-lifecycle test: after advance→reopen→re-advance, `why_trail[0]` still `'first understanding'`, `[1]` is the reopen marker, len=3. No mutation or deletion of any prior row anywhere in the diff.

### 4. POSTCONDITION-BEFORE-WHY — HOLDS
Unmet postcondition on a non-exempt gate with no why → `REFUSED: g1: postconditions unmet ['c1']` (the postcondition refusal), NOT the why prompt. The why block sits **after** the `unmet` check (line 893+ follows line 890–892). You cannot buy past unfinished work with a why.

### Test-helper default scrutiny — CLEAN, no hidden regression
The shared TEST `gate()` helper defaults `why_exempt=True` so ~legacy fixtures stay green — but the **production** default is genuinely NOT-exempt (`t.get("why_exempt")` is `None`→falsy for a missing key), and this is exercised by dedicated fixtures, NOT bypassed everywhere:
- Explicit non-exempt (`why_exempt=False`) fixtures across ~14 new tests (refuse, mechanical, digest, reopen, cascade, blank-why, postcondition-order, CLI).
- True legacy-shape (`why_exempt=None`, key omitted) fixtures: `test_existing_shape_non_exempt_refused_then_passes_with_why`, `test_cli_legacy_spine_refuses_cleanly_never_crashes`.
- My own independent legacy CLI fixture (key entirely absent) confirms the not-exempt default outside the test helper.

---

## Findings

**No blocking findings.** One low-severity observation for triage (not a #179 regression):

- **[LOW / informational] `advance --from-child` + why-refusal makes a pre-existing double-attach more reachable.** `advance` calls `attach(cl, iid, "review-result", cons)` at `scripts/checklist_engine.py:886` — *before* the new why guard (line 899+). `attach` (line 1327) appends unconditionally with no dedup. So `advance g1 --from-child child.json` (no `--why`) on a non-exempt gate attaches the child consolidation, then refuses on the missing why; re-running with `--why` attaches it a **second** time. This is pre-existing engine behavior (`main()` saves state on refusal by design; any prior refusal reason — unmet postcondition, lease — already double-attaches on re-run), but #179 introduces a common new refusal point on that exact path. No fail-closed/correctness impact: the gate stays `in-progress`, evidence is additive, and a duplicate `review-result` cannot falsely satisfy a postcondition it already satisfied once. Suggest a follow-up triage to make `attach` (or the from_child seam) idempotent; **does not block #179**.

Minor note (no action): `_latest_why_record` is O(n²) in `why_trail` length (nested reopen-supersession scan), invoked per `current`. Negligible at realistic spine sizes; flagging only for completeness.

---

## Bottom line
The engine change is fail-closed on every path I could probe, backward-compatible with old-shape spines (clean refusal, no crash, no partial/corrupt write), strictly append-only across reopen (incl. cascade), orders postconditions before the why, and grounds its production not-exempt default in dedicated fixtures rather than the test-helper default. Full suite green, no test deleted, file fence intact. **APPROVE.**

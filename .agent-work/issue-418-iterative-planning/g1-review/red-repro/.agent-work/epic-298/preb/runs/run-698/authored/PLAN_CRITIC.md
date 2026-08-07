# Cold plan critic — #698 (cmdr-698)

**Remit:** adversarially read `MISSION_FRAME.md` + `execute.json` (the converged candidate B plan). Nothing is
sacred; deliberate decisions are attackable.

**NOT COLD — stated plainly.** Doctrine wants a critic with no authoring context. This session bars subagent
dispatch, so this pass was written by the plan's own author against the written artifacts. Author-blindness is
exactly what a cold read exists to defeat, so treat every "no finding" here as weaker evidence than a genuine
cold pass would give. Recorded as an untaken road in `PLAN_ALTERNATIVES.md` and surfaced at plan approval.

**Panel-vs-single:** single, not a panel — and *because* it isn't cold, a panel of self-critics would have
added ceremony, not independence. Surfaced for overrule.

---

## Findings — APPLIED to the plan before freeze

### F1 (severe) — the `cell_key` field order is a live landmine and g1 only gestures at it

`cell_key` joins `_CELL_KEY_FIELD_NAMES` in the order
`(driver, era, vocabulary_version, class_id, channel, what_measure)` — **`class_id` sits at position 4, not
last** (`address.py:52-59`). The moment `CellAddress` is re-expressed as "slot + `class_id`", the *natural*
composition produces `(…slot five…, class_id)` — i.e. `class_id` last. That silently changes every primary key
and orphans every stored row in every existing `driver_fingerprint.db`, with no test failure unless a
characterization test pins the exact string.

The g1 imperative said "byte-identical" but did not name the trap, and a generic warning is not what stops a
plausible-looking refactor. **Applied:** g1's imperative now states the current order explicitly, flags
`class_id`-at-position-4, and requires the characterization test to assert a hard-coded expected `cell_key`
string rather than recomputing it from the same constant.

### F2 (moderate) — "get_fingerprint must now raise" mis-locates the refusal

Once the signature takes a `SlotAddress`, a malformed address can no longer *reach* `get_fingerprint` — it
fails at construction. The g2 wording ("get_fingerprint and row_count must now raise for `driver=''`…") invites
an implementer to add a redundant re-validation inside the store, which would re-create the two-places-to-forget
problem candidate B exists to remove. **Applied:** g2's imperative now says the refusal happens at
`SlotAddress` construction, the store must **not** re-validate, and the acceptance test asserts (a)
construction raises and (b) the store method is unreachable with a bad address by type.

### F3 (moderate) — H3's two halves are coupled, and the plan presented them as independent

After the re-anchoring, the 675 script writes to `_REPO_ROOT/.agent-work/666-driver-fingerprint/artifacts/`
**always** — where before it wrote relative to whatever cwd it ran from. So anchoring *guarantees* the stray
lands inside the tracked tree. The narrow `.gitignore` rule is therefore not belt-and-braces; it is **required
by** the anchoring change, and shipping the anchoring without the ignore would make H3 strictly worse.
**Applied:** g3's imperative now states the coupling and forbids landing one without the other.

### F4 (severe, environmental) — every command postcondition assumes a `py` that has pytest, and that is unverified

`py -m pytest` from this session's shell fails: `No module named pytest` — the shell's `py` resolves to a codex
runtime, not the pythoncore-3.14-64 interpreter the repo's tests need (the same runtime already known to lack
scipy). If the execute step's shell resolves `py` the same way, **every** `command` postcondition in this plan
fails on `advance` for an environmental reason, and the run burns a waiver per gate diagnosing a red that is
not about the code. Attempts to resolve the PowerShell `py` empirically were blocked by the harness permission
layer, so this stays an **unverified assumption** — which is precisely what a plan must not silently trust.
This is `lesson:ci-gate-selftest-in-ci-environment` in its local form: prove the gate works *in the executing
environment*, not just in principle. **Applied:** `e0-context` gains a toolchain self-test postcondition
(`py -m pytest --version`) plus an explicit instruction — if it fails, pin the absolute
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` in every command via the engine's `amend`
verb **before** opening g1, never by hand-editing the JSON.

### F5 (minor) — the embedded `py -c` cross-region check is quoting-fragile

`g2-store-integrate.c4` carries a one-liner with nested quotes through JSON. It is correct as written but is
the kind of thing that breaks silently on a shell change and then reads as a real violation. **Applied:**
folded into F4's `e0-context` dry-run — every command postcondition in the plan is executed once at
`e0-context` before any gate opens, so a quoting or interpreter fault surfaces at the cheapest possible moment.

## Findings — ACCEPTED as residual risk, recorded not fixed

### F6 — "no numeric change" is only as strong as the existing fit tests

`g2-store-integrate.c1` proves the suite passes; it does not independently prove no fit value moved. The
guarantee rests on `test_fit.py` / `test_bounded_validation.py` actually asserting values, plus g2-review's
requirement to diff the guard assertions for modification. Adding a golden-value snapshot gate would be new
scope for a refactor that touches no arithmetic. **Accepted**, with the mitigation named in the g2 review
imperative (diff the assertions, don't take the implementer's word — `lesson:verify-subagent-self-report`).

### F7 — `c4`'s over-reach guard is pinned to a dated archive path

`git ls-files --error-unmatch .agent-work/archive/2026-07-26-666-driver-fingerprint/...` breaks if that
directory is ever renamed. **Accepted**: it is a one-run check whose whole point is to pin *those specific*
committed files, and a glob would weaken it.

## Findings — REJECTED

### R1 — "split g2; ~48 call sites is too big for one gate"

Rejected. Every alternative split leaves the suite red at a gate boundary, which doctrine names a plan smell
costing a human waiver per gate plus a diagnostic detour in every review. The mitigation is not a smaller gate
but a fully enumerated site list (which g2's imperative carries) plus the fact that every site is positional,
so a miss is a collect-time `TypeError`.

### R2 — "make the delimiter and known-measure set injectable so validation is easier to test"

Rejected on the record; this is `PLAN_ALTERNATIVES` candidate C. Those are frozen-by-design constants, and
making them configurable invites the vocabulary drift the store's third refusal arm exists to prevent. Written
down here so the same suggestion in review has a standing answer.

### R3 — "widen H2 to the other 50 non-compliant scripts while you're in there"

Rejected. Different defect class scope (repo-wide convention), wants a lint/CI check rather than 51 hand edits,
and widening would put the fingerprint change and a repo-wide sweep in one un-revertable diff. Filed as
`tc2-698`.

## Triage of these findings

All findings were disposed by the Commander under the engagement dispatch's standing authority (no human
reachable): **F1–F5 applied to `execute.json` before freeze; F6–F7 accepted as recorded residual risk; R1–R3
rejected with reasons.** No finding was left undisposed.

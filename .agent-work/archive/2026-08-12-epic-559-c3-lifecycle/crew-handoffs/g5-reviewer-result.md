# Reviewer Result — g5: the two carried findings

**Verdict: APPROVE**

Survey driven end to end through `scripts/checklist_engine.py` at
`.agent-work/epic-559/c3-lifecycle/g5-review/review.json` (session
`constellation/epic-559/c3-lifecycle/g5/reviewer/attempt-1`): r0–r6 all recorded `pass`, consolidated
APPROVE, `current` reports `DONE: no open items`. Fowler pass recorded to
`.agent-work/epic-559/c3-lifecycle/FOWLER_PASS.json`, `verify_fowler_pass.py` exits 0.

## What was reviewed

The change is **uncommitted** — `HEAD` is still `b88f13a4` (the g4 integration commit), so the diff
under review is the working tree against `HEAD`, not `b88f13a4..HEAD` (which is empty). `git status
--short` confirms only `scripts/generate_spine.py`, `tests/test_generate_spine.py`,
`.agent-work/epic-559/c2-generate-the-spine/DESIGN_NOTE.md`, and a regenerated `map/INDEX.md` are
modified in tracked source.

## Findings

None blocking. All seven "what to verify" items and every constraint reproduced clean. One
non-blocking triage candidate.

1. **Type guard is about TYPE, not value — confirmed.** Ran all six cases directly against
   `gs.spec_shape_faults` / `gs.compile_condition` via the test module's own `_spec`/`_gate`/`_pytest_cond`
   helpers (not the report's paste — independently constructed):

   ```
   str "false"  refused=True  codes=['spec-not-yet-written-not-bool']
   str "true"   refused=True  codes=['spec-not-yet-written-not-bool']
   int 1        refused=True  codes=['spec-not-yet-written-not-bool']
   bool true    refused=False codes=[]
   bool false   refused=False codes=[]
   omitted      refused=False codes=[]

   true compiles check: None
   false compiles check kind: command
   omitted compiles check kind: command
   ```

   `true` still compiles to `check: null` (and the code path that emits `undecidable-pytest-not-yet-written`
   is unchanged); `false`/omitted still take the strict `command`-check path. **Confirmed.**

2. **Fault message truthfulness — confirmed.** `compile_condition` (`scripts/generate_spine.py:523`):
   `elif kind == "pytest" and cond.get("not_yet_written"): ... check = None`. A truthy non-bool
   (`cond.get("not_yet_written")` on a string `"false"` is `True` in Python) hits this branch and sets
   `check = None` exactly as the fault message at line 224–231 claims. The message does not misdescribe
   the defect. **Confirmed.**

3. **§7 fault vocabulary — load-bearing item, spent the most budget here.**

   Mechanical enumeration (parsed every `Fault(` call site in `scripts/generate_spine.py`, resolved the
   first string-literal argument regardless of line wrapping — 33 call sites, all resolved to a literal,
   none dynamically constructed):

   **23 total fault codes: 17 unique `spec-*`, 6 unique `probe-*`.**

   ```
   spec-*: spec-all-qualitative-postconditions, spec-artifact-missing-match, spec-config-ref-not-json,
   spec-dispatch-missing-field, spec-dispatch-undeclared, spec-dispatch-unresolved-parent,
   spec-duplicate-condition-id, spec-duplicate-gate-id, spec-empty-because,
   spec-gated-missing-postconditions, spec-malformed-claim, spec-missing-field, spec-non-integer-field,
   spec-not-yet-written-not-bool, spec-reserved-id, spec-shipped-session-specific-parent,
   spec-unknown-check-kind  (17)

   probe-*: probe-population-count-mismatch, probe-pytest-below-min-collect,
   probe-pytest-malformed-selector, probe-script-not-found, probe-script-positional-path-not-found,
   probe-script-unknown-flag  (6)
   ```

   `DESIGN_NOTE.md` §7 lists exactly the same 17 `spec-*` codes, item-for-item, with an accurate 16/1
   split (16 reachable through `spec_shape_faults()`; the 17th, `spec-shipped-session-specific-parent`,
   deliberately unwired). **Diffed the two sets: identical, zero missing, zero extra.**

   Re the Commander's calibration (17 `spec-*` in source vs 18 `spec-*` strings in the note): ran the
   note's own grep, `grep -oE '`?spec-[a-z0-9-]+`?' DESIGN_NOTE.md | sort -u`, and it returns 18 —
   the 18th is the bare substring `spec-shape` (from "Spec-shape faults", "spec_shape_faults" in prose),
   **not a fault code**. This is exactly the false-positive the handoff warned the raw grep would produce.
   The two sets **do not** genuinely disagree — 17 == 17, confirmed by diff, not by trusting either count.

   §7's title is "**Spec-shape faults** — refused before any probe," and its own text never claims to be
   "every fault code the generator can raise" — it explicitly scopes itself to the 17 `spec-*` literals
   and states that count. The 6 `probe-*` codes are a structurally distinct class (probe-time, not
   spec-shape-time) and are documented narratively per-kind in §4 instead (one, `probe-script-positional
   -path-not-found`, is named literally there; the other five are described by behavior, not by code
   string). This is a coherent, disclosed scope boundary, not an omission — filed as a non-blocking
   triage candidate below rather than a defect.

4. **§4 and §10 — confirmed accurate.** §4's `pytest` paragraph now explicitly states `not_yet_written`
   compiles to `check: null` and explains why (a close-time truth, not a generation-time one), matching
   `compile_condition` exactly. §10's four-defect table is **untouched** in this diff (`git diff` shows
   no hunk touching lines 459–481) — correctly so: the table is scoped to the four original defects
   (unquoted shell split / probe-that-can-only-fail / wrong-invocation typo / population double-wrong
   filter), and g4's `spec-dispatch-*` faults are a different concern outside that table's declared
   scope. No claim in either section contradicts the shipped code.

5. **No needless churn.** The §7 rewrite replaced an ambiguous "that last one" back-reference spanning
   two fault explanations that named different codes with explicit names — a real ambiguity fix, not
   cosmetic churn — and the note discloses exactly what changed and why in a new "Reconciled at g5"
   paragraph (omitted `spec-non-integer-field` and `spec-artifact-missing-match`, all three g4 dispatch
   codes). Confirmed against `git diff` — every changed paragraph in §4 and §7 is either new content
   (documenting behavior the note previously said nothing about) or a targeted fix to a stated defect;
   nothing correct was rewritten for its own sake.

6. **`generate_spine.py`'s missing `newline="\n"` — fixed.** The module's sole `write_text` call site
   (now line 1056, shifted by the new guard) reads
   `Path(args.out).write_text(json.dumps(compiled, indent=2) + "\n", encoding="utf-8", newline="\n")`.
   Confirmed no other `write_text`/`open(..., "w")` site exists in the file needing the same fix.

7. **Sweep unchanged.** `grep -rn not_yet_written specs/` returns nothing (neither shipped spec uses the
   field). `python scripts/validate_spine.py --sweep --root . | grep -cE '^\s+\['` → **23**, reproduced.

## Constraints

`git status --short` shows only the allowed-scope files modified in tracked source
(`scripts/generate_spine.py`, `tests/test_generate_spine.py`, `DESIGN_NOTE.md`, `map/INDEX.md`).
`checklist_engine.py`, `validate_spine.py`, `spine_lifecycle.py`, `mcp_spine_server.py`, `.mcp.json`,
`settings.json`, `docs/agents/*`, `skills/**` all untouched. `HEAD` unchanged (`b88f13a4`) — no commit,
no push to `main`.

`validate_spine.py`'s missing `not_yet_written` concept (LIFECYCLE_CONTRACT.md §7b) is correctly
**not** treated as a g5 defect — confirmed it was left alone, as instructed.

## Evidence reproduced (not accepted on the report's say-so)

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
2932 passed, 3 skipped, 1121 subtests passed in 117.91s (0:01:57)

$ python scripts/validate_spine.py --sweep --root . | grep -cE '^\s+\['
23
```

Both match the claimed post-g5 numbers exactly.

## Triage candidate (out of g5 scope, not a defect)

`DESIGN_NOTE.md` has no formal enumerated list of the 6 `probe-*` fault codes anywhere, unlike §7's
now-complete `spec-*` list. §7's own title scopes it to spec-shape faults by design, so this is not a
g5 defect, but a future note pass could add a parallel probe-fault enumeration (mirroring §7's format)
for the same completeness §7 now has. Flagged in the survey (`tc1`).

## Most likely way this gate produces a green run that is wrong

If a future edit adds a new `spec-*` fault code and updates `spec_shape_faults()` but the author forgets
to re-run §7's own enumeration command before editing the note by hand, the note would silently
under-list again — exactly the failure this wave fixed, and exactly the failure class the note's own
"Enumerated mechanically... not from memory" framing exists to prevent. Nothing in this diff makes that
self-correcting; §7 stays correct only as long as whoever next touches it actually re-runs the grep
instead of hand-editing the list. There is no test pinning §7's code list against the source the way
`g1-integrate.c3` pins §4's `CHECK_KINDS` tuple.

## Workflow Feedback

- The handoff's inherited `SPINE_FILE`/`SPINE_SESSION` env pointed at the Commander's own outer
  `execute.json` spine (`constellation/epic-559/c3-lifecycle/execute/commander`), not anything scoped to
  this g5 reviewer dispatch — `spine_status` returned the Commander's `execute` gate instructions, not a
  g5 review checklist. This is the same friction g4's and g5's implementer results already recorded
  independently; I hit it too and built my own survey at `.agent-work/epic-559/c3-lifecycle/g5-review/
  review.json` per the reviewer skill's "nothing bound" branch, matching the g1–g4 review precedent.
  Third confirmation of the same gap — worth fixing at the `run_crew.py`/MCP-server-launch level so
  future crews don't have to rediscover it per gate.
- The handoff's calibration note (17 vs 18, "may catch prose") was exactly right and made item 3 fast to
  resolve correctly instead of chasing a false discrepancy — naming the specific trap in advance is what
  made "do the comparison properly" tractable within budget. More handoffs should pre-name a known
  false-positive shape like this when the author already knows one exists.
- No other gaps; every close criterion and constraint in the handoff mapped cleanly onto a concrete,
  reproducible check.

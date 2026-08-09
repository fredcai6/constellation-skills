# Review Result

## Assigned Gate
`g7` remediation recheck (issue #456). Attempt 2: verify the fix at `ffa959c5`, not a full re-review.

## Result
`APPROVE`

## Both original blockers: fixed, independently confirmed

**Retire -> alias.** `git diff 0d1af801 ffa959c5` confirms: `TAG_START` recognizes all five words
again; `TAG_KIND_ALIAS = {"Assumption": "Rationale", "Constraint": "Rationale"}` normalizes at the
one emission site in `tag_check`, before `emit()` runs. `tag_lines` has zero diff — the cull test's
own evidence stands. `cull-verdict.json` was genuinely rewritten (not just reworded): a new
`kind_normalization` field, and the `consequence` field now correctly states a formerly-retired
word "still extracts and renders... normalized," replacing the old "will not extract or render"
claim that would otherwise have been worse than the original defect.

**The staleness join actually watches tags now.** The Commander's own finding (deeper than my
original score) is confirmed: `run()`'s old diff only ever read `p == "anchored"`; the original
join fixture carried both an anchor and a tag, so the flag fired off the untouched anchor, and the
real corpus (zero anchors) would never have been watched. Fixed: tags persist their own `span_hash`
(hashing the enclosing entity, reusing `span_hash` unchanged) and get their own `(owning symbol,
tag text)`-keyed diff in `run()`, landing in the same `stale_tags` report field and `ADVISORY`
print convention `g6` established — confirmed by reading `render.py`'s diff directly (one new
interception branch appending to the SAME list, no second channel). `g6`'s anchor-path code is
byte-identical: verified by listing all 14 hunk headers in the `extract.py` diff and confirming
none falls inside `span_hash`'s or `anchor()`'s body, not by trusting the RESULT doc's claim.
Advisory-only severity preserved (`return 1 if duplicates else 0` untouched by `stale_tags`).

**Timings finding: accepted as overruled.** Team-lead's correction is right — the constraint
governs `render_report.json`, the artifact the determinism check diffs, not a human-facing result
document. Not re-litigated.

Closing selectors reran directly on the committed tree: `-k 'comment_tags'` 24 passed / 13
subtests / exit 0; `-k 'stale_tag'` 19 passed / 13 subtests / exit 0 — exact match.

## Adversarial checks (A-E)

**A — a third disable point.** Predicted, then confirmed live: disabling persistence into
`self.tag_hashes` (a different code location from both prior attacks) leaves `new_tag_hashes`
permanently empty, collapsing to the same downstream failure. Exactly the predicted 3 tests failed,
16 passed, no survivor. Reverted, clean. No new gap at this point.

**B — is `(owning symbol, tag text)` a sound identity key?** Sound and self-consistent with the
gate's own stated rule. Two edges behave exactly as intended (duplicate tags on one symbol collapse
harmlessly; a moved tag starts fresh history, matching bootstrap behavior). One real, confirmed-live
asymmetry: **a symbol rename defeats tag staleness** — renamed a function and changed its body in
the same commit, tag/anchor comments unchanged: `stale-anchor` fired (slug-keyed, survives rename),
`stale-tag` did not (symbol-keyed, does not survive rename). Necessary consequence of the stated
design, not sloppy work, but a real, previously-unnamed asymmetry — filed as `tc3`. Whitespace/
punctuation drift in the tag's own text behaves exactly as the gate's stated rule specifies
(confirmed live), not a gap.

**C — does the zero-anchor precondition actually fail loudly?** Confirmed live: injected an anchor
into a scratch copy of the tag-only fixture; the affected test failed exactly at its own
precondition assertion with the intended message. Reverted, clean.

**D — the widened pin test: one real, non-blocking gap.** Confirmed live with a standalone AST
probe: `getattr(obj, t['kind'], default)` and `k = t['kind']; LABEL[k]` (a locally-renamed variable
before a lookup) both still evade `_kind_dispatch_nodes` — the `Call` branch only matches `.get()`
method calls, not builtin `getattr()`; the `Subscript` branch only recognizes a literal `Name` with
`id == "kind"`. Both were named as candidate evasions in the ORIGINAL handoff and neither is closed
by fix 3. Not blocking — the shipped `tag_lines` has neither shape — but the pin's docstring claim
overstates what it verifiably closes. Filed as `tc4`.

**E — the alias round-trip end to end: confirmed clean.** Built a fresh `# Constraint:` fixture,
ran a full `build`, and inspected the raw bytes of every artifact directly (not the tests'
assertions): the raw `statements.jsonl` tag row already carries `"o": "Rationale"` with zero
occurrences of the literal string "Constraint" anywhere in the file; the rendered page, and both
`extract_report.json`/`render_report.json`, likewise carry zero occurrences. Normalization happens
exactly once, at the emission call site — nothing downstream can see or leak the pre-alias kind.

## Blockers
None.

## Out-of-scope observations
- `tc3`: tag staleness does not survive a symbol rename (unlike anchor staleness) — a real,
  accepted-direction-of-error asymmetry worth a named doc line.
- `tc4`: the widened AST dispatch-on-kind pin test still misses `getattr()` dispatch and a
  locally-renamed-variable lookup — no present exploit, but the docstring claim should be narrowed
  or the check further widened.
- `tc1`/`tc2` (from the original review) remain open, unchanged by this pass.

## Workflow Feedback

- **Handoff gaps:** none — the five adversarial checks (A-E) were concrete and independently
  runnable exactly as specified.
- **Context rediscovered:** none — the diff was small and every claim in the remediation RESULT
  doc was directly checkable against it.
- **Instructions improvised around:** none.
- **What would have made this easier:** none.

## Return status
`complete`

# Cold plan critic — findings and dispositions

One critic, not a panel. Panel-vs-single surfaced at plan approval: the change lands in one function pair
and one test class, and the load-bearing question is narrow. Recorded rather than chosen silently.

The critic read the mission frame, `execute.json` and `PLAN_ALTERNATIVES.md` plus the code they target,
with no authoring context. It independently reproduced the inventory (8 populated gates, all dicts) and
independently established that no existing golden breaks, because the shared `gate()` fixture helper sets
`directives: None`. Five of its seven findings were real and changed the plan.

Dispositions are the Commander's, citing `LAUNCH_ORDER:Inherited Latitude` (test structure and where the
completeness property lives are explicitly mine).

## 1 — BLOCKING — the property loops over a hand-built fixture, not the canonical field set. ACCEPTED.

> "MISSION_FRAME 'Structural Anchors': 'The Task field table … the enumeration the property loops over.'
> It isn't. The loop is `for field, value in t.items()` over a hand-built fixture. A future Task field
> added to the schema and to real gates, but not added to this fixture, is absent from `t.items()`,
> absent from the ledger's expected set, and passes green — the identical forgetting failure the plan
> exists to close."

This is the most important finding in the pass and it is correct. My plan would have shipped a property
that closes the class only for fields someone remembered to put in the fixture. **Fix folded into
g2-implement:** the fixture's key set must be asserted a superset of the engine's own canonical Task
builder (`_build_amend_task`, `checklist_engine.py:2040`, mirrored by `append()` at `:2252`), so a field
added to the engine's Task shape and forgotten in the fixture fails mechanically.

**Stated limit, because a null with no scope is unfinished:** this closes the hole for fields the *engine*
introduces. A field introduced only by a template and never by either builder still needs a human to add
it to the fixture. The property must say so in its own docstring rather than imply coverage it lacks.

## 2 — BLOCKING — `g3-schema` c2 is satisfiable by a mention. ACCEPTED.

> "`grep -n 'directives' … | grep -q 'nested'` passes if *any* line containing 'directives' also
> contains 'nested'. … Adding 'the `directives` block renders its nested contract fields' to the
> Rendering prose satisfies c2 while table line 123 still reads `` | `directives` | `[string]` \| null ``
> — the exact drift c2's statement claims to verify."

Correct, and it is the check-that-cannot-fail shape in my own gate plan. **Fix:** c2 now extracts the
table row by fixed string and asserts *that row* carries `dict`, and separately asserts the old type
phrase is gone from the file.

## 3 — SERIOUS — `g3-schema` c1's negation cannot discriminate. ACCEPTED.

> "`! grep -n 'Known gap, not yet closed'` passes on any rewording, and passes if the Rendering section
> is deleted wholesale. Healthy and defective worlds both green."

**Fix:** c1 is now a conjunction — the old phrase absent **and** an exact positive sentence present naming
`directives` as rendered on the same omit-when-empty terms. Deleting the section now fails.

## 4 — SERIOUS — the RED-first requirement has no check behind it. ACCEPTED.

> "g1-implement c1 and g2-implement c1 both check `{"kind":"artifact","evidence_type":"implementer-result"}`
> with no `match`. Any implementer-result artifact satisfies both. A golden written after the fact …
> passes c1 identically."

Correct. **Fix:** `g1-integrate` gains a third postcondition requiring an attached `command-output`
artifact matching `proof: red-without-renderer` — the Commander re-runs the mutation in its own hands and
records the real output, per verify-claimed-side-effects. The durable machine proof remains the in-suite
negative self-test at g2; this postcondition stops the run from *asserting* a red it never saw.

## 5 — SERIOUS — a dict-only renderer collides with the fixture g2 must un-exclude. ACCEPTED.

> "Test line 4038 is `t["directives"] = ["DIRECTIVE_UNIQUE_TEXT"]` — a list of strings … a
> `_render_directive_lines()` written for `key -> nested dict` emits nothing and g2 goes red for a reason
> the plan never names. … Meanwhile g3 narrows the doc to dict-only, so a list-shaped `directives`
> silently renders nothing again: the original defect, reinstated."

A genuine collision my plan missed. **Fix:** the renderer handles **both** shapes — a flat list of
strings and a key-to-nested-dict — exactly as the anchors normalizer already handles anchors' three
corpus shapes; the fixture keeps covering both; and the corrected schema row names both.

## 6 — MINOR — red-proof R1 is redundant with the in-suite negative self-test. ACCEPTED.

R1 and the automated self-test occupy the same world. R1 dropped; R2 and R4 kept, and the reviewer
reproduces them independently.

## 7 — MINOR — fold `g3` away. DECLINED, with reason.

> "g3's only non-doc content is c3, the plan's *only* broad-suite run — self-authored, self-satisfied,
> unreviewed, and carrying a human override."

The premise is half right and the conclusion does not follow. c3 is an engine `command` postcondition:
the engine executes it on `advance` and refuses on non-zero. It cannot be attested, so "self-satisfied"
does not apply — only a recorded waiver could bypass it, and that is the audit trail working. The doc
gate stays separate because commander doctrine specifically wants a doc-only gate to carry a
**pre-authored invariant chain** rather than let an executor invent a proxy — which is exactly the defect
findings 2 and 3 caught, and the fix is to strengthen those invariants, not to delete the gate that
carries them.

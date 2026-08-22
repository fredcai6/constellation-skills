# Plan Alternatives — #371 match-shape

## The one thing being designed twice
The `match` shape for "any of these payload values satisfies me," and the resulting comparator
change to `scripts/checklist_engine.py`'s two `==`-comparison sites.

## Count and panel — a surfaced choice
**Single pair (N=2), not a panel.** This is a fairly-easy call, not an architecture-touching one:
the load-bearing interface in play (the `match` value grammar) is small, entirely local to one
file pair, and the pre-ruling itself frames it as a two-shape choice (bare list vs. an operator
dict) rather than an open design space. Per the launch order's own settle clause
(`decision:match-shape-is-yours-to-choose`), the deciding experiment is a corpus check, which a
pair resolves as well as a panel would.

**Dispatch note (untaken road, mechanical, not a design choice):** the design-it-twice contract
calls for N agents in parallel; this run has no Task-tool dispatch available to it (its tool
surface is Bash/Read/Write/Edit/WebFetch/WebSearch/Skill only — see Workflow Feedback in
`RESULT.md`), so both candidates were authored serially, in-context, by the same agent, under two
genuinely distinct named constraints, rather than by two independent processes. This weakens the
"independent perspective" property design-it-twice exists for; noted, not hidden.

## The constraints (one per candidate, each distinct and named)
- **smallest-diff** — `plan-candidate-smallest-diff.md` — bare list means "any of these";
  minimize new syntax and comparator delta.
- **most-testable** — `plan-candidate-most-testable.md` — explicit `{"any_of": [...]}` operator;
  favor legible-from-JSON intent and room to add a second operator later.

## Compared on
| Axis | smallest-diff (bare list) | most-testable (`any_of`) |
|---|---|---|
| Depth | High — the shape #371 says an author naturally reaches for now means what it looks like it means; zero new vocabulary. | Lower for the common case — the natural bare-list shape is *refused*, not accepted; the author must learn a new key for a payoff (future operators) nothing in this mission requests. |
| Locality | 2 sites, one `isinstance(v, list)` branch each. | 2 sites plus a new shared `_match_one` helper and a `dict`-shape-detection branch with more edge cases (extra keys, `any_of` beside other keys). |
| Seam placement | Same existing seam, no new function. | Same existing seam, one new internal function. |
| Testability | One scalar test + one list-membership test per site, plus the standing red-proof. | Marginally higher raw test count (shape-detection is separately testable; two `validate_spine` negative cases instead of one) — but tests more of its own added complexity, not more of the actual requirement. |

**Corpus check (the pre-ruling's named settle experiment), run against both:**
`grep -rhoE '"match": ?\{[^}]*\}' .agent-work --include=*.json` (the ~90 real driven spines/plans
under this worktree, plus `skills/*/templates/*.json`) → every match value found is a bare scalar
(`"complete"`, `"APPROVE"`, and one multi-key all-scalar dict). **Zero** list-valued or
dict-valued match values exist anywhere shipped or driven. Payload-field census
(`grep -rhoE '"payload":\{[^{}]*\}' .agent-work --include=*.json | grep '\['`) → **zero** hits: no
evidence payload field is ever list-valued either. So neither shape collides with anything real
today; the corpus check does not separate the candidates on backward-compatibility (both pass
cleanly) — it separates them on **forward** collision risk (does a future author's legitimate use
accidentally trip the new interpretation), which is exactly what `decision:match-shape-is-yours-
to-choose`'s settle clause asks: "the one that cannot be confused with a legitimate scalar
list-valued payload wins." Since no evidence payload is ever list-valued in this corpus and the
match grammar governs `match`, not raw payload shape, **both candidates are equally safe on that
specific axis** — the corpus check returns a tie there. What breaks the tie is Depth: bare list is
the shape the issue itself documents an author naturally writing, so choosing it fixes the exact
felt wedge with zero new authoring convention, while `any_of` requires teaching a convention to
avoid a wedge that bare list simply resolves.

## Framing block (presented ahead of authoring, for the record)
- **Constraints in play:** smallest-diff (minimize new syntax), most-testable (explicit,
  extensible operator form) — chosen because the pre-ruling frames the choice as exactly this
  binary.
- **Dependencies:** both candidates touch only `scripts/checklist_engine.py` (2 sites),
  `scripts/validate_spine.py` (1 new fault family), and `docs/CHECKLIST_SCHEMA.md` (1 sentence).
  Held fixed for both: no existing scalar `match` may change meaning; the widening ships live, the
  new refusal ships report-only with a named promotion trigger (both pre-ruled, not reopened
  here).
- **Illustrative sketch — not a proposal:** `isinstance(v, list)` dispatch inline at both sites.
  Offered only to prime parallel thinking; carries zero weight at convergence.

## Output — recommendation
**smallest-diff (bare list).** It wins on Depth (fixes the wedge exactly as #371 describes an
author naturally hitting it, no new syntax), ties on backward-compat (both candidates are corpus-
clean) and on forward-collision risk (neither shape exists anywhere in the corpus today, so
neither is "less confusable" than the other by the corpus check alone), and is strictly smaller in
Locality (no new shared helper, no shape-detection edge cases around extra dict keys). The
`any_of` candidate's own Risk section names the real cost of the alternative choice directly: it
would foreclose bare-list semantics later behind a taught, adopted convention. Choosing bare list
now keeps that door open in the opposite direction — nothing stops a later `any_of`/`not_in`
operator family from being added beside a plain list if a real need for a second operator
surfaces; today none has.

`validate_spine.py`'s new fault (report-only) targets what actually stays wrong under bare-list
semantics: a **malformed** list (empty, or containing a non-scalar element) — not the bare list
shape itself, which is now the correct spelling.

## Untaken-road record
- No third candidate authored (e.g., a wrapper `{"one_of": [...]}` distinguishable from a literal
  list-shaped payload value by key presence rather than by value type) — judged not worth a third
  parallel candidate: the corpus census already shows zero list-shaped payload values exist, so
  the disambiguation problem a third candidate would solve does not arise in practice, and adding
  one would cost more Locality for a case that has never occurred.
- Parallel independent-agent dispatch (design-it-twice's default execution mode) not available —
  see "Dispatch note" above; both candidates authored serially by this run's own agent instead.

## Panel-vs-single record
Single pair (N=2), not a panel — restated: fairly-easy call, small load-bearing surface, binary
shape choice already framed by the pre-ruling, corpus-measurable settle experiment. Surfaced here
for the approval checkpoint; the Admiral/human may overturn the scaling call.

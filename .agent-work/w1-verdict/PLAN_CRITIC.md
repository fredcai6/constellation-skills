# Plan Critic — #371 match-shape mechanism

Cold read of `PLAN_ALTERNATIVES.md` + `MISSION_FRAME.md` only (plus the actual source at
`scripts/checklist_engine.py`/`scripts/validate_spine.py`, since no candidate is trustworthy
without checking it against the real file). No dispatch available (see Workflow Feedback /
`PLAN_ALTERNATIVES.md` dispatch note) — this pass is self-run, adversarial-in-intent, not
adversarial-in-process; disposition is stated for each finding rather than assumed accepted.

## Finding 1 (real, adopted): a non-`dict` `match` crashes the engine today, uncaught
`want.items()` at both comparison sites assumes `want` (`chk.get("match", {})`) is a `dict`. If a
spine author writes `"match": ["APPROVE", "BLOCK"]` at the top level (a plausible typo reaching
for exactly the bare-list semantics this mission adds, one level too shallow), `list.items()`
raises `AttributeError`, uncaught, at both `_check_condition` and `attest`. Verified live:
```
>>> want = ['a','b']; all(True for k,v in want.items())
AttributeError: 'list' object has no attribute 'items'
```
This is a **more severe** instance of the same defect class the mission names ("a mistyped match
shape impossible to write silently") — a crash, not a silent wedge, but still an authoring mistake
the engine should refuse cleanly rather than blow up on. **Disposition: fix-now**, in-latitude
(`Fix-now triage: a bounded defect you find in-flight gets fixed here rather than filed`), bounded
to the same two sites already in scope: guard `isinstance(want, dict)` before the per-key loop at
both sites, refusing cleanly (`EngineError` at `attest`, `satisfied=False` at `_check_condition`)
instead of crashing. `validate_spine.py` also gets a **shape**-family fault (blocking, like its
siblings) for `match` present-but-not-`dict` — shape faults are always blocking in this module
(see `docs/agents`); this is not the report-only fault the pre-ruling scopes (that one is about a
**valid dict** whose **value** is a malformed list, addressed in Finding 2).

## Finding 2 (real, adopted): shared comparator function, not inlined duplication
Both candidates inline their comparison logic per-site. A one-line pure helper
(`have == want` unless `want` is a `list`, then `have in want`) used at both sites is strictly
better on Locality/Testability than either candidate's inline duplication, with zero added
dispatch complexity (unlike the `any_of` candidate's shape-detection branch). **Disposition:
fold into the smallest-diff candidate as an implementation refinement** — this does not reopen the
shape choice (bare list still wins per `PLAN_ALTERNATIVES.md`'s Output section), it only names how
the winning shape's comparator should be factored.

## Finding 3 (real, NOT adopted — floated instead): the guard's reach is narrower than "impossible
to write silently" implies
`validate_spine.validate()` is called from exactly two places: `generate_spine.py` (compiling
`specs/<role>.spine.toml`) and `scripts/spine_lifecycle.py` (`_compile_spine`/`open_work`). Neither
is in the path a Commander actually uses to author `execute.json` at its own `plan` step — that
file is hand-authored JSON, filled from `EXECUTE_PLAN.template.json`, and nothing calls
`validate_spine.py` against it before or during the run that authors it. (This very mission's own
`execute.json`, authored two sections below, goes unvalidated by the guard this mission adds,
except by explicit `--sweep`/direct invocation, which nothing requires.) So the new guard closes
the wedge for the shipped-template and generator paths, but a hand-authored gate plan — the most
common real authoring path — is not "impossible to write silently" past; it is merely "possible to
check, if you remember to." **Disposition: floated, not fixed.** Wiring `validate_spine` into
execute.json authoring is new check-wiring, which the launch order's fence reserves for the
sibling `w1-wiring` commander this wave ("do not create or wire a new `scripts/verify_*.py` or
`scripts/check_*.py` script... float it to the Admiral and it will be sequenced"); this is the
same shape of gap that census is measuring (a built check not wired into every path that would
benefit from it), so it is named here for the Admiral to carry, not acted on. See `RESULT.md`
Triage Candidates.

## Finding 4 (real, adopted): promotion trigger needs a genuinely actionable measurement, not a
vague "later"
A report-only fault with no concrete trigger tends to stay report-only forever by default (nobody
owns re-checking it). **Disposition: name it precisely in the PR** — promote
`falsifiable-artifact-match-malformed-list` from report-only to blocking when **both** hold: (a) a
`validate_spine.py --sweep` run across the shipped corpus reports zero occurrences, and (b) the
Admiral/human ratifies the widening-live/refusal-report-only split at the wave-2 checkpoint this
pre-ruling already names (`decision:widening-ships-live-refusal-ships-report-only`'s own `settle:`
line) — at that point flip the fault's code out of `REPORT_ONLY_FAULT_CODES`, a one-line change,
named here so it is discoverable rather than requiring a re-derivation of "what would make this
safe to promote."

## Finding 5 (real, adopted): scalar-element definition for "malformed list" needs to be explicit,
not implied
"Malformed" must be defined precisely or the report-only fault either over-fires (flagging a
legitimate single-element list, which is functionally identical to a scalar match and not a bug)
or under-fires (missing a list containing a nested dict/list, which — like the non-dict-`match`
case in Finding 1 — cannot ever equal a real evidence-payload scalar and is definitely a mistake).
**Disposition: adopted** — malformed means empty (`[]`, vacuously unsatisfiable in the wrong
direction, the mirror of `_fault_artifact_no_match`'s vacuously-satisfiable problem) OR containing
any element that is not a JSON scalar (`str`/`int`/`float`/`bool`/`None`). A single-element list is
**not** flagged — it is redundant, not wrong.

## Untaken findings
- Did not re-litigate the bare-list-vs-`any_of` choice itself — `PLAN_ALTERNATIVES.md`'s corpus
  evidence and Depth argument are sound on their own terms and this critic pass surfaces no new
  collision the corpus census missed.
- Did not propose a third `match` shape (e.g. `{"one_of": [...]}` as a middle ground) — no finding
  above depends on it, and `PLAN_ALTERNATIVES.md`'s own untaken-road entry already covers why a
  third shape adds Locality cost for a disambiguation problem that does not occur in the corpus.

## Triage (human/Admiral, per Findings 3–4 above)
Both dispositioned inline; nothing here is silently deferred without a stated reason.

# Plan candidate: most-testable (explicit `{"any_of": [...]}` operator)

## The one thing being designed twice
Same as the sibling candidate: the `match` shape for "any of these," and the two comparator sites.

## Constraint
**most-testable / explicit** — favor a shape whose intent is legible from the JSON alone and that
leaves room to add another operator later without a second shape-detection heuristic.

## Design
A `match` value of shape `{"any_of": [...]}` is a new operator form; every other value keeps
today's scalar `==`. Comparator:
```python
def _match_one(want_v, have_v):
    if isinstance(want_v, dict) and set(want_v) == {"any_of"}:
        return have_v in want_v["any_of"]
    return have_v == want_v
```
applied per-key at both sites. `"match": {"verdict": ["APPROVE", "APPROVE-WITH-FOLLOWUPS"]}` (the
literal shape #371 shows an author reaching for) is **still wrong** under this design — it is a
bare list, not `{"any_of": [...]}}` — so `validate_spine.py` must refuse *that* shape specifically
(not just malformed operator dicts), converting the wedge into a loud authoring-time rejection
rather than a silent unsatisfiable condition, and the author must learn the new key.

## Gates (most-testable shape)
- **g1** (crew): implement `_match_one` shared by both comparator sites (a small extraction that
  wasn't in the smallest-diff candidate — today the two sites each inline the comparison rather
  than share a helper, so this candidate's operator-dispatch logic is the forcing function for the
  extraction) + `validate_spine` fault for bare-list-shaped `match` (refuse "the exact wrong
  shape") + fault for a malformed `any_of` value (non-list, empty list, non-scalar elements) +
  backward-compat regression + red-proof + doc update.

## Scored
- **Depth** — lower than smallest-diff for the *common* case: an author who reaches for a bare
  list (the shape #371 itself says is natural) is refused and must go learn `any_of`; the
  operator's payoff (room to add `not_in`/`none_of` later) is speculative — no second operator is
  in this mission's scope or requested by any pre-ruling.
  **Depth on the "wrong-shape" case is deliberately not high** — it stays refused-and-explained,
  not silently accepted, exactly as `validate_spine`'s existing faults do.
- **Locality** — comparable to smallest-diff (2 sites), but adds a shared `_match_one` helper and
  a shape-detection branch (`isinstance(dict) and keys=={"any_of"}`) with more edge cases (extra
  keys in the dict, `any_of` present alongside other keys) than smallest-diff's single `isinstance
  (v, list)` check.
- **Seam placement** — same seam; introduces one new internal function.
- **Testability** — marginally higher: the shape-detection branch is independently unit-testable
  from the membership branch, and validate_spine gets a positive test (accepts `any_of`) and two
  negative tests (bare list refused, malformed `any_of` refused) versus smallest-diff's one
  negative test.

## Risk
Two `validate_spine` faults (bare-list-refused, malformed-any_of) instead of one, and the second
one (bare list is *itself* refused, unconditionally, forever) forecloses ever choosing bare-list
semantics later without an authoring-visible breaking change across every spine or template that
had already adopted `any_of`-refuses-bare-list as the taught convention.

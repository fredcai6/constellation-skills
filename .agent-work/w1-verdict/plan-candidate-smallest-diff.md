# Plan candidate: smallest-diff (bare list = "any of these")

## The one thing being designed twice
The `match` shape a condition author writes to say "any of these payload values satisfies me,"
and the comparator change needed at both `_check_condition` (artifact branch) and `attest`
(artifact branch) in `scripts/checklist_engine.py` to honor it.

## Constraint
**smallest-diff** — minimize new syntax an author must learn and minimize the comparator delta,
while fully closing the wedge.

## Design
Per-key comparison becomes: if the declared `match[k]` is a `list`, satisfied when
`ev.payload[k]` is `in` that list (membership); otherwise (current behavior, unchanged) scalar
`==`. Concretely, replace
```python
all(ev.get("payload", {}).get(k) == v for k, v in want.items())
```
with
```python
all(
    (ev.get("payload", {}).get(k) in v) if isinstance(v, list) else (ev.get("payload", {}).get(k) == v)
    for k, v in want.items()
)
```
at both sites (`_check_condition`'s artifact branch, `attest`'s artifact branch). No new dict
key, no new vocabulary — `"match": {"verdict": ["APPROVE", "APPROVE-WITH-FOLLOWUPS"]}` (the exact
shape #371 says an author naturally reaches for) now means what it looks like it means.

`validate_spine.py` gains a sibling fault to `_fault_artifact_no_match` (#562): a **malformed**
`match` value — a list containing anything other than plain scalars (str/int/bool/null), or an
empty list (vacuously unsatisfiable the same way a missing match is vacuously satisfiable, but in
the wrong direction — a check that can never pass) — is flagged, report-only, promotion trigger
named.

## Gates (smallest-diff shape)
- **g1** (crew): implement the widened comparator at both sites + the `validate_spine` malformed-
  match fault (report-only) + backward-compat regression test (every corpus match still resolves
  identically) + red-proof (unsatisfiable before, satisfiable after, pinned to shipped SHA) + doc
  sentence in `docs/CHECKLIST_SCHEMA.md`'s artifact-check row. One gate: the two comparator sites
  and the guard are one mechanism: the guard exists to catch exactly the shape mistake the
  comparator now also fixes, and splitting them risks landing the guard against a comparator that
  hasn't shipped yet (or vice versa), producing a genuinely inconsistent intermediate commit.

## Scored
- **Depth** — high: callers write exactly the natural shape (a bare list) and get the natural
  meaning; nothing new to learn, no leaked implementation detail.
- **Locality** — high: one `isinstance` branch per comparator site (2 sites), one new fault
  function beside its existing sibling.
- **Seam placement** — the seam is the existing `match`-comparison call site; no new seam
  introduced.
- **Testability** — direct: a scalar-match test and a list-match test at each of the two sites,
  plus the standing red-proof.

## Risk
A future author who genuinely wants exact-list-equality against a list-shaped **payload** value
(payload[k] IS a list, and match wants `==` against that exact list) would get membership
semantics instead. Corpus census (`.agent-work/**/*.json`, ~90 real driven spines/plans, plus
`skills/*/templates/*.json`) found **zero** list-valued payload fields and **zero** list-valued
match values anywhere shipped or driven — so this is a live risk for the *future*, not a break of
anything *existing*.

# Review: issue #181 — Gauge reader (Module 2, read side)

## VERDICT: BLOCK

An escaping `TypeError` was found in `read()` — a real violation of the
module's own headline invariant ("this reader never raises"). See finding
below. Everything else (the five named failure modes, the happy path,
`thresholds_for`, the file fence) checks out.

## Isolation

```
$ py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-181-rev
worktree OK: in C:/Programs/constellation-wt-181-rev
```

## Per-criterion results

**1. Five failure modes → None, never raise; staleness from embedded
`observed_at` not mtime.** PASS for all five as directly specified (absent
file, corrupt JSON, malformed/missing/wrong-typed field, stale-by-
`observed_at`, clock-skew). Confirmed via the suite (9 dedicated tests) and
independently reproduced via my own adversarial harness (see below).
Staleness is unambiguously computed from `record["observed_at"]`
(`scripts/gauge_reader.py:107`), never `path.stat().st_mtime` — the code
never touches file mtime at all. PASS.

**2. Valid fresh record → correct `Reading`.**
`test_fresh_record_returns_a_reading` checks all four fields round-trip
correctly against `FRESH_RECORD`. PASS.

**3. Load-bearing invariant: can a stale/malformed record ever produce a
usable `Reading`?** I tried to construct a counter-example and could not
find one. Tried: top-level JSON as list/null/number/string (all → `None`
via the `isinstance(record, dict)` guard at line 148), nested-junk `model`
field, `null`/numeric `observed_at`, `null` `fill_fraction`, float
`schema_version`, a deliberately garbage date string, and the documented
stale-boundary (`max_age` + 1s past → `None`, confirmed both in-suite and
independently). None slipped through. PASS — the invariant holds for every
case I could construct.

**4. `thresholds_for` unknown → default; known/seeded → own pair.**
`test_unknown_model_falls_back_to_default` and
`test_known_model_returns_its_keyed_pair` both pass, confirmed independently
by re-running. PASS.

**5. File fence.**
```
$ git diff 54f5965...HEAD --stat
 scripts/gauge_reader.py    | 151 +++++++++++++++++++++++++++++++++++++++++++++
 tests/test_gauge_reader.py | 133 +++++++++++++++++++++++++++++++++++++++
 2 files changed, 284 insertions(+)
```
Only the two expected files. `scripts/checklist_engine.py` untouched. PASS.

## Independent test run

```
$ PYTHONIOENCODING=utf-8 py -m pytest tests/test_gauge_reader.py -q
..............                                                           [100%]
14 passed in 0.76s
```
Matches the implementer's reported 14/14.

## Adversarial testing (per the review brief's instruction to hunt for an
escaping exception)

I wrote a standalone script exercising 14 garbage/edge shapes against
`read()` beyond what the suite covers: top-level JSON as a list, `null`, a
bare number, a bare string; `model` as a nested dict; `observed_at` as
`null` or a number; `fill_fraction` as `null`; `schema_version` as a float;
an unparseable date string; an empty `{}` record; extra unexpected fields
alongside valid ones; a naive-`observed_at` string (no UTC offset) read
against the default aware `now`; and — the one that broke it — **a
caller-supplied naive `now` read against a record whose `observed_at` has
an explicit UTC offset (i.e. is timezone-aware, which is the normal case
for any ISO-8601 timestamp with `Z` or `+00:00`)**.

12 of 13 garbage-shape cases returned `None` cleanly, matching spec. The
naive-`now` case did not:

```
RAISE [naive now vs aware observed_at] -> TypeError: can't subtract offset-naive and offset-aware datetimes
```

### Finding — BLOCK — `scripts/gauge_reader.py:107`

`_parse_record` normalizes `observed_at` to be timezone-aware if the JSON
string was naive (lines 104-105: `if observed_at.tzinfo is None: observed_at
= observed_at.replace(tzinfo=timezone.utc)`), but it never applies the same
normalization to the `now` parameter. `read()`'s own signature
(`gauge_reader.py:121-125`) accepts `now: datetime | None = None` as a
public, documented, injectable parameter — the docstring says it exists so
"callers -- and tests -- never touch the real wall clock." Nothing prevents
a caller (or a future test) from passing a naive `datetime.now()` instead
of `datetime.now(timezone.utc)` — a common, easy Python mistake, not an
exotic one.

When that happens, line 107 (`age = now - observed_at`) subtracts a naive
datetime from an aware one and Python raises `TypeError: can't subtract
offset-naive and offset-aware datetimes`. This exception is **not** caught
by any `try/except` in `_parse_record` or `read()` — the only `try/except`
in `read()` wraps just the file-read/`json.loads` step
(`gauge_reader.py:142-146`); the `try/except ValueError` around
`datetime.fromisoformat` (line 100-103) doesn't cover this either, since the
failure happens later, at the subtraction on line 107.

I confirmed this is not a corner case gated behind an unusual JSON shape:
**every** record whose `observed_at` string carries an explicit offset (the
normal, expected shape — see `FRESH_RECORD` in the implementer's own test
file, which uses `.isoformat()` on a `timezone.utc`-aware datetime and thus
always has an offset) will raise if `now` is naive. And even a record with a
*naive* `observed_at` string doesn't save you — the reader force-normalizes
`observed_at` to aware at lines 104-105, so it still collides with a naive
`now`. There is no path through `read()` where a naive `now` argument
returns `None` instead of raising.

This directly contradicts the module's own stated contract, both in the
module docstring ("every failure mode ... collapses to a single `None`" /
"it never raises") and in the review brief's explicit criterion: "A single
escaping exception on malformed input is a BLOCK." A caller-supplied `now`
without `tzinfo` isn't malformed *file* input, but it's realistic malformed
*caller* input to a public parameter this exact module chose to expose for
testability — and the whole point of Module 2 is to be the fail-safe layer
Trip (#182) can call at a gate boundary without risking a crash. An
uncaught `TypeError` here is precisely the failure mode this module exists
to prevent.

**Minimal fix:** normalize `now` the same way `observed_at` is already
normalized — e.g., at the top of `read()` right after resolving the
`now is None` default:
```python
if now.tzinfo is None:
    now = now.replace(tzinfo=timezone.utc)
```
(or the equivalent inside `_parse_record`, before line 107). This is a
one-line addition mirroring existing logic already in the file; no
architectural change needed. A regression test exercising a naive `now`
against a valid fresh record should be added alongside it.

## Summary

Criteria 1, 2, 4, 5 pass cleanly; criterion 3 holds for every case I could
construct. But the brief's own instruction to adversarially hunt for an
escaping exception surfaced exactly one: a naive `now` argument reliably
raises `TypeError` instead of returning `None`, for any realistically
timestamped record. Given the module's unconditional "never raises"
contract and its role as a fail-safe gate-boundary reader, this is a BLOCK,
not a float — but it is a one-line, low-risk fix plus one test.

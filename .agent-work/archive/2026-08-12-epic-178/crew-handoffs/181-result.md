# Result: issue #181 — Gauge reader

## Verdict: DONE (not blocked)

Implemented as frozen-spec'd. No overrides to the frozen record format; no
spec gaps surfaced against the writer (#180) or Trip (#182). One local
implementation choice worth flagging (not a spec change): the canonical
gauge path (`.agent-work/<work_id>/gauge.json`, from the epic DESIGN_SPEC
"2. Gauge" section) is passed in by the caller — `read()` takes `path` as a
required positional argument rather than defaulting to a hardcoded path,
since the reader is session/work-id-scoped and has no way to know the
work-id on its own. Trip (#182) will need to construct that path itself.

## Isolation check

```
$ py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-181
worktree OK: in C:/Programs/constellation-wt-181
```

## Summary

New module `scripts/gauge_reader.py`:

- `read(path, *, now=None, max_age=DEFAULT_MAX_AGE) -> Reading | None` — a
  plain function, no Protocol/adapter/class ceremony. Parses the frozen
  4-field record (`schema_version`, `fill_fraction`, `model`, `observed_at`)
  and collapses every failure mode to `None`, never raising:
  - absent file
  - corrupt JSON
  - malformed record (missing field, wrong type, `fill_fraction` out of
    0..1 range, `bool` masquerading as `schema_version` via Python's
    `bool <: int`)
  - stale (`now - observed_at > max_age`, judged from the embedded
    `observed_at`, not file mtime — survives copy/sync/worktree moves)
  - clock-skew (`observed_at` in the future beyond a small tolerance)
- `Reading` — a frozen dataclass with the four record fields
  (`observed_at` parsed to an aware `datetime`). Reaching the caller means
  fresh + well-formed by construction; staleness is resolved inside the
  reader so a caller structurally cannot act on stale data.
- `thresholds_for(model) -> (soft, hard)` — central model-keyed threshold
  table (`_THRESHOLDS` dict), unknown model falls back to
  `DEFAULT_THRESHOLDS`. Both current values are placeholders
  (soft=0.75, hard=0.90) commented `first-run-calibration TBD`; the
  `_THRESHOLDS` table itself ships empty (no real model entries yet) —
  every model currently resolves to the default pair until #182 or a
  follow-up seeds real entries.
- `now` and `max_age` are injectable defaults (no class hierarchy needed) —
  tests never touch the real wall clock or a hardcoded prod file path.

`scripts/checklist_engine.py` was not touched.

## Test command + full output

```
$ PYTHONIOENCODING=utf-8 py -m pytest tests/test_gauge_reader.py -q
..............                                                           [100%]
14 passed in 0.83s
```

Coverage: all five failure modes individually (absent, corrupt, missing
field, wrong-typed field, out-of-range fill_fraction, bool-as-schema_version,
unparseable observed_at, stale, clock-skew — several sub-cases beyond the
minimum five), the stale-boundary case (`max_age` + 1 second past → still
`None`), a small in-tolerance clock-skew case (still resolves, doesn't
falsely reject ordinary drift), the fresh-record happy path (all four
fields round-trip correctly), and both threshold-lookup cases (unknown
model → default, known/seeded model → its own pair).

## Files changed + diffstat

```
scripts/gauge_reader.py    | 151 +++++++++++++++++++++++++++++++++++++++++++++
tests/test_gauge_reader.py | 133 +++++++++++++++++++++++++++++++++++++++
2 files changed, 284 insertions(+)
```

Only these two files — file fence honored.

## PR

https://github.com/fredcai6/constellation-skills/pull/184
(branch `epic178-181-gauge-reader`, base `54f5965`)

## Rework 1

Review of PR #184 found one BLOCK: `read()` normalized `observed_at` to
tz-aware but never normalized the caller-supplied `now`. A naive `now`
(e.g. `datetime.now()` instead of `datetime.now(timezone.utc)`) raised
`TypeError: can't subtract offset-naive and offset-aware datetimes` on
every well-formed record — an uncaught raise that violated the reader's
own never-raises contract.

Fix: normalize a naive `now` to UTC in `read()`, the same way `observed_at`
already was, right after the `now is None` default resolves
(`scripts/gauge_reader.py`, in `read()`). Added
`test_naive_now_does_not_raise` asserting a naive `now` against a valid
fresh record returns a `Reading`, not a raise.

- `PYTHONIOENCODING=utf-8 py -m pytest tests/test_gauge_reader.py -q` →
  **15 passed** (was 14)
- Diff: 2 files changed, 17 insertions(+) (no deletions — additive fix)
- File fence unchanged: only `scripts/gauge_reader.py` +
  `tests/test_gauge_reader.py`
- Pushed to `epic178-181-gauge-reader` (commit `4a39452`), PR #184 updated
  in place — no new PR opened

## Floats / map-impact / triage

- **Float (non-blocking, informational):** the `_THRESHOLDS` table ships
  with zero real model entries — every model hits `DEFAULT_THRESHOLDS`
  today. That's consistent with "numbers are placeholders, TBD," but if
  #182 (Trip) or a later calibration pass expects at least one seeded
  model key to exist for wiring/testing purposes, that seeding wasn't done
  here and would need a follow-up.
- **Float (non-blocking, informational):** `read()`'s `path` parameter has
  no default — the caller (Trip, #182) must build the
  `.agent-work/<work_id>/gauge.json` path itself since the reader has no
  concept of "current work-id." Flagging in case #182's launch order
  assumed the reader would resolve its own path.
- No map-impact: net-new module, no existing architecture doc references
  gauge/reader concepts yet (checked — no hits before this PR).
- No triage candidates identified during this work.

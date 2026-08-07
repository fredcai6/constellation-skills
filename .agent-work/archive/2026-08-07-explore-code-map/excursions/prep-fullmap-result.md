# prep-fullmap result — the full f1Brainz derived map

Status: **COMPLETE**. The map is built, deterministic, and the trial's entry-point
page is verified correct against an independent source scan.

Everything lands under
`.agent-work/explore-code-map/evidence/x13/`. `C:\Programs\f1Brainz` was not written to.
`evidence/x7b/` and `evidence/x11/` were not touched — the scripts were copied and
adapted. No `git add` / `git commit` was run.

## Counts

| | |
| --- | --- |
| files in manifest | 1,224 (src 440, scripts 236, tests 548) |
| parsed | 1,223 |
| failures | 1 — `scripts/generate_evo_dashboard.py` starts with a U+FEFF BOM, which `ast.parse` rejects |
| modules indexed in pass 1 | 1,223 (src **and** scripts **and** tests) |
| statements | 515,678 |
| entities (supplement AST) | 14,998 |
| pages | 16,222 = 14,998 entity + 1,223 module INDEX + 1 top INDEX |
| doc holes | 8,583 of 14,998 entities (57%) have no docstring |
| markdown written | 13.9 MB (51 MB on disk — 16k small files on NTFS) |

Statements by predicate: reads 281,180 · calls 99,791 · writes 72,709 ·
param-of 25,278 · contains 15,026 · imports 14,139 · documents 7,433 · inherits 122.

## Wall time per stage

| stage | time |
| --- | --- |
| `astx.py` pass 1 (index 1,223 module tables) | 1.6 s |
| `astx.py` pass 2 (extract 1,224 files) | 9.3 s |
| `supplement.py` (1,224 files) | 2.2 s |
| `render_map.py` load stores | 1.6 s |
| `render_map.py` render 16,222 pages | 23.6 s |
| **total, cold** | **~38 s** |

No scale problem. The whole map rebuilds in well under a minute; the render is
dominated by 16k individual file writes, not by computation.

## Artifacts

```
evidence/x13/astx.py              adapted extractor (see "changes" below)
evidence/x13/supplement.py        adapted AST supplement, all 1,224 files
evidence/x13/render_map.py        self-contained lean renderer
evidence/x13/checks.py            self-checks (b) (c) (d)  -> checks_output.txt
evidence/x13/checks2.py           defect measurements       -> checks2_output.txt
evidence/x13/statements.jsonl     142 MB   <- GITIGNORE
evidence/x13/supplement.json      8.6 MB   <- GITIGNORE
evidence/x13/map/                 16,222 pages, 13.9 MB     <- GITIGNORE
evidence/x13/map/ids.jsonl        0 bytes (see below)
evidence/x13/{extract,supplement,render}_report.json
```

`map/ids.jsonl` is **empty and that is correct**: f1Brainz carries no anchor
comments yet, so there are no ids to map. The file is written anyway to establish
the well-known location.

## Self-checks

**(a) Determinism — PASS.** Built the map twice, `diff -r` between the two trees:
no output, exit 0, across all 16,222 files.

**(b) Non-ASCII provenance — PASS.** 2,718 non-ASCII lines across the 16,222 pages.
All 2,718 are traceable to a docstring line or an unparsed source value carried
through the supplement (checked by substring match against the supplement's own
docstring/attr text). **Zero** come from template text. Template strings are pure
ASCII as required.

**(c) Entity reconciliation — RECONCILED.** Reconciled on *source position*, not on
symbol, because the store's symbols are not unique (see D2).

- store `contains`: 15,026 statements at 15,026 distinct positions
- supplement: 14,998 entities at 14,998 distinct positions
- supplement positions with no store statement: **0**
- store positions with no supplement entity: **28**, fully explained —
  23 are defs nested inside a control-flow body (`for` 14, `try` 4, `if` 4,
  `with` 1) which the supplement's straight `node.body` walk does not descend
  into; 5 are same-name redefinitions in one scope (e.g. `build_findings_markdown`
  defines `fmt` three times) which collapse in the supplement's dict.

**(d) Spot check — PASS.** All 12 top-level defs of
`scripts/validate_segment_map_662.py` have pages. `split_half_boundary_drift.md`
now reports `referenced by: 3 sites in 3 modules (src.physics.pilot.pipeline,
tests.unit.physics.segment_map.derivation.test_segment_map_gating)`, which matches
an independent AST scan of all 1,224 files for the name exactly (its own module,
`src/physics/pilot/pipeline.py`, and the test). It did **not** match before the D4
fix below — see the next section.

## Changes made beyond mechanical adaptation

The brief authorised patching pass 1 to index scripts/ and tests/. Two further
changes were needed; both are contained in the `evidence/x13/` copies.

**D4 (fixed) — function-scoped imports lost every edge through them.** x7b's
`_prebind` bound a name imported *inside a function body* as an ordinary local and
threw away what it pointed at. So `from scripts.validate_segment_map_662 import
split_half_boundary_drift` inside a function in `src/physics/pilot/pipeline.py`
made the subsequent call resolve to `local:split_half_boundary_drift` — it
disappeared from the caller's `calls` and from the callee's `referenced by`. This
is exactly the trial's entry-point page, which the brief requires to be right, so I
fixed it: the scope now records the import binding and `resolve_name` /
`resolve_attr` chase it the same way module-level imports are chased.

Blast radius before the fix: 315 of 1,224 files use function-scoped imports, binding
1,112 distinct names; **2,046 calls/reads** were being dropped to `local`. After the
fix, 1 remains (a name that is both a local import and a genuine local elsewhere in
the same file). Statement counts are unchanged (515,678); the resolution mix moved:
internal +1,789, external +1,002, local −2,045, unresolved −746.

**D2 (measured, worked around, NOT fixed) — the store's `contains` symbol truncates
the enclosing chain.** A class defined inside a function is named as if it were
module-level (`neural_rate:WearRateNet` instead of
`neural_rate:_build_wear_rate_net.WearRateNet`), and a function defined inside a
method is named against the class, dropping the method
(`collector:F1DataCollector._kmh_to_ms` instead of
`collector:F1DataCollector._build_telemetry_point._kmh_to_ms`). 251 entities are
affected, and the flattening makes 15,026 definition sites collide down to 14,939
distinct symbols — i.e. **the store cannot distinguish 87 real definition sites**.

The renderer works around it: pages are keyed by the supplement's structurally
correct qualified name, and the store's symbol is recovered through a `(file, line)`
join. That join resolved **14,998 of 14,998** entities, zero misses. Fixing the
extractor itself is a design question for the grammar, not a render-time one, so it
is left named rather than patched.

## Resolution rate vs the 9-file slice

| window | statements | unresolved |
| --- | --- | --- |
| x7b core, 9 files | 2,847 | 7.55% |
| x7b all, 67 files | 44,554 | 7.69% |
| **x13, 1,224 files** | **515,678** | **9.26%** |

The rate degrades, but gently — under two points across a 180x larger window. Almost
all of the loss is one failure class: `dispatch-unknown-base` is 45,191 of the 47,744
unresolved (95%), i.e. an attribute access on a receiver whose type the two cheap
inference rules cannot pin. The rest is small and long-tailed: `unbound-name` 956,
`chained-attribute` 504, `dynamic` 460, `star-import` 232, `non-name-expr` 343,
`missing-in-module` 58. Nothing new appears at scale — the same failure shape, more
of it.

## What surprised me

**Tests dominate the map and are its noisiest class.** 9,086 of 14,998 entities
(61%) live under `tests/`, and **85% of test entity pages say "referenced by: none
found"** — correctly, since pytest discovers test functions rather than calling
them. That is 7,802 pages whose most prominent fact is a true but useless absence.

| package | entity pages | no inbound reference | no docstring |
| --- | --- | --- | --- |
| src | 4,222 | 561 (13%) | 1,725 (40%) |
| scripts | 1,690 | 102 (6%) | 1,041 (61%) |
| tests | 9,086 | 7,802 (85%) | 5,817 (64%) |

The 13% orphan rate under `src/` is the number worth looking at — with tests and
scripts now indexed, "no inbound reference" is a real signal there for the first
time, where in x11 it was an artifact of the extraction window.

**Grouping the top index by top-level package is not enough at this scale.** The
brief asked for src/scripts/tests grouping so the top INDEX stays a routing surface.
It does not: `map/INDEX.md` is **1,233 lines / 205 KB** — three headings over a flat
list of 1,223 modules. A second level (package -> subpackage) would be needed to make
it cheap to route through. Flagging, not fixing; it is a format decision.

**Entity pages themselves are the right size.** Median 15 lines, p10 12, p90 25,
largest 169. No entity page is under 9 lines. The lean per-entity format holds up
unchanged at 15k entities — the scale problem is in the indexes, not the pages.

**A rendering defect inherited from x11 (D3, not fixed).** The summary line comes
from the store's `documents` statement (first physical line of the docstring only)
and the body from the supplement (everything after). When a docstring's opening
sentence wraps across two lines, the page renders line 1, then a blank line, then the
rest of the sentence — visible on `split_half_boundary_drift.md`. Cosmetic, but it
affects every entity whose summary wraps.

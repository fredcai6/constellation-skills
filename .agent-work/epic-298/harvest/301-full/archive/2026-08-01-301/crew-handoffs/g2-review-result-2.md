# Review Result

Status values follow `skills/workbench/references/status-model.md`.

VERDICT: APPROVE

## Assigned Gate
`g2` — the validated episode writer (issue #301, epic-298) — **RE-REVIEW** of a rework
that addressed a prior BLOCK (`.agent-work/301/crew-handoffs/g2-review-result.md`).

## Result
`APPROVE`

Survey driven end-to-end through the checklist engine at
`.agent-work/301/g2-review-2/review.json` (11 items: the 6 standard reviewer checks
r0–r5, the required Fowler pass r6, plus 4 rework-specific checks appended for this
re-review — r7/r8 independent fix verification by probe, r9 independent class-hunt, r10
no-regression + C2–C8 re-confirmation). Consolidated `verdict=APPROVE` with an explicit
override-reason (r9 recorded `fail` on a genuine but non-blocking new finding — see
below), lease released. Fowler pass recorded at `.agent-work/301/g2-review-2/fowler-pass.json`,
cleared `verify_fowler_pass.py` (12 smells: 11 absent, 1 overridden with logged
standard+reason).

## Handoff compliance
The rework did exactly what the BLOCK asked: fixed both demonstrated defects in
`scripts/apply_episode_delta.py`, added TDD-red-then-green tests proving each fix, ran
an explicit sweep for the same defect class, and reverified the full gate contract.
Both fixes hold under my own, independently-authored probes (not the implementer's test
file) — see "Fix verification" below.

## Scope drift
None. `git status --short` shows exactly the 3 pre-existing untracked paths
(`scripts/apply_episode_delta.py`, `tests/fixtures/episodes/`, `tests/test_episode_store.py`)
— no new files, no edits outside those. `_LAYOUT_ADAPTER` is byte-for-byte unchanged
(`_LAYOUT_OPTION_B`, line 398); `durable_root()` still never called (2 grep hits, both
in a docstring); `LESSONS.md`/`apply_lessons_delta.py`/issue #300's manifest untouched;
the record grammar was not relitigated. No probe/scratch files were left in `scripts/`,
`tests/`, or `episodes/` — every probe ran from the scratchpad using
`tempfile.TemporaryDirectory` store roots.

## Fix verification (independent, by probe — not by reading the implementer's tests)

**Defect 1 (line-boundary guard) — HOLDS.** Own script probed `_reject_newline`
directly against 11 boundary sequences Python's `splitlines()` honors (LF, CR, CRLF,
VT, FF, `\x1c`, `\x1d`, `\x1e`, NEL `\x85`, U+2028, U+2029), each embedded, trailing,
**and leading** (the implementer's own tests only covered embedded + trailing) — all 33
combinations correctly rejected. Confirmed no false FAIL: empty string, a 100,000-char
value, real unicode (accented/CJK/emoji), a literal two-character `\n` **escape**
(backslash+n, not an actual newline), space, and tab are all correctly accepted.
End-to-end CLI probe using 4 boundary characters the implementer's own end-to-end tests
did **not** name (NEL, RS, form-feed, U+2029 — theirs covered only U+2028) confirmed the
forged-`- status: retired`-line attack is rejected pre-write in every case: exit 1,
**zero** files ever written.

**Defect 2 (write-phase atomicity) — HOLDS for its claimed scope; one disclosed residual
confirmed, judged non-blocking.** Own script forced an `OSError` on the **first** staged
write of a 2-file commit (the implementer's own test forces failure on the *second* —
the complementary case): store snapshot byte-for-byte unchanged before/after, zero stray
`.tmp-*` files. Also independently probed the residual gap the implementer's own
docstring already discloses: forcing `os.replace()` itself to fail on the 2nd of 2
*moves* (after both stagings had already succeeded) does leave the store mutated (the
1st move had already landed), though it leaves zero stray temp files. This is honestly
named in `_Transaction.commit()`'s own docstring as not fully atomic across N files
absent a WAL, which `EPISODE_STORE.md`'s markdown-in-git constraint doesn't provide.
Judged non-blocking: it is a materially smaller and rarer failure surface than the
original defect — only the OS's own already-atomic single-file rename primitive can
fail here (permission change or directory deletion mid-run, not disk-full, which is now
caught at the staging phase) — and it is disclosed, not silently claimed away. The
originally-demonstrated defect (an ordinary `write_text` failure leaving earlier writes
landed) is fully closed.

Independently reproduced (own script) that the write-phase error-message split loses no
information: a forced `OSError('[Errno 28] No space left on device')` surfaces in full
via `"error: write failed, store left unchanged: [Errno 28] No space left on device"` —
framing improved (no longer mislabeled as a delta-read failure), underlying detail
preserved.

## Class-hunt (independent) — one new instance found, lower severity, non-blocking

Re-derived the implementer's sweep claim independently rather than trusting it. `ID_RE`/
`RUN_RE`/`FIELD_RE`/`ASSERTION_HEADING_RE`/`HEADER_RE` were traced against actual
construction and are consistent (a `RUN_RE`-derived episode id always matches `ID_RE` by
construction; no case-folding or unicode normalization anywhere in the module, so that
sub-class doesn't exist here).

**Found:** `create.mechanical.artifact-ref` entries are the *one* field not run through
`.strip()` before storage in `_apply_create` — every mechanical scalar, every assertion
`statement`, `history`, and every retire field *is* `.strip()`ed before being stored,
but `artifact-ref` list entries are used raw. `parse_episode()` strips the **whole
physical line** (`line.strip()`) before matching `FIELD_RE`. Demonstrated end-to-end: an
`artifact-ref` value of `" some/path.md "` (leading+trailing plain space — not a
`splitlines()` boundary character, so it passes `_reject_newline`) is accepted by the
CLI (`rc=0`), rendered verbatim, then re-parsed as `" some/path.md"` — the **trailing**
space is silently dropped. `render(parse(text)) == text` is `False` for this input; the
existing `RoundTripTests` don't cover an `artifact-ref` with edge whitespace, so this
slipped through both the original implementation and this rework's sweep.

This is a genuine instance of the **same root-cause class** named in the rework brief —
a guard's definition of "safe" (`splitlines()`-boundary-only) disagreeing with what the
parser actually does to a stored line — on a dimension (`.strip()`-consistency) the
implementer's own sweep didn't check (their sweep verified every value routes through
`_reject_newline`, not that every value is also `.strip()`-consistent with the parser).

**Judged non-blocking**, distinct from the two BLOCK defects: whitespace-only, one field
only, no forged line, no loss of semantic content (a legitimate artifact-ref/path
reference carrying meaningful leading/trailing whitespace is not a realistic scenario),
and it does not violate any of the named close criteria C2–C8. A one-line mechanical fix
is available (`.strip()` each `artifact-ref` entry in `_apply_create`, matching the
pattern already used for every other field) — flagged as a leftover for the next touch
of this file, not worth a third rework round.

## Evidence verdict
All of `g2-result.md`'s evidence commands reproduce exactly: `pytest
tests/test_episode_store.py -q` → 24 passed, 16 subtests (match); `pytest tests/ -q` →
1181 passed, 2 skipped, 276 subtests (match); all 3 fixtures fail with exit 1 and the
claimed messages; `git status` clean; `durable_root` grep → 2 hits, both docstring-only.
Went beyond re-running claimed evidence: authored independent probes for both fixes and
a fresh class-hunt (see above) rather than trusting the implementer's own test harness.

## Code/doc quality
Determinism constraint holds (no wall-clock call added). `newline=""` used consistently
on the new staged-write path. No hidden fallback: both failure paths
(`EpisodeDeltaError`, `OSError`) fail visibly with an accurate message. Fowler pass (r6,
required): recorded and cleared the rail — 11 baseline smells absent, one
(`comments-as-deodorter`) overridden against the file's own uniform, pre-existing
dense-rationale-docstring convention (both new docstrings are load-bearing against the
exact regression class that caused the original BLOCK, not decoration).

## Map impact verdict
No new claims in `g2-result.md`'s Map Impact beyond the original review's already-verified
notes (this is a bounded rework of two defects, not a new structural change). The
originally-flagged 6th layout seam (`_new_episode_path()`, triage candidate `tc1`) is
untouched by this rework. My own new finding (artifact-ref round-trip gap) is a code-level
defect, not a map/architecture-impact item — no durable-context routing needed beyond
naming it here for the next implementer to pick up.

## Reconciliation check
No divergence from the recorded architecture beyond what the original review already
reconciled. The retirement layout placeholder is confirmed undisturbed: `_LAYOUT_ADAPTER
= _LAYOUT_OPTION_B` byte-for-byte unchanged, both adapters still fully implemented,
`TODO(g4)` markers unchanged — not re-litigated, matching the original review's accepted
ruling (placeholder, not a disguised decision).

## Blockers
None.

## Out-of-scope observations
- **New, in-scope-but-non-blocking finding (this review):** `artifact-ref` entries
  aren't `.strip()`ed before storage, unlike every other field, causing a silent
  round-trip loss of leading/trailing plain whitespace on the next parse. Fix: `.strip()`
  each `artifact-ref` entry in `_apply_create`, matching every other field's pattern.
  Recommend this land as a small mechanical fix at the next touch of
  `scripts/apply_episode_delta.py` (e.g. alongside g4's layout ratification, or as its
  own tiny follow-up) rather than a fresh rework round for this gate.
- Carried forward, unchanged, from the original BLOCKed review (not re-verified this
  round, since scope was the two Blockers + a class-hunt): the 6th unnamed layout seam
  (`_new_episode_path()`) triage candidate; top-level unrecognized op keys silently
  accepted; duplicate-op last-write-wins semantics.
- Confirmed, not a new issue: `final_path.parent.mkdir(parents=True, exist_ok=True)`
  in the new `commit()` still runs before that file's staged write (same line/ordering
  as the old code), so a staging failure on write N can leave an empty directory for
  write N's parent under the not-yet-ratified Option-A layout — pre-existing, already
  self-flagged by the implementer, no code risk (empty dir, not corrupted data).

## Workflow Feedback
Mandatory section. A `none` answer requires a run-specific reason: `none — confirmed
after review: <what you checked>`; a bare `none` is treated as an unfilled field. This
is workflow signal, not project signal: you are the only one who saw this friction — if
you do not report it here, it is lost.

- **Handoff gaps:** None load-bearing. The RE-REVIEW dispatch quoted both original
  defects verbatim with exact line numbers and reproduction shape, which made
  constructing independent (not copy-pasted) probes for each straightforward.
- **Context rediscovered:** None — the dispatch's own "Consider strip() semantics...
  and the round-trip write-then-parse identity" line pointed directly at the productive
  class-hunt probe (the `artifact-ref` finding came from taking that sentence literally
  and checking every field's strip-consistency against the parser, not just the
  newline-guard routing the implementer's own sweep checked).
- **Instructions improvised around:** The engine's `consolidate` verb refuses `APPROVE`
  while any survey item is `fail` unless given `--override-reason`. r9 (class-hunt)
  legitimately recorded `fail` because it found a real round-trip mismatch, even though
  I judged the finding non-blocking. I used `--override-reason` to carry that judgment
  through the engine rather than mis-recording r9 as `pass` to avoid the guard — this
  wasn't explicitly named in the reviewer skill for a "found something real but
  non-blocking" case, but the guard's own design (a deliberate friction point, not a
  silent pass) and the skill's own "findings ranked by severity... `APPROVE`-with-findings
  is right if criteria are met and the rest are refinements" language both point at this
  as the correct use. Worth confirming this is the intended pattern, or naming it
  explicitly in the skill for future re-reviews that find a genuine-but-lower-severity
  new instance mid-hunt.
- **What would have made this easier:** Nothing significant — quoting the two original
  defects verbatim with line numbers and repro shape, plus explicitly inviting a
  class-hunt with named dimensions (strip semantics, unicode normalization, case
  handling, round-trip identity) in the dispatch, is exactly what made this review
  productive rather than a re-read of the implementer's own claims.

## Return status
`complete`

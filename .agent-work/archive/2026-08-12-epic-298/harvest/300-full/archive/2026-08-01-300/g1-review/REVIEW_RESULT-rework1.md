# Review Result — rework 1

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1-review` — issue #300 (epic-298), re-review after rework 1.
Survey re-driven through the engine: `.agent-work/300/g1-review/review.json`
(session `reviewer-300-g1-rework1`; `r3-evidence` and `r4-quality` re-recorded from
`fail` → `pass`; consolidated `verdict=APPROVE`, findings=0).

## Result

# `APPROVE`

**0 blockers · 0 major · 0 minor.** All three findings closed. Two Fowler observations
carried forward as triage candidates (`tc5`, `tc6`), correctly out of this rework's scope.

I re-verified each fix against the world rather than against the reports — including
re-running my own three harnesses from round 1, so the before/after delta is attributable
to the fixes and not to a changed measurement.

---

## BLOCKER-1 — closed

`skipTest` → plain `return`; `scripts/verify_skip_guard.py` untouched; no allow-slot spent.
`grep -n 'skipTest'` on `tests/test_context_manifest.py` returns nothing.

I re-ran **my own** CI-simulation script — the identical one that produced the original
refusal, so this is a controlled before/after:

```
=== clean checkout has .agent-work? ===
ls: cannot access '.../ci-sim/.agent-work': No such file or directory

=== CI step: python -m pytest tests/ -q --junitxml=junit-report.xml ===
1211 passed, 2 skipped, 326 subtests passed in 34.58s
PYTEST EXIT=0

=== CI step: python scripts/verify_skip_guard.py junit-report.xml ===
skip guard ok: 2 skip(s) in report, all match documented allow-tuples
SKIP GUARD EXIT=0
```

Round 1, same script, same host: `1208 passed, 3 skipped` → `REFUSED: 1 skip(s) …` →
`SKIP GUARD EXIT=1`. Worktrees 5 before, 5 after.

The fix is the right one and the right *shape*: `return` rather than an `ALLOWED_SKIPS`
entry keeps that list meaning "cannot run on this platform" instead of "fixture absent",
and the comment now names the whole trap (gitignored → absent in CI → guard refuses) so
the next reader does not have to rediscover `ci.yml`.

The four remaining `SkipTest` calls in `tests/test_context_determinism.py` are correct and
were never in scope — those classes are not on `ALLOWED_SKIPS` and their messages
interpolate git's stderr, so they can never be allow-listed and would fail CI hard. That is
exactly the degradation I ruled acceptable, and it is unchanged.

---

## MAJOR-2 — closed, and the characterization test is genuinely discriminating

The docstring now states both conditions, says explicitly that the gate's `.gitattributes`
grep pins condition 1 **only** and structurally cannot see condition 2, and points at the
test carrying the other half. `rev()` itself is byte-unchanged — I re-ran my 16-pattern hunt:
the same four known divergences, and **0 mismatches across all 263 tracked files**.

### The Commander's specific question, answered by measurement

> *confirm the added characterization test is genuinely discriminating rather than passing
> for the wrong reason, since it asserts an `assertNotEqual` and those can pass on a broken
> oracle.*

The concern is correct in general and I did not take the implementer's single mutant as an
answer. I wrote my own set — deliberately including mutants a bare `assertNotEqual` would
be **happy** with — and rebound `cm.rev` in memory (nothing on disk edited):

```
green  control: the real rev (unmutated)
RED    M1 no LF normalisation                    '05cdef54…' == '05cdef54…'
RED    M2 constant garbage digest                '00000000…' != '5bdcf0dd…'
RED    M3 hash of something else entirely        'd684dbde…' != '5bdcf0dd…'
RED    M4 over-normalise (CRLF and lone CR)      'fbbee861…' != '5bdcf0dd…'
RED    M5 normalise LF -> CRLF instead           '05cdef54…' == '05cdef54…'
RED    M6 strip every CR                         '16f56de8…' != '5bdcf0dd…'

control green + every mutant red : True
```

**6/6 killed.** The load-bearing detail: **M2, M3, M4 and M6 all still satisfy the
`assertNotEqual`** — a garbage digest is trivially "not equal" to the oracle. They were
caught only by the two explanatory equality assertions (`git stored the bytes verbatim` /
`rev normalised them`). So the test does not rest on the `assertNotEqual` at all; the
`assertNotEqual` is the headline and the two `assertEqual`s are what actually hold it up.
That is the correct construction for a characterization test, and it is why the Commander's
concern does not land here.

Two further integrity checks, neither of which the implementer or Commander ran:

- **The second oracle does not collude with `rev`.** `_raw_blob_oid` computes the OID with
  its own `hashlib.sha1(b"blob %d\x00" …)` call and never references `cm`. If it had been
  written as a wrapper around `cm.rev`, the "why" assertions would have been tautological
  and M2/M3/M4/M6 would have survived.
- **The oracle is not hostage to a CI runner's git config.** The test hashes files in an
  out-of-tree tempdir, which made me suspect a dependence on `core.autocrlf` (a host-level
  setting, not repo-level — a plausible way for this to be green here and red in CI). I
  probed it: `git hash-object` returns the identical OID under
  `core.autocrlf=true|false|input`, for both in-tree and out-of-tree paths, because
  `.gitattributes`' `* text=auto` governs. Hypothesis tested and killed — **not** a finding,
  recorded so nobody re-opens it.

Round 1's `assertNotEqual`-based `RevIsGitBlobOid` control case (`b"alpha\r\nbeta\r\n"`,
content git *does* normalise) is present and is what kills M1 and M5.

---

## MINOR-3 — closed. Ruling on the colon strictness: **it is correct, keep it**

The Commander asked me to rule rather than wave it through. My ruling: **the colon rejection
is right, and "reject a colon anywhere" is the correct width — not over-strict for this
repo.** Three reasons, the first measured:

1. **A colon filename cannot be created on this platform at all.** I tried:
   `open(os.path.join(tmp, "a:b.md"), "w")` → `FileNotFoundError: 'a:b.md'` — NTFS parses it
   as an alternate data stream, so the ordinary file never exists. This repo carries
   `constraint:windows-corpus`. A declarable file whose name contains a colon therefore
   **cannot survive a Windows checkout**, so it cannot be part of a corpus that must work
   here. The theoretical cost the Commander worried about — rejecting a legitimate POSIX
   filename — is unreachable in *this* corpus, not merely unlikely.
2. **Zero live instances.** I scanned the three declarable roots (worktree, installed skills,
   main-checkout `.agent-work`): **0 of 2680 filenames** contain a colon.
3. **It fails visibly at the right seam.** The guard is on the *declaration*, not on files,
   so it can only ever reject something an author typed into a spine template — and it
   raises `DeclarationError` at declaration time rather than silently folding. If it ever
   does bite, it bites loudly and immediately, which is the shape this module already
   commits to everywhere else.

The implementer's stated reasoning — one condition covers both the drive-letter fold and the
NTFS-stream form because both make a declaration resolve to different content on different
operating systems — is the correct generalisation, and it is the same instinct as the
already-logged glob-metacharacter rejection.

Verified: my producer hunt's drive-letter case now raises `DeclarationError` where it
previously returned a row; the belt-and-braces comment no longer claims a guard it does not
have; three new `rejected` fixtures (`windows_drive_letter`, `windows_drive_relative`,
`ntfs_alternate_data_stream`) are committed and swept by
`test_every_rejected_fixture_raises_rather_than_degrading`.

---

## Ruling on `tc3`: acceptable as-is — **do not change the gate command**

The Commander asked whether the gate check needs to change now that only the attribute half
is pinned by it. **My ruling: no. Close `tc3` against g1 and re-point it at #301.**

- A configuration check can only pin configuration. `! grep -E '(-text|binary)' .gitattributes`
  does that job correctly and completely; the defect in round 1 was never the command, it was
  the docstring **claiming more than the command delivers**. That claim is now corrected and
  the command's exact reach is stated in prose next to it.
- The content half is now pinned by a test I have measured as discriminating. Between the two,
  the whole envelope is covered — by the mechanism suited to each half.
- The content-level guard I originally suggested would be a scan across three roots, two of
  which (`skill`, `durable`) live **outside the repo** and vary per install, and which CI does
  not even have. That is real standing machinery for a class with zero instances in 2680
  files, and it would be prevention rather than detection.
- The right home for the check is not a gate at all. It belongs where the bytes are already in
  hand — at manifest production, in #301's consumer, where `rev` could cheaply mark a row whose
  content is in the divergent class. No traversal, no scanning, and it catches the real case
  instead of a hypothetical corpus-wide one.

So `tc3` narrows to: *"#301: when the producer hashes a row, flag content git would refuse to
normalise (NUL byte or lone CR), so a divergent `rev` is visible on the row rather than
inferred from a docstring."*

---

## Confirmation that nothing new was introduced

| check | result |
|---|---|
| `rev()` byte-unchanged in behaviour (16-pattern hunt) | same 4 known divergences, **0/263** mismatches on real tracked files |
| producer hunt (16 adversarial declarations) re-run | only the drive-letter verdict moved (row → `DeclarationError`); no other behaviour changed |
| determinism acceptance test still non-vacuous after the producer edit | **3/3** environment-dependence mutants still caught, baseline green, producer byte-unchanged |
| `-k 'no_globs or newline_pinned or py312_compatible'` | 3 passed, 44 deselected, exit 0 — still cannot exit 5 |
| `git diff --stat` | still the single 8-line spine change |
| `git status --short` | same 5 entries as round 1 — no new files, none removed |
| stray worktrees | 5 before, 5 after |
| scope | `verify_skip_guard.py`, `ci.yml`, `checklist_engine.py`, `test_context_determinism.py`, spine template all untouched by the rework |

The colon guard cannot affect the shipped Commander declaration (no colons in it) and the
suite confirms it: the full run went **1209 → 1211 passed**, i.e. `+2` for the two new tests
plus the previously-skipping test now running, with no test lost.

## Reconciliation check

`no divergence Commander must reconcile.` The rework's Map Impact note is accurate and I
agree with its one substantive claim: `constraint:markdown-in-git` is now relied on
*accurately* (both halves stated, one pinned by test rather than by a command that cannot see
it), and that stated limit is worth carrying into the map. No new decisions — the colon
rejection is correctly characterised as an extension of the already-logged glob decision,
within the same latitude, for the same reason.

## Out-of-scope observations (carried forward, none blocking)

- **`tc5`** *(was the Fowler duplicated-code flag)* — `test_context_determinism.py` duplicates
  the second-checkout ritual in `setUpClass` and again inline in `RealCheckoutSkew`, and the
  copies have already drifted (only the first applies `INSTALL_SHIM`). Correctly out of this
  rework's scope; the implementer flagged it too. Extract one `_clean_checkout` contextmanager.
- **`tc6`** *(was the Fowler speculative-generality flag)* — the `run=` parameter on
  `build_manifest`/`produce` still has zero callers and zero tests; `step=` remains the seam a
  second selector could grow through; the `"step … is not a task on this checklist"` `ValueError`
  is still unreachable (`active_id` raises `KeyError` first).
- **`tc1`**, **`tc2`**, **`tc4`** from round 1 stand unchanged. **`tc3`** narrows as ruled above.

## Workflow Feedback

- **Handoff gaps:** none for the rework note — confirmed after review: it named the exact three
  defects, demanded the CI condition be *reproduced* rather than the command merely re-run, and
  explicitly told the implementer not to touch `verify_skip_guard.py`. Each of those shaped a
  fix I could verify instead of merely believe, and the implementer's own feedback identifies
  the generalisable lesson correctly: *a verification command that runs in the developer's
  environment cannot see an environment-conditional defect — the handoff has to say which
  condition to reproduce, not only which command to run.* That belongs in LESSONS.
- **Context rediscovered:** whether `git hash-object` on an out-of-tree temp path is sensitive
  to `core.autocrlf` (it is not — `* text=auto` governs). Both this suite's pre-existing CRLF
  twin test and the new characterization test depend on that, and it was written down nowhere.
  Worth one line in the test module so the next reviewer does not re-derive it as I did.
- **Instructions improvised around:** two engine-verb misfits on a `survey`, both cheap but both
  costing a REFUSED call. (1) `advance` is refused — `record` both records and advances; the
  reviewer SKILL's §3 says "advance that check", which is gated-checklist wording. (2) `reopen`
  is also gated-only ("REFUSED: reopen applies to gated checklists"), so re-recording a survey
  check after a rework is done by calling `record` again on a terminal item. That works and is
  arguably the right design, but nothing documents it — the rework path for a survey is
  undocumented and I found it by being refused.
- **What would have made this easier:** the Commander's message did the single most useful
  thing possible — it named the two judgment calls it wanted *ruled on* rather than verified,
  and said plainly that a second BLOCK was fine. That is what let me spend the round on the two
  open questions instead of re-litigating settled ground. Worth keeping as the standard shape
  for a re-review dispatch.

## Return status
`complete`

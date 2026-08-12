# Reviewer Handoff

## Gate
`g2` — the validated episode writer (issue #301, epic-298)

## What was implemented

- `scripts/apply_episode_delta.py` — the **only** write path into the episode store. Mirrors
  `scripts/apply_lessons_delta.py`: an LLM proposes a JSON delta, the script validates every op
  and applies **all-or-nothing**.
- `tests/test_episode_store.py` — 18 tests.
- `tests/fixtures/episodes/{misfiled-field,missing-retire-reason,newline-injection}-delta.json`
  — adversarial fixtures the gate closeout invokes directly.

## How to inspect

```bash
cd C:/Programs/constellation-skills-wt/298-301
git status --short          # three new untracked paths; they are NEW, so git diff shows nothing
cat scripts/apply_episode_delta.py
cat tests/test_episode_store.py
cat docs/EPISODE_STORE.md    # the frozen contract this gate implements — authoritative
```

The implementer's result is at `.agent-work/301/crew-handoffs/g2-result.md`; its handoff at
`.agent-work/301/crew-handoffs/g2-handoff.md`.

## Close criteria — verify each independently

- **C2** the writer **REJECTS** a delta filing a mechanical field under the agent-supplied bin
  or vice versa, via a per-bin field-name allowlist.
- **C3** the writer **REJECTS** (a) a `retire` op with a missing/whitespace-only reason, and
  (b) any agent-supplied value containing a newline (the injection defense against a free-text
  field forging a `- status: retired` line).
- **C4** an invalid op **anywhere** in a multi-op delta leaves the store **byte-for-byte
  unchanged** — no partial write.
- **C5** the store root resolves through the g1 seam at tracked `episodes/`, and
  `durable_root()` is **not called**.
- **C6** a `dispute` op targets **one named agent-supplied field**, changing only that field's
  standing; a sibling field's stored line is **byte-identical** before and after.
- **C7** the three fixtures exist at exactly the paths above.
- **C8** the retirement layout is **not bound** — the effect routes through the
  `apply_retirement()` seam, with the layout-independent field diff separated from the
  layout-dependent file effect.

## HUNT THESE SPECIFICALLY

**1. The layout default — the judgment call I most want a second opinion on.** The implementer
set a module constant `_LAYOUT_ADAPTER = _LAYOUT_OPTION_B`, commented as a PLACEHOLDER rather
than a ratified choice, with **both** adapters fully implemented and a test that flips the
switch and exercises Option A.

The retirement layout is held for human ratification. A default is arguably a de facto binding:
whatever runs today behaves as Option B. My provisional read is that this is acceptable — the
code must do *something*, both adapters are real and tested, binding is one constant, and no
real episodes exist yet (capture is issue #305), so there is no migration cost today. But I may
be rationalizing. **Independently judge:** is this genuinely "unbound with a placeholder," or
is it "Option B, bound, with a comment saying otherwise"? Is there a materially better shape —
and if so, is it better enough to justify rework?

**2. The wrong-answer class — the highest-value part of your review.** Per
`lesson:round-trip-tests-prove-artifacts-not-parsers`, do **not** merely re-run the suite: a
green suite over well-formed input proves the input was clean, not that the validator is
correct. **Author inputs designed to make this writer return a WRONG answer:**
- A **silent PASS on invalid input** — a delta that *should* be rejected but is accepted. Try
  misfiled fields under casing/whitespace variants, unknown field names, an empty or
  whitespace-only agent value, a `dispute` targeting a nonexistent or mechanical field, a
  retire reason that is only punctuation, duplicate ops on the same target in one delta, an op
  with a missing required key.
- A **false FAIL on valid input** — legitimate content the writer wrongly rejects. Especially:
  does single-line enforcement reject a *legitimately* long value, a value containing a
  literal `\n` escape sequence as text, or unicode?
- **Newline handling.** This is Windows with Git Bash; `\r\n` translation is a real hazard for
  both the byte-for-byte assertion (C4) and single-line enforcement (C3b). Can a `\r` alone
  smuggle content past the newline guard? Does C4's assertion still hold if a file is written
  with CRLF?

**3. All-or-nothing under partial failure.** Verify C4 is real, not asserted. Does a delta
whose *last* op is invalid truly leave earlier ops' effects unwritten? What if an op fails
*during* the write (e.g. a path that cannot be created) rather than during validation? Is the
validate-then-write separation actually complete?

**4. Test quality.** Are the 18 tests adversarial, or largely happy-path with a few negatives?
Does any test assert something that cannot fail? The implementer reports it proved several
tests red by temporarily disabling the guard in source and restoring it — I verified no
`TEMP-DISABLED` markers remain. Judge whether the tests would actually catch a regression.

## Allowed scope

Review only. **Do not edit any file.** You may create scratch files **outside** the repo (or
under `.agent-work/`) to run your adversarial probes — do not leave stray files in `scripts/`,
`tests/`, or `episodes/`, and do not leave episodes behind in the real `episodes/` directory.

## Specific exclusions

- Do not evaluate retrieval — that is g3.
- Do not ask for the retirement layout to be chosen; it is held.
- Do not propose changes to `LESSONS.md`, `apply_lessons_delta.py`, or issue #300's manifest.
- Do not re-litigate the record grammar; it was frozen and reviewed three times at g1.

## Evidence produced (reproduce it)

I independently ran, and all reproduce:

```bash
! python scripts/apply_episode_delta.py --delta tests/fixtures/episodes/misfiled-field-delta.json      # correctly FAILS
! python scripts/apply_episode_delta.py --delta tests/fixtures/episodes/missing-retire-reason-delta.json # correctly FAILS
! python scripts/apply_episode_delta.py --delta tests/fixtures/episodes/newline-injection-delta.json     # correctly FAILS
python -m pytest tests/test_episode_store.py -q    # 18 passed
python -m pytest tests/ -q                          # 1175 passed, 2 skipped (baseline was 1157)
grep -rn "TEMP-DISABLED" scripts/ tests/            # no output — clean
grep -n durable_root scripts/apply_episode_delta.py # 2 hits, both inside a docstring explaining why it is NOT used
```

Use `python`, **not** `py` — `py` has no pytest here and reports "No module named pytest".

## Return format

Return **REVIEW_RESULT** with a literal `VERDICT: APPROVE` or `VERDICT: BLOCK` line, findings
ranked most-serious-first with severities, what you verified as fine, what you could not check
and why, and a Workflow Feedback section.

Reserve `BLOCK` for an unmet close criterion or a genuine defect — a wrong-answer input you
actually demonstrated, not a hypothetical. `APPROVE`-with-findings is right if the criteria are
met and the rest are refinements; say which gate should carry each leftover.

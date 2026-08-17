# Triage candidate: `subTest` can report PASSED while the test body raises

- **Disposition:** `recommend-and-defer`. Not filed (`decision:no-issue-filing`). Not fixed —
  it is repo-wide pytest/unittest configuration, nowhere near lane A's fence.
- **Raised by:** the `g2` implementer crew, against its **own** tests; confirmed as reported
  by the `g2` reviewer, which recorded it without re-deriving it. Relayed here by
  `cmdr-567-a` because it outranks most of what this lane actually fixed.
- **Severity:** the highest of anything this lane touched. **This is a measurement-integrity
  defect**, and every other guard in the repo is downstream of it.

## The observation

While writing tests for `spine_bind`, the implementer measured **four of its own tests
reporting `PASSED` while their bodies raised `AttributeError`.** The raise happened inside a
`subTest` block, and under this repo's pytest configuration the failure did not surface as a
failure.

## Why this is the worst class of defect in this codebase

Constellation's entire quality argument rests on tests discriminating. The doctrine it ships
says so in the strongest terms it has —
`global-orchestrator.md`: *"A check whose output is identical in the healthy and the
defective world cannot discriminate, however correctly it runs."*

A `subTest` that swallows an exception is that failure applied to **the reporting layer
itself**. It is strictly worse than a vacuous test, for a reason worth stating plainly:

- A vacuous test asserts something trivially true. It is at least *honest* about having run,
  and it can be caught by mutation testing — change the code, the test still passes, and a
  careful author notices.
- A `subTest` swallowing an `AttributeError` means **the assertions after the raise never
  executed at all**, and the runner reports success. Mutation testing cannot catch it: the
  mutant is never actually evaluated. The green tick is reporting on a body that stopped.

So this defect is invisible to the one technique this lane relied on most. Note the sequence
in this very lane: mutation testing is what caught the untestable containment root (a
missing *topology*), and mutation testing is exactly what a swallowed raise would defeat.
Every "N tests green" figure in this lane's records — including my own **3263 passed** — is
only as trustworthy as this mechanism.

## What to determine, in order

1. **Reproduce it.** Write a test whose `subTest` body raises `AttributeError` and confirm
   the runner reports PASSED. This is a five-line experiment and it settles whether the
   report is accurate.
2. **Find the cause.** Candidates, in rough order of likelihood: a `pytest.ini` /
   `pyproject.toml` / `setup.cfg` option affecting `unittest` integration; a pytest version
   whose `subTest` support silently drops non-assertion exceptions; a custom
   `conftest.py` hook; or a helper in this repo that wraps `subTest` and catches broadly.
3. **Then measure the blast radius, and this is the part that matters.** Count the `subTest`
   call sites across `tests/` and state the number. Every one is a place where a raising body
   may have been reporting green. `global-orchestrator.md`'s mechanical detector applies to
   the audit itself: *any guard that loops must assert what it looped over* — so the audit
   must state its own count, not just its findings.
4. **Add a guard that cannot itself be swallowed.** A test asserting that a deliberately
   raising `subTest` body **fails** — a positive control for the test runner. If that control
   cannot be written to fail, the runner cannot be trusted and that is the finding.

## Why lane A did not fix it

Out of fence, and correctly so: it is repo-wide test configuration, not
`scripts/mcp_spine_server.py` or `scripts/checklist_engine.py`. Fixing it inside a fenced
lane would also mean changing the measurement apparatus **mid-run**, which would invalidate
this lane's own evidence — the one situation where "fix it now" is clearly wrong.

## Recommended handling

Its own small issue, taken **before** any lane that depends on green-suite evidence. If the
reproduction confirms it, then strictly speaking every green-suite claim in this wave —
mine included — carries an asterisk until the audit in step 3 is done. That is not a reason
to distrust this lane's specific proofs, which rest on **red**-proofs and mutations that were
observed failing (a test observed *failing* is not affected by a mechanism that hides
failures), but it is a reason to treat bare "the suite is green" as weaker evidence than it
looks anywhere in this repo.

## Related

- `map-ids-jsonl-empty-repo-wide.md` — a 148-test suite that was green against an empty map
  because it only ever compared the artifact to a regeneration of itself. Same family:
  a guard that agrees with itself.
- `verify-frame-refuses-every-anchor-when-degraded.md` — a gate that fails the *better*
  artifact. Also the same family: the signal does not mean what its consumer thinks.

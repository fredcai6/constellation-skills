# Review Result — g6 re-review (rework verification)

## Assigned Gate
`g6` — stale-tag detector (issue #456), rework pass on the original BLOCK

## Result
`APPROVE`

## Handoff compliance
The remediation at `cf36071f` addresses all three fixes plus the nit named in
`.agent-work/issue-456/crew-handoffs/g6-remediate.md`, and this re-review verified the fix rather
than re-reviewing the whole gate, per team-lead's instruction. Re-attacked the fix at two disable
points neither the original review nor the crew's own acceptance script used (render.py's
`stale-anchor` interception; the persistence of `span_hash` onto the emitted statement, distinct
from the team-lead's own "constant hash" attack) — both matched a-priori predictions exactly and
both reverted clean under a content-normalized `git diff --quiet` check. Across four independent
disable points now, the fix is genuinely coupled to the feature, not shaped to the two attacks
already known.

## Scope drift
Not re-checked in full this pass (out of scope for a rework-verification re-review); the crew's
own RESULT states the same three files plus the same specific exclusions untouched, consistent
with the original review's own scope-drift finding, which this rework did not touch.

## Evidence verdict
Independently re-confirmed this review: closing selector — collected via `--collect-only`,
**14 test IDs, every one containing `stale_tag`** in its method name, matching a plain run's
**14 passed**; fresh `build` then `check` into scratch `--artifacts`/`--out` — **7/7 exit 0**,
`stale_tags: []`. Trusted team-lead's own independently-reproduced full-suite number (1807
passed / 2 skipped / 684 subtests / 0 failed) rather than re-running the ~8-minute suite myself,
since team-lead is a peer coordinator who already ran it independently and the explicit ask for
this re-review was to spend effort on the adversarial re-attack.

Re-ran the crew's own `g6_disable_attack.py` unmodified: the substantive result matched the
crew's claim exactly (all 5 named tests FAILED under the attack, survivors none, all 5 PASSED
again after revert) — but the script's own `revert_clean` self-check (`git status --porcelain`)
came back `False` on this run despite the revert being byte-perfect, confirmed via `git diff
--quiet` (exit 0) and a matching `git hash-object` blob OID against `HEAD`. This is a false
negative in the evidence script's own self-check under this repo's `core.autocrlf=true` setting,
not a real revert failure — see Out-of-scope observations. Does not change the verdict.

## Code/doc quality
Not re-run in full this pass (Fowler pass is a whole-gate check, out of scope for a
rework-verification re-review); the diff itself is small and targeted — a scoped `try/except`
in `extract.py`, a one-line prefix rename plus a reworded comment in `render.py`, and test-method
extensions/additions in `tests/test_code_map.py`. Nothing in it suggests a new smell worth a
special-case check outside the normal Fowler cadence.

## Map impact verdict
- **Evidence supports claimed change:** yes — every claim in `g6-remediate-RESULT.md`'s Evidence
  section was independently reproduced or directly attacked this review (selector count, guard
  behavior, prefix rename), and the fix held under two attacks the crew did not run themselves.
- **Constraints not violated:** yes — no-timings constraint unaffected (this pass touches error
  handling and print text, not the report schema); full suite green per team-lead's independent
  run; page headers untouched (out of this diff's scope).
- **Notes match the diff:** yes — the RESULT's Scope section (`extract.py`'s read-guard,
  `render.py`'s prefix/comment, five rewritten + two new test methods) matches the diff read
  directly.
- **Decision candidates surfaced:** none required — this is a rework pass with no new authority
  question; the handoff's "explicitly NOT in this pass" list (severity, rename-sensitivity,
  `extract.run()` splitting, the `NamedTuple` suggestion) was correctly left untouched.
- **Durable context routed:** yes — one new triage candidate filed through the engine (`tc3`, the
  evidence script's flaky self-check); `tc1`/`tc2` from the original review close with this
  rework.

## Reconciliation check
No new architecture-level divergence. This pass closes the exact gap the original BLOCK named and
does not introduce a new one.

## Blockers
None.

## Out-of-scope observations
- **`tc3` (new):** `.agent-work/issue-456/evidence/g6_disable_attack.py`'s own `revert_clean`
  self-check uses `git status --porcelain` on `extract.py`, which is unreliable on this repo under
  `core.autocrlf=true` + `.gitattributes`' `text=auto` — reproduced a false `FAIL`/exit-1 on an
  unmodified re-run of the script despite the revert being byte-perfect (confirmed via `git diff
  --quiet` exit 0 and a matching `git hash-object` blob OID against `HEAD`). This is exactly the
  hazard `CREW_CONTEXT.md` itself documents ("never compare two files by raw working-tree bytes —
  compare normalized content or blob OIDs"). Does not affect the shipped fix — `extract.py` is
  genuinely, byte-for-byte what is committed. Fix: swap the `git status --porcelain` check for
  `git diff --quiet -- <path>` (exit 0 = clean); this review's own two new attack scripts
  (`g6-rereview-render-interception-attack.py`, `g6-rereview-persistence-attack.py`) use the
  corrected check as a working example.
- `tc1` (read-before-overwrite crash) and `tc2` (FAIL-text collision) from the original review
  close with this rework — both independently re-verified fixed this pass.

## Workflow Feedback

- **Handoff gaps:** none of substance. The four lettered questions (A–D) plus the two notes gave
  exactly enough structure to attack the fix hard without re-litigating the whole gate — the "pick
  a third disable point" instruction in particular translated directly into two concrete,
  falsifiable attacks with clear a-priori predictions.
- **Context rediscovered:** none beyond what the original review already surfaced.
- **Instructions improvised around:** the engine's `record --finding` CLI argument remains
  impractical for multi-paragraph findings under this worktree's compound-Bash restriction — reused
  the same wrapper-script route (`checklist_engine.main([...])` from a small Python script with an
  argv list) this reviewer's own original review already found. Still works cleanly; still not
  documented as the sanctioned route.
- **What would have made this easier:** discovered mid-review that the crew's own evidence
  script's `git status --porcelain` self-check is non-deterministically wrong on this exact repo
  under its own documented CRLF hazard — a small, reusable helper (e.g. `scripts/git_clean.py
  <path>` wrapping `git diff --quiet`) that every evidence script could import would remove this
  whole class of false-negative from recurring across future gates' acceptance scripts.

## Return status
`complete`

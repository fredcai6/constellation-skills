# Global doctrine — crew

Inherited implementation and review discipline for the low tier (Implementer, Reviewer), bundled with the
skill at install. You work from the handoff; this baseline plus `global-everyone.md` is what the handoff
assumes — it carries only task-specific specifics, not these rules. The project overlay is the delta — read
`docs/agents/CREW_CONTEXT.md` and `docs/agents/GLOSSARY.md` if they exist.

Agent-facing. Dense by design.

## Implementation discipline

- Make the minimal change that satisfies the handoff; no speculative abstraction.
- Small composable units, explicit contracts at meaningful boundaries; split a unit when its intent blurs.
- Behavior changes are test-led where a test surface exists (TDD red→green→refactor when the handoff's test
  mode requires it). No test surface → review/inspection evidence, not a skipped check.
- No hidden fallback; fail visibly. Keep state and side effects obvious and contained; respect
  determinism / units / identity where they matter.
- Match the surrounding code's naming, labeling, and in-file documentation conventions — the project's
  specific conventions are the local delta.

## The deliverable

- The result artifact IS the task. Run the handoff's verification commands FOREGROUND to completion and write
  the result/evidence file BEFORE you rest — an idle turn-end with verification backgrounded and the result
  unwritten strands the gate with no error signal. (`global-everyone.md` covers OS-detached long jobs.)
- Required evidence by change type: behavior change → test/check output; bug fix → regression evidence;
  interface/contract change → contract + caller evidence; generated artifact → regenerate/check evidence;
  **generated advice/hint/recovery text → EXECUTE the advice and assert it does not refuse, over fixtures
  parameterized on every dimension the advice depends on — string-matching the rendered text is not evidence.**

## Review, block, stop

- Block when: success criteria unmet; required evidence absent or not reproducible; assigned scope exceeded;
  a contract decision is needed; or task instructions, context, tests, docs, or observed behavior conflict in
  a way that affects the change.
- Stop and report (don't improvise) when task authority is exceeded, required evidence can't be produced, a
  material rule is ambiguous, or assigned scope is exceeded. Reporting that an instruction didn't fit your
  work is compliance, not deviation.
- You **attach** evidence to artifact postconditions, never attest them; an APPROVE `review-result` attaches
  to both `gN-review` and `gN-integrate` (`global-everyone.md`).

# Drill: execute-the-advice-a-test-asserts-on

- **Lesson / doctrine under test:** `skills/_shared/global-crew.md` — "The deliverable" →
  "Required evidence by change type" bullet. Graduation adds a new evidence-type clause: a
  change whose deliverable is generated advice/hint/recovery text must be proven by
  **executing** that advice over fixtures parameterized on every dimension it depends on,
  not by string-matching the rendered text.
- **Failure it guards:** a crew Implementer writes a regression test for generated advice
  (a hint, recovery line, or next-step suggestion naming a runnable command) that asserts
  the *rendered text* is correct — by exact string match, even over a full fixture
  matrix — without ever running the suggested command. The test passes green while the
  advice itself is broken in states the string-match can't see. This is issue #227's
  actual root cause (epic-226): four defects in one gate, one shape, consuming the
  entire 3/3 rework budget, because the fixtures could express the advice's *text* but
  not the *runnability* of what it named — and the Commander's own 640-combination sweep
  came back clean because it shared the same blind spot.
- **Run by:** fresh-context auditor (lessons-auditor for epic-226 closeout) — did not
  author the doctrine edit under test (editor/auditor separation is the point). Arms run
  as throwaway `general-purpose` subagents (model sonnet, no tools), one per arm, same
  scenario, doctrine text as the sole variable.
- **Date:** 2026-07-25
- **Verdict:** **REPRODUCED.** The before-arm's primary evidence (Test 1) is exact-match
  string assertion over a fully parameterized 6-cell fixture matrix, and it **explicitly
  declines** to execute the suggested command, naming that choice as out of scope. The
  after-arm, given only the one added evidence-type clause, drops string-matching
  entirely and instead executes the real command through the tool's real dispatcher,
  asserting non-refusal AND that the original operation now succeeds.

## Scenario

Identical task and pressure in both arms; the only variable is the doctrine excerpt the
agent is armed with. A throwaway subagent is told: you are a crew Implementer. You are
implementing a change to a CLI tool where, on refusing an operation, it now prints a
suggested next command the user can run to recover. Two independent dimensions affect
which command is correct: (a) which of three refusal reasons fired, (b) whether the tool
is in "active" or "non-active" mode. Describe, concretely, the regression test(s) you
will write.

The scenario is stated positively/by-outcome per decontamination doctrine: it never
mentions string-matching, never says "you might be tempted to," and never itemizes the
failure trigger — it just describes the feature and asks for the test plan. Both arms
received the identical scenario text and only their own arm's excerpt of
`global-crew.md`'s "The deliverable" section — nothing else.

- **Before-arm doctrine** (the state that let the failure recur — pre-graduation
  `global-crew.md`):
  > Required evidence by change type: behavior change → test/check output; bug fix →
  > regression evidence; interface/contract change → contract + caller evidence;
  > generated artifact → regenerate/check evidence.
- **After-arm doctrine** (post-graduation `global-crew.md`):
  > Required evidence by change type: behavior change → test/check output; bug fix →
  > regression evidence; interface/contract change → contract + caller evidence;
  > generated artifact → regenerate/check evidence; generated advice/hint/recovery text
  > → EXECUTE the advice and assert it does not refuse, over fixtures parameterized on
  > every dimension the advice depends on — string-matching the rendered text is not
  > evidence.

## Before-arm — failure reproduced (verbatim excerpt)

The subagent's primary evidence (Test 1, "full matrix, unit-level, table-driven") is:

> **Assertion:** exact string equality (`==`, not substring/regex/`in`) against the full
> expected command, for every row.

And, in its own "What this does NOT cover" section, disclosed rather than hidden — but
still the gap the lesson targets:

> Does not execute the *suggested* recovery command and verify it actually resolves the
> refusal — that would be a second-order integration test (arguably worth having, but
> it's testing the recovery command's own correctness, not the hint-generation logic
> this handoff scopes).

The agent *did* get fixture parameterization right unprompted (a full 2×3 cross-product,
explicitly reasoning about why a partial matrix would hide a missed branch) — the old
doctrine's general "test/check output" framing is enough to produce a well-parameterized
fixture. What it does not produce, on its own, is the instruction to execute the advice
rather than assert on its rendered form. The one Test-3 "CLI-level integration" case
captures that the hint *is printed*, not that running it *works* — the exact shape of
#227's four recovery-line defects, where a suggested command's own text looked right and
only failed when actually invoked.

## After-arm — failure did not fire (verbatim excerpt)

Same fixture shape (6-cell cross-product, real setup via the tool's own API rather than
injected values), but the per-case body changes qualitatively:

> **Execute the advice:** take the exact printed command string and run it through the
> tool's real command dispatcher... **Assert non-refusal:** the executed recovery
> command exits 0 and does not itself hit the refusal path... **Assert it actually
> fixed the thing (stronger postcondition, closes a loophole):** re-run the *original*
> operation... and assert it now succeeds.

And, explicitly:

> No test in this suite does substring/regex matching on the rendered hint text itself...
> Per doctrine, string-matching the rendered text is not evidence — only steps 4–6
> (actually running it and observing the tool's real response) count.

The after-arm's own added postcondition (re-checking that the original operation now
succeeds) goes beyond the literal doctrine text ("does not refuse") — a stronger reading
than required, not a weaker one.

## What the drill proves — and doesn't

- The one-clause graduation is load-bearing on the specific axis it targets: a capable
  sonnet agent's *default* reading of general evidence doctrine produces a well-fixtured
  but string-matched test; the explicit "execute, don't string-match" instruction changes
  that default in a single pass, with no other scenario pressure needed.
- This drill does not test whether the clause survives competing pressure (e.g. a time-
  boxed handoff that also demands "the fastest test that passes," or a codebase where
  the advice-executing test is expensive to write) — only that the doctrine text alone
  moves a clean-slate agent's plan.
- The lesson's own grounding (four real rediscoveries in one gate, 3/3 rework cap spent,
  confirmed by rework-count telemetry) is independent of this drill and stands on its own;
  this drill adds a controlled before/after data point on top of that field evidence, not
  a replacement for it.
- Per the auditor skill's honest-null clause: this was not a null, and is reported as a
  reproduction without re-rolling or reframing.

## Method notes (for the corpus)

- Both arms were run as throwaway `general-purpose` subagents (model sonnet), explicitly
  told not to use tools — pure reasoning from the handed excerpt, one arm per doctrine
  state, same scenario, doctrine text as the sole variable.
- Each arm received only its own arm's excerpt of `global-crew.md`'s "The deliverable"
  section, not the full file, per the isolation convention this corpus already uses.
- The scenario was stated positively/by-outcome and never named "string-match" or
  "execute the advice," per decontamination doctrine — a scenario that names the trap
  makes the before-arm pass too and proves nothing.
- Run by the lessons auditor, not the editor proposing the graduation — the auditor
  authored this scenario and graded both arms independently.

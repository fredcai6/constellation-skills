# Implementer Handoff

## Gate
`g3-implement` — issue #467, epic #418. Work area `.agent-work/issue-467-trip-semantics/`,
branch `epic-418/a2-467-trip-semantics`, worktree `C:/Programs/constellation-skills-wt/epic418-a2-467`.

## Task

Ship a **per-gate, tighten-only context-headroom override**, and exercise it once for real.

**(a) `gauge_reader.thresholds_for(model, headroom_tokens=0)`** subtracts an absolute-token reserve
from **both** caps before dividing by the window, **clamped at 0** so an override can only
**TIGHTEN**, never loosen. Today the signature is `thresholds_for(model)` at
`scripts/gauge_reader.py:124`; the profiles table is at `:76`. For `claude-opus-5` the profile is
`(1_000_000, 80_000, 150_000)` — window, soft cap, hard cap, all tokens.

**(b) `checklist_engine` resolves the reserve with a SINGLE reader**, from
`tasks.<gate>.context_headroom_tokens` **only**. There is **no** checklist-config tier — it would
have zero users, and one adapter is a hypothetical seam. A missing, malformed, or negative value
resolves to **0**.

**(c) The SAME resolver feeds both the advisory and the begin-work guard**, so the number the agent
is **shown** and the number it is **judged against** cannot diverge. g2 already established
`_trip_hard_band_reading` as the single place deciding "at/over hard" — extend that, do not add a
second path.

**(d) Exercise it once for real.** The commander spine template's **`execute`** gate carries a
headroom reserve: `skills/commander/templates/COMMANDER_SPINE.template.json`. It is the run's
longest gate, and its imperative already tells the agent in prose to ensure context headroom before
entering — so the reserve makes an existing prose instruction enforceable.

## Protected Intent

A gate that is known to be expensive must be able to say **"I need more room than the default"** and
have the governor enforce it — while remaining structurally incapable of saying "I need less". The
production default is a floor no gate may lower.

## Test Mode

**TDD required**, with mutation testing on every guard shipped.

## Close Criteria

- (a) `thresholds_for` takes `headroom_tokens=0`, subtracts from **both** caps, clamps at 0.
- (b) One resolver, gate-level only, missing/malformed/negative → 0.
- (c) The advisory and the begin-work guard read the **same resolved number**.
- (d) The spine template's `execute` gate carries a reserve, and the installer/template tests stay
  green.
- **Tighten-only is unreachable to violate**: a negative or hostile override cannot raise a
  threshold.
- **An override on an uncalibrated model falls back to the default** rather than computing against a
  guessed window (#252 — an uncalibrated `claude-opus-5` once read ~5x high and tripped the governor
  at ~14% of its real window; do not reintroduce that path).
- Every mutation turns its **named** test red, with total counts stated.
- The suites in Verification Commands are green.

### Test naming — load-bearing, the gate cannot close without it

The `g3-integrate` closeout runs this exact command, and pytest exits **5** on an empty collection:

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py -k 'headroom or override'
```

**Every new test must have a name matching `headroom` or `override`.** Frozen selector, not a style
preference.

## Two tests that cannot fail unless you build them exactly as specified

These are the two places this gate is most likely to ship something worthless. Both are frozen
requirements, not suggestions.

**1. THE NEGATIVE-ONLY TEST CANNOT FAIL.** A test asserting that a malformed or negative override
resolves to the default **passes with the entire mechanism dead-coded** — resolve-to-default is what
a missing feature does. So that test must, **in the same test**, also assert that a **well-formed**
override resolves to a **different** number **through the same resolver**. One test, both
assertions.

**2. THE ADMIRAL'S BINDING CONDITION — DC4 is met only by the "and not its neighbours" half.**
A test proving only that the overridden gate trips earlier **has not met DC4**. The failure mode
DC4 exists to guard against is 68 hand-authored ungraded placeholders, and **only the neighbour
assertion discriminates against it**. The neighbour-isolation test must assert **both sides by
name** — the overridden gate's behaviour changes **AND** a named neighbour gate's does not — **at
the same fill, on the same model**.

## Allowed Scope

- `scripts/gauge_reader.py` — `thresholds_for` (:124) and its docstring.
- `scripts/checklist_engine.py` — the Trip section's threshold call sites, and the new resolver.
- `skills/commander/templates/COMMANDER_SPINE.template.json` — the `execute` gate only.
- `tests/test_gauge_reader.py`, `tests/test_checklist_engine.py` — new tests, and minimal
  reconciliation of existing tests that call `thresholds_for`.
- `tests/test_init_work_area.py`, `tests/test_install_constellation.py` — **pre-authorized** for
  minimal reconciliation only, because the spine template change in (d) may ripple into template or
  installer fixtures. Reconcile them if the template edit legitimately requires it; do not otherwise
  touch them.
- `.agent-work/issue-467-trip-semantics/g3-mutation-log.md` — the mutation log.

## Specific Exclusions

- **Do NOT edit `_PROFILES`** (`scripts/gauge_reader.py:76`). The graded default stays exactly one
  table. This is the production default and it is not yours to change.
- **Do NOT ship a checklist-config tier.** Gate-level only.
- **Do NOT hand-author an override on every gate.** That would invent 68 ungraded placeholders —
  precisely the failure DC4 guards against. **Exactly one real gate carries one.**
- **Do NOT compute threshold arithmetic in the engine.** See Constraints.
- Do not re-open anything g2 shipped (`TRIP_HARD_GUARDED_VERBS`, the no-silent-close rule, the
  advisory wording). g2 is closed and reviewed.

## Constraints

- **TIGHTEN-ONLY is a safety property, not a style choice.** An override that could loosen a
  threshold would let a gate opt out of the governor. Make loosening structurally unreachable, not
  merely untested.
- **Threshold ARITHMETIC lives in `gauge_reader`** — the module that owns the window and the caps.
  The engine passes a **token count** and reads back a **fraction**; it computes no threshold.
  Recording the fraction `gauge_reader` returned is not arithmetic and does not breach
  `constraint:no-threshold-values`.
- **`thresholds_for` must stay a TOTAL function.** `_DEFAULT_PROFILE` exists only to keep it total
  for an arbitrary model string. Do **not** reintroduce it as a fallback on the **reading** path —
  an uncertain model must yield **no reading**, not a wrong one.
- **MUTATION-TEST EVERY GUARD**, including the tighten-only clamp and the neighbour isolation. Each
  log line names (i) the branch broken, (ii) the **NAMED** test that failed, (iii) the **total**
  failure count. Log to `.agent-work/issue-467-trip-semantics/g3-mutation-log.md`.
  **If a branch has no narrow mutation, say so and decline to claim specificity.** The g2
  implementer did exactly that for its M11 and the reviewer confirmed it was the right call after
  trying two narrower candidates itself. An honest declared limitation is a better outcome here than
  a 47-failure mutation dressed as proof.

## The reserve value in (d) — read this before you pick a number

`decision:execute-gate-reserve-value` is graded **`@grade: guess`**. It is the one thing in this
gate that is *not* settled, and it is deliberately revisable.

- Pick a defensible number, and **state your reasoning in a comment next to it**. Do not present it
  as measured, and do not invent a false provenance for it.
- Useful calibration: `claude-opus-5` is a 1M window with an 80K soft / 150K hard cap. The commander
  driving this run was at ~127K fill after resuming cold and driving one full three-task gate.
- **The named settle experiment is not runnable from existing artifacts, and I confirmed that
  myself:** it calls for reading `fill_fraction` from `.agent-work/*/gauge.json` at the moment
  `execute` was started, but `gauge.json` holds only the **latest** reading, and the per-gate
  context manifests under `.agent-work/*/context/` record **no fill value** at all. So do not try to
  settle it; I am reporting that gap to the Admiral, who routes it.
- The grade is `guess`, so a later run may revise your number in place without coming back to me.
  Make that easy: one obvious place, clearly commented.

## Map Anchors (inbound)

- **Structural:** `scripts/gauge_reader.py` — `thresholds_for` (:124), `_PROFILES` (:76),
  `_DEFAULT_PROFILE`. `scripts/checklist_engine.py` — the Trip section's threshold call sites (and
  `_trip_hard_band_reading`, added at g2, which is the single at/over-hard decision point).
  `skills/commander/templates/COMMANDER_SPINE.template.json` — the `execute` gate.
- **Capability:** Trip thresholds — today global-per-model; gains a per-gate tighten-only reserve.
- **Constraints/assumptions:** `constraint:no-threshold-values` — the engine does not COMPUTE
  thresholds. `constraint:tighten-only` — no override may raise a threshold.
  `constraint:global-default-untouched` — `_PROFILES` is out of scope.
- **Decision anchors:**
  - `decision:gate-headroom-absolute-tokens` — the override is an absolute-token reserve, not a fill
    fraction. All three independent design candidates converged: `_PROFILES` is already intent-first
    absolute because context-rot degradation tracks absolute token count, not window fraction, so a
    fractional override would reserve 5x more room on a 1M model than a 200K one from the same
    authored number.
    `@grade: settled/measured · leans g3-implement,g3-review`
  - `decision:headroom-not-cap` — the override states what the GATE needs, so it survives a change
    to the production default.
    `@grade: settled/measured · leans g3-implement`
  - `decision:no-config-tier` — gate-level only; the checklist-config tier is not shipped.
    `@grade: settled/measured · leans g3-implement`
  - `decision:execute-gate-reserve-value` — the token reserve carried by the spine's `execute` gate.
    `@grade: guess · leans g3-implement · settle: read fill_fraction across completed commander runs
    at the moment execute was started` — **and see the section above: that experiment is not
    runnable from existing artifacts.**

  The first three are `settled/measured` — not yours to revise; contradict one and you stop and
  return it as a decision candidate. The fourth is a `guess` — yours to author.
- **Evidence expectations:** `claim:dc4-neighbour-isolation` — at one fill, on one model, the
  overridden gate's behaviour changes and a NAMED neighbour's does not. Asserted on both sides.
- **Map confidence flags:** The launch order's role-blindness reading (crews trip at 17-21%, the
  Admiral ran to 44% untripped) is **CONFOUNDED and has been formally RETRACTED by the Admiral**.
  `docs/GAUGE_WRITER_HOOK.md` records that an orchestrator holding several spines under one key
  writes **no reading at all**, and the engine's own projection reported CONTEXT GAUGE SILENT at
  that path. **Do not use it for anything** — not to justify a threshold value, not as supporting
  evidence. Record it if you must; do not act on it.

## Deliverable Path Check

All **Committed**; `git check-ignore` exits 1 for each (`.agent-work/` is tracked in this repo).

- **Committed** — `scripts/gauge_reader.py`, `scripts/checklist_engine.py`,
  `skills/commander/templates/COMMANDER_SPINE.template.json`, `tests/test_gauge_reader.py`,
  `tests/test_checklist_engine.py`
- **Committed, new** — `.agent-work/issue-467-trip-semantics/g3-mutation-log.md`. Untracked until
  staged, so it appears in `git status` rather than `git diff`.

## Required Evidence

**Load-bearing — prove rigorously:**

1. **The neighbour-isolation test**, showing both named sides asserted at the same fill on the same
   model. Paste the test and its run.
2. **The tighten-only clamp is unreachable to violate.** Try to loosen a threshold and show you
   cannot. A test that merely asserts the clamp's happy path is not this.
3. **The malformed/negative test carries its positive assertion in the same test**, through the same
   resolver, resolving to a different number.
4. **The advisory and the guard read the same resolved number** — demonstrated, not asserted.
5. **The mutation log**, with per-mutation total failure counts.

**Confirmatory — spot-check:**

6. Uncalibrated-model fallback behaves.
7. `_PROFILES` untouched (`git diff` on that region).
8. No checklist-config tier exists.

Quote exact expected strings so tests assert equality. Derive any failure distribution mechanically
(`pytest -q | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`).

## Wiring Grep

Required. One command naming every symbol this slice adds, showing a call site outside its own
definition and outside any `--self-test` path. **State the count. Zero external call sites is a stop
condition** — and note that (c) makes this sharper than usual: a resolver the *advisory* calls but
the *guard* does not is exactly the divergence this gate exists to prevent, so show **both**
call sites.

```bash
grep -rn "<each new symbol>" --include=*.py . | grep -v "def <symbol>" | grep -v self_test
```

## Verification Commands

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py tests/test_init_work_area.py tests/test_install_constellation.py
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py -k 'headroom or override'
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

The second is the frozen `g3-integrate` closeout selector — run it and confirm it collects your
tests. The full suite baseline after g2 is **1815 passed, 2 skipped, 683 subtests**; explain any
delta.

## Suggested Model Tier

**Stronger.** Safety property, a frozen Admiral condition, and two tests that pass vacuously if
built naively.

## Authority

Settled, do not re-open: absolute-token reserve (not a fraction); headroom-not-cap; no config tier;
`_PROFILES` untouched; exactly one gate carries an override; tighten-only.

Yours to author: the reserve **value** in (d), graded `guess`.

**You must not decide alone:** anything that would let an override loosen a threshold, adding a
config tier, editing `_PROFILES`, putting threshold arithmetic in the engine, or weakening the
neighbour-isolation assertion.

## Stop Conditions

Stop and return if: allowed scope must be exceeded, a specific exclusion must be touched, required
evidence cannot be produced, a decision outside the given authority is needed, or the
neighbour-isolation test cannot be made to assert both sides.

## Return Format

Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced,
assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.

**State the reserve value you chose and your reasoning for it explicitly** — I am required to carry
it and its settle experiment up to the Admiral.

Write your result to
`.agent-work/issue-467-trip-semantics/crew-handoffs/g3-implementer-result.md`.

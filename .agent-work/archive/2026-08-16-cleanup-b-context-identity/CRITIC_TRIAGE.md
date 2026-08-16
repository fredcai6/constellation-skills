# Cold plan critic — findings triaged

Panel-vs-single: **single critic**, surfaced as the choice it was. The artifact is
a gate plan for one bounded issue, not an epic-spawning design, so the default
single applies; the launch order's own pre-rulings already carry the
architecture-level decisions this plan executes under.

Verdict returned: **PROCEED-WITH-CHANGES**. Every finding is disposed of below.
The critic did not self-triage; these dispositions are the Commander's.

| # | Sev | Disposition |
|---|---|---|
| F1 | high | **ACCEPTED — and it forces a float.** Correct and load-bearing. `engine_session` is a lease name, not an agent identity, and a relaunch reuses it by design. The claim that B retires #601's timestamp comparison was false; it is **retracted** in `PLAN_ALTERNATIVES.md`. Because the pre-ruling `decision:identity-not-time` is `@grade: settled/human`, a measured contradiction is not mine to revise → `FLOAT_TO_ADMIRAL.md`. |
| F2 | high | **ACCEPTED, with the measurement carried up.** 82/395 real session ids fail the proposed allowlist, 2 live binding entries are null, one is `'$SID'`. Design changes from *reject an unusable owner* to **normalize** it. Carried into the float because it changes what "identity" means, and because F2's cost is invisible to every check (losing the governor never fails a test). |
| F3 | high | **ACCEPTED.** The rename re-arms the `len(gauge_paths) > 1` guard that #488's path-dedup disarmed, reintroducing the "Admiral's governor dark for an entire wave" regression. The dedup key becomes an explicit design decision, with a red-before test (two spines, one binding key, one work directory). Added to the float's fact list and to the plan's open decisions. |
| F4 | medium | **ACCEPTED — my error, corrected in place.** The sidecars use *constants* (`SKIP_FILENAME`, `UNCALIBRATED_FILENAME`) on both sides, so they do not follow the gauge name. `PLAN_ALTERNATIVES.md` now says so. Whether sidecars go per-owner is a named cost. Also accepted: reserve `skip`/`uncalibrated` as owner names — both pass the allowlist and would collide. |
| F5 | medium | **ACCEPTED.** `_uncalibrated_advisory` and `_no_reading_advisory` take `base_dir` only and sit outside the trip region; leaving them on the shared path would have them report on a file nobody reads. The g1 imperative must name the advisory family and say what it resolves to. Folded into the plan rework. |
| F6 | medium | **ACCEPTED.** `g1-implement`'s single postcondition reads the crew's own status field. Adding the two proposed command postconditions: fenced paths unmodified (`git diff --name-only` over the four fenced files, empty), and no read/write path resolving the literal `gauge.json`. |
| F7 | medium | **ACCEPTED.** `g1-integrate` c3's *statement* names a comparison against a re-measured `main` baseline; its *command* measures one side. Exactly the one-sided-enumeration shape. Split into two conditions: the suite result, and an attested baseline diff with both numbers recorded. |
| F8 | medium | **ACCEPTED.** c1 runs four suites that already pass, so it cannot discriminate the healthy from the broken world without a failing-first test — which nothing required. A named new test, cited by node id in the condition statement so it can be run against the merge base, becomes a postcondition. |
| F9 | low | **ACCEPTED.** `test -f` → `test -s`, plus a grep for a field only a live capture carries (`path_source` in the binding capture, `observed_at` in the gauge). Inconsistent with g2's own `test -s`, so this was sloppiness rather than a judgment. |
| F10 | low | **ACCEPTED.** `g2-design-500` c1 greps for a token the imperative itself supplies. `DESIGN_500.md` now carries an explicit **NOT SUFFICIENT** verdict token for the check to grep, which is a fact about the answer rather than about the question. |
| F11 | low | **ACCEPTED with a ruling.** The blast radius is enumerated but nothing said who updates what. Ruling: `tests/test_spine_rail.py` (2 occurrences) is the test of a **fenced** module that lane C is editing concurrently — this lane does **not** touch it; the coupling goes to the Admiral as a cross-lane note. `episodes/**` are historical records and are never edited. Everything else in the radius gets an explicit change/no-change disposition inside g1. |

## Two things the critic got right that I want on the record separately

- **The probe's stored artifact will lie after the fix.** Post-change there is no
  `gauge.json`, so `probe_cross_key.py` takes the `after_sub is None` branch and
  prints "VERDICT: NEITHER", which misdescribes the *fixed* world to anyone
  re-running the archived artifact. The closed gate does not turn red (stored
  `satisfied` is never re-checked), so this is a misleading-artifact problem, not a
  gate problem. **Fix it in the probe when the design lands**, not before — the
  probe must keep describing the *current* world truthfully until then.
- **A runtime coupling to lane C.** The design depends on
  `spine_rail.is_usable_agent_id`; if lane C changes that predicate the gauge
  filename alphabet changes under this lane. Reading the module is permitted, but
  the coupling is now stated rather than implicit. Cross-lane note to the Admiral.

## Counts, so this is not an under-inclusive sweep

The critic enumerated **all 11** postconditions in `execute.json` and named **6**
as vacuous or near-vacuous (F6–F10 plus `g1-review` c1, which any verdict
satisfies including BLOCK). It confirmed **1** as genuinely discriminating
(`g0-measure` c1) and classified **3** as ordinary attestations. 11 = 6 + 1 + 3 +
`e0-context` c1. All 11 findings above are disposed of; none is deferred silently.

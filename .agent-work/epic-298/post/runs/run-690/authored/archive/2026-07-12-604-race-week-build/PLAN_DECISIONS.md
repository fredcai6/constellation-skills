# Plan-level design-it-twice note

**Scope distinction (per cmdr-604d precedent):** the *content*-level design-it-twice (comparing
seam candidates A/B/C) already ran in full at Wave 1 (3 parallel candidate authors + cold critic,
PR #612) and is FROZEN by owner ratification. This note covers only the *plan*-level decomposition
— how to slice the BUILD into gates — which is a much lower-risk, largely mechanical call given the
stage shape is fixed.

## Gate-decomposition alternatives considered

1. **Single combined gate** (one implement/review pass for stage-lib + CLI together). Rejected:
   the stage-library (checkpoint I/O, hashing, 4 stage functions) and the CLI dispatcher
   (subcommands, resumption orchestration, arg threading) are independently testable and the
   "smallest reasonable bite" guidance favors splitting; a single gate risks a large diff that's
   harder to review atomically.
2. **Three-way split** (checkpoint/hash core | stage functions | CLI dispatcher). Considered, but
   the checkpoint/hash core has no independent value without at least one stage function to prove
   it against — collapsing those two into one gate (both are pure-function, fixture-testable, no
   process boundary) avoids a gate whose sole deliverable is infrastructure with nothing yet using
   it.
3. **Chosen: two crew gates + one reasoning gate.** G1 = `race_week_stages.py` (checkpoint I/O +
   hash-skip logic + all 4 stage pure functions + their unit tests) — one coherent, independently
   testable library. G2 = `scripts/race_week.py` (CLI dispatcher: `collect-check`/`predict`/
   `optimize`/`explain`/`run` subcommands, arg parsing incl. `--lane`/`--db-path`/`--db-root`,
   wiring to G1's library, resumption glue) + CLI-level tests. G3 = the R9 end-to-end proof —
   authored as a **reasoning gate** (no crew dispatch): it is verification/diagnosis over code that
   already exists after G1+G2, run directly in this context so I hold first-hand evidence of the
   real top-10 output, matching doctrine's "reasoning gate" carve-out (deliverable is diagnostic
   evidence, not new code).

**Untaken road (named, not silent):** a full parallel-subagent plan-alternatives panel (2+ authors
drafting competing gate plans) was skipped. Rationale: the interface this plan builds against is
already frozen and was itself panel-reviewed at Wave 1; the remaining decision (how many gates,
what's in each) is bounded, mechanical, and low-blast-radius (all three gates operate inside the
same `scripts/`+`tests/` fence with no architecture exposure). A single authored plan + one cold
critic pass (dispatched below) is judged proportionate. This is a **scaled-down**, not skipped,
application — surfaced per doctrine's "count/panel scaled by weight, a surfaced choice."

## Cold plan critic

Dispatched as a subagent with the mission frame + this draft plan only (no authoring context, no
access to my reasoning above beyond what's written in the artifacts handed to it). The critic
independently re-verified every cited seam signature against source (including spot-checking both
sqlite DB files directly) and confirmed all citations accurate. Real findings, all fixed in
`execute.json` before dispatching any crew:

- **BLOCKING**, fixed: G3's single `check: null` postcondition covered 6 distinct claims behind one
  blanket attest — split into 6 separately-attested postconditions (c1-c6), each requiring specific
  pasted evidence.
- **SIGNIFICANT**, fixed: g1-implement's imperative described the optimize stage as calling
  `generate_report` THEN `write_beam_search_report` — wrong; `generate_report` already calls
  `write_beam_search_report` internally (`artifacts.py:227`) and writes both JSON+MD itself. Fixed
  the imperative to say so explicitly and warn against a double-write.
- **SIGNIFICANT**, fixed: hard/soft gate ordering (run aborts before explain on predict/optimize
  failure) was asserted but untested. Added a failure-injection test requirement to g2-implement.
- **SIGNIFICANT**, fixed: G3's resumption item 6 let `--force` substitute for exercising the actual
  hash-invalidation path. Split into c5 (unchanged -> skip) and c6 (real upstream content change,
  explicitly NOT `--force` -> the affected stages actually recompute, hashes differ).
- Minor, addressed: added an invalid-`--race` handling test to g2-implement (must propagate a clear
  `ValueError` from `get_calendar(year).index(gp_name)`, not swallow it).

**Verdict: PROCEED WITH FIXES** — fixes applied above; plan proceeds to crew dispatch.

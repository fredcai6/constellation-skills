# Triage recommendations — issue-99

## T1. Critical-review spine-postcondition symmetry
- **Class:** unresolved decision / tooling
- **What:** the spine plan task's new c4 attests both rigor mechanisms (plan-alternatives AND cold plan critic) under one postcondition; the critical-review standard has no engine hook of its own — the critic can't be separately attested, waived, or audited.
- **Evidence:** COMMANDER_SPINE.template.json plan task (this run's g1); flagged by plan-critic finding S9/IF3 and independently by the g1 implementer; queued as tc1 at g1-integrate.
- **Acceptance:** either c4 split into per-mechanism postconditions, or an explicit doctrine note that one attest covers both — decided, not defaulted.
- **Disposition:** **fixed-now, commit 5fad3e3** (human ruling: "splitting seems right; come up with alternatives, then hand to panel"). c4 = alternatives-before-freeze or loud skip; new c5 = cold critic on the converged candidate, after alternatives and before approval, findings human-triaged, panel choice surfaced. Ordering (generate → then critique) encoded in both statements. First redo reverted for whole-file json.dump format churn; final diff is surgical (2+/1-).

## T2. init_work_area --skill-dir verbatim substitution writes broken spines
- **Class:** bug (dogfood tooling)
- **What:** an explicit --skill-dir was substituted into spine command checks with no validation; in the source repo (scripts vendored at root) this produced check paths under nonexistent skills/<name>/scripts, forcing a mid-init re-materialization.
- **Evidence:** this run's init step (first materialization failed c1); root-caused to _resolve_skill_dir_token's unvalidated explicit branch.
- **Disposition:** **fixed-now, commit 6aa64be** — refuses visibly when the template references `<token>/scripts` and the given dir has no scripts/; regression test added; suite green (443 passed).

## T3. Superpowers execution-discipline imports (roadmap)
- **Class:** research hardening / feature
- **What:** evaluate importing superpowers' execution-phase strengths where constellation is thinner: durable progress ledger that survives compaction (vs our STATE_NOTE + crew registry), file-handoff hygiene for controller-context economy, explicit model-tier selection per role, pre-flight plan-conflict scan.
- **Evidence:** 2026-07-09 research synthesis (superpowers 6.1.1 review): design phase — constellation ahead; execution discipline — superpowers ahead. This run closed the design-phase gap (design-it-twice generalization, #99).
- **Acceptance (when picked up):** per-mechanism comparison against existing constellation equivalents; import only where a real gap exists (deletion-test each candidate); no wholesale adoption.
- **Disposition:** **recommend-and-defer — roadmap note at docs/ROADMAP.md** (human ruling 2026-07-09: "make a future roadmap note, we're going to be digging into that sort of thing soon"); deliberately NOT filed as an issue.

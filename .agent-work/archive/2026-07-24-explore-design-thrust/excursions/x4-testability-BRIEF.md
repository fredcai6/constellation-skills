# Excursion Brief: `x4-testability` — how do we make skills and the engine testable, near-term?

## The one named question

What is the cheapest *robust* near-term way to make constellation skills and the checklist engine testable — such that we can say "what we're doing makes sense" with evidence rather than vibes?

## Type

research

**Why this type:** inventory + prior-art survey + recommendation; prototyping would be a follow-up.

## What "answered" looks like

A report with three parts, landing at `.agent-work/explore-design-thrust/excursions/x4-testability-RESULT.md`:
1. **Inventory of what exists** in C:\Programs\constellation-skills: engine/script test coverage (look at tests/, any pytest suites, recent test commits), the eval runner (`run_skill_eval.py`, issues #136 evals-per-skill and #205 eval runner fixes), install-fingerprint tests, curator measurement scripts. What is actually covered vs not — derive coverage claims from commands, include the commands.
2. **Prior art**: how do other agent-skill ecosystems test skills/prompts (eval harnesses, behavioral evals, golden transcripts, CI patterns for prompt regressions)? Cited.
3. **Recommendation, honestly graded**: a ranked near-term plan. Human constraints: (a) the ENGINE itself must be extremely robust — unit/property tests on checklist_engine.py verbs are non-negotiable table stakes if gaps exist; (b) portability: the hardcoded `py` launcher keyword breaks on non-Windows setups and burns agent tokens — assess how launcher resolution should work (env probe? config? wrapper script?); (c) if full skill-level behavioral testing is impractical near-term, SAY SO — the weekly iterative cleanup cadence may be good enough, and an honest "not worth it yet" beats a flaky harness.

## Budget / stop conditions

- Budget: ~40 min; report even if partial.
- Read-only in the repo; modify nothing but the result file.
- **Scoped nulls:** every negative states what was and was NOT examined.

## Research excursion

- **Sources:** the repo itself first (tests/, scripts/, evals/, .github/workflows if any); then web for agent-skill eval prior art (Anthropic evals guidance, promptfoo/braintrust-style harnesses, skill-testing writeups).
- **Findings format:** claims cited (file paths / URLs); coverage counts command-derived, commands included.

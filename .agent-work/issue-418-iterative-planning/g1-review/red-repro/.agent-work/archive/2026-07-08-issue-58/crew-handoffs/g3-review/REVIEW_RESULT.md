# Review Result — g3 (constellation-prototyper)

## Verdict: APPROVE

Commit `b54a1eb` on `constellation/issue-58`. All nine review checks reproduced independently and passed. No blockers.

## Per-check findings

| Check | Status | Note |
|---|---|---|
| Diff scope | PASS | 6 NEW files, 194 insertions, all under `skills/prototyper/`; porcelain clean; commit on `constellation/issue-58`; no excluded path touched. |
| Spec fidelity (Chosen design 2, line by line) | PASS | Every clause present — see below. |
| measurement.md pointer-not-restatement | PASS | Points to real doctrine; quote verified verbatim; no duplication. |
| Grep invariants + genuine scoped-nulls | PASS | `NOT tested`/`disposition`/`scoped` all present; scoped-nulls is real doctrine. |
| RESULT template fields structural | PASS | NOT-tested and disposition are real headings, not soft prose. |
| HANDOFF fields enumerable for g4 freeze | PASS | Six `##` headings, one per field. |
| Frontmatter/name | PASS | `constellation-prototyper`; name+description only, matches siblings. |
| Register vs siblings | PASS | 64 lines; dense, doctrine-justified. |
| Full-suite failure attribution | PASS | 31 failures, single waived signature; reproduced. |

### Spec fidelity detail
Role/tier crew-tier + handoff-driven + no engine checklist + three dispatch contexts (SKILL.md l.8, l.10). Core doctrine all six clauses (l.14-22). Logic branch: pure portable I/O-free module + throwaway TUI (logic.md). UI branch: 3-5 structurally different variants, `?variant=` switcher, floating cycle bar, real-page mounting preference (ui.md). Measurement: scoreboard-first, one mechanism, number on the board (measurement.md). Location split by driver: human-driven in-repo / agent-driven worktree (l.43-49). Closeout with exactly three disposition values deleted / absorbed-with-commit-ref / parked-with-owner (l.51-59).

### The two care points, independently verified
1. **Scoped-nulls is genuine doctrine, not a grep token.** SKILL.md l.24-30 carries scoped verdicts (concrete example: "this reducer shape thrashed on concurrent edits, tested single-threaded only"), a mandatory `NOT tested` line, the default-next-move-is-another-variant rule, and the impossibility-needs-class-spanning-evidence claim. The same doctrine is echoed as "Scoped verdict" sections in logic.md and ui.md. Real doctrine.
2. **measurement.md points, does not restate.** It cites `skills/_shared/global-orchestrator.md` and quotes it; I confirmed the phrases "a tested **scoreboard** gate first" and "Keep losers as documented negative results" are present verbatim in that file's "Shaping and ordering" section. measurement.md adds only the crew-side contract (one-spike-one-metric, worktree location, scoped null, mandatory disposition) — no duplication of the sequencing doctrine.

## Full-suite reproduction (the third care point)
`python -m pytest tests/ -q` → **31 failed, 389 passed, 1 skipped, 14 subtests passed** — matches the implementer's claim exactly. Attributed every failure myself: all 31 carry the single signature `InstallError: source skill is missing SKILL.md: ...skills\explorer`, raised at `scripts/install_constellation.py:153` during install discovery. Per-file split (5 `test_feedback_tooling`, 26 `test_install_constellation`) is one root cause, not two problems — every install-dependent test crashes at the same discovery abort. This is waived class 1 (missing explorer SKILL.md, g4). Waived class 2 (expected-skills-list drift from the now-existing `constellation-prototyper`, g5) is genuinely **masked**: the discovery abort fires before any expected-list assertion executes, so class 2 is not yet observable — consistent with the implementer's masking note. **Zero failures fall outside the two waived root-cause classes.** (`skills/_shared/` also lacks a SKILL.md but is the shared-reference dir, correctly skipped by the installer — not a discovery target, not a failure source.)

## HANDOFF field freeze for g4 (the fourth care point)
The six fields are cleanly enumerable, one `##` heading each: **Question / Branch / Host-project conventions / Location / Stop conditions / Return format**. No prose-buried or ambiguous fields. Safe to freeze for g4's EXCURSION_BRIEF prototype-section alignment. Two benign elaborations noted below.

## Blockers
None.

## Out-of-scope observations
- measurement.md refers to the target as "the decomposition/sequencing section"; the actual heading is "## Shaping and ordering". The verbatim quote keeps it locatable, so this is cosmetic, not a defect — worth a one-word touch-up if the file is ever reopened, not now.
- HANDOFF "Host-project conventions" carries a 4th sub-bullet ("Other conventions") beyond the spec's bare `(runtime, task runner, routing)`. Benign superset; g4 mirrors the six top-level headings, and the sub-bullets are guidance, not the frozen contract.
- SKILL.md leans on deep-module vocabulary ("adapter", "seam", "deep by construction") that g5 will add to `global-crew.md`. Used lightly and self-containedly here; aligns without edits when g5 lands. No action.

## Workflow feedback (run-specific)
The handoff's care point #4 — "HANDOFF field names freeze at gate close, ambiguity is a finding now or never" — is the right kind of forcing function and it held: it made me check enumerability as a first-class gate rather than a nicety, and the template passed cleanly. One concrete improvement for the g4 reviewer handoff: state explicitly that the frozen contract is the **six top-level headings only**, and that the sub-bullets under Host-project conventions (and the "Why this branch"/"Driver" helper lines) are non-contractual guidance. Without that boundary a g4 reviewer could over-read the sub-bullets as part of the freeze and flag a harmless EXCURSION_BRIEF divergence as a contract break. Separately, the single-signature masking dynamic (class 2 hidden behind the class-1 discovery abort) is subtle enough that it is worth carrying forward verbatim into the g3-integrate handoff, exactly as the implementer suggested — the absence of expected-skills-drift failures is the *correct* g3 state, not evidence prototyper was skipped by discovery.

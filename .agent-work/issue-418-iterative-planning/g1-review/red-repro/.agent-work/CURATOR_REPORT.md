# Curator Report — weekly health pass 2026-07-27

Both instruments run. 6 project exports swept, ~20 distinct findings triaged, 6 exports cleared.
Prior report archived at `.agent-work/archive/curator-reports/CURATOR_REPORT-20260724.md`.

## Headline: a prior sweep's "resolved upstream" ruling was wrong

The 2026-07-17 sweep cleared `engine-artifact-attest` as resolved in all six projects. An f1Brainz
closeout audit challenged that. **The challenge is correct.** Verified against repo HEAD *and* the
global install (byte-identical files): `scripts/checklist_engine.py:2001` still refuses `attest` on
an artifact-kind postcondition — `attach` first is still required. A narrower improvement had
shipped — `attest --evidence <id>` satisfies an identical sibling postcondition by reference — and
the sweep generalized it into "the lesson is resolved." Two different claims; only the narrower one
is true.

Cost: four f1Brainz sub-runs (three on 07-18, one on 07-25 — eight days *after* the clear) hit the
identical pattern with zero behavior change, against a finding the fleet had been told was closed.
18 recurrences accrued while the signal was being read as stale accumulation.

**Process consequence.** The curator's standing prior is "most exported lessons are stale
accumulation," and that prior is usually right — but a wrong *clear* is far more expensive than a
wrong *route*, because it also suppresses the recurrence signal that would have caught it. A clear
must name **which claim** shipped and verify that claim against the behavior the lesson actually
describes, not an adjacent improvement in the same area. Written into every cleared export so it
does not have to be rediscovered.

## Instrument 1 — fleet sweep

| Finding | Disposition |
|---|---|
| `init_work_area.py --root` nests `.agent-work/.agent-work/` | **Mended** — PR #258 |
| REVIEWER_HANDOFF lacks `Survey State Location` | Resolved upstream — present in repo *and* install |
| `from-child-refuses-on-gated-checklist` | Resolved — already a tracked item in #220 |
| #208 TR-1 harvest doctrine | Resolved upstream — shipped 7c8ff1b |
| `engine-artifact-attest` "resolved" claim | **Corrected** → #220 |
| `current` doesn't label condition kinds | Routed → #220 |
| `run_crew.py` can't detect Agent-tool harness (11th) | Routed → #220 |
| Launch-order Data Locations asserts unverified paths | Routed → #221 |
| Canonical routing can dissolve a file fence | Routed → #221 |
| Reviewer perturb-restore wiped uncommitted work | Routed → **#259** (new) |
| `--override-reason` has no sanctioned use case | Routed → #259 |
| Resumed-subagent cwd leaks to session root | Routed → **#260** (new) |
| Agent-tool crew self-send is a no-op | Routed → #260 |
| No first-class fast-integrate gate under contention | Routed → #260 |
| Harvest completeness not mechanically checked | Routed → #208 |
| `simplification_limits` standing postcondition | Cleared — consuming project's own CLI, not shared machinery |
| `handoff-simplification-limits-paths-flag` | Cleared — same |
| 625-segmentation / 232 "nothing to export" notes | Cleared — informational |

Note on the input: 12 of these entries reached the durable log only because an f1Brainz team-lead
caught, by hand, that six staged commander trios had been collected but never merged before their
worktrees were swept. That near-miss is itself routed (#208).

## Instrument 2 — corpus health

`curate_corpus.py --root skills`: **73 findings, 52 flagged** — identical totals and distribution to
the 07-24 sweep. Zero drift. Both routed categories (invoker-tag rollout policy; description-lint
precision, incl. the suspected `explorer`/`lessons-auditor` when-to-use false positives) unchanged
and still open on #117. Null result recorded there so a future sweep can distinguish "measured,
unchanged" from "not measured."

**Install lag: none.** Diffed the whole `skills/` tree against `~/.claude/skills/`. Every content
difference is the installer's own placeholder resolution (`python` → `py`, `<skill-dir>` → absolute
path); `checklist_engine.py` is byte-identical. The 07-24 `stale-installed-corpus` pressure is not
recurring.

## Left for the human

Three genuine forks the curator declined to guess at, each flagged in its issue:

1. **#259** — is perturb-to-test *shipped reviewer doctrine* or an emergent good practice? Grepping
   the repo and the install found no such step anywhere in the corpus, yet a reviewer performed it
   and destroyed an implementer's uncommitted work doing so.
2. **#260** — sanction a fast-integrate gate, or rule that the waiver channel is correct and the
   Commander should stop treating it as friction? Both defensible.
3. **#221** — real transcripts live outside the repo under `~/.claude/projects` and carry user
   conversation content. There is no sanctioned redaction/consent path for a run that legitimately
   needs them. This scoped #227's item-5 acceptance permanently.

## Not touched

An `explore-shared-understanding` engine lease is active (explorer, heartbeat 2026-07-17). Its
`explore` step closes only on a human converge/shelve decision, so this unattended run left it
alone rather than advancing or releasing it.

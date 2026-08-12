# Plan critic — issue #704

## Honesty header: this critic is NOT cold

The doctrine wants an adversarial read by a critic with **no authoring context**. This session's
operating instruction forbids dispatching subagents, so no independent reader was available. What
follows is a **self-critique by the plan's own author**, run deliberately as an attack pass. It is
weaker than a cold read in exactly the way that matters — it cannot catch what the author never
thought of — and that limitation is recorded, not papered over. **Named untaken road: the real cold
critic (and the 3-lens panel the module's `settled/human` anchors would ordinarily justify).**

Findings are dispositioned by the Commander under the engagement's standing no-human instruction.

---

## CC1 — the identity harness could be vacuous · APPLIED to the plan

**Attack.** The whole plan rests on an identity harness catching a float-reordering regression. But
if the test grids are built from exactly-representable binary values (0.5, 0.25, 2.0 — the natural
thing a test author reaches for), their sums are bit-identical under *any* summation order. The
harness would pass a genuinely reordered implementation and prove nothing, while looking like proof.
G1 would be green, G2 would be green, and the acceptance criterion would be unmet and undetected.

**Disposition: valid, and it was a real hole.** `g1-implement` now requires non-exact values
(0.1, 0.7, 1/3, mixed magnitudes), 4–5+ cells per row/column, and — decisively — a **demonstration
that the harness bites**: temporarily reverse the summation order, confirm a golden assertion fails,
revert. An identity harness never shown to fail is an untested smoke alarm.

## CC2 — two crew gates for a ~14-line change is over-process · REJECTED, with reason

**Attack.** One gate could add the helper and the test together. Two gates buy a full extra
implement/review/integrate round-trip for a cosmetic change the issue itself called non-blocking.

**Disposition: rejected.** The ordering *is* the proof. Goldens captured after the edit prove
nothing (they would encode whatever the new code does); goldens captured before, and then left
untouched, are the only thing that makes "byte-identical" a check rather than a claim. The
G2 constraint "editing the harness is forbidden" is only meaningful because the harness closed in a
prior gate. Collapsing the gates would collapse the argument.

## CC3 — the plan assumes a green baseline nobody measured · APPLIED to the plan

**Attack.** Every gate command assumes `tests/unit/physics/instrument_panel/` and
`tests/unit/physics/pilot/` pass on main today. Planning never verified it (permission-blocked). If
anything is already red, `g1-integrate` fails on arrival, and the run either stalls or — worse — a
pre-existing failure gets mistaken for a regression caused by the refactor.

**Disposition: valid.** `e0-context` now measures the baseline *before* G1 opens and, on
pre-existing red, requires the failing node ids and main's HEAD to be recorded and either explicitly
deselected (named in the gate) or carried into a human waiver. Pre-existing red must be labelled as
such at the moment it is found, not argued about at the acceptance boundary.

## CC4 — `g2-integrate.c4` (diff scope) is attested, not machine-checked · ACCEPTED as-is

**Attack.** "Diff scope is exactly one file" is the constraint most likely to be violated by a
helpful implementer, and it is the one postcondition left as a `check: null` attestation.

**Disposition: accepted with the weakness named.** The natural command form needs the G1 commit sha,
which does not exist at authoring time; hand-waving a `HEAD~1` in would be fragile in the presence of
rework commits. The mitigation is that `g2-review` requires the reviewer to run
`git diff --name-only` and the tests/-unchanged diff independently, so the claim gets two humans-in-
the-loop rather than one attestation. If the implementation engagement wants it mechanical, it can
`amend` c4 into a command postcondition once the G1 sha is known.

## CC5 — pyright baseline diff is an expensive postcondition · APPLIED (partially)

**Attack.** `scripts/pyright_baseline_diff.py` builds a temp git worktree and runs pyright twice over
the whole repo. As a gate-closing postcondition it can run for minutes and is exactly the shape
`lesson:scope-self-authored-regression-to-import-graph` warns about.

**Disposition: partially valid.** It stays — #704's acceptance says pyright-0, so the project's own
new-errors-only gate is the right instrument, and this is a two-function change so there is nothing
narrower to scope it to. But the cost is now named in the postcondition text, `--base-ref origin/main`
is passed explicitly, and `e0-context` measures its wall clock up front so it is not discovered at the
worst moment.

## CC6 — "no report artifact needs regenerating" is derived, not measured · ACCEPTED

**Attack.** The mission frame claims `docs/physics/instrument_panel_668_gb2023q_report.md` needs no
regeneration. That is inferred from byte-identity, which is itself the thing being proven.

**Disposition: accepted as an honest derivation, not a measurement.** It is correctly *conditional*:
if byte-identity fails, the plan already routes that to a blocker rather than a waiver, and artifact
staleness would be the least of the problems. No gate change.

---

## Summary

Six attacks; **three changed the plan** (CC1, CC3, CC5), two were rejected or accepted with their
weakness stated (CC2, CC4), one was confirmed as a sound conditional (CC6). The single most valuable
finding is CC1 — without it the plan's central proof could have been ceremonial.

**Panel-vs-single, restated for approval:** a 3-lens cold panel (intent-fit / testability /
simplicity) is what this module's `settled/human` anchors would ordinarily justify. It was **not
run**, for the harness reason above, and a single non-cold self-critique stands in its place. That
substitution is the plan's largest process debt and the approver should see it as such.

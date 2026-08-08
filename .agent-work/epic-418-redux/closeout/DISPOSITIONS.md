# Epic #418 — issue disposition ledger

Satisfies `execute` postcondition **c1**: *every epic issue dispositioned (merged, honest-null
closed, deferred with ruling, or escalated)*. Built 2026-08-08 while wave 4 runs. Enumerated by
command (`gh issue list --search "418 in:body"` plus direct `gh issue view` on the seven named
workstream issues), **not from memory** — the run has already produced three errors this week from
claims carried forward and never re-derived.

**Population: 48 issues — 17 closed, 31 open.** Every one gets a line below. Nothing is left
unrouted; that is the point of the ledger.

**A rising open count is not a failure here, and the spec says so.** E's fourth done-condition was
**retired** during the 2026-08-07 revision precisely because it was falsified by this epic's own
correct execution — 117 open issues at the start, 138 during, *because doing the mechanisms work
well generates findings*. It was replaced by a standing obligation: **each workstream retires the
findings it subsumes.** So the honest measure is per-line disposition, which is what follows.

---

## A. Delivered and closed (17)

`#428 #433 #436 #437 #440 #443 #447 #454 #460 #461 #462 #463 #464 #465 #466 #488 #494`

Plus the wave-0/1 workstream issues, closed under the predecessor run: `#419 #420 #422 #425`.

**Disposition: merged.** Verified CLOSED on the forge, not by ancestry — squash-merge makes an
ancestry test return the same answer for merged and abandoned.

**Correction carried here from the log:** four of these closed via **replant** PRs, not the PR
numbers I had originally recorded. #433 → **#485**, #436 → **#472**, #460 → **#487**, #464 →
**#473**. The PRs I first recorded (#483, #469, #486, #471) are all *closed, merged=null*.

---

## B. In flight (1)

| Issue | Disposition |
|---|---|
| **#467** — A2, trip semantics | **Wave 4, running now.** One Commander, Opus. This ledger is provisional until it returns. |

---

## C. Epic workstreams not yet run — ESCALATED, awaiting Tommy (3)

| Issue | Workstream | Ruling |
|---|---|---|
| **#424** | F — MCP front door | **Escalated.** Next in the epic's confirmed order after A2. Blocked on #467 by its own terms: *F cannot type a verb whose meaning is unsettled.* |
| **#421** | C — relocate gate instructions | **Escalated.** Order says it runs against a settled verb contract, i.e. after F. |
| **#423** | E — backlog re-cut + closeout debts | **Escalated.** By design runs on *what survives* the redux, not on today's backlog. |

**These three are the checkpoint question**, and they are deliberately not mine. "Keep rolling"
authorized finishing A2; three further workstreams is a materially larger commitment. Contract
Addendum R2 records this as surfaced.

---

## D. Dissolves with #467 — do not fix separately (1)

| Issue | Ruling |
|---|---|
| **#431** — a HARD trip blocks `advance`, freezing the DIGEST the trip's own handoff needs | **Deferred into #467.** Its DC3 states #431 *dissolves* rather than being patched: once a trip changes the instruction instead of refusing the verb, the agent still advances and the DIGEST still gets written. **Verify dissolved, then close — do not patch.** The wave-4 launch order makes verification a return requirement and closing explicitly mine, not the Commander's. |

---

## E. The governor thread — recommend landing as one piece (4)

| Issue | Ruling |
|---|---|
| **#458** — the gauge writer ships nowhere | **Deferred with ruling; recommend first of the four.** Measured: tracked `.claude/settings.json` wires `spine_rail.py` and the gauge writer on *nothing*. **Every governor observation this epic made came from one laptop's untracked config.** |
| **#264** — 1144 lines, 13 tests, **unmerged**, asserting the gauge is still *measuring* | **Deferred, escalated — landing it is a scope change.** Needs a rebase over 211 commits. Its `governor-264` worktree and branch are **protected from sweep**; positive-control verified `ahead=3, uniquefiles=2`. |
| **#452** — a bare-keyed agent driving several spines gets *no* reading | **Deferred with ruling.** Same thread; attribution. |
| **#444** — nothing links the gauge record's field count across seven assertion sites | **Deferred with ruling.** Same family, lower priority. |

The argument for landing them together, recorded: this epic ran roughly **nine hours with a totally
silent governor on the orchestrator tier** and every downstream measure read that absence as a quiet
pass. #488 fixed the silencing; the other four are the difference between a mechanism that exists
and one that is known to be working.

---

## F. Closeout debt, inherited from epic #298 (4)

`#448` resolved-load-manifest unowned · `#449` #298 item J never done · `#450` B1 first
consolidation never run · `#451` 23 of 32 episodes carry unpaid signal, 7 ever harvested.

**Disposition: deferred with ruling, routed to #423 (E).** These are *pre-existing* debt this epic
inherited and did not create. E is the workstream that exists to re-cut the backlog, and #451 in
particular is a direct input to the lessons audit. Fixing them here would be scope drift.

---

## G. Template-instantiation defects — recommend a class sweep, not point fixes (2)

| Issue | Ruling |
|---|---|
| **#439** — `COMMANDER_SPINE archive.c2b`'s `<branch>` placeholder is never resolved | **Deferred with ruling.** |
| **#484** — the same gate ships an unsubstituted PR-reachability check | **Deferred with ruling.** |

**Two instantiation defects in one spine argues the class is the bug.** The second was found only
because `advance` actually ran the check and it failed — the healthy-world signal working, for once.
Recommendation to the closeout audit: sweep every shipped template for unsubstituted placeholders
rather than fixing these two by hand.

---

## H. Engine and rail defects found during the run — deferred with ruling (9)

`#427` refusals counter records zero when the refusal precedes the lease · `#430` `.spine-rail-binding.json`
accepts an unexpanded shell-variable path · `#432` a dispatched role can skip the engine entirely and
its return still passes · `#441` binding store has no lock, no reaper, unvalidated paths · `#442` the
rail and HARD refusal read badly to the agent they are aimed at · `#446` archive gate c2b accepts only
an OPEN PR, so a well-run epic is forced to `--waive` · `#453` rail binds an unexpanded shell token as
a spine path · `#455` acceptance-harness hardening · `#457` a descendant's live gate is attributed to
its ancestor.

**Disposition: deferred with ruling.** All are real, all were confirmed in the field this run, none
blocks the epic's done-conditions.

**#432 and #457 deserve naming.** #432 is *this epic's thesis stated about the constellation itself*
— a role can skip the engine and its return still passes, which is a check that cannot fail at the
compliance layer. #457 was evidenced twice this run and deliberately **not** folded into wave 3 on
the "easy fixes" amendment: both readings of the lease field are uninformative, so fixing it means
deciding how liveness is encoded at all, which ends at a load-bearing interface. That is not an easy
fix and folding it in would have misread the instruction.

---

## I. Harness and tooling (3)

| Issue | Ruling |
|---|---|
| **#468** — the role verifier's installed-skill guard passes from the source repo by accident | **Deferred with ruling.** Bit again at the wave-4 prelaunch; the workaround (use the installed copy) is recorded in the state note. |
| **#459** — mutation-floor harness reports HARNESS ERROR instead of kills | **Deferred with ruling.** |
| **#429** — `file_issue_set.py`'s github adapter fails on Windows via `--body` | **Deferred with ruling.** Same family as the four silent `gh` hazards in the lessons brief. |

---

## J. Filed by #465's triage, wave 3 (5 open, 1 already closed)

`#493` journal append still text-mode · `#495` six JSON writers pass encoding but not newline ·
`#496` CREW_CONTEXT's rule doesn't name `save()`'s byte-faithful exception · `#497` `amend()` is a
215-line long method · `#498` `amend`'s type applicability restated in six places.
**#494 is already CLOSED** — so five, not the six I reported at the wave-3 checkpoint.

**Disposition: deferred, pending Tommy's keep-or-drop at acceptance.** He has twice said he'd rather
not clutter the board. These are already filed, so the live question is whether to *keep* them.
**#493 and #495/#496 are the line-ending defect family that #465 was fixing** — found sideways from
the fix, which is the good kind of finding. #497/#498 are maintainability, explicitly flagged
*not over-budget*, and are the weakest of the five.

---

## K. The epic itself (1)

| Issue | Ruling |
|---|---|
| **#418** | Open by construction until closeout. Closes on Tommy's acceptance, after the lessons audit, cartographer reconcile and epic summary. |

---

## Wave 4 additions (2026-08-08)

| Issue | Disposition | Where it went |
|---|---|---|
| **#467** | **Merged and closed** | PR #505 -> `c875ee23`. A2 complete; DC6 partial by ruling. |
| **#431** | **Closed — verified dissolved** | RED no longer reproduces; four live trips this run cited as confirmation. |
| **#500** | Filed, deferred | Refresh-request has no served state and the compliant handoff erases its own signal. |
| **#501** | Filed, deferred | The wave-launch gate cannot run as its own spine instructs (`_installed_skills_root` accepts the repo). |
| **#502** | Filed, deferred | No provenance record names the engine build that produced a gate; four builds live. |
| **#503** | Filed, deferred | `--authority` on amend/waive is validated only as non-empty. |
| **#504** | Filed, deferred by explicit ruling | Trip ledger goes silent at closeout. Not fixed in-wave: it would have voided the review the rework earned. **This is what keeps DC6 partial.** |
| **#313** | Commented — root cause attached | The installer's interpreter probe proves an interpreter *starts*, not that it can run the suite. |
| **#442** | Commented | The printed remedy does not merely read badly — it exits 0 while doing nothing. |
| **#371** | Commented twice | Second instance recorded, then corrected: the g1 seam was two *vocabularies*, a check that cannot PASS. |
| **#266** | Commented — falsified | The trip has now fired on correct readings four times. Recommended close-as-answered. |

Crew triage candidates tc19-tc24 are recorded in the issue's own spine and carried in `RETROSPECTIVE_SOURCE.md`; tc19 is #504.

## Wave 5 — the final wave, launched 2026-08-08 (21 issues, in flight)

**Authorized by Tommy at the wave-4 checkpoint**, against a score of the epic's own five
done-conditions rather than the wave list: DC3 met, DC2 substantially met, DC1 mechanism done but
shipping not, DC4 and DC5 untouched. Then widened by him to include the #474-#480 group.

**Eight of the 21 close as duplicate collapses, and no collapse is visible from the issue titles.**
Every one was confirmed against the issue **body**, and every launch order carries that as a
NOT-OVERRIDABLE rule — a title-level sweep here is a check that cannot fail.

| Crew | Issues | Fixes | Disposition |
|---|---|---|---|
| **1** bookend gates (Opus, Commander) | #506, **#501+#468**, **#439+#484+#446** | 3 | In flight |
| **2** readiness, workstream R (Sonnet, Commander) | #458 | 1 | In flight |
| **3** crew addressing (Sonnet, implementer) | **#507+#370+#413** | 1 | In flight |
| **4** engine internals (Sonnet, implementer) | #474 #475 #476 #479 #480 #427 #503 #493 #495 | ~9 | In flight |
| **5** docs (Sonnet, implementer) | #496+#411 | 2 | In flight |

**The three collapses, verified against bodies:**

| Collapse | Shared root |
|---|---|
| #501 ≡ #468 | same function, same line — `_installed_skills_root()`, `verify_iterative_role_artifacts.py:53`. Filed once from outside, once from the spine's own imperative. |
| #439 ≡ #484 ≡ #446 | all three are the **same postcondition**, `archive.c2b`. Two are the unsubstituted `<branch>` placeholder; the third is that it accepts only an OPEN PR. |
| #507 ≡ #370 ≡ #413 | one defect, three filings, **three different epics** — a crew cannot address the Commander that dispatched it. |

**Two of the 21 were already this epic's own findings**, filed in wave 4 and now being fixed rather
than carried: #501 and #503. **#506 was filed against the gate that would otherwise have forced a
waiver to close this very epic**, and crew 1 is fixing it. That is the retire-what-you-subsume
obligation doing exactly what it was written to do.

**Explicitly left out, with reasons:** #264 (rebase over 211 commits — a scope change, and #452/#444
belong with it), #409 (cheap only once the working-notes location is ruled), #429, #500/#502/#504
(each needs design thought). #504 in particular stays deferred and is what keeps DC6 partial.

## Summary of routing

| Disposition | Count |
|---|---|
| Merged / closed | 19 (+4 from waves 0-1) |
| In flight — wave 5 | 21 |
| Deferred to their own efforts by ruling | 3 workstreams (F #424, C #421, E #423) + #264 |
| Dissolved with #467 — closed | 1 |
| Deferred with ruling | 30 |
| Open by construction | 1 (#418) |

**Zero unrouted.** Re-derived at the `close-to-w5` boundary, 2026-08-08.

**Scope is settled and nothing is escalated.** F, C and E are no longer "awaiting Tommy" — he ruled
at the wave-4 checkpoint that they become their own efforts after this epic closes. The only open
item in this ledger is wave 5 itself.

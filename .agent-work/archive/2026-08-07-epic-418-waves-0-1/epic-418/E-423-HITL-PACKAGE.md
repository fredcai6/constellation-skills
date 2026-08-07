# Issue #423 — evidence package for the human's batch confirm

**Read-only assembly.** Nothing below has been executed. No issue was closed, commented on, or labelled. Every claim was checked directly against the tracker (`gh issue view`, `gh pr view --json state`) or against files/commits in the repo — never against memory or ancestry. You confirm yes/no; the Admiral executes.

Sweep timestamp: 2026-08-05. Open backlog at time of sweep: **128 issues**.

---

## Deliverable 1 — the five uncontested closes

| # | Title | Verdict | One-line reason |
|---|---|---|---|
| [#131](https://github.com/fredcai6/constellation-skills/issues/131) | append-only journal sidecar | **CLOSE — done** | Shipped in PR #133 + #135, both `state: MERGED` |
| [#285](https://github.com/fredcai6/constellation-skills/issues/285) | graduate a lesson out of the playbook | **CLOSE — superseded** | The playbook it targets was deleted wholesale by #308; the specific lesson is confirmed migrated to an episode, but see flag below |
| [#289](https://github.com/fredcai6/constellation-skills/issues/289) | inert governor is silence w/o a sidecar | **CLOSE — empty** | Body is a literal placeholder (`@-`), 0 comments; real content lives at open issue #383 |
| [#298](https://github.com/fredcai6/constellation-skills/issues/298) | Grander Scale epic (cut 1) | **CLOSE — done, 1 gap carried** | 11 of 12 wave items (A–L) closed with real evidence; the 12th (J) is a known, already-named gap, not a reason to hold the epic open |
| [#322](https://github.com/fredcai6/constellation-skills/issues/322) | truth-layer taxonomy gap | **CLOSE — done** | Fixed by commit `1dd83a1`, verified live in `docs/CONSTELLATION_OVERVIEW.md`; see flag on the spec's settings.json note |

All five check out. None are disqualified. Two (#285, #322) carry a flag worth reading before you confirm — not a reason to hold them, just something to know.

---

## Draft evidence comments

### #131 — feat(engine): append-only journal sidecar

> **Uncontested close — done.**
>
> The append-only journal sidecar and its eval cross-verification check were built and shipped:
> - PR #133, *"feat(engine): append-only journal sidecar + eval cross-verification (#131)"* — `state: MERGED`, merged 2026-07-11.
> - PR #135, *"feat(engine): land #131 journal sidecar on main (retarget of merged PR #133)"* — `state: MERGED`, merged 2026-07-11.
>
> Both verified directly via `gh pr view --json state`, not by branch ancestry. Closing as delivered.

### #285 — lessons: graduate verify-harness-field-and-drive-real-writer

> **Close — superseded.**
>
> This issue assumes the `.agent-work/LESSONS.md` playbook mechanism (20-entry cap, hand-graduation) is still the container that needs fixing. It isn't: #308 (closed, merged as `a4934cb` / PR #407) deleted that mechanism wholesale, per Tommy's ruling that the playbook was *"a dead end between two useful things — an episodic lesson accumulator and actual updates of doctrine."* Lessons now migrate into the episode store; doctrine graduation goes through `docs/agents/*` instead.
>
> The specific lesson this issue names, `lesson:verify-harness-field-and-drive-real-writer`, is confirmed migrated: it is absent from the current `LESSONS.md` (grep finds 6 unrelated active entries, not this one) and present as `episodes/active/issue-308-004.md`.
>
> **Flag, not a blocker:** the graduation this issue actually asked for — landing the pattern in a durable testing-conventions doc, wired into the launch-order template so it stops needing hand-pasting — was explicitly declined in #308's ruling (*"just go to episodes. no doctrine updates."*). So the container is gone, but the underlying value (a durable, mechanically-delivered testing rule) hasn't landed anywhere yet — it's sitting as an unconsolidated episode. Recommend closing #285 as superseded, with the content re-surfacing when the B1-first-consolidation closeout debt (named in this epic's own workstream E, still unfiled) gets run.

### #289 — governor: an inert governor is silence WITHOUT a sidecar

> **Close — empty.**
>
> Issue body is a placeholder (`@-`) with zero comments — there is no content to act on. The title's actual topic (a governor that silently produces nothing) is already tracked with real, measured evidence at open issue **#383**, *"Governor goes silent on exactly the runs that need it"* — root-caused there to lease leakage from terminal spines that never release, with a `gauge.json` reading 36 hours stale as direct evidence. Nothing is lost by closing #289; the live version of this concern is #383, which stays open.

### #298 — Grander Scale — cut 1 (epic)

> **Close — done, with one named gap carried forward.**
>
> Verified all 12 wave items (A–L) against the tracker directly, not from memory:
>
> | item | issue | state |
> |---|---|---|
> | A — dogfood corpus + baselines | #299 | CLOSED |
> | B — projection generator + manifest | #300 | CLOSED |
> | C — episode record + durable store | #301 | CLOSED |
> | D — invariant inventory | #302 | CLOSED |
> | E — confirm-gate refusal | #303 | CLOSED |
> | F — Commander map-input contract | #304 | CLOSED |
> | G — mechanical episode capture | #305 | CLOSED |
> | H — drift check mechanization | #306 | CLOSED (the "honest null" exc-1 named) |
> | I — map-first measurement | #307 | CLOSED — **VERDICT: PASS, Tommy, 2026-08-02** (`map_before_src` 0/4 → 4/4) |
> | J — first collated consolidation | *(none filed)* | **GAP** — #308 substituted a lessons-to-episodes migration instead of running the required consolidation exercise |
> | K — coherence sweep | #309 | CLOSED |
> | L — B2 gate evaluation | #310 | CLOSED |
>
> 11 of 12 are closed with real evidence — including item I, whose verdict a stale internal note had flagged as still pending; it was in fact rendered by Tommy on 2026-08-02 (*"before source was intent … yeah, that sounds like a pass to me"*). The one gap, J, is already named in this epic's own spec as a closeout debt to file separately — it does not block closing the epic itself, since the spec's own workstream E treats it as a tracked-forward debt, not a re-open condition.
>
> Note for the record: the epic body's own checklist (the `- [ ]` boxes for A–L) was never ticked, even though 11 of 12 linked issues are closed. That's stale bookkeeping in the epic body, not evidence the work is undone — verified by checking each linked issue's actual state, not the checklist rendering.

### #322 — CONSTELLATION_OVERVIEW truth-layer taxonomy omits the episode store

> **Close — done.**
>
> This issue asked to fold the episode-store's place in the truth-layer taxonomy into #308's cutover ruling. Verified at source: commit `1dd83a1`, *"feat(#308): build docs/agents/ crew tier; fix #348 stale transcript and #322 taxonomy gap,"* explicitly fixes it, and `docs/CONSTELLATION_OVERVIEW.md` (current, lines 63–75) now lists `episodes/active/` + `episodes/retired/` as a truth layer ("raw observed history — what actually happened on real runs"). Closing as done.
>
> **Flag, not a blocker:** the epic's design spec (workstream E) attaches a note to this close — *"#322 gets its settings.json wiring pointer noted before close"* — but nothing in #322's body, its comments, or the taxonomy fix mentions settings.json; it's a documentation-taxonomy issue, unrelated to any wiring config. The spec's own critic table (finding S6) independently flagged #298/#322 as appearing twice with contradictory bullets in workstream E's draft, so this looks like leftover drafting noise rather than a real instruction attached to #322. Recommend closing #322 on the evidence above regardless; if there's a real settings.json pointer this was meant to carry, it isn't findable from #322 itself and should be traced separately (nothing here should silently absorb it).

---

## Deliverable 2 — proposed cluster boundaries

Method: reused the K1–K13 cluster map from exc-4's census (`evidence/exc-4-issues-RESULT.md` in the archived exploration), cross-checked every member against one `gh issue list --state open` sweep taken today, dropped anything since closed, and separately swept the 128 open issues for anything the original census didn't cover (mostly newer issues filed after the census ran). K2 is **not** treated as consumed by workstream A here — see flag below.

**Excluded from clustering — already individually tracked, don't need a cluster label:**
- Epic #418's own wave children: #419, #420, #421, #422, #423, #424, #425, #427, #428, #429, #430, #431 (13 issues, including #418 itself). These are freshly filed, well-scoped, and either build epic #418's mechanisms or are reproduced defects with their own evidence — they already satisfy #423's done-condition on their own terms.
- #328, #329 — K1's two named instances, explicitly owned by workstream D / issue #422 ("Wire the prose-only invariants"). They'll most likely close individually once #422 ships; no cluster label needed while that's in flight.

**Proposed clusters (K-map, still-open membership only):**

| Cluster | Theme | Open members today |
|---|---|---|
| K1 | Built-but-not-delivered (capability ships, wiring doesn't) — minus #328/#329 | 13: #345 (umbrella), #257, #280, #281, #288, #291, #313, #330, #344, #363, #373, #403, #243 — **add #208** (rescoped 2026-08-03 to exactly this shape: a missing mechanized harvest-completeness check) |
| K3 | Episode store hardening | 16: #399, #342, #318, #359, #404, #277, #319, #323, #343, #360, #361, #367, #368, #379, #400, #405 |
| K4 | Measurement methodology | 7: #351, #352, #395, #396, #397, #401, #402 |
| K5 | B2 kernel-break evidence | 3: #414, #415, #402 (overlaps K4 — both use #402) |
| K6 | Harness capability limits | 8: #408, #413, #294, #314, #222, #248, #260, #370 |
| K7 | Engine, lease, gate mechanics | 11: #357, #369, #390, #315, #371, #358, #375, #376, #311, #220, #242 |
| K8 | Artifact and tracker hygiene | 5 after this batch's closes: #354, #409, #412, #339, #411 |
| K9 | Curator-routed doctrine bundles | 7: #117, #215, #221, #223, #259, #366, #388 |
| K10 | A check that cannot register its own failure | 6: #392, #292, #372, #381, #382, #384 |
| K11 | Code-shape cleanups (Fowler-class) | 6: #272, #282, #377, #385, #386, #387 |
| K12 | Unconfirmed design threads | 5: #139, #219, #297 — **#233/#234 excluded**, already tracked as their own HITL design threads under epic #226 |
| K13 | Corpus reachability | 7: #331, #136, #290, #346, #356, #156, #394 |

**Standalone, no cluster fits:**
- **#249** — a deferred process-review commitment ("revisit whether @grade earns its authoring cost"), not a code defect or architecture-stratum item. Genuine standalone; leave unclustered per #423's own allowance for "genuine standalones."

**Needs your call before I'd apply anything — K2 (Context Governor):**

The original design spec treats cluster K2 as "consumed by workstream A" (#419, the governor re-keying fix) and drops it from workstream E's cluster list entirely. I don't think that's actually true today. K2's parent epic (#267) is closed, but **14 of its 15 member issues are still open**: #235, #264, #266, #270, #271, #274, #275, #284, #286, #287, #295, #383, #214, and #281 (also in K1). #419 fixes the identity re-keying root cause several of these describe (notably #383, which #419's own design doc names as the motivating defect), but #419 hasn't shipped yet, and nothing here confirms it will silently close the other 13. Recommend one of two calls: (a) give K2 its own cluster item like the rest, revisited once #419 lands and its actual downstream closures are known; or (b) confirm explicitly that these 14 stay open and un-clustered pending #419, if that's the intended sequencing. Either is fine — I just don't think "consumed by workstream A" is accurate yet, and didn't want to silently apply a label that assumes it.

**Sweep coverage check:** 128 open − 13 (epic-418 family) − 2 (#328/#329, D-owned) − 5 (this batch's closes, once confirmed) = 108. Of those, 94 fall into K1/K3–K13 above (incl. #208), 14 are K2 (flagged above), 1 is standalone (#249) — that's 109, one over by #402's cluster overlap (counted in both K4 and K5). Sweep is complete: every open issue outside the epic-418 family lands in exactly one bucket above (K2 flagged, not yet applied).

---

## Not covered by this package — still needed for #423's done-condition

The design spec's workstream E also calls for filing **four closeout-debt issues**, which is beyond this package's read-only mandate (issue creation is not something I can do):
1. The unowned resolved-load-manifest finding (precondition of any kernel-and-fragment split) — currently recorded nowhere but a closeout artifact.
2. #308's unmet consolidation clause — the "J" gap named in #298's evidence above.
3. The B1 first consolidation (referenced in #285's flag above).
4. The episode-store harvest (23 of 32 episodes carry unpaid signal, 7 ever harvested, per the spec's exc-3 finding).

These four still need to be filed once the batch confirm lands — they're not blocked by anything in this package, just not something I could execute under read-only latitude.

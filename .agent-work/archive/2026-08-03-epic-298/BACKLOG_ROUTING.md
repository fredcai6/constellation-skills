# Epic-298 side ledger — routing, not a list

**REWRITTEN 2026-08-02.** The first version of this file made two claims that are now false: that delivery is broken, and that group C had *earned* promotion. Both were written before the corpus reinstalls and before the closeout lessons audit was scoped. Corrections are marked inline rather than deleted, because the two errors are themselves the routing lesson.

**Counted at rewrite time, by command, not by memory:**

```
gh issue list --state all  --limit 200 --json number -q '.[].number' | awk '$1>=313' | wc -l   ->  75
gh issue list --state open --limit 200 --json number -q '.[].number' | awk '$1>=313' | wc -l   ->  67
```

**75 issues numbered ≥313 exist; 67 open.** The first version said 37/31. **Caveat I am obliged to state:** I asserted the range, not per-issue authorship — #313–#403 is this epic's filing window, and I have not verified that every number in it was filed by this run. Treat 75 as an upper bound on the epic's output and 37 as a stale lower bound. **None is in the epic's definition of done.**

This exists so the closeout decision is a decision rather than a backlog dump. Grouped by *what kind of thing they are*, because that determines who should own them and whether they travel together.

---

## A. Delivery — **the claim "delivery is broken" is retracted**

The original heading was *"Delivery is broken (5) — the group that should move first."* **It described nothing by the time it was read.** Tommy caught it directly: *"assume that we're going to reinstall after each fix round, I don't understand how there's a delivery issue."* He was right. With reinstalls standing pre-cleared and performed, a merged fix reaches agents. What remains is narrower and it is not a blocker on anything else.

| # | state | |
|---|---|---|
| ~~**362**~~ | **CLOSED** | modules bundled at `install_constellation.py:97-102`; **verified behaviourally** — both import from an installed copy, present in 10 skills |
| **344** | open | global corpus **shadows** a project install with no user-accessible override. **The staleness is gone; the shadowing mechanism is not.** A project that wants to test its own copy still cannot. |
| **395** | open | **this is the one that makes a recurrence invisible** — the fingerprint digest covers only `SKILL.md`, so it is blind to `templates/` and `scripts/` drift. #393 showed the operative doctrine now lives in templates. A blind fingerprint over the surface that carries the contract is the real exposure. |
| **328** | open | `verify_interrogation.py` / `verify_fowler_pass.py` wired as prose only |
| **329** | open | `verify_worktree_isolation.py` in zero spine templates — doctrine calls a collision *"data loss, not friction"* |
| **346** | open | `constellation-diagnose` does not register its description — **un-triggerable by intent**; 18 of 19 register |

**Revised routing:** this is no longer a *"must move first"* epic. **#395 is the one worth pulling forward**, because it is what would let anyone else detect the class. #328/#329/#346 are ordinary wiring debt and belong in the same bucket as B.

**The lesson from the error is worth more than the group.** I wrote "delivery is broken," then kept asserting it after the thing it described had been fixed. That is the same defect as #396's *a read of a moving target, reported as a property of the thing* — a state observed once and then carried as a permanent property. **Pin a routing claim to the revision you measured it at, or it outlives its subject.**

---

## B. Engine and concurrency defects (6) — **real bugs, not doctrine**

| # | |
|---|---|
| **357** | the lease does not protect the gates — child plans carry `engine_session: null`; **four mutating verbs accepted from a session-less caller while a lease was held** |
| **383** | **the context gauge is silent for exactly the runs that need it.** Subagents inherit the parent session_id; every crew claim adds a binding. **35 for this Admiral session.** The writer needs one candidate to attribute a reading, so it went quiet at the second dispatch and stayed quiet for a multi-day run. **Anti-proportional to risk** |
| **315** | command checks pass **no `cwd` at all**; five shipped relative checks are silently fragile |
| **358** | reviewer `consolidate` and artifact emission are not atomic — a complete verdict can exist with no artifact for the gate to read |
| **330** | no confirm-dead check before worktree reuse |
| **318** | `durable_root()` silos per worktree during an epic; an abandoned lease pins it forever |
| **359** | surveys bypass the capture seam entirely — **Reviewer, Cartographer, Scout, Curator all uncovered** |
| **390** | **corrected** — plans *are* editable (`amend`: add/drop/rescope/retext-check). The gap is one line wide: `imperative` is assigned only in the `add` op, so **no op supersedes a clause inside an existing imperative** |

**#357 is the most consequential**: every continuation protocol in the fleet assumes the lease is the mutual-exclusion primitive, and for gated plans it is not. It is why three agents ended up in one worktree.

**#383 is the most consequential to *this role*.** An Admiral is the run that burns context fastest and it is the one guaranteed to lose its gauge first.

---

## C. Doctrine candidates (8) — **NOT yet earned; that is the audit's call, not mine**

The original heading was *"Doctrine that earned its place (7) — graduate, do not leave as issues."* **Retracted.** I do not get to rule that a finding earned promotion — the closeout lessons audit does, with fresh context and the whole run in view. Naming the verdict in the routing file **pre-empts the mechanism that is supposed to make it.** This is the same shape as the episode-store correction Tommy made mid-run: *the thing that finds it cannot make the call on its importance.*

These are the run's **transferable candidates**. Where they land — `skills/_shared/global-*.md` (canonical, never the regenerated `references/` copies), `docs/agents/`, a template delta, or dropped — is the audit's routing decision.

**337** the check-that-cannot-fail family — **TEN costumes, not six** — plus the unifying principle: *a check whose output is identical in the healthy and the defective world cannot discriminate, however correctly it runs*, with three routes (vacuity, wrong question, wrong iteration set) and one mechanical detector: **assert what you looped over** · **396** *a read of a moving target reported as a property of the thing* — **five layers**, one fix: bind the claim to the revision you read it at · **345** built-but-not-wired, **8+ instances**, with a detection strategy: break the call site, not the callee · **319** why documented hazards recur — *you fix the instance and not the method* · **338** a held PR must declare what it still intends to push; a terminal spine and released lease describe the run, not the ref · **364** *grep for the caller* misses dead code in any module shipping its own self-test · **349** a noise decoy must not be excluded by the target lens's own guardrail · **352** assert an allowlist, not a denylist

**Weigh recurrence over severity.** A count across runs is evidence; a single agent's severity judgement is not.

---

## D. Corpus contradictions and stale doctrine — **cheap, and they mislead every reader until fixed**

**336** Charter creates the file Commander forbids · ~~**317**~~ **CLOSED** · **348** stale `.agent-work/` ignore-state doc, **created by this epic's own #326** · **343** pathless *"the current map"* recurs in cartographer/scout/explorer · **313** docs prescribe an interpreter that has no pytest · **322** overview taxonomy omits the episode store · **400** `LESSONS.md`'s preamble is unreachable through its own writer, and now instructs agents to read an empty bank — **created by #308's own migration**

**Two entries in this group were created by this epic.** That is worth naming: a run that changes doctrine generates stale doctrine as a by-product, and nothing currently catches it at the moment of change.

---

## E. Measurement-instrument findings — **only matter if the measurement continues**

**331** zero skill invocations — corpus offered and declined · **393** `TREATMENT-VERIFIED` proves **hop 0 of three**; `SKILL.md` has zero occurrences of "map" and the contract lives only in the spine template — **this invalidated a claim the Admiral repeated for two days** · **402** #304's existence is attributable, its magnitude is not · **401** vacuous `spine_materialized` · **347** the "nothing landed" evidence standard is unachievable for a skill-loaded run · **351** Commander runs externalise reasoning, thinning the gradeable artifact · **356** the commander skill's description says it cannot take a delegated dispatch, and 5/5 it did · ~~**327**~~ **CLOSED** with #305's g4

---

## F. Local defects in this epic's own new code — **owned by their issues, close with them**

**360**, **361**, **342**, **363**, **399**, **403**, **392**

---

## G. Small, unowned

**314** delegated commanders told to have subagents reply via a mechanism teammates cannot use · **323** context-projection guard gaps from #300's cold panel

---

## The decision this is for

**Volume is the question after all, and the first version got that wrong too.** It said *"volume is not the question"* and then routed on the assumption that two groups had to move first. With A retracted down to #395 and C handed back to the audit, **there is no group that blocks the others.** 67 open issues from one epic, none of them blocking, is a debt pile — and a debt pile is exactly the thing Tommy flagged when he said a lot of these *"seem navel gazy and not necessarily worth the fix while we're still doing big architectural overhauls."*

**Recommendation, revised:**

- **Pull forward exactly one: #395.** It is what makes the whole delivery class detectable rather than re-discoverable. Cheap.
- **Route C through the closeout lessons audit** and let the audit rule on each — including ruling *drop*. **Eight candidates surviving from a 75-issue run would be a good outcome, not a shortfall.**
- **Everything else is ordinary backlog and should be triaged against the Stratum A vision, not against its own severity.** Most of B, D, E, F, G are instrumentation for a measurement apparatus this epic built. If the next arc is architectural, an instrument's defect is not worth fixing until the instrument is next used.

**The honest read:** this epic's real output is the doctrine in C and the two measured results (#307's 0/4→4/4, #308's 23 episodes with 11 unknowns preserved). The other ~65 issues are the *sediment* of producing those. **Triaging them by asking "is this worth fixing?" one at a time will keep all of them.** Ask instead: *which of these does the next arc actually walk through?*

# Epic-298 lessons audit — the short list

**Fresh-context auditor, 2026-08-03. Every number below is pinned to `cad1ec3` unless another
revision is named.** This is a starting point for Tommy's review, not a routing table. Six findings
are promoted; everything else is dropped in named groups with a stated reason.

---

## 0. My limitations, first

1. **I sampled the ADMIRAL_LOG; I did not read it through.** It holds **449** entries
   (`grep -c "^- 2026-" .agent-work/epic-298/ADMIRAL_LOG.md` at `cad1ec3`), of which 350 carry a type
   tag (261 `RULING`, 25 `WAVE`, 16 `INCIDENT`, 12 `ESCALATION`, 10 `FINDING`, 26 others). **I read
   the final 200 lines in full and took a 1-in-4 stratified sample of entry openings — 112 of 449,
   first 190 characters each — plus ~10 targeted greps.** Roughly a quarter of the log passed under
   my eyes at any depth.
2. **The log is partially reconstructed.** Where I found no instance of a pattern, that is not
   evidence the pattern did not occur.
3. **Two of the six artifacts I was pointed at are not on `main`.** `B2_GATE_EVIDENCE.md` and
   commander-310's `AGENT_FEEDBACK.md` entry (line 1931) exist only in the `epic-298/310` worktree at
   `C:/Programs/constellation-skills-wt/e298-310/`. I read them there. **This is itself an instance of
   finding 6** and is how I found it.
4. **I enumerated the episode store (32 files: 5 × `issue-304-g3-*`, 25 × `issue-308-*`, 2 ×
   `issue-309-*`) and read one in full** (`issue-308-021`). I did not read the other 31.
5. I did not verify per-issue authorship of the ~75 issues numbered ≥313. I inherit the routing
   file's caveat that 75 is an upper bound on this epic's output.

---

## 1. THE SHORT LIST

Ordered by recurrence-weighted cost. Row 2 is the exception — it is promoted for constraining the
substrate rework, not for recurrence, and I say so in the row.

### 1. `a-check-that-cannot-fail` has graduated at the crew tier and not at the orchestrator tier

**What it is.** A check whose output is identical in the healthy and the defective world cannot
discriminate, however correctly it runs. Twelve-plus instances this epic (#337).

**Why it recurs.** It already stopped recurring where it was written down, and kept recurring where it
was not. `docs/agents/CREW_CONTEXT.md:78-97` (landed on `main` at `a4934cb`) carries the full family —
"a check that cannot fail is indistinguishable from one that passed", "assert against behaviour, never
against text describing it", "any guard that loops must assert what it looped over". **That file is
crew-tier by its own declaration (line 3): implementer, reviewer, prototyper.** `grep -rn "cannot
fail\|looped over\|vacuous" skills/_shared/ skills/*/SKILL.md skills/*/references/ docs/agents/` at
`cad1ec3` returns **2 lines, both in `CREW_CONTEXT.md`, none at orchestrator tier.**

And the orchestrator tier is where the expensive ones were authored: costume 10 was the Admiral's, in a
ruling about whether it was safe to change the corpus under a running commander; **costume 11 was the
Admiral's liveness probe, which polled mtime over `.agent-work/<work-id>/` while the commander it was
watching wrote continuously to `docs/` and `skills/` — a commander at `reconcile` writes to the source
tree, so the probe read silence exactly when reconcile was going well**; and one instance was authored
inside a message correcting an instance of it. Ten prior costumes misreported. That one was a step from
adjudicating a healthy commander idle.

**Named permanent home:** `skills/_shared/global-orchestrator.md`.

**What changes there.** Two clauses. (a) A short orchestrator-tier statement of the family with the
mechanical detector — *any guard that loops must assert what it looped over* — cross-referencing the
crew-tier text rather than duplicating it. (b) A concrete addition to the existing
`## Idle subagent adjudication` section, which today explicitly disclaims liveness ("This judges the
**verdict**, not liveness") and then never says how to judge liveness: **measure liveness over the whole
worktree, never over the workbench.** Grounded against a measured threshold already in the log — inter-write
gaps at `reconcile` reach ~7 minutes on a healthy commander.

*Rung note:* the strongest form is rung 1 (a script the Admiral runs instead of an ad-hoc mtime poll).
The target is a doc because no such seam exists. Flagging that for the Charter, per the form ladder.

---

### 2. You cannot decompose a role whose load surface you cannot compute (#310)

**What it is.** Named `references/` tokens do not resolve inside the citing role's own directory; the
shared `_shared/global-*.md` bundle is injected at **install** time by `scripts/install_constellation.py`
and is not present in the repo shape at all. **The B2 packet's fact: at `9a90298`, of 21 named reference
tokens, 10 do not resolve role-locally.**

**Why it is here.** *Not* recurrence — this is a single structural measurement. It is promoted because it
is a **precondition on the rework in flight**: any kernel/fragment split has to answer "what does this
role actually load?" first, and today that answer requires resolving through the installer's
`SKILL_REFERENCE_BUNDLES` table.

**I re-derived it independently and got a different number, which matters.** My own tokenizer over
`skills/*/SKILL.md` at `cad1ec3` finds **46 tokens, 29 unresolved role-locally** — same qualitative
result, different denominator, because we tokenized differently. **The count of the corpus's own
reference tokens is unit-dependent**, which is the same defect the packet's §5 escalates
(`docent` ranks 1st by lines and 5th by bytes; `admiral` 4th by lines and 1st by bytes;
`scripts/curate_corpus.py:49-50` carries `SKILL_WORD_TARGET = 400` beside `SKILL_LINE_HARD_FLAG = 500`,
words and lines in adjacent lines with no stated relationship, and bytes in play elsewhere).

**Named permanent homes:** `scripts/install_constellation.py` and `scripts/curate_corpus.py`.

**What changes there.** In the installer: emit a per-role **resolved load manifest** — the actual file set
a role loads after bundle injection — and a test asserting every named token in every `SKILL.md` resolves
to a file in that manifest. Rung 1, mechanical, and it is the artifact the rework needs before it can
split anything. In `curate_corpus.py`: name one unit and state the relationship, or delete the constants.
**This is explicitly not a request to choose a threshold** — the packet hands that up and I am not
re-routing it. It is a request to stop one shipped script from mixing three units silently.

**Carry the halted implementer's warning with it:** the instrument's *measurements* are
substrate-independent (they read git history); **its bins are not.** `WIDE-ALWAYS-LOADED` reconstructs a
loading contract that does not exist in the tree, so a substrate rework could make that bin wrong in a way
no re-run would reveal.

---

### 3. Built-but-not-wired: green tests are not evidence a deliverable landed — a call site is

**What it is.** #345, 8+ instances. commander-304: *"we reliably build the capability and unreliably wire
the guarantee."* **#344 is the outermost ring: #304 was merged, tested, reviewed, and absent from the
installed corpus** — an arm run against it would have blamed the contract for a delivery failure.

**Why it recurs.** Every existing check answers "does this exist?" and none answers "is it called?" And
the naive fix fails: #364 records that "grep for the caller" reported every self-tested helper as
production-reachable, because the module ships its own `--self-test` subcommand and `main` reaches it.
**Both #304 g2 crews independently asked for the same missing thing** — a per-slice wiring grep naming
every function in one command, so a *partial* fix is visible. Two crews converging unprompted on the same
absent field is the strongest form of this evidence.

**Named permanent home:** `skills/commander/templates/IMPLEMENTER_HANDOFF.template.md`.

**What changes there.** A required slot — **Wiring grep** — holding one command that names every symbol the
slice adds and shows, for each, a call site **outside its own definition and outside any `--self-test`
path**. Rung 2: a structural field the handoff cannot skip, not a reminder. The rule text is #364's, verbatim.

---

### 4. Enumerate the blast radius of your own change (consolidation of #408 / #145 / #319 with #348 / #400 / #404 / #405)

**What it is.** The author of a change does not enumerate what the change touched. Six instances this epic
across two tiers, and they are **one defect, not two families** — which is why I am consolidating them into
one row rather than routing them separately.

**Why it recurs.**
- **#408:** latitude-contract pre-clearance does not bind the harness permission classifier; the contract
  named `gh pr` pre-cleared and the classifier vetoed `gh pr merge` anyway, so Tommy ran it. The Admiral
  skill had *already absorbed* #145 — as a clause telling the Admiral to pre-clear **a delegated
  commander's** mechanics. **The fix was written from the outside looking in and left the fixer's own
  terminal mechanic uncovered.** That is #319, *you fix the instance and not the method*, recurring one
  tier up.
- **#348** (stale `.agent-work/` ignore-state doc) was created by this epic's own #326. **#400**
  (`LESSONS.md`'s preamble now instructs agents to read an empty bank) was created by #308's own
  migration. **#404** and **#405** are #308's own second-order effects, filed by the commander that caused
  them. Four docs made false by changes this epic made, none caught at the moment of change.
- Episode `issue-308-021` is the same defect in miniature, first-person and grounded: the commander
  enumerated 5 lesson-intake sites when a command finds 6, then wrote a guard whose character class
  excluded `.` so it could never match `.agent-work/` — **green against three live intake sites** — all
  while consolidating that exact failure mode. Recurrence count within one issue: 2, under maximal
  awareness.

**This is #337's twin at authoring time.** #337 says *assert what you looped over* when you check.
This says *enumerate what you touched* when you write. Same detector, different position in the pipeline.
Filing it as a separate slug would fork the history and undercount both.

**Named permanent home:** `skills/_shared/global-everyone.md`, adjacent to the existing
`## Verify claimed side-effects against the world` section (line 127), which today covers only the
*consumer* side — verifying a claim someone made to you.

**What changes there.** The authoring-side twin: before you call a change done, enumerate by command
(never by memory) every artifact that asserts something about what you changed, and state the count. A
fix scoped to the tier below must name why the authoring tier is exempt, or it is not exempt.

---

### 5. A terminal spine is not reachable work

**What it is.** **Every commander this epic that reached a terminal spine failed to open its PR and had to
be chased.** Three for three (ADMIRAL_LOG line 478, `cad1ec3`: *"Every commander this epic that reached a
terminal spine still had to be chased for the PR. That is now a pattern, not an incident."*). PR #407 was
opened by the Admiral, not by commander-308b.

**Why it recurs.** The `archive` step marks a spine done without proving the work is **reachable**. A
terminal spine and a released lease describe the *run*; they say nothing about the *ref*. CI does not run
on an unopened branch. Compare #338. The Admiral's own grounded ordering rule — **push → file → gates →
PR, sort by what survives your death** — came from the same source: of three commanders that died mid-gate
on #305, only committed, pushed, or filed work reached the Admiral. No spine encodes that ordering.

**Named permanent home:** `skills/commander/templates/COMMANDER_SPINE.template.json`, the `archive` step.

**What changes there.** A `command`-kind postcondition on `archive` that asserts an open PR exists for the
branch (`gh pr list --head <branch> --json number` returning a non-empty set), so the engine refuses to
mark the spine terminal on unreachable work. **Rung 1 — this is the clearest mechanical-constraint
candidate in the whole list, and it is cheap.** Note the template was modified by #304 in this epic; check
`.baseline/` before attributing anything else there to shipped doctrine.

---

### 6. Pin to a revision — and a squash-merge dissolves the pin. **This one is live right now.**

**What it is.** #396 (a read of a moving target reported as a property of the thing — six surfaces) and
#412 (an ancestry test is structurally incapable of recognising a squash-merge: `git merge-base
--is-ancestor` returns the same answer for *merged* and *abandoned*) are **one finding with two
symptoms**. This epic's standing rule *"pin every number to a revision"* points straight at commits that a
squash-merge leaves off `main`.

**Why it is promoted:** because I verified it against the tree and it threatens the document Tommy is about
to read.

At `cad1ec3`:

```
all five epic-298/* branches (305, 308, 310, 331-probe, pre-b-record): NOT ancestors of main
fc1685a  EXISTS, not an ancestor of main   — held alive by annotated tag baseline/304-trend-snapshot
a8d9467  EXISTS, not an ancestor of main   — held alive by annotated tag baseline/304-g2-approve
9a90298  EXISTS, not an ancestor of main   — held ONLY by branch epic-298/310 and origin/epic-298/310
```

**`9a90298` is the revision the B2 gate verdict pins §1, §3 and §4 to** — including the 10-of-21
reference-token fact that finding 2 above rests on. It is not tagged. **Delete `epic-298/310` after
merging and every measured number in the packet Tommy is reading becomes unverifiable.** The two `#304`
baselines survive only because someone tagged them; nothing tagged this one.

**Named permanent home:** `skills/_shared/global-everyone.md`.

**What changes there.** State the pairing: a number pinned to a revision is only durable if the revision is
reachable after the merge, and squash-merge makes branch commits unreachable — so **tag the revision, or
cite one that is an ancestor of `main`.** And second: never use an ancestry test to decide whether a branch
was merged.

**Immediate action, outside the doctrine edit:** tag `9a90298` before `epic-298/310` is deleted.

---

## 2. DROPPED, WITH REASONS

**Asserting what I looped over.** Derived by command at `cad1ec3`, not from memory:

```
cat BACKLOG_ROUTING.md LESSONS_RUN_BRIEF.md | grep -oE "\b[34][0-9]{2}\b" | sort -un | awk '$1>=313' | wc -l
  -> 51   (routing file alone: 47; brief adds 339, 397, 408, 409)
```

**51 distinct issue numbers ≥313 are in view across the two routing artifacts.** The six findings above
draw on **17** issue numbers, of which **12 are inside that 51** (#319, #337, #338, #339, #344, #345,
#348, #352, #364, #396, #400, #408) and **5 are not** (#145, #310, #404, #405, #412) — those five come
from the run brief's late-telemetry prose, commander retrospectives and the B2 packet rather than from
the routing table. **That gap is the point:** the two routing artifacts do not enumerate the same set,
which is why I unioned them instead of trusting either; a count taken from one alone would be wrong.

**The remaining 39 numbers are dispositioned below, and the groups sum to 39.** I checked that with
`comm`, not by eye — my first draft's groups summed to 29 against a stated 41, an under-inclusive
enumeration of exactly the kind finding 4 is about. The twelve I had silently omitted (#317, #326,
#327, #328, #329, #339, #346, #349, #352, #362, #397, #409) are all accounted for here or above.

**Group i — instrumentation for a measurement apparatus that may not run again (10):** #331, #393, #402,
#401, #347, #351, #356, #395, #397, #349. These are real and well-evidenced, and they only bind if another arm is run.
The rework is the live work. **#395** (the corpus fingerprint covers only `SKILL.md` and is blind to
`templates/` and `scripts/` drift) is the one the Admiral wanted pulled forward; I am leaving it here with
a marker rather than promoting it — **if an arm is ever run again, fix #395 first**, because #393 showed the
operative contract now lives in templates and a blind fingerprint would report "stable" through a reinstall
that rewrote the treatment. That is a stop-condition on the apparatus, not on the rework.

**Group ii — engine and concurrency defects already carried by their own issues (8):** #357, #383, #315,
#358, #330, #318, #359, #390. Real bugs, all filed, none blocking the substrate rework. A lessons audit
adds nothing an issue with a repro does not already carry. **#390 in particular is here because the
correction is the lesson, not the finding** — plans are *not* frozen (`amend` carries
`add`/`drop`/`rescope`/`retext-check`); the gap is one line wide (`imperative` is assigned only in the
`add` op). An over-broad root cause sends the fixer at the wrong subsystem, and re-routing it here would
re-broaden it.

**Group iii — stale doctrine and corpus contradictions; a Curator pass, not an audit (4):** #336, #343,
#313, #322. Cheap, mechanical, and they mislead every reader until fixed — but the *generating mechanism*
is already promoted as finding 4 (which carries #348 and #400 as its evidence), and these are its output.
Fix the mechanism here; sweep the output there.

**Group iv — local defects in this epic's own new code, owned by their issues (7):** #360, #361, #342,
#363, #403, #392, and the remainder of #399. They close with their issues. **One fact #399 may not carry:
applying the `strength` ruling is a data migration, not a schema edit** — at `cad1ec3` all **32/32** active
episodes carry `strength` (**173** occurrences), and **7** still carry a `## Diagnosis (optional)` section.
Both fields solicit judgement by name, which is what Tommy ruled out.

**Group v — ordinary wiring debt (3):** #328 (`verify_interrogation.py` / `verify_fowler_pass.py` wired as
prose only), #329 (`verify_worktree_isolation.py` in zero spine templates, while doctrine calls a collision
*"data loss, not friction"*), #346 (`constellation-diagnose` does not register its description — 18 of 19
do, so it is un-triggerable by intent). These are instances of finding 3's class, and they get fixed by
finding 3's mechanism landing, not by being routed one at a time.

**Group vi — closed, or not findings at all (4):** #317, #327, #362 are CLOSED. #326 is this epic's own
change (making `.agent-work/` tracked), not a finding about it.

**Group vii — small, unowned, and cheap (3):** #314 (delegated commanders told to have subagents reply via
a mechanism teammates cannot use — same root as #413's 4/4 peer-messaging failure), #323 (context-projection
guard gaps from #300's cold panel), and **#409** (working-notes files have no declared home: doctrine names
`notes-<n>.md` emphatically and never names a directory, so cold commanders default to the repo root —
**verified at `cad1ec3`: 6 of the 12 tracked repo-root files are `notes-*.md`, exactly half**, and
`notes-308.md` at 28 KB carries the content that became #399, so deletion is the wrong reflex). #409 is the
cheapest fix in the entire pile — name a directory in one doctrine line — but it is housekeeping, not a
lesson, and I am not going to dress it up as one.

**Folded into a promoted row rather than dropped — counted above, not here (2):** #339 (the inbox as a copy
rather than a pointer) is one of #396's six surfaces and rides with finding 6. #352 (*assert an allowlist,
not a denylist*) is a member of #337's family and rides with finding 1.

**Dropped as already-graduated, not as unimportant:** the check-that-cannot-fail family at *crew* tier
(#337 partial), because `docs/agents/CREW_CONTEXT.md:78-97` already carries it. Finding 1 routes only the
uncovered tier.

**Deliberately not routed, because it is a null that does not discriminate:** the open asymmetry — ~75
issues generated in this repo, zero inbound findings from three dogfood projects in the same window. Either
they hit nothing or the export path is never exercised. The sweep cannot distinguish these and does not
claim to. It is a question, not a finding, and it needs an instrument nobody has built.

**Two things the epic did right that I am recording rather than routing, because they need no fix:**
**every cold plan critic caught a blocking defect — ten for ten, no exceptions**, which is now the most
convergent process evidence in this repo; and **pre-registration saved #310's verdict** — it committed to
what *insufficient evidence* would look like before knowing whether evidence would exist, so when the
census was cut the verdict still selected a row (R5) instead of being reverse-engineered from the numbers
that did arrive.

---

## 3. ONE PARAGRAPH FOR TOMMY

The most useful thing this epic produced is not on the list of things it set out to produce. It found that
**a role's always-loaded surface cannot be computed from the role's own files** — roughly half the named
reference tokens resolve only after the installer injects them (10 of 21 at `9a90298` by the commander's
count; 29 of 46 at `cad1ec3` by mine, and *that* discrepancy is the second finding: the corpus has no
agreed unit, so even counting its own references gives different answers). You cannot split a role into a
kernel and fragments until you can say what the role loads, so that is a precondition on the work you are
about to do, and it is the one item here I would fix before anything else. Everything else on the short
list is cheap: one clause in `global-orchestrator.md` (the orchestrator tier never got the
check-that-cannot-fail rule that the crew tier already has, and the two costliest instances were both the
Admiral's), one required field in the implementer handoff, one postcondition on the commander's `archive`
step so a spine cannot go terminal on an unopened PR, and one sentence about pinning numbers to revisions
that survive a squash-merge. **That last one is urgent for a reason you should know before you start
reading: the B2 gate verdict pins its structural finding to `9a90298`, which is not an ancestor of `main`
and exists only on the `epic-298/310` branch — delete that branch and the evidence in the document
dissolves.** Tag it first. I dropped **39** issues in seven groups; the largest is instrumentation for a
measurement apparatus that may never run again, and I think you were right that it is sediment. The one I
would flag inside the drop pile is #395 — not to fix now, but as the stop-condition if you ever run another
arm. And one thing worth knowing about how this epic's own reporting errs: **both routing artifacts it
handed me under-enumerated, in opposite directions**, and my first draft of the drop list did the same
thing — 29 items against a stated 41 — which is why finding 4 is on the list rather than in the pile.

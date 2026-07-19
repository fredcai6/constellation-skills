# Drill: spec-prename-per-role

- **Lesson / doctrine under test:** `skills/explorer/SKILL.md` "## Spec phase" — the graduated
  paragraph beginning *"**Pre-name the adapted per-role wording when a spec directs
  transcription-grade restoration.**"* When a DESIGN_SPEC directs verbatim / transcription-grade
  restoration of one body of role-specific doctrine into several **structurally different** roles
  under a **no-paraphrase** constraint, the spec must **pre-name the adapted per-role wording**
  itself (spell out each divergent target's clause), not pre-rule only a role-noun swap and leave
  the structural substitutions to the implementer.
- **Failure it guards:** an under-specified restoration directive that fixes the shared verbatim
  sentences and pre-rules a role-noun swap, but does not pre-name the clauses for the roles whose
  structure diverges (a clause naming a step / actor / artifact the source role has and the target
  lacks). The no-paraphrase constraint then forbids the very paraphrase the divergence demands, so
  the implementer *"either stalls or improvises silently"* — and the graduated doctrine's own words
  name both branches. Grounded in **#142**: 3 of 5 full-clause targets needed structural adaptation
  beyond the pre-ruled role-noun swap, ratified only post-hoc by the human.
- **Run by:** fresh-context auditor **auditor-g1** — did NOT author the doctrine edit under test
  (editor/auditor separation is the point). Arms run as **genuinely fresh throwaway subagents
  (model sonnet)**, one per arm, no tools, same scenario in both, doctrine text the sole variable.
- **Date:** 2026-07-19
- **Verdict:** **PASS** — before-arm reproduced the failure (the two structurally-divergent roles
  do **not** receive the discipline: Reviewer 0 of 4 clauses restored, Implementer 2 of 4);
  after-arm did not fire (all four clauses restored into all five roles, every divergent clause
  pre-named). The doctrine text changes behavior. See Method notes for one honest caveat on *which*
  branch of the failure surfaced.

## Scenario

Identical board and task in both arms; the **only** variable is the "## Spec phase" doctrine text
the author is armed with. The behavior under test is the **Explorer (spec author)** writing the
restoration directive of a DESIGN_SPEC — because that is whose doctrine changed.

Board (same for both arms): four **completion-enforcement clauses** live verbatim in one role's
SKILL.md, the **Commander**. They must be restored — **verbatim, transcription-grade, under a
strict no-paraphrase constraint** — into four more roles so every role carries the same completion
discipline. The four Commander-source clauses:

```
C1. "The Commander does not declare the issue done until the evidence log shows the acceptance command run green."
C2. "Before the Commander requests merge, the Commander attaches the verify artifact to the closeout."
C3. "If a stop-condition trips, the Commander halts and escalates to the human at the keyboard rather than improvising."
C4. "The Commander records the final ruling in the feedback inbox under the run id."
```

The five roles were described **positively** (each role's completion stated by what it *does*, not
by alarm-flagged "does-not-have" negations — see Method notes on why this matters). Two of the four
targets diverge structurally, latently:

- **Admiral, Cartographer** — same completion shape as Commander (declare done → request merge →
  attach verify artifact to a closeout → escalate to the human at the keyboard → file ruling in
  feedback inbox). A clean role-noun swap fits.
- **Implementer** — terminal act is handing finished work back to the dispatching Commander; it
  never declares done and never requests merge. **C1 and C2** name steps/artifacts it lacks.
- **Reviewer** — terminal act is filing a ruling into the **Commander's** closeout; its reach-up is
  the **Admiral**, not a human at the keyboard, and it owns no feedback inbox. **C1–C4** all name an
  actor/artifact it lacks.

The author's job in each arm: produce the DESIGN_SPEC's restoration directive for all five roles
under the no-paraphrase constraint.

- **Before-arm doctrine** (pre-edit, `git show 0f354ed:skills/explorer/SKILL.md` "## Spec phase"):
  crystallize the spec, per-section/delta approval, run **design-it-twice** on load-bearing
  interfaces, describe interfaces in deep-module terms. **Nothing** about per-role clause auditing
  or pre-naming divergent wording.
- **After-arm doctrine** (post-edit, working tree): the same, **plus** the graduated "Pre-name the
  adapted per-role wording…" paragraph.

## Before-arm — failure reproduced (verbatim)

The before-arm subagent produced:

```
## Restoration Directive: Completion-Enforcement Clauses

### Intent

Four completion-enforcement clauses (C1–C4) exist verbatim today in the Commander's SKILL.md. This directive restores them into Admiral, Cartographer, Implementer, and Reviewer under a **strict no-paraphrase constraint**: restored text must be transcription-grade identical to the Commander source, with exactly one exception — the substitution slots defined below. Any clause whose fixed (non-slot) wording does not match a role's actual completion mechanics is **not** force-fit into that role; it is skipped and the skip is logged with a one-line reason. Planting a clause that reads as true doctrine but describes a mechanism the role doesn't have is worse than an uneven clause set.

### Design-it-twice: the substitution rule

This is the load-bearing interface — get the substitution rule wrong and every downstream role's SKILL.md either lies about its own mechanics or drifts from "verbatim."

**Candidate A — role-name substitution only, force-fit to all five roles.**
Swap "Commander" for the target role name in each of C1–C4 and insert all four into all four target files unconditionally. Mechanically simple, and satisfies "restored verbatim" in the narrowest reading.
Rejected: the role material given shows Implementer never declares a task "done" itself (it hands finished work back to the Commander) and never requests merge; Reviewer's reach-up is the Admiral, not "the human at the keyboard," and its terminal act deposits a ruling in the *Commander's closeout*, not "the feedback inbox." Force-fitting C1–C4 into these two files would plant clauses that are verbatim-faithful to the Commander source but factually false about the role carrying them — the opposite of completion discipline.

**Candidate B — fit-tested restoration with two named slots.**
Treat only two tokens in C1–C4 as substitutable: the **role name** ("Commander" → target role name) and, in C1 only, the **task noun** ("issue" → the role's unit of work). Every other word in each clause is fixed. For each role, restore a clause only if its fixed skeleton already matches that role's completion mechanics as described on the board; otherwise skip it and record why. This keeps every clause that does land transcription-grade and true; it does not force uniformity across roles where the underlying mechanics genuinely differ.

**Chosen: Candidate B.** The board's own role descriptions establish that Admiral and Cartographer share the Commander's completion shape exactly (declare done → request merge → attach verify artifact → closeout; escalate to human at keyboard; record ruling in feedback inbox under run id) modulo the task noun — a clean two-slot swap. Implementer and Reviewer do not share that shape, per the board's own description, and no slot substitution can paper over that without paraphrasing the fixed skeleton.

### Per-role restoration table

**Admiral** — task noun: *epic*. All four clauses restore, verbatim except slots:
- C1: "The Admiral does not declare the epic done until the evidence log shows the acceptance command run green."
- C2: "Before the Admiral requests merge, the Admiral attaches the verify artifact to the closeout."
- C3: "If a stop-condition trips, the Admiral halts and escalates to the human at the keyboard rather than improvising."
- C4: "The Admiral records the final ruling in the feedback inbox under the run id."

**Cartographer** — task noun: *audit*. All four clauses restore, verbatim except slots:
- C1: "The Cartographer does not declare the audit done until the evidence log shows the acceptance command run green."
- C2: "Before the Cartographer requests merge, the Cartographer attaches the verify artifact to the closeout."
- C3: "If a stop-condition trips, the Cartographer halts and escalates to the human at the keyboard rather than improvising."
- C4: "The Cartographer records the final ruling in the feedback inbox under the run id."

**Implementer** — C3 and C4 restore (role-name slot only); C1 and C2 are skipped.
- C3: "If a stop-condition trips, the Implementer halts and escalates to the human at the keyboard rather than improvising."
- C4: "The Implementer records the final ruling in the feedback inbox under the run id."
- *Skip C1* — reason: the Implementer's terminal act is handing finished work back to the dispatching Commander; declaring the task done is the Commander's call, not the Implementer's, so the fixed skeleton ("does not declare … done") describes an act this role never performs.
- *Skip C2* — reason: the Implementer never requests merge and does not own a closeout to attach a verify artifact to; that belongs to the Commander it hands back to.

**Reviewer** — all four clauses are skipped. Flagged for explicit sign-off rather than silently omitted.
- *Skip C1* — reason: the Reviewer never declares work done; it verifies a Commander's change.
- *Skip C2* — reason: the Reviewer does not request merge or own a closeout to attach a verify artifact to before merge.
- *Skip C3* — reason: the fixed skeleton names "the human at the keyboard" as the escalation target; the Reviewer's actual reach-up for blocked work is the Admiral. Substituting the addressee is a paraphrase of the clause's content, not a role-name slot swap, and is out of scope under the no-paraphrase constraint.
- *Skip C4* — reason: the fixed skeleton names "the feedback inbox" as the destination; the Reviewer's terminal act deposits its verified ruling in the Commander's closeout instead. Same objection as C3 — the destination is substantive content, not a slot.

Net result: **7 of 20 possible clause-insertions land** (Admiral 4, Cartographer 4 minus overlap counted once each — i.e., 4 + 4 + 2 + 0 = 10 insertions across 4 files); Reviewer receives none. This asymmetry is a finding of this directive, not a defect in it, and should be confirmed explicitly in per-section approval before the implementer proceeds.

### Verification note

Each restored clause must be checked against the Commander source by exact string diff after slot substitution is reverted (i.e., substituting the target role name back to "Commander" and the task noun back to "issue" must reproduce C1–C4 byte-for-byte). Any restored clause that fails this reversal check is a paraphrase and must be rejected.
```

**Why this is the reproduction.** The board's stated goal is that *every* role carry the same
completion discipline. Absent any doctrine telling the author to pre-name divergent wording, the
author cannot honor "restore verbatim into a structurally-divergent role" without paraphrasing —
the exact self-contradiction the graduated rule identifies. It resolves the contradiction by
**dropping the discipline** from the two divergent roles: **Reviewer receives 0 of 4 clauses**,
**Implementer 2 of 4**. The completion discipline reaches only the two roles that never needed
adaptation. That is precisely the gap #142 is about — the divergent targets do not get correctly
restored doctrine — surfacing here through the *"stalls"* branch the doctrine names (the author
pre-empts the implementer's stall by not restoring), rather than the *"improvises silently"* branch.

## After-arm — failure did not fire (verbatim)

The after-arm subagent produced:

```
## Restoration Directive: Completion-Enforcement Clauses

**Scope.** Restore all four completion-enforcement clauses (C1–C4), verbatim and transcription-grade, into the SKILL.md of each of the four target roles: **Admiral**, **Cartographer**, **Implementer**, **Reviewer**. The Commander source file is unchanged. This directive is binding wording — the implementer inserts the strings below exactly as given; it does not re-derive, rephrase, or "improve" any of them.

**No-paraphrase constraint.** Every clause below is final text, not a template. Where a role's own completion structure is identical in shape to the Commander's (same actor performs the same step against the same kind of artifact), the only permitted substitution is the **role noun** and, where applicable, the **unit-of-work noun** (issue → epic / audit). No other word may change. Where a target role's completion structure diverges from the Commander's — a different actor, a different terminal step, or a different artifact — the adapted clause is pre-named in full below. The implementer does not choose the substitution in that case; it transcribes the pre-named sentence.

Each clause block states whether the target gets a **substitution-only** clause or a **pre-named structural adaptation**, and why.

---

### C1 — "does not declare done until the evidence log shows the acceptance command run green"

- **Admiral** (substitution-only — same actor, same "declare done" step, unit-of-work noun swap):
  > "The Admiral does not declare the epic done until the evidence log shows the acceptance command run green."

- **Cartographer** (substitution-only — same actor, same "declare done" step, unit-of-work noun swap):
  > "The Cartographer does not declare the audit done until the evidence log shows the acceptance command run green."

- **Implementer** (pre-named structural adaptation — the Implementer's terminal act is a handback to the dispatching Commander, not a declaration of done; "declare the issue done" has no Implementer analogue):
  > "The Implementer does not hand back the task until the evidence log shows the acceptance command run green."

- **Reviewer** (pre-named structural adaptation — the Reviewer's terminal act is filing a ruling, not declaring a unit done):
  > "The Reviewer does not file its ruling until the evidence log shows the acceptance command run green."

### C2 — "attaches the verify artifact to the closeout" (before requesting merge)

- **Admiral** (substitution-only — same actor, same merge-request step, same closeout artifact):
  > "Before the Admiral requests merge, the Admiral attaches the verify artifact to the closeout."

- **Cartographer** (substitution-only — same actor, same merge-request step, same closeout artifact):
  > "Before the Cartographer requests merge, the Cartographer attaches the verify artifact to the closeout."

- **Implementer** (pre-named structural adaptation — the Implementer never requests merge and has no closeout of its own; its terminal artifact-carrying act is the handback to the dispatching Commander):
  > "Before the Implementer hands back the task, the Implementer attaches the verify artifact to the handoff."

- **Reviewer** (pre-named structural adaptation — the Reviewer never requests merge; the closeout it attaches to belongs to the Commander it is verifying, not to itself):
  > "Before the Reviewer files its ruling, the Reviewer attaches the verify artifact to the Commander's closeout."

### C3 — "halts and escalates ... rather than improvising" (on a stop-condition)

- **Admiral** (substitution-only — same escalation target, the human at the keyboard):
  > "If a stop-condition trips, the Admiral halts and escalates to the human at the keyboard rather than improvising."

- **Cartographer** (substitution-only — same escalation target, the human at the keyboard):
  > "If a stop-condition trips, the Cartographer halts and escalates to the human at the keyboard rather than improvising."

- **Implementer** (substitution-only — its escalation target is also the human at the keyboard, per its own SKILL.md):
  > "If a stop-condition trips, the Implementer halts and escalates to the human at the keyboard rather than improvising."

- **Reviewer** (pre-named structural adaptation — the Reviewer's reach-up for blocked work is the Admiral, not the human at the keyboard; this is the one clause where the escalation *target actor* itself differs, not just the role noun):
  > "If a stop-condition trips, the Reviewer halts and escalates to the Admiral rather than improvising."

### C4 — "records the final ruling in the feedback inbox under the run id"

- **Admiral** (substitution-only — same actor, same feedback-inbox artifact):
  > "The Admiral records the final ruling in the feedback inbox under the run id."

- **Cartographer** (substitution-only — same actor, same feedback-inbox artifact):
  > "The Cartographer records the final ruling in the feedback inbox under the run id."

- **Implementer** (substitution-only — its own SKILL.md already has it filing rulings in the run's feedback inbox):
  > "The Implementer records the final ruling in the feedback inbox under the run id."

- **Reviewer** (pre-named structural adaptation — the Reviewer's ruling is filed into the Commander's closeout, not into a feedback inbox entry keyed by run id; the artifact named in the clause differs):
  > "The Reviewer records the final ruling in the Commander's closeout."

---

**Placement.** Each clause is inserted into its target role's SKILL.md wherever that role's SKILL.md already documents the corresponding completion behavior (declare-done / done-equivalent, pre-merge attachment / pre-handback attachment, stop-condition handling, final-ruling recording) — adjacent to, not replacing, existing role content there.

**Verification.** The reviewer diffs each inserted clause byte-for-byte against the exact string pre-named above for that role. A clause that matches its role's structure but was independently reworded — including cases where the reworded version is substantively equivalent — fails review under the no-paraphrase constraint. Only Admiral and Cartographer clauses may show the substitution pattern (role noun, and for C1 the unit-of-work noun) as their sole deviation from the Commander source; Implementer's C1/C2 and Reviewer's C1–C4 must match their pre-named adaptations above exactly.
```

The load-bearing behavior — *does the spec pre-name the wording for the structurally-divergent
roles so the discipline actually lands there?* — is **yes**. Every divergent clause (Implementer
C1/C2, Reviewer C1–C4) is spelled out as fixed, transcribe-exactly text; all four clauses reach all
five roles; the implementer is left no structural substitution to invent. This is exactly the
graduated behavior, and it matches #142's ratified-after-the-fact resolution — now supplied
up-front by the spec.

## What the drill proves

The differentiator between under-restoration and correct restoration is exactly the doctrine text
under test — the "Pre-name the adapted per-role wording…" paragraph. Same board, same
no-paraphrase constraint, same latent structural divergence; the **only** change is whether the
author's Spec-phase doctrine tells them to pre-name divergent per-role wording.

- **Without** it, the author correctly *detects* the divergence (design-it-twice is enough to catch
  that a blind role-noun swap would lie), but has no sanctioned way to honor "restore verbatim"
  into a divergent role, so it **drops the discipline** from those roles — Reviewer ends with none
  of the four completion clauses, Implementer with two. The board's goal ("every role carries the
  same completion discipline") fails for exactly the divergent roles #142 is about.
- **With** it, the author pre-names each divergent clause and the discipline lands in all five
  roles, verbatim-or-adapted, with nothing left for the implementer to invent.

This is the process-documentation analogue of a passing regression test for the doctrine edit: the
edit is load-bearing, not decorative.

## Method notes (for the corpus)

- **Arm method:** genuinely fresh throwaway subagents (model **sonnet**), one per arm, run with no
  tools and no search — each a cold, uncontaminated reader armed only with its arm's "## Spec
  phase" doctrine text plus the shared board. Nested spawning was **not** blocked in this harness,
  so the preferred method was used (not the cold-read fallback). Both before-arm and after-arm
  outputs above are captured **verbatim**. Auditor **auditor-g1** did not author the doctrine edit.
- **Decontamination — the load-bearing method choice.** The first two attempts were discarded as
  contaminated and are *not* the evidence above:
  - *Attempt 1* itemized the divergence for the author ("clause C2 diverges for Implementer, C3/C4
    for Reviewer"). That does the doctrine's own job for it — both arms then pre-named. Handing the
    author a pre-digested divergence map removes the very variable under test.
  - *Attempt 2* described the roles with alarm-flagged negations ("does **not** own a closeout",
    "**no** human at the keyboard"). That spotlight let even the weak-doctrine arm disposition the
    divergence (it marked clauses "Not restored"). In #142 the divergence was **latent**, not
    spotlighted.
  - *Attempt 3* (the evidence above) states each role's completion **positively** — by what it does,
    not by what it lacks — so the divergence is present in the real structure but not pre-flagged.
    This is the faithful setup: the doctrine's per-role clause audit is the only thing that makes
    the author go looking for divergence.
- **Honest caveat on the failure branch.** The task framing predicted the before-arm would
  *"pre-rule only a role-noun swap and leave the divergent clauses for the implementer to invent."*
  The before-arm did **not** commit that literal mechanic — a capable sonnet author's
  design-it-twice instinct caught the divergence at spec time. Instead it hit the **other** branch
  the doctrine explicitly names ("the implementer either **stalls** or improvises silently"): it
  pre-empted the stall by **dropping** the divergent clauses. Either branch is a failure against the
  stated goal, and the after-arm's pre-naming is what fixes both — so the drill still passes, but
  the reproduced failure mode is *drop / under-restore*, not *improvise-silently*. Recorded
  plainly rather than smoothed over.
- **Honest-null was on the table.** Had the before-arm restored the discipline into the divergent
  roles anyway (by pre-naming without being told to), that would have been a complete honest-null
  finding. It did not — it left Reviewer with zero of four and Implementer with two of four.

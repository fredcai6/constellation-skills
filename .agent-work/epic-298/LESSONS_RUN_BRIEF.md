# Run Brief: `epic-298`

Compiled for the Lessons Auditor. **Pointers and telemetry, not narrative.** The run log is ~300 entries; **do not read it as a story — sample it against what you are classifying.**

## Intent

One closed vertical slice proving Constellation skills can enter, consume and improve a shared observable knowledge substrate: the reworked lessons/episode framework (B1) and the Commander map-first tracer (B3), under B0's stochastic-boundary and two-bin principles. **Honest nulls are complete deliverables.**

## Shape

**17+ dispatches across 3 waves. 9 of 12 epic issues closed** (#307 arm complete/awaiting Tommy's verdict, #308 in flight, #310 not started). **#305 alone consumed EIGHT successive commanders**; three died mid-gate. Opus throughout for cold-panel and measurement work.

## MID-RUN DOCTRINE CHANGE — read this before classifying anything

**Tommy changed the model on 2026-08-02, and it invalidates artifacts written earlier in this same run.**

> *"There are no catastrophic failures, just workarounds and inefficiencies... the thing that is finding the episodes cannot make a call on the importance, that requires a more global view. It is not smart to ask our lower level agents to diagnose. We just want observations of what happened and how they worked around it."*

**An episode is an OBSERVATION, not a diagnosis:** the observable issue · the context · the effect, **including the workaround and how many times it was needed.** **No bin, no severity, no cause classification at capture time.** The **two-bin rule is withdrawn from field capture**, which contradicts #302 and Assumption 6 at the premise.

**Schema rule:** extra fields are fine; **required fields must be OBSERVABLE**, and anything needing judgement must be **optional and not solicited by name** — *naming the subject solicits the answer*.

**Consequence for you: artifacts from waves 0–2 were authored under the old model.** A "bin ruling" or "severity" in an earlier artifact is **historical, not current doctrine**. #308's disposition table and its `dispositions_done.py` check both assert withdrawn rules and carry correction banners.

## Project-customized templates

`.agent-work/templates/` — check against `.baseline/` per TEMPLATES_MANIFEST before attributing any defect to a shipped template. **`COMMANDER_SPINE.template.json` was modified by #304 in this epic** (map-first anchor + a `c2` orientation gate); a defect found there may be this epic's own change, not baseline.

## Artifact paths

- **Run log:** `.agent-work/epic-298/ADMIRAL_LOG.md` — **partially reconstructed** (see below). Sample, do not read through.
- **State note:** `.agent-work/epic-298/STATE_NOTE.md` — the digest; read first.
- **Launch orders:** `.agent-work/epic-298/launch-orders/` (299, 300, 301, 303, 304, 305, 307, 308, 309, 310, PRE-B)
- **Measurement:** `baselines/` (PRE-A + discriminated addendum + probes + corpus fingerprints), `preb/` (PRE-B, 125 files incl. reusable instruments), `post/` (POST arm, `POST_RECORD.md`, and the preserved void set)
- **Routing:** `BACKLOG_ROUTING.md` · **Feedback:** `.agent-work/{AGENT,CONSTELLATION}_FEEDBACK.md`
- **Playbook:** `.agent-work/LESSONS.md` — **being MIGRATED INTO EPISODES by #308, not deleted.** Do not route graduations into it.

## Integrity caveat you must account for

**The ADMIRAL_LOG was destroyed mid-run and partially reconstructed.** `.agent-work/` was gitignored at the old local `main`; fast-forwarding to a commit where #326 made it tracked overwrote the log with main's wave-0 version. **292 entries recovered** — 59 from scratchpad staging files, 121 mined from the session transcript, deduped by normalized prefix. **Some wave-1/2 entries may be absent. Treat gaps as loss, not as absence of activity.**

## Telemetry — the run's actual output

- **`a-check-that-cannot-fail` (#337): TEN costumes**, plus the unifying principle: **a check whose output is identical in the healthy and the defective world cannot discriminate, however correctly it runs.** Three routes there — **vacuity** (costumes 1–9), **wrong question** (a *can-this-fail?* sweep is structurally blind to *does-it-cover-what-it-claims?*, because the answer is "yes" in both worlds), and **wrong iteration set** (costume 10 — a comparison iterating only one side never enumerates what exists only on the other). **Mechanical detector: any guard that loops must ASSERT WHAT IT LOOPED OVER.**
- **Corollary:** *assert against the behaviour, never against text that describes the behaviour.*
- **Built-but-not-wired (#345): 8+ instances.** Commander-304: *"we reliably build the capability and unreliably wire the guarantee."* **#344 is the outermost ring — #304 was merged, tested, reviewed and ABSENT from the installed corpus**, so an arm run against it would have blamed the contract for a delivery failure.
- **Carry-pointers-never-copies: SIX surfaces** — state note, inbox (#339), shipped docs, Admiral launch briefs, a reviewer's frozen in-flight survey, and a SHA that expires on squash-merge (**the first where the reference is correct when written — a copy with a delayed expiry**).
- **#307's result:** `map_before_src` **0/4 → 4/4**, but **`read_at_bootstrap` 0/4 in BOTH arms** — **"map-first" as delivered is first-among-content, not first-among-actions.** Limitation stated first: the manipulation is 8 days and +31 files, **not #304 alone**.
- **#393:** `TREATMENT-VERIFIED` proves **hop 0 of three**. `SKILL.md` has zero occurrences of "map"; the contract lives only in the spine template. **This invalidated a claim the Admiral had repeated for two days.**
- **#383:** the **context gauge was silent for the entire multi-day run** — subagents inherit the parent session_id, so every crew claim adds a binding (30+). **The Governor fails on exactly the runs that need it most; the failure is anti-proportional to risk.**
- **#390:** a frozen gate imperative can be **measured false by the work it authorises**, with no supersede mechanism. Two commanders hand-built one.
- **The episode store implements the model it was just ruled against** — `agent_supplied` closed at five kinds, blanks inexpressible, `diagnosis` and a **required** `strength` both solicit judgement by name.
- **Admiral errors, self-reported: TEN+ claims failed against the tree, every one caught by the commander it was handed to.** The pattern: *I reason about what HAPPENED; the tree records what is IN FORCE.* Plus three merges past in-flight work, a worktree swept under a live commander, and the log destruction above.
- **Every cold plan critic this epic caught a blocking defect. No exceptions.**
- **~40 issues filed (#313–#397).** That volume is the epic's real output and **none of it is in the definition of done.**

## Instruction

**Every candidate gets a routed disposition.** Graduations go to a named permanent home — `skills/_shared/global-*.md` (**canonical, never the regenerated `references/` copies**) or `docs/agents/` — **never back into the playbook.** Constellation-scoped lessons always export.

**Weigh recurrence over severity.** Per the doctrine change above, a count across runs is evidence; a single agent's severity judgement is not.

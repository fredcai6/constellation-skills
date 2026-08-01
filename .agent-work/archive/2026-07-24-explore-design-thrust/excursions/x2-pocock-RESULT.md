# Excursion Result: `x2-pocock` — what the referenced Pocock material advocates about spike-forward exploration

**Question:** What does the recent Matt Pocock video referenced by issue #224 ("encourage more prototype spike forward exploration", filed 2026-07-24) actually advocate about prototype/spike-forward exploration in AI-assisted development, and which points apply to constellation's explorer/commander flow?

**Type:** research. **Verdict:** answered, with a scoped null on the exact video (see Scope).

---

## Scope — what WAS and was NOT verified

- **NOT verified:** I did not watch the specific "latest pocock video" #224 points at. YouTube pages return only footer chrome to fetch, so I could not pull the video's own audio/transcript. #224 names no URL, so I also cannot be certain *which* video the author meant.
- **The most likely referent** is Pocock's mid-July 2026 material introducing **`/wayfinder`** and the **v1.1 skills** release (`/wayfinder`, `/research`, `/prototype`, `/to-spec`, `/to-tickets`, `/implement`), announced ~July 8 with a walkthrough video ~July 9, 2026. This is the only recent material whose thesis is literally "spike-forward exploration," matching #224's title. An **earlier** June 5 workshop ("Workflow for AI Coding," AI Engineer 2026) advocates the *opposite* posture (spec-first, "explicitly rejects speculative or exploratory approaches") — so the June workshop is almost certainly NOT the referent; the wayfinder pivot is.
- **What I verified instead (primary sources, high trust):** the actual `SKILL.md` source for `wayfinder`, `prototype`, and `research` in `mattpocock/skills` on GitHub (the mechanism itself), plus Pocock's own X posts describing wayfinder. Secondary: a transcript summary of the "Agentic Engineering Workflow" video and two workshop write-ups. Where a secondary source and the primary SKILL.md disagree, I trust the SKILL.md.

---

## What the material advocates (claims + sources)

1. **Plan huge, foggy work as a shared *map* of investigation tickets, resolved one at a time.** `/wayfinder` charts work "too big for one agent session, wrapped in fog" as a map of **decision tickets** on the issue tracker, worked one at a time "until the way to the destination is clear." Source: [wayfinder SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md).

2. **The map grows as you learn, shrinks as you answer.** Pocock, on running ~100 grilling/prototyping/research sessions for one course: the central map "grows as I learn more about the problem, shrinks as I find answers to the questions… the next evolution of /grill-me." Source: [X @mattpocockuk](https://x.com/mattpocockuk/status/2072716979195326905).

3. **Plan, don't do — the pull to build is the signal you've hit the edge of the map.** Wayfinder produces "decisions, not deliverables"; "the pull to just do the work is usually the signal you've reached the edge of the map and it's time to hand off." Source: [wayfinder SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md).

4. **Four ticket types, each a different way to resolve one decision:** **research** (AFK subagent, primary sources), **prototype** (HITL, "raise the fidelity of the discussion by making a cheap, rough, concrete artifact to react to"), **grilling** (HITL, one question at a time — the default), and **task** (do manual work — sign up for a service, provision access, move data — that *unblocks a decision*, the one type that does rather than decides). Source: [wayfinder SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md).

5. **A prototype is throwaway code that answers ONE question; the question decides the shape.** Two branches: **logic** ("does this state model feel right?" → tiny interactive terminal app pushing the state machine through hard cases) and **ui** ("what should this look like?" → several radically different variants on one route, toggled by URL param). Rules: throwaway and clearly marked from day one; one command to run; no persistence; skip polish (no tests/error handling/abstractions); surface full state after every action; capture when done. Source: [prototype SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/prototype/SKILL.md).

6. **Capture the prototype as a primary source, not just delete it.** When done: fold the validated decision into real code, then commit the prototype "to a throwaway branch, out of main," and leave a context pointer to that branch on the implementation issue. Main keeps only the validated decision. Source: [prototype SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/prototype/SKILL.md).

7. **Research runs as a background agent against primary sources, output = one cited Markdown file in the repo.** "Follow every claim back to the source that owns it." Source: [research SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/research/SKILL.md).

8. **Exploration feeds a spec; it is not the whole flow.** Explicit correction from Pocock: the flow for big work is **`/wayfinder → /to-spec → /to-tickets → /implement`**; once the map is complete you turn it into a spec — "some folks are using /wayfinder as the ENTIRE flow… don't." Source: [X @mattpocockuk](https://x.com/mattpocockuk/status/2075856898142740821).

9. **Alignment before code: interview to ~98% understanding.** `/grill-me`: "list out the 10 most consequential decisions… interview me until you understand 98% about it." Exploratory work is marked "explore" and returned to the queue before implementation. Source: [transcript summary, sozai.app](https://sozai.app/transcript/matt-pocock-agentic-engineering-workflow/).

**Contradiction surfaced (not smoothed):** the June 5 workshop write-up says Pocock "explicitly rejects speculative or exploratory approaches… not through spikes or exploratory prototypes" and favors test-first specs ([explainx.ai](https://explainx.ai/blog/matt-pocock-ai-coding-real-engineers-workshop-2026)). The July wayfinder material is a **pivot toward** exploration-first. #224's "encourage MORE spike forward exploration" is consistent with the July pivot being the referent. This is a real reversal in Pocock's stance across ~6 weeks, not a mis-read of one source.

---

## Mapping: Pocock claim → constellation mechanism → verdict

| # | Pocock claim | Constellation's current mechanism | Verdict |
|---|---|---|---|
| 1 | Wayfinder: shared **map of investigation tickets** on the tracker, too big for one session | Explorer `IDEAS_BOARD.md` + repeatable cycles; **but** it's a single-session `.agent-work/` area, not persistent tickets on the issue tracker | **Partial / GAP** — same intent, different substrate. Constellation has no multi-session, tracker-native map whose tickets are claimed/resolved concurrently. Its board is one work-area file, not a live issue graph. |
| 2 | Map **grows as you learn, shrinks as you answer** | Ideas board: candidates, verdicts, open threads, rejected-with-reasons, cycle log — explicitly "grows/culls" each consolidation | **Already-have** (strong agreement) — the board *is* this, minus the tracker substrate. |
| 3 | **Plan, don't do**; the urge to build = edge of the map, hand off | Explorer headline doctrine #1: "premature convergence is THE failure mode"; agent never initiates convergence; explorer never cuts issues | **Already-have** (strong agreement) — near-identical philosophy, and constellation's is *harder-edged* (mechanical gate `verify_spec_confirmed.py`, not just exhortation). |
| 4 | Ticket types: research / prototype / grilling / **task** | Excursion types: **research / prototype / design-it-twice**; grilling = the cycle-as-interrogation | **Mostly already-have, one GAP** — constellation *adds* design-it-twice (Pocock has no equivalent). Constellation *lacks* Pocock's **`task`** type: manual do-work (provision access, move data) that unblocks a *decision*. Worth considering as an excursion/off-ramp type. |
| 5 | Prototype = throwaway code, one question, logic/ui branches, one command, no persistence, surface state | `constellation-prototyper` — **explicitly "Adapted from mattpocock/skills"** | **Already-have** (direct descendant). Differences: constellation adds a **measurement** branch (Pocock's prototype is logic/ui only); constellation's `PROTOTYPE_HANDOFF`/`RESULT` interface + mandatory `NOT tested` line are stricter. Agreement. |
| 6 | Capture prototype as a **primary source** on a throwaway branch; pointer on the issue | Prototyper disposition: **deleted / absorbed (record commit ref) / parked-with-owner** | **Agree with a delta** — constellation's default is delete-or-absorb; Pocock defaults to *keep the throwaway branch as a primary source* + pointer. Constellation could add "captured-to-throwaway-branch + issue pointer" as an explicit disposition flavor rather than folding it under "parked." Minor gap. |
| 7 | Research = background agent, primary sources, one cited Markdown file in-repo | Explorer research excursion: **background** subagents via `run_crew.py`, cited findings, durable registry (`recover_crews.py`) | **Already-have** — constellation is *more* durable (crash-safe registry vs. plain background agent). |
| 8 | Flow: wayfinder → to-spec → to-tickets → implement; exploration feeds a spec, isn't the whole flow | explorer → **to-issues** → admiral/commander → implement; explorer "never cuts issues itself" | **Already-have** (structural match). constellation-explorer ≈ wayfinder+spec, constellation-to-issues ≈ to-tickets, commander/admiral ≈ implement. The "don't let exploration become the whole flow" boundary is enforced mechanically in constellation (explorer can't cut). |
| 9 | Alignment first: interview to ~98%, mark work "explore" and requeue | Commander/explorer `understand` step loads `constellation-interrogator` (one question at a time, recommended answers, code-answers-over-questions) | **Already-have** — the Interrogator *is* /grill-me's analogue, shared by explorer cycles and commander understand. |

---

## Directly answering #224's second hunch: "commanders can explore as part of interrogation — double-check"

**Partly true, with a real gap.** The Commander `understand` step loads `constellation-interrogator`, which carries a **code-answers-over-questions** convention, and the step includes a **feasibility probe** (run a trivial headless action to settle a question empirically instead of asking). So a Commander *can* do a lightweight spike during interrogation.

**But** the Commander's `understand` step has **no formal prototype/research/design-it-twice excursion off-ramp** — that machinery (the `EXCURSION_BRIEF`, the three excursion types, durable background dispatch, on-ramp before consolidation) lives only in **explorer**. A Commander who hits a genuine "how should this behave / look" question mid-interrogation has the interrogator's informal code-answers convention and the feasibility probe, but not the explorer's structured prototype excursion. If #224 wants Commanders to "spike forward" the way explorer does, that off-ramp would need to be ported (or explicitly scoped out as "escalate to an explorer excursion instead"). **This is the concrete design decision #224 surfaces.**

---

## One-line bottom line

Pocock's July "spike-forward" pivot (wayfinder + prototype + research) is ~80% already-embodied in constellation — often more strictly (mechanical gates, durable dispatch, design-it-twice, mandatory disposition). The two genuine deltas worth a design thread: (a) a **`task`-type** off-ramp for manual decision-unblocking work, and (b) giving the **Commander's interrogation** a real prototype excursion off-ramp rather than only the informal code-answers/feasibility-probe it has today.

---
name: constellation-prototyper
description: Build a throwaway prototype that answers one named design question, then dispose of it. Use when a handoff defines the question, branch, host conventions, and location.
---

# Constellation Prototyper

Build throwaway code that answers **one named design question** — then keep the answer, not the code. Crew-tier, handoff-driven: no engine checklist, no spine. Work the `PROTOTYPE_HANDOFF` directly and return a `PROTOTYPE_RESULT`.

Dispatchable three ways, same contract each time: as an **explorer** excursion (the excursion brief carries the prototype fields), by a **Commander**, or **standalone** by the human. The interface is `PROTOTYPE_HANDOFF` in → `PROTOTYPE_RESULT` out. The prototype artifact is not part of the interface — it is implementation, disposed at closeout.

Adapted from [mattpocock/skills](https://github.com/mattpocock/skills)' prototype skill.

## Core doctrine

A prototype is **throwaway code that answers one named question — the question decides the shape.** Everything below follows from that.

- **The question is written down before any code.** No named question, no prototype — send the handoff back. The question, not a framework or a backlog, decides what to build and when you are done.
- **One command to run.** A prototype nobody can start answers nothing. State the single command in the result.
- **No tests, no persistence, no polish.** It is throwaway. Effort spent hardening it is effort stolen from the answer. (The one thing that *may* survive is a pure logic module — see `references/logic.md` — but the shell around it stays disposable.)
- **Surface full state after every action.** The whole point is to see the shape react; hidden state hides the answer. Dump the complete state on every step, not a tasteful summary.
- **Delete or absorb when done.** The answer is the only thing worth keeping. A prototype that lingers becomes something people trust, which is the rot this skill refuses.

## Scoped nulls

Inherited doctrine — see `references/global-everyone.md` §"Scoped nulls". A prototype that says "no" has **scoped** its no. Prototype-specific: "State machines don't work here" is never a prototype's verdict; "this reducer shape thrashed on concurrent edits, tested single-threaded only" is. The `NOT tested` line in the result is **mandatory**, not a courtesy — a null with an empty scope is an unfinished result. When you are tempted to write "this can't work," write "this variant failed; here's the next variant worth trying" instead, and say so in the result — a good null is progress, not a dead end.

## Pick the branch

The handoff names the branch. If it doesn't, the question does — one decision rule each:

- **logic** — the question is *"does this state model / data shape feel right?"* Anything about reducers, state machines, event ordering, or the shape of the data. Build an interactive terminal app over a pure, portable logic module. See `references/logic.md`.
- **ui** — the question is *"what should this look like?"* Anything about layout, visual hierarchy, or which arrangement reads best. Build 3–5 structurally different variants on one route. See `references/ui.md`.
- **measurement** — the question is *"is X actually faster / smaller / better?"* Anything answered by a number. Define the metric first, implement one mechanism, put the number on the board. See `references/measurement.md`.

If a question splits across branches, split it into separate prototypes with separate handoffs — one question each.

## Location: split by driver

The handoff states the location; it follows from who drives the prototype.

- **Human-driven** prototypes — a logic TUI or UI variants the human will run and eyeball — live **in-repo, next to the real code**, clearly named as prototypes (e.g. a `*.prototype.*` marker or a marked route), one command to run. The human needs to start them without a worktree dance, and a UI variant mounted on a real page exposes problems an empty scratch route hides.
- **Agent-driven** spikes — a measurement mechanism, or parallel wild ideas — live in **throwaway worktrees**. Nobody eyeballs them live; they emit a number or a finding and are torn down.

In-repo prototypes carry a rot risk the clear naming and the mandatory disposition exist to defend against. That defense only holds if closeout actually happens.

## Closeout: disposition is mandatory

Every prototype records a **disposition** at closeout — one of exactly four, no silent rot:

- **deleted** — the answer is captured in the result; the code is gone.
- **absorbed** — a surviving piece (usually the pure logic module) was lifted into real code; record the **commit ref**.
- **parked-with-owner** — kept alive deliberately; name the owner and why. Parking without a named owner is not a disposition, it is rot.
- **captured-to-worktree** — kept as a worktree/branch reference, with a pointer from the owning issue, until the human disposes it (human ruling: keep until done — this is not a park-forever). Captured worktrees accumulate, so they carry a cap: they are swept at epic close, where each one is either re-affirmed or disposed. No new sweep automation exists for this — the cap is enforced by that closeout review, not a script.

The result is not complete until its disposition field names one of these. A prototype with no recorded disposition is the failure mode this rule exists to prevent.

## Interface

- **In:** `templates/PROTOTYPE_HANDOFF.template.md` — the one named question, branch, host-project conventions, location, stop conditions, return format.
- **Out:** `templates/PROTOTYPE_RESULT.template.md` — the answer, what was tested and what was NOT tested, what it taught beyond the question, any surviving module and where it lives, and the disposition.

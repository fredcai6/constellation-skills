# Design-it-twice brief — #467 A2 trip semantics

Panel of **3** (not a single): this introduces a load-bearing interface — issue #467 states
that **#424 (F) cannot ship a signature for `advance` until this settles**, so the shape
chosen here is consumed by another workstream. Panel-vs-single choice surfaced to the
Admiral at plan approval.

## The one design question

**How does the engine distinguish an `advance` that carries a handoff from one that starts
new work, so that at/over the HARD band it refuses only the second — and how does it then
mechanically observe whether the agent complied?**

## Why it matters (do not re-derive; this is settled ground)

Read at `d376b786`, `scripts/checklist_engine.py`:

- `advance()` (`:1854`) is the **only** writer of the append-only `why_trail`
  (`_append_why`, `:1095`), and the latest live why-record **is** the `DIGEST`
  (`_digest`, `:1139`) rendered on `current` (`_why_suffix`, `:1179`).
- `DIGEST:` + `ACTIVE <gate> — <imperative>` is the **entire** cold-start surface a fresh
  successor reads. No separate handoff document is ever written.
- `_trip_hard_gate` (`:1439`) is called from `dispatch` (`:2679`) **before** `advance` runs
  and raises unless a non-superseded `refresh-request` evidence item targets the gate with
  `why_ref == _latest_why_record(cl).id`.
- The refusal text says advance "is blocked", and the reach-up doctrine
  (`global-everyone.md` §reach-up) tells a tripped agent to file the refresh-request **and
  go idle**. Both point the agent away from the only verb that records what it learned.
  Result: the successor cold-starts on the *pre-trip* understanding. That is #431.

## Your assigned constraint

Each candidate is authored under exactly ONE named constraint. Do not hedge toward the
others; make your constraint's best case.

- **Candidate A — zero new CLI surface.** The distinction must be inferable from state the
  engine already holds. No new verb, no new flag on `advance`. Rationale to maximise: #424
  wraps the verbs as typed tools; a shape that changes no signature costs F nothing.
- **Candidate B — intent stated, never inferred.** The agent declares which advance this is
  (an explicit flag or a distinct verb). No engine decision rests on guessing what the agent
  meant. Rationale to maximise: a governor that infers intent from an artifact's presence
  cannot tell "I filed my handoff" from "an old artifact happens to be lying there".
- **Candidate C — move the refusal, add no machinery.** HARD stops refusing `advance`
  altogether and refuses `start` instead: closing the gate you are in is always allowed,
  beginning the next gate is what is blocked. No new evidence semantics, no new flags — the
  two verbs that already exist carry the distinction.

## Every candidate must also answer these three

1. **DC6 — the mechanical compliance observable.** With no refusal there is no
   self-recording: an instruction is satisfied or ignored with identical traces. #467 names
   the replacement shape: *the engine can see whether a handoff artifact appeared before the
   next advance at an over-threshold gate.* Say exactly where that record lives, what it
   contains, and what makes it **fail red** when an agent ignores the instruction. A design
   whose compliance signal is green in both the healthy and the defective world is
   disqualified — this is the epic's central defect and shipping one inside the fix for it
   is the failure mode we are being paid to avoid.
2. **DC4 — per-gate threshold override.** One graded default (today: `_PROFILES`,
   global-per-model, 1M-window models 80K soft / 150K hard → 0.08/0.15) plus an override
   mechanism that exists and is exercised at least once — one gate demonstrably carrying an
   override that changes its behaviour and **not its neighbours'**. Hand-authoring one per
   gate would invent 68 ungraded placeholders. Say where the override is read from and how
   precedence resolves. Also rule: **fraction or absolute headroom?**
3. **Two-way testability.** #467 requires DC2 tested both ways: an advance that starts new
   work above threshold is refused; one carrying a handoff is not. State the two tests and,
   for each, the exact source branch that must be broken to turn it red (mutation test).

## Fixed — not open to any candidate

- A missing or failed reading **never** forces a handoff. Every band no-ops on `None`.
- HARD means "wrap up", never "you are unsafe".
- The reading is **pushed** by the engine on tool use, never fetched by the agent.
- The trip checks at **gate boundaries only**; there is no mid-gate check.
- The global default threshold is **not** yours to retune (it is a production default; the
  Admiral has it marked for the human).
- `refresh-request` payloads are **pointers only** (`{seam, why_ref}`) — never copies of
  state.

## Comparison axes (report against all four)

**Depth** (behaviour delivered per unit of interface a caller must learn) · **Locality**
(does change and verification concentrate in one place) · **Seam placement** (the Trip bands
today ride the CLI boundary in `dispatch` so the verb functions stay pure and existing
exact-equality tests keep passing — say whether your candidate holds that line or breaks it,
and what breaking it costs) · **Testability** (can each pathway be exercised and falsified).

## Deliverable

Return via `SendMessage` to `commander-w4-467` before ending your turn. Keep it under ~500
words plus the code sketch. State: the mechanism, the DC6 record's exact shape, the DC4
override's location and precedence, the two DC2 tests with their mutation targets, the four
axes, and the **one thing your constraint makes worse**. Do not write files outside
`.agent-work/issue-467-trip-semantics/dit/`. Do not edit any source file.

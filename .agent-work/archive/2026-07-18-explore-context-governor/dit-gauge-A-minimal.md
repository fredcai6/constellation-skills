# Design-it-twice — Gauge module, Candidate A: MINIMAL-INTERFACE

**Constraint assigned:** the file is the smallest viable payload; simplest write, simplest read, simplest staleness rule; a reader learns almost nothing new.

**Scope:** module 2 (Gauge) only, per `DESIGN_SPEC.md`. Design only — no implementation.

---

## The interface

### Payload

The file contains exactly one thing: a single ASCII float, the fill fraction, on one line, nothing else.

```
0.62
```

No JSON. No object. No keys. No window size, no model name, no timestamp, no session metadata, no schema version. The writer computes `fill / window` itself (it already has to know both numbers to do the arithmetic at all — see "what this costs," below) and emits only the ratio. A reader gets a number between 0.0 and 1.0 and nothing else — this is deliberately "almost nothing new": it cannot tell you the model, the raw token counts, or why the number is what it is.

### File location convention

One file per running agent session, named by the session identifier the harness already has (Claude Code's session id from `transcript_path`, Codex's session/thread id, pi's session id), in a single well-known directory:

```
<workspace-root>/.constellation/state/gauge/<session_id>
```

No further structure — flat directory, filename is the whole addressing scheme. The engine, which already knows which session it is evaluating a gate for (it invoked or is tracking that agent), constructs the same path and reads it. This is the entire location contract: one id, one file, one directory.

### Write cadence

The writer overwrites this file on every tool call (fixed by the shared design upstream of this module). Under this module's discretion is only *how* the write happens: an atomic write (write to a temp file in the same directory, then rename over the target) so a concurrent read by the engine never observes a half-written line. That's the one piece of write-side machinery this design does not omit, because omitting it would let the read side observe garbage on a scheduling unlucky day — a correctness invariant, not an added feature.

### Staleness / freshness rule

No embedded timestamp field — the file's own filesystem mtime *is* the freshness signal. This is the simplest rule available: it costs the writer nothing extra to produce (the OS sets it automatically) and costs the reader one `stat` call, no timestamp parsing, no clock-skew reasoning between writer and reader processes.

- **Fresh:** `now - mtime <= max_age` (a single config knob, default on the order of minutes — long enough to tolerate a slow tool call or a thinking pause between calls, short enough to catch a writer that silently died).
- **Stale:** `now - mtime > max_age`, or the file's mtime cannot be read at all.

### Read contract

At each gate, the engine does exactly one read of one file:

1. `stat` the file. Missing → no reading.
2. Check mtime against `max_age`. Stale → no reading.
3. Read the single line, parse as a float.
4. Parse failure, or a value outside `[0.0, 1.0]` → no reading. (A value >1.0 is not clamped and used — it's treated as evidence the writer's arithmetic or the file itself is untrustworthy, and collapsed into the same fail-safe path as "missing.")
5. Otherwise: this fraction is the reading.

Every failure mode — missing, stale, corrupt, out-of-range — lands on the *same* single fallback: **no reading**. There is one fail-safe path, not three special-cased ones, which is itself part of what "simplest" buys here.

### Fail-safe (invariant, restated precisely for this design)

"No reading" means: the engine's gate logic proceeds exactly as if the Gauge module did not exist — no advisory question, no forced handoff. The engine never infers a high-fill state from absence; absence is silence, not alarm. The agent never reads this file itself (unchanged from the shared design — worth restating because a minimal single-scalar file is *tempting* to have an agent `cat` directly for self-report; that temptation should be resisted for the same self-report-is-confabulation reason the whole module exists).

---

## Does the thin payload starve Trip (module 3)?

The brief flags this directly, so an honest answer, not a dodge.

**Trip's stated need:** "model-keyed thresholds... need fill vs the model's window." A fraction-only payload *can* serve this — but only under one condition: **the engine must learn which model is running from somewhere other than the gauge file.** If the engine already knows the model (it dispatched the agent, or the model is recorded in engine/session state elsewhere), then Trip's per-model soft/hard thresholds are themselves just stored as fractions (e.g. Opus soft = 0.75, Haiku soft = 0.80) and this payload is sufficient — the model-keying happens on the *threshold table*, not on the gauge reading.

**Where it genuinely starves Trip:** if the engine has no independent line on the model (model swapped mid-session, or the engine's session record doesn't carry it), a bare fraction gives Trip nothing to key on — it is forced to a single universal threshold across every model, losing per-model calibration entirely. That is a real gap this design does not close; it assumes the model identity is available to the engine through some channel *other* than this file. If that assumption is false, the minimal payload is not "thin but sufficient," it's *actually insufficient* for the stated Trip requirement, and the fix would be re-widening the payload (a second field) — which is exactly the kind of scope creep this constraint is supposed to resist, so it needs to be named rather than quietly absorbed.

**A second, smaller starvation:** raw fill/window numbers are useful *debugging* signal (a human staring at "142000/200000" learns something a bare "0.71" doesn't tell them — is this a near-miss on a big window or a routine mid-session reading on a small one?). This design deliberately gives up that observability in exchange for interface size. Not fatal — the reader (the engine) never needed it — but a human debugging a Trip misfire loses a cheap diagnostic.

---

## What this costs elsewhere (honest accounting)

Pushing all normalization into the writer means **every harness adapter must independently know its model's context-window size** (a Claude Code hook needs a model→window table; a Codex equivalent needs its own; a pi extension needs its own) to compute the fraction it emits. That knowledge — "what's Opus's window, what's Haiku's" — now lives in N places instead of once, centrally, in the engine. A widened payload (raw fill + window, unnormalized) would let the engine own that table once and do the division itself, at the cost of a slightly bigger file and a reader that has to do arithmetic instead of just parsing. Minimal-interface trades system-wide knowledge locality for interface tininess — deliberately, per the constraint, but it is a real trade, not a free lunch.

---

## Self-assessment

**DEPTH** — high, by construction. The interface is one float; everything about *how* fill was measured (transcript parsing, token-field summation, the strategic-compact technique from X2, model-window lookup) is fully hidden behind it. A reader cannot even ask what's inside — there's nothing there to ask about. This is close to the ideal of a deep module: enormous functionality (a whole per-harness sensing subsystem) behind a one-line interface. Cost: the "hidden complexity" duplicates itself across adapters (see above) rather than centralizing — deep *per module*, less deep at the *system* level, because there are now three shallow-in-aggregate copies of the model-window fact instead of one deep copy.

**LOCALITY** — excellent on the read side: the engine needs zero context beyond "stat, check age, parse a float" to consume this file — no schema, no cross-referencing a model table against the payload. Worse on the write side in aggregate: the model→window fact is *not* local to one place in the system; it is scattered across every adapter that has to compute a fraction. Net: this design optimizes locality for the reader at the expense of total-system locality.

**SEAM PLACEMENT** — clean and exactly matches the brief's own framing: "the file is the portability seam." A single scalar crossing that seam is about as unambiguous a contract as a seam can carry — no version field to keep in sync across adapters, no schema drift risk between a Claude Code writer and a future pi writer. This is the constraint's strongest showing: minimalism and seam clarity reinforce each other here, they don't trade off.

**TESTABILITY** — the strongest axis under this constraint. The reader's entire test matrix is: valid float in range, missing file, empty file, non-numeric content, value >1.0, value <0.0, fresh mtime, stale mtime, unreadable mtime — nine cases, each expressible as "write this exact string to a temp file, touch its mtime, call the reader, assert the fallback." No JSON schema compatibility matrix, no partial-payload cases, no versioning tests. Falsifiable property from the spec ("does a stale file ever force a handoff?") is trivial to drive directly.

## What the constraint costs, in one line

Depth, locality-for-the-reader, seam clarity, and testability all improve because there is almost nothing left to get wrong in the file itself — but the design silently *assumes* the engine can source model identity elsewhere, and if that assumption doesn't hold, Trip's model-keyed thresholds lose their per-model calibration and the payload has to grow back to include it; the design also trades one centralized fact (model window sizes) for N duplicated copies across harness adapters, and gives up cheap raw-number debuggability for a human reading the file by hand.

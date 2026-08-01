# Gauge — design C: MAX-FLEXIBILITY / EXTENSIBLE-SIGNAL

**Constraint assigned:** a richer, versioned, extensible file record so new harnesses and new signals fit without breaking the read contract — forward/backward-compatible schema.

## 0. What the fixed spec already settles (not mine to redesign)

The file is the seam; a harness-specific writer overwrites it on every tool call; the engine reads it at each gate; the agent never reads it; **missing or stale → "no reading," never advice, never a forced handoff on absent data.** My constraint operates entirely *inside* that envelope — I'm designing the shape of the record and the tolerance rules around it, not the fail-safe posture itself, which is fixed by the spec and would be identical under any of the three candidates.

## 1. The record: a versioned envelope, not a flat blob

```json
{
  "schema_version": 1,
  "fraction": 0.74,
  "window": 200000,
  "model_id": "claude-sonnet-5",
  "source": "claude-code",
  "ts": "2026-07-18T14:32:01Z",
  "confidence": "estimated",
  "raw": {
    "input_tokens": 118000,
    "cache_read_input_tokens": 29000,
    "cache_creation_input_tokens": 1200
  },
  "signals": [],
  "ext": {}
}
```

Two tiers, deliberately unequal in how much stability they promise:

- **Required core (closed, stable):** `schema_version`, `fraction`, `window`, `model_id`, `source`, `ts`. Every reader that understands this `schema_version` MUST be able to parse these six. This is the only part of the contract a future change can *break*.
- **Optional / tolerant tier (open, additive-only):** `confidence`, `raw`, `signals`, `ext`. Absence is never an error — each has a defined neutral default (`confidence` unset → treat as `"estimated"`; `raw`/`signals`/`ext` unset → treat as absent/empty). Presence of *fields the reader has never heard of*, anywhere in the record, is never an error either — unknown keys are silently ignored, not just unknown values within known keys.

Two purpose-built escape hatches carry future growth without touching the required core:
- **`signals`** — an array of named, self-describing objects (`{"name": ..., ...}`) for a second fill estimate, a per-harness correction, a "hard-limit-imminent" flag, etc. A reader that doesn't know a given `name` skips that entry; it doesn't fail the record.
- **`ext`** — a harness-namespaced free-form bag for adapter-local data that isn't ready to be a real field yet (mirrors the "prove it with two adapters before it's a real seam" doctrine already applied to Module 1's ports design). Generic readers never look inside it.

## 2. Versioning rule

- `schema_version` is a plain integer, present on every record, starting at `1`.
- **Additive changes never bump it.** Adding an optional field, a new `signals` name, or a new `ext` key is forward-compatible by construction and ships without touching `schema_version`.
- **A bump is reserved for a genuine breaking change** — a required-core field renamed, retyped, or removed. The engine carries a `MAX_SUPPORTED_VERSION` constant; a record whose `schema_version` exceeds it is treated exactly like a missing file (see §4) — the engine doesn't try to guess at an unknown shape, it just declines to read.
- A record with **no** `schema_version` field at all is itself invalid (fail-safe collapse, §4) — extensibility must not become looseness about the one field every version needs to agree on.

## 3. Staleness rule

- Canonical clock is the record's own `ts` (not file mtime) — the writer stamps the moment it observed the fill, which stays meaningful even if the file is copied, synced, or read from a mounted volume with a different clock skew than mtime would reflect.
- `now - ts > staleness_threshold` → stale → same outcome as missing (§4). `staleness_threshold` is engine-config, not schema (a knob the operator tunes, not a per-record field) — defaulted conservatively (e.g. a small multiple of expected tool-call cadence) and out of scope for this design to pin a number, per the spec's own "tuning is a follow-up" stance.
- The file is a **snapshot, replaced wholesale on every write** — not an append-only trail. That's a deliberate difference from `why_trail`: the gauge only ever needs "the most recent reading," so there is nothing to accumulate. Write is atomic (write-temp, rename) so the reader never observes a half-written JSON body mid-write — worth naming explicitly since this file is rewritten by an external process on every tool call, unlike the checklist JSON, which is only touched inside the engine's own lease-guarded critical sections.

## 4. Fail-safe collapse

However many distinct things can go wrong, they collapse to **one** observable outcome — this is the property the whole design exists to protect, and it must survive the extensibility this candidate adds, not be diluted by it:

| Cause | Outcome |
|---|---|
| file absent | no reading |
| malformed JSON | no reading |
| `schema_version` missing | no reading |
| `schema_version` > `MAX_SUPPORTED_VERSION` | no reading |
| a required-core field missing or wrong-typed for this version | no reading |
| `ts` older than staleness threshold | no reading |

All six reduce to the identical engine behavior: no advice, never a forced handoff. The optional tier (`confidence`/`raw`/`signals`/`ext`) can never *cause* a "no reading" outcome by being malformed in a way the reader doesn't understand — an unrecognized `signals` entry or an `ext` bag with unexpected shape is skipped, not fatal. This asymmetry (required core is strict, optional tier is permissive) is the actual mechanism that makes "extensible" mean something rather than being a label.

## 5. How the named future cases actually fit

- **A second fill estimate** (different formula/source) → a new `signals` entry, e.g. `{"name": "secondary-fraction", "fraction": 0.81, "source": "..."}`. Trip v1 ignores it. A later Trip version can opt into reading it by name, with no `schema_version` bump, because the required core hasn't changed.
- **A per-harness correction factor** → starts in `ext.<harness>.correction_factor`, namespaced and ignored by any generic reader. It only graduates to a top-level field once a second harness independently wants the same correction — same "two adapters make it real" bar already used for Module 1's ports decision, applied here to fields instead of interfaces.
- **A "hard-limit-imminent" flag** → a `signals` entry (`{"name": "hard-limit-imminent", "value": true}`). Trip's hard band could read it as an early-trigger override later without touching the required core or the version number.

## 6. Deep-module description

**Invariants:** freshest-write-wins (spec-given); write is atomic; the record is always a full snapshot, never a delta; `schema_version` is present on every valid record; unknown top-level keys are always tolerated; known-optional fields absent are always treated as their defined neutral default, never as an error; required-core fields missing/malformed always collapse to "no reading"; the reader never writes to the file; the agent never reads the file directly (unchanged from the fixed spec).

**Ordering:** single-writer-per-session assumption — no concurrent writers to one file. **Open scoping question I'm flagging, not resolving:** the spec says "a well-known local file," singular, per the fixed design. If two agents run in parallel against the same repo (a Commander and a sibling Commander, say), do they get distinct gauge-file paths (session-scoped) or share one? Nothing in the fixed spec or X2/X3 pins this down, and it's outside what my constraint is meant to resolve — but it's a real gap in "the file" as currently specified, worth surfacing to whoever finalizes the interface, independent of which candidate wins.

**Error modes:** table in §4, plus: a `signals` array entry whose shape the reader doesn't recognize is skipped (not fatal); an `ext` value of unexpected type is never dereferenced by a generic reader, so it can't throw.

**Config:** `MAX_SUPPORTED_VERSION` (engine constant, bumped only when the engine ships code that understands a new breaking version — deliberately *not* built out as a multi-version table yet, see §7); `staleness_threshold` (operator-tunable, unrelated to my constraint, needed by any candidate).

## 7. Honest YAGNI assessment

The assignment asks directly whether this is justified for an experimental v1 ("try stuff and see what happens"), or speculative. Splitting the answer in two, because the two halves of "extensibility" have very different costs:

**Cheap and justified now:**
- Tolerating unknown top-level keys costs nothing — any sane JSON reader should already do this regardless of whether it's framed as "versioning."
- Reserving `schema_version: 1` on every record costs nothing to write and gives a future migration a discriminator to key off, if one is ever needed.
- Defining (but leaving empty) `signals`/`ext` costs nothing at write-time and nothing at read-time in v1, because nothing reads them yet.
- This tier is earned by the module's actual shape, not invented: Gauge is the one module in the spec with **real** adapter plurality — three named harnesses in X3 (Claude Code, Codex, pi), unlike Module 1's why-store, which the ports-and-adapters candidate itself conceded had only one real adapter and one hypothetical. Some tolerance for harness-shaped variation is not speculative here.

**Expensive and NOT justified yet:**
- A real multi-version required-field validator table (`if schema_version == 1: require [...]; elif == 2: require [...]`) has no consumer — nothing in the current spec proposes a v2. Building it now is designing for a breaking change that hasn't been requested, against a module whose own posture is explicitly "ship the minimal version, learn from use."
- `confidence` is defined but **unused** — Trip v1 (per DESIGN_SPEC §3) only reads `fraction` against a model-keyed threshold. A confidence-weighted threshold is a plausible future idea, not a current one; shipping the field costs nothing, but I want to be honest that it's dead weight until Trip actually branches on it.
- `raw` (the token breakdown) is likewise unconsumed by anything in the current design — it's diagnostic/debugging value only (useful if a human is later trying to figure out why an estimate looked wrong), not load-bearing for the engine's read contract.

**Verdict:** ship the tolerant envelope (versioned, unknown-keys-ignored, `signals`/`ext` present-but-empty) because it's nearly free and matches the module's genuine multi-harness reality — but explicitly **defer** the expensive machinery (the multi-version validator table, any actual second schema version) until a second version is actually proposed by real use. Reserve the field, don't build the machine.

## 8. Self-assessment

**DEPTH.** Moderate, and I want to be precise about where the depth actually comes from. The record hides a real cluster of ways a foreign-process-written file can be wrong (malformed, partial write, unknown version, missing field, stale clock) behind one binary "readable or not" surface — that's genuine depth, but it's a property the *fixed spec* already demands of any candidate (the "missing or stale = no reading" invariant is given, not something my constraint invented). What my constraint specifically adds is narrower: the *shape* of what's inside a valid record, and the rule that optional-tier malformation can never escalate into a "no reading" outcome the way required-core malformation does. That's real, but smaller than "depth" might suggest at a glance — I'd rather undersell it than claim the whole fail-safe collapse as this candidate's achievement.

**LOCALITY.** Mixed, with an honest crack. The *read side* can be one deep module (a single validator + tolerant-parse function the engine imports) — good locality. The *write side* cannot be, structurally: the three adapters (a Claude Code hook script, a Codex equivalent, a pi extension) are independently-authored, plausibly in different languages/runtimes, held together only by the documented JSON contract, not by shared code. This is the same honesty flag dit-why-C raised for its own port ("prompt-upheld, not engine-enforceable") — extensibility here is a *documented convention* on the write side, enforced only on the read side.

**SEAM PLACEMENT.** This is where the constraint earns its keep most clearly. I place the seam for future evolution *inside* the record itself: a closed, stable required core vs. two open escape hatches (`signals`, `ext`) that future work grows into instead of touching the core. Compare to a minimal-record candidate, which by construction has no such hatch — any future addition to a bare `{fraction, window}` record is a breaking change to *the whole contract* by default, whereas here most plausible future additions (a second estimate, a harness correction, an imminent-limit flag) never need to touch the part every reader must agree on.

**TESTABILITY.** More surface than a minimal record, and I don't think that's avoidable — every extra tolerance is itself a thing that needs a test proving it's truly inert, not just a thing that needs to exist. Falsifiable tests this candidate specifically adds, beyond the spec's own list: unknown top-level keys don't break parsing; `schema_version` beyond `MAX_SUPPORTED_VERSION` collapses to the *identical* "no reading" outcome as a missing file (not a different, half-handled outcome); a populated `signals`/`ext` doesn't change v1 Trip behavior at all (tests that opt-in fields are genuinely inert until a reader opts in); required-core-missing, malformed-JSON, and stale-ts all produce the same observable behavior (the collapse, directly from the spec's own falsifiable question).

## What the constraint costs

- **Write-side burden with no shared enforcement** — three independently-authored adapters must each honor a documented contract with no compiler/type-checker holding them to it (a real locality crack, not a hypothetical one).
- **More test surface to prove the negative** — "extra stuff is truly ignored" is its own testing obligation that a minimal record simply doesn't have.
- **Real speculative-generality risk on two named fields** (`confidence`, `raw`) — defined now, consumed by nothing in the current spec. I've recommended shipping them as free/inert rather than cutting them, but flagging honestly that they're currently ballast.
- **A soft governance risk**, not a technical one: once `ext` exists as an escape hatch, there's a temptation to leave harness-specific data there indefinitely rather than proposing it as a real field, which could slow convergence on what the stable core should contain. Worth a lightweight norm ("promote `ext.foo` once ≥2 harnesses want it," mirroring the two-adapter bar already used elsewhere in this spec) rather than a technical fix.

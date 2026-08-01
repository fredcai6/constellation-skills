# Gauge — design B: PORTS-AND-ADAPTERS

**Constraint assigned:** a formal `GaugeReader` port the engine/Trip depends on; the local-file reader as one adapter; an explicit absent/no-op adapter for harnesses without a hook; so a Codex or pi adapter slots in without touching engine policy.

## 0. What crosses the seam, and what doesn't — the read/write split the task's framing blurs

The fixed spec says: "a harness-specific hook/extension writes... to a well-known local file... **The file is the seam.** The engine reads it; the *writer* is a swappable per-harness adapter." Read literally, that sentence already answers where the seam is — at the **file format**, not at a Python interface. The task then asks for a `GaugeReader` **port** on top of that. Before designing it, one thing has to be sorted onto the right side of the boundary or the port ends up double-counting a seam that already exists:

- The **engine-facing port** (`GaugeReader`) is a **read-only** dependency. Its adapters are things that produce a `Reading | None` *inside the engine's own process*, from *some* source.
- The **per-harness writers** (Claude Code hook, Codex equivalent, pi extension) are **outside the port entirely**. They don't implement `GaugeReader` — they're independent, out-of-process, possibly-different-language producers of one shared file format. The port never sees "which harness wrote this."

This matters for the plurality question the task asks me to confirm or challenge (§5) — the "3 named harnesses" live on the **write** side, and the file format being harness-agnostic is *precisely what keeps them off the read side*. A `GaugeReader` adapter that branched on `source == "codex"` would be a seam violation, not a feature — the whole point of "the file is the seam" is that the reader never needs to know.

## 1. The port: `GaugeReader`

One method. No solicit, no write, no staleness query — staleness is resolved *before* a `Reading` is constructed, never after (see §3).

```python
# gauge_reader.py — the PORT. No import of checklist_engine; no hook/harness
# knowledge; no JSON-file knowledge beyond the Reading value shape.

@dataclass(frozen=True)
class Reading:
    fill_fraction: float    # 0.0-1.0, current context-fill estimate
    window: int              # context-window token capacity in effect this session
    model: str | None        # model id, for Trip's model-keyed threshold lookup
    source: str               # harness id ("claude-code" | "codex" | "pi" | ...) -- diagnostic only, Trip MUST NOT branch on it
    observed_at: str          # ISO-8601 UTC timestamp of the sampled tool call (not write time)

class GaugeReader(Protocol):
    def read(self) -> Reading | None:
        """Return the freshest usable reading, or None. MUST NOT raise -- every
        failure mode (absent file, corrupt file, malformed record, stale
        reading, filesystem race) collapses to None inside the adapter. A
        `Reading` that reaches the caller is, by construction, fresh and
        well-formed; Trip never re-checks either property, and cannot express
        "force on stale data" because stale data never becomes a Reading."""
```

**Why no exception type**, unlike the sibling why-port (`WhyStorePort.record()` raises `WhyRequiredError`/`IncompleteWhyError` and the adapter translates them into the engine's refusal idiom). There, failure-to-answer is a *policy violation* the engine must refuse on. Here, "nothing to read" is not an error state at all — it is the fail-safe path the whole module exists to guarantee. Giving `GaugeReader` an exception type would hand Trip something to catch and would tempt a future adapter to raise on a corrupt file instead of returning `None`, reintroducing exactly the "does a bad reading ever force a handoff" risk the spec's invariant forbids. One return type, one caller-side check (`reading is not None`), zero exception vocabulary.

## 2. The adapters (read side — this is the actual `GaugeReader` adapter set)

### 2a. `FileGaugeReader` — the only content-bearing adapter

```python
class FileGaugeReader:
    """GaugeReader backed by the well-known per-run gauge file. Reads whatever
    ANY harness's writer produced, without knowing or caring which harness
    wrote it -- this is where "the file is the seam" actually pays off."""

    def __init__(self, path: Path, max_age_s: float = 120.0):
        self._path = path
        self._max_age_s = max_age_s   # engine/session config, not a harness fact

    def read(self) -> Reading | None:
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if not isinstance(raw, dict):
                return None
            fill, window = raw.get("fill_fraction"), raw.get("window")
            observed_at = raw.get("observed_at")
            if not (isinstance(fill, (int, float)) and 0.0 <= fill <= 1.0):
                return None
            if not (isinstance(window, int) and window > 0):
                return None
            if observed_at is None:
                return None
            age_s = (_utcnow() - _parse_iso(observed_at)).total_seconds()
            if age_s > self._max_age_s or age_s < 0:
                return None   # stale, or a clock skew we don't trust -- either way, no Reading
            return Reading(
                fill_fraction=float(fill), window=window,
                model=raw.get("model"), source=raw.get("source", "unknown"),
                observed_at=observed_at,
            )
        except Exception:
            return None
```

A malformed record (missing/wrong-typed field) is treated **identically** to a corrupt or absent file — `None`, not a partial `Reading` with `fill_fraction=None`. There is exactly one "nothing to act on" value in this design, not a family of near-misses Trip would have to special-case.

### 2b. `NoOpGaugeReader` — the explicit absent adapter

```python
class NoOpGaugeReader:
    """The zero-adapter: no writer is wired for this harness/run (or gauge
    reading is deliberately disabled, e.g. a headless eval). Always None --
    behaviorally identical to FileGaugeReader against an absent path."""
    def read(self) -> Reading | None:
        return None
```

Behaviorally this is redundant with `FileGaugeReader` pointed at a path that doesn't exist yet — both return `None` forever. It earns its place anyway as a **configuration-time fact**, not a runtime behavior: wiring `NoOpGaugeReader` explicitly into a harness's engine config is a documented statement "we know this harness has no writer" (unsupported harness, or gauge intentionally off for a CI eval run), distinguishable in logs/config from "a `FileGaugeReader` is wired and *should* be seeing writes but isn't" (broken hook, race at session start, wrong path). Same fail-safe output, different diagnosability when a human is later asking "why did this run never get a soft-band nudge." That's the whole justification — it is a small module, and I'm not overselling it as more.

### 2c. `FakeGaugeReader` — the testability adapter, not named in the task but implied by it

```python
class FakeGaugeReader:
    """Test double: returns a preconfigured Reading|None. No I/O, no clock."""
    def __init__(self, reading: Reading | None = None):
        self._reading = reading
    def read(self) -> Reading | None:
        return self._reading
```

This is the adapter that actually earns the Protocol's keep in the near term (see §5) — it lets every Trip band test (soft fires at/above threshold and never below; hard refuses at/above and never lets a pass below) run with zero filesystem, zero timing, zero staleness fixtures.

## 3. Trip's call site — the invariant is structural, not a discipline

```python
def trip_band(gauge: GaugeReader, model_thresholds: dict) -> str:
    reading = gauge.read()
    if reading is None:
        return "none"           # no advice, never forces -- the entire fail-safe
                                  # invariant is this one branch
    soft, hard = model_thresholds.get(reading.model, model_thresholds["default"])
    if reading.fill_fraction >= hard:
        return "hard"
    if reading.fill_fraction >= soft:
        return "soft"
    return "none"
```

Trip contains no try/except, no staleness math, no "is this file trustworthy" logic — every one of those questions was already resolved (or collapsed to `None`) inside whichever adapter produced the `Reading`. **Freshness/staleness judgment therefore lives in the adapter, not the port** — specifically in `FileGaugeReader`, the only adapter for which "age" is even a meaningful concept (`NoOpGaugeReader` has nothing to be stale; `FakeGaugeReader` has nothing to be stale by test construction). The port's *contract* is what forces this placement: because `Reading` carries no "trust me, check `observed_at` yourself" escape hatch and the Protocol's docstring says a returned `Reading` is fresh by construction, there is no legal way for a second adapter to skip the freshness check and still satisfy the port — unlike a bare function contract, where a careless second implementation of `read_gauge()` could simply forget to check age.

## 4. The writer contract — outside the port, stated as prose discipline, not enforced by a type

Every per-harness writer (Claude Code `PostToolUse` hook parsing `transcript_path`, per the `strategic-compact` technique in X2; a Codex equivalent; a pi extension) must guarantee, to keep `FileGaugeReader` correct regardless of which harness produced the file:

1. **Atomic write** — tmp file + `os.replace`/rename, matching this repo's existing `_save_json_map` convention in `spine_rail.py`. No reader ever observes a torn/partial JSON write. This is what makes "freshest-write-wins" (a spec invariant) true without any locking.
2. **Schema conformance** — `fill_fraction` (float, 0.0–1.0), `window` (positive int), `observed_at` (ISO-8601 UTC, the *sampled* moment, not wall-clock-at-write), `model` (string), `source` (the writer's own harness id, informational only). A record missing a required field is worse than not writing — `FileGaugeReader` cannot distinguish "the writer is buggy" from "the writer is a newer/older version with a different schema," so both collapse to `None` per §2a; the writer's job is to never emit that record in the first place.
3. **Skip on uncertainty, never fabricate** — if a writer cannot compute a real estimate this tool call (missing `transcript_path`, a parse failure, an unsupported model), it must **not** write a placeholder/zero/error record. It leaves the existing file alone and lets it age into staleness naturally. A fabricated `0.0` would read to `FileGaugeReader` as genuine low fill and could suppress a nudge that should have fired.
4. **Non-blocking, fail-open** — wrapped, best-effort, never delays or fails the tool call it's attached to. Same posture `spine_rail.py`'s `PostToolUse` handler already takes for the (unrelated) spine-binding write.
5. **Session-scoped path** — write to `.agent-work/<work_id>/gauge.json`, sibling to that run's `spine.json`/`spine.json.journal`, not one global path — otherwise concurrent sessions/worktrees corrupt each other's readings. This reuses the session→spine correlation `spine_rail.py`'s `PostToolUse` handler already establishes (`binding[sid] = {"spine": ..., ...}`) rather than inventing a second binding mechanism; a gauge-writing hook can extend the same binding record with a `"gauge"` path instead of introducing new machinery.

**Nothing in this list is type-checked or Protocol-enforced.** This is the one place the "ports-and-adapters" pattern's usual guarantee doesn't reach: a Protocol disciplines same-process, same-language callers of a port. It cannot reach across a process boundary into three independently-implemented, possibly different-language producers (a Python/shell hook, a Codex extension, a TypeScript pi extension). The five guarantees above are enforced the way any external-file contract is — by `FileGaugeReader`'s defensive parsing (§2a, everything malformed → `None`) plus a schema-conformance test fixture per writer, not by a compiler or a Protocol. Worth being honest about: this is a **documented contract**, not a **structural** one, and that gap is inherent to the constraint, not a shortcut I took.

## 5. Honest seam assessment — confirm or challenge the task's "genuine plurality" premise

**Challenge, with a specific correction.** The task states this interface "has GENUINE adapter plurality (3 named harnesses), unlike the sibling why-capture interface." That's true of the **write** side and not proven of the **read** side — and the `GaugeReader` port the task actually asks me to design is the read side.

- **On the read side (the actual port):** exactly **two** production adapters exist, `FileGaugeReader` and `NoOpGaugeReader`, and that count is **structurally independent of how many harnesses exist** — three harnesses or thirty, `FileGaugeReader` still reads one file format and doesn't grow a method. So a `GaugeReader` Protocol doesn't "earn" harness plurality the way `WhyStorePort` was asked to earn storage-backend plurality — the harness plurality was already earned by the *file format* being harness-agnostic, a decision made in the fixed spec before this panel started, not by anything the port adds. What the port *does* add on top of that: `NoOpGaugeReader` as a distinguishable configuration state (§2b) and `FakeGaugeReader` for filesystem-free Trip tests (§2c) — real, but a narrower earn than "3 adapters" implies.
- **On the write side (where 3-harness plurality would actually have to show up):** checked against X2/X3, only **one of three is confirmed buildable today**. Claude Code has a working, concrete technique in hand (X2: `strategic-compact`'s `transcript_path`-parsing, token-summing hook — this is what ships first, directly). Codex: X3's excursion confirms subagent delegation and Responses-API compaction (`context_management`/`/responses/compact`), but **never confirms a per-tool-call hook point analogous to `PostToolUse` that a writer could attach to at all** — that's a real gap in the source material, not a solved problem waved through. pi: X3 confirms a general extension API (`AgentHarness`, `ctx.newSession`, tool-level `terminate`) capable enough that a per-tool-call writer is *plausible*, but no source confirms pi extensions fire on every tool call the way Claude Code's `PostToolUse` does — also unconfirmed for this specific purpose.

**Net verdict:** the "one-adapter risk" the task asked me to assess honestly is real, just **relocated**. It isn't a risk on the `GaugeReader` port (which was never going to have 3 adapters, and shouldn't). It's a risk on the writer contract in §4, where — as of the excursion material this design is built on — Claude Code is the only writer confirmed buildable now, and Codex/pi are architecturally plausible but each has a specific, named, unconfirmed gap (a hook point for Codex; per-tool-call cadence for pi). Ship-first-adapter-only is the honest expectation, same as the why-capture module, just for a different reason (write-side hook availability, not read-side backend need).

## 6. Deep-module description

**Invariants:**
- A `Reading` that reaches Trip is fresh and well-formed by construction; no caller re-validates either property (§3).
- `GaugeReader.read()` never raises, for any adapter, under any failure (§1). This is the load-bearing invariant of the whole module — the spec's "missing or stale file = no reading, never forces" collapses entirely into "does `read()` ever return something other than `None` or a valid `Reading`," which is a property of three small, individually-testable adapters, not of Trip's call sites.
- `source` is diagnostic-only; nothing in `GaugeReader`, `Reading`, or Trip's threshold lookup branches on it. Model-keyed thresholds key on `model`, never `source` — this is what keeps Trip harness-agnostic in fact, not just in name.
- The file writer never emits a partial/fabricated record (§4.3) — the file's mere presence with a given `observed_at` is meaningful; there is no "record present but I don't trust it" state for `FileGaugeReader` to reason about beyond schema/age.

**Ordering:** `FileGaugeReader.read()` is called once per gate evaluation (Trip fires at each gate, per the spec); no read-modify-write, no lease — this port is pure read, so none of `checklist_engine.py`'s `engine_session` lease/claim machinery applies or is needed here. Writer-side ordering is "freshest atomic write wins," guaranteed by tmp+replace (§4.1), independent of read timing.

**Error modes:**

| condition | `FileGaugeReader` | `NoOpGaugeReader` |
|---|---|---|
| file absent | `None` | `None` (always) |
| valid JSON, well-formed, within `max_age_s` | `Reading(...)` | n/a |
| corrupt/unparseable JSON | `None` | n/a |
| well-formed but `observed_at` older than `max_age_s` | `None` | n/a |
| missing/wrong-typed required field | `None` | n/a |
| filesystem error (permission, race mid-replace) | `None` (caught) | n/a |
| clock skew (`observed_at` in the future) | `None` | n/a |

No row raises. This table is also, directly, the falsifiable test list the spec's "Testing pathways" section asks for ("does a stale file ever force a handoff? must not") — each row is one `FileGaugeReader` unit test against a fixture file, no engine or Trip involved.

**Config:** `max_age_s` (staleness threshold) and the gauge file path are the only two knobs, both engine/session-level, neither harness-specific — consistent with `source` being diagnostic-only. Model-keyed SOFT/HARD threshold *values* are Trip's config, not the port's (Trip owns policy; the port owns fact-delivery) — named here only to be explicit that `GaugeReader` carries zero policy config, matching the spec's "engine supplies the fill fact, agent/Trip supplies judgment" split.

## 7. Self-assessment

**DEPTH.** The strongest of the three DESIGN_SPEC interfaces on this axis, and I'd say stronger than the why-port too. One method, `read() -> Reading | None`, hides file I/O, JSON parsing, schema validation, staleness computation, and corruption handling entirely — and the caller-side policy for "did we get usable data" is a single `is not None` check that cannot be gotten wrong, because there is nothing left to get wrong once a `Reading` exists. Ousterhout's "small interface, big implementation hidden behind it" bar is genuinely met here, more so than for `WhyStorePort` (which I'd graded there as "small interface over a small implementation").

**LOCALITY.** Good if `gauge_reader.py` stays a standalone module importing nothing from `checklist_engine.py` or `spine_rail.py` — same discipline as the why-port design insists on for `why_store.py`. The concrete risk here is sharper than for why-capture, though: the *writer* half of this feature (§4) will live inside `spine_rail.py`-style hook scripts, which is a natural place for an implementer to also drop the *reader* "for convenience," collapsing the read/write boundary this design spends §0 establishing. Worth flagging loudly to whoever implements: `FileGaugeReader` belongs with the engine/Trip; the writer hook belongs with the harness's hook suite; they must not become the same file just because they agree on a schema.

**SEAM PLACEMENT.** This is where I differ most from a naive reading of the task. The earned seam is not "3 harnesses = 3 adapters" — it's the read/write split in §0, which makes the file format (not a Python interface) the actual portability seam, exactly as the fixed spec already said before any panel started. The `GaugeReader` Protocol's real contribution is narrower and more defensible: it forces staleness resolution to happen exactly once, at adapter-construction boundary, so it structurally cannot leak into Trip (§3) — that is a correct and non-trivial seam decision, just a different one than "one adapter per harness."

**TESTABILITY.** Clear win, closest to the spec's own falsifiable tests of any module in this design-it-twice set: the "stale file never forces" test is a `FileGaugeReader` fixture test (§6's error-mode table, no engine); the "soft never forces, hard never passes" tests are pure `Trip` tests against `FakeGaugeReader` (§2c, no filesystem, no clock). No other module's testing pathway in the DESIGN_SPEC maps this directly onto its own interface.

**Net cost of the constraint.** Two honest costs, not one:
1. **A `Protocol` + 3 adapter classes for one method** is real overhead against "just write a bare `read_gauge(path, max_age_s) -> Reading | None` function and call it a day" — the alternative would lose exactly the `NoOpGaugeReader`-as-documented-config-state distinction (§2b) and would make `FakeGaugeReader`-style test injection slightly more awkward (monkeypatching a function vs. passing an object), but wouldn't lose any *runtime* behavior. I think the cost is worth it for the config-diagnosability and test-injection wins, but — same as the why-port's self-assessment — that's a "worth it for locality/testability," not "worth it because we're about to swap production backends."
2. **The pattern's guarantee stops at the process boundary.** Ports-and-adapters normally lets a type system (or at minimum a shared runtime) hold every adapter to the same contract. Here, three of the contract's five clauses (§4) govern code that will never be imported alongside `GaugeReader` — a Codex extension and a pi extension will likely never even see this Python Protocol. What the constraint actually buys is discipline on the **one process that matters most for correctness** (the engine's read side, where a bug means a false force or false silence) while leaving the **write side's cross-language conformance** to documentation and per-writer test fixtures — an honest, load-bearing limitation of applying this pattern to a genuinely multi-runtime system, not a gap I could have designed away under this constraint.

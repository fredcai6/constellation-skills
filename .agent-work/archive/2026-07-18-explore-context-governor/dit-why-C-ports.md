# Why-capture — design C: PORTS-AND-ADAPTERS

**Constraint assigned:** define a clean seam between the why-capture CONTRACT and the engine internals — treat the why-store as a port with a well-defined interface, and the checklist engine as one adapter of it, so a different backend could satisfy the same contract later.

## 0. What crosses the seam, and what doesn't

Before the interface: two things the fixed spec hands me must be sorted onto the right side of the boundary, or the port ends up leaking checklist-schema concerns.

- **`why_exempt`** is a *task/template-authoring* fact (set when a gate is authored, lives in the checklist JSON's `Task` object next to `postconditions`/`constraints`). It never crosses the port boundary. The port has no concept of "exempt" — it only ever sees calls for transitions someone decided to ask about. Exemption is entirely the **adapter's** filtering decision, made from data the port doesn't need to understand.
- **The prompt text** ("you've used most of your context…", or whatever imperative string solicits the why) is presentation, owned by the adapter's CLI surface (mirrors how `_rail()` builds doctrine strings at the dispatch boundary today, not inside the pure verb functions). The port never renders a prompt; it only records what came back.

This is the main payoff of the ports-and-adapters framing here: it forces "is this a why-store concern or a checklist-schema concern" to be answered for every field, instead of bolting three new columns onto the Task object and calling it done.

## 1. The port: `WhyStorePort`

A minimal write op, two read ops. Deliberately not four+ methods — one choke point for the write side keeps the "mandatory prompt, optional content" invariant enforceable in exactly one place regardless of who calls it.

```python
# why_store.py — the PORT. No import of checklist_engine; no JSON-file knowledge.

@dataclass(frozen=True)
class WhyRef:
    scope: str   # the owning plan's stable identity (checklist work_id)
    gate: str    # task/gate id within that plan

@dataclass(frozen=True)
class ContentAnswer:
    why_done: str
    now_understand: str
    next: str

class MechanicalDecline:
    """Sentinel: an explicit 'nothing new to report' answer. First-class, not a
    magic string stuffed into the three text fields — see §2 for why."""

@dataclass(frozen=True)
class WhyRecord:
    ref: WhyRef
    transition: str                 # "advance" | "attach"
    kind: str                       # "content" | "mechanical"
    why_done: str | None
    now_understand: str | None
    next: str | None
    seq: int
    ts: str

class WhyRequiredError(Exception):
    """record() called with answer=None — the mandatory-prompt invariant."""

class IncompleteWhyError(Exception):
    """record() called with a ContentAnswer carrying a blank/whitespace field."""

class WhyStorePort(Protocol):
    def record(
        self, ref: WhyRef, transition: str,
        answer: ContentAnswer | MechanicalDecline | None,
    ) -> WhyRecord:
        """Persist one why-record for this transition. `answer=None` means
        "nothing was supplied" and MUST raise WhyRequiredError — the port, not
        the caller, is the sole judge of whether silence is acceptable, so a
        second adapter cannot forget to enforce it."""

    def digest(self, scope: str) -> str | None:
        """The live 'current understanding': the most recent `now_understand`
        recorded anywhere in `scope`, skipping mechanical declines (they carry
        no content to surface). None if nothing content-bearing has been
        recorded yet — an honest 'no digest yet', not an empty string."""

    def trail(self, scope: str, gate: str | None = None) -> list[WhyRecord]:
        """Append-only history in recorded order, optionally filtered to one
        gate. Never raises on an unknown scope/gate — returns []."""
```

Four named capabilities were asked for: *solicit*, *record*, *mark mechanical*, *query the digest*, *enumerate the trail*. Mapped onto three methods deliberately:

- **solicit** isn't a port operation at all — it's the adapter deciding to ask (see §0). The port has nothing to solicit; it only receives.
- **record** and **mark mechanical** are the same operation with a tagged argument (`ContentAnswer` vs `MechanicalDecline`), not two methods. I considered a separate `decline_mechanical(ref, transition)` method for call-site self-documentation, and it's a legitimate alternative — but a single write entry point means the "was an answer supplied at all" check exists in exactly one place in the port's implementation, which is the property the ports-and-adapters constraint is buying here. Two write methods would mean two places a future adapter could get the `None`-check wrong.
- **query the digest** / **enumerate the trail** are `digest()` / `trail()`, unchanged from the ask.

## 2. Why a tagged answer, not a magic string

The fixed spec says "an explicit `mechanical` answer is first-class and valid." The cheap version of that is: let the agent literally type the word `mechanical` into `why_done`. I rejected it — a real answer that happens to start describing something as "mechanical" (e.g. `why_done: "mechanical refactor, no design decision"`) would collide with the sentinel, and the port would have no way to tell "this is a genuine 3-word answer" from "this is the decline marker." A tagged union (`ContentAnswer` | `MechanicalDecline`) can't collide — the CLI layer decides which one to construct from the presence of `--why-mechanical` vs `--why-done/--now-understand/--next`, and the port never has to parse content to guess intent.

## 3. The adapter: the checklist engine

`checklist_engine.py` is **one adapter** implementing `WhyStorePort` against the checklist's own JSON file — no new infrastructure, no network call, same persistence story as `evidence`/`amendments` today.

```python
# inside checklist_engine.py (or a small why_store_json.py it imports)

class ChecklistWhyStore:
    """WhyStorePort backed by cl["why_trail"], an append-only list living
    alongside evidence/amendments in the same checklist JSON file."""

    def __init__(self, cl: dict):
        self._cl = cl

    def record(self, ref, transition, answer):
        if answer is None:
            raise WhyRequiredError(
                f"{ref.gate}: {transition} is not why_exempt; supply "
                f"--why-done/--now-understand/--next or --why-mechanical"
            )
        if isinstance(answer, ContentAnswer):
            blanks = [f for f in ("why_done", "now_understand", "next")
                      if not getattr(answer, f).strip()]
            if blanks:
                raise IncompleteWhyError(f"{ref.gate}: why fields {blanks} cannot be blank")
            kind, wd, nu, nx = "content", answer.why_done, answer.now_understand, answer.next
        else:  # MechanicalDecline
            kind, wd, nu, nx = "mechanical", None, None, None
        trail = self._cl.setdefault("why_trail", [])
        rec = {"scope": ref.scope, "gate": ref.gate, "transition": transition,
               "kind": kind, "why_done": wd, "now_understand": nu, "next": nx,
               "seq": len(trail) + 1, "ts": _now()}
        trail.append(rec)
        return WhyRecord(ref=ref, transition=transition, kind=kind,
                          why_done=wd, now_understand=nu, next=nx,
                          seq=rec["seq"], ts=rec["ts"])

    def digest(self, scope):
        for rec in reversed(self._cl.get("why_trail", [])):
            if rec["scope"] == scope and rec["kind"] == "content":
                return rec["now_understand"]
        return None

    def trail(self, scope, gate=None):
        return [r for r in self._cl.get("why_trail", [])
                if r["scope"] == scope and (gate is None or r["gate"] == gate)]
```

**Where the adapter calls the port.** Inside `advance()`, after the existing postcondition check and before the status flip to `complete` (mirrors the existing "checks first, mutate state only once every check has passed" shape the function already has):

```python
def advance(cl, iid, why=None, from_child=None, base_dir=None):
    ... existing status / from_child / postcondition checks unchanged ...
    if not t.get("why_exempt", False):
        why_store.record(WhyRef(cl["work_id"], iid), "advance", why)
    t["status"] = "complete"
    ...
```

`why` is built by the CLI layer from `--why-done/--now-understand/--next` (→ `ContentAnswer`) or `--why-mechanical` (→ `MechanicalDecline`) or nothing (→ `None`). `dispatch()`/`_run_verb()` do this construction — the same layer that already builds `build_payload()` for `attach` — so `advance()`'s own signature stays a plain function taking an already-resolved answer, testable without touching argparse.

**Open scoping question I'm flagging, not resolving.** The fixed spec names `advance`/`attach` as the two transitions that solicit why. In the engine as it exists today, `attach()` (the Python helper) is called from many places that are *not* an agent-facing checkpoint: `advance --from-child` auto-attaches the child's consolidation, `_check_condition` auto-attaches `command-output`/`artifact-policy` evidence, `waive` auto-attaches a `waiver` record. None of those should prompt for a why — they're bookkeeping, not a gate transition an agent chose to walk through. My working assumption: why-capture hooks the **CLI `attach` subcommand specifically** (the `dispatch()`/`_run_verb()` boundary, verb == `"attach"`), not the internal helper function of the same name — mirroring how `RAIL_VERBS` already distinguishes "verbs that get doctrine text" from ordinary Python calls. Even narrowed that far, plenty of legitimate CLI `attach` calls remain (attaching a `user-decision`, a waiver's audit note) that arguably aren't "gate transitions" in the sense the governor cares about. I did not invent a further sub-classification (e.g. an `attach --milestone` flag) because that's schema-authoring judgment belonging to whoever owns the next DESIGN_SPEC pass, not something the ports-and-adapters constraint resolves by itself — but it's a real gap and I'd rather name it than paper over it.

**Enforcement placement.** The invariant — *a non-exempt transition without an answer is refused* — lives **inside the port** (`WhyRequiredError` raised by `record()`), not in the adapter. The adapter's only job is the exemption filter (call or don't call) and translating the port's exception into the engine's existing refusal idiom:

```python
except WhyRequiredError as exc:
    raise EngineError(str(exc)) from exc
```

This keeps `EngineError` — the engine's own refusal vocabulary, already wired into `main()`'s `REFUSED:` / rail-append path — decoupled from the port's exception types. A hypothetical second adapter (a different engine) would translate `WhyRequiredError` into *its own* refusal idiom, not the checklist engine's; the invariant itself travels with the port either way. I considered putting the check in the adapter instead (cheaper, no port round-trip for the "totally silent" case) and rejected it: if enforcement lived in the adapter, a second adapter would have to remember to reimplement the identical `None`-check, which is exactly the risk a "contract lives on the port" seam exists to remove.

## 4. Deep-module description

**Invariants** (hold regardless of adapter):
- Every `record()` call for a non-exempt transition carries a real `ContentAnswer` (all three fields non-blank) or an explicit `MechanicalDecline` — never `None` reaching persistence.
- The trail is append-only; no update/delete operation exists on the port. (A `reopen` cascade invalidating downstream evidence, per the existing engine, is an *adapter* concern for a later iteration — the port doesn't model supersession today; see §6.)
- `digest(scope)` is a pure function of `trail(scope)`: the latest content-bearing `now_understand`, or `None`. It is never computed or cached anywhere else — one source of truth, no drift.
- `why_exempt` never appears on the port's types. If a future adapter wants a *different* exemption rule (e.g. per-transition instead of per-gate), it changes only in that adapter's filter, never in the port.

**Ordering:** `record()` calls are strictly sequenced by the adapter's own call order (one JSON file, one process, no concurrency inside a single checklist — same assumption the existing `engine_session` lease already makes). `seq` is monotonic per scope. No ordering guarantee is made *across* scopes (different checklists' trails are independent).

**Error modes:**
| raised by | when | adapter's translation |
|---|---|---|
| `WhyRequiredError` | `record(ref, transition, None)` on effectively any call the adapter chose to make (i.e. non-exempt) | `EngineError`, surfaces as `REFUSED: ...` through the existing CLI path |
| `IncompleteWhyError` | `ContentAnswer` with a blank field | `EngineError`, same path |
| (none — soft) | `digest()`/`trail()` on an unknown scope/gate | `None` / `[]`; the read side is fail-soft by design, matching the governor's broader "missing data never forces a block" posture used elsewhere in this spec (the Gauge module) |

**Config:** none, deliberately. The temptation is a project-level toggle for "should mechanical declines count toward the digest," or "does `attach` solicit why on this project." Both would live in the *checklist schema/template* (Charter-owned, like `why_exempt` and `human_checkpoints` already are), not on the port — a configurable port is a port with more than one contract, which defeats the swap-the-backend premise this design exists to buy.

## 5. Honest seam assessment: one adapter, or two?

**One adapter today, and I don't think a second one is close.** The only concrete consumer of `WhyStorePort.record()` is `checklist_engine.py`'s `advance`/`attach`. Unlike the Gauge module (which the spec itself grounds in three real harnesses — Claude Code, Codex, pi — giving it a genuine two-adapter case), nothing in the DESIGN_SPEC names a second *write* backend for why-capture. This is exactly the "one adapter = a hypothetical seam" case the doctrine warns about.

There is a second **reader**, though, and it's worth being precise about why that doesn't rescue the seam: Module 4 (Refresh) needs to read `digest()`/`trail()` to assemble a handoff payload, independent of the `advance`/`attach` write path. That's a second *client* of the port's read side — but it reads through the same interface against the same backing store (the checklist's own `why_trail`), so it's read-diversity, not backend-diversity. It doesn't make the port a real seam; it just means the read half of the interface gets exercised by more than one caller, which is a reason to keep `digest`/`trail` narrow and stable, not evidence of genuine adapter plurality.

What I'd need to see before calling this a real seam: a second *storage* backend actually being built — e.g. a fleet-wide continuity ledger that several checklists write into, or a non-JSON-file execution substrate. Neither exists. **Verdict: speculative generality risk is real here.** The port buys real value even as a one-adapter seam (see §6), but I'm not going to claim it's validated by a second implementation, because it isn't.

## 6. Self-assessment

**DEPTH.** Reasonable. Three methods (`record`/`digest`/`trail`) hide: tagged-answer validation, the append-only accumulation, and the skip-mechanical digest walk. Call sites stay one line (`why_store.record(ref, "advance", why)`) regardless of how much validation logic sits behind it. Weakest point: `record()`'s signature (`ref`, `transition`, `answer`) is close to the adapter's own internal shape already — the interface isn't hiding much *complexity*, mostly hiding *where the check lives*. That's still a real win (see §3's enforcement-placement argument) but I'd stop short of calling this a deep module in the Ousterhout sense of "small interface, big implementation." It's a small interface over a small implementation, valuable for the invariant-locality it buys, not for complexity-hiding.

**LOCALITY.** Good, if implemented as a separate `why_store.py` module the engine imports, rather than as three more functions bolted into the existing 1500-line `checklist_engine.py`. The design doc above writes it that way deliberately. If the port and the JSON-backed adapter end up defined in the same file (plausible, given this project's "keep it in one script" habit elsewhere), locality erodes to "these are the same three functions, just typed as a Protocol" — cosmetic ports-and-adapters, not real separation. Worth flagging to whoever implements: the port's value depends on `why_store.py` importing nothing from `checklist_engine.py`, ever.

**SEAM PLACEMENT.** This is the axis I'm most confident about. Cutting the seam at "why_exempt and prompt-text stay adapter-side; the mandatory-answer invariant lives port-side" (§0, §3) is a real decision with a real alternative I rejected and explained (adapter-side enforcement, cheaper but duplicable). The seam is placed at the *invariant*, not at the *storage*, which is the right cut for a contract meant to survive a backend swap.

**TESTABILITY.** Clear win, and not hypothetical — the codebase already has a precedent for exactly this split: `evaluate_git_change_policy()` (pure) vs `_collect_changed_files()` (thin git collector) in `checklist_engine.py` today. `WhyStorePort` gets the checklist engine the same property for why-capture: `advance()`'s tests can inject an in-memory fake `WhyStorePort` (no JSON file, no `cl` mutation) to test the exemption-filter logic, and the JSON-backed `ChecklistWhyStore` can be unit-tested against a bare dict with no `advance()`/CLI machinery involved at all. Falsifiable tests from the spec's "Testing pathways" section map directly: "non-exempt advance with no why is refused" tests the adapter's filter *and* the port's `WhyRequiredError` independently; "latest `now_understand` is retrievable as the digest" tests `digest()` alone, no engine required.

**Net cost of the constraint.** The real tax here is §5, not the interface itself: I've designed and justified a port for a contract with one adapter and one hypothetical future one. If this module ships as designed and no second backend ever appears, the tagged `ContentAnswer`/`MechanicalDecline` types and the `Protocol` indirection are pure overhead versus "just add three fields to advance()/attach() and an `if not why_exempt and not why: raise`." I think the cost is worth paying here specifically *because* the enforcement-locality argument (§3) is real even in a one-adapter world — but that argument, not "we'll definitely swap backends," is the honest justification.

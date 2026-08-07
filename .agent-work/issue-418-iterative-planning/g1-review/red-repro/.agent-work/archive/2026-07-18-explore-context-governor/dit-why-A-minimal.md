# Why-capture — design A (constraint: MINIMAL-INTERFACE)

**Panel constraint:** smallest possible addition; fewest new concepts; reuse existing evidence/attest/status machinery wherever possible; a caller should have almost nothing new to learn.

## Zero-new-verb thesis

The engine already has exactly two moments where a unit of work closes and the
agent could otherwise walk away silent: `advance` (closes a gate on a `gated`
checklist) and `consolidate` (closes a `survey`). Every other closing-shaped
verb already carries a mandatory reason: `skip --reason`, `block --blocker
--authority --next`, `reopen --reason`. Those three are **already
why-compliant** — this design touches nothing about them.

So the entire why-capture module is: **three new optional CLI flags on
`advance`, the same three on `consolidate`, one new optional boolean field on
Task, and four new lines inside `current`.** No new verb, no new top-level
schema object, no new evidence-storage abstraction beyond the one enum value
the engine already uses this way for `waiver` / `artifact-policy`.

### Reading "advance/attach" in the fixed context

The context-governor intent block says "at every gate transition
(`advance`/`attach`)". Reading the engine source: `attach()` is not a second
transition verb — `advance` calls the internal `attach()` function to record
the `review-result` evidence *as part of* closing a gate (`checklist_engine.py`
line 780). I read "advance/attach" as naming that pair — the transition verb
and the evidence-recording primitive it uses internally — not as "every
generic `attach` call must now demand a why." Making bare `attach` (used
throughout for ordinary mid-task evidence — command output, waivers, artifact
policy results) interrogate the caller would be wildly disproportionate under
this constraint and would turn a housekeeping verb into a gate. I keep
`attach` itself untouched; the why rides `advance`'s *existing* internal call
to it.

## What's added

### 1. Task field: `why_exempt`

```json
{ "id": "g1", "...": "...", "why_exempt": false }
```

- Optional bool, default `false` (absent = not exempt = why is required).
- Set once, at template-authoring time, by whoever writes the checklist JSON
  (Charter / the role's `templates/*.template.json`). Never set at runtime.
- Sibling of `postconditions`/`constraints` — no new object, no new nesting.

### 2. Checklist-level field: `why_exempt` (survey only)

```json
{ "type": "survey", "...": "...", "why_exempt": false }
```

A `survey` checklist has no per-item gates — its one closing transition is
`consolidate`. So the exemption lives at the same altitude as the transition
it exempts: per-task for `gated` (matches `advance`'s per-gate granularity),
per-checklist for `survey` (matches `consolidate`'s once-per-checklist
granularity). This is not a second mechanism — it is the same field name at
the altitude each checklist type's real closing act already occurs.

### 3. Three new optional flags on `advance` and `consolidate`

```
advance <id> --why-done "..." --now-understand "..." --next "..."
consolidate --verdict ... --why-done "..." --now-understand "..." --next "..."
```

All three are plain optional strings (argparse defaults to `None`). No new
flag vocabulary is invented beyond the three field names the fixed context
already names: `why_done` / `now_understand` / `next`.

### 4. How `mechanical` is represented: it isn't — it's just content

The fixed context requires "an explicit `mechanical` answer is first-class and
valid; silence is not." The minimal way to satisfy that distinction needs
**no new type, no sentinel, no boolean flag**: the validation predicate is
"is this field a non-empty string," full stop. `--why-done mechanical` passes
that predicate exactly like a three-paragraph explanation does; an *absent*
flag does not. "Mechanical" is a **documented convention for the flag's
content**, not a piece of engine logic — the engine literally cannot tell the
difference between `mechanical` and any other short string, and it doesn't
need to. This is the single largest interface-reduction in the design: adding
a real sentinel type (e.g. `{"mechanical": true}`) would have doubled the
shape a caller has to learn for no behavioral gain.

### 5. Storage — two different existing mechanisms, one per checklist type

**Gated (`advance`):** the why becomes one more evidence item, using the
evidence list every task already has. New `Evidence.type` enum value: `why`.

```json
{
  "id": "e-g1-4",
  "type": "why",
  "payload": { "why_done": "...", "now_understand": "...", "next": "..." },
  "produced_by": "engine",
  "ts": ""
}
```

This is the exact code path `advance --from-child` already exercises
internally (`attach(cl, iid, "why", {...})`) — zero new plumbing.

**Survey (`consolidate`):** `consolidate()` already builds a `cons` dict and
assigns it to `cl["consolidation"]`. The why becomes one more key on that
dict, sibling to `verdict`/`findings`/`summary`:

```json
"consolidation": {
  "verdict": "APPROVE",
  "findings": [],
  "why": { "why_done": "...", "now_understand": "...", "next": "..." }
}
```

No evidence-list involvement for survey at all — the consolidation record
*is* the survey's one closing act, so the why rides the record that already
exists for that purpose, exactly as `consolidation.verdict` already rides it
for the reviewer's APPROVE/BLOCK.

### 6. Digest retrieval — folded into `current`, not a new verb

`current` already prepends a lease line when one exists (`_lease_line`). I add
the identical pattern: `_why_digest_line(cl)` scans for the latest why-record
and, if one exists, prepends `DIGEST: <now_understand>` to `current`'s output.

```python
def _why_digest_line(cl: dict) -> str | None:
    """Latest attached why-record's now_understand — the live 'current
    understanding' digest. Gated: scan items in order, last non-superseded
    'why' evidence wins (reopen's existing supersede cascade invalidates a
    stale digest for free — no new code). Survey: consolidation.why, if any.
    None if nothing has been recorded yet."""
    if cl.get("type") == SURVEY:
        why = (cl.get("consolidation") or {}).get("why")
        return f"DIGEST: {why['now_understand']}" if why else None
    latest = None
    for iid in cl.get("items", []):
        for ev in cl["tasks"][iid].get("evidence", []):
            if ev.get("type") == "why" and not ev.get("superseded"):
                latest = ev
    return f"DIGEST: {latest['payload']['now_understand']}" if latest else None
```

Because `current` is the verb every role already calls at the top of every
turn ("which step am I on"), the digest is surfaced for free on the call the
agent was making anyway — no new habit to teach.

**Reopen invalidation comes free.** `reopen`'s existing `_supersede_evidence`
cascade marks *every* evidence item on the target and downstream gates
superseded, indiscriminately by type. `why` evidence rides the same list, so a
reopened gate's stale digest silently stops being "latest" the moment the
cascade runs — no new invalidation logic was written for this.

## Enforcement — where it lives, and exact ordering

Both checks live **inside** `advance()` and `consolidate()`, after the
verb's existing checks, before the state mutation that closes the
transition — so a refusal is atomic: no evidence is attached and no status
changes on the why-refused path, matching the engine's existing
all-or-nothing shape for `advance`'s postcondition check and `amend`'s
copy-then-commit shape.

**`advance(cl, iid, why_done=None, now_understand=None, next_=None, ...)`:**

```
1. status must be in-progress                          (existing, unchanged)
2. --from-child: attach review-result                  (existing, unchanged)
3. postconditions must all be satisfied                (existing, unchanged)
4. NEW: if not t.get("why_exempt"):
       missing = [name for name, v in (("why_done", why_done),
                                        ("now_understand", now_understand),
                                        ("next", next_))
                  if not (v or "").strip()]
       if missing: raise EngineError(
           f"{iid}: why-answer required before advancing a non-exempt gate; "
           f"missing {missing} (a literal 'mechanical' is a valid, complete "
           f"answer for any part — silence is not)")
5. t["status"] = "complete"                             (existing, unchanged)
6. NEW: if not t.get("why_exempt"):
       attach(cl, iid, "why", {"why_done": why_done,
                                "now_understand": now_understand,
                                "next": next_})
7. return message (unchanged, including WAIVED-postconditions note)
```

Postconditions are checked **before** the why — an agent cannot buy its way
past unfinished work by supplying a beautiful why. The why is checked only
once the transition would otherwise legally succeed.

**`consolidate(cl, verdict, summary, override_reason, why_done=None,
now_understand=None, next_=None)`:** identical ordering — open-items check,
then the existing APPROVE/fails consistency guard, then (if `not
cl.get("why_exempt")`) the same missing-field check, then build `cons`
(unchanged) with `cons["why"] = {...}` added when supplied.

**Exempt path:** when `why_exempt` is true, steps 4/6 (or their consolidate
equivalents) do not run at all — the flags are simply ignored if omitted, and
still recorded if a caller supplies them anyway (no penalty for volunteering
one). This matches the fixed context precisely: "exempt gates don't prompt at
all."

## Invariants

- Every non-exempt `advance`/`consolidate` either succeeds with all three why
  fields present and non-empty, or is refused — there is no code path that
  closes a non-exempt gate/survey with fewer than three non-empty strings
  recorded.
- The most recently recorded `now_understand` (in item order, cascade-aware
  for gated; the sole record for survey) is always retrievable from `current`
  with no additional verb.
- `why` evidence and `consolidation.why` are append-only / replace-only
  through the same channels that already govern their containers (evidence
  list is append-only per task; `consolidation` is fully rebuilt only by a
  fresh `consolidate` call, which cannot run twice without new items to
  visit... actually it *can* be re-run is not possible — `consolidate`
  has no re-entry guard today and this design does not add one; out of scope
  for this module).
- The why never duplicates engine state mechanically — this half of the
  invariant is **not** engine-enforced (free text can't be), it is upheld by
  the imperative/prompt text authored alongside `why_exempt` at template time.
  Flagged honestly below as the one invariant this module cannot mechanically
  guarantee.

## Error modes

| Condition | Result |
|---|---|
| Non-exempt gate, `advance` called with any of the three flags missing/blank | `REFUSED: {iid}: why-answer required...; missing [...]` |
| Non-exempt survey, `consolidate` called with any of the three flags missing/blank | same shape, survey-level |
| Exempt gate/survey, flags omitted | succeeds, no why recorded, no error |
| Exempt gate/survey, flags supplied anyway | succeeds, why recorded (harmless) |
| Postconditions unmet AND why also missing | existing postcondition refusal fires first; why is never evaluated (no double-refusal, no partial credit) |
| `current` on a checklist with no why-record yet | no `DIGEST:` line (identical to no `LEASE:` line today) |

## Config

None. No new config file, no new `config_ref` key, no rigor dial. The only
"dial" is `why_exempt`, and it is data on the checklist itself (template-
authored), not engine config — consistent with how `postconditions` and
`override_policy` are also authored-in-place rather than centrally
configured.

## Migration cost (the one honest wrinkle)

The fixed context specifies `why_exempt` as an **opt-out** flag defaulting to
"not exempt." That is a real, if small, backward-compatibility break: every
existing shipped template's gates will start demanding a why on `advance`
the moment this ships, unless someone bulk-edits `why_exempt: true` onto them
first. This cuts against the engine's usual pattern (`engine_session`: absent
= old behavior, opt-in only) — but the fixed context is explicit about
opt-out semantics, and reversing that would violate "the design being
interfaced," not this constraint. I flag it rather than silently reinterpret
the given interface. Practical mitigation (not part of this module): a
one-time migration pass sets `why_exempt: true` on legacy templates' gates
that predate this feature, or the first `advance` refusal on an old
in-flight checklist simply prompts the agent to answer once — no data is
lost, no state is corrupted, it is a one-time surprise, not a break.

## Self-assessment on the four axes

**DEPTH — strong.** A caller who already knows `advance`/`consolidate` learns
exactly three flag names (which are literally the three field names named in
the fixed context, not new jargon) and reads the digest off a verb it already
calls every turn. In exchange, the engine gains a hard invariant: no
non-exempt gate or survey closes without a real or explicit-mechanical why on
record, retrievable without deriving it from anything. Very little new
surface for the amount of guarantee it buys.

**LOCALITY — strong, probably this design's best axis.** Every change is
inside two existing functions in one file (`advance`, `consolidate`), plus one
new helper (`_why_digest_line`) called from a third (`current`). No new file,
no new verb-dispatch entry in `_run_verb`/`parse_args` beyond three argparse
flags on two existing subparsers. A reviewer can hold the entire diff in one
screen.

**SEAM PLACEMENT — good, with one real cost.** `advance`/`consolidate` are
the two genuine "this closes" moments in the whole engine — not an invented
seam. The cost of minimalism here: because the why is captured **in the same
call** that performs the mechanical close, the two concerns (evidence-shape
verification and why-capture) are temporally fused. An agent cannot narrate
its reasoning progressively while still doing the work and then close the
gate separately later with no further narration required — every `advance`
demands a fresh, complete triad, every time, atomically. A design that
decoupled "declare your why" from "close the gate" (e.g. a standalone
mechanism) would allow incremental narration; this one trades that away for
having zero new verbs to learn. Given the assigned constraint, I judge that
trade correct, but it is a real capability the other two panel entries may
not have to give up.

**TESTABILITY — strong.** Both new checks are pure functions of
`(task_or_checklist_dict, three_optional_strings)` with no filesystem or
subprocess involvement — same shape as the existing `consolidate`
APPROVE/fails guard, which the engine already unit-tests directly. Falsifiable
per the fixed context's own testing pathway: "can a non-exempt gate pass with
no why?" is answerable by one `advance()` call with `why_done=None` and
asserting `EngineError` is raised before `t["status"]` changes and before any
`why` evidence appears — no I/O, no mocking. The digest helper is equally
pure: build a small `cl` dict by hand, assert `_why_digest_line` returns the
expected string or `None`.

**What the constraint cost, overall.** The main thing MINIMAL-INTERFACE gives
up is *flexibility of timing* (why-capture fused to the closing call, no
progressive/standalone narration channel) and a small amount of
*expressiveness* (three flat strings, no structured elaboration beyond what
the fixed context already asked for). What it buys: an agent that already
knows this engine needs to learn nothing beyond three field names it was
already going to have to think about, and a reviewer auditing the change sees
the entire mechanism in two functions.

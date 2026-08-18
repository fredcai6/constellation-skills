# Design candidate C — result

Pinned to `9b38b9d9`. All line numbers verified at this run against that commit unless a
line notes otherwise.

## 1. Candidate name and one-sentence summary

**`mutable_region`** — one optional top-level key on a gated checklist, `{"after": <gate-id
or null>, "before": <gate-id or null>}`, that names the two frozen bookend gates by id so
`amend()`'s existing `add`/`drop`/`rescope`/`retext-check` ops are refused outside the
half-open index range those two ids resolve to, and unrestricted (today's exact behavior)
when the key is absent.

## 2. The mechanism

**`checklist_engine.py` changes**, all inside or adjacent to `amend()` (`:2971`–`:3183`):

- New helper `_region_bounds(cl: dict, items: list[str]) -> tuple[int, int]`, placed next
  to `_floor()` (`:3036`). Reads `cl.get("mutable_region")`. If absent, returns
  `(0, len(items))` — no restriction, full backward compatibility. If present:
  `lo = items.index(after) + 1 if after else 0`; `hi = items.index(before) if before else
  len(items)`. (`after`/`before` are resolved by id against the CURRENT `items` list on
  every call, not cached — a region shifts automatically as gates are added/dropped inside
  it.)
- `_floor()` (`:3036`–`3043`) becomes `max(<existing status-derived floor>, lo)` — the
  existing non-pending freeze and the new region floor both apply; whichever is stricter
  wins. This is a one-line change: fold `lo` into the existing loop's initial value instead
  of starting it at `0`.
- `add`'s ceiling check (new, next to the existing floor check at `:3067`–`3072`): after
  computing `insert_at`, refuse `insert_at > hi` with a message naming the closing bookend
  (`before`) as the reason, symmetric to the existing "cannot insert before frozen gate"
  refusal.
- `drop` (`:3076`–`3088`) and `rescope` (`:3089`–`3114`): after the existing
  `status != "pending"` refusal, add one refusal: resolve `idx = new_items.index(tid)`; if
  `not (lo <= idx < hi)`, refuse with "gate lies outside the declared mutable region."
- `retext-check` (`:3115`–`3173`): same bound check, applied in addition to its existing
  `status not in ("pending", "in-progress")` refusal. This is a deliberate reading of the
  brief's own words — "**everything** outside that region is frozen" — over the narrower
  option of exempting retext-check as a non-structural fix. See §5 for the cost.
- **No change to `amend()`'s signature, its all-or-nothing commit discipline (`:3177`), or
  the `cl["amendments"]` audit record (`:3180`–3182`).** The delta's `ops` summaries already
  read `"dropped {tid}"` / `"added {nid}"` etc.; a region refusal is just one more
  `EngineError` raised before commit, so a rejected op still leaves `cl` unmutated exactly as
  today.
- **A pleasant emergent property, not a special case:** the two named bookend gates
  themselves are automatically excluded from `[lo, hi)` by construction — `after` sits at
  index `lo - 1` (outside because `lo - 1 < lo`), `before` sits at index `hi` (outside
  because the range is upper-exclusive). No separate "protect the anchors" branch is needed;
  dropping or rescoping a bookend gate is refused by the exact same bound check that governs
  every other frozen gate.

**Plan/template JSON shape.** One new optional top-level key, sibling to `type`/`items`/
`tasks`. No new nesting inside `tasks`, no new field on any individual gate.

```json
"mutable_region": {"after": "plan", "before": "archive"}
```

`after`/`before` may each independently be `null` (open bookend — see the crew case in §4).
Omitting the key entirely is the legacy shape and behaves identically to `9b38b9d9`.

**MCP door.** `spine_amend` (`scripts/mcp_spine_server.py:2046`–`2069`) needs **no schema
change** — `delta`/`reason`/`authority` are unchanged, and the tool already "writes it to a
file beside the bound spine and hands the engine that path; the engine alone validates the
ops, never this door" (`:2052`–2053`). A region refusal surfaces exactly like any other
`EngineError` amend refusal does today. The only door-side change is documentation: the
tool's `description` string gains one sentence noting that a declared `mutable_region`
additionally bounds where ops are accepted. There is **no new verb** to set or move the
region — it is authored once, as part of the plan, the same way `items`/`type` are.

**What a role does differently.** Nothing procedurally new — a role already calls `amend`
(via `spine_amend`) to re-plan a GATED checklist's middle. What changes is where the
gates it adds *live*: instead of a Commander's `execute` gate carrying a `child_checklist:
"execute.json"` that is invisible to `amend`, `mutable_region` makes it coherent to `add`
the granular work gates **directly into the main spine's `items`**, inside the declared
window, and `drop` the now-redundant `execute` placeholder. See §3.

## 3. Worked example — Commander spine

Template today (`skills/commander/templates/COMMANDER_SPINE.template.json:5`):
`init·context·understand·plan·execute·reconcile·triage·review·feedback·archive`.

Declaration added at the same top level as `"items"`:

```json
"mutable_region": {"after": "plan", "before": "archive"}
```

Resolved against this list: `after="plan"` → index 3 → `lo=4`; `before="archive"` →
index 9 → `hi=9`. Mutable window = indices `[4, 9)` = `execute, reconcile, triage, review,
feedback`. Frozen: `init, context, understand, plan` (before the window) and `archive`
(at/after the window) — exactly the human's "frozen at start and finish."

**The amend delta a Commander at `plan` sends**, in place of authoring `execute.json`:

```json
{
  "ops": [
    {"op": "drop", "id": "execute"},
    {"op": "add", "id": "g1-implement", "after": "plan",
     "title": "Implement g1", "imperative": "<dispatch the implementer crew for g1>",
     "postconditions": [{"id": "c1", "statement": "g1 implemented, evidence integrated", "check": null}]},
    {"op": "add", "id": "g1-review", "after": "g1-implement",
     "title": "Review g1", "imperative": "<dispatch the reviewer crew for g1>",
     "postconditions": [{"id": "c1", "statement": "g1 independently reviewed", "check": null}]},
    {"op": "add", "id": "g1-integrate", "after": "g1-review",
     "title": "Integrate g1", "imperative": "<merge g1's evidence, close the gate>",
     "postconditions": [{"id": "c1", "statement": "g1 evidence integrated into the spine", "check": null}]}
  ]
}
```
via `spine_amend` with `reason="author gates directly into the spine, replacing
execute.json for this run"`, `authority="human"` (interactive) or the delegated-mode
citation pattern already used elsewhere in this spine (e.g. `LAUNCH_ORDER:Mission`) for a
Commander running under an Admiral.

Walk the engine through it: `drop execute` — `execute` is `pending`, and its index (4) is in
`[4, 9)`, so it passes both the existing status gate and the new region gate. Each `add`
resolves `after` against gates that exist at validation time (`plan`, then the
just-validated `g1-implement`, then `g1-review` — `:3060`–3066` already lets a later op in
the same delta reference an id an earlier op in the SAME delta introduced, confirmed by the
existing test `test_amend_add_later_op_can_reference_earlier_added_id`), and each resulting
`insert_at` is checked against both the status floor and the new region ceiling (`hi=9`,
recomputed against the growing `new_items` on every op) — inserting at position 4, 5, 6 all
satisfy `<= 9`. The delta commits atomically; `cl["items"]` becomes `init, context,
understand, plan, g1-implement, g1-review, g1-integrate, reconcile, triage, review,
feedback, archive`. `active_id()` (positional, per `:2589`/`start`) now serves
`g1-implement` next — no different from how it serves `execute` today.

**Now the Commander tries `{"op": "drop", "id": "archive"}`.** `archive` is `pending`
(passes the status check unchanged from today), but its index is 11 (in the delta above) —
or 9 in the undeclared-region baseline — either way `index("archive") >= hi (9)`, so it
fails `lo <= idx < hi`. The engine refuses: *"drop archive: gate lies outside the declared
mutable region (frozen bookend)."* **This is the fix for fact 3's gap** — at `9b38b9d9`,
that same `drop archive` call is accepted today (`archive` is pending and nothing else
gates `drop`); with `mutable_region` declared, it is refused.

## 4. How it lands for Admiral and for crew

**Admiral** (`items`: `init, latitude, execute, closeout`; `9b38b9d9` line
`ADMIRAL_SPINE.template.json:5`). Declaration: `"mutable_region": {"after": "latitude",
"before": "closeout"}` → `lo=2, hi=3` → mutable window = `{execute}` only, at first. **The
single `execute` gate does not grow one gate per wave by itself** — the *mechanism* for
growing it already exists (`drop execute` + `add wave-1`/`wave-2`/... , same shape as the
Commander example), but nothing in this candidate makes the Admiral do that automatically;
whether to keep one `execute` gate that internally loops over `NEXT_WAVE.json` transitions
(today's actual shape, per the Admiral spine's `directives.wave_transition` block,
`:45`) or to reify waves as sibling top-level gates is the Admiral's authoring choice at
`latitude`/`plan` time, made possible but not mandated by this key. **Answering directly, as
required:** with `mutable_region` alone, waves stay the current shape — one `execute` gate
driving `NEXT_WAVE.json`/`transitions/` internally — because reifying waves as gates is an
*available* re-plan, not a *forced* one, and nothing else in this run's scope (fact 6: the
epic's own live `ADMIRAL_LOG.md`/`transitions/` middle-files already carry the wave record)
demands the reification. A future author could choose to `add` one gate per wave; this
candidate does not decide that for them.

**Crew** (`IMPLEMENTER_PLAN.template.json`, items: `m0-context, m1`). Declaration:
`"mutable_region": {"after": "m0-context", "before": null}` — `before: null` means `hi =
len(items)`, i.e. **no frozen finish**, only a frozen start. This is the one genuinely
different answer across the three roles, and it is forced by the source, not chosen for
convenience: `IMPLEMENTER_PLAN.template.json` names no gate that plays `archive`'s role —
a crew plan's last `mN` **is** its finish, and it is exactly the gate a crew is most likely
to want to retext or rescope as it discovers the real shape of the work (the human: "I
wouldn't be mad at a crew updating its plan along the way too"). Freezing crew's `m1`
onward the way Commander's `archive` is frozen would contradict the human's direction for
crew specifically. So: crew gets a frozen bookend at the start (`m0-context` — handoff
verification should never be re-plannable) and a fully open middle+finish. `m1`'s
placeholder title/imperative ("`<implementation step>`") already reads as designed to be
`rescope`d in place; this candidate makes that legible via `cl["amendments"]` instead of
silent overwrite.

## 5. Attack your own candidate

1. **An existing in-flight spine with no declaration keeps today's exact gap — this
   candidate does not retrofit safety onto anything already running.** `.agent-work/567-k/
   spine.json` and `.agent-work/epic-567-door/spine.json` are both live at `9b38b9d9` and
   both instantiated from templates that (before this candidate ships) carry no
   `mutable_region` key. `_region_bounds` returns `(0, len(items))` for them — full range,
   no restriction — so an Admiral standing at `execute` on the live epic-567-door spine can
   still `drop closeout` today, tomorrow, and for the life of that spine, because the key
   was never in the template it was instantiated from. **Not fixable within this
   constraint**: the constraint is explicitly "declare it once, at plan level," and a plan
   already instantiated has no re-instantiation path this candidate defines. The human must
   accept that shipping this candidate protects new spines, not the two spines currently
   running under this very epic — closing that gap needs a **separate**, explicit migration
   step (write `mutable_region` into a live `spine.json` by hand or via a new engine verb),
   which is out of this candidate's scope by its own "no new verb" minimalism.

2. **Someone can defeat the freeze without `--force`, using the SAME move fact 3 already
   found: rescope the bookend gate's own postconditions into a no-op before dropping it —
   except now they can't, because rescope on the bookend is refused by the identical bound
   check.** But there is a real remaining hole: **`retext-check` on a gate INSIDE the
   window can rewrite that gate's own check to something meaningless** (e.g. reduce a
   `command` check to `true`) without ever touching the frozen bookend at all, then advance
   through it trivially satisfied. This isn't new — `9b38b9d9` already allows retext-check
   on any pending/in-progress gate, correctly scoped as "a fix for the TEXT of a check, never
   a way to satisfy it" (`:2989`–2992`) — but `mutable_region` does nothing to narrow it, and
   a reviewer auditing "was the middle honestly re-planned" has to read `cl["amendments"]`
   summaries (`"retext-check g1-review.c1"`) and judge intent by eye. **Not fixable within
   this constraint** — the constraint is about WHERE amend applies, not WHAT counts as a
   legitimate check-text correction; that is `retext-check`'s own pre-existing design
   surface, unchanged here.

3. **The cost to an author who just wants a small plan: one more top-level key to get right,
   and getting it wrong fails silently in the "too permissive" direction, not the "too
   strict" one.** A typo in `after`/`before` — a gate id that doesn't exist in `items` — is
   not validated at plan-authoring time (there is no schema validator for the checklist
   shape at `9b38b9d9`; I found no `_validate_checklist`/schema-check function in
   `checklist_engine.py`). `_region_bounds`'s `items.index(after)` would raise a bare
   `ValueError` (not an `EngineError`) the FIRST time `amend` is ever called against that
   spine — likely gates, possibly waves, into the run before anyone notices the region
   declaration was broken. **Fixable within this constraint**: `_region_bounds` should
   raise an `EngineError` at first use naming the unresolvable anchor, rather than let a bare
   `ValueError` surface — a small addition I did not include in §2 originally and am flagging
   here as a required hardening, not an optional one.

4. **The migration cost of moving `execute.json` into the spine is real and this candidate
   does not make it free.** Every existing Commander imperative that references
   `execute.json` by name — `plan`'s imperative ("BEFORE authoring execute.json...",
   `COMMANDER_SPINE.template.json:49`), `execute`'s own `child_checklist: "execute.json"`
   field and its imperative's `run_crew.py`/`recover_crews.py` invocations
   (`:65`, `:76`), the `verify_iterative_role_artifacts.py commander` check that
   reads `execute`'s gate-by-gate record — all assume gate-execution detail lives in a
   CHILD checklist, not as sibling top-level gates. `mutable_region` makes authoring gates
   directly into the main spine *possible* (§3), but every one of those imperatives, and
   the `run_crew.py`/`recover_crews.py` dispatch scripts themselves (both explicitly
   off-limits to this candidate per the brief's Rules), would need to learn to drive a
   `g1-implement` main-spine gate the way they drive an `execute.json` item today. **A real
   cost the human must accept, not fixable within this run**: this candidate answers "can
   the mechanism support it" (yes) but the brief's own Rules forbid touching
   `run_crew.py`, so I cannot and do not claim the migration is done, or even that this
   candidate makes it cheap — only that it makes it POSSIBLE without a second mechanism.

## 6. Test surface

New tests, following the existing `AmendVerb`/`AmendRetextCheck` classes in
`tests/test_checklist_engine.py` (`:1417`, `:1576`):

- `tests/test_checklist_engine.py::AmendVerb::test_amend_add_refuses_past_declared_region_ceiling`
  — a gated checklist with `mutable_region: {"after": "a", "before": "d"}`; `add` with
  `after: "d"` (or no `after`, defaulting to append) is REFUSED.
- `tests/test_checklist_engine.py::AmendVerb::test_amend_drop_refuses_gate_before_region_start`
  — `drop` on a pending gate at index `< lo` is REFUSED even though status alone would
  allow it (the direct regression test for fact 3's gap).
- `tests/test_checklist_engine.py::AmendVerb::test_amend_drop_refuses_pending_closing_bookend`
  — `drop` on the `before`-named gate itself (pending) is REFUSED — the literal
  `drop archive` scenario from §3.
- `tests/test_checklist_engine.py::AmendVerb::test_amend_rescope_refuses_outside_region`
  — mirrors the drop test for `rescope`.
- `tests/test_checklist_engine.py::AmendRetextCheck::test_amend_retext_check_refuses_outside_region`
  — a pending/in-progress gate outside `[lo, hi)` still refuses retext-check despite passing
  the existing status check.
- `tests/test_checklist_engine.py::AmendVerb::test_amend_add_inside_region_succeeds_and_shifts_ceiling`
  — the Commander worked example: drop `execute`, add three gates after `plan`, confirm
  `cl["items"]` ordering and that a follow-up `add ... after="g1-integrate"` still resolves
  `hi` correctly against the now-larger list.
- `tests/test_checklist_engine.py::AmendVerb::test_amend_region_bounds_default_full_range_when_undeclared`
  — **the backward-compat test**: a checklist with no `mutable_region` key behaves
  IDENTICALLY to every existing `AmendVerb`/`AmendRetextCheck` test in the file (run the
  existing `test_amend_drops_pending_gate`/`test_amend_adds_pending_gate_at_position_and_logs`
  bodies unmodified against a checklist built the same way, assert unchanged outcomes) —
  i.e., this candidate adds no new failure mode to any spine that predates it.
- `tests/test_checklist_engine.py::AmendVerb::test_amend_refuses_unresolvable_region_anchor`
  — the hardening from §5.3: `mutable_region.after`/`before` names a gate id absent from
  `items` (e.g. already renamed, or the template is malformed); asserts an `EngineError`
  naming the anchor, not a bare `ValueError`.
- `tests/test_mcp_door_engine_cwd.py` — no new test required; `spine_amend`'s existing
  round-trip coverage already exercises the file-handoff path this candidate does not
  change.

## 7. What you are NOT claiming

- I did not check whether any OTHER engine verb besides `amend` (e.g. `append` on a survey,
  `:3186`) should also respect `mutable_region` — the brief's constraint and the human's
  direction are both scoped to re-planning a GATED checklist's middle, and `append` is
  survey-only (`:3187`), so I left it untouched, but I did not exhaustively re-read every
  verb in the file to confirm none of the others silently restructure a GATED checklist's
  `items`.
- I did not run any test, including the ones I named in §6 — the brief forbids running the
  full suite, and I was not asked to write code. §6 is a specification, not a diff.
- I did not check `_gate_headroom_tokens` (`:1648`), `_trip_hard_gate` (`:2144`), or any
  other function that reads `cl["items"]` positionally, for whether inserting/dropping gates
  mid-run (already legal today via bare `amend`, independent of this candidate) interacts
  with them — that risk exists at `9b38b9d9` already and is not new here.
- I did not verify whether `docs/agents/engine-config.json` or any per-repo config carries
  its own notion of gate freezing that `mutable_region` would need to reconcile with — I
  read only `checklist_engine.py`, the three role spine templates, `IMPLEMENTER_PLAN.
  template.json`, and `mcp_spine_server.py`'s tool list, per the brief's named source.
- The Explorer spine (`init·context·explore·spec·review·confirm·route`) is asserted from
  the brief's fact 5 (I did not re-read `EXPLORER_SPINE.template.json` myself this run) —
  the human's direction plausibly extends `mutable_region: {"after": "context", "before":
  "route"}` to it, but I did not verify that file's exact line numbers or confirm no
  Explorer-specific imperative already assumes an un-declared, fully-open middle.
- §4's Admiral answer is a claim about what this candidate ENABLES, not a recommendation
  that Admirals SHOULD reify waves as top-level gates — that tradeoff (one visible gate per
  wave vs. the current internal `NEXT_WAVE.json` loop) is a design call for whoever owns
  the Admiral skill next, which I am explicitly declining to make on their behalf.

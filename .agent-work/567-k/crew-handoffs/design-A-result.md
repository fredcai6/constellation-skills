# Design candidate A — Positional Bookends

All citations pinned to `9b38b9d9`. Every line number below was re-verified at source during
this run; none had moved from the brief's citations.

## 1. Candidate name and one-sentence summary

**Positional Bookends.** The engine treats `cl["items"][0]` and `cl["items"][-1]` — whatever ids
currently occupy the first and last slot of a checklist, recomputed fresh on every `amend()` call
— as the frozen bookends, and refuses `drop`/`rescope` against them and refuses an `add` that
would insert at or past the last slot; nothing is added to the JSON schema, because the freeze
*is* the existing `items` array read two ways instead of one.

## 2. The mechanism

**`checklist_engine.py` changes, all inside `amend()` (`:2971`):**

- After the existing copy-construction (`new_items = list(cl["items"])`, `:3032`), add two locals,
  computed once per `amend()` call from the **pre-delta** `new_items`:
  ```python
  opening_id = new_items[0] if new_items else None
  closing_id = new_items[-1] if new_items else None
  ```
  These are computed once at the top of the call, not re-derived per-op, and — because no op in
  this design is ever allowed to touch `opening_id`/`closing_id`'s occupancy of slot 0 or slot
  `len-1` — `new_items.index(closing_id)` stays valid and stable for every op in the same delta.

- **`add` (`:3047`–`:3075`).** Immediately after the existing `_floor()` check
  (`:3067`–`:3072`, "cannot insert before frozen (non-pending) gate"), add a second, symmetric
  bound:
  ```python
  if closing_id is not None and insert_at > new_items.index(closing_id):
      raise EngineError(
          f"add {nid}: cannot insert at or after the closing bookend {closing_id!r} "
          f"(position {len(new_items) - 1}); the last gate is frozen by position, "
          f"not by status",
          task_id=nid, verb="amend-add",
      )
  ```
  `_floor()` (`:3036`–`:3043`) is untouched — it still governs the *status*-based lower bound.
  This is a purely positional *upper* bound alongside it. Note the effect: `after: closing_id`
  computes `insert_at = new_items.index(closing_id) + 1`, which is exactly one past the allowed
  ceiling — refused. `after` omitted (append-at-end) computes `insert_at = len(new_items)`, also
  refused whenever the checklist is non-empty. The only way left to add a gate is to name an
  `after` that is *not* the closing bookend — i.e., into the middle.

- **`drop` (`:3076`–`:3088`).** Before the existing `status != "pending"` check, add:
  ```python
  if tid in (opening_id, closing_id):
      slot = 0 if tid == opening_id else len(new_items) - 1
      raise EngineError(
          f"drop {tid}: the gate at position {slot} is a frozen bookend and cannot "
          f"be dropped regardless of status",
          task_id=tid, verb="amend-drop", status=status,
      )
  ```
  This is what actually closes fact #3's gap: today `status == "pending"` is the *only* guard, so
  a still-pending closing bookend (`archive`, `closeout`, `route`) is wide open. Position, not
  status, is now the guard for both ends.

- **`rescope` (`:3089`–`:3114`).** Same identity check, same place, same message shape
  (`amend-rescope`).

- **`retext-check` (`:3115`–`:3173`) is deliberately left untouched.** It corrects check *text*
  on a pending/in-progress gate, never marks a condition satisfied, never changes a check's kind
  (`:3158`–`:3163`), and never changes which gates exist or their order. Structural freeze and
  textual correction are different concerns; conflating them would let a bookend's *check* still
  be neutered without ever touching `drop`/`rescope` (see §5, attack 4 — I did not close this).

- `amend()`'s docstring (`:2972`–`:3000`) gets one added paragraph documenting the positional
  freeze; no behavioral surface beyond what's above.

**What changes at the MCP door (`scripts/mcp_spine_server.py`):** nothing, structurally. The
`spine_amend` tool (`:2046`) already forwards `delta`/`reason`/`authority` to
`run_engine("amend", ...)` (`:2422`) and returns whatever the engine returns, success or
`EngineError`, through the same `_tool_error`/`as_result` path every other refusal already uses
(`:2401`–`:2422`). A bookend refusal is just one more `EngineError` riding the existing channel.
I'd update the tool's `description` string to mention the refusal so an agent reading the tool
schema learns about it without a failed call — prose, not a schema change.

**What changes in the plan/template JSON shape:** nothing. This is the constraint taken
literally. The "literal JSON fragment a spine template would carry" is the fragment every
template *already* carries and nothing more:
```json
"items": ["init", "context", "understand", "plan", "execute", "reconcile", "triage", "review", "feedback", "archive"]
```
`items[0]` ("init") and `items[-1]` ("archive") *are* the bookend declaration. There is no
`"frozen": true` key anywhere. If a plan-author wants a different opening or closing gate, they
reorder `items` — the declaration moves with the array, for free, because it was never a separate
fact to keep in sync.

**What a role does differently:** a Commander/Admiral/Explorer that wants to reshape its own
middle now calls `spine_amend` on its *own top-level spine* the same way it would today amend a
child `execute.json` or `interrogation.json` — no new verb, no new mental model, just a target
list (`cl["items"]`) that used to be conceptually static past `init` and is now understood to be
open between position 0 and position `len-1`.

## 3. Worked example

Commander spine `items` (`skills/commander/templates/COMMANDER_SPINE.template.json:5`):
`init · context · understand · plan · execute · reconcile · triage · review · feedback · archive`.

I read this run's own live spine (`.agent-work/567-k/spine.json`, read-only, not mutated) to
confirm current statuses: `init/context/understand` complete, `plan` in-progress, everything from
`execute` on is pending. Under Positional Bookends: `opening_id = "init"` — frozen by position
*and* already frozen by status (`:3080`, `status != "pending"`) since it's complete. `closing_id =
"archive"` — frozen by position alone; its status is `"pending"`, so today's engine (no patch)
would let it be dropped; mine refuses it regardless.

**The `plan`-gate amend, authoring `g1-implement`/`g1-review`/`g1-integrate` into the top-level
middle instead of into `execute.json`:**
```json
{
  "ops": [
    {
      "op": "add", "id": "g1-implement", "after": "plan",
      "title": "Implement the change",
      "imperative": "Make the minimal change per the approved plan.",
      "postconditions": [{"id": "c1", "statement": "change implemented", "check": null}]
    },
    {
      "op": "add", "id": "g1-review", "after": "g1-implement",
      "title": "Independent review",
      "imperative": "Dispatch a fresh-context reviewer against the diff.",
      "postconditions": [{"id": "c1", "statement": "review verdict recorded", "check": null}]
    },
    {
      "op": "add", "id": "g1-integrate", "after": "g1-review",
      "title": "Integrate and verify",
      "imperative": "Merge the reviewed change; run the verification command.",
      "postconditions": [{"id": "c1", "statement": "verified", "check": {"kind": "command", "command": "<exact test command>"}}]
    }
  ]
}
```
via `spine_amend` with `reason="split execute into visible top-level gates for #634"`,
`authority="commander (delegated per LAUNCH_ORDER:Mission)"` (interactive mode: `authority="human"`
after confirmation — `amend` requires human ratification "same as `waive`", `:2993`).

`_floor()` at the moment of this call is `index("plan") + 1` (plan is in-progress, the last
non-pending gate) `= 4` (0-indexed: init=0, context=1, understand=2, plan=3), i.e. the position of
`execute`. `after: "plan"` computes `insert_at = 4`, which is `== floor` — allowed. My new ceiling
check: `closing_id = "archive"` sits at `new_items.index("archive") = 9`; `insert_at = 4 ≤ 9` —
allowed. All three ops land between `plan` and `execute`, one after another. Commit succeeds;
`cl["amendments"]` gets one entry: `{"ts": ..., "reason": "...", "authority": "...", "ops":
["added g1-implement", "added g1-review", "added g1-integrate"]}` (`:3180`–`:3182`).

**Then, later, that same Commander at `execute` tries `drop archive`:**
```
amend(cl, {"ops": [{"op": "drop", "id": "archive"}]}, reason="skip archiving, low-stakes run", authority="commander")
```
Refused: `archive` is `closing_id` (`new_items[-1]`), so the identity check fires *before* the
status check ever runs:
```
EngineError: drop archive: the gate at position 9 is a frozen bookend and cannot be dropped
regardless of status
```
`cl` is unmutated (the whole delta commits or nothing does, `:3177`–`:3183`) — same all-or-nothing
guarantee as any other refused amend.

## 4. How it lands for Admiral and for crew

**Admiral.** The single `execute` gate does **not** grow one gate per wave — I checked this
directly rather than assuming it. `execute` (`skills/admiral/templates/ADMIRAL_SPINE.template.json:31`)
is the very next gate after `latitude`; in every real run it gets `start`-ed (in-progress) almost
immediately, well before wave count or shape is known. `add`'s only insertion mechanism is
`after: <existing-gate-id>`, and once `execute` is in-progress it is no longer the checklist's
last *pending* prefix boundary for `_floor()` purposes, but that's irrelevant here — the real
blocker is that decomposing "one `execute` gate" into "N wave gates" would require *dropping* the
already-started `execute` gate and replacing it with siblings, and `drop` (both today and under my
patch) only ever touches a `status == "pending"` gate (`:3081`–`:3085`); a started gate cannot be
retro-decomposed by any amend delta, mine included. So: **waves stay a different shape** — the
existing `NEXT_WAVE.json` / `transitions/<boundary-id>/` / `ADMIRAL_LOG.md` machinery inside the
single `execute` gate (`:34`, the `wave_transition` directive block, `:45`), which is exactly the
cross-agent-verdict-adjacent, doctrine-driven "second-file middle" the brief's fact #6 names and
fact #4 says must survive untouched. What Positional Bookends *does* newly buy an Admiral is the
ability to insert a brand-new **top-level** pending gate between `execute` and `closeout` for a
structural surprise the wave loop has no name for — e.g., an unplanned human-review checkpoint —
without inventing a new file for it. It does not, and structurally cannot, turn "execute" into
"wave-1, wave-2, ...".

**Crew (`IMPLEMENTER_PLAN.json`).** Same question, and here the honest answer is worse. Items
start as `["m0-context", "m1"]` (`skills/implementer/templates/IMPLEMENTER_PLAN.template.json:6`).
`opening_id = "m0-context"`, `closing_id = "m1"`. The moment the crew's plan carries only these two
gates, `m1` — the crew's *entire actual unit of work* — sits in the closing-bookend slot and is
therefore frozen against `drop`/`rescope` by position alone, even while `status == "pending"`.
That is backwards for crew: `m1` is not a ceremonial finish line the way `archive`/`closeout`/
`route` are; it's the first (and often only) real milestone, and the human's own words want *this
exact thing* — "a crew updating its plan along the way" — to stay easy. Growing to `m2` before
touching `m1` sidesteps it (then `m1` is mid-checklist, freely rescopable, and `m2` inherits the
frozen slot instead) but that's a workaround the author has to know to reach for, not a property
of the design. I address this head-on in §5 rather than patching around it, because patching
around it (e.g. exempting "checklists with exactly 2 items") is not a *positional* rule anymore —
it's a size heuristic bolted on to rescue positionality, and the constraint asked me to own a
positional answer sharply, not to smuggle in a second rule to save it.

## 5. Attack my own candidate

**1. It cannot actually be backward compatible, and no amount of engineering fixes that under
this constraint.** The hard requirement says an undeclared plan "must behave *exactly* as it does
at `9b38b9d9`." But there is, by the constraint's own design, no bit anywhere that distinguishes
"a plan that has opted into bookend enforcement" from "a plan that predates the feature" — they
are the identical bytes on disk, because I was told not to add any. The instant the patched engine
ships, `drop archive` on *every* Commander spine in flight — including this run's own
`.agent-work/567-k/spine.json` and the Admiral epic spine at `.agent-work/epic-567-door/spine.json`
— goes from succeeding (today, fact #3) to refusing. That is a real, provable behavior change on
an undeclared plan, not a hypothetical. Under "no new state," backward compatibility and a
positionally-enforced closing-bookend freeze are mutually exclusive; I cannot have both, and I am
not going to pretend I found a way. The mitigating argument — nobody's current workflow *depends*
on being able to drop its own closing gate, so the practical blast radius is near zero and the
change is strictly more conservative, never less — is real, but it does not make the requirement
true. This is the cost the human has to accept if they want this candidate: redefine "backward
compatible" to mean "no legitimate workflow breaks" rather than "bit-identical refusal set," or
reject positional-only bookends outright.

**2. The freeze can be defeated without `--force`, across two ordinary, individually-valid
calls.** Within one `amend()` call, `closing_id` is fixed at the top and nothing can dislodge it
(§2). But nothing stops a *second*, later `amend()` call from adding a new gate after the current
closing bookend via `after: <closing_id>` and getting refused... no — reread: within a *single*
call the ceiling check refuses that outright, so this exact vector is closed. The real gap is
subtler: `rescope` can rewrite a bookend gate's `title`/`imperative`/`postconditions` — wait, no,
`rescope` on `opening_id`/`closing_id` is refused too (§2, same identity check). So structural
defeat via `add`/`drop`/`rescope` is genuinely closed for a *single* bookend across all deltas,
because the bookend's identity and slot never move — there is no sequence of my three guarded ops
that ever relocates `archive` out of `new_items[-1]` or `init` out of `new_items[0]`. I looked for
the cross-delta laundering path I originally suspected (add a trailing gate after the bookend in
delta 1, drop the now-displaced old bookend in delta 2) and it does not exist under this design,
because delta 1's `add` is refused outright by the ceiling check — it can never displace
`closing_id` in the first place. The defeat that *does* survive is attack 4 below: `retext-check`.

**3. It costs an author who "just wants a small plan" real, unrecoverable friction.** This is §4's
crew finding restated as a cost rather than a curiosity: a two-gate `IMPLEMENTER_PLAN.json`
(`m0-context`, `m1`) cannot `rescope m1` — the single milestone doing all the actual work — via
`amend` at all, ever, without first padding the plan with a gate the author doesn't otherwise want,
purely to push `m1` out of the frozen slot. That's not fixable within "purely positional, no size
heuristic" — it's a structural mismatch between "freeze the ends" (built for a 10-gate ceremonial
role spine) and "the whole plan is 1–2 gates of real work" (crew's actual shape). The human has to
either accept this cost for crew, or accept that the mechanism needs *some* per-shape awareness
(which stops being purely positional).

**4. `retext-check` is a live escape hatch I deliberately did not close.** A bookend's *check text*
can still be rewritten via `retext-check` (`:3115`) on `closing_id` while it's `pending` — same-kind
swap only, never marks it satisfied — so an author who wants to defang `archive`'s `c2b`
"work is REACHABLE" command check (`skills/commander/templates/COMMANDER_SPINE.template.json:128`)
without ever calling `drop`/`rescope` can retext its `command` field to something trivially true
(e.g. `"true"`) and pass it on the next `advance`. Nothing in my mechanism inspects *what* a
`retext-check` op changes the command *to* — only that the check's `kind` stays the same
(`:3158`–`:3163`) and the gate is pending/in-progress. This is fixable in principle (extend the
identity check to also gate `retext-check` on `opening_id`/`closing_id`), but I chose not to,
because a bookend whose check text can never be corrected — not even to fix a typo'd command path
— is a worse deliverable for a real repo than one where the *shape* is frozen and the *wording* of
its check is not. If the human disagrees with that trade, closing it costs one more `tid in
(opening_id, closing_id)` guard in the `retext-check` branch (`:3115`) — cheap, but it was a
deliberate scope choice, not an oversight, and I'm flagging it as still open.

**5. The migration cost of moving `execute.json` into the spine is real and asymmetric per role.**
For Commander, the migration is mechanical and shown in §3: stop writing gates into
`execute.json`'s own `items` array and instead `amend`-add them onto the top-level spine between
`plan` and `archive`. Nothing about `execute.json`'s *existence* is forced to change — a Commander
could keep using it, or inline gates top-level, or mix both (some milestones top-level, others
still delegated to a child checklist) — the brief's fact #6 already establishes `execute.json`
exists by doctrine, not engine necessity, and my mechanism doesn't touch that necessity either way.
For Admiral, §4 already shows the migration *cannot happen at all* for the wave loop specifically
(execute starts before waves are known), so "moving `ADMIRAL_LOG.md`/`transitions/` into the
spine" is not a migration my mechanism enables — it's a no. That asymmetry — Commander's middle can
fully migrate onto the top-level spine, Admiral's cannot — means "all three roles, one mechanism"
is true at the *engine* level (identical code path, identical JSON shape) but false at the
*doctrine* level (each role still needs its own judgment about what actually moves). I want that
distinction on the record rather than glossed as "solved."

## 6. Test surface

- `tests/test_checklist_engine.py::TestAmendBookends::test_add_refused_at_or_after_closing_bookend`
  — `add` with `after: "archive"` on a fresh `COMMANDER_SPINE` copy raises `EngineError`; `cl`
  unmutated (assert `items`/`tasks` identical to pre-call snapshot).
- `tests/test_checklist_engine.py::TestAmendBookends::test_add_default_append_refused_when_nonempty`
  — `add` with no `after` (append-at-end) on a non-empty checklist raises, for the same reason.
- `tests/test_checklist_engine.py::TestAmendBookends::test_add_immediately_before_closing_bookend_allowed`
  — `add` with `after: "feedback"` (second-to-last gate) on `COMMANDER_SPINE` succeeds; the new
    gate lands directly before `archive`, `archive` stays `items[-1]`.
- `tests/test_checklist_engine.py::TestAmendBookends::test_drop_closing_bookend_refused_while_pending`
  — `drop("archive")` on a fresh copy (status `"pending"`) raises, proving position beats status
    (this is the exact gap fact #3 names, and the regression test for it).
- `tests/test_checklist_engine.py::TestAmendBookends::test_drop_opening_bookend_refused_while_pending`
  — same for `drop("init")` before `init` is ever started, proving the opening bookend is frozen
    *unconditionally*, not merely "once started" (a strictly stronger claim than fact #3's
    as-observed baseline, and worth a test precisely because it wasn't true before this patch).
- `tests/test_checklist_engine.py::TestAmendBookends::test_rescope_closing_bookend_refused`
  — `rescope("archive", {"title": "..."})` raises.
- `tests/test_checklist_engine.py::TestAmendBookends::test_retext_check_on_closing_bookend_still_allowed`
  — documents attack 4 as intentional: `retext-check` on `archive`'s `c2b` command succeeds; this
    test exists so a future patch that "fixes" this does so on purpose, not by accident.
- `tests/test_checklist_engine.py::TestAmendBookends::test_middle_gate_add_drop_rescope_unaffected`
  — all three ops against a genuinely mid-checklist pending gate (e.g. `reconcile`) behave exactly
    as at `9b38b9d9` — the middle is provably untouched by this patch.
- `tests/test_checklist_engine.py::TestAmendBookends::test_survey_amend_unaffected`
  — a `SURVEY`-type checklist's `retext-check`-only amend path (`:3013`–`:3029`) is unchanged;
    bookend logic never runs for `type == SURVEY` since `add`/`drop`/`rescope` are already refused
    there before reaching my new checks.
- **Backward-compat test (the one that proves attack 1's cost, not hides it):**
  `tests/test_checklist_engine.py::TestAmendBookends::test_backcompat_gap_drop_archive_now_refused`
  — load a `COMMANDER_SPINE`-shaped `cl` with `archive` pending and no `amendments` key at all
  (i.e., the exact shape of every spine in flight today); assert `drop("archive")` now raises. This
  test is written to **fail** against `9b38b9d9` and **pass** against my patch — it is the
  documented, checked-in proof that behavior changed for an undeclared plan, not a hidden
  regression. I'd land it with a comment pointing at this section rather than silently.
- `tests/test_checklist_engine.py::TestAmendBookends::test_implementer_plan_m1_rescope_now_refused`
  — the crew-cost finding (§5 attack 3) as a test: `rescope("m1", {...})` on a fresh
  `IMPLEMENTER_PLAN`-shaped `cl` (`["m0-context", "m1"]`) now raises, where it succeeded before.
  Checked in for the same reason as the previous test — the cost is real and should be visible in
  CI, not just in prose.

## 7. What you are NOT claiming

- I did not run any of the tests above; they're named, not written or executed, per the brief's
  "do not run the full test suite" and the general instruction to write no code.
- I did not check whether any *other* skill (beyond commander/admiral/explorer/implementer) ships
  a `type: gated` spine or plan that this would also affect — I read exactly the four artifacts the
  brief named (fact #5) and nothing wider.
- I did not check `scripts/mcp_spine_server.py` end-to-end for every other tool that might also
  read `cl["items"]` positionally and could be affected by a `drop`/`rescope` refusal changing
  which ids are reachable (e.g. `spine_status`'s rendering) — I only traced the one path
  (`spine_amend` → `run_engine("amend", ...)` → `_tool_error`/`as_result`) needed to answer "what
  changes at the MCP door."
- I did not attempt to drive `amend` against a live copy to observe the refusal message in
  practice (the rules permit copying a spine to a temp dir and trying it; I chose to reason from
  the source and the one live spine I read read-only, rather than spend the run's budget
  exercising a runtime I'm not allowed to write code to reach here).
- I am not claiming attack 1 (the backward-compatibility conflict) is unique to my candidate — I
  have not read the other design candidates and was told not to hedge toward them — but I am
  confident it is *forced* by the specific combination of "no new state" and "undeclared plans
  behave exactly as before," independent of what shape any other candidate's mechanism takes.
- I did not design what the human-facing skill doctrine (commander/admiral/explorer references)
  should say about *when* to use a top-level amend versus a child checklist — §4's Commander/Admiral
  split is an engine-capability answer, not a doctrine recommendation for which pattern a role
  *should* prefer.

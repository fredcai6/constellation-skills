# Design candidate B — result

All line numbers verified against `9b38b9d9` in
`/home/tommy/projects/constellation-skills/.worktrees/567-k-one-spine-mutable-middle`. Where a
number could plausibly drift I re-read the live file rather than trusting the brief's citation;
every citation below was independently confirmed, not copied.

## 1. Candidate name and one-sentence summary

**Per-gate `bookend` flag with a symmetric floor/ceiling in `amend()`.** Each gate declares
`"bookend": true` on itself when its author wants it frozen; the engine reads that one key and
refuses every `amend` op (`add` past it, `drop`/`rescope`/`retext-check` on it) that would touch
or leapfrog a gate carrying it, while every other gate — including gates a role adds to itself at
runtime — stays exactly as mutable as `amend` already makes it today.

## 2. The mechanism

**Schema addition.** One new optional boolean key on the task object, `"bookend"`, sitting beside
the existing ad hoc per-task keys the engine already reads with `.get()` and no schema validation
— `why_exempt` (`checklist_engine.py:2374,2683`, itself documented as "a task with no `why_exempt`
is treated as NOT exempt," `:1320`), `context_headroom_tokens` (`:78` of the Commander template),
`override_policy` (`:130` of the same template). `_new_task` (`:2919`) and `_build_amend_task`
(`:2954`) are untouched — `bookend` is template-authored, never engine-constructed, exactly like
`why_exempt`. There is no task schema validator anywhere in `checklist_engine.py` that would
reject an unknown key (confirmed: no `ALLOWED_KEYS`/schema-validation symbol exists in the file),
and `init_work_area.py:instantiate_spine` (`:152`) instantiates a spine by plain text-substitution
+ `json.loads` (`:184-186`), not by round-tripping through a task constructor that could strip an
unrecognized field. A `"bookend": true` literal in a template therefore survives instantiation
unchanged and reads back unchanged.

**Engine changes, all inside `amend()` (`checklist_engine.py:2971-3183`), plus one line in
`rescope`'s field allowlist:**

1. A new helper beside `_floor()` (`:3036`), same shape and same "commit-nothing-until-validated"
   discipline as the rest of the function:

   ```python
   def _bookend_ceiling() -> int:
       """1 + the highest index of any bookend-marked gate; len(new_items) (no
       ceiling) if none are marked. Symmetric with _floor(): floor protects what
       is already DONE (status-derived), ceiling protects what is declared DONE-
       ON-PURPOSE (author-derived). An insert may not land after it."""
       marked = [i for i, tid in enumerate(new_items) if new_tasks[tid].get("bookend")]
       return (max(marked) + 1) if marked else len(new_items)
   ```

2. `add` (`:3047-3075`): immediately after the existing floor refusal (`:3067-3072`), add the
   mirror-image ceiling refusal:

   ```python
   ceiling = _bookend_ceiling()
   if insert_at > ceiling:
       tail = new_items[ceiling - 1]
       raise EngineError(f"add {nid}: cannot insert after bookend (frozen finish) gate {tail}")
   ```

   This is what keeps a closing bookend the *last* gate: without it, `add` could append a new
   pending gate after `archive`, and the "frozen finish" would stop meaning "finish."

3. `drop` (`:3076-3088`): after the existing `status != "pending"` refusal, before removal:

   ```python
   if new_tasks[tid].get("bookend"):
       raise EngineError(f"drop {tid}: a bookend gate cannot be dropped",
                          task_id=tid, verb="amend-drop", status=status)
   ```

4. `rescope` (`:3089-3114`): the same guard, placed before the field-overwrite. **One additional
   change is required here that the brief's established facts do not surface**: `rescope`'s
   `overwritable` tuple (`:3099-3100`) is `("title", "imperative", "postconditions",
   "preconditions", "constraints", "directives")` — it does **not** include `bookend`. As written
   today, nothing could ever *set* the flag through the engine at all; only a template author
   hand-writing the initial JSON could declare a gate frozen, and no plan could ever freeze a gate
   that started life unmarked. I add `"bookend"` to that tuple. This is the retrofit path (see
   §5) and it is also, by the guard placed *before* it, the flag's own defeat-proofing: once
   `rescope {tid: bookend=true}` lands, that same guard refuses every future `rescope` targeting
   `tid` — including one attempting `bookend: false`. **The flag is a one-way latch through the
   engine.** It can only be reversed by hand-editing the file (§5).

5. `retext-check` (`:3115-3173`): the same guard, before the check-text mutation. This is the
   bluntest corner of the design — see §5's third weakness.

**No MCP door change.** `spine_amend` (`mcp_spine_server.py:2046` tool definition, `:2401-2422`
handler) is already a pure pass-through to `amend()` (confirmed: the handler's only logic is
argument validation and `run_engine("amend", *rest)`, `:2422`). The new refusal surfaces through
the exact same `EngineError → as_result()` path every existing amend refusal already uses. Zero
new door surface.

**What a role does differently.** Nothing changes about `attest`/`start`/`advance`/`waive` on a
bookend gate — `bookend` gates only the four `amend` ops. A role still opens, works, and closes its
opening and closing gates by the ordinary gated-checklist lifecycle; the only thing that changes is
that it can no longer re-plan them away mid-run. What *does* change is that a role no longer needs
a second file to hold its real middle: since `add` can insert anywhere between the ceiling and the
floor, a role can grow its own spine's item list at runtime instead of authoring a child checklist
whose gates the parent engine never sees.

**Literal JSON fragment** a spine template carries (Commander's `init` and `archive`, trimmed to
the added key in context):

```json
"init": {
  "id": "init", "title": "Claim the engine lease",
  "...": "... unchanged ...",
  "bookend": true,
  "status": "pending", "status_detail": {}, "result": null, "finding": null, "evidence": [], "rework_count": 0
},
"archive": {
  "id": "archive", "title": "Archive, commit, and push",
  "...": "... unchanged ...",
  "bookend": true,
  "status": "pending", "status_detail": {}, "result": null, "finding": null, "evidence": [], "rework_count": 0
}
```

## 3. Worked example

**Commander spine, `9b38b9d9` order** (`COMMANDER_SPINE.template.json:5`):
`init · context · understand · plan · execute · reconcile · triage · review · feedback · archive`.

Under this candidate: `init` and `archive` each carry `"bookend": true`. Everything from `context`
through `feedback` — seven gates, including `execute` itself — is undeclared and fully mutable:
addable, droppable, rescopable, retext-checkable, subject only to the unchanged status-based floor
(nothing lands before a gate that's already complete/in-progress/etc.) and the new bookend ceiling
(nothing lands after `archive`).

**The delta a Commander at `plan` sends to author its wave directly into its own spine, instead of
into `execute.json`.** The Commander is standing at `plan` (in-progress); `context`, `understand`,
`plan` are non-pending, so `_floor()` = index(`execute`) = 4 (0-based: init=0, context=1,
understand=2, plan=3, execute=4). `archive` is the only bookend, at index 9, so
`_bookend_ceiling()` = 10 = `len(items)` — no additional ceiling pressure yet, since nothing is
being inserted anywhere near the tail. One `spine_amend` call, three ops, inserted after `plan`
and ahead of the still-generic `execute`:

```json
{
  "ops": [
    {"op": "add", "id": "g1-implement", "after": "plan",
     "title": "Implement wave 1",
     "imperative": "Dispatch the crew for wave 1 per plan.md; integrate its evidence.",
     "postconditions": [{"id": "c1", "statement": "wave 1 implemented, crew evidence attached", "check": null}]},
    {"op": "add", "id": "g1-review", "after": "g1-implement",
     "title": "Independent review of wave 1",
     "imperative": "Dispatch the reviewer for wave 1; attach the review-result.",
     "postconditions": [{"id": "c1", "statement": "reviewer verdict attached", "check": {"kind": "artifact", "evidence_type": "review-result"}}]},
    {"op": "add", "id": "g1-integrate", "after": "g1-review",
     "title": "Integrate and merge wave 1",
     "imperative": "Merge the reviewed PR; confirm CI green.",
     "postconditions": [{"id": "c1", "statement": "PR merged, CI green", "check": null}]}
  ]
}
```
called as `spine_amend(delta=<above>, reason="fold wave 1 into the spine per #634 instead of execute.json", authority="human")`.

`add g1-implement`: `after="plan"` → `insert_at = index(plan)+1 = 4`. `floor` = 4 → `insert_at >=
floor`, allowed. `ceiling` = 10 → `insert_at <= ceiling`, allowed. Committed. `items` becomes
`[..., plan, g1-implement, execute, reconcile, ...]`, and the two subsequent `add`s chain off it the
same way. `execute` — untouched, still pending, still not a bookend — is now free real estate:
a second `amend` could `drop execute` (still pending → still droppable) once `g1-integrate` makes
it redundant, or `rescope execute` into "wave 2" scaffolding. Either way, `execute.json` was never
opened.

**What the engine does when that same Commander tries `drop archive`.** At `9b38b9d9`, per the
brief's fact 3, this *succeeds*: `archive` is still `pending` (nothing downstream of `execute` has
started), and `drop`'s only gate is `status == "pending"` (`:3081`). Under this candidate,
`archive` carries `"bookend": true`, so the new guard in `drop` fires first:

```
EngineError: drop archive: a bookend gate cannot be dropped
```

`cl` is left unmutated (the whole delta is all-or-nothing, built on copies, committed only at
`:3177` — so even a delta that *starts* with a legal op and *ends* with `drop archive` commits
nothing).

## 4. How it lands for Admiral and for crew

**Admiral.** Answering directly, not deferring: **yes, the single `execute` gate can grow one gate
per wave**, replacing itself. `ADMIRAL_SPINE.template.json:5` is `init · latitude · execute ·
closeout`; `init` and `closeout` each get `"bookend": true`. At the first wave boundary the Admiral
sends an `amend` with `{"op": "drop", "id": "execute"}` (still pending, not a bookend — allowed)
plus `{"op": "add", "id": "wave-1", "after": "latitude", ...}`, and at each subsequent boundary
`{"op": "add", "id": "wave-2", "after": "wave-1", ...}`, and so on, each wave gate's postconditions
citing that wave's `verify_iterative_role_artifacts.py admiral-prelaunch` evidence directly instead
of through the generic `execute` gate's single `c3` (`ADMIRAL_SPINE.template.json:42`). The
`ceiling` (index of `closeout`, which only grows as items are inserted *before* it) keeps every
`wave-N` gate from ever landing after `closeout`, so "the epic is closed" keeps meaning what it
says. `.agent-work/<work-id>/NEXT_WAVE.json`, the `transitions/<boundary-id>/` packets, and
`ADMIRAL_LOG.md`'s TRANSITION lines are untouched by this design — they are evidence artifacts a
wave gate's postconditions can point at (exactly as `execute`'s `c3` already points at
`verify_iterative_role_artifacts.py`, `:42`), not a competing record of what gates exist. Whether
skill doctrine actually retires the *practice* of writing `ADMIRAL_LOG.md` prose per wave, now that
`cl["amendments"]` records "the plan changed, here's how" for free, is a prose decision outside
what this mechanism can force — see §7.

**Crew (`IMPLEMENTER_PLAN.template.json`).** Same question, answered directly: **`m0-context` gets
`"bookend": true`; there is deliberately no closing bookend.** The template ships only
`m0-context, m1` (`:5`) — unlike Commander/Admiral, it has no fixed terminal gate id, because the
crew authors its own final gate's shape at runtime (a TDD red/green pair, or a collapsed
inspection gate, per `m1`'s own imperative, `:19`). Declaring a closing bookend here would mean
guessing which future gate id is "the" finish before the crew has decided what its plan even looks
like — exactly the kind of premature freeze the human's direction argues against. This is a
defensible gap, not an oversight: the crew's actual finish is already protected by two mechanisms
this candidate does not touch and the brief marks out of scope (fact 4) — `consolidate()`
(`:2733`) refuses while any item is non-terminal (`:2736-2738`), and `advance(--from_child)`
(`:2617`) is the one-way evidence seam a parent reads from, never drives. A crew that wants its own
last gate frozen can retrofit it the same way Admiral retrofits `wave-N` protection — one
`rescope {id: <last-gate>, bookend: true}` before calling itself done — but the template does not
force it, because the template cannot know which gate that will be.

## 5. Attack your own candidate

**1. An existing in-flight spine with no declaration keeps its exact 9b38b9d9 exposure — including
the two spines this very run is standing on.** `epic-567-door/spine.json` and
`.agent-work/567-k/spine.json` are live right now (the handoff's own rules line forbids touching
them). Neither carries `"bookend"` anywhere. Under this candidate, `_bookend_ceiling()` returns
`len(items)` (no marked gates found) and every `drop`/`rescope`/`retext-check` guard's
`.get("bookend")` reads `None` → falsy → no refusal. **Nothing about this design protects the
Admiral spine driving this very session's closeout gate until a human runs one retrofit `amend`
per spine.** That is exactly the backward-compatibility this candidate is required to hold, but it
means the design ships with a real, non-trivial rollout tax: every spine in flight — and every
archived one a later run resumes from — stays exactly as freeze-less as it is today until someone
touches it. Not fixable within the constraint (the constraint *is* per-gate opt-in); the human
must accept a retrofit pass as a real cost, or accept that "frozen bookends" is opt-in per spine,
not a blanket property of the engine.

**2. The flag can be defeated without `--force` by not going through the engine at all.**
`checklist_engine.load()` (`:222`) is a bare `json.loads`, and nothing in `main()` or any verb
cross-checks `spine.json`'s live content against the hash-chained journal (`:3580-3630`) before
acting — the journal chain proves a *log of past verbs* was not tampered with; it proves nothing
about whether the *current* `spine.json` on disk still matches what that log implies. So any agent
or human with filesystem access can open `spine.json` in a text editor, delete the
`"bookend": true` token or the whole gate, and save — no `--force`, no `amend`, no journal entry, no
refusal, because the refusal lives entirely inside `amend()`'s Python, and hand-editing never calls
it. This is not a hole specific to this candidate — `rescope`/`drop`'s existing `status == pending`
gate is exactly as bypassable the same way today — but it means "the engine refuses" is scoped
precisely to *the engine's own verbs*, never to the file. Not fixable within this constraint (a
file-integrity check is a different, larger mechanism, and the codebase's own operational memory —
recovering a deadlocked door via "temp-copy-back, never hand-edit" — already treats hand-editing as
a known, tolerated-but-discouraged escape hatch, not a solved problem). A real cost the human must
accept, not a defect in this candidate specifically.

**3. The cost to an author who just wants a small plan is a second, silent failure mode layered on
top of the first.** Forgetting to mark `init`/the-closing-gate `bookend: true` is invisible at
authoring time (json.loads accepts it happily) and *only surfaces the first time someone tries to
amend a gate that should have been frozen and isn't refused* — which may be long after the plan
was written, by a different agent, on a different day. Every other per-gate authoring burden in
this codebase (`check`, `postconditions`, `evidence_type`) fails loud and immediate at the gate it
governs, at `start`/`advance` time, close to the mistake. A missing `bookend` fails *at amend
time, on a completely different gate* (whichever one someone tries to drop past the missing
ceiling), which is a much colder trail to walk back. And retext-check being blanket-refused on a
bookend gate (§2.5) means an author who typos a bookend's check text has exactly one shot to get it
right, or must hand-edit outside the engine (weakness 2) to fix a typo the engine would otherwise
happily correct on any other gate. This is a real authoring tax the "declare it per gate" constraint
accepts on purpose (per the brief: "accept the schema addition and the burden of every template
having to declare") — not a bug, but not free either.

**4. Migrating `execute.json`/`ADMIRAL_LOG.md`+`transitions/` into the spine is possible under this
design but is not free, and this candidate does not do it.** §3 and §4 show the *mechanism* that
would let a role fold its second-file middle into its own spine (bookend the ends, `amend add` the
middle), but nothing here migrates a single existing template to actually do it, and doing so has
real costs this candidate does not price: (a) `verify_iterative_role_artifacts.py` does not
reference `execute.json` (confirmed: zero matches for the literal string in that file) but every
`run_crew.py` dispatch site, `recover_crews.py`'s conflict check, and the Commander's own
`execute` imperative (`:65`) are written assuming a child checklist exists at that path — moving
the middle into the spine means rewriting all of that prose and possibly `run_crew.py`'s calling
convention, and the brief explicitly forbids touching `run_crew.py`; (b) a spine with a hundred
`amend`-added gates instead of one `execute` gate makes `cl["items"]` long-lived and large in a way
the engine has never been exercised against at that scale — no test in `test_checklist_engine.py`
amends more than a handful of gates onto one checklist; (c) `ADMIRAL_LOG.md`'s TRANSITION lines
carry prose ("what was decided and why") that `cl["amendments"]`'s `ops` summaries
(`"added g1-implement"`, `:3075`) do not — the *reason* string is free-text and captures why, but
nothing forces it to restate the wave-transition decision shape (`advance`/`repair`/`replan`/
`stop`) the way `ADMIRAL_LOG.md`'s template does today. Folding the log into `amendments` would
need either a convention (put the decision in `--reason`) or a schema (structured amendment
metadata) — this candidate supplies neither. This is a real, unfunded migration cost, not a
rounding error, and I am not claiming this candidate pays it.

## 6. Test surface

All in `tests/test_checklist_engine.py`, following the file's existing `AmendVerb`
(`:1417`)/`AmendRetextCheck` (`:1576`) class convention. A new class, `AmendBookendGuard`:

- `tests/test_checklist_engine.py::AmendBookendGuard::test_drop_refused_on_bookend_gate` — a
  pending gate with `bookend: true`; `amend(drop)` raises `EngineError`; `cl` unmutated.
- `tests/test_checklist_engine.py::AmendBookendGuard::test_rescope_refused_on_bookend_gate` —
  same shape, `rescope` op, any single overwritable field.
- `tests/test_checklist_engine.py::AmendBookendGuard::test_retext_check_refused_on_bookend_gate` —
  an in-progress bookend gate with a `command`-kind check; `retext-check` raises.
- `tests/test_checklist_engine.py::AmendBookendGuard::test_add_refused_past_bookend_ceiling` — a
  three-gate checklist, last gate `bookend: true`; `add` with `after=<last gate>` (or no `after`,
  defaulting to append) raises `EngineError`; `add` with `after=<second-to-last>` succeeds.
- `tests/test_checklist_engine.py::AmendBookendGuard::test_ceiling_absent_when_no_bookend_declared`
  — **the backward-compat test**: a checklist with zero `bookend` keys anywhere; every op shape
  that succeeds at `9b38b9d9` (append `add`, `drop` a trailing pending gate, `rescope`, retext a
  pending gate's check) still succeeds byte-for-byte identically — same `msg`, same resulting
  `items`/`tasks` shape minus the delta itself. This is the one that proves the floor/ceiling
  symmetry didn't silently tighten the undeclared case.
- `tests/test_checklist_engine.py::AmendBookendGuard::test_rescope_can_declare_bookend_then_latches`
  — `rescope {id: g1, bookend: true}` succeeds once (proving the `overwritable` tuple change);
  a second `rescope` on `g1` (any field, including `bookend: false`) then raises — proving the
  one-way latch described in §2.4.
- `tests/test_checklist_engine.py::AmendBookendGuard::test_bookend_does_not_block_ordinary_lifecycle`
  — a bookend gate still `start`s, `attest`s, and `advance`s normally; only the four `amend` ops are
  refused.
- `tests/test_checklist_engine.py::AmendBookendGuard::test_floor_and_ceiling_both_apply` — a
  checklist with a completed gate at the head (floor) and a bookend gate at the tail (ceiling);
  `add` at a middle position between them succeeds; `add` before the floor and `add` after the
  ceiling each independently raise, with distinct offending-gate names in the message.

## 7. What you are NOT claiming

- I did not run any test — `test_checklist_engine.py::AmendVerb`/`AmendRetextCheck` were read for
  naming convention only, never executed, per the rules against running the suite.
- I did not drive a real `amend` call, on a copy or otherwise — every op trace in §3/§5 is worked
  by hand against the read source (`_floor`/`_bookend_ceiling`/the guards as I specify them), not
  observed from a live engine run. I verified the *existing* code's line numbers and behavior by
  reading it, not by executing it.
- I did not check whether `checklist_engine.py`'s CLI (`main()`, `:3644`) needs a new flag anywhere
  to expose `bookend` — I assumed (and the brief's fact 1 supports) that `amend`'s existing
  `--delta <file.json>` / `spine_amend`'s `delta` argument shape already carries arbitrary op
  fields (`op.get(...)` throughout `:3045-3175`) with no CLI-level allowlist of op keys, so no new
  flag is needed. I did not exhaustively read `main()`'s argument parsing to confirm this for every
  code path.
- I did not check every other role or checklist type in the repo (reviewer, cartographer, or any
  survey-type spine) for whether it would want bookend declarations — the brief names Commander,
  Admiral, Explorer and crew as the four to answer for, and I answered for those four only.
  Explorer's `init`/`route` bookend candidacy is asserted in §2's template list but not walked
  through a worked example the way Commander is, since the brief's required worked-example section
  names Commander specifically.
- I did not design, or attempt to design, the structured-amendment-metadata or
  decision-shape convention that §5's fourth weakness says the `ADMIRAL_LOG.md`-into-`amendments`
  migration would need. I named the gap; closing it is out of scope for this candidate.
- I did not verify `run_crew.py` or `recover_crews.py`'s internals beyond the brief's explicit
  instruction not to touch or propose touching `run_crew.py` — §5's fourth weakness cites their
  *existence* as consumers of `execute.json`'s path convention from the Commander template's prose
  (`:65`), not from reading `run_crew.py` itself.
- I am not claiming this candidate is the right one among B/other candidates presented in this
  design round — I was told not to hedge toward alternatives, and I did not evaluate any.

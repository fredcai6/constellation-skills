# Candidate A — `minimal-interface`

Design-it-twice panel, epic #567 lane A. Filled against
`DESIGN_IT_TWICE_BRIEF.md`. All line numbers are measured in this worktree
(`/home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity`).

## 1. Candidate name and my one named constraint

**Candidate A — `minimal-interface`.** The smallest possible addition to the
door's tool surface: **one** new tool whose entire job is to bind this door to a
spine file that already exists. Nothing else about the door changes shape. The 9
engine pass-through tools are untouched, `_identity_violation` is untouched,
`_bind_process_to` is untouched, and no tool other than the new one gains an
argument.

---

## 2. The design

### 2.1 The name: `spine_bind`

One name for one thing, and it must not collide with `spine_open`, which mints.

- **`spine_bind` — chosen.** "Bind" is already this module's own word for exactly
  this act, and it is the door's word, not a borrowed one:
  `_bind_process_to` (`mcp_spine_server.py:878`), `_unbound_refusal` (`:393`),
  `_HOW_TO_BIND` (`:383`), `BINDS_WITHOUT_A_BOUND_SPINE` (`:1425`), and the
  refusal text "no spine is bound to this door" (`:423`). The tool name becomes
  the literal answer to the refusal a caller is holding: the door says nothing is
  bound, and the tool is called bind. No new vocabulary enters the system.
- **`spine_open` is unharmed.** Its own description says it "Acts on a spine that
  does not exist yet" (`:1376-1377`); `spine_bind` acts only on a spine that
  already does. Open mints, bind binds. Neither verb reads as the other, and
  neither can be confused for the other by a model reading the two descriptions
  side by side.
- **`spine_attach` — rejected.** `attach` is an engine verb, already surfaced as
  `spine_evidence action: "attach"` (`:1214`, `:1526-1536`). Two meanings for one
  word on one surface.
- **`spine_resume` — rejected**, same defect: `resume` is an engine verb, surfaced
  as `spine_halt action: "resume"` (`:1271`).
- **`spine_adopt` — rejected.** "Adoption" already has a settled and unrelated
  meaning in this repo: `tests/test_mcp_adoption.py` is about the *corpus*
  adopting the door as its default path. Reusing the word would make
  "adoption test" ambiguous in the one place it is already load-bearing.

### 2.2 The tool schema

Added to `LIFECYCLE_TOOLS` (`:1368-1411`), between `spine_open` and
`spine_close`:

```python
{
    "name": "spine_bind",
    "description": (
        "Bind this door to a spine that ALREADY EXISTS, so this process can "
        "drive it with the other tools. Acts on a spine `spine_open` (or the "
        "CLI) already created -- it creates nothing and mints nothing. The "
        "session identity is NOT an argument: it is derived from the spine's "
        "own recorded origin, so binding a spine yields exactly the identity "
        "that spine was opened under. Refused for a spine outside this door's "
        "own checkout, and refused while this door still holds an active lease "
        "on a different spine (release it first). Binding the spine this door "
        "is already bound to is a no-op that succeeds."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "spine_file": {
                "type": "string",
                "description": (
                    "path to the existing spine file -- the SPINE_FILE value "
                    "`spine_open` returned. Must resolve inside this door's own "
                    "checkout."
                ),
            },
        },
        "required": ["spine_file"],
        "additionalProperties": False,
    },
},
```

**Exactly one argument, of type `string`.** No `session`. No `force`. No
`work_id`. Each omission is argued in §2.6 and §2.4.

The argument is named `spine_file`, not `path` or `plan_file`, because it is the
same key `open_work` returns (`spine_lifecycle.py:356`) and the same environment
variable the door reads at launch (`mcp_spine_server.py:176`) — a caller pastes
back the string it was handed. It is also deliberately the *honest* name: see
§2.9, where naming it anything else would be the spelling-evasion this repo's
identity guards have been defeated by six times (`:456-463`).

### 2.3 Where the dispatch goes, and what the `:137` pin implies

**`spine_bind` belongs in `call_lifecycle_tool` (`:1067`), as a third route.**
It is lifecycle-shaped by every property that put `spine_open`/`spine_close`
there: it never calls `run_engine`, it answers through `_lifecycle_result`
(`:960`), and it is not an engine pass-through. Putting it on a fourth
module-level dispatch function would be a second sibling for one tool, and
`main()`'s `tools/call` branch would then need a third routing set beside
`LIFECYCLE_TOOL_NAMES` (`:1412`) — more surface, not less, which fails my own
constraint.

`tests/test_mcp_lifecycle.py:137` pins every `return` in `call_lifecycle_tool` to
a call of a name in `ALLOWED = {"_spine_open", "_spine_close"}` (`:135`). Read
what that pin actually forbids: its own failure message (`:150-153`) says *"Route
new lifecycle logic through its own top-level dispatch function instead of adding
a third way for call_lifecycle_tool itself to answer."* The banned thing is a
**shape** — a mutate-then-return, an inlined dict, a read from somewhere the
dispatch functions never touch — not a **count**. Its positive control (`:156-180`)
plants exactly that shape and must keep failing.

So the pin implies a precise, two-line obligation, and it is the pin being obeyed
rather than weakened:

1. `tests/test_mcp_lifecycle.py:135` — `ALLOWED` becomes
   `{"_spine_open", "_spine_close", "_spine_bind"}`.
2. `call_lifecycle_tool` gains `if name == "spine_bind": return _spine_bind(args)`
   before the `raise KeyError(name)` at `:1097`.

The positive control at `:156-180` is untouched and still red on a
mutate-then-return, because it constructs its own leaky source and checks it
against the same `ALLOWED` set. That is the test for whether this edit weakened
anything: if it had, the control would go green.

The AST pin on `_spine_open`'s identifiers (`tests/test_mcp_lifecycle.py:194-206`)
does **not** reach `_spine_bind`: `_find_funcdef(tree, "_spine_open")` (`:66-67`)
resolves one `ast.FunctionDef` by exact name. That the ban is deliberately
function-scoped rather than a module sweep is itself pinned, by
`test_spine_close_is_not_held_to_the_same_ban` (`:225-234`). So `_spine_bind`
may read `SPINE`/`SESSION`, and it must — for the containment root (§2.4), for
the idempotency short-circuit (§2.7) and for its own success payload.

**One further routing fact, which an implementer will otherwise discover the hard
way.** `main()` refuses the whole tool surface when nothing is bound, at
`:1723`:

```python
unbound = None if nm in BINDS_WITHOUT_A_BOUND_SPINE else _unbound_refusal()
```

`BINDS_WITHOUT_A_BOUND_SPINE` is `{"spine_open"}` (`:1425`). Without adding
`"spine_bind"` to it, the new tool is refused by the uniform gate before
`call_lifecycle_tool` is ever reached — a bind tool that only works on an
already-bound door, which is the inverse of its purpose. The set's own comment
(`:1417-1425`) says "Exactly one name, and it is a SET rather than an `!=` so the
exemption is a listed fact a reader can find"; that decision pays off here, and
the comment's count and prose update to two.

### 2.4 The containment root — the first crux

**Unbound (no prior binding):** the root is
`_primary_checkout_for_lifecycle()` (`:797-861`). With `SPINE is None` it anchors
on `Path(__file__).resolve().parent` (`:857`) and resolves
`git rev-parse --git-common-dir`'s parent (`:858-861`) — **the primary checkout of
the repository this door's own script lives in.**

Why that root, and not a wider or narrower one:

- **It is the only root an unbound door can derive at all.** There is no
  `SPINE.parent` to confine against; that is the whole difficulty. The three
  other candidate anchors are each disqualified: the process cwd is the exact
  fail-open `_spine_from_env` was rewritten to end (`:161-169` — `Path("").resolve()`
  silently bound the door to whatever directory it stood in), and it now *moves*
  mid-call (`_standing_in_the_bound_spines_worktree`, `:573`); a new environment
  variable is barred by hard constraint 7 and by this module's own repeated
  refusal to add a fourth ambient input (`:832`); and a caller-supplied root is
  just the unconfined case wearing a parameter.
- **It is not a new derivation.** It is the same expression `_spine_open` already
  calls at `:1012` to decide where worktrees may be created. So "the set of
  spines this door may bind" is exactly "the set of spines a door in this repo
  could have opened" — one root answering two questions, in the style
  `_resolve_confined`'s docstring insists on (`:354-360`: reuse the one predicate
  with a different `bound_dir`, "not a second, differently-shaped check").
- **Not wider.** Unconfined means any readable JSON file on the disk becomes a
  candidate spine, which is `_identity_violation`'s `--from-child` hazard
  (`:481-505`) re-created one level up and worse: `from_child` can only feed
  evidence into the bound spine, whereas an unconfined bind makes an arbitrary
  file *be* the bound spine.
- **Not narrower.** The obvious narrowing is `<primary>/.worktrees` — the
  `_default_wt_root` (`spine_lifecycle.py:173-177`) that holds every spine
  `spine_open` mints. It is wrong, because real driving spines also live in the
  primary checkout's own `.agent-work/`: `_active_engine_session_spine`
  (`spine_lifecycle.py:180-209`) scans `root/.agent-work/<work_id>/` and its
  docstring records that "this epic's own driving spine is `execute.json`, not
  `spine.json`" (`:191`). A `.worktrees`-only root would refuse the primary
  checkout's own work, which is a case that actually happens.
- **A filename rule is deliberately not part of the boundary.** Requiring
  `spine.json` would be a second definition of "what is a spine", and the same
  `_active_engine_session_spine` comment already proves it false. Structure, not
  filename — the check is §2.5's, not a name match.

**Bound (a rebind):** **the same expression, `_primary_checkout_for_lifecycle()`,
unchanged.** When `SPINE is not None` it anchors on `SPINE.parent` (`:857`) and
`--git-common-dir` resolves to the primary checkout from *any* worktree, linked or
not (`:842-849`). So the boundary is invariant in words — "inside this door's own
checkout" — while the anchor moves from the script to the work. Two consequences,
both intended:

- It is emphatically **not `SPINE.parent`**. `SPINE.parent` is the currently bound
  spine's own directory; binding a sibling spine in a different worktree is the
  entire point of the tool, and `SPINE.parent` would permit only a spine in the
  same folder. This is the same reason `spine_open` passes `wt_root` rather than
  `SPINE.parent` to `_resolve_confined` (`:1019-1023`, and the docstring at
  `:354-358`: "`SPINE.parent` is the CURRENTLY bound spine's directory, an
  unrelated boundary").
- Once there IS work, containment follows the **work**, not the **code**. If the
  bound spine lives in a different repository than the script — which is not
  hypothetical, `tests/test_mcp_lifecycle.py::FullStdioRoundTripTests` does
  exactly that (`:818-823`) — a bound door may bind within the bound spine's
  repo and not within the script's. That is the correct direction: the door
  follows the tree it is driving.

The predicate is `_resolve_confined` (`:322-380`) with
`join_relative_to=None, bound_dir=<root>` — the same call shape `_spine_open`
uses at `:1020-1023`. `join_relative_to=None` because a relative `spine_file`
must resolve the way Python itself would, and because this door's cwd is a thing
that moves (`:341-350`); an implementer should pass absolute paths and the schema
description says so.

### 2.5 The complete refusal set

In dispatch order. Every message is `REFUSED: <what is wrong> -- <what to do>`,
the voice of `_unbound_refusal` (`:422-440`), `_identity_violation` (`:518-569`)
and `_rebind_refusal` (`:952-957`): name the problem, then name the remedy. Each
returns through `_tool_error` (`:731`) with a `rejection_class`, so every one of
them lands in the rejection log (`:695-728`).

**R1 — the argument is absent.** Via `_require` (`:1428`), mirroring `:990-994`:

> `spine_bind: missing required argument(s): spine_file`

`rejection_class="missing-required-argument"`.

**R2 — the argument is not a usable string** (not a `str`, or empty/whitespace),
mirroring the `spec` type check at `:997-1001`:

> `spine_bind: spine_file must be a non-empty path to an existing spine file`

`rejection_class="bad-argument-type"`.

**R3 — the containment root cannot be resolved** (`_primary_checkout_for_lifecycle`
raises `OSError`/`RuntimeError`: no `git` on PATH, a door outside any checkout and
unbound), mirroring `:1013-1017`:

> `spine_bind: could not resolve the checkout this door may bind within: <exc>`

`rejection_class="root-resolution-failed"`. Same catch tuple as `_spine_open`, so
this fails as a refusal rather than as a dead server.

**R4 — the path escapes the root.**

> `REFUSED: this door may only bind a spine inside its own checkout ('<root>'); spine_file resolves to '<candidate>', which is outside. A spine in another checkout belongs to work whose worktrees, hooks and tests this door knows nothing about, and binding it would make this process the driver of a run it cannot see. Name a spine under that checkout, or use the CLI, which is per-call by construction.`

`rejection_class="path-escape"`. The closing clause is lifted verbatim from the
existing containment refusals (`:522`, `:544`) so a caller meets one consistent
escape hatch.

**R5 — nothing usable at that path.** The five-input ladder is *not* rewritten
here; §2.8 extracts it from `_unbound_refusal` (`:426-436`) into
`_unusable_spine_reason(path) -> str | None` and both callers use it, so the
`why` clauses are byte-identical to the ones the door already emits ("that path
is a directory, not a spine file", "no file exists at that path", "that file
cannot be read (`PermissionError`)"):

> `REFUSED: spine_bind was given '<path>', but <why> -- so there is no spine there to bind. Name a spine file that exists, or call `spine_open` to mint one.`

`rejection_class="no-spine-there"`.

**R6 — it is not a spine.** The candidate does not parse as JSON, or parses to
something that is not an object. Same read `_rebind_refusal` already does at
`:946`, same catch `(OSError, ValueError)`:

> `REFUSED: '<path>' does not hold a JSON object, so it is not a spine this door could drive. Name the SPINE_FILE `spine_open` returned, or call `spine_open` to mint one.`

`rejection_class="not-a-spine"`.

**R7 — no derivable identity** (`origin.work_id` absent or empty; see §2.6):

> `REFUSED: '<path>' carries no `origin.work_id`, so this door cannot derive the session identity that spine was opened under -- and a door bound with no session cannot claim (`checklist_engine.claim` refuses an empty --session-id). Every spine `spine_open` mints carries one; a hand-written or pre-lifecycle checklist does not. Drive that one through the CLI, which takes --session-id per call.`

`rejection_class="no-derivable-identity"`. The parenthetical is the real engine
refusal at `checklist_engine.py:1022`, and this refusal exists because of the
lesson `_bind_process_to`'s docstring records at `:884-889`: "A door that cannot
`claim` is not bound, so 'bound' here means both."

**R8 — the identity this bind would assume is live somewhere else.** The
candidate spine carries an active, non-stale lease whose `session_id` equals the
session this bind would derive:

> `REFUSED: '<path>' is under an active lease held as '<session>', and that is the very identity this bind would take (it is derived from the spine's own `origin.work_id`). Two processes under one session id are indistinguishable to the engine, so this bind would put two agents on one lease. Whoever holds it must release it first (`spine_lease` with action 'release'), or its lease must go stale.`

`rejection_class="identity-held"`. This is the clause that answers
`IDENTITY_TRADE.md` §3 Option A's named failure — *"a subagent naming its
parent's spine — which is the actual failure. Two agents on one lease is what
engine session leases exist to prevent"* — rather than inheriting it. It reuses
`checklist_engine._active_lease` (`:952-958`), `checklist_engine.load_config`
(`:258-273`) and `checklist_engine._is_stale` (`:934-949`); no new notion of
"live" is defined here, for the same reason `_rebind_refusal` reuses
`_active_lease` (`:939-941`). Staleness is what preserves the legitimate case:
`assignment_session_name`'s docstring (`run_crew.py:199-206`) records that a
respawn *must* reproduce its predecessor's session string, and a genuine respawn
follows a dead predecessor, whose lease is stale.

**R9 — this door still holds a lease of its own.** `_rebind_refusal()`
(`:920-957`), reused, `rejection_class="lease-held"`, mirroring `:1007-1009`. See
§2.7 for the one-word change to its text and why it is asked *after* the
idempotency short-circuit rather than before.

Not a refusal, deliberately: **binding the spine already bound.** That is R0 in
§2.7, and it succeeds.

### 2.6 Where SESSION comes from — the second crux

**Neither an argument nor the recorded lease. It is derived from the spine's own
stamped `origin.work_id`, by the one rule `open_work` already uses to mint
`SPINE_SESSION`.**

`open_work` returns `"SPINE_SESSION": f"constellation/{work_id}"`
(`spine_lifecycle.py:357`), and `build_origin` stamps `work_id` into the spine
itself (`spine_lifecycle.py:108-116`). So for any spine `spine_open` minted, the
session that spine was opened under is **recoverable from the spine**. The rule
is currently an inline f-string inside a return dict; this candidate extracts it
into one named function and calls it from both places:

```python
# scripts/spine_lifecycle.py -- beside branch_name_for (:67) and archive_name_for (:73)
def session_id_for(work_id: str) -> str:
    """The lease identity a spine for `work_id` is driven under:
    `constellation/<work_id>`. The ONE definition -- `open_work` returns it as
    SPINE_SESSION and the door's `spine_bind` recovers it from a spine's stamped
    `origin.work_id`, so adopting a spine yields byte-identical identity to
    having been launched bound to it."""
    return f"constellation/{work_id}"
```

`open_work:357` becomes `"SPINE_SESSION": session_id_for(work_id)`. `_spine_bind`
calls `spine_lifecycle.session_id_for(origin["work_id"])`. Two callers, one
definition; a drift between "the identity a spine is opened under" and "the
identity a spine is bound under" is then not expressible.

Why not the alternatives:

- **Not an argument.** `IDENTITY_TRADE.md` §3 Option B settled this against
  evidence, and it is the shortest entry in the document: *"Option B — require a
  caller-supplied identity. Would have covered: nothing. A subagent cannot prove
  it is not its parent. Any string it can supply, it can supply its parent's.
  Cost: an argument on every call, buying no property."* A `session` argument
  would let a model name any identity, including a live one, and the engine
  matches identity by plain string equality (`run_crew.py:204-205`;
  `checklist_engine.py:992`). Deriving the session instead means **the set of
  identities this door can assume is a function of the spines it may bind**, and
  the spines it may bind are already confined (§2.4). That composition is the
  reason this candidate is not Option B.
- **Not read from the spine's recorded lease.** It fails in both directions.
  Absent when needed: a freshly minted spine has never been claimed, so
  `engine_session` is missing entirely, and `_active_lease` also reads a
  *released* lease as absent (`:952-958`) — so the lease is empty in exactly the
  common case, a parent minting and a child binding before any claim. And wrong
  when present: adopting whatever session id the file happens to record is
  literally taking someone else's name, and against an active lease it slips past
  `require_session`'s ownership refusal (`checklist_engine.py:975-994`) with no
  takeover record, which is what `claim --force --reason` exists to make loud
  (`:1069-1080`).
- **Not `run_crew.assignment_session_name`** (`run_crew.py:198-206`,
  `constellation/<work-id>/<gate>/<role>`). It cannot be derived from a spine at
  all: `gate` and `role` name the *assignment*, which is knowledge only the
  dispatcher has. The launch-time path keeps using it (`_crew_door_env` /
  `crew_env`, `run_crew.py:940-996`) and this candidate does not touch that.
  A door that binds is by definition a door nobody handed an assignment to, so
  it takes the spine-shaped identity, which is the coarser of the two.

**The collision this inherits, stated.** Two processes that bind the same spine
derive the same session string. That property is not introduced here — it is
already true of `open_work`'s own `SPINE_SESSION`, so a door bound by environment
and a door bound by `spine_bind` to the same spine were always going to be the
same identity. R8 is what keeps it from being *silent*: the second binder is
refused while the first is demonstrably live.

### 2.7 Called twice, and the interaction with the lease

**Same `spine_file` twice — idempotent success, and this ordering is the whole
reason it is idempotent.** `_spine_bind` short-circuits *before* asking
`_rebind_refusal`:

```
R0: if Path(spine_file).resolve() == SPINE:  return _lifecycle_result({... "already_bound": True})
```

Ordering matters and is easy to get backwards. `_rebind_refusal` refuses whenever
this process holds an active lease on its current spine — so an agent that binds,
claims, then calls `spine_bind` again with the same path (a retry, a
re-read-your-own-state move, a resumed transcript) would be *refused for
rebinding to where it already is*. That is not idempotent, and it would tell the
caller to release a lease it correctly holds. R0 makes the second call a no-op
that succeeds, changing nothing: no `_bind_process_to` call, no environment
write, no engine contact. Comparison is on `Path(...).resolve()`, matching
`_bind_process_to`'s own `resolve()` (`:914`) so that a relative path, a symlink
or a trailing-slash spelling of the bound spine reads as the same spine.

**A different `spine_file` — a genuine rebind, and `_rebind_refusal` governs it,
unchanged in force.** If this process holds an active lease as `SESSION` on its
current spine, R9 refuses; release first, then bind. If it holds no lease, the
bind succeeds and it is a **move, not an addition**: the previously bound spine
stops being addressable, exactly as
`tests/test_mcp_lifecycle.py:659-666` already pins for the `spine_open` rebind
("the door still answers for TWO spines after a rebind"). `_identity_violation`
follows automatically, because it compares against `SPINE` at call time
(`:517`, `:526`) — the property `IdentityGuardSurvivesARebindTests` (`:617-674`)
already measures, and this candidate adds no second guard to keep in sync.

`_rebind_refusal` needs one parameter, because its text names `spine_open`
(`:956`) and one sentence is open-specific (`:954`, "Opening new work now"):

```python
def _rebind_refusal(acting_tool: str = "spine_open") -> str | None:
    ...
    f"REFUSED: this door still holds an active lease on {str(spine)!r} as "
    f"{SESSION!r}, and one door drives one spine at a time. Rebinding this door now "
    f"would leave that lease held by nobody. Release it first (`spine_lease` with "
    f"action 'release'), then call `{acting_tool}` again."
```

One parameter, one text, both callers — never a second refusal function for the
same question, which is the failure `_identity_violation`'s docstring records six
times over (`:456-463`). "Rebinding this door now" is accurate for `spine_open`
too: its check runs before anything is minted precisely because the *rebind* is
what it is protecting (`:1004-1006`). Blast radius of the wording change,
measured: `grep -rn "still holds an active lease\|Release it first\|Opening new
work now" tests/ scripts/` finds exactly one test assertion,
`tests/test_mcp_door_unbound.py:484`, which asserts the substring
`"still holds an active lease"` — unchanged, so it still passes.

### 2.8 `_bind_process_to`'s AST pin is respected

`_spine_bind` **assigns neither `SPINE` nor `SESSION`.** Its last act on success
is a single call:

```python
_bind_process_to(str(candidate), spine_lifecycle.session_id_for(origin["work_id"]))
```

The module-wide pin (`tests/test_mcp_lifecycle.py:563-576`, via `_assignments_to`
at `:509-546`) asserts the set of scopes assigning `SPINE`/`SESSION` is exactly
`{"<module>", "_bind_process_to"}`, over every assignment form including
`AnnAssign`, `AugAssign`, walrus, `for`, `with` and `except`. `_spine_bind`
contributes no scope to that set. Both roots move in one call, never one — the
requirement `_bind_process_to`'s docstring states at `:884-889` and the reason R7
exists.

`test_the_binder_is_actually_called_from_spine_open` (`:610-614`) is unaffected:
`_spine_open` keeps its own `_bind_process_to(` call at `:1041`.

`_spine_bind` also does not duplicate `_unbound_refusal`'s ladder. The shared
extraction:

```python
def _unusable_spine_reason(spine: Path) -> str | None:
    """Why `spine` is not a readable spine file, or None when it is. The five
    inputs `_unbound_refusal` collapses (:396-419), asked about ANY candidate
    path rather than only the bound one, so `spine_bind` cannot answer the same
    question a second, differently-shaped way."""
    try:
        if spine.is_dir():
            return "that path is a directory, not a spine file"
        if not spine.exists():
            return "no file exists at that path"
        with spine.open("rb") as fh:
            fh.read(1)
    except OSError as exc:
        return f"that file cannot be read ({type(exc).__name__})"
    return None
```

`_unbound_refusal` (`:426-436`) then calls it instead of inlining the ladder,
keeping the one-byte-open decision and its rationale (`:414-419`) in one place.

### 2.9 The pin this candidate must confront head-on

`tests/test_mcp_identity.py:817`,
`test_no_tool_accepts_an_argument_that_could_redirect_the_door`, walks
`module.TOOLS` — which is `TOOLS + LIFECYCLE_TOOLS` (`:1414`), so it sees
lifecycle tools too — and flags any property name containing `"spine"`,
`"session"`, `"engine"`, `"checklist_file"` or `"identity"`
(`IDENTITY_ARG_MARKERS`, `:754`). **`spine_bind.spine_file` fails it.** It is
literally the pin's own positive control: `test_the_pin_can_fail` (`:839-857`)
plants a `spine_file` property and asserts it is caught.

This is not an obstacle to route around; it is the pin working. Its failure
message says so (`:832-837`): *"If the identity trade was deliberately re-opened,
update ... IDENTITY_TRADE.md in the same change -- this test exists so that
cannot happen silently."* So the honest diff is:

1. A **tool-scoped** exemption beside `ADDRESSES_WITHIN_BOUND_SPINE` (`:776`),
   documented in the same style, with the same "delete the runtime clause and
   this entry becomes false" discipline:
   `BINDS_THIS_DOOR = {"spine_bind": ("spine_file",)}`, applied as
   `if prop in BINDS_THIS_DOOR.get(tool["name"], ()): continue`. Scoped to the
   tool, so `spine_advance.spine_file` remains an offender, and the positive
   control at `:839` still fires because it plants the property on
   `module.TOOLS[0]` (`spine_status`), not on `spine_bind`.
2. A new section in
   `.agent-work/archive/2026-08-12-epic-418-followon-closeout/epic-418-followon/commander-f2/IDENTITY_TRADE.md`
   recording that the property in §2 is amended, in the terms of §3 — this is
   not Option A (identity is still not per-call for the 9 pass-throughs) and not
   Option B (the identity is derived, never supplied), but a third thing: a
   confined, one-shot, before-any-verb binding.

**A cheaper-looking dodge exists and must be refused.** Name the argument
`work_file` or `plan_path` and the pin passes untouched. That is exactly the
spelling game `_identity_violation`'s docstring records losing six times
(`:456-463`: "Enumerating spellings is the defect"), applied by the author
against his own test. If this candidate wins, it wins with the argument named
`spine_file` and the trade document amended.

### 2.10 Diff shape

**Added**
- `scripts/mcp_spine_server.py`: `_spine_bind(args)` — one function, ~45 lines
  including the nine refusals; `_unusable_spine_reason(spine)` — extracted from
  `_unbound_refusal`; one entry in `LIFECYCLE_TOOLS`; one route in
  `call_lifecycle_tool`.
- `scripts/spine_lifecycle.py`: `session_id_for(work_id)` — the extracted
  identity rule.
- `tests/`: a `spine_bind` suite (§4) and two pin edits (`ALLOWED` at
  `test_mcp_lifecycle.py:135`, `BINDS_THIS_DOOR` at `test_mcp_identity.py:776`).
- `IDENTITY_TRADE.md`: the amendment section from §2.9.

**Changed**
- `_unbound_refusal` (`:426-436`) delegates its ladder to
  `_unusable_spine_reason`.
- `_rebind_refusal` (`:920`) gains `acting_tool: str = "spine_open"` and one
  reworded sentence.
- `BINDS_WITHOUT_A_BOUND_SPINE` (`:1425`) gains `"spine_bind"`; its comment's
  count and prose update.
- `open_work` (`spine_lifecycle.py:357`) calls `session_id_for`.
- The module docstring: "bound at launch OR at `spine_open`" (`:30-38`) becomes
  "at launch, at `spine_open`, or at `spine_bind`", and — load-bearing prose that
  becomes false and must be rewritten, not left — "Exactly ONE declared tool
  property carries a filesystem path: `spine_advance.from_child`" (`:49-56`)
  becomes two, with the second one's confinement named.

**Deleted** — see §5.

**Nothing else.** `_identity_violation`, `run_engine`, `call_tool`, all 9
pass-through schemas, `_bind_process_to`, `_resolve_confined`,
`_primary_checkout_for_lifecycle` and `_spine_open` are untouched.

---

## 3. The isolation property

"One file per process, decided at launch or at mint" becomes **"one file per
process, decided at launch, at mint, or by one confined binding to a spine inside
this door's own checkout, whose identity the spine itself dictates."** The count
never rises above one, and the moment of decision is the only thing that moves —
which is precisely what `decision:bind-on-open-over-new-verb` already did once
(`:894-899`).

**What an agent can reach now that it could not before, stated plainly:** any
readable JSON object carrying an `origin.work_id`, anywhere inside the primary
checkout of this door's own repository — including a sibling worktree's live
spine — may become the spine this process drives. Before this, an unbound door
could reach nothing at all, and a bound door could reach only what it was
launched with or what it minted. That is a real widening on a security boundary,
and `decision:isolation-not-fencing` requires me to name it rather than let the
tests certify it.

**What still holds it in.** Four things, none of them new machinery: the root
confines *which* spines (§2.4); `origin.work_id` confines *which identities*, so
identity is a function of the spine and never of a model-supplied string (§2.6);
R8 refuses a bind onto an identity that is demonstrably live, which is the "two
agents on one lease" failure `IDENTITY_TRADE.md` §3 names, closed rather than
inherited; and `_rebind_refusal` still forbids orphaning a lease this process
holds. What an agent still cannot do: drive two spines at once, drive a spine in
another checkout, drive a checklist with no stamped origin, name its own
identity, or point any of the 9 pass-through tools anywhere (`_identity_violation`
is untouched and still an equality check against `SPINE`).

**Which side of `IDENTITY_TRADE.md`'s trade this takes.** The **env-binding**
side, unchanged. Identity stays process state — two module globals, one binder,
one equality check — and does not become a per-call argument. The composition
failure the document records is env-isolation composed with *per-call paths*; the
9 verbs that carry the engine's real power gain no path and no session argument
here. `spine_bind` adds one more *moment* at which the single binding may be set,
before any verb runs, exactly as `spine_open` already does. The composition does
not bite because there is never a call at which both a binding and a
caller-supplied identity are in play: after `spine_bind` returns, this door is
indistinguishable from a door that was launched bound to that spine — same
`SPINE`, same `SESSION`, same `os.environ` mirror (`:914-917`).

---

## 4. Four-axis self-score

**Depth — good, not excellent.** One tool hides four genuinely hard questions:
where a spine may come from, whether a file is a spine, what identity it confers,
and whether taking it collides with a live claimant. The caller sees one string
argument and either a binding or a refusal that says what to do. It leaks one
thing upward, unavoidably: the caller must possess the path. It hides nothing at
all for the 9 pass-through tools, which is a feature — they keep the shape their
guards were written for.

**Locality — strongest axis.** One new dispatch function, one schema entry, one
route, two set/constant edits, one extracted helper, one refactored ladder, one
parameterised refusal. No caller of anything changes. No behaviour of any
existing tool changes. Fan-out is two test-pin edits and one doctrine document,
and both of those are edits the pins themselves demand in their own failure text.

**Seam placement — where it loses.** The seam is at a new verb, and the caller
who "just wants `spine_status` to work" now needs to know a tool exists, know a
path, and spend a call before the call it wanted. Candidate B optimises exactly
that caller and beats me on it outright. Two smaller admissions in the same
direction: `tests/test_mcp_lifecycle.py:135`'s `ALLOWED` set has to grow, so the
tests do not want a third lifecycle route quite as freely as this design wants to
add one; and `test_mcp_identity.py:817` says, by construction, that the tests do
not want a `spine_file` property on any tool. Both are answerable (§2.3, §2.9),
neither is free.

**Testability — strong.** Every refusal is a pure function of `(args, SPINE,
filesystem)` and independently reachable: R4 with a path in `tmp_path` outside the
checkout, R5 with a directory and a missing file, R6 with `"[]"` on disk, R7 with
a spine whose `origin` is stripped, R8 with a written-in active lease under the
derived id, R9 with a claimed lease on the current spine. Idempotency (R0) is two
calls and an assertion that the second changed nothing and did not refuse. The
harness already exists: `_load_module` (`tests/test_mcp_lifecycle.py:83-119`)
gives a fresh module per binding, and `FullStdioRoundTripTests` shows the
end-to-end shape — `spine_open` in one door, `spine_bind` in a second door, drive
to terminal, `spine_close`. That round trip is the one piece of evidence I would
require before believing this design, because it is the only one that measures
"bound by binding" and "bound at launch" being the same thing.

**Where it loses, in one line:** seam placement — to Candidate B, on the caller
it inconveniences and on the two pins it has to renegotiate.

---

## 5. What it lets us delete

Honestly small. Three things, and I will not claim a fourth.

1. **`_HOW_TO_REBIND` (`:387-390`) disappears; `_HOW_TO_BIND` (`:383-386`)
   survives alone.** The two constants differ only in "bind"/"rebind" and both
   end in the same clause — "or relaunch this door with SPINE_FILE set to an
   existing spine file." That clause exists *only* because there was no in-band
   way to bind an existing spine. With `spine_bind` there is, so it goes, and the
   two constants collapse to one:

   > "Call `spine_bind` with the path to a spine that already exists, or
   > `spine_open` to mint one and bind this process to it."

2. **A whole recovery path stops being the documented answer: relaunch the
   server.** That is the deletion that matters more than the constant. Today the
   only way out of "named but unusable" without minting is to kill the door and
   restart it with a different environment; after this, it is one call. Every
   refusal that currently ends by telling a model to relaunch its own MCP server —
   advice a model inside that server usually cannot follow — stops saying so.

3. **One inline rule becomes one named function with two callers**
   (`session_id_for`, §2.6). Not a deletion of lines; a deletion of the
   *possibility* of a second definition, which is the kind `decision:net-deletion`
   is actually protecting.

**The counter-argument to item 1, which a reviewer should weigh.**
`_unbound_refusal`'s docstring argues the split "is not cosmetic" (`:404-409`):
an unbound door has no path to name, so a message promising to name one "invites
a fabricated path". My collapsed message does not promise the *door* will name a
path; it asks the *caller* to supply one, and R4/R5/R6/R7 turn a fabricated path
into a refusal rather than a binding. If a reviewer disagrees, the fallback keeps
both constants and deletes only the relaunch clause from each — the deletion is
then one clause instead of one constant, and nothing else in this candidate
changes.

**What it does not let us delete, stated so I am not claiming more than I have.**
`run_crew`'s `--spine` env-pair binding (`_crew_door_env`, `crew_env`,
`run_crew.py:940-996`) stays; it is the launch-time path and it is better than
this one when it is available. `SPINE_FILE`/`SPINE_SESSION` stay. The CLI stays.
Net line count is up, not down.

---

## 6. The strongest argument AGAINST this candidate

**`spine_bind` is a permanent hole in the security boundary that exists only
because a launcher failed, and it hands the decision to the least-informed party
in the system.**

Follow the population. Who calls this tool? An agent whose door is unbound. Why is
it unbound? Because whoever launched it did not set `SPINE_FILE`. But the caller
has to pass `spine_file` to `spine_bind` — so *someone* knew the path. That
someone is the launcher, and `run_crew --spine` already puts exactly that string
into the child's environment as a matched pair (`_crew_door_env`,
`run_crew.py:999+`; `--spine`'s own help text, `:1929-1939`). **Every dispatch
that can use `spine_bind` is a dispatch that could have been launched bound.** So
the tool's real population is dispatches where the launch path was broken or
bypassed — and the fix for a broken launcher is to fix the launcher, which
deletes the tool. Shipping the tool instead makes a broken launcher permanently
survivable, and buys that with a new, permanent, identity-moving path on the
boundary that governs the whole fleet's engine access. Constraint 6 asks what we
delete; the sharper question is what we are now unable to delete, and the answer
is this tool, forever, plus its nine refusals and its two renegotiated pins.

**And the sharpest single line: it makes a load-bearing sentence in the module
docstring false.** `:49-50` reads *"Exactly ONE declared tool property carries a
filesystem path: `spine_advance.from_child`."* `IDENTITY_TRADE.md` §2 builds on
that sentence, `test_no_tool_accepts_an_argument_that_could_redirect_the_door`
enforces it, and the reason it is stated in the singular is that the *one*
exception cost a measured gate closure on a fabricated APPROVE
(`mcp_spine_server.py:495-497`; the trade document's own transcript). This
candidate adds the second exception, and the second one is worse in kind than the
first: `from_child` can only feed evidence *into* the bound spine, whereas
`spine_file` decides *which spine is bound*. A design whose first act is to
falsify the sentence its own security argument rests on has to be very sure, and
"one confined string argument" is a smaller-sounding thing than "the door can now
be pointed."

A secondary objection, weaker but real: R8's staleness rule imports a timing
notion into a binding decision. `checklist_engine.py:1031-1063` already records
that lease ownership measured in *time* rather than *identity* is a known defect
with an issue against it (#600). R8 is correct today and inherits that defect
tomorrow.

---

## 7. What would have to be true for me to be wrong

- **If `origin.work_id` is commonly absent from the spines that need binding,**
  R7 refuses in the main case and the tool is theatre. Survey checklists, plans
  compiled outside `open_work`, and anything pre-lifecycle all lack it. The
  measurement that settles this: count spines under `.agent-work/` and
  `.worktrees/*/.agent-work/` with and without a stamped `origin.work_id`. If the
  ratio is bad, the session must come from somewhere else and this candidate's
  second crux collapses.
- **If the real complaint is "`spine_status` fails on an unbound door",** the seam
  belongs at first-call resolution, not at a new verb, and Candidate B wins on
  the caller I inconvenience. The evidence is in transcripts: what does an agent
  with an unbound door actually try first?
- **If every launcher path can be fixed,** the tool has no population (§6) and
  the correct answer is a launcher change plus a better refusal message — zero new
  tools, zero new boundary surface.
- **If one door legitimately needs to drive spines in two repositories,** my
  containment root is wrong. I claim that never happens outside a test
  (`tests/test_mcp_lifecycle.py:818-823` is the only case I found); a real
  cross-repo dispatch would falsify it.
- **If `IDENTITY_TRADE.md` §2's confinement property is not amendable** — if the
  human reads "the door cannot be pointed at another run's spine" as settled
  rather than as a recorded trade — then §2.9's amendment is not available and
  this candidate is dead as written, whatever its internals look like.
- **If two processes binding one spine turns out to be common rather than
  exceptional,** R8's refusal becomes the normal outcome and the tool refuses more
  often than it binds. That would mean identity must be per-assignment
  (`assignment_session_name`) rather than per-spine, which cannot be derived from
  a spine — and the session would have to become an argument after all, which
  `IDENTITY_TRADE.md` §3 Option B already rejected. That corner is the one place
  where I would expect this candidate to have to be replaced rather than
  repaired.

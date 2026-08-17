# Candidate B — `no-new-tool` (common-caller-first)

Design-it-twice panel, epic #567 lane A. Designed against `600de020` as read in
this worktree: `scripts/mcp_spine_server.py`, `scripts/spine_lifecycle.py`,
`tests/test_mcp_lifecycle.py`, `tests/test_mcp_door_unbound.py`,
`tests/test_mcp_identity.py`.

## 1. Candidate name and the one named constraint

**Name:** `adopt-or-mint` — `spine_open` binds to the work its `work_id` names
when that work already exists, and mints it when it does not.

**Constraint:** `no-new-tool` (common-caller-first). Zero tools are added. The
declared surface stays at 11 names and `TOOL_NAMES` (`mcp_spine_server.py:1415`)
does not change. One existing tool's argument list is relaxed by one field and
one existing refusal message becomes actionable.

**Sub-shape chosen:** (a) `spine_open` becomes adopt-or-mint.

**Sub-shape rejected:** (b) lazy self-resolution at first call, named below as
**`worktree-ambient self-resolution`**, rejected on measured evidence in §1.2.
It is the more interesting design and the tighter one on reach; it is rejected
anyway, for a reason I can point at in the test suite.

### 1.1 The caller this optimizes for

The brief's caller wants `spine_status` to work in a process that did not launch
its own door. Today that caller gets `_unbound_refusal()`
(`mcp_spine_server.py:393-440`), whose remedy text is `_HOW_TO_BIND`
(`:383-386`):

> Call `spine_open` to mint a spine and bind this process to it, or relaunch this
> door with SPINE_FILE set to an existing spine file.

Both halves are wrong for this caller. It does not want to mint anything — its
spine already exists — and it cannot relaunch its own door. So the door's own
refusal, the one channel the caller reliably reads, currently names two remedies
neither of which it can take. This candidate's whole caller-facing value is that
the same refusal becomes one the caller can act on with the surface it already
has. That is why "no new tool" is not a handicap here: the fix the common caller
needs is a *sentence* plus one branch, not a new verb.

### 1.2 Why (b) `worktree-ambient self-resolution` is rejected — named, with the measurement

Sub-shape (b) would have the unbound door resolve its own spine at first call. I
designed it far enough to cost it, because the panel should see why it lost:
anchor on `Path(__file__).resolve().parent` (never the cwd — precedent
`_engine_from_env`, `:180-197`, and `_primary_checkout_for_lifecycle`'s unbound
fallback, `:857`), take `git rev-parse --show-toplevel` from there through the
existing `_git_rev_parse` (`:773-794`), refuse outright when that toplevel is the
primary checkout, and otherwise accept the single positively-identified spine
under `<worktree>/.agent-work/` — refusing on zero and refusing on more than one.

Measured, on the six live trees in this repo right now (primary checkout plus
five linked worktrees), scanning `.agent-work/**/*.json` for dicts carrying a
non-empty `work_id`, non-empty `items` and a dict `tasks`, excluding
`.agent-work/archive/`:

| tree | adoptable spines |
| --- | --- |
| `constellation-skills` (primary) | 1 (`.agent-work/epic-567-door/spine.json`) |
| `.worktrees/567-a-spine-identity` | 1 |
| `.worktrees/567-b-external-backend` | 0 |
| `.worktrees/567-c-rail-readability` | 1 |
| `.worktrees/567-g-closeout-lease` | 1 |
| `.worktrees/issue-610-stand-up-work-area` | 1 |

So uniqueness holds today in every tree, and the design would work. It is
rejected for two reasons, the second decisive:

**Being unbound carries no intent.** "No spine is named" is not evidence that the
caller wants one found. It is equally the state of a door that must refuse — and
the previous lane (#603) made it *mean* refuse on purpose. A design that reads a
request out of a state that carries none is guessing about intent, and the guess
is unfalsifiable from inside the door.

**It turns the suite that pins the previous lane's fix red, by construction.**
`tests/test_mcp_door_unbound.py` launches the repo's own
`scripts/mcp_spine_server.py` (`:124-127`, `:152-153`) — so the door's own
`Path(__file__)` is *this* worktree's script, and this worktree holds exactly one
adoptable spine. Under (b), these go red:

- `UnboundDoorRefusesTests::test_empty_spine_file_refuses_rather_than_binding_the_cwd`
  (`:223-232`) — the test named after the defect.
- `test_unset_spine_file_refuses_instead_of_dying_at_import` (`:214`),
  `test_whitespace_only_spine_file_is_the_same_class_as_empty` (`:234`).
- `EveryToolRefusesWhenUnboundTests::test_every_tool_but_the_one_that_binds_refuses`
  (`:299-321`), which asserts a COUNT over the whole surface.
- `tests/test_mcp_identity.py::DC3InheritanceMechanismTests::test_subagent_with_no_special_configuration_gets_no_identity_never_the_parents`
  (`:639-673`), which asserts `"no spine is bound"` in the reply of a subagent
  door launched with the parent's environment stripped (`ServerInstance`'s Popen,
  `:121-131`, again `str(SERVER)` from this repo).
- `DC3PositiveControlTests::test_control_is_red_when_the_config_never_delivered`
  (`:493-528`).

Those are not incidental. DC3 measures a recorded isolation property, and (b)
makes "an unbound door" a state the suite can no longer construct against the
delivered artifact in-repo. The fix exists — `test_mcp_door_unbound.py` already
has `stage_a_checkout` (used by `BindOnOpenTests`, `:396-427`, which copies a
checkout into `tmp_path` and launches `self.repo/"scripts"/...`), so the unbound
suites could be moved onto it. But then the isolation measurement runs against a
copy, and worse, the suite's result would depend on *which tree CI checked out
into* — green from the primary checkout, red from a lane worktree. A
location-dependent security test is worse than an honest red.

The only way to give (b) intent without an ambient guess is an explicit opt-in,
and with no new tool allowed the only opt-in left is a new environment variable —
which hard constraint 7 forbids if avoidable. It is avoidable: sub-shape (a)
avoids it. So (b) is rejected on evidence, not on taste. If the panel judges the
in-repo constructibility of "unbound" expendable, (b) is the tighter candidate on
reach and should be reconsidered — see §7.

## 2. The design

### 2.1 What "already exists" means, precisely

Existence is asked about **work**, not about a spine file in isolation, and it is
asked at the two locations `work_id` can name — both derived from the caller's
`work_id`, neither from the door's location:

- `WT = spine_lifecycle.worktree_path_for(work_id, wt_root=_default_wt_root(root))`
  (`spine_lifecycle.py:58-64`, `:173-177`) — the linked worktree this `work_id`
  would own.
- `PRIMARY_WORK = root/".agent-work"/work_id` — the in-tree work area, for work
  that was never opened into a worktree (the Admiral's own epic spine is exactly
  this shape).
- `WT_WORK = WT/".agent-work"/work_id` — the work area `open_work` scaffolds
  (`spine_lifecycle.py:322`, `:348`).

`root` is `_primary_checkout_for_lifecycle()` (`mcp_spine_server.py:797-861`),
unchanged, still the only root `_spine_open` resolves.

A file in one of those two work areas is an **adoptable spine** only if all of
these hold — a positive identification, never "the first JSON we found":

1. it parses as JSON and is a `dict`;
2. its top-level `work_id` is a non-empty string and equals the requested
   `work_id` (measured present on all five live spines, including the one with
   no `origin` block);
3. `items` is non-empty and `tasks` is a `dict` — the two fields
   `closeout_refusal` reads (`spine_lifecycle.py:146-154`), i.e. it is a compiled
   plan and not a journal, a delta, an evidence file or a template;
4. it is readable (one-byte open, the same question `_unbound_refusal` asks and
   for the same reason, `:419`);
5. its resolved path is contained in the work area it was found under, via
   `_resolve_confined(candidate, join_relative_to=None, bound_dir=<work area>)` —
   the existing predicate (`:322-380`), a third `bound_dir`, precedent at
   `:354-360`. `_resolve_confined` resolves before comparing (`:377`), so a
   symlink pointing out of the work area is caught.

`.agent-work/archive/` is not searched. `close_work` moves finished work there
(`archive_name_for`, `spine_lifecycle.py:73-80`), and archived work is closed, not
adoptable.

### 2.2 The partial-existence matrix

Every cell is a decision, and "half-mint" is never one of them.

| worktree | spine in a work area | branch | outcome |
| --- | --- | --- | --- |
| exists | exactly one adoptable, in `WT_WORK` | any | **ADOPT** |
| absent | exactly one adoptable, in `PRIMARY_WORK` | any | **ADOPT** (in-tree work) |
| exists | one in `WT_WORK` *and* one in `PRIMARY_WORK` | any | **REFUSE — ambiguous** |
| exists | none | any | **REFUSE — occupied worktree, no plan** |
| exists | present but fails identification (2)-(5) | any | **REFUSE — naming the file and the failed test** |
| absent | none | exists | **REFUSE — `open_work`'s own existing git refusal, unchanged** |
| absent | none | absent | **MINT** (today's path, byte-for-byte) |

Notes on the three that could tempt a shortcut:

- *Occupied worktree, no plan.* Minting here would need `git worktree add` on an
  existing path, which `open_work` already refuses (`spine_lifecycle.py:306-308`).
  Adopting is impossible — there is no spine. So refuse, and say which of the two
  the caller must do: finish the open, or remove the worktree. This is also the
  state a closed-but-not-cleaned work_id leaves behind (`close_work` archives the
  work area and does not remove the worktree), so the refusal must name it.
- *Branch exists, nothing else.* Left exactly as it is today: `open_work` reaches
  `git worktree add ... -b <branch>` (`:319`), git refuses, `_git` raises
  `SpineLifecycleError` (`:212-216`), `_rollback` runs (`:237-244`), and
  `_spine_open` returns it as `open-refused` (`mcp_spine_server.py:1034-1035`).
  No new code, no new message.
- *Two locations.* Refusing is the whole point. A door that picks one of two is
  the design family this candidate exists to avoid.

### 2.3 Where SESSION comes from

`_bind_process_to` needs both roots, and its docstring is explicit that binding
the spine alone yields a door that cannot `claim`
(`mcp_spine_server.py:884-893`; `checklist_engine.py:1021-1022` is the engine
refusal it names). So:

**SESSION on adopt is `constellation/<work_id>` — computed by the same expression
`open_work` uses to mint it (`spine_lifecycle.py:357`).**

Make that a fact rather than a claim by extracting it, beside its two existing
pure siblings `worktree_path_for` (`:58`) and `branch_name_for` (`:67`):

```python
def session_id_for(work_id: str) -> str:
    """The engine session a door driving `work_id` binds as. Pure. Called by
    open_work's own return dict and by adopt_work, so 'adopt hands back exactly
    what mint would have handed back' is one expression, not two."""
    return f"constellation/{work_id}"
```

`open_work`'s return (`:354-361`) then calls it, and `adopt_work` calls it. There
is no ladder, no ordering, no ambient read, and no case where SESSION is absent:
`work_id` is required to reach this point at all.

Deliberately **not** taken: reading `engine_session.session_id` off the spine.
That is the recorded lease holder's identity, and adopting it is impersonation —
two processes under one session id, which the engine's idempotent-resume branch
(`checklist_engine.py:1031-1067`) would silently treat as one driver. Binding the
canonical name instead means the conflict is adjudicated by the engine, once, in
the one place that owns it: if another session holds an active lease, `claim`
refuses with "checklist already owned by active session ... use `claim --force`"
(`checklist_engine.py:1074-1079`). Read-only `spine_status` still works, because
`run_engine("current", mutating=False)` omits `--session-id` entirely
(`mcp_spine_server.py:664-666`, `:1437`).

The cost, stated: a spine whose live lease is *not* `constellation/<work_id>` —
the Admiral's epic spine, whose recorded session is a bare harness id — can be
read but not mutated by an adopting door while that lease is active. That is the
right outcome. A live human session is driving it.

### 2.4 How the caller learns the `work_id`, and whether it can tell adopt from mint

**It learns it because `work_id` is written into three things it can already
see:** the branch is the `work_id` verbatim (`branch_name_for`,
`spine_lifecycle.py:67-70`), the worktree directory is its last segment
(`worktree_path_for`, `:58-64`), and every compiled spine carries it top-level.
A caller standing in its own worktree can read it off `git rev-parse
--abbrev-ref HEAD`, and a dispatched crew has it in its launch order. So the
premise "the caller may not know its `work_id`" is measurably false for the
dispatch shapes this repo produces — and where it is true, the caller cannot be
served by this candidate at all (§7).

**Adopt is distinguishable from mint in the result.** `adopt_work` returns the
same five keys `open_work` returns (`SPINE_FILE`, `SPINE_SESSION`,
`SPINE_PARENT`, `branch`, `worktree`) plus nothing; `_spine_open` adds one key to
the payload it hands `_lifecycle_result` (`:960-965`):

```json
{"...": "...", "bound": "adopted"}   // vs "bound": "minted"
```

One word, in a payload the caller already parses, so a caller that wants to know
can check and a caller that does not care is unaffected.

### 2.5 The diff shape

**Added — `scripts/spine_lifecycle.py`:**

- `session_id_for(work_id)` — pure, §2.3.
- `adopt_work(work_id, *, root, parent) -> dict | None` — impure, read-only.
  Returns `open_work`'s five-key dict when exactly one adoptable spine is found,
  `None` when the work does not exist at all (the mint path), and raises
  `SpineLifecycleError` for every refusing cell of §2.2's matrix. Creates
  nothing, writes nothing, runs no git command that mutates.
- `_spines_under(work_dir) -> list[tuple[Path, dict]]` — one defensive scanner
  (`rglob("*.json")`, skip `OSError`/`ValueError`/non-dict, in the style
  `_active_engine_session_spine` already uses, `:180-209`).

**Changed — `scripts/spine_lifecycle.py`:**

- `_active_engine_session_spine` (`:180-209`) loses its own scan-and-load body and
  filters `_spines_under(root/".agent-work"/work_id)` instead. Its predicate is
  unchanged and deliberately stays *broader* than "adoptable" — `open_work`'s step
  3 refusal (`:310-315`) must keep firing on any JSON with an active
  `engine_session`, adoptable or not.
- `open_work`'s return dict (`:354-361`) calls `session_id_for(work_id)`.

**Changed — `scripts/mcp_spine_server.py`:**

- `_spine_open` (`:968-1042`) is re-ordered. The new body, in order: require
  `work_id` only; resolve `root` (`:1011-1017`, unchanged); `wt_root` +
  `_resolve_confined` containment (`:1019-1029`, unchanged); read `parent` from
  `SPINE_PARENT` (`:1031`, unchanged); call `spine_lifecycle.adopt_work(...)`; ask
  `_rebind_refusal(to=...)`; if adopting, `_bind_process_to(...)` and return
  `_lifecycle_result({**existing, "bound": "adopted"})`; else require `spec`,
  `open_work(...)`, `_bind_process_to(...)`, return
  `_lifecycle_result({**opened, "bound": "minted"})`.
- `_rebind_refusal` (`:920-957`) gains one keyword: `to: str | None = None`. When
  `to` resolves equal to the currently bound spine it returns `None` — rebinding
  to the spine you are already bound to is not a rebind, and without this a second
  `spine_open` on the caller's own work_id would be refused by its own lease.
  `_rebind_refusal` is a helper, not `_spine_open`, so it may read `SPINE` freely
  (`tests/test_mcp_lifecycle.py:194` is scoped to one function; the precedent is
  spelled out at `mcp_spine_server.py:828-830`).
- `_HOW_TO_BIND` (`:383-386`) is reworded to the remedy the common caller can
  actually take:

  > Call `spine_open` with the `work_id` you are driving — it binds this door to
  > that work's existing spine when the work already exists, and mints the work
  > when it does not. `work_id` is your branch name (`git rev-parse --abbrev-ref
  > HEAD`).

  `_HOW_TO_REBIND` (`:387-390`) gets the same first clause.
- `spine_open`'s schema (`:1379-1397`): `"required": ["work_id"]`; `spec`'s
  description gains "required only when the work does not exist yet". Its tool
  description (`:1371-1378`) loses "Acts on a spine that does not exist yet" and
  gains "Binds this door to `work_id`'s spine, creating the work first if it does
  not exist yet."
- `_require(args, "work_id", "spec")` (`:990`) becomes `_require(args, "work_id")`,
  with the `spec` check moved onto the mint branch, keeping its existing
  `bad-argument-type` and `missing-required-argument` rejection classes
  (`:990-1001`).

**Deleted:** the duplicated `f"constellation/{work_id}"` literal; one of the two
`rglob`+defensive-load bodies. See §5.

**Unchanged, and load-bearing that it is so:** `_bind_process_to` (`:878-917`)
itself, `_identity_violation` (`:443-570`), `run_engine` (`:629-685`),
`call_tool` (`:1435`), `call_lifecycle_tool` (`:1067-1097`), `main()`'s
`tools/call` branch (`:1713-1742`), `BINDS_WITHOUT_A_BOUND_SPINE` (`:1417-1425`),
`TOOLS`/`TOOL_NAMES`, and every `_spine_close` path.

### 2.6 Refusal messages

```
spine_open: work_id 'X' already has a worktree at <WT>, but no compiled spine
in <WT_WORK> to bind to. Either finish opening that work (a work area with a
compiled spine.json), or remove the worktree and call spine_open again to mint
it fresh. Nothing was created by this call.
```

```
spine_open: work_id 'X' names work in two places at once -- <p1> and <p2>. A
door binds one spine, and this call cannot tell which one you meant. Remove or
archive the one that is finished, then call spine_open again.
```

```
spine_open: found <p> for work_id 'X', but it is not a spine this door can
bind: <reason -- "it does not parse as JSON" / "its work_id is 'Y', not 'X'" /
"it records no gates (items/tasks)" / "it cannot be read (PermissionError)">.
Nothing was created by this call. Binding a file this door cannot identify as a
plan is how a fabricated file gets driven as one.
```

Rejection classes for `_log_rejection` (`:695-728`), reusing the existing shape:
`adopt-refused` for the first three, `open-refused` unchanged for `open_work`'s
own (`:1035`), `lease-held` unchanged for `_rebind_refusal` (`:1009`).

### 2.7 How each AST pin is respected

- **`tests/test_mcp_lifecycle.py:194`** — `_spine_open`'s own source may not
  reference `SPINE`, `SESSION` or `run_engine` (`BANNED_IDENTIFIERS`, `:63`;
  detector `_referenced_names`, `:70-71`, which matches `ast.Name` ids only).
  This bites sub-shape (a) directly, and the answer is the one the module already
  uses twice: **delegate, do not read.** `_spine_open` never asks "what am I bound
  to" — `_rebind_refusal(to=candidate)` asks it, and `_rebind_refusal` is a
  helper the ban does not cover, exactly as `_primary_checkout_for_lifecycle`
  already reads `SPINE` on `_spine_open`'s behalf (`:857`, justified at
  `:828-830`). `_spine_open` continues to call `_bind_process_to(...)`, which is an
  `ast.Name` of `_bind_process_to`, not of the banned names — this is already true
  today at `:1041`. Net: zero new banned identifiers.
- **`tests/test_mcp_lifecycle.py:563`** (module-wide assignment pin, detector
  `_assignments_to`, `:509-546`) — the only assignment sites for `SPINE`/`SESSION`
  stay `<module>` and `_bind_process_to`. The adopt branch binds *through* the one
  binder. No second binder, and no second *caller* either: both branches of
  `_spine_open` call it, as one branch does today.
- **`tests/test_mcp_lifecycle.py:137`** (`call_lifecycle_tool` return-shape pin,
  `ALLOWED = {"_spine_open", "_spine_close"}`, `:135`) — untouched.
  `call_lifecycle_tool` (`:1093-1097`) does not change at all; adopt lives inside
  `_spine_open`, which is why the adopt/mint decision must be a branch there and
  not a third route.
- **`tests/test_mcp_lifecycle.py:610-614`** (`_bind_process_to(` appears in
  `_spine_open`'s source) — still true.
- **`tests/test_mcp_lifecycle.py:236-256`** (`_spine_open` must call
  `spine_lifecycle._default_wt_root(` and must not restate `f"{root.name}-wt"`) —
  the `wt_root` derivation is unmoved.
- **`tests/test_mcp_lifecycle.py:301-308`** (`_resolve_confined` is called in
  `_spine_open`'s own source) — still called, unmoved.
- **`tests/test_mcp_identity.py`'s `call_tool` choke-point pin** — `call_tool` is
  not touched.
- **`tests/test_mcp_door_unbound.py:299-321`** — `ARGS["spine_open"]` still passes
  `work_id` and `spec` (`:296`), so relaxing `required` cannot break it; the tool
  is already exempt via `BINDS_WITHOUT_A_BOUND_SPINE`.
- **`tests/test_mcp_identity.py` DC3** — nothing an unbound door does changes. An
  unbound door still refuses every tool but `spine_open`, and `spine_open` still
  requires an explicit call with an explicit `work_id`.

**No existing test goes red.** That is the sharpest practical contrast with
sub-shape (b).

### 2.8 Can this bind the WRONG spine?

Two questions, and only the second has a real answer.

*Can it bind a spine the caller did not name?* No, and this is a structural
property rather than a likelihood. The bound path is a function of the
caller-supplied `work_id` and `root` alone. Both candidate locations are built by
joining `work_id` onto a root (§2.1); a candidate is rejected unless its own
top-level `work_id` equals the requested one (identification test 2); the path is
containment-checked against the work area it was found in (test 5, via
`_resolve_confined`, which resolves symlinks before comparing, `:377`); and two
candidates refuse instead of one winning. Nothing in the resolution reads the
process cwd, the environment beyond the already-existing `SPINE_PARENT`
(`:1031`), or the door's own location beyond `_primary_checkout_for_lifecycle`'s
existing anchor. Move the door to any directory and the same call binds the same
spine.

*Can the caller name a spine it should not have?* **Yes, and this is the real
cost of the candidate — see §3 and §6.** `work_id` is a caller-supplied name for
a spine, and the only thing between a door and another lane's work_id is
`_rebind_refusal`, which fails open in three directions by design (`:936-948`),
including "no lease".

### 2.9 Is this the cwd-binding defect wearing new clothes?

No, and the test is falsifiable rather than rhetorical.

`_spine_from_env`'s record (`:165-169`) is that `${SPINE_FILE:-}` expanded to an
empty string, `Path("").resolve()` returned the process cwd, and the door
"silently bound ... to whatever directory it was standing in". That defect had
five properties: it was **silent**, it was **unconditional** (every launch
produced a binding), it was **unidentified** (a directory satisfied it), it was
**unique by construction** (it could never notice it did not know), and its answer
**changed with the door's location**.

This candidate is the opposite on all five, and four of the five are properties of
the code rather than of the environment:

1. It fires only on an **explicit call** naming an explicit `work_id`. No call,
   no binding — an unbound door that is never asked stays unbound and keeps
   refusing.
2. The bound path is a **function of a caller-supplied name**, not of the door's
   location. This is the one that matters most: the cwd defect's answer was
   whatever directory the process stood in; this candidate's answer is identical
   from any directory.
3. The candidate must **positively identify** as a compiled plan (§2.1, tests
   1-4). A directory cannot be the answer. A journal, a delta, an evidence file,
   a template, or a spine for different work cannot be the answer.
4. **Zero and many both refuse.** The defect could not represent "I do not know."
5. The result **names what it bound** and how (`"bound": "adopted"`, the
   `SPINE_FILE`, the `SPINE_SESSION`), returned to the caller as the tool's own
   payload. There is no silent version of this path.

Fail-closed, restated in the terms the previous lane used: every refusing cell of
§2.2 leaves `SPINE` exactly as it was — `None` for an unbound door — so the very
next tool call gets `_unbound_refusal()` again (`:1723`, `:657-662`). A refused
adopt cannot leave a door half-bound, because the only assignment happens after
every check has passed, inside `_bind_process_to`, and nothing before it writes
anything at all.

## 3. The isolation property

"One file per process, decided at launch or at a successful mint" becomes **"one
file per process, decided at launch or by an explicit `spine_open` naming a
`work_id` — which may already exist."** The count is unchanged
(`decision:one-spine-per-process-stands`): one spine at a time, `_rebind_refusal`
still blocks the swap under a held lease, and `_identity_violation` still compares
every argv against `SPINE` at call time (`:517-523`), so a foreign `--file` is
refused after an adopt exactly as after a mint
(`tests/test_mcp_lifecycle.py:642-666` already measures this for a rebind). What
an agent can reach that it could not before: **a door can bind to a spine that
already exists, anywhere under `root/.agent-work/<work_id>` or
`<wt_root>/<last-segment>/.agent-work/<work_id>`, for any `work_id` it can name —
and then drive it, claim it as `constellation/<work_id>`, and `spine_close` it.**
Before this change the only spine a door could bind mid-life was one it had just
minted, which by definition nobody else was driving. That is a genuine widening of
reach and it is the price of the `no-new-tool` constraint: the widening is not
gated by a new tool with its own refusal set, it is gated by an argument on a tool
whose description says it creates things. What still holds: identity is not a
per-call argument for any of the 9 engine tools; the lease remains the only
authority over concurrent drivers, and it refuses a foreign active session in the
engine, not in the door; `--from-child` and `--delta` stay confined to
`SPINE.parent` (`:533-569`); and nothing widens for `spine_close`, which still
acts on `SPINE` alone and still requires the caller to have driven the spine to a
released terminal close (`closeout_refusal`, `spine_lifecycle.py:122-161`).

**Side of the `IDENTITY_TRADE.md` trade:** this candidate stays entirely on the
**env-binding / isolation** side. It adds no per-call path and no per-call
identity, so the composition failure that document records — env-binding times
per-call paths — cannot bite it: there is still exactly one identity for the life
of the process, and `_identity_violation` still resolves it through the engine's
own parser at call time. All that moves is *when* the single binding is decided,
which `_bind_process_to`'s own docstring already licenses (`:894-899`).

## 4. Four-axis self-score

**Depth — wins.** All of §2.2's matrix lives behind `spine_lifecycle.adopt_work`.
The tool surface is byte-identical in shape; the caller learns one optional word
in a payload it already parses, and gets a refusal message that finally names a
remedy it can take. Nothing about worktrees, work areas, archives or session
formulae leaks upward.

**Locality — mixed, and this is the weaker half.** Inside the door the change is
small and contained: one function re-ordered, one helper gains one keyword, two
strings reworded, one schema field moved out of `required`. In the library it is
one new read-only function plus one extracted formula. But it fans out once
outside the code: the skills corpus tells dispatched crews their spine is already
bound (`tests/test_mcp_adoption.py::TestTier2SpineAlreadyBoundForDispatchedCrews`,
`:838-884`), and that instruction now needs a second sentence for the crew whose
spine is bound but whose door is not. A doc fan-out with a two-sided pin over it
is real work, not a footnote.

**Seam placement — wins on the tests, loses on the name.** Every pin in
`tests/test_mcp_lifecycle.py` is already drawn around exactly the two places this
change touches, `_spine_open` and `_bind_process_to`, and none of them has to
move. That is strong evidence the seam is where the tests want it. Against: the
tool is called `spine_open` and will now sometimes open nothing. The module
already carries the identical tension for `spine_halt`, which also skips and
reopens, and already ruled on it — "a rename would break any agent mid-run, and
stability outranks the naming tension" (`:79-83`) — so the precedent is
established, but a reader meeting `spine_open` for the first time is now one
docstring away from being misled.

**Testability — wins.** Seven enumerable outcomes (§2.2), each constructible in a
throwaway repo with the helpers that already exist: `_init_repo`
(`tests/test_mcp_lifecycle.py:74-80`), `_load_module` (`:83-119`) for the door-side
branch, `_McpRpcClient` (`:357-406`) for the round trip, `stage_a_checkout`
(`tests/test_mcp_door_unbound.py`) for a full second door. `adopt_work` is a
library function testable with no door at all, and the load-bearing claim of §2.3
gets a *differential* test: open work, record the five-key dict, adopt the same
work from a second door, assert the dicts agree — which is what makes "adopt
hands back what mint would have" evidence rather than prose. The one weak spot:
"called twice" now depends on `_rebind_refusal(to=...)`, and that predicate
already has three deliberate fail-open directions (`:936-948`); a fourth
behaviour on a fail-open predicate is the part of this design most likely to be
wrong in a way a test does not notice.

**Where it loses overall: locality (the corpus fan-out) and the honest naming
tension.** And, worse than either, the isolation widening in §3 — which is not one
of the four axes, and is the thing §6 is about.

## 5. What it lets us delete

Small, and argued rather than inflated:

- The duplicated session-id formula. `f"constellation/{work_id}"` exists once
  today (`spine_lifecycle.py:357`) and would have existed twice; extracting
  `session_id_for` leaves one owner and removes the possibility of adopt and mint
  disagreeing about identity. This is the deletion that matters, because it
  converts a claim into an expression.
- One of two defensive-scan bodies. `_active_engine_session_spine`'s
  `rglob`/`try: json.loads`/`isinstance` block (`spine_lifecycle.py:192-209`)
  collapses into `_spines_under`, shared with adopt. Roughly 15 lines, and one
  fewer definition of "read every JSON under a work area without dying on a bad
  one".
- One concept: **"bind by relaunching the door."** It stays as fallback text in
  `_HOW_TO_REBIND`, but it stops being the only answer for a caller who did not
  launch its own door, which is what makes the epic's exit criterion reachable
  without a second process.

**What it does NOT let us delete, stated plainly:** no tool (that is the
constraint). Not `run_crew.py:991`'s `env["SPINE_FILE"] = spine_file` — dispatches
that do bind must keep binding, and an explicit value must keep winning over
anything derived. Not `.mcp.json`'s `${SPINE_FILE:-}` seam, which
`tests/test_mcp_identity.py`'s whole DC3 measurement is built on. Not
`_unbound_refusal`'s five-input class or its two-way wording split (`:404-409`).
Net line count is roughly flat: `adopt_work` and the matrix are new code, and
they buy a capability, not a simplification. Under `decision:net-deletion` this
candidate is close to neutral, and I would rather say so than dress up 15 lines.

## 6. The strongest argument AGAINST this candidate

**It smuggles a bind-to-anything capability in as an argument on a tool whose
description promises creation, and it does that because it was forbidden a tool of
its own.**

`_identity_violation`'s docstring records six guards that each modelled a shape a
redirect might take and were each defeated by a shape they had not enumerated
(`:456-463`), and the rule it settled on is written into the refusal text itself:
"Identity is not a per-call argument here" (`:521-522`). This candidate makes
identity a per-call argument for exactly one call. It is a *narrow* per-call
argument — a `work_id`, not a path, joined onto a root the caller cannot choose,
containment-checked, uniqueness-checked, identification-checked — but the
capability it confers is the one the door was built to withhold: pointing this
process at a spine somebody else's process created.

And the guard that limits it is the weakest one in the module.
`_rebind_refusal` fails open in three directions on purpose (`:936-948`) — nothing
bound, an unreadable spine, and **no lease**. Releasing a lease is one call, and a
door's own closeout already makes it (`:932-935`). So the reachable sequence is:
release, `spine_open` with any `work_id` in the tree, read another lane's gate
state, claim it as `constellation/<that work_id>`, drive it, and — if it is
terminal — archive it with `spine_close`. Nothing in this design refuses that.
The engine's lease refuses only while somebody is actively holding one.

The comparison that makes this damning is with the sub-shape I rejected.
`worktree-ambient self-resolution` could not do any of that: its reach was bounded
by the door's own worktree, with no caller-supplied name anywhere in the
resolution, and it refused in the shared primary checkout entirely. I rejected the
*tighter* design because it broke a test suite, and shipped the *looser* one
because it broke none. A reviewer is entitled to read that as optimizing for green
CI over the security property the CI exists to measure.

Second, smaller, and still real: my §2.8 answer is a claim about **code** for
"binds a spine the caller did not name" and only a claim about **the filesystem**
for the ambiguity cases. Uniqueness across the two candidate locations is a
property of what is on disk at call time. No code change can make it impossible
for a work area to contain exactly one adoptable spine that is not the one the
caller meant — a copy left for reference, a predecessor's plan never archived, a
nested work area. I refuse on two and identify positively, which turns most of
that class into a refusal, but "impossible" would require the caller to name the
file, which is Candidate A's design and not mine.

## 7. What would have to be true for me to be wrong

- **If the reach widening in §3 is unacceptable to the panel**, then `no-new-tool`
  is the wrong constraint for this decision, and Candidate A is right: a dedicated
  bind tool with its own refusal set, its own containment root and its own
  interaction with the lease is a *named* surface a reviewer audits, where mine is
  a branch hidden inside a tool described as creating things. My candidate is only
  the right answer if "no new tool" is a genuine requirement rather than a
  preference.
- **If callers do not reliably know their own `work_id`**, adopt-or-mint cannot be
  called and the whole candidate is unusable. I measured against it: `work_id` is
  the branch name (`spine_lifecycle.py:67-70`), the worktree's last segment
  (`:58-64`), and a top-level field of all five live spines. If a dispatch shape
  exists where an agent genuinely cannot recover it — a door in a detached HEAD, a
  worktree renamed by hand, an agent with no shell — that caller needs sub-shape
  (b)'s inference and I have nothing for it.
- **If the in-repo constructibility of "an unbound door" is expendable**, my
  rejection of `worktree-ambient self-resolution` collapses, and it should win:
  it is tighter on reach, it needs no `work_id`, and it serves the brief's
  "caller who just wants `spine_status` to work" without any extra call. The whole
  weight of my rejection sits on roughly ten tests
  (`tests/test_mcp_door_unbound.py:214-321`,
  `tests/test_mcp_identity.py:493-528` and `:639-673`) and on my judgement that a
  location-dependent isolation test is worse than a red one.
- **If `_rebind_refusal` is ever tightened to refuse any rebind**, or if
  `decision:one-spine-per-process-stands` is later read as "one spine for the life
  of the process" rather than "one at a time", the adopt branch dies with it —
  every adopt on a door that has ever been bound becomes a refusal, and the
  candidate degrades to "useful exactly once per process."
- **If a work area can legitimately hold two spines for one `work_id`** (a survey
  beside a gated plan, say — this epic's own driving spine is `execute.json`, not
  `spine.json`, per `spine_lifecycle.py:191`), then my ambiguity refusal fires on
  a normal case rather than an abnormal one, and the identification test needs a
  tie-break I have deliberately refused to design.

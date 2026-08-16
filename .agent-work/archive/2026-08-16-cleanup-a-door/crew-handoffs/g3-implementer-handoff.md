# Implementer Handoff

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing.

## Gate
`g3` — issue #603, the door cannot be bound by the session that needs it, and answers about
a demo spine when unbound. **This is the run's hardest gate.**

## Task

Two changes that compose.

### (A) Fail closed

Today an unbound door either dies or lies. Make **unset, empty, non-existent, non-file and
unreadable** one single "unbound" class, and make every tool answer a **refusal** instead of
a demo answer, a crash, or silence.

**Three distinct failure worlds are measured on the current tree, and a naive fix addresses
only one.** Do not rediscover these:

| `SPINE_FILE` | what happens now | exit |
|---|---|---|
| **unset** | `KeyError` at `mcp_spine_server.py:146`, **at import** — the server dies before it can refuse anything; the client sees only `Connection closed` | 1 |
| **empty `""`** | `Path("").resolve()` is the **cwd**, so the door silently binds itself to a directory and answers `IsADirectoryError: Is a directory: <repo root>` | 0 |
| **missing path** | was #604's crash; since g1 the door answers `isError` with a raw `FileNotFoundError` | 0 |

**The empty case is the one production will actually take.** `.mcp.json`'s form is
`${SPINE_FILE:-<default>}`, and `tests/test_mcp_spine_server.py:574` pins that the key is
*present* — so dropping the default yields `${SPINE_FILE:-}`, which expands to **empty, not
unset**. Design for empty first.

Also make **`ENGINE`** fail closed in the same motion. Measured: `SPINE_ENGINE` unset is a
`KeyError` at `:145`, also at import. A session that has no `SPINE_FILE` very likely has no
`SPINE_ENGINE` either, and then the door dies before any refusal is reachable — the same
illegible `Connection closed` this gate exists to end.

**Refusal wording splits.** An *unbound* refusal has no path to name, so a criterion that
says "name the path" is unsatisfiable there and invites a fabricated one:

- **unbound** → "no spine is bound; call `spine_open` (or set `SPINE_FILE`)"
- **missing / unreadable / not-a-file** → name the path **and** say how to rebind

### (B) Bind on open

Let a successful `spine_open` bind **this process** to the spine it just minted, per
`decision:bind-on-open-over-new-verb`.

**The measured cost, already established — do not rediscover it.** Four derivations of
`SPINE` are import-time and would strand a rebind at the old spine:

| line | derivation |
|---|---|
| `:162` | `CALLLOG` |
| `:167` | `START_MARKER` |
| `:177` | `REJECTIONLOG` |
| `:188` | `_resolve_confined(..., bound_dir: Path = SPINE.parent)` — a **default argument**, evaluated once at import. The subtlest of the four. |

An independent AST pass confirmed there is **no fifth**; every other `SPINE` reference is
inside a function body and follows a rebind for free. Make these four late-bound.

**But two further identity roots are excluded from that four-item list, and both are
proven:**

1. **`_primary_checkout_for_lifecycle` (`:593`) does its own hard `os.environ["SPINE_FILE"]`
   read**, and `_spine_open` calls it at `:657` inside `except (OSError, RuntimeError)` —
   which does **not** catch `KeyError`. So after (A) lands, an unbound session calling
   `spine_open` gets `tool error: missing or unknown 'SPINE_FILE'` — not a binding, and not
   even a refusal. **The exit criterion is not reached.** This is on `spine_open`'s own
   path, which is the whole point of the gate.

   **Preferred answer, yours to confirm or reject with reasons:** derive the primary
   checkout from the **server script's own location** (`Path(__file__).resolve()`), then
   `git rev-parse --git-common-dir` from there. It needs no new environment variable, no
   ambient cwd read, and does not reintroduce what `:568-592` argues against. **If that
   does not hold, STOP and report** rather than adding a fourth ambient input.

2. **`open_work` returns THREE binding values**, not one
   (`scripts/spine_lifecycle.py:334-340`): `SPINE_FILE`, `SPINE_SESSION`, `SPINE_PARENT`.
   Binding `SPINE` alone leaves `SESSION` empty; `run_engine` then omits `--session-id`
   (`:442`); and `checklist_engine.py:1073` raises `claim requires a non-empty
   --session-id`. **So the bound session cannot drive anything.** Rebind `SESSION` from
   `open_work`'s returned `SPINE_SESSION` too.

**Ruled for this gate:** a rebind is **refused while this process still holds an active
lease** on the current spine. That preserves one-spine-per-process and prevents orphaning a
lease. Implement and test that refusal.

### The pin — read carefully, this was corrected once already

`tests/test_mcp_lifecycle.py:194` bans the identifiers `SPINE`, `SESSION` and `run_engine`
from **`_spine_open`'s own source** (`_find_funcdef(tree, "_spine_open")`). A module-level
binder that `_spine_open` *calls* leaves that assertion **passing, unweakened** — its letter
*and* its stated purpose both survive, because the purpose is that a call meant to open
unrelated work cannot be redirected onto the bound spine, and handing a *new* identity to a
binder after a successful open does not do that.

So:

- **Keep `:194` and its positive control BYTE-IDENTICAL.** Do not soften it into an
  intent-shaped statement. An earlier draft of this plan said "extend the pin", and that
  wording would have weakened a guard in the same motion used to argue against weakening
  guards. It was corrected; do not re-introduce it.
- **ADD a new, strictly stronger assertion:** an AST pin over the **whole module** that the
  set of assignments to `SPINE` **and** to `SESSION` is exactly {module scope, the one named
  binder}, with its own **mutated positive control** proving the pin can fail. That catches
  the real regression — a second, quieter rebind site — which an `_spine_open`-scoped ban
  cannot see.

## Protected intent

A session started with **no** `SPINE_FILE` calls `spine_open`, gets bound, and drives a real
spine end to end **without touching the CLI**. That is the epic's exit criterion. "Bound"
that cannot `claim` is not bound.

## Close criteria

- Unset, empty, missing, non-file and unreadable `SPINE_FILE` all produce refusals from
  every tool, with the server **alive**. Enumerate the tools and **state the count**.
- Unset `SPINE_ENGINE` no longer kills the server at import.
- `spine_open` on an unbound door binds it, and a **mutating** verb (`claim`) then succeeds.
- `_identity_violation` still refuses an argv naming a different spine **after** a rebind.
- All four import-time `SPINE` derivations follow the rebind; the three env overrides
  (`SPINE_CALLLOG`, `SPINE_START_MARKER`, `SPINE_REJECTION_LOG`) still work.
- A rebind while a lease is held is refused.
- `:194` and its positive control are byte-identical; a new module-wide assignment pin
  exists and its own mutated control fails.
- A **committed regression test** fails on the pre-fix tree — an unbound subprocess whose
  refusal **text** is asserted. Not optional: measured, this gate's pytest postcondition
  passes identically on the healthy and the defective tree.
- The full clean-env suite is green.

## Three committed assertions break — budget for all three

Dropping `.mcp.json`'s demo default breaks these. Reconcile each **deliberately**, and say
what you did:

| Site | What it asserts |
|---|---|
| `tests/test_mcp_spine_server.py:588` | the default resolves to a real, loadable spine |
| `tests/test_wire_mcp_interpreter.py:42` | the literal `"${SPINE_FILE:-examples/mcp-interactive-demo/spine.json}"` |
| `tests/test_install_constellation.py:4021` | the same literal |

`test_mcp_spine_server.py:588` is **the guard that caught this class of defect before**.
State its **replacement invariant** — most likely *"if a default is present it must resolve
to a loadable spine"* — so the guard survives with the default gone. Do not simply delete it.

## Allowed scope

- `scripts/mcp_spine_server.py`
- `.mcp.json`
- `tests/test_mcp_*.py`, `tests/test_wire_mcp_interpreter.py`, and a new test file if you
  want one
- `tests/test_install_constellation.py` — **only** the `.mcp.json` literal-string assertion
  at `:4021`
- `examples/mcp-interactive-demo/README.md` — **only** its opening sentence (see below)

## Specific exclusions

- **`_identity_violation`'s SEMANTICS are FENCED** (launch order). It compares against
  `SPINE` at **call time** (`:310`), so it survives a rebind by construction. Changing
  *which* spine is bound is sanctioned; changing *how many* are live, or weakening the
  refusal, is **not** — that floats to the Admiral.
- **Do not add a tool that takes a spine path per call.** The order rules it out; it would
  undo the guard that makes the door safe.
- `scripts/checklist_engine.py`, `scripts/hooks/**`, `scripts/run_crew.py`,
  `scripts/gauge_reader.py` — **lanes B and C, running concurrently.** Read them; never
  modify.
- `scripts/install_constellation.py`'s and
  `skills/commander/templates/COMMANDER_SPINE.template.json`'s **doctrine/prose** — the
  launch order's "door-detection change" is **undefined** and has been floated to the
  Admiral, not invented here. Reconciling `test_install_constellation.py:4021`'s literal
  string is a different thing and **is** in scope.
- `examples/mcp-interactive-demo/spine.json` and `make_demo_spine.py` — g2's, closed.

## Constraints

- `examples/mcp-interactive-demo/README.md`'s opening sentence — "This is the checklist the
  project-scope `.mcp.json` points at" — **becomes false with this change. This gate owns
  correcting it.**
- **Answer what `CALLLOG` / `START_MARKER` / `REJECTIONLOG` ARE when nothing is bound.**
  g1's telemetry guard is scoped to `OSError` and will **not** catch an
  `AttributeError`/`TypeError` on `None`. A naive "recompute from `SPINE.parent`"
  late-binding also silently discards the env overrides, which
  `tests/test_mcp_lifecycle.py:102-103` relies on.
- Validate by launching the server as a **subprocess** with the environment under test.
  `.agent-work/cleanup-a-door/door_probe.py` supports `--unbound`, which genuinely
  **removes** the variable rather than emptying it — both cases matter and they differ.
  Pre-fix baseline: `.agent-work/cleanup-a-door/evidence/pre-fix-probes.txt`.
- **Clear `__pycache__` before every measurement** (#597).
- If you add or rename an entity, run `py -m scripts.code_map build --root .` and commit it.

## Map anchors (inbound)

- **Map entry point: none.** `map/ids.jsonl` is tracked but empty (0 bytes) — no map anchor
  resolves anywhere in this repo. Work from source.
- **Structural:** `mcp_spine_server.py:145-147` (import-time env reads), `:162/:167/:177`
  (SPINE-derived log paths), `:188` (`_resolve_confined` default arg), `:236-363`
  (`_identity_violation` — **FENCED**), `:593` (`_primary_checkout_for_lifecycle`),
  `:622-736` (`_spine_open`/`_spine_close`/`call_lifecycle_tool`);
  `spine_lifecycle.py:334-340`; `checklist_engine.py:1073` (read only); `.mcp.json`;
  `tests/test_mcp_lifecycle.py:137,194`; `tests/test_mcp_spine_server.py:574,588`.
- **Capability:** door identity acquisition — import-time-only → import-time-**or**
  bind-on-open; door refusal surface when unbound.
- **Constraints:** `constraint:identity-is-not-a-per-call-argument`;
  `constraint:one-door-one-spine-per-process`; `constraint:stdout-is-the-protocol-channel`.
- **Decision anchors:**
  - `decision:one-spine-per-process-stands` — bind-on-open changes **when** the binding is
    decided, never **how many** are live; a rebind while a lease is held is refused.
    `@grade: settled/human · leans g3-implement,g3-review`
  - `decision:fail-closed-beats-fail-open` — unbound/empty/missing/unreadable yields a
    refusal; unbound says how to bind, missing names the path.
    `@grade: settled/measured · leans g3-implement`
  - `decision:bind-on-open-over-new-verb` — bind inside `spine_open` rather than add
    `spine_bind`. `@grade: guess · leans g3-implement · settle: attempt the spine_open binding first and report what it costs`
  - Decision pressure: **what is the primary checkout when unbound** (preferred answer
    above); **add a module-wide assignment pin rather than rewrite `:194`**.
- **Evidence:** `claim:603-fails-open` — a probe transcript showing an unbound door
  refusing, then `spine_open` binding it, then `claim` succeeding.

## Deliverable path check

- **Committed** — `scripts/mcp_spine_server.py`, `.mcp.json`, the test files, README.
  `git check-ignore` exits **1** for each (not ignored), verified at dispatch.
- New files are untracked until staged.
- **Local-only** — anything under `.agent-work/`.

## Required evidence

**Load-bearing — prove rigorously:**

1. **The probe transcript that is this gate's whole point:** unbound door **refuses by
   name**, then `spine_open` **binds** it, then **`claim` succeeds**. `claim` succeeding is
   what proves `SESSION` was rebound, not just `SPINE` — a transcript that stops at
   `spine_status` does not demonstrate the exit criterion.
2. **`_identity_violation` still refuses a foreign spine after a rebind.** Test it; do not
   assume it. This is the guard that must not have been weakened.
3. **The new regression test failing pre-fix.** Demonstrate it.
4. **The new module-wide assignment pin's mutated positive control failing.**
5. **All five unbound-class inputs refuse**, with the tool count.

**Confirmatory — spot-check:**

6. Full clean-env suite:
   `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q`
7. The three env overrides still work; `:194` diffs clean.

## Wiring grep

**Required.** Name every new symbol (the binder, the fail-closed check, any helper) and show
a call site outside its own definition and outside any self-test, with **the count**. Zero
external call sites is a stop condition — a binder nothing calls is the exact shipped-inert
failure this gate cannot afford.

## Verification commands

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-a-door
find . -name __pycache__ -type d -not -path "./.git/*" -exec rm -rf {} +
py .agent-work/cleanup-a-door/door_probe.py --unbound
py .agent-work/cleanup-a-door/door_probe.py ""
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
```

## Suggested model tier

`stronger` — a design change to how a long-lived server acquires its identity, with a guard
that must stay intact while it is made reachable.

## Authority

**Already decided, not yours to revisit:** fail-closed over fail-open; one spine per
process; `_identity_violation`'s semantics are fenced; no per-call spine argument; bind
inside `spine_open` rather than a new verb; a rebind while a lease is held is refused; keep
`:194` byte-identical and add a stronger module-wide pin.

**Yours to decide, with the reason recorded:** where the fail-closed check sits; the exact
refusal wording; how the primary checkout is derived when unbound (preferred answer given —
confirm or reject with reasons); how the three broken assertions are reconciled; test
structure.

## Stop conditions

Stop and return if:

- **bind-on-open cannot be reached without weakening `_identity_violation`.** That measured
  finding **IS the deliverable** — the launch order's Honest-Null Clause says so
  explicitly. Report it and stop. **Do not ship a weakened guard.**
- the server-script-location derivation for the primary checkout does not hold and the only
  alternative is a fourth ambient input;
- allowed scope must be exceeded, or a fenced file touched;
- a decision outside the given authority is needed.

## Return format

Return `IMPLEMENTER_RESULT`: completed slice, files changed, test mode satisfied, evidence
produced, assumptions used, stop conditions hit, out-of-scope observations, workflow
feedback.

`Return status` must be one of `complete | partial | blocked | out-of-scope | failed`,
**lowercase** — copied verbatim into the gate's evidence, matched on exact case.

**Delivery.** Write the full `IMPLEMENTER_RESULT` to
`.agent-work/cleanup-a-door/crew-handoffs/g3-implementer-result.md` **before ending your
turn** — that write is the delivery.

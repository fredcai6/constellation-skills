# Candidate C — `per-call-identity`

**Constraint:** `per-call-identity` (issue #559's own filed recommendation). Generalize
`_identity_violation`'s containment so a call may NAME its own spine file, enforced to lie
within a bound **root** rather than equal a bound **file**. Isolation becomes "one tree per
process" instead of "one file per process."

Designed against `scripts/mcp_spine_server.py` in the lane worktree
`.worktrees/567-a-spine-identity`, and measured against the real `.agent-work/` tree on
2026-08-16. All line numbers are that file unless another is named.

**Verdict up front, because the evidence points one way and burying it would be
dishonest:** the mechanism generalizes cleanly — `_resolve_confined` really is the seam, the
"ask argparse, never scan tokens" property really does survive, and the guard change is four
lines. The *root* is what kills it. A root narrow enough to be safe can only be derived from a
bound file, which is the one thing the door does not have in the case this epic exists to fix;
and the only root that both needs no per-dispatch knowledge and serves an unbound door is
`<checkout>/.agent-work`, which is **124 spines wide, 99 of them with no active lease and
therefore, since #609 g2 retired the engine's location guard, subject to no ownership check at
all.** Section 6 is where I say that as an argument rather than as a hedge.

---

## 1. Candidate name and constraint

Candidate C, `per-call-identity`. One constraint, no others: a call may name its own spine,
confined to a bound root.

---

## 2. The design

### 2.1 The bound root — the crux, answered plainly

The root is a **new module global `ROOT`, read from a NEW environment variable
`SPINE_ROOT`**, with one fallback and one refusal:

```python
def _root_from_env() -> Path | None:
    """The containment ROOT: `SPINE_ROOT` when named, else the bound spine's own
    directory, else None. None means no call may name a spine."""
    named = os.environ.get("SPINE_ROOT", "").strip()
    if named:
        return Path(named).resolve()
    return None if SPINE is None else SPINE.parent

ROOT: Path | None = _root_from_env()      # beside SPINE/SESSION at :201-202
```

Constraint 7 asks me to say so plainly, so: **yes, this needs a new environment variable.**
There is no fourth place to get a root from, and I checked all of them:

| Source | Serves an unbound door? | Problem |
|---|---|---|
| `SPINE.parent` (today's containment root, `_resolve_confined` `:371-372`) | **No** | Derived from a bound FILE. No file ⇒ no root ⇒ per-call identity is unavailable in exactly the case the epic is about. |
| New `SPINE_ROOT` env var | Yes | A new variable, and whoever can set it can set `SPINE_FILE`. See §6. |
| `_primary_checkout_for_lifecycle()` (`:857-861`) — the script's own location | Yes | From a linked worktree it resolves to the **PRIMARY checkout**, whose `.agent-work/` does not contain the lane's own spine but does contain `.agent-work/epic-567-door/spine.json` — **the Admiral's live spine.** |
| The ambient cwd | Yes | Forbidden. The module docstring (`:15-28`) and `_git_rev_parse` (`:773-787`) both state that this door's cwd is now a thing that MOVES (`_standing_in_the_bound_spines_worktree`, `:573-627`) and that every location question must be asked against a NAMED directory. |

`ROOT` is asked **fresh per call**, not cached, for the same reason `_unbound_refusal` is
(`:410-414`): `spine_open` can rebind this process mid-life via `_bind_process_to`
(`:878-917`), and a root captured at import would keep confining to the directory of the
spine the door has stopped driving. That is the same import-time-derivation bug `#603`
already fixed four times over (`_resolve_confined`'s docstring, `:362-369`).

**When nothing names it:** `ROOT is None` ⇒ any call carrying a `spine` argument is refused
outright:

```
REFUSED: this call names a spine, but no containment root is bound to this door, so
there is nothing to confine it to. Relaunch this door with SPINE_ROOT set to the tree
this work lives in, or drop the `spine` argument to drive the bound spine.
```

Fail closed, never "confine to the cwd" — that is `_spine_from_env`'s `Path("")` bug
(`:165-170`) one level up.

**Honest note on the AST pin (hard constraint 2).** `tests/test_mcp_lifecycle.py:503-506`
names the module globals that ARE this door's identity and pins the assignment set to
`{module scope, _bind_process_to}` (sweep at `:564-572`). `ROOT` is a third identity global,
so intellectual honesty requires adding it to `IDENTITY_GLOBALS` and making
`_bind_process_to` assign all three. That is a widening of the pin's scope, not an evasion of
it, and a candidate that left `ROOT` outside the pin would be smuggling a fourth identity
value past the check that exists to count them.

### 2.2 The per-call resolution — one new function

```python
def _target_spine(args: dict) -> tuple[Path | None, str | None]:
    """The spine THIS call addresses: the named one when `spine` is given and
    confined to ROOT, else the bound SPINE. Returns (target, refusal)."""
```

It reuses `_resolve_confined(value, join_relative_to=ROOT, bound_dir=ROOT)` (`:322-380`) —
**the existing predicate with a third `bound_dir`**, exactly as `_spine_open` already passes
`wt_root` (`:1020-1023`). That reuse is the filed recommendation's whole claim and the claim
is true: this is not a new containment check, it is the one at `:377` asked about a different
directory. `join_relative_to=ROOT` is a genuine choice and it must be `ROOT`, not `None`: a
relative `spine` resolved against the process cwd would resolve against a cwd that moves
(`:341-350`).

Then the target must be USABLE, which is `_unbound_refusal`'s five-input question (`:393-440`)
asked about a path rather than about the global. So `_unbound_refusal` splits:

- `_unusable_refusal(path: Path | None) -> str | None` — the body of `:420-440`, parameterised.
- `_unbound_refusal()` — `return _unusable_refusal(SPINE)`, unchanged at both existing call
  sites (`main()`'s dispatch `:1723`, `run_engine`'s defense-in-depth `:657`).

One predicate, two callers. Not a second differently-shaped check — the failure
`_identity_violation`'s own docstring records six times over (`:455-463`).

### 2.3 The guard change — four lines in `_identity_violation` (`:443`)

`run_engine` (`:629`) gains a keyword-only `target: Path | None = None` and builds

```python
argv = ["--file", str(target or SPINE), verb, *rest]        # today :664
```

`_identity_violation(argv)` becomes `_identity_violation(argv, target)` and changes exactly
here:

1. `:517` — `if resolved_file != str(SPINE)` becomes `if resolved_file != str(target)`.
   **Still equality, against a path the DOOR computed**, never containment on a caller
   string. This is load-bearing; see §2.6.
2. `:535` — `join_relative_to=SPINE.parent` becomes `join_relative_to=target.parent`, and the
   implicit `bound_dir` default (`:371-372`) must be passed explicitly as `target.parent`,
   because that default reads the global.
3. `:562` — the `--delta` branch's `bound_dir` likewise becomes `target.parent`.
4. `:525-531` — the session check is **UNCHANGED**. See §2.5.

Refusal message for a `spine` outside the root:

```
REFUSED: `spine` names a spine file inside this door's bound root
('<ROOT>'); this call resolves it to '<resolved>', which is outside. A door
drives one tree, and this path is not in it.
```

### 2.4 Which tools become per-call, and which stay bound

| Tool | Line | Per-call? | Why |
|---|---|---|---|
| `spine_status` | `:1436` | **Yes** | Read-only. The single call the "just let `spine_status` work" caller wants. |
| `spine_lease` | `:1439` | **Yes**, and this is the hole | `claim` on a named spine. `force` (`:1444-1447`) is already exposed, so per-call + force = take over a lease held by another door. See §5. |
| `spine_start` | `:1463` | Yes | |
| `spine_advance` | `:1472` | Yes | `from_child` (`:1480-1481`) re-confines to `target.parent`. |
| `spine_evidence` | `:1488` | Yes | Includes `waive --force` (`:1523-1524`). |
| `spine_halt` | `:1542` | Yes | Includes `reopen` — reopening a terminal gate on a named spine. |
| `spine_survey_result` | `:1595` | Yes | |
| `spine_capture` | `:1622` | Yes | |
| `spine_amend` | `:1647` | Yes, with a write | `_write_amend_delta` (`:749-765`) writes `SPINE.parent / mcp_amend_delta_*.json` at `:763`; per-call it writes into the NAMED spine's directory. So per-call `amend` **creates a file** in another work area. |
| `spine_open` | `:968` | **No** | It acts on a spine that does not exist yet (`:969-989`); "name your own spine" is meaningless for a file with no path. Untouched, so hard constraint 4's identifier ban (`tests/test_mcp_lifecycle.py:194`) is untouched. |
| `spine_close` | `:1045` | **No** | Two reasons and both are strong. Its schema declares no field, by design (module docstring `:142-143`), and `close_work` is a **destructive git + filesystem** act whose root comes from `_worktree_root_for_lifecycle` (`:864-875`) reading `SPINE`. A per-call close is `git worktree remove` plus an archive move on a sibling's live work area. |

**The asymmetry that follows is a real cost, not a detail.** A per-call caller can drive a
named spine all the way to terminal and released, and then cannot close it: closing requires
that spine to be BOUND. So candidate C does not close the lifecycle loop the epic is about —
it makes the *middle* of the lifecycle per-call and leaves both ends bound.

Two more things must follow the target or be deliberately left behind:

- **The chdir.** `_standing_in_the_bound_spines_worktree` (`:573-627`) enters `SPINE`'s
  worktree. Under per-call it must enter the NAMED spine's worktree, or the engine call runs
  in the wrong tree. Today that is nearly inert: `#609 g2` retired
  `origin_worktree_refusal` and **the engine now reads no location at all**
  (`scripts/checklist_engine.py:86-93`). But `#315`'s cwd thread re-lands with `#610`
  (`checklist_engine.py:99-105`), and when it does, per-call chdir means *the door walks into
  whatever tree you name so that the engine's location check agrees with you.* Naming it now
  rather than discovering it then.
- **Telemetry.** `_telemetry_path` (`:212-237`) writes beside `SPINE`. It should stay bound —
  one door, one call log. Consequence, stated: a per-call drive's engine calls are logged in a
  work area that is not the one they changed, so the run record and the evidence part company.

### 2.5 The session problem — and I do not need per-call session

The dispatch's premise is that per-call FILE forces per-call SESSION. **It does not, and
recognising that is the best move available to this candidate.** `run_engine` constructs
`--session-id` itself from the global (`:665-666`); no tool declares a session field; so the
refusal at `:526-531` is never reachable with a foreign value and stays exactly as written.
A per-call `claim` records a lease under `SESSION` — an identity this door genuinely holds.
Line 528's sentence ("a claim under any other identity would record a lease nobody holds")
remains literally true.

I considered the two alternatives and both are worse:

- **Caller-supplied session.** The guard at `:526` collapses completely: there is nothing to
  compare against, so the check becomes unwritable and gets deleted. This is `IDENTITY_TRADE.md`
  §3 Option B verbatim — *"A subagent cannot prove it is not its parent. Any string it can
  supply, it can supply its parent's."* It also makes legitimate the exact mutation
  `IDENTITY_TRADE`'s sixth reviewer demonstrated: "a forged `claim` … recording a lease under
  `FORGED-SESSION` with the pin green." Turning a demonstrated attack into a feature is not a
  design, so I reject it.
- **Derived session**, e.g. `SESSION + "#" + <target relative to ROOT>`. Attractive: not
  caller-supplied, deterministic, and the guard stays an equality check the door itself can
  compute (`resolved_session == _derived_session(target)`), so the argparse property survives.
  Rejected anyway: the lease's `session_id` stops being a harness session id, so no key in
  `spine_rail`'s binding map (`scripts/hooks/spine_rail.py:473-490`, keyed
  `session_id` / `session_id#agent_id`) can ever equal it, and a human reading
  `LEASE active: <sid>` (`spine_rail.py:650-659`) sees a synthesised string. It buys
  discrimination between *spines*, which the file argument already gives, and buys nothing
  between *agents*, which is the thing that is actually undiscriminated.

**But keeping the session bound has its own cost, and it is the cost that matters.** The
caller per-call identity exists to serve is an in-session subagent, and those share the
container (`IDENTITY_TRADE.md` §4: *"The harness shares the container, and we put identity in
the container"*). So two subagents naming the same spine present the SAME `SESSION`, the
engine's `require_session` is satisfied for both, and both drive that spine believing they
hold it. The lease does not refuse; it agrees with everyone. Line 528's failure mode inverts
from *a lease nobody holds* to **a lease everybody holds**, which is quieter and therefore
worse. Today this cannot happen through the door, because both subagents are forced onto the
one bound plan; per-call identity is what lets them be on the same plan while thinking they
are on different ones.

### 2.6 Does "ask argparse, never scan tokens" survive? Yes — and here is the trap

It survives, intact, and this is candidate C's genuinely best property. The predicate stays
`checklist_engine.parse_args(argv)` at `:510` and stays an **equality** test at `:517`, just
against `str(target)` instead of `str(SPINE)`. Because `target` is a value the door computed
itself before argv existed, every defeat in the docstring's history still dies here:
`--file=X` as one token, the prefix abbreviations `--fil X` / `--fi=X` (`:456-462`), a second
`--file` ahead of the subcommand (`IDENTITY_TRADE.md`'s fifth reviewer), argv position — all
are the same option to the parser and all resolve to something that is not `target`.

**The trap, named so nobody walks into it:** the obvious implementation is
`if not Path(ns.file).is_relative_to(ROOT)`. That is wrong and it is the *seventh* defeat
waiting to happen. It replaces an equality predicate — satisfiable by exactly one string —
with a containment predicate satisfiable by every path in the tree, and it hands the caller
the choice of which one, *after* the door has already made that choice. Containment belongs
on the door's own resolution of `args["spine"]` (`_target_spine`, before argv is built);
equality belongs on the parser's answer. Two predicates in two places, never one predicate
doing both jobs.

### 2.7 Diff shape

- **Added:** `_root_from_env`, `ROOT`, `_target_spine`, `_unusable_refusal`.
- **Changed:** `_unbound_refusal` (delegates), `_identity_violation` (4 lines, `:517`/`:535`/`:562` + a parameter), `run_engine` (`:629`, one keyword + `:664`), `_write_amend_delta` (`:763`), `_standing_in_the_bound_spines_worktree` (`:616`), `_bind_process_to` (`:913-917`, third global), 9 `inputSchema`s in `TOOLS` (`:1103`), 9 branches in `call_tool` (`:1436-1668`), `.mcp.json` (one line).
- **Deleted:** nothing. See §5.
- **Untouched:** `_rebind_refusal` (`:920`), `_spine_open` (`:968`), `_spine_close` (`:1045`), `call_lifecycle_tool` (`:1067`), all three AST pins' assertions (only `IDENTITY_GLOBALS`' membership widens).

---

## 3. The isolation property, and the reach delta — measured

**Replaces:** "one file per process" with **"one tree per process: this door may address any
readable engine plan whose resolved path lies under `ROOT`, and drives every one of them
under its own single bound session."**

Measured in this worktree on 2026-08-16, `find`/`json.load` over `.agent-work/`:

| | Narrow root (`SPINE.parent`) | Wide root (`<checkout>/.agent-work`) |
|---|---|---|
| Addressable spines/plans | 3 in `.agent-work/commander-315` (`spine.json`, `execute.json`, `g1-review/review.json`); 1 in `.agent-work/epic-567-door/cmdr-a` today | **124** readable spines |
| …with NO active lease (`checklist_engine._active_lease`) | — | **99** |
| …with an active lease, reachable via `spine_lease {action: claim, force: true}` (`:1444-1447`) | — | **25** |
| Legal `--from-child` targets (JSON carrying a `consolidation` key) | 3 | **674** |
| JSON files in the tree at all | ~30 | **5998** |

**What is inside a typical bound tree, concretely.** `.agent-work/commander-315/` holds
`spine.json`, `execute.json`, `g1-review/review.json`, plus `mechanical/{init,understand,plan,context}.json`,
`context/*.json`, `crew-handoffs/`, `FOWLER_PASS.json`, `map-orientation.json`. So the NARROW
root's reach is precisely `execute.json` and `g1-review/review.json` — the Implementer's and
Reviewer's own plans. That is **exactly the capability `IDENTITY_TRADE.md` §2 named as the
price paid**: *"an in-session dispatched crew member cannot drive its own plan through the
door."* Narrow-root candidate C buys back that one sentence and nothing else, and its reach
delta is two files.

**The wide root is a different animal.** `.agent-work/` in this worktree contains 16 top-level
work areas and 132 archive entries. A door with `ROOT=<checkout>/.agent-work` can address the
Admiral's own live spine (`.agent-work/epic-567-door/spine.json` in the primary checkout),
every sibling lane's spine, and 99 spines with no active lease. That last number is the one
that matters: since `#609 g2`, **the engine reads no location at all**
(`checklist_engine.py:86-93`), and that comment says in its own words that on a spine with no
active lease *"this comparison was the sole refusal, and the engine now asserts nothing about
location. Measured from a foreign worktree: `start` and `attach` on a never-claimed spine, and
`start` after a release, went from refused to accepted, WRITING STATE INTO A TREE THE AGENT IS
NOT STANDING IN."* Those 99 spines are the repo's audit trail: released, terminal, archived run
records. Under a wide root they are writable through the door — `start`, `attach`, `reopen`,
`amend`, `advance` — with no lease refusal and no location refusal between the caller and the
file.

And 674 `consolidation`-carrying files become legal `--from-child` targets, because
containment moves from `SPINE.parent` to `target.parent` and the caller picks `target`: name
spine A, then `from_child` anything under A's directory; union that over 124 spines and the
answer is most of the tree. That is precisely the seventh reviewer's finding
(`:481-491`, `IDENTITY_TRADE.md` §2) — *any JSON file carrying a `consolidation` key can close
an artifact postcondition* — re-armed at 674× the radius it was closed at.

### What the guard can still refuse (constraint 5)

Still refused, unchanged: a spine outside `ROOT`; an unresolvable or symlink-escaping path
(`_resolve_confined` `:376-379` resolves before comparing, and a path that cannot be resolved
counts as outside); a non-existent, directory, or unreadable target (`_unusable_refusal`);
any `--file` the parser resolves to something other than the door's own computed `target`,
however spelled or positioned; any `--session-id` other than `SESSION` (`:526`); `from_child`
or `--delta` outside the named spine's own directory; a rebind while holding a lease
(`_rebind_refusal` `:920`); a `spine_open` whose `work_id` escapes `wt_root` (`:1024-1029`);
and every call at all when `ROOT` is None.

Newly reachable: everything in the table above. **"One tree" is strictly more reach than "one
file," and with a static default root it is 124× more.**

---

## 4. Four-axis self-score

- **Depth — 2/5, LOSES.** The seam leaks upward, by construction. All nine pass-through tools
  grow a `spine` argument, so every caller must decide identity on every call — and the
  callers are language models. The door's own docstring promise inverts: `:34-38` says
  "neither is ever exposed as a tool argument, so a model still cannot point the door at a
  different spine or identity mid-conversation." Candidate C's first act is to delete that
  sentence. Complexity that used to live behind the door now lives in every prompt that uses it.
- **Locality — 3/5.** The guard change is genuinely four lines and reuses the existing
  predicate — better than it looks. But the fan-out is real: 9 schemas, 9 `call_tool`
  branches, `_write_amend_delta`, the chdir, a third identity global, and a widened AST pin.
- **Seam placement — 1/5, LOSES BADLY.** The brief's question is where a door with NO bound
  spine acquires one. Candidate C answers a different question — how a door that already has
  a root addresses more than one file inside it — and its root comes from the same launch
  environment `SPINE_FILE` comes from. It is not where the caller wants the boundary, and the
  tests do not want it there either: the pins are all built around a single bound identity.
- **Testability — 5/5, WINS.** Everything is a pure function of `(args, ROOT, SPINE)`.
  No rebind, no lease interaction, `_rebind_refusal` untouched, and `_resolve_confined` is
  already exercised directly with a foreign `bound_dir`
  (`tests/test_mcp_lifecycle.py:268-311`). Each pathway falsifies alone: containment,
  usability, parser-equality, and the two path flags. Nothing assigns `SPINE`/`SESSION`, so the
  choke-point and assignment pins pass without argument.

---

## 5. What it lets us delete

**Nothing.** Said plainly, against hard constraint 6 (`decision:net-deletion`).
`_rebind_refusal` (`:920-957`) is still needed for `spine_open`. `_HOW_TO_BIND` /
`_HOW_TO_REBIND` (`:383-390`) stay. `_bind_process_to` (`:878`) stays and gains a name. The
tool surface grows by nine arguments and the config grows by one variable.

The only deletion candidate C offers is of a **property**, not of code: `IDENTITY_TRADE.md`
§2's isolation sentence and the runtime half of
`tests/test_mcp_identity.py::IdentityBindingPinTests` that enforces it. Deleting the guard
that seven reviews built is a net deletion of the wrong kind, and a candidate whose only
answer to "what do we delete" is "the security property" should be read as answering "nothing."

---

## 6. The strongest argument AGAINST this candidate

**The root has no good source, and the constraint that requires a root is what makes it
unanswerable.**

Lay the three possible roots against the question the brief actually asks:

1. **`SPINE.parent`.** Safe (reach delta: two files in a real work area) and it buys back
   exactly the sentence `IDENTITY_TRADE.md` §2 gave up. But it is derived from a bound FILE, so
   for a door with no bound spine there is no root and no per-call identity. It cannot answer
   the brief's question at all — it is an answer to an adjacent, smaller problem.
2. **`SPINE_ROOT`, set per dispatch to the lane's own work area.** Answers the question, and
   safe. But it requires the launcher to know a per-dispatch path — and a launcher that knows
   the work area's path can set `SPINE_FILE` to `<that>/spine.json` in the same breath. So in
   the case where candidate C is safe, **it buys nothing that setting `SPINE_FILE` does not
   already buy**, while adding nine tool arguments and a variable.
3. **`SPINE_ROOT` with a static default in the committed `.mcp.json`** — the one form that
   needs no per-dispatch knowledge, and therefore candidate C's only genuinely distinct
   contribution. The committed file today is three `${VAR:-default}` lines, one of which is
   already a static relative default (`"SPINE_ENGINE": "${SPINE_ENGINE:-scripts/checklist_engine.py}"`),
   so `"SPINE_ROOT": "${SPINE_ROOT:-.agent-work}"` is exactly the shape a real configuration
   would take. And that root is the 124-spine, 99-unleased, 674-`consolidation` root measured
   in §3.

So the two safe roots do not solve the problem, and the root that solves the problem is the
maximum-reach one. **That is not a tuning problem; it is the shape of the candidate.** A root
narrow enough to be safe requires per-dispatch knowledge, and per-dispatch knowledge is
sufficient to bind a file — which is what Candidates A and B do with one call and no new
variable.

Three supporting blows, each independent:

- **It deletes the door's only distinguishing property.** `IDENTITY_TRADE.md` §3 Option A
  said this in 2026-08 and the sentence has not aged: *"The CLI already IS the per-call-identity
  door — it takes `--file` and `--session-id` on every invocation. Option A does not add a
  capability; it deletes the only property that distinguishes the two doors and leaves two
  copies of the same one."* The engine's own parser confirms it: `--file` is required
  (`checklist_engine.py:3183`) and `--session-id` is available on every mutating verb
  (`:3189`). Candidate C's end state is a CLI that additionally carries a bound session, so its
  leases *look* authoritative while discriminating nobody.
- **It does not cover the actual failure.** Option A's recorded gap applies verbatim: per-call
  paths cover "a subagent naming its own spine" and not "a subagent naming its **parent's**
  spine," which is the failure that matters. Under candidate C the parent's spine is inside the
  root by construction — it is the tree's whole reason for existing — so per-call identity makes
  the uncovered case *easier*, not harder.
- **The composition failure, concretely, and yes it bites.** `IDENTITY_TRADE.md` records the
  composition failure as measured fact, not theory: `spine_advance.from_child` was a
  **declared** argument carrying a path that did not redirect `--file` at all, and it closed
  gate g1 to `complete` on a fabricated `{"verdict":"APPROVE"}` while `_identity_violation`
  stayed silent because `ns.file` still resolved to the bound spine (`:481-491`). Env-binding
  bought isolation; the per-call path defeated it *through* the binding, not around it, and the
  guard was blind because it was asking the right question about the wrong argument. Candidate
  C promotes that exact shape from the evidence path to the identity path. My design does not
  reintroduce the *mechanism* — containment is reused rather than re-shaped, equality against a
  door-computed target survives, and §2.6's trap is named — but it multiplies the *radius*: the
  containment that fix installed was `SPINE.parent`, one work area, and candidate C's only
  viable root makes it the whole `.agent-work` tree. "The composition is what fails" is
  answered here as: the composition fails at a radius, and this candidate is a proposal to
  widen the radius by two orders of magnitude.

---

## 7. What would have to be true for me to be wrong

Falsifiable, in descending order of how cheaply each could be checked:

1. **A per-lane root already exists as something the door can see, without a new variable and
   without leaving the caller's own tree.** My §2.1 table says it does not; that table is the
   load-bearing claim and it is one grep to refute. If, say, the launcher already exports a
   work-area path, root #2 becomes free and candidate C's safe form becomes its viable form.
   Then I am wrong and this candidate is the right answer.
2. **`.agent-work/archive/` moves outside the root.** 99 of the 124 spines and most of the 674
   `consolidation` files are archived. A root that means "live work only" would cut the reach
   delta by roughly an order of magnitude and change the §6 calculus materially. This is a
   cheap experiment and it is the single highest-value thing anyone could do to rescue
   candidate C.
3. **The engine regains an ownership check that binds regardless of lease.** The 99-spine hole
   exists because `#609 g2` retired `origin_worktree_refusal` and left the lease as the sole
   owner check (`checklist_engine.py:86-117`). If ownership were re-established on unleased
   spines, per-call reach would be bounded by leases rather than by the tree, and "one tree"
   would stop being 124 spines wide in practice.
4. **In-session subagents turn out to be separated by the container after all.** §2.5's cost
   and `IDENTITY_TRADE.md` §3 Option B both rest on the measured YES that a Task-tool subagent
   inherits its dispatcher's MCP scope wholesale (§3, citing
   `DC3InheritanceMechanismTests`). If that measurement is now false, a caller-supplied session
   becomes verifiable, `:526` becomes writable again, and the whole trade this candidate sits on
   is reopened in candidate C's favour.
5. **The real caller wants many spines, not one.** I assumed the demand is "let this door drive
   the one spine that already exists." If the measured demand is instead an Admiral driving
   several lane spines from one door, hard constraint 1 (`one-spine-per-process-stands`) is the
   thing to relitigate, and candidate C is the nearest design to that world — its per-call
   argument is the shape you would already have.

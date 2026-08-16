# Cold plan critic — lane A door cleanup

Read: `MISSION_FRAME.md`, `execute.json`, `scripts/mcp_spine_server.py`, `.mcp.json`,
`examples/mcp-interactive-demo/spine.json`, `tests/test_mcp_lifecycle.py`,
`tests/test_mcp_identity.py`, plus source those four cite that the plan depends on
(`scripts/checklist_engine.py`, `scripts/spine_lifecycle.py`,
`tests/test_mcp_spine_server.py`, `tests/test_install_constellation.py`,
`tests/test_wire_mcp_interpreter.py`, `examples/mcp-interactive-demo/README.md`).
`LAUNCH_ORDER.md` and `notes-a.md` were not opened.

---

## Verdict

**Not fit to freeze.** The plan is unusually well-anchored and its structural reading of
the module is accurate, but it does not reach its own exit criterion: the unbound
`spine_open` path dies on a second, unmentioned hard read of `SPINE_FILE`
(`mcp_spine_server.py:593`), and bind-on-open as scoped rebinds one of the three identity
values `open_work` itself hands back. Separately, two of the three gates carry a
mechanical postcondition that I measured passing on the *defective* tree. Four blocking
findings; g3's fix shape is also specified in a way the engine's check semantics do not
support.

---

## Findings

### 1. BLOCKING — `_primary_checkout_for_lifecycle` reads `os.environ["SPINE_FILE"]` too, and it is on the exit criterion's own path
**Lens: intent-fit.**

The plan locates the unset-`SPINE_FILE` problem at exactly one site: "`:146` is
`os.environ["SPINE_FILE"]`, so an unset var raises KeyError AT IMPORT" (`execute.json`,
g2-implement). There is a second one, and it is the first thing `spine_open` does:

```
scripts/mcp_spine_server.py:593
    spine_dir = Path(os.environ["SPINE_FILE"]).resolve().parent
```

`_spine_open` calls it at `:657` inside `try: ... except (OSError, RuntimeError)` —
`KeyError` is not caught there. It propagates to `main()`'s lifecycle branch, which
catches `KeyError` at `:1355` and renders it as `tool error: missing or unknown
'SPINE_FILE'`.

Evidence — imported the door with a valid spine, then removed `SPINE_FILE` from the
environment to simulate the post-fail-closed world g2 part A creates:

```
_primary_checkout_for_lifecycle -> KeyError 'SPINE_FILE'
_spine_open RAISES              -> KeyError 'SPINE_FILE'
```

So after g2 part A lands exactly as written, a session with no `SPINE_FILE` starts the
server, calls `spine_open`, and gets `tool error: missing or unknown 'SPINE_FILE'` — not a
binding, and not even a refusal that names a path or says how to recover. The exit
criterion ("calls `spine_open`, gets bound, drives a real spine end to end") is not
reached; something adjacent is.

This is not a detail the implementer can absorb: `_primary_checkout_for_lifecycle` is
*deliberately* ambient-`SPINE_FILE`-derived and *deliberately* not cwd-derived (its own
docstring, `:568-592`, and the `:194` pin both depend on that), so "where is the primary
checkout when nothing is bound?" is a genuine open design question with no answer in the
frame. Candidate answers all have costs: the process's cwd (reintroduces the ambient read
that `:568-592` argues against), a new `SPINE_ROOT` env var (a fourth ambient input), or a
required `root` argument on `spine_open` (a caller-supplied path into the one function
that must not take identity by argument).

**Change:** add `:593` to g2's structural anchors and its measured-cost list, and surface
"what is the primary checkout when the door is unbound" as a **decision candidate** to the
human at plan approval rather than leaving it to the implementer. Until it is answered,
g2's exit criterion is not implementable as written.

---

### 2. BLOCKING — bind-on-open rebinds `SPINE` but not `SESSION`, and `claim` refuses without one
**Lens: intent-fit.**

`open_work` returns **three** crew-binding values, not one:

```
scripts/spine_lifecycle.py:334-340
    return {
        "SPINE_FILE":    str(spine_path),
        "SPINE_SESSION": f"constellation/{work_id}",
        "SPINE_PARENT":  parent,
        ...
    }
```

The plan's bind-on-open takes `SPINE_FILE` and stops. `SESSION` (`:147`) is never
mentioned in the frame or in `execute.json`. That breaks the second half of the exit
criterion — "drives a real spine end to end":

- `run_engine` appends `--session-id` only when `SESSION` is truthy
  (`mcp_spine_server.py:442`).
- A session started with no `SPINE_FILE` is launched through `.mcp.json`, which sets
  `SPINE_SESSION` to `${SPINE_SESSION:-}` — the empty string. So `SESSION == ""` and no
  `--session-id` is ever passed.
- The first mutating verb on a freshly minted spine is `claim`, and
  `checklist_engine.py:1073` is `raise EngineError("claim requires a non-empty
  --session-id")`.

So the target session binds the new spine and is then refused at `claim`. `close_work`
also refuses while a lease is active (`spine_lifecycle.py:365-368`), so "end to end"
cannot be reached lease-less either.

This is the honest answer to the handoff's "is there a fifth?" question in the sense that
matters: not a fifth *import-time derivation of `SPINE`* (see §"checked and found sound"),
but a second identity **root** that the plan's four-item cost list quietly excludes.

**Change:** either extend bind-on-open to rebind `SESSION` from `open_work`'s returned
`SPINE_SESSION` (and say so in `decision:one-spine-per-process-stands`, since it changes
*which session id* the identity guard enforces, not how many), or state explicitly that
the exit criterion stops short of mutating verbs. Do not leave it undeclared. Related and
also undeclared: if a process rebinds while still holding an active lease on the previous
spine, that lease is orphaned. Decide whether a second bind is refused while a lease is
held.

---

### 3. BLOCKING — the fail-closed world the plan tests is not the world `.mcp.json` produces
**Lens: testability.**

g2 part A says "drop the demo default from `.mcp.json`'s `SPINE_FILE`", and every check
downstream is written for **unset**: g2-review criterion (1) is "with `SPINE_FILE` unset
the server STARTS and every tool returns a refusal". But `.mcp.json`'s form is
`${SPINE_FILE:-<default>}`, and `tests/test_mcp_spine_server.py:601` *pins* that form; the
key cannot simply be removed, because `test_mcp_json_exists_and_is_valid` asserts
`"SPINE_FILE" in entry["env"]` (`:574`). Dropping the default therefore yields
`${SPINE_FILE:-}`, which expands to the **empty string** — the same convention the file
already uses for `SPINE_SESSION`. Empty is not unset, and it does not raise `KeyError`.

Measured, on the current tree, with `SPINE_FILE=""`:

```
$ printf '<initialize>\n<tools/call spine_status>\n' | env SPINE_FILE= SPINE_ENGINE=scripts/checklist_engine.py \
    python3 scripts/mcp_spine_server.py
{"id":2,"result":{"content":[{"type":"text","text":
  "IsADirectoryError: [Errno 21] Is a directory: '/home/.../cleanup-a-door'"}],"isError":true}}
exit=0
```

`Path("").resolve()` is the **cwd**, so the door starts, silently binds itself to a
directory, and answers with a stack-type name. Compare the genuinely-unset probe on the
same tree: `exit=1`, `KeyError: 'SPINE_FILE'`. Two different failure worlds; the plan
describes and tests only the one that production will not take.

**Change:** g2 must treat unset, empty, non-existent, non-file and unreadable as one
"unbound" class, and g2-review's criterion (1) must enumerate all of them, `""` first,
with the `${SPINE_FILE:-}` expansion named as the reason.

---

### 4. BLOCKING — g1 and g2's command postconditions cannot fail
**Lens: testability.**

`g1-integrate.c1` and `g2-integrate.c1` are both `pytest` over MCP test files. I ran
g1-integrate's exact command on the **unfixed** tree:

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python3 -m pytest -q \
    tests/test_mcp_spine_server.py tests/test_mcp_identity.py tests/test_mcp_lifecycle.py \
    tests/test_mcp_door_engine_cwd.py tests/test_mcp_friction_capture.py
89 passed, 10 subtests passed in 5.36s
```

Identical output in the healthy and the defective world. Neither `g1-implement` nor
`g2-implement` requires a **committed regression test**: g1's imperative asks for the fix
and for exit codes captured in a probe, and the frame's claim table records those exit
codes as transcript evidence. A transcript is not a guard. #604 can return the day after
this merges and the suite stays green.

Note the contrast with `g3-implement`, which does it right — "make a real test in the
suite, and make sure it would FAIL on the current file — demonstrate that, do not assert
it." g1 and g2 need the same sentence.

**Change:** add to g1 and g2's imperatives an explicit deliverable: a test that fails on
the pre-fix tree and passes after (for g1, a subprocess whose exit code is asserted with
the log path pointed at an unwritable location; for g2, an unbound subprocess whose
refusal text is asserted). Then `c1`'s pytest command becomes discriminating instead of
decorative.

---

### 5. SERIOUS — g2 part A breaks three committed assertions the plan never budgets for, and one of them is out of g2's own suite
**Lens: testability.**

Dropping the default touches:

| Site | What it asserts | Effect of g2A |
|---|---|---|
| `tests/test_mcp_spine_server.py:588` | the default resolves to a real, loadable spine (`spine_path = ROOT / match.group("default")`, `assertTrue(spine_path.is_file())`) | **fails** — `ROOT / ""` is a directory |
| `tests/test_wire_mcp_interpreter.py:42` | literal `"${SPINE_FILE:-examples/mcp-interactive-demo/spine.json}"` | fails |
| `tests/test_install_constellation.py:4021` | same literal | fails, and this file is **not** in `g2-integrate.c1`'s command |

Two problems. First, `test_install_constellation.py` only runs at `g3-integrate`'s full
suite, so g2 can be integrated green while red — the gate boundary does not hold.
Second, `test_mcp_spine_server.py:588` is the guard whose docstring and the example's own
README record it catching exactly this class of defect before ("the shipped default
resolved to a path that no longer existed... that test is what caught it"). g2 requires
rewriting it, and the plan — which is otherwise scrupulous about not weakening
`test_mcp_lifecycle.py:194` — never says so or says what should replace it. That is the
same hazard, unlabelled.

**Change:** add `tests/test_install_constellation.py` to `g2-integrate.c1`'s command (or
make it the full suite). Name `test_mcp_spine_server.py:588` in g2's structural anchors
and state the replacement invariant — most likely "*if* a default is present it must
resolve to a loadable spine", so the guard survives with the default gone.

---

### 6. SERIOUS — g3's prescribed fix shape is not supported by the engine's command-check semantics
**Lens: intent-fit / testability.**

g3 says "Regenerate it with paths relative to the example directory so it runs where it is
installed." The engine runs `command` checks with **no `cwd`**:

```
scripts/checklist_engine.py:883
    proc = subprocess.run([shell, "-c", command], capture_output=True, text=True)
```

It inherits whatever directory the driving process stands in. Through the MCP door that is
the bound spine's **git toplevel** (`_standing_in_the_bound_spines_worktree` →
`_worktree_root_for_lifecycle`, `mcp_spine_server.py:600-611`) — the repo root, not
`examples/mcp-interactive-demo/`. From the CLI it is the user's cwd. So paths relative to
the example directory resolve correctly from essentially nowhere.

The generator the README names — which does still exist, at
`.agent-work/archive/2026-08-09-epic-418-followon/commander-424/crew-plans/scratch-mcp/make_scratch_spine.py`
— already records the reasoning that g3 is about to reverse without engaging it:

```
Command-check paths are ABSOLUTE (the engine runs `command` checks with no `cwd`).
```

Related, and also unhandled: the demo's checks write into `<arm>/workspace/`. Regenerated
under `examples/`, driving the demo dirties a tracked directory. Nowhere does the plan say
where that workspace lives.

Also, g3-review's criterion — "the regenerated spine actually DRIVES from a directory that
is not the one it was *generated* in" — tests the wrong variable. With relative paths the
generation directory is irrelevant; the load-bearing variable is the **driving** cwd.

**Change:** g3 must first settle *how* a shipped spine addresses its own files at all
(self-locating check text, repo-root-relative paths plus a stated "drive from the repo
root" contract, or a fixture generated at test time into `tmp_path` and never shipped),
and that choice is a decision candidate, not implementer latitude. Restate g3-review's
criterion as "drives from at least two different cwds, one of which is neither the repo
root nor the example directory."

---

### 7. SERIOUS — the pin instruction is ambiguous in the direction of weakening, and there *is* a placement that needs no pin change
**Lens: testability.** (The handoff asked for the strongest case against the plan's answer.)

First, on honesty. `test_mcp_lifecycle.py:194` bans the identifiers `SPINE`/`SESSION`/
`run_engine` from `_spine_open`'s **own source** (`_find_funcdef(tree, "_spine_open")`,
`:196-197`). A module-level rebind helper that `_spine_open` calls leaves that assertion
**passing unchanged and unweakened** — the pin's letter and its spirit both survive,
because the pin's stated purpose (`:200-203`) is that a call meant to open unrelated work
cannot be redirected onto the bound spine, and a helper that assigns a *new* binding after
a successful open does not do that. So the honest description is "add a second, stronger
assertion", not "extend this one".

That matters because the plan's wording — "EXTEND THAT PIN to state the new truth
(`spine_open` may not DRIVE the bound spine; it may hand a new identity to one named
binder)" — reads naturally as **replacing** a hard identifier ban with a softer
intent-shaped statement. If an implementer does that, the plan will have weakened a guard
in the same motion it uses to argue against weakening guards. g2-review's criterion (6)
does not catch it: "the pin was EXTENDED to assert the new truth" is satisfied by a
rewrite.

Second, the strongest case against: **there is a placement that needs no pin change at
all.** `main()`'s `tools/call` branch (`:1350-1356`) is outside both pins — the
lifecycle choke-point pin walks only `call_lifecycle_tool`'s subtree (`:139-141`) and the
identifier ban walks only `_spine_open`'s. Binding there, off the result
`call_lifecycle_tool` returned, requires zero test edits. I would still not take it:
`main()` is the transport loop, and putting an identity mutation there hides the one
event that changes what the whole process speaks for inside JSON-RPC plumbing, where no
pin looks. But the plan should say it considered and rejected it, rather than presenting
"the pin must be extended" as forced.

**Change:** say plainly "keep `:194` and its positive control byte-identical; ADD a new
assertion" — and make the added assertion the one that actually protects the invariant:
an AST pin over the **whole module** that the set of assignments to `SPINE` (and `SESSION`,
per §2) is exactly `{module scope, <the one named binder>}`, with its own mutated positive
control. That is checkable, it is strictly stronger than what exists, and it catches the
real regression (a second, quieter rebind site) that a `_spine_open`-scoped ban cannot see.

---

### 8. SERIOUS — the g1→g2 dependency is half real; the g2→g3 dependency is narrative, and g3-first is safer
**Lens: simplicity / YAGNI.**

*g1 → g2* ("telemetry can no longer kill the process, which is what makes an
unbound/missing-spine probe survivable"). Real for the **missing-directory** probe:
`_log` opens `CALLLOG` under a nonexistent `SPINE.parent`, raising `FileNotFoundError`,
an `OSError`, which g1's guard covers. Not real for the **unbound** probe, which is the
one #603 needs: with no binding there is no `SPINE.parent` to derive `CALLLOG` from at all,
so the failure is an `AttributeError`/`TypeError` on `None`, and g1's guard is explicitly
scoped to "`OSError` ... not bare `Exception`". g2 must separately answer "what are
`CALLLOG`/`START_MARKER`/`REJECTIONLOG` when nothing is bound" — a question the plan's
four-item cost list assumes away by treating late-binding as a pure relocation. (Note too
that all three have env overrides, `:162/:167/:177`; a naive "recompute from `SPINE.parent`"
late-binding silently discards `SPINE_CALLLOG`, which `test_mcp_lifecycle.py:102-103`
relies on.)

*g2 → g3* ("the demo spine is no longer `.mcp.json`'s fallback, so regenerating it can no
longer change what an unbound door answers"). This is a comfort, not a dependency —
regenerating a spine file cannot change the door's code either way. The genuine constraint
is only "never leave the shipped default pointing at a broken file", and **g3-first
satisfies it better**: fix the demo, *then* remove the default. In the plan's order, g2
deletes the demo's only consumer and g3 then spends a full gate regenerating and guarding a
fixture nothing points at — while `examples/mcp-interactive-demo/README.md` still opens
"This is the checklist the project-scope `.mcp.json` points at", which g2 makes false and
no gate corrects.

**Change:** run g3 before g2, or state why not. Either way, put
`examples/mcp-interactive-demo/README.md` in g3's *deliverables*, not just its anchors —
its regeneration command also points at the pre-archive path
`.agent-work/epic-418-followon/.../make_scratch_spine.py`, which no longer exists, and
g3-review's "no absolute or machine-specific path remains under `examples/`" is scoped to
absolute paths and will not catch a dead relative one.

---

### 9. MINOR — `SPINE_ENGINE` is the other import-time hard read, and it still kills a door that is supposed to fail closed
**Lens: intent-fit.** (Directly answers the handoff's fail-closed-reachability question.)

Measured on the current tree:

```
SPINE_FILE unset,  SPINE_ENGINE set   -> exit=1, KeyError: 'SPINE_FILE'
SPINE_FILE set,    SPINE_ENGINE unset -> exit=1, KeyError: 'SPINE_ENGINE'
```

g2 makes only the first optional. A session that has no `SPINE_FILE` because it is not
using this repo's `.mcp.json` very likely has no `SPINE_ENGINE` either, and then the door
dies at `:145` before any refusal is reachable — `Connection closed`, the same illegible
failure the plan correctly names as #604's signature.

The rest of the import block is fine: `sys.path.insert` cannot fail, and `import
checklist_engine` survives a wrong `SPINE_ENGINE` because Python already puts the server's
own `scripts/` directory on `sys.path[0]` (verified — launching from `/tmp` with a
bogus relative `SPINE_ENGINE` still starts cleanly, `exit=0`). So `:145` is the only
remaining import-time death, and it is one line.

**Change:** make `ENGINE` fail closed in the same motion as `SPINE`, or state explicitly
that a missing `SPINE_ENGINE` is out of scope and why.

---

### 10. MINOR — "a refusal naming the path" is unsatisfiable in the unbound case
**Lens: testability.** `decision:fail-closed-beats-fail-open` (frame) and g2-review's
criteria (1) and (2) both require the refusal to "name the path". When `SPINE_FILE` is
unset there is no path to name. A reviewer applying the criterion literally either blocks a
correct implementation or accepts a fabricated path. **Change:** split it — unbound
refusals say "no spine is bound; call `spine_open` (or set `SPINE_FILE`)"; missing/
unreadable refusals name the path *and* say how to rebind.

---

## What I checked and found sound

- **The four-derivation count is correct.** I enumerated it myself with an AST pass over
  the whole module — every module-level statement and every default argument evaluated at
  import that reads `SPINE`:

  ```
  L162  CALLLOG      = ... str(SPINE.parent / "mcp_calls.jsonl")
  L167  START_MARKER = ... str(SPINE.parent / "mcp_server_started")
  L177  REJECTIONLOG = ... str(SPINE.parent / "mcp_rejections.jsonl")
  L188  _resolve_confined(..., bound_dir: Path = SPINE.parent)   # default arg
  ```

  **My count: 4.** There is no fifth import-time derivation of `SPINE`; the other 20-odd
  `SPINE` references (`:310, :313, :328, :332, :345, :359, :441, :534, :611, :700`) are all
  inside function bodies and follow a rebind for free. The `:188` default argument is
  correctly identified as the subtlest. The two genuine omissions are elsewhere and are
  findings §1 (`:593`, a runtime `os.environ` read that does *not* follow a rebind and is
  fatal when unbound) and §2 (`SESSION`, a second identity root).
- **`_identity_violation` survives a rebind by construction.** It compares against `SPINE`
  at call time (`:310`), so it refuses a foreign spine under the new binding without
  modification — and g2-review criterion (4) correctly insists on testing rather than
  assuming that. The fence holds.
- **The telemetry-write inventory is complete and g1's review instruction is answerable.**
  Four filesystem writes exist in the module: `:181` and `:184` (both in `_log`,
  unguarded — g1's target), `:492` (`_log_rejection`, already guarded), `:535`
  (`_write_amend_delta`, guarded at its call site, `:1289-1294`). `_log_rejection` is
  indeed the right shape to reuse, and `OSError` is the right width for it.
- **The `#604` mechanism is correctly diagnosed.** `run_engine` calls `_log(rec)` at `:461`
  outside its own `try` (`:445-458`), and `main()` catches only `KeyError` (`:1355`,
  `:1360`), so an `OSError` from the log write unwinds the process. Accurate.
- **`stderr` is safe.** `main()` writes the protocol to `sys.stdout` only (`:1367`,
  `:1375`); `_log_rejection` already uses `sys.stderr` for the same purpose.
- **The six absolute paths in the demo spine are real and correctly located** — lines 20,
  28, 78, 86, 109, 117, all under
  `/home/tommy/projects/constellation-skills-wt/f-424`.
- **`py` resolves** (`/home/tommy/.local/bin/py`), so the postcondition commands are not
  broken on their interpreter.
- **Gate granularity is otherwise right.** Three gates for three issues, each with a review
  and an integrate, is not over-split; the `implement → review → integrate` triad carries
  its weight. My objection in §8 is to the asserted *ordering*, not the split.
- **The anchors blocks are genuinely cut from the frame** and the confidence flag about the
  empty `map/ids.jsonl` is carried into the gates rather than dropped.

## What I did NOT check

- `LAUNCH_ORDER.md` and `notes-a.md` — excluded by the handoff.
- The full test suite. I ran only `g1-integrate.c1`'s five MCP files (89 passed). I did not
  run `g2-integrate.c1`'s seven, `g3-integrate.c1`'s full sweep, or anything on Windows.
- `_identity_violation`'s internal logic (`:236-363`) — fenced, and out of scope per the
  handoff. I verified only that a rebind reaches it at call time.
- Whether `map/ids.jsonl` being empty is correctly discharged, the c6 waiver, and anything
  about `map-orientation.json`'s hash pins. Not read.
- Publication, merge strategy, `install_constellation.py`'s undefined "door-detection
  change", and the deferred items under the frame's "Out of scope".
- I did not implement or test a bind-on-open prototype. Findings §1 and §2 are established
  from the existing source and from a simulated unbound call
  (`_primary_checkout_for_lifecycle` with `SPINE_FILE` removed from the environment), not
  from a candidate patch.
- `spine_lifecycle.close_work`'s behaviour beyond its refusal-while-leased contract, and
  whether a lease-less spine can reach a terminal close — relevant to §2's severity but not
  chased.
- The `examples/mcp-interactive-demo/README.md` claim that project-scope `.mcp.json` is not
  picked up by a live session. Taken as given; not re-measured.

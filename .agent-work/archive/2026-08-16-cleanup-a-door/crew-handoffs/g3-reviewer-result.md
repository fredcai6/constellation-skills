# Review Result

## Assigned Gate
`g3` — issue #603, the door cannot be bound by the session that needs it, and answers about a
demo spine when unbound. Commit `4e1f22cb`.

## Result
`BLOCK`

Two findings. Neither touches the door's behaviour; both are one-command or one-line fixes.
The gate's actual subject matter — fail-closed, bind-on-open, and the fenced guard — is sound,
and I could not break it.

Survey driven through the engine at `.agent-work/cleanup-a-door/g3-review/review.json`
(session `constellation/cleanup-a-door/g3/reviewer/attempt-1`): 7 items, 5 pass, 2 fail,
consolidated `BLOCK`. My own probes are at `.agent-work/cleanup-a-door/g3-review/*.py`.

---

## Handoff compliance

Both halves landed. Every behavioural close criterion reproduced against **subprocess doors I
launched myself**, never this session's door.

**Criterion 1 — five unbound-class inputs refuse; tool count stated.** My sweep asks the door via
`tools/list` what it declares — **11 tools** — then calls **all 11** with required arguments
synthesized from each tool's own `inputSchema`, so the list is the door's answer, not a
hand-maintained one (`CREW_CONTEXT.md`: *define a guard by its consumer's behaviour*). Across
**six** inputs — **empty first**, then unset, whitespace, missing path, a directory, `chmod 000` —
every case gave **11/11 answered, 10 refused, server EXIT 0, stderr empty**. The 11th is
`spine_open`; I called it with a deliberately missing required argument so it could mint nothing,
and it answered `missing required argument(s): work_id, spec` — proving it passed the unbound gate
rather than being refused by it.

**Criterion 2 — no fabricated path.** For unset, empty and whitespace the refusal names no path at
all (`REFUSED: no spine is bound to this door…`); for missing, directory and unreadable it names
the path and the reason (`no file exists at that path`, `that path is a directory, not a spine
file`, `that file cannot be read (PermissionError)`). Machine-checked across all six cases:
fabricated-path refusals **= 0**.

**Criterion 3 — the exit criterion, one process, no CLI.** With `SPINE_FILE`, `SPINE_SESSION` and
`SPINE_ENGINE` all absent:

```
--- call 1: spine_status -- UNBOUND
    isError: True
    REFUSED: no spine is bound to this door, so there is nothing for this tool to act on.
    Call `spine_open` to mint a spine and bind this process to it, or relaunch this door
    with SPINE_FILE set to an existing spine file.

--- call 2: spine_open -- mints AND binds
    isError: False
    {"SPINE_FILE": ".../.worktrees/g3-reviewer-exit/.agent-work/g3-reviewer-exit/spine.json",
     "SPINE_SESSION": "constellation/g3-reviewer-exit", "SPINE_PARENT": "unknown",
     "branch": "g3-reviewer-exit", "worktree": ".../.worktrees/g3-reviewer-exit"}

--- call 3: spine_lease claim -- THE proof SESSION was rebound
    isError: False
    claimed lease constellation/g3-reviewer-exit -> active

--- call 5: spine_status
    isError: False
    LEASE active: constellation/g3-reviewer-exit (by reviewer, ...)

server exit code: 0
server stderr: (none)
```

`claim` is the load-bearing call and it is the one I got. (Call 4, `spine_start m1`, returned
`no such item 'm1'` — my throwaway spec's task shape, not a door defect; call 5 confirms the door
is genuinely driving the new spine.) Staged in a throwaway git repo and torn down; I then verified
the **real** checkout has neither the branch nor the worktree, and `git worktree list` shows only
the three legitimate ones.

**Criteria 4, 5, 6, 8, 10, 12** — see *Reconciliation check* below; all satisfied.

**Criterion 7 — `:194` byte-identical.** `git diff a69bbac4..HEAD -- tests/test_mcp_lifecycle.py |
grep "^-"` → **0 removed lines**, so nothing pre-existing changed. Stronger, by AST: the functions
at old `:137` and old `:194` are **byte-identical** at HEAD and at the *same line numbers*; no
pre-existing name was removed. The new `OneBinderPinTests` exists and its mutated control is real —
see *Reconciliation check*.

**Criterion 9 — the regression test genuinely fails pre-fix.** I swapped in `408e6d26`'s server and
ran HEAD's `tests/test_mcp_door_unbound.py`: **12 failed**, 0 passed. (The result document claims
9; the truth is stronger than claimed.) Restored the server, verified byte-identical with `cmp` and
a clean `git status`, re-ran: **12 passed**.

**Criterion 11 — README opening sentence.** Fixed. It now says `.mcp.json` *no longer* defaults to
the demo and that an unbound door refuses. But the same file has a stranded reference 60 lines
down — see *Code/doc quality*.

**Criterion 13 — full clean-env suite green. NOT MET. This is the blocker.**

**Stop conditions:** none fired. The diff is exactly the nine named files; no fenced file was
touched; `_identity_violation`'s semantics did not change.

## Scope drift

None. `git show --name-only 4e1f22cb` lists **exactly the nine files** the handoff named — no tenth.

Fenced and excluded paths are all absent from the commit: `scripts/checklist_engine.py`,
`scripts/hooks/**`, `scripts/run_crew.py`, `scripts/gauge_reader.py` (lanes B and C untouched);
`scripts/install_constellation.py` and `COMMANDER_SPINE.template.json` (the floated door-detection
doctrine change is deliberately not here, and per the handoff I did not block for it);
`examples/mcp-interactive-demo/spine.json` and `make_demo_spine.py` (g2's, closed).

`map/` "rebuilt" checked rather than assumed: `.gitignore:73` ignores `map/*`, only two map files
are tracked, and all ten new symbols do have generated pages on disk — so `map/INDEX.md` being the
sole map file in the commit is correct, not a partial rebuild. (Its *contents* are the blocker,
which is a different problem.)

## Evidence verdict

**Fails on one claim; every other claim reproduced, several stronger than stated.**

### The blocker: the suite is not green, and this commit made it red

Measured at HEAD, `__pycache__` cleared, exactly the handoff's command:

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
1 failed, 3092 passed, 6 skipped, 1153 subtests passed in 126.04s

FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
AssertionError: ...ts: 84 modules, 4743 entities... != ...ts: 83 modules, 4710 entities...
: map/INDEX.md is stale: rerun `python -m scripts.code_map build --root .` and commit the result
```

The implementer's claim is `3093 passed, 6 skipped, 0 failed`. **It does not reproduce.**

**I ruled myself out first.** The failure is byte-identical with my five probe scripts moved out of
the tree, and `scripts/code_map/discovery.py:16` excludes `.agent-work/` from the mappable corpus
outright.

**Attribution — and I nearly got this wrong.** My first attempt cloned the repo to a temp directory
and reported the test red at *every* revision including `origin/main`. That was an artifact:
`code_map` titles the index from the **directory name**, so a clone named anything other than
`constellation-skills` fails for a bogus reason. Re-run in a correctly-named clone, one revision at
a time:

| revision | | result |
|---|---|---|
| `d7b911a7` | `origin/main` | PASS |
| `a69bbac4` | gate base | PASS |
| `0060dc08` | g1 #604 | **FAIL** |
| `6856953d` | g1 closed | **FAIL** |
| `4f593b32` | g2 #605 | PASS (g2's rebuild incidentally repaired g1's) |
| `408e6d26` | g3's parent | PASS |
| `4e1f22cb` | **this commit** | **FAIL** |

The parent is green; this commit turns it red.

**Mechanism, proven not guessed.** `code_map` enumerates via `git ls-files -- '*.py'` — **tracked
files only**. The implementer's own suite evidence is stamped `07:19:27`; the commit is `07:27:11`.
The suite was run **eight minutes before the commit**, while `tests/test_mcp_door_unbound.py` was
still untracked — so the fresh build counted 83 test modules and matched the `INDEX.md` they had
just rebuilt. Committing the file made it tracked, and the same guard went red. The map *was*
rebuilt (the commit moves `scripts.mcp_spine_server` 21 → 30 entities); it was rebuilt before its
own new test file was staged.

**Remedy, verified.** At `4e1f22cb` in a clean clone, `py -m scripts.code_map build --root .`
changes `map/INDEX.md` by 3 insertions / 2 deletions, and both `MapTreeFreshness` tests pass. One
command plus a commit. Review only, so I did not apply it.

### Everything else reproduced

- unbound and empty refusals, exit 0, no fabricated path — six inputs, reproduced;
- bind-on-open through to a successful `claim` — reproduced in one process;
- the regression test red pre-fix — reproduced, **12** red where 9 was claimed;
- `:194` pure addition — reproduced, and strengthened to byte-identity;
- `IdentityGuardSurvivesARebindTests` — 17 passed;
- the three env overrides, the lease-held refusal, unset `SPINE_ENGINE` — reproduced.

Test mode is satisfied: red→green demonstrated for the regression test, and the pins carry their
own mutated positive controls.

## Code/doc quality

**One inherited rule violated, three times:** `global-everyone.md`'s *enumerate the blast radius of
your own change — by command, never by memory*. This commit renamed or deleted three identifiers
and left three artifacts naming them. All documentation, no behaviour, all one-line fixes.

1. **`scripts/mcp_spine_server.py:685`** — `_log_rejection`'s docstring still opens *"Append ONE
   record for a door-own rejection to `REJECTIONLOG`"*. This same commit deleted `REJECTIONLOG`; I
   confirmed by AST that none of `REJECTIONLOG`, `CALLLOG` or `START_MARKER` exists as an
   identifier at HEAD. The replacement is `_rejectionlog()`. This propagates:
   `map/scripts.mcp_spine_server/_log_rejection.md:8` and that package's `INDEX.md:171` are
   generated from the docstring and carry the dead name too.
2. **`scripts/mcp_spine_server.py:962-963`** — `_spine_open`'s docstring says the repo root *"comes
   from `_primary_checkout_for_lifecycle` (ambient `SPINE_FILE`, re-read fresh)"*. That is exactly
   what this commit **stopped** doing: the function now reads the `SPINE` global with a
   `Path(__file__)` fallback and no `os.environ` read at all.
3. **`examples/mcp-interactive-demo/README.md:69`** — cites
   `test_mcp_json_referenced_spine_file_exists_and_loads`, which this same commit renamed to
   `test_mcp_json_spine_file_is_overridable_and_any_default_loads`. A repo-wide grep finds the old
   name in exactly **one** place: this line. The README's *opening paragraph*, which the handoff
   asked for, is correctly fixed — the miss is 60 lines further down in the same file.

This lands squarely under `CREW_CONTEXT.md`'s own *"assert against behaviour, never against text
that describes it — docstrings are hand-authored and none is checked against what runs"*. In a
module where prose carries this much of the design, drifting prose is a defect in the design
record.

**Rules that pass:** `__pycache__` cleared before every measurement (#597); every behavioural claim
validated against a subprocess I launched; guards demonstrated able to fail rather than assumed;
fail-visibly with no hidden fallback; `encoding='utf-8'` on every new write (`newline='\n'` on the
rejection log, matching the pre-existing site).

**Fowler pass:** `.agent-work/cleanup-a-door/FOWLER_PASS.json`, `verify_fowler_pass.py` exit 0 —
12 smells, flagged `feature-envy` + `comments-as-deodorant`, overridden `duplicated-code`,
`primitive-obsession`, `speculative-generality` (each with its standard and reason logged). The
speculative-generality override is the interesting one: `BINDS_WITHOUT_A_BOUND_SPINE` is a
one-member hand-maintained list, which `CREW_CONTEXT.md` names as an anti-pattern — but that rule
is justified by the drift being *silent*, and here an omitted tool is visibly **refused**. I logged
the tension rather than dismissing it.

## Map impact verdict

- **Evidence supports claimed change:** Yes, with the one exception above. The capability claim
  (import-time-only → import-time **or** bind-on-open) is backed by a real end-to-end transcript in
  which `claim` succeeds; the new refusal surface is backed by a six-input sweep over the door's
  own declared tool list.
- **Constraints not violated:** Confirmed, and tested rather than assumed.
  `identity-is-not-a-per-call-argument` — no tool gained a spine path.
  `one-door-one-spine-per-process` — a rebind is a **move**: after one, the old spine is refused
  and the new one accepted. `stdout-is-the-protocol-channel` — stdout stayed pure JSON-RPC through
  every refusal; stderr was empty in all six sweeps.
- **Notes match the diff:** Yes. `:145-147` → `_spine_from_env`/`_engine_from_env`;
  `:162/:167/:177` → `_telemetry_path` + three accessors; `:188` default arg → `None`-then-resolve;
  `:593` no longer reads `os.environ`; `_bind_process_to` and `_rebind_refusal` new. Nothing
  overstated, nothing missing.
- **Decision candidates surfaced:** Yes, and honestly. `bind-on-open-over-new-verb` was a `guess`
  with a `settle:` experiment; the implementer ran it, reached it, and recorded the cost —
  correctly promoted to `settled/measured`. `fail-closed-beats-fail-open` is measured.
  `one-spine-per-process-stands` (`settled/human`) was upheld, not unsettled. The rejection of the
  handoff's preferred `Path(__file__)`-outright derivation was surfaced as a departure with a
  measurement behind it, not quietly taken — that is the right handling.
- **Durable context routed:** Yes, but **two of the implementer's four triage candidates are wrong**
  and Commander should not forward them — see *Out-of-scope observations*.

Not a BLOCK on map grounds: the graph-impact claims are accurate.

## Reconciliation check

**Criterion 4 — the fenced guard is intact.** `_identity_violation` is **byte-identical** to
`a69bbac4` (AST-extracted from both revisions and compared); so are `call_tool` and `_tool_error`.
`IdentityGuardSurvivesARebindTests` + `OneBinderPinTests`: **17 passed**. The rebind tests are not
vacuous — `test_the_spine_bound_by_the_rebind_is_accepted_after_it` stops a refuse-everything guard
from satisfying them, and `test_the_old_spine_is_refused_after_a_rebind` proves the move. I also
saw the guard fire **live after a real rebind**: `spine_advance --from-child /etc/passwd` was
refused naming the *new* spine's directory.

**Criterion 5 — four derivations follow the rebind, and there is no fifth.** AST scan of the
module: function default arguments referencing `SPINE`/`SESSION`/`ENGINE` = **zero** (the `:188`
hazard is genuinely gone); module-level statements referencing them = only the two assignments plus
`sys.path.insert`. Then black-box, one door, a real `spine_open` rebind, **no** env overrides:

```
OLD spine dir: mcp_calls.jsonl verbs ['current']            <- pre-rebind only
NEW spine dir: mcp_calls.jsonl verbs ['current','advance'],
               mcp_server_started, mcp_rejections.jsonl
containment refusal names the NEW spine's directory
```

All four followed. **The `CALLLOG`-is-`None` question:** I enumerated every write site in the
module — five. `_log`'s two are both `None`-guarded *before* the `OSError` try; `_log_rejection`
returns early on `None`; `_unbound_refusal:421` only opens a spine already proven non-`None`;
`_write_amend_delta:753` uses `SPINE.parent` but is reachable only through `run_engine`, which sits
behind `_unbound_refusal` **and** behind `main()`'s dispatch gate. No path reaches an unguarded
`None`, so g1's `OSError`-scoped guard is never asked to catch an `AttributeError`.

**The binder's reachability.** Assignments to `SPINE`/`SESSION` anywhere in the module: **exactly**
module scope (`:190`/`:191`) and `_bind_process_to` (`:903`/`:904`). `_bind_process_to` has exactly
one call site — `_spine_open:1028`, after `open_work` succeeds. I then attacked the pin's own
detector with twelve rebind forms:

| caught (8) | missed (4) |
|---|---|
| `Assign`, `AnnAssign`, `AugAssign`, walrus, `for`-target, `with … as`, `except … as`, tuple unpack | `globals()['SPINE']=x`, `setattr(sys.modules[__name__], …)`, `import x as SPINE`, `def SESSION():` |

Non-blocking: the hazard the pin's own docstring names — a convenience helper that quietly sets the
session — **is** caught, and none of the four misses is a plausible accidental arrival. Filed as a
triage candidate.

**Criterion 12 — `:588` is not vacuous.** The predicate is extracted as `_default_spine_problem`
with a positive control feeding it four broken defaults. I proved it can still fail **against the
real config**: mutating `.mcp.json`'s `SPINE_FILE` to `${SPINE_FILE:-examples/no-such-spine.json}`
made `test_mcp_json_spine_file_is_overridable_and_any_default_loads` fail with *"the default names
a spine that is not there"*. Restored byte-identically (`git diff` clean) and green again. A
present-but-unresolvable default is still caught.

**Criteria 6, 8, 10.** All three env overrides win and nothing lands beside the spine. A rebind
under a held lease is refused by name, **before** anything is minted — on a fresh repo with the
lease held, one `spine_open` left **no branch and no worktree** — and releasing the lease is a real
way forward, not just advice: the next `spine_open` succeeded. Unset `SPINE_ENGINE` refuses rather
than dying.

**The two reconciled test files are honest.** `test_mcp_door_engine_cwd` keeps the class's real
claim (the process neither moves nor dies) and *adds* "a refused call must never reach the engine".
The two DC3 controls keep their claim and now assert a positive refusal plus
`assertNotIn("KeyError")`, which pins the old death as an anti-assertion — strictly more evidence,
as claimed.

## Blockers

1. **Close criterion 13 unmet — the full clean-env suite is red at HEAD, and this commit caused
   it.** `tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`.
   Parent `408e6d26` green, `4e1f22cb` red. Fix: rerun `py -m scripts.code_map build --root .` and
   commit `map/INDEX.md` (verified: 3 insertions, 2 deletions, then green).
2. **Three doc references stranded by this commit's own renames** —
   `scripts/mcp_spine_server.py:685` (`REJECTIONLOG`), `scripts/mcp_spine_server.py:962-963`
   (*"ambient `SPINE_FILE`, re-read fresh"*), `examples/mcp-interactive-demo/README.md:69`
   (renamed test). Regenerate the two `map/scripts.mcp_spine_server/` pages after fixing #1.

## Out-of-scope observations

1. **Two of the implementer's four triage candidates do not reproduce — do not forward them.**
   Candidate 1 claims a door launched from another cwd with the relative `SPINE_ENGINE` *"dies at
   import with ImportError"*; measured from `cwd=/tmp`, it answered `spine_status` normally, exit
   0, stderr empty. Candidate 2 claims a bogus `SPINE_ENGINE` *"still kills the server at import"*;
   measured with `SPINE_ENGINE=/tmp/definitely-not-an-engine.py`, it answered normally, exit 0.
   The reason is structural: `ENGINE` is referenced at exactly two places in the file — its own
   assignment (`:189`) and `sys.path.insert(0, ENGINE.parent)` (`:193`) — and `checklist_engine.py`
   sits *beside* the server, whose directory Python already puts on `sys.path`. **The real fix for
   `SPINE_ENGINE` was removing the `KeyError`, which does hold; the named sibling fallback is inert
   in practice.** Replacement candidate filed: *either make `SPINE_ENGINE` do something or retire
   it*.
2. **The map-freshness ordering trap has now fired twice** — g1 (`0060dc08`) and g3 (`4e1f22cb`);
   g2 repaired g1's only incidentally. It is invisible because a rebuild run while the new file is
   still untracked passes its own guard. Worth a pre-commit hook, or doctrine that the map rebuild
   is the **last** step, after staging.
3. **The binder pin's detector misses four rebind forms** (above). Hardening, not a defect.
4. **`_rebind_refusal` depends on `checklist_engine._active_lease`**, a private cross-module
   function. Right trade today; promote to a public engine accessor at a third caller. (The
   implementer flagged this one themselves and was right to.)

All four are recorded as triage candidates `tc1`–`tc4` in the survey.

## What I did NOT check — explicit scoped nulls

- **Windows.** Every measurement is Linux, `uid 1000`, Python 3.12.3. The `chmod 000` case in
  particular does not transfer: it proves `PermissionError` handling *on POSIX*, and says nothing
  about Windows ACL behaviour or about running as root, where the read would succeed.
- **Concurrency.** I never ran two doors against one spine, nor a rebind racing a lease claim from
  another session. `_rebind_refusal` is scoped to a lease *this* session holds; I did not test what
  happens when another session takes the lease between the check and `open_work`.
- **`spine_close` after a rebind.** `_worktree_root_for_lifecycle` dereferences `SPINE.parent` with
  no `None` guard. I established by reading the dispatch that it is unreachable while unbound
  (`spine_close` is not in `BINDS_WITHOUT_A_BOUND_SPINE`, so `main()` refuses first) — but I did
  not exercise a close-after-rebind end to end.
- **The floated door-detection doctrine change** in `install_constellation.py` /
  `COMMANDER_SPINE.template.json` — excluded by the handoff, not examined.
- **`map/ids.jsonl` being empty** — the handoff excluded it; I did not investigate.
- **The demo spine and `make_demo_spine.py`** — g2's, closed, not re-reviewed.

## Workflow Feedback

- **Handoff gaps:** The handoff's *Evidence already produced* section says the new regression test
  showed *"12 failed"* while the implementer result's evidence table says *"9 failed, 0 passed"*
  for the same artifact. I measure 12. Two numbers for one measurement in the two documents I was
  told to reproduce cost me a re-run to decide which was real. Also: criterion 13 is stated as
  *"Full clean-env suite green"* with no baseline — the handoff should say **what the suite's
  count was at the gate base**, because "green" is only checkable against a number, and in this
  case the base (`a69bbac4`) and the parent (`408e6d26`) differed from HEAD by exactly the one test
  that matters.
- **Context rediscovered:** That `scripts/code_map` enumerates through `git ls-files` and titles the
  index from the **directory name**. The second fact cost me a full wrong attribution pass — I had
  a table showing the test red on `origin/main` and was one step from reporting a pre-existing
  defect. Nothing in the anchors, the handoff or `CREW_CONTEXT.md` warns that `code_map` results
  are not reproducible in a differently-named checkout. That belongs in `CREW_CONTEXT.md`'s
  Verification Discipline section.
- **Instructions improvised around:** Two.
  (a) `run_crew.py` dispatched me with the **Commander's** spine bound — `SPINE_FILE` and
  `SPINE_SESSION` pointed at `execute/commander`, whose active gate is the Commander's own
  `execute` imperative, not mine. The reviewer skill says a dispatched crew's spine is bound for it
  and that it must not author a survey when one is bound; `checklist-engine.md:36` says a
  `run_crew.py`-dispatched crew *is* the door's owner. Both are false for this dispatch. I followed
  the g1/g2 precedent, built my own survey at `.agent-work/cleanup-a-door/g3-review/review.json`,
  drove it through the **CLI**, and did not touch the Commander's spine. **The g3 implementer
  reported this exact conflict in its own workflow feedback and it reached me unchanged** — it is
  now a confirmed rhyme across two crews, not a one-off.
  (b) `REVIEW_SURVEY.template.json`'s `r6-fowler` postcondition resolves the Fowler record to
  `.agent-work/<work-id>/FOWLER_PASS.json` — one path shared by every gate in the run. Writing g3's
  pass **overwrote g2's**, which had already overwritten g1's. The record is per-gate but the path
  is per-work-id. It should be `.agent-work/<work-id>/<gate>-review/FOWLER_PASS.json`; g1's copy
  survives at `.agent-work/cleanup-a-door/g1-review/FOWLER_PASS.json` only because someone moved it
  by hand.
- **What would have made this easier:** Have the handoff's *Verification commands* block end with
  the suite's expected pass/fail/skip counts **measured at the gate base**. Criterion 13 was the
  one that broke, and it broke by a delta of exactly one test — invisible against the word "green",
  obvious against a number.

## Return status
`complete`

# Plan critic — cold review of GATE_PLAN.json / LIFECYCLE_CONTRACT.md

**Work id:** `epic-559/c3-lifecycle` · Read: `GATE_PLAN.json`, `MISSION_FRAME.md`, `LIFECYCLE_CONTRACT.md`,
plus `scripts/spine_lifecycle.py` (does not exist yet — nothing to read there), `scripts/mcp_spine_server.py`,
`scripts/generate_spine.py`, `scripts/checklist_engine.py`, `scripts/run_crew.py`,
`scripts/verify_worktree_isolation.py`, `scripts/agent_work_root.py`,
`.agent-work/epic-559/c2-generate-the-spine/DESIGN_NOTE.md`, `tests/test_mcp_identity.py`,
`tests/test_mcp_adoption.py`, `tests/test_crew_launcher.py`, `tests/test_generate_spine.py`, and the live
`.agent-work/` tree on disk. Every command below was actually run in this worktree.

None of the three named documents was missing.

---

## CONFIRMED findings

### 1. `close_work`'s file-exclusion is written as a literal filename, and nothing tests any other filename — the plan's own dominant convention would break it

**Lens: testability, intent-fit.**

LIFECYCLE_CONTRACT.md §4 (lines 160–162):

> Then: `git mv` every top-level entry under `.agent-work/<work-id>/` **except** `spine.json` and
> `spine.json.journal`, each call naming its own paths; then `git mv` the spine and its journal, **last**

`close_work(spine_path, *, root, today)` (line 142) takes `spine_path` as a parameter, but the exclusion
rule is prose-specified against the literal strings `spine.json`/`spine.json.journal`, not against
`Path(spine_path).name`. The contract never states what filename `open_work` writes either — `generate_spine`'s
`--out` is `required` (`scripts/generate_spine.py:851`, `parser.add_argument("--out", required=True, ...)`),
so `open_work` has to choose that path itself, and §3 never names the choice.

This matters because `spine.json` is a minority convention in this very repository. Measured:

```
$ find .agent-work -maxdepth 3 -iname "spine.json" | wc -l
7
$ find .agent-work -maxdepth 3 -iname "execute.json" | wc -l
20
```

`execute.json` is what a Commander actually drives — and this run's own `MISSION_FRAME.md` says so about
*itself*: "this Commander's own spine is `.agent-work/epic-559/c3-lifecycle/execute.json`" (MISSION_FRAME.md
line 93). `checklist_engine.py` and `scripts/mcp_spine_server.py` are both filename-agnostic (`--file`/`SPINE_FILE`
take any path; see the module docstring at `scripts/mcp_spine_server.py:18`). Nothing in the corpus enforces
`spine.json` as *the* name.

None of g2's or g3's close criteria exercise a spine whose basename differs from `spine.json`:
- g2-implement's six CLOSE CRITERIA (GATE_PLAN.json lines 274 ff.) all say "spine.json" or "the spine" and
  every scenario is a spine `open_work` itself created.
- g3's "full stdio JSON-RPC round trip" (GATE_PLAN.json line 493) opens a **throwaway work id through
  `spine_open` itself**, so its spine is guaranteed to be whatever `open_work` names it — the matched-pair
  case, not the general one.

So this ships either way — hardcode the literal string, or correctly derive it from `spine_path.name` — and
no test in the plan can tell the difference, because every test in the plan only ever closes a spine that
`open_work` itself opened. If a future caller ever points the bound door at any spine this epic did not open
(an `execute.json`, an `IMPLEMENTER_PLAN.json`, a `REVIEW_SURVEY.json` — all real, currently-in-use filenames:
`.agent-work/epic-559/c1-spine-lint/IMPLEMENTER_PLAN.json.journal` and siblings exist on disk right now), a
literal-hardcode implementation sweeps the live driving checklist into the "everything else" `git mv` batch
**before** the "spine last" step — the exact failure §4 exists to prevent, undetected by every close criterion
in this plan.

**Confidence:** confirmed as an unstated ambiguity + confirmed absence of any test that would catch a wrong
resolution. Whether it *ships* wrong depends on which way an implementer resolves silent prose — I did not
run anything destructive to settle that, per the stop condition.

---

### 2. `closeout_refusal` is declared "the whole close-ordering predicate, pure" — and also required to "reuse `run_crew.spine_terminal`," which is impure and cannot be called from inside a pure function

**Lens: simplicity/YAGNI, testability.**

Two contract sentences are in direct tension.

§2 (lines 81–83):
> `closeout_refusal(spine: dict, *, archive_exists: bool) -> str | None` — ... **This is the whole
> close-ordering predicate, pure and directly testable**; the impure `close_work` calls it and does nothing
> else about ordering.

§1 (line 43), Adopted from B:
> **Reuse `run_crew.spine_terminal`** rather than re-deriving terminality.

§4 (lines 154–157):
> `close_work` **refuses, doing nothing at all**, unless all of: ... every item in `items` is terminal
> (reuse `run_crew.spine_terminal`) ...

But `run_crew.spine_terminal`'s actual signature is:

```
scripts/run_crew.py:317:def spine_terminal(spine: str | os.PathLike[str], root: Path) -> bool:
```

It takes a **path**, not a dict, and it is impure by its own docstring's admission — it does
`path.read_text(encoding="utf-8")` and catches `OSError`/`json.JSONDecodeError` (`scripts/run_crew.py:345–351`).
`closeout_refusal`'s declared signature is `(spine: dict, *, archive_exists: bool)` — pure, "no Path, no open,
no subprocess" per §2's own module-level rule. There is no way to "reuse `run_crew.spine_terminal`" from
inside a function typed to take only a dict and forbidden from doing I/O — one of these has to give:

- If `closeout_refusal` really stays pure and dict-only, terminality cannot come from `spine_terminal` (which
  needs a path) — the contract's own "never re-derive terminality" instruction is then impossible to honor
  literally, and something re-derives it, contradicting §1.
- If `close_work` calls `spine_terminal` separately (as an impure precondition, before or beside
  `closeout_refusal`), then `closeout_refusal` is **not** "the whole close-ordering predicate" as §2 claims —
  the released-check and archive-exists-check live in the pure function, but the terminal-check lives outside
  it, split across two places instead of one.

Either resolution is fine as an implementation choice, but the contract asserts a single clean pure predicate
that its own reuse instruction cannot deliver — and this is exactly the "does the mechanism work AND is the
value correct" trap: a test can straightforwardly prove `closeout_refusal` returns `None`/a message correctly
for the inputs it's given, and separately prove `spine_terminal` classifies a fixture spine correctly, and
both go green — without ever proving the **wiring** between them matches what the contract calls "the whole
predicate."

**Confidence:** confirmed by direct signature comparison; not run destructively (nothing to run — the module
doesn't exist).

---

### 3. The "trap ... named at plan time" names one test site; two more, with the same shape, are not named

**Lens: testability.**

LIFECYCLE_CONTRACT.md §6 (lines 235–239):

> **The trap, and the wrong fix.** `tests/test_mcp_identity.py:998-999` iterates `module.TOOLS` and indexes
> `TOOL_MINIMAL_ARGS[tool['name']]`. Adding two tools to `TOOLS` breaks it. The required fix is to **scope
> that sweep to the engine tools** (`TOOL_NAMES - LIFECYCLE_TOOL_NAMES`).

Verified — that site exists and would `KeyError`:

```
tests/test_mcp_identity.py:998:            for tool in module.TOOLS:
tests/test_mcp_identity.py:999:                base = self.TOOL_MINIMAL_ARGS[tool["name"]]
```

But two more sites, in two **different test files**, hard-assert the tool *count* and *set* and would also
break, unmentioned by the plan:

```
tests/test_mcp_adoption.py:236:        assert set(DOOR_TOOL_NAMES) == server.TOOL_NAMES, (
tests/test_mcp_adoption.py:246:        assert len(server.TOOL_NAMES) == 9
tests/test_crew_launcher.py:536:        door_tools = {f"mcp__spine__{name}" for name in server.TOOL_NAMES}
tests/test_crew_launcher.py:551:        self.assertEqual(9, len(server.TOOL_NAMES))
```

Both are explicit regression pins against exactly this class of change — their own comments say so:

```
tests/test_mcp_adoption.py:228: """`DOOR_TOOL_NAMES` and `CLI_ONLY_VERBS` used to be hand-typed and froze at 7 tools /
tests/test_crew_launcher.py:510:    froze at 7 while `mcp_spine_server.TOOLS` grew to 9 -- two tools silently
```

`DOOR_TOOL_NAMES` (`tests/test_mcp_adoption.py:110–120`) is hand-typed *in the test file*, so it is not
blocked by the "`docs/agents/*` untouched" constraint — but it, and both hardcoded `9`s, need updating to ship
this plan, and the contract's own §6 claims the trap was "named at plan time so it is not discovered
mid-flight." As written, it names one of at least three coupled sites. The consequence is bounded (the full
suite check at g3-integrate would legitimately go red and force rework — it is not silently missed forever),
but it directly contradicts the completeness claim the contract makes about itself, and will cost a rework
cycle the plan claims to have already prevented.

**Confidence:** confirmed by direct grep and read of all three sites.

---

### 4. `open_work`'s occupied-work-id refusal names a status ("non-abandoned engine_session") that does not exist in the data it reads

**Lens: testability.**

LIFECYCLE_CONTRACT.md §3, step 3 (lines 104–106):

> **Refuse if any spine anywhere for this `work_id` carries an active, non-abandoned `engine_session`** —
> never two crews in one worktree, and never a second crew on a work id another is holding.

`engine_session` is written by `checklist_engine.claim()`/`release()`. I grepped every literal status string
ever assigned to it:

```
scripts/checklist_engine.py:1033:        "status": "active",
scripts/checklist_engine.py:1076:    sess["status"] = "released"
```

Two values, ever: `active`, `released`. There is no `abandoned` status on `engine_session` anywhere in
`checklist_engine.py`. `abandoned` **is** a real field — on a completely different registry, `run_crew.py`'s
`crew-runs.json` dispatch-attempt entries:

```
scripts/run_crew.py:249:def is_abandoned(entry: dict) -> bool:
scripts/run_crew.py:250:    return bool(entry.get("abandoned")) or entry.get("status") == "abandoned"
```

So "non-abandoned engine_session" names a distinction the actual schema it reads cannot express. Read
charitably, the intended check is probably identical in posture to `agent_work_root._active_epic_lease`
(cited by the same sentence) — `status == "active"`, full stop, "no staleness gate" by its own docstring
(`scripts/agent_work_root.py:81`). If that's right, "non-abandoned" is vestigial vocabulary borrowed from the
wrong registry, harmless once dropped. If it isn't right, an implementer has to invent a notion of "abandoned
engine_session" from nothing, and the close criteria never give it an INNOCENT case to pin the answer down —
"a VIOLATING fixture" for the occupied-work-id refusal is specified (GATE_PLAN.json line 61), but no case
distinguishes "active and abandoned" (should NOT block) from "active and not abandoned" (should block), which
is exactly the pair this qualifier exists to distinguish.

**Confidence:** confirmed — the two status literals are exhaustive by grep; the semantic gap is a genuine
reading of the contract's own words, not a guess about intent.

---

### 5. `spec-dispatch-undeclared` is a substring match on free-text `imperative` — the defect it exists to close can still move

**Lens: intent-fit.**

LIFECYCLE_CONTRACT.md §5 (lines 190–193):

> `spec-dispatch-undeclared` — **the hole neither candidate closed.** A gate whose imperative names
> `run_crew.py` but declares no dispatch is refused. Without this, the defect has *moved* rather than gone:
> "a crew forgets to type `--parent`" becomes "an author forgets to declare a dispatch," and the launch
> order's own open question ("has the defect moved rather than gone?") answers itself badly.

The detection mechanism as specified is textual — "a gate whose imperative *names* `run_crew.py`." An
imperative that describes the same dispatch without that literal substring ("hand this to an implementer
crew," "launch the crew via the launcher script") is invisible to this check by construction. So the
handoff's own framing question — "has the defect moved rather than gone?" — is not answered by this fault;
it is narrowed. The old failure ("a crew forgets `--parent`" at dispatch time, invisible for a wave) becomes
a new failure with a smaller but nonzero surface ("an author phrases a dispatch instruction without the
literal string `run_crew.py`," invisible for a wave, in exactly the same way). This is worth stating plainly
because §5 explicitly claims to have closed this hole, and the mechanism described only narrows it.

**Confidence:** confirmed by the contract's own wording; this is a critique of the design as written, not of
code that doesn't exist yet.

---

## SUSPICIONS (lower confidence — flagging, not asserting)

### 6. The contract never states how `call_lifecycle_tool` is reached from the real MCP transport

§6 says `spine_open`/`spine_close` are "Dispatched from `call_lifecycle_tool`, a module-level sibling of
`call_tool`," and separately forbids handling them inside `call_tool`'s body. But `main()`'s actual
`tools/call` handler is unconditional:

```
scripts/mcp_spine_server.py:962:        elif method == "tools/call":
scripts/mcp_spine_server.py:970:            else:
scripts/mcp_spine_server.py:972:                    result = call_tool(nm, call_args)
```

Every call, gated only by `nm not in TOOL_NAMES`, goes to `call_tool`. For a real stdio round trip (g3's own
close criterion, GATE_PLAN.json line 493: "a full stdio JSON-RPC round trip opens a throwaway work id...")
to ever reach `call_lifecycle_tool`, `main()` itself must grow a branch routing lifecycle tool names there.
That's a real, necessary change the contract never names — alongside the one it explicitly forbids. I
verified the AST pin itself (`tests/test_mcp_identity.py:1487-1489`) resolves `call_tool`'s own
`ast.FunctionDef` node and walks only that subtree, so a true sibling function is structurally outside it —
the separation the contract argues for is real and the pin does not accidentally cover it. The gap is
narrower than "the plan is wrong about the pin" (it isn't) and closer to "the plan under-specifies the one
piece of plumbing that makes the separation reachable at all."

**Confidence:** suspicion — plausibly "obvious enough an implementer fills it in correctly," but it is a real
absence, not an inference on my part, and the wrong fix (branching inside `call_tool`) is exactly what the
AST pin would then legitimately catch, so this is self-correcting either way, at the cost of a rework loop.

### 7. The "39 of 41" archive measurement folds in at least one non-work-area directory and a different date format

LIFECYCLE_CONTRACT.md §4 (lines 172–174) says 39 of 41 archive entries are date-prefixed and flat. Measured:

```
$ ls .agent-work/archive/ | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}-' | wc -l
38
$ ls .agent-work/archive/ | grep -vE '^[0-9]{4}-[0-9]{2}-[0-9]{2}-'
20260708-issue-87
curator-reports
issue-310
```

38, not 39, match the exact `YYYY-MM-DD-` form being adopted; `20260708-issue-87` is date-prefixed but in a
different (dash-less) format, and `curator-reports/` holds a single recurring markdown report
(`CURATOR_REPORT-20260724.md`), not an archived work area at all — it arguably shouldn't be in the denominator.
The conclusion (adopt the date-prefixed flat convention) is not disturbed by this, but the specific "39 of 41"
figure overstates precision by conflating a non-comparable directory into the count.

**Confidence:** low-severity, confirmed by `ls`; included because the standard asks for exact-value scrutiny,
not because it changes the decision.

### 8. The interruption test for "spine moves last" needs a mid-sequence failure injection the plan never specifies the shape of

G2's close criterion "an interruption after the other entries move leaves spine.json and its journal still at
the ORIGINAL path" requires a test that fails a real `git mv` partway through a loop of them, without mocking
away the git state the test is trying to prove survived. I found no existing house pattern in this repo for
"fail the Nth of N real subprocess calls" (only `side_effect`-based full mocks, e.g.
`tests/test_checklist_engine.py`). This is achievable, just unspecified, and worth a reviewer's attention
when it ships — is the "interruption" real (kill between two real git operations) or simulated (mock raises
on call N)? The two prove different things and the contract doesn't say which is required.

**Confidence:** low — a plausible authoring gap, not a verified one; I did not attempt to write or run such a
test.

---

## What I checked and did **not** find a problem with

Stated because the handoff asked pointed questions and a clean answer is also information:

- **`call_lifecycle_tool` as a sibling, not routing around the pin.** Verified directly: the AST pin resolves
  `call_tool`'s own `FunctionDef` node and walks only its subtree (`tests/test_mcp_identity.py:1487-1489`), so
  a true sibling function is outside it by construction, not by luck. The separation argued for in §6 is real.
- **The origin round-trip claim.** `validate_spine.py` has no unknown-top-level-key fault — checked directly;
  it only flags a *missing* `items` key and a small list of known-wrong replacement names
  (`scripts/validate_spine.py:95-113`), never an *extra* key. The claim that `origin` would survive silently
  holds.
- **The `not_yet_written` truthiness bug.** Reproduced at both cited lines
  (`scripts/generate_spine.py:424`, `:673`) — `cond.get("not_yet_written")` is a bare truthiness test, so a
  TOML string `"false"` reads as declared. Confirmed real.
- **`record()` enforces `command`-kind postconditions on survey items too**, matching §5's "behaves the same
  on `gated` and `survey`" claim (`scripts/checklist_engine.py:2339-2348`).
- **Sweep stability.** `python scripts/validate_spine.py --sweep --root .` → 23, matching the baseline. Neither
  shipped spec (`specs/implementer.spine.toml`, `specs/reviewer.spine.toml`) declares `not_yet_written` or
  `[[gate.dispatch]]`, so the new faults in g4/g5 have nothing to trip on in the shipped corpus.
- **Gate sequencing.** g1 ships the module unwired ("No door wiring in this gate," GATE_PLAN.json line 59);
  g3 wires it; g4/g5 touch unrelated files (`generate_spine.py`). I found no red window bridged by a waiver —
  each gate is independently closeable without a partially-wired intermediate state.

---

## The single most likely way this plan produces a green run that is wrong

**Finding #1.** Every specified test for `open`/`close` is a matched pair — a spine `open_work` itself
created, closed by the same call chain — so a `close_work` that hardcodes the literal string `"spine.json"`
(matching the contract's own prose exactly) ships, passes every close criterion in g1–g3, passes the full
suite, and is silently wrong the moment it's pointed at any spine this epic didn't open — which, measured on
this very repository, is the *majority* filename convention (`execute.json` outnumbers `spine.json` 20 to 7
under `.agent-work/`, and this run's own driving checklist is one of them). The intent this epic states for
itself — "the closing advance puts the work away" for *any* work, generally — is narrower in the shipped
mechanism than the tests can tell.

---

## Workflow Feedback

**What helped:** the three named lenses plus the four "specific things worth attacking" gave concrete places
to dig instead of a blank canvas, and two of them (the AST-pin sibling question, the `origin`-survives claim)
were fast to falsify-or-confirm because the contract cited exact line numbers I could go read directly —
that citation discipline is worth keeping in every contract, not just this one. The instruction to run real
commands and quote them (rather than trust the contract's own measurements) caught the "39 of 41" imprecision
in under a minute.

**What got in my way:** the contract states function signatures (`closeout_refusal`, `close_work`,
`open_work`) as prose-in-a-code-block without cross-checking them against the *actual* signature of what
they're told to reuse (`run_crew.spine_terminal` takes a path; the contract wants a pure dict-in function to
"reuse" it) — nobody ran that particular cross-check before freezing the contract, and it was a five-minute
grep once I thought to make it. A frozen contract that says "reuse X" would benefit from having actually
opened X's real signature once, the same discipline `MISSION_FRAME.md` itself models for the eight
structural measurements it lists with commands attached — sections 2–6 of `LIFECYCLE_CONTRACT.md` don't
carry that same discipline for the specific functions they name.

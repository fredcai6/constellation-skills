# PLAN_CRITIC — cold read of `commander-f2/execute.json`

Adversarial review. Inputs read: `LAUNCH_ORDER-F2-mcp-adoption.md`, `MISSION_FRAME.md`,
`execute.json`, `PROBLEM_STATEMENT.md`, plus targeted source checks named inline. No
contact with the author.

Findings are ordered by severity, then by gate.

---

## 1. BLOCKING — g4b: "through the door alone" is asserted but never measured

**Lands on:** `g4b-implement` / `g4b-review` / `g4b-integrate`, `evidence[0]`; `g4b-integrate`
`postconditions.c1`.

The claim is *"a real dispatched agent drove a real role spine to done **through the door
alone**"*. The evidence anchor asks for exactly one thing: *"The driving agent's own
`record.jsonl`, scored, showing `reached_done` true."* `reached_done` is one-sided. An agent
that hit a wall on `mcp__spine__spine_advance`, dropped to
`python scripts/checklist_engine.py advance` in a Bash call, and finished, scores
`reached_done: true` and passes this gate. That is the order's own "a measure that cannot
lose."

This is not a hard fix, because the instrument already sees the failure. F's scorer
(`.agent-work/archive/2026-08-09-epic-418-followon/commander-424/evidence/g4-dc5/score_arm.py`)
carries `ENGINE_HINT = "checklist_engine.py"` at line 55 and a whole Bash branch
(lines ~169–238) that counts CLI engine invocations inside a command's text, including inside
shell loops. The plan reuses the scorer and then declines to read the one field that would
make the measure two-sided.

**Change:** add to `g4b-integrate` a postcondition asserting the scored record shows **zero**
CLI engine invocation attempts, and name the scorer field it reads. Add the same to the
evidence anchor so it reaches the implementer handoff.

---

## 2. BLOCKING — g4b: no gate checks that the chosen role spine can even be driven through the door

**Lands on:** `g4b-implement` `preconditions.p1`; `g4a-*` `constraints[3]`.

g4a's own constraint states the fact: *"The 5 CLI-only verbs (skip, reopen, append, amend,
flag-candidate) have NO door tool."* 13 of 18 verbs are covered. g4b then requires *"A REAL
role spine from `skills/*/templates/`, not a scratch fixture"* and requires reaching DONE
through the door alone.

Nothing in the plan checks that the chosen real spine's path to DONE lies entirely inside the
13 covered verbs. If the spine the implementer picks needs `skip` on any branch, or needs
`reopen` after a mid-run correction, the acceptance claim is unreachable **by construction** —
and the plan discovers that at the last gate, after ~10 crew dispatches, with no time left to
change spines. Worse, the likely failure mode is not a clean UNMEASURED: the implementer,
under a done-shaped instruction, uses the CLI for the one uncovered verb and reports success —
which finding 1 above lets through.

**Change:** make the spine choice an explicit `g4b-implement` precondition with a check —
enumerate the verbs the chosen spine's happy path requires and assert each has a door tool,
citing the fallback table in `mcp_spine_server.py`'s docstring (already named as the authority
at g4a). Decide the spine at plan time, not in the handoff.

---

## 3. BLOCKING — g1: the gate's only mechanical check is green before the gate begins, and its evidence anchor pre-decides the trade

**Lands on:** `g1-implement` / `g1-review` / `g1-integrate`, `evidence[1]`; `g1-integrate`
`postconditions.c1`.

Two defects in one gate, both fatal to the order's stated priority ("the risky unknown ...
settle it first").

**(a) The check cannot fail.** `g1-integrate.c1` is `python -m pytest -q`. The suite is green
on `abad896d` before any g1 work exists. The gate's substantive deliverable — the written
trade naming the option taken and the property given up, which the order calls *"a required
deliverable of this gate, not a footnote"* and which
`decision:identity-trade-is-recorded` makes a gate failure to omit — has **no check of any
kind**, not a command, not an artifact check. It is carried entirely by the reviewer's prose
verdict. The one mechanical artifact the gate does require (`evidence[1]`, a test that goes
red if identity moves to a per-call argument) is satisfied by asserting the current state of
`scripts/mcp_spine_server.py:113-115` — verified: `ENGINE`, `SPINE`, `SESSION` are already
module-level `os.environ` reads at exactly those lines. A ~15-line test over unchanged code,
plus a document nobody checks, closes the gate the order says is the risky one.

**(b) The evidence anchor presupposes the outcome.** The order puts three options on the
table, one of which is *moving the spine path to a per-call argument*. `evidence[1]` demands
"a test that would go RED if a later change moved identity to a per-call argument." If the
Commander takes option 2, that anchor is self-contradictory and the gate cannot be closed as
written. The plan has silently pre-committed to option 1 or 3 while presenting the trade as
open (`decision`: *"decision pressure: which of the three options ... Carries no grade until
g1 records it"*).

**Change:** (i) add an artifact postcondition on the trade document itself, and state the
minimum it must contain (option taken, property given up, the case each rejected option would
have covered) so the reviewer verifies a frozen list rather than judging prose; (ii) rewrite
`evidence[1]` as outcome-neutral — "a test that pins whichever identity binding g1 selects and
goes red if a later change silently moves to a different one" — and note in the handoff which
option the protected intent names.

---

## 4. BLOCKING — g2: the central decision has an outcome the Commander cannot execute, and no gate resolves it before a Sonnet implementer is handed it

**Lands on:** `g2-implement` `anchors.decision[4]` ("where a door rejection lands given the
closed Mechanical allowlist"); `g2-*` `constraints[3]`.

Verified against source: the Mechanical allowlist is **hardcoded in code**, not only in docs —
`scripts/apply_episode_delta.py:166-178`, `MECHANICAL_SCALAR_FIELDS` / `MECHANICAL_INT_FIELDS`
(`refusals`, `reopens`, `rework-count`, `failed-commands`), enforced at `:947-955`. Three
consequences the plan does not carry:

- **The file is outside this Commander's ownership.** The order's File Ownership list is
  `scripts/mcp_spine_server.py`, `scripts/install_constellation.py`, `tests/test_mcp_*.py`,
  `.mcp.json`, the role spine templates, and `.agent-work/`. `apply_episode_delta.py`,
  `episode_capture.py` and `docs/EPISODE_STORE.md` are on none of them. Adding a mechanical
  field is therefore an edit to unowned files — and "changing the episode store contract" is
  **also not in the order's float-to-Admiral list**. The plan lists the decision as open
  pressure and provides no branch for the outcome that is out of scope.
- **The order's preferred granularity may be unrepresentable.** The order asks whether to
  record *"a record per rejection"*. Every Mechanical field is a scalar or an int count.
  A per-rejection record cannot live in the Mechanical bin at all, and the Agent-supplied bin
  is barred by `episodes-are-records-not-rules` reasoning about who is speaking. The plan
  never notices that the two options it presents are not symmetrically available.
- **The decision is left to the dispatch.** g1 has an explicit constraint that *"The decision
  itself is the Commander's, stated in the handoff's protected intent."* g2 has no such
  constraint. Its store-contract decision is listed as anchors-level pressure, which means a
  Sonnet implementer arrives at it with no stated answer.

**Change:** settle the landing site in the plan, before g2 dispatches — either (a) fold into
`failed-commands` with the semantics written down, and add the constraint that the Mechanical
allowlist is not to be extended; or (b) declare up front that extending it is an
Admiral float and make g2's first act the float, not the implementation. Add the g1-style
"the decision is the Commander's" constraint to g2.

---

## 5. BLOCKING — g3 misses the interpreter trap at the exact place it lands

**Lands on:** `g3-*` `constraints[1]`, `evidence[0]`, `anchors.constraint`.

Verified against source. `.mcp.json` at repo root reads:

```
"command": "python3",
"args": ["scripts/mcp_spine_server.py"],
```

`installed_path_replacements()` (`scripts/install_constellation.py:488-512`) rewrites exactly
three tokens: `"python <"`, `"<skill-dir>"`, `"<{source_name}-skill-dir>"`. `"python3"` as a
bare `command` value matches none of them, and `.mcp.json` is a project-root dotfile, not a
skill bundle, so the rewrite path would not run over it at all unless g3 deliberately routes
it there.

Meanwhile `INTERPRETER_CANDIDATES = ("py", "python3", "python")` at
`install_constellation.py:375` exists **because** `python3` is not a name you can rely on
across machines, and `resolve_interpreter()` now hard-stops rather than guessing (#539/#540).
The whole point of that work is that a hardcoded interpreter name in an installed artifact is
a defect.

g3's constraints say only *"Do NOT reintroduce a resolved-interpreter FALLBACK"* — a
don't-break-it constraint, not a do-this-here one. g3's evidence anchor is *"an installer test
proving the written `.mcp.json`'s paths resolve against the target root"* — that covers `args`
and says nothing about `command`. **A fully green g3 can ship a fresh install a config that
cannot launch the door**, and the gate's own test would not notice.

**Change:** add to g3's constraints that the installed `.mcp.json`'s `command` must carry the
run's resolved interpreter from the same single `resolve_interpreter()` probe, and extend
`evidence[0]` to "paths **and interpreter** resolve in the target." Add a case for the
`resolve_interpreter()` hard-stop: what the installer does about `.mcp.json` when no
interpreter answers.

---

## 6. BLOCKING — the suite command proves no gate's own work, at any gate

**Lands on:** `g1-integrate`, `g2-integrate`, `g3-integrate`, `g4a-integrate`,
`g4b-integrate`, all `postconditions.c1`.

All five integrate gates carry the identical command postcondition `python -m pytest -q`, and
in every one of them `c1.statement` is a compound: *"<the gate's actual claim>; full suite
green (0 failed)."* Only the second clause is mechanical. The first clause — the entire gate —
is attested prose. Since the suite is green before the run starts, **every one of these five
postconditions is satisfiable by a no-op diff plus an APPROVE verdict.** The order's rule
about measures that cannot lose applies to the plan's own gate checks, not only to g4.

It also cannot discriminate: nothing about `python -m pytest -q` at g3 says anything about the
installer, and the same green at g4a says nothing about the role spine templates. A gate whose
implementer wrote no test at all reads exactly like one that did.

Secondary risks with the same command, worth fixing while you are in there:
- It is the whole 2268-test suite, including the threaded/subprocess MCP identity tests, run
  once per integrate on top of every crew member's own runs (see finding 16).
- pytest exits non-zero on "no tests collected" (exit 5). If the engine re-runs the command
  from a cwd where collection is empty, that is a false red on a green tree.

**Change:** give each integrate gate **two** command postconditions, gate-scoped first: e.g.
`python -m pytest -q tests/test_mcp_identity.py::<the new pinning test>` at g1, the new
installer test node at g3, the new adoption test node at g4a, then the full suite. Name the
node id in the plan so the crew is verifying a frozen target rather than one it invents.

---

## 7. SHOULD-FIX — `e0-context` cannot fail, and omits the isolation proof the order requires

**Lands on:** `e0-context` `postconditions.c1`.

`c1` has `"check": null` — attest-only. It asserts a specific baseline ("2267 passed, 1
skipped, 0 failed") that nothing verifies, in a plan where every later gate's only mechanical
check is that same suite staying green. If the baseline is not what e0 says, five gates
inherit the discrepancy as noise.

Separately, the order requires `python scripts/verify_worktree_isolation.py --here
/home/tommy/projects/constellation-skills-wt/f2-mcp-adoption` to exit 0 **before the first git
operation**, and its output pasted into the return report. It appears in no task in the plan.

**Change:** give `e0-context` two command postconditions — the isolation check and the suite —
and drop the hardcoded pass count from the statement in favour of "0 failed" (the order's own
gate), so a legitimate test addition elsewhere does not read as a baseline violation.

---

## 8. SHOULD-FIX — two of the four stated dependencies are decorative, and they serialize the plan for nothing

**Lands on:** `g3-implement` `preconditions.p1`; `g4a-implement` `preconditions.p1`.

Walking each `preconditions[0].statement`:

| Gate | Stated dep | Real? |
|---|---|---|
| g1 | none (first, deliberately) | correct, and it matches the order |
| g2 | g1 — identity binding decides whether a rejection record can name its run | **real** |
| g3 | g1 — the installed env block is the identity mechanism | **real** |
| g3 | g2 — *"if the capture needs a path or variable"* | **conditional, not a dependency** |
| g4a | g1 — a dispatching role that cannot safely use the door gets a different instruction | **real**, and it is the order's own reason for g1-first |
| g4a | g3 — *"an instruction naming a door a fresh install does not ship is an instruction that cannot be followed"* | **false** |
| g4b | g4a, g2, `remeasure-never-reuse` | **real** |

The g4a→g3 claim is false on its face. The door and `.mcp.json` already exist **in this repo**;
g4a edits **this repo's** role spine templates, which are followed by agents running in this
repo. g3 is about a *fresh install elsewhere*. g4a could run to completion with g3 untouched.

The cost is not cosmetic. Preconditions gate execution: a BLOCK at g3 (the gate touching the
most trap-laden file in the run, per finding 5) now also blocks the doc-only adoption gate that
has nothing to do with it, in a plan that finding 17 argues is already at the edge of its
budget.

**Change:** g3 depends on g1 only; g4a depends on g1 only. Keep the item ordering if you want
g3 to land first for review-load reasons, but do not encode it as a precondition.

---

## 9. SHOULD-FIX — the `skills/_shared/global-*.md` trap is carried to only one of the three gates that can trip over it

**Lands on:** `g1-*` `constraints`; `g3-*` `constraints`.

The order's warning is that a crew member told to edit global doctrine must cite
`skills/_shared/global-*.md`, **not** `skills/<role>/references/global-*.md`, which
`install_constellation.py` regenerates and silently overwrites. The plan carries it as g4a
`constraints[1]` and nowhere else. Two other gates need it:

- **g1.** The order's third identity option is *"accept the composition and forbid the
  in-session case in doctrine."* If the Commander takes it, g1's deliverable is a doctrine
  edit — with no constraint telling the implementer which copy is canonical. The plan
  simultaneously requires g1 to keep `git diff` empty against the engine but says nothing
  about where a doctrine edit lands.
- **g3.** g3 edits the very installer that performs the regeneration. A change to bundling or
  to `installed_path_replacements()` can alter what gets stamped into the per-role copies.
  g3's constraints cover the interpreter, `--wire-hooks`, the tombstone and compact JSON, but
  not the regeneration it owns.

**Change:** add the canonical-source constraint to g1's and g3's constraint lists.

---

## 10. SHOULD-FIX — the two traps that produce false reds never reach the crew

**Lands on:** `g1/g2/g3/g4a` `-implement` and `-review` `constraints`.

`constraints` is what gets copied into `IMPLEMENTER_HANDOFF` / `REVIEWER_HANDOFF`. The
imperatives are Commander-facing.

- **`python3` vs `python` for pytest.** Present only in `e0-context`'s *imperative*. Every one
  of the 10 crew dispatches will run the suite — implementers to verify, reviewers to watch a
  mutation go red. `python3 -m pytest` returns `No module named pytest` and a non-zero exit
  on this host. That is a false red landing in a crew result, which the Commander then has to
  unpick. The order flags this hard enough to put it in the bootstrap floor; the plan leaves
  it out of every crew-facing block.
- **`head`/`tail` exit codes.** Present in the five `-integrate` imperatives (Commander-facing)
  and in g4b's constraints. Absent from g1, g2, g3 and g4a's constraints, i.e. from 8 of the
  10 crew handoffs.

**Change:** add both to the shared constraint block of every gate, not just g4b.

---

## 11. SHOULD-FIX — g4a's confidence flag claims a control the plan does not contain

**Lands on:** `g4a-*` `confidence_flags[0]`; `g4a-integrate` `postconditions`.

The flag reads: *"This is a DOC-ONLY gate. Per commander-core, the invariants are pre-authored
as explicit postconditions here so the crew verifies a frozen chain rather than inventing a
grep-for-marker proxy."*

`g4a-integrate` has exactly two postconditions: `c1` (the compound both-halves statement +
`python -m pytest -q`) and `c2` (verdict APPROVE). **No invariant is enumerated anywhere.** No
file is named as a postcondition, no per-file assertion exists. The flag asserts a protection
the plan does not implement, and a crew member reading it will assume the protection is
elsewhere.

The consequence is the exact proxy the flag forbids. The `MISSION_FRAME` did the hard work —
it enumerates five tiers (3 spine templates + 7 imperative fields + `commander-core.md`;
default-path prose in 6 SKILL bodies; `skills/workbench/references/checklist-engine.md`; 3
authoring templates; 4 deliberately-untouched narrative mentions) — and none of that
inventory made it into the gate as checkable postconditions. Left as is, the implementer
writes `assert "mcp__spine__" in text and "checklist_engine.py" in text` over some set of files
it chooses, which passes an edit that adds one sentence to a header while every literal command
line still names the CLI.

**Change:** pre-author the inventory as explicit postconditions on `g4a-integrate` — the named
files, and for the command-line tier the assertion that the *imperative field itself* names a
door tool. Then the flag is true.

---

## 12. SHOULD-FIX — g3's off-zero count is satisfiable by a comment, and "bundled" has no evidence

**Lands on:** `g3-*` `evidence[1]` and `g3-integrate` `postconditions.c1`.

`evidence[1]` is *"The three-count re-measurement's second count moves off zero."* Per
`PROBLEM_STATEMENT.md`, count 2 is `grep -ciE 'mcp' scripts/install_constellation.py`. A single
comment line reading `# MCP is not wired here yet` moves it off zero. One-sided.

Separately, `c1` claims *"the door script is bundled alongside the engine"* — a real, checkable
property (`SKILL_SCRIPT_BUNDLES` / `expand_script_bundle()`, named in the anchors) — and no
evidence anchor requires a test over the bundle contents. The only test named covers
`.mcp.json`'s paths.

**Change:** replace the grep count with an installer test asserting `mcp_spine_server.py` lands
at `<target>/scripts/mcp_spine_server.py` after a real install into a tmpdir, and keep the
grep count as a reported number, not as a gate.

---

## 13. SHOULD-FIX — g2's claim reaches the episode; g2's evidence does not, and #543 is unpinned

**Lands on:** `g2-integrate` `postconditions.c1`; `g2-*` `evidence`.

`c1` claims the rejections *"reach the run's episode **through `apply_episode_delta.py`**"*.
The three evidence anchors are: a seeded rejection scored by the instrument; the loud-failure
path tested; the coverage boundary stated in prose. **None of them requires an actual episode
file to be written and read back.** All three are satisfiable by unit tests over the server
that stop at the point of invoking the write path. The end-to-end half of the claim — the half
naming `apply_episode_delta.py` — has no anchor.

This matters more than usual because the order names #543 as this run's dependency, precisely
on this path: *"#541's write path runs through `apply_episode_delta.py` and
`verify_episode_captured.py`, which were mutually unsatisfiable for a nested work-id until it
landed."* This run's `work_id` is `epic-418-followon/commander-f2` — **nested**. The fix does
appear to be on the base (`5803ffeb fix(work-id): a work-id may nest`; `episode_capture.py`'s
`manifest_root(base_dir, work_id)` now takes the work-id), but nothing in the plan verifies
that, and `verify_episode_captured.py` is named in no task at any gate.

**Change:** add an evidence anchor requiring a real write and read-back under a **nested**
work-id, verified with `verify_episode_captured.py`, and add `verify_episode_captured.py` to
g2's structural anchors.

---

## 14. SHOULD-FIX — no gate owns the committed `.mcp.json`, which is in the ownership list and is g4b's launch mechanism

**Lands on:** ownership scope; `g3-*` and `g4b-*` anchors.

`.mcp.json` is named in the order's File Ownership. In the plan it appears only as a read-only
noun: g1 anchors it as "the `${VAR}` expansion mechanism", g3 as "the **source** config, whose
args path is relative to THIS repo", g4b as "the committed project-scope config the dispatch
reads at launch." **No gate has editing it as a deliverable.**

That is a real hole, not a bookkeeping one. If g1's trade adds or renames an identity variable,
or g2's capture needs a store-root or episode path in the server's environment, the committed
`.mcp.json` must change — and g4b's entire acceptance mechanism is an external dispatch that
reads that file at session launch. An unowned edit to it, made ad hoc during g2 or g4b, is
unreviewed and lands in the same file the measurement depends on.

**Change:** name the committed `.mcp.json` as an explicit deliverable of whichever gate the
Commander expects to change it (g1 if the trade touches the env block, otherwise g2), with the
compact-JSON surgical-edit constraint attached — that constraint is currently on g3 and g4a but
not on any gate that would edit `.mcp.json` itself.

---

## 15. NOTE — "every occurrence" is not testable as g2 words it

**Lands on:** `g2-*` `evidence[1]`.

*"The loud-failure path is tested: when the capture cannot write, it says so on every
occurrence."* A test that induces **one** failed write and asserts one message satisfies this
sentence while proving nothing about "every." The defect `fail-loud-every-turn` exists to
prevent is exactly once-per-run coalescing.

**Change:** require the test to induce N≥2 failed writes in one process and assert N messages.

---

## 16. NOTE — the dispatch and suite-run arithmetic in this plan

**Lands on:** whole plan.

For the record, since the framing "15 crew dispatches" is circulating: 15 is the **task** count
after `e0-context`. Crew dispatches are 10 — 5 `-implement` plus 5 `-review`; the 5
`-integrate` tasks are Commander-run. That is the correct number to budget against.

Suite runs are the number that hurts. Each implementer runs it to verify; each reviewer runs it
at least twice (baseline plus the mandated mutation, which must be watched going red **and**
back green); each integrate re-runs it in the Commander's own hands and again via `advance`.
That is on the order of 25–30 full runs of a 2268-test suite that includes barrier-released
threaded concurrency tests and subprocess MCP identity tests. Finding 6's gate-scoped-first
postcondition also buys most of this back.

---

## 17. NOTE — scope: the plan is finishable, but only if g1's dispatch pair is collapsed

**Lands on:** `g1-implement`, `g1-review`.

Judged concretely rather than atmospherically: four of the five gates are ordinary
implement/review work. The one that is not is g4b — a live external dispatch measurement that
in F took multiple attempts, four reviewer BLOCKs, and one correction that flipped the verdict
sign. g4b must be reached with budget still in hand, and everything upstream of it is
overhead against that.

**The cut I would make: drop `g1-implement` as a crew dispatch.** The plan's own constraint
says *"The decision itself is the Commander's, stated in the handoff's protected intent. The
gate encodes and evidences it; it does not re-decide it."* So the Commander writes the trade
either way, and what the dispatch adds is a ~15-line test pinning constants at
`mcp_spine_server.py:113-115` that the Commander could write in the same turn as the document.
Keep `g1-review` as a full independent crew dispatch — the mutation experiment against the
pinning test is the part with teeth — and keep `g1-integrate` unchanged. Saving: one dispatch,
roughly three full suite runs, and one handoff-authoring cycle.

**What is lost, stated plainly:** an independent implementer's cold read of the identity code
before the Commander commits to a trade. That is a real loss and it is the reason I would cut
here rather than at g2 or g3. It is partly recoverable because g1-review still reads the same
code adversarially, and fully recoverable if you fix finding 3(a) — a reviewer checking the
trade document against a frozen content list is a stronger control than a second Sonnet
writing the same test.

**Where I would not cut.** Not g4a into g4b: the acceptance run must drive the *edited*
instructions, so folding them together means one crew member authors the instructions and then
measures itself. Not g3 into anything: it is exit criterion 3, it carries the most traps
(finding 5), and it deserves its own mutation review. Not g2: it is a whole issue (#541).

---

## Verdict

This plan is structurally much better than the one the order was written to prevent — the
claim/evidence table in the mission frame is honest, g1 really is first for the reason the
order gives, and most of the named traps are carried down somewhere. But it fails on the
order's own central test in a way that is systemic rather than local: **not one of its six
gate checks can lose.** `e0-context` attests without checking; all five `-integrate` gates
carry the same repo-wide `python -m pytest -q`, which was green before the run began and is
green afterwards regardless of which gate's work landed; the compound `c1` statements put the
actual claim in prose and the mechanical clause on a suite that is indifferent to it. Layered
on that are four specific one-sided measures where the order was most explicit — g4b never
reads the CLI-invocation count its own reused scorer already produces, g4a's confidence flag
promises pre-authored invariants the gate does not contain, g3's off-zero count is satisfiable
by a comment while the interpreter trap lands unguarded on `.mcp.json`'s `"command":
"python3"`, and g2's store-contract decision is left open for a Sonnet implementer to make
against files this Commander does not own. Two decorative preconditions serialize gates that
have no real dependency. None of this requires re-planning the gate order, which is right; it
requires the plan to spend one more pass turning its claims into checks — name the test node
per gate, enumerate g4a's invariants, add the zero-CLI assertion at g4b, settle g2's landing
site before dispatch, and pin the interpreter at g3. Do that and this is a plan that can fail
honestly, which is the only kind that can pass.

# Implementation Result — g3 rework 2 (attempt 3)

> **Read this first.** The assigned string is fixed, committed and green. The improved sweep
> then found a **third** instance of the same invalidated claim, in
> `scripts/mcp_spine_server.py`'s module docstring. It is outside my allowed scope, so I did
> not touch it. **g3's "no invalidated claim survives" property is not yet true tree-wide.**
> See *Out-of-scope observations*.

## Assigned gate

`g3` — issue #603, rework 2 of a cap of 3. One blocker, text only.

## Completed slice

`tests/test_mcp_lifecycle.py:201`'s failure message no longer tells a future debugger that
`spine_open` re-reads `SPINE_FILE`. It now names the two things that actually run:
`SPINE_PARENT`, re-read fresh from the environment, and the repo root from
`_primary_checkout_for_lifecycle`, which contains no `os.environ` access at all.

Commit `176133ac`, one file.

## Scope

**Files changed:**
- `tests/test_mcp_lifecycle.py` — the failure-message string only.

**Specific exclusions touched:** `no`.
- `:194` and its mutated positive control: byte-identical. The `git diff -U0` hunk header is
  `@@ -201,3 +201,5 @@` — the replaced region is lines 201-203 and nothing else.
- `_identity_violation`, `scripts/checklist_engine.py`, `scripts/hooks/**` (including the
  fenced `spine_rail.py`), `scripts/run_crew.py`, `scripts/gauge_reader.py`,
  `scripts/install_constellation.py`, `COMMANDER_SPINE.template.json`: untouched.
- No `map/` rebuild. Correct here: the change lives inside a string literal, so no entity,
  capability or reference moved.

## Behavior changed

`no`. This is text that renders only when an assertion has already failed. No assertion, no
test logic, no control flow. The suite counts are byte-for-byte the pre-rework baseline —
which is the point, not a weak result: any movement would have meant I touched behaviour.

## The change

**Before** (`tests/test_mcp_lifecycle.py:201-203`):

```python
            "purely on ambient, server-launch-time state (SPINE_FILE/SPINE_PARENT re-read "
            "fresh) and never on the identity THIS door happens to be bound to, or a call "
            "meant to open unrelated work could be redirected onto the bound spine",
```

**After** (`:201-205`):

```python
            "purely on server-launch-time state (SPINE_PARENT re-read fresh from the "
            "environment, and the repo root from _primary_checkout_for_lifecycle, which "
            "reads no environment at all) and never on the identity THIS door happens to "
            "be bound to, or a call meant to open unrelated work could be redirected onto "
            "the bound spine",
```

Three decisions inside the wording, all mine per the handoff's *Authority*:

1. `SPINE_FILE` is gone from the claim. Measured: zero reads in `_spine_open`.
2. `re-read fresh` **stays**, now attached to `SPINE_PARENT`, because that read is real
   (`scripts/mcp_spine_server.py:1020`). The phrase was never wrong; its subject was.
3. `ambient,` was dropped. It belonged to the same invalidated claim — the repo root is not
   ambient state, it is the bound checkout or this script's own location. Leaving it would
   have left a smaller version of the defect I was sent to fix.

The surrounding claim is untouched, as instructed: `spine_open` must never act on the bound
identity, *or a call meant to open unrelated work could be redirected onto the bound spine*.

## Ground truth this is measured against

`.agent-work/cleanup-a-door/evidence/g3-rework2-ast-truth.txt` — an AST pass, not a reading:

```
_spine_open  (lines 957-1031)
  os.environ accesses: 1 at lines [1020]
  literal 'SPINE_PARENT' at line 1020
  literal 'SPINE_FILE' at line 1030      <- KEY of open_work's RETURN VALUE, not an env read
  literal 'SPINE_SESSION' at line 1030   <- same
_primary_checkout_for_lifecycle  (lines 786-850)
  os.environ accesses: 0
```

Line 1030 is `_bind_process_to(opened["SPINE_FILE"], opened["SPINE_SESSION"])`. Those two
literals are the only reason a naive grep would report `_spine_open` still "reads
`SPINE_FILE`"; the AST shows they are dict keys on `open_work`'s return value.

## Map Impact

Skipped by the template's own rule — trivial local edit inside a string literal, no
structural, capability, constraint or decision impact. `map/ids.jsonl` is empty for this
gate. One exception worth carrying up:

- **Trust limitations / drift found:** `scripts/mcp_spine_server.py`'s module docstring
  (`:128-130`) is stale against the code it documents. See *Out-of-scope observations*.
- **Triage candidates:** flagged in-engine as `tc1` on my plan
  (`.agent-work/cleanup-a-door/crew-plans/g3-rework2-implementer-plan.json`).

## Test mode

**Required:** `test-after` — inferred, not stated. The handoff has no *Test mode* section,
but "any behaviour change, any test-logic change, any assertion change" is an explicit stop
condition, which forecloses TDD. The existing pin plus its mutated positive control is the
check.

**Satisfied:** `yes` — and stronger than a text check. See evidence 1.

## Evidence

### 1. The corrected message, rendered by the branch that emits it

`docs/agents/CREW_CONTEXT.md` warns that "a grep for a message string is not a test of the
branch that emits it — especially when the message is built by an f-string, where the literal
never appears in the source at all." This message *is* built by an f-string. So I ran the
shipped assertion against a leaky `_spine_open` and read what it actually emitted, rather
than grepping for the literal:

```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py - <<'EOF'
import sys; sys.path.insert(0, '.')
import tests.test_mcp_lifecycle as t
t.SOURCE = ("def _spine_open(args):\n"
            "    if SESSION:\n"
            "        return run_engine('current', file=SPINE)\n")
case = t.SpineOpenNeverBindsIdentityTests(
    'test_spine_open_never_references_spine_session_or_run_engine')
try:
    case.test_spine_open_never_references_spine_session_or_run_engine()
    print("NO FAILURE -- message unreachable")
except AssertionError as exc:
    print(str(exc))
EOF
```

**Result:** `pass`. Full output at
`.agent-work/cleanup-a-door/evidence/g3-rework2-message-rendered.txt`; the emitted text:

```
[] != ['SESSION', 'SPINE', 'run_engine'] : _spine_open's own source now references
['SESSION', 'SPINE', 'run_engine'] -- spine_open must act purely on server-launch-time
state (SPINE_PARENT re-read fresh from the environment, and the repo root from
_primary_checkout_for_lifecycle, which reads no environment at all) and never on the
identity THIS door happens to be bound to, or a call meant to open unrelated work could
be redirected onto the bound spine
```

The pin class itself: `4 passed, 14 deselected` (also run by the engine as `m1-message.c1`,
exit 0).

### 2. The sweep — whitespace-normalized **and** AST-aware, not line-based

**Command:** `py .agent-work/cleanup-a-door/evidence/g3-rework2-sweep.py`
(full transcript with both controls: `.agent-work/cleanup-a-door/evidence/g3-rework2-sweep.txt`)

Two layers over every tracked text file:

- **Layer A** — raw content, whitespace collapsed to single spaces. Sees a phrase broken
  across **lines**.
- **Layer B** — tracked `.py` parsed through the AST, where adjacent string literals are
  *already concatenated by the parser*, plus every comment token. Sees a phrase broken across
  **literals**, which Layer A cannot: the boundary survives normalization as
  `re-read " "fresh`.

Predicate for an invalidated claim: a 200-character window around a trigger
(`re-read fresh|ambient|fresh off|deriv*`) naming **both** `SPINE_FILE` **and** `spine_open`
— because #603's fix is exactly that `spine_open` no longer reads `SPINE_FILE`.

**The loop is asserted** (`CREW_CONTEXT`: a guard that loops must assert what it looped
over). The script dies rather than reporting a clean empty sweep:

```
FILES SCANNED (layer A, whitespace-normalized, all tracked text): 10145
FILES SCANNED (layer B, AST strings + comments, tracked .py):     517
```

**It can fail, demonstrated two ways at the same revision:**

| sweep | at `359d93df` (pre-edit) | on the working tree (post-edit) |
|---|---|---|
| `git grep -F 're-read fresh' HEAD` (rework 1's method) | **0 files, tree-wide** | — |
| this sweep | **LIVE IN-SCOPE HITS: 5** | **LIVE IN-SCOPE HITS: 0** |

That 0-vs-5 at one revision is the whole finding: the phrase is on no single line, so no
line-based tool could ever have seen it.

**COUNT, working tree:** `LIVE IN-SCOPE HITS: 0` (in-scope = this rework's allowed scope,
`tests/test_mcp_lifecycle.py`). Full classification of all 10 invalidated-claim records:

| class | records | what they are |
|---|---|---|
| LIVE IN-SCOPE | **0** | my allowed scope is clean |
| LIVE OUT-OF-SCOPE | 6 | **two** distinct claims, both `scripts/mcp_spine_server.py` — see below |
| HISTORICAL | 4 | `.agent-work/**` run artifacts and `execute.json`, true when written |

Plus **85 near misses** reported separately and deliberately not counted: they name
`SPINE_FILE` without `spine_open` — true statements about the module's own launch-time
binding and about `run_crew` dispatch env, which #603 did not change.

**Honest limit of the predicate.** The fenced claim at `scripts/hooks/spine_rail.py:1081`
does **not** appear in this count, by construction: it quotes the deleted
`SPINE = Path(os.environ["SPINE_FILE"]).resolve()` as the door's existing contract without
naming `spine_open` in the window. It is a different defect class. **My zero is not a
statement about `spine_rail.py`** — the handoff fences it and reports it to the Admiral
separately.

### 3. Full clean-env suite

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-a-door
find . -name __pycache__ -type d -not -path "./.git/*" -exec rm -rf {} +
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
```

**Result:** `pass` — **3093 passed, 6 skipped, 1153 subtests passed in 125.46s. 0 failed.**
Identical to the handoff's pre-rework baseline at `359d93df`. Captured at
`.agent-work/cleanup-a-door/evidence/g3-rework2-full-suite.txt`; also re-run by the engine as
`m3-suite.c1`, exit 0. `__pycache__` cleared first, per #597. Host: Python 3.12.3,
pytest 9.1.1 (`py` — checked, per `CREW_CONTEXT`'s interpreter rule).

### 4. `git diff --stat` — exactly one file

```
$ git diff --stat -- . ':!.agent-work'
 tests/test_mcp_lifecycle.py | 8 +++++---
 1 file changed, 5 insertions(+), 3 deletions(-)
```

`.agent-work/**` is excluded deliberately: it is the checklist engine's own state, written by
engine verbs, not this rework's change — the same shape as the prior rework commit
`359d93df`, which carried only source files. `git check-ignore -v tests/test_mcp_lifecycle.py`
exits 1, so the deliverable path is committable. Captured at
`.agent-work/cleanup-a-door/evidence/g3-rework2-diffstat.txt`.

## TDD evidence, if required

Not required — test-after. The closest analogue is supplied instead: the sweep was shown red
(5 hits) at the pre-edit revision and green (0) after, and the message itself was rendered
from the failing branch rather than asserted by text match.

## Docs/contracts touched

- `tests/test_mcp_lifecycle.py` — one failure-message string. Nothing else.

## Assumptions

- **"in-scope" in the close criteria and the stop condition means my *allowed scope*
  (`tests/test_mcp_lifecycle.py`), not "anywhere live in the repo."** This is the only
  reading under which both are coherent: within my allowed scope the sole permitted change is
  a message string, so an in-scope claim that is *not* a message string is unfixable without
  exceeding scope — hence "stop". Under that reading the `mcp_spine_server.py` docstring
  below is a finding to report, exactly as the handoff already treats the fenced
  `spine_rail.py` claim, and **no stop condition fired**. If the Commander intended the
  broader reading, this run should be read as `partial` and the docstring assigned.

## Stop conditions hit

- `none`. No behaviour or assertion change was required. The sweep's one live finding is
  outside my allowed scope, not inside it — see the assumption above, which is the one call I
  had to make.

## Out-of-scope observations

**1. A THIRD instance of the invalidated claim — `scripts/mcp_spine_server.py:128-130`,
the module docstring.** Flagged in-engine as `tc1`.

```
`spine_open` never references `SPINE`, `SESSION` or `run_engine` (checked, not merely
claimed -- see `tests/test_mcp_lifecycle.py`), deriving the primary checkout it opens
work from fresh off `SPINE_FILE` (ambient, server-launch-time state) rather than the
module's own `SPINE` binding
```

Both halves are false at HEAD:

- *"fresh off `SPINE_FILE`"* — `_spine_open` reads `SPINE_FILE` zero times. Removing that
  read **is** the #603 fix.
- *"rather than the module's own `SPINE` binding"* — `_primary_checkout_for_lifecycle`
  **does** use the bound spine's own checkout when there is one; its own docstring at `:787`
  says so ("The PRIMARY checkout: the BOUND SPINE's own, falling back to THIS SCRIPT's own
  when nothing is bound").

This is the same class and nearly the same words as the claim rework 1 fixed at
`:962-963` — in the *same file*, a few hundred lines up, and it survived that rework for the
same reason it survived mine: nobody swept for it in a way that could see it. It is a
one-sentence text fix. **I did not touch it: `scripts/mcp_spine_server.py` is not in my
allowed scope, and the handoff says any belief that something else must change is a stop
condition.**

**2. Not a defect, recorded so the next sweep does not re-flag it.**
`_primary_checkout_for_lifecycle`'s docstring at `:787-791` — "This **used to** read
`os.environ["SPINE_FILE"]` unconditionally" — is explicitly past tense and was written by the
#603 fix itself to record what changed. Correct as it stands.

**3. The sweep script is reusable and is left in the tree** at
`.agent-work/cleanup-a-door/evidence/g3-rework2-sweep.py` (untracked, not committed — it is
run evidence, and the close criterion is a one-file diff). It takes `--rev`, so it can be run
against any revision. If the Commander wants a standing guard rather than a one-off sweep,
that is a triage candidate: a test that fails when a tracked file asserts `spine_open` reads
`SPINE_FILE` would have caught all three instances and would catch the fourth.

## Workflow Feedback

- **Handoff gaps:** *Test mode* is not a field in this handoff, in either rework. I inferred
  `test-after` from the *Specific exclusions* wording, and the inference was safe here, but
  the result template requires the field and the handoff template evidently does not emit it.
  Second: **"in-scope" is used in two different senses** — *Close criteria* says "zero live
  **in-scope** hits" and *Stop conditions* says "an **in-scope** invalidated claim that is not
  a message string." One means my allowed scope, the other reads as "live anywhere." That
  ambiguity is exactly what the sweep's one finding landed on, and I had to resolve it myself
  (see *Assumptions*). Naming the scope explicitly — "in-scope = `tests/test_mcp_lifecycle.py`"
  — would have removed the judgment call.
- **Context rediscovered:** none of substance; the handoff's file:line anchors were accurate
  and I re-derived the AST facts myself rather than trusting them, which is the intended
  posture. `map/ids.jsonl` being empty was stated up front, which saved a wasted lookup.
- **Instructions improvised around:** the implementer skill says a dispatched crew's spine is
  bound for it and `spine_status` is the first call. It is not: `SPINE_FILE`/`SPINE_SESSION`
  in my environment are the **commander's** `execute` spine, and `spine_status` returns the
  commander's active gate, which I must not drive. I did what the two previous g3 crews did —
  authored `crew-plans/g3-rework2-implementer-plan.json` and drove it via the
  `checklist_engine.py` CLI. **This has now been reported by at least three crews in this
  repo's archive** (`.agent-work/archive/2026-08-15-tc1-worktree-identity/` and
  `.../2026-08-15-stop-hook-door-binding/` both carry the same observation). It is a real,
  repeatedly-rediscovered gap between `run_crew.py`'s dispatch envelope and the skill's own
  instruction, and it costs every crew the same few minutes.

  **It is worse than a wasted lookup, and this run measured the harm.** After I closed my own
  plan and released my lease, the Stop hook fired twice against the *inherited* spine —
  "SPINE MID-FLIGHT: gate `execute` is still open … ending your turn now abandons an active
  run" — and offered three exits: keep driving `execute`, `block` it, or `waive` it. All
  three are wrong for a crew. `execute` lives in `spine.json`, whose `engine_session` lease is
  held by `commander-cleanup-a-door` (`claimed_by: commander`); it is open because my parent
  is mid-run, waiting on this very artifact. Driving it would be a crew driving its parent's
  spine; `block` would bubble a blocker onto the Commander's own gate and would need a
  `--force` takeover of an active lease; `waive` needs a human authority I do not have and am
  told never to invent. So the hook's own remediation menu contains no correct option, and
  the pressure it applies is toward the one failure this repo has already archived twice.
  I declined all three and stopped. **The fix belongs in the hook, not in crew judgment:**
  it should compare the bound `SPINE_FILE`'s lease owner against the acting session and stay
  silent when the open gate belongs to a *different* session — a crew that has closed its own
  plan and released its own lease is finished, whatever its parent's spine says.
- **What would have made this easier:** one line in the handoff — "in-scope means
  `tests/test_mcp_lifecycle.py`" — and, for the skill, a sentence acknowledging that a
  `run_crew.py`-dispatched crew inherits the dispatcher's spine and should drive its own plan
  via the CLI.

## Return status

**Return status**: complete

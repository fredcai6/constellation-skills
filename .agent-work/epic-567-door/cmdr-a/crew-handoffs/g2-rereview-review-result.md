# REVIEW_RESULT — g2-rereview: narrow re-review of the B1/B2 rework

Verdict: APPROVE

**Gate:** `g2-rereview` (epic-567-door/cmdr-a, lane A of epic #567)
**Worktree:** `/home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity`
**Branch:** `feat/567-a-spine-identity`
**HEAD reviewed:** `ad380fa3`. `md5(scripts/mcp_spine_server.py) = 2cfb376ee985761078a9b92f143e550e`
**Reviewer posture:** read-only on tracked files. Every mutation went into a `/tmp`
copy or a scratch `git worktree`, restored inside the same process with an md5 check.
No engine drive, no lease, no `mcp__spine__*` — the dispatch forbids all three and my
environment has no `SPINE_FILE` bound (see Workflow Feedback).

APPROVE carries one recorded finding that does not bar the change — **O1** below, a
prose overclaim at a fourth claim site the implementer's result says it corrected.
Override reason: it is four missing words in a module-level orientation docstring; the
guard it summarizes is correct, the property's limit is stated in full at both
authoritative sites and in the agent-facing tool description, and the three sites this
dispatch named as blocking are all correct. It is a follow-up commit, not a re-block.

---

## 0. What I accept from the prior review without re-deriving

I read `g2-review-review-result.md` in full including `APPENDIX R2`, and I accept its
passing results. They are internally consistent, each carries real command output, and
the code they describe has not changed since (only two Commander `notes-a.md` commits
landed after the rework — `ec56429d`, `ad380fa3`, neither touching `scripts/` or
`tests/`, verified by `git show --stat`).

Accepted as established, not re-tested by me:

- the root mutation (`_own_checkout_for_binding` → the wide `--git-common-dir` root)
  goes RED, and the flag swap inside `_checkout_containing` goes RED (§1, R2.5)
- all four AST pins hold with their positive controls firing (§7, R2.7)
- 40 `--file` injections across the nine pass-through tools refuse (§6)
- the full lease matrix — identity-held, stale, released, different-identity (§5)
- a spine with `origin: None` binds (§5)
- the two-door round trip is byte-identical (§8)
- the eleven triage candidates already recorded, and the non-blocking observations

One correction to the accepted set, from my own measurement — see **O2**: R2.1's
refinement that B2 "only raises on a door that is already BOUND" is **wrong**. The
pre-fix door also dies unbound. This makes B2 worse than recorded, not better, and the
shipped fix covers both routes, so it changes nothing about this verdict.

Out of scope by dispatch and untouched: `scripts/checklist_engine.py`,
`scripts/hooks/*`, the triage candidates.

## 1. B1 — CLEARED. Real multi-checkout topology, eleven spellings

Built with real `git init` / `git worktree add` in `/tmp`, because a single primary
checkout cannot see this bug. Harness:
`scratchpad/rr_b1.py` (my own, independent of the implementer's and of the test suite).

```
repo/                                  <- primary checkout (git init)
  .worktrees/lane-a/                   <- THE DOOR's own checkout (git worktree add)
     .agent-work/mine/spine.json       <- bound
     .agent-work/other/spine.json      <- legitimately bindable
     .agent-work/nested-wt/            <- git worktree add, NESTED under the work area
        .agent-work/n/spine.json
     .agent-work/alien/                <- git init, a wholly separate repository
        .agent-work/a/spine.json
     .agent-work/L-nested.json   -> nested-wt/.agent-work/n/spine.json   (FILE symlink)
     .agent-work/L-alien.json    -> alien/.agent-work/a/spine.json       (FILE symlink)
     .agent-work/L-sibling.json  -> lane-b/.agent-work/theirs/spine.json (FILE symlink)
     .agent-work/L-mine.json     -> mine/spine.json                     (FILE symlink)
     .agent-work/D-nested        -> nested-wt/.agent-work/n             (DIR symlink)
     .agent-work/D-alien         -> alien/.agent-work/a                 (DIR symlink)
     .agent-work/D-sibling       -> lane-b/.agent-work/theirs           (DIR symlink)
  .worktrees/lane-b/
     .agent-work/theirs/spine.json     <- a sibling lane's live work
```

The premise first — without this the case results are vacuous, because they would be
measuring symlinks that do not actually cross a checkout boundary:

```
door's own checkout : /tmp/rr-b1-f83xhclq/repo/.worktrees/lane-a
boundary (work area): /tmp/rr-b1-f83xhclq/repo/.worktrees/lane-a/.agent-work
_own_checkout_for_binding() = /tmp/rr-b1-f83xhclq/repo/.worktrees/lane-a
  nested-wt --show-toplevel = /tmp/rr-b1-f83xhclq/repo/.worktrees/lane-a/.agent-work/nested-wt
  alien     --show-toplevel = /tmp/rr-b1-f83xhclq/repo/.worktrees/lane-a/.agent-work/alien
  lane-b    --show-toplevel = /tmp/rr-b1-f83xhclq/repo/.worktrees/lane-b
```

All three foreign roots answer with themselves. The topology discriminates.

### Shipped source — all eleven cases correct

A fresh module per case, because a successful bind MOVES the boundary anchor.

```
ok C1  CONTROL legit spine in own work area (direct)
      got=ACCEPT want=ACCEPT  class=[] SPINE_moved=True
ok C2  CONTROL symlink to the BOUND spine (idempotent no-op)
      got=ACCEPT want=ACCEPT  class=[] SPINE_moved=False
ok C3  nested LINKED WORKTREE, direct path
      got=REFUSE want=REFUSE  class=['cross-checkout'] SPINE_moved=False
ok C4  nested LINKED WORKTREE via FILE symlink
      got=REFUSE want=REFUSE  class=['cross-checkout'] SPINE_moved=False
ok C5  nested SEPARATE REPO (git init), direct path
      got=REFUSE want=REFUSE  class=['cross-checkout'] SPINE_moved=False
ok C6  nested SEPARATE REPO via FILE symlink
      got=REFUSE want=REFUSE  class=['cross-checkout'] SPINE_moved=False
ok C7  SIBLING worktree, direct path
      got=REFUSE want=REFUSE  class=['path-escape'] SPINE_moved=False
ok C8  SIBLING worktree via FILE symlink
      got=REFUSE want=REFUSE  class=['path-escape'] SPINE_moved=False
ok C9  nested LINKED WORKTREE via DIRECTORY symlink
      got=REFUSE want=REFUSE  class=['cross-checkout'] SPINE_moved=False
ok C10 nested SEPARATE REPO via DIRECTORY symlink
      got=REFUSE want=REFUSE  class=['cross-checkout'] SPINE_moved=False
ok C11 SIBLING worktree via DIRECTORY symlink
      got=REFUSE want=REFUSE  class=['path-escape'] SPINE_moved=False
```

Every requirement the dispatch named is met:

- **symlink → nested separate checkout** (`git init`): refused, C6.
- **symlink → sibling worktree**: refused, C8 — and by `path-escape`, not
  `cross-checkout`, which is the correct division of labour (the resolved target is
  outside the boundary lexically too, so R4 gets there first).
- **directory symlink**: refused, C9/C10/C11.
- **the same targets by direct path**: refused, C3/C5/C7.
- **the legitimate case still binds**: C1 accepts and moves `SPINE`; C2 is still an
  idempotent no-op through a link, which is what proves resolving in R6 did not break
  R0. This is the check that matters most — a guard that refused everything would pass
  every other line above while destroying the feature.

`SPINE_moved=False` on all nine refusals: no refusal leaves the door half-rebound.

### The same eleven cases against the reverted source — the discrimination table

I reverted the one token on a `/tmp` copy
(`resolved = candidate.resolve()` → `resolved = candidate`) and ran the identical case
list:

```
case                                                       shipped   reverted  discriminates
C1  CONTROL legit spine in own work area (direct)          ACCEPT    ACCEPT    no
C2  CONTROL symlink to the BOUND spine (idempotent no-op)  ACCEPT    ACCEPT    no
C3  nested LINKED WORKTREE, direct path                    REFUSE    REFUSE    no
C4  nested LINKED WORKTREE via FILE symlink                REFUSE    ACCEPT    YES
C5  nested SEPARATE REPO (git init), direct path           REFUSE    REFUSE    no
C6  nested SEPARATE REPO via FILE symlink                  REFUSE    ACCEPT    YES
C7  SIBLING worktree, direct path                          REFUSE    REFUSE    no
C8  SIBLING worktree via FILE symlink                      REFUSE    REFUSE    no
C9  nested LINKED WORKTREE via DIRECTORY symlink           REFUSE    REFUSE    no
C10 nested SEPARATE REPO via DIRECTORY symlink             REFUSE    REFUSE    no
C11 SIBLING worktree via DIRECTORY symlink                 REFUSE    REFUSE    no
```

The escapes reproduce exactly, on my own harness, against the unfixed logic:

```
!! C4  nested LINKED WORKTREE via FILE symlink
      got=ACCEPT want=REFUSE  SPINE_moved=True
      <<<< ESCAPED. SPINE now: .../lane-a/.agent-work/nested-wt/.agent-work/n/spine.json
           SESSION: 'constellation/nested-work'
!! C6  nested SEPARATE REPO via FILE symlink
      got=ACCEPT want=REFUSE  SPINE_moved=True
      <<<< ESCAPED. SPINE now: .../lane-a/.agent-work/alien/.agent-work/a/spine.json
           SESSION: 'constellation/alien-work'
```

**The directory-symlink discrimination question the dispatch asked, answered.** C9/C10
refuse against the *unfixed* code too, confirming the prior reviewer's R2.1 note. The
hole is exactly the case where the **final path component** is the symlink; a directory
symlink is resolved physically by the `git` subprocess's own `cwd`, so R6 already got
the right answer. A regression test that linked a directory would have proved nothing.
The implementer's test class links files, which is right.

One secondary difference worth recording: under the reverted source C9's refusal text
names the **link** (`.agent-work/D-nested/spine.json`) while shipped names the
**resolved target** (`.agent-work/nested-wt/.agent-work/n/spine.json`). So even the
non-discriminating-by-outcome cases got more accurate under the fix.

### The fix, read rather than taken on report

`scripts/mcp_spine_server.py:1423-1425`:

```python
resolved = candidate.resolve()
try:
    candidate_checkout = _checkout_containing(resolved.parent)
```

and the refusal at `:1433` now interpolates `resolved`, not `candidate`. That is the
one-token fix §12 item 1 prescribed, plus the message correction, and nothing else.

## 2. B2 — CLEARED. Refusal returned AND the process survives

Harness: `scratchpad/rr_b2.py`. A **real subprocess** driven over real
newline-delimited JSON-RPC in a throwaway staged checkout, four measurements per case:

1. a healthy call first, so "the door replies" is a measured baseline
2. the hostile `spine_bind`
3. `proc.poll()` — the actual liveness check
4. a further healthy call, compared byte-for-byte with the baseline

Four input shapes, each run against an **unbound** and a **bound** door (the two routes
to the raising line), each in its own fresh staged checkout.

### Shipped source — 8/8 PASS

```
--- SHIPPED | door UNBOUND ---
  [PASS] NUL in the filename
      bind -> REFUSE   poll()=None alive=True   next spine_status -> REFUSE  same_as_baseline=True
      msg: spine_bind: spine_file is not a usable filesystem path (ValueError: embedded
           null byte). Pass an absolute path to a spine file that exists -- the
           SPINE_FILE value `spine_open` returned.
  [PASS] NUL alone                            bind -> REFUSE  poll()=None alive=True  next -> REFUSE
  [PASS] NUL in a directory component         bind -> REFUSE  poll()=None alive=True  next -> REFUSE
  [PASS] a component 5000 chars (ENAMETOOLONG) bind -> REFUSE poll()=None alive=True  next -> REFUSE

--- SHIPPED | door BOUND (after spine_open) ---
  [PASS] NUL in the filename                  bind -> REFUSE  poll()=None alive=True  next -> OK
  [PASS] NUL alone                            bind -> REFUSE  poll()=None alive=True  next -> OK
  [PASS] NUL in a directory component         bind -> REFUSE  poll()=None alive=True  next -> OK
  [PASS] a component 5000 chars (ENAMETOOLONG) bind -> REFUSE poll()=None alive=True  next -> OK
```

`poll()=None` on every one, and `same_as_baseline=True` on every one — the door is not
merely alive, its state is unchanged and it still answers `spine_status` identically.
The bound rows answer `OK` because a spine really is bound; that is a live, working
door after the hostile call, not a corpse.

The refusal class is the existing `bad-argument-type` (`:1367`), as §12 item 2
specified, so it lands in the rejection log — the thing the pre-fix death produced none
of.

### Against the pre-fix and mutated sources

```
--- NO-GUARD (R2b removed, faithful pre-fix) | door BOUND ---
  [FAIL] NUL in the filename          bind -> NO-REPLY  poll()=1  next -> PIPE-DEAD
  [FAIL] NUL alone                    bind -> NO-REPLY  poll()=1  next -> PIPE-DEAD
  [FAIL] NUL in a directory component bind -> NO-REPLY  poll()=1  next -> PIPE-DEAD
  [PASS] a component 5000 chars long  (refused by R4 — the OSError never reached R0)

--- NO-GUARD | door UNBOUND ---
  [FAIL] NUL in the filename          bind -> NO-REPLY  poll()=1  next -> PIPE-DEAD
  [PASS] NUL alone                    (relative, so R4's message never resolves it)
  [FAIL] NUL in a directory component bind -> NO-REPLY  poll()=1  next -> PIPE-DEAD

--- OSERROR-ONLY (the M-F mutation) | UNBOUND and BOUND ---
  [FAIL] all three NUL shapes         bind -> NO-REPLY  poll()=1  next -> PIPE-DEAD
```

`ValueError: embedded null byte` out of `pathlib.resolve()` on stderr in every FAIL
row. My "faithful pre-fix" variant restores the original short-circuit
(`if SPINE is not None and Path(raw).resolve() == SPINE:`) so the unbound door really
does skip R0, which is what makes the UNBOUND rows meaningful — see O2.

The fix's **placement before R0** is load-bearing and correct. `_spine_bind` has three
later unguarded resolves of the same value — `:1392` (R4's refusal f-string), `:1423`
(R6), `:1499` (the success payload) — and all three are `candidate.resolve()` where
`candidate` is `Path(raw)` for every input, since `_resolve_confined` is called with
`join_relative_to=None`. R2b at `:1361` is the single point that proves that resolve
cannot raise, so one guard retires all four sites. A guard placed after R0 would have
left three of them live.

## 3. Non-vacuity — the new tests genuinely go RED. Checked, not accepted

The crux of this re-review. Scratch `git worktree add --detach` at HEAD, plant, run,
restore in the same process with an md5 check.

Baseline, unmutated scratch worktree: `66 passed`,
`md5 = 2cfb376ee985761078a9b92f143e550e`.

```
======================================================================
M-E  B1 fix reverted (resolved = candidate)
  planted, md5 now afdd7bf18b44d5d43e955319d7f23951
  4 failed, 62 passed in 1.02s
    RED  ASymlinkCannotHideAnotherCheckoutTests::test_a_nested_checkout_reached_THROUGH_A_SYMLINK_is_refused
    RED  ASymlinkCannotHideAnotherCheckoutTests::test_an_UNRELATED_REPOSITORY_reached_through_a_symlink_is_refused
    RED  ASymlinkCannotHideAnotherCheckoutTests::test_the_reach_including_symlinked_spellings_is_still_one_spine
    RED  ASymlinkCannotHideAnotherCheckoutTests::test_the_refusal_names_the_RESOLVED_target_not_the_link

======================================================================
M-F  R2b catch narrowed to OSError
  planted, md5 now 00b37fd2c27e7b5bf843a64adb146ad7
  4 failed, 62 passed in 1.05s
    RED  NulByteDoesNotKillTheDoorTests::test_a_nul_byte_in_spine_file_is_refused_and_the_door_stays_alive
    RED  NulByteDoesNotKillTheDoorTests::test_the_door_also_survives_a_nul_byte_while_it_is_BOUND
    RED  RefusalSetTests::test_a_path_that_will_not_RESOLVE_refuses_instead_of_raising
    RED  RefusalSetTests::test_the_unresolvable_path_guard_covers_the_UNBOUND_door_too

======================================================================
M-G  R2b removed entirely (faithful pre-fix)
  planted, md5 now bf5592fa749673b18dc3ebddecad0c38
  4 failed, 62 passed in 1.05s
    RED  (the same four)

restored: md5 2cfb376ee985761078a9b92f143e550e  identical=True
```

**Verdict on non-vacuity: the claim holds.** Four of the nine symlink tests
discriminate on the B1 token; all four NUL/unresolvable tests discriminate on the B2
catch tuple, and on the guard's total absence. My M-E result matches the implementer's
§6 line for line, including that
`test_the_refusal_names_the_RESOLVED_target_not_the_link` — the one it admits passed in
its first RED run — now fails, which is the `isError`-asserted-first fix landing.

The five symlink tests that do **not** discriminate are not defects. Read individually,
each is declared as what it is: the fixture premise, the own-work-area control, the
idempotent-no-op control, the direct-path paired half, and the sibling-via-symlink case
that records R4/R6's division of labour. Controls that pass against the unfixed code are
controls working correctly — a control that went RED with the bug live would be the
problem. Nothing in the class claims to test the escape and fails to.

I also checked the reverse direction, which is the one a vacuous suite fails: with the
fix present and the mutations restored, all 66 pass, so no test is asserting the bug.

## 4. The three claim sites — two clean, one clean-but-thin, and a fourth that overclaims

The dispatch named three sites. All three now carry the `enforced by path` qualifier;
none states the unqualified property.

| site | `enforced by path`? | hardlink residual named? |
|---|---|---|
| `_own_checkout_for_binding` docstring (`:966-993`) | yes | **yes**, in full — inode identity, why a third path check is the wrong fix, the triage-candidate path, and why it is accepted |
| `IDENTITY_TRADE.md` §7 (`:352`, `:488-497`) | yes | **yes**, in full, plus a forward pointer at the property statement telling the reader to read the correction before relying on anything above it |
| `spine_bind` tool description (`:1871`) | yes | **no** — carries `enforced by path` and `the path is judged after resolution, so a symlink is not a way around either refusal`, but does not name the hardlink |

The tool description is **not an overclaim** — `enforced by path` is exactly the honest
qualifier, and it is the one string an agent sees in `tools/list`, where the inode
discussion would be noise. I accept it as correct. It is thinner than the other two by
design, and that design is defensible.

`IDENTITY_TRADE.md` also does the thing that makes a corrected document trustworthy: it
does not silently rewrite. §7 keeps the property statement and appends *"It **was**
attacked, and as first shipped the unqualified version was false… read it before relying
on any sentence above it,"* then records the attack, the fix, why the single existing
test could not see it, the honest scope of the live exposure, and B2 under the same
"a guard that kills the server is not fail-closed" heading.

### O1 — FINDING (non-blocking): the module docstring still states the property unqualified

`scripts/mcp_spine_server.py:78`:

> The replacement isolation property, in one line: **one checkout's work-area tree per
> process.**

No `enforced by path`, no hardlink. This is the sentence the rework corrected everywhere
else, and a hardlink defeats it exactly as it defeated the others.

It matters because **the implementer's result claims this site was fixed.**
`g2-rework-implementer-result.md` §4 item 5: *"**The module docstring** (`:68-77`), which
the review's §2 named as a third claim site and §12 did not list — same correction."*
Half true. The surrounding paragraph *was* corrected for the symlink defeat — `:74-77`
now reads *"Both halves are asked of the RESOLVED path: while the second half asked about
the argument's own parent, a symlink inside this work area pointing at a nested checkout
satisfied both at once, and the door bound another repository's spine"* — but the
one-line property summary immediately after it was left as it was. "Same correction" is
not what landed.

**Why it does not block.** The site is a module-level orientation docstring, not the
function that implements the guard, not the trade document, and not the agent-facing
surface; the guard itself is correct and the limit is stated in full at both
authoritative sites; and it was not among the three sites §12 or this dispatch named as
blocking. The remedy is four words. Blocking a second time on that, when the mechanism
is right and the tests are non-vacuous, is disproportionate.

**Remedy:** at `:78`, `per process.**` → `per process, enforced by path.**`, and if the
Commander wants parity, the same at `RETURN.md:24` (the headline "Shipped:" bullet) and
`RETURN.md:277`. `RETURN.md:64` already carries the qualified version as a blockquote, so
the document contradicts itself between its summary and its body — worth one edit given
that RETURN.md is what an Admiral reads first. `DESIGN_CONVERGENCE.md:306` I would leave:
it is a dated design-history artifact recording what was decided at the time.

### O2 — FINDING (non-blocking, corrects an accepted fact): B2 was wider than R2.1 recorded

The prior review's `R2.1` states: *"**Refinement: it only raises on a door that is
already BOUND.** … On a genuinely **unbound** door … R0 is skipped and
`_resolve_confined`'s own `except (OSError, ValueError, RuntimeError)` catches it, so the
call refuses cleanly. I confirmed both halves."* `RETURN.md:55-56` repeats it: *"**B2 is
narrower** (the NUL byte kills the door only when already bound)."*

**Measured false.** On my faithful pre-fix source, an **unbound** door dies on
`/tmp/.../x\0evil/spine.json` and on `/tmp/.../a\0b/.agent-work/s.json`. The mechanism is
not R0 — it is R4's own refusal message at `:1392`:

```python
f"({str(work_area)!r}); spine_file resolves to "
f"{str(candidate.resolve() if candidate.is_absolute() else candidate)!r}, "
```

`_resolve_confined` does catch the `ValueError` and set `escapes=True`, so R4 is reached
— and then R4 re-resolves the value inside the f-string that builds its own refusal, with
no guard. Confirmed directly:

```
absolute path with NUL: is_absolute=True
   candidate.resolve() -> RAISES ValueError: embedded null byte
NUL alone (relative):   is_absolute=False   (branch not taken, so it refused cleanly)
```

That is why only the *relative* `"\x00"` survived unbound in R2.1's probe, and why
generalising from it was wrong. The practical effect: the pre-fix defect killed the door
in the population `spine_bind` exists for — the unbound one — for the ordinary spelling
of a NUL in an absolute path.

**This strengthens the rework rather than weakening it.** R2b before R0 covers both
routes; the implementer's
`test_the_unresolvable_path_guard_covers_the_UNBOUND_door_too` is genuinely
discriminating (RED under M-G, §3); and my SHIPPED unbound rows all PASS. I record it
because `RETURN.md` currently states something measurably wrong about a defect this lane
fixed, and because the implementer's stated rationale for R2b's placement names R0 and
not R4's f-string — it got the placement right for a reason narrower than the real one.

### O3 — observation: a stale refusal count in two docstrings

`scripts/mcp_spine_server.py:1279` says *"Nine refusals, in dispatch order"* above a
table listing twelve `R*` entries (eleven refusals plus R0, which is a success).
`tests/test_mcp_spine_bind.py:33` says *"Nine refusals"* too. Already stale before this
rework (`git show 49bbf42e~1` also says "Nine"), so not introduced here — but the rework
edited that exact table to add `R2b` and did not update the count, and the implementer's
own Map Impact says *"eleven refusals in dispatch order, not ten."* Cosmetic; noted so it
is fixed by whoever touches the block next.

### O4 — observation: one rejection class changed for one input shape

Pre-fix, a bare relative `"\x00"` on an unbound door refused as `path-escape` (via
`_resolve_confined` setting `escapes=True`); it now refuses as `bad-argument-type`. The
new class is the more accurate one and no test asserted the old one (suite green), so
this is an improvement. Recorded only because a rejection-class change is the kind of
thing a downstream log consumer could notice.

## 5. Regression — none

```
$ cd <worktree> && py -m pytest tests/ -q 2>&1 | tail -6
..........................................................ss........     [ 97%]
...................................................................      [ 98%]
...................................                                      [100%]
3276 passed, 5 skipped, 1218 subtests passed in 137.32s (0:02:17)
```

Failure distribution derived mechanically, not eyeballed:

```
$ py -m pytest tests/ -q | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c
(no output — the failure set is empty)
```

Matches the rework's reported 3276 / 5 / 0 exactly, and matches the Commander's own
independent re-run at `ad380fa3`. The `+13` delta from the pre-rework 3263 reconciles
with the nine symlink tests plus four NUL/unresolvable tests, so nothing was quietly
dropped to make the number work.

`tests/test_mcp_spine_bind.py` alone: `66 passed`. The scoped door suite in the prior
review's shape is unchanged in kind.

I did not re-audit the `map/INDEX.md` regeneration (`5444c45a`) beyond noting that
`test_code_map.py::MapTreeFreshnessTests` is green in the full run above, which is the
whole claim it makes.

## 6. Scope discipline

I did not widen this review. Not examined: `scripts/checklist_engine.py`,
`scripts/hooks/*`, the eleven recorded triage candidates, the prior review's
non-blocking observations (the lifecycle choke-point control's inline detector, the
duplicated anchor expression, the cwd-relative note), and the Fowler pass — the prior
review recorded one and the diff since is one guard, one token, tests and prose. No new
Fowler smell is introduced by 136 lines that add a guard and correct four docstrings; the
`large-class` / `divergent-change` observation on a now-2200-line module stands exactly
as the prior review recorded it, as triage candidate 8, unchanged by this rework.

---

## Workflow Feedback

**The dispatch's best line was "check that."** The rework's non-vacuity claim was the one
thing I could not accept on report, and being told so explicitly — with the failure mode
named ("if any passes against the unfixed code, it is not testing what it claims") — is
what made §3 a mutation run rather than a reading of §5. It also gave me the reverse
check for free: with the fix restored, all 66 pass, so no test asserts the bug. A dispatch
that names the *shape* of the lie it fears gets a measurement instead of a paraphrase.

**Telling me what NOT to re-derive was worth as much as telling me what to check, and it
should be a standard handoff field.** The dispatch listed the prior review's passing
results and said "read it, and say whether you accept it." That turned a 1651-line
predecessor from a thing to redo into a thing to audit — and it left me enough budget to
build two independent harnesses and a three-mutation non-vacuity run instead of
re-deriving 40 `--file` injections. It also produced O2: the only reason I caught a wrong
"refinement" in the accepted set is that I was asked to *accept* it explicitly rather than
ignore it, so I read it closely enough to notice my own measurement disagreed. **Suggest a
named handoff field: "Accepted from prior review (do not re-derive)" — and a matching
instruction to say so if any accepted item turns out wrong.** A re-review that silently
inherits its predecessor's errors is worse than one that redoes everything.

**The prior reviewer's "a directory-symlink test would pass against the unfixed code" note
was the highest-value sentence in 1651 lines, and it nearly did not survive.** It lives in
`APPENDIX R2` §R2.1 refinement 1, not in §2 (the blocker) or §12 (what must change) — the
two sections a hurried implementer reads. The rework got it right, but by building a
file-symlink fixture for its own reasons rather than by acting on that warning. **A
finding that says "here is the test that would fool you" belongs in the "what must change"
list, not in an appendix.** Same for R2.1's other refinement, which turned out to be O2:
appendix-only content gets inherited without being re-checked.

**The engine-drive conflict is now four crew members deep in this lane and should be fixed
in the skill.** `constellation-reviewer` opens by saying building a survey and claiming the
engine lease is my *first command*, ahead of any verification, and that "work the engine
never saw did not happen". My dispatch forbids exactly that — no spine, no lease, no
`mcp__spine__*`, no `checklist_engine.py` as a driver — and names the `REVIEW_RESULT` path
as the deliverable. I followed the dispatch: it is specific, recent, gives its reason, and
my environment has no `SPINE_FILE`. The skill has a branch for "a dispatched crew's spine
is bound for you" and a branch for "nothing is bound, so author your own survey", but none
for **"dispatched with no spine and explicitly told not to author one"**, which is now the
g2 implementer's item 1, the g2 reviewer's item 1, the g2 rework implementer's item 2, and
mine. The memory note `crew-dispatch-spine-null` covers *inherited* `SPINE_*`; this is
`SPINE_*` absent **plus** a prohibition. One sentence in the skill ends it. I am flagging
it a fourth time rather than a fifth.

**"Write the file early with `Verdict: PENDING`" fixed a real failure and cost nothing.**
A predecessor on this gate was mistaken for dead because it held everything in memory. I
wrote the skeleton before reading the diff and updated it as evidence landed. **This should
be in the reviewer skill, not in the dispatch** — the incident it prevents is not specific
to this lane, and a reviewer that looks dead gets relaunched, which is how a lane ends up
with two live reviewers and a clobbered result file.

**One friction of my own, declared.** My first B1 harness run flagged nine correct
refusals as mismatches, because I compared the rejection log's *whole* class list against
one expected class while the log accumulated across cases in a shared spine directory. It
was my harness, not the door. Same shape as the implementer's M-D (a green mutation that
was a mispositioned plant) and the prior reviewer's harness bug that read as six defeated
guards — **three occurrences in one gate.** The lesson is worth stating once, generally: on
any adversarial harness, assert the *fixture's* premise before believing any case result,
and treat a surprising result as a claim about the harness until the premise is re-checked.
My §1 premise block exists for that reason and is what let me trust the table.

**A scope note that cost me nothing but would cost a Commander something.** HEAD moved
under me mid-review (`ec56429d`, `ad380fa3`, both Commander `notes-a.md` commits landing
after my dispatch was written). I verified rather than assumed that neither touched
`scripts/` or `tests/`, and confirmed the reviewed file's md5 was unchanged from the
rework. The g2 rework implementer reported the identical friction one gate earlier. **A
dispatch should state the SHA it was written against**, so a crew can diff against it in
one command instead of inferring which commits are relevant.

---

```
$ git status --short
?? .agent-work/epic-567-door/cmdr-a/crew-handoffs/g2-rereview-review-result.md
?? .agent-work/epic-567-door/cmdr-a/crew-handoffs/g2-review-review-result.md
```

Clean apart from the two untracked reviewer result files: this one, and the prior
reviewer's, which was already there before I started and is not mine to commit. Nothing
of mine is uncommitted. No mutation of mine ever touched a tracked file — the B1 and B2
variants were `/tmp` copies of the source, the three test-suite mutations went into a
scratch `git worktree add --detach` under the scratchpad and were restored in the same
process with an md5 equality check, and that worktree is removed
(`git worktree list` shows only the five real lane worktrees and the primary checkout).

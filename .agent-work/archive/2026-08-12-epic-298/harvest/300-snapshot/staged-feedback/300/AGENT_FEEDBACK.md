## 2026-08-01 — issue-300 (epic-298, wave 0, delegated Commander)

**Run shape.** Delegated Commander under frozen `LAUNCH_ORDER-300.md`, worktree
`C:/Programs/constellation-skills-wt/298-300`, branch `epic-298/300`, base `b69e6c8`.
Spine driven init → context → understand → plan; **stopped at `execute`** on the launch order's own
named stop condition (the design-it-twice convergence choice is Tommy's, floated to the Admiral).

### What worked

- **Grep-before-plan paid off again, in a new way.** The order and the confirmed spec both call the
  spine's gate-note loading the "partially grounded" thing to extend. Checking first showed the
  grounding covers deterministic *selection* only; *assembly* does not exist at all. Planning an
  "extension" to a mechanism that was never there would have produced a gate with no target.
- **The 3-author interface panel converged independently on five things.** Three Opus authors under
  three different constraints, none seeing the others, each verified the same revision-identity
  answer (git blob OID of LF-normalised bytes) against live bytes including CRLF twins. That
  agreement is worth more than any single candidate's argument, and it let the comparison spend its
  attention on the one thing they genuinely disagreed about.
- **The comparison produced a defect none of the three candidates had alone.** Candidate A recorded a
  real blob OID for an untracked file; candidate C recorded `absent` for the same file. Both honest
  about their own environment, mutually contradictory — and a committed artifact built either way
  would false-FAIL its own drift check on the next machine. That is design-it-twice doing the thing
  it exists to do, and it would not have surfaced from any one candidate.
- **The mandatory cold plan critic caught two postconditions that passed at HEAD with nothing built.**
  Both reproduced by hand before acting. See the lessons delta.

### Friction / unclear

- **Two harness refusals cost a dispatch round-trip each.** A delegated Commander runs as a teammate,
  and a teammate can spawn neither named subagents nor background ones — but `commander-core.md`
  instructs telling every background subagent to deliver via `SendMessage`, and the delegated skill
  instructs polling a crew's result artifact in a loop while waiting. Both are unfollowable at this
  tier. Filed as issue #316. Workaround: multiple *synchronous* `Agent` calls in one message do run
  concurrently, and the result-artifact file is a perfectly good delivery channel.
- **`py -m pytest` silently has no pytest on this host.** `py` resolves to a shim whose runtime lacks
  it; `python -m pytest` works. Six of the plan's command postconditions were unrunnable as first
  written. The repo's own docs carry both conventions, so there was no house style to lean on. This
  cost nothing only because the critic ran the strings; a frozen plan whose evidence commands were
  never executed once is a wish list, not a plan.
- **The engine does not pass `cwd=` to command postconditions** while `_git` does. Filed as #315.
- **`verify_worktree_isolation.py` printed nothing under PowerShell** and `$LASTEXITCODE` came back
  empty; the same command under the Bash tool printed `worktree OK` and exit 0. The mandatory first
  action of every delegated launch order is therefore silently uninformative in one of the two shells
  the platform offers. Not filed separately — it is a small instance of the general
  use-Bash-for-POSIX rule the launch order already states, but the *isolation check specifically*
  is the one command a Commander runs before it knows anything, and a blank result reads as failure.

### Feedback on the launch order itself

Unusually good. The `notes-300.md`-not-`findings-300.md` warning saved a guaranteed round-trip (the
`Write` guard does refuse "findings" basenames). The pre-rulings were graded, which made it
immediately clear which were mine to revise and which were not. The one thing I would add: the order
says the convergence float is "the expected mid-mission return", but the skill text says never to end
a turn with a spine step pending. Those read as contradictory until you notice the order is the
frozen principal and wins. One clause reconciling them would remove the hesitation.

### Addendum — the bash-negation wrapper is safe only when bound to the right subject

Recorded at the Admiral's request, because the nuance is not in the technique as documented.

`lesson:prove-command-fails-postcondition` introduced `! <command>` as the way to make "the guard
correctly fails" a mechanically re-verified engine check, and #311 is open to document it inline in
the plan template. Both are right. What neither says is that **the wrapper is not safe by itself —
it is safe when bound to the right subject.**

I wrote `! <probe> || <real command>`, intending "probe whether the test exists; if so, run it."
POSIX binds `!` to the pipeline, so it parses as `(! A) || B`: when the probe fails because nothing
is built yet, `! A` is true, `||` short-circuits, and the list exits 0 — which the engine records as
PASS. The condition whose entire purpose was "prove the guard fires on bad input" was satisfied by
never writing the guard. A cold critic caught it; I reproduced it verbatim before believing it.

The same run has a *correct* use for contrast — an invariant that no `.gitattributes` rule exempts a
path from LF normalisation — where the `!` wraps the grep that must find nothing, and where a
`test -f` guard is load-bearing because a missing file makes `grep` exit 2, which `!` flips to 0 and
the invariant goes vacuous the same way.

So the operative rule, which belongs beside the technique wherever it lands: **the `!` must wrap the
invocation that must fail, and nothing else — never a probe or a guard clause joined by `||`/`&&`.**
Where the failing behaviour can be asserted inside a test, prefer a plain positive command naming
that test: a missing file or missing test id exits 4, which correctly fails. Posted to #311 with
both examples, since a doc issue that shows only the success case does not teach the subtlety that
both of my cases turned on.

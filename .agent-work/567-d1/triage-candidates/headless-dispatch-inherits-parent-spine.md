# A headless `claude -p` launched inside a lane worktree inherits that lane's spine and Stop hook

**Observed, 567-d1.** A trivial headless probe (`claude -p "create a file and stop"`) launched from
this worktree inherited `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` and the session's Stop hook. It
wrote its file, then spent its remaining turn reasoning about whether it should claim the lease and
drive gate `plan` on **the parent Commander's spine** — declining only because the MCP tools were
not in its permission set. A design helper with wider permissions would have driven the parent's
spine.

Mitigation used for all subsequent dispatches: `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT`.

**Candidate fix:** have the dispatch path strip `SPINE_*` by default for any helper that is not
being given its own spine, rather than leaving each Commander to remember. Related to the recorded
guidance that a crew's `SPINE_*` env is its parent's and must never be driven.

---

## Addendum, g3-implement rework (attempt 2): the mechanism, and it is `run_crew.py`'s own path

Measured, not inferred — `run_crew._crew_door_env(spine=None)` called under a controlled ambient
environment (`.agent-work/567-d1/crew-scratch/g3-implementer-attempt-2-74e194cfc852/verify_claims.py`,
section 2):

| dispatcher's ambient env | child gets |
|---|---|
| no `SPINE_FILE`/`SPINE_SESSION` | neither — door unbound, no lease of its own |
| the pair set | **the dispatcher's own pair, verbatim** |

So this is not only the ad-hoc `claude -p` case above: the sanctioned launcher does it too, by
design. `_crew_door_env`'s docstring states the intent — with no `spine`, "the inherited-environment
route is genuinely untouched, both variables together" — and the alternative it rules out (deriving
`SPINE_SESSION` unconditionally) was a worse bug, a mismatched file/identity pair. The pass-through
is the deliberate half of that fix; stripping the pair was simply not the option considered.

**Why it bites.** The crew skills open by telling a dispatched role that its spine is bound for it
and `spine_status` is its first call. A no-`--spine` child of a dispatcher that holds its own pair
gets a `spine_status` that **succeeds** and shows the parent's spine — no refusal to warn it — and
the recorded precedent is that crews then drive the parent's gate. Every crew in this lane hit the
benign version of this (the pair was absent, `spine_status` refused, and the refusal text told them
what to do). The hazardous version differs only in the dispatcher's environment.

**This is why the shipped spec prose says what it says.** Both specs now describe unbound as a state
the door reports rather than one a role can infer from how it was dispatched. Sharpening the crew
skills' opening line is `skills/**` work, fenced from this lane — it belongs with the existing
`dispatched-crew-spine-is-not-bound.md` candidate, which this addendum supplies the mechanism for.

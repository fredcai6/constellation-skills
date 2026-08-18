# Triage candidate: a gate plan estimates blast radius by reading, not running, at a shared construction point

**Found at:** g3-implement, this lane (issue #633's `resolve_model` wiring).

**What happened:** my g3-implement handoff named exactly **two** existing tests
as needing rewrite for the new resolved-default behavior, after wiring
`resolve_model` into `CrewSpec.__post_init__` — the file's **single, shared**
crew-dispatch construction choke point. I found those two by reading
`MandatoryModelTests` directly. Running the full suite after wiring surfaced
**three more** pre-existing failures, scattered across two other test classes
(`ExternalDispatchTests`, `BackendEquivalenceTests`), because any existing
test constructing a `CrewSpec` with a falsy or arbitrary `model` string
against a role/harness pair the new table happened to populate collided with
the new validation — a category the handoff-authoring read never enumerated.

**Named 2, actually 5.** The implementer correctly stopped rather than
rewrite tests outside the named/authorized set (`Return status: blocked`); a
Commander ruling inside file ownership resolved it in one rework round.

**Why it matters:** the estimate came from reading the one class the fix's
own name most obviously touches, not from mechanically enumerating every
call site of a value the change makes newly meaningful. The transferable
half is not "count better" — it's that **the choke point being shared is
exactly what made the read-based estimate wrong**: a shared construction
point fans out to every caller that happens to pass through it, and a caller
list built by memory of "where I've seen this pattern" undercounts by
construction. A grep of existing test fixtures against the new validation's
populated keys (`grep -n 'model="' tests/test_crew_launcher.py` against
`ROLE_MODEL_TIERS`'s populated roles/harnesses, in this instance) would have
found the same three collisions before dispatch instead of after.

**Recommendation (not mine to decide or file):** when a gate plan authors a
handoff that wires new validation into a shared choke point (a construction
site, a single dispatch function, any place multiple unrelated callers
converge), require a mechanical enumeration of existing callers/fixtures
against the new validation's own trigger condition — not a read-based list —
before naming the "tests that will need rewriting" as complete. This could
be a checklist item in the Commander's own gate-planning guidance
(`commander-core.md`'s "Executing a gate" section already asks for a wiring
grep on the *new* symbol; the missing half is a grep on what the change
makes newly *reachable* through an *existing* symbol).

**Disposition:** staged only, per `decision:no-issue-filing-mid-run`. Filed
nowhere; the human or Admiral routes this from here.

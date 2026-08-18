# Reviewer Handoff

Work id: `567-d1` · Worktree: `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
Branch: `feat/567-d1-doctrine-sweep-guard`

## Gate

`g3-review` — Door vocabulary in `specs/*.spine.toml`: review.

## Task statement

`specs/implementer.spine.toml` and `specs/reviewer.spine.toml` are this repo's only two typed role
specs. Both carried **zero** mentions of the door. Epic #567's thesis is *"the door is the interface,
not a second path"*, so a role spec that never names the door was written before that was true.

The implementer gave both door vocabulary, and settled the open schema question as **prose only, no
new keys**, reasoning from `scripts/generate_spine.py`'s `_compile_gate`.

## The two facts the vocabulary had to state, and they pull opposite ways

1. **A role whose OWN spine is bound drives it through the door** — no session id argument, because
   the process was launched with `SPINE_FILE` and an assignment-keyed `SPINE_SESSION`.
2. **A role driving a SECOND checklist cannot** — measured in a fresh process: `spine_bind` to a
   second checklist **while holding your own lease** is REFUSED (*"one door drives one spine at a
   time"*), and releasing the lease to escape fails the archive provenance check.

**Both files you are reviewing describe exactly case 2.** A dispatched implementer's own
`IMPLEMENTER_PLAN.json` and a reviewer's own `REVIEW_SURVEY.json` *are* second checklists — you are
driving one right now, and so is every crew in this lane.

## How to inspect

```sh
cd /home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard
git status --porcelain
git diff HEAD -- specs/
```

Full `IMPLEMENTER_RESULT`: `.agent-work/567-d1/crew-handoffs/g3-implementer-result.md`.

## Close criteria

1. Both specs name the door.
2. Both state the second-checklist truth (the door refuses to rebind while the process holds its own
   lease).
3. `python3 -m pytest tests/test_cli_retirement_guard.py -q` reports **no** violation at any `specs/`
   address.
4. Both files still parse as TOML.
5. The schema question is settled with reasoning.
6. The dangling `config_ref` is recorded with evidence.

The Commander has re-run 1–4 and 6 independently (gate check exit 0, TOML parses, non-workbench site
list empty). Re-run them anyway; do not spend your budget there.

## The review's real work

### 1. Is the vocabulary TRUE?

This is the whole gate. Read both files' new prose as the role would, and check each claim against
the measurement rather than against plausibility:

- Does it promise a door path the measurement shows does not exist? **That is the failure mode.**
- Does it leave the role with no path at all? (`global-everyone.md`: *"Fail visibly … no hidden
  fallback."*)
- Does it say *why* the door cannot be moved onto a second checklist, or just that it cannot? The
  reason — one door drives one spine, and the lease is what blocks the rebind — is what stops a
  future author "fixing" it.

**Verify the refusal yourself, in a fresh process with explicit paths** rather than trusting the
quoted text. `docs/agents/ORCHESTRATOR_CONTEXT.md` §Dogfooding requires exactly that, and an
in-session observation is struck from any gate that would accept it. `scripts/mcp_spine_server.py`,
`_spine_bind` is **read-only — lane E owns it.**

### 2. Judge the schema decision

Prose only, no new keys, reasoned from `_compile_gate`. Read `scripts/generate_spine.py` yourself
and say whether that reasoning holds — specifically, whether a new key would have had a consumer. If
it would, prose-only is under-delivering; if it would not, a new key would be dead weight.

### 3. The guard is watching this file

Gate `g1` extended `tests/test_cli_retirement_guard.py` to walk `specs/**/*.toml`, precisely because
the cold plan critic flagged `specs/` as a fresh unguarded surface for this kind of text. So the new
prose is inside the walk, and it may **name** the engine as a component but not **show** the command.

Confirm the guard's silence on `specs/` is real and not vacuous: check the census line shows
`2 under specs/` and that the walk's floors pass. An absence result over a walk that stopped reaching
`specs/` reads exactly like a passing guard.

### 4. `config_ref`

Both specs set `config_ref = "docs/agents/engine-config.json"`, which **does not exist in this repo**.
The gate said *record, do not necessarily fix*. Confirm what was recorded is accurate, and say
whether leaving it was right.

## Constraints on you

1. Re-run every verification command yourself and read the exit code.
2. Do not edit anything.
3. Do not edit `tests/test_cli_retirement_guard.py`.
4. The guard failing on `skills/workbench/**` is known and expected — lane D2's fenced files, this
   lane merges last, `g5-final` re-checks after the rebase.
5. **Author any shell in POSIX form** — the engine runs `command` checks through `/bin/sh` (`dash`
   here) and `set -o pipefail` is rejected with exit 2.
6. **Do not run the whole suite while driving your own survey through the engine** —
   `tests/test_gauge_chain_writer_to_trip.py:604` snapshots every file under the repo's
   `.agent-work/` and asserts nothing moved, so your own records produce a failure that is yours. A
   sibling reviewer in this lane hit exactly that.
7. Write your Fowler record to `.agent-work/567-d1/g3-review/FOWLER_PASS.json`, not the template's
   work-id-root default — that path already holds another gate's record.

## Verification commands

```sh
cd /home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard
python3 -c "import tomllib;[tomllib.load(open(p,'rb')) for p in ['specs/implementer.spine.toml','specs/reviewer.spine.toml']];print('toml ok')"
grep -i 'door' specs/implementer.spine.toml specs/reviewer.spine.toml
python3 -m pytest tests/test_cli_retirement_guard.py -q > /tmp/g3r.log 2>&1
grep -oE '^E +(skills|specs|[.]agent-work)/[A-Za-z0-9_./-]+' /tmp/g3r.log | sed 's/^E *//' \
  | grep -v '^skills/workbench/' | sort -u        # expect nothing
grep -c 'under specs/' /tmp/g3r.log               # the census must still say the walk reached specs/
```

## Map anchors (inbound)

No architecture map exists (`map_orient` → `DEGRADED-UNPARSEABLE`). Entry points:

- `specs/implementer.spine.toml`, `specs/reviewer.spine.toml` — ~90 lines each.
- `scripts/generate_spine.py`, `_compile_gate` — what consumes a spec; the basis of the schema
  decision.
- `scripts/mcp_spine_server.py`, `_spine_bind` — the refusal text and
  `decision:one-spine-per-process-stands`. **Read-only, lane E's.**
- `.agent-work/567-d1/notes-1.md` §M1 — the fresh-process probe that measured the refusal.
- `.agent-work/567-d1/LAUNCH_ORDER.md` — the Admiral's F-1 ruling on second-checklist wording.

## Authority

Commander `567-d1`, under Admiral launch order `cmdr-567-d1` (epic #567, wave 2, lane D1).

## Stop conditions

Stop and return if: the vocabulary promises a path the measurement contradicts; the guard's silence
on `specs/` turns out to be vacuous; or reviewing would require editing a fenced file.

## Return format

Write the full `REVIEW_RESULT` to
`.agent-work/567-d1/crew-handoffs/g3-reviewer-result.md` **before ending your turn** — that write is
the delivery. Include a `Verdict` field whose value is exactly `APPROVE` or `BLOCK` (uppercase).
Include a `Workflow Feedback` section: what helped, what got in the way, and your own mistakes.

Survey state location: `.agent-work/567-d1/g3-review/review.json`.

---

# REWORK ADDENDUM — read this first

Your predecessor reviewed this gate and returned **BLOCK**, correctly and precisely. Its result is at
`.agent-work/567-d1/crew-handoffs/g3-reviewer-result.md` — **read it before anything else**. Do not
re-derive what it established.

## What it established, and what you must NOT re-open

It measured in three fresh processes **with a positive control**, and all of this stands:

- The rebind refusal is real, quoted verbatim, and total.
- It is conditioned on **holding your own lease and nothing else** — the identical `spine_bind` call
  succeeds after releasing.
- An **unbound** door binds and drives fine, identity derived from the spine's own `work_id`. So a
  crew dispatched without `--spine` **can** drive its own plan through the door. My original handoff
  claimed the opposite; the implementer refused that premise and measured it, and your predecessor
  reproduced the correction and was itself the live case. **The prose is right here.**

## The blocker, and the fix

Both specs asserted that releasing the lease is barred because *"the **archive gate** requires the
lease to cover every journaled action, so releasing it fails your own closeout."* False as stated:
`archive gate` appears nowhere in `skills/`; the Commander archive gate's only lease postcondition is
`c3` "engine session lease released" with `check: null`; `spine_lifecycle.py` refuses in the
**opposite** direction; and neither crew plan template has a closeout gate at all.

The rework does two things. Confirm both:

1. **Names the check correctly** — the *terminal provenance check*, as
   `skills/{reviewer,implementer}/SKILL.md:17` word it.
2. **Scopes the claim to its reader**, which is the better half of the fix:
   *"Dispatched without a spine of your own you arrive holding no lease — nothing to release, and the
   escape never arises."*

## What this re-review is for

**A re-review, not a fresh one.** Spend your budget on:

1. **Is the replacement true, and is every remaining factual assertion in both specs true?** That is
   what the BLOCK was actually about: not careless prose, but one claim with no measurement behind it
   sitting in a sentence advertising one. Go through the new paragraph claim by claim and name the
   file, symbol or measurement behind each. Any claim you cannot ground is a finding.
2. **Is the scoping right?** The paragraph now addresses two readers — an in-session agent holding
   its own lease, and a dispatched crew holding none. Confirm both halves are true of their reader
   and that neither reader is left with the other's rule.
3. **Did the repair land identically in both files?** The paragraph is duplicated near-verbatim; a
   divergence here is the drift this whole epic is about.
4. **Nothing regressed:** TOML parses, guard silent on `specs/` (and non-vacuously — check the census
   still says `2 under specs/`), scope confined to `specs/`.

`APPROVE` if the blocker is closed and nothing regressed. `BLOCK` again if not — this gate has
already shown a second look is worth its cost. Rework budget 1 of 3 used.

Survey state location: `.agent-work/567-d1/g3-review/review-2.json` — a **new** file, so round 1's
consolidated survey is preserved as the audit record of the BLOCK. Fowler record:
`.agent-work/567-d1/g3-review/FOWLER_PASS-2.json`.

**Write your result to `.agent-work/567-d1/crew-handoffs/g3-reviewer-result-2.md`** — a new path,
overriding the Return format section above, so round 1's result is not overwritten.

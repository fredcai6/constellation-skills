# Plan alternatives — issue #447

Two gate plans authored in parallel by independent Opus agents under **distinct constraints**, per the
design-it-twice standard. Neither author saw the other's work. Both read only `PROBLEM_STATEMENT.md`
and `MISSION_FRAME.md`.

- **A — minimum blast radius.** Smallest edit set that makes all four Done conditions true; deleting
  preferred over rewriting; every touched line a cost to justify.
- **B — maximum durability, guard as centerpiece.** Design so regression is structurally prevented;
  machine-enforced invariants over prose; "what would have caught #308 mechanically?"

## The convergence that matters: both found the same undiscovered defect

Independently, in different words, both authors found this and neither was told to look:

> `scripts/apply_episode_delta.py:505` — `store_root()` returns
> `Path(__file__).resolve().parent.parent / "episodes"`. Bundled into a skill and installed, that
> resolves to `~/.claude/skills/constellation-commander/episodes` — **the skill install directory, not
> the project repo.**

**Verified at source before acceptance** (not taken on the agents' word):

```
installed writer exists: False
store_root() would be: C:\Users\fredc\.claude\skills\constellation-commander\episodes
repo store_root() is  : C:\Programs\constellation-skills-wt\epic418-h-447\episodes
```

This is decisive for the plan. Swapping the spine onto the episode writer **without** fixing this
ships a write path that silently creates a store outside the repo while every gate reports green —
which is #308's exact failure shape wearing the new name. B's framing is the one adopted: this is
**in scope by necessity, not hardening**, because without it obligation 2 does not work at all.

## Where they diverged, and what was taken

| Question | A | B | Taken |
|---|---|---|---|
| When is the guard authored? | g1, red against untouched tree | g1, red against untouched tree | **Agreed — the tree IS the decoy.** No synthetic decoy to plant, nothing to forget to revert. |
| Guard return shape | pytest assertions | `scan() -> list[Violation(leg,path,line,detail)]`, never a bool | **B.** A bool cannot support `== [LEG_X]`, so per-leg falsification would be untestable. |
| Guard lives where | `tests/` only | `scripts/verify_retirement.py` + `tests/` | **B.** A script is runnable by a human mid-review; the test is the CI enforcement. |
| "Episodes ≠ playbook" enforced how | forbidden-phrase wordlist over `skills/**` | four topological legs, wordlist demoted to explicit backstop | **B, decisively.** See below. |
| Historical docs (`RECURSIVE_IMPROVEMENT_DESIGN.md`, 37 sites) | one superseding header, 37 sites frozen | superseding header | **A's framing.** Rewriting a design record to describe a system it did not describe is falsifying history. |
| Live-vs-record decided by | **location**, from an allowlist checked against what the installer ships | `RECORD_ONLY_ROOTS` dict with a required reason per root | **Both, merged.** Allowlist for the surface; each excluded root carries a written reason. |
| Scaffolding removal | manual final gate | `xfail(strict=True)` — strict XPASS fails the suite when the tree goes clean | **B.** One line, keeps CI honest mid-run, and removes itself by force rather than by memory. |
| Spine `c1` handling | **never delete `c1`** — it is the bare-form `attest` default; retarget in place, delete only terminal conditions | deletes/retargets freely | **A.** Verified in `checklist_engine.py`; renumbering would break bare attests. |

## The load-bearing disagreement, resolved

A's guard tests **vocabulary** ("does a line say `read` near `episode`"). B's guard tests **topology**:

1. **Bundle asymmetry** — `apply_episode_delta.py` (the writer) is bundled to commander+admiral;
   `query_episodes.py` (the only reader) is bundled to **nothing**, asserted. A reader that is never
   installed cannot be run by an installed skill. This is a fact about `SKILL_SCRIPT_BUNDLES`, not
   about anyone's intentions.
2. **No episode address in any instruction** — regex composed from `apply_episode_delta.ID_RE`, so a
   grammar change propagates instead of drifting. You cannot condition behaviour on a record without
   naming it.
3. **The output valve** — the capture verifier parses only the state header and the `- run:` line,
   never an assertion `statement`. Proven by a sentinel test (seed a store where every statement is
   `SENTINEL-DO-NOT-LEAK`, assert it appears in neither stdout nor stderr), which has its own red proof.
4. **Schema has no slot for a rule** — `AGENT_SUPPLIED_KINDS` pinned to the five past-tense
   observational kinds. A prescription needs somewhere to sit; growing that slot fails the guard.

A wordlist is paraphrase-fragile and fires on prose that legitimately *describes* the store. It is
kept as leg 5, **documented in the module docstring as the explicitly weakest leg**, so nobody later
mistakes vocabulary-matching for the invariant.

## Untaken roads, named

- **Retarget `verify_agent_feedback.py` at `episodes/` instead of replacing it.** Rejected: its whole
  contract (durable-root placement, bare-`none` rejection, the staged trio) is playbook-shaped. Porting
  it is the "re-point the read path at `episodes/`" failure the launch order names.
- **A's `git mv` to preserve blame.** Rejected: the body is ~100% rewritten, so the preserved blame
  would be misleading rather than useful.
- **A spine postcondition running the guard every run.** Rejected as over-engineering (B named it as
  such itself): pytest in CI plus the `deny_globs` tombstone are already two independent mechanisms.
- **Migrating `AGENT_FEEDBACK.md`'s 2056 prose lines into episodes.** Rejected by BOTH authors
  independently: synthesising typed assertions from unstructured prose is fabrication that the store's
  own doctrine forbids. Drop with stated reason; git history retains it.

## Converged recommendation

Seven gates: **g1** guard authored and proven red on the real tree → **g2** replacement capture
verifier + the `store_root()` fix → **g3** rewire spines and install bundles → **g4** carry the six
live lessons through the writer → **g5** delete the machinery and untrack the two files → **g6** prose
pointers, the `docs/agents/` tombstone, superseding headers → **g7** flip the guard green, remove the
xfail, full suite.

Guard first is the single choice that carries the run: every later gate's evidence becomes a named
invariant going red→green, instead of an assertion that the work was done. That is precisely what
#308 could not produce.

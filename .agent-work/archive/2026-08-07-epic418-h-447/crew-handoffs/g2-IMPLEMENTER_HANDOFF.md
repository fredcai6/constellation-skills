# Implementer handoff — g2: the replacement capture obligation

**Worktree:** `C:/Programs/constellation-skills-wt/epic418-h-447` · branch `epic-418/h-447-episodes-retirement`

## Protected intent

We are retiring `.agent-work/LESSONS.md` (a playbook agents were told to **read** and condition
behaviour on) and `.agent-work/AGENT_FEEDBACK.md` (a write-only retrospective). Both are replaced by
the episode store: **a record of what happened**.

The human's constraint, verbatim, 2026-08-06:

> *"we shouldn't be reading the episodes like lessons, it's a store for things that happened to
> replace both feedback and lessons."*

The failure mode this gate exists to avoid is building a replacement that quietly re-creates the read
path under a new directory name. **You are building the WRITE-side gate only.** If you find yourself
making it easier for an agent to read episodes back, stop — that is the defect, not the feature.

Build the replacement **before** the old machinery is deleted (that is g4), so there is never a window
with no closeout path.

## Task

### 1. `scripts/verify_episode_captured.py`

CLI: `verify_episode_captured.py <work-id> [--store-root PATH] [--phase feedback|archive]`

- Enumerate `<store-root>/active/*.md`; match episodes whose mechanical `- run:` line equals the
  work id. Exit 1 with a clear message if none match; exit 0 and print the matched ids and a count
  otherwise.
- Under `--phase archive`, additionally require `git ls-files --error-unmatch <path>` to succeed for
  each matched episode, so a run that writes an episode and forgets to `git add episodes/` genuinely
  fails. This is what replaces the old archive-phase durability question.
- A **missing** `active/` directory must be **refused, not answered**. `episodes/README.md` states the
  rule: *"A missing directory is refused, not answered"* — a typo'd `--store-root` enumerating to zero
  episodes with exit 0 reads exactly like an empty store. Match that behaviour.

### 2. THE VALVE — the load-bearing design property, not a detail

**The verifier parses ONLY the `<!-- episode-state: -->` header line and the `- run:` mechanical line.
It MUST NOT parse, store, or emit any assertion `statement`, and MUST NOT import `query_episodes`.**
Ids and counts out; statements never. That is the mechanical difference between a capture gate and a
read path: a gate that can surface episode content is one refactor away from being the playbook again.

It asserts **capture only** — no ripeness, no apply-or-defer, no dormancy, no counters. Those are
playbook concepts and they retire with the playbook. Do not port them.

**Prove the valve, do not assert it.** In `tests/test_verify_episode_captured.py`:
- Seed a temp store where **every** assertion statement is the literal `SENTINEL-DO-NOT-LEAK-9f2a`.
- Run the verifier with stdout **and** stderr captured; assert the sentinel appears in **neither**.
- Give that test its **own red proof**: monkeypatch the verifier to echo the record body, and assert
  the sentinel **is** then found. A leak test that cannot fail is worth nothing — this repo has a
  twice-observed lesson about exactly that, and it is the reason this gate is specified this way.

### 3. `store_root()` — comment only, no behaviour change

`scripts/apply_episode_delta.py:505` has:
```python
return Path(__file__).resolve().parent.parent / "episodes"
```
Measured hazard: once this script is bundled into a skill and installed, that resolves to
`~/.claude/skills/constellation-commander/episodes` — **the skill install directory, not the project
repo.** A spine that invokes the writer without an explicit `--store-root` would silently create a
store outside the repo while every gate reported green. That is #308's failure shape wearing a new name.

**Do NOT change `store_root()`'s semantics.** Its docstring already rules out `durable_root()` for a
documented reason (it would silo the store per worktree), and a retirement is not the place to
overturn that ruling. Instead: **leave a comment at `store_root()`** naming this hazard and stating
that callers on an installed copy must pass `--store-root` explicitly. g3 wires that into the spine
commands.

## Allowed scope

**CREATE:** `scripts/verify_episode_captured.py`, `tests/test_verify_episode_captured.py`.
**COMMENT ONLY:** `scripts/apply_episode_delta.py` at `store_root()`.
**Touch nothing else.** Do not edit spines, install bundles, or the guard — those are g3.

Note: `scripts/verify_retirement.py`'s `replacement-absent` leg is currently RED and names this
script. It stays red until g3 wires the spines; that is expected and is not yours to fix.

## Constraints

- `python`, **never** `py` (py has no pytest here and produces fake greens).
- Windows: `encoding='utf-8', newline='\n'` explicitly on every write.
- Do not commit — the Commander commits at integrate.
- Scope-discipline ruling in force: build what needs to work and no more; a corner case you choose not
  to chase gets a comment **at the code site** and is reported up, never silently absorbed.

## Required evidence — commands that can genuinely fail

```
python -m pytest tests/test_verify_episode_captured.py -q
python scripts/verify_episode_captured.py no-such-run --store-root episodes ; echo EXIT=$?   # MUST be 1
python scripts/verify_episode_captured.py issue-308 --store-root episodes ; echo EXIT=$?     # MUST be 0 (the store holds issue-308 episodes)
python scripts/verify_episode_captured.py issue-308 --store-root /nonexistent ; echo EXIT=$? # MUST be non-zero: refused, not answered
python -m pytest -q
```
Redirect to a file then `echo $?` — a pipe captures the pipe's exit code, not the command's.

## Close criteria

1. Passes on a seeded store; fails on an empty store; fails on a store holding only other runs' episodes.
2. `--phase archive` fails on an episode that exists but is not committed.
3. A missing `active/` directory is refused, not answered as zero.
4. The sentinel test proves no statement text reaches stdout or stderr, **and** its own red proof shows
   that test can fail.
5. No new failures in the full suite.

## Report back

`IMPLEMENTER_RESULT` to `.agent-work/epic418-h-447/results/g2-IMPLEMENTER_RESULT.md`: diff summary,
every evidence command with its **real** exit code, the sentinel red-proof output, corner cases not
chased with their comment file:line, and a **Workflow Feedback** section. Deliver your result via your
final message before ending your turn.

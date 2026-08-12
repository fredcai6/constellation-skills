# commander-315 working notes — issue #315, command-check cwd

## Worktree isolation (run first, before any git action)

```
$ py /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py \
     --here /home/tommy/projects/constellation-skills-wt/epic-568-315
worktree OK: in /home/tommy/projects/constellation-skills-wt/epic-568-315
EXIT=0
```

## The defect, confirmed in place

`scripts/checklist_engine.py:787`

```python
proc = subprocess.run([shell, "-c", command], capture_output=True, text=True)
```

No `cwd=`. The child inherits the engine process's cwd, which is the launcher's
cwd, not the spine's location.

**`base_dir` is already threaded to this exact point and is simply not used
here.** `main()` computes `base_dir = path.parent` (the spine file's directory,
line 3299) and passes it through `dispatch` → `_run_verb` → `advance`/`start`/
`record` → `_check_condition(cond, t, base_dir)`. Inside `_check_condition`, the
`git-change-policy` branch consumes it (line 862) but the `command` branch (line
831) calls `_run_check_command(chk["command"])` and drops it. So the plumbing
exists; only the last hop is missing.

## The design question: cwd resolves to WHAT?

`base_dir` is the **spine's directory** (e.g. `.agent-work/commander-315/`).
That is NOT the same as the repo root, and the difference decides the whole
blast radius. Three candidates:

- **A. `cwd = base_dir`** (spine directory)
- **B. `cwd = the repo/worktree root enclosing the spine`**
- **C. no change** (honest null)

Prior art in the repo, all pointing at B:

- `docs/CHECKLIST_SCHEMA.md:39-41` records the current behaviour as a known
  defect and states the workaround: *"A `command` check receives no `cwd`.
  Already noted in `init_work_area.resolve_spine`'s docstring (#341); measured
  live here as a check that silently found nothing when run from outside the
  repo. Every command the generator emits is therefore anchored `cd <repo-root>
  && ...`."* The anchor the corpus already reaches for is the **repo root**.
- `scripts/generate_spine.py:946` probes candidate checks at generation time
  with `subprocess.run(["bash", "-c", command], cwd=str(repo_root), ...)` — the
  generator already validates checks **against the repo root**. If the engine
  ran them anywhere else, the generator's probe would be testing a different
  thing than the engine runs.

The enumeration below settles it empirically.

## Blast-radius enumeration (by command, not from memory)

Enumerator: `scratchpad/enumerate_checks.py` — parses each checklist JSON,
walks every `check` object with `kind == "command"`, and classifies the command
text. Two distinct cwd-dependence classes, because the second is invisible to a
grep:

- **R1-RELATIVE** — the check text itself contains a relative path token
  (`scripts/x.py`, `.agent-work/<work-id>/y.json`, `--store-root episodes`).
- **R2-CWD-SCRIPT** — the check text has no relative token, but it invokes a
  script whose project root **defaults to cwd**, without pinning `--root`
  absolutely. Measured by reading each script's argparse default:

  | script | root default | verdict |
  |---|---|---|
  | `init_work_area.py` | `--root` → cwd | cwd-defaulting |
  | `verify_state_note.py` | `--root`, `default=Path(".")` | cwd-defaulting |
  | `verify_cycles.py` | `--root`, `default="."` | cwd-defaulting |
  | `verify_spec_confirmed.py` | `--root`, `default="."` | cwd-defaulting |
  | `verify_iterative_role_artifacts.py` | hardcoded `Path.cwd()`, no `--root` | cwd-defaulting |
  | `map_orient.py` | `--root` | cwd-defaulting **unless** `--root` passed |
  | `verify_episode_captured.py` | `--store-root` → skill dir (absolute) | clean unless passed a relative value |
  | `verify_interrogation.py`, `verify_fowler_pass.py`, `verify_worktree_isolation.py` | take explicit paths | clean |

Command run:

```
py scratchpad/enumerate_checks.py $(git ls-files 'skills/*/templates/*.json')
py scratchpad/enumerate_checks.py $(git ls-files '.agent-work/templates/*.json' | grep -v '/.baseline/')
```

### Counts

| corpus | total command checks | R1 | R2 | cwd-dependent | clean |
|---|---|---|---|---|---|
| `skills/*/templates/*.json` (source of truth, what installs to users) | 22 | 6 | 11 | **17** | 5 |
| `.agent-work/templates/*.json` (this project's installed mirror) | 21 | 5 | 10 | **15** | 6 |

The 5 "clean" in the source corpus: 2 × `map_orient.py --root <repo-root>`
(root pinned absolutely), 2 × `<exact test command>` (an unfilled placeholder
the authoring role supplies per run — not measurable here), and 1 × the
`gh pr list` check. That last one is honestly a sixth cwd-dependent case:
`gh` resolves the repo from cwd. Its `git -C <repo-root>` half is pinned; its
`gh` half is not. Counted as clean by the tool, flagged here as an undercount.

### Disposition of every hit

**Zero repairs needed.** The decisive measurement:

```
$ ... | grep -cE '\.\./|spine\.json|gauge\.json'
0
```

**No shipped check is authored relative to the spine directory.** Every single
relative check — all 17 — is authored relative to the **repo root**. So:

- Under **option B (cwd = repo root)**: all 17 resolve correctly. Every hit is
  *ruled correct under the new resolution*, none need repair. The fix is the
  engine change alone.
- Under **option A (cwd = spine dir)**: all 17 break at once, because
  `.agent-work/<work-id>/` is two levels below the root every check assumes.
  Option A would turn a one-line engine fix into a 17-check corpus rewrite and
  break every already-archived spine as well.

That asymmetry is the answer to the design question. **Option B.**

### Was "five" right?

**No. Filed: 5. Measured: 17** cwd-dependent command checks in the shipped
source corpus (22 total), of which 6 carry a literal relative path token and 11
are cwd-dependent only through a script whose root defaults to cwd.

If "five shipped relative checks" was counting only literal relative path
tokens, the nearest defensible number is **6** (R1 in the source corpus) — still
not 5, and it misses the 11 R2 cases entirely, which are the ones a reader would
never find by grepping for a slash. The filed number understates the exposure by
roughly 3x. This is a reporting finding, not a scope change: the repair count is
still zero, because the fix moves the resolution rule to the root all 17 already
assume.

## Pre-fix suite baseline (so "green after" means something)

```
$ py -m pytest tests/test_checklist_engine.py -q
441 passed, 140 subtests passed in 2.06s

$ py -m pytest tests/ -q -p no:randomly
2932 passed, 5 skipped, 1121 subtests passed in 120.53s
```

## Fix shape

Thread the existing `base_dir` into `_run_check_command` and resolve it to the
enclosing repo/worktree root:

- walk up from `base_dir` for a `.git` entry (a **file** in a linked worktree, a
  **directory** in a plain checkout — both count), no subprocess, no git dependency;
- no `.git` found (spine in a bare temp dir, as most engine tests do) → fall back
  to inherited cwd, i.e. exactly today's behaviour. Conservative: no test that
  builds a spine outside a repo changes meaning.
- `base_dir is None` (checklist processed without a file path) → inherited cwd.

`agent_work_root.durable_root()` is deliberately **not** used: it redirects a
linked worktree to the MAIN checkout, which is the opposite of what a check
needs — a check must run against its own worktree's files. Using it would make
this worktree's checks verify the Admiral's checkout. It is also a forbidden
file this wave; not edited, and not depended on.

The POSIX-shell routing and the `returncode 127` / `no-posix-shell` path are
untouched — `cwd=` is added only to the branch that already calls
`subprocess.run`.

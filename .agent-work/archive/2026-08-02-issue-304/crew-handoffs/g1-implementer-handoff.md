# Implementer Handoff — issue-304 gate g1: resolver, receipt, reported degraded mode

## Assigned task

Build `scripts/map_orient.py` (subcommands `orient`, `verify-orientation`), add the `<repo-root>`
placeholder to `scripts/init_work_area.py`, and ship two test files including an **executed** mutation
floor.

Work ONLY in `C:/Programs/constellation-skills-wt/e298-304`. Never touch `C:/Programs/constellation-skills`
or `C:/Programs/constellation-skills-wt/e298-331`. f1Brainz (`C:/Programs/f1Brainz`) is **read-only** —
you may read it to ground the resolver against a real map; no writes, no git operations there.

## Protected intent

The deficiency is **primacy and contract, not path**. A resolver that only resolves a path ships a
capability f1Brainz already has and fails the issue. Your half of the contract is the **REPORTED
degraded mode**: degrading is fine, degrading *silently* is refused. **Degraded is the COMMON case** —
this repo has no `docs/architecture/` at all — so give it at least equal design attention.

## Deliverables

### 1. `scripts/map_orient.py`

Two subcommands now (`verify-frame` lands in g2 — do not build it):

```
map_orient.py orient             --root ABS --work-id ID [--entrypoint REL]
map_orient.py verify-orientation --root ABS --work-id ID
map_orient.py --self-test
```

**Exit-code vocabulary — FROZEN, and it must avoid a real collision.** `argparse` exits **2** on a usage
error, an unhandled traceback exits **1**, and the engine synthesizes **127** when no POSIX shell is
found. Since the engine records only `{cmd, exit, shell}` and **discards stdout**, a mistyped flag must
never be indistinguishable from a truthful verdict. **Put the semantic codes above the collision range**
(e.g. 0 = satisfied, then 10/11/12… for the semantic verdicts). Document the table in the module
docstring. Exit 0 = contract satisfied (RESOLVED **or** a fully-discharged DEGRADED).

**stdout** first line is always one reserved literal (`RESOLVED`, `DEGRADED-NO-MAP`,
`DEGRADED-EMPTY-MAP`, `DEGRADED-UNPARSEABLE`, `UNRESOLVABLE-ROOT`) — never blank, never a bare count.
The agent runs `orient` itself, so stdout is real there; the engine only ever sees the exit code.

**Resolution rule**, ordered, first hit wins, but **record every candidate tried** (a delivery record,
not a first-hit lookup):
1. `--entrypoint REL` if given
2. `docs/architecture/generated/map.json` — parses, ≥1 `nodes[].id`
3. `docs/architecture/index.md`
4. `docs/architecture/` containing ≥1 non-empty `packets/*.md`

**RESOLVED requires CITABLE CONTENT, not mere existence.** Extract anchor ids with a format-agnostic
token scan: `\b(struct|capability|event|constraint|assumption|claim|decision):[A-Za-z0-9_.\-]+\b`.
≥1 unique real id (not a `<placeholder>`) = RESOLVED. Do **not** couple to
`build_architecture_map.parse_packet` — this repo's packet template uses bold fields while f1Brainz uses
YAML fences, and the strict parser returns zero nodes on the one repo that has a real map. Verify that
claim yourself against `C:/Programs/f1Brainz/docs/architecture/`.

A file that exists but yields nothing citable is **DEGRADED-UNPARSEABLE**, never RESOLVED. A false
RESOLVED is strictly worse than an honest DEGRADED — it satisfies the whole contract on an empty map.

**Distinguish "could not look" from "looked and found nothing"** (#265): `UNRESOLVABLE-ROOT` requires a
**positive** repo-root proof (`.git` present, or `git -C <root> rev-parse --show-toplevel` succeeds),
not an absence test. A bare non-repo directory is `UNRESOLVABLE-ROOT`, not `DEGRADED-NO-MAP`.

**Receipt** at `.agent-work/<work-id>/map-orientation.json`, schema documented in the docstring:
`schema_version, work_id, root, mode, entrypoint, anchor_count, candidates_tried[], substitutes[]
(path + content hash), unmapped[], escalation, emitted_at`.

**`verify-orientation`** — the gate check. Exit 0 on RESOLVED with a well-formed receipt, or on a
**complete** DEGRADED record. Exit non-zero (semantic code) when DEGRADED is **incomplete**: it must
carry `substitutes` **AND** `unmapped` **AND** `escalation`. All three. An empty `substitutes` list is a
refusal, not a pass. Reject `"none"` / `"n/a"` / `""` as fillers.

**Hash-pin the substitutes** (their content hash goes in the receipt) — g2's frame check compares
against this committed prior declaration rather than a same-breath assertion.

### 2. `scripts/init_work_area.py` — `<repo-root>` placeholder

Add `<repo-root>` → `str(Path(root).resolve())` in `resolve_spine()`, and add it to the
unresolved-placeholder guard regex so an unresolved token fails loudly at init.

**Get the justification right — it was wrong in the first draft and the critic caught it.** Command
checks receive **no `cwd`**, so they **inherit the launcher's cwd**. Relative checks are **fragile, not
broken** — the five already-shipped relative checks work because the launcher is normally at the repo
root. `<repo-root>` is a **robustness** improvement. Do **not** write a comment claiming it fixes a
broken mechanism. (The fragility of those five is filed separately as #341 — do not fix them here.)

### 3. `tests/test_map_orient.py` — the mutation floor

Resolution matrix; every DEGRADED reason produced distinctly; candidates recorded even after a hit.
Plus, required:

- **`test_the_shipped_index_template_itself_does_not_resolve`** — feed
  `skills/cartographer/templates/ARCHITECTURE_INDEX.template.md` verbatim; assert DEGRADED. Uses a real
  committed file so it cannot rot into an unmaintained fixture.
- **`test_this_repo_resolves_degraded`** — run against this repo root; assert `DEGRADED-NO-MAP`. It will
  legitimately flip when this repo grows a map; that is the point.
- **The partial-fill matrix** — three cases, each omitting exactly ONE of `substitutes` / `unmapped` /
  `escalation` with the other two present, each asserting refusal. This is what kills an `all`→`any`
  mutation on all three arms. Plus a positive control (complete record passes) so `return False` can't
  fake it.
- **The discriminator pair** — a non-repo bare directory → `UNRESOLVABLE-ROOT`; the same directory with
  `.git` added → `DEGRADED-NO-MAP`. They differ in exactly one bit.
- **cwd-independence** — run with `cwd` set to an unrelated tmpdir; assert the verdict is unchanged.

### 4. `tests/test_mutation_floor.py` — falsifiability, EXECUTED

Mechanically apply each named mutation to a **copy** of the module, run the floor against the copy, and
assert it goes **RED**.

**LOAD-BEARING, and the reason this file exists — assert the mutation APPLIED before asserting red.**
Assert the post-mutation source **differs** from the original and that the intended replacement text is
**present**. If the substitution did not match, **fail loudly as a harness error** — never report a
killed mutant. A mutation that silently fails to match produces a green baseline that is
**indistinguishable from a killed mutant**; commander-299 hit exactly this with a non-matching `sed`
this epic. Without the applied-assertion, the check that verifies falsifiability is itself
unfalsifiable. **Prove you changed the thing, then compare.**

Mutations to pin at minimum:
1. `all(...)` → `any(...)` in the degraded-completeness check.
2. `UNRESOLVABLE-ROOT` collapsed into `DEGRADED-NO-MAP` with exit 0 — the #315 failure mode wearing a
   friendly face, and a naive tmpdir test passes identically before and after.
3. Citable-content requirement weakened to `path.exists()` — makes an empty map read RESOLVED.

## Allowed scope

`scripts/map_orient.py` (new), `scripts/init_work_area.py` (placeholder only),
`tests/test_map_orient.py` (new), `tests/test_mutation_floor.py` (new).

## Specific exclusions

- **Do NOT build `verify-frame`** — that is g2.
- **Do NOT wire anything into any template** — that is g2.
- **Do NOT delete any prose** — that is g3.
- **Do NOT build a bootstrap/CLAUDE.md stanza.** Ruled out: the map is orchestrator content, not
  implementer content.
- **Do NOT fix the five fragile relative checks** (#341) or touch the episode store (#342).
- Do not modify `checklist_engine.py`.

## Constraints

- Windows: write every file with `encoding='utf-8', newline='\n'`.
- Run tests with `python -m pytest` (`py` has no pytest; local python is 3.14 vs CI 3.12 — **avoid
  3.13+-only APIs** such as `Path.read_text(newline=...)`, which cost 39 CI failures on PR #320).
- Match house style in `scripts/`: module docstring stating modes and honest limits, `_utf8_stdio()`,
  pure decision functions separated from impure edges, `main(argv)` + `raise SystemExit(main())`,
  a `--self-test` falsification floor.
- Two-bin rule: machinize the mechanizable; what is not mechanizable stays prose. No third bin.

## Required evidence

- `python -m pytest tests/test_map_orient.py tests/test_mutation_floor.py tests/test_init_work_area.py -q` → green.
- `python scripts/map_orient.py --self-test` → green.
- Paste the actual output of `map_orient.py orient --root <this repo> --work-id probe` showing the real
  `DEGRADED-NO-MAP` verdict in the live degraded repo.
- State the exit-code table you chose and why it avoids the argparse/traceback/127 collision.

## Verification commands (POSIX form, absolute paths)

```
cd C:/Programs/constellation-skills-wt/e298-304
python -m pytest tests/test_map_orient.py tests/test_mutation_floor.py tests/test_init_work_area.py -q
python scripts/map_orient.py --self-test
```

## Stop conditions

Stop and report rather than guessing if: the resolver cannot distinguish "could not look" from "looked
and found nothing" without changing the exit-code contract; the mutation harness cannot assert a
mutation applied; or a required test would have to be written so it cannot fail. **Report "this specific
test failed", never "this approach is impossible."**

## Return format

Write `IMPLEMENTER_RESULT` to
`.agent-work/issue-304/crew-handoffs/g1-result.md`: what you built, the evidence above pasted verbatim,
any deviation from this handoff with its reason, and any unresolved blocker. **Return thin, write fat** —
the artifact is what I read.

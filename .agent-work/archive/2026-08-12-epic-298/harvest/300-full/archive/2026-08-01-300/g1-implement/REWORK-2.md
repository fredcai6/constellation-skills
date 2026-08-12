# Rework 2 — gate `g1-implement` (cold-panel findings)

A three-lens cold panel reviewed the committed diff with no authoring context. Full critiques:
`.agent-work/300/cold-panel/CRITIC-{intent-fit,testability,simplicity}.md`. Read the testability one
in full — its method was 45 deliberate mutations in a sandbox worktree, 11 of which **survived**, and
the surviving set is the real map of where the suite is blind.

**What the panel confirmed is genuinely sound — do not touch it.** `rev()` was verified against the
`git hash-object` oracle at every edge (empty, no trailing newline, non-ASCII, CRLF, lone CR, NUL,
10 MB) with no defect found. The no-enumeration guard, the LF-pinned writes, the imported
`active_id`, the single encoder, and the lint's boundary rule in both directions all held. The
producer's core is tight and the panel said so plainly.

Fix the following. Everything else from the panel is triaged elsewhere — do not widen.

## BLOCKING B2 — the acceptance test never compares the bytes the two environments produced

`tests/test_context_determinism.py` parses both children's artifacts and re-encodes them with the
**parent's** `cm.encode`/`cm.content`. So the thing actually compared is the parent's rendering of two
parsed objects, not what the two environments wrote. The critic demonstrated it: an `encode()` whose
indent depended on `LC_ALL` produced different bytes in each environment and the test passed green.

This is the issue's single acceptance test failing to falsify the property it exists to falsify.

**Fix:** have each child compute and write its own **content bytes** (the exact bytes its own encoder
produced for the content subtree), and have the parent compare **those bytes** directly. The parent
may still parse for diagnostics, but the assertion must be over child-produced bytes. Add a
regression fixture: an encoder made environment-dependent must now **fail** the test — prove it by
running it, and paste the before/after.

## BLOCKING B1 — `/run` is not actually the exclusion set

The guarantee documented as *"a new varying field cannot become accidentally content"* is untrue.
`content()` hardcodes `k != "run"`, and the test asserts `set(m) - set(content(m)) == {"run"}`, which
is one-directional and blind to **added** keys. Injecting `run.host.cwd` into `content()` survives
the whole suite — and cwd is precisely the environment fact `run_facts()` already reads.

**Fix, two parts:**
1. Make `content()` derive from an **explicit allow-list** of content keys rather than a denial of
   one key, so a new key is excluded by default and must be deliberately admitted.
2. Make the assertion **bidirectional**: `set(manifest) == set(content) | {"run"}`, so both an added
   content key and a removed one fail.
3. Add the critic's mutation as a test: a varying field placed outside `/run` must **fail**.

Then either correct the docstring's claim or make it true. Do not leave a documented guarantee the
code does not keep — that exact defect already cost this issue one rework round in the lint.

## SERIOUS — the vacuous and unpinned cases

- **S3 `RealCheckoutSkew` is vacuous everywhere.** All six declared rows are `rev: None` on both
  sides, so its headline `assertNotEqual` never executes. Make it operate on a declaration that
  resolves to **real tracked files**, or delete it — a test that cannot fail is worse than no test,
  because it reads as coverage.
- **S6 the shipped declaration's contents are unpinned.** An entry can be silently dropped from
  `COMMANDER_SPINE.template.json`'s `context_refs` and nothing fails. Pin the expected set.
- **S7 `declaration_of`'s type guard is untested** — an invalid declaration (wrong type) silently
  becomes an empty manifest. Silence is the wrong failure mode here: raise, and test it.

## SERIOUS — committed files cite gitignored paths (three critics found this independently)

`context_manifest.py`'s `rev()` docstring cites a "gate's `.gitattributes` grep" that exists **only**
in `.agent-work/300/execute.json` — gitignored, worktree-local, and destroyed by
`git worktree remove`. The committed design-doc section cites `.agent-work/300/` files too. No reader
of `main` can open any of them.

**Fix:** remove every citation of an `.agent-work/` path from **committed** files. Where the fact
matters, state it directly in the committed text instead of pointing at a process artifact. The
`.gitattributes` condition is a real constraint — say what it is, do not cite where it is checked.

**Related, same fix:** the testability critic found that the `.gitattributes` guard does not actually
pin what the docstring leans on — exemptions scoped to the declared corpus
(`skills/**/references/*.md -text`, `docs/agents/*.md -text`) all survive it. Either widen the claim's
statement to match reality or say plainly that the guard covers only the unscoped case.

## SIMPLICITY — delete what has no caller

Verified by grep across the worktree, zero callers each: `RUN_POINTER` (advertises a JSON-pointer
contract the code does not implement), `run_facts(session_id=)` (so every manifest carries a
permanently-null field), `run_facts(now=)`, `build_manifest(run=)`, `produce(run=)`. Delete them.
`build_manifest(step=)` has one test caller which can set `init` complete as the determinism child
already does — delete it too unless removing it costs more than it saves; say which you chose.

Also delete `test_a_live_spine_in_this_work_area_also_projects` — it is a 24-line no-op whose own
comment argues for its deletion.

## Explicitly NOT in this rework — do not do these

- **Do not add a caller for the producer.** The panel's third blocker (nothing ever invokes it) is a
  **scope question floated to the Admiral**. Adding a caller would pre-empt that decision.
- Do not touch the lint's trailing-boundary rule, the py3.12 AST guard, or `AdversarialDeclarations`
  — all triaged as keep-or-file, not rework.
- Do not touch `required` in the declaration schema.

## Constraints unchanged

`python -m pytest`, never `py -m pytest`. CI pins Python 3.12 (host 3.14.3) — no
`Path.read_text(newline=)`/`write_text(newline=)`. **No `skipTest`** — CI's skip guard uses an exact
triple allow-list. cwd = worktree root. Every write pins `newline="\n"`.

## Verification

```bash
cd C:/Programs/constellation-skills-wt/298-300
python -m pytest tests/test_context_manifest.py -q
python -m pytest tests/test_context_determinism.py -q
python -m pytest tests/test_context_declaration_lint.py -q
python -m pytest tests/ -q --junitxml=junit-report.xml
python scripts/verify_skip_guard.py junit-report.xml
rm -f junit-report.xml
py scripts/verify_context_declaration.py skills/commander/templates/COMMANDER_SPINE.template.json
grep -rn "agent-work" scripts/context_manifest.py docs/CHECKLIST_ENGINE_DESIGN.md docs/CHECKLIST_SCHEMA.md   # must return NOTHING
```

**Prove B1 and B2 are fixed rather than described:** paste transcripts showing each critic mutation
(a varying field outside `/run`; an environment-dependent encoder) now **failing** the suite where it
previously passed.

## Return

`.agent-work/300/g1-implement/IMPLEMENTER_RESULT-rework2.md`. Keep it accurate to what actually
ships — a stale result artifact was itself a review finding last round.

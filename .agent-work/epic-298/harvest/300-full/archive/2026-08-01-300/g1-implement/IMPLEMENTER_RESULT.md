# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1-implement` — issue #300 (epic-298), "the deterministic projection substrate and its manifest".
Worktree: `C:/Programs/constellation-skills-wt/298-300`.

## Completed slice
All six deliverables the handoff named, driven through the engine as an 8-item `gated` plan
(`.agent-work/300/g1-implement/PLAN.json`, session `sess-300-g1`):

1. `rev()` — the LF-normalised git blob OID, in-process, no `git` subprocess, no commit SHA.
2. The optional ordered `context_refs` declaration on the spine task object.
3. A pure producer in `scripts/context_manifest.py`, selecting via the engine's own `active_id()`.
4. The one envelope, written to `.agent-work/<work-id>/context/<step>.json` with `newline="\n"`.
5. The first real declaration on the Commander spine template's `context` step.
6. The cross-environment determinism acceptance test, plus the adversarial fixture set.

No CLI verb was added. No committed `CONTEXT_PROJECTION.json` and no `scripts/context_projection.py`
(Tommy's 2026-08-01 ruling).

## Scope
**Files changed:**
- `C:/Programs/constellation-skills-wt/298-300/scripts/context_manifest.py` — **new**
- `C:/Programs/constellation-skills-wt/298-300/tests/test_context_manifest.py` — **new**
- `C:/Programs/constellation-skills-wt/298-300/tests/test_context_determinism.py` — **new**
- `C:/Programs/constellation-skills-wt/298-300/tests/fixtures/context_declarations.json` — **new**
- `C:/Programs/constellation-skills-wt/298-300/skills/commander/templates/COMMANDER_SPINE.template.json`
  — **edited**, `context` step only, +8 lines / −0

Not committed by design (gitignored, per the handoff's deliverable path check):
`C:/Programs/constellation-skills-wt/298-300/.agent-work/300/context/context.json`.

`scripts/checklist_engine.py` was **not** touched — `active_id` was already importable, so the
"edit minimally if `active_id` needs exporting" allowance was not used at all.

**Specific exclusions touched:** `no`. `docs/CHECKLIST_SCHEMA.md`,
`docs/CHECKLIST_ENGINE_DESIGN.md`, the declaration-vs-prose lint, and `verify_spec_confirmed.py`
were all left alone. The `context` step's imperative prose is byte-identical (a test asserts the
substitute-and-record and sanctioned-degradation clauses are still present).

```
$ git status --short
 M skills/commander/templates/COMMANDER_SPINE.template.json
?? scripts/context_manifest.py
?? tests/fixtures/context_declarations.json
?? tests/test_context_determinism.py
?? tests/test_context_manifest.py

$ git diff --stat
 skills/commander/templates/COMMANDER_SPINE.template.json | 8 ++++++++
 1 file changed, 8 insertions(+)
```

Deliverable path check re-verified after the change (`git check-ignore -q`; exit 1 = committable,
exit 0 = intentionally ignored):

```
1 scripts/context_manifest.py
1 tests/test_context_manifest.py
1 tests/test_context_determinism.py
1 tests/fixtures/context_declarations.json
1 skills/commander/templates/COMMANDER_SPINE.template.json
0 .agent-work/300/context/context.json
```

## Behavior changed
`yes` — new capability, no existing behavior altered. A spine task may now carry an optional
ordered `context_refs` list; the producer turns the active step's declaration into a manifest of
`{root, path, rev}` rows plus one `run` subtree, and writes it under
`.agent-work/<work-id>/context/<step>.json`. A spine without `context_refs` projects an empty
manifest and cannot crash — verified against all 13 real committed gated spine/plan templates in
the corpus, not against a fixture.

## Map Impact

- **Structural anchors touched:** `scripts/checklist_engine.py` — `active_id()` is **imported, not
  duplicated**; the module is otherwise unmodified. New sibling module
  `scripts/context_manifest.py` (`decision:producer-is-a-sibling-module` — see below).
  `skills/commander/templates/COMMANDER_SPINE.template.json` gains a task-level declaration key.
- **Capabilities added/changed/affected:** `capability:spine-keyed-context-delivery` — the
  declaration, the assembly and the record now exist alongside the pre-existing deterministic
  *selection*. New observable: a per-step delivery record with revision identity.
- **Constraints/assumptions touched:** `constraint:delivery-not-use` honored (a test asserts file
  bytes never appear in the record). `constraint:extend-dont-parallel` honored (a test asserts the
  selector function object is compiled from `checklist_engine.py` and that the producer defines no
  `active_id`). `constraint:markdown-in-git` honored via `.gitattributes`; the LF-normalisation
  invariant is now **newly relied on** by `rev()` and is pinned by the gate check.
  `constraint:windows-corpus` stressed and closed: `newline="\n"` on every text write.
  `constraint:no-foreclosure` honored — the row stays `{root, path, rev}`, i.e. a subject plus a
  source identity, expressible later as an assertion with no field to re-litigate.
- **Decision candidates / resolved decisions:**
  - `decision:rev-is-lf-normalised-blob-oid` — **confirmed by re-measurement**, see Evidence §1.
    Remains `settled/measured`.
  - `decision:declaration-field-is-context_refs` — implemented as specified.
  - `decision:no-globs-order-is-content` — implemented, and now mechanically enforced by an
    AST-level guard rather than by convention.
  - `decision:producer-is-a-sibling-module` — was graded `guess` with the settle condition "if the
    import seam creates a second effective selector, inline it into `checklist_engine.py` instead."
    **Settled in favour of the sibling module:** `from checklist_engine import active_id` produces
    no second selector, and a test pins that (`__code__.co_filename` is the engine's own file).
    Regrade to `settled/measured`.
  - **New, decided within latitude:** a declaration path containing a glob metacharacter
    (`* ? [ ]`) now **raises** rather than being recorded as one absent file. Silently emitting
    `rev: null` for `docs/*.md` would be plausible wrong output.
  - **New, decided within latitude:** `required` is honoured as *declaration metadata only* — the
    producer does not raise when a `required: true` entry is absent, because the handoff's
    "absent → `rev: null`, entry retained, no exception" rule is unconditional. Enforcement, if
    anyone wants it, belongs to the consumer.
- **Claims/evidence produced:** `claim:revision-identity-present` (Evidence §1–2),
  `claim:manifest-on-every-assembly` (Evidence §3), `claim:deterministic-across-environments`
  (Evidence §4).
- **Trust limitations / drift found:** the handoff's map-confidence flag is **confirmed live**.
  `agent_work_root.durable_root()` returned the *worktree* (`…/298-300`), not the main checkout,
  because an Admiral lease is active — so the `durable`-rooted row `.agent-work/LESSONS.md`
  resolves to `rev: null` here while it would resolve to a real OID from the main checkout. The
  producer does not assume a durable root; the caller injects it. This is the durability risk
  already flagged toward #301.
- **Triage candidates:** see "Out-of-scope observations".

## Test mode
**Required:** `test-first for rev(); test-after acceptable for the rest`
**Satisfied:** `yes` — the `rev` equality and CRLF/LF twin tests were written first and observed
failing, twice, before any correct implementation existed (transcript below). Everything else is
test-after.

## Evidence

### 1. `rev` == `git hash-object` on real tracked files (load-bearing)

```bash
$ git hash-object -- scripts/checklist_engine.py
36b3f7c0d2d6e5f5b20c695553fa713419224d88
$ git rev-parse HEAD:scripts/checklist_engine.py
36b3f7c0d2d6e5f5b20c695553fa713419224d88
$ python -c "...rev(open(...,'rb').read())..."
36b3f7c0d2d6e5f5b20c695553fa713419224d88 scripts/checklist_engine.py
d3ca09b0683007e99299feca9bea2ec6c636578b skills/commander/templates/COMMANDER_SPINE.template.json
dfe0770424b2a19faf507a501ebfc23be8f54e7b .gitattributes
```

All three agree with `git hash-object` for the engine, and `git rev-parse HEAD:<path>` agrees too.
`d3ca09b0…` is the template's **pre-edit** OID, matching the `index d3ca09b..7b5eba7` line in the
diff above — an independent cross-check that `rev` reproduces git's own object identity.

**Result:** `pass`

### 2. CRLF/LF twins produce the same `rev` (load-bearing)

```bash
$ od -c lf.md; od -c crlf.md
0000000   a   l   p   h   a  \n   b   e   t   a  \n
0000013
0000000   a   l   p   h   a  \r  \n   b   e   t   a  \r  \n
0000015
$ python -c 'print rev of each'
fbbee861521bd5355538b096fa3998541cd33909 lf.md
fbbee861521bd5355538b096fa3998541cd33909 crlf.md
$ git hash-object -- lf.md crlf.md
fbbee861521bd5355538b096fa3998541cd33909
fbbee861521bd5355538b096fa3998541cd33909
```

Genuinely different bytes on disk (11 vs 13), one identity, and it is git's identity.

**Result:** `pass`

### 3. A manifest produced by driving the **real** producer through `active_id()` (load-bearing)

Real Commander spine template, real installed skill dir, real `durable_root()`; step chosen by the
engine's selector, not pinned:

```bash
$ python -c "... spine['tasks']['init']['status']='complete';
             print('active_id(spine) ->', cm.active_id(spine));
             cm.produce(spine, roots, ROOT/'.agent-work') ..."
active_id(spine) -> context
durable_root      -> C:\Programs\constellation-skills-wt\298-300
written           -> C:\Programs\constellation-skills-wt\298-300\.agent-work\300\context\context.json

{
  "contract": 1,
  "step": "context",
  "files": [
    {
      "root": "skill",
      "path": "references/global-orchestrator.md",
      "rev": "6241c56ccda9cda53422ab3cecc1edbf168caa9c"
    },
    {
      "root": "skill",
      "path": "references/global-everyone.md",
      "rev": "b10abd32711f4579509c80e7376e9ea79806866c"
    },
    {
      "root": "repo",
      "path": "docs/agents/ORCHESTRATOR_CONTEXT.md",
      "rev": null
    },
    {
      "root": "repo",
      "path": "docs/agents/GLOSSARY.md",
      "rev": null
    },
    {
      "root": "repo",
      "path": "docs/agents/engine-config.json",
      "rev": null
    },
    {
      "root": "durable",
      "path": ".agent-work/LESSONS.md",
      "rev": null
    }
  ],
  "run": {
    "work_id": "300",
    "session_id": null,
    "generated_at": "2026-08-01T14:49:13Z",
    "roots": {
      "skill": "C:/Users/fredc/.claude/skills/constellation-commander",
      "repo": "C:/Programs/constellation-skills-wt/298-300",
      "durable": "C:/Programs/constellation-skills-wt/298-300"
    },
    "host": {
      "platform": "win32",
      "python": "3.14.3",
      "cwd": "C:/Programs/constellation-skills-wt/298-300"
    }
  }
}
```

The four `null` rows are all honest absences in *this* worktree: `docs/agents/` does not exist here
(`ls: cannot access 'docs/agents/': No such file or directory`) and `.agent-work/LESSONS.md` lives in
the main checkout, which `durable_root()` declines to return while the Admiral lease is active.

**Result:** `pass`

### 4. Cross-environment determinism (load-bearing)

Two clean `git worktree` checkouts of the same commit, at two distinct absolute paths, each running
the producer in its own child process under a different locale and hash seed:

```
--- environment 0 ---
  checkout      : C:\Users\fredc\AppData\Local\Temp\ctx-determinism-v0c9h1p7\checkout-0
  LC_ALL / LANG : C / C
  PYTHONHASHSEED: 1  (hash('constellation') = 1246491284158289739)
  step (active_id): context
  whole-file sha256 : 62e1c3f8eb90aabf676ee89f22d6c0947b46cf94083d031714d022fc2a8f2551
  CONTENT   sha256  : ece8363ca225731a0efd6d62fd102c6a0bfe79b2bd4eb9ba30522f85f1c1b6e5
--- environment 1 ---
  checkout      : C:\Users\fredc\AppData\Local\Temp\ctx-determinism-v0c9h1p7\checkout-1
  LC_ALL / LANG : tr_TR.UTF-8 / tr_TR.UTF-8
  PYTHONHASHSEED: 4242  (hash('constellation') = -1723099651878230516)
  step (active_id): context
  whole-file sha256 : 4df101e43d05e2406ec2da8338877a86fac7ba4cc247829bb2e2401eb896049a
  CONTENT   sha256  : ece8363ca225731a0efd6d62fd102c6a0bfe79b2bd4eb9ba30522f85f1c1b6e5
--- comparison ---
  distinct checkout paths : True
  whole file byte-identical : False   (expected False: /run varies)
  CONTENT byte-identical    : True   (exclusion set = exactly /run)
  keys excluded             : ['run']
--- content (identical in both environments) ---
{
  "contract": 1,
  "step": "context",
  "files": [
    {
      "root": "skill",
      "path": "references/global-orchestrator.md",
      "rev": "6241c56ccda9cda53422ab3cecc1edbf168caa9c"
    },
    {
      "root": "skill",
      "path": "references/global-everyone.md",
      "rev": "b10abd32711f4579509c80e7376e9ea79806866c"
    },
    {
      "root": "repo",
      "path": "docs/agents/ORCHESTRATOR_CONTEXT.md",
      "rev": null
    },
    {
      "root": "repo",
      "path": "docs/agents/GLOSSARY.md",
      "rev": null
    },
    {
      "root": "repo",
      "path": "docs/agents/engine-config.json",
      "rev": null
    },
    {
      "root": "durable",
      "path": ".agent-work/LESSONS.md",
      "rev": null
    }
  ]
}
--- run subtree, environment 0 (the entire exclusion set) ---
{
  "work_id": "<work-id>",
  "session_id": null,
  "generated_at": "2026-08-01T14:48:58Z",
  "roots": {
    "skill": "C:/Users/fredc/AppData/Local/Temp/ctx-determinism-v0c9h1p7/checkout-0/skills/commander",
    "repo": "C:/Users/fredc/AppData/Local/Temp/ctx-determinism-v0c9h1p7/checkout-0",
    "durable": "C:/Users/fredc/AppData/Local/Temp/ctx-determinism-v0c9h1p7/checkout-0"
  },
  "host": {
    "platform": "win32",
    "python": "3.14.3",
    "cwd": "C:/Programs/constellation-skills-wt/298-300"
  }
}
```

Notes on this run, all of them load-bearing:

- **Nothing beyond `/run` was excluded.** `keys excluded: ['run']` is asserted, not narrated.
- **The mutation is measured, not assumed** (the named Windows trap): each child reports the
  `LC_ALL`/`LANG`/`PYTHONHASHSEED` it actually saw, and the two `hash('constellation')` probes
  differ — which proves the seed was *honoured*, not merely *set*.
- **The first version of this test passed vacuously** and I fixed it rather than banking it: in a
  bare source checkout every declared row resolved to `rev: null`, so byte-identity was trivially
  true. The test now applies the same install shim the real installer performs
  (`skills/_shared/global-*.md` → `skills/<role>/references/`) to **both** checkouts, and a
  dedicated test now fails if the projection is empty.
- **Two fresh checkouts rather than this checkout vs one fresh checkout.** Deliberate, and stated
  in the test module docstring: the Commander declaration names `docs/agents/…` paths that are
  untracked-or-absent here, so comparing this working tree against a clean one would compare two
  genuinely different sets of *delivered bytes* — an honest delivery difference, not a determinism
  failure. `RealCheckoutSkew` covers that case explicitly instead of masking it, asserting the
  record's **shape** (step, rows, order) is invariant and that any `rev` difference is backed by an
  actual presence difference.
- **Honest limit, stated in the test:** same OS, same filesystem, same Python. This exercises path
  ordering, locale and hash ordering — not a cross-OS rebuild.
- **No stray worktrees:** `git worktree list` showed 5 entries before and 5 after every run;
  cleanup is in a `finally`/`tearDownClass` on every exit path.

**Result:** `pass`

### 5. The handoff's verification commands, in order

```bash
$ cd C:/Programs/constellation-skills-wt/298-300

$ python -m pytest tests/test_context_manifest.py -q
45 passed, 46 subtests passed in 0.57s
EXIT=0

$ python -m pytest tests/test_context_determinism.py -q
7 passed, 10 subtests passed in 1.74s
EXIT=0

$ python -m pytest tests/test_context_manifest.py -q -k 'no_globs or newline_pinned or py312_compatible' --no-header
3 passed, 42 deselected, 3 subtests passed in 0.19s
EXIT=0

$ grep -q 'context_refs' skills/commander/templates/COMMANDER_SPINE.template.json
EXIT=0

$ python -m pytest tests/test_checklist_engine.py -q
324 passed, 24 subtests passed in 5.09s
EXIT=0

$ python -m pytest tests/ -q
1209 passed, 2 skipped, 316 subtests passed in 39.04s
EXIT=0

$ test -f .gitattributes && ! grep -nE '(^|[[:space:]])(-text|binary)([[:space:]]|$)' .gitattributes
EXIT=0
```

The `-k` selector matches 3 tests, so it cannot exit 5. The two skips in the full suite are
pre-existing and unrelated to this change.

**Result:** `pass` — all seven exit 0.

### 6. Confirmatory spot-checks

- **Empty declaration, no crash:** asserted against all 13 real committed gated spine/plan
  templates in `skills/*/templates/*.json` (admiral, cartographer, charter, commander,
  execute-plan, explorer, implementer, scout, workbench, …) — each projects, and each whose active
  step carries no `context_refs` yields `files: []`. A second test additionally projects every live
  `.agent-work/*/spine.json` in this checkout when present.
- **Spine template edit:** +8 lines on the `context` step only; a test asserts `context` is the
  *only* task in the template carrying a declaration, and that the imperative prose still contains
  "record the substitution", "sanctioned degradation" and "do NOT create the overlay file".
- **No globs:** AST-level — none of `glob/iglob/rglob/listdir/scandir/walk/iterdir/fnmatch/sorted`
  appears as *code* in the producer (parsed, not grepped, so the module's own prose "no globs" and
  "not sorted()" cannot false-positive). Plus a behavioural half: with `os.listdir`, `os.scandir`
  and `os.walk` monkeypatched to raise, and three decoy files sitting beside the declared one, the
  producer reads exactly `['declared.md']`.
- **Newline pinned:** AST-level — every `open()` in text mode carries `newline="\n"`, and
  `write_text`/`writelines` (which cannot pin it) are rejected outright. Plus a behavioural half:
  the written file contains no `\r\n`.
- **3.12 compatible:** AST-level over the producer and every `tests/test_context_*.py` — no
  `read_text(newline=)`/`write_text(newline=)` and no 3.13+-only call. Discovered by glob so a new
  sibling test file inherits the guard rather than escaping it.
- **No subprocess/network in the producer:** AST-level — `subprocess`, `urllib`, `requests`,
  `socket`, `system`, `popen` appear nowhere as code.

## TDD evidence, if required

Required for `rev`. Red observed **twice**; the second is the discriminating one.

**Red 1 — tests written before the module existed:**

```
$ python -m pytest tests/test_context_manifest.py -q -k 'rev' --no-header
ERROR collecting tests/test_context_manifest.py
E   FileNotFoundError: [Errno 2] No such file or directory:
    'C:\\Programs\\constellation-skills-wt\\298-300\\scripts\\context_manifest.py'
1 error in 0.25s
```

A collection error is a weak red — it proves the module is missing, not that the tests
discriminate. So I sharpened it:

**Red 2 — a `rev` that hashes raw bytes with no LF normalisation:**

```
$ cat > scripts/context_manifest.py   # TEMPORARY TDD-RED STUB — deliberately wrong
  def rev(data: bytes) -> str:
      return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()

$ python -m pytest tests/test_context_manifest.py -q -k 'rev' --no-header
>       self.assertEqual(cm.rev(lf), cm.rev(crlf))
E       AssertionError: '394a612b660730cf8f0011b10fc64a6bf3826c43' != '40224cded63d315881b519dd762ebe1da16828a1'
E       - 394a612b660730cf8f0011b10fc64a6bf3826c43
E       + 40224cded63d315881b519dd762ebe1da16828a1

FAILED  ...::test_rev_crlf_twin_written_to_disk_matches_git_hash_object
SUBFAILED(path='scripts/checklist_engine.py')                       ...::test_rev_equals_git_hash_object...
SUBFAILED(path='scripts/agent_work_root.py')                        ...::test_rev_equals_git_hash_object...
SUBFAILED(path='skills/commander/templates/COMMANDER_SPINE.template.json') ...::test_rev_equals_git_hash_object...
SUBFAILED(path='.gitattributes')                                    ...::test_rev_equals_git_hash_object...
FAILED  ...::test_rev_of_crlf_and_lf_twins_is_identical
6 failed, 3 passed in 0.29s
```

This is the strong red: every working-tree file is CRLF on this host, so an un-normalised hash
disagrees with `git hash-object` on **real repository files** — exactly the silent-divergence
failure this design fears.

**Green — after adding `data.replace(b"\r\n", b"\n")` and nothing else:**

```
$ python -m pytest tests/test_context_manifest.py -q -k 'rev' --no-header
.....
5 passed, 4 subtests passed in 0.25s
```

- Failing test observed: `yes` (twice, above)
- Passing test observed: `yes`
- Refactor while green: `yes` — after the guard tests landed, `sorted(...)` was removed from two
  error messages in `resolve()` (replaced with order-preserving list comprehensions) so the
  no-globs invariant could be an absolute AST-level ban rather than a hedged one. Suite stayed
  green throughout.

## Docs/contracts touched
- `none` — deliberately. `docs/CHECKLIST_SCHEMA.md` and `docs/CHECKLIST_ENGINE_DESIGN.md` are
  gate g3's, per the handoff's Specific Exclusions. The `context_refs` contract is documented in
  `scripts/context_manifest.py`'s module docstring and in the declaration's own shape until g3
  lands the schema text.

## Assumptions
- **`required` is declaration metadata only.** The producer does not raise when a
  `required: true` entry is absent, because "absent → `rev: null`, entry retained, no exception" is
  stated unconditionally. Enforcement belongs to a consumer, not to the record.
- **`durable` is injected, never derived inside the producer.** The producer takes a root mapping
  and does not call `agent_work_root.durable_root()` itself — that call is environment-varying and
  lease-sensitive, and burying it would put an environment fact behind a pure function.
- **A CRLF fixture cannot be committed to this repo**, so the CRLF/LF twins are materialised
  byte-for-byte at test time. Under `* text=auto` + `core.autocrlf=true` a committed CRLF file is
  normalised on the way in and both twins would check out identical, passing the test vacuously.
  Forcing it would need a `-text` exemption — precisely the attribute that breaks `rev`'s equality
  with `git hash-object`. Recorded in the fixture file's own `_readme` so a later reader does not
  "fix" it.
- **The determinism test overlays the working-tree copies** of the producer, the engine and the
  spine template onto each fresh checkout. Without this it would silently measure `HEAD` — i.e.
  code that predates this change — and pass while proving nothing. Stated in the test's docstring.
- **Python 3.12 was not available on this host** (only 3.14.3), so 3.12 compatibility is asserted
  mechanically by the AST guard rather than by executing under 3.12. CI's pinned 3.12 is the real
  proof.

## Stop conditions hit
- `none`. Allowed scope was not exceeded (and in fact was under-used: `scripts/checklist_engine.py`
  needed no edit at all). No specific exclusion was touched. The determinism comparison excludes
  exactly `/run` and nothing else. `active_id()` was reused with no second selector. `rev` equalled
  `git hash-object` for every real case tried — tracked-clean, tracked-dirty, untracked,
  out-of-repo, empty, and CRLF/LF twins.

## Out-of-scope observations
1. **`scripts/context_manifest.py` is not in any role's install bundle.** `install_constellation.py`
   carries a per-role script list (`checklist_engine.py`, `init_work_area.py`, …). The producer is
   not on any of them, so it ships to the source repo but not to an installed skill tree. That is
   *correct for #300* — there is no CLI verb and no agent-facing caller yet — but whoever writes the
   first real caller (#301?) must add it, or the caller will not exist at the seat it runs from.
   Triage candidate.
2. **The `durable` root token is currently a null-producer under an Admiral lease.** Confirmed live:
   `durable_root()` returned the worktree, so `.agent-work/LESSONS.md` records `rev: null` even
   though LESSONS.md exists in the main checkout. The record is *honest* (that file genuinely was
   not delivered from there), but a consumer expecting a lessons OID will always see `null` during
   an epic. Worth naming in #301's design rather than discovering later.
3. **`contract` vs `_STATE_CONTRACT_VERSION` skew** (the DIT comparison's R4). Both read `1` today
   and are independent. I named the producer's constant `_MANIFEST_CONTRACT_VERSION` and said so in
   a comment, but nothing mechanically prevents a downstream store from conflating them.
4. **A glob metacharacter in a declaration path now raises.** This is stricter than the handoff
   specified (it only forbade the producer from *expanding* globs). I judged silent `rev: null` for
   `docs/*.md` to be plausible wrong output. If the reviewer disagrees, the check is three lines in
   `resolve()`.
5. **The `-k 'no_globs or newline_pinned or py312_compatible'` gate is coupled to test names.**
   It passes today (3 matched, exit 0), but any rename silently turns a real check into an exit-5
   failure. A `--strict-markers`-style guard or an explicit node-id list would be sturdier.

## Workflow Feedback

- **Handoff gaps:** two, both real.
  1. **"The determinism test — this is the issue's single acceptance test", step 1**, says
     *"`git worktree add` a **clean second checkout** at the same commit"*. That is under-specified
     in a way that silently produces a false-green: a clean checkout at `HEAD` does **not contain
     the change under test**, because the change is uncommitted at implementation time. If I had
     followed it literally, the test would have compared two copies of HEAD's code and passed while
     proving nothing about my producer. It also implies comparing *this* checkout against the fresh
     one, which false-FAILs on the untracked `docs/agents/` paths the Commander declaration names —
     the very hazard the handoff's own adversarial-fixture list calls out. I used two fresh
     checkouts plus a working-tree overlay and documented why. **Name the overlay requirement in
     the handoff.**
  2. **The install shim is invisible from the handoff.** The declaration is written against the
     *installed* skill layout (`references/global-orchestrator.md`), but that file is assembled at
     install time from `skills/_shared/`; it does not exist in the source tree. So the first green
     determinism run was **vacuous** — every row was `rev: null` and byte-identity was trivially
     true. Nothing in the handoff's Close Criteria would have caught it. **"A manifest is produced
     by driving the real producer" needs a companion criterion: "and the projection is non-empty."**
- **Context rediscovered:** the source-vs-installed skill layout (`skills/_shared/global-*.md` →
  `skills/<role>/references/` at install) — a map anchor for it would have saved a wrong turn. Also
  the repo's cross-import convention in `scripts/` (`sys.path.insert(0, Path(__file__).parent)`,
  used by five existing scripts) and the test-import convention (`importlib.spec_from_file_location`
  rather than a package import); both had to be read out of neighbouring files.
- **Instructions improvised around:** the implementer plan template's TDD guidance says to encode
  the red step as a `check: null` postcondition and attest it. That worked, but it makes a *weak*
  red (module-missing collection error) indistinguishable from a *strong* one (a deliberately wrong
  implementation that the tests catch). I did both and attested the strong one; the template could
  say that a collection error is not sufficient red for an identity function.
- **What would have made this easier:** one line in the handoff's determinism section —
  *"the second checkout is at HEAD and therefore lacks your uncommitted change; overlay the
  working-tree copies of the files under test onto it, and assert the projection is non-empty."*
  That single sentence covers both of the false-green traps above, which between them cost the two
  rework loops in this run.

## Return status
`complete`

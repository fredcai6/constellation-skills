# Cold critic — TESTABILITY lens (issue #300, projection substrate + manifest)

**Question I was asked to answer:** can each pathway be exercised *and falsified* on its own?

**Method.** Baseline run, then 45 deliberate mutations of the production code applied in a
throwaway `git worktree` sandbox (`ct-mut-sandbox`, since removed — `git worktree list` verified
clean), each followed by a full run of the three new test files. Plus direct probes of `rev()`
against `git hash-object`, of the child-process environment the acceptance test actually creates,
and of the lint's boundary rule. Every finding below is a mutation that **survived** or a probe
that contradicts a stated claim. No repository file under review was modified.

**Baseline:** `python -m pytest tests/ -q` → `1226 passed, 2 skipped, 329 subtests passed`
(both skips are on `scripts/verify_skip_guard.py`'s allow-list). The three new files:
`69 passed, 69 subtests passed`.

**Kill rate: 34 of 45 mutations killed.** That is a genuinely strong suite for a first cut, and
several properties are pinned by two or three independent tests. The findings below are the
holes, and the two BLOCKING ones both sit in the *acceptance* test — the one artifact the issue
was pre-ruled on.

---

## BLOCKING

### B1 — `/run` is not actually the exclusion set: a varying field placed outside `/run` passes the whole suite

The producer's module docstring states the load-bearing design claim:

> **`/run` is the entire exclusion set.** … a new varying field cannot become "accidentally
> content", because it has to be placed in one subtree or the other.

It can, and nothing catches it. Mutation **M36** puts an absolute, environment-varying value
(`run.host.cwd`) *into the compared content*:

```python
# scripts/context_manifest.py :: content()
def content(manifest):
    out = {k: v for k, v in manifest.items() if k != "run"}
    out["host_cwd"] = manifest.get("run", {}).get("host", {}).get("cwd")
    return out
```

```
M36 content leaks run.host.cwd OUTSIDE /run                *** SURVIVED ***
        69 passed, 68 subtests passed
```

Two independent reasons it survives, and both need fixing:

1. `tests/test_context_manifest.py:308` —
   `self.assertEqual(set(m) - set(cm.content(m)), {"run"})`
   is a **one-directional** set difference. It is structurally blind to any key `content()`
   *adds*. The same blindness is repeated in the acceptance test at
   `tests/test_context_determinism.py:217-218`. The assertion that would catch this is
   `assertEqual(set(cm.content(m)), set(m) - {"run"})`.
2. The two acceptance-test children **share a working directory**. `setUp`
   (`tests/test_context_determinism.py:178-181`) calls `subprocess.run(...)` with no `cwd=`, so
   both children inherit the pytest process's cwd. Probe:

```
$ (both env mutations, same probe script)
{"cwd": "C:\\Users\\fredc\\...\\scratchpad", "LC_ALL": "C", ...}
{"cwd": "C:\\Users\\fredc\\...\\scratchpad", "LC_ALL": "tr_TR.UTF-8", ...}
```

cwd is the one environment fact `run_facts()` already reads (`"cwd": Path.cwd().as_posix()`),
and it is the one the acceptance test holds constant. A near-miss confirms how thin the margin
is: the same leak injected in `build_manifest` instead of `content()` (**M20**) was killed by
exactly **one** test — `ManifestEnvelope::test_envelope_has_exactly_four_keys`, a key-list
assertion in a different file that has nothing to do with determinism. The determinism suite
passed M20 green, *including* `test_no_absolute_path_leaks_into_the_content`, which greps only
for the checkout path and not for cwd.

**What I would do.** (a) make both `set`-difference assertions bidirectional; (b) give the two
children different `cwd=` values; (c) rename/extend
`test_no_absolute_path_leaks_into_the_content` to assert no *drive-rooted absolute path of any
shape* appears in content, not just the checkout string.

### B2 — the acceptance test never compares the bytes the two environments produced

The module docstring says "each running the real producer in a child process … everything else
must be byte-identical," and the issue's acceptance criterion is a cross-environment byte
comparison. What the test actually does (`tests/test_context_determinism.py:208-215`) is parse
both children's files and **re-encode them in the parent process**:

```python
self.assertEqual(
    cm.encode(cm.content(first)).encode("utf-8"),
    cm.encode(cm.content(second)).encode("utf-8"),
)
```

`first`/`second` are `json.loads(...)` of the child artifacts, and `cm` is the *parent's* module.
Any environment dependence in serialisation is therefore normalised away before comparison. The
only assertion on the child bytes is `assertNotEqual(bytes0, bytes1)` — that they *differ*.

Mutation **M49** makes the encoder environment-dependent while still emitting valid JSON, with a
condition that is false in the parent so the parent's own encoder tests are untouched:

```python
# scripts/context_manifest.py :: encode()
_indent = 4 if os.environ.get("LC_ALL") == "tr_TR.UTF-8" else 2
return json.dumps(obj, indent=_indent, ensure_ascii=False) + "\n"
```

```
M49 encode() is environment-dependent (valid JSON, different bytes per env) -> *** SURVIVED ***
        55 passed, 68 subtests passed
```

The two environments wrote materially different bytes for identical content and the acceptance
test reported green. (Cruder versions — BOM per environment, trailing garbage — *are* killed,
but only because the artifact stops parsing in `setUp` and every test in the class errors out;
that is a parse failure, not a determinism comparison.)

**What I would do.** Have each child write a second artifact containing `encode(content(m))` —
i.e. strip `/run` **in the child, with the child's own encoder** — and byte-compare *those two
files*. That is the comparison the docstring describes and it costs three lines in `CHILD`.

---

## SERIOUS

### S3 — `RealCheckoutSkew` is vacuous in every environment, including the one it was written in

The class exists to cover untracked-vs-absent skew "explicitly instead of hiding it." In this
worktree, and in any clean checkout, **all six declared rows resolve to `rev: None` on both
sides**:

```
$ python -c "... build_manifest(COMMANDER_SPINE, roots={'skill': ROOT/'skills/commander', 'repo': ROOT, 'durable': ROOT})"
{'root': 'skill',   'path': 'references/global-orchestrator.md',      'rev': None}
{'root': 'skill',   'path': 'references/global-everyone.md',          'rev': None}
{'root': 'repo',    'path': 'docs/agents/ORCHESTRATOR_CONTEXT.md',    'rev': None}
{'root': 'repo',    'path': 'docs/agents/GLOSSARY.md',                'rev': None}
{'root': 'repo',    'path': 'docs/agents/engine-config.json',         'rev': None}
{'root': 'durable', 'path': '.agent-work/LESSONS.md',                 'rev': None}
```

(`skills/commander/references/` holds only `commander-core.md` and `crew-dispatch.md` — the
`global-*.md` files are install-time artifacts and are not in the source tree; `docs/agents/`
does not exist in this repo; `.agent-work/LESSONS.md` does not exist.)

So at `tests/test_context_determinism.py:300`, `if mine["rev"] == theirs["rev"]: continue` fires
for **every** row and the `assertNotEqual` that is the point of the test never executes. The
premise — that some skew exists — is never established and never asserted. This is the exact
"assertion whose premise is never established" pattern.

**What I would do.** Materialise the skew instead of hoping for it: write an untracked file at
one declared path in `ROOT` before projecting (cleaning up after), and `assertTrue` that at
least one row actually differed, so the test fails if the skew evaporates.

### S4 — the locale half of the "cross-environment" mutation is inert on the only platform CI runs

`.github/workflows/ci.yml` is `runs-on: windows-latest`, single job. On Windows, setting
`LC_ALL`/`LANG` changes nothing observable in CPython:

```
LC_ALL=C            → preferred_encoding cp1252, getlocale ['English_United States','1252'],
                      LC_COLLATE 'C', sorted(['a','B','ä','Z']) = ['B','Z','a','ä'], 'i'.upper()='I'
LC_ALL=tr_TR.UTF-8  → preferred_encoding cp1252, getlocale ['English_United States','1252'],
                      LC_COLLATE 'C', sorted(['a','B','ä','Z']) = ['B','Z','a','ä'], 'i'.upper()='I'
```

`test_the_locale_and_hash_seed_mutations_took_effect_inside_the_child` is named for an effect it
does not measure: for `LC_ALL`/`LANG` it asserts only `os.environ.get(...) == expected`, i.e.
that the variable was *set*. Only `PYTHONHASHSEED` gets a real behavioural probe (`hash_probe`),
and that one is honest. Net: the acceptance test's real mutation set is **{checkout path, hash
seed}**, not the three the docstring names.

**What I would do.** Either drop the locale claim from the docstring and the test name, or make
the child call `locale.setlocale(locale.LC_ALL, "")` and report a locale-sensitive probe
(`locale.strxfrm`, `locale.getlocale()`) that is asserted to *differ* between the two children —
the way `hash_probe` already is.

### S5 — the `root` token is completely unguarded, in the producer tests and in the lint

Mutation **M39** retargets a shipped declaration entry to the wrong tree:

```json
-  {"root": "repo",  "path": "docs/agents/GLOSSARY.md", "required": false}
+  {"root": "skill", "path": "docs/agents/GLOSSARY.md", "required": false}
```

```
M39 shipped declaration retargeted to the WRONG root token *** SURVIVED ***
```

`verify_context_declaration.py` compares only the `path` string against the prose; the root
token is never looked at. The manifest tests assert only `entry["root"] in cm.ROOT_TOKENS`. Yet
the lint's own docstring names this defect class explicitly: "a declaration that has been
**retargeted**, mistyped, or extended past the prose that justifies it." Retargeting the root is
retargeting — and it is the half that decides which tree is actually read. The consequence in
production is silent: the row resolves to `rev: null` forever, indistinguishable from a
legitimately-absent overlay.

**What I would do.** Extend the lint to require the *root-qualified* shape: for `root: "skill"`
require the prose to say "this skill's `<path>`" (or another declared marker); at minimum, assert
in `CommanderSpineDeclaration` that each entry's `(root, path)` pair matches an expected literal
list, so a retarget is a diff.

### S6 — the shipped declaration's contents are unpinned; an entry can be silently dropped

Mutation **M40** deletes `docs/agents/GLOSSARY.md` from `COMMANDER_SPINE.template.json`'s
`context_refs`:

```
M40 shipped declaration loses an entry (narrowing)         *** SURVIVED ***
```

`CommanderSpineDeclaration` asserts `len(declaration) > 0` and per-entry shape;
`test_declaration_projects_one_row_per_entry_in_declared_order` compares the manifest against
*the same declaration it read*, a self-referential oracle; the acceptance test asserts
`len(files) >= 1`. The lint is one-directional by design and documents this exact blind spot
("a path quietly dropped from `context_refs` while the prose still names it"). So the corpus's
first and only real declaration can silently shrink and nothing anywhere notices.

Given the lint provably cannot cover this direction, the *test suite* is the only place it can be
covered. **What I would do:** pin the expected `(root, path, required)` list as a literal in
`CommanderSpineDeclaration`. It is six rows; a deliberate change becomes a two-line diff, an
accidental one becomes a failure.

### S7 — `declaration_of`'s type guard is untested; an invalid declaration silently becomes an empty manifest

Mutation **M19** turns the raise into a silent empty result:

```python
if not isinstance(declared, Sequence) or isinstance(declared, (str, bytes)):
    return ()          # was: raise DeclarationError(...)
```

```
M19 declaration_of: swallow malformed -> ()                *** SURVIVED ***
```

`test_malformed_entries_fail_visibly` only passes *lists of bad entries*; it never passes a
`context_refs` that is a string, a dict, or a number. So `context_refs: "docs/agents/GLOSSARY.md"`
— an entirely plausible authoring mistake — would project **nothing**, with no error, and the
manifest would look perfectly valid. That is a silent PASS on invalid input, the defect class
the panel brief singles out.

**What I would do.** Add `"docs/x.md"`, `{"root": "repo", "path": "x.md"}` (a bare dict) and `7`
to `FIXTURES["rejected"]` as *declaration-level* (not entry-level) cases, driven through
`declaration_of`.

### S8 — the `.gitattributes` guard the producer docstring relies on does not exist

`scripts/context_manifest.py:86` states:

> The gate's `.gitattributes` grep pins condition 1 **only**; it structurally cannot see
> condition 2 …

There is no `.gitattributes` grep. `grep -rn "gitattributes\|text=auto\|-text" tests/ scripts/`
finds only prose and one entry in `RevIsGitBlobOid.TARGETS` (which hashes the file, it does not
inspect it). Condition 1 is therefore unpinned, and the incidental coverage it does have is an
accident of fixture naming:

```
.gitattributes += '*.md -text'                     -> KILLED    (only because the control
                                                                 fixture is named control.md)
.gitattributes += 'skills/**/references/*.md -text' -> *** SURVIVED ***
.gitattributes += 'docs/agents/*.md -text'          -> *** SURVIVED ***
.gitattributes += '.agent-work/*.md -text'          -> *** SURVIVED ***
```

Those three patterns cover **exactly the paths the shipped `context_refs` declares**. Under any
of them `rev()` stops equalling git for the doctrine Markdown this substrate exists to identify:

```
rev()           = fbbee861521bd5355538b096fa3998541cd33909
git hash-object = 17f2fc0a7500e6b218190262d5a329086ba965ff
EQUAL? False
```

Related: `RevIsGitBlobOid.TARGETS` is `checklist_engine.py`, `agent_work_root.py`, a `.json`
template and `.gitattributes` — **not one `.md` file**, the extension of the entire declared
corpus.

**What I would do.** Write the grep the docstring claims exists: assert `.gitattributes` contains
no `-text`/`binary` attribute matching any path any `context_refs` in the corpus declares. And add
a `.md` file to `TARGETS`.

---

## MINOR

**M1 — neither root-escape guard is independently exercised.** Removing the `..`/absolute check
(M07) survives; removing the post-join `startswith(base)` check (M12) survives; removing **both**
(M38) is killed. So each is load-bearing only in the other's absence, and a refactor deleting
either as "redundant" stays green while narrowing the actual guarantee. Add a test that pins each
guard's *diagnostic message*, or drive the guards separately.

**M2 — `_MANIFEST_CONTRACT_VERSION` is a self-referential oracle.** `test_envelope_has_exactly_four_keys`
asserts `m["contract"] == cm._MANIFEST_CONTRACT_VERSION` — producer compared to producer. Bumping
the constant 1 → 99 (**M33**) survives. #301 will key on this value; pin the literal.

**M3 — no golden-bytes pin on a produced manifest.** `sort_keys=True` in `encode()` (**M17**)
survives: `test_encode_is_the_one_canonical_encoder` only checks `endswith("\n")`, an em-dash, and
that `'\n  "step"'` appears somewhere. A single expected-bytes assertion over a fixed manifest
would close M3 and strengthen B2.

**M4 — `run_facts()` has no direct test.** Freezing `generated_at` to `"1970-01-01T00:00:00Z"`
(**M43**) survives, as does replacing the deliberate `ROOT_TOKENS` iteration order with dict order
(**M35**, whose "not sorted(), not dict order" comment is thus unbacked). `session_id` is never
populated by any caller and never asserted; the `run=` override parameter on `build_manifest`
/`produce` is never exercised.

**M5 — a checklist with no `work_id` silently writes to a directory named `None`.**
`produce()` → `manifest_path(root, checklist.get("work_id"), step)` → `str(None)`:
```
written to: .agent-work\None\context\context.json
run.work_id = None
```
Untested. Either fail visibly or assert the fallback.

**M6 — `required: true` on an absent file is never exercised.** Every absent-file test uses
`required: false`. The documented behaviour (advisory; no raise) has no test; a future change that
makes `required` enforced would only be caught incidentally.

**M7 — lint false FAIL on `./`-prefixed prose.** `_appears_at_path_boundary("docs/a.md", "Read
./docs/a.md first.")` → **REJECT**, because `/` is in `_PATH_CHAR`. A perfectly ordinary way to
write a repo-relative path in prose produces a lint failure on a correct declaration. Untested in
either direction. (`docs/a.md.Then` — a missing-space typo — also false-FAILs.)

**M8 — lint false PASS on `docs/a.md.~1`.** `_bounded_after`'s `.`-then-non-alnum rule accepts a
match against a different file. Narrow, but it is the same defect class the trailing rule exists
to catch.

**M9 — non-canonical path spellings are accepted and recorded verbatim.**
`docs/a.md` and `docs/./a.md` produce two rows with different `path` strings and the same `rev` —
two "different" content rows for one delivered file. Since declaration order and path text *are*
content, this is a real content-divergence vector. Untested.

**M10 — `INSTALL_SHIM` hardcodes the installed-skill layout with nothing tying it to the installer.**
`tests/test_context_determinism.py:75-80` asserts `skills/_shared/global-*.md` →
`skills/commander/references/global-*.md`. That matches `install_constellation.py`'s
`SKILL_REFERENCE_BUNDLES["commander"] = _GLOBAL_ORCHESTRATOR` **today**, but nothing checks it. If
the installer's layout moves, the acceptance test keeps producing two real `rev`s from a shim that
no longer describes reality, while real runs project `rev: null` for both required entries.

**M11 — nothing in production calls either script.** `grep -rn "context_manifest\|verify_context_declaration"`
outside `tests/` finds only docs and the lint's own docstring. `scripts/checklist_engine.py` is
unchanged by this diff, so no manifest is produced by the engine; the frame's
`claim:manifest-on-every-assembly` ("checked by a test that drives the real producer *through the
engine*") is checked by tests that call `build_manifest` directly on hand-built dicts, with
`active_id` as the only engine involvement. Separately, the lint runs in CI only *transitively*,
via `test_lint_passes_over_real_shipped_spine_templates`, whose glob is `skills/*/templates/*.json`
— a checklist anywhere else escapes it entirely. This may be a deliberate scope call
(`constraint:delivery-not-use`); flagging it because the frame's evidence surface says otherwise.

**M12 — the tests mutate shared git state.** `DeterministicAcrossEnvironments` and
`RealCheckoutSkew` run `git worktree add/remove/prune` against the real repository, which in this
project carries long-lived Admiral worktrees (`git worktree list` shows four). A `git worktree
prune` issued while another worktree's directory is momentarily unavailable would deregister it.
Low probability, non-local blast radius.

---

## What is genuinely well-tested — no findings here

- **`rev()` at its edges.** I probed every edge in the brief against `git hash-object` as oracle:
  empty (MATCH, and pinned to the literal git empty-blob OID), no trailing newline (MATCH),
  non-ASCII UTF-8 (MATCH), non-ASCII + CRLF (MATCH), UTF-16+BOM (MATCH), lone CR (MATCH),
  CR at EOF (MATCH), `\r\n\r\n` (MATCH), 10 MB of CRLF (MATCH). The documented divergence class
  (NUL byte, lone-CR-mixed-with-CRLF) is asserted *as divergence*, with a raw-blob second oracle
  saying which side moved and a control proving the oracle is not simply broken. Six independent
  mutations of `rev` (no normalisation, over-normalisation, missing blob header, truncation,
  partial `replace(..., 1)`) were all killed, several by 14+ tests.
- **Declaration order is content.** Reversing row order (M04) and deduplicating entries (M41) are
  both killed, by fixture-driven *and* hand-built tests.
- **Path rejection.** Traversal, buried traversal, backslash, absolute POSIX, drive-letter
  (leading and relative), NTFS alternate data stream, glob pattern, unknown/unmapped root, missing
  keys, empty path, smuggled row field — all killed when their guards are removed.
- **No filesystem enumeration.** `test_no_globs_or_filesystem_enumeration_anywhere_in_the_producer`
  is genuinely two-sided: an AST scan (not a grep — it correctly ignores the module's own prose
  about "no globs") *plus* a behavioural half that booby-traps `os.listdir/scandir/walk` and
  asserts exactly one file was read next to three decoys. This is the strongest test in the change.
- **LF-pinned writes.** AST half + behavioural half; `newline=` removal is killed.
- **The lint's boundary rule.** Both directions, both ends. My false-PASS/false-FAIL sweep of 15
  realistic prose shapes (markdown link, bold, possessive, anchor, semicolon, newline, backup
  sibling, numeric sibling, longer prefix) found only the two narrow cases in M7/M8. Bare-substring
  containment (M25), leading-only (M29), trailing-always-true (M28, M45) are all killed.
- **The engine-selector binding.** Both the code-object filename and the import statement are
  asserted, and step-tracks-`active_id` is exercised across a three-item lifecycle including the
  all-terminal raise. Pinning the step to `items[0]` (M15) is killed.
- **Skips.** The three `unittest.SkipTest` sites in the determinism module are *not* on
  `scripts/verify_skip_guard.py`'s allow-list, so an environmental skip turns CI red rather than
  green. `test_a_live_spine_in_this_work_area_also_projects` returns instead of skipping, for that
  exact reason, and documents why. Correct call.
- **The `::` node-id claim checks out.**
  `python -m pytest "tests/test_context_declaration_lint.py::test_divergent_declaration_is_rejected" -q`
  → `1 passed`. No `-k` selector anywhere matches nothing.

---

## Severity roll-up

| Severity | Count | IDs |
|---|---|---|
| BLOCKING | 2 | B1 (`/run` exclusion unenforced), B2 (acceptance test compares re-derived values, not produced bytes) |
| SERIOUS | 6 | S3 `RealCheckoutSkew` vacuous · S4 locale mutation inert on CI's only platform · S5 `root` token unguarded · S6 shipped declaration can silently shrink · S7 `declaration_of` type guard untested · S8 `.gitattributes` guard does not exist |
| MINOR | 12 | M1–M12 above |

**Single most important thing:** the acceptance test does not falsify the property it exists to
falsify. A varying field placed outside `/run` (B1) and an environment-dependent serialiser (B2)
both pass it green — because the two children share a working directory and because the comparison
re-encodes both artifacts in the parent process instead of byte-comparing what the children wrote.

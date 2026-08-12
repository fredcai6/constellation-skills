# Cold critic — SIMPLICITY / YAGNI

**Scope read:** `MISSION_FRAME.md`, `git diff main...HEAD` (10 files, +2177), plus the repo to
check claims. Tests run green locally (`test_context_manifest.py` +
`test_context_declaration_lint.py`: 62 passed, 59 subtests).

**Headline shape.** 543 lines of production code carrying 1351 lines of test and 159 lines of
fixture, for a substrate with **zero production callers**. The producer itself is disciplined —
one selector, one encoder, one exclusion pointer, one impure edge — and I found nothing in its
*core* path to delete. Almost everything below is in the ring around that core: unused seams,
a schema field nobody reads, a second test class that re-tests the first one through a fixture
file, and a 602-line lint guarding one declaration.

Counts: **0 BLOCKING · 7 SERIOUS · 7 MINOR.**

I do not triage. Each item states what is wrong, the evidence, and what I would delete.

---

## SERIOUS

### S1 — `required` is a schema field with no reader anywhere in the change

`required` appears in six template entries
(`skills/commander/templates/COMMANDER_SPINE.template.json:25-32`), in the schema table
(`docs/CHECKLIST_SCHEMA.md:109`), in `resolve()`'s allowed-key list
(`scripts/context_manifest.py:161`), and in two tests. **Nothing reads it.** The schema row says
so out loud: *"`required` is advisory (not enforced by the producer)"*. `rows()` explicitly
strips it (`context_manifest.py:220-223`), and one test exists purely to assert that it is
stripped (`test_required_lives_in_the_declaration_not_the_manifest`).

Its only consumer is named in the frame's own Out of Scope list: *"Degraded-mode reporting on a
missing required entry (issue F)."* That is the textbook definition of a field built for a caller
that does not exist.

**What breaks today if deleted:** nothing. Re-adding a boolean to six JSON objects when issue F
lands is a five-minute edit — which is the argument for deleting it now, not for keeping it.

**Delete:** the `required` key from all six template entries, the `"required"` entry in
`resolve()`'s allow-list, the schema-row clause, and
`test_required_lives_in_the_declaration_not_the_manifest`. Keep the `unknown` key rejection so
the field cannot drift back in unnoticed.

### S2 — five injection seams and one constant with zero callers

Verified by grep across the whole worktree (`scripts/`, `tests/`, `skills/`, `docs/`):

| element | location | callers |
|---|---|---|
| `RUN_POINTER = "/run"` | `context_manifest.py:66` | **zero, anywhere.** `content()` hardcodes `k != "run"` at :296 |
| `run_facts(session_id=)` | `:240` | zero. Every manifest ever produced carries `"session_id": null` |
| `run_facts(now=)` | `:241` | zero |
| `build_manifest(run=)` | `:272` | zero |
| `produce(run=)` | `:329` | zero |
| `build_manifest(step=)` | `:271` | one test (`test_context_manifest.py:464`), which could set `init` complete instead — the determinism child at `test_context_determinism.py:100` already does exactly that |

`session_id` is the worst of these: it is not merely an unused parameter, it emits a permanently
`null` field into every record the substrate produces, and the frame nowhere identifies a session
concept the manifest needs. `now=` is a determinism-freeze hook for a field (`generated_at`) that
lives inside the one excluded subtree and therefore never needs freezing.

`RUN_POINTER` is worse than unused — it is actively misleading. It advertises a JSON-pointer
contract that `content()` does not implement (`content()` does a top-level key filter, not a
pointer walk). Two spellings of one rule.

**Delete:** `RUN_POINTER`, `session_id`, `now`, both `run=` parameters, and `step=` (converting
the one test that uses it to mark `init` complete). That is ~15 lines of signature and ~10 lines
of docstring, and it removes the `dict(run) if run is not None else …` branch at :289.

### S3 — `AdversarialDeclarations` re-tests `ManifestEnvelope` through a fixture file

`tests/test_context_manifest.py` contains two classes that assert the same seven properties, one
inline and one via `tests/fixtures/context_declarations.json`:

| property | inline (`ManifestEnvelope`) | fixture-driven (`AdversarialDeclarations`) |
|---|---|---|
| rejected declarations raise | `:240`, `:247`, `:265`, `:274` | `:521` (same cases, plus more) |
| order permutation is a difference | `:281` | `:527` |
| duplicate paths → two rows | `:292` | `:539` |
| absent → `rev: null`, row kept | `:227` | `:535` |
| stale record does not revalidate | `:328` | `:559` |
| untracked-vs-absent confined to `rev` | `:337` | `:566` |
| CRLF/LF twins agree | `:97`, `:105` | `:544` |

`test_duplicate_declared_paths_are_both_retained` and `test_duplicate_declared_paths_are_two_rows`
are three lines apiece and assert the same thing. The CRLF property is asserted **three** times
(twice in `RevIsGitBlobOid`, once in `AdversarialDeclarations`) plus a fourth time in
`test_context_determinism.py` implicitly.

The fixture-driven versions are the better ones — `FIXTURES["rejected"]` has 15 named cases
against the inline version's 4 groups, and the fixture file documents *why* each case exists.

**Delete:** the six inline duplicates in `ManifestEnvelope` (`:240`, `:247`, `:265`, `:274`,
`:281`, `:292`, `:328`, `:337`) and the redundant CRLF twin at `:105`. Keep `ManifestEnvelope`
for the properties it uniquely owns (envelope shape, row shape, `content()`/`/run` split, reader
injection, no-file-contents). Roughly 90 lines of test, zero coverage lost.

### S4 — `test_producer_and_its_tests_are_py312_compatible` duplicates CI's own job

`tests/test_context_manifest.py:691-714`. An AST walk over the producer and its sibling test files
looking for a hand-maintained list of six 3.13+ names (`PY313_ONLY_KWARGS`, `PY313_ONLY_ATTRS`).

`.github/workflows/ci.yml:34` pins `python-version: "3.12"` and `:42` runs the whole suite on it.
Any 3.13-only API in these files fails CI directly, with a real traceback naming the real call.
The AST guard catches strictly less: only the six names someone happened to remember, and only in
files matching `tests/test_context_*.py`. It will rot (`batched` is 3.12, not 3.13 — the list is
already imprecise) and it applies to no other file in the repo.

The comment defends it with *"this epic has already shipped exactly that once"* — but the thing
that would have caught it is the 3.12 CI run, which already exists.

**Delete:** the test, both class constants, and the `own_files` property that exists only to feed
it (`:590-594`). ~30 lines.

### S5 — `test_a_live_spine_in_this_work_area_also_projects` is a 24-line no-op

`tests/test_context_manifest.py:415-438`. `.agent-work/` is gitignored, so in CI `live` is always
empty and the test returns on line 430 having asserted nothing. Thirteen of its twenty-four lines
are a comment explaining why it returns rather than skips.

That comment contains the argument for its own deletion, verbatim: *"the property this asserts is
covered far more strongly by `test_real_spine_templates_produce_a_manifest_without_crashing` over
all the real committed templates. So: no live spine, nothing extra to check."*

**Delete:** the whole method. The skip-guard reasoning it preserves belongs in
`scripts/verify_skip_guard.py`'s own docs, not in a test that never runs.

### S6 — committed artifacts cite gitignored run artifacts that will not exist

Three dangling references, all pointing into `.agent-work/`, which `.gitignore:1` excludes and
`git worktree remove` destroys:

1. `docs/CHECKLIST_ENGINE_DESIGN.md:217` — *"A design-it-twice comparison
   (`.agent-work/300/DIT-COMPARISON.md`) considered a committed, diffable
   `CONTEXT_PROJECTION.json`"*.
2. `docs/CHECKLIST_ENGINE_DESIGN.md:225` — *"stated explicitly in
   `.agent-work/300/OBLIGATIONS-301.md`"*.
3. `scripts/context_manifest.py:86` — *"The gate's `.gitattributes` grep pins condition 1
   **only**"*. I grepped: that grep exists **only** in `.agent-work/300/build_amend.py:45-46`.
   There is no such gate in the committed tree, in CI, or in any script.

A reader of the merged `main` finds three pointers to nothing. Note the irony: this is a change
whose entire subject is recording *what was available at which revision*, and its own permanent
prose depends on files that are destroyed at worktree teardown.

**Delete:** all three references. Where the fact matters, state it without the citation (e.g.
"a committed, diffable artifact was considered and ruled out of scope"). For (3), either state
the condition-1 limit without claiming a gate enforces it, or land a real check in
`.github/workflows/ci.yml`.

### S7 — the lint's trailing-boundary rule is 40 lines defending a shape that does not exist

`scripts/verify_context_declaration.py` is 207 lines, with 236 lines of test and 159 lines of
fixture — **602 lines guarding exactly one declaration**, one-directionally, in a check the
script's own docstring says *"CANNOT catch the reverse"*.

The clearest speculative unit inside it is `_bounded_after` (`:59-72`) plus
`_TRAILING_CONTINUATION_CHAR` (`:52`), plus their two fixtures
(`boundary_trailing_rejected`, `boundary_trailing_legitimate_accepted`) and two tests
(`test_context_declaration_lint.py:127`, `:140`). This machinery exists to stop a declared
`docs/agents/GLOSSARY.md` from matching a prose occurrence of `docs/agents/GLOSSARY.md.bak`, and
it needs a one-character lookahead past `.` to distinguish an extension from sentence punctuation.

No `.bak`/`.old`/`.tmp` sibling path appears in any imperative in the corpus. The failure shape
being defended against is: someone edits the prose to name a backup file, edits the declaration to
name the original, and both survive review. The leading-boundary rule (`_PATH_CHAR`, the
`agents/GLOSSARY.md` inside `docs/agents/GLOSSARY.md` case) is genuinely plausible — a shorter path
really is a prefix-suffix of a longer real one in this corpus. The trailing one is not.

**Delete:** `_bounded_after`, `_TRAILING_CONTINUATION_CHAR`, both trailing fixtures, both trailing
tests; replace with `trailing_ok = end >= len(prose) or not _PATH_CHAR.match(prose[end])`, which
is one line and over-rejects only the sentence-period case that would then need `.` excluded from
`_PATH_CHAR` — or accept plain substring matching on the trailing side. ~40 lines.

**Larger version of the same question, stated once and not padded:** the whole lint is 602 lines
for a check that fires on one task, catches one direction, and whose blind spot is documented in
four places. If it is kept, S7's narrow deletion still applies. If someone is willing to reopen
`decision:prose-stays-plus-lint`, the honest comparison is 602 lines against "a reviewer reads six
paths in a diff."

---

## MINOR

### M1 — `rev()`'s docstring names a test method

`scripts/context_manifest.py:87-88` cites
`RevIsGitBlobOid.test_rev_diverges_from_git_for_content_git_refuses_to_normalise` by full name.
Production source referencing a test method name is a rename-rot pointer in the wrong direction.
**Delete** the citation; the property is stated in the sentence above it.

### M2 — the escape guard in `resolve()` is unreachable

`scripts/context_manifest.py:196-201` plus its six-line comment. Its own comment concedes the
`..` rejection is the primary guard and that it *"cannot see"* the drive-letter/stream forms.

I fuzzed it: after the backslash (`:170`), colon (`:181`), glob (`:187`), absolute and `..`
(`:193`) rejections, no 1-, 2-, or 3-component path built from
`{a, ., .., '', /, space, ~, %, $, ", |, <, \n}` reaches it — 0 hits out of 2745 inputs. The one
case its `target != base` allowance admits is `path: "."` (`PurePosixPath(".").parts == ()`),
which resolves to the root directory and then fails downstream in `read_bytes` as an `OSError`
anyway.

**Delete** the branch and its comment (~12 lines), or keep a bare `assert` if a tripwire is wanted.

### M3 — the design-doc section restates the module docstrings

`docs/CHECKLIST_ENGINE_DESIGN.md:183-227` (45 lines) re-states, in the same terms:
"declaration order is content", "blob OID of LF-normalised bytes, computed in-process, no `git`
subprocess", "absent yields `rev: null` and keeps its row", "no globs or directory enumeration",
and the lint's one-directionality. Line 211 admits it: *"The lint's own docstring states that same
limit, in these same terms."*

**Delete** the restated mechanics; keep the two paragraphs that are genuinely doc-level and appear
nowhere in code — the relationship to `state()`/`active_id()` (`:185-192`) and the delivery-not-use
framing. ~20 lines.

### M4 — `durable` and `repo` are never distinct

`ROOT_TOKENS` has three members. Every roots mapping in the change maps `durable` to the same
directory as `repo`: `test_context_manifest.py:204`, `:386`, `:405`, `:432`, `:463`, `:487`,
`:515`, `:650`, `:762`; `test_context_determinism.py:106`, `:260`. The one real declared
`durable` path is `.agent-work/LESSONS.md`, which resolves identically under `repo`. The frame's
note that `agent_work_root.py` returns the worktree is precisely why the distinction *would*
matter — but no code in this change makes it, and no test exercises it.

A third token whose distinct meaning is unimplemented and untested is a token with one value.
**Merge** into `repo` until a caller resolves them differently, or add the one test that maps them
to different directories and asserts they resolve differently.

### M5 — three `load()` helpers and two checklist-shape predicates

`load()` is defined three times (`test_context_manifest.py:23`, `test_context_determinism.py:49`,
`test_context_declaration_lint.py:31`). `_is_gated_checklist` (`test_context_manifest.py:34`) and
`_is_checklist` (`verify_context_declaration.py:132`) are the same predicate with different
strictness. The `DECLARATION_KEY` copy in the lint is deliberately duplicated with a defending
comment (`verify_context_declaration.py:113-116`) — the defence is thin given the lint already
lives in the same `scripts/` directory as the module it copies from.

**Merge:** one `load()` in a shared test helper; one shape predicate.

### M6 — double cleanup in the enumeration booby-trap

`test_context_manifest.py:645` registers an `addCleanup` lambda restoring the patched `os`
attributes, and `:653-655` restores the same three in a `finally`. Two mechanisms, one job; the
lambda never does anything because the `finally` always runs first.
**Delete** the `addCleanup` line.

### M7 — corpus-size magic numbers and a redundant round-trip

`assertGreaterEqual(len(REAL_SPINE_TEMPLATES), 5)` (`test_context_manifest.py:403`) and
`assertGreaterEqual(len(templates), 10)` (`test_context_declaration_lint.py:178`) are hand-tuned
thresholds that must be bumped whenever the corpus grows and say nothing when it does not.
`assertGreater(len(...), 0)` carries the same "not vacuous" meaning without the maintenance.

In `EpisodeContextFieldShape` (`:757-801`), `round_tripped == manifest` (`:773-774`) and
`assert_json_native` (`:781-792`) prove the same property two ways, and `:799-801` re-asserts
`test_no_absolute_root_path_appears_in_content` (`:297`). **Delete** the round-trip assertion and
the absolute-path re-assertion; keep `assert_json_native`, which is the one that names the
acceptance criterion.

---

## Anything too thin?

**No load-bearing case is missing code.** One observation, offered as an observation and not as a
recommendation to add anything back:

`produce()`, `write_manifest()`, `manifest_path()` and the whole `run_facts()` subtree have no
production caller — nothing in `scripts/`, `skills/` or CI ever generates a manifest during a
real run. Acceptance criterion 1, "a manifest on every deterministic assembly," is therefore
currently vacuous: there are no assemblies. That follows directly from the settled no-CLI-verb
exclusion, so it is the right shape for this issue. It does mean the write path is the one place
where "built for a caller that does not exist" is *by design* rather than by accident — which is
exactly why S1 and S2 (fields and seams on that path that no one asked for) should not ride along
with it.

## What I am not attacking

The core is genuinely tight and I want that on the record rather than buried: `rev()` is eight
lines and eliminates the case analysis a commit-SHA design would have needed; `active_id()` is
imported rather than reimplemented and a test pins the `__code__.co_filename` to prove it;
`content()` is a one-line exclusion instead of a maintained mask list; there is exactly one
encoder and no stored digest to disagree with its own bytes; `newline="\n"` is load-bearing on
this platform and the AST guard for it is proportionate. `DeclarationError` raising rather than
skipping is correct and the fixture file that drives it is the best-documented artifact in the
change. None of that should be touched.

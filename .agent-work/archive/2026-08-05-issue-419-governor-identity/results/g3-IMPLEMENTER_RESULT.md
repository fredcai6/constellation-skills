# Implementation Result

## Assigned gate
`g3 — correct docs/GAUGE_WRITER_HOOK.md` (work id `issue-419-governor-identity`, worktree
`C:/Programs/constellation-skills-wt/epic418-a-419`, branch `epic-418/a-419-governor-identity`).

This file covers **three runs**: the original g3 gate (five prose edits, reviewed and confirmed
correct), **REWORK 1**, which answers the reviewer's BLOCK, and **REWORK 2**, one comment the
Commander ruled back in. The reworks are first because they are what changed since the review; the
original evidence follows unaltered below them.

- Original plan: `.agent-work/issue-419-governor-identity/g3-IMPLEMENTER_PLAN.json`
  (engine session `impl-419-g3`).
- Rework plan: `.agent-work/issue-419-governor-identity/g3r1-IMPLEMENTER_PLAN.json`
  (engine session `impl-419-g3r1`, driven m0→m4; rework 2 reopened `m3-comments` on that same plan
  under session `impl-419-g3r2` and re-drove m3→m4).

---

# REWORK 2 — the Commander ruled `find_latest_usage`'s docstring in, and the sweep found a second copy

## What was ruled

I had left `gauge_writer_hook.py:307` ("`docs/GAUGE_WRITER_HOOK.md`'s field table is wrong about this
today") because the rework handoff's own test said a *different* claim stays. The Commander ruled it
**IN**: it is false for the same reason as the six — this gate's own edit falsified it — and a
comment calling a field table wrong, sitting beside a field table we just corrected, is the exact
stale artifact this gate exists to remove. Correct ruling; I had flagged the same tension myself.

Driven through the engine as a `reopen` of `m3-comments` on the rework plan (rework 1/3), which
cascade-reset `m4-verify` and superseded its evidence, so the suite and the diff proof were both
re-earned rather than inherited.

**Fixed.** The docstring now reads "(measured; `docs/GAUGE_WRITER_HOOK.md`'s field table states both
polarities)". It keeps the fact that the polarity is measured and drops the claim about the document.

## The sweep the Commander asked for — count stated, and it found a second site

Archived: `.agent-work/issue-419-governor-identity/evidence/g3r2-doc-is-wrong-sweep.txt`.

```bash
$ grep -rn -i -E "wrong about|is wrong|out of date|outdated|stale (doc|table)|does not match the doc|contradict|GAUGE_WRITER_HOOK.md" \
    scripts/ tests/ --include=*.py --include=*.md | wc -l
35                                    # raw word-sweep hits
$ grep -rn "GAUGE_WRITER_HOOK.md" scripts/ tests/ --include=*.py | wc -l
11                                    # hits that actually name the document
```

**Count: 35 raw hits, 11 of which name the document, and TWO of those eleven assert the document is
wrong — not one.**

1. `scripts/hooks/gauge_writer_hook.py:307` — **fixed this run**, in scope.
2. **`tests/test_gauge_writer.py:1000-1001`** — the *same sentence*, copied into the test file's
   section comment above the #419 tests: "(measured; docs/GAUGE_WRITER_HOOK.md's field table is wrong
   about this today)". **Not fixed.** `tests/` is outside this rework's scope — comments only in
   `scripts/hooks/gauge_writer_hook.py`, and the ruling said nothing else changes — so I am reporting
   it rather than reaching for it. It is one comment line, the identical fix, and it needs a ruling
   the same way its twin did.

The remaining **nine** references are plain pointers, not claims about the document's correctness.
Each was read, not merely counted, and the two that assert something checkable were re-checked
against the corrected document: `install_constellation.py:541` (matcher `*`, timeout 10 — still what
the doc's snippet at :156-157 says) and `test_install_constellation.py:1996` (the doc still documents
the hand-wired `${CLAUDE_PROJECT_DIR}` form at :135-157). `scripts/hooks/spine_rail.py` names the
document zero times (grep exit 1). The other 24 word-sweep hits are unrelated modules that merely use
the words "is wrong" or "contradict" and name no document.

## Rework 2 evidence

```bash
$ git status --porcelain -- docs/ scripts/ skills/ tests/
 M docs/GAUGE_WRITER_HOOK.md
 M scripts/hooks/gauge_writer_hook.py
exit=0

$ git diff --stat -- docs/ scripts/ skills/ tests/
 docs/GAUGE_WRITER_HOOK.md          | 302 ++++++++++++++++++++++++++++---------
 scripts/hooks/gauge_writer_hook.py |  34 +++--
 2 files changed, 253 insertions(+), 83 deletions(-)
exit=0

$ python -c "<ast-normalize>"     # working file vs git show HEAD:...
exit=0                            # code identical to HEAD; comments and docstrings only
```

Still exactly two files, still nothing under `tests/` or `skills/`. The suite was re-run by the
engine after this edit — see "The suite is unmoved" below, which now reports the rework-2 run.

---

# REWORK 1 — the record is not four fields any more, and the document said it was in six places

## What the BLOCK was

`docs/GAUGE_WRITER_HOOK.md` still called the gauge record four fields, while `identity_resolution_ms`
shipped in this issue's own g2 commit `5491bd4`. The reviewer named **two** doc sites (lines 35 and
164) where the original handoff had named one, and warned that any anchor list framed as "the section
to edit" misses sites systematically in a document that asserts one code fact in four-to-five places.

**So I did not fix where I was pointed. I enumerated by command. The count is six sites, not two.**

## The enumeration — count stated, before and after

Archived: `.agent-work/issue-419-governor-identity/evidence/g3r1-fourfield-before.txt` (BEFORE) and
`g3r1-fourfield-after.txt` (AFTER, re-run after my last edit of this rework).

```bash
$ grep -n -i -E "four|4[- ]field|frozen|no extras|field count|fields only" \
    docs/GAUGE_WRITER_HOOK.md scripts/hooks/gauge_writer_hook.py scripts/hooks/spine_rail.py
exit=0
$ ... | wc -l
13          # BEFORE: 13 matching lines — doc 5, gauge_writer_hook.py 7, spine_rail.py 1
```

**BEFORE count: 13 hits across the three files. SIX distinct sites assert the four-field /
frozen-record claim; seven hits are a different claim and stay.** Adjudicated hit by hit in the
archive:

| hit | verdict |
|---|---|
| `doc:35` "writes the frozen 4-field record" | same claim, false since `5491bd4` → **fixed** (this is the site the original handoff never named) |
| `doc:55` "That report is four-state" | different claim — the installer's wiring report → left |
| `doc:164` "All four fields present, no extras." | same claim, false since `5491bd4` → **fixed** |
| `doc:251` "the frozen record's `model` field" | same class — the *frozen* epithet with no count → **fixed** (epithet dropped) |
| `doc:278` "The other four stay silent by design" | different claim — skip-cause arithmetic → left |
| `hook:10` "frozen DESIGN_SPEC #178" | different claim — a frozen design document, not the record → left |
| `hook:20` "Record is FROZEN, four fields only" | same claim → **fixed** (named in the rework handoff) |
| `hook:353` "Build the frozen 4-field record" | same claim in different words → **fixed** (see note below) |
| `hook:403-404` "that record is frozen at four fields and shared with the reader" | same claim — the matching in-code comment the handoff names → **fixed** |
| `hook:634`, `hook:638` "its four required fields" / "The four required fields" | g2's own comments, already correct → left |
| `spine_rail:9` "frozen DESIGN_SPEC #138" | different claim → left |

A token sweep is blind by construction, so I also ran a **token-blind** pass for record-shape claims
that use none of the swept words (`schema_version|fill_fraction|observed_at|REQUIRED_FIELDS|record
shape|exactly (these|the) (keys|fields)|identity_resolution_ms`). It returns the JSON sample at
`doc:154` — a top-level session's example, not a claim about every record, though it sits three lines
above the eyeball check, so I labelled it — and `hook:641`, the write itself. Nothing else states the
field count without a swept word.

**`hook:353` deserves its own line, because it is the one hit where the honest answer was not
obvious.** `compute_record`'s docstring said "Build the frozen 4-field record". That function really
does return four fields — the fifth is added by its caller at `:641` — so the sentence was locally
true and globally misleading. I kept the local truth and removed the global claim: the docstring now
says four is what *this function* returns and names the caller that adds the fifth.

**AFTER count: 20 matching lines.** The count *rises*, and that is expected: the correct statement
uses the same words as the wrong one. So the count is not the test. The test is the assertion that
had to disappear:

```bash
$ grep -n -i -E "frozen 4-field|frozen record|FROZEN, four|four fields present, no extras|four fields only" \
    docs/GAUGE_WRITER_HOOK.md scripts/hooks/gauge_writer_hook.py scripts/hooks/spine_rail.py
exit=1          # no hit — every four-field/frozen-record assertion is gone
```

## What the corrected text says

One authoritative statement, five pointers — because `duplicated-code` across the doc's assertion
sites is exactly the mechanism that let this defect survive the first pass.

- **New section `## The record is four required fields, plus one on a subagent`** (doc:45), placed
  right after "What this hook does". It opens by saying it is the one place the record's shape is
  stated. It carries a field table marking `identity_resolution_ms` **not required, dispatched agents
  only (#419)**; the fact that `scripts/gauge_reader.py` validates the four and does not reject
  extras, which is why the fifth cost the read side nothing; **what the field measures** — a float in
  milliseconds covering the two identity steps (composing the binding key, deriving that agent's own
  transcript path) and explicitly *not* the binding-store read between them, which is pre-existing
  binding resolution; **the budget — 100 ms**, the issue's stated placeholder, asserted at
  `tests/test_gauge_writer.py:1201`; and why a top-level record is byte-identical to before #419,
  which is the reason the pre-existing tests still pass.
- **doc:35** now names the four required fields and the optional fifth, and points at that section.
- **doc:164, the eyeball check** — the section the BLOCK turns on — now reads: all four required
  fields present; on a dispatched agent's gauge a fifth field `identity_resolution_ms` is also
  present and is **correct, not a defect**, and should read under 100 ms; a top-level agent's gauge
  carries exactly four; anything beyond those five is unexpected. A human inspecting a correct
  subagent gauge can no longer judge it wrong.
- **doc:154's JSON sample** is now labelled as a top-level agent's record, with a note that a
  dispatched agent's carries a fifth.
- **doc:251** drops the `frozen record` epithet.

Both facts (what it measures, the budget) were read out of `scripts/hooks/gauge_writer_hook.py:555-612`
and `tests/test_gauge_writer.py:1171-1227`, not inferred.

## Comments only, and proved mechanically

Three comment sites in `scripts/hooks/gauge_writer_hook.py` (module docstring, `compute_record`'s
docstring, the uncalibrated-sidecar comment). **Not one executable line changed**, and the proof is
not my word:

```bash
$ python -c "<ast-normalize: parse both, strip module/class/function docstrings, compare ast.dump>" \
    # compares git show HEAD:scripts/hooks/gauge_writer_hook.py against the working file
exit=0          # identical code — only comments and docstrings differ
```

**The guard was shown red before it was offered as evidence** (`CREW_CONTEXT.md`: a check that cannot
fail is indistinguishable from one that passed). I copied the working file, changed one executable
line — `record["identity_resolution_ms"] = identity_ms` → `= 0.0` — asserted the mutation actually
applied, and re-ran the same check:

```
mutation applied to <scratchpad>/mutated_hook.py
DIFFERENT
exit=1
```

The same check is the `m3-comments` postcondition in the rework plan, so the engine ran it too.

## The reviewer's two further comment candidates — one fixed, one left, deliberately

- `gauge_writer_hook.py:20` ("Record is FROZEN, four fields only") **is** the four-field claim, and
  the rework handoff names it. Fixed.
- `gauge_writer_hook.py:300-306` (`find_latest_usage`'s docstring, "docs/GAUGE_WRITER_HOOK.md's field
  table is wrong about this today") is **a different claim entirely** — it is about the sidechain
  polarity row, not the record's field count — so per the handoff's own test I left it and am saying
  so. It is still a real defect: it was made false by **this gate's own doc edit**, which is the
  authoring-side blast radius `global-everyone.md` describes. It stays a triage candidate below, and
  it is a one-line comment fix if the Commander rules it in.

## Also done: the stale-sweep observation from the review

The review's one non-reproducing artifact was my post-edit sidechain sweep, whose line numbers were
stale by a few final edits (offsets `[2,2,2,1,2]`). Re-archived **after my last edit this time**, at
`evidence/g3r1-grep-sweep-post.txt`: **5 matching lines (234, 236, 291, 350, 432), 7 occurrences** —
the same 5/7 the reviewer reproduced, now at line numbers that match the delivered file. The
token-blind counter-sweep (`non-sidechain|must be falsy|main-chain only|only main-chain`) still exits
1. The superseded artifact `evidence/g3-grep-sweep-post.txt` is left in place for audit; treat
`g3r1-grep-sweep-post.txt` as the live one.

I also rewrapped the two over-wide lines the review flagged as cosmetic in my own prior diff (now at
doc:338 and doc:438).

## Rework scope and evidence

```bash
$ git status --porcelain -- docs/ scripts/ skills/ tests/
 M docs/GAUGE_WRITER_HOOK.md
 M scripts/hooks/gauge_writer_hook.py
exit=0

$ git diff --stat -- docs/ scripts/ skills/ tests/
 docs/GAUGE_WRITER_HOOK.md          | 302 ++++++++++++++++++++++++++++---------
 scripts/hooks/gauge_writer_hook.py |  30 ++--
 2 files changed, 251 insertions(+), 81 deletions(-)
exit=0
```

Two files, and the second is comments only by the AST check above. Nothing under `tests/` or
`skills/`. Archived at `evidence/g3r1-diff-stat.txt`. Line endings checked, because this is Windows:
the hook file is 691 LF / 0 CRLF (HEAD blob 679 LF / 0 CRLF) and the document is 519 CRLF / 0 LF —
each internally consistent, so no line-ending noise rode in.

**The suite is unmoved** — run by the engine as the `m4-verify.c2` postcondition, which both runs it
and pins the count. Run twice, once per rework, the second after the reopen superseded the first:

```bash
$ python -m pytest tests -q > evidence/g3r1-pytest.txt 2>&1; grep -q "1667 passed, 2 skipped" evidence/g3r1-pytest.txt
1667 passed, 2 skipped, 550 subtests passed in 458.65s (0:07:38)     # rework 1
exit=0
1667 passed, 2 skipped, 550 subtests passed in 466.41s (0:07:46)     # rework 2, live in the archive
exit=0
```

Exactly **1667 passed, 2 skipped** — the handoff's stop condition holds. `python -m pytest`, never
`py`.

---

# The original gate — five edits, unchanged and still standing

The reviewer confirmed all three frozen invariants MET and reproduced each against the code. Nothing
below was redone in the rework; it is retained as the evidence for those five edits.

## Completed slice
All five assigned edits are in, plus four adjacent corrections named below. Every claim left in the
document was checked against `scripts/hooks/spine_rail.py` and `scripts/hooks/gauge_writer_hook.py`
at `5491bd4`, not inherited from the old text or from the handoff.

**(a) The transcript field table.** The `isSidechain` row now carries the polarity rule: falsy on a
main-chain read, truthy on a dispatched agent's own transcript, where every line reads
`isSidechain: true`. A new `agentId` row says it is top-level on the line, must equal the payload's
`agent_id`, and is not consulted on a top-level read. The table's preamble no longer claims ALL rows
hold for every read, and it now names which transcript is read for which agent.

**(b) A payload-field table** (`## The payload fields this hook reads`) with `transcript_path`,
`session_id` and `agent_id`, each with when it is present and what it is used for, followed by the
load-bearing paragraph: `agent_id` is absent from a top-level payload — the harness omits the key
rather than sending null — so identity is handed to the hook, never discovered by it, and
`"agent_id" in payload` is the test for "am I dispatched".

**`agent_type` is NOT a row, and this is a deliberate departure from the handoff.** Edit (b) named
it as a field the hook reads. No hook reads it: `grep -n "agent_type" scripts/hooks/*.py` exits 1
(archived, sweep 2 §C). It appears only in `tests/fixtures/probe_payloads.jsonl` and one assertion at
`tests/test_spine_rail.py:171`. Close criterion 2 forbids a field the code does not read, and the
dispatch forbids writing a claim I did not check, so the row is out. The document instead says in one
clause that `agent_type` is sent by the harness and read by neither hook — a negative, checked both
ways, so a later reader does not re-derive it. **The reviewer ruled this departure correct.**

**(c) The binding section.** `binding_key`'s three outcomes are now a table: bare `session_id` for a
top-level agent, `session_id#agent_id` for a dispatched one, `None` — bind nothing — when
`session_id` is falsy or `agent_id` is present but unusable. The bind-nothing case is stated with its
reason (a fallback would file the subagent's entry under the parent's key and silence the parent's own
gauge). Both usability tests are named: `spine_rail`'s reject tokens `#`, `/`, `\`, `..`, and the
gauge writer's stricter `[A-Za-z0-9_-]{1,64}` allowlist, with why the writer is stricter (it
interpolates the id into a real path). Also added: `SessionStart` always binds under the bare
`session_id` because that event carries no `agent_id`, and `session_view` merges the bare key with
every per-agent key beneath it. The exactly-one-spine coupling is restated as holding per agent.

**(d) The skip causes.** `subagent-transcript-missing` is added to the flagged list with the derived
path shape and the never-fall-back rule in the document's own voice. The section's arithmetic was
recounted against `handle_post_tool_use` at HEAD: **three** flagged (was "two"), **four** silent (was
"three"). The fourth silent cause is new and was not in the handoff's list — the acting agent's
identity does not resolve, `_binding_key` returns `None`, nothing is looked up. Leaving it out would
have made the enumeration wrong in the same way the polarity row was wrong.

**(e) Both residuals, side by side**, in `### Two residuals survive this change, and they sit side by
side` at the end of the binding section.

### Four adjacent corrections, and why each is inside the five edits

1. **Step 3 of "What this hook does"** said the parser takes "the latest non-sidechain assistant
   message". That is edit (a)'s claim stated in a second place; a token sweep would have left it
   standing if the sweep alone were trusted.
2. **Steps 1 and 2** said the hook reads `session_id` and looks it up. That is edit (c)'s claim in a
   second place. Step 2's example for #202 — "an Agent-tool subagent sharing its parent's
   `session_id` claims its own spine" — is exactly what #419 stopped, so it was replaced with the
   case that survives.
3. **The ambiguous-binding bullet** described the same superseded example and said an orchestrator is
   "ungauged for the duration of every wave it dispatches". Dispatching a wave no longer adds entries
   under the orchestrator's key. The live case is one agent holding two spines of its own — a
   Commander leasing both its `spine.json` and its `execute.json`, which I confirmed against the real
   `.agent-work/.spine-rail-binding.json` in the main checkout, where one key holds ten entries
   including both files for several runs.
4. **The HITL ordering note** said a record needs "a binding for the session". Since #419 a parent's
   claim no longer stands in for its child's. Same claim as (c), third location.

### Where I did not follow the handoff's wording, and what the code says instead

The handoff's residual 2 says that before this change a non-claiming subagent's tool call "would have
resolved against the parent's bare key and, in a single-spine session, written a reading that was
misattributed but present". Checked at `git show 4767782^:scripts/hooks/gauge_writer_hook.py`: the
pre-change call was `resolve_gauge_path(project_dir, data.get("session_id"))` and
`compute_record(transcript_path)` — the **parent's** transcript. So the record written was the
parent's own, and where the bound spine was the parent's own it was filed correctly, not
misattributed. The document therefore splits residual 2 into the two things that were really
happening:

- Where the bound spine was the parent's, the loss is coverage: a parent idle while its children work
  no longer picks up its own latest usage line until it runs a tool call itself. That loss is bounded
  — `scripts/gauge_reader.py` judges staleness from the record's `observed_at`, never file mtime
  (comment at line 28, `_parse_record` line 205), so those writes never bought freshness.
- Where the single bound spine belonged to a **different** top-level agent sharing the `session_id`,
  that write did file one agent's reading against another's spine, and #419 removes it.

Both halves are checked; the handoff's one-sentence version is true of the second and not the first.
**The reviewer reproduced this split and ruled it correct.**

## Scope
**Files changed (both runs):**
- `docs/GAUGE_WRITER_HOOK.md` — the whole original assignment plus the rework's doc sites.
- `scripts/hooks/gauge_writer_hook.py` — **comments and docstrings only**, rework only, under the
  widened scope the rework handoff granted. Proved by AST equality against HEAD.

No installed copy under `skills/` was touched — there is none:
`grep -rl "GAUGE_WRITER_HOOK" --include=*.md skills/` returns nothing. That exclusion is **vacuous
rather than satisfied**, as the reviewer noted; it could not have failed.

**Specific exclusions touched:** no. The original gate's "no code change" exclusion held for the
original run; the rework handoff replaced it with "comments only, not one executable line", and that
is met mechanically.

**Not committed.** Both runs' edits sit in the working tree so review runs against `git diff`,
matching the one-commit-per-gate shape of `340c46d` (g1) and `5491bd4` (g2), which are gate-scoped
rather than implementer-scoped.

## Behavior changed
No. Prose and comments only, and the code is byte-equal in AST terms to `5491bd4`.

## Map Impact
- **Structural anchors touched:** `docs/GAUGE_WRITER_HOOK.md` — a **new** record-shape section
  (~45), the payload-field table (~250), the transcript field table (~286), the skip-cause
  enumeration (~310), the binding-assumption section (~405) with a residuals subsection (~460).
  `scripts/hooks/gauge_writer_hook.py` — the module docstring's design contract, `compute_record`'s
  contract, the uncalibrated-sidecar rationale. No structure changed; the description of it did.
- **Constraints/assumptions touched:** the session→spine binding coupling is stated per agent rather
  than per session. The gauge record is now stated as **four required fields plus one optional field
  on the dispatched-agent path**, replacing "frozen at four" wherever that appeared. The document is
  the closest thing this repo has to an architecture packet for the governor write side; it carries
  that weight (inherited decision, per the handoff).
- **Claims/evidence produced:** the four-field enumeration (before/after), the sidechain sweep
  (re-archived post-final-edit), the payload-field list and the comments-only AST proof, all under
  `.agent-work/issue-419-governor-identity/evidence/g3*` and reproducible by command.
- **Triage candidates:** the three below.

## Test mode
**Required:** evidence-only — no runtime test surface. The handoff's frozen invariant chain plus the
rework's by-command enumeration stand in for tests.
**Satisfied:** yes. All three original invariants met (reviewer-confirmed) and the rework's evidence
list met in full.

## Evidence

### Rework — see the rework section above for the four archived commands and their exit codes
- `evidence/g3r1-fourfield-before.txt` — 13 hits, six sites, adjudicated hit by hit.
- `evidence/g3r1-fourfield-after.txt` — 20 hits; the false-assertion grep exits 1.
- `evidence/g3r1-grep-sweep-post.txt` — 5 lines / 7 occurrences, re-run after the last edit.
- `evidence/g3r1-diff-stat.txt` — status, diff stat, and the comments-only AST proof.
- `evidence/g3r2-doc-is-wrong-sweep.txt` — the Commander-requested sweep for comments asserting
  the document is wrong: 35 raw hits, 11 naming the document, 2 asserting it wrong.
- `evidence/g3r1-pytest.txt` — 1667 passed, 2 skipped, exit 0 (rework 2's run is the live one).

### Invariant 1 — no sentence still asserts the pre-fix sidechain polarity

Pre-edit sweep, archived at `evidence/g3-grep-sweep.txt`:

```bash
$ grep -n -i -E "isSidechain|sidechain|falsy" docs/GAUGE_WRITER_HOOK.md
26:3. Parses the tail of the transcript (JSONL) for the latest non-sidechain
185:  `{"type": "assistant", "isSidechain": false, "message": {"model": "...",
213:| `isSidechain` | top-level | must be falsy (subagent turns are a different context window and are skipped) |
267:  bounded tail-scan window, that is a non-sidechain assistant message with a
exit=0
```

**Count: 4 lines, 5 occurrences.** Adjudication: line 26 asserted the old polarity (fixed); 185 is a
measured sample from a real top-level transcript (kept, now qualified); 213 was the wrong row
(replaced); 267 asserted the old polarity in prose (fixed).

Post-edit sweep: **superseded** by `evidence/g3r1-grep-sweep-post.txt` (5 lines, 7 occurrences, live
line numbers 234/236/291/350/432). The earlier `evidence/g3-grep-sweep-post.txt` recorded the same
counts and adjudications at line numbers that went stale before delivery; it is retained for audit
only. Adjudication, unchanged: 234 and 291 are new and state the rule correctly; 236 is the
historical sample, now explicitly framed as a top-level session; 350 names the polarity as
agent-dependent without asserting a direction; 432 is `binding_key`'s falsy `session_id`, unrelated
to the transcript flag.

**The sweep alone was not trusted.** The field table and the whole skip-cause section were read end
to end. Two sentences asserting the old polarity were found that way — step 3 of "What this hook
does" and the no-usable-record bullet.

### Invariant 2 — payload fields, enumerated by command, compared both ways

Archived at `evidence/g3-payload-fields.txt`:

```bash
$ grep -nE "(\bdata\b|\bpayload\b)[^\n]*(\.get\(|in \(?data|in \(?payload)" scripts/hooks/spine_rail.py scripts/hooks/gauge_writer_hook.py
spine_rail.py:174:        sid = data.get("session_id")
spine_rail.py:179:        agent_id = data.get("agent_id")
spine_rail.py:324:        cwd = data.get("cwd")
spine_rail.py:413:        command = ((data.get("tool_input") or {}).get("command")) or ""
spine_rail.py:422:        sid = data.get("session_id")
spine_rail.py:427:        cwd = data.get("cwd") or str(project_dir)
spine_rail.py:536:        sid = data.get("session_id")
spine_rail.py:616:        sid = data.get("session_id")
spine_rail.py:654:                    "worktree": data.get("cwd") or str(project_dir),
gauge_writer_hook.py:225:    if "agent_id" in (data or {}) and not _is_usable_agent_id((data or {}).get("agent_id"))
gauge_writer_hook.py:551:        transcript_path = data.get("transcript_path")
gauge_writer_hook.py:592:        acting_agent_id = data.get("agent_id") if "agent_id" in data else None
exit=0

$ grep -nE "\"[A-Za-z_]+\" (not )?in \(?(data|payload)" scripts/hooks/spine_rail.py scripts/hooks/gauge_writer_hook.py
spine_rail.py:177:        if "agent_id" not in data:
exit=0

$ ... | grep -oE "\"[A-Za-z_]+\"" | sort -u        # 5 distinct keys
"agent_id"  "cwd"  "session_id"  "tool_input"  "transcript_path"

$ grep -n "agent_type" scripts/hooks/spine_rail.py scripts/hooks/gauge_writer_hook.py
exit=1
```

The first regex needs the dict name before the read, so it misses bare membership tests; the second
grep exists to close that gap, and it found `spine_rail.py:177`. Both are archived.

**code → doc:** all five appear. `transcript_path`, `session_id`, `agent_id` are table rows; `cwd`
and `tool_input` are named in the paragraph under the table as `spine_rail`'s own reads that never
reach the gauge writer.
**doc → code:** every field the document names is read at a cited line above. `agent_type` is named
only as a field neither hook reads, which the grep's exit 1 establishes.

### Invariant 3 — the stated binding key matches `binding_key`, and both residuals are named

The document's table is `spine_rail.binding_key`'s three returns, read at
`scripts/hooks/spine_rail.py:139-186`: bare `sid` when `"agent_id" not in data` (177-178);
`"<sid>#<aid>"` when the id is a non-empty string free of `#`, `/`, `\`, `..` (180-184); `None`
when `sid` is falsy (175-176) or the id is unusable (180-183). The bind-nothing case reaches the
store at `handle_post_tool_use` 424-425 (`if key is None: return {}`) — no entry written. The
gauge writer's stricter allowlist is `_AGENT_ID_ALLOWED` / `_binding_key`, 172-227. Both residuals
are named together under `### Two residuals survive this change, and they sit side by side`,
cross-referenced from the skip-cause section.

### The diff

Archived in full at `evidence/g3-diff.txt` (original run) and `evidence/g3r1-diff-stat.txt` (rework,
with the comments-only proof).

## TDD evidence, if required
Not applicable — no test surface, per the handoff's stated test mode. The one mechanical guard this
rework introduced (comments-only AST equality) was nevertheless shown red before green, against a
one-line mutation, and the mutation was asserted to have applied.

## Docs/contracts touched
- `docs/GAUGE_WRITER_HOOK.md` — the whole assignment.
- `scripts/hooks/gauge_writer_hook.py` — its design-contract docstring and two comments; the contract
  it *documents* changed at `5491bd4`, the contract it *implements* did not change here.

## Assumptions
- "The hook" in edit (b) means the gauge writer, so its payload table lists the three fields on the
  writer's own path and names `cwd`/`tool_input` as `spine_rail`'s in prose. Criterion 2 enumerates
  over both files, and both directions close either way.
- The rework's "matching in-code comment" is read as `gauge_writer_hook.py:403-404` (a `#` comment).
  `compute_record`'s docstring at `:353` was the same claim in different words, so it is fixed too;
  the enumeration is what found it, not the handoff.

## Stop conditions hit
- **Original run, "the code contradicts what you were told to write"** — hit twice, recorded rather
  than absorbed: `agent_type` (edit b) and residual 2's "misattributed but present" (edit e). The
  reviewer ruled both departures correct.
- **Original run, "something else load-bearing and wrong, outside the five edits"** — hit twice. One
  of those (the four-field claim) is what the rework fixes; the other two remain below.
- **Rework, "a moved test count"** — not hit. 1667 passed, 2 skipped, exit 0.

## Out-of-scope observations

1. **RESOLVED in rework 2** — `find_latest_usage`'s docstring ("the field table is wrong about this
   today") was ruled IN by the Commander and is fixed. Kept here because the reasoning is what the
   ruling turned on: it was false because of **this gate's own doc edit**, which is the
   authoring-side blast radius, and that beat the handoff's same-claim/different-claim test.
2. **OPEN, and it is the same defect one file over: `tests/test_gauge_writer.py:1000-1001`** carries
   the identical sentence — "(measured; docs/GAUGE_WRITER_HOOK.md's field table is wrong about this
   today)" — in the section comment above the #419 tests. Found by the rework-2 sweep, not by being
   pointed at. `tests/` is outside the granted scope so I did not touch it. One comment line, the
   same fix as its twin, and it needs the same ruling.
3. **The format-drift paragraph still says drift means "the writer silently stops producing
   records".** Wrong since **#271**, not since #419: that case now writes a `no-usable-record`
   sidecar on a single resolved candidate. No #419 change falsified it, so it stays out of scope —
   the reviewer agreed.
4. **The silent-cause bullet is incomplete** (the reviewer's tc4): it names two triggers for a `None`
   binding key (unusable `agent_id`, `spine_rail` import failure) and omits the falsy-`session_id`
   trigger. The binding table states it, so the document is not wrong overall. Not touched — outside
   both the five edits and the rework's named class.

## Workflow Feedback

- **Handoff gaps:** The original handoff's edit (b) listed `agent_type` as a field the hook reads,
  directly under a close criterion forbidding exactly that — the handoff's own body and its own gate
  disagreed. Same shape in edit (e). Both were caught only because the dispatch said to check every
  claim against the code, so **"check it, don't inherit it" belongs in the handoff, not only in the
  dispatch prompt.** The rework handoff fixed the deeper version of this by saying outright "do not
  fix where you are pointed — enumerate by command and state the count," and that instruction is what
  turned two named sites into six found ones. It should be the default wording for every prose gate,
  not a lesson learned once per BLOCK.
- **Context rediscovered:** Three things. (i) That `identity_resolution_ms` was introduced by **g2 of
  this very issue** — the reviewer had to run `git log -S` to establish it, and the rework handoff
  carries it, which is the right fix. (ii) **The budget.** The rework handoff said "say what it
  measures and against what budget" without naming either; both live only in the code and in
  `tests/test_gauge_writer.py:1173`, where 100 ms is labelled a *placeholder*. A handoff asking for a
  number should carry the number or name where it is pinned, because the implementer will otherwise
  guess or, worse, infer one from a timing. (iii) That the same four-field claim also sat in
  `compute_record`'s docstring, where it was *locally true* — an enumeration finds that, an anchor
  list never does.
- **Instructions improvised around:** The plan template assumes a command postcondition can prove the
  work, and for prose the only mechanical check available is a grep for a phrase I chose myself,
  which proves the string is present and never that the sentence is right. For the **code-comment**
  half of this rework I could do better and did: the postcondition is AST equality against `HEAD`
  with docstrings stripped, which mechanically proves "comments only, not one executable line"
  instead of asserting it. **That check is worth lifting into the templates** — any comments-only or
  docs-adjacent gate can use it verbatim, and it converts the most-likely-violated constraint of such
  a gate from a promise into a check. It is also cheap to demonstrate red, which the plan template
  never asks for but `CREW_CONTEXT.md` does.
- **What would made this easier:** state the expected end-state **counts** in the handoff — the same
  ask the reviewer made independently. This gate needed three: flagged/silent skip causes (3/4),
  payload keys (5), and record fields (4 required + 1 optional). Each was a derivation I had to
  perform and the reviewer had to re-perform. A prose gate whose close criteria are countable
  converts a derivation into a check on both sides of the desk. One caution learned here: **a count
  can legitimately go up after a correct fix** — mine went 13 → 20, because the right sentence uses
  the same words as the wrong one. The check that carries weight is the assertion that must
  *disappear*, so a handoff should name that assertion, not just a number.

## Return status
`complete`

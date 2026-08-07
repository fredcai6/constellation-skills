# Review Result — g3 RE-REVIEW: `docs/GAUGE_WRITER_HOOK.md`

**Verdict: APPROVE**

Work id `issue-419-governor-identity`, gate `g3` (after rework 1 and rework 2). Worktree
`C:/Programs/constellation-skills-wt/epic418-a-419`, branch `epic-418/a-419-governor-identity`,
base HEAD `5491bd4`.

This supersedes the BLOCK previously written at this path. That review's survey is preserved at
`.agent-work/issue-419-governor-identity/g3-review/review.json`; this re-review drove a **fresh**
survey at `.agent-work/issue-419-governor-identity/g3r2-review/review.json` (engine session
`g3-rereviewer-e8249451`, 15 checks, all visited, all pass) so the earlier verdict's provenance was
not overwritten by a reclaim.

I did not carry any earlier MET ruling forward. The document has changed by 302 lines since I read
it, so all three frozen invariants were re-verified from scratch against the code.

---

## The named fix from my BLOCK: landed, and wider than I named it

My BLOCK said the record carries a fifth field, `identity_resolution_ms`, while the document called
it frozen at four — and warned that an anchor list framed as "the sites to edit" misses sites
systematically. I named two. **The rework enumerated by command and found six. I re-enumerated
independently and confirm the six, then found a seventh the enumeration could not reach.**

I ran the enumeration against the HEAD blobs rather than accepting the implementer's table:

```
$ git show HEAD:docs/GAUGE_WRITER_HOOK.md          > head_doc.md
$ git show HEAD:scripts/hooks/gauge_writer_hook.py > head_hook.py
$ grep -n -i -E "four|4[- ]field|frozen|no extras|fields only" head_doc.md head_hook.py
11 hits — doc 4, hook 7
```

Adjudicated hit by hit, by me:

| hit | my verdict |
|---|---|
| `doc:31` "writes the frozen 4-field record" | **same claim** → must go |
| `doc:51` "That report is four-state" | different — the installer's wiring report; 4 states verified at delivered `doc:91-98` |
| `doc:158` "All four fields present, no extras." | **same claim** → must go |
| `doc:215` "the frozen record's `model` field" | **same claim** (the `frozen` epithet) → must go |
| `hook:10` "frozen DESIGN_SPEC #178" | different — a frozen design document, not the record |
| `hook:20` "Record is FROZEN, four fields only" | **same claim** → must go |
| `hook:353` "Build the frozen 4-field record" | **same claim** → must go |
| `hook:403-404` "that record is frozen at four fields" | **same claim** → must go |
| `hook:634`, `hook:638` "its four required fields" | different — g2's own comments, already correct |

**Six.** My 11 reconciles exactly with the implementer's BEFORE count of 13: their base was the
post-original-g3 working tree, which adds `doc:278` ("The other four stay silent" — a skip-cause
count, correctly left), and they also swept `spine_rail.py`, adding `spine_rail:9` ("frozen
DESIGN_SPEC #138", correctly left). So the six is corroborated from a base I reconstructed myself,
not inherited from the report.

**None survives.** The assertion that had to disappear:

```
$ grep -n -i -E "frozen 4-field|frozen record|FROZEN, four|four fields present, no extras|four fields only|frozen at four|record is frozen" \
    docs/GAUGE_WRITER_HOOK.md scripts/hooks/gauge_writer_hook.py scripts/hooks/spine_rail.py
exit=1
```

Site by site in the delivered files: `doc:35-40` names the four required plus the optional fifth and
points at the new section; `doc:202-207` — the eyeball check the BLOCK turned on — now says a fifth
field on a dispatched agent's gauge is **correct, not a defect**, so a human inspecting a correct
subagent gauge can no longer judge it wrong; `doc:294` has dropped the epithet ("the record's `model`
field"); `hook:20-27`, `hook:358-361` and `hook:412-416` are rewritten.

`hook:353` is the one that needed judgment and the call was right: `compute_record` really does
return four — the fifth is added by its caller at `:653` — so the docstring keeps the local truth
("Four is what THIS function returns, always") and names the caller that adds the fifth.

---

## The three frozen invariants — all MET, all re-verified against the code

### Invariant 1 — no sentence still asserts the pre-fix sidechain polarity. **MET.**

**Code first.** `find_latest_usage`, `scripts/hooks/gauge_writer_hook.py:319-323`:

```python
if agent_id is None:
    if d.get("isSidechain"):
        continue
elif not d.get("isSidechain") or d.get("agentId") != agent_id:
    continue
```

Falsy required on a main-chain read; truthy **and** `agentId` equality required on a dispatched
agent's own transcript. `doc:291` states exactly that, both directions. `doc:292`'s `agentId` row
states the equality and that a top-level read does not consult the field.

**Sweep, count stated:** 5 matching lines, 7 occurrences, at 234, 236, 291, 350, 432. These are the
exact line numbers in `evidence/g3r1-grep-sweep-post.txt`, so the stale-offset defect I flagged last
time is fixed — the archive now matches the delivered file. Adjudicated: 234/236 the historical
top-level sample, now explicitly framed as top-level; 291 the corrected row; 350 the skip-cause
bullet, which says "on the acting agent's side of the sidechain polarity" and is polarity-neutral by
construction; 432 is `binding_key`'s falsy `session_id`, unrelated to the transcript flag.

**The sweep is blind by construction, so I read past it.** I read `doc:278-310` (the field table and
its preamble) and `doc:312-392` (the whole skip-cause section) end to end. The preamble at 282-286 no
longer claims all rows hold for every read and names which transcript is read for which agent. Step 3
at `doc:28-34` now reads "the acting agent's own transcript … the main-chain lines of
`transcript_path` for a top-level agent, the derived subagent transcript for a dispatched one" — one
of the two sentences the token sweep alone missed.

A counter-sweep for the old rule in other words
(`non-sidechain|must be falsy|main-chain only|only main-chain|subagent turns are|are skipped|different context window`)
returns exactly one line: `doc:302`, "or changes how subagent turns are marked", inside the
format-drift trigger list. That names a drift risk; it asserts no polarity.

### Invariant 2 — payload fields match the shipped hook, both directions. **MET.**

Enumerated by command over **both** hook files, with two greps because the first is blind to a bare
membership test:

```
$ grep -nE "(\bdata\b|\bpayload\b)[^\n]*(\.get\(|in \(?data|in \(?payload)" scripts/hooks/spine_rail.py scripts/hooks/gauge_writer_hook.py
12 hits — spine_rail 174,179,324,413,422,427,536,616,654 · gauge_writer 230,563,604
$ grep -nE "\"[A-Za-z_]+\" (not )?in \(?(data|payload)" ...
adds spine_rail:177
```

**Five distinct keys:** `agent_id`, `cwd`, `session_id`, `tool_input`, `transcript_path`.

- **code → doc:** all five appear. `transcript_path`/`session_id`/`agent_id` are rows at
  `doc:259-263`; `cwd` and `tool_input` are named at `doc:273-275` as `spine_rail`'s own reads that
  never reach the gauge writer.
- **doc → code:** every field the document names is read at a line above. Nothing is claimed that the
  code does not read.

**Ruling on the dropped `agent_type` row: the departure is CORRECT.** `grep -n agent_type` over both
hook files exits 1 — no hook reads it. It appears only in `tests/fixtures/probe_payloads.jsonl`
(lines 2 and 3, both subagent payloads) and one assertion at `tests/test_spine_rail.py:171`. The
handoff's edit (b) asked for it as a field the hook reads, directly under a close criterion
forbidding exactly that; the implementer followed the code over the handoff, which is the right order
of authority. The document instead states the negative once, at `doc:275-276` — "No other payload
field is read by either hook — notably not `agent_type`, which the harness does send" — checked both
ways, so a later reader does not re-derive it.

### Invariant 3 — the stated binding key matches `spine_rail.binding_key`, both residuals named. **MET.**

`scripts/hooks/spine_rail.py:172-185` has four branches: `if not sid: return None` (175-176);
`if "agent_id" not in data: return sid` (177-178); unusable id → `None` (179-183); else the composite
(184-185). The document's table at `doc:429-432` has three rows because it merges the two `None`
branches into one — a faithful merge, not a loss. Bind-nothing is stated with its reason at
`doc:434-439`, and it matches the code's own rationale in substance: no fallback to the bare
`session_id`, because that would file the subagent's entry under the parent's key and silence the
parent's own gauge.

The gauge writer's **stricter** test is stated at `doc:440-443` and matches
`_AGENT_ID_ALLOWED = re.compile(r"\A[A-Za-z0-9_-]{1,64}\Z")` at `gauge_writer_hook.py:177`, applied in
`_binding_key` at `:230` **before** delegating — which is what the document says. The reject tokens
`#`, `/`, `\`, `..` match `_AGENT_ID_REJECT`.

Two further claims verified against code: `doc:445-447` ("`SessionStart` binds under the bare
`session_id` always") matches `spine_rail.py:647`'s own comment "Bare `sid`, NOT `binding_key(data)`
(#419)"; `doc:447-449` (`session_view` merges the bare key with every per-agent key) matches
`session_view` at `spine_rail.py:189-211`, whose prefix test uses `BINDING_KEY_SEP` so
`<sid>-something` is not treated as a child.

**Both residuals** are named side by side at `doc:461-488`. Residual 1 (an orchestrator holding
several spines under one bare key) is marked unchanged by #419. Residual 2 (the non-claiming subagent
that now writes nothing) carries the split the implementer made against the handoff's wording, and I
re-verified the basis myself this pass rather than carrying it forward:
`git show 4767782^:scripts/hooks/gauge_writer_hook.py` shows `resolve_gauge_path(project_dir,
data.get("session_id"))` and `compute_record(transcript_path)` — the **parent's** transcript. So the
pre-change write was the parent's own record, correctly filed where the bound spine was the parent's,
and misattributed only where the single bound spine belonged to a different top-level agent sharing
the `session_id`. The document states both halves. The bounded-loss claim is verified too:
`gauge_reader.py:28` resolves staleness from the record's own `observed_at`, never file mtime.

---

## The fifth-field question, and how I now rule on it

My BLOCK ruled `identity_resolution_ms` **inside invariant 1's spirit** — the document asserting
something the code does not do — because `git log -S identity_resolution_ms` returns exactly one
commit, `5491bd4`, this issue's own g2, which is precisely the causal class the handoff gives this
gate. **That ruling stands and the fix has landed at every one of the six sites.**

The rework's substance is right beyond the wording. The new section at `doc:45-75` states the field's
meaning against the code, not by inference: `identity_ms` accumulates across exactly two windows in
`handle_post_tool_use` — `_binding_key` at `:576-578` and `derive_subagent_transcript` at `:618-620` —
and the `resolve_gauge_path` binding-store read that sits between them is **not** counted, which is
what `doc:62-67` says. The 100 ms budget is real: `_IDENTITY_BUDGET_MS = 100.0` at
`tests/test_gauge_writer.py:1173`, asserted at `:1210` and again at `:1227`, and the test file pins the
dispatched key set at exactly five at `:1207-1208`.

---

## Scope, evidence and the suite

**Scope held.** Exactly three source files differ from `5491bd4`:
`docs/GAUGE_WRITER_HOOK.md` (+302/−83), `scripts/hooks/gauge_writer_hook.py` (34 lines,
comments/docstrings only), `tests/test_gauge_writer.py` (1 insertion, 1 deletion). Nothing under
`skills/`. The `skills/` exclusion stays **vacuous rather than satisfied** — no installed copy exists —
and the implementer says so himself, which is the honest reading.

**Comments-only, proved and shown red.** I wrote my own comparator rather than running the
implementer's: parse both sources with `ast`, strip the leading string `Expr` from every
Module/Class/Function body, compare `ast.dump`. `git show HEAD:scripts/hooks/gauge_writer_hook.py` vs
the working file → `IDENTICAL`, exit 0. I also read all four hunks: module docstring (17-27),
`find_latest_usage` docstring (300-311), `compute_record` docstring (355-365), one hash-comment block
above `UNCALIBRATED_FILENAME` (409-420). Nothing executable.

I then drove the guard red myself, three runs, each asserting the mutation applied before the guard
ran — because one red against one line is weaker than a red plus a control:

| run | mutation (in a scratchpad copy) | guard |
|---|---|---|
| RED 1 | `record["identity_resolution_ms"] = identity_ms` → `= 0.0` | `DIFFERENT`, exit 1 |
| RED 2 | `_AGENT_ID_ALLOWED` regex → `[A-Za-z0-9_.-]{1,128}` | `DIFFERENT`, exit 1 |
| CONTROL | `# A SIDECAR` → `# XX A SIDECAR` (comment text only) | `IDENTICAL`, exit 0 |

The control is what makes the reds mean something: the guard is not reporting "the bytes differ", it
is genuinely blind to comments and sensitive to code. The worktree was never mutated — the delivered
file still compares `IDENTICAL` to HEAD after all three runs. The AST shape is also the right one for
this repo: `CREW_CONTEXT.md` forbids comparing two files by raw working-tree bytes on Windows, and
this file carries the LF/CRLF warning, so a byte comparison would have been silently wrong.

**The Commander's fix-now in `tests/` — verified, and nothing else moved.**
`tests/test_gauge_writer.py:1001` changed from "…field table **is wrong about this today**), so the"
to "…field table **states both polarities**), so the" — word for word the wording applied to its twin
at `gauge_writer_hook.py:307`, which is right, since the two were a copied sentence. It is true against
the delivered document (`doc:291` does state both polarities), and the comment's real point survives:
line 1000 still records that every line of a subagent's own transcript is `isSidechain: true`
(measured), which is what the tests below it exercise. `git diff --numstat -- tests/` returns exactly
`1  1  tests/test_gauge_writer.py`; `git status --porcelain -- tests/` returns exactly
` M tests/test_gauge_writer.py` with zero untracked entries.

Both twins are gone by an independent sweep: my re-run reproduces 35 raw hits and 11 naming the
document, identical to the archive, but a targeted grep for any surviving
"`GAUGE_WRITER_HOOK.md` … is wrong / wrong about / out of date / outdated / stale" across `scripts/`
and `tests/` now **exits 1**, where the archived pre-fix run shows two. Of the nine remaining
pointers, I checked the two that assert something checkable and both still hold:
`install_constellation.py:535-545` pins `HOOK_MATCHER = "*"` and `HOOK_TIMEOUT = 10` "carried VERBATIM
from the snippet in docs/GAUGE_WRITER_HOOK.md", and the delivered doc still says matcher `*` and
timeout 10 at `:108-110` and `:156-157`; `test_install_constellation.py:1996`'s hand-wired
`${CLAUDE_PROJECT_DIR}` form is still documented at `doc:152-160`.

**Suite, run by me inside my own turn:**

```
$ cd C:/Programs/constellation-skills-wt/epic418-a-419 && python -m pytest tests -q
1667 passed, 2 skipped, 550 subtests passed in 484.11s (0:08:04)
exit=0
```

Exactly the pinned **1667 passed, 2 skipped**. `python`, never `py`. The unmoved count corroborates
the AST guard from a completely different direction.

**Skip-cause arithmetic recounted against `handle_post_tool_use`**, because `doc:317-323` asserts it:
three flagged (`ambiguous-binding` at `:597-602`, `no-usable-record` at `:641`,
`subagent-transcript-missing` at `:623`) and four silent (missing/unreadable `transcript_path` at
`:564`, `key is None` at `:579`, zero candidates at `:585`, plus the unwired hook, which is external to
the writer). Three and four is what the document says.

---

## Refactoring pass (Fowler)

Recorded at `.agent-work/issue-419-governor-identity/g3r2-review/FOWLER_PASS.json`;
`verify_fowler_pass.py` exits 0 (smells=12, flagged=`duplicated-code`, `shotgun-surgery`;
overridden=`large-class`, `comments-as-deodorant`; no rail exception — the pass was run, not skipped,
because the prose and comments **are** the deliverable here). Both flags are observations, neither
blocks; both overrides carry a named standard and a reason.

The one worth reading: the record's shape is now stated in roughly eight places across two files. The
rework applied the right move for prose — one authoritative section at `doc:45-75`, pointers
elsewhere — and says so explicitly. The residual is real but defensible: the two restatements that
stay verbatim (step 4, and the eyeball check) are the two a human reads mid-task, where a pointer
would cost the reader the fact at the moment they need it.

---

## Findings

### In scope — blockers

**None.**

### In scope — observations

1. `doc:66-68` pins the budget to "`tests/test_gauge_writer.py:1201`". That line is the test's `def`;
   the assert is `:1210` and the constant is `:1173`. Citing a test by its `def` line is fair, but per
   the inherited "pin a claim to the revision you read it at" rule a bare line number in prose is the
   citation form most likely to rot — naming the test function would not.
2. The `skills/` exclusion is vacuous, not satisfied. Unchanged from my first review, correctly
   reported by the implementer, and not something this gate can fix.

### Out of scope — triage candidates

**tc1 — `scripts/gauge_reader.py:24`, and this is the one I would rule in if asked.**
"The frozen gauge record has exactly these four fields — no `source`, no `window` (both cut as
YAGNI)." This is the **seventh** site of the class this gate removed, and after the rework it is the
**only** surviving four-field/frozen-record assertion anywhere in `docs/` or `scripts/`:

```
$ grep -rn -i -E "frozen[^.]{0,60}(gauge )?record|record[^.]{0,40}frozen" docs/ scripts/ --include=*.md --include=*.py
scripts/gauge_reader.py:24:# The frozen gauge record has exactly these four fields -- no `source`, no
```

False on the dispatched-agent path since `5491bd4`. Its "exactly" is the word that misleads most,
because the code directly beneath it does the opposite: `_parse_record` loops over `REQUIRED_FIELDS`
checking presence only (`:163-165`) and never rejects extras — which is precisely the property the
corrected document now cites this file for at `doc:58-60`. The implementer's enumeration could not
reach it because the sweep covered three files and this is a fourth; that is the authoring-side blast
radius `global-everyone.md` describes, one file further out than anyone looked.
`gauge_reader.py` is #181's read side and outside the granted scope, so this is a **ruling, not a
rework**. One-line fix if ruled in: *"The gauge record's four REQUIRED fields — no `source`, no
`window` (both cut as YAGNI). Extras are not rejected; #419 adds an optional `identity_resolution_ms`
on the dispatched-agent path."*

**tc2 — `scripts/hooks/gauge_writer_hook.py:543-556`.** `handle_post_tool_use`'s docstring still says
"Two of the skip causes are now POSITIVELY LOCALIZED (issue #271)" and "The other two causes stay
silent by design". Both counts are wrong as of `5491bd4`: the code now writes three localized reasons
and has three in-code silent causes. `git log -L 540,560:scripts/hooks/gauge_writer_hook.py` confirms
`5491bd4` added both the third localized cause and the third silent one while leaving this docstring
untouched. This one sits **inside** the file whose comments this gate already had scope to edit, so a
bounded fix-now is cheap if the Commander wants it. Worth noting where it leaves things: the delivered
**document** gets this right (3 and 4, recounted by me above), so the document is now more accurate
than the module it documents — the inverse of the defect this gate existed to remove.

**tc3 — no mechanical link ties the record's field count across its assertion sites.** Every change to
it is shotgun surgery and has now missed sites twice. Cheap fix: a test that imports `REQUIRED_FIELDS`
from `scripts/gauge_reader.py` and asserts `docs/GAUGE_WRITER_HOOK.md`'s field table marks exactly
those four as required. That converts a close criterion both the implementer and I derived by hand
into a check that fails on the next drift. The implementer reached the same conclusion from the
authoring side.

**Carried forward, unchanged and still out of scope:** the format-drift paragraph at `doc:299-307`
still says drift means "the writer silently stops producing records", wrong since **#271** rather than
#419 (that case now writes a `no-usable-record` sidecar on a single resolved candidate); and the
silent-cause bullet at `doc:380-383` names two triggers for a `None` binding key and omits the
falsy-`session_id` trigger, which the binding table at `doc:432` does state.

### Why I am not blocking on tc1/tc2

My BLOCK ruled the fifth field in on the test "the document asserts something the code does not do".
tc2 meets that test literally, so the line I am drawing needs stating rather than assuming. Two
reasons it falls the other side. First, **consequence**: the fifth-field defect sat in the gate's own
subject file *and* in the eyeball-check section, whose whole function is to tell a human whether a
real `gauge.json` is correct — it would have made a person judge a correct subagent gauge wrong.
tc1 and tc2 are maintainer-facing counts with no operational consequence. Second, **fixability inside
the gate**: tc1's fix site is outside the granted scope entirely, so a BLOCK would not produce a
rework, it would produce a request for a scope ruling — which is what a triage candidate already is,
minus the churn. All three frozen invariants are the gate, and all three are met against the code.

---

## Workflow Feedback

- **The handoff should have named the sweep's file set, not just the sweep.** Both the rework handoff
  and my own BLOCK framed the enumeration over "the doc and both hook files". That framing is what
  hid `gauge_reader.py:24` from everyone, twice. The document itself *points at* `gauge_reader.py` as
  the authority for "validates the four, does not reject extras" — so the file was one hop from the
  claim being edited and still outside the sweep. The generalizable fix is small: **when a handoff
  asks for an enumeration, it should say what the enumeration ranges over, and the default range
  should be "every file the changed claim is cited in or cited from", not a hand-listed set.** An
  anchor list of *files* fails the same way an anchor list of *lines* does, one level up — which is
  exactly the lesson the rework handoff already learned at the line level.
- **A re-review handoff should say where to put the new survey.** Mine said to overwrite
  `g3-REVIEW_RESULT.md` but said nothing about the survey, and the previous survey at
  `g3-review/review.json` is a consolidated, released engine artifact holding the BLOCK's provenance.
  I created a fresh survey at `g3r2-review/` rather than force-claiming the old one, because
  reclaiming would have destroyed the record of the verdict being superseded. That was a judgment I
  had to make on my own; the convention is worth stating once in the handoff template.
- **The engine's `advance` verb does not exist for a `survey`** (`REFUSED: advance is for gated
  checklists; use record`), but the reviewer skill tells the Reviewer to "record pass or fail … then
  `advance` that check" and to "run the engine's final `advance`/`consolidate`". A reviewer following
  the skill literally hits a refusal on their first check and again at the end. `record` alone
  advances a survey and `consolidate` closes it. Worth correcting in the skill text — it is a
  one-word fix and it currently reads as an error on a correct run.
- **The one thing this gate proves is worth lifting into the templates**: the AST-equality-with-
  docstrings-stripped check. It converts "comments only, not one executable line" from the most-likely-
  violated promise of a docs-adjacent gate into a mechanical check, it is trivially demonstrable red,
  and adding a comment-only **control** run (which I did and the implementer did not) is what proves
  it is measuring the right thing rather than just "bytes differ". The implementer independently asked
  for the same lift.
- **What made this review cheap**: the implementer stated a count on every sweep and archived the
  commands verbatim, so reproducing was mechanical rather than reconstructive. The one genuinely
  expensive derivation was rebuilding his "13 hits" base, which no longer exists in git — a BEFORE
  count taken against an uncommitted working tree is unreproducible by construction. Archiving the
  *file* alongside the count, not just the count, would close that.

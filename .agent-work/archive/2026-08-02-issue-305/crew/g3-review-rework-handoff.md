# REVIEWER HANDOFF — g3-review, ATTEMPT 2 (post-rework)

**Issue #305, epic #298. Worktree `C:/Programs/constellation-skills-wt/e298-305`, branch
`epic-298/305`. NEVER touch the main checkout at `C:/Programs/constellation-skills` — it
holds uncommitted human WIP and a branch checkout there destroyed a live file once already
this epic.**

**Interpreter: `python` (3.14.3, has pytest). `py` is 3.12.13 and has NO pytest — under the
PowerShell tool it silently no-ops and reads as a green suite.**

---

## Why you exist

Attempt 1 of this gate was reviewed and returned `APPROVE-WITH-FOLLOWUPS`, finding the
control real on its central claim but **two of its premise guards unable to fail**. The
commander then reopened its own gate rather than integrating. Rework landed at `9644fb3`;
I (commander-305e) verified it and landed one further fix at `283175b`. The gate was
cascade-reset, so you are the review of record for the whole of g3.

**Read first:** `.agent-work/issue-305/crew/g3-review-result.md` (attempt 1 — excellent,
and its method notes are reusable), `.agent-work/issue-305/crew/g3-implement-rework-result.md`,
and `.agent-work/issue-305/notes-1.md` (my own verification).

**Diff under review:** `git diff 3f787a3..HEAD` — exactly one non-`.agent-work` path,
`tests/test_episode_negative_control.py`.

---

## YOUR PRIMARY JOB

Try to make the negative control **pass while testing nothing**. The gate imperative names
three attacks. Attempt 1 ran them; **re-run A1 and A2 anyway** — they are the core
falsifiability and they are cheap — and treat A3 as changed ground, because FIX 3 was
written specifically to answer it.

**Per-attack success criteria, because attempt 1 said their absence cost it real time —
name the assertion you expect to see, and if you see a different one, that is a finding:**

| # | attack | what must happen | the assertion that should say so |
|---|---|---|---|
| **A1** | composer -> hardcoded constants | RED | `compare_fields` returns **all ten field names** in `test_claimed_parent_topology_...` |
| **A2** | delete the ground-truth tally | RED | topology + seam tests + R1–R4 red; the named fields, not a bare non-zero exit |
| **A3** | declared context refs -> missing files | **must not read as success** | `test_a3_a_null_manifest_does_not_read_as_success`: rows present in declaration order with `rev: null`, and `compare_manifest_rows` naming **every** declared path. `context-manifest-ref` staying *correct* is expected and is NOT the failure — it is a byte-pin over the manifest's own bytes |

**Governing instruction where attempt 1 found a contradiction, resolved:** the earlier
handoff pre-committed to BLOCK on any green named attack while also sanctioning
`APPROVE-WITH-FOLLOWUPS`. **Which governs, stated now:** BLOCK if an attack scores green
**and that green means a conclusion is unsupported**. A green whose meaning is "this field
is out of scope for this attack" is a finding to report, not a block. You judge; say which
you concluded and why. Do not round either direction.

---

## Mutations already spent — go find a NEW one

Attempt 1 called this table the most valuable thing in its handoff. It is now long. **A
repeat of anything here is not evidence.**

| by | mutation | outcome |
|---|---|---|
| impl | R1–R4 in-suite red-proofs; M-C constant sha1; M-D; M-E | caught |
| rev 1 | A1 constants; A2 delete tally | RED |
| rev 1 | A3 all-null manifest | green — answered by FIX 3 |
| rev 1 | **M1** `advance --why <prose>` + `attest --note <prose>` | **was NOT caught → fixed** |
| rev 1 | **M5** oracle reads tallies out of `compose()` | **was NOT caught → fixed** |
| rev 1 | M2 dirname-for-work_id; M3 `items[-1]`; M6 dirwalk project; M8 `out[:1]` | not caught, benign/known |
| rev 1 | M4 claim the child; M7 unclaim the parent | caught |
| impl rework | M5a composer call; M5b snapshot read | RED |
| **me** | **V1** M1's shape vs the shipped file | RED, 44 violations |
| **me** | **V2** `attest --evidence "ev-1"` — text-bearing, absent from `AGENT_TEXT_FLAGS` | RED, 8 violations, closed-world arm only |
| **me** | **V3** oracle calls `episode_capture.reopen_total`, `source` prose untouched | RED |
| **me** | **V4** role constant -> a hand-written sentence | **green → fixed at `283175b`** |
| **me** | **V5** harness composes `--claimed-by` at issue time | pre-fix PASSES, post-fix FAILS |

**Softest surfaces I have not attacked, in my honest order:** `artifact-ref` still has only
a single-element case (attempt 1's F4 — `out[:1]` passes, so the multi-element constraint is
unmet); `_flag_pairs` mis-reading a flag value beginning with `--`; the `advances >= 8`
non-vacuity floor when the real count is 14; and whether the AST layer (b) can be evaded by
an indirection the patch layer (a) also misses.

---

## The specific thing I changed, and what I want attacked about it

`283175b` widened the argv census: `--claimed-by` now counts as agent-supplied text,
`PARENT_ROLE` is a module constant, the census asserts **exactly two** declared constants,
and the docstring was corrected.

**The claim now in writing — attack it:** *the control hands the engine exactly two
agent-supplied strings, both fixed constants: `claim --claimed-by <role>`, which **is** the
`role` mechanical field by definition, and `reopen --reason "control"`, which feeds no
mechanical field.*

I deliberately did **not** make the guard fire when the role string "looks like prose" —
`role` must be *some* supplied string, so that would be unfalsifiable theatre. **If you think
that reasoning is wrong, say so plainly.** And check the census for a *third* blind spot the
way I found the second: enumerate every flag the engine accepts, and ask which carry
agent-composed strings that `AGENT_TEXT_FLAGS` still does not name.

---

## Method requirements — these are where this epic keeps drawing blood

1. **Assert the SPECIFIC assertion, never a non-zero exit.** A wrapper mapping any non-zero
   to red also reports red for an import error or a collection failure.
2. **Prove every mutation is live before you trust its colour.** For a *file* mutation, blob
   OID change. For an *in-memory* mutation, print the mutated attribute from **both** the
   pytest process and a spawned subprocess — the engine runs as a **subprocess** here, so an
   in-process `monkeypatch` cannot reach the seam.
3. **#319, and it bit me three times in one session:** the worktree file is **CRLF on all
   1119 lines**; `git show HEAD:<path>` returns **LF**. A pattern built for one base silently
   matches **zero** sites in the other and reads as "mutation applied, still green".
   `git hash-object` compares true across that boundary because its clean filter normalises —
   which is exactly why blob OID is the instrument and raw bytes are not.
4. **Put your restore in a `finally:`.** Two of my scripts died before restoring — one on a
   cp1252 encode error printing pytest output, one on a broken pipe from `| head` — each
   leaving the tree mutated. OID-check the tree after **every** battery.
5. **Assert against the behaviour, never against text that describes it** (Admiral doctrine,
   this run). Docstrings, `description=` fields and comments are hand-authored and nothing
   checks them against what runs. **This applies to your own review evidence too.**
6. Verify the synthetic consolidation was genuinely discarded **by blob OID or normalized
   content**, not by anyone's say-so, and assert `episodes/active/` non-emptiness **first** so
   the check cannot pass vacuously. Use `--untracked-files=all`.

## Baseline

`python -m pytest -q` -> **1487 passed, 2 skipped, 472 subtests** (I measured it twice).
Derive it yourself; do not inherit it.

## Verdict

`APPROVE`, `APPROVE-WITH-FOLLOWUPS`, or `BLOCK`. **`APPROVE-WITH-FOLLOWUPS` is sanctioned and
is not a soft BLOCK — do not round it in either direction, and never fabricate an `APPROVE`.**
Write your result to `.agent-work/issue-305/crew/g3-review-rework-result.md`.

Include: the attacks you ran and their exact assertion text; anything you could not verify;
scope drift; and **Workflow Feedback, blunt** — attempt 1's feedback changed this handoff and
I want the same from you.

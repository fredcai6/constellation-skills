# Review Result — issue-304 gate g1, re-review after rework

Status values follow `skills/workbench/references/status-model.md`.
Supersedes `.agent-work/issue-304/crew-handoffs/g1-review-result.md` (BLOCK).

## Assigned Gate
`issue-304 g1 — resolver, receipt, reported degraded mode` (re-review)

## Result
`APPROVE`

All three send-backs are fixed, and I verified each by execution rather than by reading the report.
The two falsifiability holes I found last pass are both closed. One minor mutation survives; it is
filed as triage, not a blocker, for reasons given below.

Survey driven end to end: `.agent-work/issue-304/g1-review-2/review.json`, session `rev2-g1-304`,
eight items, consolidated `verdict=APPROVE`, 2 triage candidates. Fowler record:
`.agent-work/issue-304/g1-review-2/fowler-pass.json` (rail exit 0).

---

## Answering the four things you asked for

### 1. Re-apply M4 — **it now dies**

Same mutation, character for character, that survived the first review:

```
MUTATION: M4 (re-applied verbatim): unmapped_declared `not any(filler)` -> `not all(filler)`
  applied: ORIGINAL.count(old)=1 mutated.count(old)=0 count(new) 0 -> 1
  source differs from original: True
  FLOOR exit=1  passed=50  failed_nodes=4
  >>> KILLED. <<<
      - tests/test_map_orient.py::PartialFillMatrix::test_one_filler_poisons_a_multi_element_unmapped_list
      - tests/test_map_orient.py::ContractShape::test_self_test_floor_passes

SUBFAILED(unmapped=['none', 'src/engine internals were never read'])
SUBFAILED(unmapped=['src/engine internals were never read', 'n/a'])
SUBFAILED(unmapped=['src/engine internals were never read', '', 'src/engine internals were never read'])
4 failed, 50 passed, 29 subtests passed in 9.13s
```

Killed by the right test, and the *individual* multi-element subtests fail — which is the precise
condition that makes `any` and `all` diverge. Both layers grew the case (`test_self_test_floor_passes`
failing means `self_test()` gained it too, not just the floor). Semantically earned, confirmed
behaviorally:

```
### SHIPPED MUTATION 4: unmapped = ["a real thing", "n/a"]
  ORIGINAL -> 'DEGRADED-NO-MAP' exit=10
  MUTANT   -> 'DEGRADED-NO-MAP' exit=0     <-- the filler discharges the record
```

### 2. A NEW mutation against the B1 fix — **killed**

The fix does two things: `pin_substitutes` emits `None` instead of the `"unreadable"` sentinel, and
`is_content_hash` requires a real sha256 shape. So the interesting attack is not the old sentinel —
it is a **well-formed forgery**: pin an unreadable path with the genuine sha256 of *empty content*
(`e3b0c442…`), which is a perfectly valid 64-char hex digest and sails through any
"is it shaped like a hash" check.

```
MUTATION: M5 (reviewer, NEW): unreadable substitute pinned with sha256 of empty content -- a VALID-SHAPED fake
  subs: '"content_hash": sha256_of(path),'
     -> '"content_hash": sha256_of(path) or hashlib.sha256(b"").hexdigest(),'
  applied: ORIGINAL.count(old)=1 mutated.count(old)=0 count(new) 0 -> 1
  FLOOR exit=1  passed=48  failed_nodes=3
  >>> KILLED. <<<
      - UnreadableSubstitute::test_a_nonexistent_substitute_path_refuses
      - UnreadableSubstitute::test_an_unreadable_substitute_is_not_pinned_with_a_sentinel
      - UnreadableSubstitute::test_the_refusal_names_the_offending_substitute
```

Killed by exactly the three tests that own the property, for the right reason (the third fails on
`'THIS_FILE_DOES_NOT_EXIST' not found in ''` — the refusal message vanished because there was no
refusal). **The hole is pinned against forgery, not merely against the literal string `"unreadable"`.**
That is the answer to "have we reopened the hole while believing we closed it": no.

### 3. Count-delta and the non-matching-anchor refusal — **both still hold** after the floor grew

```
### MUTATIONS now shipped: 5 (was 3)
### count-delta still load-bearing?
  substitutions whose replacement PRE-EXISTS in the module: 2
    - UNRESOLVABLE-ROOT collapse: '        return MODE_DEGRADED_NO_MAP\n' pre-exists 1x
    - UNRESOLVABLE-ROOT collapse: '    return EXIT_OK\n'                  pre-exists 2x

### harness still refuses a non-matching anchor loudly?
  renamed predicate : HarnessError -> HARNESS ERROR: ... occurred 0 time(s)
  renamed hash fn   : HarnessError -> HARNESS ERROR: ... occurred 0 time(s)
  stale B1 anchor   : HarnessError -> HARNESS ERROR: ... occurred 0 time(s)

### no-op (old==new) still caught at STEP 1?
  refused. 'HARNESS ERROR' present: True; 'a red run would be a lie' present: True
```

`assertIn` would still be vacuous on two substitutions, so the count delta is still doing real work.
The third anchor probe is the one worth noting: I fed it the **pre-fix B1 anchor**
(`"content_hash": sha256_of(path) or "unreadable",`), which no longer exists after the rework. The
harness refused loudly instead of crediting a kill — that is exactly the rot-detection the
applied-assertion exists for, demonstrated against a real change rather than a synthetic one.

I also re-verified the two **newly shipped** mutations are semantically earned rather than collateral:

```
### SHIPPED MUTATION 5 (is_content_hash -> bool(value.strip())): hand-written 'unreadable' sentinel
  ORIGINAL -> verify exit=10
  MUTANT   -> verify exit=0      <-- the sentinel passes as a hash-pin again
```

Note for the record: mutation 5 weakens the **hand-written-receipt** arm, not the tool-emitted one —
the `isinstance(value, str)` guard still rejects `None`, so a nonexistent path still refuses under it.
That is fine (it is a real property, really pinned), and the tool-emitted arm is covered by my M5
above. All five shipped mutations have now been behaviorally verified across the two passes.

### 4. No 3.13+-only API crept in

Scanned all five files for `Path.read_text(newline=)`, `itertools.batched`, `typing.override`,
`copy.replace`, `datetime.UTC`, `asyncio.TaskGroup`, `glob(root_dir=)`, `os.walk` → **CLEAN**. The
module still uses `datetime.now(timezone.utc)` (3.2+) and `open(..., encoding='utf-8', newline='\n')`.
Local 3.14.3 vs CI 3.12 is safe; no repeat of PR #320.

---

## On your warning that I should not trust "appears fixed"

Taken, and it changed what I did. I re-ran everything from scratch rather than confirming your
numbers, including the full suite to completion:

```
$ python -m pytest tests/test_map_orient.py tests/test_mutation_floor.py tests/test_init_work_area.py -q
91 passed, 38 subtests passed in 80.18s

$ python scripts/map_orient.py --self-test
self-test OK    (exit 0)

$ python -m pytest tests/ -q
1470 passed, 2 skipped, 448 subtests passed in 133.33s    (exit 0)
```

The full suite ran to completion with **no collection error**. Your "green on two independent polls"
now has a completed run behind it.

**B1 refuses for the right reason — checked, because you asked, and it is not "refuses everything":**

```
### A. NEGATIVE: substitute that does not exist
  orient  -> 'DEGRADED-NO-MAP' exit=10
  stderr  -> substitutes[0] 'docs/NOPE.md' is not hash-pinned (content_hash=None)
             -- an unreadable or nonexistent substitute cannot discharge the record
  receipt -> substitutes=[{'path': 'docs/NOPE.md', 'content_hash': None}]   (null, NOT a sentinel)
  verify  -> exit=10
  names the offending path: True; unmapped/escalation NOT blamed: True

### B. POSITIVE CONTROL: substitute that really exists
  orient exit=0   verify exit=0
  content_hash == sha256 of the actual bytes on disk: True

### C. one real + one missing substitute
  exit=10, blames ONLY the missing one
```

And the positive control is **load-bearing**, not decorative — a "refuse everything" fix would have
been caught:

```
MUTATION: P1: is_content_hash always False (a 'refuse everything' fix)
  FLOOR exit=1  passed=44  failed_nodes=7  >>> KILLED. <<<
      - UnreadableSubstitute::test_one_real_substitute_still_discharges
      - PartialFillMatrix::test_positive_control_a_complete_record_passes
      - PartialFillMatrix::test_a_multi_element_unmapped_list_of_real_entries_passes
      - VerifyOrientation::test_orient_with_a_full_declaration_discharges_the_degraded_record
      ...
```

One correction to my own working: an intermediate probe of mine printed
`hash is the REAL sha256 of the file content: False`. That was **my probe's bug**, not the code's — I
had written the fixture with `Path.write_text`, which translates `\n` to CRLF on Windows, so I was
comparing against the hash of the wrong bytes. Re-checked against the actual bytes on disk: the pin
matches exactly. Flagging it because a reader of my transcript would otherwise see a scary line.

---

## One surviving mutation — reported plainly, filed as triage, not a blocker

```
MUTATION: P2: CONTENT_HASH_RE {64} -> {64,} (over-long digest accepted)
  applied: ORIGINAL.count(old)=1 mutated.count(old)=0 count(new) 0 -> 1
  FLOOR exit=0  passed=51  failed_nodes=0
  >>> MUTANT SURVIVED -- the floor did NOT catch this. <<<
```

Both hand-maintained bad-hash tuples test the **lower** bound (`"a" * 63`) and neither tests an
over-long one, so under the mutant a 128-char sha512 would pass as a sha256 pin.

**Why this is not a blocker**, unlike B1 was:

- `pin_substitutes` only ever emits `hashlib.sha256(...).hexdigest()` — exactly 64 chars — so the
  tool's own output is unchanged. This is reachable only via a hand-written receipt.
- It does **not** reopen the silent-degradation hole. An unreadable path still pins `None`, and
  `is_content_hash`'s `isinstance(value, str)` guard rejects `None` regardless of the quantifier. I
  confirmed that directly rather than reasoning about it.
- An over-long digest is a shape violation that g2's comparison would fail on anyway — it cannot
  match a recomputed sha256.
- Fix is one token in each of two existing tuples (`"a" * 128`), at `scripts/map_orient.py:999` and
  `tests/test_map_orient.py:513`.

This is a coverage gap at a boundary, not a reachable false-satisfied. Filed as `tc1`.

## Blockers

- `none` — the B1 blocker is fixed, verified behaviorally in both directions, and pinned against a
  well-formed forgery by a mutation of my own devising.

## Handoff compliance

Every close criterion re-verified this pass: required suite and self-test green; exit band `10-13`
still provably clear of `1`/`2`/`126`/`127`; RESOLVED still requires citable content; `UNRESOLVABLE-ROOT`
still distinguished from `DEGRADED-NO-MAP` by a positive proof; three-way discharge intact — and now
the *quality* arm of that discharge (fillers, hash-pins) is pinned in both the single- and
multi-element cases, which is what was missing.

## Scope drift

None. The rework is confined to the substitute-readability path (`CONTENT_HASH_RE`,
`is_content_hash`, `substitute_problems`, `substitutes_declared`, `pin_substitutes`) plus new test
arms and two added mutations. No `verify-frame`, no template wiring, no prose deletion, #341/#342
untouched, `checklist_engine.py` untouched. `tc1` from my first review (`--receipt-dir`) correctly
left alone as out of scope. `notes-304.md` shows modified but has an empty diff (line-endings) and is
commander-owned, not implementer output.

## Evidence verdict

Sound. Every figure re-run from scratch. The previously-false cleanup claim (B3) is now true —
`.agent-work/probe/` is gone.

## Code/doc quality

The fix is better than the minimum. Replacing the sentinel with `None` **and** adding a shape check is
belt-and-braces: either alone would have closed my exact reproduction, but only both together survive
the valid-shaped-forgery attack. `substitutes_declared` reducing to `return not substitute_problems(receipt)`
removes a duplicated rule rather than adding one. The docstrings explain *why* the sentinel was
dangerous, which is the kind of comment that stops a future author from reintroducing it.

Fowler pass: 12 smells, 5 flagged, 3 overridden with logged standards, rail exit 0. Nothing blocking.

## Map impact verdict

Unchanged from the first pass and still accurate. One detail for g2: `content_hash` is now
**nullable**, and g2 must read `null` as "not pinned" rather than as a missing field. It is documented
in `pin_substitutes`' docstring.

## Reconciliation check

No divergence. The rework tightens one predicate inside an existing module; no new structural surface.

## Out-of-scope observations

- **`tc1` — pin the hash-shape check's upper bound.** The P2 survivor above; one token in two tuples.
- **`tc2` — the module docstring's "Honest limits" is now stale.** It still says the module "can only
  check the three fields are present and are not filler", which understates the new sha256 shape
  validation and omits the unreadable-substitute case entirely. I raised this in the first pass and it
  did not get picked up. It matters more than a normal doc nit because that section is the module's
  own statement of what it does and does not guarantee.
- **The bad-hash vocabulary is duplicated and already drifting** — `map_orient.py:999` has
  `(None, "unreadable", "", "n/a", "a"*63, "z"*64, 12345)` while `test_map_orient.py:513` has
  `("unreadable", "n/a", "", None, "a"*63, "Z"*64)`: different case, and only `self_test` carries the
  non-string. This is the same drift I flagged last pass on the filler lists, and it is *why* P2
  survived — a single missing case in two hand-maintained tuples.
- **`pin_substitutes`' untested absolute-path branch survived the rework** (`map_orient.py:770,773`).
  I flagged it partly because it was the function that produced the B1 sentinel; the sentinel is gone
  but the unexercised branch remains, and `--substitute` is still documented as repo-relative.
- **Carried forward, unchanged:** the harness's kill criterion is still class-level rather than
  reason-level (my `tc2` from the first review). Not re-litigated — but note the mitigation is
  currently *me*: I have now behaviorally verified all five shipped mutations by hand across two
  passes, and nothing in the harness does that automatically.

## Workflow Feedback

- **Handoff gaps:** Your re-review brief was materially better than a generic one — naming the exact
  claim to distrust ("a fix that refuses everything would also produce that first line") is what made
  me write the P1 always-False mutation, which I would not otherwise have thought to run. The one gap:
  it asked for "ONE NEW mutation" against the B1 fix but gave no guidance on what counts as a fair
  one. I chose the valid-shaped forgery because it defeats the obvious weak fix; a weaker reviewer
  could have satisfied the letter of the instruction by re-running something the shipped floor already
  covers and reporting a kill. "Devise one that would survive a *plausible but insufficient* fix"
  would close that.
- **Context rediscovered:** That a `survey` checklist rejects `advance` — I hit this in the first pass
  too, and the skill's own wording ("run the engine's final `advance`/`consolidate`") still points at
  gated-checklist vocabulary that does not apply to the artifact this skill creates. Also
  `flag-candidate` requires `--from` and `--statement`, documented nowhere in the skill.
- **Instructions improvised around:** Same as last pass, and it paid off twice — the reviewer skill
  has no vocabulary for *executing* anything, so I reused my scratchpad driver that imports
  `tests/test_mutation_floor.py` and drives its own `apply_mutation` / `run_floor`. Because `ORIGINAL`
  is re-read at import, the identical driver picked up the reworked module with no edits, which made
  the M4 retest a genuine like-for-like comparison rather than a re-implementation. If executed
  falsifiability becomes a standing reviewer duty, that driver belongs in the skill.
- **What would have made this easier:** One concrete change — a convention that when a reviewer's
  mutation survives, the rework adds it to `MUTATIONS` in `test_mutation_floor.py` rather than only
  adding a test. The implementer did exactly that here (3 → 5, my M4 among them), which is why the
  retest was trivial to run and trustworthy. Making it explicit in the handoff would make the pattern
  reliable instead of fortunate.

## Return status
`complete`

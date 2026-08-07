# Review Result 2 — issue-304 gate g4, scoped confirmation of `62d7e3a`

**Written as a NEW file, `g4-review-result-2.md`** (not appended), matching the `-2` precedent already
in this issue's `crew-handoffs/`. `g4-review-result.md` is unchanged and its **APPROVE still stands**.

## Scope of this pass
Only `62d7e3a`, only the four questions asked. Nothing already cleared was re-verified. Out of scope
and not touched: g1–g3, the full suite, #341, #342, #344, #363, #364.

## Result
`APPROVE`

The product-tree change is **exactly one line**, `tests/` is untouched, and the harness repair is
better than what was asked for.

```
 scripts/map_orient.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

-            note = "UNVERIFIED -- declared by the agent, not corroborated by the filesystem"
+            note = "UNVERIFIED -- declared by the agent, not in the fixed fallback set"
```

---

## Q1 — Does the new wording say what the classification means, without a mirrored overclaim?

**Yes for every state the tool can actually produce. No new overclaim, and specifically no
under-claim implying a substitute is more trustworthy than it is.** The line still leads with
`[agent-declared]` and `UNVERIFIED`, so the trust signal is unchanged; only the *reason* was corrected.

I did find one precise narrowing, and I checked it by execution rather than argument, because
`agent-declared` has **two** causes, not one. From `classify_substitute`'s own contract:

```
classify_substitute(rel_path, exists) truth table:
  docs/agents/ORCHESTRATOR_CONTEXT.md    exists=True  -> agent-declared
  README.md                              exists=True  -> known-fallback
  README.md                              exists=False -> agent-declared
```
`known-fallback` requires **membership AND presence**, so `agent-declared` means
*not-in-set* **OR** *in-set-but-absent*. The new sentence asserts only the first disjunct. Rendered
side by side at HEAD:

```
CASE A: present on disk, NOT in the fixed fallback set
  substitute: docs/agents/ORCHESTRATOR_CONTEXT.md [agent-declared] -- UNVERIFIED -- declared by the agent, not in the fixed fallback set

CASE B: IS in the fixed fallback set, but ABSENT on disk
  substitute: README.md [agent-declared] -- UNVERIFIED -- declared by the agent, not in the fixed fallback set

control: in the set AND present
  substitute: README.md [known-fallback] -- found in the fixed fallback set and present on disk
```
Case A is the reported defect, now **fixed and accurate**. Case B renders a sentence that is false
(`readme.md` *is* in `KNOWN_FALLBACK_SET`).

**But case B is not reachable by the tool, and that is what settles the severity.** `orient` refuses
an absent substitute before it can ever discharge — I ran it against a scratch root with no
`README.md`:

```
### orient exit: 10
DEGRADED-NO-MAP
degraded and NOT discharged -- still owed:
  - substitutes (what you read INSTEAD of a map, each hash-pinned)
  -     substitutes[0] 'README.md' is not hash-pinned (content_hash=None) -- an unreadable or nonexistent substitute cannot discharge the record
```
The receipt `orient` wrote carries `{'path': 'README.md', 'content_hash': None, 'source':
'agent-declared'}` — the absence is reported **accurately and specifically**, by a different and
better message than the one under review. So every substitute that reaches the report line was
hash-pinned, hence readable, hence present; under that enforced invariant the new sentence is
**exactly true**.

The only way to reach case B is a **hand-forged receipt** carrying a syntactically valid but
fabricated sha256 for an absent file. I built one to be sure rather than assume:

```
hand-forged receipt written (valid-shaped sha256 for an ABSENT README.md)
### exit: 0
substitute: README.md [agent-declared] -- UNVERIFIED -- declared by the agent, not in the fixed fallback set
```
Even there the reader is told `agent-declared` and `UNVERIFIED`, so **trustworthiness is not
overstated** — the mirrored defect you asked me to look for does not occur. Receipt forgery is
outside this contract's threat model (it targets honest-but-lazy orientation, not an adversary).

**Verdict: not a blocker, no fix requested.** Recording it only so nobody later reuses
`render_verify_report` somewhere the hash-pinned invariant does not hold. If you ever want the
sentence true unconditionally, the exact complement of the positive branch is *"not a verified
present member of the fixed fallback set"* — strictly optional, and I am **not** asking for it.

## Q2 — Does `UNVERIFIED` still pin, and are the classification logic and mutation coverage untouched?

**Yes, all three.** `tests/` is not touched by `62d7e3a` at all — the commit's only non-`.agent-work`
file is the one line above.

The pin, at `tests/test_map_orient.py:1070-1075`, asserts **both** labels and survives verbatim:
```python
    def test_an_agent_declared_substitute_is_REPORTED_as_unverified(self):
        proc = self.degraded_with(
            {"docs/notes/whatever.md": "my notes\n"}, "docs/notes/whatever.md"
        )
        self.assertIn(mo.LABEL_AGENT_DECLARED, proc.stdout)
        self.assertIn("UNVERIFIED", proc.stdout)
```
`classify_substitute`, `substitute_label`, `KNOWN_FALLBACK_SET`, `LABEL_KNOWN_FALLBACK` and
`LABEL_AGENT_DECLARED` are all byte-identical — `git diff 5787a8e..HEAD -- scripts/map_orient.py`
yields exactly two changed lines, the one string.

**Mutation coverage still APPLIES, not merely still exists** — this is the part worth checking, since
a moved anchor would silently retire a mutation. The floor raises `HarnessError` on any anchor that
does not match exactly once, so a green run proves every anchor still binds:
```
14 passed, 11 subtests passed in 136.29s (0:02:16)   ### exit: 0
```
Both label mutations anchor on lines the fix did not touch (`return entry["source"] / return
LABEL_AGENT_DECLARED`, and the `lines.append(f"substitute: ...")` call), so the provenance-reporting
mutations remain live.

## Q3 — `--self-test` and `tests/test_map_orient.py`

```
$ python scripts/map_orient.py --self-test
self-test OK
### self-test exit: 0
```
```
$ python -m pytest tests/test_map_orient.py -q
87 passed, 39 subtests passed in 11.76s
### exit: 0
```
Both green. (`python -m pytest` throughout, never `py -m pytest`.)

## Q4 — Did the harness stop substring-scanning?

**Yes — it now reads the structured field, and the implementer went one better than "fix it if it's
one line."** `g4_assert_discharged.py`:

```python
+def receipt_is_degraded(receipt: dict) -> bool:
+    """Read the receipt's STRUCTURED verdict field, never the document as a string.
+    ...``build_receipt`` writes the verdict to ``mode``; that field, and only that field, is the oracle.
+    """
+    return str(receipt.get("mode", "")).upper().startswith("DEGRADED")

-verdict = receipt.get("verdict") or receipt.get("status") or ""
-degraded = "DEGRADED" in json.dumps(receipt).upper()
+verdict = receipt.get("mode") or ""
+degraded = receipt_is_degraded(receipt)
```
`mode` is confirmed as the real field: `build_receipt` returns `"mode": orientation.mode`
(`map_orient.py:876`). The dead `receipt.get("verdict") or receipt.get("status")` fallback chain —
which is what let the structured value get fetched and discarded in the first place — is gone.

It also recorded the weakness as a **named, executable** one rather than only a note:
`g4_assert_harness_discriminates.py` pins **all three directions**, including that the *old* predicate
still reproduces the defect, so the repair itself cannot rot into a check that only ever returns the
answer we want:

```
OLD substring predicate on a RESOLVED receipt: True   <- the defect
NEW structured predicate on the same receipt:  False   <- the repair
NEW structured predicate on a DEGRADED receipt: True  <- no over-correction
HARNESS-PREDICATE-DISCRIMINATES
### exit: 0
```
That is the "can this check fail?" discipline applied to the fix for a check that could not fail —
the right shape, and it answers the question in the direction that matters. Its
`if not old_on_resolved: problems.append("the old predicate no longer reproduces the defect -- this
check has lost its point")` guard is the detail that makes it durable.

---

## Blockers
**NONE.**

## Findings

- **MINOR / observation, no fix requested:** `agent-declared` is a disjunction
  (*not-in-set* OR *in-set-but-absent*) and the new sentence names only the first disjunct. Not
  reachable through `orient`, which refuses an unpinned substitute with a more accurate message; only
  reachable via a forged receipt, where `UNVERIFIED` still warns the reader. Recorded so the line is
  not reused outside the hash-pinned invariant. Details and the executed evidence under Q1.

## Confirmation of the fix against your reasoning
The wording now states the classification's actual meaning, the trust signal (`UNVERIFIED`,
`agent-declared`) is unchanged, the oracle logic is untouched, and its mutation coverage still binds.
Taking it as fix-now was sound: an honesty defect inside the honesty feature was the right thing not
to defer, and the change is as small as the cost estimate said.

## Workflow Feedback
- **Instruction I improvised around, flagged rather than hidden:** the reviewer skill mandates driving
  a survey through the engine to a consolidated verdict. I did **not** re-open the consolidated,
  released survey for this pass, because your message scoped it explicitly as a one-string
  confirmation with "do not re-verify anything you already cleared," and a second 13-item survey for
  one string literal would have been ceremony rather than rigor. The original survey remains
  consolidated at `APPROVE` with its lease released. Flagging it because it is a genuine gap in the
  role doctrine: **there is no defined engine shape for a scoped re-confirmation round**, and this is
  the second such round on this issue (`g1-review-result-2.md`, `g2-review-result-2.md` show the same
  pattern). Overrule me and I will drive a fresh survey.
- **What worked:** naming the four questions as numbered questions with a stated out-of-scope list
  made this pass cheap and kept me from re-reviewing. The one thing that made Q1 non-trivial was not
  in your message and could not have been — that `agent-declared` is a disjunction — and it was worth
  the ten minutes to check by execution rather than accept the wording as obviously correct.

## Return status
`complete`

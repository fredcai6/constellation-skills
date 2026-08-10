# RUN_SUMMARY — commander-f2 (#542 adoption, #541 friction capture)

**Verdict: complete, with one criterion deferred and named.** 4 of 5 met with evidence
produced at their own gate. Criterion 3 deferred by Admiral ruling; **adoption is unverified
on Windows** and is not reported as achieved.

## Verdict per exit criterion

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1 | Role spine instructions name the door as default, CLI documented as fallback | **MET** | `tests/test_mcp_adoption.py`, 55 assertions over a pre-authored invariant chain, reading the JSON **imperative field by path** rather than file text. Two-sided verified by mutation in **both** directions. Count 0 → 13 files; CLI still named in 16 |
| 2 | A real dispatched agent drives a real role spine to done through the door alone, from its own call record | **MET** | `evidence/g4b/MEASUREMENT.md`: 9 door calls, **0 CLI engine invocations**, reached DONE. Two refused arms as control |
| 3 | `install_constellation.py` ships and wires `.mcp.json` | **DEFERRED — OPEN** | Count 2 **unchanged at 0**. A real install shipped neither `.mcp.json` nor the door script, verified by `ls`. #553 unfixed |
| 4 | The server's own rejections reach the run's episode, loudly when they cannot | **MET** | `tests/test_mcp_friction_capture.py` (8); `episodes/active/epic-418-followon_commander-f2-001.md`, `verify_episode_captured.py` exit 0 under a **nested** work-id |
| 5 | The identity trade decided, property given up written down | **MET** | `IDENTITY_TRADE.md`; `IdentityBindingPinTests` (9), red against six mutation classes |

## The measurement, in full

Three arms. **Bash was allowed in every one** — F's own MCP arm withheld it, which made
"zero CLI invocations" true by construction. Adoption is a claim about what an agent
*chooses* when both doors are open.

| Arm | Role | Door calls | CLI engine calls | Verdict |
|---|---|---|---|---|
| 1 | implementer, stale installed skills | 0 | 21 | REFUSED |
| 2 | implementer, freshly installed skills | 0 | 20 | REFUSED |
| 3 | a role that **owns its bound spine** | **9** | **0** | **ACCEPTED** |

All three had `{"name": "spine", "status": "connected"}` and all 7 tools offered, so arms 1
and 2 are **measured negatives, not unmeasured conditions**.

**Arms 1 and 2 measured the wrong role, and that error was mine.** Arm 2's agent obeyed
correct doctrine: g1 ruled that a seam below its container's separating granularity must not
take identity from it, and g4a wrote that into the implementer role, which is precisely the
role now told to use the CLI. Both negatives are kept, because they are what make arm 3's
exclusive door use a measurement of **choice** rather than of availability.

**Door-own friction on the accepted run: ZERO.** Reported as measured. No friction was
manufactured, and zero is not read as proof g2's capture works — that is what g2's seeded
control and its dedup mutation are for.

## What the reviewers found, which is the run's most reusable output

Six reviewer BLOCKs across 9 dispatches. Every one was taken on evidence; none overridden.
Four successive reviewers each defeated the g1 pin, one layer deeper each time:

1. *A pin over declarations is a pin over intentions.*
2. *An enumeration is not a property.*
3. *A property over the calls you make says nothing about the answers you invent.*
4. *Containment is not equality.*

The fifth limit was mine to find: black-box argument fuzzing cannot establish a property
over all argument names, so the final pin is structural — `call_tool` may answer in exactly
two ways — and mentions no argument names at all.

That pin then earned its keep in a **different** gate within the hour: g2's implementer
added a `_reject()` wrapper, creating a third way to return content, and the pin caught it.

## Residuals, stated plainly

- **g3 open.** Adoption unverified on Windows (#553).
- **g1's final increment** (equality + choke-point) is self-verified, not independently
  reviewed — the Admiral's stopping rule forbade a fifth pass.
- **g2's two fixes** and **g4a's review** are self-verified; independent review was traded
  for reaching g4b, which the Admiral protected absolutely.
- Two `APPROVE` postconditions were **force-waived with recorded reasons rather than
  forged**, so the record shows six real BLOCKs instead of a clean sheet.

## Isolation

```
$ python scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills-wt/f2-mcp-adoption
worktree OK: in /home/tommy/projects/constellation-skills-wt/f2-mcp-adoption
EXIT=0
```

Suite: **2339 passed, 1 skipped, 0 failed.** `git diff` against
`scripts/checklist_engine.py` is empty, as it was for all of F.

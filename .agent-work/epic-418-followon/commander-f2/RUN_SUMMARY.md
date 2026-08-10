# RUN_SUMMARY — commander-f2 (#542 adoption, #541 friction capture)

**Verdict: complete, with one criterion deferred and named.** 4 of 5 met with evidence
produced at their own gate. Criterion 3 deferred by Admiral ruling; **adoption is unverified
on Windows** and is not reported as achieved.

## Verdict per exit criterion

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1 | Role spine instructions name the door as default, CLI documented as fallback | **MET** | `tests/test_mcp_adoption.py`, 91 assertions over a pre-authored invariant chain, reading the JSON **imperative field by path** rather than file text. Two-sided verified by mutation in **both** directions. Count 0 → 13 files; CLI still named in 16. **Scope: the instructions say it. Whether saying it CAUSES adoption is UNMEASURED — see below** |
| 2 | A real dispatched agent drives a real role spine to done through the door alone, from its own call record | **MET** | `evidence/g4b/MEASUREMENT.md`: 9 door calls, **0 CLI engine invocations**, reached DONE, on arm 3. Basis: an agent that owns its bound spine and is offered the tools uses them. One refusing condition, observed twice (arms 1 and 2), shows the door was available and declined |
| 3 | `install_constellation.py` ships and wires `.mcp.json` | **DEFERRED — OPEN** | Count 2 **unchanged at 0**. A real install shipped neither `.mcp.json` nor the door script, verified by `ls`. #553 unfixed |
| 4 | The server's own rejections reach the run's episode, loudly when they cannot | **MET** | `tests/test_mcp_friction_capture.py` (9); `episodes/active/epic-418-followon_commander-f2-001.md`, `verify_episode_captured.py` exit 0 under a **nested** work-id |
| 5 | The identity trade decided, property given up written down | **MET** | `IDENTITY_TRADE.md`; `IdentityBindingPinTests` (10), red against seven mutation classes — the seventh being a redirect by argv POSITION (a second `--file`), which the first six pins could not see |

## The measurement, in full

Three arms. **Bash was allowed in every one** — F's own MCP arm withheld it, which made
"zero CLI invocations" true by construction. Adoption is a claim about what an agent
*chooses* when both doors are open.

| Arm | Role | Corpus loaded | Door calls | CLI engine calls | Verdict |
|---|---|---|---|---|---|
| 1 | implementer | `~/.claude/skills/constellation-implementer`, pre-g4a | 0 | 21 | REFUSED |
| 2 | implementer | **the same corpus arm 1 loaded** — arm 1 rerun | 0 | 20 | REFUSED |
| 3 | workbench, a role that **owns its bound spine** | `~/.claude/skills/constellation-workbench`, pre-g4a | **9** | **0** | **ACCEPTED** |

All three had `{"name": "spine", "status": "connected"}` and all 7 tools offered, so the
door's **availability** in a refusing arm is measured.

**Arm 2 duplicated arm 1's condition — it is not an independent second negative.** It was
reported as "freshly installed skills carrying the door"; it was not. Both implementer arms
loaded `~/.claude/skills/constellation-implementer`, whose `CORPUS.json` records
`source_commit: a1eab1f1` (2026-08-09) — **before g4a** (`e569350c`, 2026-08-10) — and which
contains **0** files naming the door. The fresh install at 02:11:45 went to the
project-local `.claude/skills/`, which no arm loaded. `evidence/g4b/MEASUREMENT.md` also
carried a block quote attributed to what the arm-2 agent read; `grep -c "share the parent"`
returns **0** across all three records, so **no agent saw that sentence** and the conclusion
drawn from it has been withdrawn, not reworded.

**All three arms loaded the pre-g4a corpus.** Arm 3 found the door through `ToolSearch`
against its launcher's `--allowedTools`, not through a role instruction — so g4a's
instruction edits were **not in the causal path of any arm**. Criterion 1's causal
contribution to adoption is therefore **UNMEASURED**: no arm created that condition, so
there is no reading to report. **UNMEASURED is not a negative** — writing an uncreated
condition down as a measured negative is the error this epic exists to stop. Criterion 1's
own claim, that the instructions name the door as default with the CLI kept as fallback, is
verified against the repo source by `tests/test_mcp_adoption.py` and stands independently.

The arm-design error is mine: arms 1 and 2 drove the implementer, which by g1's ruling is an
in-session dispatched crew member that does not own the process's bound spine, so it was
never the role that could satisfy criterion 2.

**Door-own friction on the accepted run: ZERO.** Reported as measured. No friction was
manufactured, and zero is not read as proof g2's capture works — that is what g2's seeded
control and its dedup mutation are for.

## What the reviewers found, which is the run's most reusable output

Six reviewer BLOCKs across 9 dispatches, plus four more from a cold review after this run
first reported itself complete. Every one was taken on evidence; none overridden. Five
successive reviewers each defeated the g1 pin, one layer deeper each time:

1. *A pin over declarations is a pin over intentions.*
2. *An enumeration is not a property.*
3. *A property over the calls you make says nothing about the answers you invent.*
4. *Containment is not equality.*
5. *A first-occurrence check on a value you yourself put first cannot fail.*

A further limit was mine to find: black-box argument fuzzing cannot establish a property
over all argument names, so the final pin is structural — `call_tool` may answer in exactly
two ways — and mentions no argument names at all.

That pin then earned its keep in a **different** gate within the hour: g2's implementer
added a `_reject()` wrapper, creating a third way to return content, and the pin caught it.

**A cold reviewer then found way 5 above, after this run reported itself complete, and this
paragraph is the correction:** the pin asserted `argv[argv.index("--file") + 1]`, and `index`
returns the FIRST match — which `run_engine` guarantees is the bound one. A second `--file`
injected ahead of the subcommand wins in argparse, so the door answered wholly from an
attacker-named file with `isError: False`, defeating both the runtime pin and the structural
one at once by hiding in argv **position**, a dimension neither modelled. Both `--file` and
`--session-id` are now pinned over **all** occurrences: the bound value must be the only
value the flag carries.

## Residuals, stated plainly

- **g3 open.** Adoption unverified on Windows (#553).
- **g1's final increment** (equality + choke-point) is self-verified, not independently
  reviewed — the Admiral's stopping rule forbade a fifth pass.
- **g2's two fixes** and **g4a's review** are self-verified; independent review was traded
  for reaching g4b, which the Admiral protected absolutely.
- Two `APPROVE` postconditions were **force-waived with recorded reasons rather than
  forged**, so the record shows six real BLOCKs instead of a clean sheet.
- **This run first reported itself complete with four defects still in it**, found by a cold
  review afterwards: the argv-position hole in the g1 pin, an instruction sending agents to
  two door tools that do not exist, an adoption tier that could not detect deletion of what
  it pinned, and the measurement error corrected above. All four are repaired; the pattern —
  self-verified increments traded for reaching a later gate — is the residual above, not a
  separate one.

## Isolation

```
$ python scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills-wt/f2-mcp-adoption
worktree OK: in /home/tommy/projects/constellation-skills-wt/f2-mcp-adoption
EXIT=0
```

Suite: **2339 passed, 1 skipped, 0 failed.** `git diff` against
`scripts/checklist_engine.py` is empty, as it was for all of F.

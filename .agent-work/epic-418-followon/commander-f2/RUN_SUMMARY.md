# RUN_SUMMARY — commander-f2 (#542 adoption, #541 friction capture)

**Verdict: complete, with one criterion deferred and named.** 4 of 5 met with evidence
produced at their own gate. Criterion 3 deferred by Admiral ruling; **adoption is unverified
on Windows** and is not reported as achieved.

## Verdict per exit criterion

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1 | Role spine instructions name the door as default, CLI documented as fallback | **MET** | `tests/test_mcp_adoption.py`, 282 assertions over a pre-authored invariant chain, reading the JSON **imperative field by path** rather than file text. Two-sided verified by mutation in **both** directions. The corpus is now WALKED (all 100 `.md`/`.json` files under `skills/`), not a 13-file list — the list left 87 files uncovered, including both survey checklists and `skills/admiral/SKILL.md`, and each accepted a planted violation while this file read 91/91 green. Count 0 → 13 files name a door tool; CLI still named in 16. **Scope: the instructions say it. Whether saying it CAUSES adoption is UNMEASURED — see below** |
| 2 | A real dispatched agent drives a real role spine to done through the door alone, from its own call record | **MET** | `evidence/g4b/MEASUREMENT.md`: 9 door calls, **0 CLI engine invocations**, reached DONE, on arm 3. Basis: an agent that owns its bound spine and is offered the tools uses them. One refusing condition, observed twice (arms 1 and 2), shows the door was available and declined |
| 3 | `install_constellation.py` ships and wires `.mcp.json` | **DEFERRED — OPEN** | Count 2 **unchanged at 0**. A real install shipped neither `.mcp.json` nor the door script, verified by `ls`. #553 unfixed |
| 4 | The server's own rejections reach the run's episode, loudly when they cannot | **MET** | `tests/test_mcp_friction_capture.py` (9); `episodes/active/epic-418-followon_commander-f2-001.md`, `verify_episode_captured.py` exit 0 under a **nested** work-id |
| 5 | The identity trade decided, property given up written down | **MET** | `IDENTITY_TRADE.md`; `IdentityBindingPinTests` (14, plus 8 subtests), red against the six recorded falsifications — the last being redirect by option SPELLING (`--file=X`, `--fil X`, `--fi=X`, and a forged `--session-id`), which every token-reading predicate before it could not see. The pin now asks `checklist_engine.parse_args`, and `run_engine` applies the same predicate at RUNTIME (`_identity_violation`), so IDENTITY_TRADE.md §2's sentence is true of the process and not only detectable in CI |

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

Six reviewer BLOCKs across 7 crew dispatches (`crew-runs.json`), plus five more from cold
reviews after this run first reported itself complete — four BLOCKs and one lesser finding
in the first, and this round's. Every one was taken on evidence; none overridden. Six
successive reviewers each defeated the g1 pin, one layer deeper each time:

1. *A pin over declarations is a pin over intentions.*
2. *An enumeration is not a property.*
3. *A property over the calls you make says nothing about the answers you invent.*
4. *Containment is not equality.*
5. *A first-occurrence check on a value you yourself put first cannot fail.*
6. *Enumerating shapes is the defect — a predicate over tokens is one spelling away from
   blind.*

A further limit was mine to find: black-box argument fuzzing cannot establish a property
over all argument names, so the final pin is structural — `call_tool` may answer in exactly
two ways — and mentions no argument names at all.

That pin then earned its keep in a **different** gate within the hour: g2's implementer
added a `_reject()` wrapper, creating a third way to return content, and the pin caught it.

**A cold reviewer then found way 5 above, after this run reported itself complete:** the pin
asserted `argv[argv.index("--file") + 1]`, and `index` returns the FIRST match — which
`run_engine` guarantees is the bound one. A second `--file` injected ahead of the subcommand
wins in argparse, so the door answered wholly from an attacker-named file with
`isError: False`, defeating both the runtime pin and the structural one at once by hiding in
argv **position**.

**A second cold review then found way 6, and this paragraph is that correction.** The repair
above pinned "all occurrences of the token `--file`" — still a predicate over tokens.
argparse accepts `--file=X` as one token and resolves the unambiguous prefixes `--fil` and
`--fi`; all three redirect the read and none is that token. Measured live against the real
engine, all three returned `isError: False` with the bound spine's content **gone**. The
identity half was worse: its assertion was CONDITIONAL on the token `--session-id` appearing,
and `mutating=` is reachable from `call_tool`, so a handler could suppress the bound session
and inject its own — a forged `claim` was demonstrated recording a lease under
`FORGED-SESSION` with the pin green, and `claim` is the one verb with no lease ahead of it to
fail closed on.

So the pin stopped reading argv. It hands argv to the engine's own `parse_args` and asserts
what the engine RESOLVES: `ns.file == str(SPINE)` and
`getattr(ns, "session_id", None) in (SESSION, None)`. **And the same predicate now runs
inside `run_engine` itself** (`_identity_violation`), because `IDENTITY_TRADE.md` §2 claims
the door *"can only ever touch the spine its own process was launched for"* — a claim about
runtime behaviour, which a CI pin cannot make true. Measured: the guard refuses all four
shapes, records no lease on a forged claim, leaves `spine_evidence attach` with two
`--field`s working, and leaves a malformed argv's error text byte-identical (137 bytes,
before and after).

## Residuals, stated plainly

- **g3 open.** Adoption unverified on Windows (#553).
- **g1's final increment** (equality + choke-point) is self-verified, not independently
  reviewed — the Admiral's stopping rule forbade a fifth pass.
- **g2's two fixes** and **g4a's review** are self-verified; independent review was traded
  for reaching g4b, which the Admiral protected absolutely.
- Two `APPROVE` postconditions were **force-waived with recorded reasons rather than
  forged**, so the record shows six real BLOCKs instead of a clean sheet.
- **g4b's independent review was waived, and the recorded basis for waiving it is now known
  to be false.** The basis, verbatim from `execute.json`'s `why_trail` entry `w-12`: *"The
  measurement's own two negatives are its review: an instrument that refused twice on real
  data, for two different reasons, and then accepted, has demonstrated it can lose.
  Independent review waived on budget and recorded as a residual."* The repair above
  established that arm 2 is arm 1 rerun — **one condition observed twice, not two** — and
  that the "second reason" (an agent reading a freshly installed door instruction) was never
  measured at all, because no arm loaded a corpus containing one. So the two facts the
  waiver rested on are one fact and one non-fact. The waiver is **not withdrawn and the gate
  is not re-litigated here**; it is recorded as what it is: the load-bearing gate of this
  wave closed without independent review, on grounds since falsified. It was also **absent
  from this list entirely** until now, which is its own defect — a waiver that does not
  appear among the residuals is not a recorded residual.
- **The withdrawn causal story survives in engine-owned state, and was deliberately not
  edited.** `execute.json` `w-11`/`w-12`/`w-13` and `spine.json` (the `g4b` satisfied_by,
  and the closing `why` entries) still say "two measured negatives", "two different reasons",
  "two refused arms" and "an agent obeying correct doctrine while I watched the wrong role".
  Those are the engine's journal, written at the time and not hand-editable; correcting them
  in place would forge the record of what was believed when the gate closed. This paragraph
  is the correction, and it is where a reader of those fields should be sent. The one
  Commander-authored, editable artifact that carried the story — `REPLAN_INPUT.json`, which
  feeds replanning and cited as its `source` the very document that retracted it — **has
  been corrected**.
- **This run first reported itself complete with five defects still in it**, found by a cold
  review afterwards: the argv-position hole in the g1 pin, an instruction sending agents to
  two door tools that do not exist, an adoption tier that could not detect deletion of what
  it pinned, the measurement error corrected above, and a friction-capture test that induced
  three different rejection classes so per-class and per-occurrence counting were
  indistinguishable. All five are repaired; the pattern — self-verified increments traded for
  reaching a later gate — is the residual above, not a separate one.
- **A second cold review then found five more**, all of the same shape as the first: a
  predicate that models a shape rather than asking the real thing. They are repaired in this
  round and each is recorded where it belongs — the pin and the runtime guard above, the
  adoption suite's walk and polarity checks, and the three prose corrections in this list.
- **One evidence file is mislabeled.** `evidence/g4b/run_arm_2.sh:37` redirects arm 2's
  stderr to `arm-mcp/record.err` — **arm 1's** file, which it overwrote (the file's mtime is
  02:12, arm 2's run; `arm-mcp-2/` has no `record.err` at all). No claim in this run depends
  on it: every count comes from the `.jsonl` records, which are correctly separated. Arm 1's
  stderr is not recoverable. Routed as a triage candidate (tc9) rather than reconstructed —
  there is no data to reconstruct it from.

## Isolation

```
$ python scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills-wt/f2-mcp-adoption
worktree OK: in /home/tommy/projects/constellation-skills-wt/f2-mcp-adoption
EXIT=0
```

Suite: **2572 passed, 1 skipped, 0 failed** (1087 subtests passed), `python -m pytest`, at the
head of the third repair round. It was 2339 when this run first reported itself complete and
2377 after the first repair round; the table above is measured at the same head as this line. `git diff` against
`scripts/checklist_engine.py` is empty, as it was for all of F.

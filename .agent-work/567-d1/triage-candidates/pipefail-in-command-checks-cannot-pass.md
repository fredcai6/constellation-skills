# Triage candidate — `set -o pipefail` in an engine `command` check cannot pass on POSIX

**Found at:** `g1b`, lane D1, epic #567 wave 2. Reported by the g1b implementer when the engine
refused its `advance` on a shell-dialect error rather than on its guard; reproduced directly by the
Commander.

**What was found.** The engine runs a `command` postcondition through `_find_posix_shell()`
(`scripts/checklist_engine.py:950`), which on POSIX returns `shutil.which("sh")`. On this host
`/bin/sh` is `dash`, and dash rejects the option outright, **before the check's own logic runs**:

```
$ /bin/sh -c 'set -o pipefail; echo reached'
/bin/sh: 1: set: Illegal option -o pipefail
exit 2
```

So any check authored `set -o pipefail; <real check>` fails unconditionally. It is a check that
cannot pass — the exact mirror of the failure mode the cold plan critic exists to catch.

**The provenance is the interesting part, and it is worth carrying.** This lane's cold plan critic
correctly killed `python3 -m pytest … | tail -5` as *a check that cannot fail*, and offered the
repair as *"drop `| tail -5`, or prefix `set -o pipefail;`"*. The plan took the second branch on
five checks. **The repair for a check that cannot fail produced five checks that cannot pass** —
and neither the plan author, the critic, nor the Commander who later rescoped three of those same
checks noticed, because the option looks like ordinary shell hygiene. It was found by a crew that
tried to run one.

`skills/_shared/global-everyone.md` already requires command checks to be authored in POSIX form, so
the rule exists; what is missing is anything that enforces it.

**Candidate fixes, in increasing cost:**
1. Name `set -o pipefail` explicitly as a non-POSIX form in the doctrine that already says "POSIX
   form" — cheap, and it would have prevented this.
2. Have the engine **refuse an amend/plan whose `command` check text fails to parse** under the
   shell it will actually run it in — a dry-run at authoring time rather than a surprise at
   `advance`.
3. Have the engine report a shell-dialect failure (exit 2 with an `Illegal option` stderr)
   distinctly from a genuine check failure, so the refusal names the real cause.

**Why it is a candidate and not a fix.** `scripts/checklist_engine.py` is **lane H's** this wave, and
`skills/_shared/global-everyone.md` doctrine changes route to the human under
`decision:no-doctrine-promotion`. This lane corrected its own five checks through the engine's
`retext-check` verb and re-verified them under `dash` in all three directions, which closes the
instance, not the class.

**Disposition:** `recommend-and-defer`. Pair onto an open issue at epic closeout, or record as an
episode. **Not filed as an issue** — `decision:no-issue-filing-mid-run`.

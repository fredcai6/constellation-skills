# Cold plan critic — findings and dispositions (issue #300)

Critique: `.agent-work/300/plan-critic/COLD_PLAN_CRITIC.md` (cold read of the mission frame plus the
candidate `execute.json` only; no authoring context). **5 BLOCKING · 7 SERIOUS · 7 MINOR = 19.**

Run as **mandatory**, not bias-to-yes, per `lesson:cold-critic-mandatory-for-measurement-dependent-
plans` — this plan's acceptance depends on a cross-environment determinism measurement and on
lint/parser tests, which is exactly the class that lesson names. It earned its keep: it found two
postconditions that **passed at HEAD with nothing built**.

Every finding is disposed below. A critic never self-triages; these dispositions are mine, and they
are surfaced to the Admiral because no human is reachable.

**UNTRIAGED: 0**

---

## BLOCKING

**B1 — `g3.c6`'s `! A || B` passed with the guard absent.** DISPOSITION: **EDIT — accepted, verified
myself.** I ran the string verbatim with nothing built: exit 0. The negation bound to the *collection
probe*, not the lint, so "prove the guard fires" was satisfied by never writing the guard. Replaced
with the plain command `python -m pytest tests/…::test_divergent_declaration_is_rejected -q`, which
exits 4 on a missing file or missing test id — correctly FAIL. Measured after the fix: exit 4.
This is the inverse of `lesson:prove-command-fails-postcondition`: the `!`-wrapper is right only when
it wraps *the thing that must fail*, and applying it to a probe inverts the check silently.

**B2 — `py -m pytest` has no pytest on this host; six postconditions unrunnable.** DISPOSITION:
**EDIT — accepted, verified myself.** `which py` → `/c/Users/fredc/.local/bin/py`, whose runtime
reports "No module named pytest"; `python -m pytest` → pytest 9.0.2. Every `py -m pytest` replaced
with `python -m pytest`. `py scripts/*.py` is left alone — that runtime runs stdlib scripts fine and
all such checks were measured working. The plan and `e0-context` now both state the rule explicitly.

**B3 — no gate mechanically enforced APPROVE; a BLOCK would advance every gate.** DISPOSITION:
**EDIT — accepted.** The house template (`EXECUTE_PLAN.template.json:52`) puts "returned" on the
review gate and `match: {"verdict": "APPROVE"}` on integrate; my plan had the strong *statement* on
review with no `match` anywhere. Restored the house split on all three gate triples.

**B4 — `g3.c5`'s `grep -qi 'context' docs/CHECKLIST_SCHEMA.md` was already true.** DISPOSITION:
**EDIT — accepted, verified myself** (`grep -ci` → 10 matches at HEAD). Replaced with
`grep -qE '^\| *`?context_refs`?'`, anchored on the table pipe and on the actual new field name.
Measured at HEAD: exit 1 — correctly fails today.

**B5 — the first real declaration and the plan's only acceptance test both lived inside the gate an
Admiral ruling could delete.** DISPOSITION: **EDIT — accepted; the most valuable finding of the
pass.** Under the old cut, deleting the contingent gate would have shipped a declaration field with
zero users, vacuously-empty manifests, a lint green because there was nothing to pin, and **no
cross-environment determinism evidence at all** — the pre-ruled acceptance test. Split at the real
seam: the first real spine declaration and the determinism exercise moved into **g1**; the contingent
**g2** now holds only the committed artifact and its generator. Deleting g2 now leaves #300 whole.
The `most-testable` plan alternative reached the same conclusion independently by a different route.

---

## SERIOUS

**S1 — the "consumable as #301's episode context field" acceptance criterion was owned by no
postcondition.** DISPOSITION: **EDIT — accepted.** Added `g3.c7` (the obligations artifact exists and
states both the may-rely and may-not halves) and `g3.c8` (a shape test asserting a produced run
manifest loads as JSON and is assignable to an episode `context` field untransformed), and named
both in `g3-review`'s imperative.

**S2 — "manifest on every assembly" appeared only in an anchors block, not a frozen statement.**
DISPOSITION: **EDIT — accepted.** `g1.c2`'s statement now names the real-writer assertion explicitly,
per `lesson:verify-harness-field-and-drive-real-writer`.

**S3 — the pre-ruled acceptance test was a `check: null` self-attestation.** DISPOSITION: **EDIT —
accepted, and strengthened past what the critic asked.** It is now a `kind: command` check running
`tests/test_context_determinism.py`, which creates a **clean second checkout** (`git worktree add` at
the same commit, different path) and rebuilds there under mutated `LC_ALL`/`LANG`/`PYTHONHASHSEED`.
That exercises all three named irreproducibility sources mechanically: line endings (via the CRLF/LF
twin fixtures in `g1.c2`), filesystem/path ordering (different checkout path), and locale/hash
ordering (mutated env). **Stated limit, kept honest:** same OS and same filesystem — this is not a
cross-OS rebuild, and the plan says so rather than letting the evidence overclaim. A carry-over
hazard is flagged in the gate: `lesson:windows-subprocess-env-does-not-shadow-path-resolution` means
the locale arm must *assert the mutation took effect inside the child*, not assume it.

**S4 — `g3-integrate`'s `-k 'context or checklist_engine'` filter excluded every module that reads
the changed files.** DISPOSITION: **EDIT — accepted.** The critic enumerated six modules that read
`skills/commander/` and the spine template and collect zero tests under that filter, including
`test_install_constellation.py`, which asserts on template names and iterates `skills/`. All final
integrate conditions now run the full `python -m pytest tests/ -q`. Measured at HEAD: exit 0, so the
full suite is a real green baseline, and it is fast enough that the filter bought nothing.

**S5 — the committed artifact's only freshness check ran *before* the gate that mutates doctrine.**
DISPOSITION: **EDIT — accepted.** Added `g3-integrate.c3` re-running `context_projection.py --check`
as the last thing verified, waivable with reason if the contingent gate was amended out.

**S6 — `g2` anchored on spec B2 while the frame lists B2 as out of scope.** DISPOSITION: **PARTIAL —
the frame was imprecise; EDIT the frame, keep the anchor.** Spec B2 contains two separable things:
the ahead-of-time-generation bullet (this issue's actual mandate) and the kernel-plus-fragments break
(conditional, decided at issue L). The frame's Out of Scope line named "B2" loosely and read as
excluding both. The anchor now says which half it means. The critic's *stronger* half — that none of
#300's three acceptance criteria mentions a committed artifact at all — is **accepted as real and
relayed to the Admiral**, because it sharpens the floated convergence choice rather than settling it.

**S7 — `g2.c3` promoted stated-insufficient evidence to a hard check while the discriminating one was
`null`.** DISPOSITION: **EDIT — accepted.** `c3` is kept (idempotence is worth pinning) but its
statement now says plainly that it is *necessary, not sufficient*, and names where the discriminating
evidence actually lives. With S3 fixed, the check strength is no longer inverted against the plan's
own evidence hierarchy.

---

## MINOR

**M1 — `g4`'s panel depth had no evidence; `c2` checked a hand-typed token.** DISPOSITION: **EDIT —
accepted.** `c1` now requires three named non-empty critic reports; `c2` derives a disposition count
from the record with a regex instead of trusting a typed total.

**M2 — command checks inherit the process cwd; `_run_check_command` passes no `cwd=`.** DISPOSITION:
**EDIT plus FILE UPSTREAM.** The plan and `e0-context` now state that all commands assume cwd = the
worktree root. The engine asymmetry the critic found — `_git` passes `cwd=base_dir`, the command-check
runner does not — is a genuine latent defect beyond this issue's scope and is filed to the tracker as
a triage candidate rather than banked locally.

**M3 — `windows-corpus` and `no-globs` were called load-bearing but had no check.** DISPOSITION:
**EDIT — accepted.** Added `g1.c6`, a mechanical check over the producer for filesystem enumeration
and unpinned text writes, and named both in `g1-review`'s imperative.

**M4 — `e0-context` directed the crew at three things this repo does not have.** DISPOSITION:
**EDIT — accepted.** The imperative was inherited boilerplate. It is now localized: `docs/agents/`
and `docs/architecture/` are absent by design, the substituted structural record is named, and the
frame is read first rather than last.

**M5 — `config_ref` points at a known-dead path.** DISPOSITION: **REJECT, with reason.** The shipped
`COMMANDER_SPINE.template.json` and `EXECUTE_PLAN.template.json` both carry this exact `config_ref`,
and the engine's own imperative text calls its absence *sanctioned degradation* and explicitly says
not to create the file. Dropping the key here would make this plan diverge from every other checklist
in the corpus for no behavioural gain, and the divergence would itself become a puzzle for the next
reader. The critic is right that carrying a dead reference plus an explanation is unlovely — that is
a corpus-wide cleanup, not a #300 edit, and it is filed as a triage candidate.

**M6 — anchors duplicated verbatim three times per gate (~350 of 751 lines).** DISPOSITION: **EDIT —
accepted, and it mattered mechanically.** The house template's `{"inherits": …}` idiom is now used on
every review gate. The critic's reason is the operative one: `g2` is expected to be amended via the
engine's `amend` verb, and three copies means amending three consistently or leaving two stale.

**M7 — YAGNI: the read-only CLI verb.** DISPOSITION: **EDIT — accepted, deleted outright.** No
acceptance criterion of #300 needs a CLI surface; the manifest is a JSON file. The verb would have
touched the engine's persistence control flow (two write-guard sites plus a `MUTATING_VERBS`
exemption) for a convenience print. Recorded as a named untaken road: if a consumer appears, it is a
small addition over an unchanged manifest — which is itself evidence the seam sits in the right place.

---

## The critic's non-findings, recorded because they are evidence too

Verified rather than assumed, and worth keeping so a later reader does not re-litigate them: the
POSIX shell forms are safe (the engine deliberately routes command checks through bash and refuses to
fall back to cmd.exe); `g3`'s two prose-survival invariants are genuine non-regression guards whose
phrases exist verbatim today; the structural anchor line numbers are all accurate; a `-k` filter that
deselects everything exits 5, not 0, so it cannot silently pass on zero tests; and there is **no
drift toward access tracing or transcripts** — the critic hunted that class specifically and found
none.

## Post-fix verification

All 21 command postconditions were executed verbatim in bash at HEAD before the plan was frozen.
Result: every check that should fail today fails (exit 1, 2 or 4), and the only three that pass are
the ones that must — the two prose non-regression invariants and the full test suite, which is green
at HEAD (`python -m pytest tests/ -q` → exit 0) and is therefore a real baseline rather than an
assumption. **No postcondition in the frozen plan passes vacuously.**

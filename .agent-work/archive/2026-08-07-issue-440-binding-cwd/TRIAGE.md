# Triage — issue #440 (epic-418 workstream A2)

Authority: launch order `_COMMON.md` § Inherited Latitude delegates **issue filing and commenting**.
Issue *closing* is not delegated and none is proposed here.

Four candidates, all routed. None qualified for the fix-now lane except T1, which was fixed during
the run and is recorded here rather than left unwritten.

---

## T0 (fixed-now) — the acceptance verifier passed while the bug was present

**Labels:** bug, missing test
**Disposition:** `fixed-now` — commit `89cc99a`

**What.** `verify_evidence.py` never read `binding_entries`. A treatment arm whose binding pointed at
the sandbox MAIN — the #440 defect *not* fixed — still exited 0, because the arm checks only ever
read the gauge paths and never the binding that produced them. `path_source == "git_worktree"`, the
single most load-bearing fact in the whole result, was asserted for the preflight alone.

**Why it cleared the ladder.** Bounded (one helper plus five selftest mutations, one file); adjacent
(it *is* this run's acceptance artifact); verifiable in-context (`--selftest` proves each new check
can fail); no architecture or production-default impact (a local acceptance script, not shipped code).

**Evidence.** Found by the g2 reviewer as finding F1. 46 → 59 checks, 5 → 10 selftest mutations. The
new `treatment-binds-main` mutation correctly fails where it exited 0 at `b332287`.

---

## T1 (filed) — a bare-keyed agent driving several spines at once gets NO gauge reading at all

**Labels:** bug, architecture weakness
**Importance:** This is the highest-value thing this run found, and it is **not #440**. It is what
actually keeps the context governor silent for orchestrators — the agents whose context fills first.

**What.** `resolve_gauge_path` (`gauge_writer_hook.py:235-265`) returns one candidate per spine bound
under the acting key. The ambiguity guard (`:595-606`) then refuses to write when there is more than
one. A top-level agent keys **bare**, so an Admiral that legitimately claims an epic spine plus a
crew spine or two in one session silences its own gauge for the rest of that session.

**Evidence.** Measured on the live store 2026-08-07: the one bare key held **10 entries, 3 of them
live**. Retiring the 7 dead ones would leave the guard still firing at 3 — which is why the
`decision:existing-bindings` ruling came out "leave to age out": the dead entries are a symptom, not
the disease. Before-state at `.agent-work/issue-440-binding-cwd/g3/live-binding-store-before.json`.

**Acceptance criteria.** A top-level agent driving N spines concurrently gets a reading for the spine
it is *currently acting on*, rather than none. Proven on a live run, not by unit test alone — the
same bar #419 and #440 were held to.

**Out of scope.** Changing the binding key shape is explicitly outside a Commander's inherited
latitude and must be adjudicated.

---

## T2 (filed) — `spine_rail.py` binds an unexpanded shell token verbatim as a spine path

**Labels:** bug

**What.** The hook parses the tool payload's command string and cannot tell whether the shell
expanded a token, so `--file $E` records a literal path ending in `$E`. It binds a path that can
never exist.

**Evidence.** Two such entries in the live store: `…\x` and `…\$E`. The second was written
2026-08-06T10:03:03Z under `engine_session: g2-impl-440-acceptance` — this issue's own attempt-1 crew.

**Importance.** Same family as #440 (a binding that names the wrong path) but a **different
mechanism** — command-string parsing, not root resolution — so the `fix-the-resolution-not-the-caller`
pre-ruling does not reach it. Its cost is not zero: every junk entry adds a candidate to its key and
pushes that key toward the T1 ambiguity guard.

**Deliberately not chased** under the scope-discipline ruling; documented at the code site in
`docs/GAUGE_WRITER_HOOK.md` § Known limits.

---

## T3 (filed) — `test_mutation_floor.py` reports a false HARNESS ERROR in every agent session

**Labels:** bug, tooling

**What.** `tests/test_mutation_floor.py:255` parses its own pytest subprocess output with a regex
matching `FAILED` immediately followed by the test path. It does not strip ANSI. The Claude Code
harness exports `FORCE_COLOR=3`, so pytest emits colour even into a captured pipe, the reset sequence
lands between `FAILED` and the path, every match breaks, and the meta-harness reports
`HARNESS ERROR: non-zero exit with no FAILED test node` while its own captured output plainly
contains those nodes.

**Evidence.** With the variable neutralised the file goes from **10 failed / 4 passed** to
**14 passed, exit 0**. Confirmed pre-existing: `git archive cbd9aee` into a temp tree gives 11 failed
there. It also explains the launch order's baseline discrepancy — the Admiral measured `exit 0`
outside a `FORCE_COLOR` session.

**Importance.** This fires for **every agent that runs the suite**, which is all of them. It is a
second, independent false-red in the same family as the launch order's `py`-is-not-the-test-runner
warning, and this one fires for `python` too. A Commander who trusted it would report a red baseline
that does not exist; one who dismissed it without checking would miss a real regression.

**Acceptance criteria.** Strip ANSI before matching (or run the subprocess with colour disabled), and
a test proving the parser survives coloured output.

---

## T4 (filed) — acceptance-harness hardening: remaining verifier holes and destroyed evidence

**Labels:** missing test, cleanup

Consolidates the g2 reviewer's non-material findings and the implementer crew's own candidates. Each
is commented at its code site; none was chased, per the scope-discipline ruling.

- **The freshness check cannot detect staleness.** It compares `observed_at` to
  `wall_clock_at_collect`, both written by the same `collect()` call. It proves the reading was fresh
  *when the engine read it* — the relation the trip depends on — but not that the evidence being
  presented is current. Settling that needs an out-of-band clock; the reviewer used file mtimes.
- **Per-launch headless logs are overwritten**, so a declined or killed first launch leaves no
  artifact and its diagnosis becomes uncorroborated prose. This is what stopped the reviewer settling
  whether the quiet first treatment launch was byte-identical to the one that complied.
- **`probe()` computes a verdict, writes it, and discards it** — its docstring describes a two-branch
  policy the body does not have.
- **The evidence schema is declared nowhere** (Fowler: shotgun surgery). This is the mechanism behind
  five of the eight holes the reviewer found; a declared schema would close them as a class.
- **A dispatched subagent can decline an inflation protocol** by reading the prompt's own defensive
  framing as social engineering. Observed live: the first treatment launch declined, then complied on
  an unchanged re-run. A live flakiness source for this harness family.
- **No check may assume shared agent-written state is byte-stable.** The original live-store guard
  asserted byte-identity of a file two live sessions were writing; it was replaced with a leakage
  test. Recorded so the next harness does not repeat it.

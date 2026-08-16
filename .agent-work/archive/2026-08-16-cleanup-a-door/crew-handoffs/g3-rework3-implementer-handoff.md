# Implementer Handoff — g3 REWORK 3 (attempt 4, FINAL within the rework cap)

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing.

## Gate
`g3` — issue #603. **Rework 3 of a cap of 3.** A further BLOCK escalates to the Admiral, so
this handoff is scoped to leave nothing behind.

## The functional work is settled — change no behaviour

Three independent reviews have reproduced all of #603: the six unbound-class refusals,
bind-on-open through to a successful `claim`, the regression suite red pre-fix, `:194`
byte-identical, the module-wide pin and its mutated control,
`IdentityGuardSurvivesARebindTests`, the env overrides, the lease-held rebind refusal, unset
`SPINE_ENGINE`, `map/` freshness. Suite green at `176133ac`: **3093 passed, 6 skipped, 1153
subtests, 0 failed**.

**This rework is documentation and dead test scaffolding only.**

## Why this is the fourth attempt — the mistake was mine, and it is the lesson

Rework 2's sweep reported `LIVE IN-SCOPE HITS: 0`. That number was **real and measured the
wrong set**: my handoff set `ALLOWED_SCOPE = ("tests/test_mcp_lifecycle.py",)`, which is the
rework's **edit permission**, not the change's **blast radius**. The instrument *found* the
surviving claims and its own classification filed them out of the headline.

**Blast radius is every artifact that asserts something about what you changed — regardless
of whether you were allowed to edit it.** Scope your sweep to that, and report the count of
what the change invalidated, not the count of what you were permitted to touch.

## The four invalidated claims — fix all four

**1. `scripts/mcp_spine_server.py:129-131` — the module docstring states the inverse of the code.**

> "`spine_open` … deriving the primary checkout it opens work from fresh off `SPINE_FILE`
> (ambient, server-launch-time state) rather than the module's own `SPINE` binding"

At HEAD, `_primary_checkout_for_lifecycle`'s anchor is
`SPINE.parent if SPINE is not None else Path(__file__).resolve().parent`. It reads
`SPINE_FILE` **never** and the module's own `SPINE` binding **always, when there is one**.
**Both halves of the "rather than" are backwards.** Correct it to describe the anchor that
actually runs. The surrounding point — that `_spine_open` must not be redirected onto the
bound spine — is still right; keep it.

**2. `scripts/mcp_spine_server.py:30` — a correction that was written down and not made.**

> "Ambient state is bound at server-launch time from the environment…"

`_bind_process_to`'s own docstring at `:868` already records the requirement:

> "the module docstring's *'bound at server-launch time'* is now *'bound at launch OR at
> `spine_open`'*, and **nothing may be left describing the previous spine**."

Make `:30` say that. (`tests/test_mcp_identity.py:547` quotes the stale sentence as the
seam's definition — it is prose in a class docstring, not an assertion, so correcting `:30`
will not turn it red. Update that quote too, so the propagation stops.)

**3. `tests/test_mcp_lifecycle.py:335-341` — a stale comment justifying an inert write.**

```python
# `_spine_open` deliberately RE-READS `SPINE_FILE` from the environment
# at call time (never the module's own bound `SPINE` -- that is the
# whole point of the identity pin above), so it must still be set now,
```

Both clauses are false at HEAD and the second is precisely inverted. **This is the worst of
the four, because it is not description — it justifies the `os.environ["SPINE_FILE"] = …`
write at `:341`.** The reviewer replaced that write with `os.environ.pop("SPINE_FILE", None)`
and the test **still passed**, then restored it byte-identical. **Delete the comment together
with the now-inert write it justifies**, and confirm the test still passes.

**4. `tests/test_mcp_adoption.py:98-102` — a claim #603 was written to falsify.**

> "`mcp_spine_server` reads SPINE_FILE/SPINE_ENGINE from the environment at IMPORT time and
> **raises KeyError without both set** (its own module docstring says so)"

Disproved by measurement: importing with both variables removed gives
`IMPORT OK … SPINE = None`. Correct the **rationale**. The practice it defends (hand-typing
the tool names) is still fine — only its stated reason is void. Note the parenthetical cites
the module docstring as authority, i.e. finding 1 propagating; fixing 1 is what makes this
correction true.

## Close criteria

- All four corrected; the `:341` write deleted with its comment.
- **A blast-radius sweep scoped to what this change invalidated, not to what you may edit.**
  State the command, the total scanned, and the count of live invalidated claims — which
  must be **0 in the source tree** (`scripts/`, `tests/`, `examples/`, `docs/`).
- Full clean-env suite green, with the count.
- **No behaviour change.** `git diff` should be docstrings, comments, and one deleted
  test-setup line.

## Sweep method — the part that keeps failing

Two sweeps have now missed claims, for two different reasons:

- a **line-based** `grep` cannot see a string assembled from adjacent literals (blocker 2);
- a **keyword** sweep only finds claims phrased the way you guessed — findings 3 and 4
  escaped because they say "RE-READS `SPINE_FILE`" and "reads … at IMPORT time", matching
  no trigger (blocker 3).

So: parse **AST string constants** (the parser joins implicit concatenation for you) **and**
comment runs, whitespace-collapse them, and search on the **identifiers this change touched**
(`SPINE_FILE`, `SPINE_ENGINE`, `SPINE`, `SESSION`, `spine_open`, `_primary_checkout_for_lifecycle`,
`KeyError`, "import time", "launch time") rather than on remembered phrasings. Then **read
the hits** — do not trust the classifier to sort them for you. That is what filed the last
four out of view.

## Allowed scope

- `scripts/mcp_spine_server.py` — **docstrings and comments only.**
- `tests/test_mcp_lifecycle.py` — the comment at `:335-339` and the inert write at `:341`.
- `tests/test_mcp_adoption.py` — the rationale at `:98-102`.
- `tests/test_mcp_identity.py` — the quoted stale sentence at `:547` only.

## Specific exclusions

- **Any behaviour change, assertion change, or logic change** other than deleting the one
  proven-inert `os.environ` write. Anything else is a stop condition.
- `tests/test_mcp_lifecycle.py:194` and its positive control — **byte-identical, fenced by
  three reviews.**
- `_identity_violation`; `scripts/checklist_engine.py`, `scripts/hooks/**` (including
  `spine_rail.py`'s own invalidated claim — **fenced**, lanes B/C, already reported to the
  Admiral), `scripts/run_crew.py`, `scripts/gauge_reader.py`.
- `scripts/install_constellation.py` / `COMMANDER_SPINE.template.json` doctrine.
- `episodes/**` and `map/**` prose — historical records; do not rewrite history.
- **Do not** refactor the six restatements into one source of truth. The reviewer is right
  that shotgun surgery is the durable cause, but that is a design change beyond this gate —
  it is being filed as a triage candidate.

## Constraints

- No `map/` rebuild expected (no entity changes). If one becomes necessary: **stage first,
  rebuild last, then commit** — that ordering is what caused blocker 1.
- Clear `__pycache__` before the suite measurement (#597).

## Map anchors (inbound)

Unchanged. **Map entry point: none** (`map/ids.jsonl` empty). Relevant:
`scripts/mcp_spine_server.py:30,129-131,868`; `tests/test_mcp_lifecycle.py:335-341`;
`tests/test_mcp_adoption.py:98-102`; `tests/test_mcp_identity.py:547`. No decision anchor is
touched.

## Deliverable path check

**Committed** — all four files; `git check-ignore` exits 1 for each.

## Required evidence

1. Before/after for each of the four corrections.
2. Proof the deleted `:341` write is inert — the test passing without it.
3. Your blast-radius sweep: command, total scanned, live invalidated claims (**0** in the
   source tree), and the hits you read and dismissed.
4. Full clean-env suite green, with the count.
5. `git diff --stat`.

## Wiring grep

`none — this rework adds no callable symbol.`

## Suggested model tier

`stronger` — the corrections are mechanical, but the sweep has defeated two previous attempts
and getting it right is this gate's actual deliverable.

## Authority

Already decided: all four are text/dead-scaffolding; no behaviour changes; no refactor of the
restatements; the sweep must be AST-aware and identifier-driven. Yours: the replacement
wording, and the sweep's implementation.

## Stop conditions

Stop and return if: a behaviour change proves necessary; the `:341` write turns out **not**
to be inert; or your sweep finds a live invalidated claim in a **fenced** file (report it, do
not fix it).

## Return format

`IMPLEMENTER_RESULT`, `Return status` lowercase. **Delivery:** write it to
`.agent-work/cleanup-a-door/crew-handoffs/g3-rework3-implementer-result.md` before ending
your turn.

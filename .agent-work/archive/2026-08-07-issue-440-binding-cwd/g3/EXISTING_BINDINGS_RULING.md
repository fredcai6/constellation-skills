# Ruling — `decision:existing-bindings` (issue #440, g3-close)

**Ruling: LEAVE TO AGE OUT. No mutation of the live store.**
Grade: `measured` (was `guess · leans execute`). Settled by the experiment the launch order named:
*check whether a stale binding causes a wrong reading or merely a missing one.*

Before-state recorded at `.agent-work/issue-440-binding-cwd/g3/live-binding-store-before.json`
(sha256 `2e80067d009e…`, 3 keys, 12 entries, captured 2026-08-07). Nothing was mutated, so no
dry-run was required.

## The measured live store

| key | entries | live paths | dead paths | ambiguity guard |
|---|---|---|---|---|
| `e8249451-…d405c` (bare) | 10 | 3 | 7 | **FIRES** |
| `cdcd8db2-…#a9bf3781a824a48ac` | 1 | 0 | 1 | clear |
| `cdcd8db2-…#ad611b635dad1da43` | 1 | 0 | 1 | clear |

**8 of 12 entries name a path that does not exist** — the #440 phantom-in-main shape. The launch
order's prevalence figure was 60 of 64 on 2026-08-05; the store has since been rewritten by live
activity, and the shape is unchanged.

## The question the ruling turned on: wrong reading, or merely missing?

**Merely missing. A stale entry cannot produce a wrong reading.** Three independent reasons:

1. **The engine never reads through the store.** It reads `gauge.json` beside the spine path it was
   itself invoked with. The binding store steers only the *writer*. So a wrong binding can misplace a
   write; it can never redirect a read.
2. **A key with more than one candidate writes nothing at all.**
   `gauge_writer_hook.py:595-606` — when `len(gauge_paths) > 1` the writer refuses, drops an
   `ambiguous-binding` skip flag on every candidate, and returns `{}`. Its own comment names the
   reason: cross-writing one agent's reading into an unrelated agent's work area is worse than
   silence. So the stale-plus-live case degrades to silence, not to a wrong number.
3. **A misplaced write ages into nothing.** The reader collapses any reading older than its
   30-minute freshness window to "no reading", so even a phantom `gauge.json` that a future work area
   happened to grow around would be inert by the time anyone met it.

Both failure modes are therefore **missing readings**. That is the whole basis for the least
invasive ruling, and the constraint on this gate asked for exactly that.

## Why retiring the dead entries was considered and rejected

It buys nothing measurable. Key `e8249451` is silenced by the ambiguity guard at **10** candidates;
delete all 7 dead entries and **3 live ones remain**, so the guard still fires and the agent is still
silent. Retirement would carry a real risk — a lost update against a store two live sessions are
writing right now — in exchange for no change in behaviour.

Session keys are also never reused, so every entry belonging to a finished session is unreachable by
construction. They are inert, not merely harmless.

## The finding this gate actually surfaced — and it is not #440

**The live governor is silent for the Admiral, and #440 is not the reason.** Key `e8249451` holds
**three live spines at once** — the epic spine plus two crew `review.json` spines — all under one
**bare** session key. `resolve_gauge_path` (`gauge_writer_hook.py:235-265`) returns one candidate per
bound spine, so the ambiguity guard fires and that agent gets **no reading at all**, permanently, for
as long as it drives more than one spine in a session.

This is structural, not stale data. Fixing #440 does not touch it: #440 was about *which root* a
relative `--file` resolves against, and this is about *one key legitimately holding several spines*.
It is why the store's dead entries are a symptom rather than the disease.

**Floated to the Admiral as a candidate issue, not fixed here** — it is outside #440's stated
obligation, and the scope-discipline ruling says note it and pass it up rather than absorb it.

## Second finding: `spine_rail.py` binds unexpanded shell tokens

Two entries in the live store are named `…\x` and `…\$E`. The second is an **unexpanded shell
variable recorded verbatim as a spine path** — written 2026-08-06T10:03:03Z under
`engine_session: g2-impl-440-acceptance`, i.e. by this issue's own attempt-1 crew, before my session
began. The hook parses the command string literally and cannot tell whether the shell expanded a
token, so it binds a path that can never exist.

Same family as #440 — a binding that names the wrong path — but a **different mechanism**
(command-string parsing, not root resolution), and the pre-ruling `fix-the-resolution-not-the-caller`
governs the latter. **Filed, not fixed**, per scope discipline. Its practical cost is not zero: each
junk entry adds a candidate to its key and so pushes that key toward the ambiguity guard.

## Disposition

- **Live store: untouched.** Byte-for-byte unmodified by this Commander.
- **Dead entries: leave to age out.** Inert by construction; retiring them changes no behaviour.
- **Two candidate issues floated up:** the bare-key multi-spine ambiguity silence, and the
  unexpanded-shell-token binding.

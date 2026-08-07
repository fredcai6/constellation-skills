# Ruling on `decision:existing-bindings` — the live store's broken entries

Launch order A2-440: *"the live store's 60 broken entries are **data, not code**. Decide on evidence
whether they need migrating, retiring, or simply leaving to age out, and say which."*
`@grade: guess · leans execute · settle: check whether a stale binding causes a wrong reading or merely a missing one`

Before-state preserved verbatim at
`.agent-work/issue-440-binding-cwd/evidence/binding-before-440.json` (copied read-only from
`C:/Programs/constellation-skills/.agent-work/.spine-rail-binding.json`).

## Measured state, 2026-08-06

**1 key, 8 entries, 5 of which name a spine file that does not exist.**

| Entry | Spine exists? | Why |
|---|---|---|
| `<main>/.agent-work/epic-418/spine.json` | **yes** | the Admiral, genuinely working in the main checkout |
| `<main>/.agent-work/issue-440-binding-cwd/spine.json` | no | **my own claim** — relative `--file`, resolved against the payload `cwd` |
| `<main>/.agent-work/epic418-h-447/spine.json` | no | another commander, same shape |
| `<main>/.agent-work/epic418-h-447/g1-review/review.json` | no | its crew, same shape |
| `<main>/.agent-work/issue-440-binding-cwd/crew/g1-implement/IMPLEMENTER_PLAN.json` | no | my g1 crew, same shape |
| `<main>/.agent-work/issue-440-binding-cwd/crew/g1b-ambiguity/IMPLEMENTER_PLAN.json` | no | my g1b crew, same shape |
| `<worktree>/…/crew/g1-review/review.json` | **yes** | my reviewer used an **absolute** `--file` |
| `<worktree>/…/crew/g1b-ambiguity/…` | **yes** | same |

This is a fresh, same-day replication of #419's 60-of-64 measurement, and it includes **my own
spine**. Note what separates the three good rows from the five bad ones: an **absolute** `--file`.
Every relative one landed in the main checkout. That is the defect, reproduced live, on this run.

## The settle experiment, answered

> *does a stale binding cause a WRONG reading, or merely a MISSING one?*

**Merely a missing one — but it does a second, worse thing the question did not anticipate.**

- **Not a wrong reading.** The phantom directory the writer creates in the main checkout contains a
  `gauge.json` and no `spine.json`. Nothing ever reads a gauge except at a path derived from a real
  spine, so a phantom reading is never served to anyone. It is dead weight, not misattribution.
- **But it silences the whole key.** The gauge writer only produces a reading when a binding key
  resolves to **exactly one** spine (`docs/GAUGE_WRITER_HOOK.md`, "Session→spine binding
  assumption"). This key holds **eight**. So the writer currently writes **nothing for anyone in
  this session** — including the Admiral, whose own entry is correct. The stale entries are not
  inert: they are what is keeping the governor off right now.

That reframes the disposition. Leaving them to age out is not free, and nothing reaps them
(`docs/GAUGE_WRITER_HOOK.md`: *"a successful `release` is the only removal path"*).

## Ruling: **retire the unresolvable entries; migrate nothing.**

- **Retire** — delete entries whose recorded spine path does not exist on disk. They can never
  produce a usable reading, and each one is actively holding its key ambiguous.
- **Do not migrate.** Rewriting `<main>/…/<work_id>/spine.json` to a guessed worktree path would be
  the same guess this issue just removed from the code. The agents concerned will re-claim under the
  fixed resolution on their next run; a re-claim is the honest repair.
- **Do not touch resolvable entries**, including other agents' live ones.

**Bounded and self-limiting.** After g1/g1b, an unresolvable entry can no longer be *created* — the
resolution binds nothing rather than recording a path that is not there — so this is a one-time
drain of a population that is now closed, not a recurring chore.

## Conditions I am applying to the mutation

The launch order requires a dry run and a recorded before-state; the cold critic added that the
store is shared with a live Admiral and `_save_json_map`'s read-modify-write takes **no lock**
(`docs/GAUGE_WRITER_HOOK.md`, known limit 3), so a careless prune could drop a concurrent claim.

1. Before-state copied to this worktree **before** any write (done, above).
2. Dry run first, printing exactly which entries would go.
3. Re-check each candidate's non-existence **immediately** before writing, so an entry that became
   real in between is spared.
4. Delete only entries whose spine is absent. Never a whole key, never a resolvable entry.
5. Re-read and diff after the write.

## Not fixed here, floated up

**Nothing reaps an abandoned key**, and per-agent keying multiplies the key count by every wave's
fan-out (`docs/GAUGE_WRITER_HOOK.md`, known limit 2; #419 deleted its one-time sweeper after a single
run, as that issue required). This prune is another one-time sweeper and will need writing again next
time. A durable reaper is out of #440's scope and belongs in its own issue.

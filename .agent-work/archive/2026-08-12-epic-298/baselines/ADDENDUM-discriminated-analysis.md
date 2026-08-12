# Addendum — reading the map vs orienting by it

**Post-closeout analysis. No re-run, no re-cut, no unfreeze.** Every number here is extracted
from transcripts already archived under `runs/`; the rubric stays frozen at `a226642b` and the
captured data is untouched. Added on the Admiral's direction after Tommy's ruling that the
naive ordering measure carries a confound.

---

## 1. BLOCKING CONFIRM — answered: **NO. The measured runs were not Commanders.**

The Admiral asked me to confirm, before the runs, that each measured run loads
`constellation-commander`, drives its spine, and reaches the `context` and `plan` steps where
the two pathless map-first imperatives fire.

**It does not, and did not.** Answering plainly because the confirm was raised as the one thing
that could invalidate the capture, and it partly does.

**Zero skill invocations across all five runs.** Not one `Skill` call. The runs were generic
agents with the corpus installed and *offered* — every transcript's `system/init` event lists
the `Skill` tool and all 19 constellation skills in both `skills` and `slash_commands` — and
every run declined it. Four of five never read a corpus file at all.

So the two imperatives the Admiral names (`context`: *"Read the current map…"*; `plan`:
*"Map-first: BEFORE authoring execute.json…"*) **never fired in any run.**

### What this arm therefore does and does not measure

**Scoping the null, per doctrine — a negative result kills that specific test, not the class.**

| | |
|---|---|
| **Measured** | Whether an ordinary agent, in a repo whose auto-loaded `CLAUDE.md` *lists* its architecture map, orients from that map. |
| **NOT measured** | Whether a **Commander**, under the pathless map-first imperatives, orients from that map. |

Because #304's contract lands **in Commander doctrine**, and no Commander ran, **this arm does
not test #304's surface.** A post-#304 arm instrumented identically would measure the same
generic-agent behaviour and return a null that says nothing about the contract.

This does not make the arm worthless — see §2, where it answers Tommy's question cleanly and on
its own terms. But it is not the arm the paired design assumed, and calling it one would be the
error the confirm existed to prevent.

**The harness can do it.** Forcing the load is a brief change (name the skill, or invoke the
slash command). I have not made it, because a Commander-loaded capture is a *different arm*, not
a correction to this one, and spending it is the Admiral's call. Recommendation in §5.

---

## 2. Tommy's confound — tested, and it does not bite. The opposite happens.

Tommy's concern: `CLAUDE.md` lists four docs under *"Also read before touching an area:"*, with
the architecture map as a peer of a test-commands doc and a doc-library index. If every run
dutifully reads all four at bootstrap, you get a unanimous map-first result **produced by the
reading list, not by orientation** — a false positive of the whole instrument.

**Directly checkable from the archived transcripts. It did not happen.**

| doc listed in `CLAUDE.md` | runs that read it |
|---|---|
| `README.md` | **1 of 5** — and at call **54**, not bootstrap |
| `TESTING.md` | **0 of 5** |
| `docs/DOCUMENTATION.md` | **0 of 5** |
| `docs/architecture/index.md` | **2 of 5** — at calls **33** and **8** |

**No run followed the reading list at all.** Not one read a single listed doc before touching
the area. The confound is real in principle and absent in this data — and the check that
establishes that is cheap and repeatable, which is the point of running it rather than assuming
either way.

Consequence: the naive ordering measure is **not** inflated by bootstrap compliance here. The
map reads that did occur were task-driven, not list-driven. The measure survives — but for a
reason that had to be verified, not assumed.

---

## 3. Reading vs orienting, separated

Using the Admiral's four discriminators against the archived transcripts.

| task | read at bootstrap? | map before src? | **returned to map after src?** | map-sourced cues in plan | src precision (named/opened) |
|---|---|---|---|---|---|
| #690 | no | **no** (5 vs 2) | **yes** — 5 map calls | 5 | 3/8 |
| #688 | no | **no** (23 vs 0) | **yes** — 5 map calls | 11 | 3/7 |
| #698 | no | **no** (28 vs 0) | **yes** — 3 map calls | 3 | 4/6 |
| #716 | no | n/a (`NO-SRC-READ`) | no — 1 call, at 51 | 0 | n/a |
| #704 | no | **no** (4 vs 0) | **yes** — 4 map calls | 4 | 1/1 |

**The finding, and it is sharper than "the map was read late":**

- **Orientation: 0 of 5.** No run read the map at bootstrap, and no run read it before source.
  Every single map access came *after* the source crawl had begun.
- **Use: 4 of 4.** Every run that touched source *returned* to the map afterwards — repeatedly
  (3–5 separate map calls each), which is the Admiral's signal that a read is use rather than
  ritual. A ritual read is one touch at bootstrap and never again; this is the exact inverse.
- **Citation: 4 of 5.** The plans cite map-sourced structure by name — `packets/physics.md`,
  `overlays/constraints.yml`, `reference/physics-unit-conventions.md`, the tyre-age decision
  doc. Two runs proposed *editing* map packets as part of their change.

**So the map was genuinely used — as a verification and justification resource consulted after
the seam was already found, never as the thing that found it.**

That is Tommy's gulf, measured on both sides at once: *"there is a map"* produced real
consultation and zero orientation. The listing was sufficient to make the map worth returning
to, and insufficient to make it the starting point.

This is the strongest thing in the baseline, and it holds regardless of the seam scores, the
tolerance ambiguity, or the give-away problem — none of which touch it.

---

## 4. F1's branch, and what it means for #304

The Admiral pre-registered two decisive branches. **The data lands on the second, the stronger
one:** runs do **not** consult the entrypoint first, so *the missing entrypoint was never the
binding constraint* — giving Commanders a path cannot fix what a path already failed to fix.

With the §1 scoping applied, the precise claim is narrower and still useful:

> In a repo that **lists** its architecture map in the auto-loaded bootstrap file, an ordinary
> agent consults that map for verification but never for orientation, and ignores the bootstrap
> reading list entirely.

**This locates #304 rather than undermining it,** exactly as the Admiral read it. #304's value
was never the path existing — the path exists here and produced no orientation. Its value is
closing the gulf: converting *"here is a map in a list"* into *"orient from this, before you
touch code, and report if you cannot."* The unconditional, sequenced instruction is the
untested variable. This arm shows the passive form does not work.

**Caveat carried forward:** whether #304's *active* form works on a **Commander** is untested,
because no Commander ran (§1).

---

## 5. Recommendations to the Admiral

1. **Do not extend to k=3.** Per the sequential rule: the ordering result is **unanimous** —
   5/5 source-before-map, 0/5 bootstrap-list compliance, 0/5 skill invocation. Replication buys
   nothing against a unanimous signal, and variance was never the binding constraint.
2. **Authorize a second pre arm (PRE-B) with the Commander forced to load**, on the same pin,
   before #304 merges. This arm (PRE-A) answers Tommy's question but does not test #304's
   surface. PRE-B is what pairs with the post arm. Five runs, same harness, one line changed.
3. **Resolve #332 before PRE-B**, not after — with project and global corpora indistinguishable
   at run time, a Commander-loaded arm has an unverifiable treatment, which is worse than the
   current arm's clean non-engagement.
4. **Rule on the tolerance ambiguity (#333)** before #307 pairs; the same wording must govern
   both arms.

---

## 6. Task-set shape, reframed per the Admiral's ruling

Not a degraded instrument — a differently-shaped one:

**5 ordering points · 2 seam points · 2 negative controls · 1 decline probe.**

| task | role as it turned out |
|---|---|
| #690 | seam test (degraded — body names the module basename) |
| #698 | seam test (partial — names classes, not paths) |
| #688 | **negative control** — body names the file verbatim |
| #704 | negative control (by design) |
| #716 | decline probe — no in-repo seam exists |

**#688 was predicted to be the cleanest test in the set and turned out to be a control.** Two
controls that agree is genuinely better than one, since a single control cannot separate "the
map does not help here" from noise — and here both controls behave identically to the seam
tests on the ordering axis, which is what makes the 0/5 orientation result hard to dismiss.

**The flip itself is the finding worth carrying to #307: a task's seam difficulty is not
readable from its title.** That is a fact about how tasks get selected for measurement, not
about these five, and it will recur on any future task set cut from titles.

**On the ordering axis and give-aways** (correcting my earlier read): the map-first instruction
is **unconditional** — it is not conditioned on whether the task needs the map. So on a
give-away task, skipping the map is *sensible task behaviour* and *simultaneously* a departure
from a standing instruction, and one observation records both. The axis therefore measures
**"is the map-first instruction discretionary in practice?"** and survives the give-aways
intact. Scored on all five and interpreted that way.

Here the answer is unambiguous: **in this arm the instruction was not merely discretionary, it
was never delivered** — no Commander loaded, so nothing instructed anything. The passive listing
in `CLAUDE.md` was the only map-first signal present, and it produced no orientation.

---

## 7. Method note

Tommy's steer — *"let's just make sure we're considering the context when we are doing
evaluation"* — is the reason §2 exists. The naive measure would have been reported as a clean
result without anyone checking what produced it. Both readings are now reported: the naive
ordering measure **and** the discriminated one, with the bootstrap check that establishes which
applies. They agree here, and the agreement is itself evidence rather than an assumption.

Reproduce: `runs/run-<N>/ordering.json` carries every tool call with its buckets and target;
the bootstrap and revisit checks are re-derivable from those arrays alone.

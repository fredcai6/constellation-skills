# Triage recommendations — issue #419

Ten candidates, all routed, none left unrouted. Authority: issue **filing** is delegated to this
Commander by the launch order's Inherited Latitude; issue **closing** is not, and none is proposed.
`gh issue create` is pre-cleared.

Consolidated to **five** issues rather than ten, because this epic exists partly to stop correct
findings being filed at the wrong granularity. Two candidates are `recommend-and-defer`: they have no
code target and are recorded here and in the run's workflow feedback instead of becoming tracker noise.

Nothing qualified for `fixed-now` at this step — every remaining candidate fails at least one rung of
the ladder, usually "no architecture impact" or "verifiable now". The genuinely bounded ones were
already fixed inside their gates and are recorded there (the stale four-field comments across four
files, and the two scope-discipline comments at their code sites).

---

## A — the governor still cannot fire on a worktree-dispatched run (from tc9)

**Labels:** bug, architecture weakness · **Disposition: filed as #440**

**What.** The binding store resolves a relative `--file` against the hook payload's `cwd`. For an agent
dispatched into a worktree that `cwd` is the **main checkout**, because `CLAUDE_PROJECT_DIR` is fixed at
session launch (#269). So the recorded key points at `<main checkout>/.agent-work/<work_id>/spine.json`,
which is not where the spine is. `_is_contained` passes because the *shape* is right, and the atomic
write creates parent directories, so the reading lands in a phantom `.agent-work/<work_id>/` inside the
main checkout while the engine reads the worktree copy and sees nothing.

**Importance.** This is the next thing standing between the governor and firing on real Constellation
runs, and it is the honest scope limit on #419's win. #419 proved per-agent identity end to end for
agents whose `cwd` is the project directory; a worktree-dispatched agent's reading still lands in the
wrong tree. Every wave this epic dispatches is worktree-based.

**Evidence.** Found by #419's g5 sweep dry run, 2026-08-05: **60 of 64 live entries** in
`.agent-work/.spine-rail-binding.json` were exactly this shape, including every spine claimed by #419's
own crews. Preserved at `.agent-work/archive/<date>-issue-419-governor-identity/evidence/binding-before.json`.

**Acceptance.** A worktree-dispatched agent's binding names its worktree's spine, and its `gauge.json`
lands beside that spine. Proven the way #419 proved its own claim: a live headless two-arm run, not a
fixture. A phantom `.agent-work/` must not appear in the main checkout.

**Out of scope.** The identity mechanism itself, which #419 settled.

---

## B — binding-store durability: no lock, no reaper, unvalidated paths, divergent id rules (tc1, tc5, tc10, and the unreaped key)

**Labels:** bug, cleanup, architecture weakness · **Disposition: filed as #441**

**What.** Four durability gaps in the same module, filed together because they are one owner's problem:

1. **No lock.** `_save_json_map` is atomic per write, but the surrounding load-modify-save is not, so
   two agents claiming at the same instant can lose one claim.
2. **No reaper.** A successful `release` is the only removal path, so an agent that dies or is
   cancelled leaves its key forever. #419's one-time sweeper was deleted after its single run, as that
   issue required.
3. **Unvalidated recorded path.** `--file` is taken as given, so a shell-mangled command can enter the
   store as if its fragment were a spine path.
4. **Divergent id rules.** `spine_rail` rejects a bad `agent_id` by denylist while `gauge_writer_hook`
   accepts by allowlist, so an id like `a:b` gets a binding written that the writer will never resolve.

**Importance.** Per-agent keying does not create these, but it widens the first two: a dispatched wave
now writes N entries where it wrote one. A lost write's symptom is **silence**, indistinguishable from
an idle governor — which reintroduces exactly the blindness #419 removes.

**Evidence.** (1) raised independently by two reviewers and a cold critic during #419, and commented at
`scripts/hooks/spine_rail.py:_save_json_map`. (2) commented at the release branch of the same file.
(3) the 2026-08-05 sweep found entries keyed by literal `$E` and `x`. (4) reported by #419's g2
implementer and confirmed at source by its reviewer — dict key only, no filesystem hazard.

**Acceptance.** Concurrent claims cannot lose a write (proven by a real concurrency test, not by
inspection). Abandoned keys age out by a rule someone chose. A non-`.json` `--file` is refused. One
id-validity rule, in one place, governing both modules.

**Out of scope.** Anything about *what* a reading means; this is the store's own durability.

---

## C — the engine's own output reads badly to the agent it is aimed at (tc6, tc7)

**Labels:** doctrine, architecture weakness · **Disposition: filed as #442**

**What.** Two observations from #419's live acceptance, where real dispatched agents met engine output
cold. (1) Agents read the `RAIL:` banner as a possible prompt-injection attempt and said so in their
transcripts. (2) The HARD refusal's remedy string — `Run: attach g1 --type refresh-request --field
seam=g1 --field why_ref=<why-id>` — assumes a Constellation-aware reader.

**Importance.** The rail is doctrine the engine *pushes* at the agent, and an agent that treats it as
hostile input discounts the very instruction the rail exists to deliver. The refusal is the governor's
one moment of contact with the agent it is governing: an agent that trips without the corpus loaded
gets an instruction it cannot act on. That is #331's offered-and-declined question wearing a new hat.

**Evidence.** Both observed in the archived transcripts of #419's acceptance run.

**Acceptance.** A cold agent with no corpus loaded, shown only the rail and a HARD refusal, can state
what it is being asked to do and do it. Measured on real agents, not judged by an author.

**Out of scope.** Redesigning the trip mechanic.

---

## D — `docs/agents/engine-config.json` does not exist, but every `config_ref` points at it (tc2)

**Labels:** missing doc, tooling · **Disposition: filed as #443**

**What.** Every spine and plan template carries `config_ref: docs/agents/engine-config.json`, and that
file is absent from this repo. The engine falls back silently, so the rework cap, the replan policy and
the human checkpoints are all defaults nobody chose.

**Importance.** These are the project's rigor dial. Running on unchosen defaults is a decision made by
omission, and it is invisible at every gate.

**Evidence.** Reported independently by three separate crews during #419 alone.

**Acceptance.** Either the file exists with values a human chose, or the templates stop pointing at it
and the defaults are stated where someone will read them. Silence is the thing to remove.

**Out of scope.** What the values should be — that is a Charter decision, human-only.

---

## E — nothing links the gauge record's field count across its assertion sites (tc4)

**Labels:** missing test, cleanup · **Disposition: filed as #444**

**What.** #419 found **seven** separate places asserting a four-field gauge record, across
`docs/GAUGE_WRITER_HOOK.md`, `gauge_writer_hook.py`, `gauge_reader.py` and `test_gauge_writer.py` —
and each was found by a different pass after the previous one reported clean.

**Importance.** This is the authoring-side blast-radius failure in miniature: a change to a format
silently strands every artifact asserting something about it, and the author is the only one positioned
to know and the one who does not look. Today the only thing keeping seven sites honest is that someone
looks.

**Evidence.** #419's g3 needed two review rounds; the handoff named one site, the first review found
two, the rework enumeration found six, and the re-review found a seventh in a fourth file.

**Acceptance.** A test imports `gauge_reader.REQUIRED_FIELDS` and asserts the document's field table
against it, so the next field someone adds fails a suite instead of stranding four documents.

**Out of scope.** The record's contents.

---

## F — `git worktree add` into the scratchpad fails on MAX_PATH (tc3)

**Disposition: recommend-and-defer.** Not filed: the target is crew doctrine, not this repo's code, and
this run has no authority over the corpus's crew guidance. Recorded here and exported through the run's
workflow feedback instead.

Every gate in #419 needed the isolate-the-revert move to measure non-vacuity, and every crew had to
discover the copy fallback for itself. One line in `crew-dispatch.md` would pay for itself immediately.

---

## G — an archived evidence artifact does not regenerate from its archived producer (tc8)

**Disposition: recommend-and-defer.** Not filed: it is a defect in **this run's own** evidence hygiene,
with no code target to file against.

`evidence/g4-assert-control-output.txt` has a trailing section appended from a command that was not
recorded. Every number in it reproduces independently, so no claim rests on it — but an archived
artifact that cannot be regenerated from its archived producer is not reproducible evidence, and the
next reader has no way to know which lines came from where. Found by #419's g4 reviewer. The general
rule worth carrying: archive the producer and the output together, or the output is testimony rather
than evidence.

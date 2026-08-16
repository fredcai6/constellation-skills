# Workflow feedback — `cleanup-b-context-identity`, 2026-08-16

Staged per `FENCE.md`. Honest reflection on how this run actually went, including
where I improvised and where the instructions fought each other.

## Where the tooling and the doctrine contradicted each other

1. **The context governor measured somebody else for the last third of this run.**
   From 12:46Z my `gauge.json` carried the cold-critic crew's context fill, not
   mine, because `SessionStart` bind-on-resume bound that crew's bare session key
   to my `spine.json`. I was shown 9% while genuinely at ~22%. This is the issue
   the wave was dispatched to fix, and it happened to the agent fixing it. Full
   capture in `notes-b.md` §2b — it is the strongest artifact this run produced and
   I did not have to construct it.

2. **Over HARD, the trip is a toll rather than a gate.** Every `advance --why`
   mints a new why-record, which invalidates the pending refresh-request's
   `why_ref`, so the next `start` needs a fresh `attach` keyed to the new id. Two
   extra verbs per gate transition, every transition, and it never once stopped me
   from proceeding. The agent paying the toll is the one complying.

3. **A design wave on the governor cannot stay under the governor's cap.** I
   crossed HARD at the `understand` step having read only the four artifacts the
   wave is about (`checklist_engine.py` 3551 lines, `gauge_writer_hook.py` 709,
   `gauge_reader.py` 519, `docs/GAUGE_WRITER_HOOK.md` 658). The 150K absolute cap
   and this subsystem's size are in genuine tension. Not a defect claim — a
   measured fact somebody should decide about.

4. **`verify-frame` cannot pass in this repo for any non-trivial frame.**
   `map/ids.jsonl` is empty, so `map_orient` resolves zero anchors, so every
   `decision:` anchor a frame cites is refused. The only ways through are to waive
   it or to reword anchors so they stop looking like anchors. I refused the second
   — that is gaming a check, not satisfying one — and the check's own gate text
   says it is a regression floor against map-*ignoring*, which my frame plainly is
   not. Filed as `tc1`.

## Where the launch order's stated baseline was wrong, and it mattered

- It said "no `docs/agents/` overlay in this repo". There is one
  (`ORCHESTRATOR_CONTEXT.md`, `GLOSSARY.md`, `CREW_CONTEXT.md`), and it carried a
  load-bearing rule I would otherwise have missed (the retired-learning-playbook
  section). The order's substantive point — that the governor's design intent lives
  in prose and in-code comments — was right.
- It warned that `CLAUDE_PROJECT_DIR` is fixed at session launch so a worktree runs
  the main checkout's hook against the main checkout's state (#269). In this
  session the variable was **unset entirely**, so the hook resolved the project dir
  from cwd and bound `path_source: payload_cwd` into the worktree. The hazard did
  not bite as described. A validation harness built on the order's assumption
  would have been testing a world that was not there.

Neither is a criticism of the order — both are exactly the "reconcile the order's
assumed baseline against the actual code" step paying for itself.

## What worked well

- **The cold critic earned its cost outright.** Eleven findings, three high and
  structural, and two of them were factual errors in my own documents that I had
  written down confidently. F1 retracted the load-bearing half of my
  recommendation; F2 supplied a measurement (82/395 session ids failing the
  proposed allowlist) that I had no way to guess. Dispatching it to a genuinely
  fresh context via `run_crew.py`, with "read exactly these four documents, but you
  may read source to check a specific claim", is the shape that produced this.
- **The pre-rulings with `@grade:` tags did their job.** `settled/human` on
  `decision:identity-not-time` is precisely what told me a measured contradiction
  was a float and not mine to revise. Without the grade I would probably have
  quietly redesigned around it.
- **The Honest-Null Clause changed my behaviour.** Knowing a measured negative was
  a complete deliverable is why I ran the probe before freezing a design instead of
  after.

## What I would ask for next time

- **A crew dispatched with `--handoff`/`--result` and no `--spine` should not be
  bound to the dispatcher's spine.** That single behaviour produced finding `tc2`
  and corrupted my own governor. Whatever the fix, the dispatch path should be able
  to say "this crew owns no spine".
- **Say in the order whether counting things in the live `.agent-work/` tree is in
  bounds for a critic.** Mine did it anyway and that is where its strongest
  evidence came from (F2's 82/395, the null owners, the literal `'$SID'`). It asked
  first, in its own feedback section, which is the right instinct — but it should
  not have had to.

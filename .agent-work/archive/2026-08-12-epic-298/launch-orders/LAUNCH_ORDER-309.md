# Launch Order: `commander-309 — issue #309, adversarial coherence sweep with seeded defects`

You start cold. Everything below is pasted, not pointed at.

## Mission

Issue #309 (spec B1, Testing pathways: coherence sweep): seed known incoherences into a **bounded corpus slice**, dispatch opinionated viewpoint subagents, and **measure seeded-defect recall and noise ratio.**

All findings land as **predictive episodes/proposals** in the store shipped by #301. **Direct doctrine mutation is failure** — if your sweep edits doctrine instead of proposing against it, the run has failed regardless of its recall number.

Seeding **must** operate on a copied slice, or the seeded incoherences must be reverted as an acceptance condition. **A test artifact must never become canon.** Treat that as the run's hardest safety property, not a footnote.

Acceptance: recall and noise reported; proposals attributable in the store; seeded material confirmed removed or never-live.

## The methodology bar — read this before you design the measurement

**A check that cannot fail is indistinguishable from one that passed.** This epic has paid for that line three times, and your issue is the one most exposed to it, because a recall measurement grades its own instrument.

- #300 shipped a single acceptance test that **could not falsify the property it existed to falsify** — it re-encoded both children's artifacts through the parent's encoder, so an environment-dependent encoder passed green. It had already survived **two independent reviewer rounds**, one of which returned a correct BLOCK on a different real defect. The diagnosis: *a reviewer given a handoff checks conformance to that handoff, and no handoff asked "can this test fail?"*
- #299's cold critic killed a losing condition **mathematically bounded at 0** — it could only fire when another condition had already fired. Same defect, in a rubric rather than a test.
- #299's transcript extractor self-tested against one field shape while real transcripts use others. Unfixed it would have missed **every** file read in every run and reported **total instrument failure as a clean finding**.

**Applied to you, concretely: before you trust a recall number, prove the sweep can MISS.** Run it against a slice containing a defect you know it should not find, and verify it reports the miss rather than scoring it green. A recall measurement whose instrument cannot register a miss is reporting its own construction, not the corpus.

Likewise for noise: prove the sweep can produce a false positive you then correctly reject, so the noise ratio is measured rather than assumed to be zero.

## Prior-Wave Verdicts (pasted)

**#301 — episode record + durable store. MERGED at `195e893`.** Verified on `origin/main`: `episodes/README.md`, `episodes/active/.gitkeep`, `episodes/retired/.gitkeep`. The store is genuinely in git — not nominally so, which was the check the commander itself hardened. The `active/`/`retired/` split realizes Tommy's ruling that **retirement moves the file** rather than annotating it in place.

**#302 — Tommy's two-bin ruling. No third bin; Assumption 6 stands; B0.3 unchanged.** Verbatim: *"machinize the mechanizable. we don't need stochastic reasoning for predictable logic... these are aspirations."* The third-bin candidates were not ruled *mechanizable* — they were ruled **not catastrophic**.

**Tommy's playbook ruling.** `.agent-work/LESSONS.md` is a dead end and is being retired by #308: episodes accumulate, consolidation lands in repo-local agent directions (`docs/agents/`), and live agents read local + global doctrine only. **Your proposals go to the episode store, never to LESSONS.md** (which is at its 20/20 cap and has no outcome field).

**#299's baseline — one finding that may bear on your dispatch design.** Five measured runs produced **zero `Skill` invocations**, with the `Skill` tool present and all 19 skills enumerated in every `init` event; the corpus was offered and declined on an ordinary planning brief. Your viewpoint subagents are **deliberately** dispatched, so this does not block you — but if your design assumes a subagent will pick up doctrine it was not explicitly handed, that assumption now has evidence against it. **Hand your viewpoints what they need; do not assume they will fetch it.**

## Two known defects that will bite this issue specifically

- **#321 — the episode store validates ids it LISTS but not ids it is HANDED.** A caller-supplied id escapes validation. You hand the store a large batch of seeded-finding ids programmatically, which is exactly the unvalidated path. **Fix it or work around it deliberately — do not discover it at scale.** Fixing it inside this issue is within your latitude if it is bounded; say which you chose and why.
- **#319 — episode working-tree bytes differ across worktrees under `core.autocrlf`.** Your acceptance condition *"seeded material confirmed removed/never-live"* is a comparison. If it compares raw bytes it will produce false differences. **Compare normalized content or blob OIDs.** I walked into this exact trap myself an hour after warning another issue about it — knowing the hazard is not the same as having it wired into your hands.

## Pre-Rulings

Overridable if evidence contradicts them — say so when overriding.

- decision:copied-slice-not-live-corpus — seed a **copy**. Reverting live canon is the fallback, not the plan; a revert that fails leaves a test artifact in doctrine.
  `@grade: settled/human · leans #309`
- decision:proposals-to-episode-store — all findings land as predictive episodes in `episodes/active/`. Direct doctrine mutation is failure, not a shortcut.
  `@grade: settled/inherited · leans #309,#308` (from spec B1)
- decision:prove-the-miss — the sweep must be demonstrated able to miss a defect and to raise a false positive, before either recall or noise is reported as a number.
  `@grade: settled/human · leans #309 · settle: none — a measurement that cannot fail is not a measurement`
- decision:viewpoints-are-handed-their-context — dispatch each viewpoint subagent with the doctrine it needs pasted inline; do not rely on it invoking a skill or reading a reference. Grounded in #299's zero-invocation finding.
  `@grade: guess · leans #309 · settle: if a viewpoint demonstrably fetches context unprompted, relax this`
- decision:sweep-scope-is-bounded — a bounded slice, named before seeding. If the slice grows during the run, that is a scope change and it is surfaced, not absorbed.
  `@grade: settled/human · leans #309`

## Honest-Null Clause

A measured negative is a complete, successful deliverable, reported with the same rigor as a win. **A low recall number is a result, not a failure of your run.** If opinionated viewpoint subagents turn out to find seeded incoherences poorly, or to drown them in noise, that is exactly the evidence the pathway exists to produce — and it is more useful than a flattering number.

Scoped nulls: a negative kills that specific test, never the idea class. *"This viewpoint set at this slice size got recall X"* — never *"adversarial sweeps do not work."*

## Inherited Latitude

**Delegated** — adjudicate and log: architecture/structural choices inside your deliverable; issue filing and closing on `fredcai6/constellation-skills` (`gh issue create/comment/close` pre-cleared — **file findings to the tracker directly, never bank them worktree-locally for someone to harvest**); fix-now triage; full test suite; `git push` to `epic-298/*`; merge when green **and** reviewed, gated on the CI check exit code read at source; **corpus surgery** — seeding and reverting defects in your bounded slice is explicitly pre-cleared by the latitude contract for measurement missions; model tier for sub-dispatches within Budget.

**Must float to me** — do not decide: scope changes (including slice growth); **two-bin routing rulings and pathway verdicts — Tommy's, always**; production defaults or user-visible behavior; anything out-of-taxonomy, with one line on why it fit no class.

## File Ownership

Working notes: **`notes-309.md`**. Sole writer.

> Never `findings-309.md`. The harness `Write` tool refuses any path whose basename contains "findings" — a guard against unprompted report-dumping that cannot tell this file was deliberately assigned. Three agents hit it in one epic.

## Workspace

```
C:/Programs/constellation-skills-wt/e298-309
branch: epic-298/309
base:   8de2faaa04d8db66847e3ac92d7f84cd89efa084  (origin/main)
```

**First step, before any git operation**, from inside that worktree:
```
py scripts/verify_worktree_isolation.py --here "C:/Programs/constellation-skills-wt/e298-309"
```
Must exit 0. Paste the output into your return.

**Do not touch `C:/Programs/constellation-skills`** — it holds Tommy's uncommitted work that a branch checkout would disturb. **Two other commanders are live** in `constellation-skills-wt/e298-304` and `constellation-skills-wt/e298-331`. Never enter either.

When editing global doctrine, edit canonical `skills/_shared/global-*.md` — **never** `skills/<role>/references/global-*.md`, which `install_constellation.py` regenerates at install time.

PR integration defaults to **server-side merge**.

## Inherited Context

**Python and CI — measured today; both interpreters are wrong in different directions:**
```
py     -> 3.12.13 (matches CI's pin) but pytest NOT INSTALLED -- `py -m pytest` fails outright
python -> 3.14.3  (two minors AHEAD of CI) with pytest 9.0.2
```
Run the suite with **`python -m pytest`**. **A local green is never the merge gate** — gate on the CI check exit code read at source, re-run at merge time. `Path.read_text(newline=...)` is 3.13+; it passed locally and failed CI on PR #320, costing 39 failures.

**Windows:** explicit `encoding='utf-8', newline='\n'` on every file write (default is the ANSI codepage; this epic lost a JSON delta to `UnicodeDecodeError: byte 0x97`). MAX_PATH is real — paths over ~180 chars break `git worktree add` on windows-latest. PR bodies via `gh pr create -F <tempfile>`; heredocs and PowerShell here-strings **fail for PR bodies**. Absolute paths for `git worktree add`, always.

**Engine:** never hand-edit spine/survey JSON. `--finding` text containing backticks is **shell-mangled and silently drops words** from the journal. On a **survey**, `record` is the re-record verb; `advance`/`reopen` refuse as gated-only — a reviewer hit this across five rounds in one issue and found it only by being refused. Command postconditions inherit the launcher's cwd (#315).

**Method:** *verify launch-order claims against the code* — this order states facts about the store, about #321 and #319; **if something here does not match what you find, the code wins, and say so in your return.** *Derive distribution claims from a command*, never from a test-output tail — "all N failures are in file X" comes from a `uniq -c`. *A round-trip test proves the parser, not the artifact.* *A non-reading must be visibly distinct from an uncollected one* — a defect the sweep did not find must be recorded differently from one it was never shown.

## Pre-empted Steps

- **Store choice** — `episodes/active/` per #301, shipped. Do not design a new store.
- **Destination for proposals** — the episode store, never LESSONS.md. Ruled.
- **Corpus-surgery clearance** — pre-cleared at contract time; you do not need to ask.
- **Worktree provisioning** — done.

## Budget

- **Model tier (required): Sonnet** for you. The issue is well-specified and the hard part is discipline, not reasoning depth. **Escalate to Opus and tell me** if the recall/noise design turns out to need it — that is a legitimate call, not a failure. Viewpoint subagents at Sonnet unless a viewpoint specifically needs more. **No Fable subagents at any tier — name the model explicitly on every dispatch.**
- At most 3 concurrent sub-dispatches. Two other commanders are live on this machine; if a usage-limit reset is near, defer rather than launching into it. Rewrite your crash-resume state note before **each** detach.

## Stop Conditions

Stop and return when: the slice would grow beyond what you named; a two-bin routing question or pathway verdict arises; you cannot demonstrate the sweep can miss (that is a genuine stop — report it rather than reporting recall anyway); budget crossed; **or you need context this order does not cover and cannot safely proceed without — return-and-query me, I answer and continue you.**

Asking up is always sanctioned and always legitimate. This epic has one logged Admiral error where a commander's float went unanswered and it merged on its own reading — that failure was mine. The commander on #299 floated twice, proceeded on its own recommendation while telling me what it was doing, and was right both times. That is the shape I want.

## Return Shape

Deliver your artifact and verdict **before** going idle — an idle notification with no artifact reads as stalled, not done.

1. **Verdict**: recall and noise ratio, with the slice and viewpoint set named.
2. **Evidence the instrument can fail** — the deliberate miss and the deliberate false positive, with what each produced.
3. **Proposals attributable in the store** — episode ids, and how attribution is established.
4. **Seeded material confirmed removed or never-live**, compared by normalized content or blob OID, never raw bytes.
5. **Your disposition of #321** — fixed or worked around, and why.
6. **Map impact** and **triage candidates** (filed to the tracker, numbers listed here).
7. **Workflow feedback** — what this order got wrong, what tooling made harder than necessary. Blunt is useful.
8. Your `verify_worktree_isolation.py --here` output.
9. **PR number and its CI check exit code, read at source.**

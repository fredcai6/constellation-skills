# Review Result — g4: live acceptance, a real trip from a per-agent reading

## Assigned Gate
`g4` — issue-419-governor-identity. Worktree `C:/Programs/constellation-skills-wt/epic418-a-419`,
branch `epic-418/a-419-governor-identity`, HEAD `f8b0743`. Control checkout
`C:/Programs/constellation-skills` on `main` at `990712f`, clean.

## Result
`APPROVE`

The trip is real, it came from the acting agent's own context, and I could not construct any world
in which the change did nothing and this evidence still looks like this.

Survey driven through the engine at
`.agent-work/issue-419-governor-identity/g4-review/review.json` — 23 checks, all visited, all pass,
consolidated to APPROVE. Fowler record at the same directory's `FOWLER_PASS.json`.

## What I did NOT do
I did not import either hook under test, and I did not rest on the implementer's checker. I wrote my
own parser and re-derived every number from the raw transcripts. I did re-run the implementer's
scripts afterwards, as a cross-check only.

## Handoff compliance
Met. The vehicle is the one the handoff named — headless `claude -p`, cwd inside a disposable
sandbox, a settings file wiring `PostToolUse` to this worktree's two hooks by absolute path (I read
both settings files and both launch commands). Six agents ran, covering every role the handoff
required: a parent that claimed its own spine, two dispatched siblings reading deliberately
different amounts, one subagent that claimed nothing, and one depth-2 nested dispatch. HARD was
reached on real reading (0.329482 of a 1M window), not SOFT. One agent released. The sandbox had its
own binding store, and the main checkout's live store is untouched — 6 keys, none referencing
`accept419`, none composite. `identity_resolution_ms` is present on all three dispatched records
(0.0776–0.0837 ms), inside the 100 ms budget by three orders of magnitude.

## Scope drift
None. `git status --porcelain` filtered to exclude `.agent-work` paths is empty — nothing outside
`.agent-work/` is uncommitted. The tracked `main...HEAD` diff touches only files committed at g1–g3,
all already reviewed and closed; g4 added no source change. The acceptance harness lives outside the
repo at `scratchpad/accept419/` and never entered the diff.

Cosmetic only: the g4 implementer plan's engine side-directories landed at
`.agent-work/issue-419-governor-identity-g4/`, a sibling of the issue workbench, whereas the g1–g3
review side-directories landed inside it. Still under `.agent-work/`, so not a scope breach.

## The named falsifiers — each checked, each result

| # | falsifier | result |
|---|---|---|
| 1 | binding key bare rather than `<uuid>#<hex>` | **did not fire** |
| 2 | the two agents' fills match each other | **did not fire** |
| 3 | **the pairing is crossed** | **did not fire — 2 of 2, and 4 of 4 across every agent that got a reading** |
| 4 | `observed_at` predates the agent's first chunk read | **did not fire** |
| 5 | `advance` succeeded despite a `>= hard` reading | **did not fire** |
| 6 | the control arm also tripped | **did not fire** |
| 7 | a reported output is paraphrased | **did not fire** |
| 8 | an identity value traces to the harness | **did not fire** |

**1 — key shape.** Read live from the sandbox binding store. Three keys: one bare
`e0063a6f-5f31-473e-938a-1feea2863166` holding only `wk-parent`, and two composite —
`…#a6df3902f0bf72c29` → `wk-alpha`, `…#a69093b8ea2f159f6` → `wk-bravo`. My own regex check confirms
each composite is `<36-char uuid>#<lowercase hex>`, that the uuid segment equals the counted session
directory name on disk, and that each hex segment has its own `agent-<id>.jsonl` in that session's
`subagents/` directory.

**2 — distinct fills.** Recomputed from each agent's own transcript: ALPHA 0.329482 (329 482
tokens), BRAVO 0.102211 (102 211 tokens). Peak fills across the whole run also differ (0.330102 vs
0.102629), so the divergence is a property of what each agent actually read, not of one sampling
instant.

**3 — the pairing. This is the one that carries the verdict, so here is my full route.**

I wrote `rev_recompute.py` from scratch. It imports neither `gauge_writer_hook` nor `spine_rail`, and
does not call `recompute.py`. It re-derives `total = input_tokens + cache_creation_input_tokens +
cache_read_input_tokens` over the 1 000 000-token `claude-sonnet-5` window, and it pins the
comparison to each gauge's own `observed_at` rather than to a transcript tail.

- key `…#a6df3902f0bf72c29` → `wk-alpha`. `wk-alpha/gauge.json`: `observed_at
  2026-08-06T04:32:19.675Z`, `fill_fraction 0.329482`. `agent-a6df3902f0bf72c29.jsonl` holds
  **exactly one** record at that instant, `isSidechain` true and `agentId == a6df3902f0bf72c29`,
  totalling **329 482** tokens = **0.329482**. Match.
- key `…#a69093b8ea2f159f6` → `wk-bravo`. `observed_at 04:33:30.534Z`, `fill 0.102211`.
  `agent-a69093b8ea2f159f6.jsonl` holds exactly one record at that instant, **102 211** tokens =
  **0.102211**. Match.
- parent: 0.094663 at `04:35:45.657Z`, recomputed from the parent's own **non-sidechain** records.
- depth-2 ECHO: 0.064216 at `04:35:11.133Z`, recomputed from `agent-acbcb46bdf651a3c7.jsonl`.

**COUNT: 2 of 2 for the dispatched sibling agents; 4 of 4 across every agent that got a reading.**

Four anti-cross tests, all clean: each gauge's sampled instant appears in **no other** agent's
transcript and not in the parent's, so no gauge could have been sourced from a different agent. Two
further cuts I added on my own initiative:

- every `agent-<id>.jsonl` carries exactly **one** distinct `agentId` — its own — and is entirely
  `isSidechain`, so the files cannot be confused with each other or with the parent's;
- the counterfactual: a parent-transcript fallback at ALPHA's sampled instant would have read
  **0.047769**, not 0.329482 (at BRAVO's instant, 0.051667, not 0.102211). The numbers demonstrably
  did not come from the parent.

**4 — `observed_at`.** ALPHA's first `Read` 04:31:21.087Z vs `observed_at` 04:32:19.675Z (58 s
later); BRAVO 04:32:59.547Z vs 04:33:30.534Z (31 s later). Stronger still, the four sandbox
`gauge.json` mtimes are 21:32:20.3, 21:33:31.2, 21:35:11.8 and 21:35:46.3 local (UTC−7) — each
landing 0.2–0.6 s **after** the `observed_at` it carries, interleaved across the live five-minute
run. They were written during the run at four separate moments, not pre-seeded and not
batch-written afterwards (`recompute.py` did not exist until 21:38).

**5 — the refusal.** Read from the state, not the report. `wk-alpha/spine.json`: top-level
`refusals: 1`, `tasks.g1.status: in-progress`, `g2` still `pending`; its journal holds exactly one
entry, `verb: start`, with **no advance entry at all**. All three other treatment spines:
`refusals: 0`, `g1: complete`. ALPHA's `g1` postcondition `c1` is `exit 0` and shows
`satisfied: false`, so the refusal cannot be attributed to a failing check — the only thing that
could refuse was the trip.

**6 — the control.** All four control spines `refusals: 0`, `g1: complete`. Detail below under close
criterion 5.

**7 — verbatim.** I re-extracted every `checklist_engine` `tool_use` and its paired `tool_result`
straight out of ALPHA's and BRAVO's own transcripts with my own extractor. ALPHA's `CONTEXT 12% (>=
soft)`, `CONTEXT 27% (>= hard)` and the `REFUSED: g1: context at 33% … EXIT_CODE:1` block all match
the implementer's quotes exactly. I checked the `EXIT_CODE:1` marker specifically, because run 1 was
discarded over exactly that: grep for `EXIT_CODE`, `EXITCODE` and `LASTEXITCODE` across both prompts
and `make_prompts.py` returns nothing — ALPHA appended `; echo "EXIT_CODE:$?"` to that one command
on its own initiative. BRAVO's `CONTEXT 9% (>= soft)` and `g1 -> complete` match my extraction too.

**8 — identity provenance.** I did not rely on the implementer's grep. I ran a broader sweep of my
own design: every file under `scratchpad/accept419` whose mtime **predates the counted session
start** (21:31:06 local), excluding run-1 and smoke artifacts — **71 files**, more than double the
32 the implementer walked — grepped for `agent_id`, `agentId`, each of the five agent ids the run
produced, and the session uuid prefix `e0063a6f`. Every pattern returned **0 files**. The handoff
named three evasions the grep alone cannot close; each is closed separately:

- **pre-seeded binding file** — the sandbox binding store did not exist before the run, and its live
  mtime is 21:35:15, mid-run; the ids it holds are run-2's.
- **hand-made `subagents/agent-<hex>.jsonl`** — the run-2 session dir `e0063a6f` is **not** in the
  pre-run set (which held only run-1's `b9e77515` and `memory`), so the session dir, its
  `subagents/` directory and all five `agent-*.jsonl` were created by the harness during this run. I
  reproduced that set difference on disk myself, and confirmed run 1's five agent ids are disjoint
  from run 2's. The transcripts are 32 KB–910 KB of real model turns with per-turn `usage` blocks
  and matching `.meta.json` files.
- **environment variable** — neither settings file has an `env` block, neither launch command sets
  one, and grep for `CLAUDE_`, `"env"`, `setx` and `$env:` across both settings, both launch
  commands, both prompts, `build_sandbox.py` and `make_prompts.py` returns nothing.

I also confirmed the agents were not coached: the prompts never contain the words trip, gauge, hard,
soft, band, fill or refusal, nor any target number.

## Close criteria — each met, with evidence I personally reproduced

**1. A trip fired from a per-agent reading, verified by my re-computation.** Met. 329 482 tokens over
the 1 M window = 0.329482, from the single record at 04:32:19.675Z in `agent-a6df3902f0bf72c29.jsonl`
— byte-for-byte the `fill_fraction` in `wk-alpha/gauge.json`. The refusal is in the state file, not
just the report. And ALPHA's own transcript shows the reading **moving** across its run — 12%, then
27%, then 33% at three separate engine calls — which no frozen, parent-sourced or fabricated value
could do. Cross-check: I re-ran `recompute.py`, exit 0, output byte-identical to the archive.

**2. Pairing, parent, release, non-claimer.** Met, all four halves. Exactly one bare key, holding
exactly one spine (`wk-parent`), and the parent got its own reading (0.094663, recomputed from its
own non-sidechain records); its gauge carries only the four required fields, no
`identity_resolution_ms`, so the top-level record shape is unchanged. ECHO released — `wk-echo`
`engine_session.status: released`, journal `start` then `advance` — and there is **no** composite key
ending in `acbcb46bdf651a3c7` anywhere in the store, while the parent's bare key survived that
release. CHARLIE (`a44094d0026a4e495`) has no key, and a `find` over the whole treatment sandbox
returns exactly four gauge files, one per claimed spine, with no fifth directory and no stray
sidecar. DELTA, which dispatched ECHO but claimed nothing itself, likewise bound nothing.

**3. Identity path and resolved key shape recorded.** Met, with a caveat I want on the record. The
key shape is recorded directly and is unambiguous: a silent fallback to the bare-key path would have
left three spines under one bare key, exactly as the control arm did — the two states are visibly
different, not the same state with different labels. Which path each record took is carried by the
presence or absence of `identity_resolution_ms`: it rides **only** the three dispatched-agent records
and is absent from the parent's. **Caveat:** that is an inference from a timing field, not an
explicit path label such as `source=payload-agent-id`. It is sufficient here because the alternative
path is directly observable in the same evidence, but a future run without a control arm would have
less to lean on.

**4. Nested depth-2 result.** Met, and independently verified: **RESOLVED**. I read
`agent-acbcb46bdf651a3c7.meta.json` directly — `spawnDepth: 2`, `parentAgentId: a3ab804c97222f9c5`
(DELTA). Its transcript sits directly under the **root** session's `subagents/` directory, **not**
under DELTA's — which is precisely why `derive_subagent_transcript`, which builds
`<root-transcript-minus-.jsonl>/subagents/agent-<id>.jsonl`, resolves at depth 2 at all.
`wk-echo/gauge.json` holds 0.064216 at 04:35:11.133Z; the single record at that instant in ECHO's own
transcript totals 64 216 tokens, `isSidechain` true, `agentId` its own, and that instant appears in
no other transcript. This is a genuinely new fact — the pre-build probe only ever captured
`spawnDepth 1` — and it is the good outcome: the governor is **not** blind for nested agents. Note
the pairing held even though ECHO's composite key had already been removed by its own release, so I
recomputed it from the spine directory rather than through the store.

**5. Control arm silent and byte-identical.** Met, and the control is cleaner than the report
claims. I diffed the two prompts myself normalising **only** the sandbox directory name — `diff`
exits 0, so the script the agents followed is byte-identical between arms. I diffed the two settings
files normalising only the hook directory — exit 0. Crucially, I checked which engine each arm names,
and **both prompts point at the same `checklist_engine.py`, the worktree's** — so the trip
implementation is held constant and the only variable in the whole experiment is which directory the
two `PostToolUse` hook scripts load from. I verified the control hook directory is genuinely
unmodified: `C:/Programs/constellation-skills` is on `main` at `990712f`, clean, and both its hook
files differ from the worktree copies (main's `spine_rail.py` has no `binding_key` function at all).

Result: zero readings for any dispatched agent, four `ambiguous-binding` sidecars, every `g1`
complete, `refusals: 0` everywhere. And the control gauge pipeline was demonstrably **alive**, not
merely absent — the control parent got one reading, 0.047721, sampled 8 seconds before the second
claim made the bare key ambiguous. The silence is the pre-fix blindness, not a broken control.

The sharpest number in the whole run, which I recomputed myself: control ALPHA independently reached
**0.329265** — against treatment ALPHA's 0.329482, a 0.02% difference — and the pre-fix governor
wrote nothing and let it advance.

## The two disclosures, weighed on their merits

**Treatment run 1, discarded.** Honest, and the discard **cost** the implementer evidence rather than
buying it. The counted run is genuinely the re-run: the counted binding store carries session
`e0063a6f`, whose directory was created 21:31:06, while run 1's `b9e77515` ran 21:23–21:28 and its
whole sandbox was moved to `accept419/run1/` before the counted sandbox was regenerated (corpus
mtimes 21:30:16). The two runs' agent ids are disjoint sets. Grepping the entire counted evidence
tree for `b9e77515` returns two files, and in both it is named legitimately as a pre-existing
artifact. No leak.

On whether discarding was convenient: I read run 1's archived spines. **Run 1 already had the win** —
`wk-alpha` `refusals: 1`, `g1: in-progress`, gauge 0.332189, composite key `…#ab7d5c3b6d5c61865`
present. It was discarded because `wk-bravo` and `wk-echo` were never even started (`g1: pending`, no
`refusals` field), which meant no second dispatched agent, hence no pairing count and no
distinct-fills falsifier. Discarding it made the bar **harder**, not easier.

**A bonus the implementer did not claim:** the HARD trip therefore fired in **two independent runs**,
with different session uuids, different agent ids and different fills (0.332189 and 0.329482). That
is an unplanned replication and it strengthens the result.

**BRAVO's classifier-blocked report.** **Stronger**, not weaker — and I verified that rather than
accepting the argument. The concern is legitimate: material selected after the fact by the party
being reviewed is normally weaker evidence. What defeats it here is that the selection is checkable,
and I checked it. My own extractor over `agent-a69093b8ea2f159f6.jsonl` reproduces exactly what the
implementer reported: two `current` calls, the second ending `CONTEXT 9% (>= soft)`, and an `advance`
returning `g1 -> complete`. Nothing omitted, nothing added. A `tool_result` is a machine record no
agent composed, so it cannot be paraphrased or flattered; and the selection risk is neutralised
because the raw transcript is archived alongside it, so any reviewer can redo the extraction. The
refusal hit BRAVO's **final message** only, after all its tool calls had completed, so no observation
was lost.

## Trying to explain the trip WITHOUT the change

Nine attempts. Each is killed by evidence I reproduced.

1. **A parent reading leaked into a child's spine.** The parent's transcript at ALPHA's sampled
   instant reads 0.047769, not 0.329482 — a 7× gap.
2. **The harness wrote the gauge files.** The four gauge mtimes land 0.2–0.6 s after the four
   *different* `observed_at` values they carry, spread across a five-minute window during which the
   implementer's process was blocked on the `claude -p` call (`out-treatment.txt` not written until
   21:36); `recompute.py` did not exist until 21:38. Faking this would require knowing each agent's
   token total in real time.
3. **The control arm was mis-wired so it could not trip.** Both arms name the same
   `checklist_engine.py`, so the trip code is identical; and the control's gauge pipeline
   demonstrably worked — it produced a parent reading and four `ambiguous-binding` sidecars.
4. **The control agents simply read less.** Control ALPHA reached 0.329265 against treatment ALPHA's
   0.329482 and got no reading and a clean advance.
5. **Corpus size alone causes the trip.** Refuted by 4.
6. **A stale or pre-existing gauge.** The binding store and every gauge file were absent before the
   run; each `observed_at` postdates its agent's first `Read` by 31–58 s.
7. **The two fills are one number sampled twice.** 0.329482 vs 0.102211.
8. **A crossed pairing that still looks right.** Four anti-cross timestamp-uniqueness tests, plus
   every `agent-<id>.jsonl` carrying exactly one `agentId`, its own.
9. **The agents were coached.** The prompts contain none of the relevant vocabulary and no target
   number.

**What this run does NOT establish, stated plainly:** one platform, one model (`claude-sonnet-5`),
sequential dispatch only, one counted run (replicated once by the discarded run 1). Concurrent claims
against the unlocked binding store are a real, untested property — see the triage candidates.

## Code/doc quality
Good. Fail-visibly is honoured on both sides: the control arm's hooks wrote `gauge-skip.json` records
naming `ambiguous-binding` with a `candidate_count` rather than silently writing nothing, which is
what made the negative control readable at all. Honest self-correction is visible twice and disclosed
both times — the first pairing draft compared transcript tails and self-reported a false mismatch
before being pinned to `observed_at`, and the first control assertion exited 1 on an over-broad "no
reading anywhere" claim and was **tightened** rather than weakened (I read the corrected script; it
asserts strictly more). `make_prompts.py` deserves specific credit: generating both arms from one
template with a single substituted field is what *structurally* guarantees the byte-identical-script
claim I verified, rather than leaving it to be asserted.

Fowler refactoring pass: record at `.agent-work/issue-419-governor-identity/g4-review/FOWLER_PASS.json`,
`verify_fowler_pass.py` exits 0 — 12 smells, flagged `duplicated-code`, `data-clumps`,
`shotgun-surgery`, overridden `long-method` with a logged standard. The three flags share one root:
the "arm" concept is re-derived in each of the five harness scripts. All observations, no blockers.
The shipped hook diff was Fowler-passed at g1–g3 and is closed; I did not re-pass it.

Suite: `python -m pytest -q` on the branch — **1667 passed, 2 skipped, 550 subtests passed** in
432 s, exit 0.

## Map impact verdict
- **Evidence supports claimed change:** yes. The claim "the context governor now produces a per-agent
  reading for dispatched agents, including depth 2, and refuses `advance` on it" is exactly what I
  reproduced from the raw transcripts and the spine state files.
- **Constraints not violated:** yes. The sandbox kept its own binding store and the main checkout's
  live store is untouched (6 keys, none composite, none referencing `accept419`). The 100 ms
  identity-resolution budget is now **measured**, not assumed.
- **Notes match the diff:** yes. The notes claim no source file changed; git confirms g4 added nothing
  tracked. The named anchors are the ones the observed behaviour actually runs through.
- **Decision candidates surfaced:** yes. The nested-dispatch question is answered and surfaced as a
  decision candidate rather than silently edited into the doc — correct under g4's scope.
- **Durable context routed:** partly. The depth-2 fact is surfaced in Map Impact but
  `docs/GAUGE_WRITER_HOOK.md` still says nothing about nested dispatch. Routed to Cartographer as a
  triage candidate rather than blocked, since g4's scope forbids widening.

## Reconciliation check
No divergence needing rework. One doc-reconcile candidate (depth-2 behaviour, below). The implementer
also flags that the map-anchors packet `context/g4-implement.json` has an empty `files` list and no
anchors, so Map Impact was written from the code rather than from the packet — worth fixing upstream
of the next gate.

## Blockers
- none.

## Out-of-scope observations (triage candidates, filed as `tc1`–`tc4` on the survey)
1. **`g4-assert-control-output.txt` does not reproduce from `g4-assert_control.py`.** The archived
   output carries a trailing 8-line section ("what the control arm's agents ACTUALLY consumed") that
   the archived script has no code to emit, so it was appended from an unrecorded command. Every
   number in it independently reproduces — I recomputed all five from the control transcripts (ALPHA
   0.329265, BRAVO 0.102895, CHARLIE 0.062080, DELTA 0.027522, ECHO 0.065880) — so nothing about the
   claim is wrong. But an evidence file that cannot be regenerated from its own archived script is a
   hygiene defect. Fold the section into the script, or head it with the command that produced it.
2. **`docs/GAUGE_WRITER_HOOK.md` carries nothing about nested dispatch**, yet g4 established the
   durable fact that a depth-2 agent's transcript is written directly under the root session's
   `subagents/` directory. Route to Cartographer.
3. **The archived harness re-derives the "arm" concept in each of its five scripts** (duplicated
   `check()` and `slug_for()`; a layout change would touch all five files). Only worth doing if a
   second live-acceptance run is planned.
4. **The binding store has no cross-process lock** — the implementer's own candidate, and I would
   raise its priority. `load_binding` → mutate → `save_binding` is read-modify-write on one JSON
   file, and per-agent keying makes a wave write N entries where it used to write one. g4 dispatched
   sequentially by choice, so this is untested. A lost write means that agent silently gets no
   reading — the exact blindness this issue set out to remove.

Two further observations carried from the implementer, which I confirmed in the transcripts and
consider worth keeping: agents outside a Constellation run read the engine's `RAIL:` banner as an
injection attempt (the treatment parent said so unprompted, in its own final answer), and a HARD
refusal leaves an agent with no scripted exit unless it already knows the `attach … refresh-request`
verb.

## Workflow Feedback
- **Handoff gaps:** the reviewer handoff says "Recompute from the raw transcripts yourself" but does
  not say **which** transcripts are canonical. The evidence tree ships copies under
  `g4-transcripts-treatment/`, while the originals are still live under `~/.claude/projects/<slug>/`.
  I worked from the live originals and verified the copies match by byte size, but the handoff should
  name the live path as the source of truth, because the whole point of the exercise is not to trust
  a copy the reviewed party made.
- **Context rediscovered:** three things. (a) The token formula — that `fill_fraction` is
  `(input + cache_creation + cache_read) / MODEL_WINDOWS[model]` — is only discoverable by reading
  `find_latest_usage`, which is the code under review. A reviewer told to recompute independently
  needs the formula stated in the handoff, or the independence is nominal. (b) That the sandbox and
  both live session directories still exist on disk. That is the single most valuable fact for this
  review and the handoff never mentions it; I found it by looking. (c) That both arms deliberately
  share one `checklist_engine.py`. That is the cleanest property of the whole experiment and neither
  the handoff nor the implementer result says it — I had to derive it by diffing the prompts.
- **Instructions improvised around:** the reviewer skill's Fowler pass assumes a code diff. This gate
  ships none. Rather than take the documented escape hatch — skipping the pass under an independent
  reviewer's co-sign, which I cannot self-grant — I ran the pass against the g4 work product that
  does exist, the acceptance harness, and said so in `diff_ref`. That felt like the closest compliant
  thing, but the skill should say explicitly what to smell-test when the gate's deliverable is an
  observation rather than a diff.
- **What would have made this easier:** one line in the handoff giving the live transcript path and
  the token formula. Those two facts are the entire difference between a reviewer who recomputes and
  a reviewer who re-reads.

## Return status
`complete`

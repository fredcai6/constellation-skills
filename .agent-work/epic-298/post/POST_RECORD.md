# POST — the Commander-loaded post-#304 arm (epic #298, issue #307)

**This is a HITL evidence package. Tommy adjudicates the B3 verdict. This record does not
adjudicate it, and where the evidence supports two readings both are given.**

**Arm captured. Five runs, five verified Commander loads, five clean transcripts, corpus
identical across every per-run witness, nothing landed in f1Brainz.**

The headline is a **measured positive on the ordering axis and a measured negative on the
bootstrap axis**, and the two are not in tension — see §4, which is the whole record.

Numbers in this file are pinned to branch `epic-298/307`. **This repo squash-merges, so at
PR time every SHA below stops existing in `main`; re-pin to the PR number.**

---

## READ THIS BEFORE READING ANY NUMBER

**POST pairs with PRE-B. Neither pairs with PRE-A (#299).** Run lengths are 10–61 in PRE-A and
73–148 across PRE-B/POST. **Only the boolean `map_before_src` transfers.** Raw indices are
comparable *within* the PRE-B/POST pair, because both arms are Commander-driven at the same
scale, and they are used that way in §5 only — never against PRE-A.

**The criterion was pre-registered before any POST number existed.**
`PRE_REGISTRATION.md`, committed at `a4993ec` while three captures were still in flight with
`status: "launched"` and no `treatment.json` on disk. It fixed the denominator, the handling of
the reserved literals, the four-cell reading of the two witnesses, and the threshold. It is
checkable against this branch's git history rather than trusted. **Tommy may overrule any line
of it; that is the point of writing it down early rather than late.**

---

## 1. The one variable

| | PRE-B | POST |
|---|---|---|
| corpus `source_commit` | `74953936` | `3595955` |
| contains #304 (`5d2585b`) | no | **yes** — `git merge-base --is-ancestor`, verified |
| contains #304 post-archive (`9a0cb17`) | no | **yes** |
| `SKILL.md` concat sha256 | `fcb6863163c97273d021…` | `59019a4d92b999907b58…` |
| deep tree sha256 | `4c2e6465889f8d3fd074…` (233 files) | `bb66c3556dd91fcd743e…` (264 files) |
| brief bytes | — | **content-identical, all five runs** |
| pin, task set, model, env scrub | — | identical |
| scorers | — | **byte-identical** (§8) |

**Limitation that no number in this record repairs, stated first because it bounds everything
after it: the manipulation is `74953936` → `3595955` — 8 days and +31 files — not #304 in
isolation.** `merge-base` proves #304 is *contained in* that delta; it proves nothing about
what else is. Attributing the effect to the map-first contract specifically rests on the
mechanism evidence in §5, not on the ordering number alone.

## 2. Treatment verification, and the three-hop delivery

**All five runs: `TREATMENT-VERIFIED`.** Both witnesses agree on every run: a `Skill` call to
`constellation-commander` at index 0, and a matching `Base directory for this skill:` line
resolving to `C:\Users\fredc\.claude\skills\constellation-commander` — the **global** copy, as
#332 predicts.

**But "the Commander loaded" is hop 0 of three, and this arm is the first to measure the other
two.** Filed as **#393**: measured against the installed corpus,
`constellation-commander/SKILL.md` contains **zero occurrences of the word "map"** and
`references/commander-core.md` contains zero of `map_orient`. The #304 contract exists **only**
in `templates/COMMANDER_SPINE.template.json`. An agent that loads the Commander and plans
without materializing a spine never encounters the contract at all.

| hop | what it establishes | witness | result |
|---|---|---|---|
| 0 | the Commander skill loaded | `verify_treatment.py` | **5 of 5** |
| 1 | the spine was materialized, so the contract text reached the subject | `contract_delivered` (transcript) **and** `spine-materialization.json` (filesystem) | **5 of 5**, two independent oracles agreeing |
| 2 | the contract's instrument actually ran and returned | `map_orient` calls confirmed by a verdict token in the tool result | **5 of 5**, 32 invocations, every first call `RESOLVED` |

**This is what makes the arm's verdict attributable.** PRE-B also scores `contract_delivered`
5 of 5 — its subjects drove spines to `plan` too — with **zero** `map_orient` calls, because
that corpus has no such tool. So the PRE-B/POST contrast is precisely **same delivery path,
different contract content**, not "did they use the Commander at all".

## 3. Corpus fingerprint — witnessed per run, not once per arm

| | value |
|---|---|
| BEFORE (pre-run 1) | deep `bb66c3556dd91fcd743e…`, 264 files, 19 skills, `source_commit 3595955` |
| AFTER (post-run 5) | **identical** |
| per-run witnesses | **5 enumerated, 1 distinct** |

Per-run fingerprints exist because the treatment lives on a **mutable global** (`~/.claude/skills`)
that sibling agents in this session are standing-pre-cleared to re-install into. A single
BEFORE/AFTER pair cannot distinguish "stable throughout" from "changed and changed back".

**The comparison is on the DEEP digest, not the headline one.** `skillmd_concat_sha256` covers
only each skill's `SKILL.md` and is therefore **blind to `templates/` and `scripts/` — where
the entire contract under test lives.** A shallow check would report "stable" through a
re-install that rewrote the treatment. Filed as **#395**. This arm additionally asserts the
installed **bytes** — `scripts/map_orient.py` present, and the spine template carrying the
anchor phrase *"before you open any source file"* — because `corpus_marker.source_commit` is
read verbatim out of `CORPUS.json`, a **self-report written by the installer**, which is
exactly the artifact that would lie in a #344-shaped failure.

**On the install fingerprints this arm could not find.** `LAUNCH_ORDER-307` named
`baselines/CORPUS_FINGERPRINT_{PRE,POST}_INSTALL.json` as the provenance record for the #344
install. They were absent from the entire `.agent-work/` tree when this arm checked. The
Admiral has since established why and fixed it: **the files were real but existed only in his
main checkout's working tree, uncommitted**, so no commander could reach them — the #344
install genuinely had no reachable provenance record. Now committed at `5d9e71a`. **This arm
deliberately does not switch to them.** An instrument that reads its own provenance beats one
that trusts an Admiral's, and the per-run witnesses in the table above are what the poolability
claim rests on.

## 4. THE FINDING — orientation moved before source, and did not move to bootstrap

**`map_before_src`: PRE-B `False` on 4 of 4 · POST `True` on 4 of 4.**
**`read_at_bootstrap`: PRE-B 0 of 4 · POST 0 of 4.**

| task | PRE-B `map<src` | POST `map<src` | PRE-B first map / first src | POST first map / first src |
|---|---|---|---|---|
| #690 | **no** | **YES** | 36 / 23 | **17 / 25** |
| #688 | **no** | **YES** | 27 / 23 | **21 / 37** |
| #698 | **no** | **YES** | 57 / 25 | **29 / 46** |
| #704 | **no** | **YES** | 23 / 7 | **19 / 22** |
| #716 | `NO-MAP-READ` | `NO-MAP-READ` | `NO-MAP-READ` / `NO-SRC-READ` | `NO-MAP-READ` / `NO-SRC-READ` |

**#716 is the literal row in BOTH arms**, so the boolean denominator is **4 in both** — fixed
in `PRE_REGISTRATION.md` §1 before the numbers existed, not chosen after seeing them. Reporting
this as "4/5" either way would be defective.

**Both halves are the finding, and neither should be dropped:**

- **The re-anchoring worked on the axis it targeted.** PRE-B's diagnosis was that the pre-#304
  imperative was anchored to *"before authoring `execute.json`"* — an artifact written at the
  END of a long run — so a subject could crawl source for fifty calls, read the map afterwards,
  and comply exactly. #304 re-anchored it to *"before you open any source file"* at the
  `context` step. **On the four runs that read source, the order reversed, every time.**
- **It did NOT produce bootstrap orientation, in either arm.** `read_at_bootstrap` (first map
  access at tool-call index < 3) is `False` on all four POST rows: first map reads land at
  **17, 21, 29, 19**, not at 0–2. The reason is structural and visible in the indices — the
  Commander spine runs `init` (work area, lease) before `context`, which costs 10–15 tool calls
  before the map instruction can fire at all. **"Map-first" as delivered means first-among-
  content, not first-among-actions.** Whether that distinction matters is a judgement, and it
  is Tommy's, not this record's.

## 5. The mechanism, visible in the indices

Every run shows the same chain: the contract's tool runs, *then* the map is read, *then* source.

| task | first `map_orient` | first `docs/architecture/*` read | first `src/*` read | `map_orient` calls | first verdict |
|---|---|---|---|---|---|
| #690 | **14** | 17 | 25 | 10 | `RESOLVED` |
| #688 | **20** | 21 | 37 | 7 | `RESOLVED` |
| #698 | **28** | 29 | 46 | 4 | `RESOLVED` |
| #704 | **17** | 19 | 22 | 4 | `RESOLVED` |
| #716 | **16** | `NO-MAP-READ` | `NO-SRC-READ` | 7 | `RESOLVED` |

PRE-B: **zero** `map_orient` calls across all five runs / 595 tool calls.

**#716 is the one row where the two witnesses disagree, and it is reported as a disagreement
rather than resolved.** It ran `map_orient` seven times, every call returning `RESOLVED`, and
wrote a `map-orientation.json` receipt to disk — so it demonstrably oriented on the map — yet
the frozen extractor records `NO-MAP-READ`, because the orienting happened through a tool under
`.claude/skills`, which the extractor's call-level corpus rule buckets as `skill-corpus` **and
nothing else** (§8 item 3). PRE-B's #716 also read neither map nor source, for a different
reason: it correctly determined the work lived in `constellation-skills`, not f1Brainz.

## 6. Discriminated measures — orientation vs use vs citation

Collapsing these hides the finding, which is why PRE-A's addendum separated them.

| task | arm | bootstrap | map<src | returned to map after src | map calls | cues cited/read | src precision |
|---|---|---|---|---|---|---|---|
| #690 | PRE-B | no | no | yes | 4 | 3/4 | 3/7 |
| #690 | **POST** | no | **YES** | yes | **9** | 3/6 | 3/5 |
| #688 | PRE-B | no | no | yes | 3 | 4/4 | 3/7 |
| #688 | **POST** | no | **YES** | yes | **6** | 1/4 | 4/9 |
| #698 | PRE-B | no | no | yes | 7 | 1/6 | 4/4 |
| #698 | **POST** | no | **YES** | yes | 7 | 2/2 | 4/5 |
| #704 | PRE-B | no | no | yes | 5 | 0/5 | 1/2 |
| #704 | **POST** | no | **YES** | yes | 4 | 1/2 | 1/2 |
| #716 | both | `NO-MAP-READ` | `NO-MAP-READ` | `NO-MAP-READ` | 0 | 0/0 | n/a |

**Use did not degrade.** `returned_to_map_after_src` stays `yes` on 4 of 4 — the map is still
consulted after source, so this is orientation *added*, not use *displaced*. Citation
(`map_cues_in_plan`) moves in both directions across tasks and at n = 1 supports no claim.

## 7. The three-way discrimination, as pre-registered

| verdict | this arm's evidence |
|---|---|
| **sufficient** — the contract moves orientation order | `map_before_src` 0/4 → **4/4**, with the mechanism confirmed at all three delivery hops |
| **insufficient** — loaded, order did not move | **not observed** |
| **irrelevant — delivery** — spine never materialized | **excluded**: `contract_delivered` 5/5 by two independent oracles |
| **irrelevant — install** — corpus lacks the contract | **excluded**: installed bytes asserted directly, not from the installer's marker |

Against `PRE_REGISTRATION.md` §5's threshold (**≥3 of 4 → report as sufficient**), the arm
reports **4 of 4**. **The verdict itself is Tommy's.** The two readings this record will not
choose between:

1. **The contract works.** The targeted axis moved on every run that could move, the mechanism
   is confirmed end to end, and PRE-B is a matched negative under the same instruments.
2. **The corpus moved, and #304 is the most plausible but not the only candidate.** The
   manipulation was 8 days and +31 files (§1), and n = 1 per task with no variance estimate.
   The clean way to close this is a replication, or an arm against a corpus differing from
   PRE-B's by #304 alone.

## 8. Declared limitations

1. **n = 1 per task.** No replication, no variance estimate. Direction of travel only.
2. **The manipulation is a corpus delta, not #304 in isolation** (§1). The single largest
   limitation and the one a follow-up arm should close first.
3. **The frozen extractor cannot see the mandated act.** Its call-level corpus rule credits any
   call touching `.claude/skills` as `skill-corpus` and nothing else, and the #304 contract is
   discharged by invoking a script that lives there. **The extractor was not modified** — that
   would have rescored PRE-B under different code and destroyed the pairing. Exposure measured
   instead: `map_credit_suppressed` is 1, 1, 0, 0, 2 across the five POST runs. #716's 2 are
   why its map reads are invisible (§5).
4. **The supplementary audit is new code in a reuse-disciplined experiment.** Its negative
   control (PRE-B, 0 across 5 runs / 595 calls) is guaranteed by construction and therefore
   weak on its own, so it also ships a self-test: **7/7**, including three mutants that must
   *not* count — a `Read` of `map_orient.py`, a `Grep` for the token, and a `Write` quoting the
   gate command. The first version of the audit counted all three as invocations, which alone
   would have flipped *irrelevant* into *insufficient*.
5. **Brief confound, carried deliberately and unchanged.** The `FILES I WOULD CHANGE` demand
   pushes subjects toward path-hunting and away from conceptual orientation — i.e. **against**
   the hypothesis. Content-identical to PRE-B's, so it cannot explain a PRE-B/POST difference.
6. **Bootstrap orientation is structurally unreachable under this spine** (§4). Not a defect
   this arm can separate from the contract's own effect.
7. **Harness version recorded for POST only** (`claude 2.1.220`). PRE-B did not record it, so
   the PRE-B value is **UNKNOWN, not equal** — an uncontrolled variable, stated rather than
   assumed away.
8. **Seam grading was not performed.** Out of this launch order's scope; transcripts and final
   answers are archived, so a blind grading pass remains possible without re-running anything.
   The rubric §2 tolerance ambiguity (#333) remains open and must govern both arms identically
   if the seam scores are ever paired.

## 9. Instrument identity — mechanical, not asserted

Blob-to-blob at PRE-B's merge `6774181` vs `HEAD`:

| instrument | verdict |
|---|---|
| `baselines/extract_ordering.py` (frozen) | **SAME** |
| `baselines/capture_baseline.py` | **SAME** |
| `baselines/issues.frozen.json` (the frozen brief source) | **SAME** |
| `baselines/RUBRIC.md` | **SAME** |
| `baselines/verify_capture.py` | **SAME** |
| `preb/discriminate.py` | **SAME** |
| `preb/verify_treatment.py` | **SAME** |
| `preb/fingerprint_global_corpus.py` | **SAME** |
| `preb/capture_preb.py` | **CHANGED — declared**: +16/−6, a label-only `--arm` flag the measured path never reads |

**The comparison must be blob-to-blob.** A working-tree digest comparison reports all nine as
changed, because this repo checks out CRLF while the blobs are LF. That false alarm fired twice
during this run (instruments, then briefs) and both times looked exactly like a real defect.

## 10. The first capture set was VOID — reported, not buried

**The first POST attempt produced five void captures and was discarded before any number was
computed from it.** Preserved at `runs-VOID-double-driver/` with `VOID_CAPTURE_EVIDENCE.json`.

The driver was launched twice: the first launch's compound shell command *reported failure* — a
later line errored on a wrong cwd — while its backgrounded `nohup` had already succeeded. Two
drivers then raced into the same run directories and the same log.

| run | distinct `session_id` | `result` events | malformed lines | `meta.json` said |
|---|---|---|---|---|
| 688 | **2** | **2** | 3 | `finished`, `exit=0`, 1170s |
| 690 | **2** | **2** | 1 | `finished`, `exit=0`, 1097s |
| 698 | **2** | **2** | 1 | `finished`, `exit=0`, 1152s |
| 704 / 716 | 1 | 0 | 0 | killed mid-flight |

**Nothing the arm was already checking could see this**: `meta.json` reported `exit=0` with
plausible elapsed times, and the truncation check passes because two interleaved writers still
leave a newline-terminated file. Filed as **#396**. `run_all_post.py` now takes an
`O_CREAT|O_EXCL` lock, and transcript integrity — one `system/init`, one `result`, one
`session_id`, zero malformed lines — is now a gate condition and passes on all five valid runs.

### 10.1 Why this is not a compromised measurement — the four facts, in one place

*"We re-ran the arm"* is exactly what a compromised measurement looks like from the outside. A
reader coming to this cold needs all four of these together, or they should reasonably discount
the arm:

1. **The void criterion is independent of the outcome.** *Two distinct `session_id`s and two
   `result` events in one transcript* says nothing whatever about `map_before_src`. It cannot be
   satisfied more easily by a result anyone prefers. **A void rule that could only fire on
   disappointing data is p-hacking; one that fires on process identity is hygiene.**
2. **It was applied blind.** The void set was never scored — `discriminate.py` was never run over
   it, and no ordering number from it was ever computed or seen. The criterion being
   outcome-independent protects the arm in principle; not having looked protects it in practice.
3. **The void set was preserved, not deleted** — `runs-VOID-double-driver/` with
   `VOID_CAPTURE_EVIDENCE.json`, and reported here rather than dropped. **A discarded arm that
   leaves no trace is indistinguishable from one that was never run.**
4. **`PRE_REGISTRATION.md` predates any POST number** (`a4993ec`, committed while captures were
   still in flight) **and stands unchanged.** It survived its first real test, having named in
   advance both of the ways this result could have been laundered — the #716 literal-row
   denominator, and `NO-SRC-READ` being the contract's success case rather than a missing datum.

### 10.2 The general defect — this epic's own thesis, arriving from a new direction

**`exit=0` and a plausible elapsed time are exactly what a doubled run looks like.** Every cheap
check passed: `meta.json` said `finished`, elapsed times were in range, and the truncation check
could not see it **because interleaved corruption does not truncate — the files still end on a
newline.** Only counting the thing itself caught it.

**Metadata about an artifact is not the artifact, and a check that reads the wrapper reports
clean on a corrupted payload.** That is *assert what you looped over*, reached from a completely
different direction, and it generalises to every detached capture in this fleet — not just this
one. The operational half deserves its own line: **a backgrounded `nohup` survived a compound
command that reported failure. The shell said it failed; the process disagreed and won.**

## 11. Nothing landed in f1Brainz

Per #347, the standard is enumerate-and-bound, not a zero count — a Commander driven to `plan`
authors artifacts by construction, so "zero writes" is unachievable and a boundary assertion is
strictly stronger.

| check | result |
|---|---|
| writes inside the run's own pinned worktree | **all runs clean** (`write_audit.clean` true, 5/5) |
| writes inside the worktree but outside `.agent-work/` | **0** |
| genuine forbidden git/gh operations | **0** — see below |
| per-worktree `git status --porcelain` before sweep | exactly one untracked dir each, the subject's own `.agent-work/<work-id>/` |
| transcript integrity | 5/5 clean |

**run-688 raised 5 forbidden-operation hits and all five are verifier false positives**,
adjudicated individually rather than waved through:

- **2** are `git merge-base --is-ancestor …`, which matches the reused verifier's
  `\bgit\s+merge\b` pattern. Read-only.
- **3** are `Write` calls whose **file content** mentions a git command. A `Write` cannot
  execute git; the verifier searches `json.dumps(input)`, which includes written content.

`verify_treatment.py` was **not** modified — the pairing depends on both arms being scored by
identical code — so the hits are classified by an additive adjudicator applied to both arms, and
any hit that is neither class stays REAL and fails the gate. PRE-B raised zero hits, so the
adjudicator is a no-op there.

## 12. Reproduction

```
python .agent-work/epic-298/post/map_orient_audit.py --self-test                    # 7/7
python .agent-work/epic-298/post/map_orient_audit.py .agent-work/epic-298/preb/runs/run-* --expect-zero
python .agent-work/epic-298/preb/discriminate.py .agent-work/epic-298/post/runs/run-*
python .agent-work/epic-298/post/verify_post_arm.py captures
python .agent-work/epic-298/post/verify_post_arm.py scores
python .agent-work/epic-298/post/verify_post_arm.py pairing
```

Cost and timing: five runs, **2207 s wall at 3-way concurrency**, 73–141 tool calls per run
(784–1281 s each). The void set cost a further 2241 s.

## 13. Filed to the tracker

| # | what |
|---|---|
| **#393** | the map-first contract reaches an agent only via spine materialization — `SKILL.md` has zero occurrences of "map"; "Commander loaded" is hop 0 of 3 |
| **#394** | `verify-frame` refuses every typed anchor under `DEGRADED` while the mission-frame template mandates graded decision anchors |
| **#395** | the corpus fingerprint's headline digest is blind to `templates/` and `scripts/` — where the contract lives |
| **#396** | a backgrounded process survives a compound command that reports failure, and meta-level checks cannot see the resulting corruption |
| **#397** | `verify_treatment.py`'s forbidden-operation patterns match `git merge-base` and search `Write` content |

## 14. Open for the Admiral and Tommy

- **The B3 verdict itself.** §7 gives both readings; this record does not choose.
- **Whether an arm isolating #304 is worth running** (§1, §8 item 2) — the one follow-up that
  would convert the strong reading into an attribution.
- **Whether "first-among-content" satisfies the intent, or whether bootstrap orientation was
  the goal** (§4). This is a question about what *"use the map first to orient yourself"* means,
  and it is upstream of any number here.
- **#333** (rubric §2 tolerance ambiguity) and **#352** (the PRE-B memory edit) remain open from
  PRE-B's §12 and are untouched by this arm.

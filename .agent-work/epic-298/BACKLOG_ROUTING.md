# Epic-298 side ledger — routing, not a list

37 issues filed this run; 31 open at compile time. **None is in the epic's definition of done.** This exists so the closeout decision is a decision rather than a backlog dump.

Grouped by *what kind of thing they are*, because that determines who should own them and whether they travel together.

---

## A. Delivery is broken (5) — **the group that should move first**

These are the concrete instances of #345, and several block each other's fixes from reaching anyone.

| # | |
|---|---|
| **344** | installed corpus 18 commits stale; project install is **shadowed** by global — **a merged fix does not reach agents, and there is no user-accessible override** |
| **362** | `episode_capture.py`/`context_manifest.py` in no bundle — **survives a corpus refresh**, because the file is not there to refresh |
| **328** | `verify_interrogation.py` / `verify_fowler_pass.py` wired as prose only |
| **329** | `verify_worktree_isolation.py` in zero spine templates — doctrine calls a collision *"data loss, not friction"* |
| **346** | `constellation-diagnose` does not register its description — **un-triggerable by intent**; 18 of 19 register |

**Why first:** #344 is upstream of every other fix in the repo. Until it moves, *anything* merged here is latent. #305 is currently landing the companion-invariant test that would prevent recurrence of #362 — that test is the reusable artifact.

---

## B. Engine and concurrency defects (6) — **real bugs, not doctrine**

| # | |
|---|---|
| **357** | the lease does not protect the gates — child plans carry `engine_session: null`; **four mutating verbs accepted from a session-less caller while a lease was held** |
| **315** | command checks pass **no `cwd` at all**; five shipped relative checks are silently fragile |
| **358** | reviewer `consolidate` and artifact emission are not atomic — a complete verdict can exist with no artifact for the gate to read |
| **330** | no confirm-dead check before worktree reuse |
| **318** | `durable_root()` silos per worktree during an epic; an abandoned lease pins it forever |
| **359** | surveys bypass the capture seam entirely — **Reviewer, Cartographer, Scout, Curator all uncovered** |

**#357 is the most consequential**: every continuation protocol in the fleet assumes the lease is the mutual-exclusion primitive, and for gated plans it is not. It is why three agents ended up in one worktree.

---

## C. Doctrine that earned its place (7) — **graduate, do not leave as issues**

These are the run's transferable findings. They belong in `skills/_shared/global-*.md` or `docs/agents/`, not on a tracker.

**337** the check-that-cannot-fail family — 6 costumes, plus *you cannot audit your own falsifiability* (graded side) and *a command that executes is not a command that decides* (grader side) · **345** built-but-not-wired, 8 instances, now with a **detection strategy**: break the call site, not the callee · **319** why documented hazards recur — *you fix the instance and not the method* · **338** a held PR must declare what it still intends to push; a terminal spine and released lease describe the run, not the ref · **364** *grep for the caller* misses dead code in any module shipping its own self-test · **349** a noise decoy must not be excluded by the target lens's own guardrail · **352** assert an allowlist, not a denylist

---

## D. Corpus contradictions and stale doctrine (6) — **cheap, and they mislead every reader until fixed**

**336** Charter creates the file Commander forbids · **317** `config_ref` to an absent-by-design path, plus prose explaining it is dead (folding into #304) · **348** stale `.agent-work/` ignore-state doc, **created by this epic's own #326** · **343** pathless *"the current map"* recurs in cartographer/scout/explorer · **313** docs prescribe an interpreter that has no pytest · **322** overview taxonomy omits the episode store

---

## E. Measurement-instrument findings (5) — **only matter if the measurement continues**

**331** zero skill invocations — corpus offered and declined · **347** the "nothing landed" evidence standard is unachievable for a skill-loaded run · **351** Commander runs externalise reasoning, thinning the gradeable artifact · **356** the commander skill's description says it cannot take a delegated dispatch, and 5/5 it did · **327** `run.dirty` self-caused (closing with #305's g4)

---

## F. Local defects in this epic's own new code (4) — **owned by their issues, will close with them**

**360**, **361**, **342**, **363**

---

## G. Small, unowned (2)

**314** delegated commanders told to have subagents reply via a mechanism teammates cannot use · **323** context-projection guard gaps from #300's cold panel

---

## The decision this is for

**Volume is not the question.** 37 issues from one epic is either a very productive run or the start of a debt pile, and which one it is depends entirely on whether **A** and **C** move.

- **A unfixed** means every future fix in this repo is latent — including the fixes for B, D, and F.
- **C left on the tracker** means the run's actual learning stays as 7 open issues instead of doctrine, which is precisely the failure mode Tommy's playbook ruling was about: *a lesson that never graduates is forgotten, not preserved.*
- **B, D, E, F, G can accumulate** without compounding. They are ordinary backlog.

**Recommendation:** treat **A** as a small epic of its own, route **C** through the closeout lessons audit (where it is already headed), and let the rest sit. That converts 31 open issues into one epic, one audit, and 19 ordinary tickets.

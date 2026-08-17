# Closeout pairing pass — epic #567

**DRAFT, written during wave 2.** Wave 2's own candidates are not in it yet; they land under
`.agent-work/567-{d1,d2,e,f,h}/triage-candidates/` and get appended before this pass runs.

The standing ruling, in the human's words: *"keep track of the issues, but we've been ballooning
out tracking. let's hold on to them until the end then see if we can pair them with open issues,
anything else we can file under episodes."* So each candidate gets exactly one of three
dispositions, and **none becomes a new issue**:

- **comment** — paired onto a named **open** issue as a comment.
- **episode** — recorded in `episodes/` as an observation, because no open issue fits.
- **resolved** — the candidate was fixed during this epic; recorded as resolved rather than filed.

Every pairing target below was checked for state, not assumed. `#482`, `#603`, `#145` and `#574`
are **CLOSED**, which is why nothing pairs onto them.

## Wave 1 candidates — 24 files, 27 dispositions

### Paired onto an open issue

| Candidate | → Issue | Why it fits |
|---|---|---|
| `567-a/613-lost-update-half-remains` | **#613** | It *is* #613's undelivered half. The atomicity fix shipped; the lost-update half did not. Deferred behind #615 by human ruling this wave, so the comment records the remainder against the issue that owns it. |
| `567-a/gauge-writer-hook-fixed-temp-name` | **#613** | Same defect class as #613's own subject: `_atomic_write_json`'s fixed temp name corrupts under two concurrent writers. Belongs on the atomicity issue, not a new one. |
| `567-a/hardlinks-defeat-path-based-containment` | **#559** | The documented limit of `spine_bind`'s path-based containment. Ruled deliberately **not** to close (inode containment adds surface and removes no agent work), so the comment is the record of an accepted limit. |
| `567-a/engine-init-imperative-asserts-a-false-binding` | **#559** | The spine template's `init` imperative asserts a binding that did not exist. Lane D1 is rewriting exactly this text — **verify at closeout whether D1 resolved it**, and if so record as resolved instead. |
| `567-a/launch-order-bootstrap-defects` | **#535** | Three bootstrap defects in the launch-order template, which is #535's subject. Lane F measures that template this wave. |
| `567-a/map-ids-jsonl-empty-repo-wide` | **#544** | `map/ids.jsonl` empty repo-wide means every run orients DEGRADED. **Its diagnosis is wrong and the comment must correct it:** rebuilding leaves the file empty and `map/` with no diff, because `render.py:728` writes it from *minted anchor ids* and this repo has none. Not stale-file rot — an unminted mind map. |
| `567-a/verify-frame-refuses-every-anchor-when-degraded` | **#544** | `verify-frame` refuses the template it is paired with, under a degraded map — the downstream consequence of the same generated-map problem. |
| `567-a/write-provenance-on-spine-journal` | **#369** | #369 is exactly "actor attribution": `claim --force` erases who wrote what. Recording *who* wrote each journal entry is its missing half. |
| `567-g/no-instrument-distinguishes-own-fork-writes-from-tampering` | **#369** | Same finding as `epic/tc2` from the other side. **Merge both into one comment** rather than commenting twice. |
| `epic/tc2-no-write-attribution-produces-false-tamper-reports` | **#369** | See above — this is the one that cost lane G its delivery. |
| `567-b/tc1-crew-backend-design-doc-drift` | **#432** | The spec's Decision 2 went stale *because of* #432's own fix. The drift belongs on the issue that caused it. |
| `567-b/tc2-mandatory-spine-at-dispatch` | **#432** | A direct follow-on: whether `ExternalBackend` should require `--spine` at dispatch time. #432 is still open. |
| `567-c/tc1-duplicated-precedence-prose` | **#595** | The precedence sentence is now written in two places. #595 owns that precedence. |
| `567-c/tc3-issue-595-advisory-wording-followup` | **#595** | #595's own suggested resolution point 2 was not taken. Belongs on #595. |
| `567-c/tc4-issue-522-pin-test-pattern` | **#522** | #522 *is* "pin tests guard the literal wording, not the class of defect", and this candidate reproduced it live on PR #620. |
| `567-a/a-guard-test-that-cannot-run-where-the-guard-is-needed` | **#575** | A test proving a platform fallback that cannot run on that platform — the Windows-proof issue is where this belongs. |
| `567-g/newline-sensitive-byte-identity-assertions-windows-ci` | **#495** | The candidate names the #495 family itself, and #495 is **confirmed OPEN**: "six repo JSON writers pass encoding but not newline, against CREW_CONTEXT's always-pass-newline rule" — the same defect, seen from Windows CI. |
| `epic/tc1-fork-inherits-dispatcher-spine-identity` | **#559** | Same class as #559 but strictly worse, because a fork cannot tell it is not the dispatcher. |
| `epic/tc3-launch-order-first-line-blocks-an-agent-that-cannot-cd` | **#535** | The bootstrap floor. **Merge with `567-a/launch-order-bootstrap-defects`** into one comment. |

### Recorded as an episode — no open issue fits

| Candidate | Why an episode rather than a comment |
|---|---|
| `567-a/mutate-a-copy-never-the-tracked-file` | A doctrine observation that carries its own correction: the author first reported a reviewer had died mid-mutation, then established it had not and was delivering. The self-correction is the valuable part, and it is a record, not a fix. |
| `567-a/subtest-hides-a-raising-test-body` | **Fixed during this epic** by PR #626 (q4), so there is nothing to file. The episode records that a `subTest` can report PASSED while its body raises, and that the guard now makes it greppable. |
| `567-b/tc3-imperative-detector-homograph-allowlist-growth` | The episode-observation guard cannot tell a homograph from an instruction, and its exception list has grown to 11 entries across five runs. An observation about a mechanism's decay shape. |
| `567-g/duplicated-code-in-advance-release-and-release-child-plans` | Minor Fowler duplication in two closeout primitives, non-blocking, and its parent issue #574 is **closed**. |
| `567-g/reviewer-fowler-template-work-id-substitution-bug` | A concrete template bug with no open issue to hold it. |
| `567-a/door-main-catches-only-keyerror` | The door's `main()` catches only `KeyError`, so any other raise kills it. No open issue fits. **See "Needs a decision" below** — lane E owns that file this wave and this may be better as fix-now triage than as an episode. |

### Resolved during this epic

| Candidate | Disposition |
|---|---|
| `567-c/tc2-issue-442-fenced-out` | **Resolved.** The fence was lane A's file ownership in wave 1; #442 runs as lane H this wave. Record as resolved, and close the loop on the comment thread if lane H delivers. |

### Needs a human decision at acceptance — 2 items

1. **`567-g/wire-finish-work-as-mcp-tool`.** Its parent issue **#574 is closed**, and the candidate
   asks for `finish_work` to be wired as an actual `spine_done` MCP tool — which is arguably the
   rest of #574's own intent. The three options are: record as an episode (loses the actionable
   ask), reopen #574 (against the no-new-tracking spirit but not against its letter), or fold it
   into the epic summary as unfinished business. **This is adjacent to #574's reserved question**
   — whether PR-opening lives in the engine verb or the wrapper script — which the human reserved
   and no lane may settle.
2. **`567-a/door-main-catches-only-keyerror`.** A real robustness defect in a file lane **E** owns
   right now. Fix-now triage is a *delegated* class, so the Admiral could route it to lane E
   rather than defer it — but E's launch order is frozen and adding scope mid-flight is the
   thing that strands lanes. Recommendation: leave E alone, record the episode, and let the
   human decide whether it is worth a follow-up.

## Method notes for whoever runs the pass

- **Two merges reduce 27 dispositions to 25 comments/episodes.** `567-g/no-instrument…` with
  `epic/tc2…` onto #369, and `567-a/launch-order-bootstrap-defects` with `epic/tc3…` onto #535.
  Commenting twice on one issue with the same finding is the ballooning the ruling exists to stop.
- **Re-check every target's state immediately before commenting.** Four intended targets turned
  out closed (#482, #603, #145, #574), and GitHub returned intermittent 503s all day. Every
  lookup that 503'd was retried to a real answer rather than assumed: **#495 OPEN**, **#615
  OPEN**, **#269 CLOSED** (cited in the launch orders as a hazard record, never a pairing
  target). No target in this table is unverified.
- **`gh issue comment` is a delegated class with a recorded permission fallback:** on a harness
  veto, take one human approval in the moment, then batch the remaining equivalent comments
  rather than re-litigating each one (#408's shape). Log the veto as an `INCIDENT`.
- **Episodes go through `scripts/apply_episode_delta.py` only**, always `--store-root episodes`,
  and the order is **write → `git add` → suite → commit**. Prove capture with
  `verify_episode_captured.py` before advancing. Rephrase any bare imperative verb out of an
  observation rather than growing the exception list.

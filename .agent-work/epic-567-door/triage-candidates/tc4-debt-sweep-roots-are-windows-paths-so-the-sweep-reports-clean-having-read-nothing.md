# Triage candidate: the mandated debt sweep reports "clean" on this host having read nothing

**Status:** not filed. Held to closeout per the epic's standing ruling (tracking has been
ballooning; candidates are paired onto an open issue or recorded as an episode).

**Found by:** the Admiral of epic-567-door, 2026-08-17, preparing the closeout sweep that
`constellation-admiral`'s own closeout step mandates.

**Proposed pairing:** **#561** — *"CREW_CONTEXT's Python Invocation section is wrong on the Linux
dev host."* Same family and same root cause: a doc carrying Windows-only paths that silently
misbehaves on the host actually in use. #561 is open and is lane D2's this wave, so the comment
lands on a live issue.

## The defect

`docs/DEBT_SWEEP_CADENCE.md` lists the dogfood roots as Windows paths:

```
C:/Programs/f1Brainz
C:/Programs/network_elo
C:/Programs/story_time
```

None exists on this Linux host. All three exist at `/home/tommy/projects/<name>`.

**The failure mode is the bad one.** Run the documented invocation here and it does not error:

```
$ python3 scripts/collect_feedback.py C:/Programs/f1Brainz C:/Programs/network_elo C:/Programs/story_time --out <file>
report written: <file>
EXIT=0
```

The report reads, in full:

```
# Constellation Feedback Sweep — 2026-08-17

No new or open candidates.
```

So a closeout that runs the documented command gets **exit 0 and an explicit all-clear**, having
opened zero export files. The sweep exists specifically to stop the cross-project feedback loop
going dormant, and on this host it reports the loop healthy while reading nothing. A check that
returns the same answer whether the world is fine or unreachable is not a check.

## What the sweep actually finds when pointed at the real paths

Same script, same flags, corrected roots — **10 new candidates, 2 of them recurring/validated**,
none of which had ever been collected:

| finding | occurrences | project |
|---|---|---|
| `powershell-heredoc-use-here-string` | **3** | story_time |
| `engine-session-id-flag-position-still-unfixed` | **2** | baseball_coaster |
| `worktree-isolation-not-guaranteed` | 1 | story_time |
| `commander-spine-mismatch-for-autonomous-dispatch` | 1 | story_time |
| `admiral-verifies-from-artifacts-on-commander-idle` | 1 | story_time |
| `engine-could-auto-heartbeat-on-mutating-verbs` | 1 | story_time |
| `crew-resume-async-armed-poll-insufficient` | 1 | baseball_coaster |
| `amend-op-field-name-is-op-not-kind` | 1 | baseball_coaster |
| + 2 more | 1 each | baseball_coaster |

Both reports are preserved for comparison at
`.agent-work/epic-567-door/debt-sweeps/2026-08-17-{documented,linux}-roots-report.md`.

## A second defect, in the same doc

`/home/tommy/projects/baseball_coaster/.agent-work/CONSTELLATION_FEEDBACK.md` **exists and is not
in the roots list** — and it carries 5 of the 10 findings above, including the recurring
`engine-session-id-flag-position-still-unfixed`. The doc's own rule is *"add a repo here the
first time it gains a `.agent-work/CONSTELLATION_FEEDBACK.md` export worth sweeping,"* so this is
that rule not being followed rather than an ambiguity.

`network_elo` is listed and exists but has no export, which is fine and worth noting only so the
next reader does not treat its absence as a bug.

## Why this belongs to this epic rather than being a passing observation

Two of the ten findings speak directly to work in flight:

- **`engine-session-id-flag-position-still-unfixed`** (2 occurrences) is about passing
  `--session-id` on the CLI — which is exactly the text lane D1 is sweeping out of agent-facing
  doctrine this wave. A consuming project hit it twice while the corpus still taught it.
- **`worktree-isolation-not-guaranteed`** independently reproduces, in another repo, the reason
  this epic's contract makes the Admiral provision every worktree by hand and gate the wave on
  `verify_worktree_isolation.py`: *"three parallel subagents shared the main checkout and
  collided on `git checkout -b` (one commit landed on a sibling's branch)."*

## Recommended remedy

1. Correct the roots in `docs/DEBT_SWEEP_CADENCE.md`, and add `baseball_coaster`.
2. Make the roots portable rather than absolute-per-host, or have `collect_feedback.py`
   **refuse a root that does not exist** instead of silently contributing nothing. The second is
   the smaller change and it is the one that converts a silent no-op into a loud failure.
3. Do **not** run `--mark` until these ten are dispositioned — see the Admiral's ruling in the
   log. Marking them collected while nothing has been done with them is precisely how the loop
   goes dormant while continuing to look healthy.

**Not fixed here.** `docs/DEBT_SWEEP_CADENCE.md` is lane **D1**'s file this wave (it owns
`docs/**` outside `docs/agents/CREW_CONTEXT.md` and `docs/superpowers/**`), and adding scope to a
frozen launch order mid-flight is what strands lanes.

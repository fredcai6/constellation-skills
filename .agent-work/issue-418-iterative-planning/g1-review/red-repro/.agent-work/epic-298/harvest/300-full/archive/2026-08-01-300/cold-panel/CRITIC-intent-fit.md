# Cold panel — INTENT-FIT critique (issue #300, projection generator + manifest)

Read: `.agent-work/300/MISSION_FRAME.md`, `git diff main...HEAD` (10 files, +2177), and the
repository as needed to check the change's claims. No authoring context.

Verdict in one line: the *mechanism* is honest, deterministic and well-guarded, but nothing in the
shipped system ever runs it, and the one real declaration it ships records nothing. The record's
existence and its truth both currently rest on an agent choosing to act.

---

## BLOCKING

### B1. Nothing in the delivered system ever produces a manifest. AC1 is satisfied by definition, not by construction.

**What is wrong.** `scripts/context_manifest.py` has no caller. There is no CLI verb (stated as
deliberate in the module docstring and again in `docs/CHECKLIST_ENGINE_DESIGN.md`), no call from
`scripts/checklist_engine.py`, no spine condition `check` command, and no skill/doctrine text
anywhere that tells any agent to run it. Merge this and a real Commander run produces exactly zero
manifests.

**Evidence.**

```
$ grep -rn "context_manifest" --include=* .   # excluding tests/, the module itself, gitignored .agent-work/
./docs/CHECKLIST_ENGINE_DESIGN.md:...
./docs/CHECKLIST_SCHEMA.md:109:...
$ grep -rn "context_manifest\|context manifest" skills/
(no matches)
```

The committed design doc states the situation plainly and without a successor: *"the manifest is a
JSON value a caller builds and, optionally, writes under `.agent-work/<work-id>/context/<step>.json`
via `produce()`."* It names no caller and no issue that will supply one. `produce()`, `work_id` and
`session_id` are therefore dead knobs on merge.

**Why this is an intent-fit failure, not a scope quibble.** The acceptance criterion is "a manifest
is produced on every deterministic assembly". As shipped, "assembly" *is* `build_manifest()`, which
by construction returns a manifest — so the criterion cannot fail, and cannot be observed to hold
either, because the count of assemblies in production is zero. The mission frame is explicit that
the manifest must be emitted "as a byproduct of assembly, **never as a separate act**." Right now
producing it is *only* a separate act, and one no agent is instructed to perform — i.e. the record
exists if and only if an agent is diligent enough to invoke a Python module nobody told them about.
That is the exact defect shape the review brief names.

**What I would do.** One of two, not neither: (a) wire production into the one deterministic event
that already exists — the engine's step transition, or a `check` command on the spine's own
`context` step in the style of the existing `verify_*.py` family (`skills/explorer/...` already
calls `verify_spec_confirmed.py` that way, so the seam is precedented and cheap); or (b) if the
human's ruling genuinely defers wiring, say so in the committed doc — "#300 ships the library; issue
NNN wires it" — so the gap is a recorded decision rather than an unnoticed hole. Silent option (b)
is what ships today.

---

## SERIOUS

### S1. Nothing is assembled. The manifest's headline claim — "were made available to the agent" — is not earned by anything in the diff.

**What is wrong.** The issue frames a script that *assembles* agent-facing context from canonical
Markdown; the mission frame's Intent line says "assemble it deterministically, and emit a manifest".
`rows()` reads each declared file's bytes solely to hash them and discards the content
(`scripts/context_manifest.py`, `rows()` → `{"root", "path", "rev"}`). No assembled surface is
produced anywhere, run-local or otherwise. The agent's actual context still arrives by the agent
reading the `imperative` prose and opening files by hand.

So what the manifest can honestly attest is: *these paths were declared for this step, and at
assembly time each either did not exist or held bytes with this OID.* What it says instead
(module docstring, first paragraph) is:

> "these files, in this order, at these revisions, **were made available to the agent** running this
> step."

and `docs/CHECKLIST_ENGINE_DESIGN.md` repeats it: "what was made available to the agent running this
step". Nothing in the change makes anything available to any agent. The gap between the two is
filled by agent diligence — the same defect class as B1, seen from the honesty side. It is sharpest
on `rev: null` rows, where the record simultaneously claims the file "was made available" and
records that it was not there.

Note this is *not* the thing the human ruled out. The ruling excluded a **committed per-role
projection artifact**; it did not convert "assembles context" into "hashes a path list".

**What I would do.** Either produce something (even a run-local ordered concatenation under
`.agent-work/`, which the ruling does not touch), or — cheaper and sufficient for this issue —
downgrade every claim to what the code can prove: "declared for this step, and present with this
content at assembly time." The module is otherwise scrupulously honest about its limits (see
"Sound", below); this one sentence is the outlier.

### S2. The only real declaration in the corpus projects six rows, all `rev: null`. Revision identity is present only under fixtures and a test-only install shim.

**Evidence** — running the shipped producer over the shipped template in this repo:

```
skill   references/global-orchestrator.md      rev: null
skill   references/global-everyone.md          rev: null
repo    docs/agents/ORCHESTRATOR_CONTEXT.md    rev: null
repo    docs/agents/GLOSSARY.md                rev: null
repo    docs/agents/engine-config.json         rev: null
durable .agent-work/LESSONS.md                 rev: null
```

Six of six. The `skill`-root entries exist only after `scripts/install_constellation.py` copies
`skills/_shared/global-*.md` into each role's `references/` — `skills/commander/references/` in the
source tree contains only `commander-core.md` and `crew-dispatch.md`. The `repo`-root entries are
the `docs/agents/` overlay this repo does not carry (the mission frame says so itself).

`tests/test_context_determinism.py` had to add `INSTALL_SHIM` precisely because of this, and says
so: *"without this shim every declared row would resolve to `rev: null` and the byte-identity
assertion would pass vacuously."* Credit for catching it — but the consequence stands: outside a
hand-shimmed test, no manifest with a single non-null `rev` has ever been produced in this corpus.
Add the coverage fact — 1 of 13 shipped checklist templates carries a declaration, on 1 step
(`CommanderSpineDeclaration.test_only_the_context_step_carries_a_declaration` pins this) — and the
delivered observability is: one step, of one role, in a layout this repo does not have.

AC2 ("revision identity is present") is met by the *function* beyond argument (the `git hash-object`
/ `git rev-parse HEAD:<path>` equality tests are strong, including the CRLF twins and the
deliberate-divergence test). It is met only nominally by the *substrate as shipped*.

**What I would do.** Give the corpus one declaration that resolves non-null in a bare source
checkout — the Commander spine already reads repo doctrine that exists here — or state in the
schema/design docs that the shipped declaration is written against the installed layout and is
expected to be all-null in the source repo, so a reader who runs it does not mistake an empty
manifest for a broken producer.

### S3. `manifest_path()` settles the cardinality question unilaterally, and destructively, while the frame calls it unsettled.

**What is wrong.** `manifest_path(root, work_id, step) -> <root>/<work_id>/context/<step>.json` has
no run, episode or attempt discriminator. A step re-entered after rework — the engine tracks
`rework_count`, so this is a first-class state, not a hypothetical — overwrites the earlier
manifest. The answer to "what did the agent have when it attempted this step the first time" is
destroyed by the second attempt, which is the exact question the record exists to answer.

The mission frame lists "*Manifest cardinality (one per spine step) vs #301's episode `context`
field*" under "Decision pressure — **surfaced, not settled by me**", and the design doc repeats it
as open. The code settles it, last-write-wins, and nothing marks that as provisional.

**What I would do.** Either include a discriminator (rework count / attempt / episode id) in the
filename, or make the write refuse to clobber an existing manifest, or — if the Admiral genuinely
wants it deferred — leave `manifest_path()` out of the shipped surface until #301 answers, since it
is unused today anyway (B1).

### S4. Committed docs cite two gitignored, worktree-local files. AC3's non-test half rests on a file no reader of `main` can open.

**Evidence.** `docs/CHECKLIST_ENGINE_DESIGN.md` (new section) cites
`.agent-work/300/DIT-COMPARISON.md` and `.agent-work/300/OBLIGATIONS-301.md`.

```
$ git check-ignore -v .agent-work/300/OBLIGATIONS-301.md .agent-work/300/DIT-COMPARISON.md
.gitignore:1:.agent-work/   .agent-work/300/OBLIGATIONS-301.md
.gitignore:1:.agent-work/   .agent-work/300/DIT-COMPARISON.md
```

Both vanish with `git worktree remove`. The frame's own claim line for AC3 says it is "checked by
shape/obligation assertions only" — the *shape* half is committed
(`EpisodeContextFieldShape.test_produced_manifest_is_assignable_to_episode_context_field_untransformed`),
the *obligation* half is not, and the committed doc points readers at it as if it were. A permanent
document must not sentence its reader to a file that no longer exists.

Separately on AC3's strength: the shape test proves the manifest is JSON-native and round-trips —
true, and worth pinning, but it is a property every dict of primitives has. Nothing checks any
constraint #301 actually imposes. The frame is upfront that it will not test against concurrent
code, which I accept; the fix is to move the obligations into a committed location, not to test
#301.

**What I would do.** Inline the obligations (three or four sentences: cardinality, durability,
inline-vs-reference) into `docs/CHECKLIST_ENGINE_DESIGN.md`, or into the issue tracker, and drop
both `.agent-work/` citations from committed prose.

---

## MINOR

### M1. `required` is dropped from the row, on a rationale the row itself contradicts.

`rows()` justifies it as "the manifest records what was delivered, not what was asked for" — but
`root` and `path` *are* what was asked for; only `rev` is what was delivered. The consequence is
concrete: once the run's spine (gitignored `.agent-work/<id>/spine.json`) is gone, a `rev: null` row
is permanently indistinguishable between "optional overlay legitimately absent" and "required
doctrine missing". That fact is known for free at assembly time and costs one boolean. Degraded-mode
*reporting* is properly deferred to issue F; preserving the input it would need is not the same
thing.

### M2. Root-token semantics are defined nowhere committed, and `durable` is ambiguous against the code that owns that word.

`ROOT_TOKENS = ("skill", "repo", "durable")`; `docs/CHECKLIST_SCHEMA.md` says only "`root` is one of
`skill`|`repo`|`durable`" and that resolution is caller-supplied. `scripts/agent_work_root.py`
exposes *two* candidate roots — `durable_root()` (checkout root) and `durable_agent_work()`
(`<root>/.agent-work`) — and the shipped declaration's `{"root": "durable", "path":
".agent-work/LESSONS.md"}` is correct against the first and doubles the segment against the second.
With no committed caller (B1) nothing resolves the ambiguity. The frame also flagged that
`agent_work_root.py` returns the *worktree* under an Admiral lease, so a `durable:` row is not
durable — and the diff records that nowhere a future reader will see it. One sentence per token in
the schema row fixes this.

---

## Sound — stated plainly, not padded

- **No widening toward proving use.** I looked specifically. There is no transcript reading, no
  access counting, no read-time or ordering-of-reads field, no archived file content
  (`test_manifest_never_carries_file_contents`), and no post-hoc pass over anything an agent did.
  The single impure edge is an injected byte reader used only to compute an OID. The
  delivery-not-use boundary is respected in the code — the drift is in the *wording* (S1), not the
  mechanism.
- **The governing determinism principle is honored without loopholes.** Pure functions, no LLM, no
  semantic routing, no `git` subprocess, no glob or directory enumeration (patterns are rejected
  outright rather than expanded), no sorting of declaration order, LF normalisation as the identity
  input, `newline="\n"` pinned on write, and a single-JSON-pointer exclusion set (`/run`) that makes
  "accidentally varying content" structurally hard rather than a maintained mask list. The
  acceptance test carries real anti-vacuity guards
  (`test_the_two_environments_really_are_distinct`, `..._mutations_took_effect_inside_the_child`,
  `test_the_content_is_a_real_projection_not_an_empty_one`) and states its own limit (same OS, same
  Python) instead of overclaiming a cross-platform rebuild.
- **Nothing forecloses a later assertions-with-source-and-evidence model.** `{root, path, rev}` plus
  `run.roots` is already subject + source + evidence, `contract: 1` gives the version seam, and the
  whole envelope is a plain JSON value that travels intact into an episode field. I could not find a
  shape decision here that a later truth model would have to undo.
- **The lint's honesty is exemplary and is actually enforced.** `verify_context_declaration.py`
  states its one-directional limit in its docstring, the design doc repeats it in the same terms,
  and a fixture (`prose_names_more_than_declared`) plus a test
  (`test_narrowed_declaration_is_deliberately_not_caught`) *assert* the blind spot rather than hiding
  it. Although the script is not a CI step, `test_lint_passes_over_real_shipped_spine_templates` and
  `test_default_discovery_finds_the_commander_spine_and_passes` run it over the real templates, so
  CI does enforce it. Likewise the `rev`-vs-git divergence is asserted
  (`test_rev_diverges_from_git_for_content_git_refuses_to_normalise`) rather than assumed away. This
  is the standard the rest of the change should be held to — which is why S1 stands out.
- Full suite for the new files runs green here: 69 passed, 69 subtests, 2.4s.

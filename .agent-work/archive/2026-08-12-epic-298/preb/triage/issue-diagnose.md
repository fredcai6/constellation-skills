`constellation-diagnose` is the one skill in the corpus that does **not** register its description with the harness. It is therefore effectively un-triggerable by intent: the description is the entire trigger surface, and a skill whose description is dropped can only be reached by a user typing its name.

Found incidentally while building the PRE-B measured arm for epic #298. Not a blocker for that arm; filing rather than fixing because the root cause is not established and a guessed fix would be worse than a filed finding.

## Evidence, from a fresh process, not from a session listing

A `claude -p --output-format stream-json --verbose` launch emits a `system/init` event carrying the registered `skills` list. In that event:

- 19 `constellation-*` directories exist on disk under `~/.claude/skills`
- 18 `constellation-*` names appear in `init.skills`
- the missing one is `constellation-diagnose`

Independently, in an interactive session's available-skills listing, every other constellation skill shows its frontmatter `description`, while diagnose shows `Constellation Diagnose` — which is its `# ` H1, i.e. the fallback used when no description was parsed.

## What it is not

Three plausible causes were checked and eliminated:

- **not `invoker:`** — `constellation-implementer`, `constellation-interrogator`, `constellation-reviewer`, `constellation-to-issues` all carry `invoker: both` and register normally.
- **not `": "` inside the description** — `constellation-curator`'s description contains `corpus: measure with curate_corpus.py` and registers with its description intact.
- **not description length** — diagnose's is 313 chars; `constellation-commander-delegated`'s is 397 and registers.

The only cell unique to diagnose is the **combination** of `invoker: both` with a `": "` inside the unquoted description scalar. That is a hypothesis, not a finding, and confirming it is the first step of the fix.

## Why it matters beyond cosmetics

Epic #298's PRE-A arm (#299) recorded **zero skill invocations across five measured runs** with the full corpus installed and offered. Whatever else explains that, a skill that cannot present a description to the trigger surface cannot be selected on intent at all. Corpus-health measurement (`curate_corpus.py`) should be able to catch this class mechanically — "every SKILL.md's description survives round-tripping into `init.skills`" is a checkable invariant, and right now nothing checks it.

## Suggested shape

1. Confirm the cause (quote the description scalar, or drop `invoker:`, and re-read `init.skills` from a fresh process — a session listing is not sufficient evidence).
2. Fix the file.
3. Add the round-trip invariant to the Curator's corpus-health pass, so the next occurrence is caught by measurement rather than by accident.

Present in both the global build (`source_commit 74953936`) and the repo at `857601d`, so this is not an install artifact.

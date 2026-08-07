"""Generate tests/data/retired_names.approved.txt from the live scan, one reason per line.

Written rather than hand-typed for one reason: an entry must be the EXACT string
`normalize()` produces, and a hand-transcribed 53-line census is a transcription-error
generator. The reasons below are hand-authored per line; only the mention text is machined.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, "scripts")
import verify_retirement as vr  # noqa: E402

HEADER = """\
# Frozen approval census for the `retired-name-on-shipped-surface` leg of
# scripts/verify_retirement.py (#403 / #447 g5).
#
# Format: identical to tests/data/store_mentions.approved.txt, and read by the SAME
# parser -- one `# <reason>` line, then one `<path>:<normalized line>` entry directly
# beneath it. `normalize()` collapses all whitespace. A path never contains a colon; the
# quoted line often does, so the FIRST colon separates the two fields.
#
# WHY THIS EXISTS. The leg could not reach zero and was never going to. Invariant 7 of
# #447 g5 REQUIRES ~33 sites in docs/RECURSIVE_IMPROVEMENT_DESIGN.md to survive untouched
# -- it is a June 2026 design RECORD, and rewriting it to describe a system it never
# described would falsify history. The commander spine's archive.c4 deny_globs keep both
# retired path strings as a re-staging block. scripts/stage_feedback.py survives by
# explicit ruling. With no approval mechanism at all, test_canon_is_clean's
# xfail(strict=True) could never XPASS and the scaffolding would outlive the work.
#
# THE BRIGHT LINE. A reason amounting to "an agent is still told to use the retired thing"
# is NOT approvable -- fix the surface instead. Every reason below is one of: a frozen
# historical record, a deny-glob re-staging block, a survivor script naming what it
# stages, a tombstone naming the retired files in order to forbid them, or a replacement
# naming what it replaced.
#
# NOT A PATTERN ALLOWLIST. Exact sites only, so anything new still has to be looked at by
# a human and given its own reason. Only the CONTENT half of the leg is approvable here;
# a restored file or skill DIRECTORY whose name is the retired thing fires regardless.
#
# ONE OPEN NOTE, recorded rather than silently approved: scripts/stage_feedback.py still
# writes an `AGENT_FEEDBACK.md` and a `lessons-delta.json` into its staging dir, and names
# a verifier deleted at g4. It was already orphaned before this gate -- no shipped surface
# references it outside its own tests and the historical design record -- and it is out of
# g5's scope. Filed upward as a triage candidate at #447 g5.
"""

# One reason per residual, in `scan()` order (sorted by leg, path, line).
REASONS: dict[str, list[str]] = {
    "RETURN.md": [
        "workstream A's inherited RETURN document, not editable from this gate: a finding RECORD naming the two files a merge conflict was confined to",
        "workstream A's inherited RETURN document: a finding RECORD naming where the conflicts that cost real time landed",
    ],
    "docs/CONSTELLATION_OVERVIEW.md": [
        "the ruling that the playbook is deliberately ABSENT from the artifact taxonomy -- it names the retired file in order to record the exclusion, and #447 g5 invariant 8 requires this paragraph to survive",
    ],
    "docs/RECURSIVE_IMPROVEMENT_DESIGN.md": [
        "June 2026 design record, audit table row: names where the run retrospective was then written, and records that nothing read it",
        "June 2026 design record, audit table row: names the lesson-disposition gate as it then stood",
        "June 2026 design record, audit table row: names the feedback-invariant verifier as it then stood",
        "June 2026 design record, gap analysis: records that the feedback log was write-only",
        "June 2026 design record, parenthetical: names the gate that force-settled lesson application at the feedback step",
        "June 2026 design record, proposal: names the verifier it would have extended to require a section's presence",
        "June 2026 design record, superseded-block quote: the context-step read and digest injection the design proposed",
        "June 2026 design record, superseded-block quote: names the writer the feedback step then distilled deltas through",
        "June 2026 design record, Loop 2 proposal: names the append-only log half of the split durable store",
        "June 2026 design record, Loop 2 proposal: names the curated-playbook half of the split durable store",
        "June 2026 design record, Loop 2 proposal: the context-step READ this retirement exists to abolish, kept as the record of what was proposed",
        "June 2026 design record, Loop 2 proposal: describes the delta update the playbook would take",
        "June 2026 design record, Loop 2 proposal: names the verifier extension the split would have needed",
        "June 2026 design record, Loop 3 proposal: names the gate that would refuse the feedback advance",
        "June 2026 design record, Loop 5 proposal: the SessionStart digest injection into ad-hoc sessions, kept as history",
        "June 2026 design record, sequencing list: names the read path Loop 2 would have added",
        "June 2026 design record, role survey: names the Reflector role this retirement deleted",
        "June 2026 design record, build list: names the skill it proposed and where it would be wired",
        "June 2026 design record, open question: asks whether the digest injection should be unconditional",
        "June 2026 design record, rejected alternative: names the LLM-editing shape the design refused",
        "June 2026 design record, rejected alternative: names the script that would apply deltas mechanically instead",
        "June 2026 design record, rejected alternative: names the verifier that script was proposed as a sibling of",
        "June 2026 design record, drill proposal: names where the drill link would have been enforced",
        "June 2026 design record, superseded note: records what the writer deliberately did NOT carry",
        "June 2026 design record, concurrency hazard: names the shared log two parallel Commanders would race on",
        "June 2026 design record, concurrency hazard: names the second shared file in that same race",
        "June 2026 design record, resolution: names the trio the durable-root fix made canonical",
        "June 2026 design record, resolution: names the first member of the worktree-local staged trio",
        "June 2026 design record, resolution: names the verifier that accepted the staged shape in lieu of a durable write",
        "June 2026 design record, follow-on: names what the staging script writes",
        "June 2026 design record, follow-on: names the verifier whose accepted layout that script matched",
        "June 2026 design record, ordering constraint: names the file the constraint was about",
        "June 2026 design record, trigger proposal: names the entry-count threshold that would trigger an audit",
    ],
    "docs/agents/ORCHESTRATOR_CONTEXT.md": [
        "the retirement TOMBSTONE: names both retired files in order to FORBID them and to forbid any successor playbook -- this block is where a good-faith agent acting on a stale instruction lands",
    ],
    "scripts/apply_episode_delta.py": [
        "the surviving store writer's module docstring: records which prior-art contract it inherited (validate-then-apply, all-or-nothing)",
        "the surviving store writer: records a deliberate DEPARTURE from the prior art's date stamping",
        "the surviving store writer: records that the mandatory non-empty retire reason was inherited, not re-decided",
    ],
    "scripts/init_work_area.py": [
        "placeholder-token comment: a HYPOTHETICAL example of a skill-dir token carrying hyphens, illustrating the parser's rule; it directs nobody to anything",
    ],
    "scripts/install_constellation.py": [
        "bundle comment: names, by analogy, which roles ship no script; nothing is installed under that name",
    ],
    "scripts/stage_feedback.py": [
        "survivor script's docstring: names the durable file the staged layout stood in for. Retained by explicit ruling at #447 g4; no shipped surface directs an agent to this script",
        "survivor script's docstring: names the four-file staged layout the script writes",
        "survivor script's docstring: names the verifier (deleted at g4) whose accepted shapes the layout was built to match -- a record of why the layout is what it is",
        "survivor script: the TRIO_FILES constant, the literal filenames it writes into a worktree-local staging dir",
        "survivor script: the staged file's own header text, naming the durable destination it was staged for",
        "survivor script: the FENCE.md manifest line describing one staged file",
        "survivor script: a comment naming the verifier that would have rejected an invalid staged delta",
        "survivor script: the write call that creates the staged file, named by its literal filename",
    ],
    "scripts/verify_episode_captured.py": [
        "the replacement gate's own docstring: names what it replaced, which is the fact that makes the gate's existence legible",
        "the replacement gate's own docstring: names the second retired file and the issue that retired both",
    ],
    "skills/commander/templates/COMMANDER_SPINE.template.json": [
        "commander spine archive.c4: the deny_globs RE-STAGING BLOCK. Both retired path strings are kept here deliberately so a future run cannot re-stage either file -- a stronger reason than the one they were added for",
    ],
}


def main() -> int:
    root = Path(".")
    tracked = vr.tracked_paths(root)
    shipped = [path for path in tracked if vr.is_shipped(path)]

    sites: dict[str, list[str]] = {}
    for path in shipped:
        lines = vr._read_lines(root, path)
        if lines is None:
            continue
        for line in lines:
            if any(name in line for name in vr.RETIRED_NAMES):
                sites.setdefault(path, []).append(vr.normalize(line))

    assert set(sites) == set(REASONS), (
        f"census reasons out of sync with the tree: "
        f"missing {sorted(set(sites) - set(REASONS))}, extra {sorted(set(REASONS) - set(sites))}"
    )

    out = [HEADER.rstrip("\n")]
    total = 0
    for path in sorted(sites):
        mentions, reasons = sites[path], REASONS[path]
        assert len(mentions) == len(reasons), (path, len(mentions), len(reasons))
        for mention, reason in zip(mentions, reasons):
            out.append("")
            out.append(f"# {reason}")
            out.append(f"{path}:{mention}")
            total += 1

    text = "\n".join(out) + "\n"
    census = Path(vr.RETIRED_NAME_CENSUS_PATH)
    census.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
    print(f"wrote {census} with {total} entries across {len(sites)} paths")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

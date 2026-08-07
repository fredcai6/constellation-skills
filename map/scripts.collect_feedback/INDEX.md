# scripts.collect_feedback
scripts/collect_feedback.py, 745 lines, 15 holes

Sweep consuming projects' CONSTELLATION_FEEDBACK.md exports into one report.

Reads `.agent-work/CONSTELLATION_FEEDBACK.md` from each project root and tracks
per-entry state in a sidecar (`CONSTELLATION_FEEDBACK.collected.json`): entries
are deduplicated by a semantic fingerprint (normalized observed+proposal text)
and each fingerprint carries one state: `collected` (ingested by a sweep).
Consuming repos remove a handled finding from their export rather than marking
it resolved, so there is no resolved state — collected entries stay visible in
every report until the consuming repo deletes them.

A finding's identity (fingerprint) is derived, in order of preference, from:
(1) the originating **lesson id** carried in the export's `Lesson` field — the
stable id the lessons playbook already curates (unique ids, `amend` to reword
without forking identity); (2) the **candidate slug**, with parenthetical
annotations/cross-refs stripped (those drift run-to-run but are not identity);
(3) the legacy observed+proposal **content hash**. Slugs drift even when humans
mean the same finding (`spine-lease-stale-on-long-crew` vs `...-step` vs one with
a trailing "(CORROBORATES …)"), so a stable lesson id is the durable handle;
the slug is the fallback when no lesson id is present. Recurrence is counted by
how many entries share a fingerprint — including repeats within a single
project — and a finding is promoted to validated/recurring once it reaches
RECURRENCE_THRESHOLD occurrences. Cross-project recurrence remains a distinct,
stronger callout.

Issue management stays human-gated. `--file-issues` syncs a GitHub-issue backlog
in *this* repo (the design's "opens/updates issues here") and defaults to a dry
run — it prints what it would do and touches nothing until `--confirm`. The sync
does two things, both keyed off a local ledger
(`.agent-work/CONSTELLATION_INBOX.json`, one entry per finding fingerprint):
**file** a new issue for each open validated finding not yet filed (recurring
only by default; `--include-singles` widens); and **comment** on a filed issue
when its recurrence grows past the ledger's watermark, so the backlog reflects
live pressure not day-one pressure. Both actions are idempotent — re-runs never
duplicate or re-comment. Issues are closed the normal way: a fixing PR references
the issue and a human closes it.

imports stdlib: __future__.annotations, argparse, datetime.date, hashlib, json, pathlib.Path, re, subprocess, sys
imports third-party: agent_work_root.durable_root
imported by: none found

```python
ENTRY_HEADING_RE = re.compile('^## .+$', re.MULTILINE)
FIELD_RE = re.compile('^- \\*\\*(.+?):\\*\\*\\s*`?(.*?)`?\\s*$')
PROSE_HEADING_RE = re.compile('^### (.+)$', re.MULTILINE)
INLINE_FIELD_RE = re.compile('\\*\\*([A-Z][A-Za-z /]+?):\\*\\*\\s*')
_PROSE_LABELS = {'observed': 'observed', 'upstream fix': 'proposal', 'proposal': 'proposal', 'lesson': ...
SIDECAR_NAME = 'CONSTELLATION_FEEDBACK.collected.json'
INBOX_NAME = 'CONSTELLATION_INBOX.json'
RECURRENCE_THRESHOLD = 2
Hits = dict[str, list[tuple[str, dict[str, str]]]]
```

- [_map_prose_label](_map_prose_label.md) function: HOLE: no docstring
- [_extract_inline_fields](_extract_inline_fields.md) function: Pull `**Label:** value` spans out of a prose sub-block.
- [_utf8_stdio](_utf8_stdio.md) function: Per field feedback: don't make every call site set PYTHONIOENCODING.
- [parse_entries](parse_entries.md) function: HOLE: no docstring
- [parse_prose_findings](parse_prose_findings.md) function: Parse the legacy prose export shape into finding dicts.
- [_is_finding](_is_finding.md) function: A parsed block is a real finding only if it carries at least one substantive
- [_is_prose_finding](_is_prose_finding.md) function: Prose blocks always have a candidate (derived from the heading), so a
- [iter_findings](iter_findings.md) function: Findings in either export shape (content-less blocks dropped).
- [_hash12](_hash12.md) function: HOLE: no docstring
- [_content_fingerprint](_content_fingerprint.md) function: Legacy fingerprint: hash of normalized observed+proposal prose.
- [_slugify](_slugify.md) function: Normalize a human label into a stable kebab slug.
- [_raw_slug](_raw_slug.md) function: The pre-annotation-stripping slug (the prior scheme), for back-compat lookup.
- [fingerprint](fingerprint.md) function: Stable identity for a finding, in order of preference.
- [fingerprints](fingerprints.md) function: Every key an entry may be recorded under, newest scheme first.
  - [fingerprints.add](fingerprints.add.md) method: HOLE: no docstring
- [_in_sidecar](_in_sidecar.md) function: True if any of the entry's fingerprints (new or legacy) is in `table`.
- [_sidecar_path](_sidecar_path.md) function: HOLE: no docstring
- [load_sidecar](load_sidecar.md) function: HOLE: no docstring
- [save_sidecar](save_sidecar.md) function: HOLE: no docstring
- [collect](collect.md) function: Return (new, open_unresolved) candidate groups keyed by fingerprint.
- [mark_collected](mark_collected.md) function: Record every current entry fingerprint as collected; returns count newly marked.
- [merge_hits](merge_hits.md) function: Merge candidate groups (e.g. new + open) into one fingerprint -> hits view.
- [_inbox_path_for](_inbox_path_for.md) function: HOLE: no docstring
- [load_inbox](load_inbox.md) function: HOLE: no docstring
- [save_inbox](save_inbox.md) function: HOLE: no docstring
- [issue_spec](issue_spec.md) function: Render one finding group into a fileable GitHub issue spec.
- [gh_file_issue](gh_file_issue.md) function: Default filer: open a GitHub issue via `gh`. Returns {number, url}.
- [gh_comment_issue](gh_comment_issue.md) function: Default commenter: post a comment on an existing issue via `gh`.
- [eligible_for_filing](eligible_for_filing.md) function: Open findings worth filing, most-recurring first, skipping already-filed.
- [_issue_ref](_issue_ref.md) function: A `gh`-addressable handle for a ledger entry (issue number, else url).
- [_is_open](_is_open.md) function: HOLE: no docstring
- [_recurrence_comment](_recurrence_comment.md) function: HOLE: no docstring
- [sync_issues](sync_issues.md) function: File new eligible findings and comment on filed issues whose recurrence has
- [file_issues](file_issues.md) function: Thin wrapper over `sync_issues` for callers/tests that only file.
- [_render_group](_render_group.md) function: HOLE: no docstring
- [render_report](render_report.md) function: HOLE: no docstring
- [_file_issues_cli](_file_issues_cli.md) function: Handle the --file-issues mode (file/comment); returns an exit code.
- [main](main.md) function: HOLE: no docstring

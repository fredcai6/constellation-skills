# scripts.file_issue_set
scripts/file_issue_set.py, 358 lines, 31 holes

File a cut-work issue set to a tracker — the constellation-to-issues FILER.

Ports-and-adapters (DESIGN_SPEC Section A): a tracker-agnostic issue-set
manifest is filed through ONE swappable adapter seam. Two adapters ship this
epic — `github` (the real, GitHub-first default) and `markdown` (the offline
test fixture / portability proof). A `gitlab` seam is deliberately NOT built
(the seam exists; only github + markdown ship). GitHub-first, seam-pluggable,
not GitHub-only.

Two safeties, both cheap and both load-bearing:

  * THE RAIL RUNS FIRST. `verify_issue_set` (verify_issue_set.py) gates every
    filing; a malformed set raises before ANY tracker write, so a malformed
    manifest can never reach a tracker.

  * IDEMPOTENT VIA A RECEIPT + KEY-EXISTENCE CHECK. Every epic/issue carries a
    deterministic idempotency key embedded in its filed body. A crash mid-file
    re-runs without a duplicate epic: the receipt is the fast path, and when the
    receipt is missing an entry (the crash landed between the tracker write and
    the receipt write) the adapter re-finds the already-filed item BY KEY and
    adopts it. Correctness holds at all three crash-injection points
    (before-file / after-file-before-receipt / after-receipt; TF7).

Downstream seam: the epic body is the wave-ordered task list (a topological
sort of the `blocks` edges) with AFK/HITL labels — the Admiral's intake
consumes it. Standard library only (the github adapter shells out to `gh`).

imports stdlib: __future__.annotations, argparse, hashlib, json, os, pathlib.Path, subprocess, sys
imports third-party: verify_issue_set.IssueSetError, verify_issue_set.verify_issue_set
imported by: none found

```python
KEY_PREFIX = 'constellation-key'
```

- [CrashInjected](CrashInjected.md) class: Test-only: raised at a named crash-injection point to prove idempotency.
- [_short](_short.md) function: HOLE: no docstring
- [epic_key](epic_key.md) function: HOLE: no docstring
- [issue_key](issue_key.md) function: HOLE: no docstring
- [key_marker](key_marker.md) function: The hidden marker embedded in a filed body so an adapter can find the
- [wave_order](wave_order.md) function: Kahn-style layering: wave 0 = issues nothing blocks-into (no unmet
- [build_epic_body](build_epic_body.md) function: The downstream seam: wave-ordered task list + AFK/HITL labels + the
- [build_issue_body](build_issue_body.md) function: HOLE: no docstring
- [FilingAdapter](FilingAdapter.md) class: The port. An adapter finds an item by its idempotency key (crash
  - [FilingAdapter.find_epic](FilingAdapter.find_epic.md) method: HOLE: no docstring
  - [FilingAdapter.create_epic](FilingAdapter.create_epic.md) method: HOLE: no docstring
  - [FilingAdapter.find_issue](FilingAdapter.find_issue.md) method: HOLE: no docstring
  - [FilingAdapter.create_issue](FilingAdapter.create_issue.md) method: HOLE: no docstring
- [MarkdownAdapter](MarkdownAdapter.md) class: Offline fixture / portability proof: the 'tracker' is a single markdown
  - [MarkdownAdapter.__init__](MarkdownAdapter.__init__.md) method: HOLE: no docstring
  - [MarkdownAdapter._text](MarkdownAdapter._text.md) method: HOLE: no docstring
  - [MarkdownAdapter._append](MarkdownAdapter._append.md) method: HOLE: no docstring
  - [MarkdownAdapter._find](MarkdownAdapter._find.md) method: HOLE: no docstring
  - [MarkdownAdapter.find_epic](MarkdownAdapter.find_epic.md) method: HOLE: no docstring
  - [MarkdownAdapter.create_epic](MarkdownAdapter.create_epic.md) method: HOLE: no docstring
  - [MarkdownAdapter.find_issue](MarkdownAdapter.find_issue.md) method: HOLE: no docstring
  - [MarkdownAdapter.create_issue](MarkdownAdapter.create_issue.md) method: HOLE: no docstring
  - [MarkdownAdapter.count_epics](MarkdownAdapter.count_epics.md) method: HOLE: no docstring
  - [MarkdownAdapter.count_issues](MarkdownAdapter.count_issues.md) method: HOLE: no docstring
- [GitHubAdapter](GitHubAdapter.md) class: The shipped, GitHub-first adapter. Shells out to `gh`; finds an existing
  - [GitHubAdapter.__init__](GitHubAdapter.__init__.md) method: HOLE: no docstring
  - [GitHubAdapter._gh](GitHubAdapter._gh.md) method: HOLE: no docstring
  - [GitHubAdapter._find](GitHubAdapter._find.md) method: HOLE: no docstring
  - [GitHubAdapter._create](GitHubAdapter._create.md) method: HOLE: no docstring
  - [GitHubAdapter.find_epic](GitHubAdapter.find_epic.md) method: HOLE: no docstring
  - [GitHubAdapter.create_epic](GitHubAdapter.create_epic.md) method: HOLE: no docstring
  - [GitHubAdapter.find_issue](GitHubAdapter.find_issue.md) method: HOLE: no docstring
  - [GitHubAdapter.create_issue](GitHubAdapter.create_issue.md) method: HOLE: no docstring
- [build_adapter](build_adapter.md) function: HOLE: no docstring
- [_load_receipt](_load_receipt.md) function: HOLE: no docstring
- [_write_receipt](_write_receipt.md) function: HOLE: no docstring
- [_crash](_crash.md) function: HOLE: no docstring
- [file_issue_set](file_issue_set.md) function: File the set idempotently, returning the receipt. Runs the rail first.
- [main](main.md) function: HOLE: no docstring

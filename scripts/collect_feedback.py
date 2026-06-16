#!/usr/bin/env python
"""Sweep consuming projects' CONSTELLATION_FEEDBACK.md exports into one report.

Reads `.agent-work/CONSTELLATION_FEEDBACK.md` from each project root and tracks
per-entry state in a sidecar (`CONSTELLATION_FEEDBACK.collected.json`): entries
are deduplicated by a semantic fingerprint (normalized observed+proposal text)
and each fingerprint is independently `collected` (ingested by a sweep) and
later `resolved` (acted on upstream). Collected-but-unresolved candidates stay
visible in every report until resolved — collected never means fixed.

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
does three things, all keyed off a local ledger
(`.agent-work/CONSTELLATION_INBOX.json`, one entry per finding fingerprint):
**file** a new issue for each open validated finding not yet filed (recurring
only by default; `--include-singles` widens); **comment** on a filed issue when
its recurrence grows past the ledger's watermark, so the backlog reflects live
pressure not day-one pressure; and **close** a filed issue once its finding is
resolved in any swept project, so the backlog tracks completion. The ledger makes
all three idempotent — re-runs never duplicate, re-comment, or re-close.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ENTRY_HEADING_RE = re.compile(r"^## .+$", re.MULTILINE)
FIELD_RE = re.compile(r"^- \*\*(.+?):\*\*\s*`?(.*?)`?\s*$")
SIDECAR_NAME = "CONSTELLATION_FEEDBACK.collected.json"
INBOX_NAME = "CONSTELLATION_INBOX.json"

# A finding is treated as recurring/validated once this many entries share a
# fingerprint, regardless of how many distinct projects contributed. Cross-project
# recurrence remains a distinct, stronger signal called out separately.
RECURRENCE_THRESHOLD = 2


def _utf8_stdio() -> None:
    """Per field feedback: don't make every call site set PYTHONIOENCODING."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_utf8_stdio()


def parse_entries(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    headings = list(ENTRY_HEADING_RE.finditer(text))
    for i, match in enumerate(headings):
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        block = text[match.start() : end]
        heading = match.group(0).lstrip("# ").strip()
        if heading.startswith("`<date>`"):
            continue  # template placeholder entry
        entry = {"heading": heading}
        for line in block.splitlines():
            field = FIELD_RE.match(line.strip())
            if field:
                entry[field.group(1).strip().lower()] = field.group(2).strip()
        entries.append(entry)
    return entries


def _is_finding(entry: dict[str, str]) -> bool:
    """A parsed block is a real finding only if it carries at least one substantive
    field. Section headers and malformed blocks (no candidate, observed, or
    proposal) are export noise — they otherwise hash-collide on empty content into
    bogus "recurring" candidates. Same spirit as the `<date>` placeholder skip.
    """
    return any((entry.get(k) or "").strip() for k in ("candidate", "observed", "proposal"))


def iter_findings(text: str) -> list[dict[str, str]]:
    """Parsed entries that are actually findings (content-less blocks dropped)."""
    return [e for e in parse_entries(text) if _is_finding(e)]


def _hash12(basis: str) -> str:
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:12]


def _content_fingerprint(entry: dict[str, str]) -> str:
    """Legacy fingerprint: hash of normalized observed+proposal prose.

    Kept for backward-compatible sidecar lookups (entries collected/resolved
    under the old scheme) and as the fallback when an entry has no candidate slug.
    """
    basis = (entry.get("observed", "") + "|" + entry.get("proposal", "")).lower()
    basis = re.sub(r"[^a-z0-9|]+", " ", basis)
    basis = re.sub(r"\s+", " ", basis).strip()
    return _hash12(basis)


def _slugify(text: str) -> str:
    """Normalize a human label into a stable kebab slug.

    Strips parenthetical annotations and cross-refs (e.g. "(CORROBORATES
    issue-446)") that drift run-to-run but are not part of a finding's identity,
    then collapses the rest to kebab-case.
    """
    text = re.sub(r"\([^)]*\)", " ", text.lower())
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _raw_slug(text: str) -> str:
    """The pre-annotation-stripping slug (the prior scheme), for back-compat lookup."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def fingerprint(entry: dict[str, str]) -> str:
    """Stable identity for a finding, in order of preference.

    1. the originating lesson id (`Lesson` field) — the identity the lessons
       playbook curates and keeps stable across rewording via `amend`;
    2. the candidate slug with annotations stripped — the fallback when an entry
       has no lesson id;
    3. the legacy observed+proposal content hash — last resort.
    Always 12 hex chars so the sidecar/ledger shape is unchanged.
    """
    lesson = _slugify(entry.get("lesson", ""))
    if lesson:
        return _hash12("lesson:" + lesson)
    slug = _slugify(entry.get("candidate", ""))
    if slug:
        return _hash12("candidate:" + slug)
    return _content_fingerprint(entry)


def fingerprints(entry: dict[str, str]) -> list[str]:
    """Every key an entry may be recorded under, newest scheme first.

    Includes the lesson-id fingerprint, the annotation-stripped slug fingerprint,
    the prior raw-slug fingerprint (pre-stripping), and the legacy content hash —
    so collected/resolved/filed state recorded under ANY earlier scheme still
    matches after an identity change.
    """
    out: list[str] = []

    def add(fp: str) -> None:
        if fp and fp not in out:
            out.append(fp)

    lesson = _slugify(entry.get("lesson", ""))
    if lesson:
        add(_hash12("lesson:" + lesson))
    candidate = entry.get("candidate", "")
    if _slugify(candidate):
        add(_hash12("candidate:" + _slugify(candidate)))
    if _raw_slug(candidate):
        add(_hash12("candidate:" + _raw_slug(candidate)))
    add(_content_fingerprint(entry))
    return out


def _in_sidecar(entry: dict[str, str], table: dict) -> bool:
    """True if any of the entry's fingerprints (new or legacy) is in `table`."""
    return any(fp in table for fp in fingerprints(entry))


def _sidecar_path(root: Path) -> Path:
    return root / ".agent-work" / SIDECAR_NAME


def load_sidecar(root: Path) -> dict:
    path = _sidecar_path(root)
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"collected": {}, "resolved": {}}


def save_sidecar(root: Path, state: dict) -> None:
    _sidecar_path(root).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


Hits = dict[str, list[tuple[str, dict[str, str]]]]


def collect(project_roots: list[Path]) -> tuple[Hits, Hits]:
    """Return (new, open_unresolved) candidate groups keyed by fingerprint."""
    new: Hits = {}
    open_unresolved: Hits = {}
    for root in project_roots:
        feedback = root / ".agent-work" / "CONSTELLATION_FEEDBACK.md"
        if not feedback.is_file():
            continue
        state = load_sidecar(root)
        for entry in iter_findings(feedback.read_text(encoding="utf-8")):
            fp = fingerprint(entry)
            if _in_sidecar(entry, state["resolved"]):
                continue
            bucket = open_unresolved if _in_sidecar(entry, state["collected"]) else new
            bucket.setdefault(fp, []).append((root.name, entry))
    return new, open_unresolved


def mark_collected(root: Path) -> int:
    """Record every current entry fingerprint as collected; returns count newly marked."""
    feedback = root / ".agent-work" / "CONSTELLATION_FEEDBACK.md"
    if not feedback.is_file():
        return 0
    state = load_sidecar(root)
    today = date.today().isoformat()
    marked = 0
    for entry in iter_findings(feedback.read_text(encoding="utf-8")):
        fp = fingerprint(entry)
        if not _in_sidecar(entry, state["collected"]):
            state["collected"][fp] = today
            marked += 1
    save_sidecar(root, state)
    return marked


def mark_resolved(root: Path, fp: str, note: str) -> bool:
    state = load_sidecar(root)
    if fp in state["resolved"]:
        return False
    state["resolved"][fp] = {"date": date.today().isoformat(), "note": note}
    state["collected"].setdefault(fp, date.today().isoformat())
    save_sidecar(root, state)
    return True


def resolved_across(project_roots: list[Path]) -> dict[str, str]:
    """fingerprint -> resolution note, unioned across all swept project sidecars.

    A finding resolved in any project is fixed upstream (the export is the same
    shared-machinery finding), so the inbox closes its issue.
    """
    out: dict[str, str] = {}
    for root in project_roots:
        for fp, info in load_sidecar(root).get("resolved", {}).items():
            note = info.get("note", "") if isinstance(info, dict) else str(info)
            out.setdefault(fp, note)
    return out


# --- Inbox: human-gated issue filing -------------------------------------------


def merge_hits(*groups: Hits) -> Hits:
    """Merge candidate groups (e.g. new + open) into one fingerprint -> hits view.

    Filing eligibility cares about a finding's *total* open occurrences across the
    whole sweep, regardless of which projects have already marked it collected, so
    the new and open-unresolved buckets are merged before counting recurrence.
    """
    merged: Hits = {}
    for group in groups:
        for fp, hits in group.items():
            merged.setdefault(fp, []).extend(hits)
    return merged


def _inbox_path_for(root: Path) -> Path:
    return root / ".agent-work" / INBOX_NAME


def load_inbox(path: Path) -> dict:
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"filed": {}}


def save_inbox(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def issue_spec(fp: str, hits: list[tuple[str, dict[str, str]]], labels=()) -> dict:
    """Render one finding group into a fileable GitHub issue spec."""
    first = hits[0][1]
    projects = sorted({p for p, _ in hits})
    candidate = (first.get("candidate") or "").strip()
    # A backlog title should read like a finding, not a hash. Prefer the human slug;
    # when an entry carries none, degrade to a trimmed observed snippet before the
    # bare fingerprint, so the issue is at least scannable.
    if candidate:
        label = candidate
    else:
        observed = (first.get("observed") or "").strip()
        label = (observed[:60].rstrip() + "…") if len(observed) > 60 else (observed or fp)
    title = f"[constellation-feedback] {label} ({len(hits)}× / {len(projects)} project(s))"
    body = [
        "Auto-surfaced by `scripts/collect_feedback.py` from consuming-project "
        "exports. Triage and any resulting skill/template/engine change stay "
        "human-gated — this issue is a backlog entry, not a decision.",
        "",
        f"- **fingerprint:** `{fp}`",
        f"- **occurrences:** {len(hits)} across {len(projects)} project(s): "
        f"{', '.join(projects)}",
    ]
    for key in ("observed", "cost", "proposal", "grounding", "template vintage", "confidence"):
        if first.get(key):
            body.append(f"- **{key}:** {first[key]}")
    body += [
        "",
        "_Validation signal: recurrence. Cross-project recurrence is the strongest; "
        "a single-project scope tag is a claim to verify, not a fact._",
    ]
    return {
        "fingerprint": fp,
        "candidate": candidate or fp,
        "title": title,
        "body": "\n".join(body),
        "projects": projects,
        "occurrences": len(hits),
        "labels": list(labels),
    }


def gh_file_issue(spec: dict, *, repo: str | None = None) -> dict:
    """Default filer: open a GitHub issue via `gh`. Returns {number, url}."""
    cmd = ["gh", "issue", "create", "--title", spec["title"], "--body", spec["body"]]
    for label in spec.get("labels", ()):
        cmd += ["--label", label]
    if repo:
        cmd += ["--repo", repo]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    out = result.stdout.strip()
    url = out.splitlines()[-1] if out else ""
    number = url.rstrip("/").rsplit("/", 1)[-1] if url else ""
    return {"number": number, "url": url}


def gh_comment_issue(ref: str, body: str, *, repo: str | None = None) -> dict:
    """Default commenter: post a comment on an existing issue via `gh`."""
    cmd = ["gh", "issue", "comment", ref, "--body", body]
    if repo:
        cmd += ["--repo", repo]
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    return {}


def gh_close_issue(ref: str, comment: str, *, repo: str | None = None) -> dict:
    """Default closer: close an issue with a comment via `gh`."""
    cmd = ["gh", "issue", "close", ref, "--comment", comment]
    if repo:
        cmd += ["--repo", repo]
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    return {}


def eligible_for_filing(
    merged: Hits, inbox: dict, *, include_singles: bool
) -> list[tuple[str, list[tuple[str, dict[str, str]]]]]:
    """Open findings worth filing, most-recurring first, skipping already-filed.

    Default keeps the backlog high-signal: only findings at or above the
    recurrence threshold. `include_singles` widens to every open finding.
    """
    out = []
    for fp, hits in sorted(merged.items(), key=lambda kv: -len(kv[1])):
        if fp in inbox["filed"]:
            continue
        if not include_singles and len(hits) < RECURRENCE_THRESHOLD:
            continue
        out.append((fp, hits))
    return out


def _issue_ref(entry: dict) -> str:
    """A `gh`-addressable handle for a ledger entry (issue number, else url)."""
    return entry.get("issue") or entry.get("url") or ""


def _is_open(entry: dict) -> bool:
    # Back-compat: pre-lifecycle ledger entries carry no status and are open.
    return entry.get("status", "open") == "open"


def _recurrence_comment(entry: dict, occurrences: int, projects: list[str], hits) -> str:
    was = f"{entry.get('occurrences', 0)}× / {len(entry.get('projects', []))} project(s)"
    latest = (hits[-1][1].get("grounding") or "").strip()
    body = (
        f"Recurred again — now **{occurrences}× across {len(projects)} project(s)**: "
        f"{', '.join(projects)} (was {was})."
    )
    if latest:
        body += f"\n\nLatest grounding: {latest}"
    body += (
        "\n\n_Auto-updated by collect_feedback. A recurrence is debt accruing on an "
        "unfixed finding, not added confidence — fix upstream._"
    )
    return body


def sync_issues(
    merged: Hits,
    resolved: dict[str, str],
    *,
    inbox_path: Path,
    filer=gh_file_issue,
    commenter=gh_comment_issue,
    closer=gh_close_issue,
    include_singles: bool = False,
    confirm: bool = False,
    labels=(),
    repo: str | None = None,
) -> dict:
    """Open / update / close the inbox issues for the current sweep. Dry run unless
    `confirm`. Three lifecycle actions:

    - **file** a new issue for each eligible open finding not yet in the ledger;
    - **comment** on a filed, still-open issue whose recurrence has grown since it
      was last recorded (more occurrences or a new project) — the ledger's
      occurrence/project counts are the watermark, so a comment advances them and
      re-runs never re-comment the same level;
    - **close** a filed, still-open issue whose finding is now resolved in any
      swept project — so the backlog tracks completion, not just first sighting.

    The ledger is saved after each successful action, so a mid-run gh failure
    leaves prior actions durably recorded.
    """
    inbox = load_inbox(inbox_path)
    ledger = inbox.setdefault("filed", {})

    to_file = [
        issue_spec(fp, hits, labels=labels)
        for fp, hits in eligible_for_filing(merged, inbox, include_singles=include_singles)
    ]

    to_update = []
    for fp, hits in merged.items():
        if fp in resolved:
            continue  # the close path owns a resolved finding
        entry = ledger.get(fp)
        if not entry or not _is_open(entry):
            continue
        occ, projects = len(hits), sorted({p for p, _ in hits})
        grew = occ > entry.get("occurrences", 0) or bool(
            set(projects) - set(entry.get("projects", []))
        )
        if grew:
            to_update.append((fp, entry, occ, projects, hits))

    to_close = []
    for fp, note in resolved.items():
        entry = ledger.get(fp)
        if entry and _is_open(entry):
            to_close.append((fp, entry, note))

    if not confirm:
        return {
            "would_file": to_file,
            "would_update": [
                {"fingerprint": fp, "ref": _issue_ref(e),
                 "from": f"{e.get('occurrences', 0)}×/{len(e.get('projects', []))}p",
                 "to": f"{occ}×/{len(projs)}p"}
                for fp, e, occ, projs, _ in to_update
            ],
            "would_close": [
                {"fingerprint": fp, "ref": _issue_ref(e), "note": n} for fp, e, n in to_close
            ],
            "filed": [], "updated": [], "closed": [],
        }

    filed, updated, closed = [], [], []
    for spec in to_file:
        ref = filer(spec, repo=repo)
        ledger[spec["fingerprint"]] = {
            "issue": ref.get("number", ""),
            "url": ref.get("url", ""),
            "title": spec["title"],
            "candidate": spec["candidate"],
            "projects": spec["projects"],
            "occurrences": spec["occurrences"],
            "status": "open",
            "date": date.today().isoformat(),
        }
        save_inbox(inbox_path, inbox)
        filed.append({**spec, **ref})

    for fp, entry, occ, projects, hits in to_update:
        commenter(_issue_ref(entry), _recurrence_comment(entry, occ, projects, hits), repo=repo)
        entry["occurrences"], entry["projects"] = occ, projects
        entry["last_updated"] = date.today().isoformat()
        save_inbox(inbox_path, inbox)
        updated.append({"fingerprint": fp, "ref": _issue_ref(entry), "occurrences": occ})

    for fp, entry, note in to_close:
        closer(
            _issue_ref(entry),
            f"Resolved upstream: {note}. Auto-closed by collect_feedback "
            "(finding no longer open in any swept project).",
            repo=repo,
        )
        entry["status"] = "closed"
        entry["closed_date"] = date.today().isoformat()
        entry["resolved_note"] = note
        save_inbox(inbox_path, inbox)
        closed.append({"fingerprint": fp, "ref": _issue_ref(entry), "note": note})

    return {
        "would_file": [], "would_update": [], "would_close": [],
        "filed": filed, "updated": updated, "closed": closed,
    }


def file_issues(
    merged: Hits,
    *,
    inbox_path: Path,
    filer=gh_file_issue,
    include_singles: bool = False,
    confirm: bool = False,
    labels=(),
    repo: str | None = None,
) -> dict:
    """Open-only path (file new eligible findings, no update/close). Thin wrapper
    over `sync_issues` with no resolved set; kept for callers/tests that only want
    the filing action."""
    return sync_issues(
        merged, {}, inbox_path=inbox_path, filer=filer,
        include_singles=include_singles, confirm=confirm, labels=labels, repo=repo,
    )


# --- Reporting ------------------------------------------------------------------


def _render_group(lines: list[str], title: str, group: Hits) -> None:
    if not group:
        return
    lines.append(f"## {title}")
    lines.append("")
    for fp, hits in sorted(group.items(), key=lambda kv: -len(kv[1])):
        first = hits[0][1]
        projects = sorted({p for p, _ in hits})
        lines.append(f"### {first.get('candidate', fp)} ({fp})")
        lines.append(
            f"- occurrences: {len(hits)} across {len(projects)} project(s): "
            f"{', '.join(projects)}"
        )
        for key in ("observed", "cost", "proposal", "grounding", "template vintage", "confidence"):
            if first.get(key):
                lines.append(f"- {key}: {first[key]}")
        lines.append("")


def render_report(new: Hits, open_unresolved: Hits) -> str:
    lines = [f"# Constellation Feedback Sweep — {date.today().isoformat()}", ""]
    if not new and not open_unresolved:
        lines.append("No new or open candidates.")
        return "\n".join(lines) + "\n"

    # Recurrence is counted by total occurrences sharing a fingerprint (within a
    # single project counts), not only across projects. Cross-project recurrence
    # is a distinct, stronger validation callout.
    recurring = {fp: hits for fp, hits in new.items() if len(hits) >= RECURRENCE_THRESHOLD}
    cross_project = {fp: hits for fp, hits in recurring.items() if len({p for p, _ in hits}) > 1}
    singles = {fp: hits for fp, hits in new.items() if fp not in recurring}

    lines.append(
        f"{len(new)} new candidate(s) ({len(recurring)} recurring, "
        f"{len(cross_project)} of them across multiple projects), "
        f"{len(open_unresolved)} previously collected and still unresolved."
    )
    lines.append("")
    _render_group(
        lines,
        f"New — recurring (validated, >= {RECURRENCE_THRESHOLD} occurrences)",
        recurring,
    )
    _render_group(
        lines,
        "New — cross-project recurrence (strongest validation signal)",
        cross_project,
    )
    _render_group(lines, "New — single-project (scope tag is a claim, verify)", singles)
    _render_group(lines, "Open — collected earlier, not yet resolved", open_unresolved)
    return "\n".join(lines) + "\n"


def _file_issues_cli(roots, new, open_unresolved, args, filer, commenter, closer) -> int:
    """Handle the --file-issues mode (file/update/close); returns an exit code."""
    inbox_path = args.inbox or (Path.cwd() / ".agent-work" / INBOX_NAME)
    merged = merge_hits(new, open_unresolved)
    resolved = resolved_across(roots)
    try:
        result = sync_issues(
            merged,
            resolved,
            inbox_path=inbox_path,
            filer=filer,
            commenter=commenter,
            closer=closer,
            include_singles=args.include_singles,
            confirm=args.confirm,
            labels=args.label,
            repo=args.repo,
        )
    except FileNotFoundError:
        print("error: `gh` not found on PATH; cannot manage issues", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as exc:
        print(f"error: gh failed: {exc.stderr or exc}", file=sys.stderr)
        print(f"(actions completed before the failure are recorded in {inbox_path})", file=sys.stderr)
        return 1

    if not args.confirm:
        wf, wu, wc = result["would_file"], result["would_update"], result["would_close"]
        if not (wf or wu or wc):
            print(
                "Inbox up to date: nothing to file, update, or close "
                "(recurring findings only; --include-singles to widen)."
            )
            return 0
        print(f"DRY RUN — {len(wf)} file, {len(wu)} update, {len(wc)} close; re-run with --confirm:\n")
        for spec in wf:
            print(f"  [file]   {spec['title']}")
            print(f"           fingerprint {spec['fingerprint']}, projects: {', '.join(spec['projects'])}")
        for u in wu:
            print(f"  [update] {u['ref']}  {u['from']} -> {u['to']}  ({u['fingerprint']})")
        for c in wc:
            print(f"  [close]  {c['ref']}  resolved: {c['note']}  ({c['fingerprint']})")
        return 0

    filed, updated, closed = result["filed"], result["updated"], result["closed"]
    if not (filed or updated or closed):
        print("Inbox already up to date (nothing to file, update, or close).")
        return 0
    for entry in filed:
        ref = f"#{entry['number']}" if entry.get("number") else entry.get("url", "")
        print(f"filed  {ref}: {entry['title']}")
    for u in updated:
        print(f"update {u['ref']}: now {u['occurrences']}× ({u['fingerprint']})")
    for c in closed:
        print(f"close  {c['ref']}: {c['note']} ({c['fingerprint']})")
    print(f"\nfiled {len(filed)}, updated {len(updated)}, closed {len(closed)}; ledger: {inbox_path}")
    return 0


def main(
    argv: list[str] | None = None,
    *,
    filer=gh_file_issue,
    commenter=gh_comment_issue,
    closer=gh_close_issue,
) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("projects", nargs="*", type=Path, help="Project roots to sweep")
    parser.add_argument(
        "--config", type=Path, help="JSON file with a list of project root paths"
    )
    parser.add_argument("--out", type=Path, help="Write the report here instead of stdout")
    parser.add_argument(
        "--mark", action="store_true", help="Record current entries as collected (per entry)"
    )
    parser.add_argument(
        "--resolve",
        metavar="FINGERPRINT",
        help="Mark one candidate resolved across the given projects",
    )
    parser.add_argument(
        "--note", default="", help="Resolution note for --resolve (e.g. 'fixed in PR #19')"
    )
    parser.add_argument(
        "--file-issues",
        action="store_true",
        help="Sync the issue backlog here: file new findings, comment on grown ones, "
        "close resolved ones (dry run unless --confirm)",
    )
    parser.add_argument(
        "--confirm", action="store_true", help="With --file-issues, actually open the issues"
    )
    parser.add_argument(
        "--include-singles",
        action="store_true",
        help="With --file-issues, also file single-occurrence findings (default: recurring only)",
    )
    parser.add_argument(
        "--label", action="append", default=[], help="Label to apply to filed issues (repeatable)"
    )
    parser.add_argument(
        "--inbox", type=Path, help="Inbox ledger path (default .agent-work/CONSTELLATION_INBOX.json)"
    )
    parser.add_argument("--repo", help="Target repo OWNER/NAME for gh (default: inferred from cwd)")
    args = parser.parse_args(argv)

    roots = list(args.projects)
    if args.config:
        try:
            roots.extend(Path(p) for p in json.loads(args.config.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"error: bad --config: {exc}", file=sys.stderr)
            return 2
    if not roots:
        print("error: no project roots given (args or --config)", file=sys.stderr)
        return 2

    if args.resolve:
        if not args.note.strip():
            print("error: --resolve requires --note (what resolved it)", file=sys.stderr)
            return 2
        for root in roots:
            if mark_resolved(root, args.resolve, args.note.strip()):
                print(f"resolved {args.resolve} in {root.name}: {args.note.strip()}")
        return 0

    if args.file_issues:
        new, open_unresolved = collect(roots)
        return _file_issues_cli(roots, new, open_unresolved, args, filer, commenter, closer)

    new, open_unresolved = collect(roots)
    report = render_report(new, open_unresolved)
    if args.out:
        args.out.write_text(report, encoding="utf-8")
        print(f"report written: {args.out}")
    else:
        print(report, end="")

    if args.mark:
        for root in roots:
            marked = mark_collected(root)
            if marked:
                print(f"marked {marked} entr(ies) collected in {root.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

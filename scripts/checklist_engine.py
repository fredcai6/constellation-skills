#!/usr/bin/env python
"""Workbench checklist engine: work one gated/survey plan through its gates.

The engine holds the canonical state; an agent transacts with it one step at a
time. It enforces *mechanism* (ordering, evidence shape, the rework cap, the
consolidation consistency guard) and never judges quality. See
docs/CHECKLIST_SCHEMA.md.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

GATED = "gated"
SURVEY = "survey"
TERMINAL = {"complete", "skipped"}
DEFAULT_REWORK_CAP = 3


class EngineError(Exception):
    """A refusal: the requested transition is not allowed. No exit-0."""


# --------------------------------------------------------------------------- #
# state helpers
# --------------------------------------------------------------------------- #
def load(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(path: Path, data: dict) -> None:
    Path(path).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def load_config(cl: dict, base: Path | None) -> dict:
    """Resolve config: inline `config` wins; else follow `config_ref` to a file
    (tried relative to the working dir, then to the checklist's dir); else empty."""
    if isinstance(cl.get("config"), dict):
        return cl["config"]
    ref = cl.get("config_ref")
    if ref:
        if Path(ref).is_absolute():
            candidates = [Path(ref)]
        else:
            candidates = [Path.cwd() / ref] + ([base / ref] if base is not None else [])
        for path in candidates:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                return data.get("config", data)
    return {}


def rework_cap(config: dict) -> int:
    return int((config or {}).get("rework_cap", DEFAULT_REWORK_CAP))


def task(cl: dict, iid: str) -> dict:
    if iid not in cl.get("tasks", {}):
        raise EngineError(f"no such item {iid!r}")
    return cl["tasks"][iid]


def active_id(cl: dict) -> str | None:
    """First item (in order) that is not yet terminal."""
    for iid in cl.get("items", []):
        if cl["tasks"][iid]["status"] not in TERMINAL:
            return iid
    return None


def _new_evidence_id(t: dict) -> str:
    return f"e-{t['id']}-{len(t.get('evidence', [])) + 1}"


def _check_condition(cond: dict, t: dict) -> bool:
    """Verify one condition. command -> run it; artifact -> presence/match;
    null -> the agent must have attested it (trust but verify).

    A WAIVED condition is honored without re-running its check: a human override
    (see `waive`) has accepted the condition, and re-running the command would
    overwrite `satisfied` and silently un-waive it at every `advance`."""
    if cond.get("waived"):
        return True
    chk = cond.get("check")
    if chk is None:
        return bool(cond.get("satisfied"))
    kind = chk.get("kind")
    if kind == "command":
        proc = subprocess.run(chk["command"], shell=True, capture_output=True, text=True)
        cond["satisfied"] = proc.returncode == 0
        eid = _new_evidence_id(t)
        t.setdefault("evidence", []).append(
            {
                "id": eid,
                "type": "command-output",
                "payload": {"cmd": chk["command"], "exit": proc.returncode},
                "produced_by": "engine",
                "ts": "",
            }
        )
        if cond["satisfied"]:
            cond["satisfied_by"] = eid
        return cond["satisfied"]
    if kind == "artifact":
        want = chk.get("match", {})
        for ev in t.get("evidence", []):
            if ev.get("type") == chk["evidence_type"] and all(
                ev.get("payload", {}).get(k) == v for k, v in want.items()
            ):
                cond["satisfied"] = True
                cond["satisfied_by"] = ev["id"]
                return True
        cond["satisfied"] = False
        return False
    raise EngineError(f"unknown check kind {kind!r}")


# --------------------------------------------------------------------------- #
# verbs (each returns a human/agent-readable message; refusals raise)
# --------------------------------------------------------------------------- #
def current(cl: dict) -> str:
    aid = active_id(cl)
    if aid is None:
        if cl["type"] == SURVEY and cl.get("consolidation") is None:
            return "ALL ITEMS VISITED. Next: consolidate"
        waived = []
        for iid in cl.get("items", []):
            t = cl["tasks"][iid]
            for c in t.get("postconditions", []):
                if c.get("waived"):
                    waived.append(f"{iid}.{c['id']}")
        if waived:
            return f"DONE: no open items. WAIVED: {waived}"
        return "DONE: no open items."
    t = task(cl, aid)
    return f"ACTIVE {aid} [{t['status']}] — {t['imperative']}"


def start(cl: dict, iid: str) -> str:
    t = task(cl, iid)
    if t["status"] != "pending":
        raise EngineError(f"{iid} is {t['status']!r}, cannot start")
    if cl["type"] == GATED and active_id(cl) != iid:
        raise EngineError(f"{iid} is not the active gate; start {active_id(cl)!r} first")
    unmet = [c["id"] for c in t.get("preconditions", []) if not _check_condition(c, t)]
    if unmet:
        raise EngineError(f"{iid}: preconditions unmet {unmet} (verify upstream work, then attest)")
    t["status"] = "in-progress"
    return f"{iid} -> in-progress"


def advance(cl: dict, iid: str, from_child: str | None = None, base_dir: Path | None = None) -> str:
    if cl["type"] != GATED:
        raise EngineError("advance is for gated checklists; use record")
    t = task(cl, iid)
    if t["status"] != "in-progress":
        raise EngineError(f"{iid} is {t['status']!r}, must be in-progress to advance")
    if from_child:
        child_path = Path(from_child)
        if not child_path.is_absolute() and base_dir is not None:
            child_path = base_dir / from_child
        if not child_path.exists():
            raise EngineError(f"child checklist {from_child} not found")
        cons = json.loads(child_path.read_text(encoding="utf-8")).get("consolidation")
        if not cons:
            raise EngineError(f"child {from_child} has no consolidation yet")
        attach(cl, iid, "review-result", cons)
    posts = t.get("postconditions", [])
    if not posts:
        raise EngineError(f"{iid}: a gated gate needs >=1 postcondition")
    unmet = [c["id"] for c in posts if not _check_condition(c, t)]
    if unmet:
        raise EngineError(f"{iid}: postconditions unmet {unmet}")
    t["status"] = "complete"
    waived = [c["id"] for c in posts if c.get("waived")]
    if waived:
        return f"{iid} -> complete (WAIVED postconditions {waived})"
    return f"{iid} -> complete"


def record(cl: dict, iid: str, result: str, finding: str | None) -> str:
    if cl["type"] != SURVEY:
        raise EngineError("record is for survey checklists; use advance")
    if result not in ("pass", "fail"):
        raise EngineError("result must be pass or fail")
    t = task(cl, iid)
    t["result"] = result
    t["finding"] = finding
    t["status"] = "complete"
    return f"{iid} recorded {result}" + (f": {finding}" if finding else "")


def consolidate(cl: dict, verdict: str | None, summary: str | None, override_reason: str | None) -> str:
    if cl["type"] != SURVEY:
        raise EngineError("consolidate is for survey checklists")
    open_items = [i for i in cl["items"] if cl["tasks"][i]["status"] not in TERMINAL]
    if open_items:
        raise EngineError(f"cannot consolidate; unvisited items {open_items}")
    fails = [i for i in cl["items"] if cl["tasks"][i].get("result") == "fail"]
    if verdict == "APPROVE" and fails and not override_reason:
        raise EngineError(f"cannot APPROVE with failing items {fails}; supply --override-reason")
    cons: dict = {
        "verdict": verdict,
        "findings": [
            f"{i}: {cl['tasks'][i].get('finding')}" for i in fails if cl["tasks"][i].get("finding")
        ],
    }
    if summary:
        cons["summary"] = summary
    if override_reason:
        cons["override_reason"] = override_reason
    cl["consolidation"] = cons
    return f"consolidated: verdict={verdict} findings={len(cons['findings'])}"


def skip(cl: dict, iid: str, reason: str) -> str:
    t = task(cl, iid)
    t["status"] = "skipped"
    t.setdefault("status_detail", {})["reason"] = reason
    return f"{iid} -> skipped because {reason}"


def block(cl: dict, iid: str, blocker: str, authority: str, next_action: str) -> str:
    t = task(cl, iid)
    detail = {"blocker": blocker, "authority_needed": authority, "next_action": next_action}
    t["status"] = "blocked"
    t["status_detail"] = detail
    cl.setdefault("blockers", []).append({"item": iid, **detail})
    return f"{iid} -> blocked (bubbled to parent)"


def reopen(cl: dict, iid: str, reason: str, cap: int | None = None) -> str:
    t = task(cl, iid)
    if cl["type"] != GATED:
        raise EngineError("reopen applies to gated checklists")
    if t["status"] != "complete":
        raise EngineError(f"can only reopen a complete gate; {iid} is {t['status']!r}")
    if cap is None:
        cap = rework_cap(cl.get("config", {}))
    if t.get("rework_count", 0) + 1 > cap:
        detail = {
            "blocker": f"rework cap {cap} exceeded: {reason}",
            "authority_needed": "parent agent / human",
            "next_action": "escalate; do not re-dispatch",
        }
        t["status"] = "blocked"
        t["status_detail"] = detail
        cl.setdefault("blockers", []).append({"item": iid, **detail})
        return f"ESCALATED {iid}: rework cap {cap} reached; blocked and bubbled to parent (not reopened)"
    t["rework_count"] = t.get("rework_count", 0) + 1
    t["status"] = "in-progress"
    t.setdefault("status_detail", {})["reopen_reason"] = reason
    for c in t.get("postconditions", []):
        c["satisfied"] = False
        c.pop("satisfied_by", None)
        c.pop("waived", None)  # rework re-evaluates: a prior waiver does not carry over
    return f"{iid} reopened (rework {t['rework_count']}/{cap})"


def append(cl: dict, iid: str, title: str, imperative: str) -> str:
    if cl["type"] != SURVEY:
        raise EngineError("append only on survey checklists")
    if iid in cl.get("tasks", {}):
        raise EngineError(f"item {iid!r} already exists")
    cl["tasks"][iid] = {
        "id": iid,
        "title": title,
        "imperative": imperative,
        "preconditions": [],
        "postconditions": [],
        "constraints": [],
        "directives": None,
        "child_checklist": None,
        "status": "pending",
        "status_detail": {},
        "result": None,
        "finding": None,
        "evidence": [],
        "rework_count": 0,
    }
    cl["items"].append(iid)
    return f"appended {iid}"


def attest(cl: dict, iid: str, cond_id: str, which: str, note: str | None) -> str:
    t = task(cl, iid)
    for c in t.get(which, []):
        if c["id"] == cond_id:
            if c.get("check") is not None:
                raise EngineError(f"{cond_id} is engine-checked; cannot attest")
            c["satisfied"] = True
            c["satisfied_by"] = note or "attested"
            return f"attested {iid}.{cond_id}"
    raise EngineError(f"{which} {cond_id!r} not found on {iid}")


def waive(
    cl: dict,
    iid: str,
    cond_id: str,
    which: str,
    authority: str,
    reason: str | None,
    forced: bool = False,
) -> str:
    """Human override: explicitly satisfy a condition by waiver, auditable.

    Refused unless the condition's `override_policy.allowed` is true — unless an
    explicit high-friction `--force` is given (force still demands authority +
    reason and is recorded as a forced override). The engine does not judge
    whether a waiver is wise; it records authority and refuses accidental use."""
    t = task(cl, iid)
    for c in t.get(which, []):
        if c["id"] != cond_id:
            continue
        policy = c.get("override_policy") or {}
        allowed = bool(policy.get("allowed"))
        if not allowed and not forced:
            raise EngineError(
                f"{iid}.{cond_id} is not waivable (no override policy); pass --force to override deliberately"
            )
        if not (authority or "").strip():
            raise EngineError("waive requires a non-empty --authority")
        reason = (reason or "").strip() or None
        if (policy.get("reason_required") or forced) and not reason:
            raise EngineError("waive requires a non-empty --reason")
        eid = _new_evidence_id(t)
        t.setdefault("evidence", []).append(
            {
                "id": eid,
                "type": "waiver",
                "payload": {"cond": cond_id, "authority": authority, "reason": reason, "forced": forced},
                "produced_by": "human",
                "ts": "",
            }
        )
        c["satisfied"] = True
        c["satisfied_by"] = eid
        c["waived"] = {"authority": authority, "reason": reason, "evidence": eid, "forced": forced}
        tag = " (FORCED)" if forced else ""
        return f"waived {iid}.{cond_id}{tag} by {authority} -> {eid}"
    raise EngineError(f"{which} {cond_id!r} not found on {iid}")


def attach(cl: dict, iid: str, etype: str, payload: dict) -> str:
    t = task(cl, iid)
    eid = _new_evidence_id(t)
    t.setdefault("evidence", []).append(
        {"id": eid, "type": etype, "payload": payload, "produced_by": "engine", "ts": ""}
    )
    return f"attached {eid} ({etype}) to {iid}"


def flag_candidate(cl: dict, frm: str, statement: str) -> str:
    cands = cl.setdefault("triage_candidates", [])
    cid = f"tc{len(cands) + 1}"
    cands.append({"id": cid, "from": frm, "statement": statement})
    return f"flagged {cid}"


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--file", required=True, help="checklist JSON file")
    p.add_argument("--dry-run", action="store_true", help="do not write changes back")
    sub = p.add_subparsers(dest="verb", required=True)

    sub.add_parser("current")
    s = sub.add_parser("start")
    s.add_argument("id")
    s = sub.add_parser("advance")
    s.add_argument("id")
    s.add_argument("--from-child", dest="from_child", help="child checklist file; attach its consolidation as review-result first")
    s = sub.add_parser("record")
    s.add_argument("id")
    s.add_argument("--result", required=True, choices=["pass", "fail"])
    s.add_argument("--finding")
    s = sub.add_parser("consolidate")
    s.add_argument("--verdict")
    s.add_argument("--summary")
    s.add_argument("--override-reason")
    s = sub.add_parser("skip")
    s.add_argument("id")
    s.add_argument("--reason", required=True)
    s = sub.add_parser("block")
    s.add_argument("id")
    s.add_argument("--blocker", required=True)
    s.add_argument("--authority", default="parent agent")
    s.add_argument("--next", dest="next_action", default="")
    s = sub.add_parser("reopen")
    s.add_argument("id")
    s.add_argument("--reason", required=True)
    s = sub.add_parser("append")
    s.add_argument("id")
    s.add_argument("--title", required=True)
    s.add_argument("--imperative", required=True)
    s = sub.add_parser("attest")
    s.add_argument("id")
    s.add_argument("--cond", required=True)
    s.add_argument("--which", choices=["preconditions", "postconditions"], default="preconditions")
    s.add_argument("--note")
    s = sub.add_parser("waive")
    s.add_argument("id")
    s.add_argument("--cond", required=True)
    s.add_argument("--which", choices=["preconditions", "postconditions"], default="postconditions")
    s.add_argument("--authority", required=True, help="who is accepting the risk (e.g. human)")
    s.add_argument("--reason", help="why the check is being waived")
    s.add_argument("--force", action="store_true", help="waive even without an override policy (high-friction; recorded as forced)")
    s = sub.add_parser("attach")
    s.add_argument("id")
    s.add_argument("--type", required=True)
    s.add_argument("--payload", help="JSON object (or use the quote-safe --field / --payload-file)")
    s.add_argument("--payload-file", dest="payload_file", help="path to a JSON file holding the payload")
    s.add_argument("--field", action="append", default=[], metavar="K=V", help="repeatable key=value; avoids passing JSON through the shell")
    s = sub.add_parser("flag-candidate")
    s.add_argument("--from", dest="frm", required=True)
    s.add_argument("--statement", required=True)
    return p.parse_args(argv)


def build_payload(args: argparse.Namespace) -> dict:
    """Assemble an attach payload without forcing JSON through the shell.
    Priority: --payload-file, then --payload (JSON), then --field K=V pairs."""
    if getattr(args, "payload_file", None):
        return json.loads(Path(args.payload_file).read_text(encoding="utf-8"))
    payload = json.loads(args.payload) if getattr(args, "payload", None) else {}
    for pair in getattr(args, "field", None) or []:
        key, _, value = pair.partition("=")
        payload[key] = value
    if not payload:
        raise EngineError("attach needs one of --payload-file, --payload, or --field K=V")
    return payload


def dispatch(cl: dict, args: argparse.Namespace, base_dir: Path | None = None) -> str:
    v = args.verb
    if v == "current":
        return current(cl)
    if v == "start":
        return start(cl, args.id)
    if v == "advance":
        return advance(cl, args.id, from_child=getattr(args, "from_child", None), base_dir=base_dir)
    if v == "record":
        return record(cl, args.id, args.result, args.finding)
    if v == "consolidate":
        return consolidate(cl, args.verdict, args.summary, args.override_reason)
    if v == "skip":
        return skip(cl, args.id, args.reason)
    if v == "block":
        return block(cl, args.id, args.blocker, args.authority, args.next_action)
    if v == "reopen":
        return reopen(cl, args.id, args.reason, cap=rework_cap(load_config(cl, base_dir)))
    if v == "append":
        return append(cl, args.id, args.title, args.imperative)
    if v == "attest":
        return attest(cl, args.id, args.cond, args.which, args.note)
    if v == "waive":
        return waive(cl, args.id, args.cond, args.which, args.authority, args.reason, forced=args.force)
    if v == "attach":
        return attach(cl, args.id, args.type, build_payload(args))
    if v == "flag-candidate":
        return flag_candidate(cl, args.frm, args.statement)
    raise EngineError(f"unknown verb {v!r}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    path = Path(args.file)
    cl = load(path)
    try:
        message = dispatch(cl, args, base_dir=path.parent)
    except EngineError as exc:
        # state may carry legitimate mutations (command results, escalation); persist unless read-only/dry-run
        if not args.dry_run and args.verb != "current":
            save(path, cl)
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    if not args.dry_run and args.verb != "current":
        save(path, cl)
    print(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
"""Gate assertions for the POST arm (#307). Each subcommand is a spine gate's `check`.

EVERY GUARD HERE ENUMERATES WHAT IT LOOPED OVER, and prints it, before it reports a verdict.
That rule is not decoration: a comparison that iterates the wrong set reports clean without
ever touching the interesting items, and this epic committed exactly that defect three times
in one day. A zero-length enumeration is a REFUSAL here, never a pass.

Nothing in this file scores anything. Scoring belongs to the PRE-B instruments, unmodified;
this file only asserts that they ran, over the runs they were supposed to run over, and that
the arm can prove which corpus it measured.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREB = HERE.parent / "preb"
ISSUES = [690, 688, 698, 716, 704]
PIN = "3541d2929b19de37107ae13e56776b7162d07255"


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}")


def _load(path: Path):
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return None


def check_captures() -> int:
    """Five captures exist, each pinned, each with a verified treatment."""
    runs = HERE / "runs"
    dirs = sorted(p for p in runs.glob("run-*") if p.is_dir()) if runs.is_dir() else []
    print(f"enumerated {len(dirs)} run dir(s) under {runs}: "
          f"{', '.join(p.name for p in dirs) or '(none)'}")
    if len(dirs) != len(ISSUES):
        _fail(f"expected {len(ISSUES)} run dirs, found {len(dirs)} — an arm short of its "
              "task set is not the arm")
        return 1

    ok = True
    seen_issues: list[int] = []
    launch_digests: dict[str, str] = {}
    for d in dirs:
        meta = _load(d / "meta.json")
        treat = _load(d / "treatment.json")
        order = _load(d / "ordering.json")
        if meta is None:
            _fail(f"{d.name}: no meta.json"); ok = False; continue
        if treat is None:
            _fail(f"{d.name}: no treatment.json — the capture never reached verification");
            ok = False; continue
        if order is None:
            _fail(f"{d.name}: no ordering.json — the frozen extractor never ran"); ok = False; continue

        verdict = treat.get("verdict")
        suppressed = len(treat.get("map_credit_suppressed_by_corpus_rule") or [])
        print(f"  {d.name}: issue={meta.get('issue')} arm={meta.get('arm')} "
              f"pin_ok={meta.get('pin') == PIN} "
              f"exit={meta.get('exit_code')} status={meta.get('status')} "
              f"verdict={verdict} calls={treat.get('tool_call_count')} "
              f"complete={treat.get('transcript_complete')} "
              f"answer_chars={treat.get('final_answer_chars')} "
              f"write_clean={(treat.get('write_audit') or {}).get('clean')} "
              f"forbidden={len(treat.get('forbidden_operations') or [])} "
              f"map_credit_suppressed={suppressed}")

        if isinstance(meta.get("issue"), int):
            seen_issues.append(meta["issue"])
        if meta.get("arm") != "POST":
            _fail(f"{d.name}: meta.arm is {meta.get('arm')!r}, not 'POST'"); ok = False
        if meta.get("pin") != PIN:
            _fail(f"{d.name}: pin is {meta.get('pin')!r}, not the frozen pin"); ok = False
        if verdict != "TREATMENT-VERIFIED":
            _fail(f"{d.name}: {verdict} — a run without a verified Commander load is a "
                  "FAILED CAPTURE, not a data point"); ok = False
        # A timed-out run that happens to end on a newline reads as complete, keeps its
        # TREATMENT-VERIFIED badge, and contributes a first_src_read_index drawn from a
        # TRUNCATED sample. Status and exit code are the only things that catch it.
        if meta.get("status") != "finished":
            _fail(f"{d.name}: status is {meta.get('status')!r}, not 'finished' — a stalled "
                  "or timed-out run is a FAILED CAPTURE, reported, never retried around")
            ok = False
        if meta.get("exit_code") != 0:
            _fail(f"{d.name}: exit_code {meta.get('exit_code')!r}"); ok = False
        if not treat.get("transcript_complete"):
            _fail(f"{d.name}: transcript truncated"); ok = False
        if not treat.get("final_answer_chars"):
            _fail(f"{d.name}: empty final answer — the subject never returned a plan"); ok = False
        if treat.get("forbidden_operations"):
            _fail(f"{d.name}: forbidden operations present"); ok = False
        if not (treat.get("write_audit") or {}).get("clean"):
            _fail(f"{d.name}: write audit not clean — see treatment.json write_audit"); ok = False

        # THE BRIEF IS THE ARM'S MOST LOAD-BEARING SHARED INPUT. `fetch_issue` reads a
        # frozen snapshot rather than live GitHub, so identity holds BY CONSTRUCTION — but
        # a construction argument is not evidence, and an edited snapshot or a drifted
        # substitution would be invisible. Byte-compare against PRE-B's archived brief.
        post_brief = d / "brief.md"
        preb_brief = PREB / "runs" / d.name / "brief.md"
        if not preb_brief.is_file():
            _fail(f"{d.name}: no PRE-B brief at {preb_brief} to compare against"); ok = False
        elif not post_brief.is_file():
            _fail(f"{d.name}: no brief.md"); ok = False
        else:
            a = post_brief.read_bytes()
            b = preb_brief.read_bytes()
            print(f"    brief bytes: POST={len(a)} PRE-B={len(b)} identical={a == b}")
            if a != b:
                _fail(f"{d.name}: brief differs from PRE-B's byte-for-byte — that is a "
                      "SECOND VARIABLE and it looks exactly like a treatment effect")
                ok = False

        # Per-run corpus witness: the treatment lives on a mutable global.
        fp = _load(d / "corpus-at-launch.json")
        if fp is None:
            _fail(f"{d.name}: no corpus-at-launch.json — cannot prove which corpus THIS run "
                  "loaded, only which one the arm started with")
            ok = False
        else:
            launch_digests[d.name] = fp.get("deep_tree_sha256") or ""

    print(f"  issue set seen: {sorted(seen_issues)} — expected {sorted(ISSUES)}")
    if sorted(seen_issues) != sorted(ISSUES):
        _fail("the captured issue set is not the frozen task set — POST must be the SAME "
              "five issues as PRE-B or there is nothing to pair")
        ok = False

    print(f"  per-run corpus deep digests: {len(launch_digests)} enumerated, "
          f"{len(set(launch_digests.values()))} distinct")
    if launch_digests and len(set(launch_digests.values())) != 1:
        _fail(f"the corpus CHANGED between runs: {launch_digests} — the five runs are not "
              "poolable and this must be reported, not smoothed")
        ok = False
    return 0 if ok else 1


def check_scores() -> int:
    """Both arms scored, by the same code, and the negative control still holds."""
    required = {
        "POST discriminated": HERE / "post-discriminated.json",
        "PRE-B discriminated": PREB / "preB-discriminated.json",
        "POST map_orient audit": HERE / "post-map-orient-audit.json",
        "PRE-B map_orient audit (negative control)": HERE / "preB-map-orient-audit.json",
    }
    print(f"enumerated {len(required)} required scoring artifact(s)")
    ok = True
    for label, path in required.items():
        data = _load(path)
        present = data is not None
        print(f"  {label}: {'present' if present else 'MISSING'} "
              f"({len(data) if isinstance(data, list) else '-'} rows) {path.name}")
        if not present:
            _fail(f"{label} missing at {path}"); ok = False
    if not ok:
        return 1

    preb_audit = _load(HERE / "preB-map-orient-audit.json") or []
    total = sum(r.get("map_orient_invocation_count", 0) for r in preb_audit)
    print(f"  negative control: {total} map_orient invocation(s) across "
          f"{len(preb_audit)} pre-#304 run(s) — expected 0")
    if not preb_audit:
        _fail("negative control enumerated ZERO runs — it proves nothing"); ok = False
    elif total:
        _fail(f"negative control found {total} invocation(s) in a pre-#304 arm — the audit "
              "is matching noise and the POST column cannot be trusted"); ok = False

    post = _load(HERE / "post-discriminated.json") or []
    scored = [r for r in post if r.get("status") == "ok"]
    print(f"  POST discriminated: {len(scored)} of {len(post)} rows scored ok")
    if len(scored) != len(ISSUES):
        _fail(f"expected {len(ISSUES)} scored POST rows, got {len(scored)}"); ok = False
    return 0 if ok else 1


def check_pairing() -> int:
    """The arm can PROVE which corpus it measured, and the packet exists."""
    before = _load(HERE / "corpus-fingerprint-BEFORE.json")
    after = _load(HERE / "corpus-fingerprint-AFTER.json")
    preb_before = _load(PREB / "corpus-fingerprint-BEFORE.json")
    names = ["POST BEFORE", "POST AFTER", "PRE-B BEFORE"]
    print(f"enumerated {len(names)} fingerprint(s): {', '.join(names)}")
    ok = True
    for label, fp in zip(names, (before, after, preb_before)):
        if fp is None:
            _fail(f"{label} fingerprint missing"); ok = False
            continue
        print(f"  {label}: shallow={fp.get('skillmd_concat_sha256','')[:16]} "
              f"deep={(fp.get('deep_tree_sha256') or '')[:16]} "
              f"skills={fp.get('constellation_skill_count')} "
              f"source_commit={(fp.get('corpus_marker') or {}).get('source_commit','?')[:8]}")
    if not ok:
        return 1

    if before.get("skillmd_concat_sha256") != after.get("skillmd_concat_sha256"):
        _fail("the corpus CHANGED across the POST window — the five runs are not poolable "
              "and this must be reported, not smoothed"); ok = False
    else:
        print("  corpus stable across the POST window (shallow digest identical)")

    if before.get("skillmd_concat_sha256") == preb_before.get("skillmd_concat_sha256"):
        _fail("POST and PRE-B measured the SAME corpus — there is no treatment and the arm "
              "says nothing about #304"); ok = False
    else:
        print("  POST corpus differs from PRE-B's — the treatment variable actually moved")

    packet = HERE / "POST_RECORD.md"
    print(f"  paired record: {'present' if packet.is_file() else 'MISSING'} {packet.name}")
    if not packet.is_file():
        _fail(f"no paired evidence record at {packet}"); ok = False
    return 0 if ok else 1


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("what", choices=["captures", "scores", "pairing"])
    args = p.parse_args()
    rc = {"captures": check_captures, "scores": check_scores, "pairing": check_pairing}[args.what]()
    print("PASS" if rc == 0 else "REFUSED")
    return rc


if __name__ == "__main__":
    sys.exit(main())

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


# Read-only git subcommands that the reused verifier's `\bgit\s+merge\b` pattern catches by
# accident: `merge-base` is `merge` followed by a word boundary. Listed explicitly rather
# than loosened into a regex, so adding one is a visible decision.
READ_ONLY_GIT = ("git merge-base",)


def adjudicate_forbidden(run_dir: Path, treat: dict) -> dict:
    """Classify `verify_treatment.py`'s forbidden-operation hits WITHOUT touching it.

    The reused verifier searches its FORBIDDEN patterns against `json.dumps(input)` — the
    WHOLE tool input, including the `content` of a `Write`. That produces two false-positive
    classes, both observed in this arm and neither present in PRE-B:

      1. `git merge-base --is-ancestor ...` matches `\\bgit\\s+merge\\b`. Read-only.
      2. A `Write` whose FILE CONTENT mentions `git commit` (e.g. a gate plan) is recorded as
         a forbidden operation. A `Write` cannot execute git.

    The verifier is NOT modified: it is a reused scorer and the PRE-B/POST pairing depends on
    both arms being scored by identical code. So the hits are adjudicated HERE, additively,
    by the same code over both arms — and a hit that is neither class stays REAL and fails
    the gate. The point is to avoid a false stop condition, never to explain one away.
    """
    real, benign = [], []
    for hit in treat.get("forbidden_operations") or []:
        blob = hit.get("target") or ""
        tool = hit.get("tool")
        if tool not in ("Bash", "PowerShell"):
            # Not an executor: whatever matched is text, not an action.
            benign.append({**hit, "why": f"{tool} cannot execute a command; the pattern "
                                         "matched file content, not an executed operation"})
            continue
        stripped = blob
        for phrase in READ_ONLY_GIT:
            stripped = stripped.replace(phrase, "")
        # Re-test the ORIGINAL patterns against the text with read-only forms removed.
        import re as _re
        pats = (r"\bgit\s+push\b", r"\bgh\s+pr\s+create\b",
                r"\bgh\s+issue\s+(comment|create|edit|close)\b",
                r"\bgit\s+commit\b", r"\bgit\s+merge\b")
        if any(_re.search(p, stripped) for p in pats):
            real.append(hit)
        else:
            benign.append({**hit, "why": "only read-only git subcommands matched "
                                         f"({', '.join(READ_ONLY_GIT)})"})
    return {"real": real, "benign": benign}


def transcript_integrity(run_dir: Path) -> dict:
    """One subject produces exactly ONE system/init, ONE result, ONE session_id.

    EARNED (#396). The first POST attempt was launched twice and two drivers wrote the same
    run directories. The doubled transcripts reported `exit_code: 0` with plausible elapsed
    times, and `verify_treatment.py`'s truncation check passed — two interleaved writers
    still leave a newline-terminated file. Nothing the arm was already checking could see it.
    Counting these three quantities is what exposed it, so it is a check now and not a story.
    """
    stream = run_dir / "stream.ndjson"
    if not stream.is_file():
        return {"ok": False, "reason": "no transcript"}
    init = results = malformed = 0
    sessions: set[str] = set()
    raw = stream.read_text(encoding="utf-8", errors="replace")
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            malformed += 1
            continue
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            init += 1
        if ev.get("type") == "result":
            results += 1
        if ev.get("session_id"):
            sessions.add(ev["session_id"])
    return {
        "ok": init == 1 and results == 1 and len(sessions) == 1 and malformed == 0,
        "system_init_events": init,
        "result_events": results,
        "distinct_session_ids": len(sessions),
        "malformed_json_lines": malformed,
        "newline_terminated": raw.endswith("\n"),
    }


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
        ti = transcript_integrity(d)
        print(f"    transcript: init={ti.get('system_init_events')} "
              f"results={ti.get('result_events')} "
              f"sessions={ti.get('distinct_session_ids')} "
              f"malformed={ti.get('malformed_json_lines')} ok={ti['ok']}")
        if not ti["ok"]:
            _fail(f"{d.name}: transcript integrity FAILED ({ti}) — more than one writer, or "
                  "a partial write. A capture two processes wrote is not a capture (#396)")
            ok = False

        adj = adjudicate_forbidden(d, treat)
        if treat.get("forbidden_operations"):
            print(f"    forbidden hits: {len(treat['forbidden_operations'])} raw -> "
                  f"{len(adj['real'])} REAL, {len(adj['benign'])} verifier false positives")
            for b in adj["benign"]:
                print(f"      benign idx={b['index']} {b['tool']}: {b['why']}")
        if adj["real"]:
            for r in adj["real"]:
                _fail(f"{d.name}: REAL forbidden operation at index {r['index']} "
                      f"({r['tool']}): {r['target'][:160]}")
            ok = False
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
            # LINE ENDINGS ARE NORMALIZED, and the reason is recorded because it looks like
            # a loosened check and is not. PRE-B's brief.md is COMMITTED, so the working-tree
            # copy is whatever git checked out — CRLF under this repo's settings. POST's is
            # written fresh by `capture_preb.py` with newline="\n". Comparing raw bytes
            # therefore reports a difference of exactly the line count (21-29 CR bytes here)
            # on every run, while the CONTENT is identical. The CR counts are printed rather
            # than hidden, so a real content change cannot hide behind this normalization.
            na, nb = a.replace(b"\r\n", b"\n"), b.replace(b"\r\n", b"\n")
            print(f"    brief: POST={len(a)}B (CR={a.count(bytes([13]))}) "
                  f"PRE-B={len(b)}B (CR={b.count(bytes([13]))}) "
                  f"content-identical={na == nb}")
            if na != nb:
                _fail(f"{d.name}: brief CONTENT differs from PRE-B's — that is a SECOND "
                      "VARIABLE and it looks exactly like a treatment effect")
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
    post_audit = _load(HERE / "post-map-orient-audit.json") or []
    total = sum(r.get("map_orient_invocation_count", 0) for r in preb_audit)
    print(f"  negative control: {total} map_orient invocation(s) across "
          f"{len(preb_audit)} pre-#304 run(s) — expected 0")
    # A control of size one passes a mere `if not preb_audit` guard while proving nothing.
    if len(preb_audit) != len(ISSUES):
        _fail(f"negative control covers {len(preb_audit)} run(s), not {len(ISSUES)} — a "
              "control smaller than the arm does not control it"); ok = False
    elif total:
        _fail(f"negative control found {total} invocation(s) in a pre-#304 arm — the audit "
              "is matching noise and the POST column cannot be trusted"); ok = False
    if len(post_audit) != len(ISSUES):
        _fail(f"POST audit covers {len(post_audit)} run(s), not {len(ISSUES)}"); ok = False

    # BOTH scoring files name their rows `run-690` … `run-704`, because both arms name their
    # DIRECTORIES that way. Without an arm label, `cp preb/preB-discriminated.json
    # post/post-discriminated.json` passes every other check in this function: the gate that
    # exists to prove both arms were scored could not detect that one arm was scored twice.
    for label, rows, want in (("POST audit", post_audit, "POST"),
                              ("PRE-B audit", preb_audit, "PRE-B")):
        arms = sorted({r.get("arm") for r in rows})
        print(f"  {label} arm labels: {arms} — expected ['{want}']")
        if arms != [want]:
            _fail(f"{label} rows are labelled {arms}, not exactly ['{want}'] — a scoring "
                  "file that cannot name its own arm cannot be paired with anything")
            ok = False

    post = _load(HERE / "post-discriminated.json") or []
    scored = [r for r in post if r.get("status") == "ok"]
    print(f"  POST discriminated: {len(scored)} of {len(post)} rows scored ok")
    if len(scored) != len(ISSUES):
        _fail(f"expected {len(ISSUES)} scored POST rows, got {len(scored)}"); ok = False

    # `discriminate.py` emits no arm label (it is FROZEN and stays that way), so tie its rows
    # to THIS arm's captures by a quantity only those captures can produce.
    print("  cross-checking POST discriminated rows against POST captures:")
    for row in post:
        cap = _load(HERE / "runs" / str(row.get("run")) / "ordering.json")
        if cap is None:
            _fail(f"    {row.get('run')}: no matching POST capture — this row was scored "
                  "over some OTHER arm's runs"); ok = False; continue
        same = cap.get("tool_call_count") == row.get("tool_call_count")
        print(f"    {row.get('run')}: calls row={row.get('tool_call_count')} "
              f"capture={cap.get('tool_call_count')} match={same}")
        if not same:
            _fail(f"    {row.get('run')}: scored row does not match the POST capture"); ok = False

    # The arm's central claim: the scorers are PRE-B's, unmodified.
    digests = _load(HERE / "instrument-digests.json") or {}
    print(f"  instrument digests: {len(digests)} file(s) compared PRE-B-merge vs HEAD")
    if not digests:
        _fail("no instrument-digests.json — 'the scorers are unmodified' is unverified");
        ok = False
    for name, d in sorted(digests.items()):
        identical = d.get("identical")
        note = "" if identical else "  <-- CHANGED (must be declared)"
        print(f"    {name}: {'SAME' if identical else 'CHANGED'}{note}")
    changed = {n for n, d in digests.items() if not d.get("identical")}
    allowed = {"preb/capture_preb.py"}
    if changed - allowed:
        _fail(f"instruments changed since PRE-B beyond the declared label flag: "
              f"{sorted(changed - allowed)}"); ok = False
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

    # DEEP, not shallow. `skillmd_concat_sha256` covers only each skill's SKILL.md and is
    # BLIND to references/, templates/ and scripts/ — which is where the whole contract under
    # test lives: constellation-commander/SKILL.md contains zero occurrences of the word
    # "map", while templates/COMMANDER_SPINE.template.json carries the imperative four times.
    # A shallow comparison therefore reports "stable" through a re-install that rewrites the
    # treatment, and would have reported "identical" had the delta been #304 alone. Filed as
    # #395; asserted here on the deep digest, which was already being computed and printed
    # and simply was not the thing being compared.
    if before.get("deep_tree_sha256") != after.get("deep_tree_sha256"):
        _fail("the corpus CHANGED across the POST window (deep digest) — the five runs are "
              "not poolable and this must be reported, not smoothed"); ok = False
    else:
        print("  corpus stable across the POST window (DEEP digest identical)")

    if before.get("deep_tree_sha256") == preb_before.get("deep_tree_sha256"):
        _fail("POST and PRE-B measured the SAME corpus — there is no treatment and the arm "
              "says nothing about #304"); ok = False
    else:
        print("  POST corpus differs from PRE-B's (DEEP digest) — the treatment moved")

    # DIRECT CONTENT ASSERTION, because everything above is still a digest comparison and
    # `corpus_marker.source_commit` is read verbatim out of ~/.claude/skills/CORPUS.json — a
    # SELF-REPORT WRITTEN BY THE INSTALLER, i.e. exactly the artifact that would lie in a
    # #344-shaped failure. Proving delivery from the installer's own claim is #344 again with
    # extra steps. Look at the installed bytes instead.
    corpus = Path.home() / ".claude" / "skills" / "constellation-commander"
    tool = corpus / "scripts" / "map_orient.py"
    spine = corpus / "templates" / "COMMANDER_SPINE.template.json"
    contract = "before you open any source file"
    print(f"  installed contract, asserted against BYTES not markers (root {corpus}):")
    print(f"    scripts/map_orient.py present: {tool.is_file()}")
    if not tool.is_file():
        _fail("map_orient.py is NOT in the installed corpus — this is the #344 failure and "
              "any null from this arm would be a delivery failure, not a contract failure")
        ok = False
    if not spine.is_file():
        _fail(f"{spine} absent — the contract text lives ONLY here (#393)"); ok = False
    else:
        text = spine.read_text(encoding="utf-8", errors="replace")
        hits = text.lower().count(contract)
        anchored = text.count("map_orient")
        print(f"    spine template: {anchored} map_orient reference(s), "
              f"{hits} occurrence(s) of the anchor phrase {contract!r}")
        if not hits or not anchored:
            _fail("the installed spine template does not carry the #304 anchor — the "
                  "treatment is not installed, whatever the marker says"); ok = False

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

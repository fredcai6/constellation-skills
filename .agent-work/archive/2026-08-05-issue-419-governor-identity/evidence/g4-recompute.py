#!/usr/bin/env python3
"""Independent re-computation of the g4 acceptance run (issue #419).

THE PAIRING. For each agent, the fill recomputed from THAT AGENT'S OWN
`agent-<id>.jsonl` must equal the `fill_fraction` in the `gauge.json` sitting in
the spine directory that the SAME id's binding key points at.

The recomputation is pinned to the gauge's own `observed_at`: the gauge names the
moment it sampled, so the honest comparison looks up the record carrying exactly
that timestamp in the agent's own transcript. (Comparing against the transcript
TAIL would compare two different moments -- the transcript keeps growing after the
last gauge write.) Pinning also makes the anti-crossing test direct: if agent A's
reading had been written into agent B's spine, B's gauge would name a moment that
exists only in A's transcript, and the lookup in B's own transcript finds nothing.

Every parse here is written from scratch. The hook under test is never imported.

Exit 0 only if the pairing holds and no named falsifier fires.
"""
import json
import re
import sys
from pathlib import Path

ACC = Path(__file__).resolve().parent
SB = ACC / "sb-treatment"
PROJECTS = Path("C:/Users/fredc/.claude/projects")
WINDOW = 1_000_000  # claude-sonnet-5
HARD, SOFT, BUDGET_MS = 0.15, 0.08, 100.0

UUID_RE = re.compile(r"\A[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z")
HEX_RE = re.compile(r"\A[0-9a-f]{17}\Z")

failures, notes = [], []


def check(ok, label, detail=""):
    print("%-4s | %s%s" % ("PASS" if ok else "FAIL", label, ("  -- " + detail) if detail else ""))
    if not ok:
        failures.append(label)
    return ok


def slug_for(path: Path) -> str:
    return str(path).replace("\\", "/").replace(":", "-").replace("/", "-")


def lines_of(p: Path):
    for raw in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            d = json.loads(raw)
        except Exception:
            continue
        if isinstance(d, dict):
            yield d


def usage_total(d):
    u = (d.get("message") or {}).get("usage")
    if not isinstance(u, dict):
        return None
    total = 0
    for f in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"):
        v = u.get(f)
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            return None
        total += v
    return total


def recompute_at(transcript: Path, agent_id, observed_at):
    """The record in THIS agent's own transcript carrying exactly `observed_at`.
    Returns (fill, model, tokens) or None."""
    for d in lines_of(transcript):
        if d.get("type") != "assistant" or d.get("timestamp") != observed_at:
            continue
        if agent_id is None:
            if d.get("isSidechain"):
                continue
        elif not d.get("isSidechain") or d.get("agentId") != agent_id:
            continue
        total = usage_total(d)
        if total is None:
            continue
        return total / WINDOW, (d.get("message") or {}).get("model"), total
    return None


def tail_fill(transcript: Path, agent_id):
    best = None
    for d in lines_of(transcript):
        if d.get("type") != "assistant":
            continue
        if agent_id is None:
            if d.get("isSidechain"):
                continue
        elif not d.get("isSidechain") or d.get("agentId") != agent_id:
            continue
        total = usage_total(d)
        model = (d.get("message") or {}).get("model")
        if total is None or model not in ("claude-sonnet-5", "claude-opus-5"):
            continue
        best = (total / WINDOW, model, d.get("timestamp"))
    return best


def first_corpus_read(transcript: Path, agent_id):
    for d in lines_of(transcript):
        if d.get("type") != "assistant":
            continue
        if agent_id is not None and d.get("agentId") != agent_id:
            continue
        for block in (d.get("message") or {}).get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_use" \
                    and "chunk-" in json.dumps(block.get("input") or {}):
                return d.get("timestamp")
    return None


def role_of(text: str) -> str:
    for marker, name in (("DELTA-START", "DELTA"), ("CHARLIE-DONE", "CHARLIE"),
                         ("wk-alpha", "ALPHA"), ("wk-bravo", "BRAVO"), ("wk-echo", "ECHO")):
        if marker in text:
            return name
    return "?"


def main() -> int:
    print("=== issue #419 g4 acceptance: independent re-computation (TREATMENT arm) ===\n")

    binding_file = SB / ".agent-work" / ".spine-rail-binding.json"
    binding = json.loads(binding_file.read_text(encoding="utf-8"))
    print("binding store: %s" % binding_file)
    for k, v in binding.items():
        print("  key %-62s -> %s" % (k, [Path(p).parent.name for p in v]))
    print()

    proj = PROJECTS / slug_for(SB)
    sessions = sorted((p for p in proj.iterdir() if p.is_dir() and UUID_RE.match(p.name)),
                      key=lambda p: p.stat().st_mtime)
    bare = [k for k in binding if "#" not in k]
    comp = sorted(k for k in binding if "#" in k)
    check(len(bare) == 1, "exactly one bare key (the parent)", str(bare))
    session = proj / bare[0]
    check(session.is_dir(), "the bare binding key IS this run's harness session dir", session.name)
    subdir = session / "subagents"
    agents = sorted(subdir.glob("agent-*.jsonl"))
    print("session %s -> %d agent transcripts\n" % (session.name, len(agents)))

    roles, texts = {}, {}
    for t in agents:
        aid = t.stem[len("agent-"):]
        texts[aid] = t.read_text(encoding="utf-8", errors="ignore")
        roles[aid] = role_of(texts[aid])
        print("  agent %-20s role=%-8s lines=%d" % (aid, roles[aid], len(texts[aid].splitlines())))
    print()

    check(UUID_RE.match(bare[0]) is not None, "the parent's key is a bare session uuid", bare[0])
    check(all(Path(p).parent.name == "wk-parent" for p in binding[bare[0]]),
          "the parent holds exactly its one bare-key entry, its own spine",
          str([Path(p).parent.name for p in binding[bare[0]]]))
    for k in comp:
        sid, aid = k.split("#", 1)
        check(UUID_RE.match(sid) is not None and HEX_RE.match(aid) is not None,
              "composite key is <uuid>#<hex>, not bare: %s" % k)
        check(sid == bare[0], "composite key carries this session's uuid: %s" % k)

    print("\n--- THE PAIRING: each agent's OWN transcript vs the gauge in the spine its key points at ---")
    paired, fills = 0, {}
    for k in comp:
        sid, aid = k.split("#", 1)
        spines = list(binding[k])
        if not check(len(spines) == 1, "key %s binds exactly one spine" % k, str(spines)):
            continue
        spine_dir = Path(spines[0]).parent
        gauge = json.loads((spine_dir / "gauge.json").read_text(encoding="utf-8"))
        transcript = subdir / ("agent-%s.jsonl" % aid)
        if not check(transcript.exists(), "own transcript exists for %s" % aid, str(transcript)):
            continue
        rec = recompute_at(transcript, aid, gauge["observed_at"])
        print("\n  agent %s (%s)  ->  binding key points at spine dir %s"
              % (aid, roles.get(aid, "?"), spine_dir.name))
        if rec is None:
            check(False, "PAIRED: %s's own reading is the gauge in %s" % (aid, spine_dir.name),
                  "no record at observed_at %s in its own transcript" % gauge["observed_at"])
            continue
        fill, model, tokens = rec
        print("    recomputed from agent-%s.jsonl @ %s : fill=%.6f  model=%s  tokens=%d"
              % (aid, gauge["observed_at"], fill, model, tokens))
        print("    gauge.json in %-9s                                : fill=%.6f  model=%s"
              % (spine_dir.name, gauge["fill_fraction"], gauge["model"]))
        ok = abs(fill - gauge["fill_fraction"]) < 1e-9 and model == gauge["model"]
        check(ok, "PAIRED: %s's own reading IS the gauge in %s" % (aid, spine_dir.name),
              "recomputed %.6f vs gauge %.6f" % (fill, gauge["fill_fraction"]))
        paired += 1 if ok else 0
        fills[aid] = gauge["fill_fraction"]

        # anti-crossing: this gauge's sampled moment must exist in NO other agent's transcript
        others = [o for o in roles if o != aid
                  and recompute_at(subdir / ("agent-%s.jsonl" % o), o, gauge["observed_at"])]
        check(not others, "NOT CROSSED: %s's sampled moment appears in no other agent's transcript"
              % spine_dir.name, str(others))

        ms = gauge.get("identity_resolution_ms")
        check(isinstance(ms, (int, float)) and 0 <= ms < BUDGET_MS,
              "identity_resolution_ms inside the 100ms budget for %s" % aid, "%.5f ms" % ms)
        first = first_corpus_read(transcript, aid)
        check(bool(first) and gauge["observed_at"] >= first,
              "observed_at does not predate %s's first chunk read" % aid,
              "first read %s vs observed_at %s" % (first, gauge["observed_at"]))
        t = tail_fill(transcript, aid)
        if t:
            print("    (transcript tail, for context: fill=%.6f at %s)" % (t[0], t[2]))

    print()
    check(paired == 2, "THE PAIRING HOLDS %d of 2" % paired)
    check(len(set(round(v, 6) for v in fills.values())) == len(fills) == 2,
          "the two agents' fills DIFFER", str(sorted(fills.items())))
    check(any(v >= HARD for v in fills.values()),
          "at least one agent reached the HARD band (>= %.2f)" % HARD,
          "max fill %.6f" % max(fills.values()))

    print("\n--- the parent's own reading ---")
    pg = SB / ".agent-work" / "wk-parent" / "gauge.json"
    check(pg.exists(), "the parent got its OWN reading (pre-fix it got none at all)")
    prec = json.loads(pg.read_text(encoding="utf-8"))
    print("  wk-parent gauge.json: %s" % json.dumps(prec))
    check("identity_resolution_ms" not in prec,
          "the parent's record is the untouched four fields, byte-shape unchanged")
    prt = proj / ("%s.jsonl" % session.name)
    rec = recompute_at(prt, None, prec["observed_at"])
    if rec:
        print("  recomputed from the parent's own transcript @ %s: fill=%.6f tokens=%d"
              % (prec["observed_at"], rec[0], rec[2]))
        check(abs(rec[0] - prec["fill_fraction"]) < 1e-9,
              "PAIRED: the parent's own reading IS the gauge in wk-parent",
              "recomputed %.6f vs gauge %.6f" % (rec[0], prec["fill_fraction"]))
    else:
        check(False, "the parent's gauge moment resolves in the parent's own transcript")

    print("\n--- the release (wk-echo, a NESTED depth-2 agent) ---")
    echo_ids = [a for a, r in roles.items() if r == "ECHO"]
    delta_ids = [a for a, r in roles.items() if r == "DELTA"]
    check(len(delta_ids) == 1 and len(echo_ids) == 1,
          "the nested dispatch produced its own agent transcript (depth 2)",
          "DELTA=%s ECHO=%s" % (delta_ids, echo_ids))
    eg = SB / ".agent-work" / "wk-echo" / "gauge.json"
    resolved = eg.exists()
    check(resolved, "NESTED DISPATCH RESOLVED: the depth-2 agent got its own per-agent reading")
    if resolved and echo_ids:
        erec = json.loads(eg.read_text(encoding="utf-8"))
        print("  wk-echo gauge.json: %s" % json.dumps(erec))
        et = subdir / ("agent-%s.jsonl" % echo_ids[0])
        r = recompute_at(et, echo_ids[0], erec["observed_at"])
        check(r is not None and abs(r[0] - erec["fill_fraction"]) < 1e-9,
              "PAIRED: the nested agent's own reading IS the gauge in wk-echo",
              ("recomputed %.6f vs gauge %.6f" % (r[0], erec["fill_fraction"])) if r else "no match")
        notes.append("nested depth-2 dispatch RESOLVED (agent %s, spine wk-echo)" % echo_ids[0])
    else:
        notes.append("nested depth-2 dispatch FAILED CLOSED: no reading written for wk-echo")
    echo_keys = [k for k in binding if "#" in k and k.split("#")[-1] in echo_ids]
    check(not echo_keys, "the released agent's composite key is GONE from the store", str(echo_keys))
    check(bare[0] in binding, "the parent's bare key SURVIVED that release")

    print("\n--- the non-claiming subagent ---")
    charlie = [a for a, r in roles.items() if r == "CHARLIE"]
    check(len(charlie) == 1, "the non-claiming subagent ran and made tool calls", str(charlie))
    check(not [k for k in binding if k.split("#")[-1] in charlie],
          "the non-claiming subagent bound NOTHING")
    known = {"wk-parent", "wk-alpha", "wk-bravo", "wk-echo"}
    stray = [str(p) for p in SB.glob(".agent-work/*/gauge*.json") if p.parent.name not in known]
    check(not stray, "the non-claiming subagent wrote NOTHING anywhere", str(stray))
    check(not [a for a, r in roles.items() if r == "DELTA"
               and [k for k in binding if k.split("#")[-1] == a]],
          "the nested dispatcher, which claimed nothing, bound nothing either")

    print("\n--- sidecars ---")
    side = sorted(SB.glob(".agent-work/*/gauge-*.json"))
    for p in side:
        print("  %s: %s" % (p, p.read_text(encoding="utf-8")))
    check(not side, "no skip / uncalibrated sidecar anywhere in the treatment arm",
          str([str(p) for p in side]))

    print("\n--- the trip, read from the spine STATE FILES, not from any agent's report ---")
    for wid in ("wk-alpha", "wk-bravo", "wk-echo", "wk-parent"):
        s = json.loads((SB / ".agent-work" / wid / "spine.json").read_text(encoding="utf-8"))
        print("  %-10s g1=%-12s refusals=%-3s lease=%s"
              % (wid, s["tasks"]["g1"]["status"], s.get("refusals"),
                 (s.get("engine_session") or {}).get("status")))
    a = json.loads((SB / ".agent-work" / "wk-alpha" / "spine.json").read_text(encoding="utf-8"))
    check(a["tasks"]["g1"]["status"] == "in-progress" and a.get("refusals", 0) >= 1,
          "HARD TRIP FIRED: the >= hard agent's advance was REFUSED and its gate did not move",
          "wk-alpha g1=%s refusals=%s" % (a["tasks"]["g1"]["status"], a.get("refusals")))
    b = json.loads((SB / ".agent-work" / "wk-bravo" / "spine.json").read_text(encoding="utf-8"))
    check(b["tasks"]["g1"]["status"] == "complete" and b.get("refusals", 0) == 0,
          "the below-hard agent advanced normally in the SAME arm",
          "wk-bravo g1=%s refusals=%s" % (b["tasks"]["g1"]["status"], b.get("refusals")))

    print()
    for n in notes:
        print("NOTE: %s" % n)
    print("\n%d failure(s): %s" % (len(failures), failures if failures else "none"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

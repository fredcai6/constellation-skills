#!/usr/bin/env python3
"""Control-arm assertions: the SAME script, the SAME sandbox shape, one variable --
the settings file names the MAIN checkout's unmodified hooks instead of the
worktree's. If the control also tripped, the change is not what caused the trip.
"""
import json
import sys
from pathlib import Path

ACC = Path(__file__).resolve().parent
SB = ACC / "sb-control"
failures = []


def check(ok, label, detail=""):
    print("%-4s | %s%s" % ("PASS" if ok else "FAIL", label, ("  -- " + detail) if detail else ""))
    if not ok:
        failures.append(label)
    return ok


def main() -> int:
    print("=== issue #419 g4 acceptance: CONTROL arm (main checkout's unmodified hooks) ===\n")
    bf = SB / ".agent-work" / ".spine-rail-binding.json"
    check(bf.exists(), "the control arm's own binding store was written (hooks did fire)")
    binding = json.loads(bf.read_text(encoding="utf-8")) if bf.exists() else {}
    for k, v in binding.items():
        print("  key %-62s -> %s" % (k, sorted(Path(p).parent.name for p in v)))
    print()

    comp = [k for k in binding if "#" in k]
    check(not comp, "NO composite per-agent key exists in the control arm", str(comp))
    bare = [k for k in binding if "#" not in k]
    check(len(bare) == 1, "every claim piled under ONE bare session key", str(bare))
    if bare:
        n = len(binding[bare[0]])
        check(n > 1, "that one bare key holds MORE THAN ONE spine -> ambiguous by construction",
              "%d spines: %s" % (n, sorted(Path(p).parent.name for p in binding[bare[0]])))

    print()
    # MEASURED, not assumed. The first draft of this file asserted "no reading
    # anywhere" and FAILED, because the control arm does write ONE reading: the
    # parent claims first and is briefly the sole candidate under the bare key.
    # The moment the first subagent claims, that same bare key holds 2+ spines and
    # every later write is refused as ambiguous -- so the parent's reading FREEZES
    # and no dispatched agent ever gets one. That frozen-early reading is exactly
    # the blindness this issue describes; the assertion below states it precisely
    # instead of overclaiming.
    dispatched = ("wk-alpha", "wk-bravo", "wk-echo")
    got = [w for w in dispatched if (SB / ".agent-work" / w / "gauge.json").exists()]
    check(not got, "NO dispatched agent got a reading in the control arm", str(got))
    pg = SB / ".agent-work" / "wk-parent" / "gauge.json"
    if pg.exists():
        rec = json.loads(pg.read_text(encoding="utf-8"))
        claims = sorted((e["claimed_at"], Path(p).parent.name)
                        for v in binding.values() for p, e in v.items())
        print("  claim order under the one bare key:")
        for ts, w in claims:
            print("    %s  %s" % (ts, w))
        print("  the parent's ONLY reading: %s" % json.dumps(rec))
        second = claims[1][0] if len(claims) > 1 else None
        check(second is not None and rec["observed_at"] < second,
              "the parent's one reading was sampled BEFORE the second claim, then froze",
              "sampled %s < second claim %s" % (rec["observed_at"], second))
        skip = SB / ".agent-work" / "wk-parent" / "gauge-skip.json"
        if skip.exists():
            s = json.loads(skip.read_text(encoding="utf-8"))
            check(s["reason"] == "ambiguous-binding" and s["observed_at"] > rec["observed_at"],
                  "and every later write at that same path was refused as ambiguous",
                  "skip %s at %s, candidate_count=%s"
                  % (s["reason"], s["observed_at"], s.get("candidate_count")))
        check(rec["fill_fraction"] < 0.15,
              "the parent's frozen reading never reached any band that could trip",
              "%.6f" % rec["fill_fraction"])

    side = sorted(SB.glob(".agent-work/*/gauge-*.json"))
    print("\nsidecars in the control arm: %d" % len(side))
    for p in side:
        print("  %s: %s" % (p.parent.name + "/" + p.name, p.read_text(encoding="utf-8")))

    print("\n--- spine state files ---")
    for wid in ("wk-alpha", "wk-bravo", "wk-echo", "wk-parent"):
        f = SB / ".agent-work" / wid / "spine.json"
        if not f.exists():
            continue
        s = json.loads(f.read_text(encoding="utf-8"))
        print("  %-10s g1=%-12s refusals=%-3s lease=%s"
              % (wid, s["tasks"]["g1"]["status"], s.get("refusals"),
                 (s.get("engine_session") or {}).get("status")))
    tripped = []
    for wid in ("wk-alpha", "wk-bravo", "wk-echo", "wk-parent"):
        f = SB / ".agent-work" / wid / "spine.json"
        if not f.exists():
            continue
        s = json.loads(f.read_text(encoding="utf-8"))
        if s.get("refusals", 0) > 0:
            tripped.append(wid)
    check(not tripped, "the control arm did NOT trip anywhere", str(tripped))
    a = SB / ".agent-work" / "wk-alpha" / "spine.json"
    if a.exists():
        s = json.loads(a.read_text(encoding="utf-8"))
        check(s["tasks"]["g1"]["status"] == "complete",
              "the heaviest-reading agent ADVANCED NORMALLY in the control arm",
              "wk-alpha g1=%s" % s["tasks"]["g1"]["status"])

    print("\n%d failure(s): %s" % (len(failures), failures if failures else "none"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

"""Reviewer probes -- adversarial checks on the g1 RED. Writes only under g1-review/."""
import importlib.util, shutil, sys, json
from pathlib import Path

HERE = Path(".agent-work/issue-467-trip-semantics/g1-review").resolve()
spec = importlib.util.spec_from_file_location(
    "repro_431", ".agent-work/issue-467-trip-semantics/red-repro/repro_431.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
R.SCRATCH = HERE / "probe-scratch"
if R.SCRATCH.exists(): shutil.rmtree(R.SCRATCH)

print("#"*70)
print("PROBE 1 -- tighter control: identical spine, gauge PRESENT but BELOW hard")
print("  (the repro's own Face A control removes the gauge FILE; this varies only")
print("   the NUMBER, so gauge-presence cannot be the confound.)")
print("#"*70)
sp = R.build_spine("probe-below-hard", [("c1", "reader failure modes enumerated")])
R.drive_to_mid_g2(sp, "probe-below", satisfy_g2_c1=True)
R.plant_gauge(sp, R.BELOW_HARD_FILL)          # 0.02, same file, same location
rc, out = R.engine(sp, "advance", "g2", "--why", R.CURRENT_WHY, "--session-id", "probe-below")
rc, cold = R.engine(sp, "current")
d = R.digest_of(cold)
print(f"PROBE1 advance exit={rc}")
print(f"PROBE1 DIGEST = {d!r}")
print(f"PROBE1 RESULT: digest_is_fresh={d == R.CURRENT_WHY}  digest_is_stale={d == R.PRE_TRIP_WHY}")

print()
print("#"*70)
print("PROBE 2 -- is the deadlock escapable? After the keyed refresh-request is")
print("  attached, does the SAME advance now succeed and write a fresh DIGEST?")
print("#"*70)
sp2 = R.build_spine("probe-escape", [("c1", "reader failure modes enumerated")])
R.drive_to_mid_g2(sp2, "probe-esc", satisfy_g2_c1=True)
R.plant_gauge(sp2, R.HARD_FILL)
rc, refusal = R.engine(sp2, "advance", "g2", "--why", R.CURRENT_WHY,
                       "--session-id", "probe-esc", expect_refusal=True)
wid = R._live_why_id(sp2, "probe-esc")
R.engine(sp2, "attach", "g2", "--type", "refresh-request", "--field", "seam=g2",
         "--field", f"why_ref={wid}", "--session-id", "probe-esc")
rc2, out2 = R.engine(sp2, "current")
print(f"PROBE2 post-attach `current` HARD line: {R.context_hard_line(out2)!r}")
rc3, out3 = R.engine(sp2, "advance", "g2", "--why", R.CURRENT_WHY, "--session-id", "probe-esc")
rc4, cold2 = R.engine(sp2, "current")
d2 = R.digest_of(cold2)
print(f"PROBE2 post-attach advance exit={rc3}")
print(f"PROBE2 DIGEST after that advance = {d2!r}")
print(f"PROBE2 RESULT: hard_band_released_and_advance_succeeded={rc3 == 0}  digest_now_fresh={d2 == R.CURRENT_WHY}")

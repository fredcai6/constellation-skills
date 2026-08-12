"""PROBE 3 -- verify the result's triage claim: the literal `<why-id>` attach is a silent no-op.
PROBE 4 -- is the why-record id reachable from engine OUTPUT alone (before the attach)?"""
import importlib.util, shutil
from pathlib import Path
HERE = Path(".agent-work/issue-467-trip-semantics/g1-review").resolve()
spec = importlib.util.spec_from_file_location(
    "repro_431", ".agent-work/issue-467-trip-semantics/red-repro/repro_431.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
R.SCRATCH = HERE / "probe3-scratch"
if R.SCRATCH.exists(): shutil.rmtree(R.SCRATCH)

sp = R.build_spine("probe-literal", [("c1", "reader failure modes enumerated")])
R.drive_to_mid_g2(sp, "probe-lit", satisfy_g2_c1=True)
R.plant_gauge(sp, R.HARD_FILL)
rc, pre = R.engine(sp, "current")
print("PROBE4 does pre-attach `current` contain a why-record id (w-N)? ->",
      __import__("re").findall(r"\bw-\d+\b", pre))
rc, refusal = R.engine(sp, "advance", "g2", "--why", R.CURRENT_WHY,
                       "--session-id", "probe-lit", expect_refusal=True)
print("PROBE4 does the REFUSAL contain a why-record id (w-N)? ->",
      __import__("re").findall(r"\bw-\d+\b", refusal))
rc2, att = R.engine(sp, "attach", "g2", "--type", "refresh-request", "--field", "seam=g2",
                    "--field", "why_ref=<why-id>", "--session-id", "probe-lit")
print(f"PROBE3 literal-placeholder attach exit={rc2}")
rc3, ref2 = R.engine(sp, "advance", "g2", "--why", R.CURRENT_WHY,
                     "--session-id", "probe-lit", expect_refusal=True)
print(f"PROBE3 advance after literal-placeholder attach exit={rc3}")
print("PROBE3 RESULT: attach_succeeded=%s advance_still_refused=%s (silent no-op = %s)" % (
    rc2 == 0, rc3 != 0, rc2 == 0 and rc3 != 0))

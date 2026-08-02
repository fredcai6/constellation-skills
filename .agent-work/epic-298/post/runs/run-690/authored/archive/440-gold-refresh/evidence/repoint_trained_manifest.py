"""Repoint the assembled trained manifest's module paths at the materialized bundles.

Runbook Step 3b gotcha: gold and fusion slugs have different timestamps, so
materialize_runtime_bundles.py cannot auto-discover the trained manifest; the
repoint is done manually here (relative paths into params/gold/runtime_bundles/<gold_slug>/).
"""
import json

PATH = "reports/evo/fusion_260612_000020_2018thru2024.sampled_runtime_manifest.json"
OLD = "C:\\Programs\\f1Brainz\\outputs\\evo_runs\\gold_module_training_cycle\\modules\\"
NEW = "..\\..\\params\\gold\\runtime_bundles\\gold_cycle_260611_231027_2018thru2024\\modules\\"

with open(PATH, encoding="utf-8") as f:
    m = json.load(f)

count = 0

def fix(o):
    global count
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "manifest_path" and isinstance(v, str) and v.startswith(OLD):
                o[k] = NEW + v[len(OLD):]
                count += 1
            else:
                fix(v)
    elif isinstance(o, list):
        for x in o:
            fix(x)

fix(m)
with open(PATH, "w", encoding="utf-8") as f:
    json.dump(m, f, indent=2)
print("repointed", count, "module paths")

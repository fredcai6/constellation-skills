"""Admiral-authored check: the repo's own self-checking idiom must not be flagged.

Not the crew's to edit. Exits 1 and prints the faults if the lint refuses a check
that demonstrably runs and passes real tests.
"""
import json, sys, tempfile, pathlib
sys.path.insert(0, "scripts")
import validate_spine as v

CMD = ("test $(python -m pytest -q tests/test_validate_spine.py -k Shape --collect-only "
       "2>/dev/null | grep -c '::') -ge 6 && python -m pytest -q tests/test_validate_spine.py -k Shape")

spine = {"work_id": "idiom-probe", "type": "gated", "items": ["g1"], "tasks": {"g1": {
    "id": "g1", "title": "t", "imperative": "i", "preconditions": [],
    "postconditions": [{"id": "c1", "statement": "tests pass",
                        "check": {"kind": "command", "command": CMD}, "satisfied": False}],
    "constraints": [], "directives": None, "child_checklist": None,
    "status": "pending", "status_detail": {}, "evidence": [], "rework_count": 0}}}

p = pathlib.Path(tempfile.mkdtemp()) / "s.json"
p.write_text(json.dumps(spine))
bad = [f for f in v.validate_file(str(p)) if "zero" in f.code]
for f in bad:
    print("FALSE POSITIVE:", f.code, f.message)
sys.exit(1 if bad else 0)

"""Helper: call checklist_engine.py record/consolidate with a finding read
from a file, to avoid shell-quoting a long multi-line finding through Bash.
Usage: python evident_record.py <file> record <item-id> --result pass --session-id <id>
       python evident_record.py <file> consolidate --verdict BLOCK --session-id <id>
"""
import subprocess
import sys

engine = "scripts/checklist_engine.py"
survey_file = sys.argv[1]
verb_args = sys.argv[2:]
finding_path = None
if "--finding-file" in verb_args:
    i = verb_args.index("--finding-file")
    finding_path = verb_args[i + 1]
    del verb_args[i:i + 2]
    with open(finding_path, "r", encoding="utf-8") as f:
        finding_text = f.read()
    verb_args += ["--finding", finding_text]

summary_path = None
if "--summary-file" in verb_args:
    i = verb_args.index("--summary-file")
    summary_path = verb_args[i + 1]
    del verb_args[i:i + 2]
    with open(summary_path, "r", encoding="utf-8") as f:
        summary_text = f.read()
    verb_args += ["--summary", summary_text]

if "--statement-file" in verb_args:
    i = verb_args.index("--statement-file")
    statement_path = verb_args[i + 1]
    del verb_args[i:i + 2]
    with open(statement_path, "r", encoding="utf-8") as f:
        statement_text = f.read()
    verb_args += ["--statement", statement_text]

cmd = [sys.executable, engine, "--file", survey_file] + verb_args
proc = subprocess.run(cmd, capture_output=True, text=True)
print(proc.stdout)
print(proc.stderr, file=sys.stderr)
sys.exit(proc.returncode)

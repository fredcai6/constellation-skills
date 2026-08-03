"""Drive the #688 interrogation survey through the checklist engine (survey => record)."""
import subprocess
import sys

ENGINE = "C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py"
FILE = ".agent-work/issue-688/interrogation.json"
SESSION = "interr-688"
REC = "INTERROGATION_RECORD.json"

FINDINGS = {
    "i0-context": f"Loaded #688 + its #724 routing comment (governing scope), epic #724, "
                  f"#678/#686/#687/#728, packets/physics.md stage-D, grip source at main.",
    "q1": "fact: capability = graded (not binary) session-wetness -> grip-offset sigma.",
    "q2": "fact: NO exclusion exists; rain multiplies session_offset_sigma by 4.0. Issue body wrong.",
    "q3": "fact: rain_flag_from_raw is LEGACY as of #680 (main d4cd4b79, NOT in this checkout).",
    "q4": "fact: defect survived the swap; session_rain_flag is still any-wet-sample.",
    "q5": "fact: wet_lap_fraction is R-only; measured 0/22 populated for Q in 2022 and 2023.",
    "q6": "fact: precedent damage_batch.is_wet_race (same package) + WET_EXCLUDE_THRESHOLD=0.05.",
    "q7": "fact: no committed consumer drops on rain; the weekend rule was spike-only.",
    "q8": "fact: granularity +25pts of session retention vs threshold +1-2pts (2022+23, 220 sessions).",
    "q9": "decision: producer-side only; consumer contract is #712 (owner, stream terminal).",
    "q10": "decision: lands behind #679/#678/#687 as W2 step 6; additive to the re-keyed record.",
    "q11": "decision: narrower allowed for marginal wet, 4.0 preserved at full wetness.",
    "zc-consolidate": f"record at .agent-work/issue-688/{REC}; verify_interrogation.py exit 0; "
                      f"counterpart sign-off = owner's #724 routing comment on #688.",
}


def run(*args):
    out = subprocess.run(
        [sys.executable, ENGINE, "--file", FILE, *args],
        capture_output=True, text=True,
    )
    tail = [ln for ln in (out.stdout + out.stderr).splitlines() if ln.strip()]
    return tail[-1] if tail else "(no output)"


print(run("claim", "--session-id", SESSION, "--claimed-by", "interrogator",
          "--worktree", "."))
for item, finding in FINDINGS.items():
    run("start", item, "--session-id", SESSION)
    print(f"{item}: {run('record', item, '--result', 'pass', '--finding', finding, '--session-id', SESSION)}")
print("consolidate:", run("consolidate", "--session-id", SESSION))
print(run("release", "--session-id", SESSION))

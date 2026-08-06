#!/usr/bin/env python3
"""Generate the byte-identical-except-for-sandbox run prompts for both arms.

The two arms differ in exactly one place in the LAUNCH (which hook directory the
settings file names) and in the sandbox path inside the prompt. Nothing in either
prompt names an agent, an agent id, or anything the governor could read an identity
from, and nothing tells the agents what a trip is, what output to expect, or what
number to reach.
"""
import sys
from pathlib import Path

ACC = Path(__file__).resolve().parent
ENGINE = "C:/Programs/constellation-skills-wt/epic418-a-419/scripts/checklist_engine.py"

TEMPLATE = '''We are testing a checklist tool in a scratch sandbox, using a fixed script. Please work through the steps below in order. Where a step gives a command, run it in Bash exactly as written, without adding anything to it; where it gives a file, read it in full with the Read tool (if a Read comes back truncated, continue it with an offset until you have the whole file). Paste the raw output of every command into your final answer exactly as it came back — the exact text is what we are checking, so please don't rewrite, trim or summarise it. If a command fails, don't retry it and don't try to work around it; just report exactly what came back, including any exit code the tool shows, and carry on with the next step.

STEP 1. Run:
python "{engine}" --file "{sb}/.agent-work/wk-parent/spine.json" claim --session-id sess-parent --claimed-by orchestrator

STEP 2. Run:
python "{engine}" --file "{sb}/.agent-work/wk-parent/spine.json" start g1 --session-id sess-parent

STEP 3. Dispatch a helper with the Agent tool (subagent_type "general-purpose", model "sonnet", run_in_background false) whose prompt is the ALPHA task below. Wait for it, then keep its whole answer for your final report.

ALPHA task:
"Please help test a checklist tool in a scratch sandbox. Do these steps in order. Paste the raw output of every command into your final answer exactly as it came back — the exact text is what we are checking, so please don't rewrite, trim or summarise it. If a command fails, don't retry it and don't try to work around it; just report exactly what came back, including any exit code the tool shows, and carry on. Read each file in full with the Read tool; if a Read comes back truncated, continue it with an offset until you have the whole file.

1. Run: python "{engine}" --file "{sb}/.agent-work/wk-alpha/spine.json" claim --session-id sess-alpha --claimed-by crew
2. Run: python "{engine}" --file "{sb}/.agent-work/wk-alpha/spine.json" start g1 --session-id sess-alpha
3. Read {sb}/corpus/chunk-00.txt
4. Read {sb}/corpus/chunk-01.txt
5. Read {sb}/corpus/chunk-02.txt
6. Read {sb}/corpus/chunk-03.txt
7. Run: python "{engine}" --file "{sb}/.agent-work/wk-alpha/spine.json" current
8. Read {sb}/corpus/chunk-04.txt
9. Read {sb}/corpus/chunk-05.txt
10. Read {sb}/corpus/chunk-06.txt
11. Read {sb}/corpus/chunk-07.txt
12. Run: python "{engine}" --file "{sb}/.agent-work/wk-alpha/spine.json" current
13. Run: python "{engine}" --file "{sb}/.agent-work/wk-alpha/spine.json" advance g1 --session-id sess-alpha

Then answer with the raw output of steps 1, 2, 7, 12 and 13, each under a heading naming its step number. Do not run anything else."

STEP 4. Dispatch a second helper with the Agent tool (subagent_type "general-purpose", model "sonnet", run_in_background false) whose prompt is the BRAVO task below. Wait for it, then keep its whole answer for your final report.

BRAVO task:
"Please help test a checklist tool in a scratch sandbox. Do these steps in order. Paste the raw output of every command into your final answer exactly as it came back — the exact text is what we are checking, so please don't rewrite, trim or summarise it. If a command fails, don't retry it and don't try to work around it; just report exactly what came back, including any exit code the tool shows, and carry on. Read each file in full with the Read tool; if a Read comes back truncated, continue it with an offset until you have the whole file.

1. Run: python "{engine}" --file "{sb}/.agent-work/wk-bravo/spine.json" claim --session-id sess-bravo --claimed-by crew
2. Run: python "{engine}" --file "{sb}/.agent-work/wk-bravo/spine.json" start g1 --session-id sess-bravo
3. Read {sb}/corpus/chunk-08.txt
4. Run: python "{engine}" --file "{sb}/.agent-work/wk-bravo/spine.json" current
5. Read {sb}/corpus/chunk-09.txt
6. Run: python "{engine}" --file "{sb}/.agent-work/wk-bravo/spine.json" current
7. Run: python "{engine}" --file "{sb}/.agent-work/wk-bravo/spine.json" advance g1 --session-id sess-bravo

Then answer with the raw output of steps 1, 2, 4, 6 and 7, each under a heading naming its step number. Do not run anything else."

STEP 5. Dispatch a third helper with the Agent tool (subagent_type "general-purpose", model "sonnet", run_in_background false) whose prompt is the CHARLIE task below. Wait for it, then keep its whole answer for your final report.

CHARLIE task:
"Please help test a scratch sandbox. Do these steps in order and paste the raw output of the command into your final answer exactly as it came back.

1. Read {sb}/corpus/chunk-10.txt in full with the Read tool (if the Read comes back truncated, continue it with an offset until you have the whole file).
2. Run in Bash: echo CHARLIE-DONE

Then answer with the raw output of step 2. Do not run anything else."

STEP 6. Dispatch a fourth helper with the Agent tool (subagent_type "general-purpose", model "sonnet", run_in_background false) whose prompt is the DELTA task below. Wait for it, then keep its whole answer for your final report.

DELTA task:
"Please help test a scratch sandbox. Do these steps in order.

1. Run in Bash: echo DELTA-START
2. Dispatch a helper of your own with the Agent tool (subagent_type \"general-purpose\", model \"sonnet\", run_in_background false) whose prompt is the ECHO task below. Wait for it.

ECHO task:
'Please help test a checklist tool in a scratch sandbox. Do these steps in order. Paste the raw output of every command into your final answer exactly as it came back — the exact text is what we are checking, so please do not rewrite, trim or summarise it. If a command fails, do not retry it and do not try to work around it; just report exactly what came back, including any exit code the tool shows, and carry on. Read the file in full with the Read tool; if the Read comes back truncated, continue it with an offset until you have the whole file.

1. Run: python "{engine}" --file "{sb}/.agent-work/wk-echo/spine.json" claim --session-id sess-echo --claimed-by crew
2. Run: python "{engine}" --file "{sb}/.agent-work/wk-echo/spine.json" start g1 --session-id sess-echo
3. Read {sb}/corpus/chunk-11.txt
4. Run: python "{engine}" --file "{sb}/.agent-work/wk-echo/spine.json" current
5. Run: python "{engine}" --file "{sb}/.agent-work/wk-echo/spine.json" advance g1 --session-id sess-echo
6. Run: python "{engine}" --file "{sb}/.agent-work/wk-echo/spine.json" release --session-id sess-echo

Then answer with the raw output of steps 1, 2, 4, 5 and 6, each under a heading naming its step number. Do not run anything else.'

3. Answer with the raw output of your step 1 command, then your helper's whole answer reproduced exactly as it came back. Do not run anything else."

STEP 7. Read {sb}/corpus/chunk-12.txt in full with the Read tool (continue with an offset if it comes back truncated).

STEP 8. Run:
python "{engine}" --file "{sb}/.agent-work/wk-parent/spine.json" current

STEP 9. Run:
python "{engine}" --file "{sb}/.agent-work/wk-parent/spine.json" advance g1 --session-id sess-parent

STEP 10. Your final answer is, in this order: the raw output of your own steps 1, 2, 8 and 9, then the four helpers' answers (ALPHA, BRAVO, CHARLIE, DELTA) reproduced exactly as they came back, each under a heading naming it. Nothing else.
'''


def main() -> int:
    for arm in ("treatment", "control"):
        sb = str(ACC / ("sb-" + arm)).replace("\\", "/")
        text = TEMPLATE.format(engine=ENGINE, sb=sb)
        out = ACC / ("prompt-%s.txt" % arm)
        out.write_text(text, encoding="utf-8", newline="\n")
        print("%s -> %d bytes" % (out, out.stat().st_size))
    a = (ACC / "prompt-treatment.txt").read_text(encoding="utf-8")
    b = (ACC / "prompt-control.txt").read_text(encoding="utf-8")
    print("prompts identical after normalising the sandbox path: %s"
          % (a.replace("sb-treatment", "SB") == b.replace("sb-control", "SB")))
    return 0


if __name__ == "__main__":
    sys.exit(main())

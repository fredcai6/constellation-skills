@echo off
cd /d C:\Programs\constellation-skills
set BASH_ENV=C:\tmp\codex-constellation-bash-env
"C:\Users\fredc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" scripts\checklist_engine.py --file .agent-work\issue-418-iterative-planning\execute.json advance g4-integrate --session-id root-418-execute --mechanical > .agent-work\issue-418-iterative-planning\g4-implement\g4-integrate.log 2>&1
> .agent-work\issue-418-iterative-planning\g4-implement\g4-integrate.exit echo %ERRORLEVEL%

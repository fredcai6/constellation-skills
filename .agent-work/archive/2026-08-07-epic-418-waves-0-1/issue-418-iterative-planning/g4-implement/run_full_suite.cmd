@echo off
cd /d C:\Programs\constellation-skills
uv run python -m pytest -q tests > .agent-work\issue-418-iterative-planning\g4-implement\full-suite.log 2>&1
echo %ERRORLEVEL%> .agent-work\issue-418-iterative-planning\g4-implement\full-suite.exit

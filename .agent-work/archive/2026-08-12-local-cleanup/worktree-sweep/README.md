# Worktree Sweep Preservation

Date: 2026-08-12

Removed stale registered worktrees after preserving abandoned local state:

- C:/Programs/constellation-skills/.claude/worktrees/agent-a247f573f8ff07d25 at 53c4eaee1bc628047939d8a5b6eae15ba698527f; untracked .agent-work/issue-454-force-color copied here.
- C:/Programs/constellation-skills/.claude/worktrees/agent-adbe19c21cc561d95 at 6bc86b0f43220c81961b607277c749b91de542e6; only untracked .claude/settings.local.json observed.
- C:/Programs/constellation-skills-wt/governor-264 at 3e0193da1caa626d7d15cb7365de0d66d63ebf75 on governor/264-e2e-assertion; uncommitted diff saved as governor-264-uncommitted.patch.
- C:/Users/fredc/AppData/Local/Temp/ctx-skew-d4sqs6ee/clean at 29acf140b91bd54669947774f089e7aac3269b17; locked temp detached worktree, not inspectable from sandbox due filesystem permission denial.

Committed branch heads were not deleted by this sweep.

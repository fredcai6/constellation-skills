## Wave review - boundary w4x-mechanical-and-mcp-only

M1 merged as `27a5adf5`. A dispatched crew can now drive its own spine through the door, and a respawn resumes its lease instead of force-claiming it. Three cold review rounds found three real defects before it landed, including a silent lease hijack in which a child claimed its dispatcher's live lease and got `resumed lease ... (heartbeat refreshed)` exit 0 with `claimed_by` flipped and no takeover recorded.

**The wave's own evidence falsified its governing assumption.** Four crews ran with a correctly bound door. Two used it - 24 and 22 door calls - and both had been told in their handoff to prefer it. The reviewer made zero door calls and drove its survey through the CLI. One rework crew made zero and never touched its spine at all. Binding is necessary and clearly not sufficient.

**A second gap followed from that.** The reviewer's lease carried the `attempt-1` tail the change exists to remove, because it read its session name out of its own prompt, which `build_crew_argv` fills with the attempt-tagged `session_name()`. The derived identity only takes effect through the door.

**Two mechanical defects blocked every dispatch and were worked around by hand.** `build_crew_argv` passes no `--allowedTools` and no `--permission-mode`, so each dispatch needed a gitignored settings file written first - which is almost certainly why all 7 prior crews in this epic used the external backend. And `.mcp.json` hardcodes `python3`, the one interpreter on this host without pytest.

The next wave makes both mechanical, fixes the documentation that sent three handoffs out carrying inline corrections, and sets up #559: agents stop knowing about the CLI entirely.

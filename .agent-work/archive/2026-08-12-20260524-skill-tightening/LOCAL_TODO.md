# Local Work Todo: `skill relationship tightening`

## Task summary

Review the Constellation skill set for explicit inter-skill relationships, template-first guidance, and concise handoff language. Tighten docs/tests without changing runtime code unless validation requires it.

## Source context

**Work ID:** `20260524-skill-tightening`  
**Role:** `conductor/docs implementer`  
**Route/gate:** `single documentation/test gate`  
**Handoff/framing source:** `user request in current thread`  
**Authority:** `user decision + AGENTS.md repo instructions`

## Definition of done

- [x] Skills have clearer relationship contract.
- [x] Skill definitions stay lean and point to templates/references.
- [x] Validation passes.

## Todo

- [x] Map current skill relationships and template usage.
- [x] Add tests for relationship/template discipline.
- [x] Tighten docs and skill language.
- [x] Run tests and final cleanup.

## Work log

### Step 1: `context map`

**Status:** `completed`  
**What happened:** `Read README, overview, operating principles, SKILL files, key templates, and content tests.`  
**Evidence:** `rg --files; Get-Content on docs/skills/tests`  
**Follow-up:** `Add regression tests and edit docs.`

### Step 2: `relationship contract`

**Status:** `completed`  
**What happened:** `Added overview producer/artifact/consumer contract and regression tests for relationship edges and template-first skill bodies.`  
**Evidence:** `tests/test_constellation_content.py; docs/CONSTELLATION_OVERVIEW.md`  
**Follow-up:** `Compress skill bodies under lean limits.`

### Step 3: `skill compression`

**Status:** `completed`  
**What happened:** `Compressed Workbench, Cartographer, Conductor, Crew, and Triage skill definitions while adding explicit template pointers.`  
**Evidence:** `skill body length checks in test_role_skill_bodies_stay_lean`  
**Follow-up:** `Run full tests.`

### Step 4: `verification`

**Status:** `completed`  
**What happened:** `Ran full unittest discovery and whitespace check.`  
**Evidence:** `python -m unittest discover -s tests -> OK, 61 tests; git diff --check -> exit 0 with CRLF warnings only`  
**Follow-up:** `Report outcome.`

## Current state

**Last completed step:** `verification`  
**Current blocker:** `none`  
**Next recommended action:** `Review diff and decide whether to keep tighter wording.`  
**Files/artifacts touched:** `docs/CONSTELLATION_OVERVIEW.md; skills/*/SKILL.md subset; tests/test_constellation_content.py; .agent-work/20260524-skill-tightening/LOCAL_TODO.md`  
**Open assumptions:** `No code behavior change needed.`

# scripts.install_constellation
scripts/install_constellation.py, 1394 lines, 24 holes

HOLE: no docstring

imports stdlib: __future__.annotations, argparse, dataclasses.dataclass, datetime.date, hashlib, json, os, pathlib.Path, re, shutil, subprocess, typing.Callable, typing.Iterable, typing.Mapping, typing.Sequence
imported by: none found

```python
REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / 'skills'
SHARED_REFERENCE_ROOT = SOURCE_ROOT / '_shared'
AGENT_TARGETS: dict[str, AgentTarget] = {'claude': AgentTarget(name='Claude Code', user_env_var=None, user_config_dir='.claude'...
AGENT_CHOICES = sorted((*AGENT_TARGETS, 'all'))
SCRIPT_RUNTIME_COMPANIONS: dict[str, tuple[str, ...]] = {'checklist_engine.py': ('gauge_reader.py', 'episode_capture.py', 'agent_work_root.py',...
SCRIPT_SOURCE_SUBDIRS: dict[str, str] = {'gauge_writer_hook.py': 'hooks', 'spine_rail.py': 'hooks'}
NON_INSTALLABLE_PACKAGES: frozenset[str] = frozenset({'code_map'})
SKILL_SCRIPT_BUNDLES: dict[str, tuple[str, ...]] = {'admiral': ('checklist_engine.py', 'init_work_area.py', 'verify_agent_feedback.py', 'v...
_GLOBAL_EVERYONE = ('global-everyone.md', 'windows.md')
_GLOBAL_ORCHESTRATOR = ('global-everyone.md', 'global-orchestrator.md', 'design-it-twice-brief.md', 'windows.md')
_GLOBAL_CREW = ('global-everyone.md', 'global-crew.md', 'windows.md')
_GLOBAL_ALL_TIERS = ('global-everyone.md', 'global-orchestrator.md', 'global-crew.md', 'windows.md')
SKILL_REFERENCE_BUNDLES: dict[str, tuple[str, ...]] = {'admiral': _GLOBAL_ORCHESTRATOR, 'commander-delegated': _GLOBAL_ORCHESTRATOR, 'lessons...
REWRITABLE_TEXT_SUFFIXES = {'.json', '.md', '.txt'}
INTERPRETER_CANDIDATES: tuple[str, ...] = ('py', 'python3', 'python')
DEFAULT_INTERPRETER_PROBE_TIMEOUT = 5.0
SETTINGS_FILENAME = 'settings.json'
GAUGE_WRITER_HOOK_SCRIPT = 'gauge_writer_hook.py'
HOOK_OWNER_SKILL = 'workbench'
HOOK_OWNER_INSTALL_NAME = 'constellation-workbench'
HOOK_EVENT = 'PostToolUse'
HOOK_MATCHER = '*'
HOOK_TIMEOUT = 10
HOOK_CAPABLE_AGENT_NAMES = frozenset({AGENT_TARGETS['claude'].name})
WIRING_WIRED = 'wired'
WIRING_STALE = 'stale'
WIRING_UNWIRED = 'unwired'
WIRING_UNREADABLE = 'unreadable'
WIRING_UNDETERMINABLE = 'undeterminable'
_EXPANDABLE_ENV_TOKENS = frozenset({'CLAUDE_PROJECT_DIR'})
_ESCAPED_HOOK_SCRIPT = re.escape(GAUGE_WRITER_HOOK_SCRIPT)
_HOOK_SCRIPT_PATH_RE = re.compile(f'"([^"]*{_ESCAPED_HOOK_SCRIPT})"|(\\S*{_ESCAPED_HOOK_SCRIPT})')
_ENV_TOKEN_RE = re.compile('\\$\\{([A-Za-z_][A-Za-z0-9_]*)\\}|%([A-Za-z_][A-Za-z0-9_]*)%')
CORPUS_MARKER = 'CORPUS.json'
```

- [InstallError](InstallError.md) class: Raised for clear, user-correctable installer failures.
- [Skill](Skill.md) class: HOLE: no docstring
- [AgentTarget](AgentTarget.md) class: HOLE: no docstring
- [script_source_path](script_source_path.md) function: Where a bundled script is READ from. Single resolver so validation and the
- [expand_script_bundle](expand_script_bundle.md) function: Add each script's runtime companions, preserving order and de-duplicating.
- [parse_frontmatter](parse_frontmatter.md) function: HOLE: no docstring
- [discover_skills](discover_skills.md) function: HOLE: no docstring
- [select_skills](select_skills.md) function: HOLE: no docstring
- [validate_required_scripts](validate_required_scripts.md) function: HOLE: no docstring
- [validate_required_references](validate_required_references.md) function: HOLE: no docstring
- [_platform_interpreter](_platform_interpreter.md) function: Interpreter for installed command strings: the `py` launcher on Windows,
- [InterpreterResolution](InterpreterResolution.md) class: The interpreter resolved for ONE install run, plus how it was resolved --
  - [InterpreterResolution.as_sidecar](InterpreterResolution.as_sidecar.md) method: HOLE: no docstring
- [_probe_interpreter_candidate](_probe_interpreter_candidate.md) function: Whether `<candidate> --version` exits 0 within `timeout`. A missing
- [probe_host_interpreter](probe_host_interpreter.md) function: Try each candidate in order via a REAL `<candidate> --version` subprocess
- [resolve_interpreter](resolve_interpreter.md) function: Resolve the interpreter to stamp into installed skill bodies for ONE
- [rewrite_installed_skill_paths](rewrite_installed_skill_paths.md) function: HOLE: no docstring
- [home_from_env](home_from_env.md) function: HOLE: no docstring
- [default_user_target](default_user_target.md) function: HOLE: no docstring
- [resolve_target_root](resolve_target_root.md) function: HOLE: no docstring
- [resolve_target_roots](resolve_target_roots.md) function: HOLE: no docstring
- [ensure_target_is_inside_root](ensure_target_is_inside_root.md) function: HOLE: no docstring
- [remove_existing_constellation_set](remove_existing_constellation_set.md) function: HOLE: no docstring
- [HookWiring](HookWiring.md) class: One read-only verdict about one settings.json.
- [settings_path_for_target_root](settings_path_for_target_root.md) function: The settings.json governing the agent config dir this install writes
- [installed_gauge_writer_path](installed_gauge_writer_path.md) function: HOLE: no docstring
- [_expand_env_tokens](_expand_env_tokens.md) function: Expand ONLY `_EXPANDABLE_ENV_TOKENS`, and only when actually set,
  - [_expand_env_tokens.replace](_expand_env_tokens.replace.md) method: HOLE: no docstring
- [extract_hook_script_path](extract_hook_script_path.md) function: The gauge-writer script path a hook `command` string invokes, or None
- [governor_hook_commands](governor_hook_commands.md) function: Every PostToolUse `command` string that invokes a gauge writer hook,
- [detect_hook_wiring](detect_hook_wiring.md) function: Three-state and READ-ONLY -- opens nothing for writing and creates
- [describe_hook_wiring](describe_hook_wiring.md) function: One reportable line. ASCII only -- this goes to a Windows console.
- [report_hook_wiring](report_hook_wiring.md) function: HOLE: no docstring
- [build_hook_command](build_hook_command.md) function: The literal `command` string an entry carries.
- [build_hook_entry](build_hook_entry.md) function: HOLE: no docstring
- [add_hook_entry](add_hook_entry.md) function: Append `entry` as a SIBLING in `hooks.PostToolUse`, in place. Never nests
- [wire_hooks](wire_hooks.md) function: The ONE path on which this installer writes a settings.json. Reached only
- [install_skills](install_skills.md) function: HOLE: no docstring
- [_hash_file](_hash_file.md) function: HOLE: no docstring
- [_source_commit](_source_commit.md) function: HOLE: no docstring
- [compute_corpus_id](compute_corpus_id.md) function: Content id of an installed skill tree: ``"sha256:" + sha256`` over the
- [write_corpus_marker](write_corpus_marker.md) function: Compute the corpus id and write ``<skills_dir>/CORPUS.json``. Returns the id.
- [assert_corpus](assert_corpus.md) function: Whether a copied skill tree hashes to ``expected_id`` (whole-tree). A
- [write_template_baselines](write_template_baselines.md) function: Seed pristine blank-template baselines + manifest for a project install.
- [extend_template_baselines](extend_template_baselines.md) function: Track upstream templates that aren't in this project's baseline yet.
- [write_template_working_copies](write_template_working_copies.md) function: Seed editable project-local template working copies (flat, never clobbered).
- [build_parser](build_parser.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring

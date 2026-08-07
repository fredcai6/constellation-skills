# scripts.apply_episode_delta:Episode
class, scripts/apply_episode_delta.py:231, 27 lines

```python
@dataclass
class Episode
```

HOLE: no docstring

```python
episode_id: str
run: str
project: str
role: str
spine_step: str
context_manifest_ref: str
refusals: int
reopens: int
rework_count: int
failed_commands: int
artifact_refs: list[str]
agent_supplied: dict[str, Assertion]
diagnosis: list[Assertion] = field(default_factory=list)
status: str = 'active'
retired_reason: str = ''
retired_at: str = ''
consolidated_into: str = ''
superseded_by: str = ''
```

- [all_assertions](Episode.all_assertions.md) method: Flat aid -> Assertion map spanning both agent-supplied and diagnosis bins,

calls stdlib: dataclasses.field
reads internal: Assertion x3
reads stdlib: builtins.str x14, builtins.int x4, builtins.list x3, builtins.dict x2
writes internal: Episode.agent_supplied, Episode.artifact_refs, Episode.consolidated_into, Episode.context_manifest_ref, Episode.diagnosis, Episode.episode_id, Episode.failed_commands, Episode.project, Episode.refusals, Episode.reopens, Episode.retired_at, Episode.retired_reason, Episode.rework_count, Episode.role, Episode.run, Episode.spine_step, Episode.status, Episode.superseded_by

referenced by: 9 sites, this module only

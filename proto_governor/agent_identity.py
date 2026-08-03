"""PROTOTYPE (throwaway) -- exc-6: can the governor track a subagent under its
OWN identity?

Pure logic module. No engine imports, no hook imports, no side effects beyond
reading transcript files. This is the piece that could survive into real code.

The production failure (#383): `spine_rail.py` keys `.spine-rail-binding.json`
by the harness `session_id` from the hook payload. Agent-tool subagents SHARE
the parent's `session_id`, so every crew claim piles another entry under one
key; the gauge writer sees >1 candidate, calls it ambiguous, and writes
nothing. Measured live in the main checkout: 36 bindings under one session id.

The discriminator this module uses instead: as of Claude Code 2.1.220 the
harness writes each subagent its OWN transcript at

    ~/.claude/projects/<project-slug>/<session_id>/subagents/agent-<agentId>.jsonl

and every line in it carries a distinct top-level `agentId`. The parent's
transcript stays at `<session_id>.jsonl` and its lines carry no `agentId`.
So a per-agent identity DOES exist at runtime; it is simply not the field the
binding is keyed on.

Three ways to get that identity are implemented below (V1/V2/V3) so the
prototype can report which ones actually work from inside a tool subprocess.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path

TAIL_BYTES = 2 * 1024 * 1024

MODEL_WINDOWS = {
    "claude-opus-5": 200_000,
    "claude-opus-5[1m]": 1_000_000,
    "claude-sonnet-5": 200_000,
    "claude-haiku-4-5-20251001": 200_000,
}
DEFAULT_WINDOW = 200_000


@dataclass
class AgentIdentity:
    """Who is acting right now.

    `identity_key` is the thing a binding should be keyed on. For the parent
    it is the bare session_id (unchanged from today, so parents keep working);
    for a subagent it is `<session_id>#<agent_id>`, which is unique per agent.
    """

    identity_key: str
    session_id: str
    agent_id: str | None
    transcript_path: str | None
    method: str
    is_subagent: bool

    def as_dict(self) -> dict:
        return asdict(self)


def project_slug(project_dir: Path) -> str:
    """Claude Code's on-disk slug for a project dir: non-alphanumerics -> '-'."""
    s = str(Path(project_dir).resolve())
    return "".join(c if c.isalnum() else "-" for c in s)


def transcript_root(session_id: str, project_dir: Path, home: Path | None = None) -> Path:
    home = home or Path(os.path.expanduser("~"))
    return home / ".claude" / "projects" / project_slug(project_dir) / session_id


def parent_transcript(session_id: str, project_dir: Path, home: Path | None = None) -> Path:
    root = transcript_root(session_id, project_dir, home)
    return root.with_suffix(".jsonl")


def subagent_transcripts(session_id: str, project_dir: Path, home: Path | None = None) -> list[Path]:
    d = transcript_root(session_id, project_dir, home) / "subagents"
    try:
        return sorted(d.glob("agent-*.jsonl"))
    except Exception:
        return []


def _tail_text(path: Path, nbytes: int = TAIL_BYTES) -> str:
    try:
        size = path.stat().st_size
        with open(path, "rb") as f:
            if size > nbytes:
                f.seek(size - nbytes)
            return f.read().decode("utf-8", errors="replace")
    except Exception:
        return ""


def _agent_id_from_transcript(path: Path) -> str | None:
    """Read the `agentId` any line in this subagent transcript carries."""
    text = _tail_text(path, 256 * 1024)
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        aid = rec.get("agentId")
        if aid:
            return aid
    return None


# --- V1: environment only -----------------------------------------------------

def resolve_v1_env(session_id: str) -> AgentIdentity | None:
    """Ask the environment who we are.

    The env DOES say whether we are a child (`CLAUDE_CODE_CHILD_SESSION=1`) but
    carries NO per-agent id, so every concurrent subagent resolves to the same
    key. Returns an identity only when we are the parent -- for a child it
    returns None, which is the honest answer for this method.
    """
    if os.environ.get("CLAUDE_CODE_CHILD_SESSION") == "1":
        return None
    return AgentIdentity(
        identity_key=session_id,
        session_id=session_id,
        agent_id=None,
        transcript_path=None,
        method="v1-env",
        is_subagent=False,
    )


# --- V2: self-identification by our own argv ----------------------------------

def _raw_probe_hit(path: Path, probe: str) -> bool:
    """V2a: does the probe appear ANYWHERE in this transcript's tail?

    Measured to be unusable on its own. A dispatching agent writes the child's
    command verbatim into the Agent-tool prompt, so the parent's transcript
    contains the probe too and every dispatched call resolves as ambiguous.
    Kept only so the prototype can show the contaminated variant failing.
    """
    return probe in _tail_text(path)


def _bash_probe_hit(path: Path, probe: str) -> bool:
    """V2b: does the probe appear in an actual Bash `tool_use` on this
    transcript -- i.e. did THIS agent really issue the command?

    This is the fix for V2a. A dispatcher's copy of the same text sits in an
    Agent/Task tool_use `prompt`, never in a Bash tool_use `command`, so
    matching on the structured field cleanly separates who ran it from who
    merely talked about running it.
    """
    for line in reversed(_tail_text(path).splitlines()):
        line = line.strip()
        if not line.startswith("{") or probe.split()[0] not in line:
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if rec.get("type") != "assistant":
            continue
        content = (rec.get("message") or {}).get("content") or []
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            if block.get("name") != "Bash":
                continue
            command = (block.get("input") or {}).get("command") or ""
            if probe in command:
                return True
    return False


def resolve_v2_self_probe(
    session_id: str,
    probe: str,
    project_dir: Path,
    home: Path | None = None,
    structured: bool = True,
) -> AgentIdentity | None:
    """Find which agent issued the tool call we are running inside.

    The harness persists an assistant turn's `tool_use` (command string and all)
    to the ACTING agent's transcript before the tool executes -- verified live.
    So a subprocess can locate itself by looking for its own command line.
    Exactly one hit resolves; zero or several is honest ambiguity -> None.

    `structured=False` selects the naive substring variant (V2a) that the
    prototype measured failing; the default is the structured matcher (V2b).
    """
    if not probe:
        return None
    hit = _bash_probe_hit if structured else _raw_probe_hit
    hits: list[tuple[Path, str | None]] = []
    for p in subagent_transcripts(session_id, project_dir, home):
        if hit(p, probe):
            hits.append((p, _agent_id_from_transcript(p)))
    parent = parent_transcript(session_id, project_dir, home)
    parent_hit = hit(parent, probe)
    if len(hits) == 1 and not parent_hit:
        path, aid = hits[0]
        if not aid:
            return None
        return AgentIdentity(
            identity_key=f"{session_id}#{aid}",
            session_id=session_id,
            agent_id=aid,
            transcript_path=str(path),
            method="v2-self-probe",
            is_subagent=True,
        )
    if parent_hit and not hits:
        return AgentIdentity(
            identity_key=session_id,
            session_id=session_id,
            agent_id=None,
            transcript_path=str(parent),
            method="v2-self-probe",
            is_subagent=False,
        )
    return None


# --- V3: agent declares its own id --------------------------------------------

def resolve_v3_declared(
    session_id: str,
    agent_id: str,
    project_dir: Path,
    home: Path | None = None,
) -> AgentIdentity | None:
    """Trust an `--agent-id` the caller passes, but only if a transcript by that
    name actually exists. Cooperative, and the cheapest of the three -- but it
    depends on the agent knowing and honestly reporting its own id."""
    if not agent_id:
        return None
    for p in subagent_transcripts(session_id, project_dir, home):
        if p.stem == f"agent-{agent_id}":
            return AgentIdentity(
                identity_key=f"{session_id}#{agent_id}",
                session_id=session_id,
                agent_id=agent_id,
                transcript_path=str(p),
                method="v3-declared",
                is_subagent=True,
            )
    return None


def resolve(
    session_id: str,
    project_dir: Path,
    probe: str = "",
    declared_agent_id: str = "",
    home: Path | None = None,
    structured: bool = True,
) -> AgentIdentity | None:
    """Best available identity: declared, else self-probe, else env."""
    return (
        resolve_v3_declared(session_id, declared_agent_id, project_dir, home)
        or resolve_v2_self_probe(session_id, probe, project_dir, home, structured)
        or resolve_v1_env(session_id)
    )


# --- gauge reading, per identity ----------------------------------------------

def read_fill(identity: AgentIdentity) -> dict | None:
    """The governor's reading, taken from THIS identity's own transcript.

    Same X2 sum as the production writer, but the sidechain filter is inverted
    for a subagent: in a subagent's own transcript every line is sidechain, and
    those lines are exactly the ones we want.
    """
    if not identity.transcript_path:
        return None
    text = _tail_text(Path(identity.transcript_path))
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if rec.get("type") != "assistant":
            continue
        if identity.is_subagent:
            if rec.get("agentId") != identity.agent_id:
                continue
        elif rec.get("isSidechain"):
            continue
        msg = rec.get("message") or {}
        usage = msg.get("usage") or {}
        model = msg.get("model")
        ts = rec.get("timestamp")
        try:
            total = (
                int(usage["input_tokens"])
                + int(usage["cache_creation_input_tokens"])
                + int(usage["cache_read_input_tokens"])
            )
        except Exception:
            continue
        if not model or not ts:
            continue
        window = MODEL_WINDOWS.get(model, DEFAULT_WINDOW)
        return {
            "schema_version": 1,
            "fill_fraction": round(total / window, 4),
            "model": model,
            "observed_at": ts,
        }
    return None

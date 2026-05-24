from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable, Sequence


ALLOWED_LEVELS = {
    "system-context",
    "container",
    "component",
    "code-path",
    "module",
    "function-or-method",
}
ALLOWED_NODE_STATUS = {"current", "partial", "stale", "disputed"}
ALLOWED_CONFIDENCE = {"high", "medium", "low", "unknown"}
ALLOWED_RELATIONSHIPS = {"depends-on", "serves", "constrained-by"}
SOURCE_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".cs"}


class MapBuildError(Exception):
    """Raised when architecture map inputs fail validation."""


class BuildResult:
    def __init__(self, map_data: dict[str, Any], output_path: Path | None, errors: list[str]):
        self.map_data = map_data
        self.output_path = output_path
        self.errors = errors


def normalize_value(value: str) -> str | None:
    cleaned = value.strip().strip("`").strip()
    if cleaned in {"", "none", "null"}:
        return None
    return cleaned


def repo_path(repo_root: Path, path: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def required_field(fields: dict[str, str | None], name: str, packet: Path) -> str:
    value = fields.get(name)
    if not value:
        raise MapBuildError(f"{packet} missing required field: {name}")
    return value


def parse_packet(packet: Path, repo_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    text = packet.read_text(encoding="utf-8")
    fields: dict[str, str | None] = {}
    relationships: list[dict[str, Any]] = []
    section: str | None = None

    field_re = re.compile(r"^\*\*(?P<name>[^*]+):\*\*\s*(?P<value>.*)$")
    dependency_re = re.compile(
        r"^-\s*`(?P<source>[^`]+)`\s*->\s*`(?P<target>[^`]+)`;"
        r"\s*type\s*`(?P<type>[^`]+)`;"
        r"\s*provenance\s*`(?P<provenance>[^`]+)`;"
        r"\s*confidence\s*`(?P<confidence>[^`]+)`;"
        r"\s*evidence\s*`(?P<evidence>[^`]+)`"
    )

    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue

        match = field_re.match(line.strip())
        if match:
            fields[match.group("name").strip().lower()] = normalize_value(match.group("value"))
            continue

        if section == "dependencies":
            dependency = dependency_re.match(line.strip())
            if dependency:
                relationships.append(
                    {
                        "source": dependency.group("source"),
                        "target": dependency.group("target"),
                        "type": dependency.group("type"),
                        "provenance": dependency.group("provenance"),
                        "evidence": [dependency.group("evidence")],
                        "confidence": dependency.group("confidence"),
                    }
                )

    node_id = required_field(fields, "structural node", packet)
    level = required_field(fields, "level", packet)
    status = required_field(fields, "status", packet)
    confidence = required_field(fields, "confidence", packet)

    node = {
        "id": node_id,
        "level": level,
        "parent": fields.get("parent"),
        "status": status,
        "confidence": confidence,
        "packet": repo_path(repo_root, packet),
    }
    if fields.get("path"):
        node["path"] = fields["path"]
    if fields.get("symbol"):
        node["symbol"] = fields["symbol"]
    return node, relationships


def parse_overlay_value(value: str) -> Any:
    cleaned = value.strip().strip("\"'")
    if cleaned in {"null", "none", "~"}:
        return None
    return cleaned


def parse_overlay(path: Path, repo_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    nodes: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    current_section: str | None = None
    current_item: dict[str, Any] | None = None
    in_evidence = False

    def flush() -> None:
        nonlocal current_item
        if not current_section or current_item is None:
            return
        if current_section in {"purposes", "constraints"}:
            nodes.append(
                {
                    "id": current_item.get("id"),
                    "kind": current_item.get("kind"),
                    "parent": current_item.get("parent"),
                    "label": current_item.get("label"),
                    "overlay": repo_path(repo_root, path),
                }
            )
        elif current_section == "relationships":
            item = dict(current_item)
            item.setdefault("evidence", [repo_path(repo_root, path)])
            relationships.append(item)
        current_item = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if not raw_line.startswith(" ") and raw_line.endswith(":"):
            flush()
            current_section = raw_line[:-1].strip()
            in_evidence = False
            continue

        stripped = raw_line.strip()
        if stripped.startswith("- "):
            value = stripped[2:]
            if in_evidence and current_item is not None:
                current_item.setdefault("evidence", []).append(parse_overlay_value(value))
                continue
            flush()
            current_item = {}
            if ":" in value:
                key, item_value = value.split(":", 1)
                current_item[key.strip()] = parse_overlay_value(item_value)
            continue

        if current_item is None or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        if key == "evidence":
            current_item["evidence"] = []
            in_evidence = True
            continue
        in_evidence = False
        current_item[key] = parse_overlay_value(value)

    flush()
    return nodes, relationships


def module_node_id(path: Path) -> str:
    without_suffix = path.with_suffix("").as_posix()
    stable = re.sub(r"[^A-Za-z0-9_.-]+", "_", without_suffix.replace("/", "."))
    return f"struct:module:{stable}"


def scan_source_tree(repo_root: Path, source_roots: Iterable[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    nodes: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    saw_unmapped_module = False

    for source_root in source_roots:
        root = repo_root / source_root
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if any(part.startswith(".") or part == "__pycache__" for part in path.parts):
                continue
            rel = path.relative_to(repo_root)
            if path.name.lower() in {"readme.md", "spec.md", "specification.md"}:
                findings.append(
                    {
                        "class": "parallel canonical docs",
                        "path": rel.as_posix(),
                        "message": "source-local canonical doc may duplicate architecture packet truth",
                    }
                )
                continue
            if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
                continue
            saw_unmapped_module = True
            nodes.append(
                {
                    "id": module_node_id(rel),
                    "level": "module",
                    "parent": "struct:unmapped_modules",
                    "path": rel.as_posix(),
                    "status": "current",
                    "confidence": "low",
                    "provenance": "generated",
                }
            )

    if saw_unmapped_module:
        nodes.append(
            {
                "id": "struct:unmapped_modules",
                "level": "component",
                "parent": None,
                "purpose": "Holding parent for source files without a curated structural parent.",
                "status": "partial",
                "confidence": "low",
                "provenance": "generated",
            }
        )
    return nodes, findings


def validate_map(nodes: Sequence[dict[str, Any]], relationships: Sequence[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    ids = {node.get("id") for node in nodes if node.get("id")}
    seen: set[str] = set()
    duplicates: set[str] = set()

    for node in nodes:
        node_id = node.get("id")
        if not node_id:
            errors.append("node missing id")
            continue
        if node_id in seen:
            duplicates.add(node_id)
        seen.add(node_id)

        if node_id.startswith("struct:"):
            level = node.get("level")
            if level not in ALLOWED_LEVELS:
                errors.append(f"{node_id} has invalid level: {level}")
            if node.get("status") not in ALLOWED_NODE_STATUS:
                errors.append(f"{node_id} has invalid status: {node.get('status')}")
            if node.get("confidence") not in ALLOWED_CONFIDENCE:
                errors.append(f"{node_id} has invalid confidence: {node.get('confidence')}")
            parent = node.get("parent")
            if parent and parent not in ids:
                errors.append(f"{node_id} missing parent: {parent}")

    for duplicate in sorted(duplicates):
        errors.append(f"duplicate id: {duplicate}")

    for relationship in relationships:
        rel_type = relationship.get("type")
        if rel_type not in ALLOWED_RELATIONSHIPS:
            errors.append(f"disallowed relationship type: {rel_type}")
            continue
        source = relationship.get("source")
        target = relationship.get("target")
        if source not in ids:
            errors.append(f"relationship source missing: {source}")
        if target not in ids:
            errors.append(f"relationship target missing: {target}")
        if relationship.get("confidence") and relationship.get("confidence") not in ALLOWED_CONFIDENCE:
            errors.append(f"relationship has invalid confidence: {relationship.get('confidence')}")

    return errors


def build_architecture_map(
    repo_root: str | Path,
    *,
    source_roots: Sequence[str] = ("src",),
    write_output: bool = True,
) -> BuildResult:
    root = Path(repo_root)
    architecture_root = root / "docs" / "architecture"
    packets_root = architecture_root / "packets"
    overlays_root = architecture_root / "overlays"

    nodes: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []

    for packet in sorted(packets_root.glob("*.md")) if packets_root.exists() else []:
        node, packet_relationships = parse_packet(packet, root)
        nodes.append(node)
        relationships.extend(packet_relationships)

    for overlay in sorted(overlays_root.glob("*.yml")) if overlays_root.exists() else []:
        overlay_nodes, overlay_relationships = parse_overlay(overlay, root)
        nodes.extend(overlay_nodes)
        relationships.extend(overlay_relationships)

    source_nodes, source_findings = scan_source_tree(root, source_roots)
    nodes.extend(source_nodes)
    findings.extend(source_findings)

    nodes = sorted(nodes, key=lambda item: item.get("id") or "")
    relationships = sorted(
        relationships,
        key=lambda item: (item.get("source") or "", item.get("type") or "", item.get("target") or ""),
    )
    findings = sorted(findings, key=lambda item: (item.get("class") or "", item.get("path") or ""))

    errors = validate_map(nodes, relationships)
    if errors:
        raise MapBuildError("; ".join(errors))

    map_data = {
        "version": 1,
        "nodes": nodes,
        "relationships": relationships,
        "findings": findings,
    }

    output_path = architecture_root / "generated" / "map.json"
    if write_output:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(map_data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return BuildResult(map_data=map_data, output_path=output_path if write_output else None, errors=[])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and validate Cartographer structural map artifacts.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root. Defaults to cwd.")
    parser.add_argument(
        "--source-root",
        action="append",
        dest="source_roots",
        help="Source root to scan. May be provided multiple times. Defaults to src.",
    )
    parser.add_argument("--check", action="store_true", help="Validate without writing generated map.json.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = build_architecture_map(
            args.root,
            source_roots=tuple(args.source_roots or ("src",)),
            write_output=not args.check,
        )
    except MapBuildError as exc:
        parser.exit(2, f"error: {exc}\n")

    if result.output_path:
        print(f"wrote {result.output_path}")
    else:
        print("architecture map inputs are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

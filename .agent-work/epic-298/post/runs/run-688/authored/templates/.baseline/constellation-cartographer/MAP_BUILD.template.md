# Structural Map Build

This file tells Cartographer how to regenerate generated structural map artifacts.

It is not architecture truth.

## Source Artifacts

- `docs/architecture/index.md`
- `docs/architecture/packets/`
- `docs/architecture/overlays/`
- repo source tree

## Generated Artifacts

- `docs/architecture/generated/map.json`
- `docs/architecture/generated/nodes/`
- `docs/architecture/generated/index.md`

## Build Command

```bash
python C:/Users/fredc/.claude/skills/constellation-cartographer/scripts/build_architecture_map.py --root . --source-root src
```

## Check Command

```bash
python C:/Users/fredc/.claude/skills/constellation-cartographer/scripts/build_architecture_map.py --root . --source-root src --check
```

## Required After Changing

- architecture packets
- architecture overlays
- architecture index
- source roots or map generation config

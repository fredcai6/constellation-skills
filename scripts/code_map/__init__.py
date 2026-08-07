"""code_map — derive a code map for this repository from its own source.

The pipeline is four stages, each a module here and each a CLI subcommand:

    discovery   enumerate the mappable corpus (the source the map is derived from)
    extract     two-pass AST walk -> the statement store
    supplement  second AST pass -> the fields the statement vocabulary lacks
    render      the page tree under map/

Run it as `python -m scripts.code_map <subcommand>` from the repository root.

This is the repository's first Python package under `scripts/`; the other 42
scripts are flat modules. `scripts/hooks/` is the directory precedent.

Constraint: stdlib only. CI installs pytest and coverage and nothing else, so a
third-party import means the tool cannot run at all.

Constraint: this package CANNOT be bundled into an installed skill as it stands.
`scripts/install_constellation.py` copies each required script to a FLAT
destination (`<installed skill>/scripts/<name>`), which breaks the intra-package
imports below. See NON_INSTALLABLE_SCRIPT_PACKAGES there.
"""

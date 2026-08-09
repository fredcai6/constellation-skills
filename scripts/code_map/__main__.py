"""`python -m scripts.code_map` — the package's executable form."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())

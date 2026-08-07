# src.utils
src/utils/__init__.py, 19 lines

Utility Functions Module

This module provides utility functions and configuration management
for the F1Brainz system.

Key components:
    - config: Configuration management with YAML validation
    - constants: Centralized constants (calendars, thresholds, etc.)
    - ids: Driver ID mapping between FastF1 and Ergast

Example:
    from src.utils.config import Config
    from src.utils.constants import F1_CALENDARS

    config = Config.load_config()
    seasons = Config.get_seasons()
    calendar = F1_CALENDARS[2024]

imported by: none found (scripts/ and tests/ not indexed)

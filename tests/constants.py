"""Shared filesystem paths for the test suite."""

from pathlib import Path

FILES_DIR = Path(__file__).parent / "files"

COMMANDS_FILE = str(FILES_DIR / "send_commands_from_file")
CONFIG_FILE = str(FILES_DIR / "send_configs_from_file")

"""Check the versions of a release and set the calendar version for its second build.

A release of the major version set in `[tool.nornir_scrapli.release] calver-line` is published
twice on PyPI: once with its semantic version and once with its calendar version.

Usage:
    python scripts/release.py check --tag 1.5.1 [--pypi]
    python scripts/release.py set-calver 2026.10.30
"""

import argparse
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parent.parent
INIT_FILE = ROOT / "nornir_scrapli" / "__init__.py"
PYPROJECT_FILE = ROOT / "pyproject.toml"
CHANGELOG_FILE = ROOT / "CHANGELOG.md"
PYPI_URL = "https://pypi.org/pypi/nornir-scrapli/json"

VERSION_PATTERN = re.compile(r'^__version__ = "(?P<version>[^"]*)"$', re.MULTILINE)
CALVER_PATTERN = re.compile(r"^(\d{4})\.(\d{1,2})\.(\d{1,2})(?:\.(\d+))?$")


def read_version(init_text: str) -> str:
    """Return the `__version__` value of `nornir_scrapli/__init__.py`.

    Raises:
        ValueError: if the file has no `__version__` line.

    """
    match = VERSION_PATTERN.search(init_text)
    if match is None:
        raise ValueError("nornir_scrapli/__init__.py has no __version__ line")
    return match.group("version")


def set_version(init_text: str, version: str) -> str:
    """Return the text of `nornir_scrapli/__init__.py` with `__version__` set to `version`."""
    read_version(init_text)
    return VERSION_PATTERN.sub(f'__version__ = "{version}"', init_text)


def read_release_config(pyproject_text: str) -> tuple[int, str]:
    """Return the major version that has calendar versions, and the calendar version to publish."""
    config = tomllib.loads(pyproject_text)["tool"]["nornir_scrapli"]["release"]
    return int(config["calver-line"]), str(config["calver"])


def parse_calver(value: str) -> tuple[int, int, int, int] | None:
    """Return a calendar version as a tuple to compare, or None if it is not a calendar version.

    A calendar version is `YYYY.MM.DD`, or `YYYY.MM.DD.N` for a second release on the same day.
    """
    match = CALVER_PATTERN.match(value)
    if match is None:
        return None
    year, month, day, serial = match.groups()
    try:
        date(int(year), int(month), int(day))
    except ValueError:
        return None
    return int(year), int(month), int(day), int(serial or 0)


def changelog_heading(changelog_text: str, version: str) -> str | None:
    """Return the changelog heading of `version`, or None if the changelog has none."""
    for line in changelog_text.splitlines():
        if line.startswith(f"## {version} "):
            return line
    return None


def check_release(
    tag: str,
    version: str,
    calver_line: int,
    calver: str,
    changelog_text: str,
    published_versions: list[str],
) -> list[str]:
    """Return the problems that block publishing the release; an empty list means none."""
    errors = []
    if tag != version:
        errors.append(f"the release tag {tag} does not match __version__ {version}")

    major = int(version.split(".", maxsplit=1)[0])
    if major == calver_line and not calver:
        errors.append(
            f"{version} is a {calver_line}.x release, so [tool.nornir_scrapli.release] calver "
            "must be set"
        )
    if major != calver_line and calver:
        errors.append(
            f"{version} is not a {calver_line}.x release, so [tool.nornir_scrapli.release] "
            "calver must be empty"
        )

    calver_key = parse_calver(calver) if calver else None
    if calver and calver_key is None:
        errors.append(f"calver {calver} is not a YYYY.MM.DD or YYYY.MM.DD.N version")
    if calver_key is not None:
        published = {
            key: value for value in published_versions if (key := parse_calver(value)) is not None
        }
        if published and calver_key <= max(published):
            highest = published[max(published)]
            errors.append(f"calver {calver} is not higher than the published {highest}")

    heading = changelog_heading(changelog_text, version)
    if heading is None:
        errors.append(f"CHANGELOG.md has no '## {version} ' heading")
    elif calver and f"(also published as {calver})" not in heading:
        errors.append(
            f"the CHANGELOG.md heading of {version} must say '(also published as {calver})'"
        )
    elif not calver and "also published as" in heading:
        errors.append(f"the CHANGELOG.md heading of {version} names a calendar version")

    return errors


def fetch_published_versions() -> list[str]:
    """Return the versions of nornir-scrapli published on PyPI."""
    with urllib.request.urlopen(PYPI_URL, timeout=30) as response:
        return list(json.load(response)["releases"])


def main() -> int:
    """Run the command given on the command line.

    Returns:
        The exit status: 0 on success, 1 if the release has problems.

    """
    parser = argparse.ArgumentParser(description="Check and set the versions of a release.")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="check the versions and print calver=<value>")
    check.add_argument("--tag", required=True, help="tag of the GitHub release")
    check.add_argument(
        "--pypi", action="store_true", help="check that calver is higher than the versions on PyPI"
    )
    set_calver = commands.add_parser("set-calver", help="set __version__ to a calendar version")
    set_calver.add_argument("calver")
    args = parser.parse_args()

    if args.command == "set-calver":
        INIT_FILE.write_text(set_version(INIT_FILE.read_text(), args.calver))
        return 0

    calver_line, calver = read_release_config(PYPROJECT_FILE.read_text())
    errors = check_release(
        tag=args.tag,
        version=read_version(INIT_FILE.read_text()),
        calver_line=calver_line,
        calver=calver,
        changelog_text=CHANGELOG_FILE.read_text(),
        published_versions=fetch_published_versions() if args.pypi else [],
    )
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"calver={calver}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

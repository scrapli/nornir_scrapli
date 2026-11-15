import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("tomllib")

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "release.py"
spec = importlib.util.spec_from_file_location("release", SCRIPT_PATH)
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)

CHANGELOG_WITH_CALVER = "# Changelog\n\n## 1.5.1 (also published as 2026.10.30) - 2026-10-30\n"
CHANGELOG_WITHOUT_CALVER = "# Changelog\n\n## 2.0.0 - 2026-11-02\n"
CHANGELOG_PRERELEASE = "# Changelog\n\n## 1.6.0a1 - 2026-11-14\n"
PUBLISHED = ["2025.1.30", "2026.10.13", "2023.1.30.post1", "1.5.0"]


def test_read_and_set_version():
    init_text = '"""nornir_scrapli"""\n\n__version__ = "1.5.1"\n'
    assert release.read_version(init_text) == "1.5.1"
    assert release.read_version(release.set_version(init_text, "2026.10.30")) == "2026.10.30"


def test_read_version_missing():
    with pytest.raises(ValueError):
        release.read_version('"""nornir_scrapli"""\n')


def test_read_release_config():
    pyproject_text = '[tool.nornir_scrapli.release]\ncalver-line = 1\ncalver = "2026.10.30"\n'
    assert release.read_release_config(pyproject_text) == (1, "2026.10.30")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2026.10.30", (2026, 10, 30, 0)),
        ("2025.01.30", (2025, 1, 30, 0)),
        ("2026.10.30.1", (2026, 10, 30, 1)),
        ("2026.2.30", None),
        ("1.5.1", None),
        ("2023.1.30.post1", None),
    ],
)
def test_parse_calver(value, expected):
    assert release.parse_calver(value) == expected


def test_check_release_with_calver():
    errors = release.check_release(
        "1.5.1", "1.5.1", 1, "2026.10.30", CHANGELOG_WITH_CALVER, PUBLISHED
    )
    assert errors == []


def test_check_release_without_calver():
    errors = release.check_release("2.0.0", "2.0.0", 1, "", CHANGELOG_WITHOUT_CALVER, PUBLISHED)
    assert errors == []


@pytest.mark.parametrize(
    ("version", "expected"),
    [
        ("1.6.0a1", True),
        ("1.6.0b2", True),
        ("2.0.0rc1", True),
        ("1.6.0", False),
        ("2026.11.7", False),
        ("2023.1.30.post1", False),
    ],
)
def test_is_prerelease(version, expected):
    assert release.is_prerelease(version) is expected


@pytest.mark.parametrize("version", ["1.6.0a1", "2.0.0a1"])
def test_check_release_prerelease_without_calver(version):
    changelog = f"# Changelog\n\n## {version} - 2026-11-14\n"
    assert release.check_release(version, version, 1, "", changelog, PUBLISHED) == []


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (("1.5.2", "1.5.1", 1, "2026.10.30", CHANGELOG_WITH_CALVER), "does not match"),
        (("1.5.1", "1.5.1", 1, "", CHANGELOG_WITH_CALVER), "calver must be set"),
        (("2.0.0", "2.0.0", 1, "2026.11.02", CHANGELOG_WITHOUT_CALVER), "must be empty"),
        (("1.5.1", "1.5.1", 1, "2026.10.13", CHANGELOG_WITH_CALVER), "not higher than"),
        (("1.5.1", "1.5.1", 1, "26.10.30", CHANGELOG_WITH_CALVER), "is not a YYYY.MM.DD"),
        (("1.5.1", "1.5.1", 1, "2026.10.31", CHANGELOG_WITH_CALVER), "also published as"),
        (("1.5.2", "1.5.2", 1, "2026.10.30", "## 1.5.2 - 2026-10-30\n"), "also published"),
        (("1.5.1", "1.5.1", 1, "2026.10.30", "# Changelog\n"), "no '## 1.5.1 ' heading"),
        (("1.6.0a1", "1.6.0a1", 1, "2026.11.14", CHANGELOG_PRERELEASE), "is a pre-release"),
    ],
)
def test_check_release_errors(args, message):
    errors = release.check_release(*args, PUBLISHED)
    assert any(message in error for error in errors), errors

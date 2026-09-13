"""Run project checks in locked uv environments."""

from pathlib import Path

import nox

nox.options.default_venv_backend = "uv"
nox.options.error_on_missing_interpreters = True
nox.options.sessions = [
    "unit_tests-3.13",
    "isort",
    "black",
    "pylint",
    "pydocstyle",
    "mypy",
    "darglint",
]


def sync(session, group, *args):
    """Install locked dependencies into the session environment."""
    session.run(
        "uv",
        "sync",
        "--locked",
        "--python",
        str(session.python),
        "--no-default-groups",
        "--group",
        group,
        "--no-editable",
        *args,
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )


@nox.session(python=["3.10", "3.11", "3.12", "3.13", "3.14"])
def unit_tests(session):
    """Run unit tests on supported Python versions."""
    sync(session, "test")
    package_path = session.run(
        "python",
        "-I",
        "-c",
        "import pathlib, nornir_scrapli; print(pathlib.Path(nornir_scrapli.__file__).parent)",
        silent=True,
    ).strip()
    session.run(
        "pytest",
        f"--cov={package_path}",
        "--cov-report=xml",
        "--cov-report=term",
        "tests/unit",
        *session.posargs,
    )


@nox.session(python="3.13")
def genie(session):
    """Exercise optional parsers on a compatible interpreter."""
    sync(session, "test", "--extra", "genie")
    session.run("python", "-c", "import genie.conf; import genie.libs.parser; import pyats")
    session.run("pytest", "tests/unit", *session.posargs)


@nox.session(python="3.13")
def isort(session):
    """Check import ordering."""
    sync(session, "lint")
    session.run("isort", "--check-only", ".")


@nox.session(python="3.13")
def black(session):
    """Check formatting."""
    sync(session, "lint")
    session.run("black", "--check", ".")


@nox.session(python="3.13")
def pylint(session):
    """Run pylint."""
    sync(session, "lint")
    session.run("pylint", "nornir_scrapli/")


@nox.session(python="3.13")
def pydocstyle(session):
    """Check docstrings."""
    sync(session, "lint")
    session.run("pydocstyle", "nornir_scrapli/")


@nox.session(python="3.13")
def mypy(session):
    """Check types against the minimum supported Python version."""
    sync(session, "lint")
    session.run("mypy", "--strict", "nornir_scrapli/")


@nox.session(python="3.13")
def darglint(session):
    """Check docstring signatures."""
    sync(session, "lint")
    for file in Path("nornir_scrapli").rglob("*.py"):
        session.run("darglint", str(file))


@nox.session(python="3.13")
def docs(session):
    """Build documentation in strict mode."""
    sync(session, "docs")
    session.run("mkdocs", "build", "--clean", "--strict")


@nox.session(python="3.13")
def build(session):
    """Build distributions with locked build tools."""
    sync(session, "build")
    session.run(
        "uv",
        "build",
        "--no-build-isolation",
        "--python",
        session.virtualenv.location,
        external=True,
    )

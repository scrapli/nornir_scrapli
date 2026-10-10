Contributing
=======

## Development setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) (CI uses uv 0.12.1),
clone the repository, and run `uv sync --locked`. uv uses Python 3.13 from
`.python-version` and downloads it if necessary. Supported runtime versions are Python
3.10–3.14.

Dependencies live in `pyproject.toml`; `uv.lock` records the resolved versions. Nox
creates isolated uv environments and syncs each session from the lockfile.

```shell
make test                 # Python 3.13 unit tests and coverage
make lint                 # ruff format, lint, and docstring checks, plus mypy
make format               # apply ruff formatting and safe lint fixes
make cov                  # HTML coverage
uv run --locked --only-group nox nox  # default checks on Python 3.13

# Full supported Python matrix
uv python install 3.10 3.11 3.12 3.13 3.14
uv run --locked --only-group nox nox -s unit_tests

# Documentation and distributions
uv run --locked --only-group nox nox -s docs build
```

`make test_docs` also checks links and requires the external `htmltest` executable.
`make docs` generates API documentation; `make deploy_docs` publishes the documentation.

### Optional Genie parsing

Genie/pyATS is excluded from the default environment. The optional extra currently
supports non-Windows Python 3.10–3.13, subject to upstream wheel availability for
your architecture. The dedicated Linux CI session uses Python 3.13 and checks imports
before running the tests:

```shell
uv run --locked --only-group nox nox -s genie
```

### Updating dependencies

Use `uv add --group test PACKAGE` (or the appropriate group), or edit the published
dependencies/extras in `pyproject.toml` and run `uv lock`. Preserve compatibility extras
when changing shared development tools. To upgrade a dependency within its declared
range, run `uv lock --upgrade-package PACKAGE`. Commit both the declarations and lockfile.
Regular CI uses locked dependencies; scheduled checks refresh their temporary lockfile
to test newer stable and prerelease dependencies.

Build distributions with `make build`. The Nox build session installs locked setuptools
and wheel versions and invokes `uv build --no-build-isolation`. Release CI publishes
these artifacts with `uv publish`.

Thanks for thinking about contributing to nornir_scrapli! Contributions are not expected, but are quite welcome.

Contributions of all kinds are welcomed -- typos, doc updates, adding examples, bug fixes, and feature adds.


Some notes on contributing:

- Please open an issue to discuss any bug fixes, feature adds, or really any thing that could result in a pull
 request. This allows us to all be on the same page, and could save everyone some extra work!
- Once we've discussed any changes, pull requests are of course welcome and very much appreciated!
  - All PRs should pass tests -- checkout the Makefile for some shortcuts for linting and testing.
  - Please include tests! Even simple/basic tests are better than nothing -- it helps make sure changes in the future
   don't break functionality or make things act in unexpected ways!

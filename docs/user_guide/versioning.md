# Versioning

nornir_scrapli uses [semantic versions](https://semver.org/) (`MAJOR.MINOR.PATCH`). The decision is recorded in
[issue #178](https://github.com/scrapli/nornir_scrapli/issues/178).

Releases up to `2026.10.13` have only a calendar version, such as `2025.01.30`. From `1.5.0`, each release of one
release line is also published on PyPI with a calendar version. For example, `1.5.1` can also be published as
`2026.10.30`. The two versions contain the same code.


## Release lines

The major version of nornir_scrapli matches the major version of scrapli it supports:

| nornir_scrapli | scrapli    | Version constraint | Also published with a calendar version | Branch                                     |
|----------------|------------|--------------------|----------------------------------------|--------------------------------------------|
| `1.x`          | scrapli v1 | `>=1,<2`           | Yes                                    | `main` (fixes), `develop-v1` (next minor)  |
| `2.x`          | scrapli v2 | `>=2,<3`           | Not yet                                | `develop`                                  |

- `1.x` starts at `1.5.0`, with the same code as `2026.10.13`. It starts at `1.5.0` and not `1.0.0` because the
  project has published 27 releases since 2020 ([PyPI history](https://pypi.org/project/nornir-scrapli/#history)).
- `2.x` starts at `2.0.0`. scrapli v2 changes the inventory `extras` and the task arguments, so inventories and
  scripts written for `1.x` need changes. The `cfg_*` tasks are not available in `2.x`, because scrapli_cfg has no release
  for scrapli v2.

The two lines receive releases in parallel for a period. The date when `1.x` is retired is not decided yet.


## Selecting a release line

Set a version constraint for the line you use, for example in `requirements.txt` or `pyproject.toml`:

```
# scrapli v1
nornir_scrapli>=1,<2

# scrapli v2
nornir_scrapli>=2,<3
```

Always set one of these constraints, including with `pip install --upgrade`.


## Calendar versions

Under [PEP 440](https://packaging.python.org/en/latest/specifications/version-specifiers/), every calendar version
is higher than every `1.x` and `2.x` version. For this reason, only one release line is published with calendar
versions at a time. Today this is `1.x`. As a result:

- `pip install nornir_scrapli` without a constraint, or with a calendar-version constraint such as `>=2024.1.30`,
  installs the latest calendar version, which is the latest `1.x` release. It uses scrapli v1.
- `pip install --upgrade nornir_scrapli` without a constraint moves a `2.x` installation to the latest calendar
  version, which uses scrapli v1.

The calendar version of a release is its publication date in the format `YYYY.MM.DD`. A second release on the same
day has the format `YYYY.MM.DD.N`, such as `2026.10.30.1`. When nornir_scrapli is installed from a calendar
version, `nornir_scrapli.__version__` returns the calendar version.

### Finding the semantic version of a calendar version

Each release names both versions:

- In [CHANGELOG.md](https://github.com/scrapli/nornir_scrapli/blob/main/CHANGELOG.md), the heading of the release
  names the calendar version, for example `## 1.5.1 (also published as 2026.10.30) - 2026-10-30`.
- The [GitHub release](https://github.com/scrapli/nornir_scrapli/releases) of the semantic version starts with the
  line `Also published on PyPI as 2026.10.30`.
- The git tag of the calendar version, such as `2026.10.30`, points to the same commit as the semantic-version tag.

### Moving calendar versions to `2.x`

Calendar versions will later follow `2.x` instead of `1.x`. The date is not decided yet. From that release,
installations without a constraint or with a calendar-version constraint move from scrapli v1 to scrapli v2. To stay on
scrapli v1, set the constraint `>=1,<2` before that date. The changelog will announce the change as a breaking change.


## Branches

- `main` holds bug fixes for `1.x`. `1.x` releases are tagged from `main`.
- `develop-v1` holds changes for the next `1.x` minor release. It is merged into `main` for that release.
- `develop` holds the `2.x` line. `2.x` releases are tagged from `develop`.

When `1.x` is retired, `main` holds bug fixes for `2.x`.


## Publishing a release

This section is for maintainers. The `[tool.nornir_scrapli.release]` table in `pyproject.toml` controls the calendar
version:

- `calver-line` is the major version whose releases are also published with a calendar version. It is `1` today.
- `calver` is the calendar version of the next release on the branch. It must be set for a release of the
  `calver-line` major version, and empty for any other release.

To publish a release:

1. In a pull request against the release branch:
    - Set `__version__` in `nornir_scrapli/__init__.py` to the semantic version, such as `1.5.1`.
    - Set `calver` in `pyproject.toml` to the planned publication date, such as `2026.10.30`. Leave it empty for a
      release of another major version.
    - Write the changelog heading with both versions, such as
      `## 1.5.1 (also published as 2026.10.30) - 2026-10-30`, or with the semantic version only when `calver` is empty.
2. Run `nox -s release_check -- --tag 1.5.1 --pypi`. It checks that:
    - The tag matches `__version__`.
    - `calver` is set or empty as required, and is higher than every calendar version already on PyPI.
    - The changelog heading names the calendar version.
3. Merge the pull request and create the GitHub release with the tag `1.5.1`.

The `Publish` workflow then runs the same check, and stops if it fails. It publishes the semantic version and then
the calendar version, tags the calendar version, and adds the `Also published on PyPI as` line to the GitHub release.
Both uploads skip files that are already on PyPI, so the workflow can be run again after a failure.

To move calendar versions to `2.x`, set `calver-line = 2` on every release branch.

# Versioning

nornir_scrapli uses [semantic versions](https://semver.org/) (`MAJOR.MINOR.PATCH`). The decision is recorded in
[issue #178](https://github.com/scrapli/nornir_scrapli/issues/178).

`2026.10.13` is the last release with a calendar version. Releases before it use calendar versions, such as
`2025.01.30`.


## Release lines

The major version of nornir_scrapli matches the major version of scrapli it supports:

| nornir_scrapli | scrapli    | Version constraint | Branch                                     |
|----------------|------------|--------------------|--------------------------------------------|
| `1.x`          | scrapli v1 | `>=1,<2`           | `main` (fixes), `develop-v1` (next minor)  |
| `2.x`          | scrapli v2 | `>=2,<3`           | `develop`                                  |

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


## Installing without a semantic-version constraint

Under [PEP 440](https://packaging.python.org/en/latest/specifications/version-specifiers/), `2026.10.13` is higher
than every `1.x` and `2.x` version. As a result:

- `pip install nornir_scrapli`, or a calendar-version constraint such as `>=2024.1.30`, installs `2026.10.13`.
  That release receives no further fixes.
- `pip install --upgrade nornir_scrapli` without a constraint moves a `2.x` installation to `2026.10.13`, which
  uses scrapli v1.

To receive fixes, replace calendar-version constraints with `>=1,<2` (scrapli v1) or `>=2,<3` (scrapli v2).


## Branches

- `main` holds bug fixes for `1.x`. `1.x` releases are tagged from `main`.
- `develop-v1` holds changes for the next `1.x` minor release. It is merged into `main` for that release.
- `develop` holds the `2.x` line. `2.x` releases are tagged from `develop`.

When `1.x` is retired, `main` holds bug fixes for `2.x`.

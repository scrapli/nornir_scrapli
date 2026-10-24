# Changelog

This file lists the changes in each nornir_scrapli release, starting with release 2026.10.13. For earlier releases, view the [GitHub releases page](https://github.com/scrapli/nornir_scrapli/releases).

## 1.5.0 - Unreleased

[Full list of commits since 2026.10.13](https://github.com/scrapli/nornir_scrapli/compare/2026.10.13...1.5.0)

### Breaking changes

- nornir_scrapli uses semantic versions instead of calendar versions. `1.5.0` starts the `1.x` line, for scrapli v1, and has the same package code as `2026.10.13`. The `2.x` line, for scrapli v2, starts at `2.0.0`. Select a line with the constraint `>=1,<2` or `>=2,<3`. Without a constraint, or with a calendar-version constraint such as `>=2024.1.30`, pip installs `2026.10.13`, which receives no further fixes, because `2026.10.13` is higher than every `1.x` and `2.x` version. For details, view the [versioning docs](https://scrapli.github.io/nornir_scrapli/user_guide/versioning). ([#178](https://github.com/scrapli/nornir_scrapli/issues/178), [#184](https://github.com/scrapli/nornir_scrapli/pull/184))

### Changed

- The package metadata declares the license as the SPDX expression `MIT`, and no longer has the `License :: OSI Approved :: MIT License` classifier. ([#177](https://github.com/scrapli/nornir_scrapli/pull/177))

### Development

- hatchling replaces setuptools as the build backend. The `build` dependency group is removed. ([#177](https://github.com/scrapli/nornir_scrapli/pull/177))
- Functional tests connect over SSH to FakeNOS devices on five platforms and run the core tasks. CI runs them on every commit, after the weekly prerelease dependency upgrades on Ubuntu, and before publishing a release. ([#175](https://github.com/scrapli/nornir_scrapli/pull/175))
- The locked versions of aiohttp, certifi, gitpython and virtualenv are updated in `uv.lock`. ([#180](https://github.com/scrapli/nornir_scrapli/pull/180), [#181](https://github.com/scrapli/nornir_scrapli/pull/181), [#182](https://github.com/scrapli/nornir_scrapli/pull/182), [#183](https://github.com/scrapli/nornir_scrapli/pull/183))

## 2026.10.13 - 2026-10-13

[Full list of commits since 2025.01.30](https://github.com/scrapli/nornir_scrapli/compare/2025.01.30...2026.10.13)

### Breaking changes

- nornir_scrapli no longer installs on Python 3.9. The minimum Python version is now 3.10. ([#151](https://github.com/scrapli/nornir_scrapli/pull/151))
- nornir_scrapli now requires scrapli `>=2022.01.30,<2026.2.21`. This excludes scrapli 2.0 (released as `2026.10.3`) and its pre-releases (`2026.2.22rc1` and later), because nornir_scrapli does not support scrapli 2.0 yet. The last supported scrapli release is `2026.2.20`. ([#171](https://github.com/scrapli/nornir_scrapli/pull/171))

### Added

- Python 3.14 support. The test suite runs on Python 3.10 to 3.14, on Linux and macOS. ([#151](https://github.com/scrapli/nornir_scrapli/pull/151))
- The `genie` extra now installs genie and pyats on Python 3.13 and 3.14. Before this release, the extra skipped them on Python 3.13 and later. ([#151](https://github.com/scrapli/nornir_scrapli/pull/151))

### Changed

- Dependencies are declared in `pyproject.toml`. The `requirements*.txt` files are removed. ([#151](https://github.com/scrapli/nornir_scrapli/pull/151))
- The `docs` extra now accepts `mkdocstrings[python]` versions before 2.0, instead of versions before 1.0. ([#165](https://github.com/scrapli/nornir_scrapli/pull/165))

### Development

- Development and CI environments use uv and a `uv.lock` lockfile. Nox sessions install their dependencies from that lockfile. ([#151](https://github.com/scrapli/nornir_scrapli/pull/151))
- ruff replaces black, isort, pylint, pydocstyle and darglint for formatting and linting. mypy still runs the type checks. ([#152](https://github.com/scrapli/nornir_scrapli/pull/152))
- GitHub Actions are updated to their latest supported releases. ([#151](https://github.com/scrapli/nornir_scrapli/pull/151), [#160](https://github.com/scrapli/nornir_scrapli/pull/160))
- direnv files are added to `.gitignore`. ([#154](https://github.com/scrapli/nornir_scrapli/pull/154))

# Changelog

This file lists the changes in each nornir_scrapli release, starting with release 2026.10.13. For earlier releases, view the [GitHub releases page](https://github.com/scrapli/nornir_scrapli/releases).

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

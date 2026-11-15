# Changelog

This file lists the changes in each nornir_scrapli release, starting with release 2026.10.13. For earlier releases, view the [GitHub releases page](https://github.com/scrapli/nornir_scrapli/releases).

From 1.5.0, the heading of a release that is also published with a calendar version names that version, for example `## 1.5.1 (also published as 2026.10.30) - 2026-10-30`. Pre-releases, such as `1.6.0a1`, have no calendar version.

## 1.6.0a1 - 2026-11-15

[Full list of commits since 1.5.0](https://github.com/scrapli/nornir_scrapli/compare/1.5.0...1.6.0a1)

1.6.0a1 is a pre-release of the `1.x` line, for scrapli v1. With it, you can run the Scrapli CLI and Scrapli-Cfg tasks as coroutines on the Nornir `AsyncioRunner`, with the same `scrapli` and `scrapli_cfg` connection names and the same inventory as synchronous runs. It requires Nornir 3.7.0a1, the first Nornir release with the asyncio runner. pip installs this pre-release only when you request it, with `pip install "nornir-scrapli[asyncio]==1.6.0a1"` or `pip install --pre "nornir-scrapli[asyncio]>=1,<2"`. It is not published with a calendar version, so `pip install nornir-scrapli` without a constraint still installs `2026.11.7`, the calendar version of 1.5.0. ([#179](https://github.com/scrapli/nornir_scrapli/pull/179))

### Breaking changes

- nornir_scrapli requires `nornir>=3.7.0a1`. Nornir 3.7.0a1 is the first Nornir release with the asyncio runner and the capability-aware connection plugins ([nornir-automation/nornir#1111](https://github.com/nornir-automation/nornir/pull/1111)). ([#179](https://github.com/scrapli/nornir_scrapli/pull/179))
- The `scrapli` and `scrapli_cfg` connection plugins are registered in the `nornir.plugins.capability_connections` entry point group instead of `nornir.plugins.connections`. `scrapli_netconf` stays in `nornir.plugins.connections`. `InitNornir` finds the plugins with no change. If you build a `Nornir` object without `InitNornir`, register `ScrapliCore` and `ScrapliConfig` with `CapabilityConnectionPluginRegister`. ([#179](https://github.com/scrapli/nornir_scrapli/pull/179))

### Added

- Run the Scrapli CLI and Scrapli-Cfg tasks as coroutines with the tasks in `nornir_scrapli.async_tasks`. They take the same arguments and return the same results as the synchronous tasks in `nornir_scrapli.tasks`, which do not change. NETCONF tasks stay synchronous. ([#179](https://github.com/scrapli/nornir_scrapli/pull/179)) The async tasks:
  - `get_prompt`, `send_command`, `send_commands`, `send_commands_from_file` and `send_interactive`
  - `send_config`, `send_configs` and `send_configs_from_file`
  - `cfg_get_version`, `cfg_get_config`, `cfg_load_config`, `cfg_diff_config`, `cfg_commit_config` and `cfg_abort_config`
- Install the `asyncssh` transport with the `asyncio` extra: `pip install "nornir-scrapli[asyncio]==1.6.0a1"`. When `transport` is not set in the inventory extras, a connection opened from a coroutine task uses `asyncssh`, and a connection opened from a synchronous task uses `system`. ([#179](https://github.com/scrapli/nornir_scrapli/pull/179))
- Open the `scrapli` and `scrapli_cfg` connections from synchronous tasks or from coroutine tasks. Nornir binds an open connection to the mode that opened it, and using it from the other mode raises Nornir's `ConnectionModeMismatchError`. To switch modes, close the connection first. For examples, and for how to close the connections of hosts that Nornir cancelled or timed out, view the [asyncio docs](https://github.com/scrapli/nornir_scrapli/blob/1.6.0a1/docs/user_guide/asyncio.md). ([#179](https://github.com/scrapli/nornir_scrapli/pull/179))

### Development

- `scripts/release.py check` requires an empty `calver` for a pre-release, such as `1.6.0a1`, and the `Publish` workflow then publishes the semantic version only. ([#179](https://github.com/scrapli/nornir_scrapli/pull/179))
- The test dependencies require pytest `>=8.2.0` and add pytest-asyncio in strict mode. The functional tests run the async tasks against FakeNOS devices over SSH. ([#179](https://github.com/scrapli/nornir_scrapli/pull/179))

## 1.5.0 (also published as 2026.11.07) - 2026-11-07

[Full list of commits since 2026.10.13](https://github.com/scrapli/nornir_scrapli/compare/2026.10.13...1.5.0)

### Breaking changes

- nornir_scrapli uses semantic versions instead of calendar versions. `1.5.0` starts the `1.x` line, for scrapli v1, and has the same package code as `2026.10.13`. The `2.x` line, for scrapli v2, starts at `2.0.0`. Select a line with the constraint `>=1,<2` or `>=2,<3`. Each `1.x` release is also published with a calendar version, its publication date, and the heading of the release in this changelog names it. Without a constraint, or with a calendar-version constraint such as `>=2024.1.30`, pip installs the latest calendar version, which uses scrapli v1, because every calendar version is higher than every `1.x` and `2.x` version. Calendar versions will later follow `2.x` instead of `1.x`; the date is not decided yet. For details, view the [versioning docs](https://scrapli.github.io/nornir_scrapli/user_guide/versioning). ([#178](https://github.com/scrapli/nornir_scrapli/issues/178), [#184](https://github.com/scrapli/nornir_scrapli/pull/184))

### Changed

- The package metadata declares the license as the SPDX expression `MIT`, and no longer has the `License :: OSI Approved :: MIT License` classifier. ([#177](https://github.com/scrapli/nornir_scrapli/pull/177))

### Development

- The `Publish` workflow publishes each release of the `1.x` line twice on PyPI: with its semantic version, and with the calendar version set in `[tool.nornir_scrapli.release] calver` in `pyproject.toml`. It then pushes a git tag for the calendar version and adds the calendar version to the GitHub release notes. Before publishing, `scripts/release.py` checks that the release tag matches `__version__`, that the calendar version is higher than every calendar version on PyPI, and that the changelog heading names the calendar version. Maintainers run the same check with `nox -s release_check`. ([#184](https://github.com/scrapli/nornir_scrapli/pull/184))
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

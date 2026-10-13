# Async Scrapli Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run command and configuration tasks natively through Nornir's asyncio runner using single, mode-bound connection plugins.

**Architecture:** Extend the existing CLI and configuration plugins with capability reporting and async lifecycle operations. Shared task acquisition helpers enforce the established mode on cache hits. Async task counterparts preserve raw drivers and existing ScrapliResult processing.

**Tech Stack:** Python >=3.10, Nornir async branch, Scrapli, Scrapli-Cfg, asyncssh, pytest, uv/nox.

**Spec:** `docs/superpowers/specs/2026-10-13-async-design.md`

## Global Constraints

- One registration per name in `nornir.plugins.capability_connections`.
- Use `scrapli` and `scrapli_cfg` in both modes.
- No automatic conversion of device operations between sync and async.
- Preserve sync task signatures and result semantics.
- No private Nornir cache mutation.
- No commits or pushes unless requested by the user.

## Review Focus

- Opposite-mode cache hits must fail before a device operation.
- Configuration-wrapper preparation failures must not close the shared transport.
- Failed/cancelled opening must not leak a partially opened driver.
- Failed closing must preserve state for retry.
- Inventory extras must not be mutated when wrapping a shared connection.

---

### Task 1: Branch environment and discovery

**Files:** `pyproject.toml`, `uv.lock`, `tests/unit/conftest.py`.

**Interfaces:** Nornir's `CapabilityConnectionPluginRegister`, public host async APIs, and `AsyncioRunner` at the pinned commit.

- [x] Pin the runtime dependency and add the optional asyncssh extra.
- [x] Move CLI/cfg entry points into the capability group; retain NETCONF's legacy entry point.
- [x] Update test inventory selection to `SimpleInventory` supported by the branch.
- [x] Verify installed discovery and the existing regression baseline.

### Task 2: Mode-bound connections

**Files:** `connection.py`, `connection_mode.py`, `exceptions.py`, `tests/unit/test_async_connection.py`.

**Interfaces:** `ScrapliCore.get_connection(task)`, `ScrapliCore.aget_connection(task)`, `ScrapliConfig.get_connection(task)`, `ScrapliConfig.aget_connection(task)` return guarded raw drivers/wrappers. `open`/`aopen` retain Nornir's parameter contract; `get_capabilities` returns both modes.

- [x] Write and run failing tests for both guards, lifecycle retry, failed/cancelled opening, and wrapper ownership.
- [x] Implement lifecycle state and async CLI opening with `AsyncScrapli`/`AsyncGenericDriver`.
- [x] Implement public-API cfg acquisition and preparation with `AsyncScrapliCfg`.
- [x] Route sync CLI tasks through guarded acquisition.
- [x] Run connection tests and the existing suite.

### Task 3: Native async tasks

**Files:** `async_tasks/__init__.py`, `async_tasks/core.py`, `async_tasks/cfg.py`, `tests/unit/test_async_tasks.py`.

**Interfaces:** Explicit `async def` counterparts of all eight CLI and six cfg task signatures, importing the shared guarded acquisition interfaces from Task 2.

- [x] Write and run failing runner/subtask tests for response parity, config dry-run, cfg candidate/diff/commit/abort, and wrong-mode task use.
- [x] Implement native awaited device operations; offload file reading, not device I/O.
- [x] Run task tests and full unit regression suite.

### Task 4: Integration and documentation

**Files:** `tests/functional/test_async_tasks.py`, functional fixtures, `README.md`, `docs/user_guide/asyncio.md`, `examples/asyncio_tasks.py`, CI/nox as necessary.

- [x] Write and run a real SSH command/config test through AsyncioRunner with cleanup.
- [x] Document shared inventory names, transport installation, mode guards, raw-driver limits, and upstream branch requirement.
- [x] Run unit/functional tests, lint, strict mypy, docs, and distribution builds.
- [x] Review the complete diff and report results and integration limitations.

## Execution record

- Initial baseline: 44 unit tests passed, 4 optional-parser tests skipped.
- Connection tests: 8 failures for missing async/guard APIs, then green after implementation.
- Async task tests: 22 failures for missing async tasks, then green after implementation.
- Real SSH verification found disconnected-transport logout-hook failures; two
  cleanup regression tests failed before the fix and passed after it.
- Independent final review found stale cached cfg wrappers after CLI reopening;
  all four sync/async reopening combinations failed before the identity guard
  and passed after it. No other critical, important, or minor findings.
- Final combined suite: `uv run --locked --group functional pytest tests -q --tb=short`
  — 129 passed, 4 skipped. Warnings originate from Nornir logging and synchronous
  Scrapli's system-transport forkpty use in the existing SSH lab.
- Installed-package nox unit sessions on Python 3.10, 3.11, 3.12, 3.13, and 3.14
  — 80 passed, 4 skipped on each interpreter.
- Nox ruff, strict mypy, strict docs, and wheel/sdist builds — all passed.

### Implementation rulings

- Pin the runtime Git dependency, rather than only a uv source: the released
  package and experimental branch both report Nornir 3.6.0, so a version floor
  could install an incompatible core. This requires Git/source installation until
  upstream releases the APIs.
- Keep raw driver types and enforce mode at task acquisition and plugin lifecycle
  boundaries. Bare Nornir getters and synchronous cache-removing cleanup need
  upstream preflight support; custom tasks should use the guarded helpers.
- Reject stale cfg wrappers instead of automatically replacing them, to preserve
  visibility of any candidate workflow tied to the old driver.

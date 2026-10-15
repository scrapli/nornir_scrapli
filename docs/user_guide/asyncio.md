# Asyncio usage

Nornir Scrapli provides native coroutine tasks for commands, CLI configuration,
and Scrapli-Cfg workflows. Synchronous imports remain in `nornir_scrapli.tasks`;
async imports are in `nornir_scrapli.async_tasks`.

## Install

This implementation targets Nornir's experimental `dga/feat-async-spplb` branch
at commit `01bac1d326092489d688a72cd9d19569c6e1688a` from
[PR #1111](https://github.com/nornir-automation/nornir/pull/1111). The checkout pins that Git
dependency because released Nornir 3.6.0 does not expose the capability registry
or async runner, although the experimental branch reports the same version.

```bash
pip install ".[asyncio]"
```

For development, `uv sync --locked --group test` includes the async transport.

## Configure the runner and connections

```yaml
runner:
  plugin: asyncio
  options:
    num_workers: 100
inventory:
  plugin: SimpleInventory
  options:
    host_file: inventory/hosts.yaml
    group_file: inventory/groups.yaml
    defaults_file: inventory/defaults.yaml
```

Use the existing connection names in inventory:

```yaml
# inventory/defaults.yaml
username: automation
password: your-password
connection_options:
  scrapli:
    extras:
      auth_strict_key: true
  scrapli_cfg:
    extras:
      ignore_version: false
```

When `transport` is omitted, sync opening uses Scrapli's `system` default and
async opening uses `asyncssh`. An explicit transport must support the selected
mode; `system` and `paramiko` cannot be used for async opening. Custom open/close
callbacks must also match the chosen Scrapli driver's execution mode.

Each plugin is registered once in `nornir.plugins.capability_connections`:
`ScrapliCore` under `scrapli`, and `ScrapliConfig` under `scrapli_cfg`.
Do not also register those names in the legacy registry. When constructing
`Nornir` directly instead of using `InitNornir`, register these classes with
`CapabilityConnectionPluginRegister` first.

## Run commands and configuration

```python
import asyncio

from nornir import InitNornir
from nornir_scrapli.async_tasks import send_command, send_configs


async def configure(task):
    await task.arun(task=send_command, command="show version")
    return await task.arun(
        task=send_configs,
        configs=["interface Loopback100", "description managed-by-nornir"],
        dry_run=True,
    )


async def main():
    async with InitNornir(config_file="config.yaml") as nr:
        return await nr.arun(task=configure)


results = asyncio.run(main())
```

The async tasks have the same parameters and result semantics as the sync tasks:

- `get_prompt`
- `send_command`, `send_commands`, `send_commands_from_file`
- `send_interactive`
- `send_config`, `send_configs`, `send_configs_from_file`
- `cfg_get_version`, `cfg_get_config`, `cfg_load_config`, `cfg_diff_config`,
  `cfg_commit_config`, `cfg_abort_config`

CLI configuration dry-run verifies configuration-mode access without sending
configuration. An explicit `dry_run` overrides Nornir's global setting. Command
and configuration file loading is offloaded to a thread; device I/O remains
native asynchronous I/O.

`ScrapliResult` retains the original response in `scrapli_response`. Prompt,
interactive, and cfg-version tasks retain their existing plain `Result` behavior.
NETCONF tasks remain synchronous in this implementation.

## Scrapli-Cfg workflows

```python
from nornir_scrapli.async_tasks import (
    cfg_abort_config,
    cfg_commit_config,
    cfg_diff_config,
    cfg_load_config,
)


async def candidate_workflow(task, config, apply=False):
    await task.arun(task=cfg_load_config, config=config, replace=False)
    diff = await task.arun(task=cfg_diff_config)
    if apply:
        await task.arun(task=cfg_commit_config)
    else:
        await task.arun(task=cfg_abort_config)
    return diff
```

The configuration wrapper acquires and reuses the host's `scrapli` driver and
awaits preparation once. It forces `dedicated_connection=False`; closing the
wrapper does not close the CLI driver. Candidate loading and diffing report
`changed=False`; committing reports `changed=True`. Like the synchronous cfg
tasks, cfg commit does not implicitly honor global dry-run: choose commit or
abort explicitly in the workflow.

## Connection execution modes and switching

Each plugin declares both opening capabilities, while Nornir binds an established
connection to the execution mode that opened it. CLI tasks and custom tasks use
Nornir's public getters directly:

```python
driver = task.host.get_connection("scrapli", task.nornir.config)  # synchronous task
# In a coroutine task:
driver = await task.host.aget_connection("scrapli", task.nornir.config)
mode = task.host.connection_mode("scrapli")  # "sync", "asyncio", or None
```

Nornir checks both fresh and cached access. Opposite-mode access raises
`nornir.core.exceptions.ConnectionModeMismatchError` before a device operation.
Synchronous host cleanup of an asyncio-bound connection raises the same error and
leaves the cached connection available for asynchronous cleanup. This package does
not keep a second execution-mode field or implement a parallel mode guard.

To switch execution modes, close the cfg wrapper first, then its CLI driver:

```python
await host.aclose_connection("scrapli_cfg")  # if a wrapper was opened
await host.aclose_connection("scrapli")
```

These asynchronous host cleanup methods work for sync-bound connections too:
Nornir selects the matching plugin `close` or `aclose` method. For a host with only
synchronous connections, synchronous `host.close_connection` is also available.
Once closed, `host.connection_mode(name)` returns `None`, and that name can reopen
in either mode. Ensure any explicit transport option matches the new mode and
serialize operations for each host.

Configuration tasks retain `ScrapliConfig.get_connection(task)` and
`await ScrapliConfig.aget_connection(task)` for preparing and validating the shared
configuration wrapper. Their mode checks are performed by Nornir's getters.

If the CLI driver is closed or replaced while its configuration wrapper remains
cached, configuration-task acquisition rejects that stale wrapper. Close the
wrapper before starting a new candidate workflow on the replacement driver.

Raw Scrapli driver operations remain Scrapli's API; retaining their concrete types
is necessary for Scrapli-Cfg platform selection. Use Nornir's host lifecycle APIs
for managed connections rather than calling plugin lifecycle methods directly.

## Cleanup and cancellation

Prefer `async with nr:` to clean up connections before the caller's loop exits.
For explicit cleanup, include failed hosts:

```python
await nr.aclose_connections(on_good=True, on_failed=True)
```

An unsuccessful or cancelled async opening reclaims partial resources before
propagating the original error. Async close is idempotent, and a failed close
retains plugin state for retry. Already-disconnected drivers skip device logout
hooks while still closing channel resources.

Nornir's asynchronous cleanup handles mixed inventories, including the legacy
sync-only NETCONF plugin. The plugin still owns cleanup of resources acquired before
an unsuccessful async open because Nornir does not cache unsuccessful opens. Stale
Scrapli-Cfg wrappers are also plugin-specific and remain rejected until closed.
Do not perform concurrent task operations or cleanup on the same host connection.

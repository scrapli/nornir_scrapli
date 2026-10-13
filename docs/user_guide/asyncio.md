# Asyncio usage

Nornir Scrapli provides native coroutine tasks for commands, CLI configuration,
and Scrapli-Cfg workflows. Synchronous imports remain in `nornir_scrapli.tasks`;
async imports are in `nornir_scrapli.async_tasks`.

## Install

This implementation targets Nornir's experimental `dga/feat-async-spplb` branch
at commit `f62f07aab4a1285c4c1e918151c3476472b15a84`. The checkout pins that Git
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

## Mode guards and switching

A plugin supports both opening modes, but an established connection has one
active mode. Tasks acquire the driver through `ScrapliCore.get_connection(task)`
or `await ScrapliCore.aget_connection(task)`. Configuration tasks use the matching
`ScrapliConfig` helpers. These helpers validate cache hits and reject the opposite
mode with `NornirScrapliConnectionModeError` before a device operation.

Plugin `open`/`aopen` and `close`/`aclose` operations also enforce the active mode.
To change modes, close the cfg wrapper first, then its CLI driver, using matching
host lifecycle operations. For an async connection:

```python
await host.aclose_connection("scrapli_cfg")  # if a wrapper was opened
await host.aclose_connection("scrapli")
```

For a sync connection, use `host.close_connection` instead. Once closed, the
same connection name can be reopened in the other mode. Ensure any explicit
transport option matches the new mode, and serialize operations for each host.

If the CLI driver is closed or replaced while its configuration wrapper remains
cached, configuration-task acquisition rejects that stale wrapper. Close the
wrapper before starting a new candidate workflow on the replacement driver.

### Boundaries of the experimental Nornir contract

The upstream dual-capability protocol currently promises cross-mode reuse of an
established transport. Scrapli has distinct sync and async drivers, so this
package implements a mode-bound policy instead. The capability declaration
describes supported opening modes, not interchangeable established drivers.

Nornir's bare `host.get_connection` and `host.aget_connection` currently return
opposite-mode cache hits without inspecting this package's active mode. Custom
tasks should use the guarded helpers. Direct calls on a raw Scrapli driver are
outside these guards; retaining the raw driver's concrete type is necessary for
Scrapli-Cfg platform selection.

The upstream synchronous `host.close_connection` removes its cache entry before
calling the plugin's `close`. Calling it on an async connection raises the mode
error but also removes Nornir's cache entry. Use the matching cleanup method;
if this mistake occurs, retain the plugin reference and await `plugin.aclose()`
to reclaim its transport. Host-level preflight guards require an upstream change.

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

Mixed-mode connections need matching per-host cleanup; a dual-capability plugin
opened synchronously rejects `aclose` as well as async task operations. Do not
perform concurrent task operations or cleanup on the same host connection.

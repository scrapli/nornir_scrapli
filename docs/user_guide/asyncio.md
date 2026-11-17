# Asyncio Usage

nornir_scrapli can run every task on Nornir's asyncio runner. Each host's device I/O
then runs as a coroutine on one event loop instead of in a thread per host.

!!! warning
    Asyncio support requires Nornir 3.7.0a1 or later, the first Nornir release with the
    asyncio runner and capability-aware connection plugins
    ([nornir-automation/nornir#1111](https://github.com/nornir-automation/nornir/pull/1111)).
    Nornir 3.7.0a1 is a pre-release, and its new APIs can still change. `uv` selects a
    pre-release of a transitive dependency only when asked: add `--prerelease=allow`, or
    add `nornir>=3.7.0a1` to the requirements of your own project.


## Configure the runner

Select the `asyncio` runner in the Nornir configuration:

```yaml
runner:
  plugin: asyncio
  options:
    num_workers: 20
```

`num_workers` limits how many hosts run at the same time. You can also set the runner
in code with `nr.with_runner(AsyncioRunner(num_workers=20))`, importing `AsyncioRunner`
from `nornir.plugins.runners`.

Inventory and connection options are the same as for the sync tasks. The `scrapli`
and `scrapli_netconf` connections support both modes, and scrapli v2 uses the same
transports (`bin`, `ssh2`, `telnet`) in both modes, so no inventory change is needed.


## Run async tasks

The async tasks live in `nornir_scrapli.async_tasks`. They have the same names,
parameters and results as the tasks in `nornir_scrapli.tasks`. Run them with
`await nr.arun(...)`, and run subtasks with `await task.arun(...)`:

```python
import asyncio

from nornir import AInitNornir
from nornir.core.task import Result, Task
from nornir_scrapli.async_tasks import get_prompt, send_command


async def show_version(task: Task) -> Result:
    prompt = await task.arun(get_prompt)
    await task.arun(send_command, command="show version")
    return Result(host=task.host, result=prompt.result)


async def main() -> None:
    nr = await AInitNornir(config_file="config.yaml")
    async with nr:
        results = await nr.arun(task=show_version)
    print(results["iosxe1"][2].result)


asyncio.run(main())
```

`AInitNornir` takes the same arguments as `InitNornir` and returns the same `Nornir`
object. It loads the inventory without blocking the event loop. `InitNornir` also works
in an async application, but it blocks the event loop while the inventory loads.

Leaving the `async with` block closes every connection that is still open. Without
it, call `await nr.aclose_connections(on_good=True, on_failed=True)`.

Nornir rejects an async task passed to `nr.run` and a sync task passed to `nr.arun`.
Inside an async task, `task.run(sync_task)` still works, but it blocks the event loop
until it returns.

See [examples/asyncio_usage](https://github.com/scrapli/nornir_scrapli/tree/main/examples/asyncio_usage)
for a complete example.


## A connection stays in the mode that opened it

Nornir binds each open connection to the mode that opened it. When an async task has
opened the `scrapli` connection of a host, a sync task that uses the same connection
fails with `ConnectionModeMismatchError`, and the reverse is also true.
`host.connection_mode("scrapli")` returns `"sync"`, `"asyncio"` or `None`.

To switch modes, close the connection first: `await host.aclose_connection("scrapli")`
closes a connection opened in either mode. The next task then opens a new connection
in its own mode.


Subtasks of one host that run at the same time, for example with `asyncio.gather`, share
one connection: when two of them request the `scrapli` connection while it is opening,
Nornir opens it once and gives the same connection to both. A scrapli connection runs
one operation at a time, so send the commands of one host one after the other.


## Set time limits and cancel runs

The asyncio runner accepts two time limits, in seconds: `per_host_timeout` for each host
and `timeout` for the whole run.

```yaml
runner:
  plugin: asyncio
  options:
    num_workers: 20
    per_host_timeout: 60
    timeout: 600
```

A host that exceeds a limit stops at the scrapli call that its task is awaiting. Its
result is failed and its exception is `TaskTimeoutError`. The other hosts are not
affected. `await nr.asubmit(...)` returns a handle that can cancel a run; the result of
each cancelled host has the exception `TaskCancelledError`. Both exceptions are in
`nornir.core.exceptions` and are subclasses of `BaseException`, not of `Exception`.

When a time limit or a cancellation stops a task:

- The connection stays open in Nornir, bound to asyncio mode. The device can still be
  processing the interrupted operation, so close the connection with
  `await host.aclose_connection("scrapli")` before you use the host again. Leaving the
  `async with` block also closes it.
- A task stopped while the connection is opening closes the partly opened scrapli
  driver. No connection is left open in Nornir.
- A configuration dry run still attempts to return to the starting mode.
- A `netconf_edit_config` dry run still attempts to discard the candidate datastore.

The time limits are separate from the scrapli `operation_timeout_ns` task parameter,
which limits one scrapli operation and raises a scrapli exception.

The sync tasks in `nornir_scrapli.tasks` accept the same runner options on the threaded
and serial runners. Nornir checks the limits only at the start of each subtask and at
`task.checkpoint()` calls, so a sync scrapli call that has started always finishes.


## Behavior that differs from what you might expect

- **Configuration dry runs** behave as in the sync tasks. `send_config`, `send_configs`
  and `send_configs_from_file` use `dry_run`, or the global Nornir dry-run setting when
  `dry_run` is not set. A dry run enters and leaves configuration mode, sends no
  configuration and returns a result with `result=None` and `changed=False`.
- **`netconf_edit_config` with a dry run** requires the candidate datastore as the
  target, as in the sync task. It sends the edit and then discards the candidate
  datastore. With any other target it fails before sending anything.
- **`netconf_capabilities`** sends no RPC. It returns the capabilities that the device
  sent when the session opened, because scrapli v2 stores them during the open.
- **`send_interactive`** reads the output with an async callback. Writing each input
  uses scrapli's sync `write_and_return`, because scrapli v2 has no async version of
  it. The write passes the input to the scrapli driver and does not wait for a reply.
- **Failed or cancelled opens** close the partly opened scrapli driver before the error
  reaches the task. A failed close leaves the connection open in Nornir, so the close
  can be retried.

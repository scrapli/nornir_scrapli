# Asyncio usage

Update the host credentials/address under `nornir_data`, then run `python demo.py`
from this directory.

`nornir_data/config.yaml` selects Nornir's `asyncio` runner. The demo creates the
`Nornir` object with `AInitNornir`, runs the tasks
from `nornir_scrapli.async_tasks` with `nr.arun` and `task.arun`, and closes the
connections when it leaves the `async with` block. See the
[asyncio guide](../../docs/user_guide/asyncio.md) for details.

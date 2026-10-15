[![Supported Versions](https://img.shields.io/pypi/pyversions/scrapli.svg)](https://pypi.org/project/nornir_scrapli)
[![PyPI version](https://badge.fury.io/py/scrapli.svg)](https://badge.fury.io/py/nornir_scrapli)
[![Weekly Build](https://github.com/scrapli/nornir_scrapli/workflows/Weekly%20dependency%20compatibility/badge.svg)](https://github.com/scrapli/nornir_scrapli/actions?query=workflow%3A%22Weekly+dependency+compatibility%22)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-blueviolet.svg)](https://opensource.org/licenses/MIT)

nornir_scrapli
==============

---

**Documentation**: <a href="https://scrapli.github.io/nornir_scrapli" target="_blank">https://scrapli.github.io/nornir_scrapli</a>

**Source Code**: <a href="https://github.com/scrapli/nornir_scrapli" target="_blank">https://github.com/scrapli/nornir_scrapli</a>

**Examples**: <a href="https://github.com/scrapli/nornir_scrapli/tree/master/examples" target="_blank">https://github.com/scrapli/nornir_scrapli/tree/master/examples</a>

---

nornir_scrapli -- scrapli's plugin for nornir


#### Key Features:

- __Easy__: It's easy to get going with scrapli -- check out the documentation and example links above, and you'll be 
  connecting to devices in no time.
- __Fast__: Do you like to go fast? Of course you do! All of scrapli is built with speed in mind, but if you really 
  feel the need for speed, check out the `ssh2` transport plugin to take it to the next level!
- __Great Developer Experience__: scrapli has great editor support thanks to being fully typed; that plus thorough 
  docs make developing with scrapli a breeze.
- __Well Tested__: Perhaps out of paranoia, but regardless of the reason, scrapli has lots of tests! Unit tests 
  cover the basics, regularly ran functional tests connect to virtual routers to ensure that everything works IRL! 
- __Pluggable__: scrapli provides a pluggable transport system -- don't like the currently available transports, 
  simply extend the base classes and add your own! Need additional device support? Create a simple "platform" in 
  [scrapli_community](https://github.com/scrapli/scrapli_community) to easily add new device support!
- __But wait, there's more!__: Have NETCONF devices in your environment, but love the speed and simplicity of 
  scrapli? You're in luck! Check out [scrapli_netconf](https://github.com/scrapli/scrapli_netconf)!


## Requirements

MacOS or \*nix<sup>1</sup>, Python 3.10–3.14 (development defaults to Python 3.13)

This branch targets Nornir's experimental asyncio/capability-registry implementation
and pins its Git dependency to commit `01bac1d` from
[Nornir PR #1111](https://github.com/nornir-automation/nornir/pull/1111).
Released Nornir 3.6.0 does not
contain these APIs. Both synchronous and asynchronous CLI/configuration plugins
use the capability registry in this branch.

<sup>1</sup> Although many parts of scrapli *do* run on Windows, Windows is not officially supported


## Installation

```
pip install nornir-scrapli
```

See the [docs](https://scrapli.github.io/nornir_scrapli/user_guide/installation) for other installation methods/details.



## A simple Example

```python
from nornir import InitNornir
from nornir_scrapli.tasks import send_command


nr = InitNornir(config_file="nornir_data/config.yaml")
command_results = nr.run(task=send_command, command="show version")

print("send_command result:")
print(command_results["iosxe-1"].result)
```

## Asyncio tasks

Install this checkout with the optional async SSH transport:

```bash
pip install ".[asyncio]"
```

Use the same `scrapli` and `scrapli_cfg` inventory connection names. Leave
`extras.transport` unset to use the mode-specific default (`system` for sync,
`asyncssh` for asyncio), or configure a transport compatible with your chosen mode.

```python
import asyncio

from nornir import InitNornir
from nornir_scrapli.async_tasks import send_command


async def main():
    async with InitNornir(
        config_file="nornir_data/config.yaml",
        runner={"plugin": "asyncio", "options": {"num_workers": 100}},
    ) as nr:
        return await nr.arun(task=send_command, command="show version")


results = asyncio.run(main())
```

Nornir owns connection mode binding: using a synchronous task on an established
async connection, or the reverse, raises Nornir's `ConnectionModeMismatchError`.
Use `host.connection_mode(name)` to query it and await `host.aclose_connections()`
to clean up either or both execution modes. See the
[asyncio guide](docs/user_guide/asyncio.md) for configuration workflows and cleanup.

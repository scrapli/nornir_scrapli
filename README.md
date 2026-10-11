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
- __Tested task contracts__: Unit tests cover native v2 option conversion, task arguments,
  result formatting, interactive sequencing and dry runs without requiring lab devices.
- __Custom device support__: Supply a scrapli v2 YAML definition with `extras.definition`.
- __But wait, there's more!__: Have NETCONF devices in your environment, but love the speed and simplicity of 
  scrapli? Native v2 NETCONF operations are exposed through the `scrapli_netconf` connection plugin.


## Requirements

Python 3.10–3.14 and `scrapli>=2026.10.8` (development defaults to Python 3.13).
Native wheels support Linux x86_64/aarch64 (glibc/musl) and macOS Apple silicon.
Windows and Intel macOS are unsupported.

Upgrading from v1? Follow the [migration guide](docs/user_guide/migrating_to_v2.md).
Inventory extras and task arguments change; `cfg_*` tasks are removed. Stay on
`nornir-scrapli==2026.10.10` if you need v1 or scrapli_cfg integration.


## Installation

nornir_scrapli uses [semantic versions](https://semver.org/). The major version matches the scrapli major version.
Install the release line that matches your scrapli version:

```
# scrapli v1
pip install "nornir-scrapli>=1,<2"

# scrapli v2
pip install "nornir-scrapli>=2,<3"
```

Each `1.x` release is also published with a calendar version, such as `2026.10.30`. Without a version constraint,
`pip install nornir-scrapli` installs the latest calendar version, which uses scrapli v1. Calendar versions will later
follow `2.x` instead. The changelog heading of each release names both versions. See the
[versioning docs](https://scrapli.github.io/nornir_scrapli/user_guide/versioning) and
[issue #178](https://github.com/scrapli/nornir_scrapli/issues/178) for details.

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

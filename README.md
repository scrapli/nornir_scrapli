[![Supported Versions](https://img.shields.io/pypi/pyversions/scrapli.svg)](https://pypi.org/project/nornir_scrapli)
[![PyPI version](https://badge.fury.io/py/scrapli.svg)](https://badge.fury.io/py/nornir_scrapli)
[![Weekly Build](https://github.com/scrapli/nornir_scrapli/workflows/Weekly%20Build/badge.svg)](https://github.com/scrapli/nornir_scrapli/actions?query=workflow%3A%22Weekly+Build%22)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
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

MacOS or \*nix<sup>1</sup>, Python 3.7+

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

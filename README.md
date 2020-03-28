![](https://github.com/carlmontanari/nornir_scrapli/workflows/Weekly%20Build/badge.svg)
[![PyPI version](https://badge.fury.io/py/scrapli.svg)](https://badge.fury.io/py/nornir_scrapli)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


nornir_scrapli
=======

nornir_scrapli -- [scrapli](https://github.com/carlmontanari/scrapli)'s plugin for nornir.


# Table of Contents

- [Quick Start Guide](#quick-start-guide)
  - [Installation](#installation)
  - [A Simple Example](#a-simple-example)
- [Supported Platforms](#supported-platforms)


# Quick Start Guide

## Installation

In most cases installation via pip is the simplest and best way to install nornir_scrapli.

```
pip install nornir-scrapli
```


## A Simple Example

Example inventory file (host/group/default, see "real" Nornir docs for lots more info!):
```yaml
---
iosxe-1:
  hostname: 172.18.0.11
  connection_options:
    scrapli:
      platform: cisco_iosxe
      port: 22
      extras:
        ssh_config_file: True
        auth_strict_key: False
```

```python
from nornir import InitNornir
from nornir_scrapli.tasks import (
    get_prompt,
    send_command,
    send_configs
)

nr = InitNornir(config_file="nornir_data/config.yaml")

prompt_results = nr.run(task=get_prompt)
command_results = nr.run(task=send_command, command="show version")
config_results = nr.run(
    task=send_configs,
    configs=["interface loopback123", "description nornir_scrapli was here"],
)

print("get_prompt result:")
print(prompt_results["iosxe-1"].result)
print("send_command result:")
print(prompt_results["iosxe-1"].result)
print("send_configs result:")
print(config_results["iosxe-1"].result)
```

```
$ python my_scrapli_script.py
get_prompt result:
3560CX#
send_command result:
Cisco IOS Software, C3560CX Software (C3560CX-UNIVERSALK9-M), Version 15.2(4)E7, RELEASE SOFTWARE (fc2)
<SNIP>
send_configs result:


```

# Supported Platforms

nornir_scrapli supports the "core" scrapli drivers. See [scrapli docs](https://github.com/carlmontanari/scrapli#supported-platforms) for more info.


# General Information

Nornir has historically contained it's plugins within the actual Nornir codebase itself, this however is changing. At
 time of writing (27 March 2020) the end state of how plugins will work is not 100% solidified, but this should get
  fairly close, and it works with current and hopefully future Nornir!

If you have used Nornir before, this package should be very similar, but not exactly the same. Since the plugins
 currently/used to live in Nornir you could simply import them from the appropriate package as such:
 
```python
from nornir.plugins.tasks.networking import netconf_get_config
```

With nornir_scrapli you simply install this package along side "regular" Nornir, and import the tasks from
 nornir_scrapli directly:
 
```python
from nornir_scrapli.tasks import send_command
```

As soon as a nornir_scrapli task is imported, it (nornir_scrapli) will register as a connection, and things should
 work as normal from there!

This is obviously all in a "beta" state until Nornir 3.0 is officially released and the template for what plugins
 should look like is solidified, so use with care!

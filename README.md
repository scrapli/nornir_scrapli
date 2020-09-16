![](https://github.com/carlmontanari/nornir_scrapli/workflows/Weekly%20Build/badge.svg)
[![PyPI version](https://badge.fury.io/py/scrapli.svg)](https://badge.fury.io/py/nornir_scrapli)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


nornir_scrapli
==============

*NOTE* this readme is fairly out of date. The develop branch of this repo is setup for Nornir 3.x+ (which has not
 been "officially" released, but is available on pypi with the `--pre` pip flag), while the master branch is
  functional with Nornir 2.x. The master branch is much messier, and less well tested but works just fine... as soon
   as Nornir 3.x is out officially develop will get merged to master and a new pypi release pushed.  

nornir_scrapli -- [scrapli](https://github.com/carlmontanari/scrapli)'s plugin for nornir.

Feel free to join the very awesome networktocode slack workspace [here](https://networktocode.slack.com/), where you
 will find a `scrapli` channel where you can discuss anything about scrapli, as well as tons of other channels covering
  all sorts of network/network-automation topics!


# Table of Contents

- [Quick Start Guide](#quick-start-guide)
  - [Installation](#installation)
  - [A Simple Example](#a-simple-example)
- [Supported Platforms](#supported-platforms)
- [Documentation](#documentation)
- [General Information](#general-information)


# Quick Start Guide

## Installation

In most cases installation via pip is the simplest and best way to install nornir_scrapli.

```
pip install nornir-scrapli
```


## A Simple Example

Example config file:

```yaml
---
inventory:
  plugin: YAMLInventory
  options:
    host_file: "nornir_data/hosts.yaml"
    group_file: "nornir_data/groups.yaml"
    defaults_file: "nornir_data/defaults.yaml"
```

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

## Supported Platforms

nornir_scrapli supports the "core" scrapli drivers, as well as the GenericDriver. See [scrapli docs](https://github.com
/carlmontanari/scrapli#supported-platforms) for more info. The `platform` argument in the inventory data should use
 the "normal" NAPALM style platform names or `generic`. In the hopefully near term this will be improved further to
  support `scrapli_community` platforms as well.

Example platform values (for inventory data):

```
platform: cisco_iosxe
platform: cisco_iosxr
platform: cisco_nxos
platform: arista_eos
platform: juniper_junos
platform: generic
```


# Documentation

Documentation is auto-generated [using pdoc3](https://github.com/pdoc3/pdoc). Documentation is linted (see Linting and
 Testing section) via [pydocstyle](https://github.com/PyCQA/pydocstyle/).

Documentation is hosted via GitHub Pages and can be found
[here](https://carlmontanari.github.io/nornir_scrapli/docs/nornir_scrapli/index.html). You can also view this readme as a web
 page [here](https://carlmontanari.github.io/nornir_scrapli/).

To regenerate documentation locally, use the following make command:

```
make docs
```


# General Information

Nornir has historically contained it's plugins within the actual Nornir codebase itself, this however has changed! As
 of mid September 2020, Nornir 3.0.0 has been officially released -- this move to the 3.x.x version now expects
  plugins to be external to the code base. If you are looking for pre 3.x.x support, please use the `2020.09.01
  ` version.

If you have used Nornir before (pre 3.x.x), this package should be very similar to what you already know. Since the
 plugins used to live in Nornir you could simply import them from the appropriate package as such:
 
```python
from nornir.plugins.tasks.networking import netconf_get_config
```

With nornir_scrapli you simply install this package along side "regular" Nornir, and import the tasks from
 nornir_scrapli directly:
 
```python
from nornir_scrapli.tasks import send_command
```

As soon as a nornir_scrapli task is imported, it (`nornir_scrapli`) will register as a connection, and things should
 work as normal from there!

The last important difference with nornir_scrapli is that in addition to the "normal" data in the Nornir Result
 object, nornir_scrapli also assigns the scrapli `Response` object (or list of `Response` objects) to the
  `scrapli_response` attribute. This means that you can access all of the "normal" scrapli response data from this
   object -- including things like `elapsed_time` and `textfsm_parse_output`:

```python
>>> some_nornir_result["sea-ios-1"].scrapli_response.elapsed_time
0.039469
>>> some_nornir_result["sea-ios-1"].scrapli_response.textfsm_parse_output()
[[some structured data back from the device!]]
``` 

If you would like to continue using `print_result` like "normal" in nornir, but would like to see structured data (if
 available) in the `print_result` output, you can use the nornir_scrapli `print_structured_result` function. This
  function can be imported from the scrapli functions module:
  
```python
from nornir_scrapli.functions import print_structured_result
```

This function acts pretty much exactly like the "normal" print result function, but will of course try to print the
 structured result. By default this will try to use textfsm to parse results, but it is of course configurable via
  the `parser` keyword argument. As scrapli will return an empty data structure if parsing fails, this may cause
   tasks to look like they are getting skipped in the output (nornir's print result function does not print empty
    lists), if you would like to fall back to printing the unparsed output you can do so by setting the
     `fail_to_string` keyword argument to `True` as follows:
     
```python
print_structured_result(my_agg_result, parser="genie", fail_to_string=True)
```

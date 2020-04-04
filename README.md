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
- [General Information](#general-information)


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
 time of writing (4 April 2020) the end state of how plugins will work is not 100% solidified, but this should get
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

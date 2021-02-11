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

Example inventory file (host/group/default, see "real" Nornir docs for lots more info!) -- please notice that there
 is a `scrapli` and a `scrapli_netconf` connection type here!:
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
    scrapli_netconf:
      port: 830
      extras:
        ssh_config_file: True
        auth_strict_key: False
```

**NOTE:** `scrapli-netconf` has no concept (at the moment!) of "platforms" - it simply implements RFC compliant
 NETCONF RPCs, so you do not need to pass `iosxr`, `junos` or anything like that to the `scrapli_netconf` connection
  options section!


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
print(command_results["iosxe-1"].result)
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

Netconf tasks are imported from the same package and in the same fashion as the "core" `scrapli` tasks:

```python
from nornir_scrapli.tasks import (
    netconf_lock,
    netconf_unlock,
    netconf_edit_config,
    netconf_get,
    netconf_get_config,
    netconf_rpc
)
```

And are executed in the same fashion as well:

```python
config = """<config>
    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
            <name>GigabitEthernet1</name>
            <description>scrapli was here!</description>
        </interface>
    </interfaces>
</config>"""
result = nr.run(task=netconf_edit_config, config=config)
print(result['iosxe1'][0].result)
print(result['iosxe1'][0].scrapli_response.xml_result)
```

When using the `scrapli-netconf` tasks the result object `result` will be the string of the returned data from the
 device. As with all other `nornir-scrapli` results, the `scrapli_response` object will be assigned to the `Result
 ` object and will contain all of the "normal" `scrapli` response object data (or `scrapli-netconf` response data
 ), such as the `elapsed_time`, `raw_result`, `xml_result`, etc. -- you can see this in the above example!



## Additional Examples

- [NETCONF Usage](https://github.com/scrapli/nornir_scrapli/tree/master/examples/basic_netconf_usage)
- [Structured Data](https://github.com/scrapli/nornir_scrapli/tree/master/examples/structured_data)

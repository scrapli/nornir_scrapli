# Basic Usage

Import tasks from `nornir_scrapli.tasks` and run them with Nornir:

```python
from nornir import InitNornir
from nornir_scrapli.tasks import send_command

nr = InitNornir(config_file="nornir_data/config.yaml")
results = nr.run(task=send_command, command="show version")
host_result = results["sea-ios-1"][0]
print(host_result.result)
print(host_result.scrapli_response.elapsed_time_seconds)
structured = host_result.scrapli_response.textfsm_parse(index=0)
```

The installed package registers `scrapli` and `scrapli_netconf` connection plugins.
CLI and NETCONF results retain their original native v2 result under
`scrapli_response`; command output remains a string under `result`.

## Structured output

```python
from nornir_scrapli.functions import print_structured_result

print_structured_result(results, parser="textfsm", fail_to_string=True)
```

The helper parses each input independently without changing the original result.
Select `parser="genie"` when the optional Genie dependencies are installed.

## Inventory options and transports

```yaml
connection_options:
  scrapli:
    platform: cisco_iosxe
    extras:
      session: {operation_timeout_ns: 30000000000}
      transport: {kind: bin, ssh_config_path: ~/.ssh/config}
```

Transport kinds are `bin` (default), `ssh2`, and `telnet`; they are supplied by native
scrapli v2 rather than separate Python transport plugins. Bin SSH host key checking
defaults to true. Use an explicit device platform so paging is configured correctly.

See [Migrating to v2](migrating_to_v2.md) for all option sections, argument changes,
NETCONF enum examples, interactive exchanges and dry-run behavior.

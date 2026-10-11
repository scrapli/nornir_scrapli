# Migrating to scrapli v2

This release uses `scrapli>=2026.10.8` and its native `Cli` and `Netconf` connections.
Task names and Nornir script structure stay the same. Update inventory extras and task
arguments before upgrading. The v1 line ends at `nornir-scrapli==2026.10.10`.

The first v2 release, `2026.10.3`, lacks the public NETCONF capabilities accessor.
`2026.10.8` is the earliest release supporting the complete task surface.

## Installation and removed integrations

Python 3.10–3.14 is supported on Linux x86_64/aarch64 (glibc or musl) and macOS Apple
silicon. Windows and Intel macOS have no supported scrapli v2 wheels.

The `scrapli_cfg` connection and all six `cfg_*` tasks are removed. Users needing those
tasks must stay on `2026.10.10`. The separate scrapli_netconf and scrapli_community
packages are no longer dependencies: NETCONF is included in scrapli, and custom device
support comes from definition files.

## Inventory extras

Before:

```yaml
connection_options:
  scrapli:
    platform: cisco_iosxe
    extras:
      auth_secondary: enable-password
      auth_strict_key: false
      ssh_config_file: ~/.ssh/config
      channel_log: true
      timeout_ops: 30
```

After:

```yaml
connection_options:
  scrapli:
    platform: cisco_iosxe
    extras:
      auth:
        private_key_path: ~/.ssh/id_ed25519
        lookups: {enable: enable-password}
      session:
        operation_timeout_ns: 30000000000
        recorder_path: true
      transport:
        kind: bin
        ssh_config_path: ~/.ssh/config
        enable_strict_key: false
      # definition: ./my_platform.yaml
```

Extras sections follow native objects: `auth` → `AuthOptions`, `session` →
`SessionOptions`, `transport` → transport-specific options, `cli` → `scrapli.cli.Options`,
and `netconf` → `NetconfOptions`. `cli`/`definition` apply only to the `scrapli`
connection; `netconf` applies only to `scrapli_netconf`.

Nornir hostname, port, username and password fill connection defaults. Explicit auth
values take precedence, including empty strings; `None` uses the Nornir fallback.
Nornir's `ssh.config_file` fills bin `ssh_config_path` unless explicitly set in extras.
CLI defaults to port 22 for SSH and 23 for telnet; NETCONF defaults to 830.

**Bin host key checking defaults to true**, unlike scrapli v2's own default. Set
`enable_strict_key: false` explicitly to disable it. The ssh2 transport has its own
native known-hosts options, and does not accept bin-specific strict-key/config fields.

Transport alternatives:

```yaml
transport: {kind: ssh2, known_hosts_path: ~/.ssh/known_hosts}
# or:
transport: {kind: telnet}
```

`session.recorder_path: true` becomes `scrapli_channel_<hostname>.log`, independently
for each host. A string path is preserved. Option objects are also accepted in Python
inventories and copied into fresh per-host objects:

```python
from scrapli import AuthOptions, LookupKeyValue, TransportBinOptions

extras = {
    "auth": AuthOptions(lookups=[LookupKeyValue(key="enable", value="enable-password")]),
    "transport": TransportBinOptions(enable_strict_key=True),
}
```

Unknown keys and v1 flat extras fail with `NornirScrapliInvalidOptions`, identifying
the host/key and linking to this guide. Legacy transport names such as `paramiko` and
`system` are not aliases. Use `bin`, `ssh2` or `telnet`.

## Platforms and definitions

NAPALM aliases remain: `ios`, `nxos`, `iosxr`, `eos`, `junos`. A missing platform or
`generic` selects `default`. Set an explicit device platform so the native on-open
instructions handle paging. `extras.definition` overrides platform and accepts a
built-in definition name or YAML file path. Unknown definitions raise
`NornirScrapliInvalidPlatform` with host and definition context.

Configuration tasks are allowed for any definition with the requested configuration
mode. Native mode errors fail the task if the definition lacks that mode.

## Task arguments

| v1 | v2 |
| --- | --- |
| `privilege_level` | `requested_mode` |
| `timeout_ops=30` (seconds) | `operation_timeout_ns=30000000000` (nanoseconds) |
| `strip_prompt=True` | `retain_trailing_prompt=False` |
| `stop_on_failed` | `stop_on_indicated_failure` (defaults to true) |
| `eager` | removed; select `InputHandling` explicitly |
| `failed_when_contains` | removed; edit definition `failure_indicators` |
| raw RPC `filter_` | `payload` |

No aliases are accepted. Keep `command`, `commands`, `config`, `configs`, and `file`
on their existing tasks. New `send_prompted_input` mirrors its native method:

```python
from nornir_scrapli.tasks import send_command, send_prompted_input

nr.run(task=send_command, command="show version", operation_timeout_ns=30000000000)
nr.run(task=send_prompted_input, input_="clear logging", prompt="[confirm]",
       prompt_pattern="", response="")
```

`send_interactive` retains input/expected-prompt/optional-hidden tuples. Each expected
prompt acknowledges that event's input before the next input is sent. Output buffered
before a new input cannot acknowledge it. Exact text is matched first, then a regex.
Hidden inputs are redacted from returned text and inputs; raw result bytes for hidden
exchanges contain the sanitized, normalized text rather than wire-exact output.
Native session recordings/debug logs are outside that returned-result
redaction and may include device echoes; verify their behavior for your device before
recording an exchange with secrets.

CLI configuration dry runs send no configuration. They read the current prompt,
match it against the loaded definition's mode patterns/exclusions, enter the requested
mode, then restore the matching starting mode. Ambiguous or unsupported mode patterns
fail before the transition. The Python `regex` matcher supports bundled possessive
patterns on Python 3.10, but custom native PCRE patterns need compatibility checking.

NETCONF arguments use native enums:

```python
from scrapli.netconf import DatastoreType, FilterType
from nornir_scrapli.tasks import netconf_get_config, netconf_rpc

nr.run(task=netconf_get_config, source=DatastoreType.CANDIDATE,
       filter_type=FilterType.SUBTREE, filter_="<interfaces/>")
nr.run(task=netconf_rpc, payload="<get/>")
```

`netconf_edit_config` retains `diff` and `dry_run`: it still sends the edit and then
discards candidate changes. This cannot undo running-datastore edits, and discard also
removes pre-existing uncommitted candidate changes. New mutating NETCONF operations
have no transactional dry run.

## Results and parsing

`result.result` remains output text: commands are joined with a blank line;
configuration inputs precede their outputs. NETCONF results contain reply XML.
`send_interactive` now returns output text rather than a response object.

`result.scrapli_response` is a native `scrapli.cli_result.Result` or
`scrapli.netconf_result.Result`. Its `failed` attribute is a boolean property.
`get_prompt` now also retains its native result. Capabilities still return a list.

```python
host_result = results["router"][0]
native = host_result.scrapli_response
native.elapsed_time_seconds
native.textfsm_parse(index=0)  # CLI only
native.genie_parse(index=0)    # CLI only, requires the genie extra
native.result_raw            # bytes; NETCONF exposes rpc_errors/rpc_warnings too
```

`print_structured_result` keeps its arguments, prints one parsed entry per native CLI
input, and uses each input's raw text on parse failure when `fail_to_string=True`.

## Subscriptions and notifications

Streaming operations are available on the connection rather than as one-shot tasks.
Supply a device-supported subscription payload and own its lifetime explicitly:

```python
connection = nr.inventory.hosts["router"].get_connection("scrapli_netconf", nr.config)
reply = connection.raw_rpc(payload)  # establish-subscription request supported by the device
if reply.failed:
    raise RuntimeError(reply.rpc_errors)
subscription_id = connection.get_subscription_id(reply.result)
next_subscription_message = connection.get_next_subscription(subscription_id)
next_notification = connection.get_next_notification()
```

`get_subscription_id` extracts the identifier from the establish-subscription **reply**;
it does not send the request. Message retrieval raises `scrapli.exceptions.NoMessagesException`
when no message is available; applications should poll or retry according to their stream lifecycle.

## Release verification

Unit tests patch native operations and do not prove native mode detection or callback
behavior on a device. Before release, verify every retained task on a capable real
device, especially consecutive identical prompts, hidden responses, definition failure
indicators, paging and restoring a nondefault starting mode after a CLI dry run.

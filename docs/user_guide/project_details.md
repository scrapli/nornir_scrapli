# Project Details

nornir_scrapli integrates scrapli v2 CLI and NETCONF operations with Nornir's inventory,
connection lifecycle and concurrent task execution. Tasks expose native v2 options
while returning Nornir results and retaining native results for parsing and diagnostics.

## Device platforms

Use a built-in scrapli definition name such as `cisco_iosxe`, `cisco_iosxr`,
`cisco_nxos`, `arista_eos` or `juniper_junos`. The NAPALM aliases `ios`, `iosxr`,
`nxos`, `eos` and `junos` are mapped to those names.

`generic` or an omitted platform selects the `default` definition. Set an explicit
device platform for native paging configuration. Supply custom definitions with
`extras.definition`; it overrides platform. NETCONF does not need a device platform.

## Runtime platforms

Python 3.10–3.14 is tested on Ubuntu and macOS Apple silicon. Native wheels also
support Linux aarch64 and musl. See [Installation](installation.md) and
[Migrating to v2](migrating_to_v2.md) for supported platforms and breaking changes.

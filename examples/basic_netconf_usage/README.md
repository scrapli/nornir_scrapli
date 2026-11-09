# Basic NETCONF usage

This example uses native scrapli v2 NETCONF through Nornir. Update host credentials
and addresses under `nornir_data`, then run `python demo.py` from this directory.
The demo edits interface configuration and locks/unlocks the running datastore.

NETCONF inventory options live under the retained `scrapli_netconf` connection name:

```yaml
connection_options:
  scrapli_netconf:
    port: 830
    extras:
      transport: {kind: bin, ssh_config_path: ~/.ssh/config}
```

Tasks use native enum values such as `DatastoreType.RUNNING`. Raw RPCs use `payload`.
Each RPC result's `result` contains XML; `scrapli_response` contains the native
`scrapli.netconf_result.Result` with `failed`, `rpc_errors`, `rpc_warnings`,
`elapsed_time_seconds` and `result_raw`.

See [the migration guide](../../docs/user_guide/migrating_to_v2.md) for the new option
sections and candidate-discard dry-run semantics.

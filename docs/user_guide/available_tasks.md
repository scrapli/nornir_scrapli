# Available Tasks

Tasks wrap scrapli v2 `Cli` and `Netconf` operations for Nornir. Import them from
`nornir_scrapli.tasks`; see each reference page for native argument names and defaults.


## Scrapli "core" Tasks

- [get_prompt](https://scrapli.github.io/nornir_scrapli/reference/tasks/core/get_prompt) - Get the current prompt of the device
- [send_command](https://scrapli.github.io/nornir_scrapli/reference/tasks/core/send_command) - Send a single command to the device
- [send_commands](https://scrapli.github.io/nornir_scrapli/reference/tasks/core/send_commands) - Send a list of commands to the device
- [send_commands_from_file](https://scrapli.github.io/nornir_scrapli/reference/tasks/core/send_commands_from_file) - Send a list of commands from a file to the device
- [send_config](https://scrapli.github.io/nornir_scrapli/reference/tasks/core/send_config) - Send a configuration to the device
- [send_configs](https://scrapli.github.io/nornir_scrapli/reference/tasks/core/send_configs) - Send a list of configurations to the device
- [send_configs_from_file](https://scrapli.github.io/nornir_scrapli/reference/tasks/core/send_configs_from_file) - Send a list of configurations from a file to the device
- [send_interactive](https://scrapli.github.io/nornir_scrapli/reference/tasks/core/send_interactive) -"Interact" with the device (handle prompts and inputs and things like that)
- [send_prompted_input](https://scrapli.github.io/nornir_scrapli/reference/tasks/core/send_prompted_input) - Answer a single confirmation or authentication prompt


## Scrapli Netconf Tasks

Note that not all devices will support all operations!

- [netconf_capabilities](https://scrapli.github.io/nornir_scrapli/reference/tasks/netconf/capabilities) - Get list of capabilities as exchanged during netconf connection establishment
- [netconf_commit](https://scrapli.github.io/nornir_scrapli/reference/tasks/netconf/commit) - Commit the configuration on the device
- [netconf_discard](https://scrapli.github.io/nornir_scrapli/reference/tasks/netconf/discard) - Discard the configuration on the device
- [netconf_edit_config](https://scrapli.github.io/nornir_scrapli/reference/tasks/netconf/edit_config) - Edit the configuration on the device
- [netconf_delete_config](https://scrapli.github.io/nornir_scrapli/reference/tasks/netconf/delete_config) - Delete a given datastore on the device
- [netconf_get](https://scrapli.github.io/nornir_scrapli/reference/tasks/netconf/get) - Get a subtree or xpath from the device
- [netconf_get_config](https://scrapli.github.io/nornir_scrapli/reference/tasks/netconf/get_config) - Get the configuration from the device
- [netconf_lock](https://scrapli.github.io/nornir_scrapli/reference/tasks/netconf/lock) - Lock the datastore on the device
- [netconf_unlock](https://scrapli.github.io/nornir_scrapli/reference/tasks/netconf/unlock) - Unlock the datastore on the device
- [netconf_rpc](https://scrapli.github.io/nornir_scrapli/reference/tasks/netconf/rpc) - Send a "bare" RPC to the device
- [netconf_validate](https://scrapli.github.io/nornir_scrapli/reference/tasks/netconf/validate) - Execute the`validate` rpc against a given datastore


- [netconf_copy_config](https://scrapli.github.io/nornir_scrapli/reference/tasks/netconf/copy_config) - Copy a datastore configuration
- [netconf_get_schema](https://scrapli.github.io/nornir_scrapli/reference/tasks/netconf/get_schema) - Read a schema
- [netconf_get_data](https://scrapli.github.io/nornir_scrapli/reference/tasks/netconf/get_data) - Read NMDA datastore data
- [netconf_edit_data](https://scrapli.github.io/nornir_scrapli/reference/tasks/netconf/edit_data) - Edit NMDA datastore data
- [netconf_cancel_commit](https://scrapli.github.io/nornir_scrapli/reference/tasks/netconf/cancel_commit) - Cancel a confirmed commit
- [netconf_kill_session](https://scrapli.github.io/nornir_scrapli/reference/tasks/netconf/kill_session) - Terminate a NETCONF session
- [netconf_action](https://scrapli.github.io/nornir_scrapli/reference/tasks/netconf/action) - Execute a YANG action

The `cfg_*` tasks are removed in the v2 line. See [Migrating to v2](migrating_to_v2.md).

# Available Tasks

All tasks presented here are methods that live in `scrapli` or `scrapli_netconf` -- these tasks are simply "wrapped
" in such a way that they may be used within the constructs of `nornir`! The links below link back to the `scrapli
` or `scrapli_netconf` docs for the given method -- in all (or very nearly all?) cases, the same arguments that the
 underlying library supports will be exposed to `nornir`!


## Scrapli "core" Tasks

- [get_prompt](/api_docs/tasks/#get_prompt) - Get the current prompt of the device
- [send_command](/api_docs/tasks/#send_command) - Send a single command to the device
- [send_commands](/api_docs/tasks/#send_commands) - Send a list of commands to the device
- [send_commands_from_file](/api_docs/tasks/#send_commands_from_file) - Send a list of commands from a file to the device
- [send_config](/api_docs/tasks/#send_config) - Send a configuration to the device
- [send_configs](/api_docs/tasks/#send_configs) - Send a list of configurations to the device
- [send_configs_from_file](/api_docs/tasks/#send_configs_from_file) - Send a list of configurations from a file to the device
- [send_interactive](/api_docs/tasks/#send_interactive) -"Interact" with the device (handle prompts and inputs and things like that)


## Scrapli Netconf Tasks

Note that not all devices will support all operations!

- netconf_capabilities - Get list of capabilities as exchanged during netconf connection establishment
- [netconf_commit](/api_docs/tasks/#commit) - Commit the configuration on the device
- [netconf_discard](/api_docs/tasks/#discard) - Discard the configuration on the device
- [netconf_edit_config](/api_docs/tasks/#edit_config) - Edit the configuration on the device
- [netconf_delete_config](/api_docs/tasks/#delete_config) - Delete a given datastore on the device
- [netconf_get](/api_docs/tasks/#get) - Get a subtree or xpath from the device
- [netconf_get_config](/api_docs/tasks/#get_config) - Get the configuration from the device
- [netconf_lock](/api_docs/tasks/#lock) - Lock the datastore on the device
- [netconf_unlock](/api_docs/tasks/#unlock) - Unlock the datastore on the device
- [netconf_rpc](/api_docs/tasks/#rpc) - Send a "bare" RPC to the device
- [netconf_validate](/api_docs/tasks/#netconf_validate) - Execute the `validate` rpc against a given datastore

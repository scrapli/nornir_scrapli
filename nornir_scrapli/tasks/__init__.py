"""nornir_scrapli.tasks"""
from nornir_scrapli.tasks.get_prompt import get_prompt
from nornir_scrapli.tasks.netconf_capabilities import netconf_capabilities
from nornir_scrapli.tasks.netconf_commit import netconf_commit
from nornir_scrapli.tasks.netconf_delete_config import netconf_delete_config
from nornir_scrapli.tasks.netconf_discard import netconf_discard
from nornir_scrapli.tasks.netconf_edit_config import netconf_edit_config
from nornir_scrapli.tasks.netconf_get import netconf_get
from nornir_scrapli.tasks.netconf_get_config import netconf_get_config
from nornir_scrapli.tasks.netconf_lock import netconf_lock
from nornir_scrapli.tasks.netconf_rpc import netconf_rpc
from nornir_scrapli.tasks.netconf_unlock import netconf_unlock
from nornir_scrapli.tasks.netconf_validate import netconf_validate
from nornir_scrapli.tasks.send_command import send_command
from nornir_scrapli.tasks.send_commands import send_commands
from nornir_scrapli.tasks.send_commands_from_file import send_commands_from_file
from nornir_scrapli.tasks.send_config import send_config
from nornir_scrapli.tasks.send_configs import send_configs
from nornir_scrapli.tasks.send_configs_from_file import send_configs_from_file
from nornir_scrapli.tasks.send_interactive import send_interactive

__all__ = (
    "get_prompt",
    "netconf_capabilities",
    "netconf_commit",
    "netconf_delete_config",
    "netconf_discard",
    "netconf_edit_config",
    "netconf_get",
    "netconf_get_config",
    "netconf_lock",
    "netconf_rpc",
    "netconf_unlock",
    "netconf_validate",
    "send_command",
    "send_commands",
    "send_commands_from_file",
    "send_config",
    "send_configs",
    "send_configs_from_file",
    "send_interactive",
)

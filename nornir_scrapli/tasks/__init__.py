"""nornir_scrapli.tasks"""

from nornir_scrapli.tasks.core.get_prompt import get_prompt
from nornir_scrapli.tasks.core.send_command import send_command
from nornir_scrapli.tasks.core.send_commands import send_commands
from nornir_scrapli.tasks.core.send_commands_from_file import send_commands_from_file
from nornir_scrapli.tasks.core.send_config import send_config
from nornir_scrapli.tasks.core.send_configs import send_configs
from nornir_scrapli.tasks.core.send_configs_from_file import send_configs_from_file
from nornir_scrapli.tasks.core.send_interactive import send_interactive
from nornir_scrapli.tasks.core.send_prompted_input import send_prompted_input
from nornir_scrapli.tasks.netconf.action import netconf_action
from nornir_scrapli.tasks.netconf.cancel_commit import netconf_cancel_commit
from nornir_scrapli.tasks.netconf.capabilities import netconf_capabilities
from nornir_scrapli.tasks.netconf.commit import netconf_commit
from nornir_scrapli.tasks.netconf.copy_config import netconf_copy_config
from nornir_scrapli.tasks.netconf.delete_config import netconf_delete_config
from nornir_scrapli.tasks.netconf.discard import netconf_discard
from nornir_scrapli.tasks.netconf.edit_config import netconf_edit_config
from nornir_scrapli.tasks.netconf.edit_data import netconf_edit_data
from nornir_scrapli.tasks.netconf.get import netconf_get
from nornir_scrapli.tasks.netconf.get_config import netconf_get_config
from nornir_scrapli.tasks.netconf.get_data import netconf_get_data
from nornir_scrapli.tasks.netconf.get_schema import netconf_get_schema
from nornir_scrapli.tasks.netconf.kill_session import netconf_kill_session
from nornir_scrapli.tasks.netconf.lock import netconf_lock
from nornir_scrapli.tasks.netconf.rpc import netconf_rpc
from nornir_scrapli.tasks.netconf.unlock import netconf_unlock
from nornir_scrapli.tasks.netconf.validate import netconf_validate

__all__ = (
    "get_prompt",
    "netconf_action",
    "netconf_cancel_commit",
    "netconf_capabilities",
    "netconf_commit",
    "netconf_copy_config",
    "netconf_delete_config",
    "netconf_discard",
    "netconf_edit_config",
    "netconf_edit_data",
    "netconf_get",
    "netconf_get_config",
    "netconf_get_data",
    "netconf_get_schema",
    "netconf_kill_session",
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
    "send_prompted_input",
)

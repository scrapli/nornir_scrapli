"""nornir_scrapli.tasks"""

from nornir_scrapli.tasks.cfg.abort_config import cfg_abort_config
from nornir_scrapli.tasks.cfg.commit_config import cfg_commit_config
from nornir_scrapli.tasks.cfg.diff_config import cfg_diff_config
from nornir_scrapli.tasks.cfg.get_config import cfg_get_config
from nornir_scrapli.tasks.cfg.get_version import cfg_get_version
from nornir_scrapli.tasks.cfg.load_config import cfg_load_config
from nornir_scrapli.tasks.core.get_prompt import get_prompt
from nornir_scrapli.tasks.core.send_command import send_command
from nornir_scrapli.tasks.core.send_commands import send_commands
from nornir_scrapli.tasks.core.send_commands_from_file import send_commands_from_file
from nornir_scrapli.tasks.core.send_config import send_config
from nornir_scrapli.tasks.core.send_configs import send_configs
from nornir_scrapli.tasks.core.send_configs_from_file import send_configs_from_file
from nornir_scrapli.tasks.core.send_interactive import send_interactive
from nornir_scrapli.tasks.netconf.capabilities import netconf_capabilities
from nornir_scrapli.tasks.netconf.commit import netconf_commit
from nornir_scrapli.tasks.netconf.delete_config import netconf_delete_config
from nornir_scrapli.tasks.netconf.discard import netconf_discard
from nornir_scrapli.tasks.netconf.edit_config import netconf_edit_config
from nornir_scrapli.tasks.netconf.get import netconf_get
from nornir_scrapli.tasks.netconf.get_config import netconf_get_config
from nornir_scrapli.tasks.netconf.lock import netconf_lock
from nornir_scrapli.tasks.netconf.rpc import netconf_rpc
from nornir_scrapli.tasks.netconf.unlock import netconf_unlock
from nornir_scrapli.tasks.netconf.validate import netconf_validate

__all__ = (
    "cfg_abort_config",
    "cfg_commit_config",
    "cfg_diff_config",
    "cfg_get_config",
    "cfg_get_version",
    "cfg_load_config",
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

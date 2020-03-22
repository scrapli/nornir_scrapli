"""nornir_scrapli.tasks"""
from nornir_scrapli.connection import register
from nornir_scrapli.tasks.get_prompt import get_prompt
from nornir_scrapli.tasks.send_command import send_command
from nornir_scrapli.tasks.send_commands import send_commands
from nornir_scrapli.tasks.send_configs import send_configs
from nornir_scrapli.tasks.send_interactive import send_interactive

# register the scrapli Connection plugin in nornir
register()

__all__ = (
    "get_prompt",
    "send_command",
    "send_commands",
    "send_configs",
    "send_interactive",
)

"""Minimal IOS XE CLI contract."""

from functional.helpers import Device, commands_for

__all__ = ("Device",)

NAME = "functional_cisco_iosxe"
INITIAL_PROMPT = "{base_prompt}>"
ENABLE_PROMPT = "{base_prompt}#"
CONFIG_PROMPT = "{base_prompt}(config)#"
DEVICE_NAME = "Device"
commands = commands_for("cisco_iosxe")

"""Minimal IOS XR CLI contract."""

from functional.helpers import Device, commands_for

__all__ = ("Device",)

NAME = "functional_cisco_iosxr"
INITIAL_PROMPT = "{base_prompt}#"
CONFIG_PROMPT = "{base_prompt}(config)#"
DEVICE_NAME = "Device"
commands = commands_for("cisco_iosxr")

"""Minimal synthetic Junos CLI contract."""

from functional.helpers import Device, commands_for

__all__ = ("Device",)

NAME = "functional_juniper_junos"
INITIAL_PROMPT = "{base_prompt}>"
CONFIG_PROMPT = "{base_prompt}#"
DEVICE_NAME = "Device"
commands = commands_for("juniper_junos")

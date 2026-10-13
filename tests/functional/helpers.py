"""Stateless command handlers shared by the static NOS definitions."""

import time

from functional.constants import (
    CONFIG_LINES,
    INTERACTIVE_COMMAND,
    INTERACTIVE_CONFIRMATION,
    INTERACTIVE_RESPONSE,
    SECOND_COMMAND,
    SHOW_VERSION_COMMAND,
    SLOW_RESPONSE_DELAY,
    TIMEOUT_FAILURE_HOST,
    expected_clock_output,
    expected_config_prompt,
    expected_default_prompt,
    expected_version_output,
)


class Device:
    def __init__(self, configuration_file=None):
        self.configuration_file = configuration_file


def version(_device, *, base_prompt, current_prompt, command):
    if base_prompt == TIMEOUT_FAILURE_HOST:
        time.sleep(SLOW_RESPONSE_DELAY)
    return expected_version_output(base_prompt)


def clock(_device, *, base_prompt, current_prompt, command):
    return expected_clock_output(base_prompt)


def commands_for(platform):
    low = "{base_prompt}>"
    privileged = "{base_prompt}#"
    default = expected_default_prompt("{base_prompt}", platform)
    config = expected_config_prompt("{base_prompt}", platform)
    rejection = {
        "cisco_iosxe": "% Invalid input detected",
        "cisco_nxos": "% Invalid command at '^' marker.",
        "cisco_iosxr": "% Invalid input detected",
        "arista_eos": "% Invalid input",
        "juniper_junos": "syntax error: unknown command",
    }[platform]
    commands = {
        "_default_": {"output": rejection},
        "exit": {"output": True},
        SHOW_VERSION_COMMAND: {"output": version, "prompt": default},
        SECOND_COMMAND: {"output": clock, "prompt": default},
        INTERACTIVE_COMMAND: {
            "output": INTERACTIVE_CONFIRMATION.removesuffix(" [confirm]"),
            "prompt": default,
            "new_prompt": "[confirm]",
        },
        INTERACTIVE_RESPONSE: {
            "output": "Logging cleared for {base_prompt}",
            "prompt": "[confirm]",
            "new_prompt": default,
        },
    }
    commands.update({line: {"output": "", "prompt": config} for line in CONFIG_LINES})
    if platform == "juniper_junos":
        commands.update(
            {
                "configure": {"output": "", "prompt": low, "new_prompt": config},
                "exit configuration-mode": {"output": "", "prompt": config, "new_prompt": low},
            }
        )
        startup = (
            "set cli screen-length 0",
            "set cli screen-width 511",
            "set cli complete-on-space off",
        )
    else:
        commands.update(
            {
                "configure terminal": {"output": "", "prompt": privileged, "new_prompt": config},
                "end": {"output": "", "prompt": config, "new_prompt": privileged},
            }
        )
        if platform != "cisco_iosxr":
            commands.update(
                {
                    "enable": {"output": "", "prompt": low, "new_prompt": privileged},
                    "disable": {"output": "", "prompt": privileged, "new_prompt": low},
                }
            )
        width = {"cisco_iosxe": 512, "cisco_nxos": 511, "cisco_iosxr": 512, "arista_eos": 32767}
        startup = ("terminal length 0", f"terminal width {width[platform]}")
    commands.update({command: {"output": "", "prompt": default} for command in startup})
    return commands

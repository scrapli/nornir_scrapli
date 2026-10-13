"""Exercise the public Nornir tasks over real SSH."""

from pathlib import Path
from re import escape

import pytest
from scrapli.response import Response

from functional.constants import (
    CONFIG_LINES,
    HEALTHY_REPLICAS,
    INTERACTIVE_COMMAND,
    INTERACTIVE_CONFIRMATION,
    INTERACTIVE_RESPONSE,
    KNOWN_GAPS,
    PLATFORMS,
    SECOND_COMMAND,
    SHOW_VERSION_COMMAND,
    expected_clock_output,
    expected_config_prompt,
    expected_default_prompt,
    expected_version_output,
)
from nornir.core.task import Result
from nornir_scrapli.tasks import (
    get_prompt,
    send_command,
    send_commands,
    send_commands_from_file,
    send_config,
    send_configs,
    send_configs_from_file,
    send_interactive,
)

PLATFORM_CASES = [
    pytest.param(platform, marks=pytest.mark.xfail(strict=True, reason=KNOWN_GAPS[platform]))
    if platform in KNOWN_GAPS
    else platform
    for platform in PLATFORMS
]


@pytest.mark.parametrize("platform", PLATFORM_CASES)
def test_send_command(healthy_platform_nornir, platform):
    result = healthy_platform_nornir.run(task=send_command, command=SHOW_VERSION_COMMAND)

    assert not result.failed
    assert len(result) == HEALTHY_REPLICAS
    for host_name, multi_result in result.items():
        host_result = multi_result[0]
        assert host_result.failed is False
        assert host_result.changed is False
        assert host_result.result == expected_version_output(host_name)
        assert host_result.scrapli_response.channel_input == SHOW_VERSION_COMMAND


@pytest.mark.parametrize("platform", PLATFORM_CASES)
def test_send_commands(healthy_platform_nornir, platform):
    result = healthy_platform_nornir.run(
        task=send_commands, commands=[SHOW_VERSION_COMMAND, SECOND_COMMAND]
    )

    assert not result.failed
    assert len(result) == HEALTHY_REPLICAS
    for host_name, multi_result in result.items():
        host_result = multi_result[0]
        assert host_result.failed is False
        assert host_result.changed is False
        assert host_result.result == "\n\n".join(
            [expected_version_output(host_name), expected_clock_output(host_name)]
        )
        assert [response.channel_input for response in host_result.scrapli_response] == [
            SHOW_VERSION_COMMAND,
            SECOND_COMMAND,
        ]


@pytest.mark.parametrize("platform", PLATFORM_CASES)
def test_send_commands_from_file(healthy_platform_nornir, platform):
    command_file = Path(__file__).parent / "files" / "send_commands_from_file"
    result = healthy_platform_nornir.run(task=send_commands_from_file, file=str(command_file))

    assert not result.failed
    assert len(result) == HEALTHY_REPLICAS
    for host_name, multi_result in result.items():
        host_result = multi_result[0]
        assert host_result.failed is False
        assert host_result.changed is False
        assert host_result.result == "\n\n".join(
            [expected_version_output(host_name), expected_clock_output(host_name)]
        )
        assert [response.channel_input for response in host_result.scrapli_response] == [
            SHOW_VERSION_COMMAND,
            SECOND_COMMAND,
        ]


@pytest.mark.parametrize("platform", PLATFORM_CASES)
def test_get_prompt(healthy_platform_nornir, platform):
    result = healthy_platform_nornir.run(task=get_prompt)

    assert not result.failed
    assert len(result) == HEALTHY_REPLICAS
    for host_name, multi_result in result.items():
        host_result = multi_result[0]
        assert host_result.failed is False
        assert host_result.changed is False
        assert host_result.result == expected_default_prompt(host_name, platform)


def assert_config_prompt(nr, platform):
    prompts = nr.run(task=get_prompt)

    assert not prompts.failed
    assert len(prompts) == HEALTHY_REPLICAS
    for host_name, multi_result in prompts.items():
        host_result = multi_result[0]
        assert host_result.failed is False
        assert host_result.changed is False
        assert host_result.result == expected_config_prompt(host_name, platform)
        assert host_result.result != expected_default_prompt(host_name, platform)


@pytest.mark.parametrize("platform", PLATFORM_CASES)
def test_send_config(healthy_platform_nornir, platform):
    config = "\n".join(CONFIG_LINES)
    result = healthy_platform_nornir.run(task=send_config, config=config)
    assert_config_prompt(healthy_platform_nornir, platform)

    assert not result.failed
    assert len(result) == HEALTHY_REPLICAS
    for multi_result in result.values():
        host_result = multi_result[0]
        assert host_result.failed is False
        assert host_result.changed is True
        assert host_result.result == config + "\n"
        assert isinstance(host_result.scrapli_response, Response)
        assert host_result.scrapli_response.channel_input == config
        assert host_result.scrapli_response.result == "\n"
        assert host_result.scrapli_response.failed is False


@pytest.mark.parametrize("platform", PLATFORM_CASES)
def test_send_configs(healthy_platform_nornir, platform):
    result = healthy_platform_nornir.run(task=send_configs, configs=list(CONFIG_LINES))
    assert_config_prompt(healthy_platform_nornir, platform)

    assert not result.failed
    assert len(result) == HEALTHY_REPLICAS
    for multi_result in result.values():
        host_result = multi_result[0]
        assert host_result.failed is False
        assert host_result.changed is True
        assert host_result.result == "\n".join(CONFIG_LINES) + "\n"
        assert [response.channel_input for response in host_result.scrapli_response] == list(
            CONFIG_LINES
        )
        assert [response.result for response in host_result.scrapli_response] == ["", ""]
        assert host_result.scrapli_response.failed is False


@pytest.mark.parametrize("platform", PLATFORM_CASES)
def test_send_configs_from_file(healthy_platform_nornir, platform):
    config_file = Path(__file__).parent / "files" / "send_configs_from_file"
    result = healthy_platform_nornir.run(task=send_configs_from_file, file=str(config_file))

    assert not result.failed
    assert_config_prompt(healthy_platform_nornir, platform)
    assert len(result) == HEALTHY_REPLICAS
    assert config_file.read_text() == "\n".join(CONFIG_LINES) + "\n"
    for multi_result in result.values():
        host_result = multi_result[0]
        assert host_result.failed is False
        assert host_result.changed is True
        assert host_result.result == "\n".join(CONFIG_LINES) + "\n"
        assert [response.channel_input for response in host_result.scrapli_response] == list(
            CONFIG_LINES
        )
        assert [response.result for response in host_result.scrapli_response] == ["", ""]
        assert host_result.scrapli_response.failed is False


@pytest.mark.parametrize("platform", PLATFORM_CASES)
def test_send_interactive(healthy_platform_nornir, platform):
    def interact(task):
        events = [
            (INTERACTIVE_COMMAND, INTERACTIVE_CONFIRMATION.split()[-1], False),
            (
                INTERACTIVE_RESPONSE,
                f"^{escape(expected_default_prompt(task.host.name, platform))}$",
                False,
            ),
        ]
        return send_interactive(task, interact_events=events)

    result = healthy_platform_nornir.run(task=interact)

    assert not result.failed
    assert len(result) == HEALTHY_REPLICAS
    for host_name, multi_result in result.items():
        host_result = multi_result[0]
        assert type(host_result) is Result
        assert host_result.failed is False
        assert host_result.changed is True
        assert isinstance(host_result.result, Response)
        assert host_result.result is host_result.scrapli_response
        assert host_result.scrapli_response.failed is False
        assert host_result.scrapli_response.channel_input == ", ".join(
            [INTERACTIVE_COMMAND, INTERACTIVE_RESPONSE]
        )
        confirmation = INTERACTIVE_CONFIRMATION.replace(" [confirm]", "\n[confirm]")
        assert confirmation in host_result.scrapli_response.result
        assert host_result.scrapli_response.result == (
            f"{INTERACTIVE_COMMAND}\n{confirmation}{INTERACTIVE_RESPONSE}\n"
            f"Logging cleared for {host_name}\n{expected_default_prompt(host_name, platform)}"
        )

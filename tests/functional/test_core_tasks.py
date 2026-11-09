"""Exercise the public Nornir tasks over real SSH."""

from pathlib import Path
from re import escape

import pytest
from scrapli.cli_result import Result as CliResult

from functional.constants import (
    CONFIG_LINES,
    FIRST_SECRET,
    HEALTHY_REPLICAS,
    INTERACTIVE_COMMAND,
    INTERACTIVE_CONFIRMATION,
    INTERACTIVE_RESPONSE,
    KNOWN_GAPS,
    MULTISTEP_COMMAND,
    PASSWORD_PROMPT,
    PLATFORMS,
    SECOND_COMMAND,
    SECOND_SECRET,
    SHOW_VERSION_COMMAND,
    UNDEFINED_COMMAND,
    expected_clock_output,
    expected_config_prompt,
    expected_default_prompt,
    expected_version_output,
)
from nornir_scrapli.result import ScrapliResult
from nornir_scrapli.tasks import (
    get_prompt,
    send_command,
    send_commands,
    send_commands_from_file,
    send_config,
    send_configs,
    send_configs_from_file,
    send_interactive,
    send_prompted_input,
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
        assert isinstance(host_result.scrapli_response, CliResult)
        assert host_result.scrapli_response.inputs == [SHOW_VERSION_COMMAND]


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
        assert host_result.scrapli_response.inputs == [
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
        assert host_result.scrapli_response.inputs == [
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
        assert isinstance(host_result.scrapli_response, CliResult)
        assert host_result.scrapli_response.inputs == list(CONFIG_LINES)
        assert host_result.scrapli_response.results == ["", ""]
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
        assert host_result.scrapli_response.inputs == list(CONFIG_LINES)
        assert host_result.scrapli_response.results == ["", ""]
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
        assert host_result.scrapli_response.inputs == list(CONFIG_LINES)
        assert host_result.scrapli_response.results == ["", ""]
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
        assert type(host_result) is ScrapliResult
        assert host_result.failed is False
        assert host_result.changed is True
        assert isinstance(host_result.result, str)
        assert isinstance(host_result.scrapli_response, CliResult)
        assert host_result.result == host_result.scrapli_response.result
        assert host_result.scrapli_response.failed is False
        assert host_result.scrapli_response.inputs == [
            "\n".join([INTERACTIVE_COMMAND, INTERACTIVE_RESPONSE])
        ]
        confirmation = INTERACTIVE_CONFIRMATION.replace(" [confirm]", "\r\n[confirm]")
        assert confirmation in host_result.scrapli_response.result
        assert host_result.scrapli_response.result == (
            f"{INTERACTIVE_COMMAND}\r\n{confirmation}{INTERACTIVE_RESPONSE}\r\n"
            f"Logging cleared for {host_name}\r\n{expected_default_prompt(host_name, platform)}"
        )


@pytest.mark.parametrize("platform", PLATFORM_CASES)
def test_send_prompted_input(healthy_platform_nornir, platform):
    result = healthy_platform_nornir.run(
        task=send_prompted_input,
        input_=INTERACTIVE_COMMAND,
        prompt="[confirm]",
        prompt_pattern="",
        response=INTERACTIVE_RESPONSE,
    )

    assert not result.failed
    assert len(result) == HEALTHY_REPLICAS
    for host_name, multi_result in result.items():
        host_result = multi_result[0]
        assert host_result.changed is True
        assert isinstance(host_result.result, str)
        assert isinstance(host_result.scrapli_response, CliResult)
        assert f"Logging cleared for {host_name}" in host_result.result
        assert host_result.result == host_result.scrapli_response.result


@pytest.mark.parametrize("platform", PLATFORM_CASES)
@pytest.mark.parametrize("config_task", [send_config, send_configs, send_configs_from_file])
def test_config_dry_run_restores_mode_without_sending_configs(
    healthy_platform_nornir,
    platform,
    config_task,
):
    if config_task is send_config:
        options = {"config": "\n".join(CONFIG_LINES)}
    elif config_task is send_configs:
        options = {"configs": list(CONFIG_LINES)}
    else:
        options = {"file": "does-not-exist-config.txt"}
    result = healthy_platform_nornir.run(task=config_task, dry_run=True, **options)
    prompts = healthy_platform_nornir.run(task=get_prompt)

    assert not result.failed
    assert not prompts.failed
    assert len(result) == HEALTHY_REPLICAS
    for host_name, multi_result in result.items():
        host_result = multi_result[0]
        assert host_result.result is None
        assert host_result.scrapli_response is None
        assert host_result.changed is False
        assert prompts[host_name][0].result == expected_default_prompt(host_name, platform)
        recording = Path(
            healthy_platform_nornir.inventory.hosts[host_name].data["recorder_path"]
        ).read_text()
        assert "configure" in recording
        assert not any(line in recording for line in CONFIG_LINES)


@pytest.mark.parametrize("platform", ["cisco_iosxe", "cisco_nxos", "arista_eos"])
def test_dry_run_restores_nondefault_exec_mode(healthy_platform_nornir, platform):
    def dry_run_from_exec(task):
        connection = task.host.get_connection("scrapli", task.nornir.config)
        entered = connection.enter_mode(requested_mode="exec")
        assert not entered.failed
        assert connection.get_prompt().result == task.host.name + ">"
        return send_configs(task, configs=list(CONFIG_LINES), dry_run=True)

    result = healthy_platform_nornir.run(task=dry_run_from_exec)
    prompts = healthy_platform_nornir.run(task=get_prompt)
    assert not result.failed
    assert not prompts.failed
    for host_name, multi_result in result.items():
        assert multi_result[0].changed is False
        assert prompts[host_name][0].result == host_name + ">"
        recording = Path(
            healthy_platform_nornir.inventory.hosts[host_name].data["recorder_path"]
        ).read_text()
        assert "configure" in recording
        assert not any(line in recording for line in CONFIG_LINES)


@pytest.mark.parametrize("platform", PLATFORM_CASES)
def test_repeated_hidden_prompts(healthy_platform_nornir, platform):
    def transfer(task):
        return send_interactive(
            task,
            interact_events=[
                (MULTISTEP_COMMAND, PASSWORD_PROMPT, False),
                (FIRST_SECRET, PASSWORD_PROMPT, True),
                (
                    SECOND_SECRET,
                    f"^{escape(expected_default_prompt(task.host.name, platform))}$",
                    True,
                ),
            ],
        )

    result = healthy_platform_nornir.run(task=transfer)
    assert not result.failed
    assert len(result) == HEALTHY_REPLICAS
    for host_name, multi_result in result.items():
        host_result = multi_result[0]
        native = host_result.scrapli_response
        assert host_result.changed is True
        assert f"Transfer complete for {host_name}" in host_result.result
        assert native.inputs == [MULTISTEP_COMMAND + "\n[redacted]\n[redacted]"]
        assert native.result_raw == host_result.result.encode()
        for secret in (FIRST_SECRET, SECOND_SECRET):
            assert secret not in host_result.result
            assert secret.encode() not in native.result_raw


@pytest.mark.parametrize("platform", PLATFORM_CASES)
def test_definition_failure_indicator(healthy_platform_nornir, platform):
    result = healthy_platform_nornir.run(task=send_command, command=UNDEFINED_COMMAND)
    assert result.failed
    assert len(result.failed_hosts) == HEALTHY_REPLICAS
    for multi_result in result.values():
        host_result = multi_result[0]
        assert host_result.exception is None
        assert host_result.changed is False
        assert host_result.scrapli_response.failed is True
        assert host_result.scrapli_response.results_failed_indicator
        assert host_result.scrapli_response.inputs == [UNDEFINED_COMMAND]


@pytest.mark.parametrize("platform", PLATFORM_CASES)
@pytest.mark.parametrize("stop_on_indicated_failure", [True, False])
def test_partial_batch_failure(healthy_platform_nornir, platform, stop_on_indicated_failure):
    result = healthy_platform_nornir.run(
        task=send_commands,
        commands=[SHOW_VERSION_COMMAND, UNDEFINED_COMMAND, SECOND_COMMAND],
        stop_on_indicated_failure=stop_on_indicated_failure,
    )
    assert result.failed
    for host_name, multi_result in result.items():
        host_result = multi_result[0]
        native = host_result.scrapli_response
        assert host_result.exception is None
        assert host_result.changed is False
        assert native.failed is True
        assert native.inputs == (
            [SHOW_VERSION_COMMAND, UNDEFINED_COMMAND]
            if stop_on_indicated_failure
            else [SHOW_VERSION_COMMAND, UNDEFINED_COMMAND, SECOND_COMMAND]
        )
        assert native.results[0] == expected_version_output(host_name)
        assert len(native.results) == (2 if stop_on_indicated_failure else 3)
        if not stop_on_indicated_failure:
            assert native.results[-1] == expected_clock_output(host_name)
        assert host_result.result == "\n\n".join(native.results)

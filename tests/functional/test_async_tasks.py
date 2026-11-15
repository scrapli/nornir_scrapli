"""Exercise native async tasks and cleanup against real SSH devices."""

import asyncio
from pathlib import Path
from re import escape

import pytest

from functional.constants import (
    AUTH_FAILURE_HOST,
    CONFIG_LINES,
    INTERACTIVE_COMMAND,
    INTERACTIVE_CONFIRMATION,
    INTERACTIVE_RESPONSE,
    SECOND_COMMAND,
    SHOW_VERSION_COMMAND,
    TIMEOUT_FAILURE_HOST,
    expected_clock_output,
    expected_default_prompt,
    expected_version_output,
)
from nornir import InitNornir
from nornir_scrapli import async_tasks


@pytest.fixture
def async_nornir(functional_inventory_files, fake_nos_lab):
    files = functional_inventory_files
    nr = InitNornir(
        runner={"plugin": "asyncio", "options": {"num_workers": 4}},
        inventory={
            "plugin": "SimpleInventory",
            "options": {
                "host_file": str(files.hosts),
                "group_file": str(files.groups),
                "defaults_file": str(files.defaults),
            },
        },
        logging={"enabled": False},
    )
    drivers = []

    def track(driver):
        drivers.append(driver)

    for host in nr.inventory.hosts.values():
        options = host.get_connection_parameters("scrapli")
        options.extras = {**options.extras, "transport": "asyncssh", "on_init": track}
        host.connection_options["scrapli"] = options
    yield nr
    assert all(not host.connections for host in nr.inventory.hosts.values())
    assert all(not driver.isalive() for driver in drivers)


@pytest.mark.parametrize(
    "platform", ["cisco_iosxe", "arista_eos", "cisco_iosxr", "cisco_nxos", "juniper_junos"]
)
def test_async_cli_workflow(async_nornir, platform):
    nr = async_nornir.filter(role="healthy", platform=platform)
    command_file = Path(__file__).parent / "files" / "send_commands_from_file"
    config_file = Path(__file__).parent / "files" / "send_configs_from_file"

    async def workflow(task):
        version = await task.arun(task=async_tasks.send_command, command=SHOW_VERSION_COMMAND)
        assert version[0].result == expected_version_output(task.host.name)
        multiple = await task.arun(
            task=async_tasks.send_commands, commands=[SHOW_VERSION_COMMAND, SECOND_COMMAND]
        )
        assert multiple[0].result == "\n\n".join(
            [expected_version_output(task.host.name), expected_clock_output(task.host.name)]
        )
        from_file = await task.arun(
            task=async_tasks.send_commands_from_file, file=str(command_file)
        )
        assert from_file[0].result == multiple[0].result
        prompt = await task.arun(task=async_tasks.get_prompt)
        assert prompt[0].result == expected_default_prompt(task.host.name, platform)
        dry = await task.arun(
            task=async_tasks.send_configs, configs=list(CONFIG_LINES), dry_run=True
        )
        assert dry[0].result is None
        assert dry[0].changed is False
        for func, args in (
            (async_tasks.send_config, {"config": "\n".join(CONFIG_LINES)}),
            (async_tasks.send_configs, {"configs": list(CONFIG_LINES)}),
            (async_tasks.send_configs_from_file, {"file": str(config_file)}),
        ):
            configured = await task.arun(task=func, **args)
            assert configured[0].changed is True
            assert configured[0].result == "\n".join(CONFIG_LINES) + "\n"
        interactive = await task.arun(
            task=async_tasks.send_interactive,
            interact_events=[
                (INTERACTIVE_COMMAND, INTERACTIVE_CONFIRMATION.split()[-1], False),
                (
                    INTERACTIVE_RESPONSE,
                    f"^{escape(expected_default_prompt(task.host.name, platform))}$",
                    False,
                ),
            ],
            privilege_level="exec" if platform == "juniper_junos" else "privilege_exec",
        )
        assert f"Logging cleared for {task.host.name}" in interactive[0].result.result

    async def exercise():
        async with nr:
            result = await nr.arun(task=workflow)
            assert not result.failed, {
                host: values for host, values in result.items() if values.failed
            }

    asyncio.run(exercise())


def test_async_host_failures_do_not_stop_healthy_hosts(async_nornir):
    async def exercise():
        async with async_nornir:
            result = await async_nornir.arun(
                task=async_tasks.send_command, command=SHOW_VERSION_COMMAND
            )
            assert set(result.failed_hosts) == {AUTH_FAILURE_HOST, TIMEOUT_FAILURE_HOST}
            for name, values in result.items():
                if name not in result.failed_hosts:
                    assert values[0].result == expected_version_output(name)
            await async_nornir.aclose_connections(on_good=True, on_failed=True)

    asyncio.run(exercise())

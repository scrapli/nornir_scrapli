import importlib

import pytest
from scrapli.driver.core import AsyncIOSXEDriver, IOSXEDriver
from scrapli.response import MultiResponse, Response
from scrapli_cfg.platform.core.cisco_iosxe.async_platform import AsyncScrapliCfgIOSXE
from scrapli_cfg.response import ScrapliCfgResponse

from nornir.core.exceptions import ConnectionModeMismatchError
from nornir.core.task import Result
from nornir.plugins.runners import AsyncioRunner, SerialRunner
from nornir_scrapli.tasks import send_command as sync_send_command


def response(command, output="output", failed=False):
    value = Response(host="router", channel_input=command, failed_when_contains="ERROR")
    value.record_response(b"ERROR" if failed else output.encode())
    return value


def async_nr(nr):
    nr = nr.filter(name="sea-ios-1").with_runner(AsyncioRunner(num_workers=2))
    host = nr.inventory.hosts["sea-ios-1"]
    options = host.get_connection_parameters("scrapli")
    options.extras = {**options.extras, "transport": "asyncssh"}
    host.connection_options["scrapli"] = options
    return nr


@pytest.fixture
def drivers(monkeypatch):
    async def no_io(self):
        pass

    monkeypatch.setattr(AsyncIOSXEDriver, "open", no_io)
    monkeypatch.setattr(AsyncIOSXEDriver, "close", no_io)
    monkeypatch.setattr(AsyncScrapliCfgIOSXE, "prepare", no_io)


@pytest.mark.parametrize(
    "name,arguments,method,input_key,expected,changed",
    [
        ("send_command", {"command": "show version"}, "send_command", "command", "output", False),
        (
            "send_commands",
            {"commands": ["one", "two"]},
            "send_commands",
            "commands",
            "output\n\noutput",
            False,
        ),
        ("send_commands_from_file", {}, "send_commands", "commands", "output\n\noutput", False),
        ("send_config", {"config": "one\ntwo"}, "send_config", "config", "one\ntwo\n", True),
        (
            "send_configs",
            {"configs": ["one", "two"]},
            "send_configs",
            "configs",
            "one\ntwo\n",
            True,
        ),
        ("send_configs_from_file", {}, "send_configs", "configs", "one\ntwo\n", True),
    ],
)
@pytest.mark.asyncio
async def test_async_cli_response_parity(
    nornir, drivers, monkeypatch, tmp_path, name, arguments, method, input_key, expected, changed
):
    tasks = importlib.import_module("nornir_scrapli.async_tasks")
    nr = async_nr(nornir)
    if "from_file" in name:
        path = tmp_path / "commands"
        path.write_text("one\ntwo\n")
        arguments = {"file": str(path)}

    async def send(self, **kwargs):
        assert kwargs["strip_prompt"] is False
        assert kwargs["failed_when_contains"] == "ERROR"
        assert kwargs["timeout_ops"] == 7
        inputs = kwargs[input_key]
        if input_key in {"command", "config"}:
            assert inputs == ("show version" if input_key == "command" else "one\ntwo")
            return response(inputs, "\n" if changed else "output")
        assert inputs == ["one", "two"]
        values = MultiResponse()
        values.extend(response(item, "" if changed else "output") for item in inputs)
        return values

    monkeypatch.setattr(AsyncIOSXEDriver, method, send)

    async with nr:
        result = await nr.arun(
            task=getattr(tasks, name),
            **arguments,
            strip_prompt=False,
            failed_when_contains="ERROR",
            timeout_ops=7,
        )
        value = result["sea-ios-1"][0]
        assert not value.failed, value.exception
        assert value.result == expected
        assert value.changed is changed
        assert isinstance(value.scrapli_response, (Response, MultiResponse))
    assert not nr.inventory.hosts["sea-ios-1"].connections


@pytest.mark.asyncio
async def test_async_prompt_and_interactive_nested_tasks(nornir, drivers, monkeypatch):
    tasks = importlib.import_module("nornir_scrapli.async_tasks")
    nr = async_nr(nornir)

    async def prompt(self):
        return "router#"

    async def interact(self, **kwargs):
        assert kwargs == {
            "interact_events": [("clear", "confirm", False)],
            "failed_when_contains": None,
            "privilege_level": "",
            "timeout_ops": None,
        }
        return response("clear", "cleared")

    monkeypatch.setattr(AsyncIOSXEDriver, "get_prompt", prompt)
    monkeypatch.setattr(AsyncIOSXEDriver, "send_interactive", interact)

    async def workflow(task):
        await task.arun(task=tasks.get_prompt)
        await task.arun(task=tasks.send_interactive, interact_events=[("clear", "confirm", False)])
        return Result(host=task.host, result="done")

    async with nr:
        result = await nr.arun(task=workflow)
        values = result["sea-ios-1"]
        assert not values.failed
        assert values[1].result == "router#"
        assert type(values[2]) is Result
        assert values[2].result is values[2].scrapli_response
        assert values[2].result.result == "cleared"
        assert values[2].changed is True


@pytest.mark.parametrize("name", ["send_config", "send_configs", "send_configs_from_file"])
@pytest.mark.parametrize("global_dry_run,explicit", [(False, True), (True, None)])
@pytest.mark.asyncio
async def test_async_config_dry_run(nornir, drivers, monkeypatch, name, global_dry_run, explicit):
    tasks = importlib.import_module("nornir_scrapli.async_tasks")
    nr = async_nr(nornir)
    nr.data.dry_run = global_dry_run
    privileges = []

    async def acquire(self, desired_priv):
        privileges.append(desired_priv)

    async def forbidden(self, **kwargs):
        raise AssertionError("dry run must not send configuration")

    monkeypatch.setattr(AsyncIOSXEDriver, "acquire_priv", acquire)
    monkeypatch.setattr(AsyncIOSXEDriver, "send_config", forbidden)
    monkeypatch.setattr(AsyncIOSXEDriver, "send_configs", forbidden)
    args = {
        "send_config": {"config": "one"},
        "send_configs": {"configs": ["one"]},
        "send_configs_from_file": {"file": "/must-not-read-this"},
    }[name]

    async with nr:
        result = await nr.arun(task=getattr(tasks, name), **args, dry_run=explicit)
        value = result["sea-ios-1"][0]
        assert not value.failed, value.exception
        assert value.result is None
        assert value.changed is False
        assert value.scrapli_response is None
        assert privileges == ["configuration", "privilege_exec"]


@pytest.mark.asyncio
async def test_async_failed_response_is_recorded(nornir, drivers, monkeypatch):
    tasks = importlib.import_module("nornir_scrapli.async_tasks")
    nr = async_nr(nornir)

    async def send(self, **kwargs):
        return response("bad", failed=True)

    monkeypatch.setattr(AsyncIOSXEDriver, "send_command", send)

    async with nr:
        result = await nr.arun(task=tasks.send_command, command="bad")
        assert result["sea-ios-1"].failed
        assert result["sea-ios-1"][0].result == "ERROR"
        await nr.aclose_connections(on_good=True, on_failed=True)


@pytest.mark.parametrize("opened_mode", ["sync", "asyncio"])
@pytest.mark.asyncio
async def test_wrong_mode_task_records_named_error(nornir, drivers, monkeypatch, opened_mode):
    tasks = importlib.import_module("nornir_scrapli.async_tasks")
    nr = async_nr(nornir)
    host = nr.inventory.hosts["sea-ios-1"]
    monkeypatch.setattr(IOSXEDriver, "open", lambda self: None)
    monkeypatch.setattr(IOSXEDriver, "close", lambda self: None)

    if opened_mode == "sync":
        host.connection_options["scrapli"].extras["transport"] = "system"
        host.get_connection("scrapli", nr.config)
        results = await nr.arun(task=tasks.send_command, command="show version")
        host.close_connection("scrapli")
    else:
        await host.aget_connection("scrapli", nr.config)
        results = nr.with_runner(SerialRunner()).run(task=sync_send_command, command="show version")
        await host.aclose_connections()
    assert isinstance(results["sea-ios-1"][0].exception, ConnectionModeMismatchError)


@pytest.mark.parametrize(
    "name,method,args,expected,changed",
    [
        ("cfg_get_version", "get_version", {}, "version", False),
        ("cfg_get_config", "get_config", {"source": "startup"}, "config", False),
        (
            "cfg_load_config",
            "load_config",
            {"config": "candidate", "replace": True, "filesystem": "flash"},
            "loaded",
            False,
        ),
        ("cfg_diff_config", "diff_config", {"source": "startup"}, "device diff", False),
        ("cfg_commit_config", "commit_config", {"source": "startup"}, "committed", True),
        ("cfg_abort_config", "abort_config", {}, "aborted", False),
    ],
)
@pytest.mark.asyncio
async def test_async_cfg_response_parity(
    nornir, drivers, monkeypatch, name, method, args, expected, changed
):
    tasks = importlib.import_module("nornir_scrapli.async_tasks")
    nr = async_nr(nornir)

    async def operation(self, **kwargs):
        assert kwargs == args
        if method == "get_version":
            return response("version", "version")
        value = ScrapliCfgResponse(host="router")
        value.record_response(scrapli_responses=[response(method, expected)], result=expected)
        if method == "diff_config":
            value.device_diff = "device diff"
        return value

    monkeypatch.setattr(AsyncScrapliCfgIOSXE, method, operation)

    async with nr:
        result = await nr.arun(task=getattr(tasks, name), **args)
        value = result["sea-ios-1"][0]
        assert not value.failed, value.exception
        assert value.result == expected
        assert value.changed is changed

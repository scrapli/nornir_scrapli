import pytest
from conftest import asyncify
from scrapli import Cli
from scrapli.cli import InputHandling
from scrapli.ffi_types import Cancel

from nornir.core.exceptions import ConnectionModeMismatchError
from nornir_scrapli import async_tasks, tasks


@pytest.fixture(autouse=True)
def _async_open(monkeypatch):
    monkeypatch.setattr(Cli, "open_async", asyncify(lambda self: None))
    monkeypatch.setattr(Cli, "close_async", asyncify(lambda self: None))


def _run_host(result):
    return result["sea-ios-1"][0]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name,kwargs,method,key,value",
    [
        ("send_command", {"command": "show version"}, "send_input", "input_", "show version"),
        ("send_commands", {"commands": ["a", "b"]}, "send_inputs", "inputs", ["a", "b"]),
        (
            "send_commands_from_file",
            {"file": "commands.txt"},
            "send_inputs_from_file",
            "f",
            "commands.txt",
        ),
        ("get_prompt", {}, "get_prompt", None, None),
    ],
)
async def test_command_tasks_match_sync(
    nornir, async_nornir, monkeypatch, make_cli_result, name, kwargs, method, key, value
):
    native = make_cli_result(["a", "b"], ["one", "two"], "failed")
    calls = []

    def send(self, **options):
        calls.append(options)
        return native

    monkeypatch.setattr(Cli, "open", lambda self: None)
    monkeypatch.setattr(Cli, method, send)
    monkeypatch.setattr(Cli, f"{method}_async", asyncify(send))
    cancel = Cancel()
    options = {"operation_timeout_ns": 0, "cancel": cancel}
    if name != "get_prompt":
        options.update(
            requested_mode="exec", input_handling=InputHandling.EXACT, retain_trailing_prompt=True
        )
    result = _run_host(
        await async_nornir.arun(task=getattr(async_tasks, name), **kwargs, **options)
    )
    await async_nornir.aclose_connections(on_failed=True)
    nornir.data.reset_failed_hosts()
    expected = _run_host(nornir.run(task=getattr(tasks, name), **kwargs, **options))
    assert result.exception is None
    assert result.result == expected.result
    assert result.failed is expected.failed is True
    assert result.changed is expected.changed is False
    assert result.scrapli_response is native
    assert calls[0] == calls[1]
    assert calls[0]["cancel"] is cancel
    if key:
        assert calls[0][key] == value


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name,kwargs,method,key,value",
    [
        ("send_config", {"config": "a\nb"}, "send_inputs", "inputs", ["a", "b"]),
        ("send_configs", {"configs": ["a", "b"]}, "send_inputs", "inputs", ["a", "b"]),
        (
            "send_configs_from_file",
            {"file": "config.txt"},
            "send_inputs_from_file",
            "f",
            "config.txt",
        ),
    ],
)
async def test_config_tasks(
    async_nornir, monkeypatch, make_cli_result, name, kwargs, method, key, value
):
    calls = []
    native = make_cli_result(["a", "b"], ["", ""])

    def send(self, **options):
        calls.append(options)
        return native

    monkeypatch.setattr(Cli, f"{method}_async", asyncify(send))
    result = _run_host(
        await async_nornir.arun(
            task=getattr(async_tasks, name),
            **kwargs,
            requested_mode="configuration",
            operation_timeout_ns=0,
        )
    )
    assert result.exception is None
    assert result.result == "a\nb\n"
    assert result.changed is True
    assert result.scrapli_response is native
    assert calls[0][key] == value
    assert calls[0]["retain_input"] is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name,kwargs",
    [
        ("send_config", {"config": "a"}),
        ("send_configs", {"configs": ["a"]}),
        ("send_configs_from_file", {"file": "missing.txt"}),
    ],
)
@pytest.mark.parametrize(
    "global_dry,explicit,dry", [(True, None, True), (False, True, True), (True, False, False)]
)
async def test_dry_run_restores_actual_mode(
    async_nornir, monkeypatch, make_cli_result, name, kwargs, global_dry, explicit, dry
):
    async_nornir.data.dry_run = global_dry
    modes = []
    inputs = []

    def enter(self, requested_mode, **kw):
        modes.append(requested_mode)
        return make_cli_result()

    def send(self, **kw):
        inputs.append(kw)
        return make_cli_result(["a"], [""])

    monkeypatch.setattr(
        Cli, "get_prompt_async", asyncify(lambda self, **kw: make_cli_result([""], ["router>"]))
    )
    monkeypatch.setattr(Cli, "enter_mode_async", asyncify(enter))
    monkeypatch.setattr(Cli, "send_inputs_async", asyncify(send))
    monkeypatch.setattr(Cli, "send_inputs_from_file_async", asyncify(send))
    result = _run_host(
        await async_nornir.arun(task=getattr(async_tasks, name), **kwargs, dry_run=explicit)
    )
    assert result.exception is None
    assert result.failed is False
    assert result.changed is (not dry)
    assert modes == (["configuration", "exec"] if dry else [])
    assert len(inputs) == (0 if dry else 1)
    if dry:
        assert result.result is None
        assert result.scrapli_response is None


@pytest.mark.asyncio
async def test_mode_restore_failure_keeps_entry_failure(async_nornir, monkeypatch, make_cli_result):
    from scrapli.exceptions import OperationException

    primary = OperationException("entry failed")
    cleanup = OperationException("restore failed")

    def enter(self, requested_mode, **kwargs):
        raise primary if requested_mode == "configuration" else cleanup

    monkeypatch.setattr(
        Cli, "get_prompt_async", asyncify(lambda self, **kw: make_cli_result([""], ["router>"]))
    )
    monkeypatch.setattr(Cli, "enter_mode_async", asyncify(enter))
    result = _run_host(
        await async_nornir.arun(task=async_tasks.send_configs, configs=["a"], dry_run=True)
    )
    assert result.failed is True
    assert result.exception is primary
    assert primary.__cause__ is cleanup


@pytest.mark.asyncio
async def test_prompted_input(async_nornir, monkeypatch, make_cli_result):
    native = make_cli_result(["reload"], ["Proceed? y\nrouter#"])
    calls = []

    def send(self, **kwargs):
        calls.append(kwargs)
        return native

    monkeypatch.setattr(Cli, "send_prompted_input_async", asyncify(send))
    result = _run_host(
        await async_nornir.arun(
            task=async_tasks.send_prompted_input,
            input_="reload",
            prompt="Proceed?",
            prompt_pattern="",
            response="y",
            hidden_response=True,
        )
    )
    assert result.exception is None
    assert result.changed is True
    assert result.scrapli_response is native
    assert calls[0]["hidden_response"] is True


@pytest.mark.asyncio
async def test_send_interactive_uses_async_callback(async_nornir, monkeypatch, make_cli_result):
    writes = []
    modes = []
    monkeypatch.setattr(Cli, "write_and_return", lambda self, input_: writes.append(input_))

    def enter(self, requested_mode, **kwargs):
        modes.append(requested_mode)
        return make_cli_result()

    async def read(self, callbacks, **kwargs):
        assert kwargs["operation_timeout_ns"] == 0
        callback = callbacks[0]
        assert callback.callback is None
        accumulated = ""
        for chunk in ["Pass", "word:", "Password:", "secret\nrouter#"]:
            accumulated += chunk
            await callback.callback_async(self, chunk, accumulated)
        assert callback.completes is True
        return make_cli_result([""], [accumulated])

    monkeypatch.setattr(Cli, "enter_mode_async", asyncify(enter))
    monkeypatch.setattr(Cli, "read_with_callbacks_async", read)
    result = _run_host(
        await async_nornir.arun(
            task=async_tasks.send_interactive,
            interact_events=[
                ("copy", "Password:"),
                ("user", "Password:"),
                ("secret", "router#", True),
            ],
            requested_mode="privileged_exec",
            operation_timeout_ns=0,
        )
    )
    assert result.exception is None
    assert modes == ["privileged_exec"]
    assert writes == ["copy", "user", "secret"]
    assert result.changed is True
    assert "secret" not in result.result
    assert "secret" not in str(result.scrapli_response.inputs)


@pytest.mark.asyncio
async def test_send_interactive_incomplete_fails(async_nornir, monkeypatch, make_cli_result):
    monkeypatch.setattr(Cli, "write_and_return", lambda self, input_: None)
    monkeypatch.setattr(
        Cli,
        "read_with_callbacks_async",
        asyncify(lambda self, **kwargs: make_cli_result([""], ["nothing"])),
    )
    result = _run_host(
        await async_nornir.arun(
            task=async_tasks.send_interactive, interact_events=[("copy", "Password:")]
        )
    )
    assert "ended before the final expected prompt" in str(result.exception)


@pytest.mark.asyncio
async def test_invalid_events_fail_before_connecting(async_nornir, monkeypatch):
    result = _run_host(
        await async_nornir.arun(task=async_tasks.send_interactive, interact_events=[])
    )
    assert isinstance(result.exception, ValueError)
    assert async_nornir.inventory.hosts["sea-ios-1"].connections == {}


@pytest.mark.asyncio
async def test_nested_subtasks(async_nornir, monkeypatch, make_cli_result):
    monkeypatch.setattr(
        Cli, "get_prompt_async", asyncify(lambda self, **kw: make_cli_result([""], ["router#"]))
    )
    monkeypatch.setattr(
        Cli, "send_input_async", asyncify(lambda self, **kw: make_cli_result(["show"], ["out"]))
    )

    async def workflow(task):
        prompt = await task.arun(async_tasks.get_prompt)
        await task.arun(async_tasks.send_command, command="show")
        return prompt.result

    result = await async_nornir.arun(task=workflow)
    multi = result["sea-ios-1"]
    assert not result.failed
    assert multi[0].result == "router#"
    assert [r.name for r in multi[1:]] == ["get_prompt", "send_command"]
    assert multi[2].result == "out"


@pytest.mark.asyncio
async def test_sync_task_on_async_connection_fails(async_nornir, monkeypatch, make_cli_result):
    monkeypatch.setattr(
        Cli, "get_prompt_async", asyncify(lambda self, **kw: make_cli_result([""], ["router#"]))
    )

    async def mixed(task):
        await task.arun(async_tasks.get_prompt)
        task.run(tasks.get_prompt)

    result = await async_nornir.arun(task=mixed)
    multi = result["sea-ios-1"]
    assert result.failed
    assert isinstance(multi[-1].exception, ConnectionModeMismatchError)

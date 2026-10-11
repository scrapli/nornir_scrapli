import pytest
from scrapli import Cli
from scrapli.cli import InputHandling
from scrapli.ffi_types import Cancel


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
def test_command_tasks(nornir, monkeypatch, make_cli_result, name, kwargs, method, key, value):
    from nornir_scrapli import tasks

    native = make_cli_result(["a", "b"], ["one", "two"], "failed")
    calls = []
    monkeypatch.setattr(Cli, "open", lambda self: None)

    def send(self, **options):
        calls.append(options)
        return native

    monkeypatch.setattr(Cli, method, send)
    cancel = Cancel()
    options = {"operation_timeout_ns": 0, "cancel": cancel}
    if name != "get_prompt":
        options.update(
            requested_mode="exec", input_handling=InputHandling.EXACT, retain_trailing_prompt=True
        )
    result = nornir.run(task=getattr(tasks, name), **kwargs, **options)["sea-ios-1"][0]
    assert result.exception is None
    assert result.result == ("one\ntwo" if name == "get_prompt" else "one\n\ntwo")
    assert result.failed is True
    assert result.changed is False
    assert result.scrapli_response is native
    assert calls[0]["operation_timeout_ns"] == 0
    assert calls[0]["cancel"] is cancel
    if key:
        assert calls[0][key] == value
        assert calls[0]["requested_mode"] == "exec"
        assert calls[0]["retain_trailing_prompt"] is True


@pytest.mark.parametrize(
    "key", ["timeout_ops", "strip_prompt", "privilege_level", "eager", "failed_when_contains"]
)
def test_old_arguments_fail(nornir, monkeypatch, key):
    from nornir_scrapli.tasks import send_command

    monkeypatch.setattr(Cli, "open", lambda self: None)
    result = nornir.run(task=send_command, command="show", **{key: True})["sea-ios-1"][0]
    assert isinstance(result.exception, TypeError)

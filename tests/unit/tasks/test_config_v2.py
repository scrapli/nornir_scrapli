import pytest
from scrapli import Cli


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
def test_config_tasks(nornir, monkeypatch, make_cli_result, name, kwargs, method, key, value):
    from nornir_scrapli import tasks

    calls = []
    monkeypatch.setattr(Cli, "open", lambda self: None)
    native = make_cli_result(["a", "b"], ["", ""])

    def send(self, **options):
        calls.append(options)
        return native

    monkeypatch.setattr(Cli, method, send)
    result = nornir.run(
        task=getattr(tasks, name), **kwargs, requested_mode="configuration", operation_timeout_ns=0
    )["sea-ios-1"][0]
    assert result.exception is None
    assert result.result == "a\nb\n"
    assert result.changed is True
    assert result.scrapli_response is native
    assert calls[0][key] == value
    assert calls[0]["retain_input"] is False
    assert calls[0]["operation_timeout_ns"] == 0


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
def test_dry_run_restores_actual_mode(
    nornir, monkeypatch, make_cli_result, name, kwargs, global_dry, explicit, dry
):
    from nornir_scrapli import tasks

    nornir.data.dry_run = global_dry
    modes = []
    inputs = []
    monkeypatch.setattr(Cli, "open", lambda self: None)
    monkeypatch.setattr(Cli, "get_prompt", lambda self, **kw: make_cli_result([""], ["router>"]))

    def enter(self, requested_mode, **kw):
        modes.append(requested_mode)
        return make_cli_result()

    def send(self, **kw):
        inputs.append(kw)
        return make_cli_result(["a"], [""])

    monkeypatch.setattr(Cli, "enter_mode", enter)
    monkeypatch.setattr(Cli, "send_inputs", send)
    monkeypatch.setattr(Cli, "send_inputs_from_file", send)
    result = nornir.run(task=getattr(tasks, name), **kwargs, dry_run=explicit)["sea-ios-1"][0]
    assert result.exception is None
    assert result.failed is False
    assert result.changed is (not dry)
    assert modes == (["configuration", "exec"] if dry else [])
    assert len(inputs) == (0 if dry else 1)
    if dry:
        assert result.result is None
        assert result.scrapli_response is None


def test_failed_mode_transition_is_failed_task(nornir, monkeypatch, make_cli_result):
    from nornir_scrapli.tasks import send_configs

    monkeypatch.setattr(Cli, "open", lambda self: None)
    monkeypatch.setattr(Cli, "get_prompt", lambda self, **kw: make_cli_result([""], ["router>"]))
    monkeypatch.setattr(
        Cli, "enter_mode", lambda self, **kw: make_cli_result(failed_indicator="error")
    )
    result = nornir.run(task=send_configs, configs=["a"], dry_run=True)["sea-ios-1"][0]
    assert result.failed is True
    assert result.changed is False


def test_mode_exclusions_and_ambiguity(monkeypatch, make_cli_result):
    from scrapli.exceptions import OperationException

    from nornir_scrapli.tasks.core.mode import get_current_mode

    connection = Cli("host", definition_file_or_name="cisco_iosxe")
    monkeypatch.setattr(
        Cli, "get_prompt", lambda self, **kw: make_cli_result([""], ["router(tcl)#"])
    )
    assert get_current_mode(connection) == "tclsh"
    connection.definition_string = (
        b"modes:\n - {name: one, prompt_pattern: '.*'}\n - {name: two, prompt_pattern: '.*'}\n"
    )
    with pytest.raises(OperationException, match="unambiguously"):
        get_current_mode(connection)


@pytest.mark.parametrize(
    "entry_failure,restore_failure",
    [
        ("exception", ""),
        ("", "exception"),
        ("", "reply"),
        ("exception", "exception"),
    ],
)
def test_mode_transition_failure_paths(
    nornir,
    monkeypatch,
    make_cli_result,
    entry_failure,
    restore_failure,
):
    from scrapli.exceptions import OperationException

    from nornir_scrapli.tasks import send_configs

    calls = []
    primary = OperationException("entry failed after changing mode")
    cleanup = OperationException("restore failed")
    monkeypatch.setattr(Cli, "open", lambda self: None)

    def prompt(self, **kwargs):
        calls.append("prompt")
        return make_cli_result([""], ["router>"])

    def enter(self, requested_mode, **kwargs):
        calls.append(requested_mode)
        if requested_mode == "configuration" and entry_failure:
            raise primary
        if requested_mode == "exec":
            if restore_failure == "exception":
                raise cleanup
            if restore_failure == "reply":
                return make_cli_result(failed_indicator="restore error")
        return make_cli_result()

    monkeypatch.setattr(Cli, "get_prompt", prompt)
    monkeypatch.setattr(Cli, "enter_mode", enter)
    monkeypatch.setattr(Cli, "send_inputs", lambda self, **kwargs: calls.append("config"))
    result = nornir.run(task=send_configs, configs=["a"], dry_run=True)["sea-ios-1"][0]
    assert result.failed is True
    assert calls == ["prompt", "configuration", "exec"]
    assert result.changed is False
    if entry_failure:
        assert result.exception is primary
        if restore_failure:
            assert primary.__cause__ is cleanup
    elif restore_failure == "exception":
        assert result.exception is cleanup


def test_unsupported_mode_pattern_fails_before_transitions(nornir, monkeypatch, make_cli_result):
    from nornir_scrapli.tasks import send_configs

    calls = []

    def open_connection(self):
        self.definition_string = b"modes:\n - {name: cli, prompt_pattern: '(?invalid)'}\n"

    monkeypatch.setattr(Cli, "open", open_connection)
    monkeypatch.setattr(
        Cli, "get_prompt", lambda self, **kwargs: make_cli_result([""], ["router#"])
    )
    monkeypatch.setattr(Cli, "enter_mode", lambda self, **kwargs: calls.append("mode"))
    monkeypatch.setattr(Cli, "send_inputs", lambda self, **kwargs: calls.append("config"))
    result = nornir.run(task=send_configs, configs=["a"], dry_run=True)["sea-ios-1"][0]
    assert result.failed is True
    assert "Unsupported" in str(result.exception)
    assert calls == []


def test_custom_definition_without_config_mode(nornir, monkeypatch, make_cli_result):
    from scrapli.exceptions import OperationException

    from nornir.core.inventory import ConnectionOptions
    from nornir_scrapli.tasks import send_configs

    nornir.inventory.hosts["sea-ios-1"].connection_options["scrapli"] = ConnectionOptions(
        extras={"definition": "default"},
    )
    calls = []
    monkeypatch.setattr(Cli, "open", lambda self: None)
    monkeypatch.setattr(
        Cli, "get_prompt", lambda self, **kwargs: make_cli_result([""], ["router#"])
    )

    def enter(self, requested_mode, **kwargs):
        calls.append(requested_mode)
        if requested_mode == "configuration":
            raise OperationException("No configuration mode in definition")
        return make_cli_result()

    monkeypatch.setattr(Cli, "enter_mode", enter)
    monkeypatch.setattr(Cli, "send_inputs", lambda self, **kwargs: calls.append("config"))
    result = nornir.run(task=send_configs, configs=["a"], dry_run=True)["sea-ios-1"][0]
    assert result.failed is True
    assert calls == ["configuration", "cli"]

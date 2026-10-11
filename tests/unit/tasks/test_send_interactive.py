import pytest
from scrapli import Cli


def test_ordered_repeated_fragmented_prompts(nornir, monkeypatch, make_cli_result):
    from nornir_scrapli.tasks import send_interactive

    writes = []
    monkeypatch.setattr(Cli, "open", lambda self: None)
    monkeypatch.setattr(Cli, "write_and_return", lambda self, input_: writes.append(input_))

    def read(self, callbacks, **kwargs):
        assert kwargs["operation_timeout_ns"] == 0
        assert kwargs.get("initial_input", "") == ""
        callback = callbacks[0]
        accumulated = ""
        for chunk in [
            "Pass",
            "word:",
            "Pass",
            "word:",
            "secret\n% Invalid input detected\nrouter#",
        ]:
            accumulated += chunk
            callback.callback(self, chunk, accumulated)
        assert callback.completes is True
        return make_cli_result([""], [accumulated])

    monkeypatch.setattr(Cli, "read_with_callbacks", read)
    result = nornir.run(
        task=send_interactive,
        interact_events=[("copy", "Password:"), ("user", "Password:"), ("secret", "router#", True)],
        operation_timeout_ns=0,
    )["sea-ios-1"][0]
    assert result.exception is None
    assert writes == ["copy", "user", "secret"]
    assert result.failed is True
    assert result.changed is True
    assert "secret" not in result.result
    assert "secret" not in result.scrapli_response.result_raw.decode()
    assert "secret" not in str(result.scrapli_response.inputs)


@pytest.mark.parametrize(
    "events", [[], [("one",)], [("one", "", False)], [("one", "prompt", "yes")]]
)
def test_invalid_events_fail_before_writing(nornir, monkeypatch, events):
    from nornir_scrapli.tasks import send_interactive

    writes = []
    monkeypatch.setattr(Cli, "open", lambda self: None)
    monkeypatch.setattr(Cli, "write_and_return", lambda self, input_: writes.append(input_))
    result = nornir.run(task=send_interactive, interact_events=events)["sea-ios-1"][0]
    assert isinstance(result.exception, ValueError)
    assert writes == []


def test_buffered_prompts_cannot_acknowledge_a_new_write(nornir, monkeypatch, make_cli_result):
    from nornir_scrapli.tasks import send_interactive

    writes = []
    monkeypatch.setattr(Cli, "open", lambda self: None)
    monkeypatch.setattr(Cli, "write_and_return", lambda self, input_: writes.append(input_))

    def read(self, callbacks, **kwargs):
        callback = callbacks[0]
        output = "Password:Password:router#"
        callback.callback(self, output, output)
        assert writes == ["copy", "user"]
        assert callback.completes is False
        output += "Password:"
        callback.callback(self, "Password:", output)
        assert writes == ["copy", "user", "secret"]
        assert callback.completes is False
        output += "router#"
        callback.callback(self, "router#", output)
        assert callback.completes is True
        return make_cli_result([""], [output])

    monkeypatch.setattr(Cli, "read_with_callbacks", read)
    result = nornir.run(
        task=send_interactive,
        interact_events=[("copy", "Password:"), ("user", "Password:"), ("secret", "router#", True)],
    )["sea-ios-1"][0]
    assert result.exception is None


def test_hidden_raw_echo_with_control_sequences_is_not_exposed(
    nornir, monkeypatch, make_cli_result
):
    import regex

    from nornir_scrapli.tasks import send_interactive

    monkeypatch.setattr(Cli, "open", lambda self: None)
    monkeypatch.setattr(Cli, "write_and_return", lambda self, input_: None)

    def read(self, callbacks, **kwargs):
        callbacks[0].callback(self, "secret\nrouter#", "secret\nrouter#")
        native = make_cli_result([""], ["secret\nrouter#"])
        native._results_raw = [b"sec\x1b[0mret\nrouter#"]
        return native

    monkeypatch.setattr(Cli, "read_with_callbacks", read)
    result = nornir.run(
        task=send_interactive,
        interact_events=[("secret", "router#", True)],
    )["sea-ios-1"][0]
    assert result.exception is None
    raw = result.scrapli_response.result_raw.decode()
    rendered = regex.sub(r"\x1b\[[0-9;]*m", "", raw)
    assert "secret" not in rendered

from scrapli import Cli


def test_prompted_input(nornir, monkeypatch, make_cli_result):
    from nornir_scrapli import tasks

    native = make_cli_result(["clear logging"], ["done"], "failed")
    calls = []
    monkeypatch.setattr(Cli, "open", lambda self: None)

    def send(self, **kwargs):
        calls.append(kwargs)
        return native

    monkeypatch.setattr(Cli, "send_prompted_input", send)
    result = nornir.run(
        task=tasks.send_prompted_input,
        input_="clear logging",
        prompt="[confirm]",
        prompt_pattern="",
        response="",
        hidden_response=True,
        operation_timeout_ns=0,
    )["sea-ios-1"][0]
    assert result.exception is None
    assert result.result == "done"
    assert result.failed is True
    assert result.changed is True
    assert result.scrapli_response is native
    assert calls[0]["hidden_response"] is True
    assert calls[0]["operation_timeout_ns"] == 0

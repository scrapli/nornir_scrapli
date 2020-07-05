import pytest

from nornir.core.exceptions import NornirExecutionError
from scrapli.driver.core import IOSXEDriver
from scrapli.response import Response


def test_send_commands(nornir, monkeypatch):
    from nornir_scrapli.tasks import send_commands

    def mock_open(cls):
        pass

    def mock_send_commands(cls, commands, strip_prompt, failed_when_contains, stop_on_failed):
        response = Response(host="fake_as_heck", channel_input=commands[0])
        response._record_response(b"some stuff about whatever")
        return [response]

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "send_commands", mock_send_commands)

    result = nornir.run(task=send_commands, commands=["show version"])
    assert result["sea-ios-1"][0].result == "some stuff about whatever"
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is False


def test_send_commands_not_list(nornir_raise_on_error, monkeypatch):
    from nornir_scrapli.tasks import send_commands

    def mock_open(cls):
        pass

    def mock_acquire_priv(cls, desired_priv, failed_when_contains="", stop_on_failed=False):
        pass

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "acquire_priv", mock_acquire_priv)

    with pytest.raises(NornirExecutionError) as exc:
        nornir_raise_on_error.run(task=send_commands, commands="show version")
    assert "expects a list of strings, got <class 'str'>" in str(exc.value)

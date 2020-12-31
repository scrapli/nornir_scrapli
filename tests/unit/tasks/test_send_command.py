from scrapli.driver.core import IOSXEDriver
from scrapli.response import Response


def test_send_command(nornir, monkeypatch):
    from nornir_scrapli.tasks import send_command

    def mock_open(cls):
        pass

    def mock_send_command(
        cls, command, strip_prompt, failed_when_contains, eager=False, timeout_ops=None
    ):
        response = Response(host="fake_as_heck", channel_input=command)
        response._record_response(b"some stuff about whatever")
        return response

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "send_command", mock_send_command)

    result = nornir.run(task=send_command, command="show version")
    assert result["sea-ios-1"].result == "some stuff about whatever"
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is False

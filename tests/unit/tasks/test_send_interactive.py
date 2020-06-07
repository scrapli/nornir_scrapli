from scrapli.driver.core import IOSXEDriver
from scrapli.response import Response


def test_send_interactive(nornir, monkeypatch):
    from nornir_scrapli.tasks import send_interactive

    def mock_open(cls):
        pass

    def mock_send_interactive(cls, interact_events, failed_when_contains=None, privilege_level=""):
        response = Response(
            host="fake_as_heck", channel_input=", ".join([event[0] for event in interact_events]),
        )
        response._record_response("clear logg\nClear logging buffer [confirm]\n\ncsr1000v#")
        return response

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "send_interactive", mock_send_interactive)

    result = nornir.run(
        task=send_interactive,
        interact_events=[("clear logg", "are you sure blah blah"), ("y", "csr1000#")],
    )
    assert (
        result["sea-ios-1"].result.result
        == "clear logg\nClear logging buffer [confirm]\n\ncsr1000v#"
    )
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is True

from scrapli.response import Response
from scrapli_netconf import NetconfDriver


def test_netconf_commit(nornir_netconf, monkeypatch):
    from nornir_scrapli.tasks import netconf_commit

    def mock_open(cls):
        pass

    def mock_commit(cls):
        response = Response(host="fake_as_heck", channel_input="blah")
        response.record_response(b"some stuff about whatever")
        return response

    monkeypatch.setattr(NetconfDriver, "open", mock_open)
    monkeypatch.setattr(NetconfDriver, "commit", mock_commit)

    result = nornir_netconf.run(task=netconf_commit)
    assert result["sea-ios-1"].result == "some stuff about whatever"
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is True

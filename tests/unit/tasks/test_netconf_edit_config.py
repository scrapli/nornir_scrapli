from scrapli.response import Response
from scrapli_netconf import NetconfDriver


def test_netconf_edit_config(nornir_netconf, monkeypatch):
    from nornir_scrapli.tasks import netconf_edit_config

    def mock_open(cls):
        pass

    def mock_get_config(cls, source):
        response = Response(host="fake_as_heck", channel_input="blah")
        response.record_response(b"some stuff about whatever")
        return response

    def mock_edit_config(cls, config, target):
        response = Response(host="fake_as_heck", channel_input="blah")
        response.record_response(b"some stuff about whatever")
        return response

    monkeypatch.setattr(NetconfDriver, "open", mock_open)
    monkeypatch.setattr(NetconfDriver, "get_config", mock_get_config)
    monkeypatch.setattr(NetconfDriver, "edit_config", mock_edit_config)

    result = nornir_netconf.run(task=netconf_edit_config, config="blah", target="blah")
    assert result["sea-ios-1"].result == "some stuff about whatever"
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is True

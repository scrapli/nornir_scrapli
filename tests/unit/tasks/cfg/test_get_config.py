from scrapli.driver.core import IOSXEDriver
from scrapli.response import Response
from scrapli_cfg.platform.core.cisco_iosxe.sync_platform import ScrapliCfgIOSXE
from scrapli_cfg.response import ScrapliCfgResponse


def test_get_config(nornir, monkeypatch):
    from nornir_scrapli.tasks import cfg_get_config

    def mock_open(cls):
        pass

    def mock_cfg_open(cls):
        pass

    def mock_cfg_get_config(cls, source):
        assert source == "candidate"
        response = Response(host="fake_as_heck", channel_input="blah")
        response.record_response(b"some stuff about whatever")
        cfg_response = ScrapliCfgResponse(host="fake_as_heck")
        cfg_response.record_response(scrapli_responses=[response])
        return response

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(ScrapliCfgIOSXE, "open", mock_cfg_open)
    monkeypatch.setattr(ScrapliCfgIOSXE, "get_config", mock_cfg_get_config)

    result = nornir.run(task=cfg_get_config, source="candidate")
    assert result["sea-ios-1"].result == "some stuff about whatever"
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is False
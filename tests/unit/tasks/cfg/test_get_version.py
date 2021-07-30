from scrapli.driver.core import IOSXEDriver
from scrapli.response import Response
from scrapli_cfg.platform.core.cisco_iosxe.sync_platform import ScrapliCfgIOSXE
from scrapli_cfg.response import ScrapliCfgResponse


def test_get_version(nornir, monkeypatch):
    from nornir_scrapli.tasks import cfg_get_version

    def mock_open(cls):
        pass

    def mock_cfg_prepare(cls):
        pass

    def mock_cfg_get_version(cls):
        response = Response(host="fake_as_heck", channel_input="blah")
        response.record_response(b"15.2(4)E7")
        cfg_response = ScrapliCfgResponse(host="fake_as_heck")
        cfg_response.record_response(scrapli_responses=[response])
        return response

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(ScrapliCfgIOSXE, "prepare", mock_cfg_prepare)
    monkeypatch.setattr(ScrapliCfgIOSXE, "get_version", mock_cfg_get_version)

    result = nornir.run(task=cfg_get_version)
    assert result["sea-ios-1"].result == "15.2(4)E7"
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is False

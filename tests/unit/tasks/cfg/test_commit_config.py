from scrapli.driver.core import IOSXEDriver
from scrapli.response import Response
from scrapli_cfg.platform.core.cisco_iosxe.sync_platform import ScrapliCfgIOSXE
from scrapli_cfg.response import ScrapliCfgResponse


def test_commit_config(nornir, monkeypatch):
    from nornir_scrapli.tasks import cfg_commit_config

    def mock_open(cls):
        pass

    def mock_cfg_open(cls):
        pass

    def mock_cfg_commit_config(cls, source):
        assert source == "running"
        response = Response(host="fake_as_heck", channel_input="blah")
        response.record_response(b"")
        cfg_response = ScrapliCfgResponse(host="fake_as_heck")
        cfg_response.record_response(scrapli_responses=[response])
        return cfg_response

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(ScrapliCfgIOSXE, "open", mock_cfg_open)
    monkeypatch.setattr(ScrapliCfgIOSXE, "commit_config", mock_cfg_commit_config)

    result = nornir.run(task=cfg_commit_config)
    # the result is just an empty string because there is not actual "output" from it
    assert result["sea-ios-1"].result == ""
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is True

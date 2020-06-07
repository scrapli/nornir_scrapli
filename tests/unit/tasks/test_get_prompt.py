from scrapli.driver.core import IOSXEDriver


def test_get_prompt(nornir, monkeypatch):
    from nornir_scrapli.tasks import get_prompt

    def mock_open(cls):
        pass

    def mock_get_prompt(cls):
        return "sea-ios-1#"

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "get_prompt", mock_get_prompt)

    result = nornir.run(task=get_prompt)
    assert result["sea-ios-1"].result == "sea-ios-1#"
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is False

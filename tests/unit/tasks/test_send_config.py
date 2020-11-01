from scrapli.driver import GenericDriver
from scrapli.driver.core import IOSXEDriver
from scrapli.response import Response

from nornir_scrapli.exceptions import NornirScrapliNoConfigModeGenericDriver


def test_send_config(nornir, monkeypatch):
    from nornir_scrapli.tasks import send_config

    def mock_open(cls):
        pass

    def mock_send_config(
        cls,
        config,
        strip_prompt,
        failed_when_contains="",
        stop_on_failed=False,
        privilege_level="",
        timeout_ops=None,
    ):
        response = Response(host="fake_as_heck", channel_input=config)
        response._record_response(b"some stuff about whatever")
        return response

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "send_config", mock_send_config)

    result = nornir.run(task=send_config, config="interface loopback123\nsome stuff about whatever")
    assert result["sea-ios-1"][0].result == "interface loopback123\nsome stuff about whatever"
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is True


def test_send_config_dry_run(nornir, monkeypatch):
    from nornir_scrapli.tasks import send_config

    def mock_open(cls):
        pass

    def mock_acquire_priv(cls, priv):
        return

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "acquire_priv", mock_acquire_priv)

    result = nornir.run(
        task=send_config,
        dry_run=True,
        config="interface loopback123\ndescription neat",
    )
    assert result["sea-ios-1"].result is None
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is False


def test_send_config_global_dry_run(nornir_global_dry_run, monkeypatch):
    from nornir_scrapli.tasks import send_config

    def mock_open(cls):
        pass

    def mock_acquire_priv(cls, priv):
        return

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "acquire_priv", mock_acquire_priv)

    result = nornir_global_dry_run.run(
        task=send_config,
        config="interface loopback123\ndescription neat",
    )
    assert result["sea-ios-1"].result is None
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is False


def test_send_config_generic_driver(nornir_generic, monkeypatch):
    from nornir_scrapli.tasks import send_config

    def mock_open(cls):
        pass

    monkeypatch.setattr(GenericDriver, "open", mock_open)

    result = nornir_generic.run(
        task=send_config,
        dry_run=True,
        config="interface loopback123\ndescription neat",
    )
    assert (
        "nornir_scrapli.exceptions.NornirScrapliNoConfigModeGenericDriver"
        in result["sea-ios-1"].result
    )
    assert result["sea-ios-1"].failed is True
    assert result["sea-ios-1"].changed is False
    assert isinstance(result["sea-ios-1"].exception, NornirScrapliNoConfigModeGenericDriver)

from nornir_scrapli.exceptions import NornirScrapliNoConfigModeGenericDriver
from scrapli.driver import GenericDriver
from scrapli.driver.core import IOSXEDriver
from scrapli.response import Response


def test_send_configs(nornir, monkeypatch):
    from nornir_scrapli.tasks import send_configs

    def mock_open(cls):
        pass

    def mock_send_configs(
        cls,
        configs,
        strip_prompt,
        failed_when_contains="",
        stop_on_failed=False,
        privilege_level="",
    ):
        responses = []
        response = Response(host="fake_as_heck", channel_input=configs[0])
        response._record_response(b"")
        responses.append(response)
        response = Response(host="fake_as_heck", channel_input=configs[1])
        response._record_response(b"")
        responses.append(response)
        return responses

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "send_configs", mock_send_configs)

    result = nornir.run(task=send_configs, configs=["interface loopback123", "description neat"])
    assert result["sea-ios-1"][0].result == "interface loopback123\ndescription neat\n"
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is True


def test_send_configs_dry_run(nornir, monkeypatch):
    from nornir_scrapli.tasks import send_configs

    def mock_open(cls):
        pass

    def mock_acquire_priv(cls, priv):
        return

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "acquire_priv", mock_acquire_priv)

    result = nornir.run(
        task=send_configs, dry_run=True, configs=["interface loopback123", "description neat"],
    )
    assert result["sea-ios-1"].result is None
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is False


def test_send_configs_generic_driver(nornir_generic, monkeypatch):
    from nornir_scrapli.tasks import send_configs

    def mock_open(cls):
        pass

    monkeypatch.setattr(GenericDriver, "open", mock_open)

    result = nornir_generic.run(
        task=send_configs, dry_run=True, configs=["interface loopback123", "description neat"],
    )
    assert (
        "nornir_scrapli.exceptions.NornirScrapliNoConfigModeGenericDriver"
        in result["sea-ios-1"].result
    )
    assert result["sea-ios-1"].failed is True
    assert result["sea-ios-1"].changed is False
    assert isinstance(result["sea-ios-1"].exception, NornirScrapliNoConfigModeGenericDriver)

from pathlib import Path

from scrapli.driver import GenericDriver
from scrapli.driver.core import IOSXEDriver
from scrapli.response import Response

import nornir_scrapli
from nornir_scrapli.exceptions import NornirScrapliNoConfigModeGenericDriver

CONFIG_FILE = f"{Path(nornir_scrapli.__file__).parents[1]}/tests/files/send_configs_from_file"


def test_send_configs_from_file(nornir, monkeypatch):
    from nornir_scrapli.tasks import send_configs_from_file

    def mock_open(cls):
        pass

    def mock_send_configs_from_file(
        cls,
        file,
        strip_prompt,
        failed_when_contains="",
        stop_on_failed=False,
        privilege_level="",
    ):
        with open(file, "r") as f:
            configs = f.read().splitlines()
        responses = []
        response = Response(host="fake_as_heck", channel_input=configs[0])
        response._record_response(b"")
        responses.append(response)
        response = Response(host="fake_as_heck", channel_input=configs[1])
        response._record_response(b"")
        responses.append(response)
        return responses

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "send_configs_from_file", mock_send_configs_from_file)

    result = nornir.run(
        task=send_configs_from_file,
        dry_run=False,
        file=CONFIG_FILE,
    )
    assert result["sea-ios-1"][0].result == "interface loopback123\ndescription neat\n"
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is True


def test_send_configs_from_file_dry_run(nornir, monkeypatch):
    from nornir_scrapli.tasks import send_configs_from_file

    def mock_open(cls):
        pass

    def mock_acquire_priv(cls, priv):
        return

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "acquire_priv", mock_acquire_priv)

    result = nornir.run(
        task=send_configs_from_file,
        dry_run=True,
        file=CONFIG_FILE,
    )
    assert result["sea-ios-1"].result is None
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is False


def test_send_configs_from_file_generic_driver(nornir_generic, monkeypatch):
    from nornir_scrapli.tasks import send_configs_from_file

    def mock_open(cls):
        pass

    monkeypatch.setattr(GenericDriver, "open", mock_open)

    result = nornir_generic.run(
        task=send_configs_from_file,
        dry_run=True,
        file="whatever",
    )
    assert (
        "nornir_scrapli.exceptions.NornirScrapliNoConfigModeGenericDriver"
        in result["sea-ios-1"].result
    )
    assert result["sea-ios-1"].failed is True
    assert result["sea-ios-1"].changed is False
    assert isinstance(result["sea-ios-1"].exception, NornirScrapliNoConfigModeGenericDriver)

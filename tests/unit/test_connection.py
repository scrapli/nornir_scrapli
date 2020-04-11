import os

import pytest
from nornir import InitNornir
from nornir.core.connections import Connections

from nornir_scrapli.exceptions import NornirScrapliInvalidPlatform


def test_connection_registration(nornir):
    assert "scrapli" not in Connections.available
    from nornir_scrapli.tasks import get_prompt

    assert "scrapli" in Connections.available


def test_connection_setup(nornir, monkeypatch):
    from scrapli.driver.core import IOSXEDriver

    def mock_open(cls):
        pass

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    scrapli_conn = nornir.inventory.hosts["sea-ios-1"].get_connection("scrapli", nornir.config)
    assert scrapli_conn.transport.host == "172.18.0.11"
    assert scrapli_conn.transport.port == 22
    assert scrapli_conn.transport.auth_username == "vrnetlab"
    assert scrapli_conn.transport.auth_password == "VR-netlab9"
    assert scrapli_conn.transport.auth_strict_key is False


def test_connection_invalid_platform():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = "/".join(dir_path.split("/")[:-1])

    # need to import task to ensure plugin gets registered
    from nornir_scrapli.tasks import get_prompt

    with pytest.raises(NornirScrapliInvalidPlatform) as exc:
        nornir = InitNornir(
            inventory={
                "options": {
                    "host_file": "{}/inventory_data/hosts.yaml".format(dir_path),
                    "group_file": "{}/inventory_data/bad_groups.yaml".format(dir_path),
                    "defaults_file": "{}/inventory_data/defaults.yaml".format(dir_path),
                }
            },
            dry_run=True,
        )
        nornir.inventory.hosts["sea-ios-1"].get_connection("scrapli", nornir.config)
    assert (
        str(exc.value) == "Provided platform `tacocat` is not a valid scrapli or napalm platform."
    )

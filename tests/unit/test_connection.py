import os

import pytest

from nornir import InitNornir
from nornir_scrapli.exceptions import NornirScrapliInvalidPlatform


def test_connection_core_setup(nornir, monkeypatch):
    from scrapli.driver.driver import Scrape

    def mock_open(cls):
        pass

    monkeypatch.setattr(Scrape, "open", mock_open)
    scrapli_conn = nornir.inventory.hosts["sea-ios-1"].get_connection("scrapli", nornir.config)
    assert scrapli_conn.transport.host == "172.18.0.11"
    assert scrapli_conn.transport.port == 22
    assert scrapli_conn.transport.auth_username == "vrnetlab"
    assert scrapli_conn.transport.auth_password == "VR-netlab9"
    assert scrapli_conn.transport.auth_strict_key is False


def test_connection_core_community_platform(nornir_community, monkeypatch):
    # simple test to ensure scrapli community platforms load properly
    from scrapli.driver.driver import Scrape

    def mock_open(cls):
        pass

    monkeypatch.setattr(Scrape, "open", mock_open)

    scrapli_conn = nornir_community.inventory.hosts["sea-ios-1"].get_connection(
        "scrapli", nornir_community.config
    )
    assert scrapli_conn.transport.host == "172.18.0.11"
    assert scrapli_conn.transport.port == 22
    assert scrapli_conn.transport.auth_username == "vrnetlab"
    assert scrapli_conn.transport.auth_password == "VR-netlab9"
    assert scrapli_conn.transport.auth_strict_key is False


def test_connection_core_invalid_platform():
    # ensure that invalid platforms raise an exception
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = "/".join(dir_path.split("/")[:-1])

    with pytest.raises(NornirScrapliInvalidPlatform) as exc:
        nornir = InitNornir(
            inventory={
                "plugin": "YAMLInventory",
                "options": {
                    "host_file": "{}/inventory_data/hosts.yaml".format(dir_path),
                    "group_file": "{}/inventory_data/bad_groups.yaml".format(dir_path),
                    "defaults_file": "{}/inventory_data/defaults.yaml".format(dir_path),
                },
            },
            dry_run=True,
        )
        nornir.inventory.hosts["sea-ios-1"].get_connection("scrapli", nornir.config)
    assert (
        str(exc.value)
        == "Provided platform `tacocat` is not a valid scrapli or napalm platform, or is not a valid scrapli-community platform."
    )


def test_connection_netconf_setup(nornir_netconf, monkeypatch):
    from scrapli_netconf.driver import NetconfScrape

    def mock_open(cls):
        pass

    monkeypatch.setattr(NetconfScrape, "open", mock_open)
    scrapli_conn = nornir_netconf.inventory.hosts["sea-ios-1"].get_connection(
        "scrapli_netconf", nornir_netconf.config
    )
    assert scrapli_conn.transport.host == "172.18.0.11"
    assert scrapli_conn.transport.port == 830
    assert scrapli_conn.transport.auth_username == "vrnetlab"
    assert scrapli_conn.transport.auth_password == "VR-netlab9"
    assert scrapli_conn.transport.auth_strict_key is False
    assert isinstance(scrapli_conn, NetconfScrape)


def test_connection_global_ssh_config_setting_overridden(nornir_global_ssh, monkeypatch):
    from scrapli_netconf.driver import NetconfScrape

    def mock_open(cls):
        pass

    monkeypatch.setattr(NetconfScrape, "open", mock_open)
    scrapli_conn = nornir_global_ssh.inventory.hosts["sea-ios-1"].get_connection(
        "scrapli_netconf", nornir_global_ssh.config
    )
    assert nornir_global_ssh.config.ssh.config_file == "notarealfile!"
    assert scrapli_conn._initialization_args["ssh_config_file"] == os.path.expanduser(
        "~/.ssh/config"
    )


def test_connection_global_ssh_config_setting_no_connection_option_ssh(
    nornir_global_ssh_no_connection_option_ssh, monkeypatch
):
    from scrapli.driver.driver import Scrape

    def mock_open(cls):
        pass

    monkeypatch.setattr(Scrape, "open", mock_open)
    scrapli_conn = nornir_global_ssh_no_connection_option_ssh.inventory.hosts[
        "sea-ios-1"
    ].get_connection("scrapli", nornir_global_ssh_no_connection_option_ssh.config)
    assert nornir_global_ssh_no_connection_option_ssh.config.ssh.config_file is False
    assert scrapli_conn._initialization_args["ssh_config_file"] == ""

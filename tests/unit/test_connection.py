import os

import pytest
from nornir import InitNornir
from nornir.core.connections import Connections
from nornir.core.exceptions import NornirExecutionError
from scrapli.driver.core import IOSXEDriver
from scrapli.response import Response

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
    scrapli_conn = nornir.inventory.hosts["sea-ios-1"].get_connection(
        "scrapli", nornir.config
    )
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
        str(exc.value)
        == "Provided platform `tacocat` is not a valid scrapli or napalm platform."
    )


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


def test_send_command(nornir, monkeypatch):
    from nornir_scrapli.tasks import send_command

    def mock_open(cls):
        pass

    def mock_send_command(cls, command, strip_prompt):
        response = Response(host="fake_as_heck", channel_input=command)
        response.record_response("some stuff about whatever")
        return response

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "send_command", mock_send_command)

    result = nornir.run(task=send_command, command="show version")
    assert result["sea-ios-1"].result.result == "some stuff about whatever"
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is False


def test_send_commands(nornir, monkeypatch):
    from nornir_scrapli.tasks import send_commands

    def mock_open(cls):
        pass

    def mock_send_commands(cls, commands, strip_prompt):
        response = Response(host="fake_as_heck", channel_input=commands[0])
        response.record_response("some stuff about whatever")
        return [response]

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "send_commands", mock_send_commands)

    result = nornir.run(task=send_commands, commands=["show version"])
    assert result["sea-ios-1"].result[0].result == "some stuff about whatever"
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is False


def test_send_commands_not_list(nornir_raise_on_error, monkeypatch):
    from nornir_scrapli.tasks import send_commands

    def mock_open(cls):
        pass

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)

    with pytest.raises(NornirExecutionError) as exc:
        nornir_raise_on_error.run(task=send_commands, commands="show version")
    assert "expects a list of strings, got <class 'str'>" in str(exc.value)


def test_send_configs(nornir, monkeypatch):
    from nornir_scrapli.tasks import send_configs

    def mock_open(cls):
        pass

    def mock_send_configs(cls, configs, strip_prompt):
        responses = []
        response = Response(host="fake_as_heck", channel_input=configs[0])
        response.record_response("some stuff about whatever")
        responses.append(response)
        response = Response(host="fake_as_heck", channel_input=configs[1])
        response.record_response("some stuff about whatever")
        responses.append(response)
        return [response]

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "send_configs", mock_send_configs)

    result = nornir.run(
        task=send_configs, configs=["interface loopback123", "description neat"]
    )
    assert result["sea-ios-1"].result[0].result == "some stuff about whatever"
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
        task=send_configs,
        dry_run=True,
        configs=["interface loopback123", "description neat"],
    )
    assert result["sea-ios-1"].result is None
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is False


def test_send_interactive(nornir, monkeypatch):
    from nornir_scrapli.tasks import send_interactive

    def mock_open(cls):
        pass

    def mock_send_interactive(cls, interact, hidden_response):
        response = Response(
            host="fake_as_heck",
            channel_input=interact[0],
            expectation=interact[1],
            channel_response=interact[2],
            finale=interact[3],
        )
        response.record_response("Clear logging buffer [confirm]\n\n\n3560CX#")
        return [response]

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "send_interactive", mock_send_interactive)

    result = nornir.run(
        task=send_interactive,
        interact=["clear logg", "are you sure blah blah", "y", "sea-ios-1#"],
    )
    assert (
        result["sea-ios-1"].result[0].result
        == "Clear logging buffer [confirm]\n\n\n3560CX#"
    )
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is True

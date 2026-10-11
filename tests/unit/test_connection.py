import pytest
from scrapli import Cli, Netconf
from scrapli.exceptions import OptionsException

from nornir.core.configuration import Config
from nornir_scrapli.connection import ScrapliCore, ScrapliNetconf
from nornir_scrapli.exceptions import NornirScrapliInvalidPlatform


@pytest.mark.parametrize(
    "platform,want",
    [
        ("ios", "cisco_iosxe"),
        ("nxos", "cisco_nxos"),
        ("iosxr", "cisco_iosxr"),
        ("eos", "arista_eos"),
        ("junos", "juniper_junos"),
        ("generic", "default"),
        (None, "default"),
    ],
)
def test_platforms_and_lifecycle(monkeypatch, platform, want):
    calls = []
    monkeypatch.setattr(Cli, "open", lambda self: calls.append("open"))
    monkeypatch.setattr(Cli, "close", lambda self: calls.append("close"))
    plugin = ScrapliCore()
    plugin.open("router", "user", "secret", None, platform)
    assert plugin.connection.definition_file_or_name == want
    assert plugin.connection.host == "router"
    assert plugin.connection.port == 22
    assert plugin.connection.auth_options.username == "user"
    assert plugin.connection.transport_options.enable_strict_key is True
    plugin.close()
    assert calls == ["open", "close"]


def test_unknown_platform_has_context(monkeypatch):
    monkeypatch.setattr(Cli, "open", lambda self: None)
    with pytest.raises(NornirScrapliInvalidPlatform) as exc:
        ScrapliCore().open("router", None, None, None, "nonexistent")
    assert "router" in str(exc.value)
    assert "nonexistent" in str(exc.value)
    assert isinstance(exc.value.__cause__, OptionsException)


def test_definition_overrides_platform(monkeypatch):
    monkeypatch.setattr(Cli, "open", lambda self: None)
    plugin = ScrapliCore()
    plugin.open("router", None, None, None, "nonexistent", {"definition": "cisco_iosxe"})
    assert plugin.connection.definition_file_or_name == "cisco_iosxe"


def test_custom_definition_file(monkeypatch, tmp_path):
    definition = tmp_path / "platform.yaml"
    definition.write_text(
        "prompt_pattern: '^router#\\s*$'\ndefault_mode: custom\n"
        "modes:\n - name: custom\n   prompt_pattern: '^router#\\s*$'\n",
    )
    monkeypatch.setattr(Cli, "open", lambda self: None)
    plugin = ScrapliCore()
    plugin.open("router", None, None, None, "unknown", {"definition": str(definition)})
    assert plugin.connection.definition_file_or_name == str(definition)
    assert b"default_mode: custom" in plugin.connection.definition_string


@pytest.mark.parametrize("port,want", [(None, 830), (2222, 2222)])
def test_netconf_defaults(monkeypatch, port, want):
    monkeypatch.setattr(Netconf, "open", lambda self: None)
    plugin = ScrapliNetconf()
    plugin.open("router", "user", "secret", port, None)
    assert plugin.connection.port == want
    assert plugin.connection.auth_options.password == "secret"


def test_telnet_default_port(monkeypatch):
    monkeypatch.setattr(Cli, "open", lambda self: None)
    plugin = ScrapliCore()
    plugin.open("router", None, None, None, None, {"transport": {"kind": "telnet"}})
    assert plugin.connection.port == 23


@pytest.mark.parametrize(
    "extras,want", [({}, "global"), ({"transport": {"ssh_config_path": "local"}}, "local")]
)
def test_ssh_config_precedence(monkeypatch, extras, want):
    monkeypatch.setattr(Cli, "open", lambda self: None)
    plugin = ScrapliCore()
    plugin.open(
        "router", None, None, None, None, extras, Config.from_dict(ssh={"config_file": "global"})
    )
    assert plugin.connection.transport_options.ssh_config_path == want

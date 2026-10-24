"""Translate Nornir inventory data into fresh scrapli v2 options."""

from copy import deepcopy
from dataclasses import fields
from typing import Any, Dict, Optional, Type

from scrapli import (
    AuthOptions,
    LookupKeyValue,
    NetconfOptions,
    SessionOptions,
    TransportBinOptions,
    TransportSsh2Options,
    TransportTelnetOptions,
)
from scrapli.cli import Options as CliOptions
from scrapli.netconf import Version

from nornir.core.configuration import Config
from nornir_scrapli.exceptions import NornirScrapliInvalidOptions

MIGRATION_URL = "https://scrapli.github.io/nornir_scrapli/user_guide/migrating_to_v2/"
TRANSPORTS = {
    "bin": TransportBinOptions,
    "ssh2": TransportSsh2Options,
    "telnet": TransportTelnetOptions,
}


def _invalid(hostname: str, key: str) -> str:
    return f"Invalid connection option `{key}` for host `{hostname}`; see {MIGRATION_URL}"


def _clone_lookups(value: Any, hostname: str) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        if not all(isinstance(k, str) and isinstance(v, str) for k, v in value.items()):
            raise NornirScrapliInvalidOptions(_invalid(hostname, "auth.lookups"))
        return [LookupKeyValue(key=k, value=v) for k, v in value.items()]
    if not isinstance(value, list) or not all(isinstance(x, LookupKeyValue) for x in value):
        raise NornirScrapliInvalidOptions(_invalid(hostname, "auth.lookups"))
    return [LookupKeyValue(key=x.key, value=x.value) for x in value]


def _option_data(value: Any, cls: Type[Any], hostname: str, section: str) -> Dict[str, Any]:
    if value is None:
        return {}
    names = {f.name for f in fields(cls) if f.init and not f.name.startswith("_")}
    if isinstance(value, cls):
        # Native options may already contain ctypes pointers. Copy only constructor fields.
        data = {name: getattr(value, name) for name in names}
    elif isinstance(value, dict):
        data = dict(value)
    else:
        raise NornirScrapliInvalidOptions(_invalid(hostname, section))
    for key in data:
        if key not in names:
            raise NornirScrapliInvalidOptions(_invalid(hostname, f"{section}.{key}"))
    if section == "auth":
        data["lookups"] = _clone_lookups(data.get("lookups"), hostname)
    return {key: deepcopy(val) for key, val in data.items()}


def _build_transport(value: Any, hostname: str, configuration: Optional[Config]) -> Any:
    if isinstance(value, dict):
        value = dict(value)
        kind = value.pop("kind", "bin")
        if not isinstance(kind, str) or kind not in TRANSPORTS:
            raise NornirScrapliInvalidOptions(_invalid(hostname, "transport.kind"))
        cls: Type[Any] = TRANSPORTS[kind]
    elif value is None:
        cls = TransportBinOptions
    else:
        found = next((cls for cls in TRANSPORTS.values() if isinstance(value, cls)), None)
        if found is None:
            raise NornirScrapliInvalidOptions(_invalid(hostname, "transport"))
        cls = found
    data = _option_data(value, cls, hostname, "transport")
    if cls is TransportBinOptions:
        if data.get("enable_strict_key") is None:
            data["enable_strict_key"] = True
        if data.get("ssh_config_path") is None and configuration is not None:
            data["ssh_config_path"] = configuration.ssh.config_file or None
    return cls(**data)


def build_connection_options(
    *,
    hostname: str,
    username: Optional[str],
    password: Optional[str],
    extras: Optional[Dict[str, Any]],
    configuration: Optional[Config],
    netconf: bool,
) -> Dict[str, Any]:
    """Build constructor kwargs, preserving explicit values and shared inventory data.

    Args:
        hostname: Host used in diagnostics and recording paths.
        username: Nornir username fallback.
        password: Nornir password fallback.
        extras: Nested native option data or objects.
        configuration: Global Nornir configuration.
        netconf: Whether to build NETCONF rather than CLI options.

    Returns:
        Fresh native option objects keyed by constructor argument name.

    Raises:
        NornirScrapliInvalidOptions: For an invalid section, field or transport kind.
    """
    extras = {} if extras is None else extras
    if not isinstance(extras, dict):
        raise NornirScrapliInvalidOptions(_invalid(hostname, "extras"))
    allowed = (
        {"auth", "session", "transport", "netconf"}
        if netconf
        else {"auth", "session", "transport", "cli", "definition"}
    )
    for key in extras:
        if key not in allowed:
            raise NornirScrapliInvalidOptions(_invalid(hostname, str(key)))
    auth = _option_data(extras.get("auth"), AuthOptions, hostname, "auth")
    for key, fallback in (("username", username), ("password", password)):
        if auth.get(key) is None:
            auth[key] = fallback or ""
    session = _option_data(extras.get("session"), SessionOptions, hostname, "session")
    if session.get("recorder_path") is True:
        session["recorder_path"] = f"scrapli_channel_{hostname}.log"
    if session.get("recorder_path") is False:
        session["recorder_path"] = None
    transport = _build_transport(extras.get("transport"), hostname, configuration)
    protocol_cls = NetconfOptions if netconf else CliOptions
    protocol_section = "netconf" if netconf else "cli"
    protocol = _option_data(extras.get(protocol_section), protocol_cls, hostname, protocol_section)
    if netconf and isinstance(protocol.get("preferred_version"), str):
        try:
            protocol["preferred_version"] = Version(protocol["preferred_version"])
        except ValueError:
            raise NornirScrapliInvalidOptions(
                _invalid(hostname, "netconf.preferred_version")
            ) from None
    return {
        "auth_options": AuthOptions(**auth),
        "session_options": SessionOptions(**session),
        "transport_options": transport,
        "options" if netconf else "cli_options": protocol_cls(**protocol),
    }

import pytest


def build(extras=None, host="host-a", netconf=False, username="user", password="password"):
    from nornir_scrapli.connection_options import build_connection_options

    return build_connection_options(
        hostname=host,
        username=username,
        password=password,
        extras=extras,
        configuration=None,
        netconf=netconf,
    )


def test_defaults_and_explicit_values():
    options = build()
    assert options["auth_options"].username == "user"
    assert options["transport_options"].enable_strict_key is True
    options = build({"auth": {"username": ""}, "transport": {"enable_strict_key": False}})
    assert options["auth_options"].username == ""
    assert options["transport_options"].enable_strict_key is False


def test_shared_options_are_not_mutated():
    from scrapli import AuthOptions, LookupKeyValue, SessionOptions, TransportBinOptions

    auth = AuthOptions(lookups=[LookupKeyValue(key="enable", value="secret")])
    session = SessionOptions(recorder_path=True)
    transport = TransportBinOptions()
    extras = {"auth": auth, "session": session, "transport": transport}
    a = build(extras)
    b = build(extras, host="host-b")
    assert a["session_options"].recorder_path == "scrapli_channel_host-a.log"
    assert b["session_options"].recorder_path == "scrapli_channel_host-b.log"
    assert session.recorder_path is True
    assert auth.username is None
    assert transport.enable_strict_key is None
    assert a["auth_options"] is not b["auth_options"]
    assert a["auth_options"].lookups[0] is not auth.lookups[0]


def test_lookup_mapping_and_timeouts():
    options = build(
        {"auth": {"lookups": {"enable": "secret"}}, "session": {"operation_timeout_ns": 0}}
    )
    assert [(x.key, x.value) for x in options["auth_options"].lookups] == [("enable", "secret")]
    assert options["session_options"].operation_timeout_ns == 0


@pytest.mark.parametrize("kind", ["ssh2", "telnet"])
def test_transport_specific_options(kind):
    options = build({"transport": {"kind": kind}})
    assert not hasattr(options["transport_options"], "enable_strict_key")


@pytest.mark.parametrize(
    "extras,key",
    [
        ({"auth_strict_key": False}, "auth_strict_key"),
        ({"auth_secondary": "secret"}, "auth_secondary"),
        ({"transport": "paramiko"}, "transport"),
        ({"transport": {"kind": "paramiko"}}, "transport.kind"),
        ({"auth": {"unknown": "secret"}}, "auth.unknown"),
        ({"session": "secret"}, "session"),
        ({"netconf": {}}, "netconf"),
    ],
)
def test_invalid_options_name_key_without_value(extras, key):
    from nornir_scrapli.exceptions import NornirScrapliInvalidOptions

    with pytest.raises(NornirScrapliInvalidOptions) as exc:
        build(extras)
    assert key in str(exc.value)
    assert "host-a" in str(exc.value)
    assert "migrating_to_v2" in str(exc.value)
    assert "secret" not in str(exc.value)


def test_previously_applied_auth_options_are_fresh_for_each_host():
    from ctypes import pointer

    from scrapli import AuthOptions, LookupKeyValue
    from scrapli.ffi_options import DriverOptions

    auth = AuthOptions(lookups=[LookupKeyValue(key="enable", value="secret")])
    auth.apply(options=pointer(DriverOptions()))
    a = build({"auth": auth}, username="user-a", password="password-a")
    b = build({"auth": auth}, host="host-b", username="user-b", password="password-b")
    assert a["auth_options"].username == "user-a"
    assert b["auth_options"].username == "user-b"
    assert a["auth_options"].password == "password-a"
    assert b["auth_options"].password == "password-b"
    assert auth.username is None
    assert auth.lookups[0]._key is not None
    assert a["auth_options"].lookups[0]._key is None
    assert b["auth_options"].lookups[0]._key is None

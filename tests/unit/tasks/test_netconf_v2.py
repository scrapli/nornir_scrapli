import pytest
from scrapli import Netconf
from scrapli.ffi_types import Cancel
from scrapli.netconf import (
    ConfigFilter,
    DatastoreType,
    DefaultOperation,
    DefaultsType,
    ErrorOption,
    FilterType,
    SchemaFormat,
)
from scrapli.netconf import TestOption as NetconfTestOption

OPERATIONS = [
    (
        "get",
        {
            "filter_": "<interfaces/>",
            "filter_type": FilterType.XPATH,
            "filter_namespace_prefix": "if",
            "filter_namespace": "urn:interfaces",
            "defaults_type": DefaultsType.EXPLICIT,
        },
        False,
    ),
    ("get_config", {"source": DatastoreType.CANDIDATE, "filter_": "<interfaces/>"}, False),
    (
        "edit_config",
        {
            "config": "<config/>",
            "target": DatastoreType.CANDIDATE,
            "default_operation": DefaultOperation.REPLACE,
            "test_option": NetconfTestOption.SET,
            "error_option": ErrorOption.ROLLBACK_ON_ERROR,
        },
        True,
    ),
    ("delete_config", {"target": DatastoreType.STARTUP}, True),
    ("lock", {"target": DatastoreType.CANDIDATE}, True),
    ("unlock", {"target": DatastoreType.CANDIDATE}, True),
    ("validate", {"source": DatastoreType.CANDIDATE}, False),
    ("commit", {}, True),
    ("discard", {}, True),
    (
        "rpc",
        {
            "payload": "<custom/>",
            "base_namespace_prefix": "nc",
            "extra_namespaces": [("if", "urn:interfaces")],
        },
        True,
    ),
    ("copy_config", {"source": DatastoreType.CANDIDATE, "target": DatastoreType.STARTUP}, True),
    (
        "get_schema",
        {"identifier": "interfaces", "version": "2026", "format_": SchemaFormat.YIN},
        False,
    ),
    (
        "get_data",
        {
            "source": DatastoreType.CANDIDATE,
            "max_depth": 5,
            "with_origin": True,
            "config_filter": ConfigFilter.TRUE,
            "origin_filters": "origin",
            "defaults_type": DefaultsType.TRIM,
            "filter_": "<interfaces/>",
            "filter_type": FilterType.XPATH,
            "filter_namespace_prefix": "if",
            "filter_namespace": "urn:interfaces",
        },
        False,
    ),
    (
        "edit_data",
        {"content": "<interfaces/>", "default_operation": DefaultOperation.REPLACE},
        True,
    ),
    ("cancel_commit", {"persist_id": "123"}, True),
    ("kill_session", {"session_id": 123}, True),
    ("action", {"action": "<reset/>"}, True),
]


@pytest.mark.parametrize("name,kwargs,changed", OPERATIONS)
@pytest.mark.parametrize("failed", [False, True])
def test_netconf_operations(
    nornir, monkeypatch, make_netconf_result, name, kwargs, changed, failed
):
    from nornir_scrapli import tasks

    calls = []
    native = make_netconf_result("<reply/>", "error" if failed else "")
    monkeypatch.setattr(Netconf, "open", lambda self: None)

    def send(self, **options):
        calls.append(options)
        return native

    monkeypatch.setattr(Netconf, "raw_rpc" if name == "rpc" else name, send)
    cancel = Cancel()
    result = nornir.run(
        task=getattr(tasks, "netconf_" + name), **kwargs, operation_timeout_ns=0, cancel=cancel
    )["sea-ios-1"][0]
    assert result.exception is None
    assert result.result == "<reply/>"
    assert result.failed is failed
    assert result.changed is changed
    assert result.scrapli_response is native
    assert calls[0]["operation_timeout_ns"] == 0
    assert calls[0]["cancel"] is cancel
    for key, value in kwargs.items():
        assert calls[0][key] == value


def test_capabilities(nornir, monkeypatch):
    from nornir_scrapli.tasks import netconf_capabilities

    monkeypatch.setattr(Netconf, "open", lambda self: None)
    monkeypatch.setattr(Netconf, "get_capabilities", lambda self: ["urn:capability"])
    result = nornir.run(task=netconf_capabilities)["sea-ios-1"][0]
    assert result.exception is None
    assert result.result == ["urn:capability"]
    assert result.changed is False


def test_edit_config_dry_run_diff(nornir, monkeypatch, make_netconf_result):
    from nornir_scrapli.tasks import netconf_edit_config

    calls = []
    responses = iter([make_netconf_result("<before/>"), make_netconf_result("<after/>")])
    monkeypatch.setattr(Netconf, "open", lambda self: None)

    def get(self, **kw):
        calls.append(("get", kw["source"]))
        return next(responses)

    def edit(self, **kw):
        calls.append(("edit", kw["target"]))
        return make_netconf_result()

    def discard(self, **kw):
        calls.append(("discard", None))
        return make_netconf_result()

    monkeypatch.setattr(Netconf, "get_config", get)
    monkeypatch.setattr(Netconf, "edit_config", edit)
    monkeypatch.setattr(Netconf, "discard", discard)
    result = nornir.run(
        task=netconf_edit_config,
        config="<config/>",
        target=DatastoreType.CANDIDATE,
        dry_run=True,
        diff=True,
    )["sea-ios-1"][0]
    assert result.exception is None
    assert result.changed is False
    assert "-<before/>" in result.diff
    assert "+<after/>" in result.diff
    assert calls == [
        ("get", DatastoreType.CANDIDATE),
        ("edit", DatastoreType.CANDIDATE),
        ("get", DatastoreType.CANDIDATE),
        ("discard", None),
    ]


@pytest.mark.parametrize(
    "edit_raises,read_raises,discard_failure",
    [
        (True, False, ""),
        (True, False, "reply"),
        (False, True, "reply"),
        (False, False, "reply"),
        (False, False, "exception"),
    ],
)
def test_dry_run_cleanup_preserves_primary_failure(
    nornir,
    monkeypatch,
    make_netconf_result,
    edit_raises,
    read_raises,
    discard_failure,
):
    from scrapli.exceptions import OperationException

    from nornir_scrapli.tasks import netconf_edit_config

    native = make_netconf_result()
    primary = OperationException("primary edit or read failure")
    calls = []
    monkeypatch.setattr(Netconf, "open", lambda self: None)

    def edit(self, **kwargs):
        calls.append("edit")
        if edit_raises:
            raise primary
        return native

    def get(self, **kwargs):
        calls.append("get")
        if "edit" in calls and read_raises:
            raise primary
        return make_netconf_result()

    def discard(self, **kwargs):
        calls.append("discard")
        if discard_failure == "exception":
            raise OperationException("cleanup exception")
        return make_netconf_result(rpc_errors="cleanup failed" if discard_failure else "")

    monkeypatch.setattr(Netconf, "edit_config", edit)
    monkeypatch.setattr(Netconf, "get_config", get)
    monkeypatch.setattr(Netconf, "discard", discard)
    result = nornir.run(
        task=netconf_edit_config,
        config="<config/>",
        dry_run=True,
        diff=True,
        target=DatastoreType.CANDIDATE,
    )["sea-ios-1"][0]
    assert calls[-1] == "discard"
    assert result.failed is True
    if edit_raises or read_raises:
        assert result.exception is primary
        if discard_failure:
            assert primary.__cause__ is not None
    else:
        assert result.exception is not None
    if not edit_raises:
        assert result.scrapli_response is native


def test_failed_edit_reply_survives_failed_cleanup(nornir, monkeypatch, make_netconf_result):
    from nornir_scrapli.tasks import netconf_edit_config

    native = make_netconf_result(rpc_errors="edit rejected")
    monkeypatch.setattr(Netconf, "open", lambda self: None)
    monkeypatch.setattr(Netconf, "edit_config", lambda self, **kwargs: native)
    monkeypatch.setattr(
        Netconf,
        "discard",
        lambda self, **kwargs: make_netconf_result(rpc_errors="discard rejected"),
    )
    result = nornir.run(
        task=netconf_edit_config,
        config="<config/>",
        dry_run=True,
        target=DatastoreType.CANDIDATE,
    )["sea-ios-1"][0]
    assert result.scrapli_response is native
    assert result.failed is True
    assert "edit" in str(result.exception).lower()
    assert result.exception.__cause__ is not None

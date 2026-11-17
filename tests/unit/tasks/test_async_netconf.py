import pytest
from conftest import asyncify
from scrapli import Netconf
from scrapli.exceptions import OperationException
from scrapli.ffi_types import Cancel
from scrapli.netconf import DatastoreType

from nornir_scrapli import async_tasks

from .test_netconf_v2 import OPERATIONS


@pytest.fixture(autouse=True)
def _async_open(monkeypatch):
    monkeypatch.setattr(Netconf, "open_async", asyncify(lambda self: None))


@pytest.mark.asyncio
@pytest.mark.parametrize("name,kwargs,changed", OPERATIONS)
@pytest.mark.parametrize("failed", [False, True])
async def test_netconf_operations(
    async_nornir, monkeypatch, make_netconf_result, name, kwargs, changed, failed
):
    calls = []
    native = make_netconf_result("<reply/>", "error" if failed else "")

    def send(self, **options):
        calls.append(options)
        return native

    method = "raw_rpc" if name == "rpc" else name
    monkeypatch.setattr(Netconf, f"{method}_async", asyncify(send))
    cancel = Cancel()
    result = (
        await async_nornir.arun(
            task=getattr(async_tasks, "netconf_" + name),
            **kwargs,
            operation_timeout_ns=0,
            cancel=cancel,
        )
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


@pytest.mark.asyncio
async def test_capabilities(async_nornir, monkeypatch):
    monkeypatch.setattr(Netconf, "get_capabilities", lambda self: ["urn:capability"])
    result = (await async_nornir.arun(task=async_tasks.netconf_capabilities))["sea-ios-1"][0]
    assert result.exception is None
    assert result.result == ["urn:capability"]
    assert result.changed is False


@pytest.mark.asyncio
async def test_edit_config_dry_run_diff(async_nornir, monkeypatch, make_netconf_result):
    calls = []
    responses = iter([make_netconf_result("<before/>"), make_netconf_result("<after/>")])

    def get(self, **kw):
        calls.append(("get", kw["source"]))
        return next(responses)

    def edit(self, **kw):
        calls.append(("edit", kw["target"]))
        return make_netconf_result()

    def discard(self, **kw):
        calls.append(("discard", None))
        return make_netconf_result()

    monkeypatch.setattr(Netconf, "get_config_async", asyncify(get))
    monkeypatch.setattr(Netconf, "edit_config_async", asyncify(edit))
    monkeypatch.setattr(Netconf, "discard_async", asyncify(discard))
    result = (
        await async_nornir.arun(
            task=async_tasks.netconf_edit_config,
            config="<config/>",
            target=DatastoreType.CANDIDATE,
            dry_run=True,
            diff=True,
        )
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


@pytest.mark.asyncio
@pytest.mark.parametrize("discard_failure", ["reply", "exception"])
async def test_edit_failure_survives_failed_discard(
    async_nornir, monkeypatch, make_netconf_result, discard_failure
):
    primary = OperationException("edit failed")

    def edit(self, **kwargs):
        raise primary

    def discard(self, **kwargs):
        if discard_failure == "exception":
            raise OperationException("cleanup exception")
        return make_netconf_result(rpc_errors="cleanup failed")

    monkeypatch.setattr(Netconf, "edit_config_async", asyncify(edit))
    monkeypatch.setattr(Netconf, "discard_async", asyncify(discard))
    result = (
        await async_nornir.arun(
            task=async_tasks.netconf_edit_config,
            config="<config/>",
            dry_run=True,
            target=DatastoreType.CANDIDATE,
        )
    )["sea-ios-1"][0]
    assert result.failed is True
    assert result.exception is primary
    assert primary.__cause__ is not None


@pytest.mark.asyncio
async def test_edit_config_dry_run_requires_candidate(async_nornir, monkeypatch):
    calls = []
    monkeypatch.setattr(
        Netconf, "edit_config_async", asyncify(lambda self, **kwargs: calls.append(kwargs))
    )
    result = (
        await async_nornir.arun(
            task=async_tasks.netconf_edit_config, config="<config/>", dry_run=True
        )
    )["sea-ios-1"][0]
    assert result.failed is True
    assert isinstance(result.exception, ValueError)
    assert calls == []


@pytest.mark.asyncio
async def test_delete_config_targets_candidate_by_default(
    async_nornir, monkeypatch, make_netconf_result
):
    calls = []
    monkeypatch.setattr(
        Netconf,
        "delete_config_async",
        asyncify(lambda self, **kwargs: calls.append(kwargs) or make_netconf_result()),
    )
    result = (await async_nornir.arun(task=async_tasks.netconf_delete_config))["sea-ios-1"][0]
    assert result.exception is None
    assert calls[0]["target"] is DatastoreType.CANDIDATE


@pytest.mark.asyncio
async def test_datastore_names_accepted_as_strings(async_nornir, monkeypatch, make_netconf_result):
    calls = []
    monkeypatch.setattr(
        Netconf,
        "lock_async",
        asyncify(lambda self, **kwargs: calls.append(kwargs) or make_netconf_result()),
    )
    result = (await async_nornir.arun(task=async_tasks.netconf_lock, target="candidate"))[
        "sea-ios-1"
    ][0]
    assert result.exception is None
    assert calls[0]["target"] is DatastoreType.CANDIDATE

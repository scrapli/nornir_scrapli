import asyncio

import pytest
from conftest import asyncify
from scrapli import Cli, Netconf

from nornir.core.exceptions import ConnectionModeMismatchError
from nornir_scrapli.connection import ScrapliCore, ScrapliNetconf


@pytest.mark.parametrize("plugin", [ScrapliCore, ScrapliNetconf])
def test_dual_capabilities(plugin):
    assert plugin().get_capabilities() == frozenset({"sync", "asyncio"})
    assert plugin().connection is None


@pytest.mark.asyncio
async def test_aopen_builds_same_driver_as_open(monkeypatch):
    calls = []
    monkeypatch.setattr(Cli, "open", lambda self: calls.append("open"))
    monkeypatch.setattr(Cli, "open_async", asyncify(lambda self: calls.append("open_async")))
    monkeypatch.setattr(Cli, "close_async", asyncify(lambda self: calls.append("close_async")))
    sync_plugin, async_plugin = ScrapliCore(), ScrapliCore()
    args = ("router", "user", "secret", None, "ios", {"transport": {"kind": "telnet"}})
    sync_plugin.open(*args)
    await async_plugin.aopen(*args)
    for attribute in ("host", "port", "definition_file_or_name", "definition_string"):
        assert getattr(async_plugin.connection, attribute) == getattr(
            sync_plugin.connection, attribute
        )
    assert async_plugin.connection.auth_options.username == "user"
    await async_plugin.aclose()
    await async_plugin.aclose()
    assert async_plugin.connection is None
    assert calls == ["open", "open_async", "close_async"]


@pytest.mark.asyncio
async def test_netconf_aopen_default_port(monkeypatch):
    monkeypatch.setattr(Netconf, "open_async", asyncify(lambda self: None))
    plugin = ScrapliNetconf()
    await plugin.aopen("router", "user", "secret", None, None)
    assert plugin.connection.port == 830


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", [OSError("refused"), asyncio.CancelledError()])
async def test_failed_aopen_releases_partial_driver(monkeypatch, failure):
    closed = []

    async def open_async(self):
        self.ptr = object()
        raise failure

    async def close_async(self, force=False):
        closed.append(force)
        self.ptr = None

    monkeypatch.setattr(Cli, "open_async", open_async)
    monkeypatch.setattr(Cli, "close_async", close_async)
    plugin = ScrapliCore()
    with pytest.raises(type(failure)):
        await plugin.aopen("router", None, None, None, None)
    assert closed == [True]
    assert plugin.connection is None


@pytest.mark.asyncio
async def test_failed_aopen_cleanup_error_keeps_original(monkeypatch):
    async def open_async(self):
        self.ptr = object()
        raise OSError("refused")

    async def close_async(self, force=False):
        raise RuntimeError("cleanup failed")

    monkeypatch.setattr(Cli, "open_async", open_async)
    monkeypatch.setattr(Cli, "close_async", close_async)
    with pytest.raises(OSError, match="refused"):
        await ScrapliCore().aopen("router", None, None, None, None)


@pytest.mark.asyncio
async def test_failed_aopen_without_driver_skips_cleanup(monkeypatch):
    closed = []

    async def open_async(self):
        raise OSError("refused")

    monkeypatch.setattr(Cli, "open_async", open_async)
    monkeypatch.setattr(Cli, "close_async", asyncify(lambda self, **kw: closed.append(True)))
    with pytest.raises(OSError):
        await ScrapliCore().aopen("router", None, None, None, None)
    assert closed == []


@pytest.mark.asyncio
async def test_failed_aclose_can_be_retried(monkeypatch):
    attempts = []

    async def close_async(self):
        attempts.append(True)
        if len(attempts) == 1:
            raise OSError("close failed")

    monkeypatch.setattr(Cli, "open_async", asyncify(lambda self: None))
    monkeypatch.setattr(Cli, "close_async", close_async)
    plugin = ScrapliCore()
    await plugin.aopen("router", None, None, None, None)
    with pytest.raises(OSError):
        await plugin.aclose()
    assert plugin.connection is not None
    await plugin.aclose()
    assert plugin.connection is None
    assert len(attempts) == 2


@pytest.mark.asyncio
async def test_connection_is_bound_to_opening_mode(nornir, monkeypatch):
    calls = []
    monkeypatch.setattr(Cli, "open", lambda self: calls.append("open"))
    monkeypatch.setattr(Cli, "close", lambda self: calls.append("close"))
    monkeypatch.setattr(Cli, "open_async", asyncify(lambda self: calls.append("open_async")))
    monkeypatch.setattr(Cli, "close_async", asyncify(lambda self: calls.append("close_async")))
    host = nornir.inventory.hosts["sea-ios-1"]
    connection = await host.aget_connection("scrapli", nornir.config)
    assert isinstance(connection, Cli)
    assert host.connection_mode("scrapli") == "asyncio"
    with pytest.raises(ConnectionModeMismatchError):
        host.get_connection("scrapli", nornir.config)
    await host.aclose_connection("scrapli")
    assert host.get_connection("scrapli", nornir.config) is not connection
    assert host.connection_mode("scrapli") == "sync"
    host.close_connection("scrapli")
    assert calls == ["open_async", "close_async", "open", "close"]


@pytest.mark.asyncio
async def test_async_with_nornir_closes_connections(async_nornir, monkeypatch):
    closed = []
    monkeypatch.setattr(Cli, "open_async", asyncify(lambda self: None))
    monkeypatch.setattr(Netconf, "open_async", asyncify(lambda self: None))
    monkeypatch.setattr(Cli, "close_async", asyncify(lambda self: closed.append("cli")))
    monkeypatch.setattr(Netconf, "close_async", asyncify(lambda self: closed.append("netconf")))

    async def open_both(task):
        await task.host.aget_connection("scrapli", task.nornir.config)
        await task.host.aget_connection("scrapli_netconf", task.nornir.config)

    async with async_nornir as nr:
        result = await nr.arun(task=open_both)
        assert not result.failed
    assert sorted(closed) == ["cli", "netconf"]
    assert nornir_connections(async_nornir) == {}


def nornir_connections(nr):
    return dict(nr.inventory.hosts["sea-ios-1"].connections)

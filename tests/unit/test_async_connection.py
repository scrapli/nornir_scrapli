import asyncio
from types import SimpleNamespace

import pytest
from scrapli.driver.core import AsyncIOSXEDriver, IOSXEDriver
from scrapli.driver.generic import AsyncGenericDriver
from scrapli_cfg.platform.core.cisco_iosxe.async_platform import AsyncScrapliCfgIOSXE
from scrapli_cfg.platform.core.cisco_iosxe.sync_platform import ScrapliCfgIOSXE

from nornir.core.configuration import Config
from nornir_scrapli import exceptions
from nornir_scrapli.connection import ScrapliConfig, ScrapliCore


def task_for(host, nr):
    return SimpleNamespace(host=host, nornir=nr)


def set_transport(host, transport):
    options = host.get_connection_parameters("scrapli")
    options.extras = {**options.extras, "transport": transport}
    host.connection_options["scrapli"] = options


def test_capability_discovery_and_sync_guard(nornir, monkeypatch):
    monkeypatch.setattr(IOSXEDriver, "open", lambda self: None)
    monkeypatch.setattr(IOSXEDriver, "close", lambda self: None)
    host = nornir.inventory.hosts["sea-ios-1"]
    task = task_for(host, nornir)
    conn = ScrapliCore.get_connection(task)
    assert isinstance(conn, IOSXEDriver)
    assert ScrapliCore.get_connection(task) is conn
    with pytest.raises(exceptions.NornirScrapliConnectionModeError, match=r"sync.*asyncio"):
        asyncio.run(ScrapliCore.aget_connection(task))
    with pytest.raises(exceptions.NornirScrapliConnectionModeError):
        asyncio.run(host.aclose_connection("scrapli"))
    assert host.get_connection("scrapli", nornir.config) is conn
    host.close_connection("scrapli")


def test_async_guard_reuse_and_reopen(nornir, monkeypatch):
    async def no_io(self):
        pass

    monkeypatch.setattr(AsyncIOSXEDriver, "open", no_io)
    monkeypatch.setattr(AsyncIOSXEDriver, "close", no_io)
    monkeypatch.setattr(IOSXEDriver, "open", lambda self: None)
    host = nornir.inventory.hosts["sea-ios-1"]
    set_transport(host, "asyncssh")
    task = task_for(host, nornir)

    async def exercise():
        conn = await ScrapliCore.aget_connection(task)
        assert isinstance(conn, AsyncIOSXEDriver)
        assert await ScrapliCore.aget_connection(task) is conn
        with pytest.raises(exceptions.NornirScrapliConnectionModeError, match=r"asyncio.*sync"):
            ScrapliCore.get_connection(task)
        plugin = host.connections["scrapli"]
        with pytest.raises(exceptions.NornirScrapliConnectionModeError):
            plugin.close()
        await host.aclose_connection("scrapli")
        await plugin.aclose()
        plugin.close()
        assert not host.connections

    asyncio.run(exercise())
    set_transport(host, "system")
    assert isinstance(ScrapliCore.get_connection(task), IOSXEDriver)


@pytest.mark.parametrize("cancelled", [False, True])
def test_failed_async_open_reclaims_partial_driver(monkeypatch, cancelled):
    drivers = []

    class PartialDriver:
        def __init__(self, **kwargs):
            self.closed = False
            drivers.append(self)

        async def open(self):
            if cancelled:
                raise asyncio.CancelledError
            raise RuntimeError("opening failed")

        async def close(self):
            await asyncio.sleep(0)
            self.closed = True

    monkeypatch.setattr("nornir_scrapli.connection.AsyncScrapli", PartialDriver, raising=False)
    plugin = ScrapliCore()

    async def exercise():
        error = asyncio.CancelledError if cancelled else RuntimeError
        with pytest.raises(error):
            await plugin.aopen("router", "user", "password", None, "ios", configuration=Config())
        assert drivers[0].closed
        assert plugin.connection is None
        await plugin.aclose()

    asyncio.run(exercise())


def test_async_close_failure_can_be_retried(monkeypatch):
    class Driver:
        def __init__(self, **kwargs):
            self.closes = 0

        async def open(self):
            pass

        async def close(self):
            self.closes += 1
            if self.closes == 1:
                raise RuntimeError("closing failed")

    monkeypatch.setattr("nornir_scrapli.connection.AsyncScrapli", Driver, raising=False)
    plugin = ScrapliCore()

    async def exercise():
        await plugin.aopen("router", "user", "password", None, "ios")
        conn = plugin.connection
        with pytest.raises(RuntimeError, match="closing failed"):
            await plugin.aclose()
        assert plugin.connection is conn
        await plugin.aclose()
        assert conn.closes == 2
        assert plugin.connection is None

    asyncio.run(exercise())


def test_async_generic_parameters_and_inventory_immutability(monkeypatch):
    async def no_io(self):
        pass

    monkeypatch.setattr(AsyncGenericDriver, "open", no_io)
    monkeypatch.setattr(AsyncGenericDriver, "close", no_io)
    extras = {"channel_log": True, "auth_strict_key": False}
    plugin = ScrapliCore()

    async def exercise():
        await plugin.aopen("router", None, None, None, "generic", extras=extras)
        assert isinstance(plugin.connection, AsyncGenericDriver)
        assert plugin.connection.transport_name == "asyncssh"
        assert (
            plugin.connection.channel._base_channel_args.channel_log == "scrapli_channel_router.log"
        )
        await plugin.aclose()

    asyncio.run(exercise())
    assert extras == {"channel_log": True, "auth_strict_key": False}


def test_async_cfg_wraps_shared_driver_once(nornir, monkeypatch):
    prepared = []

    async def no_io(self):
        pass

    async def prepare(self):
        prepared.append(self)

    monkeypatch.setattr(AsyncIOSXEDriver, "open", no_io)
    monkeypatch.setattr(AsyncIOSXEDriver, "close", no_io)
    monkeypatch.setattr(AsyncScrapliCfgIOSXE, "prepare", prepare)
    host = nornir.inventory.hosts["sea-ios-1"]
    set_transport(host, "asyncssh")
    task = task_for(host, nornir)

    async def exercise():
        cli = await ScrapliCore.aget_connection(task)
        cfg = await ScrapliConfig.aget_connection(task)
        assert cfg.conn is cli
        assert cfg.dedicated_connection is False
        assert await ScrapliConfig.aget_connection(task) is cfg
        assert prepared == [cfg]
        with pytest.raises(exceptions.NornirScrapliConnectionModeError):
            ScrapliConfig.get_connection(task)
        await host.aclose_connection("scrapli_cfg")
        assert await ScrapliCore.aget_connection(task) is cli
        await host.aclose_connections()
        assert not host.connections

    asyncio.run(exercise())


def test_async_cfg_prepare_failure_keeps_cli(nornir, monkeypatch):
    async def no_io(self):
        pass

    async def fail(self):
        raise RuntimeError("prepare failed")

    monkeypatch.setattr(AsyncIOSXEDriver, "open", no_io)
    monkeypatch.setattr(AsyncIOSXEDriver, "close", no_io)
    monkeypatch.setattr(AsyncScrapliCfgIOSXE, "prepare", fail)
    host = nornir.inventory.hosts["sea-ios-1"]
    set_transport(host, "asyncssh")
    task = task_for(host, nornir)

    async def exercise():
        cli = await ScrapliCore.aget_connection(task)
        with pytest.raises(RuntimeError, match="prepare failed"):
            await ScrapliConfig.aget_connection(task)
        assert "scrapli_cfg" not in host.connections
        assert await ScrapliCore.aget_connection(task) is cli
        await host.aclose_connections()

    asyncio.run(exercise())


@pytest.mark.parametrize("wrapper_mode", ["sync", "asyncio"])
@pytest.mark.parametrize("reopened_mode", ["sync", "asyncio"])
def test_cfg_rejects_stale_shared_driver(nornir, monkeypatch, wrapper_mode, reopened_mode):
    async def no_io(self):
        pass

    monkeypatch.setattr(IOSXEDriver, "open", lambda self: None)
    monkeypatch.setattr(IOSXEDriver, "close", lambda self: None)
    monkeypatch.setattr(ScrapliCfgIOSXE, "prepare", lambda self: None)
    monkeypatch.setattr(AsyncIOSXEDriver, "open", no_io)
    monkeypatch.setattr(AsyncIOSXEDriver, "close", no_io)
    monkeypatch.setattr(AsyncScrapliCfgIOSXE, "prepare", no_io)
    host = nornir.inventory.hosts["sea-ios-1"]
    task = task_for(host, nornir)

    async def exercise():
        set_transport(host, "system" if wrapper_mode == "sync" else "asyncssh")
        if wrapper_mode == "sync":
            cfg = ScrapliConfig.get_connection(task)
            host.close_connection("scrapli")
        else:
            cfg = await ScrapliConfig.aget_connection(task)
            await host.aclose_connection("scrapli")
        set_transport(host, "system" if reopened_mode == "sync" else "asyncssh")
        if reopened_mode == "sync":
            cli = ScrapliCore.get_connection(task)
        else:
            cli = await ScrapliCore.aget_connection(task)
        assert cfg.conn is not cli
        with pytest.raises(exceptions.NornirScrapliException, match=r"close|Close"):
            if wrapper_mode == "sync":
                ScrapliConfig.get_connection(task)
            else:
                await ScrapliConfig.aget_connection(task)
        assert host.connections["scrapli_cfg"].connection is cfg
        assert host.connections["scrapli"].connection is cli
        if wrapper_mode == "sync":
            host.close_connection("scrapli_cfg")
        else:
            await host.aclose_connection("scrapli_cfg")
        if reopened_mode == "sync":
            assert ScrapliConfig.get_connection(task).conn is cli
            host.close_connections()
        else:
            assert (await ScrapliConfig.aget_connection(task)).conn is cli
            await host.aclose_connections()

    asyncio.run(exercise())

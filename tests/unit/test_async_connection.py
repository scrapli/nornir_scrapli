import asyncio
from types import SimpleNamespace

import pytest
from scrapli.driver.core import AsyncIOSXEDriver, IOSXEDriver
from scrapli.driver.generic import AsyncGenericDriver
from scrapli_cfg.platform.core.cisco_iosxe.async_platform import AsyncScrapliCfgIOSXE
from scrapli_cfg.platform.core.cisco_iosxe.sync_platform import ScrapliCfgIOSXE

from nornir.core.configuration import Config
from nornir.core.exceptions import ConnectionModeMismatchError
from nornir_scrapli import exceptions
from nornir_scrapli.connection import ScrapliConfig, ScrapliCore


def task_for(host, nr):
    return SimpleNamespace(host=host, nornir=nr)


def set_transport(host, transport):
    options = host.get_connection_parameters("scrapli")
    options.extras = {**options.extras, "transport": transport}
    host.connection_options["scrapli"] = options


@pytest.mark.asyncio
async def test_capability_discovery_and_sync_guard(nornir, monkeypatch):
    closed = []

    def close(driver):
        closed.append(driver)

    monkeypatch.setattr(IOSXEDriver, "open", lambda self: None)
    monkeypatch.setattr(IOSXEDriver, "close", close)
    host = nornir.inventory.hosts["sea-ios-1"]
    conn = host.get_connection("scrapli", nornir.config)
    assert isinstance(conn, IOSXEDriver)
    assert host.connection_mode("scrapli") == "sync"
    assert host.get_connection("scrapli", nornir.config) is conn
    with pytest.raises(ConnectionModeMismatchError):
        await host.aget_connection("scrapli", nornir.config)
    assert host.get_connection("scrapli", nornir.config) is conn
    assert not closed
    await host.aclose_connection("scrapli")
    assert closed == [conn]
    assert host.connection_mode("scrapli") is None
    assert "scrapli" not in host.connections


@pytest.mark.asyncio
async def test_async_guard_reuse_and_reopen(nornir, monkeypatch):
    async def no_io(self):
        pass

    monkeypatch.setattr(AsyncIOSXEDriver, "open", no_io)
    monkeypatch.setattr(AsyncIOSXEDriver, "close", no_io)
    monkeypatch.setattr(IOSXEDriver, "open", lambda self: None)
    monkeypatch.setattr(IOSXEDriver, "close", lambda self: None)
    host = nornir.inventory.hosts["sea-ios-1"]
    set_transport(host, "asyncssh")
    conn = await host.aget_connection("scrapli", nornir.config)
    assert isinstance(conn, AsyncIOSXEDriver)
    assert host.connection_mode("scrapli") == "asyncio"
    assert await host.aget_connection("scrapli", nornir.config) is conn
    with pytest.raises(ConnectionModeMismatchError):
        host.get_connection("scrapli", nornir.config)
    plugin = host.connections["scrapli"]
    with pytest.raises(ConnectionModeMismatchError, match="aclose_connection"):
        host.close_connection("scrapli")
    assert host.connections["scrapli"] is plugin
    assert host.connection_mode("scrapli") == "asyncio"
    await host.aclose_connection("scrapli")
    await plugin.aclose()
    plugin.close()
    assert not host.connections
    assert host.connection_mode("scrapli") is None
    set_transport(host, "system")
    assert isinstance(host.get_connection("scrapli", nornir.config), IOSXEDriver)
    assert host.connection_mode("scrapli") == "sync"
    await host.aclose_connection("scrapli")


@pytest.mark.parametrize("cancelled", [False, True])
@pytest.mark.asyncio
async def test_failed_async_open_reclaims_partial_driver(monkeypatch, cancelled):
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

    error = asyncio.CancelledError if cancelled else RuntimeError
    with pytest.raises(error):
        await plugin.aopen("router", "user", "password", None, "ios", configuration=Config())
    assert drivers[0].closed
    assert plugin.connection is None
    await plugin.aclose()


@pytest.mark.asyncio
async def test_async_close_failure_can_be_retried(nornir, monkeypatch):
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
    host = nornir.inventory.hosts["sea-ios-1"]
    conn = await host.aget_connection("scrapli", nornir.config)
    plugin = host.connections["scrapli"]
    with pytest.raises(RuntimeError, match="closing failed"):
        await host.aclose_connection("scrapli")
    assert plugin.connection is conn
    assert host.connections["scrapli"] is plugin
    assert host.connection_mode("scrapli") == "asyncio"
    assert await host.aget_connection("scrapli", nornir.config) is conn
    await host.aclose_connection("scrapli")
    assert conn.closes == 2
    assert plugin.connection is None
    assert host.connection_mode("scrapli") is None


@pytest.mark.asyncio
async def test_async_generic_parameters_and_inventory_immutability(monkeypatch):
    async def no_io(self):
        pass

    monkeypatch.setattr(AsyncGenericDriver, "open", no_io)
    monkeypatch.setattr(AsyncGenericDriver, "close", no_io)
    extras = {"channel_log": True, "auth_strict_key": False}
    plugin = ScrapliCore()

    await plugin.aopen("router", None, None, None, "generic", extras=extras)
    assert isinstance(plugin.connection, AsyncGenericDriver)
    assert plugin.connection.transport_name == "asyncssh"
    assert plugin.connection.channel._base_channel_args.channel_log == "scrapli_channel_router.log"
    await plugin.aclose()
    assert extras == {"channel_log": True, "auth_strict_key": False}


@pytest.mark.asyncio
async def test_async_cfg_wraps_shared_driver_once(nornir, monkeypatch):
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

    cli = await host.aget_connection("scrapli", nornir.config)
    cfg = await ScrapliConfig.aget_connection(task)
    assert cfg.conn is cli
    assert cfg.dedicated_connection is False
    assert await ScrapliConfig.aget_connection(task) is cfg
    assert prepared == [cfg]
    with pytest.raises(ConnectionModeMismatchError):
        ScrapliConfig.get_connection(task)
    await host.aclose_connection("scrapli_cfg")
    assert await host.aget_connection("scrapli", nornir.config) is cli
    await host.aclose_connections()
    assert not host.connections


@pytest.mark.asyncio
async def test_async_cfg_prepare_failure_keeps_cli(nornir, monkeypatch):
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

    cli = await host.aget_connection("scrapli", nornir.config)
    with pytest.raises(RuntimeError, match="prepare failed"):
        await ScrapliConfig.aget_connection(task)
    assert "scrapli_cfg" not in host.connections
    assert await host.aget_connection("scrapli", nornir.config) is cli
    await host.aclose_connections()


@pytest.mark.parametrize("wrapper_mode", ["sync", "asyncio"])
@pytest.mark.parametrize("reopened_mode", ["sync", "asyncio"])
@pytest.mark.asyncio
async def test_cfg_rejects_stale_shared_driver(nornir, monkeypatch, wrapper_mode, reopened_mode):
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

    set_transport(host, "system" if wrapper_mode == "sync" else "asyncssh")
    if wrapper_mode == "sync":
        cfg = ScrapliConfig.get_connection(task)
        host.close_connection("scrapli")
    else:
        cfg = await ScrapliConfig.aget_connection(task)
        await host.aclose_connection("scrapli")
    set_transport(host, "system" if reopened_mode == "sync" else "asyncssh")
    if reopened_mode == "sync":
        cli = host.get_connection("scrapli", nornir.config)
    else:
        cli = await host.aget_connection("scrapli", nornir.config)
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


@pytest.mark.parametrize("mode", ["sync", "asyncio"])
@pytest.mark.asyncio
async def test_async_host_cleanup_closes_shared_driver_once(nornir, monkeypatch, mode):
    closed = []

    async def no_io(self):
        pass

    async def async_close(self):
        closed.append(self)

    def sync_close(driver):
        closed.append(driver)

    monkeypatch.setattr(IOSXEDriver, "open", lambda self: None)
    monkeypatch.setattr(IOSXEDriver, "close", sync_close)
    monkeypatch.setattr(ScrapliCfgIOSXE, "prepare", lambda self: None)
    monkeypatch.setattr(AsyncIOSXEDriver, "open", no_io)
    monkeypatch.setattr(AsyncIOSXEDriver, "close", async_close)
    monkeypatch.setattr(AsyncScrapliCfgIOSXE, "prepare", no_io)
    host = nornir.inventory.hosts["sea-ios-1"]
    set_transport(host, "system" if mode == "sync" else "asyncssh")
    task = task_for(host, nornir)
    cfg = (
        ScrapliConfig.get_connection(task)
        if mode == "sync"
        else await ScrapliConfig.aget_connection(task)
    )
    driver = cfg.conn
    assert host.connection_mode("scrapli") == mode
    assert host.connection_mode("scrapli_cfg") == mode

    await host.aclose_connections()

    assert closed == [driver]
    assert not host.connections
    assert host.connection_mode("scrapli") is None
    assert host.connection_mode("scrapli_cfg") is None


@pytest.mark.asyncio
async def test_mixed_legacy_and_async_connections_use_nornir_cleanup(nornir, monkeypatch):
    from scrapli_netconf.driver import NetconfDriver

    closed = []

    async def no_io(self):
        pass

    async def async_close(self):
        closed.append("scrapli")

    monkeypatch.setattr(NetconfDriver, "open", lambda self: None)
    monkeypatch.setattr(NetconfDriver, "close", lambda self: closed.append("scrapli_netconf"))
    monkeypatch.setattr(AsyncIOSXEDriver, "open", no_io)
    monkeypatch.setattr(AsyncIOSXEDriver, "close", async_close)
    host = nornir.inventory.hosts["sea-ios-1"]
    host.get_connection("scrapli_netconf", nornir.config)
    set_transport(host, "asyncssh")
    await host.aget_connection("scrapli", nornir.config)
    assert host.connection_mode("scrapli_netconf") == "sync"
    assert host.connection_mode("scrapli") == "asyncio"

    await host.aclose_connections()

    assert closed == ["scrapli_netconf", "scrapli"]
    assert not host.connections

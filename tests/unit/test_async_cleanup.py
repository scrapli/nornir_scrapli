import asyncio

import pytest
from scrapli.driver.core import AsyncIOSXEDriver

from nornir_scrapli.connection import ScrapliCore


def test_dead_async_transport_skips_device_close_hook(monkeypatch):
    async def open_without_io(self):
        pass

    async def device_hook(self):
        raise AssertionError("device hook must not run on a closed transport")

    monkeypatch.setattr(AsyncIOSXEDriver, "open", open_without_io)
    plugin = ScrapliCore()

    async def exercise():
        await plugin.aopen("router", None, None, None, "ios", extras={"on_close": device_hook})
        assert not plugin.connection.isalive()
        await plugin.aclose()
        assert plugin.connection is None

    asyncio.run(exercise())


def test_partial_async_open_closes_channel_log(monkeypatch, tmp_path):
    drivers = []

    async def fail_after_channel_open(self):
        self.channel.open()
        drivers.append(self)
        raise RuntimeError("open failed")

    monkeypatch.setattr(AsyncIOSXEDriver, "open", fail_after_channel_open)
    plugin = ScrapliCore()

    async def exercise():
        with pytest.raises(RuntimeError, match="open failed"):
            await plugin.aopen(
                "router",
                None,
                None,
                None,
                "ios",
                extras={"channel_log": str(tmp_path / "channel.log")},
            )
        assert drivers[0].channel.channel_log.closed

    asyncio.run(exercise())

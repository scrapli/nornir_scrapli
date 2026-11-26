import asyncio

import pytest
from conftest import asyncify
from scrapli import Cli, Netconf
from scrapli.netconf import DatastoreType

from nornir.core.exceptions import TaskTimeoutError
from nornir.plugins.runners import AsyncioRunner
from nornir_scrapli import async_tasks


async def hang(self, **kwargs):
    await asyncio.sleep(30)


@pytest.mark.asyncio
async def test_concurrent_subtasks_share_one_open(async_nornir, monkeypatch):
    opened = []

    async def open_async(self):
        opened.append(self)
        await asyncio.sleep(0)

    monkeypatch.setattr(Cli, "open_async", open_async)
    monkeypatch.setattr(Cli, "close_async", asyncify(lambda self: None))

    async def get_twice(task):
        return await asyncio.gather(
            task.host.aget_connection("scrapli", task.nornir.config),
            task.host.aget_connection("scrapli", task.nornir.config),
        )

    async with async_nornir as nr:
        result = (await nr.arun(task=get_twice))["sea-ios-1"][0]
    assert result.exception is None
    assert len(opened) == 1
    assert result.result[0] is result.result[1] is opened[0]


@pytest.mark.asyncio
async def test_per_host_timeout_stops_task_and_keeps_connection(nornir, monkeypatch):
    monkeypatch.setattr(Cli, "open_async", asyncify(lambda self: None))
    monkeypatch.setattr(Cli, "close_async", asyncify(lambda self: None))
    monkeypatch.setattr(Cli, "send_input_async", hang)
    nr = nornir.with_runner(AsyncioRunner(num_workers=2, per_host_timeout=0.05))
    host = nr.inventory.hosts["sea-ios-1"]
    async with nr:
        result = (await nr.arun(task=async_tasks.send_command, command="show version"))[
            "sea-ios-1"
        ][0]
        assert result.failed is True
        assert isinstance(result.exception, TaskTimeoutError)
        assert host.connection_mode("scrapli") == "asyncio"
    assert host.connection_mode("scrapli") is None


@pytest.mark.asyncio
async def test_per_host_timeout_during_open_releases_driver(nornir, monkeypatch):
    closed = []

    async def open_async(self):
        self.ptr = object()
        await asyncio.sleep(30)

    async def close_async(self, force=False):
        closed.append(force)
        self.ptr = None

    monkeypatch.setattr(Cli, "open_async", open_async)
    monkeypatch.setattr(Cli, "close_async", close_async)
    nr = nornir.with_runner(AsyncioRunner(num_workers=2, per_host_timeout=0.05))
    result = (await nr.arun(task=async_tasks.get_prompt))["sea-ios-1"][0]
    assert isinstance(result.exception, TaskTimeoutError)
    assert closed == [True]
    assert nr.inventory.hosts["sea-ios-1"].connection_mode("scrapli") is None


@pytest.mark.asyncio
async def test_timeout_during_dry_run_edit_discards_candidate(
    nornir, monkeypatch, make_netconf_result
):
    calls = []
    monkeypatch.setattr(Netconf, "open_async", asyncify(lambda self: None))
    monkeypatch.setattr(Netconf, "close_async", asyncify(lambda self: None))
    monkeypatch.setattr(Netconf, "edit_config_async", hang)
    monkeypatch.setattr(
        Netconf,
        "discard_async",
        asyncify(lambda self, **kwargs: calls.append("discard") or make_netconf_result()),
    )
    nr = nornir.with_runner(AsyncioRunner(num_workers=2, per_host_timeout=0.05))
    async with nr:
        result = (
            await nr.arun(
                task=async_tasks.netconf_edit_config,
                config="<config/>",
                dry_run=True,
                target=DatastoreType.CANDIDATE,
            )
        )["sea-ios-1"][0]
    assert isinstance(result.exception, TaskTimeoutError)
    assert calls == ["discard"]


@pytest.mark.asyncio
@pytest.mark.parametrize("restore_fails", [False, True])
async def test_timeout_during_dry_run_config_restores_mode(
    nornir, monkeypatch, make_cli_result, restore_fails
):
    modes = []

    async def enter_mode(self, *, requested_mode, **kwargs):
        modes.append(requested_mode)
        if requested_mode == "configuration":
            await asyncio.sleep(30)
        result = make_cli_result(failed_indicator="error" if restore_fails else "")
        assert result.failed is restore_fails
        return result

    monkeypatch.setattr(Cli, "open_async", asyncify(lambda self: None))
    monkeypatch.setattr(Cli, "close_async", asyncify(lambda self: None))
    monkeypatch.setattr(
        "nornir_scrapli.async_tasks.core.mode.get_current_mode",
        asyncify(lambda *args: "privileged_exec"),
    )
    monkeypatch.setattr(Cli, "enter_mode_async", enter_mode)
    nr = nornir.with_runner(AsyncioRunner(num_workers=2, per_host_timeout=0.05))
    async with nr:
        result = (await nr.arun(task=async_tasks.send_configs, configs=["a"], dry_run=True))[
            "sea-ios-1"
        ][0]
    assert modes == ["configuration", "privileged_exec"]
    assert isinstance(result.exception, TaskTimeoutError)

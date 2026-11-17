from importlib.metadata import distribution


def test_public_surface_v2():
    from nornir_scrapli import connection, tasks

    assert not hasattr(connection, "ScrapliConfig")
    assert not any(name.startswith("cfg_") for name in tasks.__all__)
    entries = {(e.group, e.name) for e in distribution("nornir_scrapli").entry_points}
    assert entries == {
        ("nornir.plugins.capability_connections", "scrapli"),
        ("nornir.plugins.capability_connections", "scrapli_netconf"),
    }


def test_async_tasks_mirror_sync_tasks():
    import inspect

    from nornir_scrapli import async_tasks, tasks

    assert async_tasks.__all__ == tasks.__all__
    for name in tasks.__all__:
        sync_task, async_task = getattr(tasks, name), getattr(async_tasks, name)
        assert inspect.iscoroutinefunction(async_task)
        assert not inspect.iscoroutinefunction(sync_task)
        assert inspect.signature(async_task) == inspect.signature(sync_task)


def test_v2_dependencies():
    requirements = distribution("nornir_scrapli").requires
    assert "scrapli>=2026.10.8" in requirements
    assert not any(
        r.split(">=")[0] in {"scrapli_cfg", "scrapli_netconf", "scrapli_community"}
        for r in requirements
    )

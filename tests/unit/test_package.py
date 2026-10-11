from importlib.metadata import distribution


def test_public_surface_v2():
    from nornir_scrapli import connection, tasks

    assert not hasattr(connection, "ScrapliConfig")
    assert not any(name.startswith("cfg_") for name in tasks.__all__)
    entries = {e.name for e in distribution("nornir_scrapli").entry_points}
    assert entries == {"scrapli", "scrapli_netconf"}


def test_v2_dependencies():
    requirements = distribution("nornir_scrapli").requires
    assert "scrapli>=2026.10.8" in requirements
    assert not any(
        r.split(">=")[0] in {"scrapli_cfg", "scrapli_netconf", "scrapli_community"}
        for r in requirements
    )

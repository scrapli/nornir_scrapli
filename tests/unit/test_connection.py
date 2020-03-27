from nornir.core.connections import Connections


def test_connection_registration(nornir):
    assert "scrapli" not in Connections.available
    from nornir_scrapli.tasks import get_prompt

    assert "scrapli" in Connections.available


def test_connection_setup(nornir):
    scrapli_conn = nornir.inventory.hosts["sea-ios-1"].get_connection(
        "scrapli", nornir.config
    )
    assert scrapli_conn.transport.host == "172.18.0.11"
    assert scrapli_conn.transport.port == 22
    assert scrapli_conn.transport.auth_username == "vrnetlab"
    assert scrapli_conn.transport.auth_password == "VR-netlab9"
    assert scrapli_conn.transport.auth_strict_key is False

import os

import pytest
from nornir import InitNornir
from nornir.core.state import GlobalState

global_data = GlobalState(dry_run=True)


@pytest.fixture(scope="function", autouse=True)
def nornir():
    """Initializes nornir"""
    dir_path = os.path.dirname(os.path.realpath(__file__))

    nornir = InitNornir(
        inventory={
            "options": {
                "host_file": "{}/inventory_data/hosts.yaml".format(dir_path),
                "group_file": "{}/inventory_data/groups.yaml".format(dir_path),
                "defaults_file": "{}/inventory_data/defaults.yaml".format(dir_path),
            }
        },
        dry_run=True,
    )
    nornir.data = global_data
    return nornir


@pytest.fixture(scope="function", autouse=True)
def nornir_generic():
    """Initializes nornir"""
    dir_path = os.path.dirname(os.path.realpath(__file__))

    nornir = InitNornir(
        inventory={
            "options": {
                "host_file": "{}/inventory_data/hosts_generic.yaml".format(dir_path),
                "group_file": "{}/inventory_data/groups.yaml".format(dir_path),
                "defaults_file": "{}/inventory_data/defaults.yaml".format(dir_path),
            }
        },
        dry_run=True,
    )
    nornir.data = global_data
    return nornir


@pytest.fixture(scope="function", autouse=True)
def nornir_raise_on_error():
    """Initializes nornir"""
    dir_path = os.path.dirname(os.path.realpath(__file__))

    nornir = InitNornir(
        inventory={
            "options": {
                "host_file": "{}/inventory_data/hosts.yaml".format(dir_path),
                "group_file": "{}/inventory_data/groups.yaml".format(dir_path),
                "defaults_file": "{}/inventory_data/defaults.yaml".format(dir_path),
            }
        },
        core={"raise_on_error": True},
        dry_run=True,
    )
    nornir.data = global_data
    return nornir


@pytest.fixture(scope="function", autouse=True)
def reset_data():
    global_data.dry_run = True
    global_data.reset_failed_hosts()

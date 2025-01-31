import os

import pytest

from nornir import InitNornir


@pytest.fixture(scope="function", autouse=True)
def nornir():
    """Initializes nornir"""
    dir_path = os.path.dirname(os.path.realpath(__file__))

    nornir = InitNornir(
        inventory={
            "plugin": "YAMLInventory",
            "options": {
                "host_file": "{}/inventory_data/hosts.yaml".format(dir_path),
                "group_file": "{}/inventory_data/groups.yaml".format(dir_path),
                "defaults_file": "{}/inventory_data/defaults.yaml".format(dir_path),
            },
        },
        dry_run=False,
        logging={"enabled": False},
    )
    return nornir


@pytest.fixture(scope="function", autouse=True)
def nornir_global_dry_run():
    """Initializes nornir"""
    dir_path = os.path.dirname(os.path.realpath(__file__))

    nornir_global_dry_run = InitNornir(
        inventory={
            "plugin": "YAMLInventory",
            "options": {
                "host_file": "{}/inventory_data/hosts.yaml".format(dir_path),
                "group_file": "{}/inventory_data/groups.yaml".format(dir_path),
                "defaults_file": "{}/inventory_data/defaults.yaml".format(dir_path),
            },
        },
        dry_run=True,
        logging={"enabled": False},
    )
    return nornir_global_dry_run


@pytest.fixture(scope="function", autouse=True)
def nornir_community():
    """Initializes nornir"""
    dir_path = os.path.dirname(os.path.realpath(__file__))

    nornir = InitNornir(
        inventory={
            "plugin": "YAMLInventory",
            "options": {
                "host_file": "{}/inventory_data/hosts.yaml".format(dir_path),
                "group_file": "{}/inventory_data/community_groups.yaml".format(dir_path),
                "defaults_file": "{}/inventory_data/defaults.yaml".format(dir_path),
            },
        },
        dry_run=False,
        logging={"enabled": False},
    )
    return nornir


@pytest.fixture(scope="function", autouse=True)
def nornir_generic():
    """Initializes nornir"""
    dir_path = os.path.dirname(os.path.realpath(__file__))

    nornir = InitNornir(
        inventory={
            "plugin": "YAMLInventory",
            "options": {
                "host_file": "{}/inventory_data/hosts_generic.yaml".format(dir_path),
                "group_file": "{}/inventory_data/groups.yaml".format(dir_path),
                "defaults_file": "{}/inventory_data/defaults.yaml".format(dir_path),
            },
        },
        dry_run=False,
        logging={"enabled": False},
    )
    return nornir


@pytest.fixture(scope="function", autouse=True)
def nornir_raise_on_error():
    """Initializes nornir"""
    dir_path = os.path.dirname(os.path.realpath(__file__))

    nornir = InitNornir(
        inventory={
            "plugin": "YAMLInventory",
            "options": {
                "host_file": "{}/inventory_data/hosts.yaml".format(dir_path),
                "group_file": "{}/inventory_data/groups.yaml".format(dir_path),
                "defaults_file": "{}/inventory_data/defaults.yaml".format(dir_path),
            },
        },
        core={"raise_on_error": True},
        logging={"enabled": False},
        dry_run=False,
    )
    return nornir


@pytest.fixture(scope="function", autouse=True)
def nornir_netconf():
    """Initializes nornir"""
    dir_path = os.path.dirname(os.path.realpath(__file__))

    nornir = InitNornir(
        inventory={
            "plugin": "YAMLInventory",
            "options": {
                "host_file": "{}/inventory_data/hosts.yaml".format(dir_path),
                "group_file": "{}/inventory_data/netconf_groups.yaml".format(dir_path),
                "defaults_file": "{}/inventory_data/defaults.yaml".format(dir_path),
            },
        },
        dry_run=False,
        logging={"enabled": False},
    )
    return nornir


@pytest.fixture(scope="function", autouse=True)
def nornir_global_ssh():
    """Initializes nornir"""
    dir_path = os.path.dirname(os.path.realpath(__file__))

    nornir_global_ssh = InitNornir(
        inventory={
            "plugin": "YAMLInventory",
            "options": {
                "host_file": "{}/inventory_data/hosts.yaml".format(dir_path),
                "group_file": "{}/inventory_data/netconf_groups.yaml".format(dir_path),
                "defaults_file": "{}/inventory_data/defaults.yaml".format(dir_path),
            },
        },
        dry_run=False,
        logging={"enabled": False},
        ssh={"config_file": "notarealfile!"},
    )
    return nornir_global_ssh


@pytest.fixture(scope="function", autouse=True)
def nornir_global_ssh_no_connection_option_ssh():
    """Initializes nornir"""
    dir_path = os.path.dirname(os.path.realpath(__file__))

    nornir_global_ssh_no_connection_option_ssh = InitNornir(
        inventory={
            "plugin": "YAMLInventory",
            "options": {
                "host_file": "{}/inventory_data/hosts.yaml".format(dir_path),
                "group_file": "{}/inventory_data/no_ssh_config_groups.yaml".format(dir_path),
                "defaults_file": "{}/inventory_data/defaults.yaml".format(dir_path),
            },
        },
        dry_run=False,
        logging={"enabled": False},
        ssh={"config_file": ""},
    )
    return nornir_global_ssh_no_connection_option_ssh

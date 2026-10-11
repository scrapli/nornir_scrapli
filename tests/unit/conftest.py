import sys
from pathlib import Path

import pytest

from nornir import InitNornir

sys.path.insert(0, str(Path(__file__).parents[1]))


@pytest.fixture
def nornir():
    root = Path(__file__).parents[1] / "inventory_data"
    return InitNornir(
        inventory={
            "plugin": "YAMLInventory",
            "options": {
                "host_file": str(root / "hosts.yaml"),
                "group_file": str(root / "groups.yaml"),
                "defaults_file": str(root / "defaults.yaml"),
            },
        },
        logging={"enabled": False},
    )


@pytest.fixture
def make_cli_result():
    from scrapli.cli_result import Result

    def make(inputs=None, outputs=None, failed_indicator=""):
        inputs = [] if inputs is None else inputs
        outputs = [] if outputs is None else outputs
        packed_inputs = [x.encode() for x in inputs]
        packed_outputs = [x.encode() for x in outputs]
        return Result(
            host="test",
            port=22,
            inputs=b"".join(packed_inputs),
            input_lens=[len(x) for x in packed_inputs],
            start_time=1,
            splits=[2] * len(outputs),
            result_raw_journals=b"",
            result_raw_journal_lens=[0] * len(outputs),
            results=b"".join(packed_outputs),
            result_lens=[len(x) for x in packed_outputs],
            results_failed_indicator=failed_indicator,
            textfsm_platform="cisco_iosxe",
            genie_platform="iosxe",
        )

    return make


@pytest.fixture
def make_netconf_result():
    from scrapli.netconf_result import Result

    def make(output="<ok/>", rpc_errors=""):
        return Result(
            input_="<rpc/>",
            host="test",
            port=830,
            start_time=1,
            end_time=2,
            result_raw_journal=b"",
            _result=output,
            rpc_warnings="",
            rpc_errors=rpc_errors,
        )

    return make

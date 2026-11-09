from importlib import import_module
from importlib.util import find_spec

import pytest

from nornir.core.inventory import Host
from nornir.core.task import AggregatedResult, MultiResult, Result


def aggregate(response):
    from nornir_scrapli.result import ScrapliResult

    result = AggregatedResult("commands")
    multi = MultiResult("commands")
    multi.append(
        ScrapliResult(
            Host("router"), response.result, response, changed=True, diff="diff", name="commands"
        )
    )
    result["router"] = multi
    return result


@pytest.mark.parametrize("to_dict", [True, False])
def test_two_inputs_are_parsed_without_mutation(monkeypatch, make_cli_result, to_dict):
    from nornir_scrapli.functions import print_structured_result

    native = make_cli_result(
        ["show ip route", "show ip route"],
        [
            "Gateway of last resort is not set\nC        10.0.0.0/24 is directly connected, GigabitEthernet1",
            "Gateway of last resort is not set\nC        10.1.0.0/24 is directly connected, GigabitEthernet2",
        ],
    )
    original = aggregate(native)
    printed = []
    module = import_module("nornir_scrapli.functions.print_structured_result")
    monkeypatch.setattr(module, "_print_result", lambda **kwargs: printed.append(kwargs["result"]))
    print_structured_result(original, to_dict=to_dict)
    entries = printed[0]["router"]
    assert len(entries) == 2
    assert "10.0.0.0" in str(entries[0].result)
    assert "10.1.0.0" in str(entries[1].result)
    assert isinstance(entries[0].result[0], dict if to_dict else list)
    assert entries[0].changed is True
    assert entries[1].diff == "diff"
    assert original["router"][0].result == native.result
    assert len(original["router"]) == 1


@pytest.mark.parametrize("fallback", [True, False])
def test_parser_failure_fallback(monkeypatch, make_cli_result, fallback):
    from nornir_scrapli.functions import print_structured_result

    original = aggregate(make_cli_result(["nonexistent", "nonexistent"], ["one", "two"]))
    printed = []
    module = import_module("nornir_scrapli.functions.print_structured_result")
    monkeypatch.setattr(module, "_print_result", lambda **kwargs: printed.append(kwargs["result"]))
    print_structured_result(original, fail_to_string=fallback)
    assert [x.result for x in printed[0]["router"]] == (["one", "two"] if fallback else [[], []])


def test_ordinary_results_pass_through(capsys):
    from nornir_scrapli.functions import print_structured_result

    original = AggregatedResult("ordinary")
    original["router"] = MultiResult("ordinary")
    original["router"].append(Result(Host("router"), "plain", name="ordinary"))
    print_structured_result(original)
    assert "plain" in capsys.readouterr().out


@pytest.mark.skipif(
    find_spec("genie") is None, reason="optional Genie dependencies are not installed"
)
def test_genie_indexed_output(make_cli_result, capsys):
    from nornir_scrapli.functions import print_structured_result

    native = make_cli_result(
        ["show ip route", "show ip route"],
        [
            "Gateway of last resort is not set\nC        10.0.0.0/24 is directly connected, GigabitEthernet1",
            "Gateway of last resort is not set\nC        10.1.0.0/24 is directly connected, GigabitEthernet2",
        ],
    )
    print_structured_result(aggregate(native), parser="genie")
    output = capsys.readouterr().out
    assert "10.0.0.0" in output
    assert "10.1.0.0" in output

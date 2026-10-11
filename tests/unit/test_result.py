import pytest

from nornir.core.inventory import Host


@pytest.mark.parametrize(
    "outputs,want", [(["one"], "one"), (["one", "two"], "one\n\ntwo"), ([], "")]
)
def test_command_format(make_cli_result, outputs, want):
    from nornir_scrapli.result import process_command_result

    response = make_cli_result(inputs=["show"] * len(outputs), outputs=outputs)
    assert process_command_result(response) == want


def test_config_format(make_cli_result):
    from nornir_scrapli.result import process_config_result

    assert (
        process_config_result(
            make_cli_result(["interface loopback123", "description neat"], ["", ""])
        )
        == "interface loopback123\ndescription neat\n"
    )
    assert (
        process_config_result(make_cli_result(["set foo"], ["line1\nline2"]))
        == "set foo\nline1\nline2"
    )


@pytest.mark.parametrize("failed", [False, True])
def test_native_failure_and_identity(make_cli_result, make_netconf_result, failed):
    from nornir_scrapli.result import ScrapliResult, process_command_result

    for response in (
        make_cli_result(["show"], ["output"], "error" if failed else ""),
        make_netconf_result(rpc_errors="error" if failed else ""),
    ):
        result = ScrapliResult(
            Host("test"), process_command_result(response), response, diff="diff"
        )
        assert result.failed is failed
        assert result.scrapli_response is response
        assert result.diff == "diff"
    assert ScrapliResult(Host("test"), None).failed is False

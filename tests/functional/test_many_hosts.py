"""Exercise concurrent host output and failure isolation over real SSH."""

from time import monotonic

from scrapli.exceptions import ScrapliAuthenticationFailed, ScrapliTimeout

from functional.constants import (
    AUTH_FAILURE_HOST,
    SECOND_COMMAND,
    SHOW_VERSION_COMMAND,
    TIMEOUT_FAILURE_HOST,
    expected_clock_output,
    expected_version_output,
)
from nornir_scrapli.tasks import send_command


def test_each_host_receives_only_its_own_output(healthy_nornir):
    assert healthy_nornir.runner.num_workers > 1
    assert not healthy_nornir.data.failed_hosts
    healthy_host_names = set(healthy_nornir.inventory.hosts)

    result = healthy_nornir.run(task=send_command, command=SHOW_VERSION_COMMAND)

    assert len(result) > 1
    assert set(result) == healthy_host_names
    assert not result.failed
    for host_name, multi_result in result.items():
        host_result = multi_result[0]
        assert not multi_result.failed
        assert host_result.result == expected_version_output(host_name)
        assert host_name in host_result.result
        assert all(
            other_name not in host_result.result for other_name in healthy_host_names - {host_name}
        )


def test_authentication_and_timeout_fail_only_the_affected_hosts(functional_nornir):
    assert functional_nornir.runner.num_workers > 1
    assert not functional_nornir.data.failed_hosts
    healthy_host_names = set(functional_nornir.filter(role="healthy").inventory.hosts)
    assert len(healthy_host_names) > 1

    start = monotonic()
    result = functional_nornir.run(task=send_command, command=SHOW_VERSION_COMMAND)
    elapsed = monotonic() - start

    assert set(result) == set(functional_nornir.inventory.hosts)
    assert set(result.failed_hosts) == {AUTH_FAILURE_HOST, TIMEOUT_FAILURE_HOST}
    assert type(result[AUTH_FAILURE_HOST].exception) is ScrapliAuthenticationFailed
    assert type(result[TIMEOUT_FAILURE_HOST].exception) is ScrapliTimeout
    for host_name in healthy_host_names:
        assert not result[host_name].failed
        assert result[host_name][0].result == expected_version_output(host_name)
    assert elapsed < 30


def test_records_next_task_behavior_after_host_failure(functional_nornir):
    """Record, rather than prescribe, behavior after failures.

    https://github.com/scrapli/nornir_scrapli/issues/143
    """
    assert functional_nornir.runner.num_workers > 1
    assert not functional_nornir.data.failed_hosts
    healthy_host_names = set(functional_nornir.filter(role="healthy").inventory.hosts)
    assert len(healthy_host_names) > 1
    failed_host_names = {AUTH_FAILURE_HOST, TIMEOUT_FAILURE_HOST}

    first_result = functional_nornir.run(task=send_command, command=SHOW_VERSION_COMMAND)

    assert set(first_result) == set(functional_nornir.inventory.hosts)
    assert set(first_result.failed_hosts) == failed_host_names
    assert functional_nornir.data.failed_hosts == failed_host_names

    second_result = functional_nornir.run(task=send_command, command=SECOND_COMMAND)

    assert set(second_result) == healthy_host_names
    assert not second_result.failed
    assert not second_result.failed_hosts
    for host_name in healthy_host_names:
        assert not second_result[host_name].failed
        assert second_result[host_name][0].result == expected_clock_output(host_name)
    assert functional_nornir.data.failed_hosts == failed_host_names

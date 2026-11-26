"""Type-checked by the mypy session: the result types that a caller of each task reads.

The functions are never called; only the type checker reads them.
"""

from typing import TYPE_CHECKING, Any, List, Optional

from scrapli.response import Response
from typing_extensions import assert_type

from nornir.core.task import AggregatedResult, MultiResult, Result
from nornir_scrapli import async_tasks, tasks
from nornir_scrapli.result import ScrapliResult

if TYPE_CHECKING:
    from nornir.core import Nornir
    from nornir.core.task import Task


def run_tasks(nr: "Nornir") -> None:
    assert_type(nr.run(task=tasks.get_prompt), AggregatedResult[str])
    assert_type(nr.run(task=tasks.send_command, command="show version"), AggregatedResult[str])
    assert_type(nr.run(task=tasks.send_commands, commands=["show version"]), AggregatedResult[str])
    assert_type(nr.run(task=tasks.send_commands_from_file, file="commands"), AggregatedResult[str])
    assert_type(
        nr.run(task=tasks.send_config, config="hostname r1"), AggregatedResult[Optional[str]]
    )
    assert_type(
        nr.run(task=tasks.send_configs, configs=["hostname r1"]), AggregatedResult[Optional[str]]
    )
    assert_type(
        nr.run(task=tasks.send_configs_from_file, file="config"), AggregatedResult[Optional[str]]
    )
    assert_type(nr.run(task=tasks.send_interactive, interact_events=[]), AggregatedResult[Response])
    assert_type(nr.run(task=tasks.cfg_get_version), AggregatedResult[str])
    assert_type(nr.run(task=tasks.cfg_get_config), AggregatedResult[str])
    assert_type(nr.run(task=tasks.cfg_load_config, config="hostname r1"), AggregatedResult[str])
    assert_type(nr.run(task=tasks.cfg_diff_config), AggregatedResult[str])
    assert_type(nr.run(task=tasks.cfg_commit_config), AggregatedResult[str])
    assert_type(nr.run(task=tasks.cfg_abort_config), AggregatedResult[str])
    assert_type(nr.run(task=tasks.netconf_capabilities), AggregatedResult[List[str]])
    assert_type(nr.run(task=tasks.netconf_get, filter_="<a/>"), AggregatedResult[str])
    assert_type(nr.run(task=tasks.netconf_get_config), AggregatedResult[str])
    assert_type(nr.run(task=tasks.netconf_edit_config, config="<a/>"), AggregatedResult[str])
    assert_type(nr.run(task=tasks.netconf_delete_config), AggregatedResult[str])
    assert_type(nr.run(task=tasks.netconf_commit), AggregatedResult[str])
    assert_type(nr.run(task=tasks.netconf_discard), AggregatedResult[str])
    assert_type(nr.run(task=tasks.netconf_lock), AggregatedResult[str])
    assert_type(nr.run(task=tasks.netconf_unlock), AggregatedResult[str])
    assert_type(nr.run(task=tasks.netconf_rpc, filter_="<a/>"), AggregatedResult[str])
    assert_type(nr.run(task=tasks.netconf_validate, source="candidate"), AggregatedResult[str])


def read_results(nr: "Nornir") -> None:
    results = nr.run(task=tasks.send_command, command="show version")
    for multi in results.values():
        assert_type(multi, MultiResult[str])
        assert_type(multi.result, str)


async def arun_tasks(nr: "Nornir") -> None:
    assert_type(await nr.arun(task=async_tasks.get_prompt), AggregatedResult[str])
    assert_type(
        await nr.arun(task=async_tasks.send_command, command="show version"),
        AggregatedResult[str],
    )
    assert_type(
        await nr.arun(task=async_tasks.send_commands, commands=["show version"]),
        AggregatedResult[str],
    )
    assert_type(
        await nr.arun(task=async_tasks.send_commands_from_file, file="commands"),
        AggregatedResult[str],
    )
    assert_type(
        await nr.arun(task=async_tasks.send_config, config="hostname r1"),
        AggregatedResult[Optional[str]],
    )
    assert_type(
        await nr.arun(task=async_tasks.send_configs, configs=["hostname r1"]),
        AggregatedResult[Optional[str]],
    )
    assert_type(
        await nr.arun(task=async_tasks.send_configs_from_file, file="config"),
        AggregatedResult[Optional[str]],
    )
    assert_type(
        await nr.arun(task=async_tasks.send_interactive, interact_events=[]),
        AggregatedResult[Response],
    )
    assert_type(await nr.arun(task=async_tasks.cfg_get_version), AggregatedResult[str])
    assert_type(await nr.arun(task=async_tasks.cfg_get_config), AggregatedResult[str])
    assert_type(
        await nr.arun(task=async_tasks.cfg_load_config, config="hostname r1"),
        AggregatedResult[str],
    )
    assert_type(await nr.arun(task=async_tasks.cfg_diff_config), AggregatedResult[str])
    assert_type(await nr.arun(task=async_tasks.cfg_commit_config), AggregatedResult[str])
    assert_type(await nr.arun(task=async_tasks.cfg_abort_config), AggregatedResult[str])


def call_task(task: "Task") -> None:
    """A task that calls another task directly reads the scrapli response from its result."""
    result = tasks.send_command(task, command="show version")
    assert_type(result, ScrapliResult[str])
    assert_type(result.result, str)
    assert_type(task.run(task=tasks.send_command, command="show version"), MultiResult[str])


def bare_scrapli_result(result: ScrapliResult) -> None:
    """A `ScrapliResult` annotation without a type keeps passing strict checks."""
    assert_type(result, ScrapliResult[Any])
    nornir_result: Result = result
    assert_type(nornir_result.result, Any)

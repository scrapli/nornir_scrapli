"""Type-checked by ``nox -s mypy``: the types the caller of a nornir_scrapli task sees.

The functions are never called; only the type checker reads them.
"""

from typing import Any, List, Optional

from typing_extensions import assert_type

from nornir.core import Nornir
from nornir.core.task import AggregatedResult, MultiResult, Result, Task
from nornir_scrapli import async_tasks, tasks


def cli_tasks_return_text(nr: Nornir) -> None:
    result = nr.run(task=tasks.send_command, command="show version")
    assert_type(result, AggregatedResult[str])
    assert_type(result["sea-ios-1"], MultiResult[str])
    assert_type(result["sea-ios-1"].result, str)
    # The entries are the results of the task and its subtasks, which return other types.
    assert_type(result["sea-ios-1"][0], Result[Any])
    assert_type(nr.run(task=tasks.send_commands, commands=["show version"]), AggregatedResult[str])
    assert_type(nr.run(task=tasks.get_prompt), AggregatedResult[str])
    assert_type(nr.run(task=tasks.send_interactive, interact_events=[]), AggregatedResult[str])


def config_tasks_return_no_text_in_a_dry_run(nr: Nornir) -> None:
    assert_type(
        nr.run(task=tasks.send_config, config="hostname r1"), AggregatedResult[Optional[str]]
    )
    assert_type(
        nr.run(task=tasks.send_configs, configs=["hostname r1"]),
        AggregatedResult[Optional[str]],
    )
    assert_type(
        nr.run(task=tasks.send_configs_from_file, file="config.txt"),
        AggregatedResult[Optional[str]],
    )


def netconf_tasks_return_xml_or_capabilities(nr: Nornir) -> None:
    assert_type(nr.run(task=tasks.netconf_get_config), AggregatedResult[str])
    assert_type(nr.run(task=tasks.netconf_edit_config, config="<config/>"), AggregatedResult[str])
    assert_type(nr.run(task=tasks.netconf_capabilities), AggregatedResult[List[str]])


def subtasks_are_typed(task: Task) -> None:
    assert_type(task.run(task=tasks.send_command, command="show version"), MultiResult[str])
    assert_type(task.run(task=tasks.netconf_capabilities).result, List[str])


async def async_tasks_are_typed(nr: Nornir, task: Task) -> None:
    assert_type(
        await nr.arun(task=async_tasks.send_command, command="show version"),
        AggregatedResult[str],
    )
    assert_type(
        await nr.arun(task=async_tasks.send_configs, configs=["hostname r1"]),
        AggregatedResult[Optional[str]],
    )
    assert_type(await nr.arun(task=async_tasks.netconf_get_config), AggregatedResult[str])
    assert_type(await nr.arun(task=async_tasks.netconf_capabilities), AggregatedResult[List[str]])
    assert_type(
        (await task.arun(task=async_tasks.send_command, command="show version")).result, str
    )

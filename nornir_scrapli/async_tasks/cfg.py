"""Native asyncio Scrapli-Cfg task counterparts."""

from typing import Any

from nornir.core.task import Result, Task
from nornir_scrapli.connection import ScrapliConfig
from nornir_scrapli.result import ScrapliResult


async def cfg_get_version(task: Task) -> Result:
    """Get the device version through the shared async configuration wrapper.

    Args:
        task: nornir task object

    Returns:
        The device version, matching the synchronous task's result semantics

    """
    conn = await ScrapliConfig.aget_connection(task)
    version = await conn.get_version()
    return Result(host=task.host, result=version.result, failed=False, changed=False)


async def cfg_get_config(task: Task, source: str = "running") -> Result:
    """Get a configuration source using Scrapli-Cfg.

    Args:
        task: nornir task object
        source: configuration source to read

    Returns:
        Configuration output and the original response

    """
    conn = await ScrapliConfig.aget_connection(task)
    response = await conn.get_config(source=source)
    return ScrapliResult(host=task.host, result=response.result, scrapli_response=response)


async def cfg_load_config(task: Task, config: str, replace: bool = False, **kwargs: Any) -> Result:
    """Load a candidate configuration without reporting it as committed.

    Args:
        task: nornir task object
        config: candidate configuration
        replace: replace rather than merge the configuration
        kwargs: additional platform-specific arguments

    Returns:
        Load output with changed=False and the original response

    """
    conn = await ScrapliConfig.aget_connection(task)
    response = await conn.load_config(config=config, replace=replace, **kwargs)
    return ScrapliResult(host=task.host, result=response.result, scrapli_response=response)


async def cfg_diff_config(task: Task, source: str = "running") -> Result:
    """Diff the candidate against a configuration source.

    Args:
        task: nornir task object
        source: configuration source to compare against

    Returns:
        The device diff, with other diff formats available in scrapli_response

    """
    conn = await ScrapliConfig.aget_connection(task)
    response = await conn.diff_config(source=source)
    return ScrapliResult(host=task.host, result=response.device_diff, scrapli_response=response)


async def cfg_commit_config(task: Task, source: str = "running") -> Result:
    """Commit the candidate configuration.

    Args:
        task: nornir task object
        source: configuration source to commit against

    Returns:
        Commit output with changed=True and the original response

    """
    conn = await ScrapliConfig.aget_connection(task)
    response = await conn.commit_config(source=source)
    return ScrapliResult(
        host=task.host, result=response.result, scrapli_response=response, changed=True
    )


async def cfg_abort_config(task: Task) -> Result:
    """Abort the candidate configuration.

    Args:
        task: nornir task object

    Returns:
        Abort output with changed=False and the original response

    """
    conn = await ScrapliConfig.aget_connection(task)
    response = await conn.abort_config()
    return ScrapliResult(host=task.host, result=response.result, scrapli_response=response)

"""Commit NETCONF candidate configuration."""

from typing import Optional

from scrapli.ffi_types import Cancel

from nornir.core.task import Task
from nornir_scrapli.result import ScrapliResult


async def netconf_commit(
    task: Task, *, operation_timeout_ns: Optional[int] = None, cancel: Optional[Cancel] = None
) -> ScrapliResult:
    """Commit the candidate datastore.

    Args:
        task: Nornir task.
        operation_timeout_ns: Operation timeout in nanoseconds.
        cancel: Native cancellation context.

    Returns:
        Nornir result containing reply XML.
    """
    connection = await task.host.aget_connection("scrapli_netconf", task.nornir.config)
    response = await connection.commit_async(
        operation_timeout_ns=operation_timeout_ns, cancel=cancel
    )
    return ScrapliResult(task.host, response.result, response, changed=True)

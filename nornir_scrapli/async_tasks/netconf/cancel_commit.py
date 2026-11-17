"""Cancel a NETCONF confirmed commit."""

from typing import Optional

from scrapli.ffi_types import Cancel

from nornir.core.task import Result, Task
from nornir_scrapli.result import ScrapliResult


async def netconf_cancel_commit(
    task: Task,
    *,
    persist_id: Optional[str] = None,
    operation_timeout_ns: Optional[int] = None,
    cancel: Optional[Cancel] = None,
) -> Result:
    """Cancel a pending confirmed commit.

    Args:
        task: Nornir task.
        persist_id: Persistent confirmed-commit identifier.
        operation_timeout_ns: Operation timeout in nanoseconds.
        cancel: Native cancellation context.

    Returns:
        Nornir result containing reply XML.
    """
    connection = await task.host.aget_connection("scrapli_netconf", task.nornir.config)
    response = await connection.cancel_commit_async(
        persist_id=persist_id, operation_timeout_ns=operation_timeout_ns, cancel=cancel
    )
    return ScrapliResult(task.host, response.result, response, changed=True)

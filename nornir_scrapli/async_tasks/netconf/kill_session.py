"""Terminate a NETCONF session."""

from typing import Optional

from scrapli.ffi_types import Cancel

from nornir.core.task import Task
from nornir_scrapli.result import ScrapliResult


async def netconf_kill_session(
    task: Task,
    session_id: int,
    *,
    operation_timeout_ns: Optional[int] = None,
    cancel: Optional[Cancel] = None,
) -> ScrapliResult:
    """Terminate the identified NETCONF session.

    Args:
        task: Nornir task.
        session_id: Session identifier to terminate.
        operation_timeout_ns: Operation timeout in nanoseconds.
        cancel: Native cancellation context.

    Returns:
        Nornir result containing reply XML.
    """
    connection = await task.host.aget_connection("scrapli_netconf", task.nornir.config)
    response = await connection.kill_session_async(
        session_id=session_id, operation_timeout_ns=operation_timeout_ns, cancel=cancel
    )
    return ScrapliResult(task.host, response.result, response, changed=True)

"""Discard NETCONF candidate changes."""

from typing import Optional

from scrapli.ffi_types import Cancel

from nornir.core.task import Result, Task
from nornir_scrapli.result import ScrapliResult


def netconf_discard(
    task: Task, *, operation_timeout_ns: Optional[int] = None, cancel: Optional[Cancel] = None
) -> Result:
    """Discard uncommitted candidate changes.

    Args:
        task: Nornir task.
        operation_timeout_ns: Operation timeout in nanoseconds.
        cancel: Native cancellation context.

    Returns:
        Nornir result containing reply XML.
    """
    connection = task.host.get_connection("scrapli_netconf", task.nornir.config)
    response = connection.discard(operation_timeout_ns=operation_timeout_ns, cancel=cancel)
    return ScrapliResult(task.host, response.result, response, changed=True)

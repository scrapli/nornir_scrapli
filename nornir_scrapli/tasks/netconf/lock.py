"""Lock a NETCONF datastore."""

from typing import Optional

from scrapli.ffi_types import Cancel
from scrapli.netconf import DatastoreType

from nornir.core.task import Result, Task
from nornir_scrapli.result import ScrapliResult


def netconf_lock(
    task: Task,
    *,
    target: DatastoreType = DatastoreType.RUNNING,
    operation_timeout_ns: Optional[int] = None,
    cancel: Optional[Cancel] = None,
) -> Result:
    """Lock the requested datastore.

    Args:
        task: Nornir task.
        target: Target datastore.
        operation_timeout_ns: Operation timeout in nanoseconds.
        cancel: Native cancellation context.

    Returns:
        Nornir result containing reply XML.
    """
    connection = task.host.get_connection("scrapli_netconf", task.nornir.config)
    response = connection.lock(
        target=target, operation_timeout_ns=operation_timeout_ns, cancel=cancel
    )
    return ScrapliResult(task.host, response.result, response, changed=True)

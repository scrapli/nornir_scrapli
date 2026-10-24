"""Edit NMDA NETCONF datastore data."""

from typing import Optional

from scrapli.ffi_types import Cancel
from scrapli.netconf import DatastoreType, DefaultOperation

from nornir.core.task import Result, Task
from nornir_scrapli.result import ScrapliResult


def netconf_edit_data(
    task: Task,
    content: str,
    *,
    target: DatastoreType = DatastoreType.RUNNING,
    default_operation: DefaultOperation = DefaultOperation.UNSET,
    operation_timeout_ns: Optional[int] = None,
    cancel: Optional[Cancel] = None,
) -> Result:
    """Edit NMDA data in the target datastore.

    Args:
        task: Nornir task.
        content: Data content XML.
        target: Target datastore.
        default_operation: Default edit operation.
        operation_timeout_ns: Operation timeout in nanoseconds.
        cancel: Native cancellation context.

    Returns:
        Nornir result containing reply XML.
    """
    connection = task.host.get_connection("scrapli_netconf", task.nornir.config)
    response = connection.edit_data(
        content=content,
        target=target,
        default_operation=default_operation,
        operation_timeout_ns=operation_timeout_ns,
        cancel=cancel,
    )
    return ScrapliResult(task.host, response.result, response, changed=True)

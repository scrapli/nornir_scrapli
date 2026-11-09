"""Copy NETCONF datastore configuration."""

from typing import Optional, Union

from scrapli.ffi_types import Cancel
from scrapli.netconf import DatastoreType

from nornir.core.task import Result, Task
from nornir_scrapli.helper import to_datastore
from nornir_scrapli.result import ScrapliResult


def netconf_copy_config(
    task: Task,
    *,
    target: Union[DatastoreType, str] = DatastoreType.RUNNING,
    source: Union[DatastoreType, str] = DatastoreType.STARTUP,
    operation_timeout_ns: Optional[int] = None,
    cancel: Optional[Cancel] = None,
) -> Result:
    """Copy the source datastore into the target.

    Args:
        task: Nornir task.
        target: Target datastore.
        source: Source datastore.
        operation_timeout_ns: Operation timeout in nanoseconds.
        cancel: Native cancellation context.

    Returns:
        Nornir result containing reply XML.
    """
    connection = task.host.get_connection("scrapli_netconf", task.nornir.config)
    response = connection.copy_config(
        target=to_datastore(target),
        source=to_datastore(source),
        operation_timeout_ns=operation_timeout_ns,
        cancel=cancel,
    )
    return ScrapliResult(task.host, response.result, response, changed=True)

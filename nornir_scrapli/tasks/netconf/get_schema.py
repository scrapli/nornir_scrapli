"""Read a NETCONF schema."""

from typing import Optional

from scrapli.ffi_types import Cancel
from scrapli.netconf import SchemaFormat

from nornir.core.task import Result, Task
from nornir_scrapli.result import ScrapliResult


def netconf_get_schema(
    task: Task,
    identifier: str,
    *,
    version: str = "",
    format_: SchemaFormat = SchemaFormat.YANG,
    operation_timeout_ns: Optional[int] = None,
    cancel: Optional[Cancel] = None,
) -> Result:
    """Read a schema by identifier and version.

    Args:
        task: Nornir task.
        identifier: Schema identifier.
        version: Schema version.
        format_: Requested schema format.
        operation_timeout_ns: Operation timeout in nanoseconds.
        cancel: Native cancellation context.

    Returns:
        Nornir result containing reply XML.
    """
    connection = task.host.get_connection("scrapli_netconf", task.nornir.config)
    response = connection.get_schema(
        identifier=identifier,
        version=version,
        format_=format_,
        operation_timeout_ns=operation_timeout_ns,
        cancel=cancel,
    )
    return ScrapliResult(task.host, response.result, response)

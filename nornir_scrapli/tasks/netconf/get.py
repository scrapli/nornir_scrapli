"""Read NETCONF data."""

from typing import Optional

from scrapli.ffi_types import Cancel
from scrapli.netconf import DefaultsType, FilterType

from nornir.core.task import Result, Task
from nornir_scrapli.result import ScrapliResult


def netconf_get(
    task: Task,
    *,
    filter_: str = "",
    filter_type: FilterType = FilterType.SUBTREE,
    filter_namespace_prefix: str = "",
    filter_namespace: str = "",
    defaults_type: DefaultsType = DefaultsType.UNSET,
    operation_timeout_ns: Optional[int] = None,
    cancel: Optional[Cancel] = None,
) -> Result:
    """Read data with native NETCONF filtering options.

    Args:
        task: Nornir task.
        filter_: Filter payload.
        filter_type: Native filter type.
        filter_namespace_prefix: Filter namespace prefix.
        filter_namespace: Filter namespace URI.
        defaults_type: Defaults reporting mode.
        operation_timeout_ns: Operation timeout in nanoseconds.
        cancel: Native cancellation context.

    Returns:
        Nornir result containing reply XML.
    """
    connection = task.host.get_connection("scrapli_netconf", task.nornir.config)
    response = connection.get(
        filter_=filter_,
        filter_type=filter_type,
        filter_namespace_prefix=filter_namespace_prefix,
        filter_namespace=filter_namespace,
        defaults_type=defaults_type,
        operation_timeout_ns=operation_timeout_ns,
        cancel=cancel,
    )
    return ScrapliResult(task.host, response.result, response)

"""Send a raw NETCONF RPC."""

from typing import List, Optional, Tuple

from scrapli.ffi_types import Cancel

from nornir.core.task import Result, Task
from nornir_scrapli.result import ScrapliResult


def netconf_rpc(
    task: Task,
    payload: str,
    *,
    base_namespace_prefix: str = "",
    extra_namespaces: Optional[List[Tuple[str, str]]] = None,
    operation_timeout_ns: Optional[int] = None,
    cancel: Optional[Cancel] = None,
) -> Result:
    """Send raw XML through the native raw_rpc operation.

    Args:
        task: Nornir task.
        payload: RPC payload XML.
        base_namespace_prefix: Base namespace prefix.
        extra_namespaces: Extra namespace prefix/URI pairs.
        operation_timeout_ns: Operation timeout in nanoseconds.
        cancel: Native cancellation context.

    Returns:
        Nornir result containing reply XML.
    """
    connection = task.host.get_connection("scrapli_netconf", task.nornir.config)
    response = connection.raw_rpc(
        payload=payload,
        base_namespace_prefix=base_namespace_prefix,
        extra_namespaces=extra_namespaces,
        operation_timeout_ns=operation_timeout_ns,
        cancel=cancel,
    )
    return ScrapliResult(task.host, response.result, response, changed=True)

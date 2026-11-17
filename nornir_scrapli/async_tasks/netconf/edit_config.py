"""Edit NETCONF configuration on an asyncio connection with optional diff and discard."""

from typing import Any, Dict, Optional, Union

from scrapli import Netconf
from scrapli.exceptions import OperationException
from scrapli.ffi_types import Cancel
from scrapli.netconf import DatastoreType, DefaultOperation, ErrorOption, TestOption

from nornir.core.task import Result, Task
from nornir_scrapli.helper import diff_xml_text, to_datastore
from nornir_scrapli.tasks.netconf.edit_config import _finish_edit


async def _discard_error(connection: Netconf, options: Dict[str, Any]) -> Optional[Exception]:
    try:
        if (await connection.discard_async(**options)).failed:
            return OperationException("Failed to discard candidate changes")
    except Exception as exc:
        return exc
    return None


async def netconf_edit_config(
    task: Task,
    config: str = "",
    dry_run: Optional[bool] = None,
    diff: bool = False,
    *,
    target: Union[DatastoreType, str] = DatastoreType.RUNNING,
    default_operation: DefaultOperation = DefaultOperation.UNSET,
    test_option: TestOption = TestOption.UNSET,
    error_option: ErrorOption = ErrorOption.UNSET,
    operation_timeout_ns: Optional[int] = None,
    cancel: Optional[Cancel] = None,
) -> Result:
    """Edit configuration and optionally diff/discard candidate changes.

    A dry run requires the candidate datastore as the target. It sends edit_config, then
    discards candidate changes, including candidate changes that existed before the task.
    A dry run with any other target fails before sending anything, because changes to the
    running or startup datastore take effect at once and cannot be discarded.

    Args:
        task: Nornir task.
        config: Configuration XML.
        dry_run: Override global dry run. Requires the candidate target.
        diff: Capture a datastore diff before discarding.
        target: Target datastore.
        default_operation: Default edit operation.
        test_option: Native testing option.
        error_option: Native error handling option.
        operation_timeout_ns: Operation timeout in nanoseconds.
        cancel: Native cancellation context.

    Returns:
        Nornir result containing edit reply XML and optional diff.

    Raises:
        ValueError: If a dry run targets a datastore other than candidate.
        OperationException: If a diff read or discard reports failure.
    """
    target = to_datastore(target)
    dry = task.global_dry_run if dry_run is None else dry_run
    if dry and target is not DatastoreType.CANDIDATE:
        raise ValueError(
            f"NETCONF edit_config dry run requires the candidate datastore, not {target.value!r}: "
            "changes to other datastores take effect at once and cannot be discarded"
        )
    connection = await task.host.aget_connection("scrapli_netconf", task.nornir.config)
    options = {"operation_timeout_ns": operation_timeout_ns, "cancel": cancel}
    original = await connection.get_config_async(source=target, **options) if diff else None
    if original is not None and original.failed:
        raise OperationException("Failed to read configuration before edit")
    diff_result = ""
    response = None
    error = None
    try:
        response = await connection.edit_config_async(
            config=config,
            target=target,
            default_operation=default_operation,
            test_option=test_option,
            error_option=error_option,
            **options,
        )
        if original is not None and not response.failed:
            edited = await connection.get_config_async(source=target, **options)
            if edited.failed:
                raise OperationException("Failed to read configuration after edit")
            diff_result = diff_xml_text(original.result, edited.result)
    except Exception as exc:
        error = exc
    finally:
        cleanup_error = await _discard_error(connection, options) if dry else None
    return _finish_edit(task, response, error, cleanup_error, dry, diff_result)

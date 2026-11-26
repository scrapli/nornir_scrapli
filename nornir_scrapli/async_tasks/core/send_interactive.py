"""Run ordered CLI interactions on an asyncio connection using one native read callback."""

from typing import List, Optional

from scrapli import Cli
from scrapli.exceptions import OperationException
from scrapli.ffi_types import Cancel

from nornir.core.task import Task
from nornir_scrapli.result import ScrapliResult
from nornir_scrapli.tasks.core.mode import load_definition
from nornir_scrapli.tasks.core.send_interactive import Event, Interaction


async def send_interactive(
    task: Task,
    interact_events: List[Event],
    *,
    requested_mode: str = "",
    operation_timeout_ns: Optional[int] = None,
    cancel: Optional[Cancel] = None,
) -> ScrapliResult:
    """Send each event only after the preceding input's expected prompt arrives.

    Args:
        task: Nornir task.
        interact_events: Input/expected-prompt tuples with optional hidden-input flag.
        requested_mode: Mode in which to begin, or the current mode when empty.
        operation_timeout_ns: Total native callback operation timeout in nanoseconds.
        cancel: Native cancellation context.

    Returns:
        Nornir result containing output and the native callback result.

    Raises:
        OperationException: If entering the requested mode fails.
    """
    interaction = Interaction(interact_events)
    connection = await task.host.aget_connection("scrapli", task.nornir.config)
    if requested_mode:
        entered = await connection.enter_mode_async(
            requested_mode=requested_mode,
            operation_timeout_ns=operation_timeout_ns,
            cancel=cancel,
        )
        if entered.failed:
            raise OperationException("Failed to enter interactive starting mode")
    definition = load_definition(connection)

    async def advance(cli: Cli, recent: str, accumulated: str) -> None:
        _ = recent
        next_input = interaction.advance(accumulated)
        if interaction.complete:
            callback.completes = True
        elif next_input is not None:
            # Scrapli v2 has no async write; the write only queues bytes for the driver.
            cli.write_and_return(input_=next_input)

    callback = interaction.read_callback(callback_async=advance)
    connection.write_and_return(input_=interaction.first_input)
    native = await connection.read_with_callbacks_async(
        callbacks=[callback],
        operation_timeout_ns=operation_timeout_ns,
        cancel=cancel,
    )
    return interaction.result(task, definition, native)

"""Run ordered CLI interactions using a single native read callback."""

from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Union

import regex
from scrapli import Cli, ReadCallback
from scrapli.cli_result import Result as CliResult
from scrapli.exceptions import OperationException
from scrapli.ffi_types import Cancel

from nornir.core.task import Result, Task
from nornir_scrapli.result import ScrapliResult
from nornir_scrapli.tasks.core.mode import load_definition

Event = Union[Tuple[str, str], Tuple[str, str, bool]]
HIDDEN_EVENT_LENGTH = 3


def _validate_events(events: List[Event]) -> None:
    if not events:
        raise ValueError("interact_events must contain at least one event")
    for event in events:
        if (
            not isinstance(event, (list, tuple))
            or len(event) not in (2, 3)
            or not isinstance(event[0], str)
            or not isinstance(event[1], str)
            or not event[1]
            or (len(event) == HIDDEN_EVENT_LENGTH and not isinstance(event[-1], bool))
        ):
            raise ValueError(
                "Each interaction requires input, expected prompt and optional hidden bool"
            )


def _prompt_end(prompt: str, output: str) -> Optional[int]:
    literal = output.find(prompt)
    if literal >= 0:
        return literal + len(prompt)
    try:
        match = regex.search(prompt, output, regex.MULTILINE)
    except regex.error:
        # Literal prompts may contain unbalanced brackets.
        return None
    return match.end() if match and match.end() > match.start() else None


class Interaction:
    """Track which interaction event the device has acknowledged.

    The tracker holds no I/O, so the sync and asyncio tasks share it and differ only in
    how they write the next input.
    """

    def __init__(self, events: List[Event]) -> None:
        """Validate the events and start at the first one.

        Args:
            events: Input/expected-prompt tuples with optional hidden-input flag.
        """
        _validate_events(events)
        self.events = events
        self.index = 0
        self.consumed = 0

    @property
    def first_input(self) -> str:
        """Input written before reading starts."""
        return self.events[0][0]

    @property
    def complete(self) -> bool:
        """Whether the final expected prompt has arrived."""
        return self.index == len(self.events)

    def advance(self, accumulated: str) -> Optional[str]:
        """Consume output and return the next input once its preceding prompt arrives.

        Args:
            accumulated: All output read so far.

        Returns:
            The next input to write, or None when nothing is to be written.
        """
        if self.complete:
            return None
        end = _prompt_end(self.events[self.index][1], accumulated[self.consumed :])
        if end is None:
            return None
        # Output already buffered before the next write cannot acknowledge that input.
        self.consumed = len(accumulated)
        self.index += 1
        if self.complete:
            return None
        return self.events[self.index][0]

    def read_callback(
        self,
        callback: Optional[Callable[[Cli, str, str], None]] = None,
        callback_async: Optional[Callable[[Cli, str, str], Awaitable[None]]] = None,
    ) -> ReadCallback:
        """Build the read callback that runs on every chunk of output.

        Native callback matching advances its own cursor on each match. The tracker keeps
        a separate acknowledgement cursor so fragments and repeated prompt text remain
        ordered.

        Args:
            callback: Sync callback function.
            callback_async: Asyncio callback function.

        Returns:
            Native read callback.
        """
        return ReadCallback(
            name="nornir-interactive",
            contains_pattern=r"[\s\S]+",
            search_depth=1,
            callback=callback,
            callback_async=callback_async,
        )

    def result(self, task: Task, definition: Dict[str, Any], native: CliResult) -> Result:
        """Check completion, hide secrets and build the Nornir result.

        Args:
            task: Nornir task.
            definition: Loaded CLI definition.
            native: Native read_with_callbacks result.

        Returns:
            Nornir result containing output and the native callback result.

        Raises:
            OperationException: If reading ended before the final expected prompt.
        """
        if not self.complete:
            raise OperationException("Interactive operation ended before the final expected prompt")
        events = self.events
        indicator = next(
            (text for text in definition.get("failure_indicators", []) if text in native.result),
            "",
        )
        native.results_failed_indicator = native.results_failed_indicator or indicator
        hidden = [
            event[0]
            for event in events
            if len(event) == HIDDEN_EVENT_LENGTH and event[-1] and event[0]
        ]
        output = native.result
        for secret in hidden:
            output = output.replace(secret, "[redacted]")
        # Raw journals may split a secret with control sequences. For hidden exchanges,
        # expose only sanitized, normalized text bytes rather than wire-exact output.
        raw = output.encode() if hidden else native.result_raw
        native.inputs = [
            "\n".join(
                "[redacted]" if len(e) == HIDDEN_EVENT_LENGTH and e[-1] else e[0] for e in events
            )
        ]
        native.results = [output]
        native._result_raw_journals = [b""]
        native._results_raw = [raw]
        return ScrapliResult(task.host, output, native, changed=True)


def send_interactive(
    task: Task,
    interact_events: List[Event],
    *,
    requested_mode: str = "",
    operation_timeout_ns: Optional[int] = None,
    cancel: Optional[Cancel] = None,
) -> Result:
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
    connection = task.host.get_connection("scrapli", task.nornir.config)
    if requested_mode:
        entered = connection.enter_mode(
            requested_mode=requested_mode,
            operation_timeout_ns=operation_timeout_ns,
            cancel=cancel,
        )
        if entered.failed:
            raise OperationException("Failed to enter interactive starting mode")
    definition = load_definition(connection)

    def advance(cli: Cli, recent: str, accumulated: str) -> None:
        _ = recent
        next_input = interaction.advance(accumulated)
        if interaction.complete:
            callback.completes = True
        elif next_input is not None:
            cli.write_and_return(input_=next_input)

    callback = interaction.read_callback(callback=advance)
    connection.write_and_return(input_=interaction.first_input)
    native = connection.read_with_callbacks(
        callbacks=[callback],
        operation_timeout_ns=operation_timeout_ns,
        cancel=cancel,
    )
    return interaction.result(task, definition, native)

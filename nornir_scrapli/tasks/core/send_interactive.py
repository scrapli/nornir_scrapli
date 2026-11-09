"""Run ordered CLI interactions using a single native read callback."""

from typing import List, Optional, Tuple, Union

import regex
from scrapli import Cli, ReadCallback
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
    _validate_events(interact_events)
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
    index = 0
    consumed = 0

    def advance(cli: Cli, recent: str, accumulated: str) -> None:
        nonlocal index, consumed
        _ = recent
        if index < len(interact_events):
            end = _prompt_end(interact_events[index][1], accumulated[consumed:])
            if end is None:
                return
            # Output already buffered before the next write cannot acknowledge that input.
            consumed = len(accumulated)
            index += 1
            if index == len(interact_events):
                callback.completes = True
                return
            cli.write_and_return(input_=interact_events[index][0])

    # Native callback matching advances its own cursor on each match. Keep our separate
    # acknowledgement cursor so fragments and repeated prompt text remain ordered.
    callback = ReadCallback(
        name="nornir-interactive",
        contains_pattern=r"[\s\S]+",
        search_depth=1,
        callback=advance,
    )
    connection.write_and_return(input_=interact_events[0][0])
    native = connection.read_with_callbacks(
        callbacks=[callback],
        operation_timeout_ns=operation_timeout_ns,
        cancel=cancel,
    )
    if index != len(interact_events):
        raise OperationException("Interactive operation ended before the final expected prompt")
    indicator = next(
        (text for text in definition.get("failure_indicators", []) if text in native.result), ""
    )
    native.results_failed_indicator = native.results_failed_indicator or indicator
    hidden = [
        event[0]
        for event in interact_events
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
            "[redacted]" if len(e) == HIDDEN_EVENT_LENGTH and e[-1] else e[0]
            for e in interact_events
        )
    ]
    native.results = [output]
    native._result_raw_journals = [b""]
    native._results_raw = [raw]
    return ScrapliResult(task.host, output, native, changed=True)

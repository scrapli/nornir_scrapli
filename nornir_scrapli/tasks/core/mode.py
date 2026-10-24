"""Resolve modes from the loaded definition and preserve dry-run starting mode."""

from typing import Any, Dict, Optional

import regex
import yaml
from scrapli import Cli
from scrapli.exceptions import OperationException
from scrapli.ffi_types import Cancel


def load_definition(connection: Cli) -> Dict[str, Any]:
    """Read the definition already loaded by the native connection.

    Args:
        connection: Native CLI connection.

    Returns:
        Definition data.

    Raises:
        OperationException: If the loaded definition is not a mapping.
    """
    definition = yaml.safe_load(connection.definition_string)
    if not isinstance(definition, dict):
        raise OperationException("Loaded CLI definition is not a mapping")
    return definition


def get_current_mode(
    connection: Cli,
    operation_timeout_ns: Optional[int] = None,
    cancel: Optional[Cancel] = None,
) -> str:
    """Identify the current prompt's unique mode before any mode changes.

    Args:
        connection: Native CLI connection.
        operation_timeout_ns: Prompt operation timeout in nanoseconds.
        cancel: Native cancellation context.

    Returns:
        The uniquely matching mode name.

    Raises:
        OperationException: If prompt retrieval fails or mode matching is ambiguous.
    """
    response = connection.get_prompt(operation_timeout_ns=operation_timeout_ns, cancel=cancel)
    if response.failed:
        raise OperationException("Failed to read starting prompt")
    prompt = response.result
    matches = []
    for mode in load_definition(connection).get("modes", []):
        try:
            matched = regex.search(mode["prompt_pattern"], prompt, regex.MULTILINE)
        except regex.error as exc:
            raise OperationException("Unsupported mode prompt pattern") from exc
        if matched and not any(text in prompt for text in mode.get("prompt_excludes", [])):
            matches.append(mode["name"])
    if len(matches) != 1:
        raise OperationException(
            "Cannot unambiguously determine starting mode from loaded definition"
        )
    return str(matches[0])


def check_config_mode(
    connection: Cli,
    requested_mode: str,
    operation_timeout_ns: Optional[int],
    cancel: Optional[Cancel],
) -> None:
    """Enter a requested mode and restore the actual starting mode without sending config.

    Args:
        connection: Native CLI connection.
        requested_mode: Configuration mode to test.
        operation_timeout_ns: Mode operation timeout in nanoseconds.
        cancel: Native cancellation context.

    Raises:
        OperationException: If a mode operation reports failure.
    """
    starting = get_current_mode(connection, operation_timeout_ns, cancel)
    original: Optional[Exception] = None
    try:
        entered = connection.enter_mode(
            requested_mode=requested_mode,
            operation_timeout_ns=operation_timeout_ns,
            cancel=cancel,
        )
        if entered.failed:
            raise OperationException("Failed to enter requested configuration mode")
    except Exception as exc:
        original = exc
        raise
    finally:
        try:
            restored = connection.enter_mode(
                requested_mode=starting,
                operation_timeout_ns=operation_timeout_ns,
                cancel=cancel,
            )
            if restored.failed:
                raise OperationException("Failed to restore starting mode")
        except Exception as exc:
            if original is not None:
                raise original from exc
            raise

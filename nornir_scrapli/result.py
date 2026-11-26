"""Adapt native scrapli v2 results to Nornir."""

from typing import TYPE_CHECKING, Any, Generic, Optional, Union

from scrapli.cli_result import Result as CliResult
from scrapli.netconf_result import Result as NetconfResult

from nornir.core.inventory import Host
from nornir.core.task import Result

if TYPE_CHECKING:
    # The default lets a bare ``ScrapliResult`` mean ``ScrapliResult[str]`` for the type
    # checker. It is declared only here, so ``typing_extensions`` is not needed at runtime.
    from typing_extensions import TypeVar

    T = TypeVar("T", default=str)
else:
    from typing import TypeVar

    T = TypeVar("T")


def process_command_result(scrapli_response: Union[CliResult, NetconfResult]) -> str:
    """Format command outputs with the plugin's blank-line separator.

    Args:
        scrapli_response: Native CLI or NETCONF result.

    Returns:
        Command output text or NETCONF XML.
    """
    if isinstance(scrapli_response, CliResult):
        return "\n\n".join(scrapli_response.results)
    return scrapli_response.result


def process_config_result(scrapli_response: CliResult) -> str:
    """Include each configuration input before its complete output.

    Args:
        scrapli_response: Native result with one input per configuration line.

    Returns:
        Configuration inputs and outputs in the legacy string format.
    """
    return "".join(
        f"{input_}\n{output}"
        for input_, output in zip(scrapli_response.inputs, scrapli_response.results)
    )


class ScrapliResult(Result[T], Generic[T]):
    """Nornir result that retains the native scrapli result.

    ``ScrapliResult[T]`` types ``result`` as ``T`` for the type checker; a bare
    ``ScrapliResult`` means ``ScrapliResult[str]``. The type parameter has no effect at
    runtime.
    """

    def __init__(
        self,
        host: Host,
        result: T,
        scrapli_response: Optional[Union[CliResult, NetconfResult]] = None,
        changed: bool = False,
        **kwargs: Any,
    ) -> None:
        """Create a Nornir result retaining the native result object.

        Args:
            host: Nornir host.
            result: Formatted output text.
            scrapli_response: Original native result.
            changed: Whether this task changes device state.
            kwargs: Additional Nornir result metadata.
        """
        super().__init__(
            host=host,
            result=result,
            failed=scrapli_response.failed if scrapli_response is not None else False,
            changed=changed,
            **kwargs,
        )
        self.scrapli_response = scrapli_response

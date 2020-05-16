"""nornir_scrapli.result"""
from typing import TYPE_CHECKING, Any, List, Optional, Union

from nornir.core.task import Result
from scrapli.response import MultiResponse, Response

if TYPE_CHECKING:
    from nornir.core.inventory import Host  # pylint: disable=C0412


def process_command_result(scrapli_response: Union[Response, MultiResponse]) -> str:
    """
    Process and return string of scrapli response(s)

    Args:
        scrapli_response: scrapli Response or MultiResponse object

    Returns:
        str: string result from nornir task or None

    Raises:
        N/A

    """
    if isinstance(scrapli_response, Response):
        return scrapli_response.result
    return "\n\n".join([response.result for response in scrapli_response])


def process_config_result(
    configs: Union[str, List[str]], scrapli_response: Union[Response, MultiResponse]
) -> str:
    """
    Process and return string of scrapli response(s)

    Args:
        configs: string or list of strings that were sent to device
        scrapli_response: scrapli Response or MultiResponse object

    Returns:
        str: string result from nornir task or None

    Raises:
        N/A

    """
    full_results = ""
    for config, response in zip(configs, scrapli_response):
        full_results += "\n".join([config, response.result])
    return full_results


class ScrapliResult(Result):
    def __init__(
        self,
        host: "Host",
        result: Optional[str],
        scrapli_response: Optional[Union[Response, MultiResponse]] = None,
        changed: bool = False,
        **kwargs: Any,
    ):
        """
        Scrapli Nornir Result object

        A "normal" nornir result object with an additional attribute "scrapli_response" which houses
        the original response object returned from scrapli

        Args:
            host: nornir task host object
            result: result text returned from scrapli task
            scrapli_response: original response object returned from scrapli task
            changed: bool indicating if a change has occurred
            kwargs: keyword arguments to pass to nornir Result

        Returns:
            N/A  # noqa DAR201

        Raises:
            N/A

        """
        failed = self._process_failed(scrapli_response=scrapli_response)

        super().__init__(host=host, result=result, failed=failed, changed=changed, **kwargs)

        self.scrapli_response = scrapli_response

    @staticmethod
    def _process_failed(scrapli_response: Optional[Union[Response, MultiResponse]]) -> bool:
        """
        Process and return string of scrapli response(s)

        Args:
            scrapli_response: scrapli Response or MultiResponse object

        Returns:
            bool: bool indicating if the nornir task failed

        Raises:
            N/A

        """
        if scrapli_response is None:
            return False
        if isinstance(scrapli_response, Response):
            return scrapli_response.failed
        if any([response.failed for response in scrapli_response]):
            return True
        return False

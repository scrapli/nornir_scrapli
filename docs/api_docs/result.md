<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module nornir_scrapli.result

nornir_scrapli.result

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""nornir_scrapli.result"""
from typing import TYPE_CHECKING, Any, Optional, Union

from scrapli.response import MultiResponse, Response

from nornir.core.task import Result

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
        result: str = scrapli_response.result
        return result
    return "\n\n".join([response.result for response in scrapli_response])


def process_config_result(scrapli_response: Union[Response, MultiResponse]) -> str:
    """
    Process and return string of scrapli response(s)

    Args:
        scrapli_response: scrapli Response or MultiResponse object

    Returns:
        str: string result from nornir task or None

    Raises:
        N/A

    """
    full_results = ""
    if isinstance(scrapli_response, Response):
        for config_input, config_result in zip(
            scrapli_response.channel_input.split("\n"), scrapli_response.result.split("\n")
        ):
            if config_input == config_result:
                full_results += f"{config_input}\n"
            else:
                full_results += "\n".join([config_input, config_result])
    else:
        for response in scrapli_response:
            full_results += "\n".join([response.channel_input, response.result])
    return full_results


class ScrapliResult(Result):  # type: ignore
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
            N/A  # noqa: DAR202

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
            failed: bool = scrapli_response.failed
            return failed
        if any([response.failed for response in scrapli_response]):
            return True
        return False
        </code>
    </pre>
</details>



## Functions

    

#### process_command_result
`process_command_result(scrapli_response: Union[scrapli.response.Response, scrapli.response.MultiResponse]) ‑> str`

```text
Process and return string of scrapli response(s)

Args:
    scrapli_response: scrapli Response or MultiResponse object

Returns:
    str: string result from nornir task or None

Raises:
    N/A
```




    

#### process_config_result
`process_config_result(scrapli_response: Union[scrapli.response.Response, scrapli.response.MultiResponse]) ‑> str`

```text
Process and return string of scrapli response(s)

Args:
    scrapli_response: scrapli Response or MultiResponse object

Returns:
    str: string result from nornir task or None

Raises:
    N/A
```




## Classes

### ScrapliResult


```text
Result of running individual tasks.

Arguments:
    changed (bool): ``True`` if the task is changing the system
    diff (obj): Diff between state of the system before/after running this task
    result (obj): Result of the task execution, see task's documentation for details
    host (:obj:`nornir.core.inventory.Host`): Reference to the host that lead ot this result
    failed (bool): Whether the execution failed or not
    severity_level (logging.LEVEL): Severity level associated to the result of the excecution
    exception (Exception): uncaught exception thrown during the exection of the task (if any)

Attributes:
    changed (bool): ``True`` if the task is changing the system
    diff (obj): Diff between state of the system before/after running this task
    result (obj): Result of the task execution, see task's documentation for details
    host (:obj:`nornir.core.inventory.Host`): Reference to the host that lead ot this result
    failed (bool): Whether the execution failed or not
    severity_level (logging.LEVEL): Severity level associated to the result of the excecution
    exception (Exception): uncaught exception thrown during the exection of the task (if any)

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
    N/A  # noqa: DAR202

Raises:
    N/A
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class ScrapliResult(Result):  # type: ignore
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
            N/A  # noqa: DAR202

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
            failed: bool = scrapli_response.failed
            return failed
        if any([response.failed for response in scrapli_response]):
            return True
        return False
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- nornir.core.task.Result
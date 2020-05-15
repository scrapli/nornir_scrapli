"""nornir_scrapli.tasks.send_commands"""
from typing import List, Optional, Union

from nornir.core.task import Result, Task


def send_commands_from_file(
    task: Task,
    file: str,
    strip_prompt: bool = True,
    failed_when_contains: Optional[Union[str, List[str]]] = None,
    stop_on_failed: bool = False,
) -> Result:
    """
    Send a list of commands from a file to device using scrapli

    Args:
        task: nornir task object
        file: string path to file
        strip_prompt: True/False strip prompt from returned output
        failed_when_contains: string or list of strings indicating failure if found in response
        stop_on_failed: True/False stop executing commands if a command fails, returns results as of
            current execution

    Returns:
        Result: nornir result object with Result.result value set to returned scrapli Response
            object

    Raises:
        N/A

    """
    scrapli_conn = task.host.get_connection("scrapli", task.nornir.config)
    scrapli_response = scrapli_conn.send_commands_from_file(
        file=file,
        strip_prompt=strip_prompt,
        failed_when_contains=failed_when_contains,
        stop_on_failed=stop_on_failed,
    )

    failed = True
    if not all([response.failed for response in scrapli_response]):
        failed = False

    full_results = "\n\n".join([response.result for response in scrapli_response])

    result = Result(host=task.host, result=full_results, failed=failed, changed=False)
    setattr(result, "scrapli_response", scrapli_response)
    return result

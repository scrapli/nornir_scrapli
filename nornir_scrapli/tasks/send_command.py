"""nornir_scrapli.tasks.send_command"""
from typing import List, Optional, Union

from nornir.core.task import Result, Task

from nornir_scrapli.result import ScrapliResult, process_command_result


def send_command(
    task: Task,
    command: str,
    strip_prompt: bool = True,
    failed_when_contains: Optional[Union[str, List[str]]] = None,
) -> Result:
    """
    Send a single command to device using scrapli

    Args:
        task: nornir task object
        command: string to send to device in privilege exec mode
        strip_prompt: True/False strip prompt from returned output
        failed_when_contains: string or list of strings indicating failure if found in response

    Returns:
        Result: scrapli nornir result object; almost identical to a "normal" nornir result object,
            but contains an additional attribute "scrapli_response" that contains the original
            response from scrapli

    Raises:
        N/A

    """
    scrapli_conn = task.host.get_connection("scrapli", task.nornir.config)
    scrapli_response = scrapli_conn.send_command(
        command=command, strip_prompt=strip_prompt, failed_when_contains=failed_when_contains
    )

    result = ScrapliResult(
        host=task.host,
        result=process_command_result(scrapli_response=scrapli_response),
        scrapli_response=scrapli_response,
        changed=False,
    )
    return result

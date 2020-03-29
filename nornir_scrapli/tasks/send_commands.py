"""nornir_scrapli.tasks.send_commands"""
from nornir.core.task import List, Result, Task


def send_commands(task: Task, commands: List[str], strip_prompt: bool = True) -> Result:
    """
    Send a single command to device using scrapli

    Args:
        task: nornir task object
        commands: list of strings to send to device in privilege exec mode
        strip_prompt: True/False strip prompt from returned output

    Returns:
        Result: nornir result object with Result.result value set to returned scrapli Response
            object

    Raises:
        N/A

    """
    scrapli_conn = task.host.get_connection("scrapli", task.nornir.config)
    scrapli_response = scrapli_conn.send_commands(
        commands=commands, strip_prompt=strip_prompt
    )

    failed = True
    if not all([response.failed for response in scrapli_response]):
        failed = False

    full_results = "\n\n".join([response.result for response in scrapli_response])

    result = Result(host=task.host, result=full_results, failed=failed, changed=False)
    setattr(result, "scrapli_response", scrapli_response)
    return result

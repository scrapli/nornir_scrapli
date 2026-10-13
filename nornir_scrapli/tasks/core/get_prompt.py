"""nornir_scrapli.tasks.get_prompt"""

from nornir.core.task import Result, Task
from nornir_scrapli.connection import ScrapliCore


def get_prompt(task: Task) -> Result:
    """
    Get current prompt from device using scrapli

    Args:
        task: nornir task object

    Returns:
        Result: nornir result object with Result.result value set to current prompt

    """
    scrapli_conn = ScrapliCore.get_connection(task)
    prompt = scrapli_conn.get_prompt()
    return Result(host=task.host, result=prompt, failed=False, changed=False)

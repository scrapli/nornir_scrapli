"""nornir_scrapli.tasks.netconf_commit"""

from nornir.core.task import Result, Task
from nornir_scrapli.result import ScrapliResult, process_command_result


def netconf_commit(
    task: Task,
) -> Result:
    """
    Commit the device config with scrapli_netconf

    Args:
        task: nornir task object

    Returns:
        Result: nornir result object with Result.result value set the string result of the
            get operation

    Raises:
        N/A

    """
    scrapli_conn = task.host.get_connection("scrapli_netconf", task.nornir.config)
    scrapli_response = scrapli_conn.commit()

    result = ScrapliResult(
        host=task.host,
        result=process_command_result(scrapli_response=scrapli_response),
        scrapli_response=scrapli_response,
        changed=True,
    )
    return result

"""nornir_scrapli.tasks.netconf_delete_config"""
from nornir.core.task import Result, Task
from nornir_scrapli.result import ScrapliResult, process_command_result


def netconf_delete_config(
    task: Task,
    target: str = "candidate",
) -> Result:
    """
    Send a "delete-config" rcp to the device with scrapli_netconf

    Args:
        task: nornir task object
        target: configuration source to target; startup|candidate

    Returns:
        Result: nornir result object with Result.result value set the string result of the
            delete operation

    Raises:
        N/A

    """
    scrapli_conn = task.host.get_connection("scrapli_netconf", task.nornir.config)
    scrapli_response = scrapli_conn.delete_config(target=target)

    result = ScrapliResult(
        host=task.host,
        result=process_command_result(scrapli_response=scrapli_response),
        scrapli_response=scrapli_response,
        changed=True,
    )
    return result

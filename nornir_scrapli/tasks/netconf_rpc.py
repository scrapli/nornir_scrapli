"""nornir_scrapli.tasks.netconf_rpc"""
from nornir.core.task import Result, Task
from nornir_scrapli.result import ScrapliResult, process_command_result


def netconf_rpc(
    task: Task,
    filter_: str,
) -> Result:
    """
    Send a "bare" rcp to the device with scrapli_netconf

    Args:
        task: nornir task object
        filter_: filter/rpc to execute

    Returns:
        Result: nornir result object with Result.result value set the string result of the
            rpc operation

    Raises:
        N/A

    """
    scrapli_conn = task.host.get_connection("scrapli_netconf", task.nornir.config)
    scrapli_response = scrapli_conn.rpc(filter_=filter_)

    result = ScrapliResult(
        host=task.host,
        result=process_command_result(scrapli_response=scrapli_response),
        scrapli_response=scrapli_response,
        changed=True,
    )
    return result

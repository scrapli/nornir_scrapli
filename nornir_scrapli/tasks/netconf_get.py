"""nornir_scrapli.tasks.netconf_get"""
from nornir.core.task import Result, Task
from nornir_scrapli.result import ScrapliResult, process_command_result


def netconf_get(
    task: Task,
    filter_: str,
    filter_type: str = "subtree",
) -> Result:
    """
    Get from the device with scrapli_netconf

    Args:
        task: nornir task object
        filter_: string filter to apply to the get
        filter_type: type of filter; subtree|xpath

    Returns:
        Result: nornir result object with Result.result value set the string result of the
            get operation

    Raises:
        N/A

    """
    scrapli_conn = task.host.get_connection("scrapli_netconf", task.nornir.config)
    scrapli_response = scrapli_conn.get(filter_=filter_, filter_type=filter_type)

    result = ScrapliResult(
        host=task.host,
        result=process_command_result(scrapli_response=scrapli_response),
        scrapli_response=scrapli_response,
        changed=False,
    )
    return result

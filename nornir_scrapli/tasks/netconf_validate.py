"""nornir_scrapli.tasks.netconf_validate"""
from nornir.core.task import Result, Task
from nornir_scrapli.result import ScrapliResult, process_command_result


def netconf_validate(
    task: Task,
    source: str,
) -> Result:
    """
    Send a "validate" rcp to the device with scrapli_netconf

    Args:
        task: nornir task object
        source: configuration source to validate; typically one of running|startup|candidate

    Returns:
        Result: nornir result object with Result.result value set the string result of the
            get operation

    Raises:
        N/A

    """
    scrapli_conn = task.host.get_connection("scrapli_netconf", task.nornir.config)
    scrapli_response = scrapli_conn.validate(source=source)

    result = ScrapliResult(
        host=task.host,
        result=process_command_result(scrapli_response=scrapli_response),
        scrapli_response=scrapli_response,
        changed=False,
    )
    return result

"""nornir_scrapli.tasks.netconf_get_config"""
from typing import List, Optional, Union

from nornir.core.task import Result, Task
from nornir_scrapli.result import ScrapliResult, process_command_result


def netconf_get_config(
    task: Task,
    source: str = "running",
    filters: Optional[Union[str, List[str]]] = None,
    filter_type: str = "subtree",
) -> Result:
    """
    Get config from the device with scrapli_netconf

    Args:
        task: nornir task object
        source: configuration source to get; typically one of running|startup|candidate
        filters: string or list of strings of filters to apply to configuration
        filter_type: type of filter; subtree|xpath

    Returns:
        Result: nornir result object with Result.result value set the string result of the
            get_config operation

    Raises:
        N/A

    """
    scrapli_conn = task.host.get_connection("scrapli_netconf", task.nornir.config)
    scrapli_response = scrapli_conn.get_config(
        source=source, filters=filters, filter_type=filter_type
    )

    result = ScrapliResult(
        host=task.host,
        result=process_command_result(scrapli_response=scrapli_response),
        scrapli_response=scrapli_response,
        changed=False,
    )
    return result

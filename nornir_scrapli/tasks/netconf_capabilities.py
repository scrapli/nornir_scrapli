"""nornir_scrapli.tasks.netconf_capabilities"""
from nornir.core.task import Result, Task


def netconf_capabilities(
    task: Task,
) -> Result:
    """
    Retrieve the device config with scrapli_netconf

    Args:
        task: nornir task object

    Returns:
        Result: nornir result object with Result.result value set to a list of strings representing
            the device capabilities

    Raises:
        N/A

    """
    scrapli_conn = task.host.get_connection("scrapli_netconf", task.nornir.config)

    result = Result(
        host=task.host,
        result=scrapli_conn.server_capabilities,
        failed=False,
        changed=False,
    )
    return result

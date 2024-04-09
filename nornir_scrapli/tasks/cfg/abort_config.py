"""nornir_scrapli.tasks.cfg_abort_config"""

from nornir.core.task import Result, Task
from nornir_scrapli.connection import ScrapliConfig
from nornir_scrapli.result import ScrapliResult


def cfg_abort_config(task: Task) -> Result:
    """
    Abort a device candidate config with scrapli-cfg

    Args:
        task: nornir task object

    Returns:
        Result: nornir result object with Result.result value set the string result of the
            load_config operation

    Raises:
        N/A

    """
    scrapli_cfg_conn = ScrapliConfig.get_connection(task=task)

    scrapli_response = scrapli_cfg_conn.abort_config()

    result = ScrapliResult(
        host=task.host,
        result=scrapli_response.result,
        scrapli_response=scrapli_response,
        changed=False,
    )

    return result

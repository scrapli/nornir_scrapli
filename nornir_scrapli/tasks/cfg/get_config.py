"""nornir_scrapli.tasks.cfg_get_config"""

from nornir.core.task import Result, Task
from nornir_scrapli.connection import ScrapliConfig
from nornir_scrapli.result import ScrapliResult


def cfg_get_config(task: Task, source: str = "running") -> Result:
    """
    Get device config with scrapli-cfg

    Args:
        task: nornir task object
        source: config source to get

    Returns:
        Result: nornir result object with Result.result value set to current prompt

    Raises:
        N/A

    """
    scrapli_cfg_conn = ScrapliConfig.get_connection(task=task)

    scrapli_response = scrapli_cfg_conn.get_config(source=source)

    result = ScrapliResult(
        host=task.host,
        result=scrapli_response.result,
        scrapli_response=scrapli_response,
        changed=False,
    )

    return result

"""nornir_scrapli.tasks.cfg.get_version"""

from nornir.core.task import Result, Task
from nornir_scrapli.connection import ScrapliConfig


def cfg_get_version(task: Task) -> Result:
    """
    Get device version with scrapli-cfg

    Args:
        task: nornir task object

    Returns:
        Result: nornir result object with Result.result value set to current version of device

    Raises:
        N/A

    """
    scrapli_cfg_conn = ScrapliConfig.get_connection(task=task)

    version = scrapli_cfg_conn.get_version()

    return Result(host=task.host, result=version.result, failed=False, changed=False)

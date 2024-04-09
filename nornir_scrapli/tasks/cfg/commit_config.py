"""nornir_scrapli.tasks.cfg_commit_config"""

from nornir.core.task import Result, Task
from nornir_scrapli.connection import ScrapliConfig
from nornir_scrapli.result import ScrapliResult


def cfg_commit_config(task: Task, source: str = "running") -> Result:
    """
    Commit a device candidate config with scrapli-cfg

    Args:
        task: nornir task object
        source: name of the config source to commit against, generally running|startup

    Returns:
        Result: nornir result object with Result.result value set the string result of the
            load_config operation

    Raises:
        N/A

    """
    scrapli_cfg_conn = ScrapliConfig.get_connection(task=task)

    scrapli_response = scrapli_cfg_conn.commit_config(source=source)

    result = ScrapliResult(
        host=task.host,
        result=scrapli_response.result,
        scrapli_response=scrapli_response,
        changed=True,
    )

    return result

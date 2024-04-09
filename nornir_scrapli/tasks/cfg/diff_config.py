"""nornir_scrapli.tasks.cfg_diff_config"""

from nornir.core.task import Result, Task
from nornir_scrapli.connection import ScrapliConfig
from nornir_scrapli.result import ScrapliResult


def cfg_diff_config(task: Task, source: str = "running") -> Result:
    """
    Diff a device candidate config vs a source config with scrapli-cfg

    The "device diff" is stored as the result. You can access the side by side or unified scrapli
    cfg diffs via the "scrapli_response" object stored in the result!

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

    scrapli_response = scrapli_cfg_conn.diff_config(source=source)

    result = ScrapliResult(
        host=task.host,
        result=scrapli_response.device_diff,
        scrapli_response=scrapli_response,
        changed=False,
    )

    return result

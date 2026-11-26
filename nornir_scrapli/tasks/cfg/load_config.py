"""nornir_scrapli.tasks.cfg_load_config"""

from nornir.core.task import Task
from nornir_scrapli.connection import ScrapliConfig
from nornir_scrapli.result import ScrapliResult


# `**kwargs: object`, not `Any`: with mypy, an `Any` parameter makes `nr.run()` type the result of
# this task as `Any`.
def cfg_load_config(
    task: Task, config: str, replace: bool = False, **kwargs: object
) -> ScrapliResult[str]:
    """
    Load device config with scrapli-cfg

    Note that `changed` will still be `False` because this is just loading a candidate config!

    Args:
        task: nornir task object
        config: string of the configuration to load
        replace: replace the configuration or not, if false configuration will be loaded as a
            merge operation
        kwargs: additional kwargs that the implementing classes may need for their platform,
            see your specific platform for details

    Returns:
        Result: nornir result object with Result.result value set the string result of the
            load_config operation

    """
    scrapli_cfg_conn = ScrapliConfig.get_connection(task=task)

    scrapli_response = scrapli_cfg_conn.load_config(config=config, replace=replace, **kwargs)

    result = ScrapliResult(
        host=task.host,
        result=scrapli_response.result,
        scrapli_response=scrapli_response,
        changed=False,
    )

    return result

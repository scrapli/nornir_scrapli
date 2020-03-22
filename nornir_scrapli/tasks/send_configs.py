"""nornir_scrapli.tasks.send_configs"""
from nornir.core.task import List, Result, Task, Union


def send_configs(
    task: Task, configs: Union[str, List[str]], strip_prompt: bool = True
) -> Result:
    """
    Send a single command to device using scrapli

    Args:
        task: nornir task object
        configs: string or list of strings to send to device in config mode
        strip_prompt: True/False strip prompt from returned output

    Returns:
        Result: nornir result object with Result.result value set to returned scrapli Response
            object

    Raises:
        N/A

    """
    scrapli_conn = task.host.get_connection("scrapli", task.nornir.config)
    scrapli_response = scrapli_conn.send_configs(
        configs=configs, strip_prompt=strip_prompt
    )

    failed = True
    if not all([response.failed for response in scrapli_response]):
        failed = False

    return Result(host=task.host, result=scrapli_response, failed=failed)

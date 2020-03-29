"""nornir_scrapli.tasks.send_configs"""
from nornir.core.task import List, Result, Task, Union


def send_configs(
    task: Task,
    dry_run: bool = False,
    configs: Union[str, List[str]] = None,
    strip_prompt: bool = True,
) -> Result:
    """
    Send a single command to device using scrapli

    Args:
        task: nornir task object
        dry_run: Whether to apply changes or not; if dry run, will ensure that it is possible to
            enter config mode, but will NOT send any configs
        configs: string or list of strings to send to device in config mode
        strip_prompt: True/False strip prompt from returned output

    Returns:
        Result: nornir result object with Result.result value set to returned scrapli Response
            object

    Raises:
        N/A

    """
    if configs is None:
        return Result(
            host=task.host, result="No configs provided...", failed=True, changed=False
        )
    if isinstance(configs, str):
        configs = [configs]

    scrapli_conn = task.host.get_connection("scrapli", task.nornir.config)

    if dry_run:
        # if dry run, try to acquire config mode then back out; do not send any configurations!
        scrapli_conn.acquire_priv("configuration")
        scrapli_conn.acquire_priv(scrapli_conn.default_desired_priv)
        return Result(host=task.host, result=None, failed=False, changed=False)

    scrapli_response = scrapli_conn.send_configs(
        configs=configs, strip_prompt=strip_prompt
    )

    failed = True
    if not all([response.failed for response in scrapli_response]):
        failed = False

    full_results = ""
    for config, response in zip(configs, scrapli_response):
        full_results += "\n".join([config, response.result])

    result = Result(host=task.host, result=full_results, failed=failed, changed=True)
    setattr(result, "scrapli_response", scrapli_response)
    return result

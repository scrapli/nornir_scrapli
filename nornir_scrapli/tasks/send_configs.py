"""nornir_scrapli.tasks.send_configs"""
from typing import List, Optional, Union

from nornir.core.task import Result, Task


def send_configs(
    task: Task,
    dry_run: bool = False,
    configs: Union[str, List[str]] = None,
    strip_prompt: bool = True,
    failed_when_contains: Optional[Union[str, List[str]]] = None,
    stop_on_failed: bool = False,
    privilege_level: str = "",
) -> Result:
    """
    Send a single command to device using scrapli

    Args:
        task: nornir task object
        dry_run: Whether to apply changes or not; if dry run, will ensure that it is possible to
            enter config mode, but will NOT send any configs
        configs: string or list of strings to send to device in config mode
        strip_prompt: True/False strip prompt from returned output
        failed_when_contains: string or list of strings indicating failure if found in response
        stop_on_failed: True/False stop executing commands if a command fails, returns results as of
            current execution
        privilege_level: name of configuration privilege level/type to acquire; this is platform
            dependent, so check the device driver for specifics. Examples of privilege_name
            would be "configuration_exclusive" for IOSXRDriver, or "configuration_private" for
            JunosDriver. You can also pass in a name of a configuration session such as
            "my-config-session" if you have registered a session using the
            "register_config_session" method of the EOSDriver or NXOSDriver.

    Returns:
        Result: nornir result object with Result.result value set to returned scrapli Response
            object

    Raises:
        N/A

    """
    if task.host.platform == "generic":
        return Result(
            host=task.host,
            result="No config mode for 'generic' platform type",
            failed=True,
            changed=False,
        )
    if configs is None:
        return Result(host=task.host, result="No configs provided...", failed=True, changed=False)

    scrapli_conn = task.host.get_connection("scrapli", task.nornir.config)

    if dry_run:
        # if dry run, try to acquire config mode then back out; do not send any configurations!
        scrapli_conn.acquire_priv("configuration")
        scrapli_conn.acquire_priv(scrapli_conn.default_desired_privilege_level)
        return Result(host=task.host, result=None, failed=False, changed=False)

    scrapli_response = scrapli_conn.send_configs(
        configs=configs,
        strip_prompt=strip_prompt,
        failed_when_contains=failed_when_contains,
        stop_on_failed=stop_on_failed,
        privilege_level=privilege_level,
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

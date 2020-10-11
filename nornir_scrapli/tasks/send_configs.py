"""nornir_scrapli.tasks.send_configs"""
from typing import List, Optional, Union

from nornir.core.task import Result, Task
from nornir_scrapli.exceptions import NornirScrapliNoConfigModeGenericDriver
from nornir_scrapli.result import ScrapliResult, process_config_result


def send_configs(
    task: Task,
    configs: List[str],
    dry_run: bool = False,
    strip_prompt: bool = True,
    failed_when_contains: Optional[Union[str, List[str]]] = None,
    stop_on_failed: bool = False,
    privilege_level: str = "",
    timeout_ops: Optional[float] = None,
) -> Result:
    """
    Send configs to device using scrapli

    Args:
        task: nornir task object
        configs: list of strings to send to device in config mode
        dry_run: Whether to apply changes or not; if dry run, will ensure that it is possible to
            enter config mode, but will NOT send any configs
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
        timeout_ops: timeout ops value for this operation; only sets the timeout_ops value for
            the duration of the operation, value is reset to initial value after operation is
            completed. Note that this is the timeout value PER CONFIG sent, not for the total
            of the configs being sent!

    Returns:
        Result: nornir result object with Result.result value set to returned scrapli Response
            object

    Raises:
        NornirScrapliNoConfigModeGenericDriver: If attempting to use this task function against a
            host that is using the "generic" platform type

    """
    if task.host.platform == "generic":
        raise NornirScrapliNoConfigModeGenericDriver("No config mode for 'generic' platform type")

    scrapli_conn = task.host.get_connection("scrapli", task.nornir.config)

    if dry_run:
        # if dry run, try to acquire config mode then back out; do not send any configurations!
        scrapli_conn.acquire_priv("configuration")
        scrapli_conn.acquire_priv(scrapli_conn.default_desired_privilege_level)
        return ScrapliResult(host=task.host, result=None, scrapli_response=None, changed=False)

    scrapli_response = scrapli_conn.send_configs(
        configs=configs,
        strip_prompt=strip_prompt,
        failed_when_contains=failed_when_contains,
        stop_on_failed=stop_on_failed,
        privilege_level=privilege_level,
        timeout_ops=timeout_ops,
    )

    result = ScrapliResult(
        host=task.host,
        result=process_config_result(scrapli_response=scrapli_response),
        scrapli_response=scrapli_response,
        changed=True,
    )
    return result

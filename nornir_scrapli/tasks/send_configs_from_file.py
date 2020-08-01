"""nornir_scrapli.tasks.send_configs_from_file"""
from nornir.core.task import List, Result, Task, Union
from typing import Optional


def send_configs_from_file(
    task: Task,
    file: str,
    dry_run: bool = False,
    strip_prompt: bool = True,
    failed_when_contains: Optional[Union[str, List[str]]] = None,
    stop_on_failed: bool = False,
    privilege_level: str = "",
) -> Result:
    """
    Send configuration(s) from a file
    Args:
        task: nornir task object
        file: string path to file
        dry_run: Whether to apply changes or not; if dry run, will ensure that it is possible to
                 enter config mode, but will NOT send any configs
        strip_prompt: True/False strip prompt from returned output
        failed_when_contains: string or list of strings indicating failure if found in response
        stop_on_failed: True/False stop executing commands if a command fails, returns results
            as of current execution; aborts configuration session if applicable (iosxr/junos or
            eos/nxos if using a configuration session)
        privilege_level: name of configuration privilege level/type to acquire; this is platform
            dependent, so check the device driver for specifics. Examples of privilege_name
            would be "exclusive" for IOSXRDriver, "private" for JunosDriver. You can also pass
            in a name of a configuration session such as "session_mysession" if you have
            registered a session using the "register_config_session" method of the EOSDriver or
            NXOSDriver.
    Returns:
            Result: nornir result object with Result.result value set to returned scrapli
                    Response object
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
    if file is None:
        return Result(
            host=task.host,
            result="No configs file provided...",
            failed=True,
            changed=False,
        )
    if isinstance(file, str):
        file = file

    scrapli_conn = task.host.get_connection("scrapli", task.nornir.config)

    if dry_run:
        # if dry run, try to acquire config mode then back out; do not send any configurations!
        scrapli_conn.acquire_priv("configuration")
        scrapli_conn.acquire_priv(scrapli_conn.default_desired_privilege_level)
        return Result(host=task.host, result=None, failed=False, changed=False)

    scrapli_response = scrapli_conn.send_configs_from_file(
        file=file,
        strip_prompt=strip_prompt,
        failed_when_contains=failed_when_contains,
        stop_on_failed=stop_on_failed,
        privilege_level=privilege_level,
    )

    failed = True
    if not all([response.failed for response in scrapli_response]):
        failed = False

    result = Result(
        host=task.host, result=scrapli_response.result, failed=failed, changed=True
    )
    setattr(result, "scrapli_response", scrapli_response)
    return result

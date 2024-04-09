"""nornir_scrapli.tasks.netconf_edit_config"""

from typing import Optional

from nornir.core.task import Result, Task
from nornir_scrapli.helper import diff_xml_text
from nornir_scrapli.result import ScrapliResult, process_command_result


def netconf_edit_config(
    task: Task,
    config: str,
    dry_run: Optional[bool] = None,
    diff: bool = False,
    target: str = "running",
) -> Result:
    """
    Edit config from the device with scrapli_netconf

    Args:
        task: nornir task object
        config: configuration to send to device
        dry_run: if True config will be pushed and then discarded; will discard anything already
            pushed that has *not* been committed already, so be careful! :D; also note that this
            will only work if there is a candidate datastore -- meaning that, for example, with
            IOSXE with a target of "running" there is no way to discard the configuration as it will
            already have been written to the running datastore
        diff: capture/set diff of target datastore xml text of before/after edit config operation
        target: configuration source to target; running|startup|candidate

    Returns:
        Result: nornir result object with Result.result value set the string result of the
            get_config operation

    Raises:
        N/A

    """
    scrapli_conn = task.host.get_connection("scrapli_netconf", task.nornir.config)

    if diff:
        original_config = scrapli_conn.get_config(source=target)

    scrapli_response = scrapli_conn.edit_config(config=config, target=target)

    if diff:
        edited_config = scrapli_conn.get_config(source=target)
        diff_result = diff_xml_text(original_config.result, edited_config.result)
    else:
        diff_result = ""

    _task_dry_run = dry_run if dry_run is not None else task.global_dry_run

    if _task_dry_run:
        scrapli_conn.discard()
        changed = False
    else:
        changed = True

    result = ScrapliResult(
        host=task.host,
        result=process_command_result(scrapli_response=scrapli_response),
        scrapli_response=scrapli_response,
        changed=changed,
        diff=diff_result,
    )
    return result

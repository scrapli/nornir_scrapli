"""nornir_scrapli.tasks.send_interactive"""
from typing import List, Optional, Tuple, Union

from nornir.core.task import Result, Task


def send_interactive(
    task: Task,
    interact_events: List[Tuple[str, str, Optional[bool]]],
    failed_when_contains: Optional[Union[str, List[str]]] = None,
    privilege_level: str = "",
) -> Result:
    """
    Send inputs in an interactive fashion using scrapli; usually used to handle prompts

    Used to interact with devices where prompts change per input, and where inputs may be hidden
    such as in the case of a password input. This can be used to respond to challenges from
    devices such as the confirmation for the command "clear logging" on IOSXE devices for
    example. You may have as many elements in the "interact_events" list as needed, and each
    element of that list should be a tuple of two or three elements. The first element is always
    the input to send as a string, the second should be the expected response as a string, and
    the optional third a bool for whether or not the input is "hidden" (i.e. password input)
    An example where we need this sort of capability:

    ```
    3560CX#copy flash: scp:
    Source filename []? test1.txt
    Address or name of remote host []? 172.31.254.100
    Destination username [carl]?
    Writing test1.txt
    Password:
    Password:
     Sink: C0644 639 test1.txt
    !
    639 bytes copied in 12.066 secs (53 bytes/sec)
    3560CX#
    ```

    To accomplish this we can use the following (in "native" scrapli):

    ```
    interact = conn.channel.send_inputs_interact(
        [
            ("copy flash: scp:", "Source filename []?", False),
            ("test1.txt", "Address or name of remote host []?", False),
            ("172.31.254.100", "Destination username [carl]?", False),
            ("carl", "Password:", False),
            ("super_secure_password", prompt, True),
        ]
    )
    ```

    If we needed to deal with more prompts we could simply continue adding tuples to the list of
    interact "events".

    Args:
        task: nornir task object
        interact_events: list of tuples containing the "interactions" with the device
            each list element must have an input and an expected response, and may have an
            optional bool for the third and final element -- the optional bool specifies if the
            input that is sent to the device is "hidden" (ex: password), if the hidden param is
            not provided it is assumed the input is "normal" (not hidden)
        failed_when_contains: list of strings that, if present in final output, represent a
            failed command/interaction
        privilege_level: name of the privilege level to operate in

    Returns:
        Result: nornir result object with Result.result value set to returned scrapli Response
            object

    Raises:
        N/A

    """
    scrapli_conn = task.host.get_connection("scrapli", task.nornir.config)
    scrapli_response = scrapli_conn.send_interactive(
        interact_events=interact_events,
        failed_when_contains=failed_when_contains,
        privilege_level=privilege_level,
    )

    result = Result(
        host=task.host,
        result=scrapli_response,
        failed=scrapli_response.failed,
        changed=True,
    )
    setattr(result, "scrapli_response", scrapli_response)
    return result

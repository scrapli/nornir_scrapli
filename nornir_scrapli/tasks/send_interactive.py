"""nornir_scrapli.tasks.send_interactive"""
from nornir.core.task import List, Result, Task


def send_interactive(
    task: Task, interact: List[str], hidden_response: bool = False
) -> Result:
    """
    Send inputs in an interactive fashion using scrapli; usually used to handle prompts

    accepts inputs and looks for expected prompt;
    sends the appropriate response, then waits for the "finale"
    returns the results of the interaction

    Args:
        task: nornir task object
        interact: list of four string elements representing...
            channel_input - initial input to send
            expected_prompt - prompt to expect after initial input
            response - response to prompt
            final_prompt - final prompt to expect
        hidden_response: True/False response is hidden (i.e. password input)

    Returns:
        Result: nornir result object with Result.result value set to returned scrapli Response
            object

    Raises:
        N/A

    """
    scrapli_conn = task.host.get_connection("scrapli", task.nornir.config)
    scrapli_response = scrapli_conn.send_interactive(
        interact=interact, hidden_response=hidden_response
    )

    result = Result(
        host=task.host,
        result=scrapli_response,
        failed=scrapli_response.failed,
        changed=True,
    )
    setattr(result, "scrapli_response", scrapli_response)
    return result

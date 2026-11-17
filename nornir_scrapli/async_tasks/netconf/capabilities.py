"""Read NETCONF capabilities from an asyncio connection."""

from nornir.core.task import Result, Task


async def netconf_capabilities(
    task: Task,
) -> Result:
    """Return the capabilities the device advertised when the session opened.

    Scrapli v2 stores the capabilities during the open, so this task sends no RPC.

    Args:
        task: Nornir task.

    Returns:
        Nornir result containing the list of capability strings.
    """
    connection = await task.host.aget_connection("scrapli_netconf", task.nornir.config)
    return Result(
        host=task.host,
        result=connection.get_capabilities(),
        failed=False,
        changed=False,
    )

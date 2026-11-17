"""nornir_scrapli.examples.asyncio_usage.demo"""

import asyncio

from nornir_utils.plugins.functions import print_result

from nornir import AInitNornir
from nornir.core.task import Result, Task
from nornir_scrapli.async_tasks import get_prompt, send_command, send_configs


async def check_and_configure(task: Task) -> Result:
    """Read the prompt, run a command and test a configuration change as a dry run.

    Returns:
        Result naming the prompt that was read.
    """
    prompt = await task.arun(get_prompt)
    await task.arun(send_command, command="show version")
    await task.arun(send_configs, configs=["interface loopback123"], dry_run=True)
    return Result(host=task.host, result=f"checked {prompt.result}")


async def main() -> None:
    """Run the workflow on every host concurrently with the asyncio runner."""
    # AInitNornir loads the inventory without blocking the event loop
    nr = await AInitNornir(config_file="nornir_data/config.yaml")
    # leaving the `async with` block closes every connection opened during the run
    async with nr:
        results = await nr.arun(task=check_and_configure)
    print_result(results)


if __name__ == "__main__":
    asyncio.run(main())

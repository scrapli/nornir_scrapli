"""Run a command and a configuration dry run with Nornir's asyncio runner."""

import argparse
import asyncio

from nornir import InitNornir
from nornir.core.task import Result, Task
from nornir_scrapli.async_tasks import send_command, send_configs


async def configure(task: Task) -> Result:
    await task.arun(task=send_command, command="show version")
    result = await task.arun(
        task=send_configs,
        configs=["interface Loopback100", "description managed-by-nornir"],
        dry_run=True,
    )
    return result[0]


async def main(config_file: str) -> None:
    async with InitNornir(
        config_file=config_file,
        runner={"plugin": "asyncio", "options": {"num_workers": 100}},
    ) as nr:
        results = await nr.arun(task=configure)
        for hostname, result in results.items():
            print(hostname, result.failed, result[0].result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config_file", help="Nornir configuration with a SimpleInventory")
    asyncio.run(main(parser.parse_args().config_file))

"""nornir_scrapli.functions.print_structured_result"""
import logging
import threading
from typing import List, Optional

from nornir.core.task import AggregatedResult, MultiResult, Result
from nornir.plugins.functions.text import _print_result
from scrapli.response import Response

LOCK = threading.Lock()


def print_structured_result(
    result: Result,
    host: Optional[str] = None,
    nr_vars: Optional[List[str]] = None,
    failed: bool = False,
    severity_level: int = logging.INFO,
    parser: str = "textfsm",
    fail_to_string: bool = False,
) -> None:
    """
    Prints the :obj:`nornir.core.task.Result` from a previous task to screen

    Arguments:
        result: from a previous task
        host: nornir host object for the task
        nr_vars: Which attributes you want to print
        failed: if `True` assume the task failed
        severity_level: Print only errors with this severity level or higher
        parser: textfsm|genie -- parser to parse output with
        fail_to_string: fallback to printing unstructured output or have tasks skipped (because
            print_result won't print empty lists which scrapli returns if parsing fails)

    """
    updated_agg_result = AggregatedResult(result.name)
    for hostname, multi_result in result.items():
        updated_multi_result = MultiResult(result.name)
        for individual_result in multi_result:
            scrapli_responses = getattr(individual_result, "scrapli_response", None)
            if isinstance(scrapli_responses, Response):
                scrapli_responses = [scrapli_responses]
            if not scrapli_responses:
                updated_multi_result.append(individual_result)
                continue
            for scrapli_response in scrapli_responses:
                parser_method = getattr(scrapli_response, f"{parser}_parse_output")
                updated_result = Result(
                    host=individual_result.host,
                    changed=individual_result.changed,
                    diff=individual_result.diff,
                    exception=individual_result.exception,
                    failed=individual_result.failed,
                    name=individual_result.name,
                    severity_level=individual_result.severity_level,
                    stderr=individual_result.stderr,
                    stdout=individual_result.stdout,
                )
                structured_result = parser_method()
                if not structured_result and fail_to_string:
                    updated_result.result = scrapli_response.result
                else:
                    updated_result.result = structured_result
                updated_multi_result.append(updated_result)
        if updated_multi_result:
            updated_agg_result[hostname] = updated_multi_result  # noqa

    LOCK.acquire()
    try:
        _print_result(updated_agg_result, host, nr_vars, failed, severity_level)
    finally:
        LOCK.release()

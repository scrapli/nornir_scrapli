"""nornir_scrapli.functions.print_structured_result"""
import logging
import threading

from nornir_utils.plugins.functions.print_result import _print_result
from scrapli.response import Response

from nornir.core.task import AggregatedResult, MultiResult, Result
from nornir_scrapli.result import ScrapliResult

LOCK = threading.Lock()


def print_structured_result(
    result: ScrapliResult,
    failed: bool = False,
    severity_level: int = logging.INFO,
    parser: str = "textfsm",
    to_dict: bool = True,
    fail_to_string: bool = False,
) -> None:
    """
    Prints the :obj:`nornir.core.task.Result` from a previous task to screen

    Arguments:
        result: from a previous task
        failed: if `True` assume the task failed
        severity_level: Print only errors with this severity level or higher
        parser: textfsm|genie -- parser to parse output with
        to_dict: output structured data in dict form instead -- basically put k:v instead of just
            lists of lists of values for textfsm output; ignored if parser == "genie"
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

                if parser == "textfsm":
                    structured_result = parser_method(to_dict=to_dict)
                else:
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
        _print_result(
            result=updated_agg_result, attrs=None, failed=failed, severity_level=severity_level
        )
    finally:
        LOCK.release()

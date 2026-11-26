import typing

import pytest

from nornir.core.task import Result
from nornir_scrapli import async_tasks, tasks
from nornir_scrapli.result import ScrapliResult

TASKS = [
    pytest.param(getattr(module, name), id=f"{module.__name__}.{name}")
    for module in (tasks, async_tasks)
    for name in module.__all__
]


@pytest.mark.parametrize("task", TASKS)
def test_task_return_annotation_types_the_result(task):
    """A bare ``Result`` annotation would make the result ``Any`` for the type checker."""
    annotation = typing.get_type_hints(task)["return"]

    origin = typing.get_origin(annotation) or annotation
    assert origin is ScrapliResult or (origin is Result and typing.get_args(annotation))

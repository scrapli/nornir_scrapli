"""nornir_scrapli.helper"""

import difflib
from typing import Union

from scrapli.netconf import DatastoreType

ANSI_GREEN = "\033[92m"
ANSI_RED = "\033[91m"
ANSI_END = "\033[0m"


def diff_xml_text(document_one: str, document_two: str) -> str:
    """
    Diff xml text strings

    Really could be just "diff text" but also ensuring we ignore the "message-id" lines. This is
    really pretty simple and not always super great, but better than nothing for now!

    Args:
        document_one: string of xml doc 1
        document_two: string of xml doc 2

    Returns:
        str: unified diff of the two input documents

    """
    # ignore message-id stuff -- maybe more in the future?
    document_one_lines = [line for line in document_one.splitlines() if "message-id" not in line]
    document_two_lines = [line for line in document_two.splitlines() if "message-id" not in line]
    diff = difflib.unified_diff(document_one_lines, document_two_lines)

    diff_lines = []
    for line in diff:
        if line.startswith("---") or line.startswith("+++"):
            # may as well just strip out the header lines and such, we dont care about them
            continue
        if line.startswith("+"):
            diff_lines.append(f"{ANSI_GREEN}{line}{ANSI_END}")
        elif line.startswith("-"):
            diff_lines.append(f"{ANSI_RED}{line}{ANSI_END}")
        else:
            diff_lines.append(line)

    return "\n".join(diff_lines)


def to_datastore(value: Union[DatastoreType, str]) -> DatastoreType:
    """
    Convert a datastore name to the scrapli datastore enum

    nornir_scrapli 1.x accepted datastore names as strings, such as "candidate". Accepting them
    here keeps those calls working with scrapli v2, which requires the enum.

    Args:
        value: datastore enum member or name, such as "running" or "candidate"

    Returns:
        DatastoreType: matching datastore enum member

    Raises:
        ValueError: if the value does not name a datastore

    """
    if isinstance(value, DatastoreType):
        return value
    try:
        return DatastoreType(value.lower())
    except (AttributeError, ValueError) as exc:
        names = ", ".join(member.value for member in DatastoreType)
        raise ValueError(f"Unknown NETCONF datastore {value!r}; expected one of: {names}") from exc

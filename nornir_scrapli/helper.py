"""nornir_scrapli.helper"""

import difflib

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

    Raises:
        N/A

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

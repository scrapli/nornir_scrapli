"""nornir_scrapli.helper"""
import difflib


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
    return "\n".join(diff)

<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module nornir_scrapli.helper

nornir_scrapli.helper

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
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
        </code>
    </pre>
</details>



## Functions

    

#### diff_xml_text
`diff_xml_text(document_one: str, document_two: str) ‑> str`

```text
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
```
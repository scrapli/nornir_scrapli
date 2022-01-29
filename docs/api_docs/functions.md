<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module nornir_scrapli.functions

nornir_scrapli.functions

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""nornir_scrapli.functions"""
from nornir_scrapli.functions.print_structured_result import print_structured_result

__all__ = ("print_structured_result",)
        </code>
    </pre>
</details>



## Functions

    

#### print_structured_result
`print_structured_result(result: nornir.core.task.AggregatedResult, failed: bool = False, severity_level: int = 20, parser: str = 'textfsm', to_dict: bool = True, fail_to_string: bool = False) ‑> None`

```text
Prints the :obj:`nornir.core.task.Result` from a previous task to screen

Arguments:
    result: Nornir AggregateResult object from a previous task
    failed: if `True` assume the task failed
    severity_level: Print only errors with this severity level or higher
    parser: textfsm|genie -- parser to parse output with
    to_dict: output structured data in dict form instead -- basically put k:v instead of just
        lists of lists of values for textfsm output; ignored if parser == "genie"
    fail_to_string: fallback to printing unstructured output or have tasks skipped (because
        print_result won't print empty lists which scrapli returns if parsing fails)
```
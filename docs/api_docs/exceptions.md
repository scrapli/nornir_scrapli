<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module nornir_scrapli.exceptions

nornir_scrapli.exceptions

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""nornir_scrapli.exceptions"""


class NornirScrapliException(Exception):
    """nornir_scrapli base exception"""


class NornirScrapliInvalidPlatform(NornirScrapliException):
    """nornir_scrapli base exception"""


class NornirScrapliNoConfigModeGenericDriver(NornirScrapliException):
    """nornir_scrapli exception for attempting config mode on generic platform"""
        </code>
    </pre>
</details>




## Classes

### NornirScrapliException


```text
nornir_scrapli base exception
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class NornirScrapliException(Exception):
    """nornir_scrapli base exception"""
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- builtins.Exception
- builtins.BaseException
#### Descendants
- nornir_scrapli.exceptions.NornirScrapliInvalidPlatform
- nornir_scrapli.exceptions.NornirScrapliNoConfigModeGenericDriver



### NornirScrapliInvalidPlatform


```text
nornir_scrapli base exception
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class NornirScrapliInvalidPlatform(NornirScrapliException):
    """nornir_scrapli base exception"""
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- nornir_scrapli.exceptions.NornirScrapliException
- builtins.Exception
- builtins.BaseException



### NornirScrapliNoConfigModeGenericDriver


```text
nornir_scrapli exception for attempting config mode on generic platform
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class NornirScrapliNoConfigModeGenericDriver(NornirScrapliException):
    """nornir_scrapli exception for attempting config mode on generic platform"""
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- nornir_scrapli.exceptions.NornirScrapliException
- builtins.Exception
- builtins.BaseException
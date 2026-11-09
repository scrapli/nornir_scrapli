# Structured data

Update the host credentials/address under `nornir_data`, then run `python demo.py`
from this directory. Install `nornir-scrapli[genie]` to run the optional Genie examples.

The demo shows ordinary output, `print_structured_result` with TextFSM/Genie, parse
failure fallback, and direct access to native indexed parsing:

```python
native = results["iosxe1"][0].scrapli_response
textfsm_results = native.textfsm_parse(index=0)
genie_results = native.genie_parse(index=0)
```

For a multi-command result, use the corresponding input index. The printing helper
handles every index automatically and leaves the original aggregate unchanged.
Bin SSH key checking is on by default; add an explicit `enable_strict_key: false` to
the transport section only when that is the desired connection policy.

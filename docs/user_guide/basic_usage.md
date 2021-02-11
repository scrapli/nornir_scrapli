# Basic Usage

## Basic Information/Usage

Nornir has historically contained it's plugins within the actual Nornir codebase itself, this however has changed! As
 of mid September 2020, Nornir 3.0.0 has been officially released -- this move to the 3.x.x version now expects
  plugins to be external to the code base. If you are looking for pre 3.x.x support, please use the `2020.09.01
  ` version.

If you have used Nornir before (pre 3.x.x), this package should be very similar to what you already know. Since the
 plugins used to live in Nornir you could simply import them from the appropriate package as such:
 
```python
from nornir.plugins.tasks.networking import netconf_get_config
```

With nornir_scrapli you simply install this package along side "regular" Nornir, and import the tasks from
 nornir_scrapli directly:
 
```python
from nornir_scrapli.tasks import send_command
```

As soon as a nornir_scrapli task is imported, it (`nornir_scrapli`) will register as a connection, and things should
 work as normal from there!

The last important difference with nornir_scrapli is that in addition to the "normal" data in the Nornir Result
 object, nornir_scrapli also assigns the scrapli `Response` object (or list of `Response` objects) to the
  `scrapli_response` attribute. This means that you can access all of the "normal" scrapli response data from this
   object -- including things like `elapsed_time` and `textfsm_parse_output`:

```python
>>> some_nornir_result["sea-ios-1"].scrapli_response.elapsed_time
0.039469
>>> some_nornir_result["sea-ios-1"].scrapli_response.textfsm_parse_output()
[[some structured data back from the device!]]
``` 

If you would like to continue using `print_result` like "normal" in nornir, but would like to see structured data (if
 available) in the `print_result` output, you can use the nornir_scrapli `print_structured_result` function. This
  function can be imported from the scrapli functions module:
  
```python
from nornir_scrapli.functions import print_structured_result
```

This function acts pretty much exactly like the "normal" print result function, but will of course try to print the
 structured result. By default this will try to use textfsm to parse results, but it is of course configurable via
  the `parser` keyword argument. As scrapli will return an empty data structure if parsing fails, this may cause
   tasks to look like they are getting skipped in the output (nornir's print result function does not print empty
    lists), if you would like to fall back to printing the unparsed output you can do so by setting the
     `fail_to_string` keyword argument to `True` as follows:
     
```python
print_structured_result(my_agg_result, parser="genie", fail_to_string=True)
```


## Using Different Transports

nornir_scrapli supports all *synchronous* scrapli transport plugins. By default, the "system" transport will be used, 
however you can change this in the `extras` section of your nornir inventory:

```yaml
connection_options:
  scrapli:
    port: 22
    extras:
      ssh_config_file: True
      auth_strict_key: False
      transport: ssh2
```

Note that you will need to install `scrapli_ssh2` or `scrapli_paramiko` if you want to use those transport plugins!

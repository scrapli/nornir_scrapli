# Project Details

## What is nornir_scrapli

nornir_scrapli is scrapli (and scrapli netconf's) plugin for Nornir. Nearly all (synchronous) methods of scrapli are 
available/exposed in nornir scrapli. So if you enjoy scrapli, but also want the built-in concurrency and inventory 
management afforded by nornir, this is the place to be!


## Supported Platforms

nornir_scrapli supports the "core" scrapli drivers, the GenericDriver (for use with linux hosts generally speaking
), and the [scrapli_community](https://github.com/scrapli/scrapli_community) platforms as well! See
[scrapli core docs](https://github.com/carlmontanari/scrapli#supported-platforms) and the
[scrapli community docs](https://github.com/scrapli/scrapli_community#supported-platforms) for more info. The `platform
` argument in the inventory data should use the "normal" NAPALM style platform names, `generic`, or the name of the
 scrapli_community platform (i.e. `huawei_vrp`)). 

Example platform values (for inventory data):

```
platform: cisco_iosxe
platform: cisco_iosxr
platform: cisco_nxos
platform: arista_eos
platform: juniper_junos
platform: generic
platform: huawei_vrp
```


## Related Scrapli Libraries

This repo is the nornir plugin for scrapli, however there are other libraries/repos in the scrapli family
 -- here is a list/link to all of the other scrapli things!


- [scrapli](/more_scrapli/scrapli)
- [scrapli_netconf](/more_scrapli/scrapli_netconf)
- [scrapli_community](/more_scrapli/scrapli_community)
- [scrapli_cfg](/more_scrapli/scrapli_cfg)
- [scrapli_replay](/more_scrapli/scrapli_replay)

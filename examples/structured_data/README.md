structured_data
===============

This directory contains a very simple setup to demo fetching/parsing structured data from a device with the
 `nornir_scrapli` `nornir` plugin.

A very standard `YAMLInventory` lives in the `nornir_data` directory along with a simple `config.yaml` file. There is
 a single host in this inventory -- this host is the IOSXE device in my `scrapli` functional test setup. You can read
  about how to set up that test environment with `vrnetlab` [here](https://github.com/carlmontanari/scrapli#testing) in the `scrapli` documentation. Or you can of
   course just update this inventory to point to a host in your environment for testing!

Below is the output of executing the `demo.py` script; please see inline in the script for comments which describe
 how the script works/how to work with structured data via `nornir_scrapli`!

```
$ python demo.py
send_command********************************************************************
* iosxe1 ** changed : False ****************************************************
vvvv send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
Cisco IOS Software, C3560CX Software (C3560CX-UNIVERSALK9-M), Version 15.2(4)E7, RELEASE SOFTWARE (fc2)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2018 by Cisco Systems, Inc.
Compiled Tue 18-Sep-18 13:20 by prod_rel_team

ROM: Bootstrap program is C3560CX boot loader
BOOTLDR: C3560CX Boot Loader (C3560CX-HBOOT-M) Version 15.2(4r)E5, RELEASE SOFTWARE (fc4)

C3560CX uptime is 2 weeks, 4 days, 9 hours, 58 minutes
System returned to ROM by power-on
System restarted at 00:19:10 PDT Tue Sep 8 2020
System image file is "flash:c3560cx-universalk9-mz.152-4.E7.bin"
Last reload reason: power-on



This product contains cryptographic features and is subject to United
States and local country laws governing import, export, transfer and
use. Delivery of Cisco cryptographic products does not imply
third-party authority to import, export, distribute or use encryption.
Importers, exporters, distributors and users are responsible for
compliance with U.S. and local country laws. By using this product you
agree to comply with applicable laws and regulations. If you are unable
to comply with U.S. and local laws, return this product immediately.

A summary of U.S. laws governing Cisco cryptographic products may be found at:
http://www.cisco.com/wwl/export/crypto/tool/stqrg.html

If you require further assistance please contact us by sending email to
export@cisco.com.

License Level: ipservices
License Type: Permanent Right-To-Use
Next reload license Level: ipservices

cisco WS-C3560CX-8PC-S (APM86XXX) processor (revision A0) with 524288K bytes of memory.
Processor board ID FOC1911Y0NH
Last reset from power-on
5 Virtual Ethernet interfaces
12 Gigabit Ethernet interfaces
The password-recovery mechanism is enabled.

512K bytes of flash-simulated non-volatile configuration memory.
Base ethernet MAC Address       : C8:00:84:B2:E9:80
Motherboard assembly number     : 73-16471-04
Power supply part number        : 341-0675-01
Motherboard serial number       : FOC190608U7
Power supply serial number      : DCB190430Z0
Model revision number           : A0
Motherboard revision number     : A0
Model number                    : WS-C3560CX-8PC-S
System serial number            : FOC1911Y0NH
Top Assembly Part Number        : 68-5359-01
Top Assembly Revision Number    : A0
Version ID                      : V01
CLEI Code Number                : CMM1400DRA
Hardware Board Revision Number  : 0x02


Switch Ports Model                     SW Version            SW Image
------ ----- -----                     ----------            ----------
*    1 12    WS-C3560CX-8PC-S          15.2(4)E7             C3560CX-UNIVERSALK9-M


Configuration register is 0xF
^^^^ END send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
send_command********************************************************************
* iosxe1 ** changed : False ****************************************************
vvvv send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
{ 'version': { 'bootldr': 'C3560CX Boot Loader (C3560CX-HBOOT-M) Version '
                          '15.2(4r)E5, RELEASE SOFTWARE (fc4)',
               'chassis': 'WS-C3560CX-8PC-S',
               'chassis_sn': 'FOC1911Y0NH',
               'compiled_by': 'prod_rel_team',
               'compiled_date': 'Tue 18-Sep-18 13:20',
               'curr_config_register': '0xF',
               'hostname': 'C3560CX',
               'image_id': 'C3560CX-UNIVERSALK9-M',
               'image_type': 'production image',
               'last_reload_reason': 'power-on',
               'license_level': 'ipservices',
               'license_type': 'Permanent Right-To-Use',
               'main_mem': '524288',
               'mem_size': { 'flash-simulated non-volatile configuration': '512'},
               'next_reload_license_level': 'ipservices',
               'number_of_intfs': { 'Gigabit Ethernet': '12',
                                    'Virtual Ethernet': '5'},
               'os': 'IOS',
               'platform': 'C3560CX',
               'processor_type': 'APM86XXX',
               'returned_to_rom_by': 'power-on',
               'rom': 'Bootstrap program is C3560CX boot loader',
               'rtr_type': 'WS-C3560CX-8PC-S',
               'system_image': 'flash:c3560cx-universalk9-mz.152-4.E7.bin',
               'system_restarted_at': '00:19:10 PDT Tue Sep 8 2020',
               'uptime': '2 weeks, 4 days, 9 hours, 58 minutes',
               'version': '15.2(4)E7',
               'version_short': '15.2'}}
^^^^ END send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
send_command********************************************************************
* iosxe1 ** changed : False ****************************************************
vvvv send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
[ { 'config_register': '0xF',
    'hardware': ['WS-C3560CX-8PC-S'],
    'hostname': 'C3560CX',
    'mac': ['C8:00:84:B2:E9:80'],
    'reload_reason': 'power-on',
    'rommon': 'Bootstrap',
    'running_image': 'c3560cx-universalk9-mz.152-4.E7.bin',
    'serial': ['FOC1911Y0NH'],
    'uptime': '2 weeks, 4 days, 9 hours, 58 minutes',
    'version': '15.2(4)E7'}]
^^^^ END send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
send_command********************************************************************
* iosxe1 ** changed : False ****************************************************
vvvv send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
[ { 'config_register': '0xF',
    'hardware': ['WS-C3560CX-8PC-S'],
    'hostname': 'C3560CX',
    'mac': ['C8:00:84:B2:E9:80'],
    'reload_reason': 'power-on',
    'rommon': 'Bootstrap',
    'running_image': 'c3560cx-universalk9-mz.152-4.E7.bin',
    'serial': ['FOC1911Y0NH'],
    'uptime': '2 weeks, 4 days, 9 hours, 58 minutes',
    'version': '15.2(4)E7'}]
^^^^ END send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<class 'nornir_scrapli.result.ScrapliResult'>
['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_process_failed', 'changed', 'diff', 'exception', 'failed', 'host', 'name', 'result', 'scrapli_response', 'severity_level', 'stderr', 'stdout']
<class 'scrapli.response.Response'>
['__bool__', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_record_response', 'channel_input', 'elapsed_time', 'failed', 'failed_when_contains', 'finish_time', 'genie_parse_output', 'genie_platform', 'host', 'raise_for_status', 'raw_result', 'result', 'start_time', 'textfsm_parse_output', 'textfsm_platform']
TEXTFSM RESULTS: 
 [{'version': '15.2(4)E7', 'rommon': 'Bootstrap', 'hostname': 'C3560CX', 'uptime': '2 weeks, 4 days, 9 hours, 58 minutes', 'reload_reason': 'power-on', 'running_image': 'c3560cx-universalk9-mz.152-4.E7.bin', 'hardware': ['WS-C3560CX-8PC-S'], 'serial': ['FOC1911Y0NH'], 'config_register': '0xF', 'mac': ['C8:00:84:B2:E9:80']}]
GENIE RESULTS: 
 {'version': {'version_short': '15.2', 'platform': 'C3560CX', 'version': '15.2(4)E7', 'image_id': 'C3560CX-UNIVERSALK9-M', 'os': 'IOS', 'image_type': 'production image', 'compiled_date': 'Tue 18-Sep-18 13:20', 'compiled_by': 'prod_rel_team', 'rom': 'Bootstrap program is C3560CX boot loader', 'bootldr': 'C3560CX Boot Loader (C3560CX-HBOOT-M) Version 15.2(4r)E5, RELEASE SOFTWARE (fc4)', 'hostname': 'C3560CX', 'uptime': '2 weeks, 4 days, 9 hours, 58 minutes', 'returned_to_rom_by': 'power-on', 'system_restarted_at': '00:19:10 PDT Tue Sep 8 2020', 'system_image': 'flash:c3560cx-universalk9-mz.152-4.E7.bin', 'last_reload_reason': 'power-on', 'license_level': 'ipservices', 'license_type': 'Permanent Right-To-Use', 'next_reload_license_level': 'ipservices', 'chassis': 'WS-C3560CX-8PC-S', 'main_mem': '524288', 'processor_type': 'APM86XXX', 'rtr_type': 'WS-C3560CX-8PC-S', 'chassis_sn': 'FOC1911Y0NH', 'number_of_intfs': {'Virtual Ethernet': '5', 'Gigabit Ethernet': '12'}, 'mem_size': {'flash-simulated non-volatile configuration': '512'}, 'curr_config_register': '0xF'}}
```

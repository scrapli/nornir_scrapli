import sys

import pytest
from scrapli.response import Response

from nornir.core.inventory import Host
from nornir.core.task import AggregatedResult, MultiResult, Result
from nornir_scrapli.functions import print_structured_result

IOSXE_SHOW_VERSION = """Cisco IOS XE Software, Version 16.04.01
Cisco IOS Software [Everest], CSR1000V Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.4.1, RELEASE SOFTWARE (fc2)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2016 by Cisco Systems, Inc.
Compiled Sun 27-Nov-16 13:02 by mcpre


Cisco IOS-XE software, Copyright (c) 2005-2016 by cisco Systems, Inc.
All rights reserved.  Certain components of Cisco IOS-XE software are
licensed under the GNU General Public License ("GPL") Version 2.0.  The
software code licensed under GPL Version 2.0 is free software that comes
with ABSOLUTELY NO WARRANTY.  You can redistribute and/or modify such
GPL code under the terms of GPL Version 2.0.  For more details, see the
documentation or "License Notice" file accompanying the IOS-XE software,
or the applicable URL provided on the flyer accompanying the IOS-XE
software.


ROM: IOS-XE ROMMON

csr1000v uptime is 2 hours, 43 minutes
Uptime for this control processor is 2 hours, 45 minutes
System returned to ROM by reload
System image file is "bootflash:packages.conf"
Last reload reason: reload



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

License Level: ax
License Type: Default. No valid license found.
Next reload license Level: ax

cisco CSR1000V (VXE) processor (revision VXE) with 2052375K/3075K bytes of memory.
Processor board ID 9FKLJWM5EB0
10 Gigabit Ethernet interfaces
32768K bytes of non-volatile configuration memory.
3985132K bytes of physical memory.
7774207K bytes of virtual hard disk at bootflash:.
0K bytes of  at webui:.

Configuration register is 0x2102

csr1000v#"""

IOSXE_SHOW_IP_ROUTE = """Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2
       i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
       ia - IS-IS inter area, * - candidate default, U - per-user static route
       o - ODR, P - periodic downloaded static route, H - NHRP, l - LISP
       a - application route
       + - replicated route, % - next hop override, p - overrides from PfR

Gateway of last resort is not set

      10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks
C        10.0.0.0/24 is directly connected, GigabitEthernet1
L        10.0.0.15/32 is directly connected, GigabitEthernet1"""

RAW_RESULT = "\n".join([IOSXE_SHOW_VERSION, IOSXE_SHOW_IP_ROUTE])

TEST_SCRAPLI_RESPONSE_ONE = Response(
    host="sea-ios-1",
    channel_input="show version",
    textfsm_platform="cisco_iosxe",
    genie_platform="iosxe",
)
TEST_SCRAPLI_RESPONSE_ONE.record_response(result=IOSXE_SHOW_VERSION.encode())
TEST_SCRAPLI_RESPONSE_TWO = Response(
    host="sea-ios-1",
    channel_input="show ip route",
    textfsm_platform="cisco_iosxe",
    genie_platform="iosxe",
)
TEST_SCRAPLI_RESPONSE_TWO.record_response(result=IOSXE_SHOW_IP_ROUTE.encode())
TEST_SCRAPLI_RESPONSE = [TEST_SCRAPLI_RESPONSE_ONE, TEST_SCRAPLI_RESPONSE_TWO]

TEST_HOST = Host(name="sea-ios-1")
TEST_AGG_RESULT = AggregatedResult("send_commands")
TEST_MULTI_RESULT = MultiResult("send_commands")
TEST_RESULT = Result(host=TEST_HOST, result=RAW_RESULT, name="send_commands")
setattr(TEST_RESULT, "scrapli_response", TEST_SCRAPLI_RESPONSE)

TEST_MULTI_RESULT.append(TEST_RESULT)

TEST_AGG_RESULT[TEST_HOST.name] = TEST_MULTI_RESULT


@pytest.mark.parametrize(
    "structured_result",
    [
        (
            True,
            "\x1b[1m\x1b[36msend_commands*******************************************************************\n\x1b[1m\x1b[34m* sea-ios-1 ** changed : False *************************************************\n\x1b[1m\x1b[32mvvvv send_commands ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO\n[ { 'config_register': '0x2102',\n    'hardware': ['CSR1000V'],\n    'hostname': 'csr1000v',\n    'mac': [],\n    'reload_reason': 'reload',\n    'rommon': 'IOS-XE',\n    'running_image': 'packages.conf',\n    'serial': ['9FKLJWM5EB0'],\n    'uptime': '2 hours, 43 minutes',\n    'version': '16.4.1'}]\n\x1b[1m\x1b[32m---- send_commands ** changed : False ------------------------------------------ INFO\n[ { 'distance': '',\n    'mask': '24',\n    'metric': '',\n    'network': '10.0.0.0',\n    'nexthop_if': 'GigabitEthernet1',\n    'nexthop_ip': '',\n    'protocol': 'C',\n    'type': '',\n    'uptime': ''},\n  { 'distance': '',\n    'mask': '32',\n    'metric': '',\n    'network': '10.0.0.15',\n    'nexthop_if': 'GigabitEthernet1',\n    'nexthop_ip': '',\n    'protocol': 'L',\n    'type': '',\n    'uptime': ''}]\n\x1b[1m\x1b[32m^^^^ END send_commands ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
        ),
        (
            False,
            "\x1b[1m\x1b[36msend_commands*******************************************************************\n\x1b[1m\x1b[34m* sea-ios-1 ** changed : False *************************************************\n\x1b[1m\x1b[32mvvvv send_commands ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO\n[ [ '16.4.1',\n    'IOS-XE',\n    'csr1000v',\n    '2 hours, 43 minutes',\n    'reload',\n    'packages.conf',\n    ['CSR1000V'],\n    ['9FKLJWM5EB0'],\n    '0x2102',\n    []]]\n\x1b[1m\x1b[32m---- send_commands ** changed : False ------------------------------------------ INFO\n[ ['C', '', '10.0.0.0', '24', '', '', '', 'GigabitEthernet1', ''],\n  ['L', '', '10.0.0.15', '32', '', '', '', 'GigabitEthernet1', '']]\n\x1b[1m\x1b[32m^^^^ END send_commands ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
        ),
    ],
    ids=["True", "False"],
)
def test_print_structured_result(capsys, structured_result):
    print_structured_result(TEST_AGG_RESULT, to_dict=structured_result[0])
    captured = capsys.readouterr()
    assert captured.out == structured_result[1]


@pytest.mark.parametrize(
    "structured_result",
    [
        (
            True,
            "\x1b[1m\x1b[36msend_commands*******************************************************************\n\x1b[1m\x1b[34m* sea-ios-1 ** changed : False *************************************************\n\x1b[1m\x1b[32mvvvv send_commands ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO\n{ 'version': { 'chassis': 'CSR1000V',\n               'chassis_sn': '9FKLJWM5EB0',\n               'compiled_by': 'mcpre',\n               'compiled_date': 'Sun 27-Nov-16 13:02',\n               'curr_config_register': '0x2102',\n               'disks': { 'bootflash:.': { 'disk_size': '7774207',\n                                           'type_of_disk': 'virtual hard disk'},\n                          'webui:.': {'disk_size': '0', 'type_of_disk': ''}},\n               'hostname': 'csr1000v',\n               'image_id': 'X86_64_LINUX_IOSD-UNIVERSALK9-M',\n               'image_type': 'production image',\n               'label': 'RELEASE SOFTWARE (fc2)',\n               'last_reload_reason': 'reload',\n               'license_level': 'ax',\n               'license_type': 'Default. No valid license found.',\n               'main_mem': '2052375',\n               'mem_size': { 'non-volatile configuration': '32768',\n                             'physical': '3985132'},\n               'next_reload_license_level': 'ax',\n               'number_of_intfs': {'Gigabit Ethernet': '10'},\n               'os': 'IOS-XE',\n               'platform': 'CSR1000V',\n               'processor_type': 'VXE',\n               'returned_to_rom_by': 'reload',\n               'rom': 'IOS-XE ROMMON',\n               'rtr_type': 'CSR1000V',\n               'system_image': 'bootflash:packages.conf',\n               'uptime': '2 hours, 43 minutes',\n               'uptime_this_cp': '2 hours, 45 minutes',\n               'version': '16.4.1',\n               'version_short': '16.4',\n               'xe_version': '16.04.01'}}\n\x1b[1m\x1b[32m---- send_commands ** changed : False ------------------------------------------ INFO\n{ 'vrf': { 'default': { 'address_family': { 'ipv4': { 'routes': { '10.0.0.0/24': { 'active': True,\n                                                                                   'next_hop': { 'outgoing_interface': { 'GigabitEthernet1': { 'outgoing_interface': 'GigabitEthernet1'}}},\n                                                                                   'route': '10.0.0.0/24',\n                                                                                   'source_protocol': 'connected',\n                                                                                   'source_protocol_codes': 'C'},\n                                                                  '10.0.0.15/32': { 'active': True,\n                                                                                    'next_hop': { 'outgoing_interface': { 'GigabitEthernet1': { 'outgoing_interface': 'GigabitEthernet1'}}},\n                                                                                    'route': '10.0.0.15/32',\n                                                                                    'source_protocol': 'local',\n                                                                                    'source_protocol_codes': 'L'}}}}}}}\n\x1b[1m\x1b[32m^^^^ END send_commands ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
        ),
        (
            False,
            "\x1b[1m\x1b[36msend_commands*******************************************************************\n\x1b[1m\x1b[34m* sea-ios-1 ** changed : False *************************************************\n\x1b[1m\x1b[32mvvvv send_commands ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO\n{ 'version': { 'chassis': 'CSR1000V',\n               'chassis_sn': '9FKLJWM5EB0',\n               'compiled_by': 'mcpre',\n               'compiled_date': 'Sun 27-Nov-16 13:02',\n               'curr_config_register': '0x2102',\n               'disks': { 'bootflash:.': { 'disk_size': '7774207',\n                                           'type_of_disk': 'virtual hard disk'},\n                          'webui:.': {'disk_size': '0', 'type_of_disk': ''}},\n               'hostname': 'csr1000v',\n               'image_id': 'X86_64_LINUX_IOSD-UNIVERSALK9-M',\n               'image_type': 'production image',\n               'label': 'RELEASE SOFTWARE (fc2)',\n               'last_reload_reason': 'reload',\n               'license_level': 'ax',\n               'license_type': 'Default. No valid license found.',\n               'main_mem': '2052375',\n               'mem_size': { 'non-volatile configuration': '32768',\n                             'physical': '3985132'},\n               'next_reload_license_level': 'ax',\n               'number_of_intfs': {'Gigabit Ethernet': '10'},\n               'os': 'IOS-XE',\n               'platform': 'CSR1000V',\n               'processor_type': 'VXE',\n               'returned_to_rom_by': 'reload',\n               'rom': 'IOS-XE ROMMON',\n               'rtr_type': 'CSR1000V',\n               'system_image': 'bootflash:packages.conf',\n               'uptime': '2 hours, 43 minutes',\n               'uptime_this_cp': '2 hours, 45 minutes',\n               'version': '16.4.1',\n               'version_short': '16.4',\n               'xe_version': '16.04.01'}}\n\x1b[1m\x1b[32m---- send_commands ** changed : False ------------------------------------------ INFO\n{ 'vrf': { 'default': { 'address_family': { 'ipv4': { 'routes': { '10.0.0.0/24': { 'active': True,\n                                                                                   'next_hop': { 'outgoing_interface': { 'GigabitEthernet1': { 'outgoing_interface': 'GigabitEthernet1'}}},\n                                                                                   'route': '10.0.0.0/24',\n                                                                                   'source_protocol': 'connected',\n                                                                                   'source_protocol_codes': 'C'},\n                                                                  '10.0.0.15/32': { 'active': True,\n                                                                                    'next_hop': { 'outgoing_interface': { 'GigabitEthernet1': { 'outgoing_interface': 'GigabitEthernet1'}}},\n                                                                                    'route': '10.0.0.15/32',\n                                                                                    'source_protocol': 'local',\n                                                                                    'source_protocol_codes': 'L'}}}}}}}\n\x1b[1m\x1b[32m^^^^ END send_commands ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
        ),
    ],
    ids=["True", "False"],
)
def test_print_structured_result_genie(capsys, structured_result):
    print_structured_result(TEST_AGG_RESULT, parser="genie")
    captured = capsys.readouterr()
    assert captured.out == structured_result[1]


@pytest.mark.parametrize(
    "structured_result",
    [
        (
            True,
            "\x1b[1m\x1b[36msend_commands*******************************************************************\n\x1b[1m\x1b[34m* sea-ios-1 ** changed : False *************************************************\n\x1b[1m\x1b[32mvvvv send_commands ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO\n{ 'version': { 'chassis': 'CSR1000V',\n               'chassis_sn': '9FKLJWM5EB0',\n               'compiled_by': 'mcpre',\n               'compiled_date': 'Sun 27-Nov-16 13:02',\n               'curr_config_register': '0x2102',\n               'disks': { 'bootflash:.': { 'disk_size': '7774207',\n                                           'type_of_disk': 'virtual hard disk'},\n                          'webui:.': {'disk_size': '0', 'type_of_disk': ''}},\n               'hostname': 'csr1000v',\n               'image_id': 'X86_64_LINUX_IOSD-UNIVERSALK9-M',\n               'image_type': 'production image',\n               'label': 'RELEASE SOFTWARE (fc2)',\n               'last_reload_reason': 'reload',\n               'license_level': 'ax',\n               'license_type': 'Default. No valid license found.',\n               'main_mem': '2052375',\n               'mem_size': { 'non-volatile configuration': '32768',\n                             'physical': '3985132'},\n               'next_reload_license_level': 'ax',\n               'number_of_intfs': {'Gigabit Ethernet': '10'},\n               'os': 'IOS-XE',\n               'platform': 'CSR1000V',\n               'processor_type': 'VXE',\n               'returned_to_rom_by': 'reload',\n               'rom': 'IOS-XE ROMMON',\n               'rtr_type': 'CSR1000V',\n               'system_image': 'bootflash:packages.conf',\n               'uptime': '2 hours, 43 minutes',\n               'uptime_this_cp': '2 hours, 45 minutes',\n               'version': '16.4.1',\n               'version_short': '16.4',\n               'xe_version': '16.04.01'}}\n\x1b[1m\x1b[32m---- send_commands ** changed : False ------------------------------------------ INFO\n{ 'vrf': { 'default': { 'address_family': { 'ipv4': { 'routes': { '10.0.0.0/24': { 'active': True,\n                                                                                   'next_hop': { 'outgoing_interface': { 'GigabitEthernet1': { 'outgoing_interface': 'GigabitEthernet1'}}},\n                                                                                   'route': '10.0.0.0/24',\n                                                                                   'source_protocol': 'connected',\n                                                                                   'source_protocol_codes': 'C'},\n                                                                  '10.0.0.15/32': { 'active': True,\n                                                                                    'next_hop': { 'outgoing_interface': { 'GigabitEthernet1': { 'outgoing_interface': 'GigabitEthernet1'}}},\n                                                                                    'route': '10.0.0.15/32',\n                                                                                    'source_protocol': 'local',\n                                                                                    'source_protocol_codes': 'L'}}}}}}}\n\x1b[1m\x1b[32m^^^^ END send_commands ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
        ),
        (
            False,
            "\x1b[1m\x1b[36msend_commands*******************************************************************\n\x1b[1m\x1b[34m* sea-ios-1 ** changed : False *************************************************\n\x1b[1m\x1b[32mvvvv send_commands ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO\n{ 'version': { 'chassis': 'CSR1000V',\n               'chassis_sn': '9FKLJWM5EB0',\n               'compiled_by': 'mcpre',\n               'compiled_date': 'Sun 27-Nov-16 13:02',\n               'curr_config_register': '0x2102',\n               'disks': { 'bootflash:.': { 'disk_size': '7774207',\n                                           'type_of_disk': 'virtual hard disk'},\n                          'webui:.': {'disk_size': '0', 'type_of_disk': ''}},\n               'hostname': 'csr1000v',\n               'image_id': 'X86_64_LINUX_IOSD-UNIVERSALK9-M',\n               'image_type': 'production image',\n               'label': 'RELEASE SOFTWARE (fc2)',\n               'last_reload_reason': 'reload',\n               'license_level': 'ax',\n               'license_type': 'Default. No valid license found.',\n               'main_mem': '2052375',\n               'mem_size': { 'non-volatile configuration': '32768',\n                             'physical': '3985132'},\n               'next_reload_license_level': 'ax',\n               'number_of_intfs': {'Gigabit Ethernet': '10'},\n               'os': 'IOS-XE',\n               'platform': 'CSR1000V',\n               'processor_type': 'VXE',\n               'returned_to_rom_by': 'reload',\n               'rom': 'IOS-XE ROMMON',\n               'rtr_type': 'CSR1000V',\n               'system_image': 'bootflash:packages.conf',\n               'uptime': '2 hours, 43 minutes',\n               'uptime_this_cp': '2 hours, 45 minutes',\n               'version': '16.4.1',\n               'version_short': '16.4',\n               'xe_version': '16.04.01'}}\n\x1b[1m\x1b[32m---- send_commands ** changed : False ------------------------------------------ INFO\n{ 'vrf': { 'default': { 'address_family': { 'ipv4': { 'routes': { '10.0.0.0/24': { 'active': True,\n                                                                                   'next_hop': { 'outgoing_interface': { 'GigabitEthernet1': { 'outgoing_interface': 'GigabitEthernet1'}}},\n                                                                                   'route': '10.0.0.0/24',\n                                                                                   'source_protocol': 'connected',\n                                                                                   'source_protocol_codes': 'C'},\n                                                                  '10.0.0.15/32': { 'active': True,\n                                                                                    'next_hop': { 'outgoing_interface': { 'GigabitEthernet1': { 'outgoing_interface': 'GigabitEthernet1'}}},\n                                                                                    'route': '10.0.0.15/32',\n                                                                                    'source_protocol': 'local',\n                                                                                    'source_protocol_codes': 'L'}}}}}}}\n\x1b[1m\x1b[32m^^^^ END send_commands ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
        ),
    ],
    ids=["True", "False"],
)
def test_print_structured_result_genie_to_dict(capsys, structured_result):
    print_structured_result(TEST_AGG_RESULT, parser="genie")
    captured = capsys.readouterr()
    assert captured.out == structured_result[1]


def test_print_structured_result_fallback(capsys):
    test_agg_result_fail_to_string = TEST_AGG_RESULT
    test_agg_result_fail_to_string["sea-ios-1"][0].scrapli_response[0].textfsm_platform = "nope"
    print_structured_result(test_agg_result_fail_to_string, fail_to_string=True)
    captured = capsys.readouterr()
    assert (
        captured.out
        == """\x1b[1m\x1b[36msend_commands*******************************************************************\n\x1b[1m\x1b[34m* sea-ios-1 ** changed : False *************************************************\n\x1b[1m\x1b[32mvvvv send_commands ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO\nCisco IOS XE Software, Version 16.04.01\nCisco IOS Software [Everest], CSR1000V Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.4.1, RELEASE SOFTWARE (fc2)\nTechnical Support: http://www.cisco.com/techsupport\nCopyright (c) 1986-2016 by Cisco Systems, Inc.\nCompiled Sun 27-Nov-16 13:02 by mcpre\n\n\nCisco IOS-XE software, Copyright (c) 2005-2016 by cisco Systems, Inc.\nAll rights reserved.  Certain components of Cisco IOS-XE software are\nlicensed under the GNU General Public License ("GPL") Version 2.0.  The\nsoftware code licensed under GPL Version 2.0 is free software that comes\nwith ABSOLUTELY NO WARRANTY.  You can redistribute and/or modify such\nGPL code under the terms of GPL Version 2.0.  For more details, see the\ndocumentation or "License Notice" file accompanying the IOS-XE software,\nor the applicable URL provided on the flyer accompanying the IOS-XE\nsoftware.\n\n\nROM: IOS-XE ROMMON\n\ncsr1000v uptime is 2 hours, 43 minutes\nUptime for this control processor is 2 hours, 45 minutes\nSystem returned to ROM by reload\nSystem image file is "bootflash:packages.conf"\nLast reload reason: reload\n\n\n\nThis product contains cryptographic features and is subject to United\nStates and local country laws governing import, export, transfer and\nuse. Delivery of Cisco cryptographic products does not imply\nthird-party authority to import, export, distribute or use encryption.\nImporters, exporters, distributors and users are responsible for\ncompliance with U.S. and local country laws. By using this product you\nagree to comply with applicable laws and regulations. If you are unable\nto comply with U.S. and local laws, return this product immediately.\n\nA summary of U.S. laws governing Cisco cryptographic products may be found at:\nhttp://www.cisco.com/wwl/export/crypto/tool/stqrg.html\n\nIf you require further assistance please contact us by sending email to\nexport@cisco.com.\n\nLicense Level: ax\nLicense Type: Default. No valid license found.\nNext reload license Level: ax\n\ncisco CSR1000V (VXE) processor (revision VXE) with 2052375K/3075K bytes of memory.\nProcessor board ID 9FKLJWM5EB0\n10 Gigabit Ethernet interfaces\n32768K bytes of non-volatile configuration memory.\n3985132K bytes of physical memory.\n7774207K bytes of virtual hard disk at bootflash:.\n0K bytes of  at webui:.\n\nConfiguration register is 0x2102\n\ncsr1000v#\n\x1b[1m\x1b[32m---- send_commands ** changed : False ------------------------------------------ INFO\n[ { \'distance\': \'\',\n    \'mask\': \'24\',\n    \'metric\': \'\',\n    \'network\': \'10.0.0.0\',\n    \'nexthop_if\': \'GigabitEthernet1\',\n    \'nexthop_ip\': \'\',\n    \'protocol\': \'C\',\n    \'type\': \'\',\n    \'uptime\': \'\'},\n  { \'distance\': \'\',\n    \'mask\': \'32\',\n    \'metric\': \'\',\n    \'network\': \'10.0.0.15\',\n    \'nexthop_if\': \'GigabitEthernet1\',\n    \'nexthop_ip\': \'\',\n    \'protocol\': \'L\',\n    \'type\': \'\',\n    \'uptime\': \'\'}]\n\x1b[1m\x1b[32m^^^^ END send_commands ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"""
    )


def test_print_structured_result_non_scrapli(capsys):
    test_agg_result_fail_to_string = TEST_AGG_RESULT
    del test_agg_result_fail_to_string["sea-ios-1"][0].scrapli_response
    print_structured_result(TEST_AGG_RESULT, fail_to_string=True)
    captured = capsys.readouterr()
    assert (
        captured.out
        == """\x1b[1m\x1b[36msend_commands*******************************************************************\n\x1b[1m\x1b[34m* sea-ios-1 ** changed : False *************************************************\n\x1b[1m\x1b[32mvvvv send_commands ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO\nCisco IOS XE Software, Version 16.04.01\nCisco IOS Software [Everest], CSR1000V Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.4.1, RELEASE SOFTWARE (fc2)\nTechnical Support: http://www.cisco.com/techsupport\nCopyright (c) 1986-2016 by Cisco Systems, Inc.\nCompiled Sun 27-Nov-16 13:02 by mcpre\n\n\nCisco IOS-XE software, Copyright (c) 2005-2016 by cisco Systems, Inc.\nAll rights reserved.  Certain components of Cisco IOS-XE software are\nlicensed under the GNU General Public License ("GPL") Version 2.0.  The\nsoftware code licensed under GPL Version 2.0 is free software that comes\nwith ABSOLUTELY NO WARRANTY.  You can redistribute and/or modify such\nGPL code under the terms of GPL Version 2.0.  For more details, see the\ndocumentation or "License Notice" file accompanying the IOS-XE software,\nor the applicable URL provided on the flyer accompanying the IOS-XE\nsoftware.\n\n\nROM: IOS-XE ROMMON\n\ncsr1000v uptime is 2 hours, 43 minutes\nUptime for this control processor is 2 hours, 45 minutes\nSystem returned to ROM by reload\nSystem image file is "bootflash:packages.conf"\nLast reload reason: reload\n\n\n\nThis product contains cryptographic features and is subject to United\nStates and local country laws governing import, export, transfer and\nuse. Delivery of Cisco cryptographic products does not imply\nthird-party authority to import, export, distribute or use encryption.\nImporters, exporters, distributors and users are responsible for\ncompliance with U.S. and local country laws. By using this product you\nagree to comply with applicable laws and regulations. If you are unable\nto comply with U.S. and local laws, return this product immediately.\n\nA summary of U.S. laws governing Cisco cryptographic products may be found at:\nhttp://www.cisco.com/wwl/export/crypto/tool/stqrg.html\n\nIf you require further assistance please contact us by sending email to\nexport@cisco.com.\n\nLicense Level: ax\nLicense Type: Default. No valid license found.\nNext reload license Level: ax\n\ncisco CSR1000V (VXE) processor (revision VXE) with 2052375K/3075K bytes of memory.\nProcessor board ID 9FKLJWM5EB0\n10 Gigabit Ethernet interfaces\n32768K bytes of non-volatile configuration memory.\n3985132K bytes of physical memory.\n7774207K bytes of virtual hard disk at bootflash:.\n0K bytes of  at webui:.\n\nConfiguration register is 0x2102\n\ncsr1000v#\nCodes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP\n       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area\n       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2\n       E1 - OSPF external type 1, E2 - OSPF external type 2\n       i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2\n       ia - IS-IS inter area, * - candidate default, U - per-user static route\n       o - ODR, P - periodic downloaded static route, H - NHRP, l - LISP\n       a - application route\n       + - replicated route, % - next hop override, p - overrides from PfR\n\nGateway of last resort is not set\n\n      10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks\nC        10.0.0.0/24 is directly connected, GigabitEthernet1\nL        10.0.0.15/32 is directly connected, GigabitEthernet1\n\x1b[1m\x1b[32m^^^^ END send_commands ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"""
    )

from nornir_utils.plugins.functions.print_result import print_result

from nornir import InitNornir
from nornir_scrapli.tasks import (
    netconf_capabilities,
    netconf_edit_config,
    netconf_get,
    netconf_get_config,
    netconf_lock,
    netconf_rpc,
    netconf_unlock,
)


def main() -> None:
    nr = InitNornir(config_file="nornir_data/config.yaml")

    capabilities_result = nr.run(task=netconf_capabilities)
    print_result(capabilities_result)

    config_result = nr.run(task=netconf_get_config)
    print_result(config_result)

    filter_ = """<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
      <interface>
        <name>
          GigabitEthernet1
        </name>
      </interface>
    </interfaces>"""
    result = nr.run(task=netconf_get, filter_=filter_)
    print_result(result)

    print("edit-config", "*" * 50)
    config = """<config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>GigabitEthernet1</name>
                <description>scrapli was here!</description>
            </interface>
        </interfaces>
    </config>"""
    result = nr.run(task=netconf_edit_config, config=config)
    print_result(result)

    result = nr.run(task=netconf_lock, target="running")
    print_result(result)

    result = nr.run(task=netconf_unlock, target="running")
    print_result(result)

    rpc = """<get><filter type="subtree"><interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
      <interface>
        <name>
          GigabitEthernet1
        </name>
      </interface>
    </interfaces></filter></get>"""
    result = nr.run(task=netconf_rpc, filter_=rpc)
    print_result(result)

    # checking out the result object you can see the original scrapli response object as well
    print(dir(result["iosxe1"][0]))
    print(type(result["iosxe1"][0].scrapli_response))
    print(dir(result["iosxe1"][0].scrapli_response))
    print(result["iosxe1"][0].scrapli_response.elapsed_time)
    print(result["iosxe1"][0].scrapli_response.xml_result)


if __name__ == "__main__":
    main()

import re

from nornir_scrapli.helper import diff_xml_text


def strip_ansi(buf: bytes) -> bytes:
    """
    Strip ansi characters from output

    Args:
        buf: bytes from previous reads if needed

    Returns:
        bytes: bytes output read from channel with ansi characters removed

    Raises:
        N/A

    """
    ansi_escape_pattern = re.compile(rb"\x1b(\[.*?[@-~]|\].*?(\x07|\x1b\\))")
    buf = re.sub(pattern=ansi_escape_pattern, repl=b"", string=buf)
    return buf


def test_diff_xml_text():
    xml_one = """<data>
    <ssh>
        <server>
            <v2/>
            <netconf-vrf-table>
                <vrf>
                    <vrf-name>default</vrf-name>
                    <blah>someblah</blah>
                    <enable/>
                </vrf>
            </netconf-vrf-table>
        </server>
    </ssh>    
    <netconf-yang>
        <agent>
            <ssh>
                <enable/>
            </ssh>
        </agent>
    </netconf-yang>
</data>"""
    xml_two = """<data>
    <ssh>
        <server>
            <v2/>
            <netconf-vrf-table>
                <vrf>
                    <vrf-name>default</vrf-name>
                    <enable/>
                </vrf>
            </netconf-vrf-table>
        </server>
    </ssh>    
    <netconf-yang>
        <agent>
            <ssh>
                <disable/>
            </ssh>
        </agent>
    </netconf-yang>
</data>"""
    expected_diff = """@@ -5,7 +5,6 @@

             <netconf-vrf-table>
                 <vrf>
                     <vrf-name>default</vrf-name>
-                    <blah>someblah</blah>
                     <enable/>
                 </vrf>
             </netconf-vrf-table>
@@ -14,7 +13,7 @@

     <netconf-yang>
         <agent>
             <ssh>
-                <enable/>
+                <disable/>
             </ssh>
         </agent>
     </netconf-yang>"""
    actual_diff = diff_xml_text(document_one=xml_one, document_two=xml_two)
    assert strip_ansi(actual_diff.encode()).decode() == expected_diff

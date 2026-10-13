"""Stable values for the fake lab and its assertions."""

PLATFORMS = ("cisco_iosxe", "cisco_nxos", "cisco_iosxr", "arista_eos", "juniper_junos")
SUPPORTED_PLATFORMS = PLATFORMS
KNOWN_GAPS = {}
HEALTHY_REPLICAS = 2
USERNAME = "functional"
PASSWORD = "functional-password"
REJECTED_LOGIN_PASSWORD = "different-server-password"
SHOW_VERSION_COMMAND = "show version"
SECOND_COMMAND = "show clock"
CONFIG_LINES = ("interface Loopback0", "description functional-test")
INTERACTIVE_COMMAND = "clear logging"
INTERACTIVE_CONFIRMATION = "Clear logging buffer [confirm]"
INTERACTIVE_RESPONSE = "y"
AUTH_FAILURE_HOST = "cisco-iosxe-auth-failure"
TIMEOUT_FAILURE_HOST = "cisco-iosxe-timeout"
TIMEOUT_OPS = 2.0
SLOW_RESPONSE_DELAY = 4.0


def expected_version_output(hostname: str) -> str:
    return f"FakeNOS version for {hostname}"


def expected_clock_output(hostname: str) -> str:
    return f"{hostname} 00:00:00 UTC"


def expected_default_prompt(hostname: str, platform: str) -> str:
    return hostname + (">" if platform == "juniper_junos" else "#")


def expected_config_prompt(hostname: str, platform: str) -> str:
    return hostname + ("#" if platform == "juniper_junos" else "(config)#")

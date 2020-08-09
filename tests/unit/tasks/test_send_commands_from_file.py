from pathlib import Path

import nornir_scrapli
from scrapli.driver.core import IOSXEDriver
from scrapli.response import Response

COMMANDS_FILE = f"{Path(nornir_scrapli.__file__).parents[1]}/tests/files/send_commands_from_file"


def test_send_commands_from_file(nornir, monkeypatch):
    from nornir_scrapli.tasks import send_commands_from_file

    def mock_open(cls):
        pass

    def mock_send_commands_from_file(
        cls, file, strip_prompt, failed_when_contains="", stop_on_failed=False, privilege_level="",
    ):
        with open(file, "r") as f:
            commands = f.read().splitlines()
        response = Response(host="fake_as_heck", channel_input=commands[0])
        response._record_response(b"some stuff about whatever")
        return [response]

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "send_commands_from_file", mock_send_commands_from_file)

    result = nornir.run(task=send_commands_from_file, file=COMMANDS_FILE,)
    assert result["sea-ios-1"][0].result == "some stuff about whatever"
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is False

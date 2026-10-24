# Functional tests

Run from the repository root on Linux with uv and an OpenSSH client available:

```bash
make test_functional
# Equivalent locked Python 3.13 session:
uv run --locked --only-group nox nox -s functional_tests
# A focused path and pytest filter:
uv run --locked --only-group nox nox -s functional_tests -- tests/functional/test_core_tasks.py -k test_send_command
```

Arguments after `--` replace the default `tests/functional` selection. Include
`tests/functional` or a path/node ID within it when adding options such as `-k` or
`-v`; options alone let pytest collect the whole repository. To check fixture
isolation across both suites, use `-- tests/unit tests/functional`.

## Native v2 coverage

The suite starts FakeNOS SSH servers on dynamically allocated loopback ports and
exercises the real Nornir connection plugin, libscrapli bin transport, built-in v2
platform definitions, and all nine public CLI tasks. There are two healthy hosts for
each of `cisco_iosxe`, `cisco_nxos`, `cisco_iosxr`, `arista_eos`, and `juniper_junos`,
plus rejected-login and slow-response hosts. The suite has **86 cases**, with no
xfails or skipped platforms:

- Command, batch/file, configuration, prompt, interactive and prompted-input tasks.
- Native `scrapli.cli_result.Result` inputs/outputs, failure status, and preserved
  Nornir result string formatting.
- All three CLI configuration dry runs: configuration mode is entered and the
  original mode restored without sending configuration, verified from SSH recordings.
- Nondefault unprivileged exec restoration on IOS XE, NX-OS and EOS.
- Consecutive identical password prompts and hidden response redaction.
- Built-in definition failure indicators and batches that stop/continue after failure.
- Concurrent host-output isolation and authentication/timeout failure isolation.

FakeNOS simulates the v2 enable password challenge and abbreviated `term width` /
`term len` initialization commands. Inventory extras use native `auth`, `session`,
and `transport` sections. Bin key checking is explicitly disabled only for these
ephemeral loopback servers; SSH configuration and known-hosts paths are `/dev/null`.
Timeouts are expressed in nanoseconds.

These are simulated CLI exchanges, not validation against real network operating
systems. Tests need no real devices, service containers, external credentials, or SSH
configuration. Credentials and hidden-response values are test-local constants.
Package installation requires the locked dependencies. Other runtime platforms,
Python versions, NETCONF and configuration-management tasks remain outside this
functional suite's scope.

## Results and lifecycle

Applied configuration tasks leave connections in configuration mode:
`{host}(config)#` on Cisco/Arista and `{host}#` on Junos (whose exec prompt is
`{host}>`). Dry runs return to the actual starting mode. Interactive callbacks retain
the FakeNOS wire's CRLF text; command/config operations use native cleaned outputs.

scrapli v2 reports these simulated rejected-login and timeout operations as
`OperationException`; tests distinguish `permission denied` and `TimeoutExceeded`
diagnostics. The following Nornir task skips failed hosts and continues on healthy
hosts, recording the behavior relevant to
[#143](https://github.com/scrapli/nornir_scrapli/issues/143).

The fixture observes construction and native allocation release through a small `Cli`
subclass. It does not replace native network or task methods. This avoids treating
the native pointer as a liveness flag: scrapli 2026.10.8 does not clear that pointer
when it frees the allocation. Healthy connections must be released by normal Nornir
close before the fixture's rescue path runs; failed/orphaned connections are force
closed. Lab listeners, worker threads and sockets must also terminate.

Per-test native SSH recordings are written beneath pytest's temporary directory,
one file per port. They intentionally include FakeNOS's echoed test-only credentials;
returned hidden task results must be redacted. Do not treat recording files as evidence
that native log/recording redaction works for real credentials.

Unit and Genie sessions target `tests/unit`; functional tests target
`tests/functional` by default. Bare nox still selects only `unit_tests-3.13`, `ruff`,
and `mypy`. Functional tests gate commit CI and both publish workflows.

## Verification evidence

After rebasing the v2 migration onto `dga/chore-testing-zcw51` at `054297c`, the full
locked functional session passed **86 cases in 147.50 seconds** on Linux,
Python 3.13.14, scrapli 2026.10.8 and FakeNOS 1.2.1. The prior 43-case v1 stability
runs on the testing branch do not establish v2 stability or real-device behavior.

The combined unit/functional selection also passed **207 tests with one optional
Genie skip in 148.42 seconds**, verifying that the relocated unit fixtures do not
leak into the functional suite. Locked Ruff, strict mypy, strict documentation build
and minimum-version unit checks passed after the rebase.

The v2 branch still needs real-device validation before release, including custom
mode patterns, native logs/recordings and NETCONF operations. Local simulator timing
does not establish GitHub job timing or an unchanged 20-run stability criterion.

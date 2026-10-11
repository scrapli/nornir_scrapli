# Plan: functional tests against FakeNOS fake devices

Tracking issue: [#172](https://github.com/scrapli/nornir_scrapli/issues/172)

## Summary

Release maintainers cannot verify that a `nornir_scrapli` release still connects to devices and runs its tasks. Every test in `tests/unit/` uses `monkeypatch` to replace scrapli driver methods, so CI never opens an SSH session. This matters now because the plugin must move to scrapli 2026.10.03 ([#157](https://github.com/scrapli/nornir_scrapli/issues/157), [#158](https://github.com/scrapli/nornir_scrapli/issues/158)).

The plan adds a separate functional test session that:

- starts fake SSH devices with [FakeNOS](https://github.com/fakenos/fakenos)
- runs the 8 core `scrapli` tasks against them through Nornir
- runs in `commit.yaml`, in the weekly `pre_release.yaml` job and in `publish.yaml`, where a failure stops the publish

Not decided yet:

- which of the five core platforms FakeNOS can imitate well enough (step 1 answers this)
- whether the fake devices can produce a rejected login and a command that does not answer in time (step 1 answers this)

## Scope agreed in the idea brief

### In scope

- The core `scrapli` connection plugin and its 8 tasks: `send_command`, `send_commands`, `send_commands_from_file`, `send_config`, `send_configs`, `send_configs_from_file`, `send_interactive`, `get_prompt`.
- The five scrapli core platforms: `cisco_iosxe`, `cisco_nxos`, `cisco_iosxr`, `arista_eos`, `juniper_junos`. A platform that FakeNOS cannot imitate is recorded as a known gap and does not block the work.
- Running tasks on many hosts at the same time, including one host that fails.
- One Python version (3.13) on Linux.

### Out of scope

- The `scrapli_cfg` and `scrapli_netconf` connection plugins.
- The `generic` platform and the `scrapli_community` platforms.
- Other Python versions and macOS.
- Tests against real network operating system images, for example containerlab with Arista cEOS or Nokia SR Linux.
- Running the unit tests in `publish.yaml`.
- Deciding the correct behavior for the [#143](https://github.com/scrapli/nornir_scrapli/issues/143) scenario. The tests record today's behavior only.

### Requirements

| ID | Requirement |
|---|---|
| FR-001 | The session runs all 8 core tasks against fake devices. |
| FR-002 | The session covers the five core platforms, as far as FakeNOS can imitate them. |
| FR-003 | Tasks run on at least two fake hosts per platform, with more than one Nornir worker. Each host's result contains only that host's output. |
| FR-004 | When one fake host fails (login rejected, or no answer in time), only that host is marked as failed. |
| FR-005 | The session records what happens on the next task after a host failed (the #143 scenario). |
| FR-006 | `commit.yaml` runs the session on every push and pull request. |
| FR-007 | `pre_release.yaml` runs the session after `uv lock --upgrade`. |
| FR-008 | `publish.yaml` runs the session before `uv publish` and stops the publish if it fails. |

### Success criteria

- SC-001: the session finishes in under 5 minutes on a standard GitHub Actions Linux runner.
- SC-002: the session passes 20 runs in a row on `main` with no code change.
- SC-003: a deliberate break makes the session fail, for example a connection that never opens, or a task that sends the wrong command.
- SC-004: the session needs nothing outside the test job: no real devices, no container images and no credentials.

## What is known about FakeNOS today

These findings come from reading the FakeNOS 1.2.1 and SIMNOS 2.4.0 packages downloaded from PyPI, and the scrapli 2026.2.20 drivers installed from `uv.lock`.

### Package versions and Python support

- [FakeNOS 1.2.1](https://pypi.org/project/fakenos/) was released on 2026-08-15. It requires Python 3.11 to 3.14 and depends on `paramiko<=4.0`, `pyyaml`, `pydantic`, `jinja2` and `detect`.
- [SIMNOS 2.4.0](https://pypi.org/project/simnos/), a fork of FakeNOS, was released on 2026-06-10. It requires Python 3.13 or 3.14 and `paramiko>=4.0,<6.0`.
- `nornir_scrapli` declares `requires-python = ">=3.10"`. `uv lock` resolves every dependency group for every supported Python version. The new dependency therefore needs a `python_version >= '3.11'` condition (FakeNOS) or `python_version >= '3.13'` condition (SIMNOS).

### How FakeNOS behaves

- Each host can have its own username, password and port. `replicas` starts several identical hosts on consecutive ports.
- The shell answers a command only when the command text matches a defined command exactly and the current prompt matches the command's `prompt` field. Any other input returns the `_default_` output, which is `Unknown command`.
- A command can change the current prompt through `new_prompt`. This is how a definition moves between exec, privileged exec and configuration mode.
- A command's output can be a Python function. FakeNOS calls it with the host's `base_prompt` (the host name by default), the current prompt and the command text. The function can return a new prompt along with the output.
- An empty line does nothing and only prints the prompt again.
- Custom platform definitions can be loaded from a `.yaml` or `.py` file.

### Gaps between the built-in definitions and scrapli's drivers

The built-in definitions for the five platforms were written for Netmiko. They have these gaps for scrapli:

- **No configuration mode commands on any of the five platforms.** None of them defines `configure terminal`, `end` or `disable` (or `configure` and `exit configuration-mode` for Junos). scrapli enters configuration mode with these commands before `send_config` and `send_configs`, so those tasks cannot work with the built-in definitions.
- **IOS XR starts at the wrong prompt.** FakeNOS starts IOS XR at `{host}>`. scrapli's IOS XR driver has no privilege level that ends in `>`. Its lowest level is `privilege_exec`, with a prompt ending in `#`.
- **Some terminal width commands are missing.** scrapli sends these commands when a session opens:

  | Platform | Commands scrapli sends | Defined in FakeNOS |
  |---|---|---|
  | `cisco_iosxe` | `terminal length 0`, `terminal width 512` | `terminal length 0` only. FakeNOS defines `terminal width 511`. |
  | `cisco_nxos` | `terminal length 0`, `terminal width 511` | Both |
  | `cisco_iosxr` | `terminal length 0`, `terminal width 512` | Both |
  | `arista_eos` | `terminal length 0`, `terminal width 32767` | `terminal length 0` only |
  | `juniper_junos` | `set cli screen-length 0`, `set cli screen-width 511`, `set cli complete-on-space off` | All three |

  A missing command returns `Unknown command` without a leading `%`. scrapli's failure strings all start with `%`, so a missing command does not fail the session. It is still better for the definitions to answer each command, so that a test does not depend on that detail.

- **The Junos prompts match scrapli's patterns.** FakeNOS uses `{host}>` and `{host}(config)#`. scrapli's Junos patterns accept both, because they allow parentheses in the host part of the prompt.

**Consequence:** the project needs its own five platform definitions. The built-in definitions are a starting point for command output, not something the tests can use as they are.

## Step 1: Test FakeNOS against scrapli outside the repository

**Goal:** answer the two open questions before anything goes into the repository.

**Where:** a script in a scratch directory, with a throwaway environment (`uv run --with fakenos --with scrapli==2026.2.20 ...`). Nothing is committed.

### Tasks

1. Write five minimal custom definitions, one per platform. Each definition contains:
   - the initial prompt and the prompts for each privilege level, matching scrapli's patterns (see the table under step 2)
   - the commands scrapli sends when a session opens
   - the commands that move between privilege levels
   - `show version`
   - one configuration line, for example `interface Loopback0`
   - one interactive sequence (see step 2)
2. Start FakeNOS with two hosts per platform and connect with scrapli's core driver for each platform, using the default `system` transport. Run `open`, `get_prompt`, `send_command`, `send_config` and `send_interactive`.
3. Start one host with a password that does not match the client's password. Check that scrapli raises an authentication error.
4. Start one host whose `show version` output function sleeps longer than the client's `timeout_ops`. Check that scrapli raises a timeout error for that host only.
5. Record whether OpenSSH (scrapli's `system` transport) and FakeNOS's paramiko SSH server agree on key exchange and host key algorithms. Record which SSH client options are needed (for example `auth_strict_key: false`, and an empty SSH config file).
6. Run steps 2 to 4 once with the built-in definitions, to confirm the gaps listed above.
7. Repeat a short version with SIMNOS, if FakeNOS fails on something SIMNOS might handle differently.

### Output

A comment on #172 that contains:

- a table with one row per platform: works with the built-in definition, works with a custom definition, known gaps
- the answer to open question 2 (rejected login and slow answer)
- the SSH client options needed
- the choice between FakeNOS and SIMNOS, with the reason. FakeNOS is the default, because it supports Python 3.11 and later and its last release is more recent.

### Exit condition

Step 2 starts when at least one platform works end to end. A platform that does not work becomes a known gap, as agreed in the idea brief.

## Step 2: Add the dependency, nox session and fake devices (first pull request)

### Dependency

In `pyproject.toml`, add a dependency group:

```toml
[dependency-groups]
functional = [
    {include-group = "test"},
    "fakenos>=1.2.1; python_version >= '3.11'",
]
```

Then run `uv lock` and commit the updated `uv.lock`. The `dev` group does not include `functional`, so `uv sync` for contributors does not change.

### nox session

In `noxfile.py`, add a session that reuses the existing `sync()` helper:

```python
@nox.session(python="3.13")
def functional_tests(session):
    """Run functional tests against fake devices."""
    sync(session, "functional")
    session.run("pytest", "tests/functional", *session.posargs)
```

- Do not add `functional_tests` to `nox.options.sessions`, so `nox` with no arguments behaves as it does today.
- In the `Makefile`, add a `test_functional` target that runs `$(NOX) -s functional_tests`, and add it to `.PHONY`.
- The `unit_tests` and `genie` sessions keep running `tests/unit` only. Check that they do not collect `tests/functional`.

### Layout

```
tests/functional/
├── __init__.py
├── conftest.py              # starts FakeNOS, builds the Nornir inventory
├── constants.py             # credentials, host counts, timeouts
├── nos/                     # platform definitions owned by the project
│   ├── cisco_iosxe.yaml
│   ├── cisco_nxos.yaml
│   ├── cisco_iosxr.yaml
│   ├── arista_eos.yaml
│   └── juniper_junos.yaml
├── files/                   # input for send_commands_from_file and send_configs_from_file
├── test_core_tasks.py
└── test_many_hosts.py
```

The definitions can be `.py` files instead of `.yaml` if output functions are needed (per-host output, slow answers). Step 1 decides which format works better.

### Platform definitions

Each definition must contain the prompts below and the commands scrapli sends. The prompt patterns come from scrapli 2026.2.20 (`scrapli/driver/core/<platform>/base_driver.py`).

| Platform | Initial prompt | Privileged exec prompt | Configuration prompt | Commands to enter and leave privileged exec | Commands to enter and leave configuration mode |
|---|---|---|---|---|---|
| `cisco_iosxe` | `{host}>` | `{host}#` | `{host}(config)#` | `enable`, `disable` | `configure terminal`, `end` |
| `cisco_nxos` | `{host}>` | `{host}#` | `{host}(config)#` | `enable`, `disable` | `configure terminal`, `end` |
| `cisco_iosxr` | `{host}#` | `{host}#` (same level) | `{host}(config)#` | none | `configure terminal`, `end` |
| `arista_eos` | `{host}>` | `{host}#` | `{host}(config)#` | `enable`, `disable` | `configure terminal`, `end` |
| `juniper_junos` | `{host}>` | none. scrapli uses `exec` as the default level. | `{host}#` | none | `configure`, `exit configuration-mode` |

Each definition must also contain:

- the commands scrapli sends when a session opens (see the table under "Gaps between the built-in definitions and scrapli's drivers")
- `show version`, whose output contains the host name, through an output function, so that FR-003 can check that each result belongs to its host
- the configuration lines used by the tests, for example `interface Loopback0` and `description functional-test`. They return an empty output and keep the configuration prompt.
- one interactive sequence. For example, `clear logging` prints `Clear logging buffer [confirm]` and changes the prompt to `[confirm]`, and then `y` returns to the privileged exec prompt.
- a slow command, for example `show slow`, whose output function sleeps longer than the client's `timeout_ops`. It is used only by the slow host.

Keep the definitions short. They imitate how a device behaves in a session, not its full command set.

### Fake devices fixture

In `tests/functional/conftest.py`:

- A session-scoped fixture starts one FakeNOS instance with:
  - two hosts per platform that works, using `replicas: 2`
  - one `cisco_iosxe` host whose password does not match the inventory password (login rejected)
  - one `cisco_iosxe` host that uses the slow command (no answer in time)
- Hosts listen on `127.0.0.1`. Ports come from a free port range picked at runtime, so parallel CI jobs and local runs do not collide.
- The fixture waits until every port accepts TCP connections before it yields, and stops FakeNOS when the session ends.

### Nornir inventory fixture

- A session-scoped fixture writes `hosts.yaml`, `groups.yaml` and `defaults.yaml` to a temporary directory and calls `InitNornir` with the `threaded` runner and `num_workers` set to the number of hosts.
- One group per platform sets `connection_options.scrapli.platform`, `port` and `extras`, in the same format as `tests/inventory_data/groups.yaml`. `extras` contains the SSH client options found in step 1, for example `auth_strict_key: false` and `ssh_config_file: false`.
- `timeout_ops` is set low (for example 5 seconds) in `defaults.yaml`, so the slow host fails quickly. This keeps the session under SC-001.
- A function-scoped fixture returns a filtered Nornir object for each test (healthy hosts only, or all hosts), and closes connections after the test with `nr.close_connections()`.

### Fixtures in `tests/conftest.py`

`tests/conftest.py` defines `autouse` fixtures that load the unit test inventory for every test. pytest also runs them for `tests/functional`. They are harmless but add work to every test. If they slow the session or interfere with it, move them to `tests/unit/conftest.py` in the same pull request.

### CI job in `commit.yaml`

Add a `functional` job to `.github/workflows/commit.yaml`, on `ubuntu-latest`, with the same `setup-uv` step as the other jobs:

```yaml
  functional:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: astral-sh/setup-uv@v10.1.0
        with:
          version: "0.12.1"
          python-version: "3.13"
          enable-cache: auto
      - run: uv run --locked --only-group nox nox -s functional_tests
```

The job must not use any secrets, so that it runs on pull requests from forks and from Dependabot (SC-004).

## Step 3: Write the tests (same pull request as step 2, or a second one if step 2 is large)

### `test_core_tasks.py` (FR-001, FR-002)

- One test per task, 8 in total, each run on the healthy hosts of every platform. Use `pytest.mark.parametrize` on the platform, so that a failing platform shows up by name.
- Each test checks:
  - the `AggregatedResult` has no failed host
  - each host's result contains the output its fake device returns for that command
  - for `send_config` and `send_configs`, the host is back at the privileged exec prompt afterwards (or the exec prompt on Junos)
- `send_commands_from_file` and `send_configs_from_file` read from `tests/functional/files/`.
- `send_interactive` uses the interactive sequence from the platform definition.
- A platform recorded as a known gap in step 1 is marked with `pytest.mark.xfail` and a reason that links to the #172 comment, so the gap stays visible in the test report.

### `test_many_hosts.py` (FR-003, FR-004, FR-005)

- **Each host gets its own result (FR-003):** run `send_command("show version")` on all healthy hosts at the same time. For each host, check that its result contains its own host name and no other host's name.
- **A failing host fails only itself (FR-004):** run `send_command("show version")` on all hosts, the two failing hosts included. Check that:
  - `AggregatedResult.failed_hosts` contains exactly the host with the wrong password and the slow host
  - the host with the wrong password failed with an authentication error
  - the slow host failed with a timeout error
  - every other host's result is a success
- **Today's behavior on the next task (FR-005):** after the run above, run a second `send_command` on all hosts. Assert what happens today:
  - whether Nornir skips the failed hosts (they stay in `nr.data.failed_hosts`)
  - whether the healthy hosts run the task

  Name the test so it is clear that it records behavior and does not define it, for example `test_records_next_task_behavior_after_host_failure`, and link #143 in its docstring.

### Rules for all tests

- No test sleeps to wait for something. The fixtures wait for ports to open, and scrapli's timeouts handle the slow host.
- Tests do not depend on each other. The FR-005 test runs both tasks itself.
- Assertions compare against values defined in the platform definitions or `constants.py`, never against output copied into the test.

## Step 4: Run the session before releases (separate pull request)

This step goes in its own pull request, because a mistake in `publish.yaml` blocks releases.

### `pre_release.yaml` (FR-007)

Add a job, or a step limited to Ubuntu, that runs after `uv lock --upgrade`:

```yaml
      - if: matrix.os == 'ubuntu-latest'
        run: uv run --locked --only-group nox nox -s functional_tests
```

The existing job runs on Ubuntu and macOS. The functional session runs on Ubuntu only, as agreed in the brief.

### `publish.yaml` (FR-008)

Add a step before `build and publish`:

```yaml
      - name: functional tests
        run: uv run --locked --only-group nox nox -s functional_tests
```

If the step fails, the job stops, `uv publish` does not run and the release branch is not created.

## Step 5: Check the success criteria (before closing #172)

| Criterion | How to check it | Where to record the result |
|---|---|---|
| SC-001: under 5 minutes | Read the duration of the `functional` job in GitHub Actions. | Pull request description |
| SC-002: 20 runs in a row pass | Run `for i in $(seq 20); do make test_functional \|\| break; done` locally, and run the job several times with `workflow_dispatch`. | Pull request description |
| SC-003: a deliberate break fails the session | On a throwaway branch, make one change at a time and confirm the session fails: (1) make `ScrapliCore.open` raise before connecting, (2) make the `send_command` task send a different command. | Pull request description. These are not permanent tests. |
| SC-004: nothing outside the test job | Confirm the job uses no secrets, and open a test pull request from a fork. | Pull request description |

## Pull requests

1. **Step 2 and step 3:** dependency, nox session, platform definitions, fixtures, tests, `commit.yaml` job. Split into two pull requests if the review is too large: infrastructure plus `test_core_tasks.py` first, then `test_many_hosts.py`.
2. **Step 4:** `pre_release.yaml` and `publish.yaml`.

Each pull request includes a changelog entry if the project starts using one. It does not use one today.

## Risks

- **The platform definitions need maintenance.** If scrapli changes the commands its drivers send when a session opens, or its prompt patterns, the definitions must change too. The weekly `pre_release.yaml` job detects this.
- **OpenSSH and paramiko may not agree on algorithms.** Step 1 checks this before any code goes into the repository. If they do not agree, the fallback is scrapli's `paramiko` or `ssh2` transport in the functional inventory. That would test a different transport than most users run.
- **FakeNOS is maintained by a small group.** If it stops being maintained, SIMNOS is the closest replacement. The definitions use the same format, but SIMNOS needs Python 3.13 or later and `paramiko>=4.0`.
- **The #158 migration changes the scrapli API.** The plan builds against scrapli 2026.2.20 on purpose. The tests call Nornir tasks, not scrapli directly, so the migration should mostly leave them unchanged. Whether scrapli 2026.10.03 still supports the same transports and prompt patterns is not known.

## Sources

- Issue [#172](https://github.com/scrapli/nornir_scrapli/issues/172): the proposal
- Issues [#157](https://github.com/scrapli/nornir_scrapli/issues/157) and [#158](https://github.com/scrapli/nornir_scrapli/issues/158): the scrapli 2026.10.03 upgrade
- Issue [#143](https://github.com/scrapli/nornir_scrapli/issues/143): one host's failure stopped the next task on 52 hosts
- [FakeNOS on PyPI](https://pypi.org/project/fakenos/) and [FakeNOS repository](https://github.com/fakenos/fakenos)
- [SIMNOS on PyPI](https://pypi.org/project/simnos/) and [SIMNOS repository](https://github.com/Route-Reflector/simnos/)
- scrapli 2026.2.20 driver files, installed from `uv.lock`: `scrapli/driver/core/<platform>/base_driver.py` and `sync_driver.py`
- Repository files: `noxfile.py`, `Makefile`, `pyproject.toml`, `tests/conftest.py`, `tests/inventory_data/groups.yaml`, `.github/workflows/commit.yaml`, `pre_release.yaml`, `publish.yaml`

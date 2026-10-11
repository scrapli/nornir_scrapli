# FakeNOS Functional Tests Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a self-contained Python 3.13 functional-test suite that exercises all eight core `nornir_scrapli` tasks against concurrent FakeNOS SSH devices and gates commits, prerelease dependency checks, and publishing.

**Architecture:** A session-scoped FakeNOS lab owns two healthy devices per supported core platform plus isolated authentication and timeout failures. Function-scoped Nornir instances consume generated YAML inventory so connections and failed-host state cannot leak between tests; project-owned Python NOS definitions provide deterministic per-host output and prompt transitions. A dedicated nox session keeps the slower functional suite out of default local checks while three GitHub workflows invoke it at the required gates.

**Tech Stack:** Python 3.13, pytest 7, Nornir 3.6, nornir_scrapli, scrapli 2026.2.20 or the subsequently locked compatible version, FakeNOS 1.2.1 by default, nox, uv, GitHub Actions

**Spec:** `functional-tests-plan.md`

## Global Constraints

- Exercise only the core `scrapli` connection plugin and these tasks: `send_command`, `send_commands`, `send_commands_from_file`, `send_config`, `send_configs`, `send_configs_from_file`, `send_interactive`, and `get_prompt`.
- Cover `cisco_iosxe`, `cisco_nxos`, `cisco_iosxr`, `arista_eos`, and `juniper_junos` wherever the compatibility spike proves FakeNOS can imitate them; record unsupported platforms with strict xfails linked to the permanent issue #172 spike comment.
- Run two healthy hosts per supported platform with more than one Nornir worker, plus one rejected-login IOS XE host and one timeout IOS XE host.
- Run functional tests on Linux with Python 3.13 only; do not add them to `nox.options.sessions`.
- Do not cover `scrapli_cfg`, `scrapli_netconf`, `generic`, community platforms, real network images, macOS, or additional Python versions.
- Do not change production modules to make the tests pass. Any product defect exposed by the suite is separate work.
- Use no credentials, containers, external services, or resources outside the test process.
- Keep the full functional session under five minutes and use fixture readiness checks rather than test sleeps.
- Use a fresh Nornir instance for every test and call `close_connections(on_good=True, on_failed=True)` during teardown.
- Keep all SSH and timeout settings in each platform group's `connection_options.scrapli.extras`; Nornir does not deep-merge `extras` from defaults and groups.
- Current locked scrapli leaves `send_config`, `send_configs`, and `send_configs_from_file` in configuration mode. Assert the configuration prompt after those tasks rather than the privileged prompt proposed in the source document.
- Current Nornir skips hosts retained in `nr.data.failed_hosts` on the next default run. Record that behavior for issue #143 without declaring it the desired product behavior.
- Complete Tasks 2 through 7 as the first pull request and Task 8 as a separate release-workflow pull request because an error in `publish.yaml` can block releases.

## Review Focus

- File-backed command/config inputs, including their trailing newline, must be parsed into the expected commands without creating a blank command; Task 4 and Task 5 pin this through exact `channel_input` assertions.
- A configuration task changes connection state; Task 5 immediately runs `get_prompt` on the same connections and checks each platform's configuration prompt.
- A slow response must not block healthy hosts or leak a connection during teardown; Task 6 checks exact failed hosts, healthy successes, elapsed time, and a second fresh test run.
- Concurrent hosts must not receive another host's output; Task 6 checks each result for its own host name and against every other healthy host name.
- Failed-host state must not accidentally suppress healthy hosts on the next task; Task 6 performs both runs in one test and checks the exact second result keys and retained global failed-host set.

---

### Task 1: Resolve the FakeNOS Compatibility Gate

**Files:**
- Do not commit repository files; use `/tmp/nornir-scrapli-fakenos-spike/` for the throwaway script and definitions.
- Record: permanent comment on GitHub issue #172

**Interfaces:**
- Consumes: FakeNOS 1.2.1, SIMNOS 2.4.0 only as fallback, scrapli 2026.2.20, and the prompt/startup-command table in `functional-tests-plan.md`.
- Produces: selected emulator package/version, exact server start/stop API, custom definition module contract, supported platform tuple, known-gap reasons, SSH `extras`, stable authentication/timeout exception classes, per-host port assignment, and timeout-host isolation strategy.

- [ ] **Step 1: Create an isolated spike environment**

Run:

```bash
mkdir -p /tmp/nornir-scrapli-fakenos-spike
uv run --directory /tmp/nornir-scrapli-fakenos-spike --python 3.13 --with fakenos==1.2.1 --with scrapli==2026.2.20 python -c "import fakenos, scrapli; print(fakenos.__version__, scrapli.__version__)"
```

Expected: both pinned packages import under Python 3.13. If FakeNOS does not expose `__version__`, print `importlib.metadata.version("fakenos")` instead.

- [ ] **Step 2: Implement five minimal throwaway platform definitions**

Each definition must provide the initial/default/configuration prompts from the spec, startup commands, privilege transitions, `show version`, `show clock`, both configuration lines, the interactive sequence, `exit`, and a delayed response. Make `show version` include the server host name.

- [ ] **Step 3: Probe healthy sessions and concurrency**

Start two replicas per platform and, with scrapli's `system` transport, call `open()`, `get_prompt()`, `send_command("show version")`, `send_config("interface Loopback0")`, `send_interactive(...)`, and `close()` concurrently.

Expected: record pass/fail separately for every platform, the prompt after `send_config`, required OpenSSH options, and whether one FakeNOS instance can host mixed definitions.

- [ ] **Step 4: Probe isolated authentication and operation failures**

Connect once with a wrong client password and once to a host whose `show version` response exceeds `timeout_ops`.

Expected: record the exact exception classes exposed to callers, prove the sleeping handler does not delay healthy hosts, and prove both failed sessions can be stopped without hanging.

- [ ] **Step 5: Test built-in definitions and the SIMNOS fallback**

Run the short healthy probe against FakeNOS's built-ins to confirm the documented gaps. Test SIMNOS only if FakeNOS cannot satisfy a requirement that the fork plausibly supports.

- [ ] **Step 6: Publish the decision record on issue #172**

Include one row per platform for built-in/custom support and known gaps, the selected emulator and reason, exact SSH options, exception classes, lifecycle API, timeout strategy, and a permalink to the comment.

Expected: every value listed in this task's `Produces` block has a concrete answer. Stop implementation if no platform works end to end.

### Task 2: Add the Isolated Functional-Test Entry Point

**Files:**
- Modify: `pyproject.toml:89-112`
- Modify: `uv.lock`
- Modify: `noxfile.py:7-11,14-29,53-58`
- Modify: `Makefile:1-19`
- Move: `tests/conftest.py` to `tests/unit/conftest.py`

**Interfaces:**
- Consumes: emulator package/version chosen in Task 1.
- Produces: dependency group `functional`; nox session `functional_tests(session)`; Make target `test_functional`; unit-only autouse fixtures.

- [ ] **Step 1: Add a failing lock-group check**

Add the exact group, substituting the package/version only if Task 1 selected SIMNOS:

```toml
functional = [
    {include-group = "test"},
    "fakenos>=1.2.1; python_version >= '3.11'",
]
```

Run: `uv sync --locked --only-group functional`

Expected: FAIL because `uv.lock` does not yet contain the new group.

- [ ] **Step 2: Regenerate and validate the lock file**

Run: `uv lock && uv lock --check && uv sync --locked --only-group functional`

Expected: all commands PASS, and the `dev` group still does not include `functional`.

- [ ] **Step 3: Add the nox session**

Add this interface without adding it to `nox.options.sessions`:

```python
@nox.session(python="3.13")
def functional_tests(session):
    """Run functional tests against fake devices."""
    sync(session, "functional")
    test_args = session.posargs or ["tests/functional"]
    session.run("pytest", *test_args)
```

This `posargs` fallback allows focused node IDs without collecting `tests/functional` twice.

- [ ] **Step 4: Add the Make target**

Add `test_functional` to `.PHONY` and define:

```make
test_functional:
	$(NOX) -s functional_tests
```

- [ ] **Step 5: Isolate unit autouse fixtures**

Move `tests/conftest.py` unchanged to `tests/unit/conftest.py`. Do not leave root-level autouse fixtures, because all eight currently instantiate unit inventories for every collected functional test.

- [ ] **Step 6: Verify session selection and unit isolation**

Run:

```bash
uv run --locked --only-group nox nox -l
uv run --locked --only-group nox nox -s unit_tests-3.13
uv run --locked --only-group nox nox -s genie-3.13
```

Expected: `functional_tests` is listed but absent from default sessions; unit and Genie tests pass and collect only `tests/unit`.

- [ ] **Step 7: Commit the test entry point**

```bash
git add pyproject.toml uv.lock noxfile.py Makefile tests/conftest.py tests/unit/conftest.py
git commit -m "test: add functional test session"
```

### Task 3: Build the Fake Device Lab and First End-to-End Test

**Files:**
- Create: `tests/functional/__init__.py`
- Create: `tests/functional/constants.py`
- Create: `tests/functional/conftest.py`
- Create: `tests/functional/nos/cisco_iosxe.py`
- Create: `tests/functional/nos/cisco_nxos.py`
- Create: `tests/functional/nos/cisco_iosxr.py`
- Create: `tests/functional/nos/arista_eos.py`
- Create: `tests/functional/nos/juniper_junos.py`
- Create if required by Task 1: `tests/functional/nos/cisco_iosxe_slow.py`
- Create: `tests/functional/test_core_tasks.py`

**Interfaces:**
- Consumes: exact FakeNOS lifecycle/definition contract, SSH options, supported platforms, and known gaps from Task 1.
- Produces: `PLATFORMS`, `SUPPORTED_PLATFORMS`, `KNOWN_GAPS`, deterministic expected-value helpers, `FakeHost`, `FakeNosLab`, `InventoryFiles`, `fake_nos_lab`, `functional_inventory_files`, `functional_nornir`, `healthy_nornir`, `healthy_platform_nornir`, and a passing `test_send_command`.

- [ ] **Step 1: Define stable test values and expected-value helpers**

In `tests/functional/constants.py`, define these names with values confirmed by Task 1:

```python
PLATFORMS = (
    "cisco_iosxe",
    "cisco_nxos",
    "cisco_iosxr",
    "arista_eos",
    "juniper_junos",
)
SUPPORTED_PLATFORMS = (...)  # Exact Task 1 result.
KNOWN_GAPS = {...}  # platform -> permanent issue #172 comment URL/reason.
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

def expected_version_output(hostname: str) -> str: ...
def expected_clock_output(hostname: str) -> str: ...
def expected_default_prompt(hostname: str, platform: str) -> str: ...
def expected_config_prompt(hostname: str, platform: str) -> str: ...
```

The definitions and tests must call the same helpers; do not duplicate output literals in assertions.

- [ ] **Step 2: Write the first failing functional test**

In `tests/functional/test_core_tasks.py`, build `PLATFORM_CASES` from all five `PLATFORMS`, applying `pytest.mark.xfail(strict=True, reason=...)` to entries in `KNOWN_GAPS`, then add:

```python
@pytest.mark.parametrize("platform", PLATFORM_CASES)
def test_send_command(healthy_platform_nornir, platform):
    result = healthy_platform_nornir.run(
        task=send_command,
        command=SHOW_VERSION_COMMAND,
    )

    assert not result.failed
    assert len(result) == HEALTHY_REPLICAS
    for host_name, multi_result in result.items():
        host_result = multi_result[0]
        assert host_result.failed is False
        assert host_result.changed is False
        assert host_result.result == expected_version_output(host_name)
        assert host_result.scrapli_response.channel_input == SHOW_VERSION_COMMAND
```

Run: `uv run --locked --only-group nox nox -s functional_tests -- tests/functional/test_core_tasks.py::test_send_command`

Expected: FAIL because the fixtures and definitions do not exist yet.

- [ ] **Step 3: Implement the minimal custom NOS definitions**

Follow the exact module schema proven in Task 1. Each definition must include only startup commands, privilege transitions, `show version`, `show clock`, configuration lines, interaction, slow behavior where applicable, and `exit`. Use `{host}`-derived output and the prompt table from the spec.

- [ ] **Step 4: Implement project-owned fixture data types**

In `tests/functional/conftest.py`, define:

```python
@dataclass(frozen=True)
class FakeHost:
    name: str
    platform: str
    port: int
    role: str

@dataclass(frozen=True)
class FakeNosLab:
    hosts: tuple[FakeHost, ...]
    supported_platforms: tuple[str, ...]

@dataclass(frozen=True)
class InventoryFiles:
    hosts: Path
    groups: Path
    defaults: Path
```

Keep FakeNOS-specific objects private to the fixture module.

- [ ] **Step 5: Implement `fake_nos_lab`**

Signature:

```python
@pytest.fixture(scope="session")
def fake_nos_lab(tmp_path_factory: pytest.TempPathFactory) -> Iterator[FakeNosLab]: ...
```

Start two healthy hosts per `SUPPORTED_PLATFORMS`, one wrong-password IOS XE host, and one isolated slow IOS XE host. Bind only to `127.0.0.1`, use runtime-assigned or safely reserved ports according to Task 1, poll TCP readiness with a bounded deadline, yield metadata, then stop and join every server in `finally`.

- [ ] **Step 6: Generate Nornir YAML inventory**

Signature:

```python
@pytest.fixture(scope="session")
def functional_inventory_files(
    fake_nos_lab: FakeNosLab,
    tmp_path_factory: pytest.TempPathFactory,
) -> InventoryFiles: ...
```

Write host-level `hostname: 127.0.0.1`, unique `port`, platform group, and role. Put `platform`, `transport`, `auth_strict_key`, SSH-config choice, and `timeout_ops` together under each group's `connection_options.scrapli.extras`. Give only the auth-failure server the mismatched server password.

- [ ] **Step 7: Implement fresh Nornir fixtures**

Signatures:

```python
@pytest.fixture
def functional_nornir(
    functional_inventory_files: InventoryFiles,
    fake_nos_lab: FakeNosLab,
) -> Iterator[Nornir]: ...

@pytest.fixture
def healthy_nornir(functional_nornir: Nornir) -> Nornir: ...

@pytest.fixture
def healthy_platform_nornir(
    functional_nornir: Nornir,
    platform: str,
) -> Nornir: ...
```

Initialize the threaded runner with `num_workers=len(fake_nos_lab.hosts)`. Filter by inventory `role` and `platform`. In teardown call `close_connections(on_good=True, on_failed=True)` and `data.reset_failed_hosts()`.

- [ ] **Step 8: Run the first end-to-end test**

Run: `uv run --locked --only-group nox nox -s functional_tests -- tests/functional/test_core_tasks.py::test_send_command -vv`

Expected: two healthy results per supported platform pass; known gaps appear as strict xfails; no teardown hang or leaked FakeNOS process remains.

- [ ] **Step 9: Commit the lab and first test**

```bash
git add tests/functional
git commit -m "test: add FakeNOS functional lab"
```

### Task 4: Cover Command, File, and Prompt Tasks

**Files:**
- Modify: `tests/functional/test_core_tasks.py`
- Create: `tests/functional/files/send_commands_from_file`

**Interfaces:**
- Consumes: `healthy_platform_nornir`, `PLATFORM_CASES`, command constants, and expected-value helpers from Task 3.
- Produces: coverage for `send_commands`, `send_commands_from_file`, and `get_prompt`, completing the non-mutating core-task cases.

- [ ] **Step 1: Write failing tests for command lists, command files, and prompts**

Add these parameterized tests:

```python
def test_send_commands(healthy_platform_nornir, platform): ...
def test_send_commands_from_file(healthy_platform_nornir, platform): ...
def test_get_prompt(healthy_platform_nornir, platform): ...
```

For command-list and file cases, run `SHOW_VERSION_COMMAND` and `SECOND_COMMAND`; assert two hosts, no failures, `changed is False`, exact `"\n\n"`-joined public results, and exact `response.channel_input` values in `scrapli_response`. For prompts, assert `expected_default_prompt(host_name, platform)` and `changed is False`.

- [ ] **Step 2: Verify the new tests fail for missing file/definition behavior**

Run: `uv run --locked --only-group nox nox -s functional_tests -- tests/functional/test_core_tasks.py -k "send_commands or get_prompt" -vv`

Expected: at least the newly added cases FAIL before their fixture data is complete.

- [ ] **Step 3: Add exact file input and minimal definition responses**

Write `show version` and `show clock`, one per line, to `tests/functional/files/send_commands_from_file`. Adjust only custom definitions needed to satisfy the exact commands; do not add unrelated emulation.

- [ ] **Step 4: Verify all non-mutating task tests**

Run: `uv run --locked --only-group nox nox -s functional_tests -- tests/functional/test_core_tasks.py -k "send_command or send_commands or get_prompt" -vv`

Expected: PASS for supported platforms with only documented strict xfails.

- [ ] **Step 5: Commit command and prompt coverage**

```bash
git add tests/functional/test_core_tasks.py tests/functional/files/send_commands_from_file tests/functional/nos
git commit -m "test: cover core command tasks against FakeNOS"
```

### Task 5: Cover Configuration and Interactive Tasks

**Files:**
- Modify: `tests/functional/test_core_tasks.py`
- Create: `tests/functional/files/send_configs_from_file`
- Modify as needed: `tests/functional/nos/*.py`

**Interfaces:**
- Consumes: `CONFIG_LINES`, interactive constants, expected configuration prompts, and `healthy_platform_nornir`.
- Produces: coverage for `send_config`, `send_configs`, `send_configs_from_file`, and `send_interactive`, completing FR-001 and FR-002.

- [ ] **Step 1: Write failing configuration tests**

Add parameterized tests named `test_send_config`, `test_send_configs`, and `test_send_configs_from_file`. Each must assert two hosts, no failures, `changed is True`, expected configuration input in the public result and `scrapli_response`, then run `get_prompt` on the same filtered Nornir object and assert `expected_config_prompt(host_name, platform)`.

- [ ] **Step 2: Write the failing interactive test**

Add `test_send_interactive`, passing events derived from `INTERACTIVE_COMMAND`, `INTERACTIVE_CONFIRMATION`, and `INTERACTIVE_RESPONSE`. For each host assert:

```python
assert host_result.failed is False
assert host_result.changed is True
assert host_result.result is host_result.scrapli_response
assert INTERACTIVE_CONFIRMATION in host_result.scrapli_response.result
```

- [ ] **Step 3: Run the focused tests to verify failure**

Run: `uv run --locked --only-group nox nox -s functional_tests -- tests/functional/test_core_tasks.py -k "config or interactive" -vv`

Expected: FAIL on missing configuration-file input or incomplete prompt transitions.

- [ ] **Step 4: Add exact file input and complete state transitions**

Write the two `CONFIG_LINES`, one per line, to `tests/functional/files/send_configs_from_file`. Add only the configuration and interactive transitions required by the failing tests, including startup and close transitions validated in Task 1.

- [ ] **Step 5: Verify all eight task cases together**

Run: `uv run --locked --only-group nox nox -s functional_tests -- tests/functional/test_core_tasks.py -vv`

Expected: eight parameterized task tests pass on every supported platform; known gaps remain visible as strict xfails.

- [ ] **Step 6: Commit configuration and interaction coverage**

```bash
git add tests/functional/test_core_tasks.py tests/functional/files/send_configs_from_file tests/functional/nos
git commit -m "test: cover config and interactive tasks"
```

### Task 6: Prove Concurrency and Failure Isolation

**Files:**
- Create: `tests/functional/test_many_hosts.py`
- Modify as needed: `tests/functional/conftest.py`
- Modify as needed: `tests/functional/nos/cisco_iosxe_slow.py`

**Interfaces:**
- Consumes: `functional_nornir`, `healthy_nornir`, exact exception classes from Task 1, host-role constants, and deterministic host output.
- Produces: FR-003 host isolation, FR-004 failure isolation, and FR-005 current next-task behavior.

- [ ] **Step 1: Write the failing per-host-output test**

Add `test_each_host_receives_only_its_own_output(healthy_nornir)`. Run `send_command(SHOW_VERSION_COMMAND)` once across all healthy hosts. Assert more than one result, no failures, every result contains its own host name, and every result excludes every other healthy host name.

- [ ] **Step 2: Write the failing authentication/timeout isolation test**

Add `test_authentication_and_timeout_fail_only_the_affected_hosts(functional_nornir)`. Time one all-host `show version` run and assert:

```python
assert set(result.failed_hosts) == {AUTH_FAILURE_HOST, TIMEOUT_FAILURE_HOST}
assert isinstance(result[AUTH_FAILURE_HOST].exception, AUTH_EXCEPTION_FROM_SPIKE)
assert isinstance(result[TIMEOUT_FAILURE_HOST].exception, TIMEOUT_EXCEPTION_FROM_SPIKE)
assert all(not result[name].failed for name in healthy_host_names)
assert elapsed < 30
```

Use the stable exception imports confirmed in Task 1, normally `ScrapliAuthenticationFailed` and `ScrapliTimeout`.

- [ ] **Step 3: Write the failing issue #143 behavior test**

Add `test_records_next_task_behavior_after_host_failure(functional_nornir)` with a docstring linking issue #143 and stating that it records, rather than prescribes, behavior. Run the all-host failure-producing command, then run `SECOND_COMMAND` without resetting failures. Assert the first run has exactly the two failed hosts; the second result keys equal all healthy host names; the second run has no failures; and `functional_nornir.data.failed_hosts` still equals the two failed names.

- [ ] **Step 4: Run all three tests to verify failure**

Run: `uv run --locked --only-group nox nox -s functional_tests -- tests/functional/test_many_hosts.py -vv`

Expected: at least one test FAIL until host-specific output, timeout isolation, and role filtering are complete.

- [ ] **Step 5: Complete only the fixture/definition behavior required by failures**

Keep the timeout host in a separate server instance if Task 1 showed a sleeping handler can serialize peers. Ensure the failure command is `show version` for every host, so the all-host run naturally produces both failures while healthy hosts succeed.

- [ ] **Step 6: Verify repeatability and teardown**

Run:

```bash
uv run --locked --only-group nox nox -s functional_tests -- tests/functional/test_many_hosts.py -vv
uv run --locked --only-group nox nox -s functional_tests -- tests/functional/test_many_hosts.py -vv
```

Expected: both runs PASS with the same host sets and no port collision or teardown delay.

- [ ] **Step 7: Commit many-host coverage**

```bash
git add tests/functional/test_many_hosts.py tests/functional/conftest.py tests/functional/nos
git commit -m "test: verify functional host failure isolation"
```

### Task 7: Gate Every Commit with Functional Tests

**Files:**
- Modify: `.github/workflows/commit.yaml:5-46`

**Interfaces:**
- Consumes: nox session `functional_tests` from Task 2.
- Produces: independent `functional` GitHub Actions job on every push, pull request, and manual run.

- [ ] **Step 1: Add the functional job**

Add an Ubuntu job parallel to `checks`, `unit_tests`, and `genie`:

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

Do not add secrets, service containers, or workflow permissions.

- [ ] **Step 2: Validate workflow syntax and the local equivalent**

Run:

```bash
uv run --locked --only-group nox nox -s functional_tests
uv run --locked --only-group nox nox -s ruff mypy
```

Expected: both commands PASS. If the repository has `actionlint` available, also run `actionlint .github/workflows/commit.yaml`; otherwise inspect the Actions parse result on the pull request.

- [ ] **Step 3: Commit commit-workflow coverage**

```bash
git add .github/workflows/commit.yaml
git commit -m "ci: run functional tests on commits"
```

### Task 8: Gate Prerelease Checks and Publishing

**Files:**
- Modify: `.github/workflows/pre_release.yaml:18-26`
- Modify: `.github/workflows/publish.yaml:10-24`

**Interfaces:**
- Consumes: stable functional suite merged from Tasks 2 through 7.
- Produces: Ubuntu-only post-upgrade prerelease check and pre-publish release gate.

- [ ] **Step 1: Add the Ubuntu-only prerelease step**

Immediately after `uv lock --upgrade`, add:

```yaml
      - if: matrix.os == 'ubuntu-latest'
        run: uv run --locked --only-group nox nox -s functional_tests
```

Keep the existing unit-test step on both matrix operating systems.

- [ ] **Step 2: Add the publish gate**

Immediately before `build and publish`, add:

```yaml
      - name: functional tests
        run: uv run --locked --only-group nox nox -s functional_tests
```

Keep `UV_PUBLISH_TOKEN` scoped only to `build and publish`; the functional step must not receive it. GitHub's default step failure behavior must prevent both `uv publish` and release-branch creation.

- [ ] **Step 3: Validate both workflow paths without changing the committed lock**

Run:

```bash
uv run --locked --only-group nox nox -s functional_tests
```

Expected: the current locked functional suite passes locally. Push the release-workflow pull request and invoke `pre_release.yaml` with `workflow_dispatch`; that disposable runner must complete `UV_PRERELEASE=allow uv lock --upgrade` and the following functional step successfully. Confirm by inspection that the publish functional step precedes the only step carrying `UV_PUBLISH_TOKEN` and that no `if: always()` or `continue-on-error` can bypass its failure.

- [ ] **Step 4: Commit release gates separately**

```bash
git add .github/workflows/pre_release.yaml .github/workflows/publish.yaml
git commit -m "ci: gate releases with functional tests"
```

### Task 9: Verify Acceptance and Record Evidence

**Files:**
- Modify only if a defect is found: files owned by Tasks 2 through 8
- Record: pull request description and issue #172

**Interfaces:**
- Consumes: complete functional suite and all three workflow integrations.
- Produces: evidence for SC-001 through SC-004 and a closure-ready issue record.

- [ ] **Step 1: Run the full local quality suite**

Run:

```bash
uv lock --check
uv run --locked --only-group nox nox -s ruff mypy docs build unit_tests-3.13 functional_tests
```

Expected: all sessions PASS. Confirm `unit_tests` and `genie` still target only `tests/unit`, while `functional_tests` targets only `tests/functional` by default.

- [ ] **Step 2: Prove the default nox command did not change**

Run: `uv run --locked --only-group nox nox`

Expected: only `unit_tests-3.13`, `ruff`, and `mypy` run.

- [ ] **Step 3: Run the stability loop**

Run:

```bash
for i in $(seq 1 20); do make test_functional || break; done
```

Expected: 20 consecutive PASS results with no port collision, leaked process, or intermittent timeout. Record total and per-run duration in the first pull request description.

- [ ] **Step 4: Prove deliberate product breaks are detected**

On a throwaway branch, separately make `ScrapliCore.open` raise before connecting and make `send_command` send an undefined command. Run `make test_functional` after each change.

Expected: each deliberate break fails the functional suite for the relevant reason. Revert the throwaway changes and record the commands/results; do not commit mutation tests.

- [ ] **Step 5: Verify CI isolation and timing**

Observe the `functional` job on a normal pull request and a fork or Dependabot pull request. Confirm it receives no secrets, uses no service containers, and completes in under five minutes. Manually rerun it enough times to supplement the local 20-run stability evidence.

- [ ] **Step 6: Record final evidence**

Update both pull request descriptions and issue #172 with supported/xfail platforms, elapsed time, 20-run result, deliberate-break result, fork result, and links to passing commit/prerelease workflow runs.

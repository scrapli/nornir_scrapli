# Functional tests

Run from the repository root on Linux with uv and an OpenSSH client available:

```bash
make test_functional
# Equivalent locked Python 3.13 session:
uv run --locked --only-group nox nox -s functional_tests
# Optional pytest selection:
uv run --locked --only-group nox nox -s functional_tests -- tests/functional/test_core_tasks.py
# Focused path plus pytest filter:
uv run --locked --only-group nox nox -s functional_tests -- tests/functional/test_core_tasks.py -k test_send_command
```

Arguments after `--` replace the default `tests/functional` selection. Overrides
must include `tests/functional` or a path/node ID within it, even when adding
options such as `-k` or `-v`. Options alone let pytest collect the whole repository.

The session starts FakeNOS SSH servers on dynamically allocated loopback ports,
then exercises the actual Nornir connection plugin, scrapli system transport, and
eight public core tasks. There are two healthy hosts for each of `cisco_iosxe`,
`cisco_nxos`, `cisco_iosxr`, `arista_eos`, and `juniper_junos`, plus rejected-login
and slow-response hosts. All five custom platform definitions are supported;
there are currently no xfails. The full suite contains 43 test cases.

These are simulated CLI exchanges, not validation against real network operating
systems. Tests need no real devices, service containers, external device
credentials, or SSH configuration. Credentials are test-local constants. Package
installation still requires the locked dependencies. Other platforms, Python
versions, NETCONF, and scrapli-cfg are outside this suite's scope.

Configuration tasks currently leave connections in configuration mode:
`{host}(config)#` on Cisco/Arista and `{host}#` on Junos (whose exec prompt is
`{host}>`). Tests record this behavior rather than require a return to exec.
After an authentication/timeout failure, the next task skips failed hosts and
continues on healthy hosts; this records current behavior for
[#143](https://github.com/scrapli/nornir_scrapli/issues/143).

Unit and Genie sessions target `tests/unit`; functional tests target
`tests/functional` by default. Bare nox still selects only `unit_tests-3.13`,
`ruff`, and `mypy`.

## Acceptance evidence

Historical local verification on 2026-10-11 (Linux, Python 3.13.14, locked scrapli
2026.2.20 and FakeNOS 1.2.1), before the final teardown liveness check:

- `uv lock --check` and all six quality sessions passed (`ruff`, `mypy`, `docs`,
  `build`, `unit_tests-3.13`, `functional_tests`). Units: 44 passed, 4 skipped.
- **20/20 consecutive unchanged local stability sessions passed**, each with
  43 passing cases. Full `make test_functional` durations, including locked
  setup and teardown: **1,773.229 seconds total (29m33.229s)**,
  **88.332–89.030 seconds per run**, mean 88.661 seconds. This was a feature
  worktree run, not `main`. An earlier tool-interrupted batch is excluded.
- Two disposable subprocess-only mutations of actual product function code
  were detected by the full suite: raising in `ScrapliCore.open` before connection
  produced **43 failures**, pytest exit 1, in 6.613 seconds command elapsed;
  changing the actual `send_command` wrapper's driver call to an undefined
  command produced **8 failures / 35 passes**, exit 1, in 82.624 seconds.
  Both restored their original code objects; production files were never edited.
- After mutation checks, the full locked session passed again: **43 passed**,
  88.622 seconds command elapsed. Original file hashes matched.

The final review added a healthy-driver liveness assertion immediately after
normal Nornir close, before unconditional resource rescue. This changes
`tests/functional/conftest.py`'s hash; the 20-run series above applies to the
earlier snapshot, not the final fixture. Current final-review verification:

- One full `make test_functional` run: **43 passed, 114 warnings in 87.92s**;
  **88.830 seconds** command elapsed, exit 0.
- Locked Ruff and mypy sessions passed: 86 files formatted, all lint checks
  passed, and no type issues in 36 production source files.
- A focused scratch probe replaced normal Nornir close with an intentional no-op:
  the healthy-driver assertion surfaced and both live drivers were rescued.
  The probe passed with the final fixture and failed against the earlier fixture,
  which silently rescued them without detecting the ineffective normal close.

Exact current commands and hash delta are in the final-review fix-wave section
of the report below.

Per-run logs, exact commands, timings, mutation call counts, and pending-criteria
details are saved locally in
`.superpowers/sdd/2026-10-11-functional-tests/task-9-report.md` and its
`task-9-logs/` directory. These scratch artifacts are git-ignored. Successful
functional runs emit 114 OpenSSH `forkpty` deprecation warnings.

Remote acceptance remains pending: SC-001's under-five-minute GitHub Actions
Linux job timing; SC-002's 20 unchanged runs on `main` and supplementary GitHub
reruns; a passing normal and fork/Dependabot PR job without secrets or services;
and passing commit and upgraded-prerelease workflow links. Local timing and
worktree stability do not establish these GitHub criteria. Release gating is
statically configured before publishing; execution evidence remains pending.

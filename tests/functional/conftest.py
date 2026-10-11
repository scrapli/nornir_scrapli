"""Bounded loopback FakeNOS lab and fresh Nornir inventories."""

import errno
import socket
import threading
import time
import traceback
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml
from fakenos import FakeNOS
from fakenos.plugins.servers.ssh_server_paramiko import ParamikoSshServer
from paramiko import SSHException

from functional.constants import (
    AUTH_FAILURE_HOST,
    HEALTHY_REPLICAS,
    PASSWORD,
    REJECTED_LOGIN_PASSWORD,
    SLOW_RESPONSE_DELAY,
    SUPPORTED_PLATFORMS,
    TIMEOUT_FAILURE_HOST,
    TIMEOUT_OPS,
    USERNAME,
)
from nornir import InitNornir
from nornir.core import Nornir


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


class _LabThreads:
    """Track listener threads and their descendants independently of pytest phases."""

    def __init__(self):
        self.threads = []
        self.errors = []
        self.local = threading.local()
        self.lock = threading.Lock()
        self.patch = pytest.MonkeyPatch()

    def __enter__(self):
        original_start = threading.Thread.start

        def start(thread, *args, **kwargs):
            if getattr(self.local, "owned", False):
                original_run = thread.run

                def run():
                    with self.owner():
                        try:
                            original_run()
                        except BaseException:
                            with self.lock:
                                self.errors.append((thread.name, traceback.format_exc()))
                            raise

                thread.run = run
                with self.lock:
                    self.threads.append(thread)
            return original_start(thread, *args, **kwargs)

        self.patch.setattr(threading.Thread, "start", start)
        return self

    def __exit__(self, *_exc):
        self.patch.undo()

    @contextmanager
    def owner(self):
        previous = getattr(self.local, "owned", False)
        self.local.owned = True
        try:
            yield
        finally:
            self.local.owned = previous

    def finish(self, timeout):
        deadline = time.monotonic() + timeout
        while True:
            with self.lock:
                remaining = [thread for thread in self.threads if thread.is_alive()]
            if not remaining or time.monotonic() >= deadline:
                break
            for thread in remaining:
                thread.join(timeout=max(0, deadline - time.monotonic()))
        assert not remaining, f"Lab threads survived teardown: {remaining}"
        assert not self.errors, f"Unexpected lab thread failures: {self.errors}"


@pytest.fixture(scope="session")
def _lab_threads():
    with _LabThreads() as threads:
        try:
            yield threads
        finally:
            threads.finish(timeout=SLOW_RESPONSE_DELAY + 3)


class _LabServer(ParamikoSshServer):
    """Account only for the two proven FakeNOS 1.2.1 worker errors."""

    def __init__(self, *, lab_threads, **kwargs):
        super().__init__(**kwargs)
        self.lab_threads = lab_threads
        self.readiness_peers = set()
        self.expected_errors = []
        self.unexpected_errors = []

    def start(self):
        with self.lab_threads.owner():
            super().start()

    def connection_function(self, client, is_running):
        peer = client.getpeername()
        try:
            super().connection_function(client, is_running)
        except Exception as exc:
            frames = []
            traceback = exc.__traceback__
            while traceback:
                frames.append(traceback.tb_frame)
                traceback = traceback.tb_next
            origin = frames[-1]
            readiness_error = (
                peer in self.readiness_peers
                and type(exc) is SSHException
                and str(exc)
                in {
                    "Error reading SSH protocol banner",
                    "Error reading SSH protocol banner[Errno 104] Connection reset by peer",
                }
            )
            auth_error = (
                self.password == REJECTED_LOGIN_PASSWORD
                and type(exc) is AttributeError
                and str(exc) == "'NoneType' object has no attribute 'makefile'"
                and origin.f_code is ParamikoSshServer.connection_function.__code__
                and origin.f_locals.get("channel", False) is None
            )
            if readiness_error or auth_error:
                self.expected_errors.append((peer, repr(exc)))
                return
            self.unexpected_errors.append(repr(exc))
            raise


def _wait_ready(net):
    deadline = time.monotonic() + 5
    for host in net.hosts.values():
        while True:
            try:
                with socket.socket() as probe:
                    probe.settimeout(0.2)
                    probe.bind(("127.0.0.1", 0))
                    host.server.readiness_peers.add(probe.getsockname())
                    probe.connect(("127.0.0.1", host.port))
                break
            except (ConnectionRefusedError, TimeoutError):
                if time.monotonic() >= deadline:
                    raise
                time.sleep(0.02)


def _stop_lab(net, lab_threads):
    servers = [host.server for host in net.hosts.values() if host.server is not None]
    owned_ports = [host.port for host in net.hosts.values() if host.running]
    try:
        net.stop()
    finally:
        # FakeNOS's bounded stop does not cancel a sleeping command handler.
        lab_threads.finish(timeout=SLOW_RESPONSE_DELAY + 3)
        assert not [error for server in servers for error in server.unexpected_errors]
        for port in owned_ports:
            with socket.socket() as probe:
                probe.settimeout(0.2)
                assert probe.connect_ex(("127.0.0.1", port)) != 0


@pytest.fixture(scope="session")
def fake_nos_lab(tmp_path_factory: pytest.TempPathFactory, _lab_threads) -> Iterator[FakeNosLab]:
    log_path = tmp_path_factory.mktemp("fake-nos") / "expected-worker-errors.txt"
    identities = [
        (f"{platform.replace('_', '-')}-{replica}", platform, "healthy")
        for platform in SUPPORTED_PLATFORMS
        for replica in range(HEALTHY_REPLICAS)
    ] + [
        (AUTH_FAILURE_HOST, "cisco_iosxe", "auth_failure"),
        (TIMEOUT_FAILURE_HOST, "cisco_iosxe", "timeout_failure"),
    ]
    for attempt in range(3):
        with ExitStack() as reservations:
            ports = []
            for _ in identities:
                reservation = reservations.enter_context(socket.socket())
                reservation.bind(("127.0.0.1", 0))
                ports.append(reservation.getsockname()[1])
            hosts = tuple(
                FakeHost(name, platform, port, role)
                for (name, platform, role), port in zip(identities, ports, strict=True)
            )
            net = FakeNOS(
                inventory={
                    "default": {
                        "username": USERNAME,
                        "password": PASSWORD,
                        "server": {
                            "plugin": "ParamikoSshServer",
                            "configuration": {"address": "127.0.0.1", "timeout": 1},
                        },
                    },
                    "hosts": {
                        host.name: {
                            "port": host.port,
                            "password": REJECTED_LOGIN_PASSWORD
                            if host.role == "auth_failure"
                            else PASSWORD,
                            "nos": {"plugin": f"functional_{host.platform}"},
                        }
                        for host in hosts
                    },
                },
                plugins=[
                    str(Path(__file__).parent / "nos" / f"{p}.py") for p in SUPPORTED_PLATFORMS
                ],
            )

            def server_factory(**kwargs):
                return _LabServer(lab_threads=_lab_threads, **kwargs)

            net.servers_plugins["ParamikoSshServer"] = server_factory
        try:
            net.start()
            _wait_ready(net)
        except OSError as exc:
            _stop_lab(net, _lab_threads)
            if exc.errno != errno.EADDRINUSE or attempt == 2:
                raise
        except BaseException:
            _stop_lab(net, _lab_threads)
            raise
        else:
            break
    servers = [host.server for host in net.hosts.values()]
    try:
        yield FakeNosLab(hosts, SUPPORTED_PLATFORMS)
    finally:
        try:
            _stop_lab(net, _lab_threads)
        finally:
            log_path.write_text(
                "\n".join(repr(error) for server in servers for error in server.expected_errors)
            )


@pytest.fixture(scope="session")
def functional_inventory_files(
    fake_nos_lab: FakeNosLab, tmp_path_factory: pytest.TempPathFactory
) -> InventoryFiles:
    root = tmp_path_factory.mktemp("functional-inventory")
    files = InventoryFiles(root / "hosts.yaml", root / "groups.yaml", root / "defaults.yaml")
    hosts = {
        host.name: {
            "hostname": "127.0.0.1",
            "port": host.port,
            "platform": host.platform,
            "groups": [host.platform],
            "data": {"role": host.role},
        }
        for host in fake_nos_lab.hosts
    }
    groups = {
        platform: {
            "connection_options": {
                "scrapli": {
                    "platform": platform,
                    "extras": {
                        "transport": "system",
                        "auth_strict_key": False,
                        "ssh_config_file": False,
                        "ssh_known_hosts_file": False,
                        "auth_secondary": PASSWORD,
                        "timeout_socket": 3,
                        "timeout_transport": 5,
                        "timeout_ops": TIMEOUT_OPS,
                    },
                }
            }
        }
        for platform in SUPPORTED_PLATFORMS
    }
    for path, data in (
        (files.hosts, hosts),
        (files.groups, groups),
        (files.defaults, {"username": USERNAME, "password": PASSWORD}),
    ):
        path.write_text(yaml.safe_dump(data))
    return files


@pytest.fixture
def functional_nornir(
    functional_inventory_files: InventoryFiles, fake_nos_lab: FakeNosLab
) -> Iterator[Nornir]:
    files = functional_inventory_files
    nr = InitNornir(
        runner={"plugin": "threaded", "options": {"num_workers": len(fake_nos_lab.hosts)}},
        inventory={
            "plugin": "SimpleInventory",
            "options": {
                "host_file": str(files.hosts),
                "group_file": str(files.groups),
                "defaults_file": str(files.defaults),
            },
        },
        logging={"enabled": False},
    )
    drivers = []
    lock = threading.Lock()

    def track_driver(driver):
        # Called before transport.open(), including rejected/incomplete opens.
        with lock:
            drivers.append(driver)

    for host in nr.inventory.hosts.values():
        options = host.get_connection_parameters("scrapli")
        options.extras = {**options.extras, "on_init": track_driver}
        host.connection_options["scrapli"] = options
    try:
        yield nr
    finally:
        stored = {
            id(plugin.connection): name
            for name, host in nr.inventory.hosts.items()
            for plugin in host.connections.values()
            if hasattr(plugin, "connection")
        }
        for driver in drivers:
            if (
                id(driver) not in stored
                or stored[id(driver)] in nr.data.failed_hosts
                or not driver.isalive()
            ):
                driver.on_close = None
        try:
            # Nornir otherwise records teardown errors without raising them.
            nr.config.core.raise_on_error = True
            nr.close_connections(on_good=True, on_failed=True)
            surviving_healthy = [
                stored[id(driver)]
                for driver in drivers
                if id(driver) in stored
                and stored[id(driver)] not in nr.data.failed_hosts
                and driver.isalive()
            ]
            assert not surviving_healthy, (
                f"Healthy drivers survived normal close: {surviving_healthy}"
            )
        finally:
            try:
                errors = []
                for driver in drivers:
                    # Reclaim orphaned opens; stored healthy drivers kept their CLI close hook.
                    try:
                        if id(driver) not in stored:
                            driver.close()
                        else:
                            driver.transport.close()
                            driver.channel.close()
                        assert not driver.isalive()
                    except Exception as exc:  # noqa: PERF203 - Reclaim every driver after a close failure.
                        errors.append(exc)
                if errors:
                    raise RuntimeError(f"Driver cleanup failed: {errors}") from errors[0]
            finally:
                nr.data.reset_failed_hosts()


@pytest.fixture
def healthy_nornir(functional_nornir: Nornir) -> Nornir:
    return functional_nornir.filter(role="healthy")


@pytest.fixture
def healthy_platform_nornir(functional_nornir: Nornir, platform: str) -> Nornir:
    return functional_nornir.filter(role="healthy", platform=platform)

"""Execution-mode state shared by capability-aware connection plugins."""

from typing import Any, FrozenSet, Optional

from nornir.core.plugins.connections import ConnectionCapability
from nornir_scrapli.exceptions import NornirScrapliConnectionModeError, NornirScrapliException


class ModeBoundConnection:
    """A plugin that chooses one supported execution mode when opening."""

    connection_name: str

    def __init__(self) -> None:
        """Initialize without opening a transport."""
        self.connection: Any = None
        self.mode: Optional[ConnectionCapability] = None

    def get_capabilities(self) -> FrozenSet[ConnectionCapability]:
        """Return the supported opening modes, without device I/O."""
        return frozenset({"sync", "asyncio"})

    def require_mode(self, requested: ConnectionCapability) -> None:
        """Reject access through a different mode from the established connection.

        Args:
            requested: execution mode required by the caller

        Raises:
            NornirScrapliConnectionModeError: if the established mode differs

        """
        if self.mode is not None and self.mode != requested:
            raise NornirScrapliConnectionModeError(
                f"Connection '{self.connection_name}' was opened in {self.mode} mode, "
                f"but {requested} access was requested. Use the matching task/lifecycle "
                "methods, or close the connection and its configuration wrapper before "
                "reopening in the other mode."
            )

    def require_unopened(self, requested: ConnectionCapability) -> None:
        """Reject reopening an established connection.

        Args:
            requested: execution mode required by the caller

        Raises:
            NornirScrapliException: if a connection is already established

        """
        self.require_mode(requested)
        if self.connection is not None:
            raise NornirScrapliException(
                f"Connection '{self.connection_name}' is already open; close it before reopening."
            )

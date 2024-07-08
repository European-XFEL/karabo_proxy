from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class TopologyInfo:
    """Devices, Devices Servers, Clients (instances of ikarabo) and Macros in
    the topology.
    """
    device: Dict[str, Dict[str, Any]]
    server: Dict[str, Dict[str, Any]]
    client: Dict[str, Dict[str, Any]]
    macro: Dict[str, Dict[str, Any]]


@dataclass
class DevicesInfo:
    """Devices in the topology."""
    devices: Dict[str, Dict[str, Any]]

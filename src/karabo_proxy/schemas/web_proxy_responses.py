from dataclasses import dataclass


@dataclass
class WriteResponse:
    """The result of a write operation, like setting a device configuration or
    an injected property."""
    success: bool
    reason: str

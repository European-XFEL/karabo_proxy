from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class WriteResponse:
    """The result of a write operation, like setting a device configuration or
    an injected property."""
    success: bool
    reason: str
    # The execution of slots with parameters returns a reply with the return
    # values of the slot as a dictionary.
    reply: Optional[Dict[str, Any]] = field(default=None)

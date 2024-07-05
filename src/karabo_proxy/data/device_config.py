from dataclasses import dataclass
from typing import Dict, List, Union

PropertyValue = Union[
    None, bool, int, float, str, List[bool], List[int], List[float],
    List[str]]


@dataclass
class PropertyInfo:
    value: PropertyValue
    timestamp: float
    tid: int


DeviceConfigInfo = Dict[str, PropertyInfo]

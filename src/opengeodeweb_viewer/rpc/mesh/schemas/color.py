from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Point:
    x: float
    y: float


@dataclass
class Color:
    name: str
    """Name of the AOI"""

    points: List[Point]
    z: float
    id: Optional[str] = None

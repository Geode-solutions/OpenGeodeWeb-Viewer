# Standard library imports
from dataclasses import dataclass

# Third party imports
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class PolyhedraColorMap:
    id: str
    points: list[list[float]]  # [value, r, g, b]

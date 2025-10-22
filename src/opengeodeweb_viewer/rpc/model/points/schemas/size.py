from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class Size(DataClassJsonMixin):
    id: str
    size: float

from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class Width(DataClassJsonMixin):
    id: str
    width: float

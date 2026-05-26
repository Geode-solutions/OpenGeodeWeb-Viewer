from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class PickColormap(DataClassJsonMixin):
    x: float
    y: float

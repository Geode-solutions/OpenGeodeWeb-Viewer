from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class Axes(DataClassJsonMixin):
    visibility: bool

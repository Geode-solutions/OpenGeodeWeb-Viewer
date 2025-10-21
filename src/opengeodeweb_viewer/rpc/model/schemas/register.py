from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class Register(DataClassJsonMixin):
    id: str

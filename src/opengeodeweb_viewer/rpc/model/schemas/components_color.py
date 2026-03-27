from dataclasses import dataclass
from opengeodeweb_microservice.schemas import Color


@dataclass
class ComponentsColor:
    id: str
    block_ids: list[int]
    color: Color

    @classmethod
    def from_dict(cls, data: dict) -> "ComponentsColor":
        return cls(
            id=data["id"],
            block_ids=data["block_ids"],
            color=Color(**data["color"]),
        )

# Standard library imports
from pathlib import Path

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.typed_rpc import typed_rpc

from . import schemas


class VtkModelLinesAttributeEdgeView(VtkModelView):
    model_lines_attribute_edge_prefix = (
        "opengeodeweb_viewer.model.lines.attribute.edge."
    )
    model_lines_attribute_edge_schemas_dict = get_schemas_dict(
        Path(__file__).parent / "schemas"
    )

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(model_lines_attribute_edge_prefix, schemas.attribute_route)
    def setModelLinesEdgeAttribute(
        self, params: schemas.Attribute
    ) -> schemas.AttributeResponse:
        self.displayAttributeOnCells(
            params.id,
            params.block_ids,
            params.name,
            params.item,
            params.points,
            params.minimum,
            params.maximum,
            params.no_data_color,
        )
        return schemas.AttributeResponse()

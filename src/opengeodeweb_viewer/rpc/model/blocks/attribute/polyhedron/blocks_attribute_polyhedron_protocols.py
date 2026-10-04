# Standard library imports
import os

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.typed_rpc import typed_rpc
from . import schemas


class VtkModelBlocksAttributePolyhedronView(VtkModelView):
    model_blocks_attribute_polyhedron_prefix = (
        "opengeodeweb_viewer.model.blocks.attribute.polyhedron."
    )
    model_blocks_attribute_polyhedron_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(model_blocks_attribute_polyhedron_prefix, schemas.attribute_route)
    def setModelBlocksPolyhedronAttribute(
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

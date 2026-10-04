# Standard library imports
import os

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.typed_rpc import typed_rpc
from . import schemas


class VtkModelCornersAttributeVertexView(VtkModelView):
    model_corners_attribute_vertex_prefix = (
        "opengeodeweb_viewer.model.corners.attribute.vertex."
    )
    model_corners_attribute_vertex_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(model_corners_attribute_vertex_prefix, schemas.attribute_route)
    def setModelCornersVertexAttribute(
        self, params: schemas.Attribute
    ) -> schemas.AttributeResponse:
        self.displayAttributeOnVertices(
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

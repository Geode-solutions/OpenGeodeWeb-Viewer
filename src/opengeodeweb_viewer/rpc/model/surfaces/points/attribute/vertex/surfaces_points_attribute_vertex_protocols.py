# Standard library imports
from pathlib import Path

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.typed_rpc import typed_rpc

from . import schemas


class VtkModelSurfacesPointsAttributeVertexView(VtkModelView):
    model_surfaces_points_attribute_vertex_prefix = (
        "opengeodeweb_viewer.model.surfaces.points.attribute.vertex."
    )
    model_surfaces_points_attribute_vertex_schemas_dict = get_schemas_dict(
        Path(__file__).parent / "schemas"
    )

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(model_surfaces_points_attribute_vertex_prefix, schemas.attribute_route)
    def set_model_surfaces_points_vertex_attribute(
        self, params: schemas.Attribute
    ) -> schemas.AttributeResponse:
        self.set_component_points_attribute(params.id, "surfaces", params.block_ids, params)
        return schemas.AttributeResponse()

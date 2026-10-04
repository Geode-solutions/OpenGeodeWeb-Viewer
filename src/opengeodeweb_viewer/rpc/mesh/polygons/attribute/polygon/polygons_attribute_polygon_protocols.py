# Standard library imports
import os

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.typed_rpc import typed_rpc
from . import schemas


class VtkMeshPolygonsAttributePolygonView(VtkMeshView):
    mesh_polygons_attribute_polygon_prefix = (
        "opengeodeweb_viewer.mesh.polygons.attribute.polygon."
    )
    mesh_polygons_attribute_polygon_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(mesh_polygons_attribute_polygon_prefix, schemas.attribute_route)
    def setMeshPolygonsPolygonAttribute(
        self, params: schemas.Attribute
    ) -> schemas.AttributeResponse:
        self.displayAttributeOnCells(
            params.id,
            params.name,
            params.item,
            params.points,
            params.minimum,
            params.maximum,
            params.no_data_color,
        )
        return schemas.AttributeResponse()

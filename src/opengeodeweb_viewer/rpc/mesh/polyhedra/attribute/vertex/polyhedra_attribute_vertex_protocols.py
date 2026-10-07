# Standard library imports
from pathlib import Path

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.typed_rpc import typed_rpc

from . import schemas


class VtkMeshPolyhedraAttributeVertexView(VtkMeshView):
    mesh_polyhedra_attribute_vertex_prefix = (
        "opengeodeweb_viewer.mesh.polyhedra.attribute.vertex."
    )
    mesh_polyhedra_attribute_vertex_schemas_dict = get_schemas_dict(
        Path(__file__).parent / "schemas"
    )

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(mesh_polyhedra_attribute_vertex_prefix, schemas.attribute_route)
    def setMeshPolyhedraVertexAttribute(
        self, params: schemas.Attribute
    ) -> schemas.AttributeResponse:
        self.displayAttributeOnVertices(
            params.id,
            params.name,
            params.item,
            params.points,
            params.minimum,
            params.maximum,
            params.no_data_color,
        )
        return schemas.AttributeResponse()

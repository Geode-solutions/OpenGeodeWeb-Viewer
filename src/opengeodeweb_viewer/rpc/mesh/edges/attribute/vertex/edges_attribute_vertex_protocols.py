# Standard library imports
from pathlib import Path

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.typed_rpc import typed_rpc

from . import schemas


class VtkMeshEdgesAttributeVertexView(VtkMeshView):
    mesh_edges_attribute_vertex_prefix = "opengeodeweb_viewer.mesh.edges.attribute.vertex."
    mesh_edges_attribute_vertex_schemas_dict = get_schemas_dict(Path(__file__).parent / "schemas")

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(mesh_edges_attribute_vertex_prefix, schemas.attribute_route)
    def set_mesh_edges_vertex_attribute(
        self, params: schemas.Attribute
    ) -> schemas.AttributeResponse:
        self.display_attribute_on_vertices(params.id, params)
        return schemas.AttributeResponse()

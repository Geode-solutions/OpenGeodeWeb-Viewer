# Standard library imports
from pathlib import Path

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.typed_rpc import typed_rpc

from . import schemas


class VtkMeshPolyhedraAttributePolyhedronView(VtkMeshView):
    mesh_polyhedra_attribute_polyhedron_prefix = (
        "opengeodeweb_viewer.mesh.polyhedra.attribute.polyhedron."
    )
    mesh_polyhedra_attribute_polyhedron_schemas_dict = get_schemas_dict(
        Path(__file__).parent / "schemas"
    )

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(mesh_polyhedra_attribute_polyhedron_prefix, schemas.attribute_route)
    def setMeshPolyhedraPolyhedronAttribute(
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

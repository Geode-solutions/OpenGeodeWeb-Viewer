# Standard library imports
from pathlib import Path

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.typed_rpc import typed_rpc

from . import schemas


class VtkModelSurfacesAttributePolygonView(VtkModelView):
    model_surfaces_attribute_polygon_prefix = (
        "opengeodeweb_viewer.model.surfaces.attribute.polygon."
    )
    model_surfaces_attribute_polygon_schemas_dict = get_schemas_dict(
        Path(__file__).parent / "schemas"
    )

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(model_surfaces_attribute_polygon_prefix, schemas.attribute_route)
    def setModelSurfacesPolygonAttribute(
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

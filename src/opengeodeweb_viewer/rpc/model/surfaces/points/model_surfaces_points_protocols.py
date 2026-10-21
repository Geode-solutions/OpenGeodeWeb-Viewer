# Standard library imports
from pathlib import Path

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.typed_rpc import typed_rpc

from . import schemas


class VtkModelSurfacesPointsView(VtkModelView):
    model_surfaces_points_prefix = "opengeodeweb_viewer.model.surfaces.points."
    model_surfaces_points_schemas_dict = get_schemas_dict(Path(__file__).parent / "schemas")

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(model_surfaces_points_prefix, schemas.visibility_route)
    def set_model_surfaces_points_visibility(
        self, params: schemas.Visibility
    ) -> schemas.VisibilityResponse:
        self.set_component_points_visibility(
            params.id, "surfaces", params.block_ids, visibility=params.visibility
        )
        return schemas.VisibilityResponse()

    @typed_rpc(model_surfaces_points_prefix, schemas.color_route)
    def set_model_surfaces_points_color(self, params: schemas.Color) -> schemas.ColorResponse:
        self.set_component_points_color(params.id, "surfaces", params.block_ids, params.color)
        return schemas.ColorResponse()

    @typed_rpc(model_surfaces_points_prefix, schemas.size_route)
    def set_model_surfaces_points_size(self, params: schemas.Size) -> schemas.SizeResponse:
        self.set_component_points_size(params.id, "surfaces", params.block_ids, params.size)
        return schemas.SizeResponse()

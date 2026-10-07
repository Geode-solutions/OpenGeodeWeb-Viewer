# Standard library imports
from pathlib import Path

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.typed_rpc import typed_rpc

from . import schemas


class VtkModelBlocksView(VtkModelView):
    model_blocks_prefix = "opengeodeweb_viewer.model.blocks."
    model_blocks_schemas_dict = get_schemas_dict(Path(__file__).parent / "schemas")

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(model_blocks_prefix, schemas.visibility_route)
    def set_model_blocks_polyhedra_visibility(
        self, params: schemas.Visibility
    ) -> schemas.VisibilityResponse:
        self.set_blocks_visibility(params.id, params.block_ids, visibility=params.visibility)
        return schemas.VisibilityResponse()

    @typed_rpc(model_blocks_prefix, schemas.color_route)
    def set_model_blocks_color(self, params: schemas.Color) -> schemas.ColorResponse:
        pipeline = self.get_vtk_pipeline(params.id)
        colors = self.apply_color(
            pipeline,
            params.block_ids,
            params.color_mode.value,
            params.color,
            params.collection_id,
        )
        return schemas.ColorResponse.from_dict({"colors": colors})

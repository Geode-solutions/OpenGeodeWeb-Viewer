# Standard library imports
import os

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.typed_rpc import typed_rpc
from . import schemas


class VtkModelLinesView(VtkModelView):
    model_lines_prefix = "opengeodeweb_viewer.model.lines."
    model_lines_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(model_lines_prefix, schemas.visibility_route)
    def setModelLinesEdgesVisibility(
        self, params: schemas.Visibility
    ) -> schemas.VisibilityResponse:
        self.SetBlocksVisibility(params.id, params.block_ids, params.visibility)
        return schemas.VisibilityResponse()

    @typed_rpc(model_lines_prefix, schemas.color_route)
    def setModelLinesColor(self, params: schemas.Color) -> schemas.ColorResponse:
        pipeline = self.get_vtk_pipeline(params.id)
        colors = self.apply_color(
            pipeline,
            params.block_ids,
            params.color_mode.value,
            params.color,
            params.collection_id,
        )
        return schemas.ColorResponse.from_dict({"colors": colors})

# Standard library imports
from pathlib import Path

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.typed_rpc import typed_rpc

from . import schemas


class VtkModelBlocksEdgesView(VtkModelView):
    model_blocks_edges_prefix = "opengeodeweb_viewer.model.blocks.edges."
    model_blocks_edges_schemas_dict = get_schemas_dict(Path(__file__).parent / "schemas")

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(model_blocks_edges_prefix, schemas.visibility_route)
    def set_model_blocks_edges_visibility(
        self, params: schemas.Visibility
    ) -> schemas.VisibilityResponse:
        self.set_component_edges_visibility(
            params.id, "blocks", params.block_ids, visibility=params.visibility
        )
        return schemas.VisibilityResponse()

    @typed_rpc(model_blocks_edges_prefix, schemas.color_route)
    def set_model_blocks_edges_color(self, params: schemas.Color) -> schemas.ColorResponse:
        self.set_component_edges_color(params.id, "blocks", params.block_ids, params.color)
        return schemas.ColorResponse()

    @typed_rpc(model_blocks_edges_prefix, schemas.width_route)
    def set_model_blocks_edges_width(self, params: schemas.Width) -> schemas.WidthResponse:
        self.set_component_edges_width(params.id, "blocks", params.block_ids, params.width)
        return schemas.WidthResponse()

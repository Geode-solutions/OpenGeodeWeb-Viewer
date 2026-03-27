# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.utils_functions import validate_schema, RpcParams
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from . import schemas


class VtkModelBlocksEdgesView(VtkModelView):
    model_blocks_edges_prefix = "opengeodeweb_viewer.model.blocks.edges."
    model_blocks_edges_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(
        model_blocks_edges_prefix + model_blocks_edges_schemas_dict["visibility"]["rpc"]
    )
    def setModelBlocksEdgesVisibility(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.model_blocks_edges_schemas_dict["visibility"],
            self.model_blocks_edges_prefix,
        )
        params = schemas.Visibility.from_dict(rpc_params)
        self.SetEdgesVisibility(params.id, params.visibility)

    @exportRpc(
        model_blocks_edges_prefix + model_blocks_edges_schemas_dict["color"]["rpc"]
    )
    def setModelBlocksEdgesColor(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.model_blocks_edges_schemas_dict["color"],
            self.model_blocks_edges_prefix,
        )
        params = schemas.Color.from_dict(rpc_params)
        self.SetEdgesColor(params.id, params.color.r, params.color.g, params.color.b)

    @exportRpc(
        model_blocks_edges_prefix + model_blocks_edges_schemas_dict["width"]["rpc"]
    )
    def setModelBlocksEdgesWidth(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.model_blocks_edges_schemas_dict["width"],
            self.model_blocks_edges_prefix,
        )
        params = schemas.Width.from_dict(rpc_params)
        self.SetEdgesWidth(params.id, params.width)

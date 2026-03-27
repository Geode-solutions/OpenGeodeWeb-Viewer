# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc  # type: ignore
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.utils_functions import validate_schema, RpcParams
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from . import schemas


class VtkModelBlocksView(VtkModelView):
    model_blocks_prefix = "opengeodeweb_viewer.model.blocks."
    model_blocks_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(
        model_blocks_prefix + model_blocks_schemas_dict["edges_visibility"]["rpc"]
    )
    def setModelBlocksEdgesVisibility(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.model_blocks_schemas_dict["edges_visibility"],
            self.model_blocks_prefix,
        )
        params = schemas.Visibility.from_dict(rpc_params)
        self.SetCategoryEdgesVisibility(params.id, "blocks", params.visibility)

    @exportRpc(
        model_blocks_prefix + model_blocks_schemas_dict["points_visibility"]["rpc"]
    )
    def setModelBlocksPointsVisibility(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.model_blocks_schemas_dict["points_visibility"],
            self.model_blocks_prefix,
        )
        params = schemas.Visibility.from_dict(rpc_params)
        self.SetCategoryPointsVisibility(params.id, "blocks", params.visibility)

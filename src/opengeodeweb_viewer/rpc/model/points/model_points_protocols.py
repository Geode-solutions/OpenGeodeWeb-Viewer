# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc  # type: ignore
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.utils_functions import (
    validate_schema,
    RpcParams,
)
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from . import schemas


class VtkModelPointsView(VtkModelView):
    model_points_prefix = "opengeodeweb_viewer.model.points."
    model_points_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(model_points_prefix + model_points_schemas_dict["visibility"]["rpc"])
    def setModelPointsVisibility(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.model_points_schemas_dict["visibility"],
            self.model_points_prefix,
        )
        params = schemas.Visibility.from_dict(rpc_params)
        self.SetPointsVisibility(params.id, params.visibility)

    @exportRpc(model_points_prefix + model_points_schemas_dict["size"]["rpc"])
    def setModelPointsSize(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.model_points_schemas_dict["size"], self.model_points_prefix
        )
        params = schemas.Size.from_dict(rpc_params)
        self.SetPointsSize(params.id, params.size)

import os
from wslink import register as exportRpc
from opengeodeweb_microservice.schemas import get_schemas_dict
from opengeodeweb_viewer.utils_functions import validate_schema, RpcParams
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from . import schemas


class VtkModelLinesPointsView(VtkModelView):
    model_lines_points_prefix = "opengeodeweb_viewer.model.lines.points."
    model_lines_points_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(model_lines_points_prefix + model_lines_points_schemas_dict["visibility"]["rpc"])
    def setModelLinesPointsVisibility(self, rpc_params: RpcParams) -> None:
        validate_schema(rpc_params, self.model_lines_points_schemas_dict["visibility"], self.model_lines_points_prefix)
        params = schemas.Visibility.from_dict(rpc_params)
        self.SetPointsVisibility(params.id, params.visibility)

    @exportRpc(model_lines_points_prefix + model_lines_points_schemas_dict["size"]["rpc"])
    def setModelLinesPointsSize(self, rpc_params: RpcParams) -> None:
        validate_schema(rpc_params, self.model_lines_points_schemas_dict["size"], self.model_lines_points_prefix)
        params = schemas.Size.from_dict(rpc_params)
        self.SetPointsSize(params.id, params.size)

    @exportRpc(model_lines_points_prefix + model_lines_points_schemas_dict["color"]["rpc"])
    def setModelLinesPointsColor(self, rpc_params: RpcParams) -> None:
        validate_schema(rpc_params, self.model_lines_points_schemas_dict["color"], self.model_lines_points_prefix)
        params = schemas.Color.from_dict(rpc_params)
        self.SetPointsColor(params.id, params.color.r, params.color.g, params.color.b)
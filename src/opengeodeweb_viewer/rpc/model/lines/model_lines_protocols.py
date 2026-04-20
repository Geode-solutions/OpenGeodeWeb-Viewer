# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc  # type: ignore
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.utils_functions import validate_schema, RpcParams
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView, ColorResult
from . import schemas


class VtkModelLinesView(VtkModelView):
    model_lines_prefix = "opengeodeweb_viewer.model.lines."
    model_lines_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(model_lines_prefix + model_lines_schemas_dict["visibility"]["rpc"])
    def setModelLinesEdgesVisibility(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.model_lines_schemas_dict["visibility"],
            self.model_lines_prefix,
        )
        params = schemas.Visibility.from_dict(rpc_params)
        self.SetBlocksVisibility(params.id, params.block_ids, params.visibility)

    @exportRpc(model_lines_prefix + model_lines_schemas_dict["color"]["rpc"])
    def setModelLinesColor(self, rpc_params: RpcParams) -> list[ColorResult]:
        validate_schema(
            rpc_params,
            self.model_lines_schemas_dict["color"],
            self.model_lines_prefix,
        )
        params = schemas.Color.from_dict(rpc_params)
        pipeline = self.get_vtk_pipeline(params.id)
        return self.apply_color(
            pipeline, params.block_ids, params.color_mode.value, params.color
        )

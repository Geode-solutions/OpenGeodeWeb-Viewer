# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView


class VtkModelLinesView(VtkModelView):
    model_lines_prefix = "opengeodeweb_viewer.model.lines."
    model_lines_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self):
        super().__init__()

    @exportRpc(model_lines_prefix + model_lines_schemas_dict["visibility"]["rpc"])
    def setModelLinesEdgesVisibility(self, params):
        validate_schema(
            params,
            self.model_lines_schemas_dict["visibility"],
            self.model_lines_prefix,
        )
        id, block_ids, visibility = (
            params["id"],
            params["block_ids"],
            params["visibility"],
        )
        self.SetBlocksVisibility(id, block_ids, visibility)

    @exportRpc(model_lines_prefix + model_lines_schemas_dict["color"]["rpc"])
    def setModelLinesEdgesColor(self, params):
        validate_schema(
            params,
            self.model_lines_schemas_dict["color"],
            self.model_lines_prefix,
        )
        id, block_ids, red, green, blue = (
            params["id"],
            params["block_ids"],
            params["color"]["r"],
            params["color"]["g"],
            params["color"]["b"],
        )
        self.SetBlocksColor(id, block_ids, red, green, blue)

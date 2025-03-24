# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView


class VtkModelCornersView(VtkModelView):
    model_corners_prefix = "opengeodeweb_viewer.model.corners."
    model_corners_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self):
        super().__init__()

    @exportRpc(model_corners_prefix + model_corners_schemas_dict["visibility"]["rpc"])
    def setModelCornersPointsVisibility(self, params):
        validate_schema(
            params,
            self.model_corners_schemas_dict["visibility"],
            self.model_corners_prefix,
        )
        id, block_ids, visibility = (
            params["id"],
            params["block_ids"],
            params["visibility"],
        )
        self.SetBlocksVisibility(id, block_ids, visibility)

    @exportRpc(model_corners_prefix + model_corners_schemas_dict["color"]["rpc"])
    def setModelCornersPointsColor(self, params):
        validate_schema(
            params,
            self.model_corners_schemas_dict["color"],
            self.model_corners_prefix,
        )
        id, block_ids, red, green, blue = (
            params["id"],
            params["block_ids"],
            params["color"]["r"],
            params["color"]["g"],
            params["color"]["b"],
        )
        self.SetBlocksColor(id, block_ids, red, green, blue)

# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView

class VtkModelCornersPointsView(VtkModelView):
    model_corners_points_prefix = "opengeodeweb_viewer.model.corners.points."
    model_corners_points_schemas_dict = get_schemas_dict(os.path.join(os.path.dirname(__file__), "schemas"))

    def __init__(self):
        super().__init__()

    @exportRpc(model_corners_points_prefix + model_corners_points_schemas_dict["visibility"]["rpc"])
    def setCornersPointsSize(self, params):
        print(self.model_corners_points_prefix + self.model_corners_points_schemas_dict["visibility"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.model_corners_points_schemas_dict["visibility"])
        id, block_ids, visibility = params["id"], params["block_ids"], params["visibility"]
        self.SetBlocksVisibility(id, block_ids, visibility)
    
    # @exportRpc(model_corners_points_prefix + model_corners_points_schemas_dict["size"]["rpc"])
    # def setCornersPointsSize(self, params):
    #     print(self.model_corners_points_prefix + self.model_corners_points_schemas_dict["size"]["rpc"], f"{params=}", flush=True)
    #     validate_schema(params, self.model_corners_points_schemas_dict["size"])
    #     id, block_ids, size = params["id"], params["block_ids"], params["size"]
    #     self.setBlockPointsSize(id, block_ids, size)

    # @exportRpc(model_corners_points_prefix + model_corners_points_schemas_dict["color"]["rpc"])
    # def setCornersPointsColor(self, params):
    #     print(self.model_corners_points_prefix + self.model_corners_points_schemas_dict["color"]["rpc"], f"{params=}", flush=True)
    #     validate_schema(params, self.model_corners_points_schemas_dict["color"])
    #     id, block_ids = params["id"], params["block_ids"]
    #     red, green, blue = params["color"]["r"], params["color"]["g"], params["color"]["b"]
    #     self.setBlockPointsColor(id, block_ids, red, green, blue)


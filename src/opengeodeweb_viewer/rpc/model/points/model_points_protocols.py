# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView


class VtkModelPointsView(VtkModelView):
    model_points_prefix = "opengeodeweb_viewer.model.points."
    model_points_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self):
        super().__init__()

    @exportRpc(model_points_prefix + model_points_schemas_dict["visibility"]["rpc"])
    def setModelPointsVisibility(self, params):
        validate_schema(
            params,
            self.model_points_schemas_dict["visibility"],
            self.model_points_prefix,
        )
        id, visibility = params["id"], params["visibility"]
        self.SetPointsVisibility(id, visibility)

    @exportRpc(model_points_prefix + model_points_schemas_dict["size"]["rpc"])
    def setModelPointsSize(self, params):
        validate_schema(
            params, self.model_points_schemas_dict["size"], self.model_points_prefix
        )
        id, size = params["id"], params["size"]
        self.SetPointsSize(id, size)

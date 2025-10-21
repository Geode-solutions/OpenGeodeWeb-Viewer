# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from . import schemas


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
        params = schemas.Visibility.from_dict(params)
        self.SetPointsVisibility(params.id, params.visibility)

    @exportRpc(model_points_prefix + model_points_schemas_dict["size"]["rpc"])
    def setModelPointsSize(self, params):
        validate_schema(
            params, self.model_points_schemas_dict["size"], self.model_points_prefix
        )
        params = schemas.Size.from_dict(params)
        self.SetPointsSize(params.id, params.size)

# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView


class VtkModelEdgesView(VtkModelView):
    model_edges_prefix = "opengeodeweb_viewer.model.edges."
    model_edges_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self):
        super().__init__()

    @exportRpc(model_edges_prefix + model_edges_schemas_dict["visibility"]["rpc"])
    def setModelEdgesVisibility(self, params):
        validate_schema(
            params, self.model_edges_schemas_dict["visibility"], self.model_edges_prefix
        )
        id, visibility = params["id"], params["visibility"]
        self.SetEdgesVisibility(id, visibility)

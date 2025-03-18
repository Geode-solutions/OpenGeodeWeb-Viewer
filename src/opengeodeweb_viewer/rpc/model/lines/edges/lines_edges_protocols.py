# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView


class VtkModelLinesEdgesView(VtkModelView):
    model_lines_edges_prefix = "opengeodeweb_viewer.model.lines.edges."
    model_lines_edges_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self):
        super().__init__()

    @exportRpc(
        model_lines_edges_prefix + model_lines_edges_schemas_dict["visibility"]["rpc"]
    )
    def setModelSurfacesPolygonsVisibility(self, params):
        print(
            self.model_lines_edges_prefix
            + self.model_lines_edges_schemas_dict["visibility"]["rpc"],
            f"{params=}",
            flush=True,
        )
        validate_schema(params, self.model_lines_edges_schemas_dict["visibility"])
        id, block_ids, visibility = (
            params["id"],
            params["block_ids"],
            params["visibility"],
        )
        self.SetBlocksVisibility(id, block_ids, visibility)

# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView


class VtkModelSurfacesPolygonsView(VtkModelView):
    model_surfaces_polygons_prefix = "opengeodeweb_viewer.model.surfaces.polygons."
    model_surfaces_polygons_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self):
        super().__init__()

    @exportRpc(
        model_surfaces_polygons_prefix
        + model_surfaces_polygons_schemas_dict["visibility"]["rpc"]
    )
    def setModelSurfacesPolygonsVisibility(self, params):
        print(
            self.model_surfaces_polygons_prefix
            + self.model_surfaces_polygons_schemas_dict["visibility"]["rpc"],
            f"{params=}",
            flush=True,
        )
        validate_schema(params, self.model_surfaces_polygons_schemas_dict["visibility"])
        id, block_ids, visibility = (
            params["id"],
            params["block_ids"],
            params["visibility"],
        )
        self.SetBlocksVisibility(id, block_ids, visibility)

    @exportRpc(
        model_surfaces_polygons_prefix
        + model_surfaces_polygons_schemas_dict["color"]["rpc"]
    )
    def setModelSurfacesPolygonsCOlor(self, params):
        print(
            self.model_surfaces_polygons_prefix
            + self.model_surfaces_polygons_schemas_dict["color"]["rpc"],
            f"{params=}",
            flush=True,
        )
        validate_schema(params, self.model_surfaces_polygons_schemas_dict["color"])
        id, block_ids, red, green, blue = (
            params["id"],
            params["block_ids"],
            params["color"]["r"],
            params["color"]["g"],
            params["color"]["b"],
        )
        self.SetBlocksColor(id, block_ids, red, green, blue)

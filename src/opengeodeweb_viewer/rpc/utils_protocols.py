# Standard library imports
import os

# Third party imports
import vtk
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.vtk_protocol import VtkView


class VtkUtilsView(VtkView):
    mesh_prefix = "opengeodeweb_viewer.utils"
    mesh_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(mesh_prefix + mesh_schemas_dict["kill"]["rpc"])
    def kill(self, params) -> None:
        validate_schema(params, self.mesh_schemas_dict["kill"], self.mesh_prefix)
        print("Manual viewer kill, shutting down...", flush=True)
        os._exit(0)

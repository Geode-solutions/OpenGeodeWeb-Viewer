# type: ignore
# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict
from opengeodeweb_viewer.vtk_protocol import VtkView


class VtkUtilsView(VtkView):
    ogw_prefix = "opengeodeweb_viewer."
    ogw_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(ogw_prefix + ogw_schemas_dict["kill"]["rpc"])
    def kill(self) -> None:
        print("Manual viewer kill, shutting down...", flush=True)
        os._exit(0)

# Standard library imports
import os
import asyncio

# Third party imports
from wslink import register as exportRpc, server  # type: ignore

# Local application imports
from opengeodeweb_microservice.schemas import get_schemas_dict
from opengeodeweb_viewer.vtk_protocol import VtkView


class VtkUtilsView(VtkView):
    utils_prefix = "opengeodeweb_viewer."
    utils_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(utils_prefix + utils_schemas_dict["kill"]["rpc"])
    async def kill(self) -> None:
        print("Manual viewer kill, shutting down...", flush=True)
        await server.stop_webserver()
        os._exit(0)

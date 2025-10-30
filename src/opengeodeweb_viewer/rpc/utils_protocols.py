# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc  # type: ignore

# Local application imports
from opengeodeweb_microservice.schemas import get_schemas_dict
from opengeodeweb_viewer.vtk_protocol import VtkView
from opengeodeweb_microservice.database import connection


class VtkUtilsView(VtkView):
    utils_prefix = "opengeodeweb_viewer."
    utils_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(utils_prefix + utils_schemas_dict["kill"]["rpc"])
    def kill(self) -> None:
        print(
            f"{self.utils_prefix + self.utils_schemas_dict['kill']['rpc']}", flush=True
        )
        print("Manual viewer kill, shutting down...", flush=True)
        os._exit(0)

    @exportRpc(utils_prefix + utils_schemas_dict["reset_project"]["rpc"])
    def resetProject(self, rpc_params: dict | None = None) -> None:
        print(
            f"{self.utils_prefix + self.utils_schemas_dict['reset_project']['rpc']}",
            flush=True,
        )
        renderWindow = self.getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()

        renderer.RemoveAllViewProps()

        widget = self.get_widget()
        if widget is not None:
            try:
                widget.EnabledOff()
            except Exception:
                pass
        self.coreServer.setSharedObject("widget", None)
        self.coreServer.setSharedObject("grid_scale", None)
        self.coreServer.setSharedObject("axes", None)

        self.get_data_base().clear()

        # Clean up any existing database session
        if connection.scoped_session_registry is not None:
            connection.scoped_session_registry.remove()
        if connection.engine is not None:
            connection.engine.dispose()
        # Reset all connection attributes to None
        connection.engine = connection.session_factory = connection.scoped_session_registry = None

        db_full_path = os.path.join(self.DATA_FOLDER_PATH, "project.db")
        connection.init_database(db_full_path, create_tables=False)

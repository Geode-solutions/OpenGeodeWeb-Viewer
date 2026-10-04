# Standard library imports
import os
from threading import Timer

# Third party imports

# Local application imports
from opengeodeweb_microservice.schemas import get_schemas_dict
from opengeodeweb_viewer.vtk_protocol import VtkView
from opengeodeweb_microservice.database import connection
from opengeodeweb_viewer.typed_rpc import typed_rpc
from . import schemas


class VtkUtilsView(VtkView):
    utils_prefix = "opengeodeweb_viewer."
    utils_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(utils_prefix, schemas.kill_route)
    def kill(self, params: schemas.Kill) -> schemas.KillResponse:
        print("Manual viewer kill, shutting down...", flush=True)
        Timer(0.5, os._exit, [0]).start()
        return schemas.KillResponse()

    @typed_rpc(utils_prefix, schemas.import_project_route)
    def importProject(
        self, params: schemas.ImportProject
    ) -> schemas.ImportProjectResponse:
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

        self._release_database()

        db_full_path = os.path.join(self.DATA_FOLDER_PATH, "project.db")
        connection.init_database(db_full_path, create_tables=False)
        return schemas.ImportProjectResponse()

    @typed_rpc(utils_prefix, schemas.release_database_route)
    def releaseDatabase(
        self, params: schemas.ReleaseDatabase
    ) -> schemas.ReleaseDatabaseResponse:
        self._release_database()
        return schemas.ReleaseDatabaseResponse()

    def _release_database(self) -> None:
        if connection.scoped_session_registry is not None:
            connection.scoped_session_registry.remove()
        if connection.engine is not None:
            connection.engine.dispose()
        connection.engine = connection.session_factory = (
            connection.scoped_session_registry
        ) = None

# Standard library imports
import contextlib
import logging
import os
from pathlib import Path
from threading import Timer

from opengeodeweb_microservice.database import connection

# Third party imports
# Local application imports
from opengeodeweb_microservice.schemas import get_schemas_dict

from opengeodeweb_viewer.typed_rpc import typed_rpc
from opengeodeweb_viewer.vtk_protocol import VtkView

from . import schemas

logger = logging.getLogger(__name__)


class VtkUtilsView(VtkView):
    utils_prefix = "opengeodeweb_viewer."
    utils_schemas_dict = get_schemas_dict(Path(__file__).parent / "schemas")

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(utils_prefix, schemas.kill_route)
    def kill(self, _params: schemas.Kill) -> schemas.KillResponse:
        logger.info("Manual viewer kill, shutting down...")
        Timer(0.5, os._exit, [0]).start()
        return schemas.KillResponse()

    @typed_rpc(utils_prefix, schemas.import_project_route)
    def import_project(self, _params: schemas.ImportProject) -> schemas.ImportProjectResponse:
        widget = self.get_widget()
        if widget is not None:
            with contextlib.suppress(Exception):
                widget.EnabledOff()
        self.coreServer.setSharedObject("widget", None)
        self.coreServer.setSharedObject("grid_scale", None)
        self.coreServer.setSharedObject("axes", None)

        self.get_data_base().clear()

        self._release_database()

        db_full_path = Path(self.DATA_FOLDER_PATH) / "project.db"
        connection.init_database(db_full_path, create_tables=False)
        return schemas.ImportProjectResponse()

    @typed_rpc(utils_prefix, schemas.release_database_route)
    def release_database(self, _params: schemas.ReleaseDatabase) -> schemas.ReleaseDatabaseResponse:
        self._release_database()
        return schemas.ReleaseDatabaseResponse()

    def _release_database(self) -> None:
        connection.close_database()

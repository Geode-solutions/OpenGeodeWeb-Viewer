# Standard library imports
import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

from opengeodeweb_microservice.database import connection
from vtkmodules.vtkCommonCore import vtkFileOutputWindow, vtkOutputWindow
from vtkmodules.vtkRenderingCore import vtkRenderer, vtkRenderWindow
from vtkmodules.web import protocols as vtk_protocols

# Third party imports
from vtkmodules.web.wslink import ServerProtocol
from wslink import server  # type: ignore[import-untyped]

# Local application imports
from opengeodeweb_viewer.config import Config, DevConfig, ProdConfig, TestConfig
from opengeodeweb_viewer.rpc.generic.generic_protocols import VtkGenericView
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.rpc.protocols import MESH_PROTOCOLS, MODEL_PROTOCOLS
from opengeodeweb_viewer.rpc.utils_protocols import VtkUtilsView
from opengeodeweb_viewer.rpc.viewer.viewer_protocols import VtkViewerView
from opengeodeweb_viewer.vtk_protocol import VtkTypingMixin, VtkView

# =============================================================================
# Server class
# =============================================================================


logger = logging.getLogger(__name__)


class _Server(VtkTypingMixin, ServerProtocol):
    # Defaults
    authKey = "wslink-secret"  # noqa: N815 wslink option name
    view = None
    debug = False

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--project_folder_path",
            help="Path to the folder where data is stored",
        )

    @staticmethod
    def configure(args: argparse.Namespace) -> None:
        # Standard args
        _Server.authKey = args.authKey

    def initialize(self) -> None:
        # Bring used components
        self.registerVtkWebProtocol(vtk_protocols.vtkWebMouseHandler())
        self.registerVtkWebProtocol(vtk_protocols.vtkWebViewPort())
        publisher = vtk_protocols.vtkWebPublishImageDelivery(decode=False)  # type: ignore[no-untyped-call]
        publisher.deltaStaleTimeBeforeRender = 0.1
        self.registerVtkWebProtocol(publisher)
        self.setSharedObject("db", {})
        self.setSharedObject("publisher", publisher)

        # Custom API
        mesh_protocols = VtkMeshView()
        model_protocols = VtkModelView()
        self.registerVtkWebProtocol(VtkView())
        self.registerVtkWebProtocol(VtkUtilsView())
        self.registerVtkWebProtocol(VtkViewerView())
        self.registerVtkWebProtocol(mesh_protocols)
        for protocol_class in MESH_PROTOCOLS:
            self.registerVtkWebProtocol(protocol_class())
        self.registerVtkWebProtocol(model_protocols)
        for protocol_class in MODEL_PROTOCOLS:
            self.registerVtkWebProtocol(protocol_class())
        self.registerVtkWebProtocol(VtkGenericView(mesh_protocols, model_protocols))

        # tell the C++ web app to use no encoding.
        # ParaViewWebPublishImageDelivery must be set to decode=False to match.
        self.getApplication().SetImageEncoding(0)

        # Update authentication key to use
        self.updateSecret(_Server.authKey)

        err_out = vtkFileOutputWindow()
        err_out.SetFileName("VTK.txt")
        vtk_std_err_out = vtkOutputWindow()
        vtk_std_err_out.SetInstance(err_out)

        if not _Server.view:
            renderer = vtkRenderer()
            render_window = vtkRenderWindow()
            render_window.AddRenderer(renderer)
            self.setSharedObject("renderer", renderer)
            self.getApplication().GetObjectIdMap().SetActiveObject("VIEW", render_window)

            render_window.SetOffScreenRendering(not _Server.debug)


# =============================================================================
# Main: Parse args and start serverviewId
# =============================================================================


def _configure_logging(python_env: str) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    package_logger = logging.getLogger("opengeodeweb_viewer")
    package_logger.addHandler(handler)
    package_logger.propagate = False
    package_logger.setLevel(logging.DEBUG if python_env in ("dev", "test") else logging.INFO)


def run_server(server_protocol: type[ServerProtocol] = _Server) -> None:
    parser = argparse.ArgumentParser(description="Vtk server")
    server.add_arguments(parser)
    parser.set_defaults(port=None, host=None)
    server_protocol.add_arguments(parser)
    args = parser.parse_args()

    if args.project_folder_path is None:
        msg = "project_folder_path must be provided"
        raise ValueError(msg)
    args.project_folder_path = str(Path(args.project_folder_path).resolve())

    python_env = os.environ.get("PYTHON_ENV", "prod").strip().lower()
    _configure_logging(python_env)

    app_config: Config
    if python_env == "prod":
        app_config = ProdConfig(args.project_folder_path)
    elif python_env == "dev":
        app_config = DevConfig(args.project_folder_path)
    elif python_env == "test":
        app_config = TestConfig(args.project_folder_path)
    else:
        msg = f"Unknown PYTHON_ENV: {python_env!r}"
        raise ValueError(msg)

    if args.host is not None:
        app_config.HOST = str(args.host)
    else:
        args.host = app_config.HOST

    if args.port is not None:
        app_config.PORT = str(args.port)
    else:
        args.port = app_config.PORT

    app_config.sync_env()

    db_full_path = Path(os.environ["DATA_FOLDER_PATH"]) / "project.db"
    connection.init_database(db_full_path, create_tables=False)
    logger.info("Viewer connected to database at: %s", db_full_path)

    logger.info("args=%s", args)
    server_protocol.configure(args)
    # Python 3.14 no longer creates a default event loop, which wslink 1.x expects
    asyncio.set_event_loop(asyncio.new_event_loop())
    server.start_webserver(options=args, protocol=server_protocol)


if __name__ == "__main__":
    run_server()

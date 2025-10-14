# Standard library imports
import argparse
import os

# Third party imports
import vtk
from vtk.web import wslink as vtk_wslink
from vtk.web import protocols as vtk_protocols
from wslink import server
from opengeodeweb_microservice.database import connection

# Local application imports
from .config import *
from .vtk_protocol import VtkView
from .rpc.viewer.viewer_protocols import VtkViewerView
from .rpc.mesh.mesh_protocols import VtkMeshView
from .rpc.mesh.points.mesh_points_protocols import VtkMeshPointsView
from .rpc.mesh.edges.mesh_edges_protocols import VtkMeshEdgesView
from .rpc.mesh.polygons.polygons_protocols import VtkMeshPolygonsView
from .rpc.mesh.polyhedra.polyhedra_protocols import VtkMeshPolyhedraView
from .rpc.model.model_protocols import VtkModelView
from .rpc.model.edges.model_edges_protocols import (
    VtkModelEdgesView,
)
from .rpc.model.points.model_points_protocols import (
    VtkModelPointsView,
)
from .rpc.model.corners.model_corners_protocols import (
    VtkModelCornersView,
)
from .rpc.model.lines.model_lines_protocols import (
    VtkModelLinesView,
)
from .rpc.model.surfaces.model_surfaces_protocols import (
    VtkModelSurfacesView,
)
from .rpc.model.blocks.model_blocks_protocols import (
    VtkModelBlocksView,
)
from .rpc.generic.generic_protocols import VtkGenericView
from .rpc.utils_protocols import VtkUtilsView  # type: ignore


# =============================================================================
# Server class
# =============================================================================


class _Server(vtk_wslink.ServerProtocol):
    # Defaults
    authKey = "wslink-secret"
    view = None
    debug = False

    @staticmethod
    def add_arguments(parser):
        parser.add_argument(
            "--data_folder_path",
            default=os.environ.get("DATA_FOLDER_PATH"),
            help="Path to the folder where data is stored",
        )

    @staticmethod
    def configure(args):
        # Standard args
        _Server.authKey = args.authKey

    def initialize(self):
        # Bring used components
        self.registerVtkWebProtocol(vtk_protocols.vtkWebMouseHandler())
        self.registerVtkWebProtocol(vtk_protocols.vtkWebViewPort())
        publisher = vtk_protocols.vtkWebPublishImageDelivery(decode=False)
        publisher.deltaStaleTimeBeforeRender = 0.1
        self.registerVtkWebProtocol(publisher)
        self.setSharedObject("db", dict())
        self.setSharedObject("publisher", publisher)

        # Custom API
        mesh_protocols = VtkMeshView()
        model_protocols = VtkModelView()
        vtk_view = VtkView()
        self.registerVtkWebProtocol(vtk_view)
        self.registerVtkWebProtocol(VtkUtilsView())
        self.registerVtkWebProtocol(VtkViewerView())
        self.registerVtkWebProtocol(mesh_protocols)
        self.registerVtkWebProtocol(VtkMeshPointsView())
        self.registerVtkWebProtocol(VtkMeshEdgesView())
        self.registerVtkWebProtocol(VtkMeshPolygonsView())
        self.registerVtkWebProtocol(VtkMeshPolyhedraView())
        self.registerVtkWebProtocol(model_protocols)
        self.registerVtkWebProtocol(VtkModelEdgesView())
        self.registerVtkWebProtocol(VtkModelPointsView())
        self.registerVtkWebProtocol(VtkModelCornersView())
        self.registerVtkWebProtocol(VtkModelLinesView())
        self.registerVtkWebProtocol(VtkModelSurfacesView())
        self.registerVtkWebProtocol(VtkModelBlocksView())
        self.registerVtkWebProtocol(VtkGenericView(mesh_protocols, model_protocols))

        # tell the C++ web app to use no encoding.
        # ParaViewWebPublishImageDelivery must be set to decode=False to match.
        self.getApplication().SetImageEncoding(0)

        # Update authentication key to use
        self.updateSecret(_Server.authKey)

        if not _Server.view:
            renderer = vtk.vtkRenderer()
            renderWindow = vtk.vtkRenderWindow()
            renderWindow.AddRenderer(renderer)
            self.setSharedObject("renderer", renderer)
            self.getApplication().GetObjectIdMap().SetActiveObject("VIEW", renderWindow)

            renderWindow.SetOffScreenRendering(not _Server.debug)


# =============================================================================
# Main: Parse args and start serverviewId
# =============================================================================


def run_server(Server=_Server):
    PYTHON_ENV = os.environ.get("PYTHON_ENV", default="prod").strip().lower()
    if PYTHON_ENV == "prod":
        prod_config()
    elif PYTHON_ENV == "dev":
        dev_config()

    parser = argparse.ArgumentParser(description="Vtk server")
    server.add_arguments(parser)

    Server.add_arguments(parser)
    args = parser.parse_args()

    if not "host" in args:
        args.host = os.environ["DEFAULT_HOST"]
    if not "port" in args or args.port == 8080:
        args.port = os.environ.get("DEFAULT_PORT")
    if "data_folder_path" in args and args.data_folder_path:
        os.environ["DATA_FOLDER_PATH"] = args.data_folder_path

    db_full_path = os.path.join(os.environ["DATA_FOLDER_PATH"], "project.db")
    connection.init_database(db_full_path, create_tables=False)
    print(f"Viewer connected to database at: {db_full_path}", flush=True)

    print(f"{args=}", flush=True)
    Server.configure(args)

    server.start_webserver(options=args, protocol=Server)


if __name__ == "__main__":
    run_server()

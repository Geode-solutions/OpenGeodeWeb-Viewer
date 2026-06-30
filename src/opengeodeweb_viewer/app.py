# Standard library imports
import argparse
import os
from typing import Any, cast, Protocol, runtime_checkable

# Third party imports
from vtkmodules.web.wslink import ServerProtocol
from vtkmodules.web import protocols as vtk_protocols
from wslink import server  # type: ignore
from vtkmodules.vtkWebCore import vtkWebApplication
from vtkmodules.vtkRenderingCore import vtkRenderer, vtkRenderWindow
from vtkmodules.vtkCommonCore import vtkFileOutputWindow, vtkOutputWindow
from opengeodeweb_microservice.database import connection

# Local application imports
from opengeodeweb_viewer.config import *
from opengeodeweb_viewer.vtk_protocol import VtkView, VtkTypingMixin
from opengeodeweb_viewer.rpc.viewer.viewer_protocols import VtkViewerView
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.points.points_protocols import VtkMeshPointsView
from opengeodeweb_viewer.rpc.mesh.points.attribute.vertex.points_attribute_vertex_protocols import (
    VtkMeshPointsAttributeVertexView,
)
from opengeodeweb_viewer.rpc.mesh.edges.edges_protocols import VtkMeshEdgesView
from opengeodeweb_viewer.rpc.mesh.edges.attribute.vertex.edges_attribute_vertex_protocols import (
    VtkMeshEdgesAttributeVertexView,
)
from opengeodeweb_viewer.rpc.mesh.edges.attribute.edge.edges_attribute_edge_protocols import (
    VtkMeshEdgesAttributeEdgeView,
)
from opengeodeweb_viewer.rpc.mesh.cells.cells_protocols import VtkMeshCellsView
from opengeodeweb_viewer.rpc.mesh.cells.attribute.vertex.cells_attribute_vertex_protocols import (
    VtkMeshCellsAttributeVertexView,
)
from opengeodeweb_viewer.rpc.mesh.cells.attribute.cell.cells_attribute_cell_protocols import (
    VtkMeshCellsAttributeCellView,
)
from opengeodeweb_viewer.rpc.mesh.polygons.polygons_protocols import VtkMeshPolygonsView
from opengeodeweb_viewer.rpc.mesh.polygons.attribute.vertex.polygons_attribute_vertex_protocols import (
    VtkMeshPolygonsAttributeVertexView,
)
from opengeodeweb_viewer.rpc.mesh.polygons.attribute.polygon.polygons_attribute_polygon_protocols import (
    VtkMeshPolygonsAttributePolygonView,
)
from opengeodeweb_viewer.rpc.mesh.polyhedra.polyhedra_protocols import (
    VtkMeshPolyhedraView,
)
from opengeodeweb_viewer.rpc.mesh.polyhedra.attribute.vertex.polyhedra_attribute_vertex_protocols import (
    VtkMeshPolyhedraAttributeVertexView,
)
from opengeodeweb_viewer.rpc.mesh.polyhedra.attribute.polyhedron.polyhedra_attribute_polyhedron_protocols import (
    VtkMeshPolyhedraAttributePolyhedronView,
)
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.rpc.model.edges.model_edges_protocols import (
    VtkModelEdgesView,
)
from opengeodeweb_viewer.rpc.model.points.model_points_protocols import (
    VtkModelPointsView,
)
from opengeodeweb_viewer.rpc.model.corners.model_corners_protocols import (
    VtkModelCornersView,
)
from opengeodeweb_viewer.rpc.model.lines.model_lines_protocols import (
    VtkModelLinesView,
)
from opengeodeweb_viewer.rpc.model.surfaces.model_surfaces_protocols import (
    VtkModelSurfacesView,
)
from opengeodeweb_viewer.rpc.model.blocks.model_blocks_protocols import (
    VtkModelBlocksView,
)
from opengeodeweb_viewer.rpc.model.corners.attribute.vertex.corners_attribute_vertex_protocols import (
    VtkModelCornersAttributeVertexView,
)
from opengeodeweb_viewer.rpc.model.lines.attribute.vertex.lines_attribute_vertex_protocols import (
    VtkModelLinesAttributeVertexView,
)
from opengeodeweb_viewer.rpc.model.lines.attribute.edge.lines_attribute_edge_protocols import (
    VtkModelLinesAttributeEdgeView,
)
from opengeodeweb_viewer.rpc.model.surfaces.attribute.vertex.surfaces_attribute_vertex_protocols import (
    VtkModelSurfacesAttributeVertexView,
)
from opengeodeweb_viewer.rpc.model.surfaces.attribute.polygon.surfaces_attribute_polygon_protocols import (
    VtkModelSurfacesAttributePolygonView,
)
from opengeodeweb_viewer.rpc.model.blocks.attribute.vertex.blocks_attribute_vertex_protocols import (
    VtkModelBlocksAttributeVertexView,
)
from opengeodeweb_viewer.rpc.model.blocks.attribute.polyhedron.blocks_attribute_polyhedron_protocols import (
    VtkModelBlocksAttributePolyhedronView,
)
from opengeodeweb_viewer.rpc.generic.generic_protocols import VtkGenericView
from opengeodeweb_viewer.rpc.utils_protocols import VtkUtilsView

# =============================================================================
# Server class
# =============================================================================


class _Server(VtkTypingMixin, ServerProtocol):
    # Defaults
    authKey = "wslink-secret"
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
        publisher = vtk_protocols.vtkWebPublishImageDelivery(decode=False)  # type: ignore
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
        self.registerVtkWebProtocol(VtkMeshPointsAttributeVertexView())
        self.registerVtkWebProtocol(VtkMeshEdgesView())
        self.registerVtkWebProtocol(VtkMeshEdgesAttributeVertexView())
        self.registerVtkWebProtocol(VtkMeshEdgesAttributeEdgeView())
        self.registerVtkWebProtocol(VtkMeshCellsView())
        self.registerVtkWebProtocol(VtkMeshCellsAttributeVertexView())
        self.registerVtkWebProtocol(VtkMeshCellsAttributeCellView())
        self.registerVtkWebProtocol(VtkMeshPolygonsView())
        self.registerVtkWebProtocol(VtkMeshPolygonsAttributeVertexView())
        self.registerVtkWebProtocol(VtkMeshPolygonsAttributePolygonView())
        self.registerVtkWebProtocol(VtkMeshPolyhedraView())
        self.registerVtkWebProtocol(VtkMeshPolyhedraAttributeVertexView())
        self.registerVtkWebProtocol(VtkMeshPolyhedraAttributePolyhedronView())
        self.registerVtkWebProtocol(model_protocols)
        self.registerVtkWebProtocol(VtkModelEdgesView())
        self.registerVtkWebProtocol(VtkModelPointsView())
        self.registerVtkWebProtocol(VtkModelCornersView())
        self.registerVtkWebProtocol(VtkModelLinesView())
        self.registerVtkWebProtocol(VtkModelSurfacesView())
        self.registerVtkWebProtocol(VtkModelBlocksView())
        self.registerVtkWebProtocol(VtkModelCornersAttributeVertexView())
        self.registerVtkWebProtocol(VtkModelLinesAttributeVertexView())
        self.registerVtkWebProtocol(VtkModelLinesAttributeEdgeView())
        self.registerVtkWebProtocol(VtkModelSurfacesAttributeVertexView())
        self.registerVtkWebProtocol(VtkModelSurfacesAttributePolygonView())
        self.registerVtkWebProtocol(VtkModelBlocksAttributeVertexView())
        self.registerVtkWebProtocol(VtkModelBlocksAttributePolyhedronView())
        self.registerVtkWebProtocol(VtkGenericView(mesh_protocols, model_protocols))

        # tell the C++ web app to use no encoding.
        # ParaViewWebPublishImageDelivery must be set to decode=False to match.
        self.getApplication().SetImageEncoding(0)

        # Update authentication key to use
        self.updateSecret(_Server.authKey)

        errOut = vtkFileOutputWindow()
        errOut.SetFileName("VTK.txt")
        vtkStdErrOut = vtkOutputWindow()
        vtkStdErrOut.SetInstance(errOut)

        if not _Server.view:
            renderer = vtkRenderer()
            renderWindow = vtkRenderWindow()
            renderWindow.AddRenderer(renderer)
            self.setSharedObject("renderer", renderer)
            self.getApplication().GetObjectIdMap().SetActiveObject("VIEW", renderWindow)

            renderWindow.SetOffScreenRendering(not _Server.debug)


# =============================================================================
# Main: Parse args and start serverviewId
# =============================================================================


def run_server(Server: type[ServerProtocol] = _Server) -> None:
    parser = argparse.ArgumentParser(description="Vtk server")
    server.add_arguments(parser)
    parser.set_defaults(port=None, host=None)
    Server.add_arguments(parser)
    args = parser.parse_args()

    if not "project_folder_path" in args:
        raise ValueError("project_folder_path must be provided")

    PYTHON_ENV = os.environ.get("PYTHON_ENV", "prod").strip().lower()

    app_config: Config
    if PYTHON_ENV == "prod":
        app_config = ProdConfig(args.project_folder_path)
    elif PYTHON_ENV == "dev":
        app_config = DevConfig(args.project_folder_path)
    elif PYTHON_ENV == "test":
        app_config = TestConfig(args.project_folder_path)
    else:
        raise ValueError(f"Unknown PYTHON_ENV: {PYTHON_ENV!r}")

    if args.host is None:
        args.host = app_config.HOST
    if args.port is None:
        args.port = app_config.PORT

    db_full_path = os.path.join(os.environ["DATA_FOLDER_PATH"], "project.db")
    connection.init_database(db_full_path, create_tables=False)
    print(f"Viewer connected to database at: {db_full_path}", flush=True)

    print(f"{args=}", flush=True)
    Server.configure(args)

    server.start_webserver(options=args, protocol=Server)


if __name__ == "__main__":
    run_server()

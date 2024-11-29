# Standard library imports
import argparse
import os
import sys

# Third party imports
import vtk
from vtk.web import wslink as vtk_wslink
from vtk.web import protocols as vtk_protocols
from wslink import server

# Local application imports
from .config import *
from .vtk_protocol import VtkView
from .rpc.viewer.viewer_protocols import VtkViewerView
from .rpc.mesh.mesh_protocols import VtkMeshView
from .rpc.model.model_protocols import VtkModelView
from .rpc.generic.generic_protocols import VtkGenericView


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
            "--data_folder_path", default=os.environ.get("DATA_FOLDER_PATH"), help="Path to the folder where data is stored"
        )

    @staticmethod
    def configure(args):
        # Standard args
        _Server.authKey = args.authKey

    def initialize(self):
        # Bring used components
        self.registerVtkWebProtocol(vtk_protocols.vtkWebMouseHandler())
        self.registerVtkWebProtocol(vtk_protocols.vtkWebViewPort())
        self.registerVtkWebProtocol(
            vtk_protocols.vtkWebPublishImageDelivery(decode=False)
        )
        self.setSharedObject("db", dict())

        # Custom API
        mesh_protocols = VtkMeshView()
        model_protocols = VtkModelView()
        self.registerVtkWebProtocol(VtkView())
        self.registerVtkWebProtocol(VtkViewerView())
        self.registerVtkWebProtocol(mesh_protocols)
        self.registerVtkWebProtocol(model_protocols)
        self.registerVtkWebProtocol(VtkGenericView(mesh_protocols,model_protocols))

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

            renderWindowInteractor = vtk.vtkRenderWindowInteractor()
            renderWindowInteractor.SetRenderWindow(renderWindow)
            renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()
            renderWindowInteractor.EnableRenderOff()
            self.getApplication().GetObjectIdMap().SetActiveObject("VIEW", renderWindow)

            widget = vtk.vtkOrientationMarkerWidget()
            widget.SetInteractor(renderWindowInteractor)
            widget.SetViewport(0.0, 0.0, 0.2, 0.2)
            axes = vtk.vtkAxesActor()
            widget.SetOrientationMarker(axes)
            widget.EnabledOn()
            widget.InteractiveOff()
            renderWindow.SetOffScreenRendering(not _Server.debug)
            self.setSharedObject("marker", widget)


# =============================================================================
# Main: Parse args and start serverviewId
# =============================================================================


def run_server():
    PYTHON_ENV = os.environ.get("PYTHON_ENV", default="prod").strip().lower()
    if PYTHON_ENV == "prod":
        prod_config()
    elif PYTHON_ENV == "dev":
        dev_config()

    parser = argparse.ArgumentParser(description="Vtk server")
    server.add_arguments(parser)

    _Server.add_arguments(parser)
    args = parser.parse_args()
    
    if not "host" in args:
        args.host = os.environ["DEFAULT_HOST"]
    if not "port" in args or args.port == 8080:
        args.port = os.environ.get("DEFAULT_PORT")
    if "data_folder_path" in args:
        os.environ["DATA_FOLDER_PATH"] = args.data_folder_path

    print(f"{args=}", flush=True)
    _Server.configure(args)
    server.start_webserver(options=args, protocol=_Server)


if __name__ == "__main__":
    run_server()

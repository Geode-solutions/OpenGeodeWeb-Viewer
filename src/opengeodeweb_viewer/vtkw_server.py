import sys
import argparse
import os

from wslink import server
from vtk.web import wslink as vtk_wslink
from vtk.web import protocols as vtk_protocols
import vtk
from .vtk_protocol import VtkView
import dotenv
from .config import *


# =============================================================================
# Server class
# =============================================================================


class _Server(vtk_wslink.ServerProtocol):
    # Defaults
    authKey = "wslink-secret"
    view = None

    @staticmethod
    def add_arguments(parser):
        parser.add_argument(
            "--virtual-env", default=None, help="Path to virtual environment to use"
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
        self.registerVtkWebProtocol(VtkView())

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
            self.setSharedObject("marker", widget)


# =============================================================================
# Main: Parse args and start serverviewId
# =============================================================================


def run_server():
    basedir = os.path.abspath(os.path.dirname(__file__))
    dot_env_path = os.path.join(basedir, "../../.env")
    if os.path.isfile(dot_env_path):
        dotenv.load_dotenv(dot_env_path)
    PYTHON_ENV = os.environ.get("PYTHON_ENV", default="prod").strip().lower()
    if PYTHON_ENV == "prod":
        prod_config()
    elif PYTHON_ENV == "dev":
        dev_config()

    parser = argparse.ArgumentParser(description="Vtk server")
    server.add_arguments(parser)

    _Server.add_arguments(parser)
    args = parser.parse_args()
    args.port = os.environ.get("PORT")
    args.host = os.environ.get("HOST")
    print(f"{args=}", flush=True)

    _Server.configure(args)
    server.start_webserver(options=args, protocol=_Server)


if __name__ == "__main__":
    run_server()

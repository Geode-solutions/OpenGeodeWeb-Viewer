<<<<<<< HEAD:vtkw_server.py
=======
r"""
    This module is a ParaViewWeb server application.
    The following command line illustrates how to use it::

        $ vtkpython .../server.py

    Any ParaViewWeb executable script comes with a set of standard arguments that can be overrides if need be::

        --port 8080
            Port number on which the HTTP server will listen.

        --content /path-to-web-content/
            Directory that you want to serve as static web content.
            By default, this variable is empty which means that we rely on another
            server to deliver the static content and the current process only
            focuses on the WebSocket connectivity of clients.

        --authKey vtkweb-secret
            Secret key that should be provided by the client to allow it to make
            any WebSocket communication. The client will assume if none is given
            that the server expects "vtkweb-secret" as secret key.

"""

>>>>>>> ea4cf8b996857bec06815067f98b044360db3d55:src/opengeodeweb_viewer/vtkw-server.py
import sys
import argparse
import config
import os

from wslink import server
from vtk.web import wslink as vtk_wslink
from vtk.web import protocols as vtk_protocols
import vtk
from vtk_protocol import VtkView
import dotenv

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


if __name__ == "__main__":
    if os.path.isfile("./.env"):
        basedir = os.path.abspath(os.path.dirname(__file__))
        dotenv.load_dotenv(os.path.join(basedir, ".env"))
    PYTHON_ENV = os.environ.get("PYTHON_ENV", default="prod").strip().lower()
    if PYTHON_ENV == "prod":
        config.prod_config()
    elif PYTHON_ENV == "dev":
        config.dev_config()

    parser = argparse.ArgumentParser(description="Vtk server")
    server.add_arguments(parser)

    _Server.add_arguments(parser)
    args = parser.parse_args()
    args.port = os.environ.get("PORT")
    args.host = os.environ.get("HOST")
    print(f"{args=}", flush=True)

    _Server.configure(args)
    server.start_webserver(options=args, protocol=_Server)

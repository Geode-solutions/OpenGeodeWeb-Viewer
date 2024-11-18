# Standard library imports
import json
import os

# Third party imports
import vtk
from vtk.web import protocols as vtk_protocols
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import validate_schema
from opengeodeweb_viewer.vtk_protocol import VtkView

class VtkModelView(VtkView):
    def toto():
        return ""
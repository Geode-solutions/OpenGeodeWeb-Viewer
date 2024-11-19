# Standard library imports
import json
import os

# Third party imports
import vtk
from vtk.web import protocols as vtk_protocols
from vtkmodules.vtkIOImage import vtkPNGWriter, vtkJPEGWriter
from vtkmodules.vtkRenderingCore import (vtkWindowToImageFilter)
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.vtk_protocol import VtkView


schemas_dir = os.path.join(os.path.dirname(__file__), "schemas")
schemas_dict = get_schemas_dict(schemas_dir)

class VtkMeshView(VtkObjectView):
    def __init__(self):
        super().__init__()

    @exportRpc(schemas_dict["toggle_object_visibility"]["rpc"])
    def toggle_object_visibility(self, params):
        print(f"{schemas_dict["toggle_object_visibility"]["rpc"]=}", flush=True)
        validate_schema(params, schemas_dict["toggle_object_visibility"])
        super().SetVisibility(params)

    @exportRpc(schemas_dict["set_opacity"]["rpc"])
    def SetOpacity(self, params):
        print(f"{schemas_dict["set_opacity"]["rpc"]=}", flush=True)
        validate_schema(params, schemas_dict["set_opacity"])
        super().SetOpacity(params)

    @exportRpc(schemas_dict["toggle_edge_visibility"]["rpc"])
    def setEdgeVisibility(self, params):
        print(f"{schemas_dict["toggle_edge_visibility"]["rpc"]=}", flush=True)
        validate_schema(params, schemas_dict["toggle_edge_visibility"])
        print(f"{params=}", flush=True)
        super().SetEdgeVisibility(params)

    @exportRpc(schemas_dict["toggle_point_visibility"]["rpc"])
    def setPointVisibility(self, params):
        validate_schema(params, schemas_dict["toggle_point_visibility"])
        super().SetVertexVisibility(params)

    @exportRpc(schemas_dict["set_point_size"]["rpc"])
    def setPointSize(self, params):
        validate_schema(params, schemas_dict["set_point_size"])
        super().SetPointSize(params)

    @exportRpc(schemas_dict["set_color"]["rpc"])
    def setColor(self, params):
        validate_schema(params, schemas_dict["set_color"])
        super().SetColor(params)

    @exportRpc(schemas_dict["display_vertex_attribute"]["rpc"])
    def setVertexAttribute(self, params):
        validate_schema(params, schemas_dict["display_vertex_attribute"])
        print(f"{params=}", flush=True)
        id = params["id"]
        name = params["name"]
        mapper = self.get_object(id)["mapper"]
        mapper.SelectColorArray(name)
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUsePointFieldData()
        self.render()

    @exportRpc(schemas_dict["display_polygon_attribute"]["rpc"])
    def setPolygonAttribute(self, id, name):
        store = self.getObject(id)
        cpp = store["cpp"]
        print(cpp.nb_polygons())
        cells = store["vtk"].GetCellData()
        print(store["vtk"].GetNumberOfCells())
        manager = cpp.polygon_attribute_manager()
        if not manager.attribute_exists(name):
            return
        if not cells.HasArray(name):
            data = self.computeAttributeData(manager, name)
            cells.AddArray(data)
        cells.SetActiveScalars(name)
        mapper = store["mapper"]
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUseCellData()
        mapper.SetScalarRange(cells.GetScalars().GetRange())
        self.render()
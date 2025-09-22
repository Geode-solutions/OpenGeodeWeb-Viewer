# Standard library imports
import os

# Third party imports
import vtk
from vtkmodules.vtkRenderingCore import vtkCompositeDataDisplayAttributes
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.object.object_methods import VtkObjectView


class VtkModelView(VtkObjectView):
    model_prefix = "opengeodeweb_viewer.model."
    model_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self):
        super().__init__()

    def _build_model_pipeline(self, file_path: str):
        reader = vtk.vtkXMLMultiBlockDataReader()
        reader.SetFileName(file_path)
        geometry = vtk.vtkGeometryFilter()
        geometry.SetInputConnection(reader.GetOutputPort())
        mapper = vtk.vtkCompositePolyDataMapper()
        mapper.SetInputConnection(geometry.GetOutputPort())
        attributes = vtkCompositeDataDisplayAttributes()
        mapper.SetCompositeDataDisplayAttributes(attributes)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        return reader, geometry, mapper, actor

    @exportRpc(model_prefix + model_schemas_dict["register"]["rpc"])
    def registerModel(self, params):
        validate_schema(params, self.model_schemas_dict["register"], self.model_prefix)
        data_id = params["id"]
        try:
            _ = self.get_data(data_id)
            file_path = self.get_data_file_path(data_id)

            reader, geometry, mapper, actor = self._build_model_pipeline(file_path)
            renderer = self.get_renderer()
            renderer.AddActor(actor)

            self.register_object(data_id, reader, geometry, actor, mapper, {})
            self.get_object(data_id)["max_dimension"] = "default"
            renderWindow = self.getView("-1")
            renderer.ResetCamera()
            renderWindow.Render()
            self.render()
        except Exception as e:
            print(f"Error registering model {data_id}: {str(e)}", flush=True)
            raise

    @exportRpc(model_prefix + model_schemas_dict["deregister"]["rpc"])
    def deregisterModel(self, params):
        validate_schema(
            params, self.model_schemas_dict["deregister"], self.model_prefix
        )
        data_id = params["id"]

        if data_id in self.get_data_base():
            obj = self.get_object(data_id)
            if "actor" in obj and obj["actor"]:
                renderer = self.get_renderer()
                renderer.RemoveActor(obj["actor"])

        self.deregister_object(data_id)
        self.render()

    @exportRpc(model_prefix + model_schemas_dict["visibility"]["rpc"])
    def setModelVisibility(self, params):
        validate_schema(
            params, self.model_schemas_dict["visibility"], self.model_prefix
        )
        data_id, visibility = params["id"], params["visibility"]
        self.SetVisibility(data_id, visibility)

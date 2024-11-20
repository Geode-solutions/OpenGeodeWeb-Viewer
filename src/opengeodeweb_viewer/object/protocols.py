# Standard library imports
import os

# Third party imports
import vtk
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.vtk_protocol import VtkView

schemas_dir = os.path.join(os.path.dirname(__file__), "schemas")
schemas_dict = get_schemas_dict(schemas_dir)


class VtkObjectView(VtkView):
    def __init__(self):
        super().__init__()

    @exportRpc(schemas_dict["register"]["rpc"])
    def registerObject(self, params):
        validate_schema(params, schemas_dict["register"])
        try:
            id = params["id"]
            file_name = params["file_name"]
            FOLDER_PATH = os.path.dirname(__file__)

            actor = vtk.vtkActor()
            if ".vtm" in file_name:
                reader = vtk.vtkXMLMultiBlockDataReader()
                filter = vtk.vtkGeometryFilter()
                filter.SetInputConnection(reader.GetOutputPort())
                mapper = vtk.vtkCompositePolyDataMapper()
                mapper.SetInputConnection(filter.GetOutputPort())
            else:
                reader = vtk.vtkXMLGenericDataObjectReader()
                filter = {}
                mapper = vtk.vtkDataSetMapper()
                mapper.SetInputConnection(reader.GetOutputPort())
                
            self.register_object(id, reader, filter, actor, mapper, {})

            reader.SetFileName(os.path.join(self.DATA_FOLDER_PATH, file_name))

            actor.SetMapper(mapper)
            mapper.SetColorModeToMapScalars()
            mapper.SetResolveCoincidentTopologyLineOffsetParameters(1, -0.1)
            mapper.SetResolveCoincidentTopologyPolygonOffsetParameters(2, 0)
            mapper.SetResolveCoincidentTopologyPointOffsetParameter(-2)

            renderWindow = self.getView("-1")
            renderer = renderWindow.GetRenderers().GetFirstRenderer()
            renderer.AddActor(actor)
            renderer.ResetCamera()
            renderWindow.Render()
            self.render()
        except Exception as e:
            print("error : ", str(e), flush=True)

    @exportRpc(schemas_dict["deregister"]["rpc"])
    def deregisterObject(self, params):
        validate_schema(params, schemas_dict["deregister"])
        print(f"{params=}", flush=True)
        id = params["id"]
        object = self.get_object(id)
        actor = object["actor"]
        renderWindow = self.getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()
        renderer.RemoveActor(actor)
        print(f"{object=}", flush=True)
        self.deregister_object(id)
        self.render()

    
    @exportRpc(schemas_dict["apply_textures"]["rpc"])
    def applyTextures(self, params):
        validate_schema(params, schemas_dict["apply_textures"])
        print(f"{params=}", flush=True)
        id = params["id"]
        textures = params["textures"]
        textures_array = []
        images_reader_array = []

        data = self.get_object(id)
        mapper = data["mapper"]
        actor = data["actor"]
        reader = data["reader"]

        polydata_mapper = mapper.GetPolyDataMapper()
        poly_data = reader.GetPolyDataOutput()

        for index, value in enumerate(textures):
            texture_name = value["texture_name"]
            texture_file_name = value["texture_file_name"]
            print(f"{texture_name=} {texture_file_name=}", flush=True)

            new_texture = vtk.vtkTexture()
            image_reader = vtk.vtkXMLImageDataReader()
            image_reader.SetFileName(
                os.path.join(self.DATA_FOLDER_PATH, texture_file_name)
            )

            shader_texture_name = f"VTK_TEXTURE_UNIT_{index}"
            polydata_mapper.MapDataArrayToMultiTextureAttribute(
                shader_texture_name,
                texture_name,
                vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS,
            )

            if index == 0:
                new_texture.SetBlendingMode(
                    vtk.vtkTexture.VTK_TEXTURE_BLENDING_MODE_REPLACE
                )
            else:
                new_texture.SetBlendingMode(
                    vtk.vtkTexture.VTK_TEXTURE_BLENDING_MODE_ADD
                )

            images_reader_array.append(image_reader)
            new_texture.SetInputConnection(image_reader.GetOutputPort())

            actor.GetProperty().SetTexture(shader_texture_name, new_texture)

            textures_array.append(new_texture)
            images_reader_array.append(image_reader)

        self.render()


    def SetVisibility(self, params):
        validate_schema(params, schemas_dict["set_visibility"])
        id = params["id"]
        visibility = bool(params["visibility"])
        actor = self.get_object(id)["actor"]
        actor.SetVisibility(visibility)
        self.render()

    def SetOpacity(self, params):
        print(f"{params=}", flush=True)
        validate_schema(params, schemas_dict["set_opacity"])
        id = params["id"]
        opacity = float(params["opacity"])
        actor = self.get_object(id)["actor"]
        actor.GetProperty().SetOpacity(opacity)
        self.render()
    
    def SetColor(self, params):
        validate_schema(params, schemas_dict["set_color"])
        id = params["id"]
        color = params["color"]
        mapper = self.get_object(id)["mapper"]
        mapper.ScalarVisibilityOff()
        actor = self.get_object(id)["actor"]
        actor.GetProperty().SetColor(color)
        self.render()

    def SetEdgeVisibility(self, params):
        print(f"{params=}", flush=True)
        validate_schema(params, schemas_dict["set_edge_visibility"])
        id = params["id"]
        visibility = bool(params["visibility"])
        actor = self.get_object(id)["actor"]
        actor.GetProperty().SetEdgeVisibility(visibility)
        self.render()

    def SetVertexVisibility(self, params):
        print(f"{params=}", flush=True)
        validate_schema(params, schemas_dict["set_vertex_visility"])
        id = params["id"]
        visibility = bool(params["visibility"])
        actor = self.get_object(id)["actor"]
        actor.GetProperty().SetVertexVisibility(visibility)
        self.render()

    def SetPointSize(self, params):
        validate_schema(params, schemas_dict["set_point_size"])
        id = params["id"]
        size = float(params["size"])
        actor = self.get_object(id)["actor"]
        actor.GetProperty().SetPointSize(size)
        self.render()
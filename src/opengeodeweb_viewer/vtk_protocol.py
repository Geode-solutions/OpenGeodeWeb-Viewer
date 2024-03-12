import json
import os
from vtk.web import protocols as vtk_protocols
from wslink import register as exportRpc
import vtk
from .function import validate_schemas

schemas = os.path.join(os.path.dirname(__file__), "rpc/schemas")

with open(os.path.join(schemas, "create_visualization.json"), "r") as file:
    create_visualization_json = json.load(file)
with open(os.path.join(schemas, "reset_camera.json"), "r") as file:
    reset_camera_json = json.load(file)
with open(os.path.join(schemas, "create_object_pipeline.json"), "r") as file:
    create_object_pipeline_json = json.load(file)
with open(os.path.join(schemas, "delete_object_pipeline.json"), "r") as file:
    delete_object_pipeline_json = json.load(file)
with open(os.path.join(schemas, "toggle_object_visibility.json"), "r") as file:
    toggle_object_visibility_json = json.load(file)
with open(os.path.join(schemas, "apply_textures.json"), "r") as file:
    apply_textures_json = json.load(file)
with open(os.path.join(schemas, "update_data.json"), "r") as file:
    update_data_json = json.load(file)
with open(os.path.join(schemas, "get_point_position.json"), "r") as file:
    get_point_position_json = json.load(file)
with open(os.path.join(schemas, "reset.json"), "r") as file:
    reset_json = json.load(file)
with open(os.path.join(schemas, "toggle_edge_visibility.json"), "r") as file:
    toggle_edge_visibility_json = json.load(file)
with open(os.path.join(schemas, "point_size.json"), "r") as file:
    point_size_json = json.load(file)
with open(os.path.join(schemas, "toggle_point_visibility.json"), "r") as file:
    toggle_point_visibility_json = json.load(file)
with open(os.path.join(schemas, "set_color.json"), "r") as file:
    set_color_json = json.load(file)
with open(os.path.join(schemas, "set_vertex_attribute.json"), "r") as file:
    set_vertex_attribute_json = json.load(file)


class VtkView(vtk_protocols.vtkWebProtocol):
    def __init__(self):
        self.DATA_FOLDER_PATH = os.getenv("DATA_FOLDER_PATH")
        self.DataReader = vtk.vtkXMLPolyDataReader()
        self.ImageReader = vtk.vtkXMLImageDataReader()

    @exportRpc(create_visualization_json["rpc"])
    def create_visualization(self, params):
        validate_schemas(params, create_visualization_json)
        renderWindow = self.getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()
        renderer.SetBackground([180 / 255, 180 / 255, 180 / 255])
        renderer.ResetCamera()
        renderWindow.Render()
        self.render()

    @exportRpc(reset_camera_json["rpc"])
    def reset_camera(self, params):
        print(f"{params=}", flush=True)
        validate_schemas(params, reset_camera_json)
        renderWindow = self.getView("-1")
        renderWindow.GetRenderers().GetFirstRenderer().ResetCamera()
        renderWindow.Render()
        self.render()

    @exportRpc(create_object_pipeline_json["rpc"])
    def create_object_pipeline(self, params):
        validate_schemas(params, create_object_pipeline_json)
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
                self.register_object(id, reader, filter, actor, mapper, {})
            else:
                reader = vtk.vtkXMLGenericDataObjectReader()
                mapper = vtk.vtkDataSetMapper()
                mapper.SetInputConnection(reader.GetOutputPort())
                self.register_object(id, reader, {}, actor, mapper, {})

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

    @exportRpc(delete_object_pipeline_json["rpc"])
    def delete_object_pipeline(self, params):
        validate_schemas(params, delete_object_pipeline_json)
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

    @exportRpc(toggle_object_visibility_json["rpc"])
    def toggle_object_visibility(self, params):
        validate_schemas(params, toggle_object_visibility_json)
        print(f"{params=}", flush=True)
        id = params["id"]
        is_visible = params["is_visible"]
        object = self.get_object(id)
        actor = object["actor"]
        actor.SetVisibility(is_visible)
        self.render()

    @exportRpc(apply_textures_json["rpc"])
    def apply_textures(self, params):
        validate_schemas(params, apply_textures_json)
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

    @exportRpc(update_data_json["rpc"])
    def update_data(self, params):
        validate_schemas(params, update_data_json)
        print(f"{params=}", flush=True)
        id = params["id"]

        data = self.get_object(id)
        reader = data["reader"]
        reader.Update()
        mapper = data["mapper"]
        tag = vtk.reference(0)
        scalars = vtk.vtkAbstractMapper.GetAbstractScalars(
            reader.GetOutput(),
            mapper.GetScalarMode(),
            mapper.GetArrayAccessMode(),
            mapper.GetArrayId(),
            mapper.GetArrayName(),
            tag,
        )
        mapper.SetScalarRange(scalars.GetRange())
        self.render()

    @exportRpc(get_point_position_json["rpc"])
    def get_point_position(self, params):
        validate_schemas(params, get_point_position_json)
        x = float(params["x"])
        y = float(params["y"])
        xyz = [x, y, 0.0]
        picker = vtk.vtkWorldPointPicker()
        picker.Pick(xyz, self.get_renderer())
        ppos = picker.GetPickPosition()
        return {"x": ppos[0], "y": ppos[1], "z": ppos[2]}

    @exportRpc(reset_json["rpc"])
    def reset(self, params):
        validate_schemas(params, reset_json)
        renderWindow = self.getView("-1")
        renderWindow.GetRenderers().GetFirstRenderer().RemoveAllViewProps()

    @exportRpc(toggle_edge_visibility_json["rpc"])
    def setEdgeVisibility(self, params):
        validate_schemas(params, toggle_edge_visibility_json)
        print(f"{params=}", flush=True)
        id = params["id"]
        visibility = bool(params["visibility"])
        actor = self.get_object(id)["actor"]
        actor.GetProperty().SetEdgeVisibility(visibility)
        self.render()

    @exportRpc(toggle_point_visibility_json["rpc"])
    def setPointVisibility(self, params):
        validate_schemas(params, toggle_point_visibility_json)
        id = params["id"]
        visibility = bool(params["visibility"])
        actor = self.get_object(id)["actor"]
        actor.GetProperty().SetVertexVisibility(visibility)
        self.render()

    @exportRpc(point_size_json["rpc"])
    def setPointSize(self, params):
        validate_schemas(params, point_size_json)
        id = params["id"]
        size = float(params["size"])
        actor = self.get_object(id)["actor"]
        actor.GetProperty().SetPointSize(size)
        self.render()

    @exportRpc(set_color_json["rpc"])
    def setColor(self, params):
        validate_schemas(params, set_color_json)
        id = params["id"]
        red = params["red"]
        green = params["green"]
        blue = params["blue"]
        self.get_object(id)["mapper"].ScalarVisibilityOff()
        actor = self.get_object(id)["actor"]
        actor.GetProperty().SetColor(red, green, blue)
        self.render()

    @exportRpc(set_vertex_attribute_json["rpc"])
    def setVertexAttribute(self, params):
        validate_schemas(params, set_vertex_attribute_json)
        print(f"{params=}", flush=True)
        id = params["id"]
        name = params["name"]
        mapper = self.get_object(id)["mapper"]
        mapper.SelectColorArray(name)
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUsePointFieldData()
        self.render()

    def get_data_base(self):
        return self.getSharedObject("db")

    def get_renderer(self):
        return self.getSharedObject("renderer")

    def get_object(self, id):
        return self.get_data_base()[id]

    def get_protocol(self, name):
        for p in self.coreServer.getLinkProtocols():
            if type(p).__name__ == name:
                return p

    def render(self, view=-1):
        self.get_protocol("vtkWebPublishImageDelivery").imagePush({"view": view})

    def register_object(self, id, reader, filter, actor, mapper, textures):
        self.get_data_base()[id] = {
            "reader": reader,
            "filter": filter,
            "actor": actor,
            "mapper": mapper,
            "textures": textures,
        }

    def deregister_object(self, id):
        del self.get_data_base()[id]
